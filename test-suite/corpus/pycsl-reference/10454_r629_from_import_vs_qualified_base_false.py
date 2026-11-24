r"""Test 10454 -- run #9 u72, review rt80 R2c, route #629 (FAIL, PRE-EXISTING; extends route #345).
`from qh72 import Base` (m returns 2) beside `class X(qg72.Base)` (m returns 1): the attribute base was read
as the from-imported `Base`, so `x.m() == 2` PROVED at L20. CPython prints "result 1".
REFUSED: PYCSL-SEM-IMPORT-BASE-CLASS-AMBIGUOUS.
"""
# pycsl-expected: FAIL
from qh72 import Base
import qg72


class X(qg72.Base):
    pass


#@ ensures \result == 2
#@ assigns \nothing
def g(x: X) -> int:
    return x.m()


if __name__ == "__main__":
    print("result", g(X()))
