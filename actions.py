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

def register(name, channel):
    """
    Registers a team, setting them up with everything they could need.
    ONLY RUNNABLE BY CONTROL.
    """
    print("Registering", name)
    if add_team(name, channel):
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