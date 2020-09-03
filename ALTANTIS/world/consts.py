# A list of implemented attributes
# Other attributes will do nothing, so are prevented from being added
ATTRIBUTES = ["deposit", "diverse", "hiddenness", "weather", "docking", "obstacle", "ruins", "junk", "wallstyle", "name"]
# A mapping of the permissible weather states and their map characters.
WEATHER = {"calm": "C", "normal": ".", "rough": "R", "stormy": "S"}
# A list of characters able to be used for wall alternate styles (such as in bases)
WALL_STYLES = ["b", "h", "z", "v", "p", "l"]
"""
All possible "command line options"
w: walls (obstacle)
d: docking stations
s: storm (all weather)
t: treasure
n: NPCs
a: ruins (?)
j: junk
m: mineral deposits
e: diverse ecosystem
"""
MAX_OPTIONS = ["w", "d", "s", "t", "n", "a", "j", "m", "e"]