"""Test 0286 — Quicksort on an array of integers (sorted postcondition)"""
# pycsl-flags: --no-proof
_ = 0  # anchor
#@ requires \length(arr) >= hi
#@ requires 0 <= lo
#@ requires lo < hi
#@ ensures lo <= \result and \result < hi
#@ ensures \forall k; lo <= k and k < \result ==> arr[k] <= arr[\result]
#@ ensures \forall k; \result < k and k < hi ==> arr[k] >= arr[\result]
#@ ensures \forall k; 0 <= k and k < lo ==> arr[k] == \old(arr[k])
#@ ensures \forall k; hi <= k and k < \length(arr) ==> arr[k] == \old(arr[k])
#@ assigns arr[lo..hi]
def partition(arr: list, lo: int, hi: int) -> int:
    pivot_idx = hi - 1
    pivot_val = arr[pivot_idx]
    i = lo
    j = lo
    #@ loop invariant lo <= i and i <= j
    #@ loop invariant lo <= j and j <= pivot_idx
    #@ loop invariant \forall k; lo <= k and k < i ==> arr[k] <= pivot_val
    #@ loop invariant \forall k; i <= k and k < j ==> arr[k] > pivot_val
    #@ loop invariant arr[pivot_idx] == pivot_val
    #@ loop invariant \forall k; 0 <= k and k < lo ==> arr[k] == \old(arr[k])
    #@ loop invariant \forall k; hi <= k and k < \length(arr) ==> arr[k] == \old(arr[k])
    #@ loop variant pivot_idx - j
    while j < pivot_idx:
        if arr[j] <= pivot_val:
            t1 = arr[i]
            arr[i] = arr[j]
            arr[j] = t1
            i = i + 1
        j = j + 1
    t2 = arr[i]
    arr[i] = arr[pivot_idx]
    arr[pivot_idx] = t2
    return i

#@ requires \length(arr) >= hi
#@ requires 0 <= lo
#@ requires lo <= hi
#@ ensures \is_sorted(arr, lo, hi)
#@ ensures \forall k; 0 <= k and k < lo ==> arr[k] == \old(arr[k])
#@ ensures \forall k; hi <= k and k < \length(arr) ==> arr[k] == \old(arr[k])
#@ assigns arr[lo..hi]
#@ \variant hi - lo
def quicksort_rec(arr: list, lo: int, hi: int) -> int:
    if hi - lo <= 1:
        return 0
    else:
        p = partition(arr, lo, hi)
        r1 = quicksort_rec(arr, lo, p)
        r2 = quicksort_rec(arr, p + 1, hi)
        return 0

#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \is_sorted(arr, 0, n)
#@ assigns arr[0..n]
def quicksort(arr: list, n: int) -> int:
    r = quicksort_rec(arr, 0, n)
    return 0

if __name__ == "__main__":
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    quicksort(a, 8)
    assert a == [1, 1, 2, 3, 4, 5, 6, 9]

    b = [1]
    quicksort(b, 1)
    assert b == [1]

    c = [5, 4, 3, 2, 1]
    quicksort(c, 5)
    assert c == [1, 2, 3, 4, 5]

    d = [1, 2, 3, 4, 5]
    quicksort(d, 5)
    assert d == [1, 2, 3, 4, 5]

    e = []
    quicksort(e, 0)
    assert e == []

    print("PASS")
