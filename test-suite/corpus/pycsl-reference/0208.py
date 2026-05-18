"""Test 0208 - ghost counter in for loop"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \length(arr) > 0
#@ ensures \result >= 0
def count_positive(arr: list) -> int:
    c: int = 0
    #@ ghost total = 0
    #@ loop invariant 0 <= c and c <= i
    #@ loop invariant total == i
    #@ loop variant \length(arr) - i
    for i in range(len(arr)):
        #@ ghost total += 1
        if arr[i] > 0:
            c = c + 1
    return c
