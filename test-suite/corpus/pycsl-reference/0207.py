"""Test 0207 - ghost counter in while loop"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == n
def count_to_n(n: int) -> int:
    i: int = 0
    #@ ghost count = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant count == i
    #@ loop variant n - i
    while i < n:
        #@ ghost count += 1
        i = i + 1
    return i
