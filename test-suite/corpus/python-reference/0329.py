"""Test 0329 — Python Reference 3.2.13.4: Slice objects (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_13_4_a(x: int) -> int:
    """Variation A for Slice objects."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_13_4_a(4) == 5
