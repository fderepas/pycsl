r"""G29 f5 — ROUTE #148 family (float literal truncated to int): annotated store in __init__"""
from dataclasses import dataclass, field
from typing import NamedTuple
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r: float = 2.5


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
