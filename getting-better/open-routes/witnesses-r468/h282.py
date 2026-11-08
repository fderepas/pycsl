from typing import List


def g(x: List[int]) -> None:
    list(map(x.append, [1]))
