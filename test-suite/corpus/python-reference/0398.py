"""Test 0398 — Python Reference 5.3.2: Finders and loaders (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_3_2_b(x: int) -> int:
    """Variation B for Finders and loaders."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_3_2_b(3) == 6
