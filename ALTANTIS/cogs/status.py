import json, httpx
from discord.ext import commands
from typing import List, Tuple, Dict, Any, Sequence

from ALTANTIS.utils.consts import CONTROL_ROLE, CAPTAIN, MAP_DOMAIN, MAP_TOKEN, X_LIMIT, Y_LIMIT, SCIENTIST, ENGINEER
from ALTANTIS.utils.bot import perform, perform_async, perform_unsafe, perform_async_unsafe, get_team, main_loop
from ALTANTIS.utils.actions import DiscordAction, Message, FAIL_REACT
from ALTANTIS.utils.text import list_to_and_separated
from ALTANTIS.utils.errors import SquareOutOfBoundsError
from ALTANTIS.world.world import in_world, get_square
from ALTANTIS.world.consts import MAX_OPTIONS
from ALTANTIS.npcs.npc import filtered_npcs
from ALTANTIS.subs.state import get_sub, get_sub_objects, filtered_teams, with_sub
from ALTANTIS.subs.sub import Submarine

class Status(commands.Cog):
    """
    All commands that get the status of your submarine and its local environment.
    """
    @commands.command()
    @commands.has_any_role(CAPTAIN, ENGINEER, SCIENTIST, CONTROL_ROLE)
    async def map(self, ctx):
        """
        Shows a map of the world, including your submarine!
        """
        await perform_async(print_map, ctx, get_team(ctx.channel))

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def mapall(self, ctx, *opts):
        """
        (CONTROL) Shows a map of the world, including all submarines.
        """
        if opts == ():
            await perform_async_unsafe(print_map, ctx, None, True, True)
        else:
            await perform_async_unsafe(print_map, ctx, None, list(opts), True)
    
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def zoom(self, ctx, x : int, y : int):
        """
        (CONTROL) Gives all details of a given square <x>, <y>.
        """
        await perform_unsafe(zoom_in, ctx, x, y, main_loop)

    @commands.command()
    @commands.has_any_role(CAPTAIN, ENGINEER, SCIENTIST, CONTROL_ROLE)
    async def status(self, ctx):
        """
        Reports the status of the submarine, including power and direction.
        """
        await perform(get_status, ctx, get_team(ctx.channel), main_loop)
    
    @commands.command()
    @commands.has_any_role(SCIENTIST, CONTROL_ROLE)
    async def scan(self, ctx):
        """
        Repeats the scan message sent at the start of the current tick.
        """
        await perform(get_scan, ctx, get_team(ctx.channel))

async def print_map(team: str, options: Sequence[str] = ("w", "d", "s", "a", "m", "e"), show_hidden: bool = False) -> DiscordAction:
    """
    Prints the map from the perspective of one submarine, or all if team is None.
    """
    subs = []
    max_options = ["w", "d", "s", "t", "n", "a", "j", "m", "e"]
    if options is True:
        options = MAX_OPTIONS
    options = list(filter(lambda v: v in max_options, options))
    if team is None:
        subs = get_sub_objects()
    else:
        sub = get_sub(team)
        if sub is None:
            return FAIL_REACT
        else:
            subs = [sub]
    map_string, map_arr = draw_map(subs, list(options), show_hidden)
    map_json = json.dumps(map_arr)
    async with httpx.AsyncClient() as client:
        url = MAP_DOMAIN+"/api/map/"
        res = await client.post(url, data={"map": map_string, "key": MAP_TOKEN, "names": map_json})
        if res.status_code == 200:
            final_url = MAP_DOMAIN+res.json()['url']
            return Message(f"The map is visible here: {final_url}")
    return FAIL_REACT

def draw_map(subs: List[Submarine], to_show: List[str], show_hidden: bool) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Draws an ASCII version of the map.
    Also returns a JSON of additional information.
    `subs` is a list of submarines, which are marked 0-9 on the map.
    """
    SUB_CHARS = ['1','2','3','4','5','6','7','8','9','0','-','+','=']
    map_string = ""
    map_json = []
    for y in range(Y_LIMIT):
        row = ""
        for x in range(X_LIMIT):
            square = get_square(x, y)
            if square is None:
                raise SquareOutOfBoundsError((x, y))
            tile_char = square.to_char(to_show, show_hidden, list(map(lambda sub: sub._name, subs)))
            tile_name = square.map_name(to_show, show_hidden, list(map(lambda sub: sub._name, subs)))
            if tile_name is not None:
                map_json.append({"x": x, "y": y, "name": tile_name})
            if "n" in to_show:
                npcs_in_square = filtered_npcs(lambda n: n.x == x and n.y == y)
                if len(npcs_in_square) > 0:
                    tile_char = "N"
                    npcs_str = list_to_and_separated(list(map(lambda n: n.name(), npcs_in_square)))
                    map_json.append({"x": x, "y": y, "name": npcs_str})
            for i in range(len(subs)):
                (sx, sy) = subs[i].movement.get_position()
                if sx == x and sy == y:
                    tile_char = SUB_CHARS[i]
                    map_json.append({"x": x, "y": y, "name": subs[i].name()})
            row += tile_char
        map_string += row + "\n"
    return map_string, map_json

def zoom_in(x : int, y : int, loop) -> DiscordAction:
    if in_world(x, y):
        report = f"Report for square **({x}, {y})**\n"
        # since in_world => get_square : Cell (not None)
        report += get_square(x, y).square_status() + "\n\n" # type: ignore
        # See if any subs are here, and if so print their status.
        subs_in_square = filtered_teams(lambda sub: sub.movement.x == x and sub.movement.y == y)
        for sub in subs_in_square:
            report += sub.status_message(loop) + "\n\n"
        return Message(report)
    return Message("Chosen square is outside the world boundaries!")

def get_status(team : str, loop) -> DiscordAction:
    def do_status(sub):
        status_message = sub.status_message(loop)
        return Message(status_message)
    return with_sub(team, do_status, FAIL_REACT)

def get_scan(team : str) -> DiscordAction:
    def do_scan(sub):
        message = sub.scan.previous_scan()
        if message != "":
            return Message(message)
        return Message("No scan done yet!")
    return with_sub(team, do_scan, FAIL_REACT)
