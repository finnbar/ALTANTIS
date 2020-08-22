"""
All possible NPC types.
"""

import npc, world

class Squid(npc.NPC):
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.tick_count = 0
        self.health = 2
        self.treasure = "gold"
    
    async def on_tick(self):
        await self.damage_tick()
        if self.tick_count >= 3:
            self.tick_count -= 3
            for entity in world.all_in_square(self.x, self.y):
                if entity.name != self.name:
                    await entity.send_message(f"The squid {self.name.title()} blooped you for one damage!", "scientist")
                    entity.damage(1)
        else:
            self.tick_count += 1