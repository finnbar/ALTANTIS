"""
Runs the game, performing the right actions at fixed time intervals.
"""

from sub import get_teams, get_sub, state
from world import undersea_map
from utils import OKAY_REACT, FAIL_REACT

import jsonpickle

async def perform_timestep(counter):
    """
    Does all time-related stuff, including movement, power changes and so on.
    Called at a time interval, when allowed.
    """
    print(f"Running turn {counter}.")
    for subname in get_teams():
        sub = get_sub(subname)
        message_opening = f"---------**TURN {counter}**----------\n"
        captain_message = ""
        navigator_message = ""
        engineer_message = ""
        scientist_message = ""

        # The sub should only activate if it is active. I know, novel.
        if not sub.activated():
            continue

        # Power manipulation:
        power_message = sub.apply_power_schedule()
        if power_message:
            power_message = f"{power_message}\n"
            captain_message += power_message
            engineer_message += power_message

        # Actions that aren't moving:

        # Movement:
        move_message = sub.movement_tick()
        if move_message:
            move_message = f"{move_message}\n"
            captain_message += move_message
            navigator_message += move_message
        
        if captain_message == "":
            captain_message = "\n"
        await sub.send_message(f"{message_opening}{captain_message[:-1]}", "captain")
        if navigator_message != "":
            await sub.send_message(f"{message_opening}{navigator_message[:-1]}", "navigator")
        if engineer_message != "":
            await sub.send_message(f"{message_opening}{engineer_message[:-1]}", "engineer")
        if scientist_message != "":
            await sub.send_message(f"{message_opening}{scientist_message[:-1]}", "scientist")
    
    save_game()

# TODO: due to Discord objects in Submarine, I can't just pickle. Will need to think properly.
# The best way to do this is probably an o.__dict__ with Discord channels replaced by their IDs.
# I might be able to cheat this with a DiscordChannel class of my own with its own to_json.

def save_game():
    """
    Save the game to map.json and state.json.
    We save the map and state separately, so they can be loaded separately.
    This must be called at the end of the loop, as to guarantee that we're
    not about to overwrite important data being written during it.
    """
    state_pickle = jsonpickle.encode(state)
    map_pickle = jsonpickle.encode(undersea_map)
    with open("state.json", "w") as state_file:
        state_file.write(state_pickle)
    with open("map.json", "w") as map_file:
        map_file.write(map_pickle)

def load_game(which):
    """
    Loads the state (from state.json), map (from map.json) or both.
    Does not check whether the files exist.
    This is destructive, so needs the exact correct argument.
    """
    if which not in ["both", "map", "state"]:
        return FAIL_REACT
    if which in ["both", "map"]:
        with open("map.json", "r") as map_file:
            map_pickle = map_file.read()
            global undersea_map
            undersea_map = jsonpickle.decode(map_pickle)
    if which in ["both", "state"]:
        with open("state.json", "r") as state_file:
            state_pickle = state_file.read()
            global state
            state = jsonpickle.decode(state_pickle)
    return OKAY_REACT