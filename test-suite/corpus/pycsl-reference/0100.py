"""Test 0100 — PyCSL Annotation Reference 3.2.1 (variation A)"""
_ = 0  # anchor
#@ requires \length(arr) == n
#@ requires n >= 0
#@ ensures \forall i; 0 <= i and i < n ==> arr[i] == 0
#@ assigns arr[0..n]
def test_forall_zero(arr: list, n: int) -> None:
    """Forall: all elements set to zero."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \forall j; 0 <= j and j < i ==> arr[j] == 0
    #@ loop variant n - i
    while i < n:
        arr[i] = 0
        i = i + 1

if __name__ == "__main__":
    a = [1, 2, 3]
    test_forall_zero(a, 3)
    assert a == [0, 0, 0]
