"""genexp-erasure-wall R2c: a generator expression as the argument to `all`/`any`
INSIDE a `#@` spec clause (`#@ assert all(x >= 0 for x in a)`) now PARSES and lowers
FAITHFULLY.

Before R2c the contract grammar rejected it outright (`PyCSL Syntax Error … expected
')' (got NAME 'for')`), and a non-genexp `all(arr)` in a spec assert lowered to the
unconstrained `all_1`/`any_1` oracle (sound-but-vacuous, wall-lessons (l)).

R2c desugars the genexp to the EXISTING bounded quantifier — `all(P for x in dom)`
becomes exactly the CSLNode `\forall x in dom; P` builds, and `any(...)` becomes
`\exists x in dom; P` (quantification.md P3, via `_mk_in`). The emitted WhyML is
BYTE-IDENTICAL to the hand-written quantifier form, so the lowering, IR, and the
3-axiom certificate are all reused — no new value model, no oracle.

POSITIVE witness: each assert is a REAL, provable obligation about the input. Under the
old oracle none of these could be discharged (the answer was an arbitrary `all_1`/`any_1`
bool). See 0939 for the evil twin that MUST NOT prove."""
from typing import List


#@ requires n >= 0 and \length(a) == n
#@ requires \forall i; 0 <= i and i < n ==> a[i] >= 0
#@ assigns \nothing
def all_nonneg(a: List[int], n: int) -> int:
    # `all` over a genexp -> a real universally-quantified obligation, provable from
    # the precondition. No `all_1` oracle in the emitted .mlw.
    #@ assert all(x >= 0 for x in a)
    return 0


#@ requires n >= 1 and \length(a) == n
#@ requires a[0] > 10
#@ assigns \nothing
def any_big(a: List[int], n: int) -> int:
    # `any` over a genexp -> a real existentially-quantified obligation, witnessed by a[0].
    #@ assert any(x > 10 for x in a)
    return 0
