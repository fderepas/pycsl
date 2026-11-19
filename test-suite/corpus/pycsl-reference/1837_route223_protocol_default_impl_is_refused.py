r"""Test 1837 — ROUTE #223 WITNESS (expected FAIL/REFUSED): a `Protocol` member's BODY was
discarded while its CONTRACT was assumed.

A protocol member is emitted as a bodyless `val` DEFINED BY ITS CONTRACT — the refinement
target every `#@ conforms_to` is checked against — and `visit_ClassDef` returns WITHOUT
`generic_visit`, so the body is never visited. The code's own comment states the premise:
"the protocol class body carries ONLY member declarations ... so skipping the walk is
correct", and the member's body is "`...`/`pass` by PEP 544 convention".

PEP 544 ALSO PERMITS A DEFAULT IMPLEMENTATION. Write one and the model keeps the CONTRACT
and drops the CODE. At the parent commit this file reported

    [+] Verification SUCCESS! All contracts formally proven.

for `\result == 99` where CPython answers **1**, and the TRUE twin (`\result == 1`) FAILED.
The emission is the whole story:

    val c__m (self: c) : int
      ensures  { (result = 99) }

an abstract val carrying the protocol's contract, with `return 1` nowhere in the module.
Drop the `(Protocol)` base and the identical class FAILS (corpus 1838) — the checker works,
and one token switched it off.

REFUSED, NOT MODELLED. Emitting the default implementation AND keeping the abstract
refinement target is a real design question — the member would be both a specification and a
definition, and `#@ conforms_to` refinement is stated against the former — and the honest
interim answer is to reject a construct the model cannot carry rather than to trust it. A
`...`/`pass` member is untouched (corpus 1839).

FOUND BY WALKING `visit_ClassDef`'s EARLY RETURNS, which is the same generator that produced
route #219 (the FIRST early return of `visit_FunctionDef`) and route #222 (its second). Three
routes from one question: what does this dispatcher decline to visit, and what did the
comment beside it promise about that?
"""
# pycsl-expected: FAIL
from typing import Protocol
_ = 0  # anchor


class P(Protocol):
    #@ ensures \result == 99
    def m(self) -> int:
        return 1


class C(P):
    def __init__(self) -> None:
        self.v: int = 0


#@ ensures \result == 99
def use() -> int:
    c = C()
    return c.m()
