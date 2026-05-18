"""Test 0498 — Python Reference 8.10.1: Generic functions (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_10_1_b(x: int) -> int:
    """Variation B for Generic functions."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_10_1_b(3) == 6
