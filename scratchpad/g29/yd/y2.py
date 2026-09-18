r"""generator with return value"""
from typing import List, Iterator, Generator
_ = 0  # anchor


def gen() -> Iterator[int]:
    yield 1
    return


#@ ensures \result == 0
def probe() -> int:
    n = 0
    for x in gen():
        n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
