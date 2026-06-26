# GAP-001 — Missing required TypedDict key silently filled with default

**Construct:** `TypedDict` (TY2 tier)
**Clause:** T9 (missing/extra keys rejected, total=True) — typeddict-twoplane-spec.md §1.3
**Plane:** Static (Interpreted)
**Finding type:** Lowering gap — missing-key rejection not enforced
**Severity:** Medium — T9's "missing required key is a static error" is a load-bearing
construction-typing obligation; silently filling the default hides the error and lets an
ill-typed construction through Why3 type-checking.

## Witness
- Driver: `typing-engagement/ty2/conformance/T9_missing_key.py`
  (`def f() -> Point: return {"x": 1}` — `Point` declares required `x: int, y: int`,
  the literal is missing `y`).

## Evidence
The driver type-checks and proves (L3-tc ✓, Verification SUCCESS) when the spec says it
MUST FAIL. The emitted `.mlw`:

```whyml
type point = { mutable x: int; mutable y: int }

let function f () : point
  requires { true }
  ensures  { true }
=
  { x = 1; y = 0 }     (* the missing `y` is silently filled with its default 0 *)
end
```

Why3's record-literal type-checking DOES require every field be present — but the lowering
fills the missing field with its `field_defaults` value (`0` for an int field) BEFORE
handing the literal to Why3, so Why3 sees a complete literal and accepts it. The static
rejection the spec requires (T9: "a literal missing a required key is a static error") is
bypassed.

The same applies to EXTRA keys: a literal `{"x": 1, "y": 2, "z": 3}` would drop the
unknown `z` silently (the lowering matches keys against declared fields and ignores
extras) rather than rejecting it.

## NO-BLEND
This is a static-plane lowering gap, NOT a blend. The runtime shim is not involved (the
static driver never calls the shim). The risk here is the opposite of a blend: the static
plane currently carries a WEAKER obligation than the spec requires (T9 not enforced),
which is divergence-by-weakness — a bug per `typing-global-impl.md` §0.

## Recommendation to core-agent
1. In `_typeddict_record_literal` (module6_whyml/expressions.py), when the construction
   context is a TypedDict record, REQUIRE every declared field to be present in the dict
   literal's keys; a missing required field should raise a `PyCSLSemanticError` (code
   `PYCSL-SEM-TYPEDDICT-MISSING-KEY`) BEFORE emitting the record literal — not silently
   fill the default. (The default-filling is correct for the `Point()` zero-arg
   construction path via `_call_record_constructor`, but NOT for the dict-literal path,
   which the spec T8/T9 treat as a fully-specified construction.)
2. Symmetrically, an EXTRA key (a key in the literal not in the declared fields) should
   raise `PYCSL-SEM-TYPEDDICT-EXTRA-KEY`.
3. Re-run the conformance drivers; T9 (negative) must now FAIL with the
   `PYCSL-SEM-TYPEDDICT-MISSING-KEY` error, and a new T9-extra negative must FAIL with
   `PYCSL-SEM-TYPEDDICT-EXTRA-KEY`.

## Status
**RESOLVED.** The core-agent fixed `_typeddict_record_literal` to raise
`PyCSLSemanticError` (code `PYCSL-SEM-TYPEDDICT-MISSING-KEY` /
`PYCSL-SEM-TYPEDDICT-EXTRA-KEY`) for missing/extra keys, instead of silently
filling defaults. T9 (negative) now FAILs with the correct error; a new
extra-key negative also FAILs. Positive cases (T8 construction, T5 field
access) still PASS. Re-verified: 80/80 pycsl-reference drivers PASS (no
byte-diff regression); os proof SUCCESS.
