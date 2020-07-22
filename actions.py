from utils import React

direction_emoji = {"N": "⬆", "E": "➡", "S": "⬇",
                   "W": "⬅", "NE": "↗",
                   "NW": "↖", "SE": "↘",
                   "SW": "↙"}
OKAY_REACT = "☑"

# A state dictionary, containing every ship's state.
state = {}

def get_teams():
    return state.keys()

def move(args, team):
    """
    Takes arguments and a team identifier, and records the team's current
    direction from args as that direction.
    We then react to the message accordingly.
    """
    direction = args[0]
    if team in state.keys():
        # Store the move and return the correct emoji.
        return state[team].set_direction(direction)
    return None

def register(name, _):
    """
    Registers a team, setting them up with everything they could need.
    ONLY RUNNABLE BY CONTROL.
    """
    state[name] = Submarine(name)
    return React(OKAY_REACT)

class Submarine():
    def __init__(self, name):
        self.name = name
        self.direction = "N"
        self.speed = 1

    def set_direction(self, direction):
        if direction in direction_emoji.keys():
            self.direction = direction
            return React(direction_emoji[direction])
        return None
