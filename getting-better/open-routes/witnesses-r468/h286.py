from typing import List


def k(y: List[int]) -> None:
    y.append(1)


def g(x: List[int]) -> None:
    k(x)
