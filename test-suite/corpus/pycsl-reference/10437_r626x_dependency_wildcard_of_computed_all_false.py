r"""Test 10437 -- run #9 u71, review rt79 w2, route #626 (FAIL, PRE-EXISTING). As 10435, but zp37's
`__all__` is COMPUTED (`["b"] + []`): CPython's `from zp37 import *` in the dependency zd37 still loads
zp37.b, whose import-time code rebinds `zh37.one`, so `cd <tree root> && python <this file>` prints
"result 5". Base c115e0a5a and u69 73f47db9d PROVED the claim below. pycsl cannot read a computed list, so the
wildcard is REFUSED: PYCSL-SEM-IMPORT-WILDCARD-ALL-UNKNOWN.
"""
# pycsl-expected: FAIL
import zh37
from zd37 import three


#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    return zh37.one() + three()


if __name__ == "__main__":
    print("result", g())
