"""Test 0399 — Python Reference 5.3.3: Import hooks (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_3_3_a(x: int) -> int:
    """Variation A for Import hooks."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_3_3_a(4) == 5
