r"""Test 1441 - ROUTE #146, the FAITHFUL direction: with `xfld` moved to the by-name channel, `yfld` is Python's first positional parameter, `Pee(5, xfld=1).yfld` is 5 and PROVES.
"""
from dataclasses import dataclass, field

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = field(kw_only=True, default=0)
    yfld: int = 0


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    p = Pee(5, xfld=1)
    return p.yfld
