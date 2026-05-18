"""Test 0072 — PyCSL Annotation Reference 2.2.1 (variation A)"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == n * 2
def test_loop_double(n: int) -> int:
    """Loop invariant: doubling via addition."""
    s = 0
    i = 0
    #@ loop invariant s == i * 2
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        s = s + 2
        i = i + 1
    return s

if __name__ == "__main__":
    assert test_loop_double(5) == 10
