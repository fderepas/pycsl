"""Test 0244 — Python Reference 2.2: Other tokens (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_2_b(x: int) -> int:
    """Variation B for Other tokens."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_2_b(3) == 6
