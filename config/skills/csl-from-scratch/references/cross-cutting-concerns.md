# Cross-cutting concerns

Operational concerns that span phases. Load when navigating a
specific boundary question (annotation-vs-proof, auto-trust,
test-numbering, RAG, layer terminology, TCB tiers).

---

## The annotation-vs-proof gap

The surface `#@` syntax must be *projectable from / to* the
formal AST. Discrepancy here silently breaks trust. Defend it
with a round-trip theorem (PyCSL's `Phase1d_StmtToIr.v`
`stmt_to_ir_simple_roundtrip`) and with a byte-diff between
the extracted formal `emit_stmt` and the actual Python Module
6 output on the reference corpus.

## Auto-trust as safety valve

When Module 6 can't represent a pattern, auto-trust the
enclosing function: emit a `val` (contract-only WhyML
declaration) instead of `let` (full body). Track the patterns;
close them via Phase 5 refactors. PyCSL pattern:
`_should_auto_trust_*` predicates in
`src/pycsl/module6_whyml/auto_trust.py`. Examples:

- `_should_auto_trust_array_return`: array-returning functions
  with early returns (Why3 forbids `array int` in exception
  payloads).
- `_should_auto_trust_set_op`: BinOp(`|`/`&`/`^`/`-`) on
  map-typed operands (Python's set-union doesn't lower cleanly).
- `_should_auto_trust_map_return`: functions returning
  `set`/`dict`/`frozenset` — semantics lost in the lowering.

Each auto-trust trigger is a *bug in the verifier*, not in the
user's code. Track them as a queue and close them.

## Reference test discipline

- **Never renumber.** Tests are load-bearing; the traceability
  matrix references them by ID. If 0142 deprecates, leave 0142's
  slot empty; add 0143 for the replacement.
- **Numbered ranges**: 0001-0199 host-language coverage,
  0200-0499 annotation coverage, 0500-0999 stdlib + memory
  models, 1000+ regression tests for closed bugs.

## Skills + RAG for LLM annotation assistance

Once the *CSL is mature, LLM agents can write annotations for
you. Skill files in `config/skills/` become the RAG corpus.
PyCSL's pattern:

- `config/skills/<skill>/SKILL.md` — markdown with frontmatter.
- `src/skill2rag/` — indexer (Chroma vector store).
- `bin/skill2rag` CLI — `build`, `query`, `chunks`.
- Agents under `src/pycsl/agents/` — annotation generators
  reading the RAG index for relevant context.

**Don't build the agent infrastructure too early**. The agents
work on the *mature* surface, not the under-construction one.
Start at Phase 8+, not Phase 1.

## Layer terminology

PyCSL's discovered layering (cite
[`self-annot-2.md`](../../../../self-annot-2.md)):

- **Layer 0** — formal semantics (Rocq + Lean theorems).
- **Layer 1** — `\trusted reviewer:` no-proof gate on the
  self-annotate source.
- **Layer 2** — full-proof per-module verification.
- **Layer 3** — Why3 trust val-spec module (cert-as-witness).
- **Layer 4** — IR-shape correspondence (`ir_to_stmt`
  round-trip).

## TCB tiers

Cite [`docs/glossary/trusted-computing-base.md`](../../../../docs/glossary/trusted-computing-base.md):

- **0a** — verified, axiom-free. Theorems closed under the
  global context with no PyCSL-specific assumptions.
- **0b** — standard kernel axioms (propext, funext for Coq;
  propext, Classical.choice, Quot.sound for Lean).
- **1** — named PyCSL-specific axioms (auditable, replaceable).
- **2** — `\trusted reviewer:` modules (out of formal scope by
  design).
- **3** — meta-level (parsers, canonicalizers, audit
  state-machines).
- **4** — tool stack (Coq, Lean, OCaml, Why3, SMT solvers,
  opam, …).

Every assumption in the verifier maps to exactly one tier. The
tier inventory is the README of the trust chain.
