"""Test 0274 — Python Reference 2.5.6: Raw string literals (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_6_b(x: int) -> int:
    """Variation B for Raw string literals."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_6_b(3) == 6
