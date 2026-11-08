from typing import List


def parse(s: str) -> int:
    return int(s)


def pair(s: str) -> int:
    a, b = s.split(",")
    return 0


def shift(x: int) -> int:
    return 1 << x


def first(xs: List[int]) -> int:
    return xs[0]
