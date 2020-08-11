"""
Inventory system for holding items, trading items and losing items.
Also features The Crane.
"""

from consts import CURRENCY_NAME
from world import pick_up_treasure, bury_treasure_at

class Inventory():
    def __init__(self, sub):
        self.sub = sub
        self.inventory = {CURRENCY_NAME: 1}

        # THE CRANE.
        # It takes two ticks to resolve - one to send it down and a second to
        # pull it back up.
        # crane_down is the state of the crane.
        self.crane_down = False
        # crane_holds is what the crane contains.
        self.crane_holds = None
        # schedule_crane is whether the crane command has been called.
        self.schedule_crane = False
    
    def add(self, item, quantity=1):
        if not item in self.inventory:
            self.inventory[item] = 0
        self.inventory[item] += quantity
        return True
    
    def remove(self, item, quantity=1):
        if not item in self.inventory:
            return False
        if self.inventory[item] < quantity:
            return False
        self.inventory[item] -= quantity
        return True
    
    def drop_crane(self):
        if not self.schedule_crane and not self.crane_down:
            self.schedule_crane = True
            return True
        return False
    
    def crane_tick(self):
        if self.sub.power.get_power("crane") == 0:
            # Drop what's currently being held.
            if self.crane_holds:
                bury_treasure_at(self.crane_holds, self.sub.movement.get_position())
                self.crane_holds = None
            return ""
        if self.schedule_crane and not self.crane_down:
            # The crane goes down!
            self.crane_down = True
            self.schedule_crane = False
            # Attempt to pick up the item.
            self.crane_holds = pick_up_treasure(self.sub.movement.get_position())
            return f"Crane went down and found {self.crane_holds}! Coming up next turn!"
        elif self.crane_down:
            # The crane comes back up! Oh no
            self.crane_down = False
            treasure = self.crane_holds
            self.add(treasure)
            self.crane_holds = None
            return f"Crane came back up with {treasure}!"
        return ""
    
    def status(self):
        message = ""

        for item in self.inventory:
            if self.inventory[item] > 0:
                message += f"{self.inventory[item]}x {item}\n"
        
        if message == "":
            return ""
        else:
            return f"**Inventory**\n{message}"