"""Test 0004 — PyCSL Annotation Reference 2.2.1"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == n * (n - 1) // 2
def test_loop_invariant(n: int) -> int:
    """Loop invariant: inductive property preserved each iteration."""
    s = 0
    i = 0
    #@ loop invariant s == i * (i - 1) // 2
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        s = s + i
        i = i + 1
    return s

if __name__ == "__main__":
    assert test_loop_invariant(5) == 10  # 0+1+2+3+4 = 10, 5*4/2 = 10 ✓
    assert test_loop_invariant(0) == 0
