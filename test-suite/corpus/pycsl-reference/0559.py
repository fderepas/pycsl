"""Test 0559 — recursive (inductive) lemma over a #@ datatype (lemma.md P2/S3).

`to_int` has NO sign postcondition, so `to_int(n) >= 0` is NOT provable by SMT
alone (it needs induction on `n`). The recursive `#@ lemma to_int_nonneg` supplies
it: its self-call on the structurally-smaller `m` is the induction hypothesis, and
`#@ \variant n` makes the recursion well-founded. Lowers to `let rec lemma … variant
{ n } = match … to_int_nonneg m … end`. No proof assistant involved.
"""
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
#@ \variant n
#@ assigns \nothing
def to_int_nonneg(n: Nat) -> None:
    match n:
        case Z():
            pass
        case S(m):
            to_int_nonneg(m)
