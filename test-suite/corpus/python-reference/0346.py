"""Test 0346 — Python Reference 3.3.3.5: Executing the class body (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_3_5_b(x: int) -> int:
    """Variation B for Executing the class body."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_3_5_b(3) == 6
