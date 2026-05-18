"""Test 0101 — PyCSL Annotation Reference 3.2.1 (variation B)"""
_ = 0  # anchor
#@ requires \length(arr) == n
#@ requires n >= 0
#@ ensures \forall i; 0 <= i and i < n ==> arr[i] == i
#@ assigns arr[0..n]
def test_forall_iota(arr: list, n: int) -> None:
    """Forall: each element equals its index."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \forall j; 0 <= j and j < i ==> arr[j] == j
    #@ loop variant n - i
    while i < n:
        arr[i] = i
        i = i + 1

if __name__ == "__main__":
    a = [0, 0, 0]
    test_forall_iota(a, 3)
    assert a == [0, 1, 2]
