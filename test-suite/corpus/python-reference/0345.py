"""Test 0345 — Python Reference 3.3.3.5: Executing the class body (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_3_5_a(x: int) -> int:
    """Variation A for Executing the class body."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_3_5_a(4) == 5
