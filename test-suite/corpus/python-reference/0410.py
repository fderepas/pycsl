"""Test 0410 — Python Reference 5.4.4: __path__ attributes on modules (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_4_4_b(x: int) -> int:
    """Variation B for __path__ attributes on modules."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_4_4_b(3) == 6
