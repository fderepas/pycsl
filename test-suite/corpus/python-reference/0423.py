"""Test 0423 — Python Reference 5.8.1: __main__.__spec__ (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_8_1_a(x: int) -> int:
    """Variation A for __main__.__spec__."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_8_1_a(4) == 5
