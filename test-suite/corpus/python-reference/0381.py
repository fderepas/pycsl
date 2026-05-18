"""Test 0381 — Python Reference 4.2.5: Builtins and restricted execution (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_4_2_5_a(x: int) -> int:
    """Variation A for Builtins and restricted execution."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_4_2_5_a(4) == 5
