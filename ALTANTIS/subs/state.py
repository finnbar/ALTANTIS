"""
Manages the state dictionary, which keeps track of all submarines.
"""

from ALTANTIS.subs.sub import sub_from_dict, Submarine
from ALTANTIS.utils.actions import DiscordAction

from typing import Dict, List, Any, Callable, Awaitable, Optional
from copy import deepcopy
import discord

state : Dict[str, Submarine] = {}

def get_subs() -> List[str]:
    """
    Gets all possible teams.
    """
    return list(state.keys())

def get_sub_objects() -> List[Submarine]:
    return list(state.values())

def filtered_teams(pred : Callable[[Submarine], bool]) -> List[Submarine]:
    """
    Gets all subs that satisfy some predicate.
    """
    subs = []
    for sub in state:
        if pred(state[sub]):
            subs.append(state[sub])
    return subs

def get_sub(name : str) -> Optional[Submarine]:
    """
    Gets the Submarine object associated with `name`.
    """
    if name in state:
        return state[name]
    return None

def with_sub(name : str, function : Callable[[Submarine], DiscordAction], fail : DiscordAction) -> DiscordAction:
    sub = get_sub(name)
    if sub:
        return function(sub)
    return fail

async def with_sub_async(name : str, function : Callable[[Submarine], Awaitable[DiscordAction]], fail : DiscordAction) -> DiscordAction:
    sub = get_sub(name)
    if sub:
        return await function(sub)
    return fail

def add_team(name : str, category : discord.CategoryChannel, x : int, y : int, keyword : str) -> bool:
    """
    Adds a team with the name, if able.
    """
    if name not in get_subs():
        child_channels = category.text_channels
        channel_dict = {}
        for channel in child_channels:
            channel_dict[channel.name] = channel
        state[name] = Submarine(name, channel_dict, x, y, keyword)
        return True
    return False

def remove_team(name : str) -> bool:
    """
    Removes the team with that name, if able.
    """
    if name in get_subs():
        del state[name]
        return True
    return False

def state_to_dict() -> Dict[str, Dict[str, Any]]:
    """
    Convert our state to a dictionary. This just runs to_dict on each member of
    the state.
    """
    temp_state = deepcopy(state)
    state_dict = {}
    for subname in temp_state:
        state_dict[subname] = temp_state[subname].to_dict()
    return state_dict

def state_from_dict(dictionary : Dict[str, Dict[str, Any]], client : discord.Client):
    """
    Overwrites state with the state made by state_to_dict.
    """
    global state
    new_state = {}
    for subname in dictionary:
        new_state[subname] = sub_from_dict(dictionary[subname], client)
    state = new_state