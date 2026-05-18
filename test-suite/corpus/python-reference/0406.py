"""Test 0406 — Python Reference 5.4.2: Submodules (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_4_2_b(x: int) -> int:
    """Variation B for Submodules."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_4_2_b(3) == 6
