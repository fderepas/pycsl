"""Test 0233 — Python Reference 2.1.6: Implicit line joining (variation A)"""
_ = 0  # anchor
#@ ensures \result == a + b + c
def test_implicit_join_a(a: int, b: int, c: int) -> int:
    """Implicit joining via parentheses."""
    return (a
            + b
            + c)

if __name__ == "__main__":
    assert test_implicit_join_a(1, 2, 3) == 6
