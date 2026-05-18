"""Test 0073 — PyCSL Annotation Reference 2.2.1 (variation B)"""
_ = 0  # anchor
#@ requires n >= 1
#@ ensures \result == n
def test_loop_countdown(n: int) -> int:
    """Loop invariant with countdown pattern."""
    i = n
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant i
    while i > 0:
        i = i - 1
    return n - i

if __name__ == "__main__":
    assert test_loop_countdown(7) == 7
