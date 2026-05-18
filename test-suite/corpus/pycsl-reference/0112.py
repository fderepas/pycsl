"""Test 0112 — PyCSL Annotation Reference 3.2.7 (variation A)"""
_ = 0  # anchor
#@ ensures \result == a - b + c
def test_add_sub_mix(a: int, b: int, c: int) -> int:
    """Mixed addition and subtraction."""
    return a - b + c

if __name__ == "__main__":
    assert test_add_sub_mix(10, 3, 5) == 12
