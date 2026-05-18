"""Test 0311 — Python Reference 3.2.10.2: Special methods (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_10_2_a(x: int) -> int:
    """Variation A for Special methods."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_10_2_a(4) == 5
