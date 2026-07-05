"""Test 0849 — NEGATIVE boundary: map-leaf (dict-of-list) inner mutation is REJECTED.

wrong-lowering-to-fix.md §WL-04f (nested-inner-mutation) residual. The option-(c)
inner-mutation store is implemented for a SEQ leaf only (`List[List[str]]`/
`List[List[float]]` → `array (seq τ)`, write `a[i] <- Seq.set a[i] j v`; 0804/0847),
and the int leaf routes to `matrix int` (0802/0803). A MAP leaf — `List[Dict[int,int]]`
~ `array (map int (option int))` — has NO implemented mutable-inner store: an inner
item write `a[i][k] = v` would need the map analog `a[i] <- map_update a[i] k (Some v)`,
which is a separate (unspiked) construct. Rather than emit an unsound / broken update,
the transpiler REJECTS it — the generic subscript-set path coerces the inner `map`
container to `int` and Why3 type-fails (fail-closed, TYPEERR). This lock documents the
boundary; it MUST stay unproven. If it ever PROVES, a map-leaf inner mutation is being
silently mis-modelled.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List, Dict

#@ requires 0 <= i and i < len(a)
#@ ensures \result == 0
def map_leaf_inner_mutate(a: List[Dict[int, int]], i: int, k: int, v: int) -> int:
    a[i][k] = v
    return 0
