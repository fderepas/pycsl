"""Test 0301 — Python Reference 3.2.8.6: Built-in functions (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_8_6_a(x: int) -> int:
    """Variation A for Built-in functions."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_8_6_a(4) == 5
