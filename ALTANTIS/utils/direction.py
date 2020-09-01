import math
from typing import Optional, Tuple

directions = {"n": (0, -1), "ne": (1, -1), "e": (1, 0), "se": (1, 1),
              "s": (0, 1), "sw": (-1, 1), "w": (-1, 0), "nw": (-1, -1)}
reverse_dir = {"n": "s", "ne": "sw", "e": "w", "se": "nw", "s": "n",
               "sw": "ne", "w": "e", "nw": "se"}

def diagonal_distance(pa : int, pb : int) -> int:
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

def determine_direction(pa : int, pb : int) -> Optional[str]:
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

def go_in_direction(direction : str) -> Tuple[int, int]:
    return directions[direction]