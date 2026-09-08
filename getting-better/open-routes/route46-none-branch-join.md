# OPEN ROUTE #46 — route #44's `None` record is FLOW-INSENSITIVE, and a BRANCH walks past it

**Found 2026-09-08 by relaunch #48 while closing route #44, at commit `c9bb23b2`.
NOT CLOSED — the residue is measured, and the obvious repair was BUILT and REFUTED.**

## The demonstration (default `hoare` model, no flags, Python run to confirm)

```python
#@ requires c > 0
#@ ensures \result == 7
#@ assigns \nothing
def f(c: int) -> int:
    if c > 0:
        x = None
    else:
        x = 5
    if x == 0:             # Python: `None == 0` is False -> f(1) returns 0
        return 7
    return 0
```
Proves at `c9bb23b2` (and at every earlier commit). Reproducer:
`/tmp/w48probe/j1_none_branch_leak.py`, kept as `scratchpad/w48/probe/j1_none_branch_leak.py`.

## Why route #44's fix does not reach it

Route #44 records a `None` binding in `_erased_truthy_locals` and makes a READ of that name
the opaque `pycsl_none`. The record is **linear**: it is written when the assignment is
EMITTED and CLEARED when the name is rebound, exactly as route #41 established. Emission
walks the `if` body and then the `else` body, so the `else`'s `x = 5` clears the record the
`then`'s `x = None` had set, and the guard after the join reads the ordinary `!x`. In the
`then` branch the model still holds `x := 0`, so `x == 0` is decidable there.

## THE OBVIOUS REPAIR WAS BUILT AND IT IS REFUTED — do not re-attempt it as stated

**"Never clear a `None` record" (a STICKY record) closes this reproducer and introduces a
NEW UNSOUNDNESS of its own.** Measured, both halves:

* it DOES close it (`j1` fails closed) and the corpus byte-diff stays at the same single
  line;
* but `_to_bool` reads the SAME dict, and route #44's truthiness arm answers `false` for a
  `None`-recorded name — which is faithful only on the path that bound `None`. With a
  sticky record, `cls = None; cls = <str>; if cls:` collapsed to the literal `false` on a
  path where the string is non-empty. MEASURED in the `module6_whyml/types.py` mirror
  emission: `if (not (not (str_eq_op !cls "")))` became `if (not false)`.
* a second sticky variant, gated at READ time on the name not being string-typed, ALSO
  fails: the read then falls through to route #41's per-name arm (the name is still IN the
  dict), so a string local emitted `pycsl_erased_receiver_name` — an `int` — into
  `str_eq_op`, a Why3 TYPE ERROR. Both variants are in this window's record.

**THE LESSON, and it generalizes past this route: `bool(x) is False` and `x is the None
singleton` are PATH facts, and a flow-INSENSITIVE record cannot carry a path fact. Route
#41 got away with it because its facts ("this name is bound to a generator") were only ever
used to REFUSE; route #44's are used to DECIDE.**

## REOPENING CAPABILITY

A real JOIN at `_handle_if_stmt`: save the record before the branches, emit each branch from
the saved state, and merge by UNION (a name recorded in EITHER branch stays recorded after
the join, and its `_to_bool` arm must then become opaque rather than `false`, because
falsiness is no longer certain). The cost is honest and was measured: `_handle_if_stmt` is
an UNTRUSTED mirror method, so the build owes a verbatim mirror body sync, an extension of
its `assigns` clause to include `_erased_truthy_locals` (the frame plane will demand it),
and a whole-file re-proof of `module6_whyml/stmt_control_flow.py`.

## What is NOT affected, so the residue is not overstated

* A `while` loop does not leak: the loop havocs locals the invariant does not pin, so
  `x = None; while ...; if x == 0:` already fails closed (measured).
* Both-branches-`None` does not leak (the record survives).
* The four shapes route #44 closes (witnesses `1053`–`1055` are route #42's; route #44's are
  `1058`–`1061`) are unaffected — they are all straight-line.
