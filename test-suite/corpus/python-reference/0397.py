"""Test 0397 — Python Reference 5.3.2: Finders and loaders (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_3_2_a(x: int) -> int:
    """Variation A for Finders and loaders."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_3_2_a(4) == 5
