"""Test 0565 — full P2 quantified-fact wrapper over a recursive #@ datatype (scc2.md).

`all_nonneg`'s postcondition is a universal over the recursive datatype `Nat`,
`\forall x: Nat; to_int(x) >= 0` — NOT SMT-dischargeable directly (it needs
induction). The recursive `#@ lemma to_int_nonneg` proves it by induction; `#@ uses
to_int_nonneg` cites that lemma so it is emitted BEFORE the wrapper (scc2.md (B)),
putting its general fact `\forall n. to_int(n) >= 0` in scope to discharge the goal.

Two orderings are at play, both now handled:
  (A) `to_int` (named in the ensures) before the wrapper — the scc.md contract-
      reference edge;
  (B) the lemma before the wrapper — the scc2.md `#@ uses` citation edge.

`#@ uses` is a NON-instantiating ordering citation (cf. an explicit
`to_int_nonneg(Z())` body call, which also works but instantiates a dummy argument).
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


#@ ensures \forall x: Nat; to_int(x) >= 0
#@ uses to_int_nonneg
#@ assigns \nothing
def all_nonneg() -> int:
    return 0
