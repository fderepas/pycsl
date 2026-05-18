"""Test 0499 — Python Reference 8.10.3: Generic type aliases (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_10_3_a(x: int) -> int:
    """Variation A for Generic type aliases."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_10_3_a(4) == 5
