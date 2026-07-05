"""Test 0203 - bounded int32 with loop and ref variables"""
_ = 0  # anchor
#@ assumes bounded_int(32)
#@ requires 0 <= n and n <= 100
#@ ensures \result == n * (n + 1) // 2
def sum_to_n(n: int) -> int:
    s: int = 0
    i: int = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant s == i * (i + 1) // 2
    #@ loop variant n - i
    while i < n:
        i = i + 1
        s = s + i
    return s
