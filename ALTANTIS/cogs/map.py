from discord.ext import commands

from ALTANTIS.utils.consts import CONTROL_ROLE
from ALTANTIS.utils.bot import perform_unsafe
from ALTANTIS.utils.actions import DiscordAction, OKAY_REACT, FAIL_REACT
from ALTANTIS.world.world import get_square, bury_treasure_at

class MapModification(commands.Cog):
    """
    Allows control to add and remove things from the map.
    """
    @commands.command(name="bury")
    @commands.has_role(CONTROL_ROLE)
    async def bury(self, ctx, treasure, x : int, y : int):
        """
        (CONTROL) Buries a treasure <treasure> at location (<x>, <y>).
        """
        await perform_unsafe(bury_treasure, ctx, treasure, x, y)

    @commands.command(name="add_attribute")
    @commands.has_role(CONTROL_ROLE)
    async def add_attribute(self, ctx, attribute, value, x : int, y : int):
        """
        (CONTROL) Add <attribute> to the square <x> <y> taking optional value <value>.
        """
        await perform_unsafe(add_attribute_to, ctx, x, y, attribute, value)

    @commands.command(name="remove_attribute")
    @commands.has_role(CONTROL_ROLE)
    async def remove_attribute(self, ctx, attribute, x : int, y : int):
        """
        (CONTROL) Remove <attribute> from the square <x> <y>.
        """
        await perform_unsafe(remove_attribute_from, ctx, x, y, attribute)

def bury_treasure(name : str, x : int, y : int) -> DiscordAction:
    if bury_treasure_at(name, (x, y)):
        return OKAY_REACT
    return FAIL_REACT

def add_attribute_to(x : int, y : int, attribute : str, value) -> DiscordAction:
    square = get_square(x, y)
    if square and square.add_attribute(attribute, value):
        return OKAY_REACT
    return FAIL_REACT

def remove_attribute_from(x : int, y : int, attribute : str) -> DiscordAction:
    square = get_square(x, y)
    if square and square.remove_attribute(attribute):
        return OKAY_REACT
    return FAIL_REACT
