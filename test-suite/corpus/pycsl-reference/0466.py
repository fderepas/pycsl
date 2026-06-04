"""Test 0466 — store model: `\valid(arr, n)` heap-validity precondition.

Store-model twin of 0465 (`\valid` lowers to `(valid !store arr n)`).
"""
# pycsl-flags: --memory-model store
_ = 0  # anchor
#@ requires \valid(arr, n)
#@ requires n >= 1
#@ ensures arr[0] == 5
#@ ensures \result == n
def set_head(arr: list, n: int) -> int:
    arr[0] = 5
    return n
