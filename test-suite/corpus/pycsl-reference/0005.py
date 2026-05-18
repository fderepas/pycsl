"""Test 0005 — PyCSL Annotation Reference 2.2.2"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == n
def test_loop_variant(n: int) -> int:
    """Loop variant: termination measure, must decrease and stay >= 0."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_loop_variant(10) == 10
    assert test_loop_variant(0) == 0
