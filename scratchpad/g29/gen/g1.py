r"""G29 GEN1 — iterating a user GENERATOR."""
from typing import Iterator
_ = 0  # anchor


def gen() -> Iterator[int]:
    yield 1
    yield 2


#@ ensures \result != 3
def probe() -> int:
    t = 0
    for x in gen():
        t = t + x
    return t


if __name__ == "__main__":
    print("CPython:", probe())
