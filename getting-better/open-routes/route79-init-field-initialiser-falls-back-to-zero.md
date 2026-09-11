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

## THE REPAIR, SCOPED

Fail CLOSED at the capture site: when an `__init__` assigns a field whose RHS is **outside** the
captured shape, raise rather than silently omitting it, so the allocation site can never fall
back to `0` for a field the constructor demonstrably sets. Keep the captured (params-only) shape
exactly as it is — the k03 control proves it is faithful and it carries the corpus.

**BLAST RADIUS IS NOT YET MEASURED AND MUST BE, BEFORE BUILDING.** Unlike #77 and #78 (both
measured at zero), this shape is idiomatic and the corpus is very likely to contain it. The
census to run first is: every `__init__` in `test-suite/corpus/`, `src/self-annotate/`,
`src/pycsl/` and `src/pycsl_lib/` that assigns a field from an RHS naming anything outside the
parameter set. **If that census is large, a blanket refusal is a completeness regression with a
real cost, and the honest alternative is to emit an UNCONSTRAINED value for the omitted field
(genuinely "less precise") rather than a literal 0 — which is what the comment already claims
the code does.** That alternative is likely the better repair and should be priced first.

## WITNESSES

`scratchpad/w58/c/k02_init_default_fallback.py`, `k02_twin.py`, `k03_init_const_expr.py`
(control), `k03_twin.py`, `k09_init_module_const.py`, `k10_init_self_field.py`.
