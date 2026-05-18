"""Test 0240 — Python Reference 2.1.9: Whitespace between tokens (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_1_9_b(x: int) -> int:
    """Variation B for Whitespace between tokens."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_1_9_b(3) == 6
