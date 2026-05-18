"""Test 0226 — Python Reference 2.1.2: Physical lines (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_1_2_b(x: int) -> int:
    """Variation B for Physical lines."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_1_2_b(3) == 6
