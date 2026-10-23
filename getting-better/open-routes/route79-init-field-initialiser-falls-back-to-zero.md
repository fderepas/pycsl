# ROUTE #79 — AN `__init__` FIELD INITIALISER OUTSIDE THE CAPTURE SHAPE SILENTLY BECOMES 0

**STATUS: FOUND 2026-09-11 (gen #8). CLOSED AND FULLY GATED 2026-09-12 (gen #10),
AT ZERO MEASURED COST. The 70% figure below and gen #9's 17-mirror-site correction are BOTH
over-counts and are kept only as the record of how the price came down.**

> ## CLOSING EVIDENCE (gen #10)
>
> | gate | verdict |
> |------|---------|
> | soundness planes | **34/34 green**, rc=0 (`--slow`) |
> | byte-diff, pycsl-reference | **979/979 inert**, 0 MOVED / 0 GONE / 0 APPEARED |
> | byte-diff, python-reference | **2203/2203 inert**, same |
> | zero-byte check, BOTH sides | 0 / 0, `/tmp` at 15% |
> | **mirror emission** | **53/53 BYTE-IDENTICAL — ZERO whole-file re-proofs owed** |
> | IR conformance | 38/38 core + 38/38 front-end, 0 MISMATCH, determinism 10/10 |
> | fidelity | rc=0, 887 verbatim, no mirror sync owed |
> | mirror-coverage ratchet | **549 KEPT** |
> | `check-bespoke-model-drift` | passed WITHOUT `--update` |
> | reference suite | **3340/3359, ZERO XPASS, rc=1**; failure set 19 vs 19 BYTE-IDENTICAL |
>
> ## THE CARRIER THAT WAS NOT IN THIS FILE, AND WHY NO CENSUS COULD HAVE FOUND IT
>
> `_collect_init_construction` computed the parameter set and then did `if not pset: break`.
> **A PARAMETERLESS `__init__` NEVER HAD A SINGLE INITIALISER EXAMINED**, so every computed
> field it set took the literal `0` — the widest form of the defect. Measured:
> `K = 8; class C: def __init__(self): self.x = K + 1` proves `\result == 0`, CPython 9.
> The census in this file is written as *the complement of the live capture rule*, so it can
> only ever enumerate constructors that REACH that rule. **A GUARD'S EARLY EXIT IS PART OF
> THE GUARD, AND A CENSUS DEFINED AS A PREDICATE'S COMPLEMENT SILENTLY EXCLUDES EVERY INPUT
> THAT NEVER REACHED THE PREDICATE.** The repair is placed BEFORE the `break`; witness 1214
> is the witness for that placement specifically.
>
> ## WHY THE MIRROR COST WAS ZERO, WHICH IS NOT THE SAME AS "THE CENSUS WAS WRONG"
>
> The eight mirror sites the census predicts are REAL classifications. They cost nothing
> because **this erasure only bites at an ALLOCATION SITE**: `_field_default` is reached only
> from `_call_record_constructor`. `frontend__ConcurrencyChecker.mlw` emits the record TYPE
> (`mutable strict_mode: int`) and contains NO RECORD LITERAL — the class is never allocated
> in lowered code. **A FIELD-LEVEL CENSUS COUNTS DECLARATIONS; THE DEFECT LIVES AT
> ALLOCATIONS. THE EMISSION IS THE AUTHORITY OVER BOTH.**
>
> A repair that moves nothing anywhere is also the exact shape of route #82's SILENT NO-OP,
> so the zero was NOT taken on trust: the four carriers CHANGED VERDICT (they proved at HEAD
> and refuse now), which proves Module 6 consumes the new IR key.

> ## gen #9 CORRECTION — THE 70% BLAST RADIUS IS AN OVER-COUNT, AND THE REPAIR IS CHEAPER THAN RECORDED
>
> The census below applies the complement of the capture rule and reports **489 of 703 (70%)**,
> concluding that a blanket refusal is off the table. The complement is **not one population, it
> is three**, and only the third is this route:
>
> | class | what it is | count | is it the defect? |
> |-------|-----------|-------|-------------------|
> | (i) | a LITERAL RHS with NO free names (`self.balance = 0`, `self.start = 7`) | **376** | **NO — `field_defaults` captures it faithfully** |
> | (ii) | params-only, captured | 192 | no |
> | (iii) | the RHS names something OUTSIDE the parameter set | **133** | **YES — this is all of #79** |
>
> Class (i) was **verified, not assumed**: conformance golden 0442's source has
> `self.start: int = 7` inside `__init__` and its golden IR carries `field_defaults={'start': 7}`.
> `construction_synth.py`'s own docstring says so too — *"Constant RHS (e.g. `self.start = 7`) is
> already handled by `field_defaults`, so it is intentionally NOT re-captured here."*
>
> Splitting class (iii) again by which arm of `_field_default` it reaches:
>
>     INT arm (the arm THIS route's exploit uses)   72    corpus 0 · mirror 17 · pycsl 32 · lib 23
>     array arm                                     32    corpus 30
>     dict/set arm                                  29    corpus 0
>
> **THERE ARE ZERO INT-ARM SITES IN THE VERIFIED CORPUS**, and none of the 38 IR-conformance
> goldens has one either (every uncaptured field in all 15 record-bearing goldens is a literal).
> So an INT-arm unconstrained-value repair is predicted **byte-inert over the verified corpus and
> over all 38 goldens**; the remaining cost is the **17 mirror sites**, which is a
> whole-file-proof question rather than a completeness regression.
>
> **LESSON: A CENSUS KEYED ON THE COMPLEMENT OF A GUARD MEASURES EVERYTHING THE GUARD DOES NOT
> CAPTURE, WHICH IS NOT THE SAME SET AS EVERYTHING THE GUARD GETS WRONG.** Split the complement by
> WHY each member fell out before pricing a repair from it.
>
> **TWO SIBLING ROUTES CAME OUT OF THAT RE-MEASUREMENT**, both reaching this same erasure site by
> a different upstream cause, and they change the picture for the repair:
>
> * **ROUTE #82 (CLOSED by gen #9, FAITHFULLY)** — a keyword-only or positional-only `__init__`
>   parameter was invisible to the capture rule, so `P(v=7).v` proved `\result == 0`. Found by
>   reading the OUTLIER ROWS of the corrected census: four of the 133 were `PyCSLError`'s
>   `self.filename = filename` and friends, which obviously should have been captured.
>   **Every field #82 recovered LEAVES this route's omitted set**, so #79 is smaller again.
> * **ROUTE #83 (OPEN)** — a field store NESTED IN CONTROL FLOW in `__init__` is never even
>   considered (`for stmt in child.body:  # top-level only`). Blast radius 5, all in
>   `src/pycsl_lib`.
>
> **STRATEGIC CONSEQUENCE:** #79's unconstrained-value repair would close #79 AND #83 at once.
> But #82 shows the better move where the information EXISTS is a FAITHFUL CAPTURE, not an
> unconstrained value — it turns a soundness fix into a completeness GAIN. **Prefer faithful
> capture wherever the value is recoverable; fall back to unconstrained only where it genuinely
> is not.** For #79 proper (`self.n = len(items)`) the value is NOT recoverable at the allocation
> site, so unconstrained remains right there.

**CLASS: the #69 class, the serious one** — a FALSE POSTCONDITION about ordinary, TOTAL Python.
No `no_exception`, no opt-in.

**THIS IS THE WIDEST-REACHING ROUTE FOUND THIS GENERATION.** #77 needs a slice delete and #78
needs `collections.deque`; #79 needs only `self.n = len(items)` in a constructor. That is
ordinary, idiomatic Python that appears in almost any class.

## THE EXPLOIT

```python
from typing import List
class C:
    n: int
    def __init__(self, items: List[int]) -> None:
        self.n = len(items)

#@ ensures \result == 0
def f() -> int:
    c = C([1, 2, 3])
    return c.n
```

    CPython:  3
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

## THE MECHANISM, AND THE FALSE SENTENCE THAT GUARDS IT

`src/pycsl/frontend/module5/construction_synth.py` captures a field initialiser only when the
RHS mentions **`__init__` parameters and nothing else** (the rule is of the form
`names and (names & pset) and names <= pset`). Anything else is **omitted**, and at the
allocation site `_field_default` supplies `rec_info['defaults'].get(fn, 0)` — **a literal
`0`** — because `__init__` is never emitted as a function at all: it is inlined as a record
literal.

The comment says the omitted field *"falls back to its default witness (sound, just less
precise)"*. **It is not less precise, it is WRONG.** "Less precise" would be an unconstrained
value; a literal `0` is a definite false fact, and the emitter then proves postconditions from
it.

**SAME SHAPE AS #78's FALSE JUSTIFICATION.** Both routes are guarded by a comment asserting an
erasure is sound. Treat every such sentence as an unproven lemma — see #78 for the phrase list
worth grepping.

## BOTH DIRECTIONS, MEASURED — AND THE CONTROL THAT BOUNDS IT

| driver | RHS | claim | CPython | PyCSL |
|--------|-----|-------|---------|-------|
| k02 | `self.n = len(items)` | `\result == 0` | **3** | **PROVED** ❌ |
| k02 twin | same | `\result == 3` | 3 | refused (Timeout) |
| k09 | `self.x = n + K` (K a MODULE CONST) | `\result == 0` | **8** | **PROVED** ❌ |
| k10 | `self.b = self.a + 1` (a SELF FIELD) | `\result == 0` | **6** | **PROVED** ❌ |
| **k03 — the CONTROL** | `self.x = n + 1` (params ONLY) | `\result == 0` | 6 | **refused** ✅ |
| k03 twin — the control's true claim | same | `\result == 6` | 6 | **PROVED** ✅ faithful |

**The control is what makes this precise rather than alarming.** An RHS that mentions only
`__init__` parameters is captured and is FAITHFUL in both directions. The defect is exactly the
set of RHSs that reference **anything outside the parameter set** — a builtin (`len`), a module
constant, another `self` field, a helper call. That is the boundary the repair must key on, and
it is the same boundary the existing capture rule already computes, so the fix reads the rule
that is already there rather than inventing one.

## A CORROBORATING SIGNPOST IN A SECOND MODULE

`src/pycsl/module6_whyml/preamble.py` (~4786) carries the matching admission on the checking
side — *"ONLY CHECK A BODY THAT IS THE REAL CONSTRUCTOR … it produces `{ fields = (Array.make 0
0) }`, which is a different program from `self.fields = initial`"* — and reacts with `continue`,
i.e. it **skips checking the constructor contract** while leaving every allocation site on the
wrong literal. So the erasure and the decision not to check it are in different modules, which
is structurally the same "guard and hazard in different modules" fact that #77 recorded.

## THE REPAIR — BLAST RADIUS **MEASURED**, AND IT SETTLES THE DIRECTION

An AST census over `test-suite/corpus/`, `src/self-annotate/`, `src/pycsl/` and
`src/pycsl_lib/`, applying the live capture rule (`names and (names & pset) and names <= pset`)
to every `self.<field> = <rhs>` in every `__init__`:

    __init__ methods scanned       : 293
    self.<field> = ... assignments : 703
    NOT captured (the #79 shape)   : 489      <-- 70%
    by root: corpus 158 · mirror 85 · src/pycsl 122 · src/pycsl_lib 124

**SEVENTY PERCENT OF CONSTRUCTOR FIELD INITIALISERS IN THE REPOSITORY ARE OUTSIDE THE CAPTURE
SHAPE**, including 158 in the verified corpus and 85 in the self-annotation mirror. (This is an
over-approximation of the *exploitable* set — many of those classes are never lowered as records,
and many fields are never read in a clause — but the order of magnitude is not in doubt.)

**THEREFORE A BLANKET REFUSAL IS REFUTED BEFORE IT IS BUILT.** It would be a completeness
regression across the corpus and the mirror at once, and it would almost certainly fail the
byte-inertness and whole-file-proof planes. The measurement pays for itself by killing the
obvious repair cheaply.

**THE REPAIR THAT SURVIVES THE MEASUREMENT** is the one the comment already *claims* is
happening: for an omitted field, emit an **UNCONSTRAINED** value rather than the literal `0`.
That is genuinely "sound, just less precise" — it makes `\result == 0` unprovable (closing the
route) while leaving every program that does not depend on the field's value exactly as it is.
The cost to price next is whether an unconstrained field breaks existing proofs that silently
depend on the `0` (a real risk given 85 mirror sites), which is a whole-file-proof question and
is the next thing to measure.

**A FAIL-CLOSED REFUSAL AT THE CAPTURE SITE WAS THE FIRST REPAIR SCOPED, AND THE CENSUS ABOVE
REFUTED IT** before a line was written. Recording that here rather than deleting it: the obvious
repair for #77 and #78 (refuse the unmodelled shape) does NOT transfer to #79, because #77's and
#78's blast radii were zero and #79's is 70%. **The reflex "refuse what you cannot model" is
correct only when the census says the construct is rare — measure first, every time.**

Re-run the census with `getting-better/route77-80-witnesses/r79-blast-radius-census.py`; it
applies the live capture rule directly, so it stays honest if that rule changes.

## WITNESSES

`scratchpad/w58/c/k02_init_default_fallback.py`, `k02_twin.py`, `k03_init_const_expr.py`
(control), `k03_twin.py`, `k09_init_module_const.py`, `k10_init_self_field.py`.
