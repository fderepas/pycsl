---
name: pycsl-audit-pycsl-language
description: >-
  Audits that the PyCSL language is internally consistent end-to-end after any
  change to it. Use this skill whenever you touch the PyCSL language surface — add
  or modify a `#@` contract clause/directive, edit the Lark grammar in
  `Module2_Parser.py`, change semantic validation (Module4), IR emission (Module5),
  or WhyML translation (Module6/`module6_whyml/`) — or before merging/releasing a
  language change. It verifies the clause is wired through every stage
  (grammar → validate → IR → WhyML), documented across all five normative surfaces,
  covered by the reference corpus, and — critically — that its lowering is
  *semantically faithful* (the trap that bit the behaviors plan twice). Triggers on
  phrasings like "I added a new contract directive", "audit the PyCSL language",
  "did I wire this clause through everywhere", "is this consistent before merge",
  "run the language gate", or "does PyCSL actually prove this construct".
---

# Audit PyCSL Language Consistency

PyCSL's language surface is defined in **four implementation stages** and mirrored in
**five documentation surfaces** and a **golden corpus**. A change is *consistent* only
when all of them agree. No single tool checks the whole chain — the gate scripts check
the mechanical parts, but the **end-to-end wiring** and **semantic fidelity** of a clause
are a manual audit. This skill is that audit. Run it every time you change the language.

## The consistency invariant

Every `#@` contract clause / directive (and every Python-subset construct) must line up
across all of these, or the language is in drift:

```
  surface (one #@ directive)
        │
   ┌────┴─────────────────────────────────────────────────────────────┐
   │ IMPLEMENTATION CHAIN (must be wired through every stage)           │
   │   G  grammar      src/pycsl/Module2_Parser.py  (Lark PYCSL_GRAMMAR │
   │                   + ?contract: alternation + transformer method)   │
   │   V  validate     src/pycsl/Module4_SemanticAnalyzer.py            │
   │   I  IR           src/pycsl/Module5_IREmitter.py                   │
   │   W  WhyML        src/pycsl/module6_whyml/  (or a documented no-op) │
   ├────────────────────────────────────────────────────────────────── ┤
   │ DOCUMENTATION (all five surfaces — enforced by doc-coherency.py)   │
   │   test-suite/annotations.md          ← CANONICAL source            │
   │   README.md                          (quick-reference table)       │
   │   docs/pycsl-concrete-syntax-reference.md     (grammar)            │
   │   docs/pycsl-static-semantics-reference.md    (well-formedness)    │
   │   docs/pycsl-translational-reference.md       (WhyML translation)  │
   │   + a relevant config/skills/ skill                                │
   ├──────────────────────────────────────────────────────────────────┤
   │ CORPUS (a golden pair proving it works)                            │
   │   test-suite/corpus/pycsl-reference/NNNN.py + NNNN.mlw             │
   └────────────────────────────────────────────────────────────────────┘
```

## Runbook — the gate commands (run in this order)

**One command bundles the mechanical subset:**
```bash
bin/audit-pycsl-language.sh           # grammar build + doc-coherency + mod-index + corpus + mirrors
bin/audit-pycsl-language.sh --quick   # mechanical checks only (skip corpus + mirrors) for fast iteration
```
It sets `PYTHONHASHSEED=0` and `CMMI_AUDIT_NESTED=1` for you and exits non-zero on drift.
The individual steps below are what it runs (and what to reach for when narrowing a
failure); the end-to-end clause audit and semantic-fidelity check further down are **not**
automated — do them by hand.

Run from the repo root with the project venv. **Determinism:** prefix WhyML-affecting
runs with `PYTHONHASHSEED=0` — `set`-ordered emission is hash-seed-dependent and will make
proofs/goldens flap otherwise.

1. **Full CMMI gate** (the umbrella; includes mod-index, struct promotion, and the
   language-surface coherency check):
   ```bash
   CMMI_AUDIT_NESTED=1 timeout 300 bin/cmmi-audit.sh
   ```
   ⚠ **Always set `CMMI_AUDIT_NESTED=1` and a `timeout`.** The ER-retrospective step
   re-invokes the supervisor, which can re-enter the audit and CPU-explode; the env var
   makes the nested run skip that step. Target: `N passed, 0 failed`.

2. **Language-surface doc coherency** (the heart of this audit — five-surface parity for
   every `#@` directive; canonical source is `test-suite/annotations.md`):
   ```bash
   bin/doc-coherency.py --check            # 0 = all surfaces document every directive
   bin/doc-coherency.py --list-directives  # the canonical directive set
   ```
   This is governed in detail by the **`pycsl-doc-coherency`** skill — consult it to fix
   any gap (it tells you which surface is missing the directive).

3. **Reference corpus** (every `NNNN.py` re-verifies; goldens hold):
   ```bash
   PYTHONHASHSEED=0 bin/run-reference-tests.sh
   ```

4. **Self-annotation mirrors still verify** (PyCSL proves its own modules under
   `--no-proof`):
   ```bash
   PYTHONHASHSEED=0 make self-annotate-verify
   ```

5. **Proof-citation cross-check** (if you touched `#@ proof rocq/lean` plumbing):
   ```bash
   bin/check-proof-crosscheck.sh
   ```

6. **Skill RAG index is complete + fresh** (so a changed/added skill stays
   discoverable — embedding-free, fast, CI-safe):
   ```bash
   make rag-verify     # 0 = in sync · 1 = drift (run `make rag-build`) · 2 = index not built
   ```

If a clause is genuinely WhyML-no-op (like the Python `assert` statement — see below), the
corpus and gate still pass; the *no-op must be documented* in the translational reference
(`T[[#@ ...]] = ()`), which `doc-coherency.py` checks for.

## End-to-end clause audit (what the gate can NOT do for you)

The gate confirms *documentation parity* and *that the corpus still proves*. It does **not**
confirm that a clause is actually wired through every implementation stage, nor that it
*means what you think*. Do this by hand for any clause you added or changed.

**(A) Enumerate the grammar's clause keywords** (don't trust a stale list — read it):
```bash
# the ?contract: alternation and the clause productions
sed -n '/?contract:/,/^$/p' src/pycsl/Module2_Parser.py
grep -nE '": "(requires|ensures|assigns|...)' src/pycsl/Module2_Parser.py   # production rules
```

**(B) For your clause, confirm each stage is present** (substitute the clause's node class,
e.g. `Requires`, `RaisesDecl`, `BoundedIntDecl`):
```bash
CLS=YourClauseNode
grep -rn "$CLS" src/pycsl/Module2_Parser.py        # G: AST node + transformer method
grep -rn "$CLS\|csl_<field>" src/pycsl/Module3_Weaver.py          # dispatched onto the AST node
grep -rn "csl_<field>\|$CLS" src/pycsl/Module4_SemanticAnalyzer.py # V: validated
grep -rn "<ir_key>" src/pycsl/Module5_IREmitter.py                # I: serialized to IR
grep -rn "<ir_key>" src/pycsl/module6_whyml/*.py                  # W: emitted (or documented no-op)
```
A clause that parses but is dropped before WhyML is **silent drift** — it looks supported
and proves nothing. That is the failure mode this audit exists to catch.

**(C) Confirm a corpus pair exists** that exercises the clause and that its `.mlw` golden
contains the expected WhyML:
```bash
grep -rln "#@ your_clause" test-suite/corpus/pycsl-reference/*.py
```
Per project convention, **new language features must add a `NNNN.py`/`NNNN.mlw` pair** to
`test-suite/corpus/pycsl-reference/` (and, ideally, a negative case that must *fail*).

## Semantic-fidelity discipline — verify the primitive before you lower onto it

The subtlest drift is a clause that is wired through every stage and documented, but whose
lowering **does not mean what it claims**. Two real examples from PyCSL:

- **PyCSL `assert` ≠ ACSL `assert`.** The Python `assert` statement is emitted as `()` and
  **skipped by the prover** (`module6_whyml/statements.py`: *"Python assert statements are
  runtime checks, not proof obligations"*). There is no `#@ assert` proof-obligation clause.
  So you cannot use an `assert` to discharge a verification goal — it has no teeth.
- **A "checked" property is not a "required" one.** A precondition (`requires`) is *assumed*
  inside the body; a postcondition (`ensures`) is *proved* by the function. Lowering a
  property that must be *proved* (e.g. case-completeness) onto a `requires` makes it
  vacuously pass. Pre-state proof goals belong in `ensures \old(...)`, not `requires`.

**Rule:** before lowering a new construct onto an existing primitive, *read the emitter*
for that primitive and confirm what WhyML it produces and whether the prover sees it. Ask:
*is this proved, assumed, or dropped?* Confirm with a **negative corpus test** — a spec that
*should* fail verification and does. If your construct can be made wrong and still "passes",
it has no teeth, and the audit has failed even though every box is green.

## Change-type → what to audit

| You changed… | Minimum audit |
|---|---|
| A new `#@ clause` | Full chain (B), all 5 doc surfaces (gate 2), a +/− corpus pair (C), semantic-fidelity check |
| Grammar only (syntax tweak) | `pycsl --no-proof` on samples, corpus (gate 3), concrete-syntax doc |
| Validation rule (Module4) | corpus (gate 3) incl. a case that should now be rejected; static-semantics doc |
| IR shape (Module5) | corpus goldens regen + `PYTHONHASHSEED=0` diff; mod-index (gate 1) |
| WhyML emission (Module6) | corpus goldens + Why3 proof closes; translational doc; semantic-fidelity check |
| A pipeline module's *code* (not language) | gate 1 (mod-index def-counts), self-annotate (gate 4) |

## House rules / gotchas

- **`CMMI_AUDIT_NESTED=1` + `timeout`** for any `cmmi-audit.sh` run (ER-recursion guard).
- **`PYTHONHASHSEED=0`** for anything that emits or diffs WhyML (determinism).
- **mod-index drift** after editing a module's def count: regenerate the owning System with
  `bin/cmmi-mod-index.py --system <SYx-Name>` (never `--file` — it dup-numbers MO dirs).
- **`test-suite/annotations.md` is canonical** and its numbering never changes; add new
  directives there first, then propagate to the other four surfaces.
- A WhyML **no-op is legitimate** but must be declared as `T[[…]] = ()` in the translational
  reference, or `doc-coherency.py` flags it.
- The **skill RAG index** (`data/embeddings/skills_index.json`) is a **local, gitignored**
  artifact built against **localhost** ollama (`nomic-embed-text`), not the remote LLM
  endpoint. After adding or editing any skill, run `make rag-build` to re-index (a full
  rebuild — there is no incremental build) and `make rag-verify` to confirm it is complete
  and fresh. A skill absent from the index cannot auto-surface to agents.

## Related skills & references

- **`pycsl-doc-coherency`** — the five-surface parity invariant + how to fix a gap.
- **`pycsl-annotate`** — the master language reference (every clause's syntax/semantics).
- **`pycsl-docs`** — the three-layer doc stack (syntax / static-semantics / translation).
- **`pycsl-how-to-develop`** — pipeline architecture, test suite, Why3 quirks.
- **`pycsl-ub-catalog`** / **`pycsl-exception-model`** — the UB categories and exception
  semantics, when the change touches those surfaces.
- Authoritative files: `src/pycsl/Module2_Parser.py` (grammar), `test-suite/annotations.md`
  (canonical directives), `docs/pycsl-{concrete-syntax,static-semantics,translational}-reference.md`.
