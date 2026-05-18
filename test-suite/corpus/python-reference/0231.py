"""Test 0231 — Python Reference 2.1.5: Explicit line joining (variation A)"""
_ = 0  # anchor
#@ ensures \result == a + b
def test_explicit_join_a(a: int, \
                          b: int) -> int:
    """Backslash line continuation in function signature."""
    return a + \
           b

if __name__ == "__main__":
    assert test_explicit_join_a(10, 20) == 30
