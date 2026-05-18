"""Test 0402 — Python Reference 5.3.4: The meta path (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_3_4_b(x: int) -> int:
    """Variation B for The meta path."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_3_4_b(3) == 6
