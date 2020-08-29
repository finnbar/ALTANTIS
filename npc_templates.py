"""
All possible NPC types.
"""

import npc, world, control, sub

class Squid(npc.NPC):
    classname = "squid"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = "gold"
    
    async def attack(self):
        if self.tick_count >= 3:
            self.tick_count -= 3
            for entity in world.all_in_square(self.get_position()):
                if entity.name != self.name:
                    await self.do_attack(entity, 1, f"The squid {self.name.title()} blooped you for one damage!")
        else:
            self.tick_count += 1

class NewsBouy(npc.NPC):
    classname = "bouy"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.health = 5

    async def send_message(self, content, _):
        await control.notify_news(content)

class GoldTrader(npc.NPC):
    classname = "gold_trader"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
    
    async def on_tick(self):
        await super().on_tick()
        for entity in world.all_in_square(self.get_position()):
            if type(entity) is sub.Submarine:
                await entity.send_message(f"Trader {self.name.title()} here! Use `!interact 1` to pay 2 Gold for one Circuitry, or `!interact 2` to pay one Circuitry for 2 Gold.", "captain")

    async def interact(self, sub, option):
        if option == "1":
            if sub.inventory.remove("gold", 2):
                sub.inventory.add("circuitry", 1)
                return "Traded two Gold for one Circuitry!"
            return "Could not perform that trade!"
        elif option == "2":
            if sub.inventory.remove("circuitry", 1):
                sub.inventory.add("gold", 2)
                return "Traded one Circuitry for two Gold!"
            return "Could not perform that trade!"
        return "Invalid option."