"""Test 0626 — growable list local via the seq model: concat proves the length law (07-1705 P3).

A list local that is *grown* (`a += b`) is modelled as a `ref (seq int)` (seq-promotion
analysis), so concatenation is `a := !a ++ snapshot(b)` over the immutable `seq.Seq` `++` — whose
length-additive axiom lets `len(a)` after the concat **prove** `3 + 2 == 5`. The previous opaque
`array_extend` model could only type-check this, not prove the assembled length.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \result == 5
#@ assigns \nothing
def build() -> int:
    a = [1, 2, 3]
    b = [4, 5]
    a += b
    return len(a)
