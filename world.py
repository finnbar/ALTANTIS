"""
Deals with the world map, which submarines explore.
"""

from utils import diagonal_distance, directions, reverse_dir, determine_direction, list_to_and_separated

class Cell():
    def __init__(self):
        # The item this square contains.
        self.treasure = None
        # Fundamentally describes how the square acts. These are described
        # throughout the class. A cell with no attributes acts like Empty from
        # the previous version - has no extra difficulty etc.
        self.attributes = {}
    
    def is_obstacle(self):
        # obstacle: this cell cannot be entered.
        return "obstacle" in self.attributes
    
    def pick_up(self):
        treas = self.treasure
        self.treasure = None
        return treas
    
    def bury_treasure(self, treasure):
        if self.treasure is None:
            self.treasure = treasure
            return True
        return False
    
    def outward_broadcast(self, strength):
        # This is what the sub sees when scanning this cell.
        if "hiddenness" in self.attributes and self.attributes["hiddenness"] > strength:
            return ""
        broadcast = []
        if "storm" in self.attributes:
            broadcast.append("storm brewing")
        if self.treasure is not None:
            if strength > 2:
                broadcast.append(f"{self.treasure.lower()}")
            else:
                broadcast.append("a treasure chest")
        if "docking" in self.attributes:
            broadcast.append(f"docking station \"{self.attributes['docking'].lower()}\"")
        return list_to_and_separated(broadcast).capitalize()
    
    def on_entry(self, sub):
        # This is what happens when a sub attempts to enter this space.
        # This includes docking and damage.
        if "docking" in self.attributes:
            sub.movement.set_direction(reverse_dir[sub.movement.get_direction()])
            sub.power.activate(False)
            (x, y) = sub.movement.get_position()
            return f"Docked at **{self.attributes['docking']}** at position ({x}, {y})! The power has been stopped."
        if "obstacle" in self.attributes:
            message = sub.power.damage(1)
            sub.movement.set_direction(reverse_dir[sub.movement.get_direction()])
            return f"The submarine hit a wall and took one damage!\n{message}"
        return ""

    def to_char(self, to_show):
        if "T" in to_show and self.treasure is not None:
            return "T"
        if "W" in to_show and "obstacle" in self.attributes:
            return "W"
        if "D" in to_show and "docking" in self.attributes:
            return "D"
        if "S" in to_show and "storm" in self.attributes:
            return "S"
        return "."
    
    def difficulty(self):
        if "storm" in self.attributes:
            return 8
        elif "calm" in self.attributes:
            return 2
        return 4
    
    def add_attribute(self, attr, val=""):
        if attr not in self.attributes:
            self.attributes[attr] = val
            return True
        return False
    
    def remove_attribute(self, attr):
        if attr in self.attributes:
            del self.attributes[attr]
            return True
        return False

# Map size.
X_LIMIT = 40
Y_LIMIT = 40

undersea_map = [[Cell() for _ in range(Y_LIMIT)] for _ in range(X_LIMIT)]

def possible_directions():
    return directions.keys()

def get_square(x, y):
    if 0 <= x < X_LIMIT and 0 <= y < Y_LIMIT:
        return undersea_map[x][y]
    return None

def bury_treasure_at(name, pos):
    (x, y) = pos
    if 0 <= x < X_LIMIT and 0 <= y < Y_LIMIT:
        return undersea_map[x][y].bury_treasure(name)
    return False

def pick_up_treasure(pos):
    (x, y) = pos
    if 0 <= x < X_LIMIT and 0 <= y < Y_LIMIT:
        return undersea_map[x][y].pick_up()
    return None

def explore_submap(pos, dist):
    """
    Explores the area centered around pos = (cx, cy) spanning distance dist.
    Returns all outward_broadcast events (as a list) formatted for output.
    """
    events = []
    (cx, cy) = pos
    for i in range(-dist, dist+1):
        x = cx + i
        if x < 0 or x >= X_LIMIT:
            continue
        for j in range(-dist, dist+1):
            y = cy + j
            if y < 0 or y >= Y_LIMIT:
                continue
            this_dist = diagonal_distance((0, 0), (i, j))
            event = undersea_map[x][y].outward_broadcast(dist - this_dist)
            if event != "":
                direction = determine_direction((cx, cy), (x, y))
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
        sub.movement.set_direction(reverse_dir[sub.movement.get_direction()])
        return x, y, f"Your submarine reached the boundaries of the world, so was pushed back (now facing **{sub.movement.direction}**) and did not move this turn!"
    message = undersea_map[new_x][new_y].on_entry(sub)
    if undersea_map[new_x][new_y].is_obstacle():
        return x, y, message
    return new_x, new_y, message

def draw_map(subs, to_show):
    """
    Draws an ASCII version of the map.
    `subs` is a list of submarines, which are marked 0-9 on the map.
    """
    map_string = ""
    for y in range(Y_LIMIT):
        row = ""
        for x in range(X_LIMIT):
            tile_char = undersea_map[x][y].to_char(to_show)
            # NOTE: NPC checking will go here, if "N" in to_show
            for i in range(len(subs)):
                (sx, sy) = subs[i].movement.get_position()
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
    return (undersea_map_dicts, X_LIMIT, Y_LIMIT)

def map_from_dict(triple):
    """
    Takes a triple generated by map_to_dict and overwrites our map with it.
    """
    global X_LIMIT, Y_LIMIT, undersea_map
    (map_dicts, X_LIMIT, Y_LIMIT) = triple
    undersea_map_new = [[Cell() for _ in range(Y_LIMIT)] for _ in range(X_LIMIT)]
    for i in range(X_LIMIT):
        for j in range(Y_LIMIT):
            undersea_map_new[i][j].__dict__ = map_dicts[i][j]
    undersea_map = undersea_map_new