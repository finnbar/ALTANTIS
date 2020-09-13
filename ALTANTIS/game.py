"""
Runs the game, performing the right actions at fixed time intervals.
"""

from ALTANTIS.subs.state import get_subs, get_sub, state_to_dict, state_from_dict, get_sub_objects
from ALTANTIS.subs.sub import Submarine
from ALTANTIS.npcs.npc import npc_tick, npcs_to_json, npcs_from_json
from ALTANTIS.world.world import map_tick, map_to_dict, map_from_dict
from ALTANTIS.utils.actions import FAIL_REACT, OKAY_REACT
from ALTANTIS.utils.emergencies import emergencies

import json, datetime, os, gzip, random
from typing import List, Dict

NO_SAVE = False

async def perform_timestep(counter : int):
    """
    Does all time-related stuff, including movement, power changes and so on.
    Called at a time interval, when allowed.
    """
    global NO_SAVE
    NO_SAVE = True

    print(f"Running turn {counter}.")

    def is_active_sub(sub):
        return sub.power.activated()

    # Get all active subs. (Can you tell I'm a functional programmer?)
    # Note: we still collect all messages for all subs, as there are some
    # messages that inactive subs should receive.
    subsubset : List[Submarine] = list(filter(is_active_sub, get_sub_objects()))
    submessages : Dict[str, Dict[str, str]] = {i: {"engineer": "", "captain": "", "scientist": ""} for i in get_subs()}
    message_opening : str = f"---------**TURN {counter}**----------\n"

    # Emergency messaging
    for sub in subsubset:
        if sub.power.total_power == 1:
            subname = sub._name
            emergency_message = f"**EMERGENCY!!!** {random.choice(emergencies)}\n"
            submessages[subname]["captain"] += emergency_message
            submessages[subname]["scientist"] += emergency_message
            submessages[subname]["engineer"] += emergency_message

    # Power management
    for sub in subsubset:
        power_message = sub.power.apply_power_schedule()
        if power_message:
            subname = sub._name
            power_message = f"{power_message}\n"
            submessages[subname]["captain"] += power_message
            submessages[subname]["engineer"] += power_message

    # Weapons
    for sub in subsubset:
        weapons_message = sub.weapons.weaponry_tick()
        if weapons_message:
            weapons_message = f"{weapons_message}\n"
            submessages[sub._name]["captain"] += weapons_message
    
    # NPCs
    await npc_tick()
    # Map
    map_tick()

    # The crane
    for sub in subsubset:
        crane_message = await sub.inventory.crane_tick()
        if crane_message:
            crane_message = f"{crane_message}\n"
            submessages[sub._name]["scientist"] += crane_message

    # Movement, trade and puzzles
    for sub in subsubset:
        move_message, trade_messages = await sub.movement.movement_tick()
        if move_message:
            move_message = f"{move_message}\n"
            submessages[sub._name]["captain"] += move_message
        for target in trade_messages:
            submessages[target]["captain"] += trade_messages[target] + "\n"
    
    # Scanning (as we enter a new square only)
    for sub in subsubset:
        scan_message = sub.scan.scan_string()
        if scan_message != "":
            subname = sub._name
            submessages[subname]["captain"] += scan_message
            submessages[subname]["scientist"] += scan_message
    
    # Postponed events
    for sub in subsubset:
        await sub.upgrades.postponed_tick()

    # Damage
    for sub in get_sub_objects():
        damage_message = await sub.power.damage_tick()
        if damage_message:
            subname = sub._name
            damage_message = f"{damage_message}\n"
            submessages[subname]["captain"] += damage_message
            submessages[subname]["engineer"] += damage_message
            submessages[subname]["scientist"] += damage_message

    for sub in get_sub_objects():
        messages = submessages[sub._name]
        if messages["captain"] == "":
            if sub._name not in map(lambda s: s._name, subsubset):
                if sub.power.total_power <= 0:
                    messages["captain"] = "Your submarine is **dead** so nothing happened.\n"
                else:
                    messages["captain"] = "Your submarine is deactivated so nothing happened.\n"
            else:
                messages["captain"] = "Your submarine is active, but there is nothing to notify you about.\n"
        await sub.send_message(f"{message_opening}{messages['captain'][:-1]}", "captain")
        if messages["engineer"] != "":
            await sub.send_message(f"{message_opening}{messages['engineer'][:-1]}", "engineer")
        if messages["scientist"] != "":
            await sub.send_message(f"{message_opening}{messages['scientist'][:-1]}", "scientist")

    NO_SAVE = False
    save_game()

def save_game():
    """
    Save the game to map.json, state.json and npcs.json.
    We save the map and state separately, so they can be loaded separately.
    This must be called at the end of the loop, as to guarantee that we're
    not about to overwrite important data being written during it.
    """
    if NO_SAVE:
        print("SAVE FAILED")
        return False
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state_dict = state_to_dict()
    map_dict = map_to_dict()
    npcs_dict = npcs_to_json()
    # Write a new save at this timestamp.
    with gzip.open(f"saves/state/{timestamp}.json.gz", "wt") as state_file:
        json.dump(state_dict, state_file)
    with gzip.open(f"saves/map/{timestamp}.json.gz", "wt") as map_file:
        json.dump(map_dict, map_file)
    with gzip.open(f"saves/npc/{timestamp}.json.gz", "wt") as npcs_file:
        json.dump(npcs_dict, npcs_file)
    return True

def load_game(which : str, offset : int, bot):
    """
    Loads the state (from state.json), map (from map.json), npcs (from npcs.json) or all.
    Does not check whether the files exist.
    This is destructive, so needs the exact correct argument.
    """
    # Get the relevant timestamp. We arbitrarily choose map to find the correct name.
    prefix = f"{os.curdir}/saves"
    filenames = sorted(os.listdir(f"{prefix}/map/"), reverse=True)
    if offset >= len(filenames):
        return FAIL_REACT
    filename = filenames[offset]
    if which not in ["all", "map", "npcs", "state"]:
        return FAIL_REACT
    if which in ["all", "map"]:
        with gzip.open(f"{prefix}/map/{filename}", "r") as map_file:
            map_string = map_file.read()
            map_json = json.loads(map_string)
            map_from_dict(map_json)
    if which in ["all", "state"]:
        with gzip.open(f"{prefix}/state/{filename}", "r") as state_file:
            state_string = state_file.read()
            state_json = json.loads(state_string)
            state_from_dict(state_json, bot)
    if which in ["all", "npcs"]:
        with gzip.open(f"{prefix}/npc/{filename}", "r") as npc_file:
            npc_string = npc_file.read()
            npc_json = json.loads(npc_string)
            npcs_from_json(npc_json)
    return OKAY_REACT