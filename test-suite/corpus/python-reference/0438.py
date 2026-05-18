"""Test 0438 — Python Reference 6.2.10.2: Examples (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_2_10_2_b(x: int) -> int:
    """Variation B for Examples."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_2_10_2_b(3) == 6
