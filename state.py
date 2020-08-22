"""
Manages the state dictionary, which keeps track of all submarines.
"""

from sub import sub_from_dict, Submarine

state = {}

def get_subs():
    """
    Gets all possible teams.
    """
    return list(state.keys())

def filtered_teams(pred):
    """
    Gets all names of subs that satisfy some predicate.
    """
    subs = []
    for sub in state:
        if pred(state[sub]):
            subs.append(sub)
    return subs

def get_sub(name):
    """
    Gets the Submarine object associated with `name`.
    """
    if name in state:
        return state[name]

def add_team(name, category, x, y):
    """
    Adds a team with the name, if able.
    """
    if name not in get_subs():
        child_channels = category.text_channels
        channel_dict = {}
        for channel in child_channels:
            channel_dict[channel.name] = channel
        state[name] = Submarine(name, channel_dict, x, y)
        return True
    return False

def remove_team(name):
    """
    Removes the team with that name, if able.
    """
    if name in get_subs():
        del state[name]
        return True
    return False

def state_to_dict():
    """
    Convert our state to a dictionary. This just runs to_dict on each member of
    the state.
    """
    state_dict = {}
    for subname in state:
        state_dict[subname] = state[subname].to_dict()
    return state_dict

def state_from_dict(dictionary, client):
    """
    Overwrites state with the state made by state_to_dict.
    """
    global state
    new_state = {}
    for subname in dictionary:
        new_state[subname] = sub_from_dict(dictionary[subname], client)
    state = new_state