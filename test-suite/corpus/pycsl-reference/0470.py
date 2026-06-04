"""Test 0470 — store model: `\at(arr[i], L)` value at a label point.

Store-model twin of 0469 (`\at` lowers to `Map.get (store at PRE) (arr + 0)`).
"""
# pycsl-flags: --memory-model store
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \at(arr[0], PRE) + 2
#@ ensures \result == k
def bump_at(arr: list, k: int) -> int:
    #@ label PRE
    arr[0] = arr[0] + 2
    return k
