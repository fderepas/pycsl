r"""Test 1678 - ROUTE #191 control (gen #30): the opaque is ONE shared constant, so a `None` store is still RECOGNISED as `None`. `b.v = None` then `b.v is None` proves - the repair turns the WRONG comparison against the integer 0 undecided without turning the RIGHT comparison against `None` undecided too.
"""
from typing import Optional

_ = 0  # anchor


class Box:
    #@ assigns self.v
    #@ ensures self.v == 5
    def __init__(self) -> None:
        self.v: Optional[int] = 5


#@ ensures \result == 1
def probe() -> int:
    b = Box()
    b.v = None
    if b.v is None:
        return 1
    return 2
