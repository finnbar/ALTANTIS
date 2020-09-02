"""
Deals with the world map, which submarines explore.
"""

from ALTANTIS.utils.text import list_to_and_separated
from ALTANTIS.utils.direction import reverse_dir, directions
from ALTANTIS.utils.consts import X_LIMIT, Y_LIMIT

import random
from typing import List, Optional, Tuple, Any, Dict


class Cell():
    # A list of implemented attributes
    # Other attributes will do nothing, so are prevented from being added
    ATTRIBUTES = ["deposit", "diverse", "hiddenness", "weather", "docking", "obstacle", "ruins", "junk"]
    WEATHER = {"calm": "C", "normal": ".", "rough": "R", "stormy": "S"}
    # A list of characters able to be used for wall alternate styles (such as in bases)
    # Currently just b for base.
    WALL_STYLES = ["b"]

    def __init__(self):
        # The items this square contains.
        self.treasure = []
        # Fundamentally describes how the square acts. These are described
        # throughout the class. A cell with no attributes acts like Empty from
        # the previous version - has no extra difficulty etc.
        self.attributes = {}

    def cell_tick(self):
        if not ("deposit" in self.attributes or "diverse" in self.attributes):
            return
        if "deposit" in self.attributes and random.random() < 0.03:
            self.treasure.append(random.choice(["tool", "plating"]))
        if "diverse" in self.attributes and random.random() < 0.03:
            self.treasure.append("specimen")
        if "ruins" in self.attributes and random.random() < 0.03:
            self.treasure.append(random.choice(["tool", "circuitry"]))

    def treasure_string(self) -> str:
        return list_to_and_separated(list(map(lambda t: t.title(), self.treasure)))

    def square_status(self) -> str:
        return f"This square has treasures {self.treasure_string()} and attributes {self.attributes}."

    def is_obstacle(self) -> bool:
        # obstacle: this cell cannot be entered.
        return "obstacle" in self.attributes

    def pick_up(self, power: int) -> List[str]:
        power = min(power, len(self.treasure))
        treasures = []
        for _ in range(power):
            treas = random.choice(self.treasure)
            self.treasure.remove(treas)
            treasures.append(treas)
        return treasures

    def bury_treasure(self, treasure: str) -> bool:
        self.treasure.append(treasure)
        return True

    def outward_broadcast(self, strength: int) -> str:
        # This is what the sub sees when scanning this cell.
        if "hiddenness" in self.attributes and self.attributes["hiddenness"] > strength:
            return ""
        broadcast = []
        if self.attributes.get("weather", "normal") == "stormy":
            broadcast.append("storm brewing")
        if len(self.treasure) > 0:
            if strength > 2:
                broadcast.append(self.treasure_string())
            else:
                plural = ""
                if len(self.treasure) != 1:
                    plural = "s"
                broadcast.append(f"{len(self.treasure)} treasure{plural}")
        if "diverse" in self.attributes:
            broadcast.append("a diverse ecosystem")
        if "ruins" in self.attributes:
            broadcast.append(f"some ruins ({self.attributes['ruins']})")
        if "junk" in self.attributes:
            broadcast.append("some submarine debris")
        if "deposit" in self.attributes:
            broadcast.append("a mineral deposit")
        if "docking" in self.attributes:
            broadcast.append(f"docking station \"{self.attributes['docking'].title()}\"")
        return list_to_and_separated(broadcast).capitalize()

    # We can't type check this because it would cause a circular import.
    def on_entry(self, sub) -> str:
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

    def to_char(self, to_show: List[str]) -> str:
        if "t" in to_show and len(self.treasure) > 0:
            return "T"
        if "r" in to_show and "ruins" in self.attributes:
            return "R"
        if "j" in to_show and "junk" in self.attributes:
            return "J"
        if "m" in to_show and "deposit" in self.attributes:
            return "M"
        if "e" in to_show and "diverse" in self.attributes:
            return "D"
        if "w" in to_show and "obstacle" in self.attributes:
            if "wallstyle" in self.attributes and self.attributes['wallstyle'] in self.WALL_STYLES:
                return self.attributes['wallstyle']
            else:
                return "W"
        if "d" in to_show and "docking" in self.attributes:
            return "D"
        if "s" in to_show and "weather" in self.attributes:
            return self.WEATHER.get(self.attributes.get("weather", "normal"), ".")
        return "."

    def map_name(self, to_show: List[str]) -> Optional[str]:
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

    def docked_at(self) -> Optional[str]:
        # Returns its name if it's a docking station, else None
        if "docking" in self.attributes:
            return self.attributes["docking"].title()
        return None

    def difficulty(self) -> int:
        difficulties = {"storm": 8, "rough": 6, "normal": 4, "calm": 2}
        if "weather" in self.attributes:
            return difficulties.get(self.attributes['weather'], 4)
        return 4

    def add_attribute(self, attr: str, val="") -> bool:
        if attr not in self.ATTRIBUTES:
            return False
        if attr not in self.attributes or self.attributes[attr] != val:
            self.attributes[attr] = val
            return True
        return False

    def remove_attribute(self, attr: str) -> bool:
        if attr in self.attributes:
            del self.attributes[attr]
            return True
        return False


undersea_map = [[Cell() for _ in range(Y_LIMIT)] for _ in range(X_LIMIT)]


def in_world(x: int, y: int) -> bool:
    return 0 <= x < X_LIMIT and 0 <= y < Y_LIMIT


def possible_directions() -> List[str]:
    return list(directions.keys())


def get_square(x: int, y: int) -> Optional[Cell]:
    if in_world(x, y):
        return undersea_map[x][y]
    return None


def bury_treasure_at(name: str, pos: Tuple[int, int]) -> bool:
    (x, y) = pos
    if in_world(x, y):
        return undersea_map[x][y].bury_treasure(name)
    return False


def pick_up_treasure(pos: Tuple[int, int], power: int) -> List[str]:
    (x, y) = pos
    if in_world(x, y):
        return undersea_map[x][y].pick_up(power)
    return []


def map_tick():
    for x in range(X_LIMIT):
        for y in range(Y_LIMIT):
            undersea_map[x][y].cell_tick()


def map_to_dict() -> Dict[str, Any]:
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


def map_from_dict(dictionary: Dict[str, Any]):
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
