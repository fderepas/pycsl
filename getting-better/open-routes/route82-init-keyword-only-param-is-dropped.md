# ROUTE #82 — AN `__init__` KEYWORD-ONLY (OR POSITIONAL-ONLY) PARAMETER IS DROPPED, AND EVERY FIELD IT INITIALISES BECOMES A LITERAL `0`

**STATUS: FOUND AND REPRODUCED 2026-09-12 (gen #9). BOTH DIRECTIONS MEASURED ON FOUR
CARRIERS, WITH AN EXACT CONTROL. OPEN.**

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
| **kw3 — THE CONTROL** | ORDINARY POSITIONAL `v` | `\result == 0` | 7 | **refused** |
| kw3 twin — the control's true claim | ORDINARY POSITIONAL `v` | `\result == 7` | 7 | **PROVED** — faithful |

**THE CONTROL IS AS TIGHT AS A CONTROL GETS.** It is the SAME class, the SAME field, the SAME
constructor argument value and the SAME clause. Only the parameter's *kind* changes. Positional
is faithful in BOTH directions; keyword-only and positional-only are wrong in BOTH directions.
So this is a route, not a gap, and its boundary is not a matter of judgement.

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

## REPAIR — SCOPED, NOT YET BUILT

Read all three parameter lists, in Python's own binding order:

```python
init_params = [a.arg for a in
               (child.args.posonlyargs + child.args.args + child.args.kwonlyargs)
               if a.arg != 'self']
```

with the caveat that `init_params` is ALSO consumed as a **positional** binding list by
`_call_record_constructor` (the positional-prefix rule binds `args[i]` to `init_params[i]`).
Appending the keyword-only names to that same list would make them bind POSITIONALLY, which is
a *different* wrong model — Python never binds a keyword-only parameter from a positional
argument. **So the repair must keep the positional-bindable prefix (`posonlyargs + args`)
SEPARATE from the keyword-only names**, letting WL-07's `kwargs_map` bind the latter by name
only. Getting this wrong trades one wrong model for another, exactly as the one-token
alternative did in #77 — so it must be measured, not reasoned about.

**Blast radius: NOT YET MEASURED.** Census `__init__` methods with non-empty `posonlyargs` or
`kwonlyargs` across `test-suite/corpus/`, `src/self-annotate/`, `src/pycsl/` and
`src/pycsl_lib/` before building. `src/self-annotate/src/errors.py::PyCSLError` is a known
instance **in the mirror**, so this interacts with the whole-file mirror proofs.

## RELATION TO #79

Same erasure site (`_field_default`'s literal `0`), different upstream cause: #79 is an RHS the
rule declines to capture, #82 is a PARAMETER the rule cannot see. **A repair for #79 (emit an
unconstrained value for an omitted field) would also close #82's false proofs**, since #82's
fields are omitted for the same reason. But #82 additionally has a *correct* answer available —
the parameter is right there — so it deserves a faithful capture rather than an unconstrained
value. Fixing #82 first also SHRINKS #79: every field #82 recovers leaves the omitted set.

## WITNESSES

`getting-better/route82-witnesses/kw1.py`, `kw1twin.py`, `kw2.py`, `kw2twin.py`,
`kw3ctl.py` (the control), `kw3ctltwin.py`, `kw4pos.py`, `kw5req.py`.
