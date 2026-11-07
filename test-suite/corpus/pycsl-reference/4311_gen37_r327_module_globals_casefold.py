r"""Test 4311 -- gen #37 route #327 (expected FAIL): module-level `k = three()` and `K = seven()` lower to ONE opaque `val constant k`, so `g1() == g2()` relates one constant to itself (CPython 3 != 7). Refused at base by #325 (opaque-int compare); REFUSED first by the module-level PYCSL-R327-IDENT-COLLISION now.
"""
# pycsl-expected: FAIL
#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3
#@ ensures \result == 7
#@ assigns \nothing
def seven() -> int:
    return 7
k = three()
K = seven()
#@ assigns \nothing
def g1() -> int:
    return k
#@ assigns \nothing
def g2() -> int:
    return K
#@ ensures \result == True
#@ assigns \nothing
def h() -> bool:
    return g1() == g2()

if __name__ == "__main__":
    assert h() == True, h()
