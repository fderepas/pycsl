"""Test 0473 — strings: __getitem__ slicing (`s[a:b]`).

A slice is a substring of the stated length. PROVES as of strings-plan Stage 2: `s[a:b]`
lowers to Why3 `String.substring s a (b-a)` — the logic symbol in a spec, and a `val
str_sub_op` bridge in a program (body) context. The length postcondition
(`String.length result = b - a`) is discharged from a lemma baked into the bridge's
`ensures` (the general `String.length (substring …)` algebra otherwise OOMs the SMT solver)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires 0 <= a and a <= b and b <= \str_length(s)
#@ ensures \str_length(\result) == b - a
#@ ensures \result == \str_sub(s, a, b)
#@ assigns \nothing
def substr(s: str, a: int, b: int) -> str:
    return s[a:b]
