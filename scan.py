"""
Allows the sub to scan and be scanned.
"""

from utils import diagonal_distance, determine_direction
from world import explore_submap
from state import get_sub, get_subs

from random import shuffle

class ScanSystem():
    def __init__(self, sub):
        self.sub = sub
        self.prev_scan = ""

    def outward_broadcast(self, strength):
        """
        Shows information about this sub to others based on the strength of
        scanners. This strength is at least zero (comms power - distance).
        This strength allows for secrecy and limited information.
        TODO: Make this way more interesting. It's currently just sub name.
        Could add direction of motion, whether it's got cargo etc.
        """
        subname = ""
        if strength > 0: subname = f" {self.sub.name.title()}"
        return f"Submarine{subname}"

    def scan(self):
        """
        Perform a scanner sweep of the local area.
        This finds all subs and objects in range, and returns them.
        """
        scanners_range = 2*self.sub.power.get_power("scanners") - 2
        if scanners_range < 0:
            return []
        my_position = self.sub.movement.get_position()
        events = explore_submap(my_position, scanners_range, [self.sub.name])
        shuffle(events)
        return events
    
    def scan_string(self):
        events = self.scan()
        scan_message = ""
        if len(events) > 0:
            scan_message = "**Scanners found:**\n"
            scan_message += "\n".join(events)
            scan_message += "\n"
        self.prev_scan = scan_message
        return scan_message
    
    def previous_scan(self):
        return self.prev_scan