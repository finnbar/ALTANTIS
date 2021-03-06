from discord.ext import commands

from ALTANTIS.utils.consts import CONTROL_ROLE, CAPTAIN
from ALTANTIS.utils.bot import perform, perform_async, perform_unsafe, perform_async_unsafe, get_team
from ALTANTIS.utils.actions import DiscordAction, Message, OKAY_REACT, FAIL_REACT
from ALTANTIS.subs.state import with_sub_async

class Comms(commands.Cog):
    """
    Commands for communicating with your fellow subs.
    """
    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def broadcast(self, ctx, *message):
        """
        Broadcasts a <message> to all in range. Requires the sub to be activated.
        Note that this can be provided in quotes or not - we consume all arguments.
        """
        await perform_async(broadcast, ctx, get_team(ctx.channel), " ".join(message))
    
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def control_message(self, ctx, message):
        """
        (CONTROL) Sends to this team the message <message>, regardless of distance.
        """
        await perform_async_unsafe(shout_at_team, ctx, get_team(ctx.channel), message)

async def shout_at_team(team : str, message : str) -> DiscordAction:
    async def do_shout(sub):
        await sub.send_to_all(message)
        return OKAY_REACT
    return await with_sub_async(team, do_shout, FAIL_REACT)

async def broadcast(team : str, message : str) -> DiscordAction:
    async def do_broadcast(sub):
        if sub.power.activated():
            return Message(await sub.comms.broadcast(message))
        return FAIL_REACT
    return await with_sub_async(team, do_broadcast, FAIL_REACT)