"""Test 0483 — Python Reference 8.4.3: :keyword:`!else` clause (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_4_3_a(x: int) -> int:
    """Variation A for :keyword:`!else` clause."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_4_3_a(4) == 5
