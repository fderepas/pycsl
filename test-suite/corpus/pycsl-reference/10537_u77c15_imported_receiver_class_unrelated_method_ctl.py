r"""Test 10537 -- run #9 u77, review rt87 c15 (route #634), the IMPORTER side of 10532. Control: the helper zu77a.f
declares `#@ assigns \nothing` and returns `r.total()` (R.total pure; an unrelated S.total writes `self.n`).
The importer measures the imported body's frame with the receiver resolved through the annotation `R`, so it is
not refused; the caller claims r.a unchanged (`cd <tree root> && python <this file>` prints "CPython g(R(1,2)) = 1").
run9-u76 REFUSED it (PYCSL-FUNCTION-FRAME in the importer).
"""
# pycsl-expected: PASS
from zu77a import R, f


#@ requires r.a == 1
#@ ensures \result == 1
def g(r: R) -> int:
    f(r)
    return r.a


if __name__ == "__main__":
    print("CPython g(R(1,2)) =", g(R(1, 2)))
