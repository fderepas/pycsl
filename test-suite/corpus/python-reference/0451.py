"""Test 0451 — Python Reference 6.6: Unary arithmetic (variation A)"""
_ = 0  # anchor
#@ ensures \result == 0 - x
def test_unary_a(x: int) -> int:
    """Unary negation operator."""
    return 0 - x

if __name__ == "__main__":
    assert test_unary_a(5) == -5
