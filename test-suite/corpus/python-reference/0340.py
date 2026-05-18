"""Test 0340 — Python Reference 3.3.3.2: Resolving MRO entries (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_3_2_b(x: int) -> int:
    """Variation B for Resolving MRO entries."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_3_2_b(3) == 6
