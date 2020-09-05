"""
All possible NPC types.
"""

import random

from ALTANTIS.utils.consts import CURRENCY_NAME, RESOURCES
from ALTANTIS.utils.control import notify_news
from ALTANTIS.world.world import get_square
from ALTANTIS.world.extras import all_in_submap, explode
from ALTANTIS.npcs.npc import NPC, add_npc

# TODO: Large Storm Generator

class PhotographableNPC(NPC):
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.photo = "https://www.warwicktabletop.co.uk/static/megagame/2020/"

    async def interact(self, sub, _) -> str:
        return self.take_photo(sub)
    
    def is_carbon(self) -> bool:
        return True

class Squid(PhotographableNPC):
    classname = "squid"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = [CURRENCY_NAME]
        self.photo += "squid.png"
    
    async def attack(self):
        if self.tick_count >= 3:
            self.tick_count -= 3
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 1, f"{self.name()} blooped you for one damage!")
        else:
            self.tick_count += 1

class BigSquid(PhotographableNPC):
    classname = "giant_squid"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 3
        self.treasure = [CURRENCY_NAME, CURRENCY_NAME]
        self.typename = "Giant Squid"
        self.photo += "giant-squid.png"

    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 1, f"{self.name()} blooped you for one damage!")
        else:
            self.tick_count += 1

class Octopus(PhotographableNPC):
    classname = "octopus"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 1
        self.treasure = [random.choice(RESOURCES)]
        self.typename = "Giant Octopus"
        self.photo += "giant-octopus.png"

    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 2, f"{self.name()} constricted you for one damage!")
        else:
            self.tick_count += 1

class Shark(PhotographableNPC):
    classname = "shark"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = [random.choice(RESOURCES)]
    
    async def attack(self):
        if self.tick_count >= 3:
            self.tick_count -= 3
            self.move_towards_sub(4)
            targets = self.all_subs_in_square()
            for sub in targets:
                await self.do_attack(sub, 1, f"{self.name()} snapped you for one damage!")
            if len(targets) > 0:
                self.move(random.choice([-1,0,1]), random.choice([-1,0,1]))
        else:
            self.tick_count += 1

class Hammerhead(Shark):
    classname = "hammerhead"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.typename = "Hammerhead Shark"
        self.photo += "hammerhead.png"

class Bull(Shark):
    classname = "bullshark"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.typename = "Bull Shark"
        self.photo += "bull-shark.png"

class Orca(Shark):
    classname = "orca"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.photo += "orca.png"

class Whale(PhotographableNPC):
    classname = "whale"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 5
        self.treasure = [CURRENCY_NAME] * 3

    async def on_tick(self):
        await super().on_tick()
        for sub in self.all_subs_in_square():
            await sub.send_message(f"{self.name()} is having a _whale_ of a time.", "captain")

class WhaleShark(Whale):
    classname = "whaleshark"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.typename = "Whale Shark"
        self.photo += "whale-shark.png"
        self.treasure.append("petuniabowl")

class Humpback(Whale):
    classname = "humpback"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.photo += "humpback-whale.png"

class Dolphin(PhotographableNPC):
    classname = "dolphin"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 2
        self.treasure = ["unexploded bomb*"]
        self.photo += "dolphin.png"

    async def interact(self, sub, arg):
        photo_message = super().interact(sub, arg)
        return f"The dolphin made a few happy noises!\n{photo_message}"

class MantaRay(PhotographableNPC):
    classname = "mantaray"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 2
        self.treasure = [random.choice(RESOURCES)] * 2
        self.typename = "Manta Ray"
        self.photo += "manta-ray.png"
    
    async def interact(self, sub, arg):
        photo_message = super().interact(sub, arg)
        return f"The manta ray swims happily!\n{photo_message}"
    
    async def deathrattle(self):
        hears_rattle = all_in_submap(self.get_position(), 5, npc_exclusions=[self.id])
        for entity in hears_rattle:
            await entity.send_message(f"Manta Ray at ({self.x}, {self.y}) was killed. The Manta Rayvenge Squad hears its cry!", "captain")
        # Then summon four eel as a "fuck you".
        locations = [(0,1), (1,0), (-1,0), (0,-1)]
        locations = list(map(lambda p: (self.x+p[0], self.y+p[1]), locations))
        for location in locations:
            add_npc("eel", location[0], location[1], None)

class Turtle(PhotographableNPC):
    classname = "turtle"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 2
        self.treasure = [CURRENCY_NAME] * 3
        self.photo += "turtle.png"
    
    async def interact(self, sub, arg):
        photo_message = super().interact(sub, arg)
        return f"The turtle swims happily!\n{photo_message}"
    
    async def deathrattle(self):
        hears_rattle = all_in_submap(self.get_position(), 5, npc_exclusions=[self.id])
        for entity in hears_rattle:
            await entity.send_message(f"Turtle at ({self.x}, {self.y}) was killed. The Turtle Revenge Squad hears its cry!", "captain")
        # Then summon four eel as a "fuck you".
        locations = [(0,1), (1,0), (-1,0), (0,-1)]
        locations = list(map(lambda p: (self.x+p[0], self.y+p[1]), locations))
        for location in locations:
            add_npc("squid", location[0], location[1], None)

class Eel(PhotographableNPC):
    classname = "eel"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 2
        self.treasure = [random.choice(RESOURCES)]
        self.tick_count = 0
        self.typename = "Giant Eel"
        self.photo += "electric-eel.png"
    
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

class AnglerFish(PhotographableNPC):
    classname = "angler"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = [CURRENCY_NAME, random.choice(RESOURCES)]
        self.stealth = 2
        self.typename = "Angler Fish"
        self.photo += "angler-fish.png"

    async def attack(self):
        if self.tick_count >= 2:
            self.tick_count -= 2
            for sub in self.all_subs_in_square():
                await self.do_attack(sub, 1, f"{self.name()} jumped out from hiding and did 1 damage!")
        else:
            self.tick_count += 1

class Urchin(PhotographableNPC):
    classname = "urchin"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 2
        self.treasure = [random.choice(RESOURCES)]
        self.stealth = 1
        self.observant = True
        # Which subs were in this square previously.
        self.visited = []
        self.photo += "giant-sea-urchin.png"
    
    async def attack(self):
        new_visited = []
        for sub in self.all_subs_in_square():
            new_visited.append(sub.name)
            if sub.name not in self.visited:
                await self.do_attack(sub, 1, f"{self.name()} jumped out from hiding and did 1 damage on your arrival!")
        self.visited = new_visited

class Crab(PhotographableNPC):
    classname = "crab"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.treasure = ["crab meat"]
        self.typename = "Giant Crab"
        self.photo += "giant-crab.png"
    
    async def attack(self):
        for sub in self.all_subs_in_square():
            if sub.inventory.crane_down:
                # Snip the crane lead and otherwise mess it up.
                if await self.do_attack(sub, 2, f"{self.name()} snipped at your crane cable and caused a balance issue, dealing two damage!"):
                    sub.upgrades.add_keyword("snipped")
                    message = sub.inventory.crane_falters()
                    if message:
                        await sub.send_message(message, "captain")

class Jellyfish(PhotographableNPC):
    classname = "jellyfish"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.stealth = 2
        self.photo += "giant-jellyfish.png"

class DeepOne(NPC):
    classname = "deepone"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 5
    
    async def attack(self):
        self.move_towards_sub(4)
        targets = self.all_subs_in_square()
        for sub in targets:
            if not "culty" in sub.upgrades.keywords:
                await self.do_attack(sub, 1, f"{self.name()} did one eldrich damage!")
    
    def is_carbon(self) -> bool:
        return True

class Ears(NPC):
    classname = "ears"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 3
    
    async def attack(self):
        parent = self.get_parent()
        if parent is None:
            return
        scanned = all_in_submap(self.get_position(), 1, [parent._name], [self.id])
        message = ""
        if len(scanned) == 0:
            return
        for entity in scanned:
            message += f"**{entity.name()}** at ({entity.x}, {entity.y})\n"
        await parent.send_message(f"**Ears** (#{self.id}) scanned this turn:\n{message}", "scientist")
    
    async def send_message(self, content, channel):
        await super().send_message(content, channel)
        parent = self.get_parent()
        if parent is not None:
            full_message = f"Event from Ears ({self.x}, {self.y}):\n{content}"
            await parent.send_message(full_message, "scientist")

class DeepOneTwo(DeepOne):
    classname = "deeponetwo"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.stealth = 2

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
        self.stealth = 1

    async def attack(self):
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
        await super().on_tick()
        for dx in range(-2,3):
            for dy in range(-2,3):
                sq = get_square(self.x + dx, self.y + dy)
                if sq: sq.add_attribute("weather", "storm")

    async def deathrattle(self):
        await super().deathrattle()
        for dx in range(-2,3):
            for dy in range(-2,3):
                sq = get_square(self.x + dx, self.y + dy)
                if sq: sq.add_attribute("weather", "normal")

class RoughSeasGenerator(NPC):
    classname = "rougher"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.storm_dist = 0
        self.tick_count = 0
        self.stealth = 13
        self.health = 100

    async def on_tick(self):
        await super().on_tick()
        self.tick_count += 1
        if self.tick_count >= 2:
            self.tick_count -= 2
            # Make all squares which are storm_dist away rough seas.
            # Because we use diagonal distance, this is a square perimeter.
            sd = self.storm_dist
            corners = [(sd, sd), (-sd, -sd)]
            for corner in corners:
                for x in range(-sd, sd+1):
                    sq = get_square(self.x+x, self.y+corner[1])
                    if sq: sq.add_attribute("weather", "rough")
                for y in range(-sd, sd+1):
                    sq = get_square(self.x+corner[0], self.y+y)
                    if sq: sq.add_attribute("weather", "rough")
            self.storm_dist += 1
    
    async def deathrattle(self):
        await super().deathrattle()
        sd = self.storm_dist
        for dx in range(-sd, sd+1):
            for dy in range(-sd, sd+1):
                sq = get_square(self.x+dx, self.y+dy)
                if sq: sq.add_attribute("weather", "normal")

class Trader(NPC):
    classname = "trader"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.resource = random.choice(RESOURCES)
        self.typename = f"{self.resource.title()} Trader"

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

class Quarry(NPC):
    classname = "quarry"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 14
    
    async def on_tick(self):
        await super().on_tick()
        if random.random() > 0.6:
            square = get_square(self.x, self.y)
            if square: square.bury_treasure("plating")
    
    def is_weak(self) -> bool:
        return False

class BreedingGround(NPC):
    classname = "breeding"
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.health = 10
    
    async def on_tick(self):
        await super().on_tick()
        if random.random() > 0.6:
            square = get_square(self.x, self.y)
            if square: square.bury_treasure("specimen")
    
    def is_weak(self) -> bool:
        return False
    
    def is_carbon(self) -> bool:
        return True

ALL_NPCS = [AnglerFish, BigSquid, BreedingGround, Bull, Crab, DeepOne, DeepOneTwo, Dolphin, Ears, Eel, Trader, Hammerhead, Humpback, Jellyfish, MantaRay, Mine, NewsBouy, Octopus, Orca, Quarry, RoughSeasGenerator, Squid, StormGenerator, Turtle, Urchin]
