"""Test 0116 — PyCSL Annotation Reference 3.2.9 (variation A)"""
_ = 0  # anchor
#@ ensures \result == -x
def test_unary_neg(x: int) -> int:
    """Unary negation."""
    return 0 - x

if __name__ == "__main__":
    assert test_unary_neg(5) == -5
