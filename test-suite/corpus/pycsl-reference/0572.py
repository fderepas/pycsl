"""Test 0572 — relational inductive predicate (inductive.md P3): reachability.

`reach(a, b)` is a 2-place least-fixpoint relation whose step rule is NON-structural
(`reach(x+1, z) ==> reach(x, z)` recurses on `x+1`, not a subterm) — exactly the kind of
relation a terminating function cannot express, which is the point of inductive
predicates. Built on the existing single-predicate machinery (inductive.md P1): multi-arg
predicates and nested typed quantifiers in rule bodies already work. Introduction
discharges `reach(0, 2)`: reach(2,2) [refl] → reach(1,2) [step] → reach(0,2) [step].
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ inductive reach(a: int, b: int):
#@     reach_refl: \forall x: int; reach(x, x)
#@     reach_step: \forall x: int; \forall z: int; reach(x + 1, z) ==> reach(x, z)


#@ ensures reach(0, 2)
#@ assigns \nothing
def fact() -> int:
    return 0
