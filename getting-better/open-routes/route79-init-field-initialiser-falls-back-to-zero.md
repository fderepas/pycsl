# ROUTE #79 — AN `__init__` FIELD INITIALISER OUTSIDE THE CAPTURE SHAPE SILENTLY BECOMES 0

**STATUS: FOUND AND REPRODUCED 2026-09-11 (gen #8). BOTH DIRECTIONS MEASURED. OPEN — repair
scoped below.**

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
