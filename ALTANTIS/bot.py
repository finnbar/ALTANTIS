"""
The main entry point for our bot, which tells Discord what commands the bot can
perform and how to do so.
"""

from discord.ext import commands

from ALTANTIS.utils.bot import bot
from ALTANTIS.utils.consts import ADMIN_NAME, TOKEN

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You do not have the correct role for this command.")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("No command under that name was found!")
    elif isinstance(error, commands.errors.MaxConcurrencyReached):
        await ctx.send("Please wait, ALTANTIS is dealing with too many requests right now!")
    elif isinstance(error, commands.errors.UserInputError):
        await ctx.send(f"Sorry, that input wasn't understood. Try running !help <command> if you are unsure what went wrong. The exact error returned was: {error}")
    else:
        await ctx.send(f"ERROR: {error}.\n**PAGING {ADMIN_NAME} to make sure that ALTANTIS is working okay.**")

from ALTANTIS.cogs.comms import Comms
from ALTANTIS.cogs.crane import Crane
from ALTANTIS.cogs.danger import DangerZone
from ALTANTIS.cogs.engineering import Engineering
from ALTANTIS.cogs.inventory import Inventory
from ALTANTIS.cogs.management import GameManagement
from ALTANTIS.cogs.map import MapModification
from ALTANTIS.cogs.movement import Movement
from ALTANTIS.cogs.npcs import NPCs
from ALTANTIS.cogs.power import PowerManagement
from ALTANTIS.cogs.status import Status
from ALTANTIS.cogs.upgrades import UpgradeManagement
from ALTANTIS.cogs.weapons import Weaponry

bot.add_cog(Comms())
bot.add_cog(Crane())
bot.add_cog(DangerZone())
bot.add_cog(Engineering())
bot.add_cog(GameManagement())
bot.add_cog(Inventory())
bot.add_cog(MapModification())
bot.add_cog(NPCs())
bot.add_cog(Movement())
bot.add_cog(PowerManagement())
bot.add_cog(Status())
bot.add_cog(UpgradeManagement())
bot.add_cog(Weaponry())

def run_bot():
    print("ALTANTIS READY")
    bot.run(TOKEN)

from ALTANTIS.npcs.npc import load_npc_types
load_npc_types()