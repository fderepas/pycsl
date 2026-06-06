"""Test 0560 — negative: a recursive lemma WITHOUT `#@ \variant` is rejected.

The soundness lynchpin (lemma.md §3 / spec §7.2). `bad_lemma` calls itself but
declares no `#@ \variant`, so the recursion is ill-founded — an unsound "proof by
assuming the goal" that could derive anything. Module 4 (`_validate_lemma`) rejects
it BEFORE any proving run. Negative twin of the recursive flagship 0559.

Committed `# pycsl-expected: FAIL` and STAYS failing.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ datatype Nat = Z | S(Nat)


#@ \variant n
#@ assigns \nothing
def to_int(n: Nat) -> int:
    match n:
        case Z():
            return 0
        case S(m):
            return 1 + to_int(m)


#@ lemma
#@ ensures to_int(n) >= 0
#@ assigns \nothing
def bad_lemma(n: Nat) -> None:
    match n:
        case Z():
            pass
        case S(m):
            bad_lemma(m)
