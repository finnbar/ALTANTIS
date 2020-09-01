from typing import Tuple, List

from ALTANTIS.utils.entity import Entity
from ALTANTIS.utils.direction import diagonal_distance

def all_in_submap(pos : Tuple[int, int], dist : int, sub_exclusions : List[str] = [], npc_exclusions : List[int] = []) -> List[Entity]:
    from ALTANTIS.subs.state import filtered_teams, get_sub
    from ALTANTIS.npcs.npc import filtered_npcs, get_npc
    """
    Gets all entities some distance from the chosen square.
    Ignores any entities in exclusions.
    """
    subs_in_range = filtered_teams(
        lambda sub: diagonal_distance(sub.movement.get_position(), pos) <= dist and sub._name not in sub_exclusions
    )
    sub_objects = list(map(get_sub, subs_in_range))
    npcs_in_range = filtered_npcs(
        lambda npc: diagonal_distance(npc.get_position(), pos) <= dist and npc.id not in npc_exclusions
    )
    npc_objects = list(map(get_npc, npcs_in_range))
    return sub_objects + npc_objects

async def explode(pos : Tuple[int, int], power : int, sub_exclusions : List[str] = [], npc_exclusions : List[int] = []):
    """
    Makes an explosion in pos, dealing power damage to the centre square,
    power-1 to the surrounding ones, power-2 to those that surround and
    so on.
    """
    from ALTANTIS.subs.state import get_subs, get_sub
    from ALTANTIS.npcs.npc import get_npcs, get_npc
    for subname in get_subs():
        if subname in sub_exclusions:
            continue

        sub = get_sub(subname)
        sub_pos = sub.movement.get_position()
        sub_dist = diagonal_distance(pos, sub_pos)
        damage = power - sub_dist

        if damage > 0:
            await sub.send_message(f"Explosion in {pos}!", "captain")
            sub.damage(damage)
    
    for npcid in get_npcs():
        if npcid in npc_exclusions:
            continue
        
        npc_obj = get_npc(npcid)
        npc_pos = npc_obj.get_position()
        npc_dist = diagonal_distance(pos, npc_pos)
        damage = power - npc_dist

        if damage > 0:
            await npc_obj.send_message(f"Explosion in {pos}!", "captain")
            npc_obj.damage(damage)
