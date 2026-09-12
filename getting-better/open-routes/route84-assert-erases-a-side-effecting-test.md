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

## BLAST RADIUS — MEASURED, AND THE CARVE-OUT'S OWN COST FIGURE IS INFLATED ~24x

`desugar.py` justifies the erasure with *"1450 asserts across this tree stay exactly as they
are"*. That number is both **stale** and, far more importantly, **measuring the wrong
population**:

    TOTAL asserts in the four source roots            1212   (not 1450)
      inside `if __name__ == "__main__":`             1162   <- DRIVER HARNESS, never lowered
                                                              as body code
      inside a FUNCTION BODY (actually lowered)         50
        of those, PURE test (no call at all)            29   <- untouched by any repair
        of those, test CONTAINS A CALL                  21   <- THE ENTIRE DECISION SET

**THE WHOLE OF ROUTE #84's COST IS 21 ASSERTS**, every one of them in `test-suite/corpus`
except a single `len(...)` in `src/pycsl/frontend/pure_ast.py`. **ZERO in the self-annotation
mirror and ZERO in `src/pycsl_lib`**, so no whole-file mirror re-proof is at risk.

And of those 21, most tests are transparently PURE — `len(...)`, `hasattr`, `isinstance`,
`callable`, `type(...) is Meta`, `identity(42) == 42`, `f(1, 'x') == 1`, `eval('2 + 3') == 5`.
The genuinely EFFECTFUL ones are a handful: `buf.read() == 'hello'` (0065), `f.read() == 'hello'`
(0191) — a stream read ADVANCES THE POSITION, which is exactly this route's hazard and which my
first mutator-name census MISSED because `read` was not in the name list — plus five
`asyncio.run(...)` tests and two calls on a freshly constructed object (`C()() == 42`,
`C()[5] == 10`).

**THE MEASUREMENT KILLS THE OBVIOUS REPAIR AND RESCUES THE ROUTE.** "Refuse any assert whose
test contains a call" reads as catastrophic against the raw 1108 with-call figure and is merely
a 21-file completeness question once the `__main__` harnesses are excluded — but 21 corpus
regressions is still too many to take blind.

**THE REPAIR DESIGN FORK, TO BE SETTLED BY MEASUREMENT:**

1. **A MUTATOR-NAME BLOCKLIST IS THE WRONG SHAPE AND THIS CAMPAIGN ALREADY KNOWS IT.** My own
   first census used one and scored ZERO hits, because `read` was not on it — while `read` is
   precisely one of the live mutators. Gen #7 banked *"a blocklist keyed on syntax fails OPEN"*
   and #77 confirmed it across a module boundary. Do not build one here.
2. **KEY ON THE EMITTER'S OWN PURITY ANALYSIS, NOT ON NAMES.** Module 5 already computes
   `_detect_purity`, and the campaign already owns mutation machinery
   (`find_iteration_mutations`, `check-dropped-mutation`, the `assigns` frame analysis). An
   assert whose test is PROVABLY PURE by that existing analysis stays exactly as it is; anything
   else is refused. This reuses a certified recognizer instead of inventing one — lesson (p),
   census-first: **the analysis already exists, so scope the repair around it rather than around
   a new construct.**
3. **Lower the test's effects and discard only its boolean value.** The most faithful option and
   the most work; it also reopens the aborting-path question the carve-out was avoiding.

Option 2 is the one to price first. The 21 sites are few enough to inspect INDIVIDUALLY before
and after, which is the honest way to confirm a purity classifier is not failing open.

## THE 21 ROWS, AND WHAT EACH CANDIDATE RULE WOULD REFUSE — PRICED

Every one of the 21 asserts was classified by hand. Three candidate rules, scored against them:

| rule | what it allows | refuses |
|------|----------------|---------|
| A | ONLY whitelisted pure builtins | **12 of 21** |
| B | refuse any method/attribute call, or a call of a call | **8 of 21** |
| C | refuse method calls on a VALUE (`sys`/`ast`/`math` module calls allowed) | 8 of 21 |

**RULE B's EIGHT ARE EXACTLY THE EFFECTFUL ONES**, which is the result that matters:

    buf.read() == 'hello'          (0065)   a stream read ADVANCES THE POSITION
    f.read()   == 'hello'          (0191)   likewise
    C()() == 42                    (0090)   calls __call__ on a fresh instance
    asyncio.run(...)               (0098, 0152, 0207, 0208, 0209)  runs an event loop

**RULE A OVER-REFUSES**: it rejects `eval('2 + 3') == 5`, `identity(42) == 42`, `f(1, 'x') == 1`
and `C()[5] == 10`, which are pure in fact. A whitelist of BUILTIN NAMES is too blunt because
most of these calls are to USER functions.

**BUT RULE B FAILS OPEN, AND THAT IS DISQUALIFYING ON ITS OWN TERMS.** `identity(42)` and
`f(1, 'x')` are plain calls to user functions, and a user function is free to mutate. Rule B
would wave them through on SYNTAX — which is gen #7's "a blocklist keyed on syntax fails OPEN"
for the third time in this route's history (my mutator-name census was the first, Rule B is the
second).

**THEREFORE THE RULE TO BUILD IS THE ONE THAT ASKS THE EXISTING ANALYSIS, NOT THE SYNTAX:**

> An `assert` is lowered to `()` only if EVERY call in its test is either (a) a whitelisted
> PURE BUILTIN, or (b) a user function the IR already marks `pure` — which
> `module5/memoization_rt.py::_detect_purity` computes today as
> `assigns 
othing AND not diverges AND not trusted`. Anything else is REFUSED.

That fails CLOSED on every unknown (method calls, `eval`, constructors, event loops) and it
reuses a purity signal the campaign already certified and already relies on for memoization
soundness — lesson (p), census-first, rather than inventing a classifier.

**REMAINING COST TO CONFIRM BEFORE BUILDING:** how many of the refused files CURRENTLY PASS. Of
the 21, `python-reference/0082` is already in the tolerated 19-failure baseline; the rest pass
today, so the rule above is a **deliberate completeness regression of roughly 9-11 corpus
files**, each of which would move from a silent FALSE PROOF to an explicit refusal. That is the
campaign's thesis working as intended, but it MOVES THE SUITE BASELINE from 19 failures to about
30 and must therefore be stated plainly and justified FILE BY FILE — not absorbed quietly. Read
the exact set off the suite log rather than predicting it.

## WITNESSES

`getting-better/route84-witnesses/a1.py`, `a1twin.py`, `a4req.py`, `a5ctl.py` (**the control —
the same mutation outside an assert is a PIPELINE ERROR**), plus the two recorded non-carriers
`a2.py` and `a3app.py`.
