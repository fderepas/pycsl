r"""Test 10471 -- run #9 u73, route #631 (u73 probe g1; FAIL if PRE-EXISTING, see the u73 report). The
package zu73c has a submodule b.py and a module-level PEP 562 `__getattr__` that answers "b" with a class
whose `one()` returns 2. CPython's `from zu73c import b` looks the attribute up FIRST, so `__getattr__`
answers and the submodule is never loaded: `cd <tree root> && python <this file>` prints "result 2".
REFUSED: PYCSL-SEM-IMPORT-MODULE-HOOK (u73: a module-level `__getattr__` / `__mro_entries__` in a reached
module other than the program).
"""
# pycsl-expected: FAIL
from zu73c import b


#@ ensures \result == 1
def g() -> int:
    return b.one()


if __name__ == "__main__":
    print("result", g())
