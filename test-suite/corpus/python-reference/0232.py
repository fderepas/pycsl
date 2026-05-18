"""Test 0232 — Python Reference 2.1.5: Explicit line joining (variation B)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_explicit_join_b(x: int) -> int:
    """Backslash continuation in expression."""
    result = x \
             + 1
    return result

if __name__ == "__main__":
    assert test_explicit_join_b(7) == 8
