r"""generator yields counted"""
from typing import List, Iterator, Generator
_ = 0  # anchor


def gen() -> Iterator[int]:
    yield 1
    yield 2


#@ ensures \result == 0
def probe() -> int:
    n = 0
    for x in gen():
        n = n + x
    return n


if __name__ == "__main__":
    print("CPython:", probe())
