r"""G29 GT4 — a module-level list mutated by a function (no global statement needed)."""
from typing import List
_ = 0  # anchor
items: List[int] = [0]


def poke() -> None:
    items[0] = 9


#@ ensures \result == 0
def probe() -> int:
    poke()
    return items[0]


if __name__ == "__main__":
    print("CPython:", probe())
