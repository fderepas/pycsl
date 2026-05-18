"""Test 0485 — Python Reference 8.4.4: :keyword:`!finally` clause (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_4_4_a(x: int) -> int:
    """Variation A for :keyword:`!finally` clause."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_4_4_a(4) == 5
