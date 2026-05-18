"""Test 0221 — Python Reference 1.2.1: Lexical and Syntactic definitions (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_1_2_1_a(x: int) -> int:
    """Variation A for Lexical and Syntactic definitions."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_1_2_1_a(4) == 5
