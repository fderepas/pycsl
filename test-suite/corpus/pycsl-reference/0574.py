"""Test 0574 — mutually-inductive predicates (`#@ inductive … with …`, inductive.md P2).

`even` and `odd` are defined as ONE least-fixpoint group: each rule references the other
predicate, so they cannot be declared separately (the first would reference the
not-yet-declared second). A `#@ with <q>(<sig>):` continuation block joins `q` into the
group started by `#@ inductive`; the whole group folds into one Why3
`inductive even int = | … with odd int = | …` (no closing `end`). Introduction discharges
`even(4)`: even(0) → odd(1) → even(2) → odd(3) → even(4).
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ inductive even(n: int):
#@     even_zero: even(0)
#@     even_succ: \forall m: int; odd(m) ==> even(m + 1)
#@ with odd(n: int):
#@     odd_succ: \forall m: int; even(m) ==> odd(m + 1)


#@ ensures even(4)
#@ assigns \nothing
def fact() -> int:
    return 0
