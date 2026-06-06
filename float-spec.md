# PyCSL Enhancement Proposal: IEEE-754 Floating-Point

**Status:** Draft / high-level design
**Scope:** floating-point types, rounded operators, the real bridge, conversions, static semantics, WhyML lowering, soundness
**Audience:** PyCSL maintainers, contract authors
**Builds on:** the existing `float`→`real` lowering (retained as the *idealized* model — see §2); composes with bitvectors (float↔bv) and `#@ lemma` (error-bound proofs)
**Non-goal:** implementation patches — this specifies *what* must hold, not the diff.

---

## 1. Motivation

PyCSL currently lowers `float` to Why3 `real`. That is a useful *idealization* — it treats a
floating-point value as an exact real number — but it is **unsound for genuine floating-point
code**, because real arithmetic ignores everything that makes IEEE-754 hard:

- **rounding**: `a + b` is not the real sum but its rounding to the nearest representable value, so
  `(a + b) + c != a + (b + c)` and distributivity fails;
- **special values**: NaN (with `NaN != NaN`), ±infinity from overflow, signed zero;
- **finite precision and subnormals**.

A property proved in the real model may simply be false for the floats the program actually
computes. Why3 offers the sound path: the `ieee_float` library, compliant with IEEE-754 and mapped
to the SMT-LIB FloatingPoint theory, *and* a real-axiomatized model — both relating each float to a
real value through rounding. This proposal surfaces real IEEE-754 floats in PyCSL **on top of** the
existing real model rather than replacing it.

## 2. Two coexisting models, bridged by `to_real`

The design keeps both layers and the bridge between them:

| Annotation | Why3 target | Semantics | Use |
|---|---|---|---|
| `real` (the idealized model, today's `float`) | `real` | exact mathematical reals | algorithm-level reasoning where rounding is irrelevant; the *specification reference* |
| `float32` / `float64` (new) | `ieee_float.Float32` / `Float64` | exact IEEE-754 binary32/64 | code whose correctness depends on rounding / special values |

Every finite IEEE float `x` has a real value `\to_real(x)`, and each rounded operation is the
*rounding of the exact real result*: `\to_real(a ⊕ b) == \round(mode, \to_real(a) + \to_real(b))`.
This is the load-bearing relationship — it lets a contract state correctness as a bound between the
computed float and the ideal real, and lets reasoning drop to the fast real model wherever exactness
is acceptable. (Why3 provides exactly this via its two float modules and their `to_real`/`round`
functions; PyCSL exposes the same bridge.)

## 3. Surface model

```
fptype ::= "float32" | "float64"
```

- Arithmetic `+ - * /` is **rounded** (default round-to-nearest-ties-to-even, `RNE`).
- `==`, `<`, `<=`, `>`, `>=` are **IEEE comparisons** (NaN is unordered: `NaN == NaN` is false,
  and `NaN < x`, `x < NaN` are both false).
- Division does **not** generate a div-by-zero VC (IEEE total: yields ±inf or NaN); finiteness is
  asserted where needed.
- Rounding modes available as constants: `RNE`, `RNA`, `RTP`, `RTN`, `RTZ`.

```python
#@ ensures \to_real(\result) == \round(RNE, \to_real(a) + \to_real(b))   # the meaning of fp add
#@ assigns \nothing
def fadd(a: float64, b: float64) -> float64:
    return a + b

#@ requires \is_finite(x)                # without this, x == x is NOT provable (NaN)
#@ ensures \result == True
#@ assigns \nothing
def reflexive_eq(x: float64) -> bool:
    return x == x
```

The second example is the soundness point in miniature: in the `real` model `x == x` is trivially
true; for IEEE floats it requires excluding NaN.

## 4. Operators and their lowering (Module 6)

A `float64` lowers to `Float64.t` (similarly `float32`→`Float32.t`). Operators map to `ieee_float`:

| Python (fp operands) | Meaning | Why3 (`Float64.`) |
|---|---|---|
| `a + b`, `-`, `*`, `/` | rounded arithmetic | `add RNE`, `sub RNE`, `mul RNE`, `div RNE` |
| `-a` | negation (exact) | `neg a` |
| `\abs(a)`, `\sqrt(a)` | abs / rounded sqrt | `abs a`, `sqrt RNE a` |
| `a == b`, `!=` | IEEE equality (NaN unordered) | `eq` / `<>` |
| `a < b`, `<=`, `>`, `>=` | IEEE ordered comparison | `lt`, `le`, `gt`, `ge` |
| `\to_real(a)` (spec) | real value of a finite float | `to_real a` |
| `\round(m, r)` (spec) | round a real under mode `m` | `round m r` |
| `\is_finite(a)`, `\is_nan(a)`, `\is_infinite(a)` (spec) | classification | `is_finite`, `is_nan`, `is_infinite` |

A non-default rounding mode is written explicitly: `\fadd(a, b, RTP)` style intrinsics, or a
function/module pragma `#@ rounding RTP`.

## 5. The real bridge in contracts

`#@ requires`/`#@ ensures`/loop invariants may use `\to_real`, `\round`, the classifiers
(`\is_finite`/`\is_nan`/`\is_infinite`), and real-valued arithmetic on `\to_real(...)` terms. The
canonical idioms:

```python
# exact relationship (definitional)
#@ ensures \to_real(\result) == \round(RNE, \to_real(a) * \to_real(b))

# rounding-error bound, stated against the ideal real
#@ requires \is_finite(a) and \is_finite(b) and \is_finite(\result)
#@ ensures \abs(\to_real(\result) - (\to_real(a) + \to_real(b))) <= unit_roundoff * \abs(\to_real(a) + \to_real(b))
```

Error-bound goals typically mix float and real reasoning, which is the hard case (§8); they are
discharged with helper `#@ lemma` functions, exactly as for the bitvector↔int bridge.

## 6. Conversions

No implicit coercion across the real/float boundary, between widths, or to/from integers and
bitvectors — all explicit, with rounding/range made visible:

| Form | Meaning | Why3 |
|---|---|---|
| `\to_real(x)` | finite float → exact real | `to_real` |
| `\fp_of_int(n, mode)` | int → float (rounded) | `of_int mode n` |
| `\fp_to_int(x, mode)` | float → int (rounded; VC: finite & in range) | `to_int mode x` |
| `\fp_cast(x, W, mode)` | float32 ↔ float64 (rounded) | width converters |
| `\fp_of_bv(b, mode)` / `\fp_to_bv(x, mode)` | float ↔ bitvector | the `of_sbv*`/`to_ubv*` converters |

The float↔bitvector converters tie this proposal to the bitvector one: a value can cross from a
`uint32` bit pattern to a `float32` and back, each crossing explicit and rounding-annotated.

## 7. CPython faithfulness (a positive note)

Unlike the bitvector case — where CPython's unbounded `int` does not match modular words — **CPython's
`float` *is* IEEE-754 binary64**. So `float64` is the rare PyCSL type whose verified model matches
the runtime semantics essentially exactly (modulo NaN payloads and `math`-library functions). That
makes `float64` verification genuinely faithful to the running program. `float32` has **no** native
CPython counterpart (Python has only binary64 floats; binary32 appears via `numpy`/`array`/struct
packing), so `float32` is a model for interop, embedded, and storage formats rather than for plain
CPython `float` values — and the spec says so rather than implying otherwise.

## 8. Soundness (mandatory rules)

1. **Idealized vs IEEE are distinct types.** `real` (today's `float`→`real`) keeps the exact-real
   semantics; `float32`/`float64` carry IEEE semantics. Crossing requires `\to_real` / `\round`.
   Code that needs soundness about actual floats uses `float32`/`float64`.
2. **No implicit coercion.** real↔float, float32↔float64, int↔float, and bv↔float crossings are all
   explicit (§6). Silent promotion (e.g. treating a `float64` as a `real`) is rejected — it is the
   mechanism by which rounding gets hidden.
3. **NaN-aware comparison.** `==`/`<`/`<=` lower to IEEE comparisons; the analyzer SHOULD warn when
   a contract assumes a NaN-violating law (e.g. `x == x`, `not (a < b) ==> a >= b`) without a
   `\is_finite`/`not \is_nan` guard.
4. **Total division, asserted finiteness.** Float `/` produces no div-by-zero VC (IEEE yields
   ±inf/NaN); a contract that needs a finite result states `\is_finite(\result)`.
5. **Explicit rounding mode.** Default `RNE`; any other mode is named at the operation or via a
   pragma, never inferred.
6. **`\fp_to_int` range obligation.** Converting a float to an int generates `\is_finite(x)` and an
   in-range VC (NaN/inf/out-of-range conversion is otherwise undefined).

## 9. Module impact

| Module | Change |
|---|---|
| **Module 2 — Parser** | recognise `float32`/`float64`; rounding-mode constants; `\to_real`/`\round`/`\is_*`/`\fp_*` |
| **Module 3 — Weaver** | carry the width and the active rounding mode per binding/scope |
| **Module 4 — Semantic Analyzer** | enforce §8 (distinct types, no implicit coercion, NaN-law warnings, conversion VCs); literal typing |
| **Module 5 — IR Emitter** (`ir_schema`) | fp-typed nodes `(width)`, rounding-mode annotations, conversion nodes |
| **Module 6 — WhyML Transpiler** | `use ieee_float.Float32/Float64`; map operators per §4 with rounding mode; emit the real bridge and conversions; select backend driver (§10) |

## 10. Backend selection (the "on top of real" payoff)

Two lowering modes, both retaining the real bridge, chosen per driver or pragma:

- **SMT-FP mode** (`ieee_float.Float*` → SMT-LIB FloatingPoint theory): exact bit-level IEEE
  semantics, dispatched to FP-capable solvers (Z3, CVC5, Bitwuzla via bit-blasting). Best for
  special-value and exact-rounding goals.
- **Real-axiomatized mode** (the `floating_point`-style model, VCs encoded over reals): floats
  related to reals by rounding axioms. Best when a goal must combine with real-valued lemmas and
  error analysis — literally reasoning *on top of* `real`.

The real bridge (`\to_real`/`\round`) is identical in both, so a development can move between modes
without rewriting its specifications.

## 11. Phasing

| Phase | Delivers | Risk |
|---|---|---|
| **P1 — Core IEEE** | `float32`/`float64`; rounded `+ - * /`, `neg`, `abs`, `sqrt` (RNE); IEEE comparisons; `\to_real`/`\is_finite`/`\is_nan`; SMT-FP backend | medium |
| **P2 — Rounding & special values** | full rounding-mode control; NaN/inf/signed-zero-aware contracts; real-axiomatized backend mode | medium |
| **P3 — Conversions & error bounds** | int↔float, float32↔float64, float↔bitvector; error-bound idioms + helper lemmas | medium–high; mixed real/float goals |
| **P4 — Consolidation** | clarify/retire the legacy idealized `float`→`real` default; subnormal reasoning; transcendental-function axiom libraries (out-of-core) | medium |

Each phase ships corpus drivers in the existing numbering style: PASS demos (the `fadd` rounding
relationship; a finite-bounded sum; a NaN-guarded comparison) and FAIL twins — `x == x` proved
**without** a NaN guard (must fail), an implicit `float64`→`real` use (rejected), a float→int
conversion **without** the range/finite VC, and an associativity claim `(a+b)+c == a+(b+c)` for
floats (must fail, demonstrating the unsoundness of the old real-only view).

## 12. Validation

- **Soundness contrast:** the NaN and associativity FAIL twins confirm the IEEE model rejects laws
  the old `float`→`real` idealization wrongly accepted — the core reason for the feature.
- **Bridge correctness:** `\to_real(a + b) == \round(RNE, \to_real(a) + \to_real(b))` discharges
  definitionally; an error-bound example closes with a `#@ lemma`.
- **TR-BUG-1 revisited:** float constants are handled through the IEEE model rather than an ad-hoc
  `float` round-trip, removing the documented large-integer-constant precision bug for fp-typed
  code.
- **Backend parity:** the same specifications discharge under both SMT-FP and real-axiomatized
  modes (the latter exercising the real bridge directly).

## 13. Open questions

1. **Default of `float`.** Should bare `float` remain the idealized `real` (back-compatible) or
   become `float64` (sound by default, but a breaking change)? A migration path and lint are needed
   either way.
2. **Backend default.** SMT-FP (best automation for special values) vs real-axiomatized (best for
   error analysis) — chosen globally, per-function, or by goal shape?
3. **Transcendentals.** `sin`/`cos`/`exp`/`log` are not IEEE basic operations; they require
   axiomatized libraries with their own error specs — a follow-on, explicitly out of core scope.
4. **Mixed real/float automation.** Heuristics and a standard helper-lemma library for the goals
   that straddle the bridge (the dominant proof-effort sink).
5. **float32 sourcing.** Since CPython has no binary32, how do `float32` values enter a verified
   program — `numpy`/`struct`/`array` boundaries — and how is that boundary specified?

---

### Appendix — position in the roadmap

IEEE floats are the second **Tier 2** track alongside bitvectors: where the Tier 1 quartet
(polymorphic datatypes, inductive predicates, typed quantifiers, lemma functions) extends PyCSL's
*logical* reasoning over structured data, the Tier 2 tracks add *machine-level* precision —
bitvectors for bits, floats for rounding. They interlock: the float↔bitvector converters (§6) join
the two Tier 2 tracks, error-bound contracts (§5) are stated with quantifiers and discharged with
lemma functions, and a float can be a payload in a polymorphic datatype. The unifying principle
holds once more — each feature is a thin Python-facing surface over a capability Why3 already
implements, here the `ieee_float` library layered, as requested, **on top of** the existing real
model.
