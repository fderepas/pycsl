"""Test 0452 — Python Reference 6.6: Unary arithmetic (variation B)"""
_ = 0  # anchor
#@ ensures \result == x
def test_unary_b(x: int) -> int:
    """Unary plus (identity)."""
    return x

if __name__ == "__main__":
    assert test_unary_b(7) == 7
