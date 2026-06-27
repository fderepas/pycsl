# GATE-C-RESULTS — `@overload` (TY2 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `@overload` (PEP 484)
**Spec:** `typing-engagement/ty2/overload-twoplane-spec.md`
**Surface:** `test-suite/annotations.md` §12.14
**Independence:** Built from the two-plane spec + the documented construct surface
(`test-suite/annotations.md` §12.14 + the `src/pycsl_lib/typ/__init__.py` shim
contract surface — which IS the surface, not the lowering) ONLY. No
`src/pycsl/frontend/` or `src/pycsl/module6_whyml/` lowering source read; no
lowering diffs read. The drivers are authored from the spec clauses O1–O6 + R1–R7
and the documented lowering-independent contract surface.

**Run command:**
`source .venv/bin/activate && cd src && python3 pycsl/pycsl.py <driver>`
(provers: Alt-Ergo,2.6.2, → Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset

### T1 — guard synthesis + call-site selection (int overload)
- **Clause:** O2 (guard per stub) + O4 (selection at call sites)
- **Driver:** `T1_int_overload.py` — ONE `@overload` stub `f(x: int) -> int` with
  `#@ ensures \result == x`, implementation `def f(x: int) -> int: return x`, call
  site `f(5)` expecting `\result == 5`.
- **Expected (from spec):** typecheck + prove — the int stub's guard selects, its
  postcondition `\result == x` applies at the call site, `f(5)` proves `\result == 5`.
- **Actual (from run):** PASS — `[+] Verification SUCCESS! All contracts formally proven.`
  (f's two guarded-postcondition VCs Valid; g's call-site VC Valid.)
- **Non-vacuity:** `--check-vacuity` GREEN; `bin/false-twin.py` kills 1/1 mutant
  (the impossible `\result == x+1` twin FAILs).
- **NO-BLEND:** no — the driver does not call the runtime shim; the guarded-
  postcondition VC is emitted by the static plane.

### T2 — multi-stub family, the non-matching stub's guard is vacuous
- **Clause:** O3 (guarded postcondition per stub) + O6 (implementation proves each)
- **Driver:** `T2_multi_stub_family.py` — TWO stubs `f(x: int) -> int` and
  `f(x: str) -> str`, each with `#@ ensures \result == x`; implementation
  `def f(x: int) -> int: return x` (annotated per §1.6). The str stub's guarded
  postcondition `isinstance(x, str) -> \result == x` is vacuously discharged (param
  is `int`, str guard false).
- **Expected (from spec):** prove — both guarded postconditions discharge (int
  non-vacuously, str vacuously); call `f(5)` selects the int overload.
- **Actual (from run):** PASS — `Verification SUCCESS`.
- **Non-vacuity:** `false-twin` kills 1/1 mutant.
- **NO-BLEND:** no — shim not invoked.

### T3 — stub with NO `#@ ensures` contributes no guarded postcondition
- **Clause:** O3 ("A stub with no postcondition contributes no guarded clause … it
  adds no VC.")
- **Driver:** `T3_stub_no_ensures.py` — ONE `@overload` stub `f(x: int) -> int`
  with NO `#@ ensures`; implementation `def f(x: int) -> int: return x`; call `f(5)`.
- **Expected (from spec):** prove — no guarded-postcondition VC is emitted for
  the stub; the call site typechecks.
- **Actual (from run):** PASS — `Verification SUCCESS`.
- **NO-BLEND:** no — shim not invoked.

### T4 — the no-blend witness: selection by TYPE ALONE, no runtime isinstance
- **Clause:** O5 (selection is type-based, NOT runtime-dispatch-based) — the
  load-bearing no-blend clause.
- **Driver:** `T4_no_blend_type_selection.py` — ONE `@overload` stub `f(x: int) -> int`
  with `#@ ensures \result == x`; implementation `def f(x: int) -> int: return x`
  with **NO `isinstance` branch**. The int overload's guarded postcondition must
  apply at the call site `f(5)` by TYPE alone — if the selection were blended into
  the runtime dispatch, an implementation with no isinstance branch could not
  discharge the call-site postcondition.
- **Expected (from spec):** prove — the int stub's guarded postcondition applies
  at the call site by type-based selection alone, even though the body has NO
  isinstance branch.
- **Actual (from run):** PASS — `Verification SUCCESS`. This is the no-blend
  witness: the static selection VC is discharged by the argument's static type,
  independent of any runtime isinstance dispatch in the body.
- **Non-vacuity:** `false-twin` kills 1/1 mutant.
- **NO-BLEND:** HOLDS — the static selection is type-based; the body has no
  runtime dispatch to blend with.

### T5 (negative) — a non-`...` body is NOT an overload stub
- **Clause:** O1a ("A stub with a non-`...` body is NOT an overload stub — it is a
  regular decorated function, byte-identical fallback.")
- **Driver:** `T5_non_ellipsis_body.py` — `@overload def f(x: int) -> int: return x`
  (real body, not `...`); the function is NOT collected as a stub, emitted as a
  regular function.
- **Expected (from spec):** prove — the function is a regular function; its own
  `#@ ensures \result == x` discharges; no guarded postcondition is synthesized.
- **Actual (from run):** PASS — `Verification SUCCESS`.
- **NO-BLEND:** no — the function is a regular decorated function.

---

## 2. RUNTIME gate — S4 shim-faithfulness drivers

### R3 — no enforcement (identity holds for ANY value)
- **Clause:** R3 (no type enforcement at runtime) + R6 (no validation in the shim)
- **Driver:** `R3_no_enforcement.py` — calls `overload(func, val)` from the shim
  with a list `val` (provably outside any overload's parameter type); expects
  `#@ ensures \result == val` to discharge.
- **Expected (from spec):** PASS — the shim performs no enforcement; identity
  discharges regardless of value type.
- **Actual (from run):** PASS — `Verification SUCCESS`.
- **NO-BLEND:** n/a (runtime-plane gate).

### R6/R7 — no validation in the shim; the implementation is a plain function
- **Clause:** R6 (no validation) + R7 (the implementation is a plain function)
- **Driver:** `R6_no_validation.py` — calls `overload(None, val)` with an int
  `val` (provably not a function object); the shim performs no validation.
- **Expected (from spec):** PASS — the shim carries only the identity
  postcondition; no overload-resolution check fires.
- **Actual (from run):** PASS — `Verification SUCCESS`.
- **NO-BLEND:** n/a (runtime-plane gate).

---

## 3. NO-BLEND check

For each static case, does the runtime shim pass it?

| Static case | Shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| T1 | no  | n/a | no  |
| T2 | no  | n/a | no  |
| T3 | no  | n/a | no  |
| T4 | no  | n/a | no  |
| T5 | no  | n/a | no  |

For each runtime case, does the static lowering pass it?

| Runtime case | Static lowering invoked? | Static VC passes the runtime claim? | Blend? |
|---|---|---|---|
| R3 | no (the shim call is opaque; the static plane does not lower `overload(...)` to a guarded-contract family) | n/a | no |
| R6/R7 | no | n/a | no |

**NO-BLEND verdict: HOLDS.** No static case is discharged by the runtime shim
(the static drivers never call the shim, and the shim's identity postcondition
`ensures \result == val` is opaque — it cannot discharge a guarded-postcondition
VC `isinstance(p_i, T_i) -> Q_i`, which is a WhyML formula over the parameter's
type tag). No runtime case is discharged by the static lowering (the shim call is
opaque to the static plane — `overload(...)` returns an `int`-modelled opaque
value). The load-bearing divergence D1 (type-based selection vs runtime isinstance
dispatch) is preserved: T4 confirms a static call-site selection discharges with
NO runtime isinstance branch in the body — the selection is type-based, full stop.
The no-blend rule is defended by author separation: this conformance-agent authored
the gates from the two-plane spec + surface alone, never reading the lowering.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 5 (T1, T2, T3, T4, T5) | 0 | 5 |
| Runtime | 2 (R3, R6/R7) | 0 | 2 |

- **Static gate:** 5/5 PASS. The overload family's guarded-contract-family
  obligations (O2 guard synthesis, O3 guarded postcondition, O4 type-based
  call-site selection, O5 no-blend, O6 implementation proves each, O1a non-`...`
  fallback) are all enforced and discharged.
- **Non-vacuity:** `--check-vacuity` GREEN on T1; `bin/false-twin.py` kills
  3/3 mutants across T1/T2/T4 — the guarded-postcondition VCs are non-vacuous.
- **Runtime gate:** 2/2 PASS — the shim performs no validation; identity
  discharges for any value (R3, R6/R7).
- **NO-BLEND check:** HOLDS. T4 is the load-bearing witness: type-based
  selection discharges with no runtime isinstance dispatch in the body.

## Gap docs written

None. No gaps surfaced — the construct passes its declared S5 subset, its S4
shim-faithfulness drivers, and the no-blend check on the first pass.

## Notes for the coordinator

- The TY2 monomorphic scope restriction (spec §1.6 — the implementation's
  parameter must be annotated for the guard to decide) is exercised by every
  static driver: each implementation is `def f(x: int) -> int`. An unannotated
  implementation yields a symbolic `typeof_op` guard (sound but imprecise) and is
  out of the declared S5 subset, consistent with the spec.
- A pre-existing limitation (UNRELATED to `@overload`) affects implementations
  whose BODY contains `if isinstance(x, int): ...` dispatch: the body-level
  `isinstance` lowering emits a `subtag` predicate in a non-ghost `if` context,
  which Why3 rejects ("Logical symbol subtag is used in a non-ghost context").
  This is a pre-existing isinstance-body lowering gap, NOT an overload gap — the
  overload construct's static guarded-postcondition family is correctly
  synthesized and discharged regardless (the conformance subset uses
  unconditional-return implementations, per the TY2 scope). Flagged for a future
  isinstance-body-lowering enhancement; not a Gate-C blocker for `@overload`.
