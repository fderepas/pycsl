"""Test 0002 — Python Reference 1.2.1: Lexical and Syntactic definitions"""
_ = 0  # anchor
#@ ensures \result == a + b
def test_notation(a: int, b: int) -> int:
    """Lexical/syntactic notation: basic expression evaluation."""
    return a + b

if __name__ == "__main__":
    assert test_notation(2, 3) == 5
