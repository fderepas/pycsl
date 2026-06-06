"""Test 0568 — bounded quantification over a set (quantification P3 / scc3.md Phase B).

`\forall x: int in s; x >= 0` ("every element of set `s` is non-negative") desugars to
`\forall x: int; (x in s) ==> x >= 0` (reusing the P1 typed binder + `in` membership +
implication). For a set, `x in s` lowers to the clean KEY membership
`match Map.get s x with Some _ -> true | None -> false` (scc3.md Phase B — `_csl_in`
dispatches on the collection type, not the positional sequence search that would put
`Array.length` on a map). Given `k in s`, the universal instantiates at `k` by natural
e-matching on `Map.get s k` — no explicit trigger needed (Phase C avoided for sets).

Negative twin 0569 drops `k in s`.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires \forall x: int in s; x >= 0
#@ requires k in s
#@ ensures \result >= 0
#@ assigns \nothing
def pick(s: set, k: int) -> int:
    return k
