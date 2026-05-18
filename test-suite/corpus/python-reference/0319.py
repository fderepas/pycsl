"""Test 0319 — Python Reference 3.2.13.1.2: Methods on code objects (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_13_1_2_a(x: int) -> int:
    """Variation A for Methods on code objects."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_13_1_2_a(4) == 5
