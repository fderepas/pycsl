"""Test 0304 — Python Reference 3.2.8.7: Built-in methods (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_8_7_b(x: int) -> int:
    """Variation B for Built-in methods."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_8_7_b(3) == 6
