"""Test 0349 — Python Reference 3.3.3.7: Uses for metaclasses (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_3_7_a(x: int) -> int:
    """Variation A for Uses for metaclasses."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_3_7_a(4) == 5
