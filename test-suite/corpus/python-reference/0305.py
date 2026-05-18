"""Test 0305 — Python Reference 3.2.8.8: Classes (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_8_8_a(x: int) -> int:
    """Variation A for Classes."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_8_8_a(4) == 5
