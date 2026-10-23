r"""Test 2273 — route #242 (expected FAIL): the nondeterminism one call away. `r` carries no frame
clause, so it was already a plain `let` (fresh per call); but `g` (no writes) only CALLS `r`, and as a
`let function` it froze `r ()` per argument: `g() == g()` PROVED `\result == 1` at f0fc0201 while
CPython `m()` = 0 (two distinct generator objects). A body calling a nondeterministic function is
itself nondeterministic, so `g` is a plain `let` too: unproved.
"""
# pycsl-expected: FAIL
from typing import Any


def r() -> Any:
    return (v for v in [1])


#@ assigns \nothing
def g() -> Any:
    return r()


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    if g() == g():
        return 1
    return 0
