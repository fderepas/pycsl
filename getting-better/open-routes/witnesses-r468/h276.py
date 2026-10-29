from typing import List


def g(x: List[int]) -> None:
    getattr(x, 'append')(1)
