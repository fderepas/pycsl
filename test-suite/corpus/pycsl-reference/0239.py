"""Test 0239 — PyCSL Annotation Reference 7.2 (tuple unpack assignment)"""
_ = 0  # anchor
#@ requires a >= 0 and b >= 0
#@ ensures \result >= 0
def test_swap_unpack(a: int, b: int) -> int:
    x, y = a, b
    return x + y

if __name__ == "__main__":
    assert test_swap_unpack(3, 4) == 7
    assert test_swap_unpack(0, 0) == 0
