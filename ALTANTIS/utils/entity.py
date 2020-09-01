from typing import Tuple

class Entity():
    def get_position(self) -> Tuple[int, int]:
        raise NotImplementedError

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