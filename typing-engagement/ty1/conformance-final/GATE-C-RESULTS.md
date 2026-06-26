# GATE-C-RESULTS — `Final` (TY1 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `Final` (PEP 591)
**Spec:** `typing-engagement/ty1/final-twoplane-spec.md`
**Surface:** `test-suite/annotations.md` §12.10, `src/pycsl_lib/typ/__init__.py` (the `Final` shim)
**Independence:** Built from the two-plane spec + construct surface ONLY.
No `src/pycsl/` source read; no lowering diffs read. The single runtime
shim read was `src/pycsl_lib/typ/__init__.py` (the *pycsl_lib* shim
surface, NOT the `src/pycsl/` lowering implementation) — permitted because
it is the runtime-plane public surface that the §12.10 spec names.

**Run command:**
`source .venv/bin/activate && python3 src/pycsl/pycsl.py <driver>`
(provers: Alt-Ergo,2.6.2, → Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset

### F1+ (positive) — module-level Final is write-once (declaration write)
- **Clause:** F1 (§1.1, S5 case (a)) — load-bearing write-once rule.
- **Driver:** `F1_write_once.py` — `x: Final[int] = 5` at module scope; `def f() -> int: return x` with `ensures \result == x`.
- **Expected (from spec):** PASS — the declaration write is at module scope (NOT a function body), so the syntactic write-site check (`_check_final` F1 arm) does not flag it; the read of `x` discharges the postcondition. The annotation's type is the inner type `T` (F3 — no narrowing).
- **Actual (from run):** PASS — `Sub-goal postcondition of goal f'vc. Prover result is: Valid (0.00s, 6 steps).`; `[+] Verification SUCCESS! All contracts formally proven.`
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the VC is the static-plane postcondition on a read.

### F1- (negative) — reassigning a module-level Final name is a static error
- **Clause:** F1 (§1.1, S5 case (b)) — a declaration followed by a later reassignment of the same name must be rejected.
- **Driver:** `F1_reassignment.py` — `x: Final[int] = 5; def f() -> int: x = 6; return x`.
- **Expected (from spec):** FAIL (PIPELINE ERROR) — the reassignment of `x` inside a function body is a disallowed write site; the syntactic write-site check (`_check_final` F1 arm) raises `PyCSLSemanticError` at the semantic-analysis stage, before any WhyML is emitted. The runtime would execute the reassignment (FR3); the rejection is static-plane only (FD1 divergence).
- **Actual (from run):** FAIL (PIPELINE ERROR) — `[!] PIPELINE ERROR: Final: cannot reassign Final name 'x' in function 'f' (F1 — write-once at declaration; PEP 591). The name is declared `Final` at module/class scope and may be written only at its declaration.` No WhyML is emitted.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the rejection is at the static-plane write-site check.

### F2+ (positive) — instance-attribute Final: write inside __init__ is OK
- **Clause:** F2 (§1.2, S5 case (a)) — load-bearing `__init__`-only write rule.
- **Driver:** `F2_init_write.py` — `class C: attr: Final[int]; def __init__(self): self.attr = 0`; `def get(c: C) -> int: return c.attr` with `ensures \result == c.attr`.
- **Expected (from spec):** PASS — the class-body declaration `attr: Final[int]` is NOT a write (F2a — it establishes the attribute's existence and its `Final` write-policy); the first (and only) permitted write happens in `__init__`, which is within the allowed perimeter. The read of `c.attr` discharges the postcondition. The attribute's type is `int` (F3).
- **Actual (from run):** PASS — `Sub-goal postcondition of goal get'vc. Prover result is: Valid (0.01s, 6 steps).`; `[+] Verification SUCCESS! All contracts formally proven.`
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the VC is the static-plane postcondition on a read.

### F2- (negative) — writing a Final instance attribute outside __init__ is an error
- **Clause:** F2 (§1.2, S5 case (b)) — a write to `self.attr` in a method of `C` other than `__init__` must be rejected.
- **Driver:** `F2_write_outside_init.py` — `class C: attr: Final[int]; def __init__(self): self.attr = 0; def m(self) -> int: self.attr = 1; return self.attr`.
- **Expected (from spec):** FAIL (PIPELINE ERROR) — the write to `self.attr` inside `m` (not `__init__`) is a disallowed write site; the syntactic write-site check (`_check_final` F2 arm) raises `PyCSLSemanticError` at the semantic-analysis stage, before any WhyML is emitted. The runtime would execute the write (FR3); the rejection is static-plane only (FD1 divergence).
- **Actual (from run):** FAIL (PIPELINE ERROR) — `[!] PIPELINE ERROR: Final: cannot write Final instance attribute 'self.attr' in function 'c__m' (F2 — __init__-only writes; PEP 591). The attribute is declared `Final` and may be written only in the declaring class's __init__.` No WhyML is emitted.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the rejection is at the static-plane write-site check.

### F3 — Final does NOT narrow or refine the type
- **Clause:** F3 (§1.3) — load-bearing no-narrowing rule.
- **Driver:** `F3_no_narrowing.py` — `x: Final[int] = 5; def f() -> int: return x + 1` with `ensures \result == 6`.
- **Expected (from spec):** PASS — the type of `x` is `int` (NOT `Literal[5]`); `Final` adds the write-restriction (F1), NOT a value-set refinement. Arithmetic `x + 1` is well-typed and `\\result == 6` discharges. No narrowing VC is emitted.
- **Actual (from run):** PASS — `Sub-goal postcondition of goal f'vc. Prover result is: Valid (0.00s, 14 steps).`; `[+] Verification SUCCESS! All contracts formally proven.`
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the VC is the static-plane arithmetic postcondition. The 14-step count (vs 6 for a bare `return x`) is consistent with the `+ 1` arithmetic lowering; no narrowing obligation is emitted.

---

## 2. RUNTIME gate — S4 shim-faithfulness drivers

### FR3 — no enforcement (the Final shim is identity)
- **Clause:** FR3 (§2.1) — the runtime does NOT enforce the write-restriction.
- **Driver:** `FR3_no_enforcement.py` — calls `Final(int, None, val)` from `pycsl_lib.typ` with an int, a string, and a list; expects `#@ ensures \result == val` to discharge for all. The driver also performs a runtime reassignment (`v = 5; v = 6`) — exactly the case F1 rejects statically — and expects the shim to NOT enforce write-once.
- **Expected (from spec):** PASS — the shim performs no enforcement; identity discharges regardless of value type or write-policy violation (FR3 — a reassignment at runtime is allowed).
- **Actual (from run):** PASS — three VCs all `Valid (0.01s, 6 steps)` (`call_int'vc`, `call_list'vc`, `call_string'vc`); `[+] Verification SUCCESS! All contracts formally proven.` The shim's identity postcondition discharges for an int, a string, and a list — no enforcement, no descriptor intervention.
- **NO-BLEND:** n/a (runtime-plane gate). The shim performs no validation; a reassignment at runtime succeeds (FR3). The static write-policy is NOT discharged by the shim (it is a semantic check, invisible to the runtime).

### FR6 — Final is NOT a distinct runtime class / no descriptor
- **Clause:** FR6 (§2.3) — the shim must not introduce a descriptor or write-guard.
- **Driver:** `FR6_no_descriptor.py` — `identity_once` calls `Final(int, None, val)` once; `identity_twice` calls it twice with the same `val` and returns the second result. Both carry `#@ ensures \result == val`.
- **Expected (from spec):** PASS — the identity postcondition discharges for both; no descriptor intervenes. A descriptor that raised on a second write (the canonical FD2 blend) would block `identity_twice` and the postcondition would not discharge.
- **Actual (from run):** PASS — `identity_once'vc: Valid (0.01s, 6 steps)`; `identity_twice'vc: Valid (0.01s, 20 steps)`; `[+] Verification SUCCESS! All contracts formally proven.` Two successive shim calls discharge identity — no descriptor blocks the second call.
- **NO-BLEND:** n/a (runtime-plane gate). The shim introduces no distinct `Final` runtime class, no write-guard descriptor, no enforcement hook (FR6).

---

## 3. NO-BLEND check (sharpened for Final — FD2)

### NOBLEND_FD2 — the runtime shim must NOT rescue a static write-policy violation
- **Clause:** FD2 (§3) sharpening F1 (§1.1) — the load-bearing Final no-blend divergence.
- **Driver:** `NOBLEND_FD2_shim_does_not_rescue.py` — `x: Final[int] = 5` at module scope; `def g(val) -> int: x = 6; return FinalShim(int, None, val)` with `ensures \result == 6`. The function BOTH (a) reassigns the module-level `Final` name `x` inside a function body (a static error per F1) AND (b) invokes the runtime `Final` shim.
- **Expected (from spec):** FAIL (PIPELINE ERROR) — the static write-site check (`_check_final` F1 arm) must flag the reassignment of `x` in `g`, INDEPENDENTLY of whether the `Final` shim is invoked elsewhere in the same function. The runtime shim's identity postcondition must NOT "rescue" the static write-policy violation: the static VC is the write-policy check (does a disallowed write site exist?), a syntactic property of the program, discharged independently of any runtime behaviour. If this driver PASSES, the runtime shim is blending the planes (FD2 violation): the static write-policy is being discharged by the runtime shim's identity postcondition instead of by the syntactic write-site check.
- **Actual (from run):** FAIL (PIPELINE ERROR) — `[!] PIPELINE ERROR: Final: cannot reassign Final name 'x' in function 'g' (F1 — write-once at declaration; PEP 591). The name is declared `Final` at module/class scope and may be written only at its declaration.` No WhyML is emitted. The static write-site check fires DESPITE the `from pycsl_lib.typ import Final as FinalShim` import and the `FinalShim(int, None, val)` call inside `g` — the shim does NOT rescue the static violation.
- **NO-BLEND verdict:** HOLDS. The static write-policy check (F1) fires correctly on the reassignment of `x` in `g`, regardless of the runtime shim's presence in the same function. The runtime `Final` shim's identity postcondition does NOT substitute for the static write-site check. There is no plane blending.

### Cross-check table

| Static case | Shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| F1+   | no | n/a | no |
| F1−   | no | n/a | no |
| F2+   | no | n/a | no |
| F2−   | no | n/a | no |
| F3    | no | n/a | no |
| FD2   | YES (imported + called in `g`) | n/a (the static write-site check correctly fires BEFORE the shim could discharge anything) | no |

**NO-BLEND verdict: HOLDS.** No static case is discharged by the runtime
shim. The FD2 probe is the strongest possible test: the driver
DELIBERATELY invokes the `Final` shim inside the same function that
commits the static write-policy violation. The static write-site check
fires at the semantic-analysis stage (before any WhyML is emitted, before
the shim's identity postcondition could be appealed to), so the shim
cannot "rescue" the violation. The static plane's write-policy and the
runtime plane's no-enforcement are carried as SEPARATE contracts, as
FD2/FD3 require.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 3 (F1+, F2+, F3) | 2 (F1−, F2− — expected FAIL) | 5 |
| Runtime | 2 (FR3, FR6) | 0 | 2 |
| NO-BLEND | 1 (FD2 — expected FAIL) | 0 | 1 |

- **Static gate:** 5/5 conformance — all five cases behave as the spec requires. The three positive cases (F1+, F2+, F3) PASS; the two negative cases (F1−, F2−) correctly FAIL at the semantic-analysis stage with `PyCSLSemanticError` raised by the syntactic write-site check (`_check_final`), before any WhyML is emitted. The error messages cite the correct clause (F1 / F2) and PEP 591.
- **Runtime gate:** 2/2 PASS — the `Final` shim is identity (`#@ ensures \result == val`), performs no validation (FR3), introduces no descriptor (FR6). The identity postcondition discharges for int/string/list (FR3) and for two successive calls (FR6 — no descriptor blocks the second write).
- **NO-BLEND check:** HOLDS. The FD2 probe correctly FAILs: the static write-site check fires on the reassignment of `x` in `g` DESPITE the `Final` shim being imported and invoked in the same function. The runtime shim's identity postcondition does NOT substitute for the static write-policy check.

## Gap docs written

None. `Final` is fully sound: the write-restriction is a syntactic
write-site check (decidable by construction; the two-plane spec §4
confirms full soundness). The static gate conforms 5/5; the runtime gate
conforms 2/2; the NO-BLEND probe HOLDS. No GT gap is tagged for `Final`
— consistent with the two-plane spec's "No GT gap is tagged for `Final`"
claim (§4) and the §12.10 surface's "No GT gap" claim.

## Notes for the coordinator

- All five static cases conform to the two-plane spec: F1 positive/negative, F2 positive/negative, F3 no-narrowing. No static lowering gap was found. The error messages produced by `_check_final` are clause-accurate (cite F1/F2 and PEP 591).
- The two runtime PASSes are the cleanest result for `Final`: unlike the `Literal`/`Union` side (which inherits the GAP-003 shim-identity seam mismatch), the `Final` shim's identity postcondition discharges cleanly for every value type and for two successive calls — confirming the shim introduces no descriptor (FR6) and performs no enforcement (FR3).
- The NO-BLEND verdict is the load-bearing result: the FD2 probe deliberately invokes the `Final` shim inside the same function that commits the F1 write-policy violation, and the static write-site check STILL fires (at semantic analysis, before WhyML emission). The runtime shim does NOT rescue the static violation — the two planes are carried as separate contracts.
- This matches the reference corpus (tests 0734–0737) and the §12.10 surface claim that `Final` is "fully sound — no GT gap".
