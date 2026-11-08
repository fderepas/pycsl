r"""G29 GT7 — a module-level list mutated by a function between two reads: the reads differ."""
from typing import List
_ = 0  # anchor
items: List[int] = [0]


def poke() -> None:
    items[0] = 9


#@ ensures \result == True
def probe() -> bool:
    a = items[0]
    poke()
    b = items[0]
    return a == b


if __name__ == "__main__":
    print("CPython:", probe())
