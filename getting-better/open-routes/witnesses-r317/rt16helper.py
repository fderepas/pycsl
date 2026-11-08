from typing import List

def poke(xs: List[int]) -> None:
    if len(xs) > 0:
        xs[0] = 5

class H:
    def __init__(self) -> None:
        self.n = 0
    def poke(self, xs: List[int]) -> None:
        if len(xs) > 0:
            xs[0] = 5
