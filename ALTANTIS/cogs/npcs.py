from discord.ext import commands
from typing import Optional

from ALTANTIS.utils.consts import CONTROL_ROLE
from ALTANTIS.utils.bot import perform_unsafe, get_team, perform_async_unsafe
from ALTANTIS.utils.actions import DiscordAction, Message, OKAY_REACT, FAIL_REACT
from ALTANTIS.utils.text import list_to_and_separated
from ALTANTIS.subs.state import get_sub
from ALTANTIS.npcs.npc import add_npc, get_npc, kill_npc, get_npc_types

class NPCs(commands.Cog):
    """
    Allows control of NPCs
    """    
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def add_npc(self, ctx, npctype, x : int, y : int):
        """
        (CONTROL) Add an NPC <npcname> of <npctype> to the map at (<x>, <y>).
        """
        await perform_unsafe(add_npc_to_map, ctx, npctype, x, y, get_team(ctx.channel))
    
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def remove_npc(self, ctx, npcid : int, rattle : bool = True):
        """
        (CONTROL) Remove the NPC with the given id.
        """
        await perform_async_unsafe(remove_npc_from_map, ctx, npcid, rattle)
    
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def npc_types(self, ctx):
        """
        (CONTROL) Prints out all possible NPC types.
        """
        await perform_unsafe(printout_npc_types, ctx)
    
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def mutate(self, ctx, npc : int, health : int):
        """
        (CONTROL) Sets an NPC <npc>'s health to <health>.
        """
        await perform_unsafe(set_npc_health, ctx, npc, health)

def add_npc_to_map(ntype : str, x : int, y : int, team : Optional[str]) -> DiscordAction:
    sub = None
    if team and get_sub(team):
        sub = team
    return Message(add_npc(ntype, x, y, sub))

async def remove_npc_from_map(npcid : int, rattle : bool) -> DiscordAction:
    if await kill_npc(npcid, rattle):
        return OKAY_REACT
    return FAIL_REACT

def printout_npc_types() -> DiscordAction:
    types = list_to_and_separated(get_npc_types())
    return Message(f"Possible NPC types: {types}.")

def set_npc_health(npcid : int, health : int) -> DiscordAction:
    if health <= 0:
        return FAIL_REACT
    npc = get_npc(npcid)
    if npc is not None:
        npc.health = health
        return OKAY_REACT
    return FAIL_REACT