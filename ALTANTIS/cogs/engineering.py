from discord.ext import commands
from typing import Optional

from ALTANTIS.utils.consts import CONTROL_ROLE, ENGINEER
from ALTANTIS.utils.bot import perform, perform_async, perform_unsafe, perform_async_unsafe, get_team
from ALTANTIS.utils.actions import DiscordAction, Message, OKAY_REACT, FAIL_REACT
from ALTANTIS.subs.state import with_sub_async

class Engineering(commands.Cog):
    """
    Commands for dealing with the engineering issues.
    """
    @commands.command(name="puzzle")
    @commands.has_any_role(ENGINEER, CONTROL_ROLE)
    async def repair_puzzle(self, ctx):
        """
        Gives you a puzzle, which must be solved before you next move. If you
        already have a puzzle in progress, it will be treated as if you ran out of
        time!
        """
        await perform_async(give_team_puzzle, ctx, get_team(ctx.channel), "repair")

    @commands.command(name="answer")
    @commands.has_any_role(ENGINEER, CONTROL_ROLE)
    async def answer_puzzle(self, ctx, answer: str):
        """
        Lets you answer a set puzzle that hasn't resolved yet.
        """
        await perform_async(answer_team_puzzle, ctx, get_team(ctx.channel), answer)

    @commands.command(name="force_puzzle")
    @commands.has_role(CONTROL_ROLE)
    async def force_puzzle(self, ctx):
        """
        (CONTROL) Gives this team a puzzle, resolving any puzzles they currently have.
        """
        await perform_async(give_team_puzzle, ctx, get_team(ctx.channel), "fixing")

async def give_team_puzzle(team : str, reason : str) -> DiscordAction:
    async def do_puzzle(sub):
        await sub.puzzles.send_puzzle(reason)
        return OKAY_REACT
    return await with_sub_async(team, do_puzzle, FAIL_REACT)

async def answer_team_puzzle(team : str, answer : str) -> DiscordAction:
    async def do_answer(sub):
        await sub.puzzles.resolve_puzzle(answer)
        return OKAY_REACT
    return await with_sub_async(team, do_answer, FAIL_REACT)