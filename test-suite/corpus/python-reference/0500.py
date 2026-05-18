"""Test 0500 — Python Reference 8.10.3: Generic type aliases (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_10_3_b(x: int) -> int:
    """Variation B for Generic type aliases."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_10_3_b(3) == 6
