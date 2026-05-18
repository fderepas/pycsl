"""Test 0409 — Python Reference 5.4.4: __path__ attributes on modules (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_4_4_a(x: int) -> int:
    """Variation A for __path__ attributes on modules."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_4_4_a(4) == 5
