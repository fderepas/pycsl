from typing import List


def g(x: List[int]) -> None:
    import bisect
    bisect.insort(x, 1)
