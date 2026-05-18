"""Test 0360 — Python Reference 3.3.10: Customizing positional arguments in class pattern matching (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_10_b(x: int) -> int:
    """Variation B for Customizing positional arguments in class pattern matching."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_10_b(3) == 6
