"""Test 0323 — Python Reference 3.2.13.2.2: Special writable attributes (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_13_2_2_a(x: int) -> int:
    """Variation A for Special writable attributes."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_13_2_2_a(4) == 5
