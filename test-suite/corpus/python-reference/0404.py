"""Test 0404 — Python Reference 5.4.1: Loaders (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_4_1_b(x: int) -> int:
    """Variation B for Loaders."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_4_1_b(3) == 6
