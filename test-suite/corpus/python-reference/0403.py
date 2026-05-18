"""Test 0403 — Python Reference 5.4.1: Loaders (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_4_1_a(x: int) -> int:
    """Variation A for Loaders."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_4_1_a(4) == 5
