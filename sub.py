"""
Manages the submarines as a whole and the individual submarines within it.
"""

from world import move_on_map, possible_directions

# State dictionary, filled with submarines.
state = {}

def get_teams():
    """
    Gets all possible teams.
    """
    return state.keys()

def get_sub(name):
    """
    Gets the Submarine object associated with `name`.
    """
    return state[name]

def add_team(name, channel):
    """
    Adds a team with the name, if able.
    """
    if name not in get_teams():
        state[name] = Submarine(name, channel)
        return True
    return False

class Submarine():
    def __init__(self, name, channel):
        self.name = name
        self.channel = channel
        self.direction = "N"
        self.speed = 1
        self.x = 0
        self.y = 0
        self.is_on = False

    def set_direction(self, direction):
        if direction in possible_directions():
            self.direction = direction
            return True
        return False

    def get_direction(self):
        return self.direction

    def get_position(self):
        return (self.x, self.y)

    def power(self):
        self.is_on = not self.is_on
        return True

    def powered(self):
        return self.is_on

    def move(self):
        self.x, self.y = move_on_map(self.direction, self.x, self.y)

    async def send_message(self, content):
        await self.channel.send(content)
