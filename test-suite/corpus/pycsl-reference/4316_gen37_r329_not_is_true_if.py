r"""Test 4316 -- gen #37 route #329 (expected FAIL): `if not (x is True): return 0` with `x = 1`: `\result == 7` PROVED (CPython 0) — #42's exploit under `not`. REFUSED.
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    x = 1
    if not (x is True):
        return 0
    return 7

if __name__ == "__main__":
    assert g() == 7, g()
