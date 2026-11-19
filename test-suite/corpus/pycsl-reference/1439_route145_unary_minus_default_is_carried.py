r"""Test 1439 - ROUTE #145, the FAITHFUL direction: the class-body default `-7` is now FOLDED with `_const_int_value` - carried, not fabricated - and `\result == -7` PROVES.
"""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = -7


#@ ensures \result == -7
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
