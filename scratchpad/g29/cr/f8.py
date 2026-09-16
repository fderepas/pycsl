r"""G29 f8 — ROUTE #148 family (float literal truncated to int): second (last-wins) store"""
from dataclasses import dataclass, field
from typing import NamedTuple
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r = 1
        self.r = 2.5


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
