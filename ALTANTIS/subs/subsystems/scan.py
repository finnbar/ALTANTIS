"""
Allows the sub to scan and be scanned.
"""
from random import shuffle
from typing import Tuple, List, Collection

from ALTANTIS.utils.direction import diagonal_distance, determine_direction
from ALTANTIS.utils.consts import X_LIMIT, Y_LIMIT
from ALTANTIS.subs.state import get_sub, get_subs
from ALTANTIS.npcs.npc import get_npc, get_npcs
from ALTANTIS.world.world import get_square
from ..sub import Submarine

class ScanSystem():
    def __init__(self, sub : Submarine):
        self.sub = sub
        self.prev_scan = ""

    def outward_broadcast(self, strength : int) -> str:
        """
        Shows information about this sub to others based on the strength of
        scanners. This strength is at least zero (comms power - distance).
        This strength allows for secrecy and limited information.
        Could add direction of motion, whether it's got cargo etc.
        """
        subname = ""
        unused_power = self.sub.power.unused_power()
        if "stealthy" in self.sub.upgrades.keywords and strength < min(3, unused_power):
            return ""
        if strength > 0:
            subname = f" {self.sub.name()}"
        else:
            subname = " ???"
        return f"Submarine{subname}"

    def scan(self) -> List[str]:
        """
        Perform a scanner sweep of the local area.
        This finds all subs and objects in range, and returns them.
        """
        scanners_range = int(1.5*self.sub.power.get_power("scanners"))
        if scanners_range < 0:
            return []
        my_position = self.sub.movement.get_position()
        with_distance = "triangulation" in self.sub.upgrades.keywords
        events = explore_submap(my_position, scanners_range, sub_exclusions=[self.sub._name], with_distance=with_distance)
        get_square(*my_position).has_been_scanned(self.sub._name, self.sub.power.get_power("scanners"))
        shuffle(events)
        return events
    
    def scan_string(self) -> str:
        events = self.scan()
        scan_message = ""
        if len(events) > 0:
            scan_message = "**Scanners found:**\n"
            scan_message += "\n".join(events)
            scan_message += "\n"
        self.prev_scan = scan_message
        return scan_message
    
    def previous_scan(self) -> str:
        return self.prev_scan
    
def explore_submap(pos : Tuple[int, int], dist : int, sub_exclusions : Collection[str] = (), npc_exclusions : Collection[int] = (), with_distance : bool = False) -> List[str]:
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
            event = get_square(x, y).outward_broadcast(dist - this_dist)
            if event != "":
                direction = determine_direction((cx, cy), (x, y))
                if direction is None:
                    event = f"{event} - in your current square!"
                else:
                    distance_measure = ""
                    if with_distance:
                        distance_measure = f" at a distance of {this_dist} away"
                    event = f"{event} - in direction {direction.upper()}{distance_measure}!"
                events.append(event)

    # Then, submarines.
    for subname in get_subs():
        if subname in sub_exclusions:
            continue

        sub = get_sub(subname)
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
    for npcid in get_npcs():
        if npcid in npc_exclusions:
            continue
        
        npc_obj = get_npc(npcid)
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