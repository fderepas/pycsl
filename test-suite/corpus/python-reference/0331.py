"""Test 0331 — Python Reference 3.2.13.5: Static method objects (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_13_5_a(x: int) -> int:
    """Variation A for Static method objects."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_13_5_a(4) == 5
