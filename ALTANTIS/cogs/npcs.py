from discord.ext import commands
from typing import Optional

from ALTANTIS.utils.consts import CONTROL_ROLE, CAPTAIN
from ALTANTIS.utils.bot import perform, perform_async, perform_unsafe, perform_async_unsafe, get_team
from ALTANTIS.utils.actions import DiscordAction, Message, OKAY_REACT, FAIL_REACT
from ALTANTIS.utils.text import list_to_and_separated
from ALTANTIS.npcs.npc import add_npc, kill_npc, get_npc_types

class NPCs(commands.Cog):
    """
    Allows control of NPCs
    """    
    @commands.command(name="add_npc")
    @commands.has_role(CONTROL_ROLE)
    async def add_npc(self, ctx, npctype, x : int, y : int):
        """
        (CONTROL) Add an NPC <npcname> of <npctype> to the map at (<x>, <y>).
        """
        await perform_unsafe(add_npc_to_map, ctx, npctype, x, y)
    
    @commands.command(name="remove_npc")
    @commands.has_role(CONTROL_ROLE)
    async def remove_npc(self, ctx, npcid : int):
        """
        (CONTROL) Remove the NPC with the given id.
        """
        await perform_unsafe(remove_npc_from_map, ctx, npcid)
    
    @commands.command(name="npc_types")
    @commands.has_role(CONTROL_ROLE)
    async def npc_types(self, ctx):
        """
        (CONTROL) Prints out all possible NPC types.
        """
        await perform_unsafe(printout_npc_types, ctx)

def add_npc_to_map(ntype : str, x : int, y : int) -> DiscordAction:
    return Message(add_npc(ntype, x, y))

def remove_npc_from_map(npcid : int) -> DiscordAction:
    if kill_npc(npcid):
        return OKAY_REACT
    return FAIL_REACT

def printout_npc_types() -> DiscordAction:
    types = list_to_and_separated(get_npc_types())
    return Message(f"Possible NPC types: {types}.")