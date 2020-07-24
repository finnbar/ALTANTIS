"""
Deals with the world map, which submarines explore.
"""

class Empty():
    def __init__(self):
        pass

    def is_obstacle(self):
        return False
    
    def pick_up(self):
        return False
    
    def on_entry(self, sub):
        return None

    def to_char(self):
        return " "

class Wall(Empty):
    def __init__(self, damaging):
        self.damaging = damaging
    
    def is_obstacle(self):
        return True
    
    def on_entry(self, sub):
        sub.damage(self.damaging)
        return f"The submarine hit a wall and took {self.damaging} damage!"
    
    def to_char(self):
        return "W"

class Treasure(Empty):
    def __init__(self, name):
        self.name = name
        # TODO (no rush): make treasure appear to a player once scanned successfully.
        # May need to do via a list of players that can see each treasure.
        self.visible = False
    
    def pick_up(self):
        return True
    
    def to_char(self):
        if self.visible:
            return "T"
        return " "

class DockingStation(Empty):
    def __init__(self, name, direction):
        self.name = name
        self.direction = direction
    
    def on_entry(self, sub):
        sub.set_direction(self.direction)
        sub.power(False)
        (x, y) = sub.get_position()
        return f"Docked at **{self.name}** at position ({x}, {y})! The power has been stopped."
    
    def to_char(self):
        return "D"

# Map size.
X_LIMIT = 40
Y_LIMIT = 40

undersea_map = [[Empty() for _ in range(Y_LIMIT)] for _ in range(X_LIMIT)]
# TODO: Remove and replace with actual map.
undersea_map[0][39] = DockingStation("The Docking Station", "E")

directions = {"N": (0, -1), "NE": (1, -1), "E": (1, 0), "SE": (1, 1),
              "S": (0, 1), "SW": (-1, 1), "W": (-1, 0), "NW": (-1, -1)}

def possible_directions():
    return directions.keys()

def move_on_map(sub, direction, x, y):
    motion = directions[direction]
    new_x = (x + motion[0]) % X_LIMIT
    new_y = (y + motion[1]) % Y_LIMIT
    message = undersea_map[new_x][new_y].on_entry(sub)
    if undersea_map[new_x][new_y].is_obstacle():
        return x, y, message
    return new_x, new_y, message

def ascii_map(subs):
    """
    Draws an ASCII version of the map.
    `subs` is a list of submarines, which are marked 0-9 on the map.
    """
    map_string = ""
    for y in range(Y_LIMIT):
        row = ""
        for x in range(X_LIMIT):
            tile_char = undersea_map[x][y].to_char()
            for i in range(len(subs)):
                (sx, sy) = subs[i].get_position()
                if sx == x and sy == y:
                    tile_char = str(i)
            row += tile_char
        map_string += row + "\n"
    return map_string