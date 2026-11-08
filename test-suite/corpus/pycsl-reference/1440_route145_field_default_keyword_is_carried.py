r"""Test 1440 - ROUTE #145, the FAITHFUL direction: `field(default=5)` is unwrapped and the 5 is carried, so `\result == 5` PROVES.
"""
from dataclasses import dataclass, field

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = field(default=5)


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
