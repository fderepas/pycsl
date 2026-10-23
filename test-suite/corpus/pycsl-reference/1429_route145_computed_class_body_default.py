r"""Test 1429 - ROUTE #145, the second shape: `xfld: int = 2 + 3` is a `BinOp`, equally name-free and equally unmatched. `\result == 0` PROVED while CPython returns 5. A name-free COMPUTED default that does not fold is now marked UNKNOWN (`(any int)`) rather than given a witness value - the true twin `\result == 5` is REFUSED too, which is the honest answer.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = 2 + 3


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
