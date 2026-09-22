# Routes #210 and #211 — a `#@ check` stamped into a body that is never lowered

**Status:** BOTH CLOSED (gen #30). SEV-1. The same defect in two of the `happy` forms, and
the twin for #211 is ONE ANNOTATION LINE.

## The shape

A `happy` policy enforces itself by INJECTING something into a body:

* `protects <path> except <fn>` stamps `#@ check False` on every non-exempt write site —
  that is how corpus **0612** fails.
* `<name>(n): protects p[a:b]` (the parametric form) stamps `#@ check False` on every
  non-exempt write with no `#@ footprint` — that is how corpus **0615** fails.

A `\trusted` / `\abstract` body **is never lowered**, so its stamped sites evaporate. The
policy is then enforced by nothing at all, and the run says "All contracts formally proven".

## The witnesses

`1718` (route #210) — `protects g.v except setter`, and:

```python
#@ requires n >= 0
#@ assigns \nothing        # the frame LIES; route #209's boundary reads this line
#@ \trusted
def liar(n: int) -> None:
    g.v = n                # the body writes the protected path
```

`1719` (route #211) — 0614's own parametric shape, and:

```python
#@ requires v >= 0
#@ assigns d.disk
#@ \trusted                # remove this ONE LINE and the file FAILS
def rogue(v: int) -> None:
    d.disk[900] = v        # inside object 6's region, no footprint, not exempt
```

Both printed **"Verification SUCCESS! All contracts formally proven"**. CPython agrees with
both violations.

## Why #209's repair did not cover them

Route #209 gave the `protects` form a trust boundary keyed on the stub's DECLARED
`#@ assigns`. That is exactly the line a liar controls. The repair for #210/#211 keys on
the WRITE SITES THE POLICY ALREADY COLLECTS (`_collect_protect_sites`,
`_collect_protect_index_sites`) — the body is right there in the AST, because **`\trusted`
means "not lowered", not "not readable"**, which is the same observation
`bin/check-trusted-frame-honesty.py` was built on.

## The repair

A site whose enclosing function is `\trusted`/`\abstract`, not exempt and not `\preserves`
now RAISES instead of receiving an inert stamp — in `Module3_Weaver`, whose mirror twin is
`\trusted reviewer: pycsl-self-annotate`, so no marker, no mirror edit, no re-proof.

## What generalised out of them

`bin/check-happy-trust-boundaries.py` — an EXECUTABLE gate that runs a carrier and a
control for each boundary through the shipping pipeline (`--no-proof`, ~3s for ten
programs). It exists because #209 and #211 both READ correctly in the source and could not
fire, so a source-grep gate would have passed them.

And the same question asked outside the `happy` forms found `#@ complete` / `#@ disjoint`
on a bodyless function: false guards that FAIL for an ordinary function and PROVE the
moment `\trusted` is added (witness **1720**). That one is NOT called a route — the caller
exploit was built and refused — and it is refused anyway, ahead of the day something
consumes it.

## Controls

`1717` (the trusted writer WITH `#@ \preserves`) passes; `0611`, `0614`, `1253` prove;
`0612`, `0613`, `0615`, `1047`, `1716` stay refused.
