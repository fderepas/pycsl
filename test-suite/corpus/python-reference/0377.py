"""Test 0377 — Python Reference 4.2.3: Annotation scopes (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_4_2_3_a(x: int) -> int:
    """Variation A for Annotation scopes."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_4_2_3_a(4) == 5
