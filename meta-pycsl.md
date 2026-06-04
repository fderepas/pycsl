# Implementation plan: meta-properties in PyCSL (`#@ assert`/`check` → HILAREs)

> Refines `metacsl-roadmap.md` (the sequencing) into an executable plan, applying the
> discipline the `act` feature proved out (`act.md`). Scope is fixed by the roadmap: the
> target is **cross-cutting whole-program integrity/confidentiality invariants over many
> functions** — *not* the Frama-C multi-plugin machinery.

## What the `act` work taught us (and how it shapes this)

1. **Desugar/expand to existing primitives — never grow the TCB.** `act` added a whole
   construct with **0 new IR nodes, 0 backend change, 0 `\trusted`**, all in the front-end.
   Meta-properties do the same at *program* scope: expand one requirement into many ordinary
   per-site obligations.
2. **Verify the target primitive's *real* semantics first.** `act` sidestepped a missing
   primitive (PyCSL's `assert` is emitted as `()` and **never proved** —
   `module6_whyml/statements.py:1198`) by lowering `complete`/`disjoint` to `ensures \old(…)`.
   **Meta-properties cannot sidestep it** — a HILARE expands to per-*site* obligations, which
   are statement-level asserts. So **Stage A must build a real statement-level proof
   obligation** before Stage B.
3. **Contain the front-end change; prove byte-identical.** `act` gated its Module1 fold on an
   `act` header and proved all 410 corpus files harvest unchanged. Every stage here repeats
   that: gate on the new directive, prove non-users are byte-identical.
4. **Emission has coercion gotchas.** The `_to_bool` fix (`\old(comparison)` is boolean) was
   needed for `act`; Stage A/B assertions over comparisons will lean on the same path.
5. **Gates are non-negotiable:** 5-surface doc-coherency, reference-corpus demos *including a
   negative case with teeth*, determinism (ordered, `PYTHONHASHSEED=0`), SY3 mod-index regen,
   `audit-pycsl-language`, RAG.

## Stages & dependency

```
Stage A  real statement-level proof obligation (#@ assert / #@ check)
         ├─ first customer: migrate act's complete/disjoint onto an entry assert
         │  (removes act's normal-return-only caveat)
         └─ prerequisite for ▼
Stage B  meta-properties (HILAREs): expand one whole-program requirement
         into per-site Stage-A obligations
```

Stage A ships value on its own (statement assertions are independently useful) and **locks
nothing**; do it first.

---

## Stage A — `#@ assert P` / `#@ check P` (statement-level proof obligations)

A genuine proof obligation at a program point: `assert` = prove-and-**assume** (P becomes a
hypothesis afterward); `check` = prove-and-**discard** (no hypothesis) — mirroring ACSL and
WhyML (`assert`/`check`/`assume` are reserved in `module6_whyml/identifiers.py`). **Distinct
from** the Python `assert` statement, which stays a no-op (`statements.py:1198`) — do not
conflate them.

These are **statement-position** `#@` directives — same shape as `#@ label L`, so reuse that
machinery as the model:

- **Module1** — `#@ assert P` / `#@ check P` are own-line `#@` before a statement; they
  harvest like `label` (no `act`-style folding needed). *Contained:* non-assert harvesting
  byte-identical.
- **Module2** — grammar `assert_decl: "assert" expr` / `check_decl: "check" expr`; nodes
  `CheckPoint(kind, expr)`. (`assert`/`check` confirmed-free as contract keywords — verify
  vs the existing reserved set first.)
- **Module3** — attach to the following `ast.stmt` (the post-weave `ast.walk` step that
  attaches `csl_labels` is the template → add `csl_checkpoints`).
- **Module5** — emit a **new** IR stmt, e.g. `{"stmt": "ProofAssert", "kind": "assert"|"check",
  "test": <expr-ir>}`, prepended before the statement's own IR (the `Label` prepend at
  `Module5_IREmitter.py` is the template). Keep the existing Python-`assert` `Assert` IR and
  its `()` emission **unchanged**.
- **Module6** — emit `assert { P }` / `check { P }` for `ProofAssert` (a real obligation Why3
  discharges). Reuse `_expr_to_whyml` + the `_to_bool` boolean handling.
- **Module4** — validate the expression in the statement's scope (`\result` rules per
  position; same `_validate_contract` machinery).

**First customer — migrate `act`'s `complete`/`disjoint`.** Re-lower them (Module3 desugar)
from `ensures \old(g1)||…` to a **function-entry** `#@ assert (g1 || …)` (and per-pair for
disjoint). At entry the preconditions are hypotheses, so this discharges `Pre ⟹ …` on **all**
paths — removing `act`'s documented normal-return-only caveat. This also exercises Stage A on
a known case before Stage B leans on it.

**Stage A gates:** corpus byte-identical for non-assert files; doc-coherency 5 surfaces for
`assert`/`check`; corpus demos — a true `#@ assert` proves, a **false one fails** (teeth), and
`check` vs `assert` differ on whether the fact is usable downstream; the act-migration demos
(0454–0456) still behave (0456 still fails completeness, now via the entry assert).

---

## Stage B — meta-properties / HILAREs (cross-cutting invariants)

One module-level high-level requirement that **expands** into many Stage-A obligations at
every matching site. Adapt the MetAcsl model (`config/skills/acsl/references/metacsl-reference.md`:
target / context / property; the `\writing`/`\reading` contexts; `\written`/`\read`
meta-variables) — keep the *model*, drop the plugin/CLI surface.

### B1 — Surface + parse
A module-level directive declaring (context, property). Decide the concrete `#@` syntax
(open question — see below); e.g. an integrity HILARE:
`#@ meta writing: \written in secret_region ==> \caller == "encrypt"`. Module1 harvests it as
a module-level contract; Module2 parses to a `MetaProperty(context, predicate)` node; Module4
validates the meta-variables are used only in their context.

### B2 — Site identification (the core new pass)
A **whole-program pass** (new `Module3b` / a post-weave walk) that enumerates the matching
program points in PyCSL's IR/AST:
- `\writing` context → every write site: `ast.Assign`, `FieldAssign`/`FieldAugAssign`,
  `ArraySet` (the IR stmt kinds Module5 already emits).
- `\reading` context → every read site: `FieldGet`, subscript/`Subscript` reads.
The pass must respect the **memory model** (`hoare` value-semantic arrays vs `typed`/`store`
heap `Map.get`/`Map.set`) — writes/reads are emitted differently per model.

### B3 — Expansion to Stage-A obligations
At each matched site, **inject a Stage-A `#@ check`** instantiating the meta-variables
(`\written` → the site's lvalue, `\read` → the rvalue) into the HILARE predicate. Because
PyCSL is **modular** (each function proved in isolation against callee contracts), a
whole-program property is enforced exactly by materializing it as a per-site obligation in
every function — which is what this expansion produces. `check` (not `assert`) is the right
default: a meta-obligation shouldn't silently become an assumed hypothesis.

### B4 — Worked property + corpus
Pick **one integrity property first** ("no function but `encrypt` writes `secret`"): a small
multi-function corpus demo where the property holds, plus a **negative** demo where a
stray write violates it and the expanded `check` fails (teeth). Confidentiality (`\reading`)
follows once integrity lands.

### B5 — Docs + gates
5-surface doc-coherency for the meta directive(s); reference-corpus pairs; the negative
demo; determinism (ordered site enumeration — never a `set`); attribution (each injected
`check` carries the HILARE name so a failure names the property and the site).

**Stage B scope discipline:** integrity (`\writing`) before confidentiality (`\reading`);
`hoare` model first (typed/store heap sites are a follow-up); per-site `check` injection only
— no new backend/IR-expression surface beyond Stage A's `ProofAssert`.

---

## Cross-cutting discipline (applied at every phase, per the `act` experience)

- **Containment + corpus differential** — gate new front-end behavior on the new directive;
  prove non-users byte-identical (the squeeze).
- **Verify-before-lower** — never assume a primitive's behavior; confirm *proved / assumed /
  dropped* (the `assert`-is-a-no-op trap is exactly why Stage A exists).
- **Negative test for teeth** — every obligation-introducing feature ships a demo that
  *fails* when the property is false.
- **Determinism + attribution** — ordered passes; carry the source construct/property name to
  emission (the prover only sees the expanded form).
- **0 `\trusted`** preserved at every stage; everything lowers to obligations Why3 discharges.
- **Per-feature gates** — SY3 mod-index regen, `bin/doc-coherency.py --check`,
  `bin/audit-pycsl-language.sh`, `make rag-build`/`rag-verify`, full `run-reference-tests.sh`.

## Verification (end-to-end, per stage)
1. **Stage A:** `pycsl` proves a true `#@ assert`/`check`; a false one FAILS; `check` leaves
   no downstream hypothesis (a contrived test that only closes if `assert` did and fails if
   `check`); act-migration corpus (0454–0456) unchanged in verdict; non-assert corpus
   byte-identical (Module1) + emission-identical (old vs new).
2. **Stage B:** the integrity demo proves; the violating demo FAILS at the offending site
   (failure message names the HILARE + site); non-meta corpus unaffected.
3. **Gates green** at each merge: doc-coherency (5 surfaces), mod-index `--verify --all`,
   `audit-pycsl-language --quick`, then full proof corpus.

## Open decisions (resolve at the start of each stage)
- **Stage A:** `assert` vs `check` keyword choice + whether to also support
  `#@ assume` (auditable hole, like ACSL `admit`); the IR stmt name (`ProofAssert`).
- **Stage B:** the concrete HILARE `#@` syntax (a `meta`-block in the `act` block style, or a
  flat directive); how a "site" is identified across the three memory models; whether the
  meta predicate may reference function contracts (callees') or only the site's lvalue/rvalue;
  whether expansion runs pre- or post-IR (AST sites vs IR sites).
