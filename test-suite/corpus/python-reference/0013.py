"""Test 0013 — Python Reference 2.2: Other tokens"""
_ = 0  # anchor
#@ ensures \result == a + b
def test_other_tokens(a: int, b: int) -> int:
    """Operators, delimiters, and other tokens."""
    c = a + b
    return c

if __name__ == "__main__":
    assert test_other_tokens(2, 3) == 5
