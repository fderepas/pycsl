"""Test 0357 — Python Reference 3.3.9: With Statement Context Managers (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_9_a(x: int) -> int:
    """Variation A for With Statement Context Managers."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_9_a(4) == 5
