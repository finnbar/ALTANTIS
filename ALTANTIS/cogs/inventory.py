from discord.ext import commands

from ALTANTIS.utils.consts import CONTROL_ROLE, CAPTAIN, CURRENCY_NAME
from ALTANTIS.utils.bot import perform, perform_async, perform_async_unsafe, get_team
from ALTANTIS.utils.actions import DiscordAction, Message, OKAY_REACT, FAIL_REACT
from ALTANTIS.utils.text import to_pair_list
from ALTANTIS.subs.state import with_sub, with_sub_async, get_sub
from ALTANTIS.npcs.npc import interact_in_square

class Inventory(commands.Cog):
    """
    Commands for trading with subs on the same space as you, and generally interacting with inventories.
    """
    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def drop(self, ctx, item):
        """
        Drops the item specified by <item>. You cannot drop key items (those ending in *).
        """
        await perform(drop_item, ctx, get_team(ctx.channel), item)

    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def trade(self, ctx, team, *args):
        """
        Begins a trade with <team>, where you offer item1 quantity1 item2 quantity2 and so on.
        For example: !trade team_name Fish 10 "Gold coin" 3
        """
        await perform_async(arrange_trade, ctx, get_team(ctx.channel), team, list(args))

    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def offer(self, ctx, *args):
        """
        Makes a counteroffer in your current trade, of form item1 quantity1 item2 quantity2...
        For example: !offer Fish 10 "Gold coin" 4
        """
        await perform_async(make_offer, ctx, get_team(ctx.channel), list(args))

    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def accept_trade(self, ctx):
        """
        Accepts the current trade. A trade will only complete once both parties have accepted the trade.
        """
        await perform_async(accept_offer, ctx, get_team(ctx.channel))

    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def reject_trade(self, ctx):
        """
        Rejects and ends the current trade.
        """
        await perform_async(reject_offer, ctx, get_team(ctx.channel))
    
    @commands.command()
    @commands.has_any_role(CAPTAIN, CONTROL_ROLE)
    async def interact(self, ctx, arg = None):
        """
        Some NPCs will ask you to call this.
        """
        await perform_async(sub_interacts, ctx, get_team(ctx.channel), arg)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def give(self, ctx, item, quantity : int = 1):
        """
        (CONTROL) Gives this team an <item> with optional <quantity>.
        """
        await perform_async_unsafe(give_item_to_team, ctx, get_team(ctx.channel), item, quantity)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def pay(self, ctx, amount : int):
        """
        (CONTROL) Pays this team <amount> money. Shorthand for !give with currency name.
        """
        await perform_async_unsafe(give_item_to_team, ctx, get_team(ctx.channel), CURRENCY_NAME, amount)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def take(self, ctx, item, quantity : int = 1):
        """
        (CONTROL) Take <quantity> of <item> away from this team. Do not use this during a trade.
        """
        await perform_async_unsafe(take_item_from_team, ctx, get_team(ctx.channel), item, quantity)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def get_paid(self, ctx, amount : int):
        """
        (CONTROL) Get paid by this team <amount> money. Shorthand for !take with currency name. Do not use this during a trade.
        """
        await perform_async_unsafe(take_item_from_team, ctx, get_team(ctx.channel), CURRENCY_NAME, amount)

async def arrange_trade(team : str, partner : str, items) -> DiscordAction:
    pair_list = []
    try:
        pair_list = to_pair_list(items)
    except ValueError as _:
        return Message("Input list is badly formatted.")
    sub = get_sub(team)
    partner_sub = get_sub(partner)
    if sub and partner_sub:
        return Message(await sub.inventory.begin_trade(partner_sub, pair_list))
    return Message("Didn't recognise the submarine asked for.")

async def make_offer(team : str, items) -> DiscordAction:
    pair_list = to_pair_list(items)
    if pair_list is None:
        return Message("Input list is badly formatted.")
    async def do_offer(sub):
        return Message(await sub.inventory.make_offer(pair_list))
    return await with_sub_async(team, do_offer, FAIL_REACT)

async def accept_offer(team : str) -> DiscordAction:
    async def do_accept(sub):
        return Message(await sub.inventory.accept_trade())
    return await with_sub_async(team, do_accept, FAIL_REACT)

async def reject_offer(team : str) -> DiscordAction:
    async def do_reject(sub):
        return Message(await sub.inventory.reject_trade())
    return await with_sub_async(team, do_reject, FAIL_REACT)

async def sub_interacts(team : str, arg) -> DiscordAction:
    async def do_interact(sub):
        message = await interact_in_square(sub, sub.movement.get_position(), arg)
        if message != "":
            return Message(message)
        return Message("Nothing to report.")
    return await with_sub_async(team, do_interact, FAIL_REACT)

async def give_item_to_team(team : str, item : str, quantity : int) -> DiscordAction:
    async def do_give(sub):
        if sub.inventory.add(item, quantity):
            await sub.send_message(f"Obtained {quantity}x {item.title()}!", "captain")
            return OKAY_REACT
        return FAIL_REACT
    return await with_sub_async(team, do_give, FAIL_REACT)

async def take_item_from_team(team : str, item : str, quantity : int) -> DiscordAction:
    async def do_take(sub):
        if sub.inventory.remove(item, quantity):
            await sub.send_message(f"Lost {quantity}x {item.title()}!", "captain")
            return OKAY_REACT
        return FAIL_REACT
    return await with_sub_async(team, do_take, FAIL_REACT)

def drop_item(team : str, item : str) -> DiscordAction:
    def drop(sub):
        return Message(sub.inventory.drop(item))
    return with_sub(team, drop, FAIL_REACT)