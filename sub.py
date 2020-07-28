"""
Manages the submarines as a whole and the individual submarines within it.
"""

from random import choice

from world import move_on_map, possible_directions

# State dictionary, filled with submarines.
state = {}

def get_teams():
    """
    Gets all possible teams.
    """
    return state.keys()

def get_sub(name):
    """
    Gets the Submarine object associated with `name`.
    """
    return state[name]

def add_team(name, channel):
    """
    Adds a team with the name, if able.
    """
    if name not in get_teams():
        state[name] = Submarine(name, channel)
        return True
    return False

MAX_SPEED = 4

class Submarine():
    def __init__(self, name, channel):
        self.name = name
        self.channel = channel
        self.direction = "N"
        # power is a dictionary mapping systems to (current power, total power possible).
        self.power = {"engine": (0,1), "scanner": (1,1), "comms": (1,2), "crane": (0,1), "weapons": (1,1)}
        # power_cap acts as health - if your power_cap would go _below_ zero, you explode.
        self.power_cap = 3
        # max_power_cap allows for healing up until that cap.
        self.max_power_cap = 3
        # innate power is power that you're not allowed to change.
        # Control can use this to provide a mandatory upgrade.
        self.innate_power = {"engine": 1}
        self.x = 0
        self.y = 0
        self.active = False

    def get_power(self, system):
        """
        Returns the power given to a system, both innately and otherwise.
        """
        used = 0
        if system in self.power:
            used += self.power[system][0]
        if system in self.innate_power:
            used += self.innate_power[system]
        return used
    
    def activation_divisor(self):
        """
        Returns the "activation divisor" - that is, what division of loops this
        submarine should activate during. Lower number => activates more.
        """
        return MAX_SPEED - self.get_power("engine") + 1
    
    def power_use(self):
        use = 0
        for system in self.power:
            use += self.power[system][0]
        return use
    
    def power_systems(self, systems):
        """
        Attempts to give power to the list of things to power `systems`.
        Will not change anything if it would mean you go over the power cap.
        Will ignore systems that do not already exist, except for verifying
        whether we have enough power to perform the operation (if we do but it
        looks like we don't due to an unknown system being named, tough).
        """
        if len(systems) > self.power_cap - self.power_use():
            return False
        power_copy = self.power.copy()
        for system in systems:
            if system in power_copy:
                (use, maxi) = power_copy[system]
                use += 1
                if use > maxi:
                    return False
                power_copy[system] = (use, maxi)
        self.power = power_copy
        return True
    
    def unpower_systems(self, systems):
        """
        Attempts to remove power from all of the named systems in `systems`.
        Will ignore systems that do not already exist.
        """
        power_copy = self.power.copy()
        for system in systems:
            if system in power_copy:
                (use, maxi) = power_copy[system]
                use -= 1
                if use < 0:
                    return False
                power_copy[system] = (use, maxi)
        self.power = power_copy
        return True

    def set_direction(self, direction):
        if direction in possible_directions():
            self.direction = direction
            return True
        return False

    def get_direction(self):
        return self.direction

    def get_position(self):
        return (self.x, self.y)

    def activate(self, value):
        self.active = value
        return True

    def activated(self):
        return self.active

    def move(self):
        self.x, self.y, message = move_on_map(self, self.direction, self.x, self.y)
        return message
    
    def damage(self, amount):
        if amount <= 0:
            return ""
        self.power_cap -= 1
        # If the submarine is now below zero power, it explodes.
        if self.power_cap < 0:
            self.activate(False)
            return "**SUBMARINE DESTROYED. PLEASE SPEAK TO CONTROL.**"
        # Otherwise, if there is unused power, damage that first.
        system = ""
        if self.power_use() < self.power_cap:
            system = "reserves"
        else:
            # Pick a system at random to lose power.
            available_systems = filter(lambda system: self.power[system][0] > 0, self.power)
            system = choice(list(available_systems))
            self.unpower_systems([system])
        # If the submarine hits zero, soak up all remaining damage.
        if self.power_cap == 0:
            return (
                f"Damage taken to {system}!\n"
                "**EMERGENCY SUBMARINE POWER INITIATED!!! ONLY BASIC ENGINE FUNCTIONALITY AVAILABLE!!!**"
            )
        # Else continue taking damage.
        message = self.damage(amount - 1)
        return f"Damage taken to {system}!\n" + message

    def heal(self, amount):
        self.power_cap = min(self.power_cap + amount, self.max_power_cap)
        return f"Healed back up to {self.power_cap} power!"

    def get_message_error(self, distance):
        """
        We define the message error as the proportion of incorrect characters
        in a message. This error increases with distance between two subs.
        We (arbitrarily) define this error as 5%/comms per point of distance.
        The error never goes above 100%. Messages with 100% are not received.
        """
        if self.power["comms"] == 0:
            return 100
        return max(distance * 5 / self.power["comms"], 100)

    def status_message(self):
        message = (
            f"Status for **{self.name}**\n"
            f"------------------------------------\n"
        )
        
        if self.activated():
            message += f"Currently moving **{self.direction}** and in position ({self.x}, {self.y}).\n\n"
        else:
            message += f"Submarine is currently offline.\n\n"

        message += f"**Power status** ({self.power_use()}/{self.power_cap} used):\n"

        for system in self.power:
            (use, maxi) = self.power[system]
            innate = 0
            if system in self.innate_power:
                innate = self.innate_power[system]
            
            power_status = f"({use}/{maxi}"
            if innate > 0:
                power_status += f" with {innate} innate"
            power_status += ")"

            system_status = "offline"
            if use + innate > 0:
                system_status = "online"
            message += f"* **{system.capitalize()}** is {system_status} {power_status}\n"

        # TODO: add inventory here.
        return message + "\nNo more to report."

    async def send_message(self, content):
        await self.channel.send(content)
