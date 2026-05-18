"""Test 0355 — Python Reference 3.3.6: Emulating callable objects (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_6_a(x: int) -> int:
    """Variation A for Emulating callable objects."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_6_a(4) == 5
