"""Test 0222 — Python Reference 1.2.1: Lexical and Syntactic definitions (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_1_2_1_b(x: int) -> int:
    """Variation B for Lexical and Syntactic definitions."""
    return x + x

if __name__ == "__main__":
    assert test_ref_1_2_1_b(3) == 6
