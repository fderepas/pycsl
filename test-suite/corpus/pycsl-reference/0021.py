"""Test 0021 — PyCSL Annotation Reference 3.2.1"""
_ = 0  # anchor
#@ requires \length(arr) == n
#@ requires n > 0
#@ ensures \forall i; 0 <= i and i < n ==> arr[i] >= 0
#@ assigns arr[0..n]
def test_quantifiers(arr: list, n: int) -> None:
    """Quantifier operators: \forall and \exists."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \forall j; 0 <= j and j < i ==> arr[j] >= 0
    #@ loop variant n - i
    while i < n:
        if arr[i] < 0:
            arr[i] = 0 - arr[i]
        i = i + 1

if __name__ == "__main__":
    a = [-1, 2, -3]
    test_quantifiers(a, 3)
    assert all(x >= 0 for x in a)
