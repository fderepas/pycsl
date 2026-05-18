"""Test 0075 — PyCSL Annotation Reference 2.2.2 (variation B)"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == 0
def test_variant_to_zero(n: int) -> int:
    """Loop variant decreasing to zero."""
    i = n
    #@ loop invariant 0 <= i
    #@ loop variant i
    while i > 0:
        i = i - 1
    return i

if __name__ == "__main__":
    assert test_variant_to_zero(100) == 0
