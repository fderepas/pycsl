r"""Test 10451 -- run #9 u72, review rt80 R1f, route #628 (FAIL, PRE-EXISTING). `qe72` binds `f = _b.f`
(`import qc72 as _b`; qc72.f returns 1). The program's own `f` returns 2. `qe72.f()` was rewritten to the
bare `f` and bound to the local def: `g() == 2` PROVED at L20. CPython prints "result 1". Now the
assignment re-export is followed to qc72: the claim fails.
"""
# pycsl-expected: FAIL
import qe72


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return qe72.f()


if __name__ == "__main__":
    print("result", g())
