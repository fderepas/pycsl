r"""Test 10450 -- run #9 u72, review rt80 R1a, route #628 (FAIL, PRE-EXISTING). `qd72` has no `def f`: it
re-exports qc72's `f` (returns 1). The program defines its OWN `f` (returns 2). pycsl found no in-file `f`
in qd72 and rewrote `qd72.f()` to the bare `f`, which bound to the local def, so `g() == 2` PROVED at L20.
CPython runs qc72.f and prints "result 1". Now the re-export is followed to qc72 and `qd72.f()` binds to
qc72's `f` under its own name: the claim fails.
"""
# pycsl-expected: FAIL
import qd72


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return qd72.f()


if __name__ == "__main__":
    print("result", g())
