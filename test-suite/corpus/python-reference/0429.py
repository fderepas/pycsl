"""Test 0429 — Python Reference 6.2.2.1: Private name mangling (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_2_2_1_a(x: int) -> int:
    """Variation A for Private name mangling."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_2_2_1_a(4) == 5
