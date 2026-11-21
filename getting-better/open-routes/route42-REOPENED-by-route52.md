# ROUTE #42 IS **REOPENED** AND LIVE AT HEAD — and the plane that should have caught it
# has a blind spot that made the reopening look byte-inert
# (found 2026-09-09 by relaunch #50, from the FIRST reference-suite run to COMPLETE since
#  route #52 landed)

## THE FACT

`test-suite/corpus/pycsl-reference/1053_route42_int_is_true` — route #42's own negative
witness, `# pycsl-expected: FAIL` — **PROVES** at HEAD. So do `1054_route42_int_is_false`
and `1055_route42_int_isnot_true`. Three XPASS.

An XPASS on a route witness is not a test-hygiene problem. It is the harness saying, in the
way it was designed to say it, that **a closed soundness route is open again**. Route #42 is
`<int> is True` proving `\result == 7` where Python returns 0.

## BISECTED — IT IS ROUTE #52 (`223424b9`), AND EVERY STEP WAS MEASURED

| commit | 1053 |
|---|---|
| `d7ce974c` route #42 fully banked | fails closed |
| `5342bea1` routes #47/#48 closed | fails closed |
| `5f57a95d` routes #46/#50 closed | fails closed |
| **`223424b9` route #52 closed** | **PROVES — route #42 OPEN** |

At `5f57a95d` the file does not merely fail, it is **REFUSED**, with route #42's own message:

> `[whyml-emit]: an IDENTITY test against a `bool` literal (`X is True` / `X is False`) is
> refused unless the emitter can SHOW `X` is a Python `bool` (ROUTE #42).`

**WHY IT HAPPENED.** Route #42's repair was a WHITELIST: `X is <bool literal>` is admitted
only where the emitter can SHOW `X` is a Python `bool`, and REFUSED otherwise. Route #52
deliberately replaced that with a BLACKLIST — its own commit message states the departure —
refusing `is` between operands it can show are value-typed, and leaving everything else
narrowed to `==`. For `x = 1; if x is True:` the emitter cannot show `x` is value-typed any
more than it could show it is a `bool`, so the blacklist does not fire, the refusal is gone,
and the operand falls back to the `==` narrowing that IS route #42's original defect.

**This is route #52's own stated lesson turned on itself.** Its message says a whitelist
"would have to refuse the SIX non-singleton `is` sites in the whole tree" and chose a
blacklist for that reason. The choice was defensible; what was missed is that #42's
whitelist was not an alternative spelling of the same rule — it was carrying a REFUSAL that
the blacklist does not reproduce.

## HOW IT GOT PAST THE PLANES — A REAL BLIND SPOT, NOT CARELESSNESS

Route #52 landed claiming, and the progress log records, *"mirror emission 0 of 53 move and
all 53 emit; corpus byte-diff ZERO over 887"*. The corpus half of that claim is TRUE AND
USELESS, and the reason is structural:

> **A byte-diff compares the files present on BOTH sides. At `5f57a95d`, `1053` is REFUSED,
> so it emits NO `.mlw` at all. It therefore has no baseline counterpart, and a
> diff-the-common-files sweep reports ZERO CHANGES while a REFUSAL has silently become an
> EMISSION — which is the one direction that can only ever be a soundness loss.**

The mirror half of the plane does guard this: it asserts "all 53 still emit". The corpus half
counts emissions (`emitted N of M`) but nothing compares that N across the two sides.

**I had the same one-sided blind spot this window** and should say so: my own sweeps check
`GONE` (a file that stops emitting) and not `APPEARED`. They happened to be safe because the
`emitted N of M` counts matched on both sides for routes #51 and #55, but that was luck of
inspection, not a gate.

## WHY NOBODY SAW IT FOR A WHOLE WINDOW

The corpus XPASS rule has counted as a failure since relaunch #44 and it worked perfectly —
the harness flagged all three the first time it was asked. **It was simply never asked**: the
reference suite has not run to COMPLETION since route #52 landed. Window #49's run was
killed; this window's runs 2, 3 and 4 were killed by me (I landed while they ran); run 5 is
the first completed suite since, and it found this in its first pass.

**This is the campaign's own lesson, paid for a third time: a signal nobody collects is not
a signal.** #49 found `check-trusted-raises-honesty` RED at HEAD with nobody looking; #50
found only `doc-coherency` wired into the runner; and now a CLOSED SOUNDNESS ROUTE has been
open for a window because the one gate that catches it takes 85 minutes and kept being
killed.

## THE SUITE RESULT IN FULL (run 5, rc=1, 3229/3251)

22 confirmed failures = the standing nineteen + THESE THREE XPASS. The nineteen are
`pycsl-reference/0211`–`0220`, `0700`, `0701` and `python-reference/0043, 0048, 0079, 0080,
0082, 0095, 0110`. **`0700` is separately diagnosed** in
`finding-0700-module-level-record-default.md`.

## THE REPAIR (scoped, NOT yet built)

Restore route #42's refusal ON TOP OF route #52's blacklist — they are not alternatives.
The bool-singleton test needs its own arm, ahead of the blacklist: `X is <True|False>` is
ADMITTED only where the emitter can show `X` is a Python `bool`, and REFUSED otherwise,
exactly as `d7ce974c` had it. Route #52's blacklist then keeps its own job (str/int/tuple/
list/dict/set identity) and its two semantic exemptions (`x is x`, and the
None/Ellipsis/NotImplemented singleton family) untouched.

**Gate it with the thing that failed here**: after the change, `1053`/`1054`/`1055` must go
back to REFUSED, `1092`/`1093` (route #52's own witnesses) must keep their verdicts, and the
corpus sweep must be compared BY EMISSION COUNT as well as by byte-diff.

## AND FIX THE PLANE, NOT ONLY THE ROUTE

The byte-diff sweep must fail when a corpus file that emitted NO `.mlw` on the baseline side
emits one on the candidate side. That is a two-line change to the comparison and it is the
only reason this route survived a landing that was, in every other respect, carefully
measured.

---

# STATUS — RE-CLOSED (2026-09-09). The cause was DEAD CODE, not a change of policy.

Reading the code made the diagnosis sharper than the bisect alone could. Route #42's refusal
had not been *replaced* by route #52's blacklist — it had been left in the file and made
**unreachable twice over**:

```python
            if _r52_bad is not None and _r42_other is None:      # <- requires _r42_other None
                raise _R52Err(...)                               # <- unconditional
                if not _r42_ok:                                  # <- DEAD: after a raise
                    raise _R42Err(... _r42_other.get("type") ...) # <- and derefs _r42_other
```

The guard requires `_r42_other is None` while the body dereferences `_r42_other`: the arm
could not have run even if the `raise` above it were removed. That is the tell, and it is why
this reads as a merge/indentation accident rather than a decision.

**THE FIX**: route #42's refusal is restored at its own level, guarded by
`_r42_other is not None and not _r42_ok`, and placed AHEAD of route #52's blacklist. The two
are disjoint by construction — #52's guard already excludes the bool-literal case — so #52
keeps its own job and both its semantic exemptions (`x is x`, and the
None/Ellipsis/NotImplemented singleton family) untouched.

## MEASURED AT THE RE-CLOSED TREE

  * `1053`/`1054`/`1055` are REFUSED again, each by **route #42's own message**, and
    `1092` is still refused by **route #52's own message** while `1093` still PROVES — so
    the two refusals are localised to their own routes and neither swallowed the other
  * mirror emission **0 of 53 move**, all 53 emit, **L3-tc 53/53** — which also means queue
    D's in-flight `expressions`/`statements` proofs are NOT superseded by this fix
  * corpus: **3 files stop emitting** (exactly `1053`/`1054`/`1055` — that IS the fix) and
    **0 files move**; compared in BOTH directions this time
  * both fidelity planes byte-identical to HEAD's own runs
  * metric UNCHANGED 456/481/25/0; mirror-coverage, raises-honesty, type-keyed,
    vacuous-drivers, emit-ir-arm-postconditions and doc-coherency all rc=0

## STILL OWED — THE PLANE FIX

The corpus byte-diff must fail when a file that emitted NO `.mlw` on the baseline side emits
one on the candidate side. Until that exists, the same class of regression can land again
with a green measurement. The comparison is currently an AD-HOC DRIVER PROCEDURE, not a
script — `bin/byte-diff-sweep.sh` only EMITS into a directory and the diffing is done by
whoever runs it, which is precisely why the direction nobody thought to check was never
checked.
