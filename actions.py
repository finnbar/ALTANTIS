"""
The backend for all Discord actions, which allow players to control their sub.
"""

from utils import React, OKAY_REACT, FAIL_REACT
from state import get_teams, get_sub, add_team

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
