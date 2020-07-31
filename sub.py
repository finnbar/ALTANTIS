"""
Manages the submarines as a whole and the individual submarines within it.
"""

from random import choice, random
from time import time as now

from world import move_on_map, possible_directions, get_square, X_LIMIT, Y_LIMIT

# State dictionary, filled with submarines.
state = {}

def get_teams():
    """
    Gets all possible teams.
    """
    return list(state.keys())

def get_sub(name):
    """
    Gets the Submarine object associated with `name`.
    """
    if name in state:
        return state[name]

def add_team(name, category):
    """
    Adds a team with the name, if able.
    """
    if name not in get_teams():
        child_channels = category.text_channels
        channel_dict = {}
        for channel in child_channels:
            channel_dict[channel.name] = channel
        state[name] = Submarine(name, channel_dict)
        return True
    return False

MAX_SPEED = 4
GARBLE = 10
COMMS_COOLDOWN = 30

class Submarine():
    def __init__(self, name, channels):
        self.name = name
        self.channels = channels
        self.direction = "N"
        # power is a dictionary mapping systems to their current power.
        self.power = {"engines": 0, "scanners": 1, "comms": 1, "crane": 0, "weapons": 1}
        # power_max is the maximum power for each system.
        self.power_max = {"engines": 1, "scanners": 1, "comms": 2, "crane": 1, "weapons": 1}
        # total_power acts as health - if your total_power would go _below_ zero, you explode.
        self.total_power = 3
        # total_power_max allows for healing up until that cap.
        self.total_power_max = 3
        # innate power is power that you're not allowed to change.
        # Control can use this to provide a mandatory upgrade.
        self.innate_power = {"engines": 1}
        # Power only updates at game tick, so we need to keep track of the changes made.
        self.scheduled_power = self.power.copy()
        self.x = 0
        self.y = 0
        self.active = False
        # movement_progress is how much energy has been put towards a move.
        # Once it reaches a value determined by the engines, we move!
        self.movement_progress = 0
        # last_comms is the time when the Comms were last used.
        self.last_comms = 0

    def get_power(self, system):
        """
        Returns the power given to a system, both innately and otherwise.
        """
        used = 0
        if system in self.power:
            used += self.power[system]
        if system in self.innate_power:
            used += self.innate_power[system]
        return used
    
    def movement_tick(self):
        """
        Updates internal state and moves if it is time to do so.
        """
        self.movement_progress += self.get_power("engines")
        threshold = get_square(self.x, self.y).difficulty()
        if self.movement_progress >= threshold:
            self.movement_progress -= threshold
            direction = self.direction # Direction can change as result of movement.
            message = self.move()
            move_status = (
                f"Moved **{self.name}** in direction **{direction}**!\n"
                f"**{self.name}** is now at position **{self.get_position()}**."
            )
            if message:
                return f"{message}\n{move_status}"
            return move_status
        return None
    
    def power_use(self, power):
        use = 0
        for system in power:
            use += power[system]
        return use
    
    def apply_power_schedule(self):
        # Check for changes and add these to the string.
        message = ""
        for system in self.power:
            difference = self.scheduled_power[system] - self.power[system]
            connective = "increased"
            if difference < 0:
                connective = "decreased"
            if difference != 0:
                message += f"Power to **{system}** {connective} by {abs(difference)}.\n"
        self.power = self.scheduled_power
        if message == "":
            return None
        return message
    
    def power_systems(self, systems):
        """
        Attempts to give power to the list of things to power `systems`.
        Will not change anything if it would mean you go over the power cap.
        Will ignore systems that do not already exist, except for verifying
        whether we have enough power to perform the operation (if we do but it
        looks like we don't due to an unknown system being named, tough).
        """
        if len(systems) > self.total_power - self.power_use(self.scheduled_power):
            return False
        power_copy = self.scheduled_power.copy()
        for system in systems:
            if system in power_copy:
                use = power_copy[system]
                maxi = self.power_max[system]
                use += 1
                if use > maxi:
                    return False
                power_copy[system] = use
        self.scheduled_power = power_copy
        return True
    
    def unpower_systems(self, systems):
        """
        Attempts to remove power from all of the named systems in `systems`.
        Will ignore systems that do not already exist.
        """
        power_copy = self.scheduled_power.copy()
        for system in systems:
            if system in power_copy:
                use = power_copy[system]
                use -= 1
                if use < 0:
                    return False
                power_copy[system] = use
        self.scheduled_power = power_copy
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
        self.total_power -= 1
        # If the submarine is now below zero power, it explodes.
        if self.total_power < 0:
            self.activate(False)
            return "**SUBMARINE DESTROYED. PLEASE SPEAK TO CONTROL.**"
        # Otherwise, if there is unused power, damage that first.
        system = ""
        if self.power_use(self.power) < self.total_power:
            system = "reserves"
        else:
            # Pick a system at random to lose power.
            available_systems = filter(lambda system: self.power[system] > 0, self.power)
            system = choice(list(available_systems))
            self.unpower_systems([system])
        # If the submarine hits zero, soak up all remaining damage.
        if self.total_power == 0:
            return (
                f"Damage taken to {system}!\n"
                "**EMERGENCY SUBMARINE POWER INITIATED!!! ONLY BASIC ENGINE FUNCTIONALITY AVAILABLE!!!**"
            )
        # Else continue taking damage.
        message = self.damage(amount - 1)
        return f"Damage taken to {system}!\n" + message

    def heal(self, amount):
        self.total_power = min(self.total_power + amount, self.total_power_max)
        return f"Healed back up to {self.total_power} power!"

    def garble(self, content, distance):
        """
        We define the message error as the proportion of incorrect characters
        in a message. This error increases with distance between two subs.
        We define this error as GARBLE/comms per point of distance.
        The error never goes above 100%. Messages with 100% are not received.
        """
        if self.power["comms"] == 0:
            return None
        message_error = min(distance * GARBLE / self.power["comms"], 100)
        if message_error == 100:
            return None
        new_content = list(content)
        for i in range(len(new_content)):
            if new_content[i] not in [" ", "\n", "\r"] and random() < message_error / 100:
                new_content[i] = "_"
        return "".join(new_content)

    def status_message(self):
        message = (
            f"Status for **{self.name}**\n"
            f"------------------------------------\n"
        )
        
        if self.activated():
            message += f"Currently moving **{self.direction}** and in position ({self.x}, {self.y}).\n\n"
        else:
            message += f"Submarine is currently offline.\n\n"

        message += f"**Power status** ({self.power_use(self.power)}/{self.total_power}/{self.total_power_max} used/available/max):\n"

        for system in self.power:
            use = self.power[system]
            maxi = self.power_max[system]
            innate = 0
            scheduled = self.scheduled_power[system]
            difference = scheduled - use

            if system in self.innate_power:
                innate = self.innate_power[system]
            
            power_status = f"({use}/{maxi}"
            if innate > 0 or difference != 0:
                power_status += " with"
            if innate > 0:
                power_status += f" {innate} innate"
                if difference != 0:
                    power_status += ","
            if difference != 0:
                plusminus = "+"
                if difference < 0:
                    plusminus = "-"
                power_status += f" {plusminus}{abs(difference)} scheduled"
            power_status += ")"

            system_status = "offline"
            if use + innate > 0:
                system_status = "online"
            message += f"* **{system.capitalize()}** is {system_status} {power_status}\n"

        # TODO: add inventory here.
        return message + "\nNo more to report."

    async def send_message(self, content, channel):
        if self.channels[channel]:
            await self.channels[channel].send(content)
            return True
        return False
    
    async def send_to_all(self, content):
        for channel in self.channels:
            await self.channels[channel].send(content)
        return True
    
    async def broadcast(self, content):
        if self.last_comms + COMMS_COOLDOWN > now():
            return False
        subnames = get_teams()
        for subname in subnames:
            if subname == self.name:
                continue

            sub = get_sub(subname)

            # First, get manhattan distance with diagonals.
            # I don't know what this is called, but the fastest route is
            # to take the diagonal and then do any excess.
            # To do wraparound, we consider both distances, so |x1-x2| and
            # X_LIMIT - |x1-x2| (and the same for y).
            xdist = abs(sub.x - self.x)
            xdist = min(40 - xdist, xdist)
            ydist = abs(sub.y - self.y)
            ydist = min(40 - ydist, ydist)
            dist = min(xdist, ydist) + abs(xdist - ydist)
            garbled = self.garble(content, dist)
            if garbled is not None:
                await sub.send_message(f"**Message received from {self.name}**:\n`{garbled}`\n**END MESSAGE**")
        self.last_comms = now()
        return True