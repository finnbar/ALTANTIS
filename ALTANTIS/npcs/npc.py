from __future__ import annotations
"""
Deals with NPCs in general, and how they operate.
(Individual NPCs will be put elsewhere.)
"""

from ALTANTIS.subs.state import filtered_teams, get_sub
from ALTANTIS.subs.sub import Submarine
from ALTANTIS.world.world import bury_treasure_at, in_world, get_square
from ALTANTIS.world.extras import all_in_submap
from ALTANTIS.utils.control import notify_control
from ALTANTIS.utils.entity import Entity
from ALTANTIS.utils.direction import diagonal_distance, determine_direction, go_in_direction, rotate_direction

from typing import Tuple, List, Callable, Dict, Any, Optional

class NPC(Entity):
    classname = ""
    def __init__(self, id : int, x : int, y : int):
        self.health = 1
        self.treasure : List[str] = []
        self.x = x
        self.y = y
        self.id = id
        self.stealth = 0
        self.damage_to_apply = 0
        self.camo = False
        self.observant = False
        self.photo = ""
        self.typename = self.classname.title()
        self.parent : Optional[str] = None
    
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
        if self.observant:
            return True
        if type(entity) is Submarine:
            return not "camo" in entity.upgrades.keywords
        else:
            return not entity.camo
    
    def name(self) -> str:
        return f"{self.typename} (#{self.id})"
    
    def full_name(self) -> str:
        return f"{self.typename} (#{self.id} at {self.x}, {self.y})"

    async def send_message(self, content, _):
        await notify_control(f"Event from {self.name()}! {content}")

    async def damage_tick(self):
        if self.damage_to_apply > 0:
            self.health -= self.damage_to_apply
            if self.health <= 0:
                for treasure in self.treasure:
                    bury_treasure_at(treasure, (self.x, self.y))
                await notify_control(f"**{self.full_name()}** took a total of {self.damage_to_apply} damage and **died**!")
                await self.deathrattle()
                kill_npc(self.id)
            else:
                await notify_control(f"**{self.full_name()}** took a total of {self.damage_to_apply} damage!")
            self.damage_to_apply = 0
            self.observant = True

    async def deathrattle(self):
        hears_rattle = all_in_submap(self.get_position(), 5, npc_exclusions=[self.id])
        for entity in hears_rattle:
            await entity.send_message(f"ENTITY **{self.name().upper()}** HAS DIED", "captain")

    def damage(self, amount : int):
        self.damage_to_apply += amount
    
    def outward_broadcast(self, strength : int) -> str:
        if strength >= self.stealth:
            return self.name()
        return ""
    
    def move(self, dx : int, dy : int) -> bool:
        sq = get_square(self.x + dx, self.y + dy)
        if sq is not None and sq.can_npc_enter():
            self.x += dx
            self.y += dy
            return True
        return False
    
    def move_towards_sub(self, dist : int) -> bool:
        """
        Looks for the closest sub in range, and moves towards it.
        """
        nearby_entities : List[Entity] = all_in_submap(self.get_position(), dist)
        closest : Tuple[Optional[Submarine], int] = (None, 0)
        for entity in nearby_entities:
            if isinstance(entity, Submarine):
                sub : Submarine = entity
                this_dist = diagonal_distance(self.get_position(), sub.get_position())
                if (closest[0] is None) or this_dist < closest[1]:
                    closest = (entity, this_dist)
        if closest[0] is not None:
            direction = determine_direction(self.get_position(), closest[0].get_position())
            if direction is not None:
                rotated = rotate_direction(direction)
                directions = [direction]
                if rotated is not None:
                    directions.append(rotated[0])
                    directions.append(rotated[1])
                for possible_direction in directions:
                    if self.move(*go_in_direction(possible_direction)):
                        return True
        return False
    
    def get_position(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def is_weak(self) -> bool:
        return True
    
    async def interact(self, sub: Submarine, arg: Any) -> str:
        return ""
    
    def all_subs_in_square(self) -> List[Submarine]:
        return filtered_teams(lambda sub: sub.movement.x == self.x and sub.movement.y == self.y)
    
    def all_npcs_in_square(self) -> List[NPC]:
        return filtered_npcs(lambda npc: npc.x == self.x and npc.y == self.y and npc != self)

    def all_in_square(self) -> List[Entity]:
        """
        Gets all entities (subs and NPCs) in your square except yourself.
        """
        result : List[Entity] = []
        for sub in self.all_subs_in_square():
            result.append(sub)
        for npc in self.all_npcs_in_square():
            result.append(npc)
        return result
    
    def take_photo(self, sub : Submarine):
        if self.photo == "":
            return ""
        photo_name = f"{self.typename.lower()} photo*"
        if sub.inventory.has(photo_name):
            return "Your photo came out all blurry..."
        sub.inventory.add(photo_name)
        return f"You took a photo of a {self.typename}! {self.photo}"
    
    def add_parent(self, parent : str):
        self.parent = parent
    
    def get_parent(self) -> Optional[Submarine]:
        if self.parent is None:
            return None
        return get_sub(self.parent)

npc_types = {}

def load_npc_types():
    # Woo let's continue to avoid circular imports!
    from ALTANTIS.npcs.templates import ALL_NPCS

    # Available NPC types. Note that "NPC" is used liberally here - it can refer to
    # monsters, non-player characters, and structures such as mines.
    for cl in ALL_NPCS:
        npc_types[cl.classname] = cl

# All NPCs, listed by ID.
npcs : List[NPC] = []

def get_npc_types() -> List[str]:
    return list(npc_types.keys())

def get_npcs() -> List[int]:
    return list(range(len(npcs)))

def get_npc_objects() -> List[NPC]:
    return npcs

async def kill_npc(id : int, rattle : bool = True) -> bool:
    if id in range(len(npcs)):
        if rattle: await npcs[id].deathrattle()
        del npcs[id]
        return True
    return False

async def npc_tick():
    for npc in npcs:
        await npc.on_tick()

def filtered_npcs(pred : Callable[[NPC], bool]) -> List[NPC]:
    """
    Gets all names of npcs that satisfy some predicate.
    """
    result = []
    for index in range(len(npcs)):
        npc = npcs[index]
        if pred(npcs[index]):
            result.append(npc)
    return result

async def interact_in_square(sub : Submarine, square : Tuple[int, int], arg) -> str:
    in_square = filtered_npcs(lambda npc: (npc.x, npc.y) == square)
    message = ""
    for npc in in_square:
        if sub.power.get_power("scanners") >= npc.stealth:
            npc_message = await npc.interact(sub, arg)
            if npc_message != "":
                message += f"Interaction with **{npc.name()}**: {npc_message}\n"
    return message

def get_npc(npcid : int) -> Optional[NPC]:
    if npcid in get_npcs():
        return npcs[npcid]
    return None

def add_npc(npctype : str, x : int, y : int, sub : Optional[str]):
    if not in_world(x, y):
        return "Cannot place an NPC outside of the map."
    if npctype in npc_types:
        id = len(npcs)
        new_npc = npc_types[npctype](id, x, y)
        if sub is not None:
            new_npc.add_parent(sub)
        npcs.append(new_npc)
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