r"""Test 1650 - ROUTE #183 control (gen #29): a field initialised to None and then assigned a real value in `__init__` keeps its captured default, and `c.v == 3` proves.
"""
from typing import Optional
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v: Optional[int] = None
        self.v = 3


#@ ensures \result == True
def probe() -> bool:
    c = C()
    return c.v == 3
