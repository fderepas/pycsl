"""Test 0497 — Python Reference 8.10.1: Generic functions (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_10_1_a(x: int) -> int:
    """Variation A for Generic functions."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_10_1_a(4) == 5
