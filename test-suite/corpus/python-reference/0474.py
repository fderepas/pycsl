"""Test 0474 — Python Reference 7.11.2: Future statements (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_7_11_2_b(x: int) -> int:
    """Variation B for Future statements."""
    return x + x

if __name__ == "__main__":
    assert test_ref_7_11_2_b(3) == 6
