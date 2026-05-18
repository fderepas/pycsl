"""Test 0198 - PyCSL Annotation Reference 1.1 (sum contract atom)"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 0
#@ ensures \result == \sum(arr, 0, n)
def sum_array(arr: list, n: int) -> int:
    s: int = 0
    i: int = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant s == \sum(arr, 0, i)
    #@ loop variant n - i
    while i < n:
        s = s + arr[i]
        i = i + 1
    return s
