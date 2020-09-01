"""
Deals with NPCs in general, and how they operate.
(Individual NPCs will be put elsewhere.)
"""

import world, sub
from control import notify_control
from utils import Entity, diagonal_distance, determine_direction, go_in_direction

from typing import Tuple, List, Callable, Dict, Any

class NPC(Entity):
    classname = ""
    def __init__(self, id : int, x : int, y : int):
        self.health = 1
        self.treasure = []
        self.x = x
        self.y = y
        self.id = id
        self.stealth = 0
        self.damage_to_apply = 0
        self.keywords = []
    
    async def on_tick(self):
        await self.damage_tick()
        await self.attack()
    
    async def attack(self):
        pass

    async def do_attack(self, entity, amount, message) -> bool:
        if self.attackable(entity):
            await entity.send_message(message, "scientist")
            entity.damage(amount)
            return True
        return False

    def attackable(self, entity) -> bool:
        if type(entity) is sub.Submarine:
            return not "camo" in entity.upgrades.keywords
        else:
            return not "camo" in entity.keywords
    
    def name(self) -> str:
        return f"{self.classname.title()} (#{self.id})"
    
    def full_name(self) -> str:
        return f"{self.classname.title()} (#{self.id} at {self.x}, {self.y})"

    async def send_message(self, content, _):
        await notify_control(f"Event from {self.name()}! {content}")

    async def damage_tick(self):
        if self.damage_to_apply > 0:
            self.health -= self.damage_to_apply
            if self.health <= 0:
                for treasure in self.treasure:
                    world.bury_treasure_at(treasure, (self.x, self.y))
                await notify_control(f"**{self.full_name()}** took a total of {self.damage_to_apply} damage and **died**!")
                await self.deathrattle()
                kill_npc(self.id)
            else:
                await notify_control(f"**{self.full_name()}** took a total of {self.damage_to_apply} damage!")
            self.damage_to_apply = 0

    async def deathrattle(self):
        hears_rattle = world.all_in_submap(self.get_position(), 5, npc_exclusions=[self.id])
        for entity in hears_rattle:
            await entity.send_message(f"ENTITY **{self.name().upper()}** HAS DIED", "captain")

    def damage(self, amount : int):
        self.damage_to_apply += amount
    
    def outward_broadcast(self, strength : int) -> str:
        if strength >= self.stealth:
            return self.name()
        return ""
    
    def move(self, dx : int, dy : int):
        if world.in_world(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
    
    def move_towards_sub(self, dist : str):
        """
        Looks for the closest sub in range, and moves towards it.
        """
        nearby_entities = world.all_in_submap(self.get_position(), dist)
        closest = (None, 0)
        for entity in nearby_entities:
            if type(entity) is sub.Submarine:
                this_dist = diagonal_distance(self.get_position(), entity.get_position())
                if (closest[0] is None) or this_dist < closest[1]:
                    closest = (entity, this_dist)
        if closest[0] is not None:
            direction = determine_direction(self.get_position(), closest[0].get_position())
            if direction is not None:
                self.move(*go_in_direction(direction))
    
    def get_position(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def is_weak(self) -> bool:
        return True
    
    async def interact(self, sub) -> str:
        return ""

import npc_templates as _npc

# Available NPC types. Note that "NPC" is used liberally here - it can refer to
# monsters, non-player characters, and structures such as mines.
npc_classes = [_npc.Squid, _npc.BigSquid, _npc.Dolphin, _npc.Eel, _npc.Mine, _npc.StormGenerator, _npc.Whale, _npc.Octopus, _npc.NewsBouy, _npc.GoldTrader, _npc.Urchin, _npc.MantaRay, _npc.AnglerFish, _npc.Shark, _npc.Crab]
npc_types = {}
for cl in npc_classes:
    npc_types[cl.classname] = cl

# All NPCs, listed by ID.
npcs = []

def get_npc_types() -> List[str]:
    return npc_types.keys()

def get_npcs() -> List[int]:
    return range(len(npcs))

def kill_npc(id : int) -> bool:
    if id in range(len(npcs)):
        del npcs[id]
        return True
    return False

async def npc_tick():
    for npc in npcs:
        await npc.on_tick()

def filtered_npcs(pred : Callable[[NPC], bool]) -> List[int]:
    """
    Gets all names of npcs that satisfy some predicate.
    """
    result = []
    for index in range(len(npcs)):
        if pred(npcs[index]):
            result.append(index)
    return result

async def interact_in_square(sub : sub.Submarine, square : Tuple[int, int], arg) -> str:
    in_square = filtered_npcs(lambda npc: (npc.x, npc.y) == square)
    message = ""
    for npcid in in_square:
        npc = get_npc(npcid)
        npc_message = await npc.interact(sub, arg)
        if npc_message != "":
            message += f"Interaction with **{npcid.title()}**: {npc_message}\n"
    return message

def get_npc(npcid : int) -> NPC:
    if npcid in get_npcs():
        return npcs[npcid]
    return None

def add_npc(npctype : str, x : int, y : int):
    if not world.in_world(x, y):
        return "Cannot place an NPC outside of the map."
    if npctype in npc_types:
        id = len(npcs)
        npcs.append(npc_types[npctype](id, x, y))
        return f"Created NPC #{id} of type {npctype.title()}!"
    return "That NPC type does not exist."

def npcs_to_json() -> List[Dict[str, Any]]:
    npcs_list = []
    for npc in npcs:
        npcs_list.append(npc.__dict__.copy())
        npcs_list[-1]["classname"] = npc.classname
    return npcs_list

def npcs_from_json(json : List[Dict[str, Any]]):
    global npcs
    npcs = []
    for npc in json:
        new_npc = npc_types[npc["classname"]](0, 0, 0)
        del npc["classname"]
        new_npc.__dict__ = npc
        npcs.append(new_npc)