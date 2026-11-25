r"""Test 10474 -- run #9 u73, review rt81 p4, route #633 (FAIL, PRE-EXISTING). `mock.patch("zu73m.b",
K).start()` resolves the DOTTED STRING itself, imports zu73m and sets its attribute b to K: no attribute
store, no setattr call, so no store rule saw it, and `cd <tree root> && python <this file>` prints "result 2".
L19 c115e0a5a and 08e65645c PROVED the claim below. REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED (route #326:
`unittest` joins the dynamic-import list, u73).
"""
# pycsl-expected: FAIL
import zu73m.b
from unittest import mock


class K:
    @staticmethod
    def one() -> int:
        return 2


mock.patch("zu73m.b", K).start()


#@ ensures \result == 1
def g() -> int:
    return zu73m.b.one()


if __name__ == "__main__":
    print("result", g())
