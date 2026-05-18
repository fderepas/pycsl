"""Test 0227 — Python Reference 2.1.3: Comments (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_1_3_a(x: int) -> int:
    """Variation A for Comments."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_1_3_a(4) == 5
