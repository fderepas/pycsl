# PyCSL Refactoring Proposal: A Language-Agnostic Core (IR Schema + WhyML Backend)

**Status:** Draft / high-level design
**Scope:** architecture, the front-end/core boundary, the IR as a stable interface, the WhyML backend, conformance testing, migration
**Audience:** PyCSL maintainers; prospective GoCSL / CCSL implementers
**Motivation source:** the port discussion (avoid triplicating the backend) and the field report (honest signals, structured diagnostics)
**Non-goal:** new contract features (those are separate proposals); changing WhyML/Why3 semantics; self-verification.

---

## 1. Goal

PyCSL's value is mostly **language-agnostic**. The Python-specific work is confined to the early
stages (ingest source, parse via libcst, weave contracts onto the AST by line number). The hard,
corpus-tested machinery — the IR, the WhyML emitter, the memory and exception models,
`proof2why3`, the audit, and the proof orchestration — is about lowering *an imperative IR plus
contracts* to WhyML and has nothing to do with Python.

This proposal draws an explicit seam through the existing pipeline so that:

1. the language-agnostic core (IR → WhyML → proof) is a **single component**, hardened once;
2. each source language (Python today; Go and C later) is a **thin front-end** that emits a
   canonical IR and nothing more;
3. every future contract feature and every UX/agent improvement is implemented **once, in the
   core**, and is immediately available to all front-ends.

The IR is the contract between the two halves. It already exists internally (`ir_schema.py`,
emitted by Module 5, consumed by Module 6); this proposal promotes it from an implementation
detail to a **documented, versioned, serializable interface**.

## 2. Current architecture (where the seam is today)

```
Python source
  → Module 1  Ingestor          ─┐
  → Module 2  Parser (libcst)    │  language-specific
  → Module 3  Weaver (line-match)─┘
  → Module 4  Semantic Analyzer  ─┐
  → Module 5  IR Emitter          │  language-agnostic in principle,
  → Module 6  WhyML Transpiler    │  but entangled with the Python AST today
  → Why3 → SMT solvers           ─┘  (+ proof2why3, audit_proof)
```

The boundary is *implied* but not enforced: the IR is an in-memory Python structure, semantic
analysis still reaches into the Python AST, and there is no serialized, validated IR document a
non-Python front-end could produce.

## 3. Target architecture

```
┌─ FRONT-END (per language) ─────────────┐      ┌─ CORE (shared, language-agnostic) ───────────────┐
│  source → AST → weave contracts        │      │  IR ingest + schema validation                   │
│  → emit canonical IR  ──────────────────────▶ │  → semantic analysis (on IR)        [Level 2]     │
│  (Python: libcst; Go: go/ast+go/types; │ IR   │  → WhyML emission (backend)         [Level 3 gen] │
│   C: libclang)                          │ doc  │  → typecheck generated WhyML        [Level 3 tc]  │
└─────────────────────────────────────────┘      │  → proof orchestration (Why3, provers, audit)    │
                                                  │  → structured diagnostics + run report           │
                                                  └───────────────────────────────────────────────────┘
```

- **Front-end** = today's Modules 1–3, per language. Its sole output is a well-formed IR document.
- **Core** = semantic analysis (re-pointed at the IR), the WhyML backend (Module 6), and proof
  orchestration. The core makes **no** language-specific assumptions.

The conceptual change to Module 5: the IR *definition* (`ir_schema`) becomes the shared interface;
the IR *construction* moves into each front-end; the core's first step becomes **IR ingest +
validation** instead of building the IR from a Python AST.

## 4. The front-end contract

Every front-end MUST emit an IR document that:

1. **conforms to the published IR schema** (§5) and declares its `ir_version` and `source_language`;
2. **carries resolved types** on every binding (the PyCSL type vocabulary — `int`, `bool`, `str`,
   `float`, declared datatypes, etc.), having already done language-native name resolution and
   type-hint interpretation;
3. **attaches every contract clause to a concrete IR node** (function, loop, statement). A contract
   that resolves to no node is a front-end error — this is precisely where the *silent
   contract-drop* failure from the field report is eliminated, because "attached to nothing" is now
   representable and rejected rather than silently lost;
4. **records a source span** (`file`, `line`, `col`, `end`) on every node, so core diagnostics map
   back to the original Go/C/Python source.

A front-end MAY assume the core will perform all *logical* well-formedness checking (§6); it is not
responsible for re-implementing the forbidden-expression rules, positivity, frame analysis, etc.

## 5. The IR schema

A formal, versioned, **language-neutral** specification, published as a machine-readable schema
(JSON Schema or a `.proto`), with a canonical serialization (recommended: JSON for tooling
friendliness; a binary form optional later).

**Node taxonomy (illustrative, not exhaustive):**

- **Module**: ordered declarations; `ir_version`, `source_language`, `memory_model`
  (`hoare`/`typed`/`store`/`concurrent`).
- **Type declarations**: algebraic datatypes (nullary/payload constructors; recursive;
  mutually-recursive groups) — the `#@ datatype` content, language-neutral.
- **Function**: typed parameters, return type, contract block, body; flags (`recursive`,
  `trusted`, `diverges`, `lemma`), `variant`.
- **Contract clauses**: `requires`, `ensures`, `assigns`, `variant`, `raises`, `no_exception`,
  behavior (`act`/`given`/`complete`/`disjoint`), class invariants — as structured nodes, not
  strings.
- **Statements**: assignment, `if`, `while`/`for` (with loop invariant/variant), `match` over a
  datatype, `return`, ghost statements, `assert`/`check`.
- **Expressions**: literals, variables, arithmetic/boolean/comparison, quantifiers (with typed
  binders), `\old`/`\at`/labels, the `\`-operator family with explicit arities, pure-function
  application, constructor application, pattern captures.
- **Source span** on every node (§4.4).

**Type system:** the IR carries the PyCSL type vocabulary explicitly; it is *semantically
analyzable* (declared types present) but the core performs the *validation* (§6). This keeps
language-native typing in the front-end and language-agnostic logic checks in the core.

**Versioning:** the IR is now a wire format between separately-versioned components. It carries a
semantic `ir_version`; the core declares the range it accepts; a compatibility policy governs
additive vs breaking changes. Every run and capability manifest is stamped with the IR and tool
versions (closing the reproducibility gap from the field report).

**Relationship to Why3's own IVL:** Why3 itself accepts an S-expression input intended as an
intermediate language (its `Ptree`). PyCSL's IR sits *above* that — it carries contracts, memory
model, and proof metadata that `Ptree` does not. The backend (§7) may therefore either emit WhyML
*text* (as today) or, as an optimization, emit Why3's S-expression `Ptree` directly; the IR schema
is independent of that choice.

## 6. The language-agnostic core

Responsibilities, in order:

1. **IR ingest & schema validation** — reject malformed IR documents with precise, located errors;
   verify `ir_version` compatibility.
2. **Semantic analysis (Level 2)** — on the IR: contract well-formedness, IR-level type checking,
   the forbidden-expression rules, datatype/positivity checks, frame (`assigns`) consistency,
   `\variant` requirements for recursion, behavior-block coverage. (Today's Module 4, re-pointed at
   the IR.)
3. **WhyML emission (Level 3, generation)** — the backend (§7).
4. **WhyML typecheck (Level 3, typecheck)** — run Why3's typechecker on the emitted WhyML and gate
   success on it. *This is the fix for the field report's most dangerous issue:* "SUCCESS" must mean
   at least well-typed WhyML, never merely "text emitted."
5. **Proof orchestration (Level 3, proof)** — Why3 task management, prover selection,
   `proof2why3`/audit for `#@ proof`, result collection.
6. **Diagnostics & run report** — structured, coded, located (§8).

The core makes no reference to Python, libcst, Go, or C. Its only input is the IR.

## 7. The WhyML backend

Today's Module 6, isolated as the core's lowering stage: IR → WhyML. It owns the memory models,
the exception model, the datatype/match lowering, and the contract-to-WhyML mapping. Two cleanups
the refactor should fold in:

- **Emit clean WhyML** — drop the dead `val constant` block for pattern-bound captures (field-report
  A5); the backend now has the full typed IR and can scope captures correctly.
- **Output mode** — default to WhyML text (`.mlw`, unchanged behaviour); optionally target Why3's
  `Ptree` S-expression to skip a re-parse. Either way the typecheck step (§6.4) runs.

## 8. Diagnostics across the boundary

Because every IR node carries a source span (§4.4), a core-detected error can be reported against
the original source line in *any* front-end's language. Diagnostics are structured and coded
(`{code, level, message, file, line, col, rule_id, suggested_fix}`), per the field report — and
the per-level status line (`L1 ✓ L2 ✓ L3-typecheck ✓ L3-proof skipped`) is emitted by the core, so
every front-end inherits honest signals for free.

## 9. Conformance testing (two corpora)

The reference corpus is PyCSL's de-facto source of truth; the refactor *splits* it to match the new
boundary:

- **Core corpus (golden IR):** language-neutral IR documents → expected WhyML and expected
  pass/fail. This tests the core *independently of any front-end*, and becomes the conformance
  suite GoCSL/CCSL implementers target.
- **Front-end corpora (source → IR):** for each language, source files → expected canonical IR.
  This tests that a front-end lowers its language correctly, decoupled from the backend.

A capability manifest (field report B1/B5) is generated from the passing core corpus, so "what the
core supports" can never drift from reality and is shared across all front-ends.

## 10. Soundness / TCB framing

This refactor sharpens the trusted-base story from the earlier TCB analysis. The core (IR → WhyML →
proof) becomes a **single, shared, safety-critical component** that can be hardened, documented, and
even partially formalized once — rather than re-implemented and re-trusted per language. Each
front-end's trust obligation is narrowed to one thing: *faithfully capturing its source language's
semantics in the IR* (the front-end-translation-soundness condition). Splitting the TCB this way
also makes it auditable: the core's IR→WhyML mapping is the obvious target for the kind of
machine-checked soundness work that already exists for parts of Why3's logic.

## 11. Migration plan (incremental, corpus-gated)

No big-bang rewrite. Each step preserves behaviour, gated by reproducing the existing corpus.

1. **Extract & document `ir_schema`** as a standalone, versioned spec with a JSON serialization;
   add a serializer/deserializer.
2. **Re-point semantic analysis at the IR** — Module 4 consumes IR, not the Python AST. Validate by
   re-running the corpus to identical results.
3. **Split the Python front-end** (Modules 1–3 + IR construction) into its own package emitting the
   serialized IR; the core now ingests IR.
4. **Add the WhyML typecheck gate** (§6.4) and structured diagnostics (§8).
5. **Carve the two corpora** (§9) and generate the capability manifest.
6. **Freeze the front-end contract** (§4) and publish the conformance suite — at which point a Go or
   C front-end can be developed against a stable target.

Each step is independently shippable and reversible.

## 12. Phasing

| Phase | Delivers | Risk |
|---|---|---|
| **P1 — IR as interface** | documented, versioned, serializable IR; round-trip serializer; corpus reproduced | low |
| **P2 — Core re-pointed at IR** | semantic analysis + backend consume IR only; Python front-end isolated | medium |
| **P3 — Honest core** | WhyML typecheck gate, structured/located diagnostics, per-level status, capability manifest | medium |
| **P4 — Conformance & second front-end** | split corpora, frozen front-end contract; a thin Go front-end (`go/ast`+`go/types`) as the first external validator | medium |

## 13. Open questions

1. **Serialization choice.** JSON (tooling-friendly, agent-readable) vs a binary/`.proto` (compact,
   typed) — or JSON now with a binary option later?
2. **How much resolution is the front-end's job?** Exactly where does name/type resolution end and
   core semantic analysis begin — what minimal typed IR must a front-end always produce?
3. **Backend output target.** Stay with WhyML text, or adopt Why3's `Ptree` S-expression to drop a
   parse step? Trade-off: stability of text vs tighter coupling to a Why3 internal format.
4. **Memory-model coverage in the IR.** Are `typed`/`store`/`concurrent` fully expressible in the
   neutral IR, or do they need model-specific extensions?
5. **Versioning policy.** What counts as an additive vs breaking IR change, and how long are old
   `ir_version`s supported by the core?

---

### Appendix — why this is the keystone

This refactor is the enabler the rest of the work depends on:

- **Porting (GoCSL / CCSL):** a new language becomes a thin front-end emitting the IR — exactly the
  recommendation from the port analysis — instead of a re-implemented verifier. Go's
  `go/ast`/`go/types` makes the first external front-end cheap; C is best served by aligning with
  Frama-C/ACSL, which already targets this backend.
- **Feature proposals:** polymorphic datatypes, inductive predicates, lemma functions, quantifiers,
  bitvectors, and IEEE-754 floats are all implemented **once in the core** (IR nodes + WhyML
  lowering) and become available to every front-end the moment its language can express them.
- **UX & agent-friendliness:** honest success signals, structured diagnostics, no silent drops, and
  the capability manifest are all naturally realised at the core boundary, so every front-end
  inherits them.

The IR is the single seam that turns a Python-shaped tool into a verification *platform*.
