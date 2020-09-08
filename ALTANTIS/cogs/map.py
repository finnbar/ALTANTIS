from discord.ext.commands.core import command
from ALTANTIS.world.consts import WEATHER
from discord.ext import commands

from ALTANTIS.utils.consts import CONTROL_ROLE
from ALTANTIS.utils.bot import perform_unsafe
from ALTANTIS.utils.actions import DiscordAction, OKAY_REACT, FAIL_REACT
from ALTANTIS.world.world import get_square, bury_treasure_at
from ALTANTIS.world.consts import WEATHER

class MapModification(commands.Cog):
    """
    Allows control to add and remove things from the map.
    """
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def bury(self, ctx, treasure, x : int, y : int):
        """
        (CONTROL) Buries a treasure <treasure> at location (<x>, <y>).
        """
        await perform_unsafe(bury_treasure, ctx, treasure, x, y)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def add_attribute(self, ctx, attribute, value, x : int, y : int):
        """
        (CONTROL) Add <attribute> to the square <x> <y> taking optional value <value>.
        """
        await perform_unsafe(add_attribute_to, ctx, x, y, attribute, value)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def remove_attribute(self, ctx, attribute, x : int, y : int):
        """
        (CONTROL) Remove <attribute> from the square <x> <y>.
        """
        await perform_unsafe(remove_attribute_from, ctx, x, y, attribute)
    
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def mass_weather(self, ctx, preset):
        """
        (CONTROL) Loads a preset file from "/weather" and applies that weather to the entire map.
        Do not do this unless you know what you're doing!
        """
        await perform_unsafe(mass_weather, ctx, preset)

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

def mass_weather(preset : str):
    CHAR_TO_WEATHER = {WEATHER[k].lower(): k.lower() for k in WEATHER}
    try:
        with open(f"weather/{preset}.txt") as f:
            # First, try to load the file.
            map_arr = f.readlines()
            for y in range(len(map_arr)):
                for x in range(len(map_arr[y])):
                    # Then for each square, set the weather accordingly.
                    sq = get_square(x, y)
                    if sq is not None:
                        char = map_arr[y][x].lower()
                        if char in CHAR_TO_WEATHER:
                            sq.attributes["weather"] = CHAR_TO_WEATHER[char]
        return OKAY_REACT
    except:
        return FAIL_REACT