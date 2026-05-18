"""Test 0472 — Python Reference 7.11.1.1: Compatibility via ``__lazy_modules__`` (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_7_11_1_1_b(x: int) -> int:
    """Variation B for Compatibility via ``__lazy_modules__``."""
    return x + x

if __name__ == "__main__":
    assert test_ref_7_11_1_1_b(3) == 6
