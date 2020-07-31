"""
The backend for all Discord actions, which allow players to control their sub.
"""

from utils import React, Message, OKAY_REACT, FAIL_REACT
from sub import get_teams, get_sub, add_team
from world import ascii_map

direction_emoji = {"N": "⬆", "E": "➡", "S": "⬇",
                   "W": "⬅", "NE": "↗",
                   "NW": "↖", "SE": "↘",
                   "SW": "↙"}

def move(direction, team):
    """
    Records the team's direction.
    We then react to the message accordingly.
    """
    print("Setting direction of", team, "to", direction)
    if team in get_teams():
        # Store the move and return the correct emoji.
        if get_sub(team).set_direction(direction):
            return React(direction_emoji[direction])
    return FAIL_REACT

async def register(category):
    """
    Registers a team, setting them up with everything they could need.
    Requires a category with the required subchannels.
    ONLY RUNNABLE BY CONTROL.
    """
    print("Registering", category.name)
    if add_team(category.name, category):
        sub = get_sub(category.name)
        if sub:
            await sub.send_to_all(f"Channel registered for sub **{category.name}**.")
            return OKAY_REACT
    return FAIL_REACT

def set_activation(team, value):
    """
    Sets the submarine's power to `value`.
    """
    sub = get_sub(team)
    if sub:
        print("Setting power of", team, "to", value)
        if sub.activated() == value:
            return Message(f"{team} unchanged.")
        sub.activate(value)
        if sub.activated():
            return Message(f"{team} is **ON** and running! Current direction: **{sub.get_direction()}**.")
        return Message(f"{team} is **OFF** and halted!")
    return FAIL_REACT

def power_systems(team, systems):
    """
    Powers `systems` of the submarine `team` if able.
    """
    sub = get_sub(team)
    if sub:
        print("Applying power increases of", team, "to", systems)
        if sub.power_systems(systems):
            return Message(f"Scheduled power increase of systems {systems} for {team}!")
        return Message(f"Could not power all of {systems} so did not change anything.")
    return FAIL_REACT

def unpower_systems(team, systems):
    """
    Unpowers `systems` of the submarine `team` if able.
    """
    sub = get_sub(team)
    if sub:
        print("Applying power decreases of", team, "to", systems)
        if sub.unpower_systems(systems):
            return Message(f"Scheduled power decrease of systems {systems} for {team}!")
        return Message(f"Could not unpower all of {systems} so did not change anything.")
    return FAIL_REACT

def print_map(team):
    """
    Prints the map from the perspective of one submarine, or all if team is None.
    """
    subs = []
    if team is None:
        subs = [get_sub(sub) for sub in get_teams()]
    else:
        sub = get_sub(team)
        if sub is None:
            return FAIL_REACT
        subs = [sub]
    print("Printing map for", subs)
    formatted = f"```\n"
    map_string = ascii_map(subs)
    formatted += map_string + "\n```\n"
    subs_string = "With submarines: "
    for i in range(len(subs)):
        subs_string += f"{i}: {subs[i].name}, "
    formatted += subs_string[:-2]
    return Message(formatted)

def get_status(team):
    sub = get_sub(team)
    if sub:
        status_message = sub.status_message()
        return Message(status_message)
    return FAIL_REACT

async def broadcast(team, message):
    sub = get_sub(team)
    if sub and sub.activated():
        print(f"Going to broadcast {message}!")
        result = await sub.broadcast(message)
        if result:
            return OKAY_REACT
        else:
            return Message("The radio is still in use! (It has a thirty second cooldown.)")
    return FAIL_REACT

async def deal_damage(team, amount, reason):
    sub = get_sub(team)
    if sub:
        damage_message = sub.damage(amount)
        if reason: await sub.send_to_all(reason)
        await sub.send_to_all(damage_message)
        return OKAY_REACT
    return FAIL_REACT

async def shout_at_team(team, message):
    sub = get_sub(team)
    if sub:
        await sub.send_to_all(message)
        return OKAY_REACT
    return FAIL_REACT

async def upgrade_sub(team, amount):
    sub = get_sub(team)
    if sub:
        sub.power_cap += amount
        await sub.send_message(f"Submarine {team} was upgraded! Power cap increased by {amount}.", "engineer")
        return OKAY_REACT
    return FAIL_REACT