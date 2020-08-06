"""
Manages the submarines as a whole and the individual submarines within it.
"""

from random import choice, random, shuffle
from time import time as now
from utils import diagonal_distance, determine_direction

from world import move_on_map, possible_directions, get_square, X_LIMIT, Y_LIMIT, explore_submap

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

def add_team(name, category, x, y):
    """
    Adds a team with the name, if able.
    """
    if name not in get_teams():
        child_channels = category.text_channels
        channel_dict = {}
        for channel in child_channels:
            channel_dict[channel.name] = channel
        state[name] = Submarine(name, channel_dict, x, y)
        return True
    return False

MAX_SPEED = 4
GARBLE = 10
COMMS_COOLDOWN = 30

class Submarine():
    def __init__(self, name, channels, x, y):
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
        self.x = x
        self.y = y
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
    
    def add_system(self, systemname):
        """
        Adds a new system with max power 1.
        """
        if systemname in self.power:
            return False
        self.power[systemname] = 0
        self.power_max[systemname] = 1
        return True
    
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
    
    def modify_system(self, systemname, amount):
        """
        Upgrades or downgrades a system systemname by amount.
        Specify a negative amount to downgrade.
        """
        if not systemname in self.power_max:
            return False
        if self.power_max[systemname] + amount < 0:
            return False
        self.power_max[systemname] += amount
        self.power[systemname] = min(self.power[systemname], self.power_max[systemname])
        return True
    
    def modify_innate_system(self, systemname, amount):
        """
        Upgrades or downgrads an innate system systemname by amount.
        """
        if not systemname in self.power_max:
            return False
        current_innate = 0
        if systemname in self.innate_power:
            current_innate = self.innate_power[systemname]
        if current_innate + amount < 0:
            return False
        self.innate_power[systemname] = current_innate + amount
        return True
    
    def power_systems(self, systems):
        """
        Attempts to give power to the list of things to power `systems`.
        Will not change anything if it would mean you go over the power cap.
        If you name a system that doesn't exist, it will not apply the changes.
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
            else:
                return False
        self.scheduled_power = power_copy
        return True
    
    def unpower_systems(self, systems):
        """
        Attempts to remove power from all of the named systems in `systems`.
        If you specify a system that doesn't exist, it will fail.
        """
        power_copy = self.scheduled_power.copy()
        for system in systems:
            if system in power_copy:
                use = power_copy[system]
                use -= 1
                if use < 0:
                    return False
                power_copy[system] = use
            else:
                return False
        self.scheduled_power = power_copy
        return True

    def set_direction(self, direction):
        if direction in possible_directions():
            self.direction = direction
            return True
        return False

    def get_direction(self):
        return self.direction

    def set_position(self, x, y):
        if 0 <= x < X_LIMIT and 0 <= y < Y_LIMIT:
            self.x = x
            self.y = y
            return True
        return False

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
        if self.get_power("comms") == 0:
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

            # Don't print out information on systems that cannot be powered.
            if maxi + innate <= 0:
                continue

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
    
    def outward_broadcast(self, strength):
        """
        Shows information about this sub to others based on the strength of
        scanners. This strength is at least zero (comms power - distance).
        This strength allows for secrecy and limited information.
        TODO: Make this way more interesting. It's currently just sub name.
        Could add direction of motion, whether it's got cargo etc.
        """
        subname = ""
        if strength > 0: subname = f" {self.name}"
        return f"SUBMARINE{subname}"
    
    def scan(self):
        """
        Perform a scanner sweep of the local area.
        This finds all subs and objects in range, and returns them.
        """
        scanners_range = 2*self.get_power("scanners") - 2
        events = explore_submap(self.x, self.y, scanners_range)
        for subname in get_teams():
            if subname == self.name:
                continue
        
            sub = get_sub(subname)
            dist = diagonal_distance(self.x, self.y, sub.x, sub.y)
            if dist > scanners_range:
                continue

            event = sub.outward_broadcast(scanners_range - dist)
            direction = determine_direction(self.x, self.y, sub.x, sub.y)
            if direction is None:
                event = f"{event} in your current square!"
            else:
                event = f"{event} in direction {direction}!"
            events.append(event)
        shuffle(events)
        return events

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
        for subname in get_teams():
            if subname == self.name:
                continue

            sub = get_sub(subname)

            dist = diagonal_distance(self.x, self.y, sub.x, sub.y)
            garbled = self.garble(content, dist)
            if garbled is not None:
                await sub.send_message(f"**Message received from {self.name}**:\n`{garbled}`\n**END MESSAGE**")
        self.last_comms = now()
        return True
    
    def to_dict(self):
        """
        Converts this submarine instance to a serialisable dictionary.
        We just use self.__dict__ and then convert things as necessary.
        """
        dictionary = self.__dict__.copy()

        # self.channels: convert channels to their IDs.
        ids = {}
        for channel in self.channels:
            ids[channel] = self.channels[channel].id
        dictionary["channels"] = ids

        return dictionary
    
def sub_from_dict(dictionary, client):
    """
    Creates a submarine from a serialised dictionary.
    """
    newsub = Submarine("", {}, 0, 0)

    # self.channels: turn channel IDs into their objects.
    channels = dictionary["channels"]
    for channel in channels:
        channels[channel] = client.get_channel(channels[channel])

    newsub.__dict__ = dictionary
    return newsub

def state_to_dict():
    """
    Convert our state to a dictionary. This just runs to_dict on each member of
    the state.
    """
    state_dict = {}
    for subname in state:
        state_dict[subname] = state[subname].to_dict()
    return state_dict

def state_from_dict(dictionary, client):
    """
    Overwrites state with the state made by state_to_dict.
    """
    global state
    new_state = {}
    for subname in dictionary:
        new_state[subname] = sub_from_dict(dictionary[subname], client)
    state = new_state