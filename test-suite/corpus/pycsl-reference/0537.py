"""Test 0537 — `\\permutation` spec operator plumbing (A2b Gap 1).

`\\permutation(a, b)` is a spec-only predicate asserting `a` is a permutation of
`b` (same multiset of elements). Unlike `\\array_eq` it does NOT unfold to a
first-order formula — permutation needs transitive-closure/multiset reasoning
the SMT solver cannot derive — so it lowers to an UNINTERPRETED Why3
`predicate permut`. This is Gap 1 of the A2b framing-lemma plan
(`a2b-stage4-scaffold.md`): the operator itself, before any axiom about it.

Plumbing driver (no axiom yet): under `requires \\permutation(a, b)` and
`assigns \\nothing`, the same predicate holds at exit — `ensures
\\permutation(a, b)` is discharged by the (uninterpreted-but-consistent)
`permut a b` term being invariant. Fails today: `\\permutation` is not in the
contract grammar (parse error). Flips when the operator is wired
Module2→4→5→6. The reflexivity / reversal AXIOMS (`#@ proof`) come in the later
stage-4 steps.
"""
_ = 0  # anchor
from typing import List


#@ requires \permutation(a, b)
#@ ensures \permutation(a, b)
#@ assigns \nothing
def carries_perm(a: List[int], b: List[int]) -> int:
    return 0
