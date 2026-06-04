"""Test 0465 — typed model: `\valid(arr, n)` heap-validity precondition.

`\valid(arr, n)` asserts arr is an allocated region of length >= n; in the typed model it
lowers to `(valid !int_mem arr n)`. The write arr[0] = 5 is in-bounds under it.
"""
# pycsl-flags: --memory-model typed
_ = 0  # anchor
#@ requires \valid(arr, n)
#@ requires n >= 1
#@ ensures arr[0] == 5
#@ ensures \result == n
def set_head(arr: list, n: int) -> int:
    arr[0] = 5
    return n
