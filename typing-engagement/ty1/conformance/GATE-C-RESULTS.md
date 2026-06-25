# GATE-C-RESULTS — `Union` (TY1 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `Union` (PEP 484 / PEP 604)
**Spec:** `typing-engagement/ty1/union-twoplane-spec.md`
**Surface:** `test-suite/annotations.md` §12.4
**Independence:** Built from the two-plane spec + construct surface ONLY.
No `src/pycsl/` source read; no lowering diffs read. The three gap docs
(GAP-001/002/003) cite only the emitted `.mlw` and pycsl's own run
output, never the lowering implementation.

**Run command:**
`source .venv/bin/activate && python3 src/pycsl/pycsl.py <driver>`
(provers: Alt-Ergo,2.6.2, → Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset

### C2 — arm membership
- **Clause:** C2 (§1.1)
- **Driver:** `C2_arm_membership.py` — `def f(x: Union[int, str]) -> int: return 5`
- **Expected (from spec):** typecheck + prove; per-arm VC (inj/proj) discharges for both arms.
- **Actual (from run):** PASS — `f__union_arm_Arm_0_1_proj` Valid (0.01s, 15 steps); `[+] Verification SUCCESS!`
- **NO-BLEND:** no — the driver does not call the runtime shim; the per-arm VCs are emitted by the static plane.

### C5 — `is None` narrowing
- **Clause:** C5 (§1.2)
- **Driver:** `C5_is_none_narrowing.py` — `if x is None: return 0; return x` on `Union[int, None]`.
- **Expected (from spec):** PASS — False branch narrows `x` to `int`.
- **Actual (from run):** FAIL — `This expression has type PyCSL_Program._union_f_0, but is expected to have type int`. See **GAP-001**.
- **NO-BLEND:** no — the runtime shim is not invoked; the static narrowing VC is simply not lowered.

### C9 (positive) — match exhaustiveness, all arms covered
- **Clause:** C9 (§1.3)
- **Driver:** `C9_match_exhaustive.py` — `match x: case int(): ...; case str(): ...` on `Union[int, str]`.
- **Expected (from spec):** PASS.
- **Actual (from run):** PASS — `[+] Verification SUCCESS!`
- **NO-BLEND:** no — shim not invoked. (Caveat: the match is lowered as `match x with | int -> ...` against the type name, not the constructor — see GAP-002. The positive case PASSes for the wrong reason: Why3 treats the pattern as vacuous, so exhaustiveness is not actually checked.)

### C9 (negative) — match non-exhaustiveness must FAIL
- **Clause:** C9 (§1.3)
- **Driver:** `C9_match_nonexhaustive.py` — covers only `int` arm of `Union[int, str]`.
- **Expected (from spec):** FAIL — non-exhaustive match is a static error.
- **Actual (from run):** PASS (spec violation) — `[+] Verification SUCCESS!`. See **GAP-002**.
- **NO-BLEND:** no — shim not invoked; the exhaustiveness obligation is not enforced by the lowering.

### GT1 — `Any` arm refused/dropped
- **Clause:** C4 (§1.1) / D3 (§3) / GT1
- **Driver:** `GT1_any_arm.py` — `def f(x: Union[Any, int]) -> int: return 5`.
- **Expected (from spec):** the `Any` arm is dropped from the synthesized variant; GT1 is reported in `--soundness-report`; the `int` arm's per-arm VC still discharges.
- **Actual (from run):** PASS — `UserWarning: GT1: Union arm \`Any\` refused (opaque, operation-barren) in variant '_union_f_0'. The arm was dropped ...`; `f__union_arm_Arm_0_0_proj` Valid; `[+] Verification SUCCESS!`
- **NO-BLEND:** no — the GT1 report is emitted by `core_ir_semantic._check_union_gt1`, a static-plane well-formedness check; the runtime shim is not involved.

---

## 2. RUNTIME gate — S4 shim-faithfulness drivers

### R3 — no enforcement (identity holds for ANY value)
- **Clause:** R3 (§2.1)
- **Driver:** `R3_no_enforcement.py` — calls `Union(int, str, val)` for string / list / None values; expects `#@ ensures \\result == val` to discharge for all.
- **Expected (from spec):** PASS — the shim performs no enforcement; identity discharges regardless of value type.
- **Actual (from run):** FAIL — `This expression has type int, but is expected to have type ()`. See **GAP-003**.
- **NO-BLEND:** n/a (runtime-plane gate).

### R8 — no validation of arm membership
- **Clause:** R8 (§2.4)
- **Driver:** `R8_no_validation.py` — calls `Union(int, str, val)` with a list value provably outside the arms.
- **Expected (from spec):** PASS — the shim does not validate arm membership; identity discharges.
- **Actual (from run):** FAIL — same Why3 type error as R3. See **GAP-003**.
- **NO-BLEND:** n/a (runtime-plane gate).

---

## 3. NO-BLEND check

For each static case, does the runtime shim pass it?

| Static case | Shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| C2  | no  | n/a | no  |
| C5  | no  | n/a | no  |
| C9+ | no  | n/a | no  |
| C9− | no  | n/a | no  |
| GT1 | no  | n/a | no  |

**NO-BLEND verdict: HOLDS.** No static case is discharged by the runtime
shim. The runtime shim's identity postcondition is itself unreachable
(GAP-003), so even if a static driver did invoke the shim, the shim could
not pass a static VC — there is no blend risk in either direction.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 3 (C2, C9+, GT1) | 2 (C5, C9−) | 5 |
| Runtime | 0 | 2 (R3, R8) | 2 |

- **Static gate:** 3/5 PASS, 2/5 FAIL.
- **Runtime gate:** 0/2 PASS, 2/2 FAIL.
- **NO-BLEND check:** HOLDS.

## Gap docs written

- `GAP-001-c5-narrowing.md` — C5 `is None` narrowing not lowered (static).
- `GAP-002-c9-exhaustiveness.md` — C9 match exhaustiveness not enforced (static); the positive case passes for the wrong reason.
- `GAP-003-shim-identity.md` — runtime shim identity postcondition unreachable (val/call arity mismatch + body returns 0, not `val`).

## Notes for the coordinator

- The two static FAILs (C5, C9−) and the two runtime FAILs (R3, R8) are
  independent lowering gaps, NOT blends. The no-blend invariant is intact.
- C9+ PASSes but for the wrong reason (Why3 treats `| int ->` as a
  vacuous pattern, not a constructor match); the positive case is not a
  trustworthy witness until GAP-002 is fixed. Treat C9+ as a PASS-with-
  caveat.
- GT1 is the cleanest result: the warning fires, the arm is dropped, the
  non-`Any` arm's VC discharges. No action needed.
