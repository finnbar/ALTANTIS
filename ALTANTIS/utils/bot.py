from discord.ext import commands, tasks
from typing import Optional, List
import discord

from ALTANTIS.utils.consts import GAME_SPEED
from ALTANTIS.utils.actions import FAIL_REACT
from ALTANTIS.game import perform_timestep
from ALTANTIS.subs.state import get_subs

bot = commands.Bot(command_prefix="!")

@bot.check
async def globally_block_control_room(ctx):
    return ctx.message.channel.name != "control-room"

def get_team(channel : discord.TextChannel) -> Optional[str]:
    """
    Gets the name of the category channel of the channel the message was sent in.
    """
    category_channel = bot.get_channel(channel.category_id)
    if category_channel:
        team = category_channel.name.lower()
        if team in get_subs():
            return team
    return None

def to_lowercase_list(args) -> List[str]:
    alist = list(args)
    for i in range(len(alist)):
        if type(alist[i]) == str:
            alist[i] = alist[i].lower()
    return alist

# Main game loop
@tasks.loop(seconds=GAME_SPEED)
async def main_loop():
    await perform_timestep(main_loop.current_loop)

async def perform(fn, ctx, *args):
    """
    Checks if the main loop is running, and if so performs the function.
    """
    if main_loop.is_running():
        await perform_unsafe(fn, ctx, *args)
    else:
        await FAIL_REACT.do_status(ctx)

async def perform_unsafe(fn, ctx, *args):
    """
    Performs an action fn with *args and then performs the Discord action
    returned by fn using the context ctx.
    NOTE: This can run outside of the main loop, so should only be called
    if you are certain this will not be an issue.
    """
    lower_args = to_lowercase_list(args)
    status = fn(*lower_args)
    if status: await status.do_status(ctx)

async def perform_async(fn, ctx, *args):
    """
    Checks if the main loop is running, and if so performs the async function.
    """
    if main_loop.is_running():
        await perform_async_unsafe(fn, ctx, *args)
    else:
        await FAIL_REACT.do_status(ctx)

async def perform_async_unsafe(fn, ctx, *args):
    """
    Performs an async fn with *args and then the Discord action returned
    by fn using the context ctx.
    NOTE: This can run outside of the main loop, so should only be called
    if you are certain this will not be an issue.
    """
    lower_args = to_lowercase_list(args)
    status = await fn(*lower_args)
    if status: await status.do_status(ctx)