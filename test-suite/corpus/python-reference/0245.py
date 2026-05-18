"""Test 0245 — Python Reference 2.3.1: Keywords (variation A)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result >= 0
def test_keywords_a(x: int) -> int:
    """if/else keywords."""
    if x > 10:
        return x
    else:
        return x + 1

if __name__ == "__main__":
    assert test_keywords_a(0) == 1
