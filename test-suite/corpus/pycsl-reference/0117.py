"""Test 0117 — PyCSL Annotation Reference 3.2.9 (variation B)"""
_ = 0  # anchor
#@ ensures \result == +x
def test_unary_plus(x: int) -> int:
    """Unary plus (identity)."""
    return x

if __name__ == "__main__":
    assert test_unary_plus(7) == 7
