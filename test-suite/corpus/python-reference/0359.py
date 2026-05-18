"""Test 0359 — Python Reference 3.3.10: Customizing positional arguments in class pattern matching (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_10_a(x: int) -> int:
    """Variation A for Customizing positional arguments in class pattern matching."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_10_a(4) == 5
