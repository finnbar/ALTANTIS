"""
The main entry point for our bot, which tells Discord what commands the bot can
perform and how to do so.
"""

import os

from discord.ext import commands, tasks
from dotenv import load_dotenv

from actions import move, register, get_teams, set_power, print_map
from game import perform_timestep
from utils import OKAY_REACT

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CONTROL_ROLE = "CONTROL"
# The speed of the game, in _seconds_. Remember that most submarines will start
# moving every four "turns", so really you should think about 4*GAME_SPEED.
GAME_SPEED = 1

# SERIAL COMMANDS

bot = commands.Bot(command_prefix="!")

@bot.command(name="move")
async def player_move(ctx, direction):
    """
    `move direction` sets the direction of the user's submarine to the compass direction `direction`.
    """
    await perform(move, ctx, direction, get_team(ctx.author))

@bot.command(name="force_move")
@commands.has_role(CONTROL_ROLE)
async def control_move(ctx, team, direction):
    """
    `force_move team direction` moves `team`'s submarine in compass direction `direction`.
    """
    await perform(move, ctx, direction, team)

@bot.command(name="register")
@commands.has_role(CONTROL_ROLE)
async def register_team(ctx, name):
    """
    `register name` registers a team with the name `name` to the channel this
    message was received from.
    """
    await perform(register, ctx, name, ctx.message.channel)

@bot.command(name="on")
async def on(ctx):
    await perform(set_power, ctx, get_team(ctx.author), True)

@bot.command(name="off")
async def off(ctx):
    await perform(set_power, ctx, get_team(ctx.author), False)

@bot.command(name="map")
async def player_map(ctx):
    await perform(print_map, ctx, get_team(ctx.author))

@bot.command(name="mapall")
@commands.has_role(CONTROL_ROLE)
async def control_map(ctx):
    await perform(print_map, ctx, None)

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
    print(fn.__name__, args)
    status = fn(*args)
    if status: await status.do_status(ctx)

# LOOP HANDLING

@tasks.loop(seconds=GAME_SPEED)
async def main_loop():
    await perform_timestep(main_loop.current_loop)

@bot.command(name="startloop")
@commands.has_role(CONTROL_ROLE)
async def startloop(ctx):
    main_loop.start()
    await OKAY_REACT.do_status(ctx)

@bot.command(name="stoploop")
@commands.has_role(CONTROL_ROLE)
async def stoploop(ctx):
    main_loop.stop()
    await OKAY_REACT.do_status(ctx)

# ERROR HANDLING AND BOT STARTUP

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

print("ALTANTIS READY")
bot.run(TOKEN)
