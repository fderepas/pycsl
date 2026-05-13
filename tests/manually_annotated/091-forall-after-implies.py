"""Quantifier test: \forall after ==> — prove all elements checked so far
differ from the target when the search has not yet found a match."""

#@ requires \valid(arr, n) and n >= 1
#@ requires \exists j; 0 <= j and j < n and arr[j] == target
#@ assigns \nothing
#@ ensures \result >= 0 and \result < n
def search(arr: list, n: int, target: int) -> int:
    i = 0
    found = 0
    result = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant found == 0 or found == 1
    #@ loop invariant result >= 0
    #@ loop invariant found == 1 ==> result < n
    #@ loop invariant found == 0 ==> \exists j; i <= j and j < n and arr[j] == target
    #@ loop variant n - i
    while i < n:
        if found == 0:
            if arr[i] == target:
                result = i
                found = 1
        i = i + 1
    return result
