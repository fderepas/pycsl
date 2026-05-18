"""Test 0426 — Python Reference 5.9: References (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_9_b(x: int) -> int:
    """Variation B for References."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_9_b(3) == 6
