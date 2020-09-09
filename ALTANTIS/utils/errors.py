from typing import Tuple

class SubmarineOutOfBoundsError(RuntimeError):
    def __init__(self, pos : Tuple[int, int], message=None):
        if message is None:
            self.message = f"Submarine out of bounds! (found in ({pos[0]}, {pos[1]}))"
        else:
            self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return self.message

class SquareOutOfBoundsError(RuntimeError):
    def __init__(self, pos : Tuple[int, int], message=None):
        if message is None:
            self.message = f"Square ({pos[0]}, {pos[1]}) is out of bounds."
        else:
            self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return self.message