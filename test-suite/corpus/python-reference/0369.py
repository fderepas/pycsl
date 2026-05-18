"""Test 0369 — Python Reference 3.4.4: Asynchronous Context Managers (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_4_4_a(x: int) -> int:
    """Variation A for Asynchronous Context Managers."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_4_4_a(4) == 5
