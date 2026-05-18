"""Test 0415 — Python Reference 5.5.1: Path entry finders (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_5_1_a(x: int) -> int:
    """Variation A for Path entry finders."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_5_1_a(4) == 5
