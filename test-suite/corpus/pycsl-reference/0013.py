"""Test 0013 — PyCSL Annotation Reference 3.1.6"""
_ = 0  # anchor
#@ requires \length(arr) >= 2
#@ ensures arr[0] == \old(arr[1])
#@ ensures arr[1] == \old(arr[0])
#@ assigns arr[0..2]
def test_old_expr(arr: list) -> None:
    """Old atom: \old(expr) refers to value at function entry."""
    tmp = arr[0]
    arr[0] = arr[1]
    arr[1] = tmp

if __name__ == "__main__":
    a = [1, 2]
    test_old_expr(a)
    assert a == [2, 1]
