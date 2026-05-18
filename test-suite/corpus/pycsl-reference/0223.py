"""Test 0223 — PyCSL Annotation Reference 7.1 (assert in loop)"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result >= 0
def test_assert_in_loop(n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant total >= 0 and i >= 0 and i <= n
    #@ loop variant n - i
    while i < n:
        assert i >= 0, "index must be non-negative"
        total = total + i
        i = i + 1
    return total

if __name__ == "__main__":
    assert test_assert_in_loop(0) == 0
    assert test_assert_in_loop(4) == 6
