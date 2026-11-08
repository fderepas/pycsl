# ROUTE #102 — A BARE `#@ assigns g` ON A BODYLESS `val` EMITS **NO FRAME AT ALL**

**Severity 1. CLOSED gen #18 (2026-09-13). Found by re-running the carrier list gen #17
attached to route #101 — MEASURED, not assumed.**

## THE ONE-LINE STATEMENT

The FOURTH spelling of "this stub writes through a parameter". `#@ assigns g` lowers to IR
`{"type": "Var", "name": "g"}`, which matched neither frame collector in
`_emit_frame_condition` and never reached `_unframed_regions`, so route #98's refusal could not
fire. The `val` was emitted PURE and a caller proved the array unchanged across it.

## BOTH DIRECTIONS MEASURED (at 5795cfef)

| arm | verdict |
|---|---|
| FALSE fact `ensures \result == 7` | **PROVES** — `Verification SUCCESS! All contracts formally proven.` |
| CPython ground truth | `d([7,7,7]) = 5`, `a` after `= [5, 7, 7]` |
| after the repair | FAILS (`1 goal(s) remain unproven`) |

## WHY IT IS ITS OWN ROUTE AND NOT A FOOTNOTE TO #101

Gen #17 NAMED this carrier in route #101's file and wrote: *"check both further carriers
rather than assuming the one repair covers them — a carrier surviving a repair is a second
route."* It was checked at baseline BEFORE the repair landed, it was LIVE, and it has its own
IR node type, its own parse path and its own witness (1290). Recording it as a footnote would
have hidden a measured sev-1 exploit inside another route's changelog.

## THE REPAIR

Shared with route #101: one collector arm keyed on the **resolved write root** rather than on
the node type. Peel every `Subscript` layer off the target, then dispatch on what is actually
written; a `Var` root whose `whyml_ident` is an array parameter of the emitted signature yields
`writes { g }`. Route #98's emitted-name-space rule applies IN FULL.

## THE DELIBERATE CARVE-OUT, AND WHY IT IS NOT A SILENT DROP

A bare `Var` that is **not** an array parameter is NOT routed into the refusal. An `int`/`str`
parameter is emitted BY VALUE, so a callee write to it is invisible to the caller and needs no
frame; refusing those would reject a large and sound population (the self-annotation mirrors
alone spell hundreds of `#@ assigns <local>`). Witness 1289 and the k4 probe pin that.

**THE RESIDUE IS NAMED, NOT WAVED AT:** a bare `Var` naming a **RECORD-typed** parameter (a
class instance) is emitted as a mutable Why3 record and would need a frame. That case is
UNPROBED at the close of gen #18 and is the first item on the next generation's list.

## REOPENING / CLOSING CONDITION

CLOSED: witness `1290_route102_bare_var_assigns_on_a_bodyless_val_had_no_frame.py` PROVED at
5795cfef and FAILS at HEAD. REOPENS if any frame collector is again keyed on a node type
rather than on the resolved write path, or when the record-typed-parameter residue is probed
and found live.
