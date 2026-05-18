"""Test 0224 — PyCSL Annotation Reference 3.2.8 (floor div in contract)"""
_ = 0  # anchor
#@ requires n > 0
#@ ensures \result == n // 2
def test_half(n: int) -> int:
    return n // 2

if __name__ == "__main__":
    assert test_half(10) == 5
    assert test_half(7) == 3
