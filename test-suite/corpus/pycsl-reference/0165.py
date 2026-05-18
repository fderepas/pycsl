"""Test 0165 — PyCSL Annotation Reference 9.3 (variation B)"""
_ = 0  # anchor
# pycsl-flags: --fun top
#@ ensures \result == x * 2
def base(x: int) -> int:
    return x + x

#@ ensures \result == x * 2 + 1
def mid(x: int) -> int:
    return base(x) + 1

#@ ensures \result == x * 2 + 2
def top(x: int) -> int:
    return mid(x) + 1

if __name__ == "__main__":
    assert top(3) == 8
