"""Test 0097 — PyCSL Annotation Reference 3.1.10 (variation B)"""
_ = 0  # anchor
#@ requires \length(x) >= n
#@ requires \length(y) >= n
#@ requires \separated(x, n, y, n)
#@ requires n >= 1
#@ ensures x[0] == y[0]
#@ assigns x[0..1]
def test_separated_copy_first(x: list, y: list, n: int) -> None:
    """Separated: copy first element between arrays."""
    x[0] = y[0]

if __name__ == "__main__":
    x = [0, 0]
    y = [42, 1]
    test_separated_copy_first(x, y, 2)
    assert x[0] == 42
