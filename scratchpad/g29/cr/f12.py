r"""G29 f12 — ROUTE #148 family (float literal truncated to int): class-level attribute read through an instance"""
from dataclasses import dataclass, field
from typing import NamedTuple
_ = 0  # anchor


class Cy:
    r = 2.5
    def __init__(self) -> None:
        pass


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
