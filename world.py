"""
Deals with the world map, which submarines explore.
"""

# Map size.
X_LIMIT = 50
Y_LIMIT = 50

directions = {"N": (0, -1), "NE": (1, -1), "E": (1, 0), "SE": (1, 1),
              "S": (0, 1), "SW": (-1, 1), "W": (-1, 0), "NW": (-1, -1)}

def possible_directions():
    return directions.keys()

def move_on_map(direction, x, y):
    motion = directions[direction]
    x += motion[0]
    y += motion[1]
    x = x % X_LIMIT
    y = y % Y_LIMIT
    return x,y