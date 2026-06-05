"""Test 0539 — reversal is a permutation, via an imported framing lemma (A2b Gap 5).

THE headline A2b demonstration: `reverse(xs)` returns `list(reversed(xs))`, and
its postcondition `\\permutation(\\result, xs)` is discharged ONLY by a
proof-assistant-IMPORTED axiom — the SMT solver cannot derive it (the `permut`
predicate is uninterpreted; permutation needs multiset/transitive-closure
reasoning that is not first-order).

`reversed(xs)` models the reversed sequence as `array_rev xs` (an abstract
`array int` op). The imported lemma `rev_permutation : forall s. permut
(array_rev s) s` — proved once in Rocq (`Permutation_rev`) and Lean
(`List.reverse_perm`), cross-validated, cited via `#@ proof` — gives exactly
`permut (array_rev xs) xs`, i.e. `permut \\result xs`.

This is the proof-out philosophy applied to a framing/permutation property: the
reasoning that doesn't fit SMT is done in the proof assistant and carried across
the bridge. Stage-4 spike confirmed the whole shape is sound over `array int`
(no `seq` snapshot; Gap 2 obviated). Builds on 0537 (the `\\permutation`
operator) and 0538 (the first imported `permut` axiom). Fails without the axiom
(uninterpreted `permut (array_rev xs) xs` is unprovable); flips to PASS once the
`#@ proof` directives import `rev_permutation`.
"""
_ = 0  # anchor
from typing import List


#@ proof rocq Pycsl.Reference.Perm.rev_permutation
#@ proof lean Pycsl.Reference.Perm.rev_permutation
#@ ensures \permutation(\result, xs)
#@ assigns \nothing
def reverse(xs: List[int]) -> List[int]:
    return list(reversed(xs))
