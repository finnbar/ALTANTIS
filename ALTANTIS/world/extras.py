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
    result : List[Entity] = []
    subs_in_range = filtered_teams(
        lambda sub: diagonal_distance(sub.movement.get_position(), pos) <= dist and sub._name not in sub_exclusions
    )
    for sub in subs_in_range:
        result.append(sub)
    npcs_in_range = filtered_npcs(
        lambda npc: diagonal_distance(npc.get_position(), pos) <= dist and npc.id not in npc_exclusions
    )
    for npc in npcs_in_range:
        result.append(npc)
    return result

async def explode(pos : Tuple[int, int], power : int, sub_exclusions : List[str] = [], npc_exclusions : List[int] = []):
    """
    Makes an explosion in pos, dealing power damage to the centre square,
    power-1 to the surrounding ones, power-2 to those that surround and
    so on.
    """
    from ALTANTIS.subs.state import get_sub_objects
    from ALTANTIS.npcs.npc import get_npc_objects
    for sub in get_sub_objects():
        if sub._name in sub_exclusions:
            continue

        sub_pos = sub.movement.get_position()
        sub_dist = diagonal_distance(pos, sub_pos)
        damage = power - sub_dist

        if damage > 0:
            await sub.send_message(f"Explosion in {pos}!", "captain")
            sub.damage(damage)
    
    for npc in get_npc_objects():
        if npc.id in npc_exclusions:
            continue
        
        npc_pos = npc.get_position()
        npc_dist = diagonal_distance(pos, npc_pos)
        damage = power - npc_dist

        if damage > 0:
            await npc.send_message(f"Explosion in {pos}!", "captain")
            npc.damage(damage)
