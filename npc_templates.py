"""
All possible NPC types.
"""

import npc, world, control, sub
from consts import CURRENCY_NAME, RESOURCES

import random

class Squid(npc.NPC):
    classname = "squid"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = [CURRENCY_NAME]
    
    async def attack(self):
        if self.tick_count >= 3:
            self.tick_count -= 3
            for entity in world.all_in_square(self.get_position()):
                if entity.name != self.name:
                    await self.do_attack(entity, 1, f"The squid {self.name.title()} blooped you for one damage!")
        else:
            self.tick_count += 1

class BigSquid(npc.NPC):
    classname = "giant_squid"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.tick_count = 0
        self.health = 3
        self.treasure = [CURRENCY_NAME, CURRENCY_NAME]
    
    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            for entity in world.all_in_square(self.get_position()):
                if entity.name != self.name:
                    await self.do_attack(entity, 1, f"The giant squid {self.name.title()} blooped you for one damage!")
        else:
            self.tick_count += 1

class Octopus(npc.NPC):
    classname = "octopus"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.tick_count = 0
        self.health = 1
        self.treasure = [random.choice(RESOURCES)]
    
    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            for entity in world.all_in_square(self.get_position()):
                if entity.name != self.name:
                    await self.do_attack(entity, 2, f"The octopus {self.name.title()} constricted you for one damage!")
        else:
            self.tick_count += 1

class Shark(npc.NPC):
    classname = "shark"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = [random.choice(RESOURCES)]
    
    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            self.move_towards_sub(4)
            for entity in world.all_in_square(self.get_position()):
                if entity.name != self.name:
                    await self.do_attack(entity, 1, f"The shark {self.name.title()} snapped you for one damage!")
        else:
            self.tick_count += 1

class Whale(npc.NPC):
    classname = "whale"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.health = 5
        self.treasure = [CURRENCY_NAME] * 3

    async def on_tick(self):
        await super().on_tick()
        for entity in world.all_in_square(self.get_position()):
            if type(entity) is sub.Submarine:
                await entity.send_message(f"The whale {self.name.title()} is having a _whale_ of a time.", "captain")

class Dolphin(npc.NPC):
    classname = "dolphin"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.health = 2
        self.treasure = ["unexploded bomb*"]

    async def interact(self, *_):
        return "The dolphin made a few happy noises!"

class MantaRay(npc.NPC):
    classname = "mantaray"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.health = 2
        self.treasure = [random.choice(RESOURCES)] * 2

    async def interact(self, *_):
        return "The manta ray swims happily!"
    
    async def deathrattle(self):
        await super().deathrattle()
        # Then summon four eel as a "fuck you".
        locations = [(0,1), (1,0), (-1,0), (0,-1)]
        locations = list(map(lambda p: (self.x+p[0], self.y+p[1]), locations))
        rand_id = random.randrange(100000)
        for location in locations:
            npc.add_npc(f"Manta Ray Revenge Squad ({location[0]}{location[1]}{rand_id})", "eel", location[0], location[1])

class Eel(npc.NPC):
    classname = "eel"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.health = 2
        self.treasure = [random.choice(RESOURCES)]
        self.tick_count = 0
    
    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            # First, move randomly:
            self.move(random.choice([-1,0,1]), random.choice([-1,0,1]))
            # Then attack:
            for entity in world.all_in_square(self.get_position()):
                if type(entity) is sub.Submarine:
                    await self.do_attack(entity, 2, f"The eel {self.name.title()} zapped you for one damage and (temporarily) shocked your submarine!")
                    entity.upgrades.add_keyword("shocked", 5, 0)
        else:
            self.tick_count += 1

class AnglerFish(npc.NPC):
    classname = "angler"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = [CURRENCY_NAME, random.choice(RESOURCES)]
        self.stealth = 2
    
    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            for entity in world.all_in_square(self.get_position()):
                if entity.name != self.name:
                    await self.do_attack(entity, 1, f"The angler fish {self.name.title()} jumped out from hiding and did 1 damage!")
        else:
            self.tick_count += 1

class Urchin(npc.NPC):
    classname = "urchin"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.health = 2
        self.treasure = [random.choice(RESOURCES)]
        self.stealth = 1
        # Which subs were in this square previously.
        self.visited = []
    
    async def attack(self):
        new_visited = []
        for entity in world.all_in_square(self.get_position()):
            if type(entity) is sub.Submarine:
                new_visited.append(entity.name)
                if entity.name not in self.visited:
                    await self.do_attack(entity, 1, f"The urchin {self.name.title()} jumped out from hiding and did 1 damage on your arrival!")
        self.visited = new_visited

class Crab(npc.NPC):
    classname = "crab"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.treasure = ["crab meat"]
    
    async def attack(self):
        for entity in world.all_in_square(self.get_position()):
            if type(entity) is sub.Submarine:
                if entity.inventory.crane_down:
                    # Snip the crane lead and otherwise mess it up.
                    if await self.do_attack(entity, 2, f"The crab {self.name.title()} snipped at your crane cable and caused a balance issue, dealing two damage!"):
                        entity.upgrades.add_keyword("snipped")
                        message = entity.inventory.crane_falters()
                        if message:
                            await entity.send_message(message, "captain")

class NewsBouy(npc.NPC):
    classname = "bouy"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.health = 5

    async def send_message(self, content, _):
        await control.notify_news(content)

class Mine(npc.NPC):
    classname = "mine"
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.countdown = 10

    async def on_tick(self):
        for entity in world.all_in_square(self.get_position()):
            if type(entity) is sub.Submarine:
                if self.countdown <= 0:
                    self.damage(1)
                else:
                    self.countdown -= 1
                    for entity in world.all_in_square(self.get_position()):
                        await entity.send_message(str(self.countdown), "captain")
    
    async def deathrattle(self):
        await world.explode(self.get_position(), 2)

class StormGenerator(npc.NPC):
    classname = "stormer"
    async def on_tick(self):
        for dx in range(-2,3):
            for dy in range(-2,3):
                sq = world.get_square(self.x + dx, self.y + dy)
                if sq: sq.add_attribute("stormy")

    async def deathrattle(self):
        for dx in range(-2,3):
            for dy in range(-2,3):
                sq = world.get_square(self.x + dx, self.y + dy)
                if sq: sq.remove_attribute("stormy")

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