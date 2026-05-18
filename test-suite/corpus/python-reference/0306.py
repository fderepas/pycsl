"""Test 0306 — Python Reference 3.2.8.8: Classes (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_8_8_b(x: int) -> int:
    """Variation B for Classes."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_8_8_b(3) == 6
