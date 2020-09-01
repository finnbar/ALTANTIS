from discord.ext import commands
from typing import Optional

from ALTANTIS.utils.consts import CONTROL_ROLE, CAPTAIN
from ALTANTIS.utils.bot import perform, perform_async, perform_unsafe, perform_async_unsafe, get_team
from ALTANTIS.utils.actions import DiscordAction, Message, OKAY_REACT, FAIL_REACT, to_react
from ALTANTIS.world.extras import explode
from ALTANTIS.subs.state import with_sub_async, remove_team

class DangerZone(commands.Cog):
    """
    DO NOT USE COMMANDS HERE UNLESS YOU ARE ABSOLUTELY CERTAIN.
    """
    @commands.command(name="death")
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def death(self, ctx, subname):
        """
        Kills your submarine. This isn't a joke. Must be called with your submarine's full name.
        """
        await perform_async(kill_sub, ctx, get_team(ctx.channel), subname)

    @commands.command(name="kill_team")
    @commands.has_role(CONTROL_ROLE)
    async def kill_team(self, ctx, team):
        """
        (CONTROL) Kills the team <team>, removing any trace of their existence bar their channels.
        This deletes their Submarine object, so all game progress is erased.
        Do NOT use this unless you are absolutely sure. (There's a reason you have to specify the team name, and that's to make it actively harder to call this command.)
        """
        await perform_unsafe(delete_team, ctx, team)
    
    @commands.command(name="explode")
    @commands.has_role(CONTROL_ROLE)
    async def explode(self, ctx, x : int, y : int, amount : int):
        """
        (CONTROL) Causes an explosion in (x, y), dealing amount damage to the central square.
        It also deals amount-1 damage to the surrounding squares, amount-2 to those surrounding and so on.
        DO NOT RUN !explode x y 40 OR ANY SIMILARLY LARGE AMOUNT OF DAMAGE AS THAT WILL KILL EVERYTHING.
        """
        await perform_async_unsafe(explode_square, ctx, x, y, amount)

async def kill_sub(team : str, verify : str) -> DiscordAction:
    async def do_kill(sub):
        if sub._name == verify:
            sub.damage(sub.power.total_power)
            await sub.send_to_all("Submarine took catastrophic damage and will die on next game loop.")
            return OKAY_REACT
    return await with_sub_async(team, do_kill, FAIL_REACT)

def delete_team(team : str) -> DiscordAction:
    # DELETES THE TEAM IN QUESTION. DO NOT DO THIS UNLESS YOU ARE ABSOLUTELY CERTAIN.
    return to_react(remove_team(team))

async def explode_square(x : int, y : int, power : int) -> DiscordAction:
    await explode((x, y), power)
    return OKAY_REACT