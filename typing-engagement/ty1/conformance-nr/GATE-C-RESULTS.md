# GATE-C-RESULTS — `NoReturn` (TY1 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `NoReturn` (PEP 484)
**Spec:** `typing-engagement/ty1/noreturn-twoplane-spec.md`
**Surface:** `test-suite/annotations.md` §12.11, `src/pycsl_lib/typ/__init__.py` (the `NoReturn` shim)
**Independence:** Built from the two-plane spec + construct surface ONLY.
No `src/pycsl/` source read; no lowering diffs read. The single runtime
shim read was `src/pycsl_lib/typ/__init__.py` (the *pycsl_lib* shim
surface, NOT the `src/pycsl/` lowering implementation) — permitted because
it is the runtime-plane public surface that the §12.11 spec names (it
defines `NoReturn = None`, the introspectable alias object, NR-R1/NR-R4).

**Run commands:**
- Static: `source .venv/bin/activate && python3 src/pycsl/pycsl.py <driver>`
- Vacuity: `... pycsl.py <driver> --check-vacuity`
- Runtime: `python3 <driver>` (plain CPython — the runtime plane is not a pycsl VC)
- (provers: Alt-Ergo,2.6.2, → Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset

### NR1 — `-> NoReturn` lowers to `ensures { false }` (positive)
- **Clause:** NR1 (§1.0) — the load-bearing static clause: a `NoReturn` function carries the `false` postcondition; the body `raise Exception()` has no normal-exit path, so `false` discharges by path-absence (not by an inconsistent context).
- **Driver:** `NR1_noreturn_raises.py` — `def f() -> NoReturn: raise Exception()`.
- **Expected (from spec):** PASS — the `ensures { false }` VC discharges because the body raises (NR2a satisfied); no normal exit exists.
- **Actual (from run):** PASS — `[+] Verification SUCCESS! All contracts formally proven.`
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the VC is the static-plane false-postcondition on a raising body.

### NR2a — a NoReturn body that returns normally is a static ERROR (negative)
- **Clause:** NR2a (§1.0) — a `NoReturn` body must support divergence (raise or diverge); a bare `return` is a normal-exit path, so the `false` postcondition is genuinely unprovable (wrong, not vacuous).
- **Driver:** `NR2a_noreturn_returns.py` — `def f() -> NoReturn: return 1`.
- **Expected (from spec):** FAIL (PIPELINE ERROR) — the body-supports-divergence check (`_check_noreturn` / `_check_diverges`) rejects the `return` at semantic analysis, before any WhyML is emitted. The runtime would execute the `return` (NR-R3); the rejection is static-plane only (NR-D1).
- **Actual (from run):** FAIL (PIPELINE ERROR) — ``[!] PIPELINE ERROR: `-> NoReturn` on function 'f' is not justified: its body contains a `return` statement (a normal-exit path). A NoReturn function must never return normally — every path must raise or diverge (NR2a / PEP 484). ...`` No WhyML is emitted.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the rejection is at the static body-divergence check.

### NR3 — a statement after a NoReturn call is dead code (negative)
- **Clause:** NR3 (§1.1) — the callee's `false` postcondition (NR1) makes the continuation path contradictory; the successor is statically unreachable and is reported as dead code (a SOUND dead branch — not vacuity).
- **Driver:** `NR3_dead_successor.py` — `f() -> NoReturn` raises; `caller` does `f(); x = 1; return x`.
- **Expected (from spec):** FAIL (PIPELINE ERROR) — the dead-successor check (`_check_noreturn_successors`) flags the statement following the `f()` call as unreachable at semantic analysis.
- **Actual (from run):** FAIL (PIPELINE ERROR) — ``[!] PIPELINE ERROR: Dead code in function 'caller': this statement follows a call to a `NoReturn` function, which never returns normally (NR3 / PEP 484). The continuation path is unreachable. ...`` No WhyML is emitted.
- **NO-BLEND:** n/a — driver does not invoke the runtime shim; the rejection is at the static dead-successor check.

### NR4a — THE LOAD-BEARING CLAUSE, half A — a declared-NoReturn function is EXEMPTED from the vacuity probe
- **Clause:** NR4 (§1.2 — the soundness keystone, half A) — a `NoReturn` function ALREADY HAS a `false` postcondition by design (NR1); it is INDISTINGUISHABLE from a vacuous one under the gate's probe and would be false-positively flagged. The gate MUST EXEMPT it, KEYED ON THE `-> NoReturn` ANNOTATION (the IR `is_noreturn` flag), NOT on the inferred postcondition.
- **Driver:** `NR4a_noreturn_exempt.py` — `def f() -> NoReturn: raise Exception()`, run with `--check-vacuity`.
- **Expected (from spec):** PASS — the file verifies AND the non-vacuity gate does NOT flag `f` (it is exempted via the `is_noreturn` IR flag).
- **Actual (from run):** PASS — `[+] Verification SUCCESS! All contracts formally proven.` The non-vacuity gate emitted NO `NON-VACUITY GATE FAILED` line; `f` was exempted.
- **NO-BLEND:** n/a (static-plane gate). The exemption is keyed on the declared annotation, per NR4 mechanism item 1; the runtime shim is not invoked by this driver.

### NR4b — THE LOAD-BEARING CLAUSE, half B — a genuinely-vacuous function (NO NoReturn) is STILL flagged
- **Clause:** NR4 (§1.2 — the soundness keystone, half B) — the exemption is keyed on the ANNOTATION, not on the inferred `false` postcondition; the latter would exempt every genuinely-vacuous function, defeating the gate. A function with an inconsistent context (contradictory preconditions `requires x > 0` AND `requires x < 0`) and NO `NoReturn` annotation must STILL be probed and flagged.
- **Driver:** `NR4b_genuinely_vacuous_flagged.py` — `def g(x) -> int` with `requires x > 0; requires x < 0; ensures \result == x; return x`, run with `--check-vacuity`.
- **Expected (from spec):** FAIL (VACUITY GATE FAILED) — the contradictory preconditions make the context inconsistent, the injected `false`-goal proves Valid, and `g` is flagged as vacuously green. The NoReturn exemption does NOT extend to it (no `-> NoReturn` annotation).
- **Actual (from run):** FAIL (VACUITY GATE FAILED) — `Sub-goal postcondition of goal g'vc. Prover result is: Valid (0.00s, 32 steps).`; `[-] NON-VACUITY GATE FAILED: ... g (proves \`ensures false\`) ...`; `[-] Verification FAILED (vacuous proof).`
- **NO-BLEND:** n/a (static-plane gate). The exemption is correctly NARROW: it spares the declared-`NoReturn` function (NR4a) but NOT the genuinely-vacuous function (NR4b). The two halves together confirm the exemption is keyed on the annotation, not on the inferred postcondition.

---

## 2. RUNTIME gate — S4 shim-faithfulness drivers

### NR-R3 — no enforcement (the NoReturn shim is identity/introspection, not a check)
- **Clause:** NR-R3 (§2.1 — the central negative sentence) — the runtime does NOT check that a `NoReturn`-annotated function diverges or raises. A function annotated `-> NoReturn` that RETURNS a value (a program bug) returns at runtime without error; the runtime does not raise, warn, or trap. (S3 central negative sentence; resolved by S4 — `NoReturn` is an introspectable alias object.)
- **Driver:** `NRR3_no_enforcement.py` — `from pycsl_lib.typ import NoReturn` (which is `None` — the alias object, NR-R1/NR-R4); `def f() -> NoReturn: return 1`. Run with plain `python3` (NOT pycsl — the runtime plane is not a VC).
- **Expected (from spec):** PASS (at runtime) — `f()` returns 1, no error raised by the shim. The shim performs no enforcement of divergence.
- **Actual (from run):** PASS — `python3 NRR3_no_enforcement.py` printed `PASS`; `f()` returned 1 and `assert NoReturn is None` held. The shim did not trap the returning `NoReturn` function.
- **NO-BLEND:** n/a (runtime-plane gate). The shim constructs the introspectable alias object and performs no validation of the function's control flow (NR-R4). The static plane would reject this function (NR2a); the runtime plane does not.

---

## 3. NO-BLEND check (sharpened for NoReturn — NR-D2)

### NOBLEND_NRD2 — the runtime shim must NOT rescue a static false-postcondition violation
- **Clause:** NR-D2 (§3 — the no-blend rule) — the static plane's `false` postcondition (NR1) MUST NOT be discharged by the runtime's behaviour. The static proof requires a proof-time argument (NR2a — a diverges-supporting body) that every normal-exit path is absent; the runtime must not be allowed to "pass" the static false-postcondition.
- **Driver:** `NOBLEND_NRD2_shim_does_not_rescue.py` — `from pycsl_lib.typ import NoReturn as NoReturnShim`; `def f() -> NoReturn: return 1` (a static NR2a violation — the body returns normally) AND `g` references the runtime `NoReturnShim` alias object. The driver DELIBERATELY invokes the runtime shim's surface in the same module that commits the static NR2a violation.
- **Expected (from spec):** FAIL (PIPELINE ERROR) — the static body-supports-divergence check (`_check_noreturn`) must flag the `return` in `f`, INDEPENDENTLY of whether the `NoReturn` shim is imported/referenced elsewhere in the module. The runtime shim's alias-object behaviour must NOT "rescue" the static NR2a violation: the static VC is the body-divergence check (does a normal-exit path exist?), a syntactic property of the body, discharged independently of any runtime behaviour. If this driver PASSES, the runtime shim is blending the planes (NR-D2 violation).
- **Actual (from run):** FAIL (PIPELINE ERROR) — ``[!] PIPELINE ERROR: `-> NoReturn` on function 'f' is not justified: its body contains a `return` statement (a normal-exit path). A NoReturn function must never return normally — every path must raise or diverge (NR2a / PEP 484). ...`` No WhyML is emitted. The static body-divergence check fired DESPITE the `from pycsl_lib.typ import NoReturn as NoReturnShim` import and the `NoReturnShim` reference in `g` — the shim did NOT rescue the static violation.
- **NO-BLEND verdict:** HOLDS. The static body-divergence check (NR2a) fires correctly on the `return` in `f`, regardless of the runtime shim's presence in the same module. The runtime `NoReturn` shim's alias-object behaviour does NOT substitute for the static body-divergence check. There is no plane blending.

### Cross-check table

| Static case | Shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| NR1   | no | n/a | no |
| NR2a  | no | n/a | no |
| NR3   | no | n/a | no |
| NR4a  | no | n/a (gate exempts via `is_noreturn` flag, not via the shim) | no |
| NR4b  | no | n/a (genuinely-vacuous function has no NoReturn; gate flags it) | no |
| NR-D2 | YES (imported + referenced in `g`) | n/a (the static body-divergence check correctly fires BEFORE the shim could discharge anything) | no |

**NO-BLEND verdict: HOLDS.** No static case is discharged by the runtime
shim. The NR-D2 probe is the strongest possible test: the driver
DELIBERATELY imports and references the `NoReturn` shim in the same module
that commits the static NR2a body-divergence violation. The static
body-divergence check fires at the semantic-analysis stage (before any
WhyML is emitted, before the shim's alias-object behaviour could be
appealed to), so the shim cannot "rescue" the violation. The static
plane's false-postcondition/body-divergence obligation and the runtime
plane's no-enforcement are carried as SEPARATE contracts, as NR-D2/NR-D4
require.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 2 (NR1, NR4a) | 3 (NR2a, NR3, NR4b — expected FAIL) | 5 |
| Runtime | 1 (NR-R3) | 0 | 1 |
| NO-BLEND | 1 (NR-D2 — expected FAIL) | 0 | 1 |

- **Static gate:** 5/5 conformance — all five cases behave as the spec requires. The two positive cases (NR1, NR4a) PASS; the three negative cases (NR2a, NR3, NR4b) correctly FAIL at the semantic-analysis / vacuity-gate stage. The NR2a and NR3 error messages cite the correct clause (NR2a / NR3) and PEP 484.
- **NR4 keystone:** HOLDS on BOTH halves. NR4a — a declared-`NoReturn` function PASSES `--check-vacuity` (exempted via the `is_noreturn` IR flag, keyed on the annotation). NR4b — a genuinely-vacuous function (contradictory preconditions, NO `NoReturn`) is STILL FLAGGED by `--check-vacuity`. The exemption is correctly NARROW: keyed on the declared `-> NoReturn` annotation, NOT on the inferred `false` postcondition (the latter would exempt every genuinely-vacuous function and defeat the gate).
- **Runtime gate:** 1/1 PASS — the `NoReturn` shim is the introspectable alias object (`NoReturn = None`, NR-R1/NR-R4) with NO enforcement (NR-R3). A `NoReturn`-annotated function that returns at runtime runs without error; the shim performs no validation of the function's control flow.
- **NO-BLEND check:** HOLDS. The NR-D2 probe correctly FAILs: the static body-divergence check fires on the `return` in `f` DESPITE the `NoReturn` shim being imported and referenced in the same module. The runtime shim's alias-object behaviour does NOT substitute for the static body-divergence check.

## Gap docs written

None. `NoReturn` is SOUND: the `false` postcondition is a genuine proof
obligation (the function must be shown to raise or diverge — NR2a rejects
a body that returns normally), not an unsoundness. The NR4 vacuity-gate
exemption is a gate-precision concern (it prevents a false POSITIVE —
flagging a faithful `NoReturn` function — not a false negative), and it is
correctly keyed on the declared annotation so it does not extend to
genuinely-vacuous functions (NR4b confirms). No GT gap is tagged for
`NoReturn` — consistent with the two-plane spec's "No GT gap is tagged in
this spec" claim (§4) and the §12.11 surface's "No GT gap" claim.

## Notes for the coordinator

- All five static cases conform to the two-plane spec: NR1 positive (false postcondition discharges on a raising body), NR2a negative (returning body rejected), NR3 negative (dead successor rejected), NR4a positive (NoReturn exempted from vacuity probe), NR4b negative (genuinely-vacuous function still flagged). No static lowering gap was found. The error messages produced by the body-divergence and dead-successor checks are clause-accurate (cite NR2a / NR3 and PEP 484).
- The NR4 keystone is the load-bearing result of this engagement: the exemption is confirmed sound on BOTH halves. The NoReturn function is EXEMPTED (NR4a) and a genuinely-vacuous function with NO NoReturn annotation is STILL FLAGGED (NR4b). The exemption is keyed on the declared `-> NoReturn` annotation (the IR `is_noreturn` flag), not on the inferred `false` postcondition — exactly as NR4 mechanism item 1 requires.
- The single runtime PASS is the cleanest result for `NoReturn`: the shim is the introspectable alias object (`NoReturn = None`) with no enforcement (NR-R3), confirming the central negative sentence (the runtime does not enforce annotations).
- The NO-BLEND verdict is the second load-bearing result: the NR-D2 probe deliberately imports and references the `NoReturn` shim in the same module that commits the NR2a body-divergence violation, and the static body-divergence check STILL fires (at semantic analysis, before WhyML emission). The runtime shim does NOT rescue the static violation — the two planes are carried as separate contracts.
- This matches the reference corpus (tests 0738–0741) and the §12.11 surface claim that `NoReturn` carries "No GT gap".
