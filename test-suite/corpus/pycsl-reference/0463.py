"""Test 0463 — typed model: `\old(arr[i])` heap snapshot across an array write.

A single in-place update `arr[0] = arr[0] + 1`. In the typed model the read/write lower
to `Map.get`/`Map.set` on the global heap `int_mem`, and `\old(arr[0])` lowers to
`Map.get (old !int_mem) (arr + 0)`, so the postcondition relates the post- and pre-state
heaps. The function returns a non-heap value (`k`) so its result is not ghost-tainted.
"""
# pycsl-flags: --memory-model typed
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \old(arr[0]) + 1
#@ ensures \result == k
def bump0(arr: list, k: int) -> int:
    arr[0] = arr[0] + 1
    return k
