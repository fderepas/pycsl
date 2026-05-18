"""Test 0276 — Python Reference 2.5.7: f-strings (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_7_b(x: int) -> int:
    """Variation B for f-strings."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_7_b(3) == 6
