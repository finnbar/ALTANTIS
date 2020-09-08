from discord.ext import commands
from typing import List

from ALTANTIS.utils.consts import CONTROL_ROLE, ENGINEER
from ALTANTIS.utils.bot import perform, perform_async, get_team
from ALTANTIS.utils.actions import DiscordAction, Message, OKAY_REACT, FAIL_REACT
from ALTANTIS.subs.state import with_sub, with_sub_async

class PowerManagement(commands.Cog):
    """
    Commands for powering, unpowering, healing and damaging subsystems.
    """
    @commands.command()
    @commands.has_any_role(ENGINEER, CONTROL_ROLE)
    async def power(self, ctx, *systems):
        """
        Gives one power to all of <systems> (any number of systems, can repeat).
        Fails if this would overload the power.
        NOTE: This is cumulative - it acts based on all previous calls to this (before the game tick).
        """
        await perform(power_systems, ctx, get_team(ctx.channel), list(systems))

    @commands.command()
    @commands.has_any_role(ENGINEER, CONTROL_ROLE)
    async def unpower(self, ctx, *systems):
        """
        Removes one power from all of <systems> (any number of systems, can repeat).
        Fails if a system would have less than zero power.
        NOTE: This is cumulative - it acts based on all previous calls to this (before the game tick).
        """
        await perform(unpower_systems, ctx, get_team(ctx.channel), list(systems))

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def damage(self, ctx, amount : int, reason=""):
        """
        (CONTROL) Forces this team to take <amount> damage at next loop. You can optionally specify a <reason> which will be messaged to them before.
        """
        await perform_async(deal_damage, ctx, get_team(ctx.channel), amount, reason)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def heal(self, ctx, amount : int, reason=""):
        """
        (CONTROL) Forces this team to take <amount> healing at next loop. You can optionally specify a <reason> which will be messaged to them before.
        """
        await perform_async(heal_up, ctx, get_team(ctx.channel), amount, reason)

def power_systems(team : str, systems : List[str]) -> DiscordAction:
    """
    Powers `systems` of the submarine `team` if able.
    """
    def do_power(sub):
        result = sub.power.power_systems(systems)
        return Message(result)
    return with_sub(team, do_power, FAIL_REACT)

def unpower_systems(team : str, systems : List[str]) -> DiscordAction:
    """
    Unpowers `systems` of the submarine `team` if able.
    """
    def do_unpower(sub):
        result = sub.power.unpower_systems(systems)
        return Message(result)
    return with_sub(team, do_unpower, FAIL_REACT)

async def deal_damage(team : str, amount : int, reason : str) -> DiscordAction:
    async def do_damage(sub):
        sub.damage(amount)
        if reason: await sub.send_to_all(reason)
        return OKAY_REACT
    return await with_sub_async(team, do_damage, FAIL_REACT)

async def heal_up(team : str, amount : int, reason : str) -> DiscordAction:
    async def do_heal(sub):
        sub.power.heal(amount)
        if reason: await sub.send_to_all(reason)
        return OKAY_REACT
    return await with_sub_async(team, do_heal, FAIL_REACT)
