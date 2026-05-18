"""Test 0167 — PyCSL Annotation Reference 9.4 (variation B)"""
_ = 0  # anchor
# pycsl-flags: --fun square
#@ ensures \result == x * x
def square(x: int) -> int:
    return x * x

#@ ensures \result == 0
def buggy(x: int) -> int:
    return x

if __name__ == "__main__":
    assert square(4) == 16
