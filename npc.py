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
        self.treasure = []
        self.x = x
        self.y = y
        self.name = name
        self.stealth = 0
        self.damage_to_apply = 0
        self.keywords = []
    
    async def on_tick(self):
        await self.damage_tick()
        await self.attack()
    
    async def attack(self):
        pass

    async def do_attack(self, entity, amount, message):
        if self.attackable(entity):
            await entity.send_message(message, "scientist")
            entity.damage(amount)

    def attackable(self, entity):
        if type(entity) == NPC:
            return not "camo" in entity.keywords
        else:
            return not "camo" in entity.upgrades.keywords

    async def send_message(self, content, _):
        await notify_control(f"Event from {self.name.title()}! {content}")

    async def damage_tick(self):
        if self.damage_to_apply > 0:
            self.health -= self.damage_to_apply
            if self.health <= 0:
                for treasure in self.treasure:
                    world.bury_treasure_at(treasure, (self.x, self.y))
                await notify_control(f"**{self.name.title()}** took a total of {self.damage_to_apply} damage and **died**!")
                await self.deathrattle()
                kill_npc(self.name)
            else:
                await notify_control(f"**{self.name.title()}** took a total of {self.damage_to_apply} damage!")
            self.damage_to_apply = 0

    async def deathrattle(self):
        hears_rattle = world.all_in_submap(self.get_position(), 5, [self.name])
        for entity in hears_rattle:
            await entity.send_message(f"ENTITY **{self.name.upper()}** ({self.x}, {self.y}) HAS DIED", "captain")

    def damage(self, amount):
        self.damage_to_apply += amount
    
    def outward_broadcast(self, strength):
        if strength >= self.stealth:
            return self.name.title()
        return ""
    
    def move(self, dx, dy):
        if world.in_world(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
    
    def get_position(self):
        return (self.x, self.y)
    
    def is_weak(self):
        return True
    
    async def interact(self, sub):
        return ""

import npc_templates as _npc

# Available NPC types. Note that "NPC" is used liberally here - it can refer to
# monsters, non-player characters, and structures such as mines.
npc_classes = [_npc.Squid, _npc.NewsBouy, _npc.GoldTrader]
npc_types = {}
for cl in npc_classes:
    npc_types[cl.classname] = cl

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

async def interact_in_square(sub, square, arg):
    in_square = filtered_npcs(lambda npc: (npc.x, npc.y) == square)
    message = ""
    for npcname in in_square:
        npc = get_npc(npcname)
        npc_message = await npc.interact(sub, arg)
        if npc_message != "":
            message += f"Interaction with **{npcname.title()}**: {npc_message}\n"
    return message

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

def npcs_to_dict():
    npcs_dict = {}
    for npc in npcs:
        npcs_dict[npc] = npcs[npc].__dict__.copy()
        npcs_dict[npc]["classname"] = npcs[npc].classname
    return npcs_dict

def npcs_from_dict(json):
    for npc_name in json:
        new_npc = npc_types[json[npc_name]["classname"]]("", 0, 0)
        del json[npc_name]["classname"]
        new_npc.__dict__ = json[npc_name]
        npcs[npc_name] = new_npc