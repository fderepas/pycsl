r"""Test 4320 -- gen #37 route #329 (expected FAIL): `7 if not (n is True) and n == n else 0` under `requires n == 1` PROVED `\result == 0` (CPython 7): `is` under `not` under `and` in an if-expression test. REFUSED.
"""
# pycsl-expected: FAIL
#@ requires n == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(n: int) -> int:
    return 7 if not (n is True) and n == n else 0

if __name__ == "__main__":
    assert g(1) == 0, g(1)
