"""Test 0417 — Python Reference 5.5.2: Path entry finder protocol (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_5_2_a(x: int) -> int:
    """Variation A for Path entry finder protocol."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_5_2_a(4) == 5
