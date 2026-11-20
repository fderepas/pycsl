r"""Test 10293 -- R614 unresolved aliases / unknown callees (lvZ2, run #8; expected FAIL): a parameter annotated through
`P = NewType("P", Path)` (a call-built alias the pass cannot resolve); CPython: False.
REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`), fail-closed.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from typing import NewType

P = NewType("P", Path)


#@ ensures \result == True
#@ assigns \nothing
def f(p: P) -> bool:
    return p == str(p)


if __name__ == "__main__":
    r = f(P(Path("a")))
    print("VIOLATION contract" if r is not True else "result", r)
