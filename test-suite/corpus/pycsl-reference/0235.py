"""Test 0235 — PyCSL Annotation Reference 7.3 (walrus in condition)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result >= 0
def test_walrus_cond(x: int) -> int:
    if (n := x + 1) > 5:
        return n
    return x

if __name__ == "__main__":
    assert test_walrus_cond(10) == 11
    assert test_walrus_cond(2) == 2
