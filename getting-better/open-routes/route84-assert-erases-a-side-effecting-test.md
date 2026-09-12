# ROUTE #84 — AN `assert` ERASES ITS TEST WHOLESALE, SIDE EFFECTS INCLUDED — AND IT LAUNDERS A CONSTRUCT THE EMITTER OTHERWISE REFUSES

**STATUS: FOUND AND REPRODUCED 2026-09-12 (gen #9). BOTH DIRECTIONS MEASURED, WITH AN EXACT
CONTROL. OPEN.**

**CLASS: the #69 class** — a FALSE POSTCONDITION about ordinary, TOTAL Python. No
`no_exception`, no opt-in. **The assertion HOLDS**, so CPython does not abort: the program runs
to completion and returns a different value.

## THE EXPLOIT

```python
from typing import List

#@ ensures \result == 3
def f() -> int:
    xs: List[int] = [1, 2, 3]
    assert xs.pop() == 3        # the assertion is TRUE — Python never aborts — but xs SHRINKS
    return len(xs)
```

    CPython:  2
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

## BOTH DIRECTIONS, AND THE CONTROL IS THE BEST PART

| driver | shape | claim | CPython | PyCSL |
|--------|-------|-------|---------|-------|
| a1 | `assert xs.pop() == 3` then `len(xs)` | `\result == 3` | **2** | **PROVED** |
| a1 twin | same | `\result == 2` | 2 | refused |
| a4req | the stale length DISCHARGES `requires n == 3` | — | runtime n is **2** | **PROVED** |
| **a5ctl — THE CONTROL** | the SAME `xs.pop()`, OUTSIDE any assert | `\result == 2` | 2 | **PIPELINE ERROR** |

**THE CONTROL IS WHAT MAKES THIS SERIOUS.** `xs.pop()` on its own is a construct this build
REFUSES outright — a pipeline error. Wrapped in an `assert` whose test is true, the very same
mutation is SILENTLY DROPPED and a false postcondition becomes provable. **The `assert` is not
merely lossy; it LAUNDERS a refused construct past its own guard.** That is a strictly worse
failure mode than an unmodelled operation, because the refusal that exists for this exact
mutation never fires.

a4req is the ESCALATION: the stale length discharges a callee's `requires n == 3` at a call site
where the runtime value is 2, so the defect crosses the call graph.

## THE MECHANISM, AND THE CARVE-OUT THAT GUARDS IT

`module6_whyml/statements.py` lowers an assert to nothing at all:

```python
        elif isinstance(stmt, AssertStmt):
            code = f'{indent}()'
```

Module 5 **does** keep the test in the IR (`_py_stmt_assert`), so the information is present and
is discarded one stage later. Two comments justify it:

* `module6_whyml/functions.py`: *"A Python `assert` is DROPPED by Module 6 (it lowers to `()`,
  measured on `python-reference/0177`), so a read inside one is not a leak."*
* `frontend/desugar.py`: *"OUTSIDE a handler that is CONSERVATIVE and sound: the model must
  discharge the postcondition on the path Python aborts, which is strictly harder, so 1450
  asserts across this tree stay exactly as they are."*

**BOTH ARGUMENTS ARE ABOUT A FAILING ASSERT, AND BOTH ARE CORRECT ABOUT IT.** Neither says
anything about the case measured here: an assert whose test **succeeds** and whose test
**mutates**. "Conservative" is a claim about the control-flow consequence; it is not a licence to
discard the evaluation. And note the shape of the second justification — *"1450 asserts across
this tree stay exactly as they are"* — which is a census of PyCSL's own sources, not a property
of the lowering. That is the same species of signpost as #78's "a sound under-approximation".

Route #16's existing refusal covers only an `assert` inside a CATCHING `try`
(`desugar.py:338`), which is the control-flow hazard, not this one.

## WHAT DOES **NOT** REPRODUCE — RECORDED SO IT IS NOT RE-PROBED

* **`assert xs.pop() == 3` then `xs[0]` is NOT a carrier** (a2). CPython and PyCSL both answer
  1, because popping the LAST element does not move index 0. The erasure is real but this
  carrier cannot see it. **A carrier has to be chosen so the dropped effect is OBSERVABLE at the
  read** — a length read, or an element at an index the mutation moves.
* **`xs.append(9)` between two asserts is REFUSED** (a3app) — fail-closed, so the append path is
  not a second carrier in this spelling.

## REPAIR — SCOPED, NOT BUILT

The information is in the IR, so the honest options are:

1. **Refuse an `assert` whose test is not provably pure** — i.e. whose test contains a call, a
   method call, or any mutating operation. This is the fail-closed option and it matches how the
   emitter already treats the same mutation outside an assert (the a5ctl control is a pipeline
   error, so refusing is CONSISTENT with the surrounding design rather than new behaviour).
2. **Lower the test's side effects and then discard only its boolean value.** More faithful and
   strictly more work; it also re-opens the question the carve-out was avoiding, namely what the
   model should do on the aborting path.

Option 1 is the shape #77/#78/#80 used and it is almost certainly right here, because the
construct is ALREADY refused one token away.

**BLAST RADIUS: NOT YET MEASURED, AND IT IS THE DECIDING NUMBER.** `desugar.py` cites **1450
asserts across this tree**, so unlike #80 (radius zero) and #82 (radius 8) this one could be
expensive. **Census asserts whose TEST CONTAINS A CALL** — not all asserts — across
`test-suite/corpus/`, `src/self-annotate/`, `src/pycsl/` and `src/pycsl_lib/` before writing a
line. A pure-test assert (`assert n > 0`) must stay exactly as it is; the whole question is how
many tests call something, and of those how many call something that mutates.

## WITNESSES

`getting-better/route84-witnesses/a1.py`, `a1twin.py`, `a4req.py`, `a5ctl.py` (**the control —
the same mutation outside an assert is a PIPELINE ERROR**), plus the two recorded non-carriers
`a2.py` and `a3app.py`.
