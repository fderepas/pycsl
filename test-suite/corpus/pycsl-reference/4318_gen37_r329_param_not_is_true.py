r"""Test 4318 -- gen #37 route #329 (expected FAIL): int parameter `n == 1`: `if not (n is True): return 0` PROVED `\result == 7` (CPython 0). REFUSED.
"""
# pycsl-expected: FAIL
#@ requires n == 1
#@ ensures \result == 7
#@ assigns \nothing
def g(n: int) -> int:
    if not (n is True):
        return 0
    return 7

if __name__ == "__main__":
    assert g(1) == 7, g(1)
