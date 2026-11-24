r"""Test 10436 -- run #9 u71, review rt79 w2, route #626 (FAIL, PRE-EXISTING). As 10435, through a
SUB-package: the dependency zd36 does `from zp36.sub import *` and zp36/sub/__init__.py sets
`__all__ = ["b"]`, so CPython loads zp36.sub.b, whose import-time code rebinds `zh36.one`; `cd <tree root>
&& python <this file>` prints "result 5". Base c115e0a5a and u69 73f47db9d PROVED the claim below. REFUSED
by route #483 (PYCSL-R483-IMPORT-TIME-NAMESPACE-WRITER) once the `__all__` submodule is followed.
"""
# pycsl-expected: FAIL
import zh36
from zd36 import three


#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    return zh36.one() + three()


if __name__ == "__main__":
    print("result", g())
