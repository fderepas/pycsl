"""Test 0480 — Python Reference 8.1: if statement (variation B)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures x >= 10 ==> \result == x
#@ ensures x < 10 ==> \result == 10
def test_if_b(x: int) -> int:
    """if/else: clamp minimum."""
    if x >= 10:
        return x
    else:
        return 10

if __name__ == "__main__":
    assert test_if_b(15) == 15
    assert test_if_b(5) == 10
