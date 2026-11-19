from typing import List


def g(x: List[int]) -> None:
    {}.setdefault(0, x).append(1)
