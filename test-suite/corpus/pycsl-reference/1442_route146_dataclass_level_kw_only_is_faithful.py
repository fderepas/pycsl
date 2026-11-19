r"""Test 1442 - ROUTE #146 control: `@dataclass(kw_only=True)` called with ALL keywords was already faithful before the repair and must stay faithful after it - `Pee(yfld=1, xfld=2).yfld` is 1 and PROVES on both sides.
"""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass(kw_only=True)
class Pee:
    xfld: int = 0
    yfld: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = Pee(yfld=1, xfld=2)
    return p.yfld
