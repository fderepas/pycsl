"""Test 0280 — Python Reference 2.5.9: Formal grammar for f-strings (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_9_b(x: int) -> int:
    """Variation B for Formal grammar for f-strings."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_9_b(3) == 6
