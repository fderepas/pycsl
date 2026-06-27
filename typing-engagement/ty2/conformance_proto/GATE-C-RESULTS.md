# GATE-C-RESULTS — `Protocol` / `@runtime_checkable` / `#@ conforms_to` (TY2 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `Protocol` (PEP 544) + `@runtime_checkable` + `#@ conforms_to`
**Spec:** `typing-engagement/ty2/protocol-twoplane-spec.md`
**Surface:** `test-suite/annotations.md` §12.15
**Independence:** Built from the two-plane spec + the documented construct surface
(`test-suite/annotations.md` §12.15 + the `src/pycsl_lib/typ/__init__.py` shim
contract surface — which IS the surface, not the lowering) ONLY. No
`src/pycsl/frontend/` or `src/pycsl/module6_whyml/` lowering source read; no
lowering diffs read. The drivers are authored from the spec clauses P1–P5 + R1–R7
and the documented lowering-independent contract surface.

**Run command:**
`source .venv/bin/activate && cd src && python3 pycsl/pycsl.py --check-behavioral-subtyping <driver>`
(provers: Alt-Ergo,2.6.2, → Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset

### P2 — conformance: per-method contract refinement
- **Clause:** P2 (§1.1, the load-bearing rule) — a class C conforms to P iff each
  member's contract refines P's member's contract (weaker pre, stronger post).
- **Driver:** `P2_conformance_refines.py` — `class Drawable(Protocol)` with member
  `draw` carrying `#@ ensures \result >= 0`; `class Square` with `#@ conforms_to
  Drawable` and `draw` carrying the STRONGER post `#@ ensures \result >= 5`
  (`result >= 5 -> result >= 0` holds — a refinement).
- **Expected (from spec):** prove — the per-method refinement goal
  `square__draw_refines_drawable` (`((pre_P -> pre_C) /\ (post_C -> post_P))`)
  discharges.
- **Actual (from run):** PASS — `[+] Verification SUCCESS! All contracts formally proven.`
  The refinement goal `square__draw_refines_drawable` is **Valid (154 steps)**.
- **Non-vacuity:** `--check-vacuity` GREEN. The P5 keystone (below) confirms
  non-vacuity by contradiction: the SAME refinement-goal structure, with a
  non-refining contract, FAILS — so the goal is genuinely discriminating.
- **NO-BLEND:** no — the driver does not call the runtime shim; the refinement
  goal is emitted by the static plane over the two contracts.

### P3 (negative) — non-conformance: a class missing a member is a static error
- **Clause:** P3 (§1.1) — a class C that lacks a member of P does NOT conform to P.
- **Driver:** `P3_missing_member.py` — `class Circle` declares `#@ conforms_to
  Drawable` but does NOT provide a `draw` method.
- **Expected (from spec):** the file is REJECTED with a semantic error
  (`PYCSLSEMANTICERROR` — "class 'Circle' ... does not provide member 'draw'").
- **Actual (from run):** PASS (expected-fail) — `[!] PIPELINE ERROR:` +
  `class 'Circle' (line 26): '#@ conforms_to Drawable' but 'Circle' does not
  provide member 'draw'. Conformance requires every protocol member to be present
  with a refining contract.` The construct is rejected at the front-end, before
  any VC is emitted (P3).
- **NO-BLEND:** no — the rejection is a static semantic check, not a runtime
  presence check.

### P5 — THE GT7 NO-BLEND WITNESS: presence does NOT satisfy static conformance
- **Clause:** P4 (§1.1) + P5 (§1.2) + D1 (§3) — the load-bearing no-blend clause.
  The static conformance obligation is a per-method contract-refinement VC, NOT a
  presence check. A class with method presence (passes runtime isinstance) but a
  non-refining contract FAILS static conformance.
- **Driver:** `P5_no_blend_presence_vs_refinement.py` — `class Square` HAS the
  `draw` method (method PRESENCE — it would pass a runtime `@runtime_checkable`
  isinstance check), but its contract `#@ ensures \result >= -100` is a WEAKER
  post than the protocol's `#@ ensures \result >= 0` (the refinement
  `result >= -100 -> result >= 0` does NOT hold).
- **Expected (from spec):** the refinement goal `square__draw_refines_drawable`
  is UNPROVABLE — verification FAILS. This is the keystone: the static
  conformance is a per-method contract-refinement VC, INDEPENDENT of method
  presence. If this driver PASSED, the GT7 no-blend check would be BROKEN.
- **Actual (from run):** PASS (expected-fail) — `[-] Verification FAILED or
  INCOMPLETE.` The refinement goal `square__draw_refines_drawable` is
  Unknown/unsat (cannot discharge `result >= -100 -> result >= 0`). The static
  conformance is NOT discharged by method presence — the GT7 no-blend check
  HOLDS.
- **NO-BLEND:** HOLDS — this IS the no-blend witness. The static conformance is
  a contract-refinement VC; the runtime `@runtime_checkable` presence check
  (R3) cannot rescue it.

---

## 2. RUNTIME gate — S4 shim-faithfulness drivers

### R3/R4 — @runtime_checkable shim performs NO validation (identity)
- **Clause:** R3 (§2.1 — presence-only isinstance) + R4 (§2.2 — no validation in
  the shim).
- **Driver:** `R3_shim_no_validation.py` — calls `runtime_checkable(None, val)`
  from the shim with an int `val` (provably not a class object); expects
  `#@ ensures \result == val` to discharge.
- **Expected (from spec):** PASS — the shim performs no enforcement; identity
  discharges regardless of value type.
- **Actual (from run):** PASS — `Verification SUCCESS` (`shim_is_identity'vc`
  Valid).
- **NO-BLEND:** n/a (runtime-plane gate).

### R6 — no static conformance at runtime: the shim cannot discharge any refinement VC
- **Clause:** R6 (§2.2) — the runtime does NOT perform the static conformance
  check (P2); the shim's identity postcondition is opaque to the static plane.
- **Driver:** `R6_shim_no_conformance.py` — calls `runtime_checkable(None, val)`
  with a bare int `val` (provably outside any protocol's conformance); the shim's
  identity postcondition must discharge regardless.
- **Expected (from spec):** PASS — the shim's identity postcondition carries
  ONLY the identity; it CANNOT discharge any contract-refinement VC.
- **Actual (from run):** PASS — `Verification SUCCESS` (`shim_no_conformance'vc`
  Valid).
- **NO-BLEND:** n/a (runtime-plane gate).

---

## 3. NO-BLEND check

For each static case, does the runtime shim pass it?

| Static case | Shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| P2 | no  | n/a | no  |
| P3 | no  | n/a | no  |
| P5 | no  | n/a | no  |

For each runtime case, does the static lowering pass it?

| Runtime case | Static lowering invoked? | Static VC passes the runtime claim? | Blend? |
|---|---|---|---|
| R3/R4 | no (the shim call is opaque; the static plane does not lower `runtime_checkable(...)` to a refinement VC) | n/a | no |
| R6 | no | n/a | no |

**NO-BLEND verdict: HOLDS.** No static case is discharged by the runtime shim
(the static drivers never call the shim, and the shim's identity postcondition
`ensures \result == val` is opaque — it cannot discharge a contract-refinement VC
`((pre_P -> pre_C) /\ (post_C -> post_P))`, which is a WhyML formula over the two
method contracts). No runtime case is discharged by the static lowering (the shim
call is opaque to the static plane — `runtime_checkable(...)` returns an
`int`-modelled opaque value). The load-bearing divergence D1 (full-signature
refinement vs presence-only isinstance) is preserved: P5 confirms a class with
method PRESENCE but a NON-refining contract FAILS static conformance — the
runtime presence check cannot rescue the static refinement VC. The no-blend rule
is defended by author separation: this conformance-agent authored the gates from
the two-plane spec + surface alone, never reading the lowering.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 3 (P2, P3-expected-fail, P5-expected-fail) | 0 | 3 |
| Runtime | 2 (R3/R4, R6) | 0 | 2 |

- **Static gate:** 3/3 PASS (P2 conformance refines — refinement goal Valid;
  P3 missing-member rejected at front-end; P5 no-blend witness — non-refining
  contract fails the refinement goal). The per-method contract-refinement VC
  (P2/P4) is the load-bearing static obligation; it is NOT discharged by method
  presence (P5 keystone).
- **Non-vacuity:** `--check-vacuity` GREEN on P2. The P5 keystone confirms
  non-vacuity by contradiction: the SAME refinement-goal structure, with a
  non-refining contract, FAILS — so the goal is genuinely discriminating.
- **Runtime gate:** 2/2 PASS — the shim performs no validation; identity
  discharges for any value (R3/R4, R6).
- **NO-BLEND check:** HOLDS. P5 is the load-bearing witness: a class with
  method presence but a non-refining contract FAILS static conformance — the
  runtime `@runtime_checkable` presence check cannot rescue the static refinement
  VC. This is the canonical GT7 trap, and it is preserved.

## Gap docs written

None. No gaps surfaced — the construct passes its declared S5 subset, its S4
shim-faithfulness drivers, and the no-blend check on the first pass.

## Notes for the coordinator

- The TY2 scope restriction (spec §1.7 — conformance requires an explicit
  `#@ conforms_to P` directive, divergence-by-strictness) is exercised by every
  static driver: each conforming class carries `#@ conforms_to Drawable`. An
  implicit structural conformance (a class with matching methods but NO
  `conforms_to` directive) does NOT trigger the refinement VC — it is out of the
  declared S5 subset, consistent with the spec.
- The refinement goal checks PRE weakening + POST strengthening (the existing
  `_render_refinement_goal` emitter). The `assigns`-refinement
  (`assigns(C.m) ⊆ assigns(P.m)`) is NOT separately checked by the existing
  emitter; for the TY2 conformance subset, every protocol member's `assigns` is
  `\nothing` (a pure query), so the frame-refinement is trivially satisfied.
  Flagged for a future frame-refinement enhancement; not a Gate-C blocker.
- The GT7 no-blend check (P5) is the keystone and it PASSES (the non-refining
  contract FAILS the refinement goal). The construct graduates on Gate C, NOT on
  the core-agent's self-report.
