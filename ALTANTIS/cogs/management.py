import discord
from discord.ext import commands
from typing import Optional

from ALTANTIS.utils.consts import CONTROL_ROLE, CAPTAIN
from ALTANTIS.utils.bot import perform, perform_async, perform_unsafe, perform_async_unsafe, get_team, bot, main_loop
from ALTANTIS.utils.actions import DiscordAction, Message, OKAY_REACT, FAIL_REACT
from ALTANTIS.utils.roles import create_or_return_role
from ALTANTIS.utils.control import init_control_notifs, init_news_notifs
from ALTANTIS.subs.state import add_team, get_sub
from ALTANTIS.game import load_game, save_game

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
    
    @commands.command(name="save")
    @commands.has_role(CONTROL_ROLE)
    async def save(self, ctx):
        """
        (CONTROL) Saves the game. Please do not do this unless you know what you're doing.
        The game automatically saves every turn, so that should be enough.
        However, this is useful if you are about to do something that might break, or if you want to save the starting state of the game without running any turns.
        I will reemphasise this, however: PLEASE DO NOT USE THIS COMMAND UNLESS YOU KNOW WHAT YOU'RE DOING.
        It may protect you from running it at the same time as the main loop, but it won't protect you from stupidity.
        """
        if save_game():
            await OKAY_REACT.do_status(ctx)
        else:
            await FAIL_REACT.do_status(ctx)
    
    @commands.command(name="make_submarine")
    async def make_sub(self, ctx, name, captain : discord.Member, engineer : discord.Member, scientist : discord.Member, x : int = 0, y : int = 0):
        """
        (CONTROL) Creates channels, roles and a sub for the inputted team.
        """
        await perform_async_unsafe(make_submarine, ctx, ctx.guild, name, captain, engineer, scientist, x, y)

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

async def make_submarine(guild : discord.Guild, name : str, captain : discord.Member, engineer : discord.Member, scientist : discord.Member, x : int, y : int) -> DiscordAction:
    """
    Makes a submarine with the name <name> and members Captain, Engineer and Scientist.
    Creates a category with <name>, then channels for each player.
    Then creates the relevant roles (if they don't exist already), and assigns them to players.
    Finally, we register this team as a submarine.
    """
    if get_sub(name):
        return FAIL_REACT

    category = await guild.create_category_channel(name)
    # Create roles if needed.
    captain_role = await create_or_return_role(guild, "captain", mentionable=True)
    engineer_role = await create_or_return_role(guild, "engineer", mentionable=True)
    scientist_role = await create_or_return_role(guild, "scientist", mentionable=True)
    control_role = await create_or_return_role(guild, CONTROL_ROLE, hoist=True, mentionable=True)
    altantis_role = await create_or_return_role(guild, "ALTANTIS", hoist=True)
    submarine_role = await create_or_return_role(guild, name, hoist=True)
    specific_capt = await create_or_return_role(guild, f"captain-{name}")
    specific_engi = await create_or_return_role(guild, f"engineer-{name}")
    specific_sci = await create_or_return_role(guild, f"scientist-{name}")

    # Add roles to players.
    await captain.add_roles(captain_role, submarine_role, specific_capt)
    await engineer.add_roles(engineer_role, submarine_role, specific_engi)
    await scientist.add_roles(scientist_role, submarine_role, specific_sci)

    # Add perms to created text channels.
    def allow_control_and_one(channel):
        if channel is not None:
            return {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                channel: discord.PermissionOverwrite(read_messages=True),
                control_role: discord.PermissionOverwrite(read_messages=True),
                altantis_role: discord.PermissionOverwrite(read_messages=True)
            }
        else:
            return {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                control_role: discord.PermissionOverwrite(read_messages=True),
                altantis_role: discord.PermissionOverwrite(read_messages=True)
            }

    await category.create_text_channel("captain", overwrites=allow_control_and_one(specific_capt))
    await category.create_text_channel("engineer", overwrites=allow_control_and_one(specific_engi))
    await category.create_text_channel("scientist", overwrites=allow_control_and_one(specific_sci))
    await category.create_text_channel("control", overwrites=allow_control_and_one(None))
    await category.create_voice_channel("submarine", overwrites=allow_control_and_one(submarine_role))
    return await register(category, x, y)

async def register(category : discord.CategoryChannel, x : int, y : int) -> DiscordAction:
    """
    Registers a team, setting them up with everything they could need.
    Requires a category with the required subchannels.
    ONLY RUNNABLE BY CONTROL.
    """
    if add_team(category.name.lower(), category, x, y):
        sub = get_sub(category.name.lower())
        if sub:
            await sub.send_to_all(f"Channel registered for sub **{category.name.title()}**.")
            return OKAY_REACT
    return FAIL_REACT
