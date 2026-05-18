"""Test 0303 — Python Reference 3.2.8.7: Built-in methods (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_8_7_a(x: int) -> int:
    """Variation A for Built-in methods."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_8_7_a(4) == 5
