"""Test 0424 — Python Reference 5.8.1: __main__.__spec__ (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_8_1_b(x: int) -> int:
    """Variation B for __main__.__spec__."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_8_1_b(3) == 6
