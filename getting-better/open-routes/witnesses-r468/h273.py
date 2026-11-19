from typing import List


def g(x: List[int]) -> None:
    x[len(x):] = [1]
