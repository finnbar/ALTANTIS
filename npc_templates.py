"""
All possible NPC types.
"""

import npc, world, control

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