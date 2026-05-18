"""Test 0382 — Python Reference 4.2.5: Builtins and restricted execution (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_4_2_5_b(x: int) -> int:
    """Variation B for Builtins and restricted execution."""
    return x + x

if __name__ == "__main__":
    assert test_ref_4_2_5_b(3) == 6
