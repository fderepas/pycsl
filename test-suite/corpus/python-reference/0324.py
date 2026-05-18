"""Test 0324 — Python Reference 3.2.13.2.2: Special writable attributes (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_13_2_2_b(x: int) -> int:
    """Variation B for Special writable attributes."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_13_2_2_b(3) == 6
