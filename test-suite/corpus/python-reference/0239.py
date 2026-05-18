"""Test 0239 — Python Reference 2.1.9: Whitespace between tokens (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_1_9_a(x: int) -> int:
    """Variation A for Whitespace between tokens."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_1_9_a(4) == 5
