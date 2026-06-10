# refactor.md — refactoring PyCSL toward a language-agnostic core

**What this is.** A practical guide for evolving the PyCSL codebase toward the architecture in
`pycsl-language-agnostic-core-spec.md` — a thin per-language **front-end** that emits a canonical IR, and
a hardened, language-agnostic **core** (IR → WhyML → Why3 → SMT) that everything reuses. It is not a
big-bang rewrite plan; it is a set of **laws every refactor here must obey**, the **current state to
refactor *from***, and a **phased, gated sequence** to get there. It synthesizes the architecture spec
with what the rest of this work established: the source-of-truth/TCB discipline
(`docs/formal-filesystem.md`, `csl-philosophy`), deterministic emission (`pycsl-how-to-develop`
→ `why3-quirks.md`), and the leaf-first proof method.

The north star, in one line: **the IR is the single seam that turns a Python-shaped tool into a
verification platform.** Refactor toward making that seam explicit, versioned, and auditable — and never
at the cost of behavior, determinism, or fidelity.

---

## 1. The laws — what governs every refactor in this codebase

These are not style preferences; they are the conditions under which a refactor here is *safe*. Violate
one and the refactor is unsound or unverifiable, however clean it looks.

1. **Behaviour-preserving, corpus-gated — no big-bang.** Every step reproduces the existing reference
   corpus exactly. A refactor that "looks equivalent" is not equivalent until the corpus says so. Each
   step is independently shippable and reversible.
2. **The byte-diff is the gate — and it requires deterministic emission.** "Equivalent" means the
   generated `.mlw` is *byte-identical*. That gate only works because emission is now reproducible — so
   **anything that flows into emitted output must be ordered by content, never by Python set/dict-hash
   iteration or the built-in `hash()`** (both per-process randomized). Before trusting a byte-diff,
   regenerate the same input 4–5× and confirm one hash; a single run can look stable by luck. This is the
   precondition that makes a conformance corpus (Phase E) even testable.
3. **The source of truth defines the TCB split.** The whole point of the seam is to narrow each
   front-end's trust obligation to *one* thing: **faithfully capturing its source language's semantics in
   the IR** (fidelity to that language's authorities — the source of truth). Refactor toward making that
   boundary explicit and auditable; the core is the single shared safety-critical component, hardened
   once. Never let a refactor smear language-specific assumptions into the core, or logic checks into a
   front-end.
4. **Faithfulness over convenience — even mid-refactor.** Moving code is the moment a convenient
   abstraction tempts you. Resist: the IR must carry the *real* semantics — faithful types (no
   coerce-to-`int`), kept partiality (a partial function keeps its `requires`, never totalized), and a
   source span on every node. A refactor that simplifies by abstracting away the representation is
   *coherent and wrong*.
5. **Fail loud, never silent.** A contract that attaches to no IR node must be *rejected*, not dropped;
   a malformed IR must error with a located message. The refactor should make "attached to nothing"
   representable and refused — the seam is where silent contract-drop dies.
6. **Leaf-first, compose-don't-re-derive — for the code as for the proofs.** When you split a module,
   give the extracted piece a *narrow, true contract* and let callers stand on it, exactly as a verified
   leaf lets its callers compose rather than re-derive. Don't refactor a function by inlining its
   callees' logic back into it.

---

## 2. Refactor *from* here, not from zero (current state)

The spec was written before much of this existed. Take stock first — several load-bearing pieces are
already in place, which changes where the work actually is.

**Already realized / in motion:**
- The IR is a **JSON IR with `TypedDict` definitions + runtime validation** (`src/pycsl/ir_schema.py`:
  "the top-level JSON IR produced by Module 5 and consumed by Module 6"). Most of §5's "machine-readable,
  validated" is done.
- **IR-as-artifact tooling exists** — `bin/pycsl-ir-dump.py`, `bin/ir-to-rocq-ast.py`.
- **Emission is deterministic** (the set-iteration and `hash()` sources were fixed). Byte-diff is
  trustworthy.
- **Fail-loud is doctrine**; the front-end uses `pure_ast` (a pure-Python AST — *not* libcst, as the
  dated spec says).

**Still entangled / aspirational (this is the real work):**
- The IR is validated but **not versioned** — no `ir_version` / `source_language` stamp, no frozen
  published schema, no compatibility policy.
- **Semantic analysis (Module 4) still reaches into the Python AST** — it is not yet a pure IR consumer.
  This is the central entanglement to break.
- No serialized IR boundary the core ingests; no **two conformance corpora**; no second front-end.

---

## 3. The seam (where to cut)

```
┌─ FRONT-END (per language) ────────────┐        ┌─ CORE (shared, language-agnostic) ──────────────┐
│  Module 1 Ingestor                     │        │  IR ingest + schema/version validation          │
│  Module 2 Parser (contract grammar)    │  IR    │  → semantic analysis (on IR)        [Module 4]   │
│  Module 3 Weaver (attach contracts)    │ ─────▶ │  → WhyML emission                   [Module 6]   │
│  Module 5 IR construction              │  doc   │  → WhyML typecheck gate                          │
│  (Python today: pure_ast)              │        │  → proof orchestration (Why3/SMT, proof2why3)    │
└────────────────────────────────────────┘        │  → structured, located diagnostics + run report │
                                                   └────────────────────────────────────────────────┘
```

Front-end = Modules 1–3 **plus IR construction** (today inside Module 5). Core = the IR *definition*
(`ir_schema`, shared), semantic analysis re-pointed at the IR, the WhyML backend, and proof. The
conceptual move: **the IR definition is the interface; IR construction moves into the front-end; the
core's first step becomes IR ingest + validation, not building IR from a Python AST.**

---

## 4. The phased sequence (each phase shippable, reversible, gated)

Updated from the spec's §11–12 to start from §2's actual state.

| Phase | Move | Gate (all phases also: corpus byte-clean, `os` 0-unproven, doc-coherency green) |
|---|---|---|
| **A — IR as a versioned interface** ✓ *landed (`99f755d`)* | Add `ir_version` + `source_language` to `ir_schema`; make `pycsl-ir-dump.py` the canonical (de)serializer with a **round-trip identity** (`load(dump(ir)) == ir`); document the schema + a compatibility policy. | round-trip identity holds; corpus `.mlw` **byte-identical** (re-verify determinism 4–5×). |
| **B — Re-point the core at the IR** *(in progress — B0 `3cee4ae`, B1 `61e2603`, B2 `6a88baf`, B3 `4f690e0`, B4a `f987b80`, B4b `56a6716` landed)* | Make Module 4 (semantic analysis) consume the IR, **not** the Python AST. A multi-step re-architecture, not one commit (Module 4 mutates-and-returns the AST Module 5 consumes, conflates resolution with logic-checks, 126 `ast.*` couplings). **Landed:** B0 ✓ function-level spans; B1 ✓ the IR-semantic-check seam (`core_ir_semantic`, §6.2); B2 ✓ `no_exception`; B3 ✓ `assigns`-region base typing; **B4a ✓ statement-level spans** (loop nodes carry `line`); **B4b ✓ `predicate_bases`** (`\length`-on-dict / `\valid`/`\separated`) migrated via a **surface-tracking walk** that reconstructs every context — `function 'F'` / `while loop at line N inside function 'F'` (innermost loop) / `(ghost 'g')` / `(ghost 'g[...]')` — gated by characterization drivers `0667`–`0673` (XFAIL, byte-identical messages) `6c4c62b`. Each brick full-corpus-gated (zero change to existing drivers), messages reproduced exactly. **Also landed:** **`quant_binders` ✓** (`56733a2`) — typed-binder resolution migrated onto the *shared* surface-tracking walk (generalized to apply predicate-base + quant-binder + future checks; `known` reconstructed from `type_decls`, which include classes), gated by 0556/0674/0675. **`proj_indices` — does NOT migrate** (`6149728`): it is a *precondition guard* Module 5's ProjExpr emission depends on (reads `index.value`), so it must run before Module 5 and cannot move to the post-Module-5 seam — the gate caught the `'Var'` crash and it was reverted; it stays in Module 4 until Module 5's ProjExpr emission is hardened (added 0676/0677 loop/ghost coverage for the surviving Module-4 check). **AST-only checks — ALL 5 MIGRATED:** `subscript_assignments` (`24ca228`) + `checkpoints` (`97096c9`) needed *no* plumbing (the IR already carried `ArraySet`/`ProofAssert`); `no_mutable_defaults` (`bb33f0c`) via a front-end `has_mutable_default` flag (which *closed* a keyword-only gap); `acts` (`dcc2a6e`) plumbs the pre-desugar act/given/complete/disjoint structure as an `acts` IR field; `happy` (`a0bd81a`) plumbs a module-level `happy` blob (short method names, sidestepping the IR's `Class__method` flattening) and the core runs a cross-method pass. **`function_contracts` — MIGRATED:** the dispatcher's bulk had already moved (quant/predicate); the 2 survivors — `\result`-only-in-ensures and contract variable-scope — moved to `_check_contract_scope`, with Module 4's `extract_variables` ported to the IR as `_ir_free_vars` (generic `Var` collection + string-base specials − binders); gated by 0281/0282/0283 (existing) + 0688/0689/0690 and a 12-driver over-extraction spot-check. **B-final (wedge) ✓** (`60dec3b`): Module 5 now builds its own `symbol_table`/dict-types directly from the AST (ported resolution + `_get_type_name`/`_get_dict_*` helpers, exact insertion order), breaking the M5←M4 scope dependency — byte-exact (331 drivers identical incl. nested/str-keyed dicts, ghosts, for-loops, class methods). **Remaining for full B-final:** migrate Module 4's ghost-string-op `+=` check (the last `current_scope` consumer) to the core; drop `_build_function_scope` + the dead `csl_*` stashes; reorder M5 before M4. **Lesson:** not every Module-4 check is a pure post-hoc validator — some (like proj_indices) are preconditions later modules rely on, and those can't migrate to the seam without first hardening the dependent module; and most "AST-only" checks turned out to have their data already in the IR. | per brick: full-corpus identical pass/fail **and** error-message diff; identical `.mlw` (byte-diff); migrated-check messages reproduced exactly. |
| **C — Split the front-end** *(in progress)* | Move Modules 1–3 + IR construction into their own package; the core *ingests serialized IR*. The seam becomes a real wire. **Scoped:** the core (`Module6` + `module6_whyml` + `core_ir_semantic`) is ALREADY import-clean (zero front-end imports) and M5→M6 is ALREADY a JSON string (`Module6.__init__` does `json.loads`). **C0 ✓ (`2426e67`):** re-validate the *post-mutation* IR at the real seam — closes a latent bug where `validate_ir` ran only on the *pre*-mutation IR (before `_apply_inheritance`/`_composition`/`_inline_globals`), so the IR M6 actually consumes was never structurally checked. **C1 ✓ (`9b0e02e`):** Module 5 emits an `imports` IR field and `_resolve_imports` reads it instead of walking the AST — the last non-IR thing crossing post-M5; IR 1.0→1.1 (additive); byte-exact on all import + `--deep` drivers. **Remaining:** C2 — lift M1–3 + M5 + the four `pycsl.py` IR passes into a `frontend/` package. | corpus reproduced through the serialized boundary; `dump → ingest → prove` matches in-memory. |
| **D — Honest core** *(in progress)* | Add the **WhyML-typecheck gate** (a run is `SUCCESS` only if the emitted WhyML at least *type-checks* — never merely "text emitted"); structured, coded, **located** diagnostics; per-level status line; capability manifest. **D0 ✓ (`5b2662b`):** `--typecheck` runs `why3 prove --type-only` + reports `L1 ✓ L2 ✓ L3-tc {✓\|✗}`, exits non-zero on a non-type-checking emission. **FINDING:** 54 of 588 emitting drivers produce WhyML that does NOT type-check (28 concurrency + 26 other) — dishonest `--no-proof` SUCCESSes, real (the production `why3 prove` fails them identically). Ships opt-in (flipping default-on would regress those 54); `docs/typecheck-audit.md` + `bin/typecheck-audit.sh` track the backlog. **D1 (partial) ✓ (`7b7804c`):** fixed the concurrency root cause — a logic `predicate` dereferencing a program `ref` — by parameterizing the predicate + applying with the deref at use sites; eliminated on all 36 concurrency drivers, 7 now fully type-check, non-concurrency byte-identical. The fix peeled the onion to a SECOND blocker (25 drivers): `#@ \diverges` on a worker lowers to a `diverges` effect why3 rejects on the non-blocking model — a *modelling* decision, not a turnkey fix. **Remaining:** D1 the `\diverges` cohort + the 26 non-concurrency type-fails; D2 default-on + gate SUCCESS; structured codes + manifest. | every former silent "success" now states which level it reached; manifest generated from the passing corpus. |
| **E — Conformance & freeze** *(in progress)* | Carve **two corpora** — golden-IR → expected-WhyML (core alone), and source → expected-IR (front-end alone); **freeze the front-end contract**. A second front-end (Go via `go/ast`+`go/types`, or C aligned with Frama-C/ACSL) is then developable against a stable target. **E0 ✓ (`86baa2f`):** `bin/core-only-conformance.py` (imports ONLY the core; asserts no M1–5 in `sys.modules`) re-derives byte-identical WhyML from 14 golden IRs — **14/14, front-end not imported**: concrete proof the core is independently invokable. **E1 ✓ (`90fe16e`):** `bin/pycsl-ir-dump.py --resolved` applies the 3 pure post-M5 IR passes so the golden IR == what Module 6 consumes; corpus grown **14→28** to cover inheritance/composition/module-global-inline drivers — **28/28 byte-identical, front-end not imported**. **Remaining:** import drivers in the corpus (need `_resolve_imports` dependency context), corpus (2) source→expected-IR (front-end alone), the freeze. | core corpus passes with *no* front-end; front-end corpus passes with *no* prover. |

Do not start a phase before the prior phase's gate is green. B is the hard one (the entanglement); A is
the cheap, certain win that makes B's byte-diff trustworthy.

---

## 5. What "done" means for a step — the gate, concretely

A refactor step is finished only when **all** of these hold (this is the project's existing gating
discipline, applied to the seam):

- **Corpus byte-clean:** `bin/run-reference-tests.sh` (or the byte-diff harness) shows the `.mlw` for
  every driver byte-identical to before — *after* confirming emission is deterministic
  (regenerate 4–5× → one hash).
- **`os` still proves 0 unproven** (the heaviest real client of the core) and `formal_0001` 18/18.
- **doc-coherency green** (`bin/doc-coherency.py --check`) — a structural change must not drop a
  directive surface.
- **The TCB ledger is unchanged or shrunk** — a refactor must never silently add an axiom or a
  `\trusted`; if it does, that is a finding, not a step.

---

## 6. Hazards specific to this repo (read before touching anything)

- **Determinism regressions are invisible to one run.** Any new `set`/`dict` iteration or `hash()` on
  emitted-output material reintroduces per-process non-determinism. Order by content (`sorted`), use the
  deterministic `stable_hash`, and *re-test 4–5×*.
- **Destructive git.** `git checkout -- .` and `git stash -u … drop` silently eat uncommitted work;
  commit untracked plans/`*.md` before any sync, merge, or branch dance.
- **The self-annotate mirror.** If you move code in `src/pycsl/`, the mirror under the self-annotation
  layer can drift — re-sync rather than leave it inconsistent.
- **Don't "tidy" semantics.** No coerce-to-`int`, no totalizing a partial leaf, no abstracting the byte
  layout away — these read as cleanups and are fidelity regressions (law §1.4).

---

## 7. Why this is the keystone

Every other ambition depends on this seam. **Porting** (GoCSL/CCSL) becomes a thin front-end emitting
the IR instead of a re-implemented verifier. **Features** (polymorphic datatypes, inductive predicates,
bitvectors, IEEE-754 floats — and the `#@ for` sugar's successors) are implemented **once in the core**
and reach every front-end. And the **methodology that the platform exists to serve** — the descent and
return of `docs/formal-filesystem.md`: *source of truth → faithful model → concrete test → leaf-to-API
proof → formal test* — becomes a capability of the core, available to any language whose front-end can
faithfully reach the IR. Refactor toward the seam, hold the laws, and the tool becomes a platform.
