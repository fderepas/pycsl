"""Test 0243 — Python Reference 2.2: Other tokens (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_2_a(x: int) -> int:
    """Variation A for Other tokens."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_2_a(4) == 5
