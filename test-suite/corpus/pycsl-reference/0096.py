"""Test 0096 — PyCSL Annotation Reference 3.1.10 (variation A)"""
_ = 0  # anchor
#@ requires \length(a) >= 1
#@ requires \length(b) >= 1
#@ requires \separated(a, 1, b, 1)
#@ ensures a[0] == 99
#@ assigns a[0..1]
def test_separated_single(a: list, b: list) -> None:
    """Separated: single-element regions."""
    a[0] = 99

if __name__ == "__main__":
    a = [0]
    b = [1]
    test_separated_single(a, b)
    assert a[0] == 99
