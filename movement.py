"""
Allows the sub to move.
"""

from world import move_on_map, possible_directions, get_square, X_LIMIT, Y_LIMIT, explore_submap
from consts import GAME_SPEED, direction_emoji, TICK, CROSS

import math, datetime

class MovementControls():
    def __init__(self, sub, x, y):
        self.sub = sub
        self.direction = "N"
        self.x = x
        self.y = y
        # movement_progress is how much energy has been put towards a move.
        # Once it reaches a value determined by the engines, we move!
        self.movement_progress = 0
    
    async def movement_tick(self):
        """
        Updates internal state and moves if it is time to do so.
        """
        self.movement_progress += self.sub.power.get_power("engines")
        threshold = get_square(self.x, self.y).difficulty()
        if self.movement_progress >= threshold:
            self.movement_progress -= threshold
            direction = self.direction # Direction can change as result of movement.
            message = self.move()
            move_status = (
                f"Moved **{self.sub.name}** in direction **{direction}**!\n"
                f"**{self.sub.name}** is now at position **{self.get_position()}**."
            )

            # Do all the puzzles stuff.
            await self.sub.puzzles.movement_tick()

            # Finally, return our movement.
            if message:
                return f"{message}\n{move_status}"
            return move_status
        return None
    
    def set_direction(self, direction):
        if direction in possible_directions():
            self.direction = direction
            return True
        return False

    def get_direction(self):
        return self.direction

    def set_position(self, x, y):
        if 0 <= x < X_LIMIT and 0 <= y < Y_LIMIT:
            self.x = x
            self.y = y
            return True
        return False

    def get_position(self):
        return (self.x, self.y)

    def move(self):
        self.x, self.y, message = move_on_map(self.sub, self.direction, self.x, self.y)
        return message
    
    def status(self, loop):
        message = ""
        power_system = self.sub.power

        if power_system.activated():
            time_until_next = math.inf
            if loop:
                time_until_next = loop.next_iteration.timestamp() - datetime.datetime.now().timestamp()
            threshold = get_square(self.x, self.y).difficulty()
            turns_until_move = math.ceil(max(threshold - self.movement_progress, 0) / power_system.get_power("engines"))
            turns_plural = "turns" if turns_until_move > 1 else "turn"
            time_until_move = time_until_next + GAME_SPEED * (turns_until_move - 1)
            message += f"Submarine is currently online. {TICK}\n"
            message += f"Next game turn will occur in {int(time_until_next)}s.\n"
            message += f"Next move estimated to occur in {int(time_until_move)}s ({turns_until_move} {turns_plural}).\n"
            message += f"Currently moving **{self.direction}** ({direction_emoji[self.direction]}) and in position **({self.x}, {self.y})**.\n\n"
        else:
            message += f"Submarine is currently offline. {CROSS}\n\n"
        return message