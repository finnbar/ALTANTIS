"""
Deals with the world map, which submarines explore.
"""

from utils import diagonal_distance, directions, reverse_dir, determine_direction, list_to_and_separated
import state, npc

from random import choice

class Cell():
    def __init__(self):
        # The items this square contains.
        self.treasure = []
        # Fundamentally describes how the square acts. These are described
        # throughout the class. A cell with no attributes acts like Empty from
        # the previous version - has no extra difficulty etc.
        self.attributes = {}
    
    def treasure_string(self):
        return list_to_and_separated(list(map(lambda t: t.title(), self.treasure)))
    
    def square_status(self):
        return f"This square has treasures {self.treasure_string()} and attributes {self.attributes}."
    
    def is_obstacle(self):
        # obstacle: this cell cannot be entered.
        return "obstacle" in self.attributes
    
    def pick_up(self, power):
        power = min(power, len(self.treasure))
        treasures = []
        for _ in range(power):
            treas = choice(self.treasure)
            self.treasure.remove(treas)
            treasures.append(treas)
        return treasures
    
    def bury_treasure(self, treasure):
        self.treasure.append(treasure)
        return True
    
    def outward_broadcast(self, strength):
        # This is what the sub sees when scanning this cell.
        if "hiddenness" in self.attributes and self.attributes["hiddenness"] > strength:
            return ""
        broadcast = []
        if "storm" in self.attributes:
            broadcast.append("storm brewing")
        if len(self.treasure) > 0:
            if strength > 2:
                broadcast.append(self.treasure_string())
            else:
                plural = ""
                if len(self.treasure) > 1:
                    plural = "s"
                broadcast.append(f"{len(self.treasure)} treasure{plural}")
        if "docking" in self.attributes:
            broadcast.append(f"docking station \"{self.attributes['docking'].title()}\"")
        return list_to_and_separated(broadcast).capitalize()
    
    async def on_entry(self, sub):
        # This is what happens when a sub attempts to enter this space.
        # This includes docking and damage.
        if "docking" in self.attributes:
            sub.movement.set_direction(reverse_dir[sub.movement.get_direction()])
            sub.power.activate(False)
            (x, y) = sub.movement.get_position()
            return f"Docked at **{self.attributes['docking'].title()}** at position ({x}, {y})! The power has been stopped. Please call !exit_sub to leave the submarine and enter the docking station."
        if "obstacle" in self.attributes:
            message = sub.damage(1)
            sub.movement.set_direction(reverse_dir[sub.movement.get_direction()])
            return f"The submarine hit a wall and took one damage!\n{message}"
        return ""

    def to_char(self, to_show):
        if "t" in to_show and len(self.treasure) > 0:
            return "T"
        if "w" in to_show and "obstacle" in self.attributes:
            return "W"
        if "d" in to_show and "docking" in self.attributes:
            return "D"
        if "s" in to_show and "storm" in self.attributes:
            return "S"
        if "c" in to_show and "calm" in self.attributes:
            return "C"
        return "."
    
    def map_name(self, to_show):
        # For Thomas' map drawing code.
        # Gives names to squares that make sense.
        name = ""
        if "t" in to_show and len(self.treasure) > 0:
            name = self.treasure_string()
        if "d" in to_show and "docking" in self.attributes:
            name = self.attributes["docking"].title()
        if name != "":
            return name
        return None
    
    def docked_at(self):
        # Returns its name if it's a docking station, else None
        if "docking" in self.attributes:
            return self.attributes["docking"].title()
        return None
    
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

def in_world(x, y):
    return 0 <= x < X_LIMIT and 0 <= y < Y_LIMIT

def possible_directions():
    return directions.keys()

def get_square(x, y):
    if in_world(x, y):
        return undersea_map[x][y]
    return None

def bury_treasure_at(name, pos):
    (x, y) = pos
    if in_world(x, y):
        return undersea_map[x][y].bury_treasure(name)
    return False

def pick_up_treasure(pos, power):
    (x, y) = pos
    if in_world(x, y):
        return undersea_map[x][y].pick_up(power)
    return []

def investigate_square(x, y, loop):
    if in_world(x, y):
        report = f"Report for square **({x}, {y})**\n"
        report += get_square(x, y).square_status() + "\n\n"
        # See if any subs are here, and if so print their status.
        subs_in_square = state.filtered_teams(lambda sub: sub.movement.x == x and sub.movement.y == y)
        for subname in subs_in_square:
            sub = state.get_sub(subname)
            report += sub.status_message(loop) + "\n\n"
        return report

def all_in_square(pos):
    """
    Gets all entities (subs and NPCs) in the chosen square.
    """
    (x, y) = pos
    subs_in_square = state.filtered_teams(lambda sub: sub.movement.x == x and sub.movement.y == y)
    sub_objects = list(map(state.get_sub, subs_in_square))
    npcs_in_square = npc.filtered_npcs(lambda npc: npc.x == x and npc.y == y)
    npc_objects = list(map(npc.get_npc, npcs_in_square))
    return sub_objects + npc_objects

def all_in_submap(pos, dist, exclusions=[]):
    """
    Gets all entities some distance from the chosen square.
    Ignores any entities in exclusions.
    """
    subs_in_range = state.filtered_teams(
        lambda sub: diagonal_distance(sub.movement.get_position(), pos) <= dist and sub.name not in exclusions
    )
    sub_objects = list(map(state.get_sub, subs_in_range))
    npcs_in_range = npc.filtered_npcs(
        lambda npc: diagonal_distance(npc.get_position(), pos) <= dist and npc.name not in exclusions
    )
    npc_objects = list(map(npc.get_npc, npcs_in_range))
    return sub_objects + npc_objects

async def explode(pos, power, exclusions=[]):
    """
    Makes an explosion in pos, dealing power damage to the centre square,
    power-1 to the surrounding ones, power-2 to those that surround and
    so on.
    """
    for subname in state.get_subs():
        if subname in exclusions:
            continue

        sub = state.get_sub(subname)
        sub_pos = sub.movement.get_position()
        sub_dist = diagonal_distance(pos, sub_pos)
        damage = power - sub_dist

        if damage > 0:
            await sub.send_message(f"Explosion in {pos}!", "captain")
            sub.damage(damage)
    
    for npcname in npc.get_npcs():
        if npcname in exclusions:
            continue
        
        npc_obj = npc.get_npc(npcname)
        npc_pos = npc_obj.get_position()
        npc_dist = diagonal_distance(pos, npc_pos)
        damage = power - npc_dist

        if damage > 0:
            await npc_obj.send_message(f"Explosion in {pos}!", "captain")
            npc_obj.damage(damage)

def explore_submap(pos, dist, exclusions=[], with_distance=False):
    """
    Explores the area centered around pos = (cx, cy) spanning distance dist.
    Returns all outward_broadcast events (as a list) formatted for output.
    Ignores any NPCs or subs with a name included in exclusions.
    """
    events = []
    (cx, cy) = pos
    # First, map squares.
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
                    distance_measure = ""
                    if with_distance:
                        distance_measure = f" at a distance of {this_dist} away"
                    event = f"{event} in direction {direction.upper()}{distance_measure}!"
                events.append(event)

    # Then, submarines.
    for subname in state.get_subs():
        if subname in exclusions:
            continue

        sub = state.get_sub(subname)
        sub_pos = sub.movement.get_position()
        sub_dist = diagonal_distance(pos, sub_pos)

        # If out of range, drop it.
        if sub_dist > dist:
            continue
        
        event = sub.scan.outward_broadcast(dist - sub_dist)
        direction = determine_direction(pos, sub_pos)
        if direction is None:
            event = f"{event} in your current square!"
        else:
            event = f"{event} in direction {direction.upper()}!"
        events.append(event)
    
    # Finally, NPCs.
    for npcname in npc.get_npcs():
        if npcname in exclusions:
            continue
        
        npc_obj = npc.get_npc(npcname)
        npc_pos = npc_obj.get_position()
        npc_dist = diagonal_distance(pos, npc_pos)

        if npc_dist > dist:
            continue

        event = npc_obj.outward_broadcast(dist - npc_dist)
        direction = determine_direction(pos, npc_pos)
        if direction is None:
            event = f"{event} in your current square!"
        else:
            event = f"{event} in direction {direction.upper()}!"
        events.append(event)

    return events

async def move_on_map(sub, direction, x, y):
    motion = directions[direction]
    new_x = x + motion[0]
    new_y = y + motion[1]
    if not in_world(new_x, new_y):
        # Crashed into the boundaries of the world, whoops.
        sub.movement.set_direction(reverse_dir[sub.movement.get_direction()])
        return x, y, f"Your submarine reached the boundaries of the world, so was pushed back (now facing **{sub.movement.direction.upper()}**) and did not move this turn!"
    message = await undersea_map[new_x][new_y].on_entry(sub)
    if undersea_map[new_x][new_y].is_obstacle():
        return x, y, message
    return new_x, new_y, message

def draw_map(subs, to_show):
    """
    Draws an ASCII version of the map.
    Also returns a JSON of additional information.
    `subs` is a list of submarines, which are marked 0-9 on the map.
    """
    map_string = ""
    map_json = []
    for y in range(Y_LIMIT):
        row = ""
        for x in range(X_LIMIT):
            tile_char = undersea_map[x][y].to_char(to_show)
            tile_name = undersea_map[x][y].map_name(to_show)
            if "n" in to_show:
                npcs_in_square = npc.filtered_npcs(lambda n: n.x == x and n.y == y)
                if len(npcs_in_square) > 0:
                    tile_char = "N"
                    tile_name = list_to_and_separated(list(map(lambda n: n.title(), npcs_in_square)))
            for i in range(len(subs)):
                (sx, sy) = subs[i].movement.get_position()
                if sx == x and sy == y:
                    tile_char = str(i)
                    tile_name = subs[i].name.title()
            row += tile_char
            if tile_name is not None:
                map_json.append({"x": x, "y": y, "name": tile_name})
        map_string += row + "\n"
    return map_string, map_json

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
    return {"map": undersea_map_dicts, "x_limit": X_LIMIT, "y_limit": Y_LIMIT}

def map_from_dict(dictionary):
    """
    Takes a triple generated by map_to_dict and overwrites our map with it.
    """
    global X_LIMIT, Y_LIMIT, undersea_map
    X_LIMIT = dictionary["x_limit"]
    Y_LIMIT = dictionary["y_limit"]
    map_dicts = dictionary["map"]
    undersea_map_new = [[Cell() for _ in range(Y_LIMIT)] for _ in range(X_LIMIT)]
    for i in range(X_LIMIT):
        for j in range(Y_LIMIT):
            undersea_map_new[i][j].__dict__ = map_dicts[i][j]
    undersea_map = undersea_map_new