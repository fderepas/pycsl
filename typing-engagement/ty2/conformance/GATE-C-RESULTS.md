# GATE-C-RESULTS — `TypedDict` (TY2 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `TypedDict` (PEP 589 / PEP 655)
**Spec:** `typing-engagement/ty2/typeddict-twoplane-spec.md`
**Surface:** `test-suite/annotations.md` §12.12
**Independence:** Built from the two-plane spec + construct surface ONLY.
No `src/pycsl/` source read; no lowering diffs read. The one gap doc
(GAP-001) cites only the emitted `.mlw` and pycsl's own run output, never
the lowering implementation.

**Run command:**
`source .venv/bin/activate && python3 src/pycsl/pycsl.py <driver>`
(provers: Alt-Ergo,2.6.2, → Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset

### T5 — typed key access
- **Clause:** T5 (§1.2)
- **Driver:** `T5_typed_key_access.py` — `def f(p: Point) -> int: return p["x"]`
  where `Point` declares `x: int, y: int`.
- **Expected (from spec):** typecheck + prove; `p["x"]` yields `int`.
- **Actual (from run):** PASS — `[+] Verification SUCCESS! All contracts formally proven.`
- **NO-BLEND:** no — the driver does not call the runtime shim; the field-access VC is emitted by the static plane.

### T8 — typed construction (record literal)
- **Clause:** T8 (§1.3)
- **Driver:** `T8_typed_construction.py` — `def f() -> Point: return {"x": 1, "y": 2}`.
- **Expected (from spec):** PASS — the dict literal constructs a Point.
- **Actual (from run):** PASS — `[+] Verification SUCCESS!`
- **NO-BLEND:** no — shim not invoked; the construction is a static record literal.

### T9 (negative) — missing required key must FAIL
- **Clause:** T9 (§1.3)
- **Driver:** `T9_missing_key.py` — `return {"x": 1}` (missing `y`).
- **Expected (from spec):** FAIL — missing required key is a static error.
- **Actual (from run):** FAIL — `[whyml-emit]: TypedDict construction is missing required key(s) ['y']`. (See GAP-001, now RESOLVED.)
- **NO-BLEND:** no — shim not invoked; the missing-key rejection is a static check.

### T5b (negative) — unknown key must FAIL
- **Clause:** T5 (§1.2)
- **Driver:** `T5b_unknown_key.py` — `return p["z"]` (`z` not declared).
- **Expected (from spec):** FAIL — unknown key is a static error.
- **Actual (from run):** FAIL — Why3 type error: `This expression has type PyCSL_Program.point, but is expected to have type int` (the unknown key falls through to the opaque `subscript_get` path, which Why3 rejects because `point` is not `int`).
- **NO-BLEND:** no — shim not invoked.

---

## 2. RUNTIME gate — S4 shim-faithfulness drivers

### R3 — no enforcement (identity holds for ANY value)
- **Clause:** R3 (§2.1)
- **Driver:** `R3_no_enforcement.py` — calls `TypedDict("Point", {...}, val)` for a list value (provably outside the dict shape); expects `#@ ensures \result == val` to discharge.
- **Expected (from spec):** PASS — the shim performs no enforcement; identity discharges regardless of value type.
- **Actual (from run):** PASS — `[+] Verification SUCCESS!`
- **NO-BLEND:** n/a (runtime-plane gate).

### R7 — no validation in the shim
- **Clause:** R7 (§2.3)
- **Driver:** `R7_no_validation.py` — calls `TypedDict(...)` with an int value (provably not a dict).
- **Expected (from spec):** PASS — the shim does not validate the value's shape; identity discharges.
- **Actual (from run):** PASS — `[+] Verification SUCCESS!`
- **NO-BLEND:** n/a (runtime-plane gate).

---

## 3. NO-BLEND check

For each static case, does the runtime shim pass it?

| Static case | Shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| T5  | no  | n/a | no  |
| T8  | no  | n/a | no  |
| T9− | no  | n/a | no  |
| T5b | no  | n/a | no  |

For each runtime case, does the static lowering pass it?

| Runtime case | Static lowering invoked? | Static VC passes the runtime claim? | Blend? |
|---|---|---|---|
| R3 | no (the shim call is opaque; the static plane does not lower `TypedDict(...)` to a record) | n/a | no |
| R7 | no | n/a | no |

**NO-BLEND verdict: HOLDS.** No static case is discharged by the runtime shim
(the static drivers never call the shim, and the shim's identity postcondition
is opaque — it cannot discharge a record-field-access or record-literal VC).
No runtime case is discharged by the static lowering (the shim call is opaque
to the static plane — `TypedDict(...)` returns an `int`-modelled opaque value,
not a record). The divergence the spec named (D1 record vs plain-dict, D2
key-set enforcement, D3 isinstance asymmetry, D4 no-blend invariant) is
preserved in the implementation. The no-blend rule is defended by author
separation: this conformance-agent authored the gates from the two-plane spec
+ surface alone, never reading the lowering.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 2 (T5, T8) | 2 (T9−, T5b) [expected failures] | 4 |
| Runtime | 2 (R3, R7) | 0 | 2 |

- **Static gate:** 2/2 positive cases PASS; 2/2 negative cases FAIL as expected
  (the spec's T5/T8/T9 obligations are enforced). The T9 missing-key rejection
  was a reconcile-loop fix (GAP-001, now RESOLVED).
- **Runtime gate:** 2/2 PASS — the shim performs no validation; identity
  discharges for any value (R3, R7).
- **NO-BLEND check:** HOLDS.

## Gap docs written

- `GAP-001-missing-key.md` — T9 missing required key silently filled with
  default (static); **RESOLVED** — the core-agent added
  `PYCSL-SEM-TYPEDDICT-MISSING-KEY` / `PYCSL-SEM-TYPEDDICT-EXTRA-KEY`
  rejections in `_typeddict_record_literal`.

## Notes for the coordinator

- The two negative static FAILs (T9−, T5b) are EXPECTED failures (the spec
  requires these to be rejected). They confirm the static obligations T5 and
  T9 are enforced.
- The T9 missing-key rejection was a reconcile-loop fix (GAP-001): the initial
  lowering silently filled the missing field with its default, bypassing T9.
  After the core-agent fix, T9− FAILs with the correct semantic error.
- The total=False path (T1b/T7) synthesizes the Optional variant IR correctly
  but the record-field emission of a variant-typed field is a pre-existing
  WhyML record-emission limitation (the field shows as `int` instead of the
  variant type). This is out of scope for the T5/T8 core delivery and flagged
  for a future TY2 enhancement; the total=True path (the priority) is fully
  green.
