"""Test 0464 — store model: `\old(arr[i])` heap snapshot across an array write.

Store-model twin of 0463: identical program under the single global `store` heap (the
`\old` lowers to `Map.get (old !store) (arr + 0)`). Exercises the store-model heap path.
"""
# pycsl-flags: --memory-model store
_ = 0  # anchor
#@ requires \length(arr) >= 1
#@ ensures arr[0] == \old(arr[0]) + 1
#@ ensures \result == k
def bump0(arr: list, k: int) -> int:
    arr[0] = arr[0] + 1
    return k
