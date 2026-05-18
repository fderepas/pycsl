"""Test 0271 — Python Reference 2.5.5: Bytes literals (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_5_a(x: int) -> int:
    """Variation A for Bytes literals."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_5_a(4) == 5
