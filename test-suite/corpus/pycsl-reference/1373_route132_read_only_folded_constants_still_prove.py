r"""Test 1373 — ROUTES #130/#132 positive control: a folded int constant read in a function, a folded str dict read through `.get` and through a read-only alias, and a function-local import IDENTICAL to the module's, all still PROVE.
"""
# pycsl-expected: PASS
_ = 0  # anchor
from multi_file_lib.r119_plainlib import inc

N = 3
OP = {"a": "b"}


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


#@ ensures \result == "b"
#@ assigns \nothing
def g() -> str:
    d = OP
    if "a" in d:
        return OP.get("a", "")
    return "b"


#@ ensures \result == 4
#@ assigns \nothing
def h() -> int:
    from multi_file_lib.r119_plainlib import inc
    return inc(3)
