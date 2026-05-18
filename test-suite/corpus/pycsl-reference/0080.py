"""Test 0080 — PyCSL Annotation Reference 3.1.1 (variation A)"""
_ = 0  # anchor
#@ ensures \result == 0
def test_zero_literal() -> int:
    """Number atom: zero literal."""
    return 0

if __name__ == "__main__":
    assert test_zero_literal() == 0
