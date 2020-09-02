from typing import Tuple

class Entity():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_position(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def damage(self, amount):
        raise NotImplementedError

    async def send_message(self, content, channel):
        raise NotImplementedError

    def outward_broadcast(self, strength) -> str:
        return ""

    def is_weak(self) -> bool:
        """
        Whether the submarine is affected by stunning shots.
        """
        return False

    def name(self) -> str:
        """
        The primary key.
        """
        raise NotImplementedError