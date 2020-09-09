"""
Allows the sub to move.
"""
import math, datetime
from typing import Tuple, Optional

from ALTANTIS.world.world import possible_directions, get_square, in_world, Cell
from ALTANTIS.utils.consts import GAME_SPEED, direction_emoji, TICK, CROSS
from ALTANTIS.utils.direction import directions, reverse_dir
from ALTANTIS.utils.errors import SubmarineOutOfBoundsError
from ..sub import Submarine

class MovementControls():
    def __init__(self, sub : Submarine, x : int, y : int):
        self.sub = sub
        self.direction = "n"
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
        if "blessing" in self.sub.upgrades.keywords:
            # Bound difficulty above by four (normal waters)
            threshold = min(4, threshold)
        if self.movement_progress >= threshold:
            self.movement_progress -= threshold
            direction = self.direction # Direction can change as result of movement.
            message = await self.move()
            move_status = (
                f"Moved **{self.sub.name()}** in direction **{direction.upper()}**!\n"
                f"**{self.sub.name()}** is now at position **{self.get_position()}**."
            )

            # Do all the puzzles stuff.
            await self.sub.puzzles.movement_tick()

            # Cancel trades, if necessary.
            trade_messages = self.sub.inventory.timeout_trade()

            # Finally, return our movement.
            if message:
                return f"{message}\n{move_status}", trade_messages
            return move_status, trade_messages
        return None, {}
    
    def set_direction(self, direction : str) -> bool:
        if direction in possible_directions():
            self.direction = direction
            return True
        return False

    def get_direction(self) -> str:
        return self.direction

    def set_position(self, x : int, y : int) -> bool:
        if in_world(x, y):
            self.x = x
            self.y = y
            return True
        return False

    def get_position(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def get_square(self) -> Cell:
        sq = get_square(self.x, self.y)
        if sq is None:
            raise SubmarineOutOfBoundsError((self.x, self.y))
        return sq

    async def move(self) -> str:
        motion = directions[self.direction]
        new_x = self.x + motion[0]
        new_y = self.y + motion[1]
        if not in_world(new_x, new_y):
            # Crashed into the boundaries of the world, whoops.
            self.set_direction(reverse_dir[self.get_direction()])
            return f"Your submarine reached the boundaries of the world, so was pushed back (now facing **{self.direction.upper()}**) and did not move this turn!"
        # in_world(new_x, new_y) => get_square(new_x, new_y) : Cell (not None)
        message, obstacle = get_square(new_x, new_y).on_entry(self.sub) # type: ignore
        if obstacle:
            return message
        self.x = new_x
        self.y = new_y
        return message
    
    def status(self, loop) -> str:
        message = ""
        power_system = self.sub.power

        if power_system.activated():
            time_until_next = math.inf
            if loop and loop.next_iteration:
                time_until_next = loop.next_iteration.timestamp() - datetime.datetime.now().timestamp()
            threshold = self.get_square().difficulty()
            turns_until_move = math.ceil(max(threshold - self.movement_progress, 0) / power_system.get_power("engines"))
            turns_plural = "turns" if turns_until_move > 1 else "turn"
            time_until_move = time_until_next + GAME_SPEED * (turns_until_move - 1)
            message += f"Submarine is currently online. {TICK}\n"
            if time_until_next != math.inf:
                message += f"Next game turn will occur in {int(time_until_next)}s.\n"
                message += f"Next move estimated to occur in {int(time_until_move)}s ({turns_until_move} {turns_plural}).\n"
            message += f"Currently moving **{self.direction.upper()}** ({direction_emoji[self.direction]}) and in position **({self.x}, {self.y})**.\n\n"
        else:
            message += f"Submarine is currently offline. {CROSS}\n\n"
        return message