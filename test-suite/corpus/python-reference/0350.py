"""Test 0350 — Python Reference 3.3.3.7: Uses for metaclasses (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_3_7_b(x: int) -> int:
    """Variation B for Uses for metaclasses."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_3_7_b(3) == 6
