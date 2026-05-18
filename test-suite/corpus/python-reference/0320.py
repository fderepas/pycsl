"""Test 0320 — Python Reference 3.2.13.1.2: Methods on code objects (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_13_1_2_b(x: int) -> int:
    """Variation B for Methods on code objects."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_13_1_2_b(3) == 6
