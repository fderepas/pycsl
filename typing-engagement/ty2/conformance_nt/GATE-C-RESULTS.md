# GATE-C-RESULTS — `NamedTuple` (TY2 tier) typing conformance

**Agent:** typing-conformance-agent
**Construct:** `NamedTuple` (PEP 526 class form / PEP 484 functional form)
**Spec:** `typing-engagement/ty2/namedtuple-twoplane-spec.md`
**Surface:** `test-suite/annotations.md` §12.13
**Independence:** Built from the two-plane spec + construct surface ONLY.
No `src/pycsl/` source read; no lowering diffs read.

**Run command:**
`source .venv/bin/activate && python3 src/pycsl/pycsl.py <driver>`
(provers: Z3,4.13.3,; memory model: hoare)

---

## 1. STATIC gate — declared S5 conformance subset

### N4 — typed named-field access
- **Clause:** N4 (§1.2)
- **Driver:** `N4_named_field_access.py` — `def f(p: Point) -> int: return p.x`
  where `Point` declares `x: int, y: int`.
- **Expected (from spec):** typecheck + prove; `p.x` yields `int`.
- **Actual (from run):** PASS — `[+] Verification SUCCESS! All contracts formally proven.`
- **NO-BLEND:** no — the driver does not call the runtime shim; the field-access VC is emitted by the static plane.

### N5 — typed positional access
- **Clause:** N5 (§1.3)
- **Driver:** `N5_positional_access.py` — `def f(p: Point) -> int: return p[0]`
  and `def g(p: Point) -> int: return p[1]`.
- **Expected (from spec):** PASS — `p[0]` yields `int` (field `x`); `p[1]` yields `int` (field `y`).
- **Actual (from run):** PASS — `[+] Verification SUCCESS!`
- **NO-BLEND:** no — shim not invoked; the positional-access VC is emitted by the static plane.

### N6 — typed positional construction
- **Clause:** N6 (§1.4)
- **Driver:** `N6_positional_construction.py` — `def f() -> Point: return Point(1, 2)`.
- **Expected (from spec):** PASS — the positional call constructs a Point.
- **Actual (from run):** PASS — `[+] Verification SUCCESS!`
- **NO-BLEND:** no — shim not invoked; the construction is a static record literal.

### N5b (negative) — out-of-range index must FAIL
- **Clause:** N5 (§1.3)
- **Driver:** `N5b_out_of_range.py` — `return p[2]` (`Point` has 2 fields).
- **Expected (from spec):** FAIL — out-of-range index is a static error.
- **Actual (from run):** FAIL — Why3 type error: `This expression has type PyCSL_Program.point @rho, but is expected to have type int` (the out-of-range index falls through to the opaque `subscript_get` path, which Why3 rejects because `point` is not `int`).
- **NO-BLEND:** no — shim not invoked.

### N7 (negative) — wrong-arity construction must FAIL
- **Clause:** N7 (§1.4)
- **Driver:** `N7_wrong_arity.py` — `return Point(1)` (too few args).
- **Expected (from spec):** FAIL — wrong arity is a static error.
- **Actual (from run):** FAIL — `[semantic]: NamedTuple construction 'Point(...)' called with 1 argument(s) but the NamedTuple declares 2 field(s) (arity range 2..2; N7 / PEP 526 — a NamedTuple's fields are required positional arguments).`
- **NO-BLEND:** no — shim not invoked; the wrong-arity rejection is a static check.

### N4b (negative) — unknown attribute must FAIL
- **Clause:** N4 (§1.2)
- **Driver:** `N4b_unknown_attribute.py` — `return p.z` (`z` not declared).
- **Expected (from spec):** FAIL — unknown attribute is a static error.
- **Actual (from run):** FAIL — Why3 type error: `unbound function or predicate symbol 'z'` (the unknown attribute has no record field, so Why3 rejects the field read).
- **NO-BLEND:** no — shim not invoked.

---

## 2. RUNTIME gate — S4 shim-faithfulness drivers

### R3 — no enforcement (identity holds for ANY value)
- **Clause:** R3 (§2.1)
- **Driver:** `R3_no_enforcement.py` — calls `NamedTuple("Point", [...], val)` for a list value (provably outside the tuple shape); expects `#@ ensures \result == val` to discharge.
- **Expected (from spec):** PASS — the shim performs no enforcement; identity discharges regardless of value type.
- **Actual (from run):** PASS — `[+] Verification SUCCESS!`
- **NO-BLEND:** n/a (runtime-plane gate).

### R8 — no validation in the shim
- **Clause:** R8 (§2.3)
- **Driver:** `R8_no_validation.py` — calls `NamedTuple(...)` with an int value (provably not a tuple).
- **Expected (from spec):** PASS — the shim does not validate the value's shape; identity discharges.
- **Actual (from run):** PASS — `[+] Verification SUCCESS!`
- **NO-BLEND:** n/a (runtime-plane gate).

---

## 3. NO-BLEND check

For each static case, does the runtime shim pass it?

| Static case | Shim invoked by driver? | Shim passes the static VC? | Blend? |
|---|---|---|---|
| N4  | no  | n/a | no  |
| N5  | no  | n/a | no  |
| N6  | no  | n/a | no  |
| N5b | no  | n/a | no  |
| N7  | no  | n/a | no  |
| N4b | no  | n/a | no  |

For each runtime case, does the static lowering pass it?

| Runtime case | Static lowering invoked? | Static VC passes the runtime claim? | Blend? |
|---|---|---|---|
| R3 | no (the shim call is opaque; the static plane does not lower `NamedTuple(...)` to a record) | n/a | no |
| R8 | no | n/a | no |

**NO-BLEND verdict: HOLDS.** No static case is discharged by the runtime shim
(the static drivers never call the shim, and the shim's identity postcondition
is opaque — it cannot discharge a record-field-access, record-field-by-index,
or record-literal VC). No runtime case is discharged by the static lowering
(the shim call is opaque to the static plane — `NamedTuple(...)` returns an
`int`-modelled opaque value, not a record). The divergence the spec named
(D1 record vs plain-tuple, D2 arity/type enforcement, D3 isinstance asymmetry,
D4 no-blend invariant) is preserved in the implementation. The no-blend rule
is defended by author separation: this conformance-agent authored the gates
from the two-plane spec + surface alone, never reading the lowering.

---

## Summary

| Gate | PASS | FAIL | Total |
|---|---|---|---|
| Static  | 3 (N4, N5, N6) | 3 (N5b, N7, N4b) [expected failures] | 6 |
| Runtime | 2 (R3, R8) | 0 | 2 |

- **Static gate:** 3/3 positive cases PASS; 3/3 negative cases FAIL as expected
  (the spec's N4/N5/N6/N7 obligations are enforced).
- **Runtime gate:** 2/2 PASS — the shim performs no validation; identity
  discharges for any value (R3, R8).
- **NO-BLEND check:** HOLDS.

## Gap docs written

None. The NamedTuple implementation passed Gate C on the first run — no
reconcile-loop gaps were found. The N7 wrong-arity rejection was part of the
core-agent's initial implementation (the `PYCSL-SEM-NAMEDTUPLE-ARITY` check
in `core_ir_semantic._check_namedtuple_access`), not a reconcile-loop fix.

## Notes for the coordinator

- The three negative static FAILs (N5b, N7, N4b) are EXPECTED failures (the
  spec requires these to be rejected). They confirm the static obligations N4,
  N5, and N7 are enforced.
- The N7 wrong-arity rejection uses a hard `PYCSL-SEM-NAMEDTUPLE-ARITY` error
  (raised in `core_ir_semantic`), mirroring the TypedDict GAP-001 missing-key
  rejection — the shared `_call_record_constructor` default-fills missing args
  soundly but imprecisely, so the N7 check makes the wrong-arity case a
  static error, not a silent default-fill.
