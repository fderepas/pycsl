"""Test 0628 — element read of a seq-modelled list local after concat (07-1705 P3).

A seq-modelled (growable) list local supports element reads: `a[i]` lowers to `Seq.get !a i`.
After `a = [1,2]; b = [3,4]; a += b`, the read `a[0]` proves `== 1` via the `seq.Seq` `++` and
`cons`/`get` axioms — element placement through a concat, on the immutable seq model.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \result == 1
#@ assigns \nothing
def first() -> int:
    a = [1, 2]
    b = [3, 4]
    a += b
    return a[0]
