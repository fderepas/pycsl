"""Test 0091 — PyCSL Annotation Reference 3.1.7 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ requires arr[0] >= 0
#@ ensures arr[0] == \old(arr[0]) + 1
#@ assigns arr[0..1]
def test_at_incr(arr: list) -> None:
    """At: single increment with label."""
    #@ label SNAP
    arr[0] = arr[0] + 1

if __name__ == "__main__":
    a = [7]
    test_at_incr(a)
    assert a[0] == 8
