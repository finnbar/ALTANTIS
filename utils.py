"""
Utility classes for Statuses (return values from Discord actions).
Also utility functions for distances and directions.
"""

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

OKAY_REACT = React("☑")
FAIL_REACT = React("❌")

class Message(Status):
    def __init__(self, contents):
        self.contents = contents

    async def do_status(self, ctx):
        await ctx.send(self.contents)

directions = {"N": (0, -1), "NE": (1, -1), "E": (1, 0), "SE": (1, 1),
              "S": (0, 1), "SW": (-1, 1), "W": (-1, 0), "NW": (-1, -1)}
reverse_dir = {"N": "S", "NE": "SW", "E": "W", "SE": "NW", "S": "N",
               "SW": "NE", "W": "E", "NW": "SE"}

import math

def diagonal_distance(ax, ay, bx, by):
    """
    Gets manhattan distance with diagonals between (ax, ay) and (bx, by).
    I don't know what this is called, but the fastest route is to take the
    diagonal and then do any excess.
    """
    xdist = abs(ax - bx)
    ydist = abs(ay - by)
    dist = min(xdist, ydist) + abs(xdist - ydist)
    return dist

def determine_direction(ax, ay, bx, by):
    """
    Determines which compass direction (bx, by) is from (ax, ay).
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
    if by - ay == 0 and bx - ax == 0:
        return None

    angle = math.atan2(by - ay, bx - ax)
    y_val = ""
    # It's northern if the angle is between -7pi/8 and -pi/8.
    if -7*math.pi / 8 <= angle <= -math.pi / 8:
        y_val = "N"
    # Southern case is similar: between pi/8 and 7pi/8.
    if 7*math.pi / 8 >= angle >= math.pi / 8:
        y_val = "S"
    x_val = ""
    # Western if the absolute of the angle is larger than 5pi/8.
    if abs(angle) > 5*math.pi / 8:
        x_val = "W"
    # Eastern if the absolute is less than 3pi/8.
    if abs(angle) < 3*math.pi / 8:
        x_val = "E"
    return y_val + x_val