# GATE-C-RESULTS — `cast` (TY1 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `cast` (PEP 484, §"Casts")
**Spec:** `typing-engagement/ty1/cast-twoplane-spec.md`
**Surface:** `src/pycsl_lib/typ/__init__.py:cast` (the *pycsl_lib* runtime shim surface named by the spec); the declared S5 subset for `cast` is **empty by construction** (cast carries no dischargeable static judgment), so no `test-suite/annotations.md` clause is named.
**Independence:** Built from the two-plane spec + construct surface ONLY.
No `src/pycsl/` source read; no lowering diffs read. The single runtime
shim read was `src/pycsl_lib/typ/__init__.py` (the *pycsl_lib* shim
surface, NOT the `src/pycsl/` lowering implementation) — permitted
because it is the runtime-plane public surface that the spec §2 names.

**Run command:**
`source .venv/bin/activate && python3 src/pycsl/pycsl.py <driver>`
(provers: Alt-Ergo,2.6.2, → Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset (empty by construction)

The two-plane spec §1/§4 declares `cast`'s S5 subset **empty**: `cast(t, v)`
is an unchecked static hint, NOT a dischargeable VC. PyCSL does not lower it
to a `requires`/`ensures` obligation over `t`. The "static gate" is
therefore minimal — it probes only the *absence* of an obligation (the
honesty point), not the discharge of one.

### CA1 — identity postcondition discharges
- **Clause:** CA1 (§1, §4) — degenerate positive: the only thing the static plane can observe about `cast(int, 5)` is the identity postcondition inherited from the runtime shim.
- **Driver:** `CA1_identity.py` — `def f() -> int: return cast(int, 5)` with `#@ ensures \result == 5`.
- **Expected (from spec):** PASS — the identity postcondition discharges because `cast(int, 5)` returns 5 unchanged; no static obligation over `t` is emitted.
- **Actual (from run):** PASS — `Sub-goal postcondition of goal f'vc. Prover result is: Valid (0.01s, 6 steps).`; `[+] Verification SUCCESS!`. (Why3 warns `unused variable typ` — confirming the `typ` argument carries no obligation.)
- **NO-BLEND:** n/a — driver does not invoke any static-plane narrowing; the only VC is the identity postcondition inherited from the runtime shim. The static plane contributes nothing on top.

### CA2 — honesty check: a "wrong" cast must NOT be rejected
- **Clause:** CA2 (§1, §4 — the honesty point): cast is unchecked by definition (PEP 484); PyCSL does NOT lower `cast(t, v)` to a VC over `t`. A cast that "claims" a type not matching the value — `cast(str, 5)` — must still PASS: a shim/lowering that REJECTED it would be blending the planes (emitting a static obligation that S1/S2 grant no authority for and that the runtime plane does not back).
- **Driver:** `CA2_no_type_check.py` — `def f() -> int: return cast(str, 5)` with `#@ ensures \result == 5`. The claimed type `str` does not match the value `5` (int).
- **Expected (from spec):** PASS — cast does not verify the type; the identity postcondition `\\result == 5` discharges regardless of the claimed type.
- **Actual (from run):** PASS — `Sub-goal postcondition of goal f'vc. Prover result is: Valid (0.01s, 6 steps).`; `[+] Verification SUCCESS!`. (Why3 warns `unused variable typ` — confirming the `str` argument is recorded as a hint, not lowered to an obligation.) The honesty point holds: cast is unchecked; a "wrong" cast is NOT rejected.
- **NO-BLEND:** n/a — driver does not invoke any static-plane narrowing; no `requires` over `t` is synthesized. This is the **cleanest no-blend witness on the static side**: the construct that *could* have been blended (a type assertion) is explicitly recorded as NOT lowering to an obligation.

---

## 2. RUNTIME gate — S4 shim-faithfulness drivers

### CR1 — cast returns v unchanged for any value type (int, str, None)
- **Clause:** CR1 (§2) — `cast(t, v)` returns `v` unchanged at runtime. Per S3 the library reference documents `cast` as "return `v` unchanged" — pure identity; S4 (CPython `Lib/typing.py`) implements it literally as `def cast(typ, val): return val`. The shim carries only `ensures \\result == val` and performs NO type check, NO conversion, NO narrowing, NO validation. Identity must discharge for ANY value type.
- **Driver:** `CR1_returns_unchanged.py` — three functions calling `cast(int, val)`, `cast(str, val)`, `cast(type(None), val)` for int / str / None values respectively; each `#@ ensures \\result == val`.
- **Expected (from spec):** PASS — identity discharges regardless of value type.
- **Actual (from run):** PASS — three VCs all `Valid (0.01s, 6 steps)` (`call_int'vc`, `call_none'vc`, `call_str'vc`); `[+] Verification SUCCESS!`.
- **NO-BLEND:** n/a (runtime-plane gate).

### CR2 — cast performs NO conversion (identity, not coercion)
- **Clause:** CR2 (§2 — no conversion): `cast(t, v)` returns `v` UNCHANGED — it does NOT convert `v` to type `t`. The sharpest test is `cast(int, "hello")`: a CONVERTING shim would either raise (`int("hello")` raises `ValueError` in CPython) or return a converted int. The faithful shim returns `"hello"` unchanged — a string — and the identity postcondition `\\result == "hello"` discharges with the ORIGINAL value, NOT with a converted int.
- **Driver:** `CR2_no_conversion.py` — `cast_int_on_string(val)` calls `cast(int, val)` on a string value, with `#@ ensures \\result == val`.
- **Expected (from spec):** PASS — `cast(int, "hello")` returns `"hello"` unchanged; the identity postcondition holds with the original (string) value, NOT with a converted int.
- **Actual (from run):** PASS — `Sub-goal postcondition of goal cast_int_on_string'vc. Prover result is: Valid (0.01s, 6 steps).`; `[+] Verification SUCCESS!`. (Why3 warns `unused variable typ` — confirming `int` is a hint, not a coercion target.) The runtime-plane honesty point holds: cast does NOT convert.
- **NO-BLEND:** n/a (runtime-plane gate).

---

## 3. NO-BLEND check

The two-plane spec §3 states the no-blend rule (§0 of `typing-global-impl.md`)
is **vacuously satisfied** for `cast`: there is no static claim to blend
with the runtime claim, so the rule "neither plane's contract may stand
in for the other" has nothing to forbid. The no-blend trap table (§3.2)
names `cast`'s trap as "a `cast` that validates"; this conformance run
rules that trap out by confirming no validation clause exists on either
plane.

### Cross-check table

| Static case | Runtime shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| CA1 | yes (calls `cast(int, 5)`) | the only VC is the *runtime* identity postcondition `\\result == 5`, NOT a static obligation — there is no static VC over `t` to "pass" | no |
| CA2 | yes (calls `cast(str, 5)`) | same — only the runtime identity postcondition `\\result == 5`; no static VC over `t` exists to "pass"; the "wrong" cast is NOT rejected, confirming no static obligation was synthesized | no |

**Vacuous-probe: is there any case where a runtime check discharges a static obligation?**

NO. There is no case where a runtime check discharges a static obligation
for `cast`, because:

1. The static plane emits **no** obligation over `t` (CA1/CA2 confirm this:
   the `typ` argument is unused in the emitted WhyML, warned about by Why3,
   and a "wrong" cast `cast(str, 5)` is NOT rejected — so no `requires` over
   `t` and no `v : t` proof goal exists). There is nothing on the static
   side for a runtime check to discharge.
2. The runtime plane performs **no** check (CR1/CR2 confirm this: the
   shim's body is `return val`, its only contract is `ensures \\result ==
   val`, and `cast(int, "hello")` returns `"hello"` unchanged — no
   conversion, no validation). There is no runtime check that could
   substitute for a static obligation even if one existed.

`cast` is the **degenerate case** the spec §3 names: the only typing
construct where the static plane does NOT lower to an obligation. With
nothing on the static side and nothing checking on the runtime side, the
no-blend rule is vacuously satisfied — neither plane's contract can stand
in for the other because there is nothing to stand in.

**NO-BLEND verdict: HOLDS (vacuously).** No static case is discharged by
the runtime shim. There is no blend risk in either direction.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 2 (CA1, CA2) | 0 | 2 |
| Runtime | 2 (CR1, CR2) | 0 | 2 |
| NO-BLEND | 1 (vacuous — no case to probe) | 0 | 1 |

- **Static gate:** 2/2 PASS. CA1 confirms the identity postcondition
  discharges; CA2 confirms the honesty point — a "wrong" cast
  (`cast(str, 5)`) is NOT rejected, because `cast` carries no static
  obligation over `t`. The declared S5 subset is empty by construction,
  and this run confirms that emptiness empirically (no `requires`/`ensures`
  over `t` is synthesized; Why3 reports `typ` as an unused variable in
  every driver).
- **Runtime gate:** 2/2 PASS. CR1 confirms identity discharges for int,
  str, and None; CR2 confirms `cast(int, "hello")` returns `"hello"`
  unchanged — no conversion, no validation. The shim's body
  (`return val`) faithfully implements S4's `def cast(typ, val): return
  val`, and the single `ensures \\result == val` postcondition is realizable and discharges.
- **NO-BLEND check:** HOLDS (vacuously). There is no case where a runtime
  check discharges a static obligation — `cast` has neither. This is the
  substantive finding the spec §3 records: the absence of a divergence
  section is NOT an omission.

## Gap docs written

None. No gap was found on either plane. This is the **cleanest
conformance result in the TY1 typing engagement so far** — every driver
discharges at 6 steps with no caveat, no inherited shim-identity gap
(unlike Union R3/R8 and Literal LR3, where the `Union`/`Literal` shim
bodies returned `0` and the call-shape mismatched the val arity). The
`cast` shim's body is `return val` and its call shape matches the val
arity, so the identity postcondition is reachable and discharges.

## Notes for the coordinator

- `cast` is fully conformant on both planes with zero gap. The spec's
  classification ("Shimmed on BOTH planes", GT gap: None, S5 subset:
  empty by construction) is confirmed empirically.
- The contrast with `Union`/`Literal` is instructive: the `cast` shim is
  the only `pycsl_lib/typ` shim whose body actually returns `val` (the
  `Union`/`Literal` shim bodies return `0`, which is why their runtime
  identity postconditions are unreachable — see GAP-003 / GAP-LIT-003).
  The `cast` shim is the faithful reference shape for the
  `pycsl_lib/typ` identity-shim family.
- The NO-BLEND verdict is vacuous but substantive: `cast` is the one
  construct where the static plane does NOT lower to an obligation, so
  the no-blend rule has nothing to forbid. This is the honesty point the
  spec §1 records — not a weakness.
- CA2 is the load-bearing honesty probe: if `cast(str, 5)` ever FAILS
  verification, that signals a plane-blend regression (a `requires` over
  `t` was synthesized, which S1/S2 grant no authority for). Re-run CA2 on
  any change to the `cast` lowering.
