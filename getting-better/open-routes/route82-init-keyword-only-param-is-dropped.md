# ROUTE #82 — AN `__init__` KEYWORD-ONLY (OR POSITIONAL-ONLY) PARAMETER IS DROPPED, AND EVERY FIELD IT INITIALISES BECOMES A LITERAL `0`

**STATUS: FOUND, REPAIRED AND FULLY GATED 2026-09-12 (gen #9). CLOSED — AND CLOSED FAITHFULLY,
not by refusal, so it is a COMPLETENESS GAIN as well as a soundness fix.**

**CLASS: the #69 class, the serious one** — a FALSE POSTCONDITION about ordinary, TOTAL
Python. No `no_exception`, no opt-in, no unusual construct.

**THIS IS THE WIDEST ROUTE IN THE #79 FAMILY, AND IT IS WIDER THAN #79 ITSELF.** #79 needs an
RHS outside the capture shape (`self.n = len(items)`). #82 needs **nothing but `self.v = v`** —
the single most ordinary line a constructor can contain. All it takes is for `v` to be declared
after a `*` or before a `/`.

## THE EXPLOIT

```python
class P:
    v: int
    def __init__(self, *, v: int = 0) -> None:
        self.v = v

#@ ensures \result == 0
def f() -> int:
    p = P(v=7)
    return p.v
```

    CPython:  7
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

## BOTH DIRECTIONS, FOUR CARRIERS, AND A CONTROL THAT PINS THE BOUNDARY EXACTLY

| driver | `__init__` parameter kind | claim | CPython | PyCSL |
|--------|---------------------------|-------|---------|-------|
| kw1 | KEYWORD-ONLY `*, v` | `\result == 0` | **7** | **PROVED** |
| kw1 twin | same | `\result == 7` | 7 | refused |
| kw2 | KEYWORD-ONLY `b`, RHS `b + 1` | `\result == 0` | **6** | **PROVED** |
| kw2 twin | same | `\result == 6` | 6 | refused |
| kw4 | POSITIONAL-ONLY `v, /` | `\result == 0` | **7** | **PROVED** |
| kw5 | KEYWORD-ONLY, `requires` discharge | `requires n == 0`, runtime n is **7** | — | **PROVED** |
| kw6 | KEYWORD-ONLY `v: int = 5`, OMITTED at the call | `\result == 0` | **5** | **PROVED** |
| **kw3 — THE CONTROL** | ORDINARY POSITIONAL `v` | `\result == 0` | 7 | **refused** |
| kw3 twin — the control's true claim | ORDINARY POSITIONAL `v` | `\result == 7` | 7 | **PROVED** — faithful |

**THE CONTROL IS AS TIGHT AS A CONTROL GETS.** It is the SAME class, the SAME field, the SAME
constructor argument value and the SAME clause. Only the parameter's *kind* changes. Positional
is faithful in BOTH directions; keyword-only and positional-only are wrong in BOTH directions.
So this is a route, not a gap, and its boundary is not a matter of judgement.

**A FIFTH CARRIER, AND IT CONSTRAINS THE REPAIR (kw6).** A keyword-only parameter with a
NONZERO DEFAULT that is OMITTED at the call site is wrong too:

```python
def __init__(self, *, v: int = 5) -> None: self.v = v
...  p = P(); return p.v        #@ ensures \result == 0   <-- PROVED; CPython returns 5
```

So it is not enough to bind the keyword arguments that are SUPPLIED. The repair must also
capture each keyword-only parameter's CONSTANT DEFAULT, because an omitted keyword-only
parameter is exactly the case where the current literal `0` is most likely to be read as
"the default" — and it is only right when that default happens to be `0`.

**kw5 IS THE ESCALATION.** The stale `0` DISCHARGES A CALLEE'S `requires n == 0` at a call site
where the runtime value is `7`. The callee's own proof is then sound relative to a precondition
the caller never establishes, so the unsoundness is laundered through a correct proof and
propagates across the call graph.

## THE MECHANISM — ONE ATTRIBUTE ACCESS

`src/pycsl/frontend/module5/construction_synth.py::_collect_init_construction` computes the
constructor's formal-parameter set as

```python
init_params = [a.arg for a in child.args.args if a.arg != 'self']
```

`ast.arguments.args` holds **only** the plain positional-or-keyword parameters. Python's AST
keeps the other two kinds in **sibling** fields — `child.args.posonlyargs` and
`child.args.kwonlyargs` — and both are simply not read. So for a keyword-only constructor:

* `pset` is EMPTY, the rule `if not pset: break` fires, and `init_params`/`init_body` come back
  empty;
* every field therefore falls through to `_field_default` in
  `module6_whyml/expressions.py`, which returns `rec_info['defaults'].get(fn, 0)` — **a literal
  `0`**;
* and `_call_record_constructor`'s WL-07 keyword binding cannot save it, because that path binds
  keyword arguments **by name onto `init_params`**, which is the very list that came back empty.

**THE `*` IS NOT PARSED AWAY OR REJECTED — IT IS SILENTLY READ AS "THIS CONSTRUCTOR HAS NO
PARAMETERS".** That is why the failure is quiet.

## HOW IT WAS FOUND — AND THE GENERATOR IS WORTH MORE THAN THE ROUTE

It was NOT found by probing `__init__`. It was found by **obeying rule (o) and re-verifying an
inherited census instead of building on it.** Gen #8 priced #79's repair off "489 of 703 (70%)
constructor field initialisers are outside the capture shape". Re-running that census at HEAD
and splitting the complement by *why* each member fell out gave 376 / 192 / **133** — the first
class being literal RHSs that `field_defaults` captures perfectly well. While reading the 133
survivors one by one, four of them were `PyCSLError.__init__`'s `self.filename = filename`,
`self.line = line`, `self.stage = stage`, `self.code = code` — assignments that are *obviously*
params-only and had no business being in the list. **The census was not wrong; the capture rule
was.** Chasing why those four appeared produced #82.

**THE GENERATOR: WHEN A CENSUS RETURNS A MEMBER THAT OBVIOUSLY SHOULD NOT BE THERE, THE BUG IS
AS LIKELY TO BE IN THE RULE THE CENSUS APPLIES AS IN THE CENSUS.** An "impossible" row in a
measurement is a free probe into the rule that produced it — read the outliers, never just the
totals. This is the counterpart to gen #8's "a comment asserting an erasure is sound is an
unproven lemma": here, *an inherited number is an unproven lemma too*, and the cheapest way to
test it is to look at the rows it is made of.

## CLOSED — THE REPAIR AS BUILT

Read all three parameter lists, in Python's own binding order:

```python
init_params = [a.arg for a in
               (child.args.posonlyargs + child.args.args + child.args.kwonlyargs)
               if a.arg != 'self']
```

**AND THE TRAP WAS REAL, SO THE TWO LISTS ARE KEPT SEPARATE.** `init_params` is ALSO consumed
as the **positional** binding list by `_call_record_constructor` (`args[i]` binds
`init_params[i]`). Appending the keyword-only names to it would bind them FROM POSITIONAL
ARGUMENTS, which Python never does — a DIFFERENT wrong model in place of the old one, exactly
as #77's one-token alternative would have been. So:

* `init_params` = `posonlyargs + args` — the positional-bindable prefix, in Python's own order.
  (Positional-only parameters DO bind positionally and belong here; they were missing before.)
* `init_kwonly_params` / `init_kwonly_defaults` — NEW additive IR keys, emitted only when the
  constructor has keyword-only parameters, so absent for the other 288 of 296 constructors and
  byte-identical there.
* `pset` — which only decides whether an RHS is EXPRESSIBLE from the parameters — sees all three
  kinds.

Module 6 binds the keyword-only names **BY NAME ONLY**, and seeds each omitted one from its
captured CONSTANT default (the kw6 carrier).

### THE BUG IN THE FIRST BUILD, AND THE LESSON THAT COST

The first build fixed the POSITIONAL-ONLY carrier and left every KEYWORD-ONLY one still proving
the false `0`. **Module 6 does not read the IR `type_decl`.** `preamble.py` builds
`_record_types` by copying a **SELECTED LIST OF KEYS**, so a new IR key is silently dropped on
the floor unless it is added there too.

**LESSON: WHEN THREADING A NEW IR KEY FROM MODULE 5 TO MODULE 6, THE `type_decl` IS NOT THE
INTERFACE — THE HAND-WRITTEN `rec_info` COPY IN `preamble.py` IS.** A key absent from that copy
reads back as its default, and the repair is a silent no-op that passes every gate.

**A SECOND LESSON, ABOUT DEBUGGING RATHER THAN ABOUT PYCSL.** An isolated harness that does
`sys.path.insert(0, 'src/pycsl')` and calls the emitter method directly gets a **DIFFERENT `ast`
module** than the emitter's own, so `isinstance(child, ast.FunctionDef)` is FALSE and the method
silently returns empty. The harness said the Module-5 code never ran; the real pipeline said it
did. **THE REAL PIPELINE WAS RIGHT, and the tell was already on the table** — the
positional-only carrier HAD changed behaviour, which is impossible if that code never executed.
Debug through the real pipeline, not a hand-built harness.

### GATES, ALL GREEN

* **byte-inert over BOTH corpora** against a pre-repair worktree baseline at `d5ab8bbd`:
  pycsl-ref **971/971**, python-ref **2204/2204**, **0 MOVED / 0 GONE / 0 APPEARED** — exactly
  as the blast-radius census predicted (zero corpus sites).
* **IR conformance 38/38 core + 38/38 front-end, 0 MISMATCH**, determinism 10/10 — the
  rule-(k) risk, since this route ADDS IR KEYS. The additive-when-empty design held: no golden
  has a keyword-only constructor, so no frozen golden moved and **no re-baselining was needed or
  considered.**
* fidelity rc=0 (887 un-trusted mirror functions verbatim) — **all four edited regions are
  OUTSIDE the mirror's un-trusted surface** (`construction_synth.py` is not mirrored at all, and
  `_call_record_constructor` is a `#@ \trusted` bodyless stub), so **NO mirror sync and NO
  whole-file re-proof were owed.** The #78 shape, as predicted before building.
* mirror **type-only 53/53, 0 ILL-TYPED** (rule (j) — `preamble.py` was edited).
* **34/34 planes, all green** — including `check-bespoke-model-drift`, which stayed green
  because no bespoke model moved.
* **reference suite 3333/3352, ZERO XPASS**, rc=1 (the baseline condition), with the 19-failure
  set **byte-identical** to the route-#80 run and the comparison **verified non-vacuous** (19
  lines on each side).

### WITNESSES IN THE CORPUS

`1204` keyword-only bound (true claim PROVES) · `1205` keyword-only NONZERO default omitted ·
`1206` positional-only bound · `1207` **the negative witness** (the false claim must NOT prove) ·
`1208` **the positional CONTROL locked**, so a future change cannot quietly alter the one shape
that was never broken. Both directions are pinned: 1204 makes the true claim provable and 1207
makes the false one unprovable. Either alone would also pass for a repair that merely REFUSED
the construct, which would have been a completeness regression on 8 constructors — including
`PyCSLError` in the self-annotation mirror.

**BLAST RADIUS: MEASURED, AND IT IS TINY.** Of 296 `__init__` methods across
`test-suite/corpus/`, `src/self-annotate/`, `src/pycsl/` and `src/pycsl_lib/`:

    with KEYWORD-ONLY params      8      corpus 0 · mirror 2 · src/pycsl 3 · src/pycsl_lib 2
    with POSITIONAL-ONLY params   0      (none anywhere in the repository)
    of those, initialising a field from a dropped parameter   7

**ZERO in the verified corpus**, so the repair is predicted byte-inert over both corpora and
over all 38 IR-conformance goldens. The real cost is the TWO mirror classes
(`src/self-annotate/src/errors.py::PyCSLError` — whose `filename`/`line`/`stage`/`code` are
ALL dropped — and `ConcurrencyChecker`), which makes this a whole-file-mirror-proof question,
not a completeness-regression one. The positional-only carrier (kw4) is real but has no site
in the repository, so covering it costs nothing and is worth doing for the same reason #77's
dynamic-bound case was.

## RELATION TO #79

Same erasure site (`_field_default`'s literal `0`), different upstream cause: #79 is an RHS the
rule declines to capture, #82 is a PARAMETER the rule cannot see. **A repair for #79 (emit an
unconstrained value for an omitted field) would also close #82's false proofs**, since #82's
fields are omitted for the same reason. But #82 additionally has a *correct* answer available —
the parameter is right there — so it deserves a faithful capture rather than an unconstrained
value. Fixing #82 first also SHRINKS #79: every field #82 recovers leaves the omitted set.

## WITNESSES

`getting-better/route82-witnesses/kw1.py`, `kw1twin.py`, `kw2.py`, `kw2twin.py`,
`kw3ctl.py` (the control), `kw3ctltwin.py`, `kw4pos.py`, `kw5req.py`, `kw6def.py`.
