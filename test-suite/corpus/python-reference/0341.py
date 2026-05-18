"""Test 0341 — Python Reference 3.3.3.3: Determining the appropriate metaclass (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_3_3_a(x: int) -> int:
    """Variation A for Determining the appropriate metaclass."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_3_3_a(4) == 5
