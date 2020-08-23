"""
The main entry point for our bot, which tells Discord what commands the bot can
perform and how to do so.
"""

import os

from discord.ext import commands, tasks
from dotenv import load_dotenv
from typing import Optional

from actions import *
from game import perform_timestep, load_game
from utils import OKAY_REACT
from consts import *
from control import init_control_notifs, init_news_notifs

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!")

# Main game loop
@tasks.loop(seconds=GAME_SPEED)
async def main_loop():
    await perform_timestep(main_loop.current_loop)

class Movement(commands.Cog):
    """
    All commands that allow you to move the submarine.
    """
    @commands.command(name="setdir")
    @commands.has_role(CAPTAIN)
    async def player_move(self, ctx, direction):
        """
        Sets the direction of your submarine to <direction>.
        """
        await perform(move, ctx, direction, get_team(ctx.author))

    @commands.command(name="force_setdir")
    @commands.has_role(CONTROL_ROLE)
    async def control_move(self, ctx, team, direction):
        """
        (CONTROL) Forces <team>'s submarine to a given direction. Does not inform them.
        """
        await perform_unsafe(move, ctx, direction, team)

    @commands.command(name="teleport")
    @commands.has_role(CONTROL_ROLE)
    async def teleport_sub(self, ctx, team, x : int, y : int):
        """
        (CONTROL) Teleports <teams>'s submarine to a given (<x>, <y>). Does not inform them.
        Also does _not_ check if the position is blocked, but does check if it's a valid point in the world.
        """
        await perform_unsafe(teleport, ctx, team, x, y)

    @commands.command(name="activate")
    @commands.has_role(CAPTAIN)
    async def on(self, ctx):
        """
        Activates your submarine, allowing it to move and do actions in real-time.
        """
        await perform_async(set_activation, ctx, get_team(ctx.author), True)

    @commands.command(name="deactivate")
    @commands.has_role(CAPTAIN)
    async def off(self, ctx):
        """
        Deactivates your submarine, stopping it from moving and performing actions.
        Needed for docking.
        """
        await perform_async(set_activation, ctx, get_team(ctx.author), False)

class Status(commands.Cog):
    """
    All commands that get the status of your submarine and its local environment.
    """
    @commands.command(name="map")
    @commands.has_role(CAPTAIN)
    async def player_map(self, ctx):
        """
        Shows a map of the world, including your submarine!
        """
        await perform(print_map, ctx, get_team(ctx.author))

    @commands.command(name="mapall")
    @commands.has_role(CONTROL_ROLE)
    async def control_map(self, ctx, *opts):
        """
        (CONTROL) Shows a map of the world, including all submarines.
        """
        if opts == ():
            await perform_unsafe(print_map, ctx, None, True)
        else:
            await perform_unsafe(print_map, ctx, None, list(opts))
    
    @commands.command(name="zoom")
    @commands.has_role(CONTROL_ROLE)
    async def zoom(self, ctx, x : int, y : int):
        """
        (CONTROL) Gives all details of a given square <x>, <y>.
        """
        await perform_unsafe(zoom_in, ctx, x, y, main_loop)

    @commands.command(name="status")
    async def status(self, ctx):
        """
        Reports the status of the submarine, including power and direction.
        """
        await perform(get_status, ctx, get_team(ctx.author), main_loop)
    
    @commands.command(name="scan")
    async def scan(self, ctx):
        """
        Repeats the scan message sent at the start of the current tick.
        """
        await perform(get_scan, ctx, get_team(ctx.author))

class PowerManagement(commands.Cog):
    """
    Commands for powering, unpowering, healing and damaging subsystems.
    """
    @commands.command(name="power")
    @commands.has_role(ENGINEER)
    async def power(self, ctx, *systems):
        """
        Gives one power to all of <systems> (any number of systems, can repeat).
        Fails if this would overload the power.
        NOTE: This is cumulative - it acts based on all previous calls to this (before the game tick).
        """
        await perform(power_systems, ctx, get_team(ctx.author), list(systems))

    @commands.command(name="force_power")
    @commands.has_role(CONTROL_ROLE)
    async def control_power(self, ctx, team, *systems):
        """
        (CONTROL) Forces <team> to give one power to all of <systems>.
        """
        await perform_unsafe(power_systems, ctx, team, list(systems))

    @commands.command(name="unpower")
    @commands.has_role(ENGINEER)
    async def unpower(self, ctx, *systems):
        """
        Removes one power from all of <systems> (any number of systems, can repeat).
        Fails if a system would have less than zero power.
        NOTE: This is cumulative - it acts based on all previous calls to this (before the game tick).
        """
        await perform(unpower_systems, ctx, get_team(ctx.author), list(systems))

    @commands.command(name="force_unpower")
    @commands.has_role(CONTROL_ROLE)
    async def control_unpower(self, ctx, team, *systems):
        """
        (CONTROL) Forces <team> to remove one power from all of <systems>.
        """
        await perform_unsafe(unpower_systems, ctx, team, list(systems))
    
    @commands.command(name="damage")
    @commands.has_role(CONTROL_ROLE)
    async def damage(self, ctx, team, amount : int, reason=""):
        """
        (CONTROL) Forces <team> to take <amount> damage at next loop. You can optionally specify a <reason> which will be messaged to them before.
        """
        await perform_async(deal_damage, ctx, team, amount, reason)

    @commands.command(name="heal")
    @commands.has_role(CONTROL_ROLE)
    async def perform_healing(self, ctx, team, amount : int, reason=""):
        """
        (CONTROL) Forces <team> to take <amount> healing at next loop. You can optionally specify a <reason> which will be messaged to them before.
        """
        await perform_async(heal_up, ctx, team, amount, reason)

class UpgradeManagement(commands.Cog):
    """
    Commands for upgrading and downgrading submarines.
    """
    @commands.command(name="upgrade")
    @commands.has_role(CONTROL_ROLE)
    async def upgrade(self, ctx, team, amount : int):
        """
        (CONTROL) Upgrades <team>'s reactor by <amount>.
        You can specify a negative number, but this will not check that the resulting state makes sense (that is, the team is not using more power than they have) - in general you should use !damage instead.
        """
        await perform_async_unsafe(upgrade_sub, ctx, team, amount)

    @commands.command(name="upgrade_system")
    @commands.has_role(CONTROL_ROLE)
    async def upgrade_system(self, ctx, team, system, amount : int):
        """
        (CONTROL) Upgrades <team>'s system by <amount>.
        You can specify a negative number to downgrade, and it will check that this makes sense.
        """
        await perform_async_unsafe(upgrade_sub_system, ctx, team, system, amount)

    @commands.command(name="upgrade_innate")
    @commands.has_role(CONTROL_ROLE)
    async def upgrade_innate(self, ctx, team, system, amount : int):
        """
        (CONTROL) Upgrades <team>'s innate system by <amount>.
        You can specify a negative number to downgrade, and it will check that this makes sense.
        """
        await perform_async_unsafe(upgrade_sub_innate, ctx, team, system, amount)

    @commands.command(name="install_system")
    @commands.has_role(CONTROL_ROLE)
    async def new_system(self, ctx, team, system):
        """
        (CONTROL) Gives <team> access to new system <system>.
        """
        await perform_async_unsafe(add_system, ctx, team, system)
    
    @commands.command(name="install_keyword")
    @commands.has_role(CONTROL_ROLE)
    async def install_keyword(self, ctx, team, keyword, turn_limit : Optional[int] = None):
        """
        (CONTROL) Gives <team> a brand new <keyword>! (This is for upgrades outside of power.)
        """
        await perform_async_unsafe(add_keyword_to_sub, ctx, team, keyword, turn_limit)

    @commands.command(name="uninstall_keyword")
    @commands.has_role(CONTROL_ROLE)
    async def uninstall_keyword(self, ctx, team, keyword):
        """
        (CONTROL) Removes <keyword> from <team>. (This is for upgrades outside of power.)
        """
        await perform_async_unsafe(remove_keyword_from_sub, ctx, team, keyword)

class Comms(commands.Cog):
    """
    Commands for communicating with your fellow subs.
    """
    @commands.command(name="broadcast")
    @commands.has_role(CAPTAIN)
    async def do_broadcast(self, ctx, message):
        """
        Broadcasts a <message> to all in range. Requires the sub to be activated.
        """
        await perform_async(broadcast, ctx, get_team(ctx.author), message)
    
    @commands.command(name="control_message")
    @commands.has_role(CONTROL_ROLE)
    async def message_team(self, ctx, team, message):
        """
        (CONTROL) Sends to <team> the message <message>, regardless of distance.
        """
        await perform_async_unsafe(shout_at_team, ctx, team, message)

class Inventory(commands.Cog):
    """
    Commands for trading with subs on the same space as you, and generally interacting with inventories.
    """
    @commands.command(name="drop")
    @commands.has_role(CAPTAIN)
    async def drop(self, ctx, item):
        """
        Drops the item specified by <item> and optional quantity <quantity>.
        You cannot drop items in ALL CAPS. (These are undroppable due to being
        important or dangerous.)
        """
        await perform(drop_item, ctx, get_team(ctx.author), item)

    @commands.command(name="trade")
    @commands.has_role(CAPTAIN)
    async def trade(self, ctx, team, *args):
        """
        Begins a trade with <team>, where you offer item1 quantity1 item2 quantity2 and so on.
        For example: !trade team_name Fish 10 "Gold coin" 3
        """
        await perform_async(arrange_trade, ctx, get_team(ctx.author), team, list(args))

    @commands.command(name="offer")
    @commands.has_role(CAPTAIN)
    async def offer(self, ctx, *args):
        """
        Makes a counteroffer in your current trade, of form item1 quantity1 item2 quantity2...
        For example: !offer Fish 10 "Gold coin" 4
        """
        await perform_async(make_offer, ctx, get_team(ctx.author), list(args))

    @commands.command(name="accept_trade")
    @commands.has_role(CAPTAIN)
    async def accept_trade(self, ctx):
        """
        Accepts the current trade. A trade will only complete once both parties have accepted the trade.
        """
        await perform_async(accept_offer, ctx, get_team(ctx.author))

    @commands.command(name="reject_trade")
    @commands.has_role(CAPTAIN)
    async def reject_trade(self, ctx):
        """
        Rejects and ends the current trade.
        """
        await perform_async(reject_offer, ctx, get_team(ctx.author))

    @commands.command(name="give")
    @commands.has_role(CONTROL_ROLE)
    async def give(self, ctx, team, item, quantity : int = 1):
        """
        (CONTROL) Gives <team> an <item> with optional <quantity>.
        """
        await perform_async_unsafe(give_item_to_team, ctx, team, item, quantity)

    @commands.command(name="pay")
    @commands.has_role(CONTROL_ROLE)
    async def pay(self, ctx, team, amount : int):
        """
        (CONTROL) Pay a <team> <amount> money. Shorthand for !give with currency name.
        """
        await perform_async_unsafe(give_item_to_team, ctx, team, CURRENCY_NAME, amount)

    @commands.command(name="take")
    @commands.has_role(CONTROL_ROLE)
    async def take(self, ctx, team, item, quantity : int = 1):
        """
        (CONTROL) Take <quantity> of <item> away from <team>. Do not use this during a trade.
        """
        await perform_async_unsafe(take_item_from_team, ctx, team, item, quantity)

    @commands.command(name="get_paid")
    @commands.has_role(CONTROL_ROLE)
    async def get_paid(self, ctx, team, amount : int):
        """
        (CONTROL) Get paid by <team> <amount> money. Shorthand for !take with currency name. Do not use this during a trade.
        """
        await perform_async_unsafe(take_item_from_team, ctx, team, CURRENCY_NAME, amount)

class Engineering(commands.Cog):
    """
    Commands for dealing with the engineering issues.
    """
    @commands.command(name="puzzle")
    @commands.has_role(ENGINEER)
    async def repair_puzzle(self, ctx):
        """
        Gives you a puzzle, which must be solved before you next move. If you
        already have a puzzle in progress, it will be treated as if you ran out of
        time!
        """
        await perform_async(give_team_puzzle, ctx, get_team(ctx.author), "repair")

    @commands.command(name="answer")
    @commands.has_role(ENGINEER)
    async def answer_puzzle(self, ctx, answer: str):
        """
        Lets you answer a set puzzle that hasn't resolved yet.
        """
        await perform_async(answer_team_puzzle, ctx, get_team(ctx.author), answer)

    @commands.command(name="force_puzzle")
    @commands.has_role(CONTROL_ROLE)
    async def force_puzzle(self, ctx, team):
        """
        (CONTROL) Gives team <team> a puzzle, resolving any puzzles they currently have.
        """
        await perform_async(give_team_puzzle, ctx, team, "fixing")

class Crane(commands.Cog):
    """
    Commands for operating the crane.
    """
    @commands.command(name="crane")
    @commands.has_role(SCIENTIST)
    async def crane(self, ctx):
        """
        Drops the crane in your current location. Takes two turns to resolve.
        """
        await perform(drop_crane, ctx, get_team(ctx.author))

class DangerZone(commands.Cog):
    """
    DO NOT USE COMMANDS HERE UNLESS YOU ARE ABSOLUTELY CERTAIN.
    """
    @commands.command(name="death")
    @commands.has_role(CAPTAIN)
    async def death(self, ctx, subname):
        """
        Kills your submarine. This isn't a joke. Must be called with your submarine's full name.
        """
        await perform_async(kill_sub, ctx, get_team(ctx.author), subname)

    @commands.command(name="kill_team")
    @commands.has_role(CONTROL_ROLE)
    async def kill_team(self, ctx, team):
        """
        (CONTROL) Kills the team <team>, removing any trace of their existence bar their channels.
        This deletes their Submarine object, so all game progress is erased.
        Do NOT use this unless you are absolutely sure.
        """
        await perform_unsafe(delete_team, ctx, team)
    
    @commands.command(name="explode")
    @commands.has_role(CONTROL_ROLE)
    async def explode(self, ctx, x : int, y : int, amount : int):
        """
        (CONTROL) Causes an explosion in (x, y), dealing amount damage to the central square.
        It also deals amount-1 damage to the surrounding squares, amount-2 to those surrounding and so on.
        DO NOT RUN !explode x y 40 OR ANY SIMILARLY LARGE AMOUNT OF DAMAGE AS THAT WILL KILL EVERYTHING.
        """
        await perform_async_unsafe(explode_square, ctx, x, y, amount)

class GameManagement(commands.Cog):
    """
    Control commands for starting, pausing and ending the game.
    """
    @commands.command(name="load")
    @commands.has_role(CONTROL_ROLE)
    async def load(self, ctx, arg):
        """
        (CONTROL) Loads either the map, state or both from file. You must specify "map", "state" or "both" as the single argument.
        """
        await perform_unsafe(load_game, ctx, arg, bot)

    @commands.command(name="register")
    @commands.has_role(CONTROL_ROLE)
    async def register_team(self, ctx, x : int = 0, y : int = 0):
        """
        (CONTROL) Registers a new team (with sub at (x,y) defaulting to (0,0)) to the parent channel category.
        Assumes that its name is the name of channel category, and that a channel exists per role in that category: #engineer, #captain and #scientist.
        """
        await perform_async_unsafe(register, ctx, ctx.message.channel.category, x, y)

    @commands.command(name="startloop")
    @commands.has_role(CONTROL_ROLE)
    async def startloop(self, ctx):
        """
        (CONTROL) Starts the main game loop, so that all submarines can act if activated.
        You should use this at the start of the game, and then only again if you have to pause the game for some reason.
        """
        main_loop.start()
        await OKAY_REACT.do_status(ctx)

    @commands.command(name="stoploop")
    @commands.has_role(CONTROL_ROLE)
    async def stoploop(self, ctx):
        """
        (CONTROL) Stops the main game loop, effectively pausing the game.
        You should only use this at the end of the game, or if you need to pause the game for some reason.
        """
        main_loop.stop()
        await OKAY_REACT.do_status(ctx)
    
    @commands.command(name="set_alerts_channel")
    @commands.has_role(CONTROL_ROLE)
    async def set_alerts_channel(self, ctx):
        """
        (CONTROL) Sets up a channel for control alerts, which notify control directly of important occurrences.
        """
        init_control_notifs(ctx.channel)
        await OKAY_REACT.do_status(ctx)

    @commands.command(name="set_news_channel")
    @commands.has_role(CONTROL_ROLE)
    async def set_news_channel(self, ctx):
        """
        (CONTROL) Sets up a channel for news alerts, which allows the news to listen in via their bouys.
        """
        init_news_notifs(ctx.channel)
        await OKAY_REACT.do_status(ctx)

class MapModification(commands.Cog):
    """
    Allows control to add and remove things from the map.
    """
    @commands.command(name="bury")
    @commands.has_role(CONTROL_ROLE)
    async def bury(self, ctx, treasure, x : int, y : int):
        """
        (CONTROL) Buries a treasure <treasure> at location (<x>, <y>).
        """
        await perform_unsafe(bury_treasure, ctx, treasure, x, y)

    @commands.command(name="add_attribute")
    @commands.has_role(CONTROL_ROLE)
    async def add_attribute(self, ctx, attribute, value, x : int, y : int):
        """
        (CONTROL) Add <attribute> to the square <x> <y> taking optional value <value>.
        """
        await perform_unsafe(add_attribute_to, ctx, x, y, attribute, value)

    @commands.command(name="remove_attribute")
    @commands.has_role(CONTROL_ROLE)
    async def remove_attribute(self, ctx, attribute, x : int, y : int):
        """
        (CONTROL) Remove <attribute> from the square <x> <y>.
        """
        await perform_unsafe(remove_attribute_from, ctx, x, y, attribute)
    
    @commands.command(name="add_npc")
    @commands.has_role(CONTROL_ROLE)
    async def add_npc(self, ctx, npcname, npctype, x : int, y : int):
        """
        (CONTROL) Add an NPC <npcname> of <npctype> to the map at (<x>, <y>).
        """
        await perform_unsafe(add_npc_to_map, ctx, npcname, npctype, x, y)

class Weaponry(commands.Cog):
    """
    Allows your submarine to shoot.
    """

    @commands.command(name="shoot_damaging")
    @commands.has_role(SCIENTIST)
    async def damaging(self, ctx, x : int, y : int):
        """
        Schedules a damaging shot at (<x>, <y>). This uses two weapons charges.
        """
        await perform(schedule_shot, ctx, x, y, get_team(ctx.author), True)
    
    @commands.command(name="shoot_stunning")
    @commands.has_role(SCIENTIST)
    async def nondamaging(self, ctx, x : int, y : int):
        """
        Schedules a nondamaging shot at (<x>, <y>). This uses two weapons charges.
        """
        await perform(schedule_shot, ctx, x, y, get_team(ctx.author), False)

# HELPER FUNCTIONS

def get_team(author):
    """
    Gets the first role that has a submarine associated with it, or None.
    """
    roles = list(map(lambda x: x.name.lower(), author.roles))
    for team in get_subs():
        if team in roles:
            return team
    return None

def to_lowercase_list(args):
    alist = list(args)
    for i in range(len(alist)):
        if type(alist[i]) == str:
            alist[i] = alist[i].lower()
    return alist

async def perform(fn, ctx, *args):
    """
    Checks if the main loop is running, and if so performs the function.
    """
    if main_loop.is_running():
        await perform_unsafe(fn, ctx, *args)
    else:
        await FAIL_REACT.do_status(ctx)

async def perform_unsafe(fn, ctx, *args):
    """
    Performs an action fn with *args and then performs the Discord action
    returned by fn using the context ctx.
    NOTE: This can run outside of the main loop, so should only be called
    if you are certain this will not be an issue.
    """
    lower_args = to_lowercase_list(args)
    status = fn(*lower_args)
    if status: await status.do_status(ctx)

async def perform_async(fn, ctx, *args):
    """
    Checks if the main loop is running, and if so performs the async function.
    """
    if main_loop.is_running():
        await perform_async_unsafe(fn, ctx, *args)
    else:
        await FAIL_REACT.do_status(ctx)

async def perform_async_unsafe(fn, ctx, *args):
    """
    Performs an async fn with *args and then the Discord action returned
    by fn using the context ctx.
    NOTE: This can run outside of the main loop, so should only be called
    if you are certain this will not be an issue.
    """
    lower_args = to_lowercase_list(args)
    status = await fn(*lower_args)
    if status: await status.do_status(ctx)

# ERROR HANDLING AND BOT STARTUP

@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You do not have the correct role for this command.")
    else:
        await ctx.send(f"ERROR: {error}")

bot.add_cog(Comms())
bot.add_cog(Crane())
bot.add_cog(DangerZone())
bot.add_cog(Engineering())
bot.add_cog(GameManagement())
bot.add_cog(Inventory())
bot.add_cog(MapModification())
bot.add_cog(Movement())
bot.add_cog(PowerManagement())
bot.add_cog(Status())
bot.add_cog(UpgradeManagement())
bot.add_cog(Weaponry())

print("ALTANTIS READY")
bot.run(TOKEN)
