r"""Test 4315 -- gen #37 route #329 (expected FAIL): `x = 1; return 7 if x is True else 0` emitted `if (!x = 1)` and PROVED 7 (CPython 0): the #42 refusal was skipped in an if-expression test. REFUSED (route #42 refusal).
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    x = 1
    return 7 if x is True else 0

if __name__ == "__main__":
    assert g() == 7, g()
