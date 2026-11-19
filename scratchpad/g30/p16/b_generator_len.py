from typing import List


def gen():
    yield 1
    yield 2


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = list(gen())
    return len(xs)
