"""
Allows the sub to scan and be scanned.
"""

from utils import diagonal_distance, determine_direction
from world import explore_submap
from state import get_sub, get_teams

from random import shuffle

class ScanSystem():
    def __init__(self, sub):
        self.sub = sub

    def outward_broadcast(self, strength):
        """
        Shows information about this sub to others based on the strength of
        scanners. This strength is at least zero (comms power - distance).
        This strength allows for secrecy and limited information.
        TODO: Make this way more interesting. It's currently just sub name.
        Could add direction of motion, whether it's got cargo etc.
        """
        subname = ""
        if strength > 0: subname = f" {self.sub.name}"
        return f"SUBMARINE{subname}"

    def scan(self):
        """
        Perform a scanner sweep of the local area.
        This finds all subs and objects in range, and returns them.
        """
        scanners_range = 2*self.sub.power.get_power("scanners") - 2
        my_position = self.sub.movement.get_position()
        events = explore_submap(my_position, scanners_range)
        for subname in get_teams():
            if subname == self.sub.name:
                continue
        
            sub = get_sub(subname)
            sub_position = sub.movement.get_position()
            dist = diagonal_distance(my_position, sub_position)
            if dist > scanners_range:
                continue

            event = sub.outward_broadcast(scanners_range - dist)
            direction = determine_direction(my_position, sub_position)
            if direction is None:
                event = f"{event} in your current square!"
            else:
                event = f"{event} in direction {direction}!"
            events.append(event)
        shuffle(events)
        return events

