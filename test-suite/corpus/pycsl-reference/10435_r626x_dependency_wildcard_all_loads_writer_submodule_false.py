r"""Test 10435 -- run #9 u71, review rt79 w2, route #626 (FAIL, PRE-EXISTING). The dependency zd35 does
`from zp35 import *`, and zp35/__init__.py sets `__all__ = ["b"]`: CPython's wildcard import LOADS the
submodule zp35.b (every `__all__` name the package does not bind), whose import-time code rebinds
`zh35.one` to a function returning 2, so `cd <tree root> && python <this file>` prints "result 5". Neither
the u60 import walk nor the #483 import-time closure followed the `*` (base c115e0a5a and u69 73f47db9d
PROVED the claim below). The closures now follow the `__all__` submodules: REFUSED by route #483
(PYCSL-R483-IMPORT-TIME-NAMESPACE-WRITER) for zp35/b.py's import-time store.
"""
# pycsl-expected: FAIL
import zh35
from zd35 import three


#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    return zh35.one() + three()


if __name__ == "__main__":
    print("result", g())
