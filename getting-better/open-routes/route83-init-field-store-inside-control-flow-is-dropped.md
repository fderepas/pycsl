# ROUTE #83 — A FIELD STORE INSIDE CONTROL FLOW IN `__init__` IS DROPPED, AND THE FIELD BECOMES A LITERAL `0`

**STATUS: FOUND AND REPRODUCED 2026-09-12 (gen #9). BOTH DIRECTIONS MEASURED ON FOUR CARRIERS,
WITH A CONTROL THAT REFUTED THE MECHANISM IT WAS PREDICTED TO HAVE. OPEN.**

**CLASS: the #69 class** — a FALSE POSTCONDITION about ordinary, TOTAL Python. No
`no_exception`, no opt-in.

## THE EXPLOIT

```python
class C:
    v: int
    def __init__(self, n: int) -> None:
        self.v: int = 0
        if n > 0:
            self.v = n          # a CONDITIONAL field store — never captured

#@ ensures \result == 0
def f() -> int:
    c = C(7)
    return c.v
```

    CPython:  7
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

## BOTH DIRECTIONS, FOUR CARRIERS

| driver | shape | claim | CPython | PyCSL |
|--------|-------|-------|---------|-------|
| c1 | ANNOTATED store inside `if` | `\result == 0` | **7** | **PROVED** |
| c1 twin | same | `\result == 7` | 7 | refused |
| c1ctl | **UN-ANNOTATED** store inside `if` | `\result == 0` | **7** | **PROVED** |
| c1ctl twin | same | `\result == 7` | 7 | refused |
| c3loop | store inside a `while` | `\result == 0` | **7** | **PROVED** |
| c2req | the stale `0` DISCHARGES `requires m == 0` | — | runtime m is **7** | **PROVED** |

c2req is the ESCALATION: a callee's precondition is discharged from a value the caller never
establishes, so the defect crosses the call graph.

## THE CONTROL REFUTED THE PREDICTED MECHANISM, AND THAT IS THE MOST USEFUL THING HERE

This route was reached from the gen-#9 carve-out census, whose top-ranked candidate predicted a
specific mechanism: `desugar.py` protects every `AnnAssign` inside `__init__` from the
annotated-store normalizer, and `Module5_IREmitter._py_stmt_annassign` has **no `else`** for an
Attribute target, so an ANNOTATED `self.v: int = n` emits no IR at all. Both halves of that are
TRUE — I verified them in the source by hand.

**But the control shows the annotation is IRRELEVANT.** `c1ctl`, which drops the annotation and
writes a plain `self.v = n` inside the same `if`, proves the same false claim and refuses the
same true twin. So the `AnnAssign` hole is real but it is **not what makes this exploitable**.

The actual cause is one line up, in
`frontend/module5/construction_synth.py::_collect_init_construction`:

```python
            for stmt in child.body:  # top-level only — no ast.walk
```

**Only TOP-LEVEL statements of `__init__` are considered at all.** A store nested in any `if`,
`for`, `while` or `with` is invisible to the capture rule regardless of its RHS or its
annotation, so the field falls to `_field_default`'s literal `0` in
`module6_whyml/expressions.py`. The carve-out is stated in the docstring immediately above:

> *"Soundness: only flat top-level assignments are captured (no control flow — a
> conditional/looping init can't be reduced to a single record literal)"*

which is the #78/#79 sentence again: **an erasure justified by calling it sound, where the
emitted value is a DEFINITE literal rather than an unconstrained one.** "Cannot be reduced to a
single record literal" is a correct statement about the *representation*; supplying `0` is not
the sound consequence of it.

**LESSON: A CENSUS CANDIDATE'S MECHANISM STORY IS A HYPOTHESIS, NOT A FINDING — AND THE CONTROL
IS WHAT SEPARATES THEM.** Had I built the repair the candidate described (handle the Attribute
target in `_py_stmt_annassign`), it would have fixed the annotated spelling and left the
un-annotated one — the *more common* one — wide open, while every gate went green. One control
driver, costing two minutes, was the difference.

## RELATION TO #79 AND #82

All three are the same erasure site (`_field_default`'s literal `0`) reached by three different
upstream causes:

| route | cause | needs |
|-------|-------|-------|
| #79 | the RHS names something outside the parameter set | `self.n = len(items)` |
| #82 | the PARAMETER is keyword-only or positional-only, so the rule cannot see it | `self.v = v` |
| #83 | the STATEMENT is not at the top level of `__init__` | `if c: self.v = n` |

**#79's unconstrained-value repair would close all three**, which is an argument for doing it —
but #82 was closed FAITHFULLY instead (the parameter was right there), and #83 may admit the
same treatment, since the capture rule could walk into straight-line-dominated branches. Prefer
a faithful capture where the information exists; fall back to unconstrained only where it does
not.

## BLAST RADIUS — MEASURED

`self.<field> = ...` nested inside control flow in an `__init__`, across `test-suite/corpus/`,
`src/self-annotate/`, `src/pycsl/` and `src/pycsl_lib/` (296 `__init__` methods):

    total                5
    test-suite/corpus    0
    src/self-annotate    0
    src/pycsl            0
    src/pycsl_lib        5      (StringIO._size, JSONEncoder.default/item_separator,
                                 Popen._pid, Sha256._input)

**ZERO in the verified corpus, the mirror and the compiler itself**, so a repair is predicted
byte-inert over both corpora and over the 38 IR-conformance goldens, and owes no mirror
re-proof. The five library sites are the only thing to price.

## REPAIR — NOT YET BUILT

Two options, to be decided by measurement:
1. **Faithful capture of the unconditional case.** A store that DOMINATES the end of `__init__`
   (e.g. the last statement of both arms of an `if`/`else`) has a determinate value and could be
   captured. Narrow, and it does not cover `c1`, where the store is conditional in the real
   sense.
2. **Unconstrained value for a field written anywhere in `__init__` but not captured.** This is
   #79's repair and it covers all of #79/#82/#83. It makes `\result == 0` unprovable without
   claiming anything false.

**THE TRAP TO AVOID (recorded so it is not rediscovered):** do NOT repair
`_py_stmt_annassign`'s missing Attribute arm and call this closed. That fixes only the annotated
spelling, and `c1ctl` proves the un-annotated one is equally live.

## WITNESSES

`getting-better/route83-witnesses/c1.py`, `c1twin.py`, `c1ctl.py` (**the control that refuted
the predicted mechanism**), `c1ctltwin.py`, `c2req.py`, `c3loop.py`.
