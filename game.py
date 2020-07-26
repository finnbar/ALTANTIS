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

        # The sub should only activate if it is its turn.
        if (not sub.activated()) or counter % sub.activation_divisor() != 0:
            break

        # Actions!
        direction = sub.get_direction() # since sub.get_direction() may change.
        move_message = sub.move()
        if move_message:
            await sub.send_message(move_message)

        # Status report!
        message = (
            f"Moved **{subname}** in direction **{direction}**!\n"
            f"**{subname}** is now at position **{sub.get_position()}**."
        )
        await sub.send_message(message)
