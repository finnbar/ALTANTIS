"""
Utility classes for Statuses (return values from Discord actions).
Also utility functions for distances and directions.
"""

from consts import TICK, CROSS

# Messaging utilities

class Status():
    def __init__(self):
        pass

    async def do_status(self):
        pass

class React(Status):
    def __init__(self, react):
        self.react = react

    async def do_status(self, ctx):
        await ctx.message.add_reaction(self.react)

OKAY_REACT = React(TICK)
FAIL_REACT = React(CROSS)

class Message(Status):
    def __init__(self, contents):
        self.contents = contents

    async def do_status(self, ctx):
        await ctx.send(self.contents)

# Direction utilities

directions = {"n": (0, -1), "ne": (1, -1), "e": (1, 0), "se": (1, 1),
              "s": (0, 1), "sw": (-1, 1), "w": (-1, 0), "nw": (-1, -1)}
reverse_dir = {"n": "s", "ne": "sw", "e": "w", "se": "nw", "s": "n",
               "sw": "ne", "w": "e", "nw": "se"}

import math

def diagonal_distance(pa, pb):
    """
    Gets manhattan distance with diagonals between points pa and pb.
    I don't know what this is called, but the fastest route is to take the
    diagonal and then do any excess.
    """
    (ax, ay) = pa
    (bx, by) = pb
    xdist = abs(ax - bx)
    ydist = abs(ay - by)
    dist = min(xdist, ydist) + abs(xdist - ydist)
    return dist

def determine_direction(pa, pb):
    """
    Determines which compass direction coord pb is from pa.
    This would normally be easy, but guess which idiot made everything work in
    eight compass directions instead of four? (Me, that's who.)
    Also, we have an extra fun bonus: the world has top left being (0, 0).
    Also also, Python's angles are -pi to pi, where 0 is East.
    To solve this, we define regions where each of the four starting directions
    should be present, which are annotated.
    Simple idea: ±pi/8 and ±7pi/8 are the points where a vector is closer to
    E/W than NE/NW/SE/SW, and ±3pi/8 and ±5pi/8 are then points where a vector
    is closer to N/S than NE/NW/SE/SW.
    """
    (ax, ay) = pa
    (bx, by) = pb

    if by - ay == 0 and bx - ax == 0:
        return None

    angle = math.atan2(by - ay, bx - ax)
    y_val = ""
    # It's northern if the angle is between -7pi/8 and -pi/8.
    if -7*math.pi / 8 <= angle <= -math.pi / 8:
        y_val = "n"
    # Southern case is similar: between pi/8 and 7pi/8.
    if 7*math.pi / 8 >= angle >= math.pi / 8:
        y_val = "s"
    x_val = ""
    # Western if the absolute of the angle is larger than 5pi/8.
    if abs(angle) > 5*math.pi / 8:
        x_val = "w"
    # Eastern if the absolute is less than 3pi/8.
    if abs(angle) < 3*math.pi / 8:
        x_val = "e"
    return y_val + x_val

def go_in_direction(direction):
    return directions[direction]

# Textual utilities

def list_to_and_separated(items):
    if len(items) == 0:
        return ""
    if len(items) == 1:
        return items[0]
    # Turn into a list with commas to separate elements.
    result = []
    for item in items:
        result.append(item)
        result.append(", ")
    # Then remove the last comma and replace the second last comma with " and "
    result = result[:-1]
    result[-2] = " and "
    return "".join(result)

def to_titled_list(items):
    return list_to_and_separated(list(map(lambda x: x.title(), items)))

def to_pair_list(items):
    pairs = []
    if len(items) % 2 == 1:
        raise ValueError("Input list is badly formatted.")
    for i in range(0, len(items), 2):
        pairs.append((items[i], int(items[i+1])))
    return pairs

# Roles helper

async def create_or_return_role(guild, role, **kwargs):
    all_roles = await guild.fetch_roles()
    for r in all_roles:
        if r.name == role:
            return r
    return await guild.create_role(name=role, **kwargs)

# Helper class for dealing with NPCs and Submarines together.

class Entity():
    def get_position(self):
        raise NotImplementedError

    def damage(self, amount):
        raise NotImplementedError

    async def send_message(self, content, channel):
        raise NotImplementedError

    def outward_broadcast(self, strength):
        return ""

    def is_weak(self):
        """
        Whether the submarine is affected by stunning shots.
        """
        return False
    
    def name(self):
        """
        The primary key.
        """
        raise NotImplementedError