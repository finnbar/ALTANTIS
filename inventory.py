"""
Inventory system for holding items, trading items and losing items.
Also features The Crane.
"""

from consts import CURRENCY_NAME

class Inventory():
    def __init__(self, sub):
        self.sub = sub
        self.inventory = {CURRENCY_NAME: 1}
    
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
    
    def status(self):
        message = ""

        for item in self.inventory:
            if self.inventory[item] > 0:
                message += f"{self.inventory[item]}x {item}\n"
        
        if message == "":
            return ""
        else:
            return f"**Inventory**\n{message}"