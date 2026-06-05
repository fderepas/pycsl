"""Test 0538 — imported permutation axiom over `array int` (A2b Gap 2/3 bridge).

Proves `\\permutation(a, a)` NOT by any first-order unfolding (the `permut`
predicate is uninterpreted) but via a proof-assistant-IMPORTED reflexivity axiom
`permut_refl : forall s. permut s s`, cited with `#@ proof rocq` / `#@ proof
lean`. Cross-validated by 0538.proofs/rocq/Perm.v (`Permutation_refl`) and
0538.proofs/lean/Perm.lean (`List.Perm.refl`).

This is the concrete demonstration that the A2b framing-lemma shape works
end-to-end over `array int` — the stage-4 spike found the mutable `array int` is
sound in a logic axiom (no `seq` snapshot needed; Gap 2 obviated). It is the
first time an imported axiom constrains PyCSL's `\\permutation` operator (Gap 1,
0537); the reversal lemma `permut (rev s) s` is the same shape with a non-trivial
proof (the remaining stage-4 step).

Fails without the axiom (uninterpreted `permut a a` is unprovable); flips to PASS
once the `#@ proof` directives import `permut_refl`.
"""
_ = 0  # anchor
from typing import List


#@ proof rocq Pycsl.Reference.Perm.permut_refl
#@ proof lean Pycsl.Reference.Perm.permut_refl
#@ ensures \permutation(a, a)
#@ assigns \nothing
def self_perm(a: List[int]) -> int:
    return 0
