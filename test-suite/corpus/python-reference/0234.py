"""Test 0234 — Python Reference 2.1.6: Implicit line joining (variation B)"""
_ = 0  # anchor
#@ ensures \result == x + y
def test_implicit_join_b(x: int, y: int) -> int:
    """Implicit joining in return expression."""
    return (x +
            y)

if __name__ == "__main__":
    assert test_implicit_join_b(5, 3) == 8
