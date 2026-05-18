"""Test 0405 — Python Reference 5.4.2: Submodules (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_4_2_a(x: int) -> int:
    """Variation A for Submodules."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_4_2_a(4) == 5
