"""Test 0473 — Python Reference 7.11.2: Future statements (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_7_11_2_a(x: int) -> int:
    """Variation A for Future statements."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_7_11_2_a(4) == 5
