"""
Manage the state dictionary and the individual submarines within it.
"""

# State dictionary, filled with submarines.
state = {}
# Map size.
X_LIMIT = 50
Y_LIMIT = 50

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

directions = {"N": (0, -1), "NE": (1, -1), "E": (1, 0), "SE": (1, 1),
              "S": (0, 1), "SW": (-1, 1), "W": (-1, 0), "NW": (-1, -1)}

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
        if direction in directions:
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
        motion = directions[self.direction]
        self.x += motion[0]
        self.y += motion[1]
        self.x = self.x % X_LIMIT
        self.y = self.y % Y_LIMIT

    async def send_message(self, content):
        await self.channel.send(content)
