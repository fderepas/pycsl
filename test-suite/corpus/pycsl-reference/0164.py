"""Test 0164 — PyCSL Annotation Reference 9.3 (variation A)"""
_ = 0  # anchor
# pycsl-flags: --fun caller
#@ ensures \result == x + 1
def helper(x: int) -> int:
    return x + 1

#@ ensures \result == x + 2
def caller(x: int) -> int:
    return helper(x) + 1

#@ ensures \result == 999
def unrelated(x: int) -> int:
    return 0

if __name__ == "__main__":
    assert caller(5) == 7
