"""
Runs the game, performing the right actions at fixed time intervals.
"""

from sub import get_teams, get_sub

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