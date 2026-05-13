"""Quantifier test: \exists in a precondition — guarantees a match exists."""

#@ requires \valid(arr, n) and n >= 1
#@ requires \exists j; 0 <= j and j < n and arr[j] == target
#@ assigns \nothing
#@ ensures \result >= 0
def find_index(arr: list, n: int, target: int) -> int:
    i = 0
    found = 0
    result = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant found == 0 or found == 1
    #@ loop invariant result >= 0
    #@ loop variant n - i
    while i < n:
        if found == 0:
            if arr[i] == target:
                result = i
                found = 1
        i = i + 1
    return result
