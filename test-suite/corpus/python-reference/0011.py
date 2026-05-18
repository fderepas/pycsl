"""Test 0011 — Python Reference 2.1.9: Whitespace between tokens"""
_ = 0  # anchor
#@ ensures \result == a + b
def test_whitespace_between_tokens(a: int, b: int) -> int:
    """Whitespace separates tokens."""
    return a+b

if __name__ == "__main__":
    assert test_whitespace_between_tokens(3, 4) == 7
