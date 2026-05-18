"""Test 0471 — Python Reference 7.11.1.1: Compatibility via ``__lazy_modules__`` (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_7_11_1_1_a(x: int) -> int:
    """Variation A for Compatibility via ``__lazy_modules__``."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_7_11_1_1_a(4) == 5
