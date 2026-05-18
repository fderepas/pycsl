"""Test 0337 — Python Reference 3.3.3.1: Metaclasses (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_3_1_a(x: int) -> int:
    """Variation A for Metaclasses."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_3_1_a(4) == 5
