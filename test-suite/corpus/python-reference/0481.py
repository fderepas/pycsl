"""Test 0481 — Python Reference 8.4.2: :keyword:`!except*` clause (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_4_2_a(x: int) -> int:
    """Variation A for :keyword:`!except*` clause."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_4_2_a(4) == 5
