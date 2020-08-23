"""
Runs the game, performing the right actions at fixed time intervals.
"""

from state import get_subs, get_sub, state_to_dict, state_from_dict
from world import map_to_dict, map_from_dict
from utils import OKAY_REACT, FAIL_REACT
from npc import npc_tick

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
        return sub.power.activated()

    # Get all active subs. (Can you tell I'm a functional programmer?)
    # Note: we still collect all messages for all subs, as there are some
    # messages that inactive subs should receive.
    subsubset = list(filter(is_active_sub, get_subs()))
    submessages = {i: {"engineer": "", "captain": "", "scientist": ""} for i in get_subs()}
    message_opening = f"---------**TURN {counter}**----------\n"

    # Power management
    for subname in subsubset:
        sub = get_sub(subname)
        power_message = sub.power.apply_power_schedule()
        if power_message:
            power_message = f"{power_message}\n"
            submessages[subname]["captain"] += power_message
            submessages[subname]["engineer"] += power_message

    # Weapons
    for subname in subsubset:
        sub = get_sub(subname)
        weapons_message = sub.weapons.weaponry_tick()
        if weapons_message:
            weapons_message = f"{weapons_message}\n"
            submessages[subname]["captain"] += weapons_message
    
    # NPCs
    await npc_tick()

    # The crane
    for subname in subsubset:
        sub = get_sub(subname)
        crane_message = await sub.inventory.crane_tick()
        if crane_message:
            crane_message = f"{crane_message}\n"
            submessages[subname]["scientist"] += crane_message

    # Movement, trade and puzzles
    for subname in subsubset:
        sub = get_sub(subname)
        move_message, trade_messages = await sub.movement.movement_tick()
        if move_message:
            move_message = f"{move_message}\n"
            submessages[subname]["captain"] += move_message
        for target in trade_messages:
            submessages[target]["captain"] += trade_messages[target] + "\n"
    
    # Scanning (as we enter a new square only)
    for subname in subsubset:
        sub = get_sub(subname)
        scan_message = sub.scan.scan_string()
        if scan_message != "":
            submessages[subname]["captain"] += scan_message
            submessages[subname]["scientist"] += scan_message
    
    # Postponed events
    for subname in subsubset:
        sub = get_sub(subname)
        await sub.upgrades.postponed_tick()

    # Damage
    for subname in get_subs():
        sub = get_sub(subname)
        damage_message = await sub.power.damage_tick()
        if damage_message:
            damage_message = f"{damage_message}\n"
            submessages[subname]["captain"] += damage_message
            submessages[subname]["engineer"] += damage_message
            submessages[subname]["scientist"] += damage_message

    for subname in get_subs():
        messages = submessages[subname]
        sub = get_sub(subname)
        if messages["captain"] == "":
            if subname not in subsubset:
                messages["captain"] = "Your submarine is deactivated so nothing happened.\n"
            else:
                messages["captain"] = "Your submarine is active, but there is nothing to notify you about.\n"
        await sub.send_message(f"{message_opening}{messages['captain'][:-1]}", "captain")
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