# PyCSL Enhancement Proposal: Bitvectors

**Status:** Draft / high-level design
**Scope:** fixed-width integer types, bit operators, conversions, static semantics, WhyML lowering, soundness
**Audience:** PyCSL maintainers, contract authors
**Relates to:** `#@ assumes bounded_int(N)` (overflow-checked ints — complementary, see §2); `#@ lemma` (bridge proofs)
**Non-goal:** implementation patches — this specifies *what* must hold, not the diff.

---

## 1. Motivation

PyCSL can reason about integer *magnitude* (`bounded_int(N)` adds overflow proof obligations to
`+`, `-`, `*`), but it cannot reason about integer *bits*. Programs whose correctness depends on
bit-level behaviour are therefore out of reach or, worse, silently unsound when bitwise operators
are treated as opaque integer operations:

- masks and bitfield extraction (`(x >> k) & mask`),
- two's-complement / modular wraparound (`a + b` mod 2³²),
- bit-twiddling idioms (`x & (x-1)`, `x & -x`, population count, parity),
- hashing, checksums, flag registers, and packed encodings.

Why3 provides a dedicated, decidable, **bit-precise** path: the `bv` library with fixed-width
modules `BV8`/`BV16`/`BV32`/`BV64`, and SMT backends implement the FixedSizeBitVectors theory
natively (efficient bit-blasting, plus overflow-detection operators). This proposal surfaces
fixed-width machine words in PyCSL and lowers their operations to Why3 bitvectors.

## 2. Where bitvectors sit (vs `bounded_int`)

These are **complementary** machine-integer models, distinguished by their arithmetic semantics:

| Aspect | `#@ assumes bounded_int(N)` | **bitvector types** (new) |
|---|---|---|
| Value model | mathematical `int` with bounds | two's-complement N-bit word |
| `+ - *` | overflow **proof obligation** | **modular wraparound** (no VC) |
| Bitwise `& \| ^ ~ << >>` | not modelled bit-precisely | native, bit-precise |
| Signedness | inherent to `int` | part of the type (`uintN` / `intN`) |
| Why3 target | `mach.int` (ranged int) | `bv.BVN` |
| Use when | "my arithmetic must not overflow" | "my masks/shifts/wraparound are correct" |

A single function may use both — e.g. a `bounded_int` loop counter alongside a `uint32` hash
accumulator — with **explicit conversions** at the boundary (§5).

## 3. Surface model

Fixed-width integer types are introduced as PEP 484-style annotations, parameterized by width and
signedness:

```
bvtype ::= "uint8" | "uint16" | "uint32" | "uint64"
         | "int8"  | "int16"  | "int32"  | "int64"
```

Semantics: arithmetic `+ - *` is **modular** (wraps mod 2ᴺ, no overflow VC — that is the defining
difference from `bounded_int`); bitwise operators have their exact bit meaning; signedness selects
the meaning of `>>`, comparisons, and `//`/`%`.

```python
#@ ensures (\result & (\result - 1)) == 0      # result has at most one set bit
#@ assigns \nothing
def lowest_set_bit(x: uint32) -> uint32:
    return x & (~x + 1)                         # == x & -x, isolates the lowest set bit

#@ requires 0 <= k and k < 32                   # shift-range obligation (§7.2)
#@ ensures \bv_to_uint(\result) < 2             # an extracted bit is 0 or 1
#@ assigns \nothing
def get_bit(x: uint32, k: int) -> uint32:
    return (x >> k) & 1
```

Integer literals take the bitvector type of their context when unambiguous (`x & 1` reads `1` as
`uint32`); otherwise an explicit conversion is required (§5).

## 4. Operators and their lowering (Module 6)

A `uint32`/`int32` value lowers to Why3 `BV32.t` (similarly BV8/BV16/BV64). Operators map to the
`bv` module functions; **signedness selects the variant**:

| Python (operands of type `BVN`) | Meaning | Why3 (`BVN.`) |
|---|---|---|
| `a & b`, `a \| b`, `a ^ b`, `~a` | bitwise | `bw_and`, `bw_or`, `bw_xor`, `bw_not` |
| `a << k`, `a >> k` (`k : int`) | shifts | `lsl`, and `lsr` (unsigned) / `asr` (signed) |
| `a + b`, `a - b`, `a * b` | modular arith | `add`, `sub`, `mul` |
| `-a` | two's-complement negate | `neg` |
| `a < b`, `<=`, `>`, `>=` | comparison | `ult`/`ule`/… (unsigned) or `slt`/`sle`/… (signed) |
| `a == b`, `a != b` | equality | `eq` / `<>` |
| `a // b`, `a % b` | div / rem | `udiv`/`urem` (unsigned) or `sdiv`/`srem` (signed) |

Shifts by a bitvector amount lower to `lsl_bv`/`lsr_bv`/`asr_bv`; the `int`-amount forms above use
`lsl`/`lsr`/`asr` guarded by §7.2.

## 5. Conversions (the friction point)

There is **no implicit coercion** between widths, between signedness, or between bitvectors and
`int`. All crossings are explicit, with truncation/extension semantics made visible:

| Form | Meaning | Why3 |
|---|---|---|
| `\bv_to_uint(x)` | unsigned value `0 .. 2ᴺ-1` as `int` | `BVN.to_uint x` / `t'int` |
| `\bv_to_int(x)` | signed value as `int` | `BVN.to_int x` |
| `\bv_of_int(n, N)` | `int` → N-bit word, mod 2ᴺ | `BVN.of_int n` |
| `\bv_cast(x, M)` | width change (truncate/zero/sign-extend) | the `BVN`↔`BVM` converters |

Bitvector reasoning is decidable and fast in isolation, but goals that **mix** bitvector and
unbounded-`int` reasoning across these bridges are the known hard case (the Dafny bit-vector
cookbook documents exactly this for width casts and shift amounts). PyCSL's guidance: keep a
computation in one domain where possible, and discharge cross-domain equalities with a `#@ lemma`
(small-width helper lemmas, the cookbook technique). This mirrors the float↔real and
polymorphism-encoding caveats elsewhere in the toolchain.

## 6. Contract-level operators

Permitted in `#@ requires`/`#@ ensures`/loop invariants, in addition to the bitwise operators on
bv-typed terms: `\bv_to_uint`, `\bv_to_int`, `\bv_of_int`, `\bv_cast` (§5), and `\nth(x, i)` — the
`i`-th bit of `x` as a boolean (lowers to `BVN.nth`). Width constants (`\bv_width(x)`) are
available for generic bounds.

## 7. Soundness (mandatory rules)

1. **No implicit coercion.** Width changes, signedness changes, and int↔bv crossings must be
   explicit (§5). Silent truncation is the dominant unsoundness in bit-level code and is rejected.
2. **Shift-range obligation.** For `a << k` / `a >> k` with `k : int`, a proof obligation
   `0 <= k and k < width` is generated (out-of-range shift behaviour is otherwise platform/word
   dependent). Authors may instead use a bitvector shift amount, which is total.
3. **Division/remainder nonzero.** `a // b` / `a % b` generate `b != 0`, as for integers.
4. **Same-type bitwise operands.** `&`, `|`, `^` require operands of identical width and
   signedness; mixing requires an explicit `\bv_cast`.
5. **Signedness honoured.** `>>`, comparisons, and `//`/`%` lower to the unsigned or signed Why3
   function according to the operand type; an author cannot accidentally get unsigned comparison on
   a signed value.

## 8. Model-vs-runtime faithfulness (honest caveat)

A bitvector annotation is a **contract-level** type, as with every other PyCSL type. CPython
integers are unbounded and do **not** wrap, so the verified bitvector model (modular arithmetic)
is faithful to the running Python program only where the code actually realises wraparound — e.g.
by masking (`& 0xFFFFFFFF`). PyCSL verifies the program *as a bitvector program*; matching real
CPython semantics is the author's responsibility (explicit masking, or treating the `uintN`
annotation as an assertion that values stay in range). This is the same model/runtime gap as
`float`→`real`, and the spec states it rather than hiding it. (A future option in §12 is to have
PyCSL insert or check the masking automatically.)

## 9. Module impact

| Module | Change |
|---|---|
| **Module 2 — Parser** | recognise `uintN`/`intN` annotations; accept bitwise operators in contract expressions on bv-typed terms; parse `\bv_*` / `\nth` |
| **Module 3 — Weaver** | carry the width/signedness of each typed binding |
| **Module 4 — Semantic Analyzer** | enforce §7 (no implicit coercion, same-type bitwise, shift-range & div VCs, signedness); literal-typing rules |
| **Module 5 — IR Emitter** (`ir_schema`) | bv-typed nodes carrying `(width, signed)`; conversion nodes |
| **Module 6 — WhyML Transpiler** | emit `use bv.BVN`; map operators per §4 by signedness; emit conversions per §5; attach shift/div preconditions |

## 10. Phasing

| Phase | Delivers | Risk |
|---|---|---|
| **P1 — Bit logic** | `uintN`/`intN` types; `& \| ^ ~`, equality; pure single-width bv reasoning | low; native SMT bv, no bridges |
| **P2 — Shifts & arithmetic** | `<< >>` with shift-range VCs; modular `+ - *`; signed/unsigned comparisons; `// %` with nonzero VC | low–medium |
| **P3 — Conversions** | int↔bv and cross-width casts (§5); `\bv_*`/`\nth` contract operators; bridge-helper lemma patterns | medium; mixed-theory goals |
| **P4 — Integration** | interplay with `bounded_int`; float↔bv converters; optional auto-masking for CPython faithfulness (§8); rotations / popcount intrinsics | medium |

Each phase ships corpus drivers in the existing numbering style: PASS demos (isolate-lowest-bit,
power-of-two test `x & (x-1) == 0`, bitfield extract, a popcount loop with a bit-counting
invariant) and FAIL twins — a **width mismatch without a cast**, a **shift without a range guard**,
a **signed/unsigned comparison confusion**, and a **division without a nonzero precondition** —
all of which must be rejected or fail to discharge.

## 11. Validation

- **Bit-precision corpus:** the idioms above verify automatically, demonstrating reasoning that is
  hopeless when `&`/`<<` are treated as opaque integer operations.
- **Soundness gates:** the FAIL twins (§10) confirm Module 4 rejects implicit coercion,
  unguarded shifts, and signedness mistakes.
- **Bridge corpus:** a small int↔bv example that needs a helper `#@ lemma` to close, validating
  the §5 guidance and the lemma-function interplay.
- **Encoding check:** generated WhyML typechecks and dispatches to a bitvector-capable backend
  (e.g. Z3/CVC5/Bitwuzla), confirming the FixedSizeBitVectors path is exercised.

## 12. Open questions

1. **CPython faithfulness.** Should PyCSL *insert* masking to make the bitvector model match the
   running program, *check* that the author masked, or simply *document* the gap (current default)?
2. **Bridge automation.** Can common int↔bv lemmas (small-width casts, shift/cast commutation) be
   provided as a built-in library so authors don't re-derive the cookbook lemmas?
3. **Arbitrary widths.** Beyond 8/16/32/64 — are parameterised widths (`uint<N>`) worth the
   complexity, given Why3 supports additional `BVN` via cloning?
4. **Bitvectors as indices / memory.** Interaction with the array/memory model when an address or
   index is a `uintN`.
5. **Mixed-theory performance.** Heuristics for when to keep a value in bv vs int to avoid the
   slow combined-theory goals.

---

### Appendix — position in the broader roadmap

Bitvectors are a **Tier 2** capability: unlike the Tier 1 quartet (polymorphic datatypes,
inductive predicates, typed quantifiers, lemma functions), which extend PyCSL's *logical*
reasoning over structured data, bitvectors open a distinct audience — systems, embedded, hashing,
and packed-encoding code — by giving PyCSL *machine-level* precision. The two tiers compose: a
bitvector accumulator can be a payload in a polymorphic datatype, a bit-level invariant can be
stated with a quantifier, and an int↔bv bridge is discharged with a lemma function. Each remains a
thin Python-facing surface over a capability Why3 already implements — here, the `bv` library and
the SMT FixedSizeBitVectors theory.
