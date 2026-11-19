r"""Test 1675 - ROUTE #191 carrier (gen #30): a `None` STORED into an instance FIELD after construction read back as the integer 0. Route #183 closed the CONSTRUCTOR position; a post-construction `b.v = None` reaches the TYPED `NoneExpr` arm and answered the literal `0`, so `b.v == 0` PROVED True while CPython says False. Closed by the same general repair.
"""
# pycsl-expected: FAIL
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
    if b.v == 0:
        return 1
    return 2
