"""
Deals with NPCs in general, and how they operate.
(Individual NPCs will be put elsewhere.)
"""

import world
from control import notify_control
from utils import Entity

class NPC(Entity):
    def __init__(self, name, x, y):
        self.health = 1
        self.treasure = None
        self.x = x
        self.y = y
        self.name = name
        self.stealth = 0
        self.damage_to_apply = 0
    
    async def on_tick(self):
        raise NotImplementedError

    async def send_message(self, content, _):
        await notify_control(f"Event from {self.name.title()}! {content}")

    async def damage_tick(self):
        self.health -= self.damage_to_apply
        if self.health <= 0:
            if self.treasure:
                world.bury_treasure_at(self.treasure, (self.x, self.y))
            await notify_control(f"**{self.name.title()}** took a total of {self.damage_to_apply} damage and **died**!")
            kill_npc(self.name)
        else:
            await notify_control(f"**{self.name.title()}** took a total of {self.damage_to_apply} damage!")
        self.damage_to_apply = 0

    def damage(self, amount):
        self.damage_to_apply += amount
    
    def outward_broadcast(self, strength):
        if strength >= self.stealth:
            return self.name.title()
        return ""
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    
    def get_position(self):
        return (self.x, self.y)
    
    def is_weak(self):
        return True

import npc_templates as _npc

# Available NPC types. Note that "NPC" is used liberally here - it can refer to
# monsters, non-player characters, and structures such as mines.
npc_types = {"squid": _npc.Squid}

# All NPCs, listed by name.
npcs = {}

def get_npcs():
    return npcs.keys()

def kill_npc(name):
    if name in npcs:
        del npcs[name]

async def npc_tick():
    for npc in npcs:
        await npcs[npc].on_tick()

def filtered_npcs(pred):
    """
    Gets all names of npcs that satisfy some predicate.
    """
    result = []
    for npc in npcs:
        if pred(npcs[npc]):
            result.append(npc)
    return result

def get_npc(npcname):
    if npcname in npcs:
        return npcs[npcname]
    return None

def add_npc(npcname, npctype, x, y):
    if not world.in_world(x, y):
        return "Cannot place an NPC outside of the map."
    if npcname in npcs:
        return "An NPC with than name already exists."
    if npctype in npc_types:
        npcs[npcname] = npc_types[npctype](npcname, x, y)
        return f"Created NPC {npcname.title()} of type {npctype.title()}!"
    return "That NPC type does not exist."