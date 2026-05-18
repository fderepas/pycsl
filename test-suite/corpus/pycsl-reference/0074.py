"""Test 0074 — PyCSL Annotation Reference 2.2.2 (variation A)"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == n * n
def test_variant_square(n: int) -> int:
    """Loop variant ensuring termination of squaring loop."""
    s = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant s == i * n
    #@ loop variant n - i
    while i < n:
        s = s + n
        i = i + 1
    return s

if __name__ == "__main__":
    assert test_variant_square(4) == 16
