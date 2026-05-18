"""Test 0339 — Python Reference 3.3.3.2: Resolving MRO entries (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_3_2_a(x: int) -> int:
    """Variation A for Resolving MRO entries."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_3_2_a(4) == 5
