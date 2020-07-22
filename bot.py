import os

from discord.ext import commands
from dotenv import load_dotenv

from actions import move, register, get_teams

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CONTROL_ROLE = "CONTROL"

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
    `register name` registers a team with the name `name`.
    """
    await perform(register, ctx, name)

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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

print("ALTANTIS READY")
bot.run(TOKEN)

