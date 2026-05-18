"""Test 0338 — Python Reference 3.3.3.1: Metaclasses (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_3_1_b(x: int) -> int:
    """Variation B for Metaclasses."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_3_1_b(3) == 6
