# ROUTE #84 — AN `assert` ERASES ITS TEST WHOLESALE, SIDE EFFECTS INCLUDED — AND IT LAUNDERS A CONSTRUCT THE EMITTER OTHERWISE REFUSES

**STATUS: FOUND, REPAIRED AND FULLY GATED 2026-09-12 (gen #9). CLOSED.** SIX CARRIERS, BOTH
DIRECTIONS, WITH AN EXACT CONTROL.

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


## THE REPAIR AS BUILT — AND IT WAS NARROWED 9x BY REFUTING MY OWN FIRST DESIGN

The guard lives inline in the `AssertStmt` arm of `module6_whyml/statements.py`, diagnostic code
`PYCSL-M6-ASSERT-EFFECTFUL-TEST`. It refuses in exactly two cases:

* **(a) a DOTTED callee whose receiver prefix is a TRACKED LOCAL** — `xs.pop()` on a list local,
  `buf.read()` on a StringIO local. That is the measured hazard.
* **(b) a call to a user function whose effects are not KNOWN to be none** — known either because
  the IR marks it `pure` (`_detect_purity`: `assigns \nothing`, not `\diverges`, not
  `\trusted`) or because its body is exactly `return <expr>` with no call and no store anywhere
  inside it.

### THE FIRST DESIGN COST NINE CORPUS FILES AND THE MEASUREMENT KILLED IT

The first build refused any call the purity oracle could not clear. The byte-diff priced that at
**NINE newly-refused `python-reference` files** (0065, 0098, 0109, 0148, 0152, 0207, 0208, 0210,
0213). I then tested whether those passes were **HOLLOW** — whether the files passed only because
the construct was erased, in which case refusing them would cost nothing real. **THEY WERE NOT.**
Hoisting `asyncio.run(outer())` out of the assert into a plain assignment **still proves**: the
emitter already lowers it as an opaque value, so refusing it is a pure completeness regression on
a program this build handles correctly.

**That is #79's lesson recurring on my own work: the obvious repair was refuted by its blast
radius before it landed.** Narrowing to the two arms above cut the cost from **nine files to
one** — `python-reference/0065` (`buf.read()`), which is the genuine hazard.

### ARM (b) WAS TESTED FOR ITS KEEP, NOT ASSUMED — AND IT FOUND A SIXTH CARRIER

Arm (b) is the expensive half, so I disabled it and re-measured. With it off,

```python
#@ assigns c.v
def bump(c: C) -> int:
    c.v = 7
    return 0
...
assert bump(c) == 0
return c.v        #@ ensures \result == 1    <-- PROVED; CPython returns 7
```

**proves a false claim.** So arm (b) stays, and this record-field mutation is a sixth carrier.
Note that my FIRST attempt at justifying arm (b) used a LIST-parameter mutation, which turned out
to be **already refused pre-repair** for an unrelated WL-05 reason — it was not evidence, and I
withdrew it. The record-field version is.

### THE `_detect_purity` ORACLE IS WEAK ON UNANNOTATED CODE, AND THAT COST TWO FILES

`_detect_purity` keys on the **CONTRACT**. In unannotated code — all of
`test-suite/corpus/python-reference/` — nothing is ever marked pure, so arm (b) refused even
`def identity(x): return x`. That is a completeness loss with no soundness gain, measured at two
files (0210, 0213). The rescue is the narrowest one that works and it inspects the **BODY**, not
a name: a single `return <expr>` containing no call and no store cannot mutate anything. It
correctly rejects both `bump` and `sneak`.

### A RATCHET CAUGHT IT, AND THE RATCHET WAS KEPT

`check-mirror-coverage` went **RATCHET BROKEN 552 > 549**: it counts every `ast.FunctionDef` in
the live tree, **nested ones included**, so two helper methods plus their inner walkers added
three unmirrored names. Rule (k) forbids re-baselining a ratchet to make a gate green, and adding
`\trusted` mirror stubs would have **RAISED the trust-surface metric for what is a pure
refusal**. The guard was therefore rewritten **inline with explicit worklists and zero new
defs** — ratchet back to 549, metric untouched at 459, no mirror sync and no whole-file re-proof
owed (fidelity rc=0, 887 verbatim).

## RESIDUES AND REOPENING CONDITIONS

* **A CALL OF A CALL IS NOT COVERED.** `python-reference/0090`'s `assert C()() == 42` still
  proves: the outer call is neither dotted nor a registry name, so neither arm fires.
  **REOPENING: a `__call__` that mutates.** Not chased because the `__call__` protocol is not
  otherwise modelled, but it is a real hole in this guard and it is written down rather than
  implied.
* **A NESTED function that mutates is not caught by arm (b)'s registry lookup** if Module 5 does
  not hoist it into `ir["functions"]`. The trivially-pure body check does not help here — it only
  ever ADMITS. **REOPENING: a nested `def` with a store, called from an assert test.**
* **`python-reference/0065` is now REFUSED and that is the intended verdict** — `buf.read()`
  advances the stream position, which is precisely this route's hazard. It moves from a silent
  false-proof-enabler to an explicit refusal.


## GATES — ALL GREEN, AND THE COST IS ONE FILE

* **byte-inert** vs a pre-repair worktree baseline at `08ea403f`: pycsl-ref **976/976, 0 MOVED /
  0 GONE / 0 APPEARED**; python-ref **2204 -> 2203, 1 GONE / 0 UNEXPECTED**, declared
  `--expect-gone pyref__0065`. Zero-byte files checked on BOTH sides (see the hazard below).
* **IR conformance 38/38 core + 38/38 front-end, 0 MISMATCH**, determinism 10/10.
* **fidelity rc=0** (887 un-trusted mirror functions verbatim) — **no mirror sync and no
  whole-file re-proof owed**.
* **`check-mirror-coverage` ratchet 549 KEPT, NOT RE-BASELINED** — the guard was rewritten inline
  with zero new defs instead.
* **34/34 planes green.**
* **reference suite 3333/3352, ZERO XPASS**, rc=1 (the baseline condition), with the 19-failure
  set **byte-identical** to the route-#82 close and the comparison verified NON-VACUOUS (19 lines
  on each side).

The intermediate run — before `0065` was marked — was **3332/3352 with exactly 20 failures**, the
set being the 19 baseline PLUS `0065` and nothing else. That number is recorded because it is the
honest, unabsorbed cost of the repair.

**`python-reference/0065` IS NOW A NEGATIVE WITNESS, NOT AN UNTRACKED FAILURE.** It is marked
`# pycsl-expected: FAIL` with the mechanism in its docstring, so the **XPASS rule guards it**: if
it ever starts proving again, route #84 has reopened and the suite says so. Leaving it as a bare
failure would have moved the tolerated baseline 19 -> 20 and put it beyond every ratchet — the
#44 lesson ("a negative witness that cannot fail is not a test") applied in the other direction.

## A MEASUREMENT HAZARD THIS ROUTE UNCOVERED — READ BEFORE TRUSTING ANY BYTE-DIFF

The first #84 sweep reported **15 MOVED in pycsl-ref**, which is impossible for a guard that only
RAISES or FALLS THROUGH. Those 15 candidate files were **ZERO BYTES**, in a contiguous block
(0557-0572), with none on the baseline side: one parallel worker's batch failed to write with
`/tmp` at 77% from accumulated worktrees and sweep dirs.

**THE FAILURE IS SILENT AND BIDIRECTIONAL. Had the empty file landed on the BASELINE side, the
diff would have reported a FALSE GREEN** and a real emission change would have passed unnoticed.
Always run `find <sweepdir> -name '*.mlw' -size 0 | wc -l` on BOTH sides before believing a
byte-diff verdict, and watch `df`. (`git worktree add` also fails with an opaque "could not reset
index file to revision 'HEAD'" when `/tmp` is full.)
