"""Test 0254 — Python Reference 2.5.2: String prefixes (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_2_b(x: int) -> int:
    """Variation B for String prefixes."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_2_b(3) == 6
