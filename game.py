"""
Runs the game, performing the right actions at fixed time intervals.
"""

from state import get_teams, get_sub

async def perform_timestep():
    """
    Does all time-related stuff, including movement, power changes and so on.
    Called at a time interval, when allowed.
    """
    print("Running turn!")
    for subname in get_teams():
        sub = get_sub(subname)
        
        # Actions!
        sub.move()
        
        # Status report!
        message = (
            f"Moved **{subname}** in direction **{sub.get_direction()}**!\n"
            f"**{subname}** is now at position **{sub.get_position()}**."
        )
        await sub.send_message(message)
