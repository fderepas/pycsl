"""Test 0275 — Python Reference 2.5.7: f-strings (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_7_a(x: int) -> int:
    """Variation A for f-strings."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_7_a(4) == 5
