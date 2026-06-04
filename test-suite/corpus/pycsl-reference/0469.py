"""Test 0469 — typed model: `\at(arr[i], L)` value at a label point.

`\at(arr[0], PRE)` is arr[0] at the entry label PRE (its pre-write value); in the typed
model it lowers to `Map.get (int_mem at PRE) (arr + 0)`. The postcondition relates the
post-write element to its value at the label.
"""
# pycsl-flags: --memory-model typed
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \at(arr[0], PRE) + 2
#@ ensures \result == k
def bump_at(arr: list, k: int) -> int:
    #@ label PRE
    arr[0] = arr[0] + 2
    return k
