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

---

# SHAPE (c) — THE PARAMETER, AND IT IS THE CHEAPEST OF THE THREE
# (found 2026-09-09 by relaunch #50, probing the residue class the ladder named)

`scratchpad/w51/p1.py`, `[+] Verification SUCCESS` at `51a771c4`:

```python
@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures \result == 7        # <-- FALSE: `o.probe(None)` returns 0 in Python
    #@ assigns \nothing
    def probe(self, s: str) -> int:
        if s is None:
            return 0
        return 7

o = C(); assert o.probe(None) == 0     # runs, and holds
```

No annotation lie, no field store, no branch join, no call. A `str`-annotated PARAMETER is
enough. It is the cheapest reproduction in the whole class and it needs the least from the
attacker: one parameter and one `is None`.

**CONTROL `scratchpad/w51/p2.py`** — shape (b) with the `@mutable_state` decorator REMOVED:
fails closed. So the gate is exactly `@mutable_state`, for the field shape as for the local
shape, and the three shapes are one defect.

## THE CLASS, RE-STATED WITH ALL THREE MEMBERS MEASURED AT `51a771c4`

| shape | operand of `is None` | verdict | what the model needed and did not have |
|---|---|---|---|
| (a) `q2.py` | a LOCAL bound from a CALL whose `-> str` is contradicted by `return None` | **PROVES a false contract** | the callee's real return set |
| (b) `q5.py` | a FIELD `self.name` declared `str`, stored `None` by a caller | **PROVES a false contract** | nothing establishes a field's non-None-ness |
| (c) `p1.py` | a PARAMETER declared `str`, passed `None` by a caller | **PROVES a false contract** | nothing establishes a parameter's non-None-ness |
| control `q1.py` | callee declares the HONEST `Optional[str]` | fails closed | — |
| control `q4.py` | the same lie at `-> int` | fails closed (reaches route #44's opaque) | — |
| control `p2.py` | shape (b) without `@mutable_state` | fails closed | — |

## WHAT THIS DOES TO THE RECOMMENDATION ABOVE

The recorded recommendation — REFUSE THE LIE in Module 4, scoped to `-> str` — fixes shape
(a) ONLY. Shapes (b) and (c) contain **no lie to refuse**: a `dataclass` field hint and a
parameter hint are both unenforced by Python, and the caller is simply outside the function.
Landing the Module-4 refusal alone would close the cheapest reproduction's SIBLING and leave
the cheapest one open, which is not a closure.

**THE ROOT IS THE ARM, NOT THE ANNOTATION.** `module6_whyml/expressions.py`'s string
`is None` fall-through answers the literal `false` whenever the operand is string-typed and
the class is `@mutable_state`, and route #50 already wrote the sentence that condemns it:
*which answer is right is a question about the BINDING, not about the type.* Route #50 gave
the arm two binding-justified answers (`None#empty` decided, `AMBIG` opaque) and left the
third — the always-present `false` — justified by nothing but the type. Shapes (a), (b) and
(c) are the three ways to reach it with no binding at all.

---

# STATUS — INCREMENT 1 LANDED (shapes (b) and (c) CLOSED); shape (a) is increment 2

**LANDED**: the Module 6 root fix. The always-present answer is now made only about a name
the function actually BINDS (`_r51_bound_names`, collected by route #46's existing pre-scan
walk — same traversal, no nested `def`, so no mirror-coverage movement). A PARAMETER, a
`self.<f>` FIELD and every non-name operand get the same type-preserving `pycsl_none_str`
opaque route #50 installed one arm above: **no new model**.

Shapes (b) and (c) FAIL CLOSED. Shape (a) still proves, and that is correct rather than a
miss — `s = self.pick(c)` *is* a bound local, so only a trustworthy callee annotation can
justify deciding with it. That is increment 2.

## MEASURED, FRESH FROM THE SURFACE

  * mirror emission — **1 of 53 moves** (2 lines), all 53 still emit, **L3-tc 53/53**
  * corpus byte-diff — **0 of 903** pre-existing emissions move; only the two new route
    witnesses `1100`/`1101` do, which is what they are for
  * both fidelity planes **byte-identical to HEAD's own runs** (each is RED at HEAD and is
    used differentially — that is why every handoff says "byte-identical", never "rc=0")
  * route #50's witnesses all still behave: `1085`/`1086`/`1088` FAIL, and `1087` — the
    COMPLETENESS GAIN — still PROVES
  * `1102` is the PRECISION GUARD: a local bound to a literal in the same function keeps its
    DECIDED answer, so this is a narrowing and not a retreat
  * metric UNCHANGED (markers 456 / grep 481 / offset 25); raises-honesty rc=0 at 70;
    mirror-coverage rc=0 at 550/41; doc-coherency rc=0; doc §T.5.12r
  * OWED: the whole-file re-proof of `frontend/Module2_Parser` — the one mirror this moves.

## THE MOVED LINE IS THE ROUTE, IN THE EMITTER'S OWN CONTRACT PARSER

`Module2_Parser::_ContractParser.expect_name(self, val: str = None)` — a parameter whose
declared type is contradicted by **its own default**. Its guard

```python
    if not self.at_name() or (val is not None and not self.at_name(val)):
```

emitted the `val is not None` conjunct as the literal `true` — the conjunct **deleted** — and
every `expect_name()` call with no argument passes `None`, so the deleted conjunct is the
COMMON PATH, not a corner case. Third route running (#46, #50, #51) that turned out to be
live in the mirror rather than merely constructible.

## INCREMENT 2 IS BUILT AND HELD BACK, WITH ITS COST MEASURED

`_check_scalar_return_annotation` (`PYCSL-SEM-RETANN`) refuses a `-> str` contradicted by an
explicit `return None`; q2 is refused by it. Held back because its TRUE blast radius is one
VERIFIED (not `\trusted`) mirror method — `stmt_control_flow::_try_union_is_none_match`,
whose `-> str` contradicts both its own body and the LIVE signature (`-> Any`) — and
correcting that annotation owes a full re-proof of that file.

**A FALSE POSITIVE WAS FOUND IN THE CHECK BEFORE IT COULD BE BELIEVED.** The first census
said FOUR functions break; two were `core_ir_semantic::_lemma_calls_trusted` (live AND
mirror), which returns the EMPTY STRING and whose only bare `return` is the early exit of a
NESTED `walk` helper. A nested `def` has its own returns and its own annotation, and the
check now refuses to descend into one. True blast radius: **one** function.

**RESIDUE**: a callee that returns `None` IMPLICITLY, by falling off the end, has no
`return None` for the check to see (`scratchpad/w51/q6.py`). It fails closed today but by a
TYPE ACCIDENT — the missing-return path makes Why3 expect `()` where a `string` is supplied
— not by anything that intends to. The same accident makes `\result != None` on a lying
`-> str` fail (`scratchpad/w51/p3.py`). If either accident is ever fixed, this check must
grow the fall-through arm with it.
