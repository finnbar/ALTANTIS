import discord
from discord.ext import commands

from ALTANTIS.utils.consts import CONTROL_ROLE, CAPTAIN, direction_emoji
from ALTANTIS.utils.bot import perform, perform_async, perform_unsafe, get_team
from ALTANTIS.utils.actions import DiscordAction, Message, React, OKAY_REACT, FAIL_REACT
from ALTANTIS.subs.state import with_sub, with_sub_async

class Movement(commands.Cog):
    """
    All commands that allow you to move the submarine.
    """
    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def setdir(self, ctx, direction):
        """
        Sets the direction of your submarine to <direction>.
        """
        await perform(move, ctx, direction, get_team(ctx.channel))

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def teleport(self, ctx, x : int, y : int):
        """
        (CONTROL) Teleports the submarine of the team of the channel to a given (<x>, <y>). Does not inform them.
        Also does _not_ check if the position is blocked, but does check if it's a valid point in the world.
        """
        await perform_unsafe(teleport, ctx, get_team(ctx.channel), x, y)

    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def activate(self, ctx):
        """
        Activates your submarine, allowing it to move and do actions in real-time.
        """
        await perform_async(set_activation, ctx, get_team(ctx.channel), ctx.guild, True)

    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def deactivate(self, ctx):
        """
        Deactivates your submarine, stopping it from moving and performing actions.
        Needed for docking.
        """
        await perform_async(set_activation, ctx, get_team(ctx.channel), ctx.guild, False)
    
    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def exit_sub(self, ctx):
        """
        Allows crew to leave a sub. Call only while you are docked.
        """
        await perform_async(exit_submarine, ctx, get_team(ctx.channel), ctx.guild)

def move(direction : str, subname : str) -> DiscordAction:
    """
    Records the team's direction.
    We then react to the message accordingly.
    """
    def do_move(sub):
        # Store the move and return the correct emoji.
        if sub.movement.set_direction(direction):
            return React(direction_emoji[direction])
        return FAIL_REACT
    return with_sub(subname, do_move, FAIL_REACT)

def teleport(subname : str, x : int, y : int) -> DiscordAction:
    """
    Teleports team to (x,y), checking if the space is in the world.
    """
    def do_teleport(sub):
        if sub.movement.set_position(x, y):
            return OKAY_REACT
        return FAIL_REACT
    return with_sub(subname, do_teleport, FAIL_REACT)

async def set_activation(team : str, guild : discord.Guild, value : bool) -> DiscordAction:
    """
    Sets the submarine's power to `value`.
    """
    async def do_set(sub):
        if sub.power.activated() == value:
            return Message(f"{team.title()} activation unchanged.")
        sub.power.activate(value)
        if sub.power.activated():
            await sub.undocking(guild)
            await sub.send_to_all(f"{team.title()} is **ON** and running! Current direction: **{sub.movement.get_direction().upper()}**.")
            return OKAY_REACT
        await sub.send_to_all(f"{team.title()} is **OFF** and halted!")
        return OKAY_REACT
    return await with_sub_async(team, do_set, FAIL_REACT)

async def exit_submarine(team : str, guild : discord.Guild) -> DiscordAction:
    async def do_exit(sub):
        message = await sub.docking(guild)
        return Message(message)
    return await with_sub_async(team, do_exit, FAIL_REACT)