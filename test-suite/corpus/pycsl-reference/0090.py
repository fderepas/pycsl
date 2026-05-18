"""Test 0090 — PyCSL Annotation Reference 3.1.7 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \old(arr[0]) + 5
#@ assigns arr[0..1]
def test_at_five(arr: list) -> None:
    """At: five increments."""
    #@ label L1
    arr[0] = arr[0] + 1
    arr[0] = arr[0] + 1
    arr[0] = arr[0] + 1
    arr[0] = arr[0] + 1
    arr[0] = arr[0] + 1

if __name__ == "__main__":
    a = [0]
    test_at_five(a)
    assert a[0] == 5
