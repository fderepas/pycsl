"""Test 0325 — Python Reference 3.2.13.2.3: Frame object methods (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_13_2_3_a(x: int) -> int:
    """Variation A for Frame object methods."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_13_2_3_a(4) == 5
