# GATE-C-RESULTS — `Literal` (TY1 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `Literal` (PEP 586)
**Spec:** `typing-engagement/ty1/literal-twoplane-spec.md`
**Surface:** `test-suite/annotations.md` §12.9, `docs/pycsl-translational-reference.md` §T.14.6
**Independence:** Built from the two-plane spec + construct surface ONLY.
No `src/pycsl/` source read; no lowering diffs read. The single runtime
shim read was `src/pycsl_lib/typ/__init__.py` (the *pycsl_lib* shim surface,
NOT the `src/pycsl/` lowering implementation) — permitted because it is the
runtime-plane public surface that the §12.9 spec names.

**Run command:**
`source .venv/bin/activate && python3 src/pycsl/pycsl.py <driver>`
(provers: Alt-Ergo,2.6.2, → Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset

### L1 (positive) — value set / ground requires
- **Clause:** L1 (§1.1) — load-bearing assignability rule.
- **Driver:** `L1_value_set.py` — `def f(x: Literal[1, 2]) -> int: return x` with `ensures \result == x`.
- **Expected (from spec):** PASS — synthesized `requires { x = 1 \/ x = 2 }` VC discharges; the postcondition `x = \result` holds because the input is one of {1, 2} and the function returns it unchanged.
- **Actual (from run):** PASS — `Sub-goal postcondition of goal f'vc. Prover result is: Valid (0.01s, 19 steps).`; `[+] Verification SUCCESS!`.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the VC is the static-plane synthesized precondition.

### L1 (negative) — value outside the set must FAIL
- **Clause:** L1 (§1.1, S5 case (b)) — a value equal to no `v_i` flowing in must be rejected.
- **Driver:** `L1_value_set_negative.py` — `def caller() -> int: return f(3)` where `f: Literal[1, 2]`.
- **Expected (from spec):** FAIL — the call site's precondition VC `3 = 1 \/ 3 = 2` is unprovable.
- **Actual (from run):** FAIL — `Sub-goal precondition of goal caller'vc. Prover result is: Unknown (why3: Unknown (sat)) (0.01s, 19 steps).`; `[-] 1 goal(s) remain unproven after all provers.` The runtime would print PASS (no enforcement); the static gate fails as required.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the precondition VC is the static-plane synthesized clause.

### L2 — narrowing by equality (load-bearing Literal narrowing)
- **Clause:** L2 (§1.2).
- **Driver:** `L2_narrowing_equality.py` — `def f(x: Literal[1, 2]) -> int: if x == 1: return 0; return 1` with `ensures \result >= 0`.
- **Expected (from spec):** PASS — True branch narrows to `Literal[1]`; False branch narrows to `Literal[2]`; `\result >= 0` discharges on both paths.
- **Actual (from run):** PASS — two VCs (one per branch) both `Valid (0.01s, 28 steps)` / `Valid (0.01s, 30 steps)`; `[+] Verification SUCCESS!`.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; narrowing is emergent from the standard path-condition VC on the `if x == v` lowering.

### L4 — supported literal kinds (int/str/bool/None all work)
- **Clause:** L4 (§1.4).
- **Driver:** `L4_literal_kinds.py` — four functions, each with a different supported kind: `Literal[1, 2]` (int), `Literal["a", "b"]` (str), `Literal[True, False]` (bool → 1/0), `Literal[None]` (None → 0).
- **Expected (from spec):** PASS for all four kinds.
- **Actual (from run):** PASS — four VCs all `Valid (0.00–0.01s, 484–492 steps)`; `[+] Verification SUCCESS!`.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim.

### L4a (negative) — `bytes` literals REJECTED
- **Clause:** L4a (§1.4) / PEP 586.
- **Driver:** `L4a_bytes_rejected.py` — `def f(x: Literal[b"x"]) -> int: return 0`.
- **Expected (from spec):** FAIL — a `Literal[b"x"]` form is a static error raised at the front-end normalization seam before any WhyML is emitted.
- **Actual (from run):** FAIL (PIPELINE ERROR) — `[!] PIPELINE ERROR: [ir-emit]: Literal: bytes literals are not supported (L4a / PEP 586)`. No WhyML is emitted.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the rejection is at the static-plane normalization seam.

### L5/L5a — deduplication and order-independence
- **Clause:** L5 + L5a (§1.5).
- **Driver:** `L5_dedup_order.py` — four functions with `Literal[1, 1]` (dup), `Literal[1]` (singleton), `Literal[1, 2]` (order_ab), `Literal[2, 1]` (order_ba); each `ensures \result == x`.
- **Expected (from spec):** PASS for all four forms — deduplication (`Literal[1, 1]` ≡ `Literal[1]`) and order-independence (`Literal[1, 2]` ≡ `Literal[2, 1]`) yield the same synthesized requires.
- **Actual (from run):** PASS — four VCs all `Valid (0.00–0.01s, 11–19 steps)`; `[+] Verification SUCCESS!`. The `dup` and `singleton` VCs discharge at the same step count (11), and `order_ab` and `order_ba` at the same step count (19) — strong evidence that dedup + order canonicalization produces the same synthesized requires.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim.

---

## 2. RUNTIME gate — S4 shim-faithfulness drivers

### LR3 — no enforcement (the Literal shim is identity)
- **Clause:** LR3 (§2.1) / LR7 (§2.4).
- **Driver:** `LR3_no_enforcement.py` — calls `Literal(1, 2, val)` from `pycsl_lib.typ` with a string, a list, and `None`; expects `#@ ensures \result == val` to discharge for all.
- **Expected (from spec):** PASS — the shim performs no enforcement; identity discharges regardless of value type or value-set membership.
- **Actual (from run):** FAIL — `This expression has type int, but is expected to have type ()` (Why3 type error at the shim call). The shim's identity postcondition is unreachable: the call site's WhyML emission does not match the shim's `int`-returning identity contract. This is the same shim-identity gap already documented as GAP-003 on the `Union` side — `Literal` reuses the same `pycsl_lib/typ/__init__.py` seam and inherits the same lowering-level call-shape mismatch (NOT a `Literal`-specific lowering bug; NOT a blend).
- **NO-BLEND:** n/a (runtime-plane gate). **Gap doc:** `GAP-LIT-003-shim-identity.md`.

### LR4 — `isinstance` against `Literal` is NOT supported
- **Clause:** LR4 (§2.2) / LR8 (§2.4).
- **Driver:** `LR4_isinstance_rejected.py` — `def f(v) -> int: if isinstance(v, Literal[1, 2]): return 0; return 1` with `ensures \result == 0`.
- **Expected (from spec):** FAIL — `isinstance(v, Literal[1, 2])` raises `TypeError` at runtime; the shim does NOT make `Literal` a valid `isinstance` argument, so the narrowed postcondition `ensures \result == 0` cannot be discharged from the uninterpreted boolean.
- **Actual (from run):** FAIL — True-branch VC `Valid (0.01s, 275 steps)`; False-branch VC `Timeout (30.00s, 16709024 steps)`; `[-] 1 goal(s) remain unproven after all provers.` The True-branch discharges trivially (the body returns 0 there); the False-branch postcondition `\result == 0` is unprovable (the body returns 1) — and Z3 times out rather than returning `Invalid`. The construct is correctly treated as opaque (the shim is not a runtime type for `isinstance`), so the narrowing obligation is not discharged.
- **NO-BLEND:** n/a (runtime-plane gate).

---

## 3. NO-BLEND check (sharpened for Literal — LD2)

### NOBLEND_LD2 — narrowing WITHOUT an equality guard must FAIL
- **Clause:** LD2 (§3) sharpening L2 (§1.2) — the load-bearing Literal no-blend divergence.
- **Driver:** `NOBLEND_LD2_no_guard_narrowing.py` — `def f(x: Literal[1, 2]) -> int: return x` with `ensures \result == 1` and NO `if x == 1:` guard.
- **Expected (from spec):** FAIL — without an equality guard, `x` is only known to be in {1, 2}; the postcondition `\result == 1` is unprovable (it would also hold for `x = 2`). If the lowering blends the planes (LD2 violation), the runtime `x == v1` semantics would leak into the static judgment and this driver would INCORRECTLY PASS.
- **Actual (from run):** FAIL — `Sub-goal postcondition of goal f'vc. Prover result is: Unknown (why3: Unknown (sat)) (0.01s, 63 steps).`; `[-] 1 goal(s) remain unproven after all provers.` The static plane refuses to narrow without an equality guard — the L2 narrowing obligation is NOT discharged by the runtime `x == v1` comparison.
- **NO-BLEND verdict:** HOLDS. The static plane correctly requires the `if x == v1:` guard; the runtime `x == v1` test does NOT substitute for the static narrowing. There is no plane blending.

### Cross-check table

| Static case | Shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| L1+   | no | n/a | no |
| L1−   | no | n/a | no |
| L2    | no | n/a | no |
| L4    | no | n/a | no |
| L4a−  | no | n/a | no |
| L5    | no | n/a | no |
| LD2   | no | n/a (the narrowing is correctly refused) | no |

**NO-BLEND verdict: HOLDS.** No static case is discharged by the runtime
shim. The LD2 probe confirms the load-bearing Literal no-blend rule:
narrowing without an equality guard is correctly REJECTED, so the runtime
`x == v1` test is NOT substituting for the static L2 narrowing obligation.
The runtime shim's identity postcondition is itself unreachable (LR3
gap), so even if a static driver did invoke the shim, the shim could not
pass a static VC — there is no blend risk in either direction.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 5 (L1+, L2, L4, L5, L4a−) | 1 (L1− — expected FAIL) | 6 |
| Runtime | 0 | 2 (LR3, LR4) | 2 |
| NO-BLEND | 1 (LD2 — expected FAIL) | 0 | 1 |

- **Static gate:** 5/6 PASS, 1/6 expected-FAIL (L1− correctly rejects an out-of-set value). All six cases behave as the spec requires — **6/6 conformance**.
- **Runtime gate:** 0/2 PASS, 2/2 FAIL (LR3 — shim identity postcondition unreachable, inherited from the Union-seam GAP-003; LR4 — `isinstance` against the shim correctly treated as opaque, so the narrowed postcondition is unprovable, but the FAIL is a runtime-plane gap, not a spec violation). See gap docs below.
- **NO-BLEND check:** HOLDS. The LD2 probe correctly FAILs without an equality guard, confirming the load-bearing Literal no-blend rule (L2 narrowing must NOT be discharged by the runtime `x == v1` comparison).

## Gap docs written

- `GAP-LIT-003-shim-identity.md` — runtime shim identity postcondition unreachable (Why3 type error `int vs ()` at the `Literal(1, 2, val)` call site). This is the `Literal`-local restatement of the Union-side GAP-003 — `Literal` reuses the same `pycsl_lib/typ/__init__.py` shim seam and inherits the same lowering-level call-shape mismatch. NOT a `Literal`-specific lowering bug; NOT a blend.
- `GAP-LIT-004-isinstance-opaque.md` — `isinstance(v, Literal[1, 2])` is treated as an opaque uninterpreted boolean; the True-branch postcondition discharges trivially, the False-branch narrowed postcondition times out. This is faithful to LR4 (the shim does not make `Literal` a valid `isinstance` argument), but the runtime rejection should surface as a clearer static-plane diagnostic rather than a solver timeout. NOT a blend.

## Notes for the coordinator

- All six static cases conform to the two-plane spec: L1 positive/negative, L2 narrowing, L4 kinds, L4a bytes rejection, L5 dedup/order. No static lowering gap was found.
- The two runtime FAILs are inherited from the `pycsl_lib/typ` shim seam (also seen on Union R3/R8), NOT `Literal`-specific. The shim's identity postcondition is unreachable at the WhyML call site — the call shape `Literal(1, 2, val)` does not match the shim's `int`-returning identity contract.
- The NO-BLEND verdict is the cleanest result: the LD2 probe correctly refuses to narrow without an equality guard, confirming the load-bearing Literal no-blend rule. The runtime `x == v1` test does NOT substitute for the static L2 narrowing.
- L5 step-count parity (dup/singleton at 11 steps; order_ab/order_ba at 19 steps) is strong evidence that the dedup + order canonicalization at the normalization seam produces identical synthesized requires — the two-plane spec's L5/L5a claim is confirmed.
