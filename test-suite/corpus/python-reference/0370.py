"""Test 0370 — Python Reference 3.4.4: Asynchronous Context Managers (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_4_4_b(x: int) -> int:
    """Variation B for Asynchronous Context Managers."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_4_4_b(3) == 6
