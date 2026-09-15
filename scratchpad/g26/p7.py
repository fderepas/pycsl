r"""P7 — #136 widen: DYNAMIC exec rebinding a builtin at module scope (1366's twin)."""
_ = 0  # anchor
from typing import List

exec("le" + "n = sum")


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [5]
    return len(xs)
