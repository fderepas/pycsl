# OPEN ROUTE #51 — A `-> str` THAT RETURNS `None` IS BELIEVED, AND THE BELIEF IS DECIDED WITH
# (found 2026-09-08 by relaunch #49, immediately after landing routes #46/#50 at `5f57a95d`)

**This is the residue route #50 NAMED and left**, probed the moment #50 landed: "a local bound
from a CALL that returns `Optional[str]` is not syntactically `None`-bound, so it still reads
as always-present". The probe found the sharper form — the callee does not even have to say
`Optional`.

## The demonstration (`scratchpad/w49/probe50/q2.py`, `[+] Verification SUCCESS` at `5f57a95d`)

```python
@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures True
    def pick(self, c: int) -> str:        # <-- DECLARES `str`
        if c > 0:
            return "a"
        return None                       # <-- and returns None anyway

    #@ requires c < 0
    #@ ensures \result == 7               # <-- FALSE OF THE PROGRAM: Python returns 0
    def m(self, c: int) -> int:
        s = self.pick(c)
        if s is None:
            return 0
        return 7
```

`s` is typed `str` from `pick`'s annotation and is never SYNTACTICALLY bound to `None`, so
route #50's third answer — the always-present `false`, the one deliberately kept because it is
what makes that repair byte-inert where the defect is not — fires and deletes the branch.

## The three controls that localise it, all measured at `5f57a95d`

| probe | shape | verdict |
|---|---|---|
| `q1.py` | the callee declares `Optional[str]` — the HONEST spelling | fails closed |
| `q4.py` | the callee declares `-> int` and returns `None` | fails closed (the int path has no always-present arm; it reaches route #44's opaque `pycsl_none`) |
| `q2.py` | the callee declares `-> str` and returns `None` | **PROVES a contract false of the program** |

So the route is exactly: **a SCALAR-`str` return annotation that the body contradicts, consumed
by an `is None` test inside a `@mutable_state` class.**

## CENSUS — it is live in the mirror, and the count is small (AST scan, this tree)

Functions annotated `-> str`/`-> int`/`-> bool`/`-> float`/`-> bytes` containing a literal
`return None`:

    mirror (src/self-annotate/src)   10      live (src/pycsl)   3
    src/pycsl_lib                     0      both corpora       0

Of the ten mirror sites exactly ONE is `-> str` — `module6_whyml/stmt_control_flow.py::
_try_union_is_none_match` — and the other nine are `-> int`, which the `q4` control shows fails
closed today. The three live-only sites are `agents/agent_annotate/guards.py::
_rewrite_return_in_if_inside_while` (`-> str`), `module6_whyml/expressions.py::
_disp_state_independent` (`-> bool`) and `module6_whyml/abstract_ops.py::
_advance_past_referenced_axiom_decls` (`-> int`).

## TWO CANDIDATE REPAIRS, and the choice is a real trade

1. **REFUSE THE LIE (Module 4).** A function whose return annotation is a non-`Optional` scalar
   may not `return None`. Fail-closed, cheap to write, and it says something true. COST: it
   breaks the ten mirror functions until their annotations are corrected to `Optional[...]`,
   and changing a return annotation changes that mirror's emission and owes a re-proof — for
   nine of them to state something the model already fails closed on.
2. **STOP DECIDING (Module 6).** Treat a str-typed local bound from a CALL to a same-module
   function that can return `None` as `AMBIG`, i.e. route #46's mark reached through the call
   graph. Narrower — it costs only the one `-> str` site — but it needs callee-body knowledge
   at the caller's emission, which the emitter has only as `_module_method_return_annotations`
   today.

**RECOMMENDATION: (1), scoped to `-> str` only.** The `-> int` half is fail-closed already, so
a refusal there buys nothing and costs nine re-annotations; the `-> str` half is the live route
and has exactly one mirror site to fix. That keeps the repair honest and its blast radius one
file.

## SHAPE (b), FOUND MINUTES LATER AND WORSE — THE FIELD NEEDS NO LIE AT ALL

`scratchpad/w49/probe50/q5.py`, `[+] Verification SUCCESS` at `b0e9b284`:

```python
@mutable_state
@dataclass
class C:
    name: str = ""

    #@ requires True
    #@ ensures \result == 7        # <-- FALSE: with `o.name = None`, Python returns 0
    #@ assigns \nothing
    def probe(self) -> int:
        if self.name is None:
            return 0
        return 7

o = C(); o.name = None; assert o.probe() == 0     # runs, and holds
```

There is no annotation lie here and no branch join: a `dataclass` field hint is not enforced
by Python, the caller simply stores `None`, and the always-present arm answers `false` from
the field's declared TYPE. **The common thread of routes #50, #51(a) and #51(b) is one
sentence: the model decides `is None` from a TYPE where only a BINDING could justify it.**

**The field case is the expensive one and the cost must be measured before it is built.**
Nothing establishes a field's non-None-ness — its value comes from outside the function — so
the sound answer is the opaque `str_eq_op self.<f> pycsl_none_str`, i.e. UNDECIDABLE. The
emitter's own code leans on such guards (`self._current_self_type = None` in
`_reset_function_state`, read back as `is None` elsewhere), so this will move mirror emission
and may cost whole-file proofs. That is honest work, not a hidden cost, and it is the reason
this shape is RECORDED here rather than landed in the same increment as #50.
