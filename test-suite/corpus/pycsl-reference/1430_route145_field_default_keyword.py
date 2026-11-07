r"""Test 1430 - ROUTE #145, the third shape: `field(default=5)` is the dataclass spelling of a default and its RHS is a `Call`, so the collector matched nothing. `\result == 0` PROVED while CPython returns 5. The `field(default=<x>)` wrapper is now unwrapped before the constant test.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = field(default=5)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
