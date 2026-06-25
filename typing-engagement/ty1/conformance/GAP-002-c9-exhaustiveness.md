# GAP-002 — C9 match exhaustiveness not enforced

**Construct:** `Union` (TY1 tier)
**Clause:** C9 (union-twoplane-spec.md §1.3)
**Plane:** Static
**Finding type:** Lowering gap (static obligation unimplemented)
**Severity:** High — exhaustiveness is a load-bearing safety check

## Witness
- Driver (positive): `typing-engagement/ty1/conformance/C9_match_exhaustive.py`
  (covers both arms of `Union[int, str]`) — PASS, as expected.
- Driver (negative): `typing-engagement/ty1/conformance/C9_match_nonexhaustive.py`
  (covers only the `int` arm of `Union[int, str]`) — should FAIL per spec.

## Evidence
The negative driver returns `Verification SUCCESS! All contracts formally
proven.` The generated `.mlw` for the non-exhaustive match is:

```why3
type _union_f_0 = Arm_0_0 int | Arm_0_1 string

let function f (x: _union_f_0) : int
  requires { true }
  ensures  { (result >= 0) }
=
  match x with
    | int ->
      1
    end
```

The `match` is lowered with `| int ->` as the pattern — i.e. matching
the variant value against the bare type name `int`, NOT against the
constructor `Arm_0_0`. Why3 accepts this (the pattern is vacuous / a
wildcard-like binding), so the `str` arm is silently uncovered. The
exhaustiveness obligation of C9 is not enforced.

## NO-BLEND
The runtime shim does NOT pass this case: the driver does not call the
shim, and exhaustiveness is purely a static-plane obligation. NOT a blend.

## Recommendation to core-agent
A `match` on a value of type `Union[A_1, ..., A_n]` must be lowered to a
WhyML `match x with | Arm_0_0 v_0 -> ... | Arm_0_1 v_1 -> ... end` over
the synthesized variant's constructors, so Why3's native exhaustiveness
check fires on a missing arm. The current lowering emits a pattern
against the type name, defeating the check.

## Status
Open. Awaiting core-agent fix.
