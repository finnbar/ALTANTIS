"""
All possible NPC types.
"""

import random

from ALTANTIS.utils.consts import CURRENCY_NAME, RESOURCES
from ALTANTIS.utils.control import notify_news
from ALTANTIS.world.world import get_square
from ALTANTIS.world.extras import all_in_submap, explode
from ALTANTIS.npcs.npc import NPC, add_npc

# TODO: DeepOne NPC, Large Storm Generator

class Squid(NPC):
    classname = "squid"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = [CURRENCY_NAME]
    
    async def attack(self):
        if self.tick_count >= 3:
            self.tick_count -= 3
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 1, f"{self.name()} blooped you for one damage!")
        else:
            self.tick_count += 1

class BigSquid(NPC):
    classname = "giant_squid"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 3
        self.treasure = [CURRENCY_NAME, CURRENCY_NAME]

    def name(self):
        # Override to add a space
        return f"Giant Squid (#{self.id})"
    
    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 1, f"{self.name()} blooped you for one damage!")
        else:
            self.tick_count += 1

class Octopus(NPC):
    classname = "octopus"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 1
        self.treasure = [random.choice(RESOURCES)]

    def name(self):
        # Override to add the fact that it's big
        return f"Giant Octopus (#{self.id})"
    
    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 2, f"{self.name()} constricted you for one damage!")
        else:
            self.tick_count += 1

class Shark(NPC):
    classname = "shark"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = [random.choice(RESOURCES)]
    
    async def attack(self):
        # TODO: retreat after attack?
        if self.tick_count >= 3:
            self.tick_count -= 3
            self.move_towards_sub(4)
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 1, f"{self.name()} snapped you for one damage!")
        else:
            self.tick_count += 1

class Whale(NPC):
    classname = "whale"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 5
        self.treasure = [CURRENCY_NAME] * 3

    async def on_tick(self):
        await super().on_tick()
        for sub in self.all_subs_in_square():
            await sub.send_message(f"{self.name()} is having a _whale_ of a time.", "captain")

class Dolphin(NPC):
    classname = "dolphin"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 2
        self.treasure = ["unexploded bomb*"]

    async def interact(self, *_):
        return "The dolphin made a few happy noises!"

class MantaRay(NPC):
    classname = "mantaray"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 2
        self.treasure = [random.choice(RESOURCES)] * 2
    
    def name(self):
        # Override to add a space
        return f"Manta Ray (#{self.id})"

    async def interact(self, *_):
        return "The manta ray swims happily!"
    
    async def deathrattle(self):
        hears_rattle = all_in_submap(self.get_position(), 5, npc_exclusions=[self.id])
        for entity in hears_rattle:
            await entity.send_message(f"Manta Ray at ({self.x}, {self.y}) was killed. The Manta Rayvenge Squad hears its cry!", "captain")
        # Then summon four eel as a "fuck you".
        locations = [(0,1), (1,0), (-1,0), (0,-1)]
        locations = list(map(lambda p: (self.x+p[0], self.y+p[1]), locations))
        for location in locations:
            add_npc("eel", location[0], location[1])

class Eel(NPC):
    classname = "eel"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 2
        self.treasure = [random.choice(RESOURCES)]
        self.tick_count = 0
    
    def name(self):
        # Override to add the fact that it's big
        return f"Giant Eel (#{self.id})"

    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            # First, move randomly:
            self.move(random.choice([-1,0,1]), random.choice([-1,0,1]))
            # Then attack:
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 1, f"{self.name()} zapped you for one damage and (temporarily) shocked your submarine!")
                sub.upgrades.add_keyword("shocked", 5, 0)
        else:
            self.tick_count += 1

class AnglerFish(NPC):
    classname = "angler"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = [CURRENCY_NAME, random.choice(RESOURCES)]
        self.stealth = 2

    def name(self):
        # Override to add a space
        return f"Angler Fish (#{self.id})"
    
    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 1, f"{self.name()} jumped out from hiding and did 1 damage!")
        else:
            self.tick_count += 1

class Urchin(NPC):
    classname = "urchin"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 2
        self.treasure = [random.choice(RESOURCES)]
        self.stealth = 1
        self.observant = True
        # Which subs were in this square previously.
        self.visited = []
    
    async def attack(self):
        new_visited = []
        for sub in self.all_subs_in_square():
            new_visited.append(sub.name)
            if sub.name not in self.visited:
                await self.do_attack(sub, 1, f"{self.name()} jumped out from hiding and did 1 damage on your arrival!")
        self.visited = new_visited

class Crab(NPC):
    classname = "crab"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.treasure = ["crab meat"]
    
    def name(self):
        # crab big
        return f"Giant Crab (#{self.id})"

    async def attack(self):
        for sub in self.all_subs_in_square():
            if sub.inventory.crane_down:
                # Snip the crane lead and otherwise mess it up.
                if await self.do_attack(sub, 2, f"{self.name()} snipped at your crane cable and caused a balance issue, dealing two damage!"):
                    sub.upgrades.add_keyword("snipped")
                    message = sub.inventory.crane_falters()
                    if message:
                        await sub.send_message(message, "captain")

class NewsBouy(NPC):
    classname = "bouy"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 5

    async def send_message(self, content, _):
        await notify_news(content)

class Mine(NPC):
    classname = "mine"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.countdown = 10

    async def on_tick(self):
        for sub in self.all_subs_in_square():
            if self.countdown <= 0:
                self.damage(1)
            else:
                self.countdown -= 1
                for sub in self.all_subs_in_square():
                    await sub.send_message(str(self.countdown), "captain")
    
    async def deathrattle(self):
        await explode(self.get_position(), 2)

class StormGenerator(NPC):
    classname = "stormer"
    async def on_tick(self):
        for dx in range(-2,3):
            for dy in range(-2,3):
                sq = get_square(self.x + dx, self.y + dy)
                if sq: sq.add_attribute("stormy")

    async def deathrattle(self):
        for dx in range(-2,3):
            for dy in range(-2,3):
                sq = get_square(self.x + dx, self.y + dy)
                if sq: sq.remove_attribute("stormy")

class GoldTrader(NPC):
    classname = "gold_trader"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.resource = random.choice(RESOURCES)

    def name(self):
        return f"{self.resource.title()} Trader (#{self.id})"
    
    async def on_tick(self):
        await super().on_tick()
        for sub in self.all_subs_in_square():
            await sub.send_message(f"{self.name()} here! Use `!interact 1` to pay 2 Gold for one {self.resource.title()}, or `!interact 2` to pay one {self.resource.title()} for 2 Gold.", "captain")

    async def interact(self, sub, option):
        if option == "1":
            if sub.inventory.remove("gold", 2):
                sub.inventory.add(self.resource, 1)
                return f"Traded two Gold for one {self.resource.title()}!"
            return "Could not perform that trade!"
        elif option == "2":
            if sub.inventory.remove(self.resource, 1):
                sub.inventory.add("gold", 2)
                return f"Traded one {self.resource.title()} for two Gold!"
            return "Could not perform that trade!"
        return "Invalid option."