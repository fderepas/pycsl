# GAP-003 — Runtime shim identity postcondition cannot discharge (call-shape mismatch)

**Construct:** `Union` (TY1 tier)
**Clause:** R3 (no enforcement), R8 (no validation) — union-twoplane-spec.md §2.1, §2.4
**Plane:** Runtime (Shimmed)
**Finding type:** Shim-vs-lowering mismatch (identity postcondition unreachable)
**Severity:** Medium — the shim's identity claim is the entire runtime contract; if it cannot discharge, the runtime plane carries no verified meaning.

## Witness
- Driver: `typing-engagement/ty1/conformance/R3_no_enforcement.py`
  (`Union(int, str, val)` for string / list / None values).
- Driver: `typing-engagement/ty1/conformance/R8_no_validation.py`
  (`Union(int, str, val)` with a list value provably outside the arms).

## Evidence
Both drivers FAIL with the same Why3 type error:

```
File ".../.pycsl_mae1n35n.mlw", line 18, characters 11-14:
This expression has type int, but is expected to have type ()
[-] Verification FAILED or INCOMPLETE.
```

The generated `.mlw` declares the shim as a zero-argument abstract val:

```why3
val union () : int
  ensures  { (result = py_val) }   (* linear *)
```

but the call site emits it with the args present:

```why3
(union int str py_val)
```

Why3 rejects the call (the val takes `()` but is given three `int` args),
so the identity postcondition is never discharged — neither for a value
in an arm nor for a value outside any arm.

## Body-vs-postcondition inconsistency (secondary)
Independently of the lowering, the shim's body is
`def Union(*args) -> int: return 0`, but its postcondition is
`#@ ensures \\result == val`. The body proves `\\result == 0`, not
`\\result == val`. The identity postcondition could only ever hold when
`val == 0`. The shim body does not implement identity.

## NO-BLEND
This is a runtime-plane gap, not a blend. The shim does NOT pass any
static case (the static drivers never call the shim, and the shim's
postcondition does not discharge any static narrowing / exhaustiveness /
assignability VC). The risk here is the opposite of a blend: the runtime
plane currently carries NO verified meaning at all, which is faithful to
S3 (R3: no enforcement) but fails the spec's R8 requirement that the
shim's identity postcondition actually discharge.

## Recommendation to core-agent
1. Lower `Union(*args)` to a val whose arity matches the call shape, OR
   lower the call site to `union ()` and pass `val` via a dedicated
   parameter so the identity postcondition can be expressed and discharged.
2. Make the shim body `return val` (not `return 0`) so the
   `ensures \\result == val` postcondition is realizable.

## Status
Open. Awaiting core-agent fix.
