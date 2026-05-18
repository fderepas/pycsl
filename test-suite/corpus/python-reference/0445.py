"""Test 0445 — Python Reference 6.3.2.3: "Starred" subscriptions (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_3_2_3_a(x: int) -> int:
    """Variation A for "Starred" subscriptions."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_3_2_3_a(4) == 5
