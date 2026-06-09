# sugar-for-spec.md — specification of the `#@ for` contract-expansion sugar

**Status:** Specification (what the construct *is* and *means* — no implementation wiring)
**Date:** 2026-06-09

A `#@ for` block is **bounded macro-expansion** for contract clauses: it lets a fixed, repetitive set of
`#@` clauses (e.g. the codec's 18 inode field-range `requires` or 64 byte-range `ensures`) be written
once as a loop over a *compile-time-constant* range, and **desugars to the exact ground clauses** a
human would otherwise type by hand. It is a front-end convenience only — it introduces **no new logical
construct** and changes **no semantics**.

---

## 1. Motivation

Two reasons, both concrete:

- **Readability.** Today a fixed-size byte/field structure forces long, error-prone runs of
  near-identical clauses:
  ```
  #@ requires 0 <= data[offset + 0] and data[offset + 0] <= 255
  #@ requires 0 <= data[offset + 1] and data[offset + 1] <= 255
  #@ requires 0 <= data[offset + 2] and data[offset + 2] <= 255
  #@ requires 0 <= data[offset + 3] and data[offset + 3] <= 255
  ```
  One indented loop expresses the same intent without the copy-paste.

- **Proof cost — the decisive distinction from `\forall`.** A logical quantifier
  `\forall i; (0 <= i and i < 4) ==> P(i)` in a `requires`/`ensures` is **expensive**: the SMT backend
  must instantiate it by trigger-based E-matching at every goal that sees it, and that cost compounds.
  The `#@ for` sugar instead produces **ground** clauses `P(0) … P(3)` — no quantifier, no instantiation
  search. So it delivers loop-level readability with the proof cost of plain ground facts. This is the
  same lever that the os codec work needed: fixed-size repetitive obligations want ground expansion, not
  a quantifier.

`#@ for` is therefore a *compaction of hand-written clauses*, explicitly **not** a substitute for
`\forall` (which remains the tool for symbolic or unbounded properties). §7 states the guidance.

## 2. Syntax (surface form)

A `#@ for` block is a block-header `#@` line followed by an indentation-significant body, mirroring the
existing own-line block headers (`#@ act NAME:`, `#@ happy NAME:`, `#@ inductive NAME(sig):`), whose
clauses sit **exactly four spaces deeper than the header**:

```
#@ for <var> in range(<lo>, <hi>):
#@     <clause-1 using <var>>
#@     <clause-2 using <var>>
#@     ...
```

- `<var>` is a single identifier (the loop index).
- `range(<lo>, <hi>)` and the one-argument `range(<hi>)` (meaning `range(0, <hi>)`) are accepted; the
  three-argument `range(<lo>, <hi>, <step>)` is reserved for a later revision (see §8).
- Each body line is an ordinary contract clause (`requires`/`ensures` in the first version — §3) that may
  mention `<var>` in any integer position (array index, arithmetic, comparison).
- Indentation is the block delimiter: the body is the maximal run of `#@` lines indented deeper than the
  header; the first `#@` line at the header's indentation (or shallower) ends the block.

Example (the codec excerpt above, sugared):
```
#@ for i in range(0, 4):
#@     requires 0 <= data[offset + i] and data[offset + i] <= 255
```

## 3. What may appear in the body (scope of v1)

- **In scope:** `requires` and `ensures` clauses. These are the repetitive, high-payoff cases (codec
  byte/field ranges, fixed-width readback equalities).
- **Deferred (later revision):** `assigns` regions and `loop invariant` bodies driven by `#@ for`. They
  are not precluded by the model below, only out of the first cut.
- A body clause **must mention `<var>`** at least once (a body clause independent of `<var>` would
  produce identical copies — a likely mistake; flagged, not silently expanded).

## 4. Semantics — the desugaring (meaning-preserving)

Let a `#@ for v in range(lo, hi):` block have body clauses `C₁ … Cₖ`. Its meaning is **exactly** the
clause sequence obtained by:

1. Evaluating `lo` and `hi` to integers at expansion time (they must be compile-time constants — §5).
2. For each integer `m` in the Python range `[lo, hi)` (lower-inclusive, **upper-exclusive**), in
   ascending order:
   - emit `C₁[v := m], C₂[v := m], …, Cₖ[v := m]`, where `Cⱼ[v := m]` is `Cⱼ` with every occurrence of
     `v` replaced by the **integer literal** `m`.
3. The emitted clauses take the place of the block, in order, as if hand-written there.

Consequences that are part of the contract of this feature:

- **Ground output.** Because `v` becomes a literal, every emitted clause is quantifier-free (unless the
  body clause itself contains a `\forall` the author wrote). The expansion adds no quantifier.
- **Count.** The block expands to exactly `(hi - lo) × k` clauses. An empty range (`hi <= lo`) expands to
  **zero** clauses (the block is inert — allowed, and a warning-worthy no-op).
- **Order-preserving.** The emitted clauses appear in iteration-then-body order, so any order-sensitive
  reading (e.g. clause-numbered documentation) is deterministic.
- **Equivalence.** The sugared form and the corresponding hand-written clauses are **indistinguishable**
  to every downstream stage — same well-formedness, same generated WhyML, same verification conditions.
  `#@ for` is a *spelling*, not a meaning.

## 5. Well-formedness constraints

A `#@ for` block is well-formed iff:

1. **Static bounds.** `lo` and `hi` are integer literals, or named constants resolvable to integers at
   expansion time. A non-constant bound (a parameter, a runtime expression) is a **hard, fail-loud
   error** — never a silent fallback to `\forall` or to skipping expansion. (The intended use is
   fixed-size structures, where the bounds are always constants.)
2. **Integer index.** `<var>` ranges over integers and is used only in integer positions. It is bound
   **only** within the block; it must not shadow an in-scope name, and it does not escape the block.
3. **Non-empty body**, each line a permitted clause kind (§3), each mentioning `<var>`.
4. **No nesting** in the first version: a `#@ for` body may not contain another `#@ for` (deferred — §8).
5. **Indentation** is exactly four spaces deeper than the header, consistent with the other block
   headers; ragged or tab indentation is an error.

Errors are reported against the header line with enough context to locate the offending bound/clause.

## 6. Faithfulness and soundness

- **No new trust, no new semantics.** Because the block desugars to ordinary ground clauses that already
  have a defined meaning, it adds nothing to the trusted computing base and introduces no new proof
  obligation kind. Soundness is inherited from the clauses it expands to.
- **Auditable.** The expansion is observable: the desugared `#@` clauses can be emitted/dumped and
  compared against a hand-written reference. This makes the equivalence (§4) checkable, not assumed.
- **Faithful to Python.** `range` semantics match Python exactly (upper-exclusive; `range(n)` ≡
  `range(0, n)`), so a reader's Python intuition is correct — no off-by-one surprises.

## 7. Relationship to `\forall` (authoring guidance)

Both express "a property over a set of indices," but they are not interchangeable:

| | `#@ for i in range(a, b):` | `\forall i; (a <= i and i < b) ==> P(i)` |
|---|---|---|
| Kind | macro: expands to ground clauses | logical quantifier |
| Bounds | must be **compile-time constants** | may be **symbolic / unbounded** |
| SMT cost | none beyond the ground facts | trigger-based instantiation (E-matching) |
| Use when | a **fixed-size** structure (codec bytes, struct fields, a 16-slot table) | the bound is symbolic, or the set is large/unbounded |

Rule of thumb: **fixed and small → `#@ for`; symbolic or unbounded → `\forall`.** The first buys
readability without proof cost; the second buys generality at instantiation cost.

## 8. Out of scope (this revision)

- `range(lo, hi, step)` (the three-argument form) and reverse ranges.
- Nested `#@ for` blocks.
- `#@ for`-driven `assigns` regions and `loop invariant` bodies.
- Iterating over anything other than an integer `range` (no `for x in [list]`, no `enumerate`).
- Any change to `\forall` or to the downstream clause kinds — `#@ for` only *produces* existing clauses.

## 9. Acceptance criteria

1. **Byte-identical equivalence (the headline test).** Rewriting the os inode codec's hand-written
   clauses with `#@ for` (the 18 field-range `requires`, the per-byte `ensures`, the 64-byte read
   requires) desugars to clauses that produce **byte-identical generated WhyML** to the current
   hand-written form — i.e. `codec.py` still proves exactly as it does today, and the corpus emission is
   unchanged for the rewritten files.
2. **Ground output.** The expansion of a `#@ for` block contains **no quantifier** introduced by the
   sugar (verified by inspecting the desugared clauses / the generated WhyML).
3. **Error behavior.** A non-constant bound, an empty/ill-formed body, a shadowing index, or nested
   `#@ for` each produce a clear, fail-loud error at the header line — never silent expansion or a
   silent fallback.
4. **Reference corpus.** A new corpus driver exercises a `#@ for` block (a small fixed-size requires and
   ensures) and proves; a sibling driver with a deliberately wrong bound is a documented expected error.
5. **Documentation parity.** The construct is documented across the normative surfaces (concrete syntax,
   static semantics, translational — the last noting it is *pre-clause desugaring*, producing no new
   translation rule) and the authoring-guidance distinction from `\forall` (§7) is recorded.
