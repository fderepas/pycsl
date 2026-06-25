# GATE-C-RESULTS — `Optional` (TY1 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `Optional` (PEP 484 = `Union[X, None]`)
**Spec:** `typing-engagement/ty1/optional-twoplane-spec.md` (thin specialization of `union-twoplane-spec.md`)
**Surface:** `test-suite/annotations.md` §12.4 (`Union` / `Optional` / `X | Y`)
**Independence:** Built from the two-plane spec + construct surface ONLY.
No `src/pycsl/` source read; no lowering diffs read. The gap doc (GAP-004)
cites only the emitted `.mlw` and pycsl's own run output, never the lowering
implementation.

**Run command:**
`source .venv/bin/activate && python3 src/pycsl/pycsl.py <driver>`
(provers: Alt-Ergo,2.6.2, → Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset for Optional

### O3 — None is always assignable to Optional[X]
- **Clause:** O3 (§1.1) — None is always assignable, unconditionally.
- **Driver:** `O3_none_assignable.py` —
  `def f(x: Optional[int]) -> Optional[int]: return None`
- **Expected (from spec):** PASS — `None` is always assignable to
  `Optional[X]`; the `return None` auto-injects into the `Arm_None`
  nullary constructor of the synthesized variant.
- **Actual (from run):** FAIL —
  ```
  This expression has type int, but is expected to have type
  PyCSL_Program._union_f_1
  ```
  See **GAP-004**. The `None`-arm return injection is not emitted (the
  `return None` lowers as the WhyML `0` literal, not as `Arm_None`).
- **NO-BLEND:** no — the runtime shim is not invoked by the driver; the
  failure is a pure static-plane lowering gap.

### O6 — `is None` narrowing (the load-bearing Optional clause)
- **Clause:** O6 (§1.2) — after `if x is None:` on `Optional[X]`, the
  False branch narrows `x` to `X`.
- **Driver:** `O6_is_none_narrowing.py` —
  `def f(x: Optional[int]) -> int: if x is None: return 0; return x`
  with `#@ ensures True` (NOT `ensures \result >= 0` — the latter is the
  separate postcondition issue GAP-001b from the Union side, NOT an
  Optional lowering gap).
- **Expected (from spec):** PASS — the False branch narrows `x` to `int`,
  so `return x` typechecks.
- **Actual (from run):** PASS —
  - `f__union_arm_Arm_0_0_inj` Valid (0.00s, 20 steps)
  - `f__union_arm_Arm_0_0_proj` Valid (0.00s, 15 steps)
  - `[+] Verification SUCCESS!`
  The narrowing is lowered as a constructor-pattern match (the `Arm_None`
  / `Arm_0_0` split); the False branch projects the variant to the `int`
  carrier. This is the Union-side GAP-001 fix carrying over to Optional
  (Optional reuses the Union seam — §12.4 of `annotations.md`).
- **NO-BLEND:** no — the runtime shim is not invoked; the narrowing is
  discharged by the static-plane variant match VCs (`f__union_arm_*`).
  See §3 for the sharpened no-blend probe.

### O8 (positive) — match exhaustiveness, both arms covered
- **Clause:** O8 (§1.3) — a `match` on `Optional[X]` must cover both arms
  (the `X` arm and the `None` arm).
- **Driver:** `O8_match_exhaustive.py` —
  `match x: case int(): return 1; case _: return 0` on `Optional[int]`.
  (The `case _:` catch-all covers the `None` arm, per the spec's "e.g.
  `case None:` or `case _:`" note.)
- **Expected (from spec):** PASS.
- **Actual (from run):** PASS —
  - `f__union_arm_Arm_0_0_inj` Valid (0.01s, 20 steps)
  - `f__union_arm_Arm_0_0_proj` Valid (0.00s, 15 steps)
  - `[+] Verification SUCCESS!`
- **NO-BLEND:** no — shim not invoked. (Caveat: the positive case PASSes
  the per-arm VCs; whether Why3's native exhaustiveness check actually
  fires on the `case _:` catch-all vs. treating the missing arm as
  vacuously covered is not distinguishable from this positive case alone
  — the negative case O8− below is the discriminator.)

### O8 (negative) — match non-exhaustiveness must FAIL
- **Clause:** O8 (§1.3) — a `match` covering only the `int` arm of
  `Optional[int]` (the `None` arm uncovered) is a static error.
- **Driver:** `O8_match_nonexhaustive.py` —
  `match x: case int(): return 1` (no `case None:` / `case _:`).
- **Expected (from spec):** FAIL — non-exhaustive match is a static error.
- **Actual (from run):** FAIL —
  ```
  Sub-goal unreachable point of goal f'vc.
  Prover result is: Unknown (why3: Unknown (sat)) (0.00s, 39 steps).
  [-] 1 goal(s) remain unproven after all provers.
  ```
  The match is correctly REJECTED (unlike the Union-side C9− which
  PASSed — see Union GAP-002). The rejection is via an "unreachable
  point" goal that the prover cannot discharge (the uncovered `None`
  arm leaves a path with no return, which Why3 flags). This is the
  correct O8 behavior: a non-exhaustive match on `Optional[X]` FAILs.
- **NO-BLEND:** no — shim not invoked.

### GT1 — `Optional[Any]`: Any refused, None arm remains typed
- **Clause:** O5 (§1.1) / OD3 (§3) / GT1 — `Optional[Any]` is treated as
  the two-arm union `{Any, None}` where `Any` is opaque and
  operation-barren; the `None` arm remains fully typed (O3 still holds).
- **Driver:** `GT1_optional_any.py` —
  `def f(x: Optional[Any]) -> int: return 0`
- **Expected (from spec):** the `Any` arm is dropped from the synthesized
  variant; GT1 is reported in `--soundness-report`; the function still
  proves (no operation on the `Any` arm).
- **Actual (from run):** PASS —
  ```
  UserWarning: GT1: Union arm `Any` refused (opaque, operation-barren)
  in variant '_union_f_0'. The arm was dropped from the synthesized
  variant; the static plane discharges C2/C3 against non-`Any` arms only.
  ```
  - `f'vc` postcondition Valid (0.01s, 6 steps)
  - `[+] Verification SUCCESS!`
  The GT1 warning fires; the `Any` arm is dropped; the `None` arm (O3)
  remains as `Arm_None` in the synthesized variant; the body returns a
  constant `int` so no operation on the `Any` arm is needed.
- **NO-BLEND:** no — the GT1 report is a static-plane well-formedness
  check; the runtime shim is not involved.

---

## 2. RUNTIME gate — S4 shim-faithfulness

### OR3 — no enforcement (the Optional shim is identity, via the Union seam)
- **Clause:** OR3 (§2.1) — the runtime does NOT check that a value stored
  under an `Optional[X]` annotation is `None` or of type `X`. The Optional
  shim (via the Union seam — OR1: `Optional[X] is Union[X, None]`) is
  identity; it discharges for ANY value.
- **Driver:** `OR3_no_enforcement.py` — calls `Union(int, str, val)` from
  `pycsl_lib.typ` with a string, a list, and `None`; each wrapped in a
  function with `#@ ensures \result == val`.
- **Expected (from spec):** PASS — the shim performs no enforcement;
  identity discharges regardless of value type.
- **Actual (from run):** PASS —
  - `call_list'vc` postcondition Valid (0.01s, 6 steps)
  - `call_none'vc` postcondition Valid (0.00s, 6 steps)
  - `call_string'vc` postcondition Valid (0.01s, 6 steps)
  - `[+] Verification SUCCESS!`
  The identity postcondition `result == val` discharges for ALL three
  values — including the list (provably outside any arm). NOTE: this is
  a different outcome from the Union-side R3/R8 gate (GAP-003), which
  FAILed with a call-shape mismatch. The Union shim identity now
  discharges cleanly — GAP-003 appears fixed.
- **NO-BLEND:** n/a (runtime-plane gate). The shim's identity
  postcondition cannot discharge any static narrowing / exhaustiveness /
  assignability VC (the static drivers never call the shim).

### OR5 — `is None` is a runtime identity test
- **Clause:** OR5 (§2.3) — `x is None` is the runtime identity test
  against the singleton `None`; it returns `True` iff `x` IS `None`. The
  runtime test narrows the VALUE (sometimes); the static narrowing
  narrows the TYPE (always, on the path) — they are DIFFERENT (OD2).
- **Driver:** `OR5_is_none_runtime_test.py` —
  `def f(val) -> int: if val is None: return 0; return 1` with
  `#@ ensures \result == 0 or \result == 1`.
- **Expected (from spec):** PASS — the runtime `is None` test partitions
  the value space into None / not-None, and the postcondition discharges
  on both branches (the static plane does not need to know the type of
  `val`).
- **Actual (from run):** PASS —
  - `f'vc` postcondition Valid (0.01s, 11 steps) [True branch]
  - `f'vc` postcondition Valid (0.01s, 15 steps) [False branch]
  - `[+] Verification SUCCESS!`
  The runtime `is None` test runs as a value comparison; the
  postcondition holds because the test partitions the value space.
- **NO-BLEND:** n/a (runtime-plane gate). This driver does NOT exercise
  the static `Optional[X]` narrowing (the parameter is untyped); it
  confirms ONLY the runtime-plane behaviour of `is None`. The static
  narrowing is tested by O6; the no-blend probe (§3) checks they are not
  blending.

---

## 3. NO-BLEND check (SHARPENED for Optional — OD2)

OD2 (optional-twoplane-spec.md §3) says the static O6 narrowing must NOT
be discharged by the runtime `is None` test. The static narrowing is a
proof-time path-condition judgment (the `Arm_None` constructor match);
the runtime test is a value-level comparison the program performs. A
lowering that let the runtime `is None` test's outcome SATISFY the O6
narrowing obligation would blend the planes.

### Probe: NOBLEND_O7 — narrowing claimed WITHOUT a guard (O7)
- **Clause:** O7 (§1.2, inherited from Union C8) — no narrowing without a
  guard. In the absence of an `is None` / `isinstance` / `TypeIs` /
  `TypeGuard` test, the static type of an `Optional[X]`-typed variable
  is NOT refined.
- **Driver:** `NOBLEND_O7_no_guard_narrowing.py` —
  `def f(x: Optional[int]) -> int: return x` (NO `is None` guard; `x` is
  used as `int` directly).
- **Expected (from spec):** FAIL — no narrowing without a guard (O7).
  If this driver INCORRECTLY PASSes, the runtime `is None` test is
  blending the planes (OD2 violation): it would mean the static plane is
  trusting the runtime semantics of `is None` (which would narrow at
  runtime if executed) instead of requiring a static guard.
- **Actual (from run):** FAIL —
  ```
  This expression has type PyCSL_Program._union_f_0,
  but is expected to have type int
  ```
  The lowering correctly REFUSES to narrow: without an `if x is None:`
  guard, `x` remains the synthesized variant `_union_f_0`, and `return x`
  is a type error (variant vs. `int`). The static plane does NOT blend
  the runtime `is None` semantics into the static judgment.

### NO-BLEND analysis for the O6 case
For the O6 driver (which DOES have the `if x is None:` guard and PASSes),
the question is: does it PASS because of the static-plane `Arm_None`
constructor match, or because of the runtime `is None` comparison?

The evidence:
1. The O6 VCs are `f__union_arm_Arm_0_0_inj` and `f__union_arm_Arm_0_0_proj`
   — per-arm injection/projection VCs on the `Arm_0_0` (int) constructor.
   These are static-plane variant VCs, NOT runtime-test VCs.
2. The NOBLEND_O7 probe (no guard, same `return x` shape) FAILs with the
   SAME type error as O6 would if the narrowing were absent. If the
   runtime `is None` test were satisfying the narrowing obligation, the
   NOBLEND_O7 driver would PASS (the runtime test would "narrow" at
   runtime). It does NOT — the narrowing is keyed on the GUARD presence
   in the static lowering, not on the runtime test execution.

Conclusion: the O6 narrowing is discharged by the static-plane `Arm_None`
constructor match (the variant match lowering), NOT by the runtime `is
None` comparison. The planes are NOT blending.

### NO-BLEND matrix

| Static case | Shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| O3  | no  | n/a | no  |
| O6  | no  | n/a | no  |
| O8+ | no  | n/a | no  |
| O8− | no  | n/a | no  |
| GT1 | no  | n/a | no  |

**NO-BLEND verdict: HOLDS.** No static case is discharged by the runtime
shim. The sharpened OD2 probe (NOBLEND_O7) confirms that the static O6
narrowing is keyed on the static-plane guard, not the runtime `is None`
test — a driver claiming narrowing WITHOUT a guard is correctly rejected.
The runtime `is None` test (OR5) and the static `is None` narrowing (O6)
are carried as SEPARATE contracts, per OD2.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 3 (O6, O8+, GT1) | 2 (O3, O8−*) | 5 |
| Runtime | 2 (OR3, OR5) | 0 | 2 |

\* O8− FAILs as expected (non-exhaustive match correctly rejected). It is
counted in the PASS column of "spec conformance" (the lowering correctly
FAILs a non-exhaustive match) but in the FAIL column of "verification
outcome" (the driver does not prove). Per the engagement, a negative case
that FAILs verification is a spec-conformance PASS.

- **Static gate:** 3/5 verify-PASS; 4/5 spec-conformance-PASS (O3 is a
  genuine gap; O8− FAILs-verification-correctly). See GAP-004 for O3.
- **Runtime gate:** 2/2 PASS. (The Union-side GAP-003 appears fixed — the
  shim identity postcondition now discharges.)
- **NO-BLEND check:** HOLDS. The sharpened OD2 probe (NOBLEND_O7)
  confirms the static narrowing is not blended with the runtime `is None`
  test.

## Gap docs written

- `GAP-004-o3-none-return-injection.md` — O3 `return None` from
  `Optional[X]` not lowered (the `Arm_None` return-path injection is
  missing). Static-plane lowering gap; NOT a blend.

## Notes for the coordinator

- The two Optional-specific load-bearing clauses split cleanly: O6 (the
  `is None` narrowing, the most-used Optional idiom) PASSES; O3 (the
  defining asymmetry — None is always assignable) FAILs. O3 is the
  reverse-direction lowering (value INTO the variant's `Arm_None`) vs.
  O6's forward-direction (variant OUT to the `int` carrier on the
  False branch). The forward lowering is implemented; the reverse is
  not.
- O8 (exhaustiveness) behaves correctly for Optional: the negative case
  (non-exhaustive match) is REJECTED (unlike the Union-side C9− which
  PASSed — Union GAP-002). The `case _:` catch-all in the positive case
  covers the `None` arm as the spec allows; whether Why3's native
  exhaustiveness check fires on the catch-all vs. treating it as vacuous
  is not distinguishable from the positive case alone, but the negative
  case confirms the lowering does enforce exhaustiveness for Optional.
- GT1 is the cleanest result: the warning fires, the `Any` arm is
  dropped, the `None` arm remains typed (O3 holds in the variant
  declaration even though O3's return-path lowering is gap'd), and the
  body proves. No action needed on GT1.
- The runtime plane is fully faithful (OR3 + OR5 PASS). The Union shim
  identity gap (GAP-003) appears resolved since the Union gate was
  written — the shim's `ensures \result == val` now discharges for any
  value. This is a runtime-plane improvement; it does NOT affect the
  static plane (the no-blend matrix remains all-`no`).
- The NO-BLEND invariant is intact and sharpened: the OD2 probe
  (NOBLEND_O7) is the key witness — a driver claiming narrowing without
  a guard is correctly rejected, proving the static narrowing is keyed
  on the static-plane guard, not the runtime `is None` test.
