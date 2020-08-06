"""
Deals with the world map, which submarines explore.
"""

from utils import diagonal_distance, directions, reverse_dir, determine_direction

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
        return "."
    
    def outward_broadcast(self, strength):
        return ""
    
    def difficulty(self):
        """
        Defines how difficult it is to leave a square.
        4 is the normal (takes a one-engine sub four turns).
        8 is difficult terrain, 2 is easy and so on.
        """
        return 4

    def replaceable(self):
        """
        Defines whether this cell is replaceable.
        Used to avoid accidents when dropping or burying treasure.
        """
        return True

class Stormy(Empty):
    def __init__(self, difficulty):
        self.diff = difficulty
    
    def to_char(self):
        return "!"
    
    def outward_broadcast(self, strength):
        if strength >= 2:
            return "Storm brewing"
        return ""
    
    def difficulty(self):
        return self.diff

class Wall(Empty):
    def __init__(self, damaging):
        self.damaging = damaging
    
    def is_obstacle(self):
        return True
    
    def on_entry(self, sub):
        sub.damage(self.damaging)
        sub.set_direction(reverse_dir[sub.get_direction()])
        return f"The submarine hit a wall and took {self.damaging} damage!"
    
    def to_char(self):
        return "W"
    
    def replaceable(self):
        return False

class Treasure(Empty):
    def __init__(self, name):
        self.name = name
        self.visible = False
    
    def outward_broadcast(self, strength):
        if strength > 2:
            return self.name
        return "Treasure"
    
    def pick_up(self):
        return True
    
    def to_char(self):
        if self.visible:
            return "T"
        return "."

class DockingStation(Empty):
    def __init__(self, name, direction):
        self.name = name
        self.direction = direction
    
    def outward_broadcast(self, strength):
        return self.name
    
    def on_entry(self, sub):
        sub.set_direction(self.direction)
        sub.activate(False)
        (x, y) = sub.get_position()
        return f"Docked at **{self.name}** at position ({x}, {y})! The power has been stopped."
    
    def to_char(self):
        return "D"
    
    def replaceable(self):
        return False

# Map size.
X_LIMIT = 40
Y_LIMIT = 40

undersea_map = [[Empty() for _ in range(Y_LIMIT)] for _ in range(X_LIMIT)]

def possible_directions():
    return directions.keys()

def get_square(x, y):
    return undersea_map[x][y]

def bury_treasure_at(name, x, y):
    if 0 <= x < X_LIMIT and 0 <= y < Y_LIMIT:
        if undersea_map[x][y].replaceable():
            undersea_map[x][y] = Treasure(name)
            return True
    return False

def explore_submap(cx, cy, dist):
    """
    Explores the area centered around (cx, cy) spanning distance dist.
    Returns all outward_broadcast events (as a list) formatted for output.
    """
    events = []
    for i in range(-dist, dist+1):
        x = cx + i
        if x < 0 or x >= X_LIMIT:
            continue
        for j in range(-dist, dist+1):
            y = cy + j
            if y < 0 or y >= Y_LIMIT:
                continue
            this_dist = diagonal_distance(0, 0, i, j)
            event = undersea_map[x][y].outward_broadcast(dist - this_dist)
            if event != "":
                direction = determine_direction(cx, cy, x, y)
                if direction is None:
                    event = f"{event} in your current square!"
                else:
                    event = f"{event} in direction {direction}!"
                events.append(event)
    return events

def move_on_map(sub, direction, x, y):
    motion = directions[direction]
    new_x = x + motion[0]
    new_y = y + motion[1]
    if not (0 <= new_x < X_LIMIT) or not (0 <= new_y < Y_LIMIT):
        # Crashed into the boundaries of the world, whoops.
        sub.set_direction(reverse_dir[sub.get_direction()])
        return x, y, f"Your submarine reached the boundaries of the world, so was pushed back (now facing **{sub.direction}**) and did not move this turn!"
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

def map_to_dict():
    """
    Converts our map to dict form. Since each of our map entries can be
    trivially converted into dicts, we just convert them individually.
    We also append a class identifier so they can be recreated correctly.
    """
    undersea_map_dicts = [[{} for _ in range(Y_LIMIT)] for _ in range(X_LIMIT)]
    for i in range(X_LIMIT):
        for j in range(Y_LIMIT):
            undersea_map_dicts[i][j] = undersea_map[i][j].__dict__
            undersea_map_dicts[i][j]["__classname__"] = type(undersea_map[i][j]).__name__
    return (undersea_map_dicts, X_LIMIT, Y_LIMIT)

def map_from_dict(triple):
    """
    Takes a triple generated by map_to_dict and overwrites our map with it.
    """
    global X_LIMIT, Y_LIMIT, undersea_map
    (map_dicts, X_LIMIT, Y_LIMIT) = triple
    undersea_map_new = [[Empty() for _ in range(Y_LIMIT)] for _ in range(X_LIMIT)]
    for i in range(X_LIMIT):
        for j in range(Y_LIMIT):
            class_name = map_dicts[i][j]["__classname__"]
            # NOTE: this dictionary has to be manually updated each time. Lovely.
            classes = {"Empty": lambda: Empty(),
                       "DockingStation": lambda: DockingStation("", "N"),
                       "Stormy": lambda: Stormy(1),
                       "Treasure": lambda: Treasure(""),
                       "Wall": lambda: Wall(1)}
            if class_name not in classes:
                return False
            undersea_map_new[i][j] = classes[class_name]()
            map_dicts[i][j]["__classname__"] = None
            undersea_map_new[i][j].__dict__ = map_dicts[i][j]
    undersea_map = undersea_map_new