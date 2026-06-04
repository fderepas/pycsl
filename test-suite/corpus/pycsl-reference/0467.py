"""Test 0467 — typed model: `\separated` makes a disjoint array provably unaffected.

Writing a[0] cannot change b[0] because the regions are `\separated`. In the typed model
`\separated(a, 1, b, 1)` lowers to `(separated a 1 b 1)`, giving the prover `a+0 <> b+0`,
so `b[0] == \old(b[0])` is discharged through the `Map.set`/`Map.get` on `int_mem`. The
`\assigns a[0..1]` frame bounds the write. (The canonical typed-model aliasing showcase.)
"""
# pycsl-flags: --memory-model typed
_ = 0  # anchor
#@ requires \valid(a, 1)
#@ requires \valid(b, 1)
#@ requires \separated(a, 1, b, 1)
#@ assigns a[0..1]
#@ ensures a[0] == 9
#@ ensures b[0] == \old(b[0])
#@ ensures \result == k
def write_a(a: list, b: list, k: int) -> int:
    a[0] = 9
    return k
