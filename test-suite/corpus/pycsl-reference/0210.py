"""Test 0210 — Rocq fallback: --rocq generates proof obligations when SMT fails.

This test has a loop invariant that is intentionally too weak for the postcondition,
causing SMT solvers to fail. The --rocq flag generates .v proof skeletons.
The test verifies that .v files are generated (expected SMT failure).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result >= n
def accumulate_weak(n: int) -> int:
    """Sum 1+1+...+1 (n+1 times). Invariant only tracks s >= 0, not s >= i."""
    s = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n + 1
    #@ loop invariant s >= 0
    #@ loop variant n - i
    while i <= n:
        s = s + 1
        i = i + 1
    return s

if __name__ == "__main__":
    assert accumulate_weak(0) == 1
    assert accumulate_weak(5) == 6
