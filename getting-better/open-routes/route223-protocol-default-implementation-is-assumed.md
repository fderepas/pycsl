# Route #223 (CLOSED same day) — a `Protocol` member's BODY is discarded and its CONTRACT is assumed

**Found:** 2026-09-23, gen #31, by walking the early returns of
`Module5_IREmitter.visit_ClassDef` — the third route in one afternoon from the same question.
Route #219 came from the FIRST early return of `visit_FunctionDef`, #222 from its second, and
this from `visit_ClassDef`'s Protocol branch.

## The decisive signature

```python
from typing import Protocol

class P(Protocol):
    #@ ensures \result == 99
    def m(self) -> int:
        return 1                     # the real answer, and it is not 99


class C(P):
    def __init__(self) -> None:
        self.v: int = 0


#@ ensures \result == 99
def use() -> int:
    c = C()
    return c.m()
```

    [+] Verification SUCCESS! All contracts formally proven.

CPython answers **1**. The TRUE twin (`\result == 1`) **FAILS**. The route standard, met
exactly.

## The mechanism, and the comment that named its own premise

`_emit_protocol_interface` emits each member as an `abstract: True` function — a bodyless
`val` DEFINED BY ITS CONTRACT, the refinement target (P1a) every `#@ conforms_to` is checked
against — and `visit_ClassDef` then returns **without** `generic_visit`. The comment beside
that return states the premise in as many words:

> NOTE: no `generic_visit(node)` — the protocol members are emitted explicitly by
> `_emit_protocol_interface` (as `abstract: True` vals). ... **The protocol class body
> carries ONLY member declarations** (no nested classes / assigns that need visiting), so
> skipping the walk is correct.

and `_emit_protocol_interface`'s docstring adds "The member's body (`...`/`pass` by PEP 544
convention) is NOT lowered."

**PEP 544 also permits a DEFAULT IMPLEMENTATION.** Write one and the model keeps the CONTRACT
and drops the CODE. The emission is the whole story:

```
  type p = {  }
  type c = { mutable v: int }
  val c_m_0 () : int           ensures { (result = 99) }
  val c__m (self: c) : int     ensures { (result = 99) }
  val p__m (self: p) : int     ensures { (result = 99) }
  let py_use () : int ensures { (result = 99) } = let c = { v = 0 } in (c_m_0 ())
```

`return 1` appears nowhere in the module, and the inherited member is abstract on the
CONFORMING class too. Drop the `(Protocol)` base and the identical class FAILS.

**LESSON (t3), THIRD INSTANCE OF THE DAY, in its sharpest form yet:** the comment did not
merely fail to mention the case — it ASSERTED the opposite, as the justification for the
skip. "The protocol class body carries ONLY member declarations" is a claim about Python,
and this repository has already learned once (route in `Module5_IREmitter` ~2080) that "out
of scope because it raises" is itself a claim about Python and must be PROBED, not reasoned
about. A justification written beside a skip is the highest-yield thing to falsify, because
the skip is exactly as wide as the claim is wrong.

## The repair (landed): REFUSED, not modelled

`PYCSL-SEM-PROTOCOL-DEFAULT-IMPL` fires when a `Protocol` member has a body that is not
`...`, `pass`, or a docstring. Emitting the default implementation AND keeping the abstract
refinement target is a real design question — the member would be both a specification and a
definition, and `#@ conforms_to` refinement is stated against the former — and the honest
interim answer is to reject a construct the model cannot carry rather than to trust it.

AT THE `_run_pipeline` CHOKE POINT, for the reason route #222 learned an hour earlier: the
natural site is `_emit_protocol_interface`, whose mirror twin is `\trusted` and contains NO
`raise` today, so a refusal there would ADD it to `check-trusted-raises-honesty`'s SILENT
population and move a ratchet. `_run_pipeline` is already in that population.

CENSUS BEFORE LANDING (lesson d3): `class ...(Protocol)` occurs in 3 corpus files, 0 mirror,
0 live and 1 `pycsl_lib` source, and NONE declares a member with a non-trivial body. All
three corpus files and `pycsl_lib/typ` keep their verdicts.

## Witnesses

* `1837_route223_protocol_default_impl_is_refused.py`         — expected FAIL (the carrier)
* `1838_route223_ctl_same_class_without_protocol.py`          — expected FAIL, one token
  apart; this is what makes #223 a route and not a missing feature
* `1839_route223_ctl_declaration_only_protocol_verifies.py`   — expected PASS: a
  declaration-only protocol whose conforming class IS checked against the contract. Without
  it the repair is indistinguishable from a ban on the feature.
