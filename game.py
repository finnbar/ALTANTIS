"""
Runs the game, performing the right actions at fixed time intervals.
"""

from sub import get_teams, get_sub, state_to_dict, state_from_dict
from world import map_to_dict, map_from_dict
from utils import OKAY_REACT, FAIL_REACT

import json

async def perform_timestep(counter):
    """
    Does all time-related stuff, including movement, power changes and so on.
    Called at a time interval, when allowed.
    """
    print(f"Running turn {counter}.")

    def is_active_sub(subname):
        sub = get_sub(subname)
        if not sub: return False
        return sub.activated()

    # Get all active subs. (Can you tell I'm a functional programmer?)
    subsubset = list(filter(is_active_sub, get_teams()))
    submessages = {i: {"engineer": "", "captain": "", "navigator": "", "scientist": ""} for i in subsubset}
    message_opening = f"---------**TURN {counter}**----------\n"

    # Power management
    for subname in subsubset:
        sub = get_sub(subname)
        power_message = sub.apply_power_schedule()
        if power_message:
            power_message = f"{power_message}\n"
            submessages[subname]["captain"] += power_message
            submessages[subname]["engineer"] += power_message
    
    # Movement
    for subname in subsubset:
        sub = get_sub(subname)
        move_message = await sub.movement_tick()
        if move_message:
            move_message = f"{move_message}\n"
            submessages[subname]["captain"] += move_message
            submessages[subname]["navigator"] += move_message
    
    # Scanning (as we enter a new square only)
    # TODO: Only make scanner print when things change. This will require
    # tracking past results and not shuffling them preemptively.
    for subname in subsubset:
        sub = get_sub(subname)
        scan_result = sub.scan()
        if len(scan_result) > 0:
            scan_message = "**Scanners found:**\n"
            scan_message += "\n".join(scan_result)
            scan_message += "\n"
            submessages[subname]["captain"] += scan_message
            submessages[subname]["scientist"] += scan_message

    for subname in subsubset:
        messages = submessages[subname]
        if messages["captain"] == "":
            messages["captain"] = "\n"
        await sub.send_message(f"{message_opening}{messages['captain'][:-1]}", "captain")
        if messages["navigator"] != "":
            await sub.send_message(f"{message_opening}{messages['navigator'][:-1]}", "navigator")
        if messages["engineer"] != "":
            await sub.send_message(f"{message_opening}{messages['engineer'][:-1]}", "engineer")
        if messages["scientist"] != "":
            await sub.send_message(f"{message_opening}{messages['scientist'][:-1]}", "scientist")

    save_game()

def save_game():
    """
    Save the game to map.json and state.json.
    We save the map and state separately, so they can be loaded separately.
    This must be called at the end of the loop, as to guarantee that we're
    not about to overwrite important data being written during it.
    """
    state_dict = state_to_dict()
    map_dict = map_to_dict()
    with open("state.json", "w") as state_file:
        state_file.write(json.dumps(state_dict))
    with open("map.json", "w") as map_file:
        map_file.write(json.dumps(map_dict))

def load_game(which, bot):
    """
    Loads the state (from state.json), map (from map.json) or both.
    Does not check whether the files exist.
    This is destructive, so needs the exact correct argument.
    """
    if which not in ["both", "map", "state"]:
        return FAIL_REACT
    if which in ["both", "map"]:
        with open("map.json", "r") as map_file:
            map_string = map_file.read()
            map_json = json.loads(map_string)
            map_from_dict(map_json)
    if which in ["both", "state"]:
        with open("state.json", "r") as state_file:
            state_string = state_file.read()
            state_json = json.loads(state_string)
            state_from_dict(state_json, bot)
    return OKAY_REACT