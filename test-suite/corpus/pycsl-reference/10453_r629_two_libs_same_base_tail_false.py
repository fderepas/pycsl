r"""Test 10453 -- run #9 u72, review rt80 R2a, route #629 (FAIL, PRE-EXISTING; extends route #345).
`class X(qg72.Base)` (m returns 1) and `class Y(qh72.Base)` (m returns 2). Bases are read by their bare tail
`Base`, injected once from the first module import, so Y got qg72's `m` and `x.m() + 10 * y.m() == 11 or
22` PROVED at L20. CPython prints "result 21". REFUSED: PYCSL-SEM-IMPORT-BASE-CLASS-AMBIGUOUS.
"""
# pycsl-expected: FAIL
import qg72
import qh72


class X(qg72.Base):
    pass


class Y(qh72.Base):
    pass


#@ ensures \result == 11 or \result == 22
#@ assigns \nothing
def g(x: X, y: Y) -> int:
    return x.m() + 10 * y.m()


if __name__ == "__main__":
    print("result", g(X(), Y()))
