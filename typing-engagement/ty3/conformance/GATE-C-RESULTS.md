# TY3 Gate C Results — TypeVar/Generic + Whole-Module Monomorphization

**Status:** Gate C PASS (with one recorded gap — multi-instantiation Module 6
field-mangling, see `33-1700-typing-gap-9.md`).
**Date:** 2026-06-27
**Construct:** TypeVar/Generic (PEP 484 + PEP 695) — TY3 generic layer.
**Two-plane spec:** `typevar-generic-twoplane-spec.md`.
**Conformance-agent:** authored from the spec + the construct surface ONLY
(never read `src/pycsl/` or the diff).

## (a) STATIC gate — S5 conformance subset

| Driver | Spec clause | Expected | Result |
|---|---|---|---|
| `S5_int.py` | G2/G3 (one int instantiation → name-mangled specialized copy with substituted contract provable) | SUCCESS (10/10 VCs) | ✅ SUCCESS |
| `S5_bound_pass.py` | G4 (`C[T: int]` instantiated with `int` — admissible) | SUCCESS | ✅ SUCCESS |
| `S5_bound_reject.py` | G4 reject (`C[T: int]` instantiated with `str` — invariant check, GT2) | PIPELINE ERROR `PYCSL-TY3-BOUND` | ✅ ERROR |
| `S5_uninstantiated.py` | G5 (un-instantiated generic → declaration-only, no specialized copy) | SUCCESS (no VC) | ✅ SUCCESS |
| `S5_gt4_polyrec.py` | G6/GT4 (polymorphic recursion `f[T]()` inside `f[T]`) | PIPELINE ERROR `PYCSL-TY3-GT4` | ✅ ERROR |
| `S5_gt3_paramspec.py` | G7/GT3 (`ParamSpec`/`TypeVarTuple` schema-only) | PIPELINE ERROR `PYCSL-TY3-GT3` | ✅ ERROR |

**Verdict:** the construct passes every case in its declared S5 subset; each
static obligation clause maps to a passing case (or the expected loud-fail).

## (b) RUNTIME gate — S4 shim-faithfulness

| Driver | Spec clause | Expected | Result |
|---|---|---|---|
| `R3_shim_no_bound.py` | R1/R2/R3 (TypeVar/Generic are introspectable objects, bound NOT checked) | SUCCESS (shim identity, no enforcement) | ✅ SUCCESS |

**Verdict:** the shim agrees with S4; nothing it does enforces what S3 says is
unenforced. The bound is recorded on `__bound__` but NOT checked at runtime
(R3) — confirmed by `C[str]()` constructing an ordinary instance with no
check.

## (c) NO-BLEND check (independence-based)

| Driver | Spec clause | Expected | Result |
|---|---|---|---|
| `P5_no_blend.py` | D1 (an un-instantiated generic must NOT claim a per-instance theorem it never emitted) | SUCCESS — only the `bool` specialization is emitted; an int theorem would have no specialization to carry it | ✅ SUCCESS |

**Verdict:** the runtime gate does NOT pass the static claim and vice versa.
The monomorphization pass removes the original generic decl + methods when
specializing (the per-instance theorem lives ONLY on the specialized copy); an
un-instantiated generic emits NO specialized copy and NO per-instance VC
(recorded Ignored/GT8). The no-blend trap (D1) is preserved.

## Gap (recorded, NOT shortcut)

`33-1700-typing-gap-9.md` — the multi-instantiation case (`Stack[int]` +
`Stack[str]` in one module) hits a Module 6 field-mangling consistency gap
(fields get class-prefixed in the record decl but the invariant/requires
references don't). This is a Module 6 lowering gap, NOT a monomorphization
bug — the IR is well-formed. The single-instantiation path (the feasibility-
probe shape, the S5_int driver) proves 10/10 VCs. Recorded honestly per the
impl guide §0; not shortcut with `\trusted`.

## Graduation

The construct **graduates to Normative** for the single-instantiation-per-
generic case (the load-bearing path the overview §4.1 names and the probe
verified). The multi-instantiation case is gated behind the recorded gap doc.
