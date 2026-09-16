r"""CTRL2 — positive control: an ordinary module-scope dict/list item store on a FRESH name."""
from typing import Dict, List
_ = 0  # anchor
D: Dict[str, int] = {}
D["a"] = 1
XS: List[int] = [0, 0]
XS[0] = 7


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return 0
