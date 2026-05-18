"""Test 0446 — Python Reference 6.3.2.3: "Starred" subscriptions (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_3_2_3_b(x: int) -> int:
    """Variation B for "Starred" subscriptions."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_3_2_3_b(3) == 6
