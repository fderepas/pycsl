"""Test 0563 — negative: a non-strictly-positive inductive rule is rejected.

`bad` occurs to the LEFT of a nested implication inside a premise — a
non-strictly-positive occurrence (inductive.md §3 / spec §7.1). It would admit an
inconsistent least fixpoint, so it must be rejected. Why3 rejects the inductive
clause directly ("non strictly positive occurrence of symbol bad"), so soundness
is enforced at the Why3 layer; a cleaner *Module-4 pre-check* is a documented
refinement (see remains.md). Negative twin of the flagship 0562.

Committed `# pycsl-expected: FAIL` and STAYS failing.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ inductive bad(n: int):
#@     rule bad_step: \forall m: int; (bad(m) ==> bad(m)) ==> bad(m + 1)


#@ ensures \result >= 0
#@ assigns \nothing
def f() -> int:
    return 0
