# sugar-for-impl.md — implementation plan for the `#@ for` contract-expansion sugar

**Status:** Implementation plan (derives from `sugar-for-spec.md`)
**Implements:** the `#@ for VAR in range(lo, hi):` block that desugars to ground `requires`/`ensures`.

The guiding fact: `#@ for` is **front-end desugaring to existing clauses**. Modules 4–6 (semantic
analysis, IR emission, WhyML translation) **do not change** — they only ever see the expanded ground
clauses. Two existing mechanisms are the templates, so this is an *additive* feature on well-trodden
paths, not new machinery:

- **Block-header folding** already parses indentation-significant `#@` blocks: `Module1_Ingestor`'s
  `_BLOCK_HDRS` / `_match_block_hdr` / `_fold_blocks` handle `#@ act NAME:`, `#@ happy NAME:`,
  `#@ inductive NAME(sig):` with bodies "exactly four spaces deeper than the header."
- **Clause desugaring** already expands a compact clause into ordinary `requires`/`ensures`:
  `Module3_Weaver._desugar_acts` (and the HAPPY meta-pass) turn `act`/`complete`/`disjoint` into plain
  clauses.

`#@ for` slots into both: a new block header (like `inductive`) whose body is desugared (like `act`).

---

## 1. Where each piece lives (the four touchpoints)

| Stage | Change | Template to follow |
|---|---|---|
| **Module1 (Ingestor)** | recognise `for VAR in range(...):` as a block header; fold its 4-space body | `_BLOCK_HDRS`, `_match_block_hdr`, `_fold_blocks` (as for `inductive`) |
| **Module2 (Parser)** | grammar production for the folded `for`-block → a `ForExpand` CSL node | `act_block`/`inductive_decl` productions + the `Act`/`Inductive` node classes |
| **Module3 (Weaver)** | desugar each `ForExpand` into ground `requires`/`ensures` (unroll + substitute) | `_desugar_acts` |
| **Module4 (SemanticAnalyzer)** | validate the `ForExpand` *pre-desugar* (the §5 well-formedness rules) | `_validate_acts` |
| **Modules 5–6** | **no change** — they receive the desugared ground clauses | — |

## 2. Component plan

### C1 — Module1: recognise and fold the `for` header
- Add `_FOR_HDR = re.compile(r"^\s*for\s+(\w+)\s+in\s+range\s*\(([^)]*)\)\s*:\s*$")` and append
  `("for", _FOR_HDR)` to `_BLOCK_HDRS`. Group 1 = the index var; group 2 = the raw range-args string.
- `_match_block_hdr` returns `("for", "<var> in range(<args>)")` (or a small structured payload) so the
  folded header reconstructed for Module2 carries the var and the range arguments verbatim — exactly as
  `happy NAME(param):` preserves its parameter in the reconstructed header.
- `_fold_blocks` already collects the deeper-indented body lines; the `for` block folds identically to
  `inductive` (header + the run of 4-space-deeper `#@` clause lines).
- **No change to indentation handling** — reuse `_indent_width` (spaces-only; tabs already rejected).

### C2 — Module2: grammar + `ForExpand` node
- Add a `for_block` production to the contract grammar (alongside `act_block`, `inductive_decl`), parsing
  `for VAR in range( bound (, bound)? ) : <clause>+` where each `<clause>` is an ordinary
  `requires`/`ensures` clause (reuse the existing clause productions; the index `VAR` parses as a normal
  identifier inside clause expressions).
- Add a `ForExpand` CSL node (mirroring `Act`) holding: `var: str`, `lo: expr`, `hi: expr` (parsed
  bound expressions; one-arg `range(hi)` sets `lo` to the integer literal `0`), and
  `body: List[clause-node]`.
- The body clauses are stored **unsubstituted** (with `VAR` still free); substitution happens in
  Module3.

### C3 — Module3: the desugar (`_desugar_for`)
The core. For each `ForExpand`:
1. **Resolve the bounds to integers** (§3 below). On failure → fail-loud error.
2. For `m` in `range(lo, hi)` (ascending, upper-exclusive), for each body clause `Cⱼ`: produce
   `Cⱼ[VAR := IntLit(m)]` — a deep copy of the clause AST with every `Name(VAR)` replaced by an integer
   literal node (§3 below).
3. Splice the produced clauses into the function's contract list **in place of** the `ForExpand`, in
   iteration-then-body order, so downstream sees an ordinary clause sequence.
- Runs in the same desugar phase as `_desugar_acts` (before the IR is emitted); the `ForExpand` node may
  be stashed (like `node.csl_acts`) for Module4 to validate against, then dropped.

### C4 — Module4: validate pre-desugar (`_validate_for`)
Enforce the §5 well-formedness rules on the `ForExpand` node (before/independently of expansion), each a
hard error at the header line: non-constant bound; non-integer or shadowing index; empty body or a body
clause not mentioning `VAR`; a disallowed body clause kind; a nested `#@ for`.

## 3. The two non-trivial bits

### 3a — Static-bounds resolution
- **v1: integer literals only** (`range(0, 4)`, `range(64)`). `lo`/`hi` must be literal-int expr nodes;
  anything else is the §5 "non-constant bound" error. This covers the codec (all bounds are literals).
- **v1.1 (follow-on): named integer constants** (`range(0, NUM_BLOCKS)`). Requires threading the
  module's resolved integer constants (the `O_RDONLY = 0`-style module literals) into the desugar so a
  `Name` bound can be looked up. Staged second because it needs the constant table at desugar time; the
  v1 literal-only path is unblocked without it.
- **Never** fall back to `\forall` or to skipping expansion on a non-constant bound — fail loud (§5.1).

### 3b — Index substitution
- A pure syntactic substitution over the parsed clause AST: replace each `Name` node whose id equals
  `VAR` with an `IntLit(m)` node; recurse through all expression children. Deep-copy the body clause per
  iteration so the iterations are independent.
- `VAR` is integer-typed and appears only in integer positions; the substitution does not need typing —
  it is a literal-for-name replacement, and the resulting clause is type-checked normally by Module4
  *after* desugaring (so a misuse of `VAR` surfaces as an ordinary clause type error on the expanded
  form).

## 4. Error handling (fail-loud, per spec §5)
Each reported against the header line with context:
- non-constant `lo`/`hi`; reversed/empty range is allowed but warns (inert, zero clauses);
- index `VAR` shadows an in-scope name, or is used in a non-integer position (the latter caught
  post-desugar as a clause type error);
- empty body, a body clause not mentioning `VAR`, or a disallowed clause kind;
- a nested `#@ for` (v1).

## 5. Build order (phased; each step independently testable)
1. **C1+C2 (parse only).** Recognise + fold + parse a `for`-block into a `ForExpand` node; assert the
   node shape on a unit input. No desugar yet. Gate: parses; existing corpus byte-clean (additive
   grammar must not perturb other parses).
2. **C3 (desugar, literals).** Implement `_desugar_for` for literal bounds + substitution. Gate: a tiny
   driver with `#@ for i in range(0,4): requires …` desugars and proves; **the desugared clauses match a
   hand-written reference** (the equivalence check).
3. **C4 (validation/errors).** Add the fail-loud checks; gate with the expected-error drivers.
4. **v1.1 (named constants).** Thread the constant table; gate with `range(0, NUM_BLOCKS)`.

## 6. Testing
- **Headline equivalence (acceptance §9.1).** Rewrite the os inode codec's hand-written clauses (the 18
  field-range `requires`, the per-byte `ensures`, the 64-byte read requires) with `#@ for`; assert the
  generated WhyML is **byte-identical** to the current hand-written form (the corpus byte-diff harness)
  and `codec.py` still proves unchanged. This is the proof that the sugar is meaning-preserving.
- **Ground-output check.** Inspect the desugared clauses / generated WhyML for a `#@ for` block — no
  quantifier introduced by the sugar.
- **Reference corpus.** A new `pycsl-reference` driver exercising a small `#@ for` requires+ensures
  (proves), plus sibling expected-error drivers (non-constant bound; nested `for`; body clause not
  mentioning the index).
- **Idempotence/order.** A block with multiple body clauses expands in iteration-then-body order
  (assert against the reference).

## 7. Documentation (parity, per the doc-coherency discipline)
- **Concrete syntax reference:** the `for`-block production + the four-space-body rule (cross-referencing
  the sibling block headers).
- **Static semantics reference:** the §5 well-formedness rules (static bounds, integer index, body
  constraints) + their error codes.
- **Translational reference:** a one-line note that `#@ for` is **pre-clause desugaring** — it produces
  existing `requires`/`ensures` and therefore adds **no new translation rule** (the key point for the
  small audit surface).
- **README + a skill:** the `\forall`-vs-`for` authoring guidance (spec §7).
- **`test-suite/annotations.md`:** the canonical paragraph for the construct (the doc-coherency source of
  truth), so `bin/doc-coherency.py --check` stays green.

## 8. Risks (small, by construction)
- **Indentation edge cases** (mixed depth, blank `#@` lines inside a block) — reuse `_fold_blocks`'
  existing handling; add unit cases. Low risk (the mechanism is proven by `act`/`inductive`).
- **Bound resolution scope** — v1 literal-only avoids the constant-table threading; the named-constant
  follow-on is the only part touching how constants reach the weaver.
- **Grammar regression** — an additive production could in principle perturb existing parses; the
  full-corpus byte-diff gate (step 1) catches it.
- **Faithfulness** — none beyond the clauses produced; the byte-identical codec test *is* the soundness
  argument (the sugar must be indistinguishable from hand-writing).
