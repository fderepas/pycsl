"""Test 0300 — Python Reference 3.2.8.5: Asynchronous generator functions (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_8_5_b(x: int) -> int:
    """Variation B for Asynchronous generator functions."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_8_5_b(3) == 6
