from discord.ext import commands
from typing import Optional

from discord.ext.commands.core import command

from ALTANTIS.utils.consts import CONTROL_ROLE
from ALTANTIS.utils.bot import perform_async_unsafe, get_team, perform_unsafe
from ALTANTIS.utils.actions import DiscordAction, OKAY_REACT, FAIL_REACT, Message
from ALTANTIS.subs.state import with_sub_async
from ALTANTIS.subs.subsystems.upgrades import VALID_UPGRADES

class UpgradeManagement(commands.Cog):
    """
    Commands for upgrading and downgrading submarines.
    """
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def upgrade(self, ctx, amount : int):
        """
        (CONTROL) Upgrades this team's reactor by <amount>.
        You can specify a negative number, but this will not check that the resulting state makes sense (that is, the team is not using more power than they have) - in general you should use !damage instead.
        """
        await perform_async_unsafe(upgrade_sub, ctx, get_team(ctx.channel), amount)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def upgrade_system(self, ctx, system, amount : int):
        """
        (CONTROL) Upgrades this team's system by <amount>.
        You can specify a negative number to downgrade, and it will check that this makes sense.
        """
        await perform_async_unsafe(upgrade_sub_system, ctx, get_team(ctx.channel), system, amount)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def upgrade_innate(self, ctx, system, amount : int):
        """
        (CONTROL) Upgrades this team's innate system by <amount>.
        You can specify a negative number to downgrade, and it will check that this makes sense.
        """
        await perform_async_unsafe(upgrade_sub_innate, ctx, get_team(ctx.channel), system, amount)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def install_system(self, ctx, system):
        """
        (CONTROL) Gives this team access to new system <system>.
        """
        await perform_async_unsafe(add_system, ctx, get_team(ctx.channel), system)
    
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def add_keyword(self, ctx, keyword, turn_limit : Optional[int] = None, damage : int = 1):
        """
        (CONTROL) Gives this team a brand new <keyword>! (This is for upgrades outside of power.)
        """
        await perform_async_unsafe(add_keyword_to_sub, ctx, get_team(ctx.channel), keyword, turn_limit, damage)

    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def remove_keyword(self, ctx, keyword):
        """
        (CONTROL) Removes <keyword> from this team. (This is for upgrades outside of power.)
        """
        await perform_async_unsafe(remove_keyword_from_sub, ctx, get_team(ctx.channel), keyword)
    
    @commands.command()
    @commands.has_role(CONTROL_ROLE)
    async def list_upgrades(self, ctx):
        """
        (CONTROL) Lists all keywords that are implemented in code along with their ability.
        """
        await perform_unsafe(list_keywords, ctx)

async def upgrade_sub(team : str, amount : int) -> DiscordAction:
    async def do_upgrade(sub):
        sub.power.modify_reactor(amount)
        await sub.send_message(f"Submarine **{team.title()}** was upgraded! Power cap increased by {amount}.", "engineer")
        return OKAY_REACT
    return await with_sub_async(team, do_upgrade, FAIL_REACT)

async def upgrade_sub_system(team : str, system : str, amount : int) -> DiscordAction:
    async def do_upgrade(sub):
        if sub.power.modify_system(system, amount):
            await sub.send_message(f"Submarine **{team.title()}** was upgraded! **{system.title()}** max power increased by {amount}.", "engineer")
            return OKAY_REACT
        return FAIL_REACT
    return await with_sub_async(team, do_upgrade, FAIL_REACT)

async def upgrade_sub_innate(team : str, system : str, amount : int) -> DiscordAction:
    async def do_upgrade(sub):
        if sub.power.modify_innate(system, amount):
            await sub.send_message(f"Submarine **{team.title()}** was upgraded! **{system.title()}** innate power increased by {amount}.", "engineer")
            return OKAY_REACT
        return FAIL_REACT
    return await with_sub_async(team, do_upgrade, FAIL_REACT)

async def add_system(team : str, system : str) -> DiscordAction:
    async def do_add(sub):
        if sub.power.add_system(system):
            await sub.send_message(f"Submarine **{team.title()}** was upgraded! New system **{system}** was installed.", "engineer")
            return OKAY_REACT
        return FAIL_REACT
    return await with_sub_async(team, do_add, FAIL_REACT)

async def add_keyword_to_sub(team : str, keyword : str, turn_limit : Optional[int], damage : int) -> DiscordAction:
    async def do_add(sub):
        message = sub.upgrades.add_keyword(keyword, turn_limit, damage)
        if message is not None:
            await sub.send_message(f"Submarine **{team.title()}** was upgraded with the keyword **{keyword}**!", "engineer")
            return Message(message)
        return FAIL_REACT
    return await with_sub_async(team, do_add, FAIL_REACT)

async def remove_keyword_from_sub(team : str, keyword : str) -> DiscordAction:
    async def do_remove(sub):
        if sub.upgrades.remove_keyword(keyword):
            await sub.send_message(f"Submarine **{team.title()}** was downgraded, as keyword **{keyword}** was removed.", "engineer")
            return OKAY_REACT
        return FAIL_REACT
    return await with_sub_async(team, do_remove, FAIL_REACT)

def list_keywords() -> DiscordAction:
    message = ""
    for upgrade in VALID_UPGRADES:
        message += f"`{upgrade}`: {VALID_UPGRADES[upgrade]}\n"
    return Message(message)