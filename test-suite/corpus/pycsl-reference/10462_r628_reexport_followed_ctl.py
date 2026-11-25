r"""Test 10462 -- run #9 u72, route #628 (PASS control). `qd72.f()` reaches qc72's `f` (1) through the
re-export, the program's own `f` returns 2: `qd72.f() + f() == 3` proves, CPython agrees.
"""
# pycsl-expected: PASS
import qd72


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return 2


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return qd72.f() + f()


if __name__ == "__main__":
    assert g() == 3
