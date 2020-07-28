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

        # Actions that aren't moving:

        # Movement:
        move_message = sub.movement_tick() or ""
        message += f"{move_message}\n"
        
        await sub.send_message(f"{message}\nTurn completed.")