r"""Test 1433 - ROUTE #144, the FAITHFUL direction: the same derived `@dataclass` now binds `C(1, 2)` to a=1, b=2 and the TRUE claim `\result == 2` PROVES. FAILED before the repair (the model bound nothing); a repair that only refuses would leave this failing too.
"""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class B:
    a: int


@dataclass
class C(B):
    b: int


#@ ensures \result == 2
#@ assigns \nothing
def probe() -> int:
    c = C(1, 2)
    return c.b
