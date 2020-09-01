"""
Allows the sub to scan and be scanned.
"""

from utils import diagonal_distance, determine_direction
from world import explore_submap
from state import get_sub, get_subs
import sub

from random import shuffle
from typing import Tuple, List

class ScanSystem():
    def __init__(self, sub : sub.Submarine):
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
        scanners_range = 2*self.sub.power.get_power("scanners") - 2
        if scanners_range < 0:
            return []
        my_position = self.sub.movement.get_position()
        with_distance = "triangulation" in self.sub.upgrades.keywords
        events = explore_submap(my_position, scanners_range, sub_exclusions=[self.sub._name], with_distance=with_distance)
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