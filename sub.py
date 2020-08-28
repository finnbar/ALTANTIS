"""
Manages individual submarines, including their subsystems.
"""

from consts import GAME_SPEED
from utils import Entity, list_to_and_separated, to_titled_list, create_or_return_role
from world import get_square

from discord import File as DFile
from random import choice, random, shuffle
import math, datetime

MAX_SPEED = 4

subsystems = ["power", "comms", "movement", "puzzles", "scan", "inventory", "weapons", "upgrades"]

class Submarine(Entity):
    def __init__(self, name, channels, x, y):
        # To avoid circular dependencies.
        # The one dependency is that Scan and Comms need the list of available
        # subs, but that needs this class, which needs Scan and Comms.
        from power import PowerManager
        from scan import ScanSystem
        from comms import CommsSystem
        from puzzles import EngineeringPuzzles
        from movement import MovementControls
        from inventory import Inventory
        from weapons import Weaponry
        from upgrades import Upgrades

        self.name = name
        self.channels = channels
        self.power = PowerManager(self)
        self.comms = CommsSystem(self)
        self.movement = MovementControls(self, x, y)
        self.puzzles = EngineeringPuzzles(self)
        self.scan = ScanSystem(self)
        self.inventory = Inventory(self)
        self.weapons = Weaponry(self)
        self.upgrades = Upgrades(self)

    def status_message(self, loop):
        message = (
            f"Status for **{self.name.title()}**\n"
            f"------------------------------------\n\n"
        )
        
        message += self.movement.status(loop)
        message += self.power.status()
        message += self.inventory.status()
        message += self.weapons.status()
        message += self.upgrades.upgrade_status()

        return message + "\nNo more to report."
    
    async def send_message(self, content, channel, filename=None):
        fp = None
        if filename:
            fp = DFile(filename)
        if self.channels[channel]:
            await self.channels[channel].send(content, file=fp)
            return True
        return False
    
    async def send_to_all(self, content):
        for channel in self.channels:
            await self.channels[channel].send(content)
        return True
    
    def damage(self, amount):
        self.power.damage(amount)
    
    async def docking(self, guild):
        """
        Finds all members of this sub (by finding those with the relevant role)
        and gives them the docked-at-{base_name} role.
        This is undone when the sub is activated.
        """
        def has_subname_role(member):
            roles = member.roles
            role_names = map(lambda r: r.name, roles)
            return self.name in role_names

        (x, y) = self.movement.get_position()
        square = get_square(x, y)
        location = square.docked_at()
        if location:
            role_name = f"docked-at-{location.lower()}"
            in_sub = filter(has_subname_role, guild.members)
            role = await create_or_return_role(guild, role_name)
            for member in in_sub:
                await member.add_roles(role)
            await self.send_to_all(f"Team has left submarine at **{location.title()}**. You will be automatically returned when the submarine is turned back on.")
            return "Successfully left the submarine."
        return "Unable to leave the submarine."
    
    async def undocking(self, guild):
        """
        Finds all members of this sub (by finding those with the relevant role)
        and then removes any docked-at-{x} role.
        Call this when a sub is activated.
        """
        def has_subname_role(member):
            roles = member.roles
            role_names = map(lambda r: r.name, roles)
            return self.name in role_names

        in_sub = filter(has_subname_role, guild.members)
        for member in in_sub:
            roles_to_remove = []
            for role in member.roles:
                if str.startswith(role.name, "docked-at-"):
                    roles_to_remove.append(role)
            await member.remove_roles(*roles_to_remove)
    
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

        # Each subsystem needs to be turned into a dict, and then have its
        # parent reference removed.
        for subsystem in subsystems:
            dictionary[subsystem] = self.__getattribute__(subsystem).__dict__.copy()
            dictionary[subsystem]["sub"] = None
        
        # Delete trade progress.
        dictionary["inventory"]["trading_partner"] = None
        dictionary["inventory"]["offer"] = {}
        dictionary["inventory"]["accepting"] = False
        dictionary["inventory"]["my_turn"] = False

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
    
    # Subsystems need to be remade into their classes.
    for subsystem in subsystems:
        # First, set the self-reference.
        # newsub.__getattribute__... is the sub link generated by the
        # constructor of Submarine.
        dictionary[subsystem]["sub"] = newsub.__getattribute__(subsystem).sub
        # Then, load in the dictionary (initialising the child class).
        newsub.__getattribute__(subsystem).__dict__ = dictionary[subsystem]
        # Finally, modify the dictionary to contain the actual instantiated
        # subsystem as opposed to the dictionary form.
        dictionary[subsystem] = newsub.__getattribute__(subsystem)

    newsub.__dict__ = dictionary
    return newsub