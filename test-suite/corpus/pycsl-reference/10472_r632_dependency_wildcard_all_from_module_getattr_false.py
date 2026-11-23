r"""Test 10472 -- run #9 u73, review rt81 x3, route #632 (FAIL, PRE-EXISTING). The dependency zu73d does
`from zu73e import *`; zu73e/__init__.py binds no `__all__` but its module-level PEP 562 `__getattr__`
answers the (computed) name "__all__" with ["w"], and CPython's wildcard reads `__all__` with getattr, so it
LOADS zu73e/w.py, whose import-time `zu73h.one = _two` makes `cd <tree root> && python <this file>` print
"result 5". L19 c115e0a5a and 08e65645c PROVED the claim below (no `__all__` binding = nothing followed).
REFUSED: PYCSL-SEM-IMPORT-WILDCARD-ALL-UNKNOWN (u73: an `__init__` with a module-level `__getattr__`).
"""
# pycsl-expected: FAIL
import zu73h
from zu73d import three


#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    return zu73h.one() + three()


if __name__ == "__main__":
    print("result", g())
