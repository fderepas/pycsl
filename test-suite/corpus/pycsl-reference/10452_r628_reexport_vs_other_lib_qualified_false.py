r"""Test 10452 -- run #9 u72, review rt80 R1d, route #628 (FAIL, PRE-EXISTING). Two module-qualified calls:
`qf72.f()` (qf72's own `f`, returns 2) and `qd72.f()` (a re-export of qc72's `f`, returns 1). The re-export
was rewritten to the bare `f` and bound to qf72's: `g() == 4` PROVED at L20. CPython prints "result 3".
Now each call binds to its own def: the claim fails.
"""
# pycsl-expected: FAIL
import qf72
import qd72


#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    return qf72.f() + qd72.f()


if __name__ == "__main__":
    print("result", g())
