r"""P16 — module-scope mutation of a module int list."""
_ = 0  # anchor
from typing import List

XS: List[int] = [1, 2]



#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return len(XS)
