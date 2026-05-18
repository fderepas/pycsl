"""Test 0358 — Python Reference 3.3.9: With Statement Context Managers (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_9_b(x: int) -> int:
    """Variation B for With Statement Context Managers."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_9_b(3) == 6
