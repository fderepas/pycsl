"""Test 0378 — Python Reference 4.2.3: Annotation scopes (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_4_2_3_b(x: int) -> int:
    """Variation B for Annotation scopes."""
    return x + x

if __name__ == "__main__":
    assert test_ref_4_2_3_b(3) == 6
