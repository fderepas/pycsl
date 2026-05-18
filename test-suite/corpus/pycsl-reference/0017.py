"""Test 0017 — PyCSL Annotation Reference 3.1.10"""
_ = 0  # anchor
#@ requires \length(src) >= n
#@ requires \length(dst) >= n
#@ requires \separated(src, n, dst, n)
#@ requires n >= 0
#@ assigns dst[0..n]
def test_separated(src: list, dst: list, n: int) -> None:
    """Separated atom: \separated(a, na, b, nb) asserts disjoint regions."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        dst[i] = src[i]
        i = i + 1

if __name__ == "__main__":
    s = [1, 2, 3]
    d = [0, 0, 0]
    test_separated(s, d, 3)
    assert d == [1, 2, 3]
