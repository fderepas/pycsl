r"""Test 1834 — ROUTE #222 WITNESS (expected FAIL/REFUSED): a `#@ requires` on an
`@overload` stub was SILENTLY DISCARDED.

An `@overload` family contributes only its `#@ ensures` clauses: each becomes the guarded
postcondition `isinstance(p, T) ==> Q` on the IMPLEMENTATION, and the stub node itself is
discarded (`_is_overload_stub` / `_synthesize_overload_guard`, which reads `csl_ensures` and
nothing else). Every OTHER clause went nowhere and said nothing.

MEASURED at the parent commit, with the declared precondition plainly violated:

    #@ requires x > 100
    @overload
    def f(x: int) -> int: ...
    #@ ensures \result == x
    def f(x: int) -> int:  return x
    #@ ensures \result == 0
    def use() -> int:      return f(0)
    [+] Verification SUCCESS! All contracts formally proven.

and the emission shows the clause is not weakened but ABSENT:

    let f (x: int) : int  ensures { (result = x) }  =  x

Write the identical `#@ requires x > 100` on the IMPLEMENTATION (corpus 1836) and `f(0)` is
correctly refused — so the checker was never broken, it was bypassed by where the clause was
written.

IT IS SOUND AND STILL WRONG TO BE SILENT. Dropping a PRECONDITION proves the callee under a
weaker assumption, so the body must discharge its postcondition without it and no caller
gains anything false. What is wrong is that a contract the user WROTE is enforced nowhere
while the tool prints `All contracts formally proven` — the headline routes #216 and #219
turn on. Refused rather than carried: deciding which arm's guard a precondition should hide
under is a real design question and not one to answer inside a refusal.

THE REFUSAL LIVES AT THE `_run_pipeline` CHOKE POINT, not at the early return itself, and
that was not the first draft. Placed at `visit_FunctionDef`, the refusal adds a `raise` to a
LIVE function whose MIRROR twin is `\trusted` and declares no `#@ raises`:
`check-trusted-raises-honesty` went 62 -> 64 SILENT (two mirror files carry a `\trusted`
stub named `visit_FunctionDef`, so ONE new raise counted twice), and the mirror emission
gained an `exception` + a `raises` clause. `_run_pipeline`'s twin is `\trusted` and ALREADY
in that population, so the refusal there costs nothing — the choke-point rule routes
#206-#215 used. Worth noticing HOW that cost surfaced: the first placement passed fidelity
AND the corpus byte-diff (0 MOVED over 1328 files) and still moved a trust ratchet by two. A
byte-diff over the CORPUS cannot see a cost that lands in the MIRROR.

HOW IT WENT UNNOTICED: `@overload` appears in ZERO corpus files. The concrete-syntax
reference documents the `ensures` path in careful detail (§ "@overload guarded-contract-family
lowering") and says nothing about the other clauses — which is how a discarded clause
survives, because the documentation describes what IS carried and the reader supplies the
rest.
"""
# pycsl-expected: FAIL
from typing import overload
_ = 0  # anchor


#@ requires x > 100
@overload
def f(x: int) -> int: ...


#@ ensures \result == x
def f(x: int) -> int:
    return x


#@ ensures \result == 0
def use() -> int:
    return f(0)
