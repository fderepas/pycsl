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

PyCSL's discovered layering:

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

## Keep values prover-known (the opacity squeeze)

A functional proof can only constrain values the SMT prover can
*see*. The recurring failure mode is an expression that lowers to
an **opaque** symbol — an uninterpreted `val` whose value is
unconstrained — so any goal that bounds or relates it is
unprovable (or worse, *vacuously* discharged when the spec itself
degenerated). Most "why won't this discharge?" debugging in PyCSL
reduces to: something that is concrete in the Python is opaque in
the WhyML. Prefer the concrete lowering at every step:

- **Class-level constants → literals.** `self.CAP` for a class-body
  `CAP = 64` lowers to the literal `(64)` (Module 5
  `_collect_class_constants` → `type_decls[...]["constants"]`;
  Module 6 `_handle_field_get_expr` resolves it via
  `_class_constants`). Before this, a class constant was an opaque
  `getattr_<cls>` and every bound against it failed — which is why
  the de-trusted `UnixInodeFileSystem` had to hand-inline `512`
  for `BLOCK_SIZE`. Now `self.CONST` is usable directly in
  `requires`/`ensures`/bodies.
- **Slice-read → `Array.sub`, slice-write → `Array.blit`.** Both
  carry content postconditions (`result[i] = a[ofs+i]` /
  `dst[dofs+i] = src[sofs+i]`), so a round-trip `sub(blit(x)) = x`
  closes in pure Why3. An opaque `array_slice` val does not.
- **Read packed integers arithmetically, not via `struct.unpack`
  of unknown bytes.** `disk[o]*256 + disk[o+1]` keeps the value
  concrete; `struct.unpack` of bytes the prover didn't watch a
  matching `pack` write yields an opaque head.
- **`\array_eq` (and any spec emitting a `forall`) is vacuous
  outside the `hoare` memory model** — it lowers to `true` under
  other models. Corpus tests that assert array equality MUST carry
  `# pycsl-flags: --memory-model hoare`, or they pass while proving
  nothing.
- **A free function over a module-global object verifies only
  *vacuously*.** Reads/calls on an undeclared global (`_fs.method()`,
  `_fs.field[i]`) emit abstract `val` ops and pass with no real
  obligation. The proven pattern for "self == a modeled object" is
  a **self-contained class** that re-declares its fields + class
  invariants (cf. corpus `0427`/`0428`); cross-file inheritance is
  *not* modeled (`visit_ClassDef` ignores `node.bases`).

Two contract idioms that exploit this:

- **`raises X when C` does not validate `X`** against
  `KNOWN_EXCEPTIONS` (only `no_exception` does). A plain
  `raise X` in the body declares the WhyML exception via
  `collect_user_exceptions`, so domain exceptions
  (`FileNotFoundError`, …) work with no exception-model change.
- **`assigns \nothing` buys referential transparency.** If a
  pure helper `h(...)` is `assigns \nothing`, re-invoking it inside
  a `raises … when h(...) …` clause equals the body's local binding
  of the same call, so a raise guarded by exactly its `when`
  condition discharges as a trivial `C → C`. The strong functional
  spec of `h` is then needed only for *meaning*, not for the
  raise-site VC.
