"""Test 0302 — Python Reference 3.2.8.6: Built-in functions (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_8_6_b(x: int) -> int:
    """Variation B for Built-in functions."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_8_6_b(3) == 6
