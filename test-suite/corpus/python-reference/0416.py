"""Test 0416 — Python Reference 5.5.1: Path entry finders (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_5_1_b(x: int) -> int:
    """Variation B for Path entry finders."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_5_1_b(3) == 6
