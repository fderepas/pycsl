"""Test 0765 — string concatenation is content-faithful (not just length).

cleared-string.md S3. `(a + b)[:len(a)] == a` — the headline concat-content
claim. `a + b` lowers to `str_concat_op` pinned to Why3's native `concat a b`,
and the slice to `String.substring`; Why3 1.8.2's rich `string.String` theory
(`prefixof_concat` / `substring`) discharges the exact-CONTENT postcondition with
NO new axiom. The old length-only model could prove only `len((a+b)[:len a]) ==
len a`, never that the prefix EQUALS `a`.
"""
_ = 0  # anchor


#@ ensures \result == a
#@ assigns \nothing
def concat_prefix(a: str, b: str) -> str:
    return (a + b)[:len(a)]
