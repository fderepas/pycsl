"""Test 0418 — Python Reference 5.5.2: Path entry finder protocol (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_5_2_b(x: int) -> int:
    """Variation B for Path entry finder protocol."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_5_2_b(3) == 6
