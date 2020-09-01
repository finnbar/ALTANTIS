"""
The main entry point for our bot, which tells Discord what commands the bot can
perform and how to do so.
"""

from discord.ext import commands, tasks

from ALTANTIS.utils.bot import bot
from ALTANTIS.utils.consts import TOKEN

@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You do not have the correct role for this command.")
    else:
        await ctx.send(f"ERROR: {error}")

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