"""Test 0430 — Python Reference 6.2.2.1: Private name mangling (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_2_2_1_b(x: int) -> int:
    """Variation B for Private name mangling."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_2_2_1_b(3) == 6
