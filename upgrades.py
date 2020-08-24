"""
A subsystem for upgrades, handed to subs via keywords from control.
"""

from utils import to_titled_list, list_to_and_separated

class Upgrades():
    def __init__(self, sub):
        self.sub = sub
        # Used for special abilities gifted by control.
        self.keywords = []
        # Used for events that should happen on a given turn.
        # Consists of (int, string, (fn name, argument)) triples.
        self.postponed_events = []
    
    def upgrade_status(self):
        status = ""
        if len(self.keywords) > 0:
            status += f"You have active upgrades: {to_titled_list(self.keywords)}.\n"
        postponed = []
        for event in self.postponed_events:
            postponed.append(f"{event[1].title()} ({event[0]})")
        if len(postponed) > 0:
            status += f"Events happening in later turns: {list_to_and_separated(postponed)}.\n"
        return status
    
    async def postponed_tick(self):
        unresolved = []
        for event in self.postponed_events:
            (count, desc, fn) = event
            if count <= 1:
                # Resolve the event.
                # As Python cannot serialise functions, we have to define cases.
                if fn[0] == "remove_equip":
                    (_, keyword, damage) = fn
                    await self.remove_equip(keyword, damage)
            else:
                unresolved.append((count-1, desc, fn))
        self.postponed_events = unresolved

    def add_keyword(self, keyword, turn_limit=None, damage=1):
        if keyword not in self.keywords:
            self.keywords.append(keyword)
            if turn_limit is not None:
                verb = "dissapates" if damage <= 0 else "explodes"
                self.postponed_events.append((turn_limit, f"**{keyword}** {verb}", ("remove_equip", keyword, damage)))
            return True
        return False

    def remove_keyword(self, keyword):
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            return True
        return False
    
    async def remove_equip(self, keyword, damage=1):
        if self.remove_keyword(keyword):
            self.sub.damage(damage)
            result = "fizzled out"
            if damage == 1:
                result = "exploded and dealt one damage"
            else:
                result = f"dramatically exploded and dealt {damage} damage"
            await self.sub.send_message(f"**{keyword.title()}** {result}!", "engineer")
    