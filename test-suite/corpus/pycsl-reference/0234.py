"""Test 0234 — PyCSL Annotation Reference 7.3 (walrus operator)"""
_ = 0  # anchor
#@ requires x > 0
#@ ensures \result > 0
def test_walrus(x: int) -> int:
    y = (z := x + 1)
    return y

if __name__ == "__main__":
    assert test_walrus(5) == 6
    assert test_walrus(1) == 2
