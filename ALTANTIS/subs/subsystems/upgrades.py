"""
A subsystem for upgrades, handed to subs via keywords from control.
"""

from ALTANTIS.cogs.map import mass_weather
from typing import Tuple, Any, Optional, List

from ALTANTIS.utils.text import to_titled_list, list_to_and_separated
from ..sub import Submarine

VALID_UPGRADES = {"clarity": "Gives you unscrambled messages up to a distance of 2p (p = comms power) away from your submarine.",
                  "snipped": "Your crane cable is broken.",
                  "fastcrane": "Your crane now works at double speed (so only takes one tick to get its cargo).",
                  "blessing": "Your sub ignores movement penalties from weather.",
                  "overclocked": "Everything has +1 innate power.",
                  "shocked": "You cannot modify the power distribution of your submarine.",
                  "ticking": "Has a chance to explode and deal extra damage to you when hit. Also makes an annoying ticking noise.",
                  "wearfree": "You no longer gain engineering puzzles due to wear and tear. (This should only be given to a submarine in exceptional circumstances.)",
                  "stealthy": "Subs need 3+ scanning strength in order to see you.",
                  "camo": "Undamaged NPCs don't attack you. (Restrictions apply.)",
                  "triangulation": "Objects in the scanner now have their distance as well as direction.",
                  "antiplastic": "Damaging shots deal more damage to manmade structures.",
                  "anticarbon": "Damaging shots deal more damage to biological structures."}

class Upgrades():
    def __init__(self, sub : Submarine):
        self.sub = sub
        # Used for special abilities gifted by control.
        self.keywords = []
        # Used for events that should happen on a given turn.
        # Consists of (int, string, (fn name, argument)) triples.
        self.postponed_events : List[Tuple[int, str, Tuple[str, Any, Any]]] = []
    
    def upgrade_status(self) -> str:
        status = ""
        if len(self.keywords) > 0:
            status = f"You have active upgrades:\n"
            for keyword in self.keywords:
                if keyword in VALID_UPGRADES:
                    status += f"`{keyword}`: {VALID_UPGRADES[keyword]}\n"
                else:
                    status += f"`{keyword}`: Unknown functionality.\n"
        postponed = []
        for event in self.postponed_events:
            postponed.append(f"{event[1].title()} ({event[0]})")
        if len(postponed) > 0:
            status += f"Events happening in later turns: {list_to_and_separated(postponed)}.\n"
        if "ticking" in self.keywords:
            status += "Something makes an annoying ticking noise!\n"
        return status
    
    async def postponed_tick(self):
        unresolved : List[Tuple[int, str, Tuple[str, Any, Any]]] = []
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

    def add_keyword(self, keyword : str, turn_limit : Optional[int] = None, damage : int = 1) -> Optional[str]:
        if keyword not in self.keywords:
            self.keywords.append(keyword)
            if turn_limit is not None:
                verb = "dissapates" if damage <= 0 else "explodes"
                self.postponed_events.append((turn_limit, f"**{keyword}** {verb}", ("remove_equip", keyword, damage)))
            if keyword in VALID_UPGRADES:
                return f"Added {keyword}!"
            return f"Added {keyword}, but it is not implemented anywhere in code."
        return f"Could not add keyword {keyword}."

    def remove_keyword(self, keyword : str) -> bool:
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            return True
        return False
    
    async def remove_equip(self, keyword : str, damage : int = 1):
        if self.remove_keyword(keyword):
            self.sub.damage(damage)
            result = "fizzled out"
            if damage == 1:
                result = "exploded and dealt one damage"
            else:
                result = f"dramatically exploded and dealt {damage} damage"
            await self.sub.send_message(f"**{keyword.title()}** {result}!", "engineer")
    