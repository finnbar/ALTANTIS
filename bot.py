import os

import discord
from dotenv import load_dotenv

from actions import move, register, get_teams

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CONTROL_ROLE = "CONTROL"

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user or message.content[0] != "!":
        return
    if to_run = get_command(message):
        # status is either None or something to do.
        status = to_run(get_team(message))

def get_command(message):
    """
    Get the command (!xxx ...) from a message's content.
    """
    content = message.content
    commands = {"!move": control_acts(move),
                "!register": control_only(register)}
    for command in commands:
        if args = get_arguments(command, content):
            return lambda x: commands[command](args, x)
    return None

def get_arguments(prefix, content):
    parts = content.split(" ")
    if parts[0] == prefix:
        return parts[1:]
    return None

def control_only(fn):
    """
    control_only() functions can only be run by members of team CONTROL_ROLE.
    As such, we check that the team running them is CONTROL_ROLE.
    On failure, we return None.
    """
    def safe(args, x):
        if x == CONTROL_ROLE:
            return fn(args, x)
        return None
    return safe

def control_acts(fn):
    """
    control_acts() functions allow members of team CONTROL_ROLE to pretend to
    be another team. These functions, when run by a member of control, consider
    the last argument of those functions to be the team running them.
    """
    def pretend(args, x):
        if x == CONTROL_ROLE:
            return fn(args[:-1], args[-1])
        return fn(args, x)
    return pretend

def get_team(message):
    """
    Gets the first role that has a submarine associated with it, or None.
    """
    roles = message.author.roles
    for team in get_teams():
        if team in roles:
            return team
    return None

client.run(TOKEN)

