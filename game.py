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
        message = ""

        # The sub should only activate if it is active. I know, novel.
        if not sub.activated():
            break

        # Power manipulation:
        power_message = sub.apply_power_schedule()
        if power_message:
            message += f"{power_message}\n"

        # Actions that aren't moving:

        # Movement:
        move_message = sub.movement_tick()
        if move_message:
            message += f"{move_message}\n"
        
        if message == "":
            message = "Nothing to report.\n"
        await sub.send_message(f"---------**TURN {counter}**----------\n{message[:-1]}")