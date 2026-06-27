# TY3 Gate C Results — `Callable` (PEP 484) + PEP 695 surface confirmation

**Status:** Gate C PASS.
**Date:** 2026-06-27
**Construct:** `Callable` (PEP 484) — the final TY3 construct — plus the PEP 695
type-parameter surface confirmation.
**Two-plane spec:** `typing-engagement/ty3/callable-twoplane-spec.md` (Gate A APPROVED).
**Conformance-agent:** authored from the spec + the construct surface ONLY
(never read `src/pycsl/` or the diff).

## (a) STATIC gate — S5 conformance subset

| Driver | Spec clause | Expected | Result |
|---|---|---|---|
| `S5_pass.py` | C1/C2/C3 (function-type param; call type-checks; result int) | SUCCESS (Valid) | ✅ SUCCESS (apply_fn + add_one VCs Valid; `assert r == 6` discharges) |
| `S5_arg_reject.py` | C2 (arg-type match: `f(s)` with `s: str` on `Callable[[int], int]`) | WhyML type error | ✅ ERROR "string, expected int" |
| `S5_ret_reject.py` | C3 (result type: `-> str` body `return f(0)`) | WhyML type error | ✅ ERROR "int, expected string" |
| `S5_c4_unprovable.py` | C4 (bare Callable gives NO value postcondition; `ensures \result == n+1` unprovable) | UNPROVABLE (sound refusal) | ✅ UNPROVABLE (Unknown — NOT shortcut with `\trusted`) |
| `C6_pep695_surface.py` | C6 (PEP 695 `type_params` flows end-to-end; `Cell[int]()` monomorphizes) | SUCCESS (Valid) | ✅ SUCCESS (cell_int VCs Valid — the monomorphizer specialized `Cell[T]` → `Cell_int`) |

**Verdict:** the construct passes every case in its declared S5 subset; each
static obligation clause maps to a passing case (or the expected reject /
sound-unprovable). C4's unprovability is the load-bearing no-blend guard on the
static side — a bare Callable refuses a value theorem the function-type does not
justify.

## (b) RUNTIME gate — S4 shim-faithfulness

| Driver | Spec clause | Expected | Result |
|---|---|---|---|
| `R3_shim_no_enforcement.py` | R1/R2/R3 (`Callable[[...], R]` is an introspectable alias; `callable(x)` presence-only; NO signature check) | SUCCESS (shim identity, no enforcement) | ✅ SUCCESS (the alias is subscriptable; no check runs) |

**Verdict:** the shim agrees with S4; nothing it does enforces what S3 says is
unenforced. `Callable[[...], R]` constructs an introspectable alias; the bound
signature is recorded for introspection but NOT checked at runtime (R3).

## (c) NO-BLEND check (independence-based)

| Driver | Spec clause | Expected | Result |
|---|---|---|---|
| `D1_no_blend.py` | D1 (the runtime `callable()` presence check must NOT discharge the static function-type obligation) | SUCCESS — the static function-type obligation is a WhyML arrow parameter + Why3 typecheck, NOT a runtime presence check | ✅ SUCCESS (the static half proves; the runtime presence check carries no static force) |

**Verdict:** the runtime gate does NOT pass the static claim and vice versa. The
static function-type obligation is a WhyML arrow parameter discharged by Why3's
typecheck (C2/C3); the runtime `callable()` / `isinstance(x, Callable)` is a
signature-agnostic presence check (R2). The divergence the spec named (D1) is
preserved in the implementation: the static signature obligation is NOT
discharged by the runtime callable check — confirmed negatively by
`S5_c4_unprovable.py` (the static claim fails while the runtime presence check
would accept any callable). The no-blend trap is preserved.

## Gap (recorded, NOT shortcut)

None. C4's unprovability is a SOUND refusal (a bare Callable gives no value
theorem), not a gap — it is the no-blend keystone working as designed. The
scope limit (C5 — `bytes`/`list`/`dict`/`set`/`Any`/nested-`Callable`/ellipsis
rejected with `PYCSL-TY3-CALLABLE-SCOPE`) is divergence-by-strictness, recorded
in the two-plane spec §1.5 and the static-semantics reference §S.TY3.8, not a
gap.

## Graduation

The construct **graduates to Normative**. The `Callable` surface is in
`test-suite/annotations.md` §12.17 and all three reference docs (concrete
§T.TY3.5, static §S.TY3.8/§S.TY3.9, translational §T.TY3.8); doc-coherency
green. The PEP 695 type-parameter surface is confirmed first-class end-to-end
(`C6_pep695_surface.py` — the monomorphizer specializes `Cell[T]` → `Cell_int`).
This is the FINAL construct of the typing engagement; its graduation completes
the entire `typing-global-impl.md` engagement (TY0–TY3).
