import json, httpx
from discord.ext import commands
from typing import List, Tuple, Dict, Any, Sequence

from ALTANTIS.utils.consts import CONTROL_ROLE, CAPTAIN, MAP_DOMAIN, MAP_TOKEN, X_LIMIT, Y_LIMIT
from ALTANTIS.utils.bot import perform, perform_async, perform_unsafe, perform_async_unsafe, get_team, main_loop
from ALTANTIS.utils.actions import DiscordAction, Message, FAIL_REACT
from ALTANTIS.utils.text import list_to_and_separated
from ALTANTIS.world.world import in_world, get_square
from ALTANTIS.npcs.npc import filtered_npcs, get_npc
from ALTANTIS.subs.state import get_sub, get_sub_objects, filtered_teams, with_sub
from ALTANTIS.subs.sub import Submarine

class Status(commands.Cog):
    """
    All commands that get the status of your submarine and its local environment.
    """
    @commands.command(name="map")
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def player_map(self, ctx):
        """
        Shows a map of the world, including your submarine!
        """
        await perform_async(print_map, ctx, get_team(ctx.channel))

    @commands.command(name="mapall")
    @commands.has_role(CONTROL_ROLE)
    async def control_map(self, ctx, *opts):
        """
        (CONTROL) Shows a map of the world, including all submarines.
        """
        if opts == ():
            await perform_async_unsafe(print_map, ctx, None, True)
        else:
            await perform_async_unsafe(print_map, ctx, None, list(opts))
    
    @commands.command(name="zoom")
    @commands.has_role(CONTROL_ROLE)
    async def zoom(self, ctx, x : int, y : int):
        """
        (CONTROL) Gives all details of a given square <x>, <y>.
        """
        await perform_unsafe(zoom_in, ctx, x, y, main_loop)

    @commands.command(name="status")
    async def status(self, ctx):
        """
        Reports the status of the submarine, including power and direction.
        """
        await perform(get_status, ctx, get_team(ctx.channel), main_loop)
    
    @commands.command(name="scan")
    async def scan(self, ctx):
        """
        Repeats the scan message sent at the start of the current tick.
        """
        await perform(get_scan, ctx, get_team(ctx.channel))

async def print_map(team : str, options:Sequence[str] = ("w", "d", "s")) -> DiscordAction:
    """
    Prints the map from the perspective of one submarine, or all if team is None.
    """
    subs = []
    max_options = ["w", "d", "s", "t", "n", "r", "j", "m", "e"]
    if options is True:
        options = max_options
    options = list(filter(lambda v: v in max_options, options))
    if team is None:
        subs = get_sub_objects()
    else:
        sub = get_sub(team)
        if sub is None:
            return FAIL_REACT
        else:
            subs = [sub]
    map_string, map_arr = draw_map(subs, options)
    map_json = json.dumps(map_arr)
    async with httpx.AsyncClient() as client:
        url = MAP_DOMAIN+"/api/map/"
        res = await client.post(url, data={"map": map_string, "key": MAP_TOKEN, "names": map_json})
        if res.status_code == 200:
            final_url = MAP_DOMAIN+res.json()['url']
            return Message(f"The map is visible here: {final_url}")
    return FAIL_REACT

def draw_map(subs : List[Submarine], to_show : List[str]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Draws an ASCII version of the map.
    Also returns a JSON of additional information.
    `subs` is a list of submarines, which are marked 0-9 on the map.
    """
    map_string = ""
    map_json = []
    for y in range(Y_LIMIT):
        row = ""
        for x in range(X_LIMIT):
            square = get_square(x, y)
            tile_char = square.to_char(to_show)
            tile_name = square.map_name(to_show)
            if "n" in to_show:
                npcs_in_square = filtered_npcs(lambda n: n.x == x and n.y == y)
                if len(npcs_in_square) > 0:
                    tile_char = "N"
                    tile_name = list_to_and_separated(list(map(lambda n: get_npc(n).name(), npcs_in_square)))
            for i in range(len(subs)):
                (sx, sy) = subs[i].movement.get_position()
                if sx == x and sy == y:
                    tile_char = str(i)
                    tile_name = subs[i].name()
            row += tile_char
            if tile_name is not None:
                map_json.append({"x": x, "y": y, "name": tile_name})
        map_string += row + "\n"
    return map_string, map_json

def zoom_in(x : int, y : int, loop) -> DiscordAction:
    if in_world(x, y):
        report = f"Report for square **({x}, {y})**\n"
        report += get_square(x, y).square_status() + "\n\n"
        # See if any subs are here, and if so print their status.
        subs_in_square = filtered_teams(lambda sub: sub.movement.x == x and sub.movement.y == y)
        for subname in subs_in_square:
            sub = get_sub(subname)
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
        return Message(sub.scan.previous_scan())
    return with_sub(team, do_scan, FAIL_REACT)