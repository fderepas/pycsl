"""Test 0014 — PyCSL Annotation Reference 3.1.7"""
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \old(arr[0]) + 2
#@ assigns arr[0..1]
def test_at_expr(arr: list) -> None:
    """At atom: \at(expr, L) refers to value at label L."""
    #@ label MID
    arr[0] = arr[0] + 1
    arr[0] = arr[0] + 1

if __name__ == "__main__":
    a = [10]
    test_at_expr(a)
    assert a[0] == 12
