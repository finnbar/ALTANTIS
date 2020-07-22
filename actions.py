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

def move(direction, team):
    """
    Records the team's direction.
    We then react to the message accordingly.
    """
    print("Setting direction of", team, "to", direction)
    if team in state.keys():
        # Store the move and return the correct emoji.
        return state[team].set_direction(direction)
    return None

def register(name):
    """
    Registers a team, setting them up with everything they could need.
    ONLY RUNNABLE BY CONTROL.
    """
    print("Registering", name)
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
