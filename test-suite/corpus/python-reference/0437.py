"""Test 0437 — Python Reference 6.2.10.2: Examples (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_2_10_2_a(x: int) -> int:
    """Variation A for Examples."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_2_10_2_a(4) == 5
