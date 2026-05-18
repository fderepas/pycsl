"""Test 0209 - ghost variable in function postcondition"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == n * (n + 1) / 2
def gauss_sum(n: int) -> int:
    s: int = 0
    i: int = 0
    #@ ghost steps = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant s == i * (i + 1) / 2
    #@ loop invariant steps == i
    #@ loop variant n - i
    while i < n:
        i = i + 1
        #@ ghost steps += 1
        s = s + i
    return s
