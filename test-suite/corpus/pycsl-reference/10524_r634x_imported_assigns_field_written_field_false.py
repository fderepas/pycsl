r"""Test 10524 -- run #9 u76, review rt84 F2, route #634. The helper zu76b.f declares `#@ assigns r.b`
(honest) and writes r.b = 5; the caller claims r.b is still 0 (`cd <tree root> && python <this file>` prints
"CPython g(R(1,0)) = 5"): the importer val carries `writes { r.b }`, so the claim is unprovable: VERIFY-FAIL.
"""
# pycsl-expected: FAIL
from zu76b import R, f


#@ requires r.b == 0
#@ ensures \result == 0
def g(r: R) -> int:
    f(r)
    return r.b


if __name__ == "__main__":
    print("CPython g(R(1,0)) =", g(R(1, 0)))
