r"""generator function raising on second next, caught"""
from typing import List, Iterator
_ = 0  # anchor


def gen() -> Iterator[int]:
    yield 1
    raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    n = 0
    try:
        for x in gen():
            n = n + x
    except ValueError:
        return 9
    return n - 1


if __name__ == "__main__":
    print("CPython:", probe())
