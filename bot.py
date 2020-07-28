"""
The main entry point for our bot, which tells Discord what commands the bot can
perform and how to do so.
"""

import os

from discord.ext import commands, tasks
from dotenv import load_dotenv

from actions import *
from game import perform_timestep
from utils import OKAY_REACT

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CONTROL_ROLE = "CONTROL"
# The speed of the game, in _seconds_. Remember that most submarines will start
# moving every four "turns", so really you should think about 4*GAME_SPEED.
GAME_SPEED = 5

# GENERAL COMMANDS

# TODO: CREATE COGS FOR THE DIFFERENT SETS OF COMMANDS (e.g. one for movement, one for power etc)

bot = commands.Bot(command_prefix="!")

@bot.command(name="move")
async def player_move(ctx, direction):
    """
    Sets the direction of your submarine to <direction>.
    """
    await perform(move, ctx, direction, get_team(ctx.author))

@bot.command(name="force_move")
@commands.has_role(CONTROL_ROLE)
async def control_move(ctx, team, direction):
    """
    (CONTROL) Forces <team>'s submarine to a given direction. Does not inform them.
    """
    await perform(move, ctx, direction, team)

@bot.command(name="register")
@commands.has_role(CONTROL_ROLE)
async def register_team(ctx, name):
    """
    (CONTROL) Registers a new team with <name> to the channel this was called in.
    This means that all messages sent by this submarine will be sent to this channel.
    """
    await perform(register, ctx, name, ctx.message.channel)

@bot.command(name="activate")
async def on(ctx):
    """
    Activates your submarine, allowing it to move and do actions in real-time.
    """
    await perform(set_activation, ctx, get_team(ctx.author), True)

@bot.command(name="deactivate")
async def off(ctx):
    """
    Deactivates your submarine, stopping it from moving and performing actions.
    Needed for docking.
    """
    await perform(set_activation, ctx, get_team(ctx.author), False)

@bot.command(name="map")
async def player_map(ctx):
    """
    Shows a map of the world, including your submarine!
    """
    await perform(print_map, ctx, get_team(ctx.author))

@bot.command(name="mapall")
@commands.has_role(CONTROL_ROLE)
async def control_map(ctx):
    """
    (CONTROL) Shows a map of the world, including all submarines.
    """
    await perform(print_map, ctx, None)

@bot.command(name="power")
async def power(ctx, *systems):
    """
    Gives one power to all of <systems> (any number of systems, can repeat).
    Fails if this would overload the power.
    """
    await perform(power_systems, ctx, get_team(ctx.author), list(systems))

@bot.command(name="force_power")
@commands.has_role(CONTROL_ROLE)
async def control_power(ctx, team, *systems):
    """
    (CONTROL) Forces <team> to give one power to all of <systems>.
    """
    await perform(power_systems, ctx, team, list(systems))

@bot.command(name="unpower")
async def unpower(ctx, *systems):
    """
    Removes one power from all of <systems> (any number of systems, can repeat).
    Fails if this would reduce a system's power below zero.
    """
    await perform(unpower_systems, ctx, get_team(ctx.author), list(systems))

@bot.command(name="force_unpower")
@commands.has_role(CONTROL_ROLE)
async def control_unpower(ctx, team, *systems):
    """
    (CONTROL) Forces <team> to remove one power from all of <systems>.
    """
    await perform(unpower_systems, ctx, team, list(systems))

@bot.command(name="status")
async def status(ctx):
    """
    Reports the status of the submarine, including power and direction.
    """
    await perform(get_status, ctx, get_team(ctx.author))

# LOOP HANDLING

@tasks.loop(seconds=GAME_SPEED)
async def main_loop():
    await perform_timestep(main_loop.current_loop)

@bot.command(name="startloop")
@commands.has_role(CONTROL_ROLE)
async def startloop(ctx):
    """
    (CONTROL) Starts the main game loop, so that all submarines can act if activated.
    You should use this at the start of the game, and then only again if you have to pause the game for some reason.
    """
    main_loop.start()
    await OKAY_REACT.do_status(ctx)

@bot.command(name="stoploop")
@commands.has_role(CONTROL_ROLE)
async def stoploop(ctx):
    """
    (CONTROL) Stops the main game loop, effectively pausing the game.
    You should only use this at the end of the game, or if you need to pause the game for some reason.
    """
    main_loop.stop()
    await OKAY_REACT.do_status(ctx)

# USEFUL CONTROL FUNCTIONALITY

@bot.command(name="control_message")
@commands.has_role(CONTROL_ROLE)
async def message_team(ctx, team, message):
    """
    (CONTROL) Sends to <team> the message <message>, regardless of distance.
    """
    await perform_async(shout_at_team, ctx, team, message)

@bot.command(name="damage")
@commands.has_role(CONTROL_ROLE)
async def damage(ctx, team, amount : int, reason=""):
    """
    (CONTROL) Forces <team> to take <amount> damage. You can optionally specify a <reason> which will be messaged to them before.
    """
    await perform_async(deal_damage, ctx, team, amount, reason)

@bot.command(name="upgrade")
@commands.has_role(CONTROL_ROLE)
async def upgrade(ctx, team, amount : int):
    """
    (CONTROL) Upgrades <team>'s reactor by <amount>.
    You can specify a negative number, but this will not check that the resulting state makes sense (that is, the team is not using more power than they have) - in general you should use !damage instead.
    """
    await perform_async(upgrade_sub, ctx, team, amount)

# HELPER FUNCTIONS

def get_team(author):
    """
    Gets the first role that has a submarine associated with it, or None.
    """
    roles = list(map(lambda x: x.name, author.roles))
    for team in get_teams():
        if team in roles:
            return team
    return None

async def perform(fn, ctx, *args):
    """
    Performs an action fn with *args and then performs the Discord action
    returned by fn using the context ctx.
    """
    status = fn(*args)
    if status: await status.do_status(ctx)

async def perform_async(fn, ctx, *args):
    """
    Performs an async fn with *args and then the Discord action returned
    by fn using the context ctx.
    """
    status = await fn(*args)
    if status: await status.do_status(ctx)

# ERROR HANDLING AND BOT STARTUP

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

print("ALTANTIS READY")
bot.run(TOKEN)
