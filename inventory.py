"""
Inventory system for holding items, trading items and losing items.
Also features The Crane.
"""

from consts import CURRENCY_NAME
from world import pick_up_treasure, bury_treasure_at
from utils import list_to_and_separated
from control import notify_control

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

        # TRADING
        # An aside: we don't save this data because it is difficult to serialise
        # and restoring an incomplete trade isn't actually helpful.
        # Who you're trading with, as a Submarine object.
        self.trading_partner = None
        # What you've offered.
        self.offer = {}
        self.accepting = False
        self.my_turn = False
    
    def add(self, item, quantity=1):
        if not item in self.inventory:
            self.inventory[item] = 0
        self.inventory[item] += quantity
        return True
    
    def add_many(self, items):
        for item in items:
            self.add(item, items[item])
        return True
    
    def remove(self, item, quantity=1):
        if not item in self.inventory:
            return False
        if self.inventory[item] < quantity:
            return False
        self.inventory[item] -= quantity
        return True
    
    def remove_many(self, items):
        for item in items:
            if not self.remove(item, items[item]):
                return False
        return True
    
    def drop_crane(self):
        if not self.schedule_crane and not self.crane_down:
            self.schedule_crane = True
            return True
        return False
    
    def send_crane_down(self):
        # The crane goes down!
        self.crane_down = True
        self.schedule_crane = False
        # Attempt to pick up the item.
        self.crane_holds = pick_up_treasure(self.sub.movement.get_position())
    
    async def send_crane_up(self):
        # The crane comes back up! Oh no
        self.crane_down = False
        treasure = self.crane_holds
        self.add(treasure)
        self.crane_holds = None
        await notify_control(f"**{self.sub.name}** picked up treasure **{treasure}**!")
        return treasure
    
    async def crane_tick(self):
        if self.sub.power.get_power("crane") == 0:
            # Drop what's currently being held.
            if self.crane_holds:
                treasure = self.crane_holds
                bury_treasure_at(treasure, self.sub.movement.get_position())
                self.crane_holds = None
                return f"Dropped {treasure} because the crane was unpowered..."
            return ""
        if self.schedule_crane and not self.crane_down:
            self.send_crane_down()
            if self.sub.power.get_power("crane") == 1:
                return f"Crane went down and found a treasure chest! Coming up next turn!"
            treasure = await self.send_crane_up()
            return f"Crane went down and up again, finding {treasure}!"
        elif self.crane_down:
            treasure = await self.send_crane_up()
            return f"Crane came back up with {treasure}!"
        return ""

    def valid_offer(self, items):
        """
        Formats an offer ((item, quantity) pairs) into a valid one, or returns None if it is not valid.
        """
        # First, construct the offer (just in case repeats are included).
        offer = {}
        for (item, quantity) in items:
            if quantity <= 0:
                return None
            if item not in offer:
                offer[item] = 0
            offer[item] += quantity
        # Then check against the quantities listed:
        for item in offer:
            if item not in self.inventory:
                return None
            if offer[item] > self.inventory[item]:
                return None
        return offer
    
    def offer_as_text(self, offer):
        if len(offer) == 0:
            return "nothing"
        offer_list = []
        for item in offer:
            offer_list.append(f"{offer[item]}x {item}")
        return list_to_and_separated(offer_list)
    
    async def begin_trade(self, partner, items):
        """
        Begin a trade with <partner> and the opening offer <items>.
        partner is a sub object, items is [(item, quantity), ...]
        """
        # Check that both of you are in the same place.
        if self.sub.movement.get_position() != partner.movement.get_position():
            return "You must be in the same location to trade."

        # Check that both you and partner are free to trade.
        if self.trading_partner is not None:
            return "You cannot start a trade while you have an ongoing trade."
        if partner.inventory.trading_partner is not None:
            return "You cannot trade with someone who is currently busy trading."

        # Check that the offer made is okay.
        offer = self.valid_offer(items)
        if not offer:
            return "Offer provided is impossible."
        
        # If all these checks pass, commence the trade!
        self.trading_partner = partner
        self.offer = offer
        self.accepting = False
        self.my_turn = False
        offer_text = self.offer_as_text(offer)
        await partner.inventory.received_trade(self.sub, offer_text)
        return f"You have offered **{offer_text}** to {partner.name}. Wait for them to respond to the trade, and then you may give a counteroffer with `!offer`, `!accept_trade` if you agree with what they've said, or `!reject_trade` if you don't want to trade anymore. You have until either sub next moves to complete the trade."

    async def received_trade(self, sub, offer_text):
        self.accepting = False
        self.trading_partner = sub
        self.my_turn = True
        await self.sub.send_message(f"**{sub.name}** asked for trade! They are offering **{offer_text}**. Respond with `!offer` to present your side of the trade, `!accept_trade` if you want to offer nothing in exchange, or `!reject_trade` if you don't want to trade. You have until either sub next moves to complete the trade.", "captain")
    
    async def reject_trade(self):
        """
        End a currently running trade.
        """
        if not self.trading_partner:
            return None

        partner_name = self.trading_partner.name
        self.trading_partner.inventory.reset_trade_state()
        self.reset_trade_state()
        await self.trading_partner.send_message(f"Trade with **{self.sub.name}** cancelled due to rejection.", "captain")
        return f"Trade with **{partner_name}** cancelled due to rejection."
    
    def reset_trade_state(self):
        self.offer = {}
        self.accepting = False
        self.my_turn = False
        self.trading_partner = None
    
    def timeout_trade(self):
        """
        Timeout a currently running trade.
        """
        if self.trading_partner is None:
            return {}
        partner = self.trading_partner
        self.reset_trade_state()
        partner.inventory.reset_trade_state()
        return {self.sub.name: f"Trade with {partner.name} cancelled due to timeout.",
                partner.name: f"Trade with {self.sub.name} cancelled due to timeout."}
    
    async def make_offer(self, items):
        """
        Modify your existing offer in this trade.
        """
        if not self.trading_partner:
            return "You must have a trade in progress to be able to make an offer!"
        if not self.my_turn:
            return "You must wait for an offer before you can make a counteroffer!"
        offer = self.valid_offer(items)
        if offer is None:
            return "You must provide a valid offer!"
        self.offer = offer
        self.my_turn = False
        self.accepting = False
        offer_text = self.offer_as_text(offer)
        await self.trading_partner.inventory.received_offer(offer_text)
        return f"Counteroffer of **{offer_text}** made."
    
    async def received_offer(self, offer_text):
        self.my_turn = True
        self.accepting = False
        await self.sub.send_message(f"Received counteroffer of **{offer_text}**.", "captain")
    
    async def accept_trade(self):
        self.accepting = True
        if not self.trading_partner.inventory.accepting:
            self.my_turn = False
            await self.trading_partner.inventory.received_accept()
            return "Accepted offer! Waiting on trade partner to accept as well."
        # The trade should be done now!
        # First, remove from inventories.
        self.remove_many(self.offer)
        self.trading_partner.inventory.remove_many(self.trading_partner.inventory.offer)
        # Then swap offers, and add them to inventories.
        self.offer, self.trading_partner.inventory.offer = self.trading_partner.inventory.offer, self.offer
        self.add_many(self.offer)
        self.trading_partner.inventory.add_many(self.trading_partner.inventory.offer)
        await self.trading_partner.send_message("Trade completed.", "captain")
        self.trading_partner.inventory.reset_trade_state()
        self.reset_trade_state()
        return "Trade completed."

    async def received_accept(self):
        self.my_turn = True
        await self.sub.send_message("Trading partner accepted this offer! Please run `!accept_trade` if you accept it as well, otherwise you can continue to make counteroffers or even reject the trade.", "captain")

    def status(self):
        message = ""

        for item in self.inventory:
            if self.inventory[item] > 0:
                message += f"{self.inventory[item]}x {item}\n"
        
        if message == "":
            return ""
        else:
            return f"**Inventory**\n{message}"