"""Test 0253 — Python Reference 2.5.2: String prefixes (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_2_a(x: int) -> int:
    """Variation A for String prefixes."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_2_a(4) == 5
