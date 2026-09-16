r"""Test 1521 - ROUTE #154 control (gen #29): a NON-escaping read of the list field in `__init__` (`len(self.xs)` in a test) keeps route #87's literal, and `C().xs[0] == 1` PROVES on both sides of the repair.
"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]
        if len(self.xs) > 5:
            pass


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.xs[0]

