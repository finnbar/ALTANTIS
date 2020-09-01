from discord.ext import commands

from ALTANTIS.utils.consts import CONTROL_ROLE, SCIENTIST
from ALTANTIS.utils.bot import perform, get_team
from ALTANTIS.utils.actions import Message, FAIL_REACT
from ALTANTIS.subs.state import with_sub

class Weaponry(commands.Cog):
    """
    Allows your submarine to shoot.
    """

    @commands.command(name="shoot_damaging")
    @commands.has_any_role(SCIENTIST, CONTROL_ROLE)
    async def damaging(self, ctx, x : int, y : int):
        """
        Schedules a damaging shot at (<x>, <y>). This uses two weapons charges.
        """
        await perform(schedule_shot, ctx, x, y, get_team(ctx.channel), True)
    
    @commands.command(name="shoot_stunning")
    @commands.has_any_role(SCIENTIST, CONTROL_ROLE)
    async def nondamaging(self, ctx, x : int, y : int):
        """
        Schedules a nondamaging shot at (<x>, <y>). This uses two weapons charges.
        """
        await perform(schedule_shot, ctx, x, y, get_team(ctx.channel), False)

def schedule_shot(x : int, y : int, team : str, damaging : bool):
    def do_schedule(sub):
        return Message(sub.weapons.prepare_shot(damaging, x, y))
    return with_sub(team, do_schedule, FAIL_REACT)