"""Test 0479 — Python Reference 8.1: if statement (variation A)"""
_ = 0  # anchor
#@ ensures x > 0 ==> \result == 1
#@ ensures x == 0 ==> \result == 0
#@ ensures x < 0 ==> \result == -1
def test_if_a(x: int) -> int:
    """if/elif/else chain: sign function."""
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return 0 - 1

if __name__ == "__main__":
    assert test_if_a(5) == 1
    assert test_if_a(0) == 0
    assert test_if_a(-3) == -1
