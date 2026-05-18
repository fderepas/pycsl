"""Test 0508 — Python Reference 9.3: Interactive input (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_9_3_b(x: int) -> int:
    """Variation B for Interactive input."""
    return x + x

if __name__ == "__main__":
    assert test_ref_9_3_b(3) == 6
