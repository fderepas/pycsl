"""Test 0482 — Python Reference 8.4.2: :keyword:`!except*` clause (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_4_2_b(x: int) -> int:
    """Variation B for :keyword:`!except*` clause."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_4_2_b(3) == 6
