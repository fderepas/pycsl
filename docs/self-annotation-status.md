# Self-annotation status (Squeeze S4)

**Last regenerated:** 2026-05-31
**Squeeze:** S4 (Self-annotation) per `csl-from-scratch` §0.5
**Owning System:** SY8-SelfAnnotate (`src/self-annotate/`), per
[`projects/pycsl/PROJECT.md`](../projects/pycsl/PROJECT.md)
**Live suite:** `bin/run-self-annotation-suite.sh`
**Verifier mirror:** `src/self-annotate/src/` (file-for-file mirror of `src/pycsl/`)

---

## Headline

**26/26 modules prove. Coverage is broad, depth is thin.**

All proves are mechanical PASSes from `pycsl <file>.py`, but only
**1 module is body-verified** (`src/pycsl/errors.py`); the other
**22 ship as `\trusted reviewer: pycsl-self-annotate`** with
contract surface only; 2 are empty `__init__.py`.

The Squeeze S4 mechanical gate is **satisfied** — the verifier
verifies its own implementation, end-to-end. The *strength* of the
verification is what's incomplete.

---

## Live suite output

```
$ bin/run-self-annotation-suite.sh
[PASS] src/self-annotate/src/__init__.py
[PASS] src/self-annotate/src/module6_whyml/__init__.py
[PASS] src/self-annotate/src/import_classifier.py
[PASS] src/self-annotate/src/ConcurrencyChecker.py
[PASS] src/self-annotate/src/audit_proof.py
[PASS] src/self-annotate/src/Module1_Ingestor.py
[PASS] src/self-annotate/src/Module2_Parser.py
[PASS] src/self-annotate/src/Module3_Weaver.py
[PASS] src/self-annotate/src/Module4_SemanticAnalyzer.py
[PASS] src/self-annotate/src/Module5_IREmitter.py
[PASS] src/self-annotate/src/Module6_WhyMLTranspiler.py
[PASS] src/self-annotate/src/pycsl.py
[PASS] src/self-annotate/src/module6_whyml/auto_trust.py
[PASS] src/self-annotate/src/module6_whyml/expressions.py
[PASS] src/self-annotate/src/module6_whyml/statements.py
[PASS] src/self-annotate/src/module6_whyml/preamble.py

===============================
 Self-annotation: 26/26 proved
===============================
```

The suite is wired into `bin/run-reference-tests.sh` as a CI gate.

---

## Coverage by bucket

Per [`src/self-annotate/coverage-report.md`](../src/self-annotate/coverage-report.md)
(last regenerated 2026-05-28):

| Bucket | Discipline | Module count | Examples |
|---|---|---:|---|
| **A** (tractable now) | Bodies CAN be proven once stdlib stubs land; today they ship `\trusted` | **11** | `errors.py` (the *one* fully proven), `ir_schema.py`, `exception_model.py`, 6 `module6_whyml/` submodules (`identifiers`, `scc`, `abstract_ops`, `types`, `functions`, `ir_scanner`), 2 `__init__.py` |
| **B** (needs richer stubs) | Pure Python but uses `ast.NodeVisitor` patterns PyCSL can't resolve yet | **2** | `import_classifier.py`, `ConcurrencyChecker.py` |
| **C** (research-grade) | Uses libcst / Lark / in-place AST mutation / recursive string-building — modelling these is multi-quarter work | **13** | `Module1_Ingestor` through `Module6_WhyMLTranspiler`, `audit_proof.py`, `pycsl.py`, 4 heavier `module6_whyml/` mixins (`auto_trust`, `expressions`, `statements`, `preamble`) |

### Verification strength

| Strength | Count |
|---|---:|
| Body-verified (full proof) | **1** (`errors.py`) |
| `\trusted reviewer:` (contract surface only) | **22** |
| Empty `__init__.py` | 2 |

`errors.py` is the only module where the prover sees the actual
implementation — it proves `#@ class invariant self.line >= 0`
against the in-source body. Everything else ships
`\trusted reviewer: pycsl-self-annotate` at every function/method
with stub bodies that return type-appropriate placeholders.

---

## Annotation density in the mirror

`src/self-annotate/src/` is a file-for-file mirror of `src/pycsl/`
with `#@` annotations layered on. Top-annotated modules:

| Module | `#@` lines | LOC |
|---|---:|---:|
| `Module5_IREmitter.py` | 522 | 1,584 |
| `Module2_Parser.py` | 440 | 1,200 |
| `Module4_SemanticAnalyzer.py` | 130 | 643 |
| `pycsl.py` | 88 | 908 |
| `audit_proof.py` | 64 | 504 |
| `Module3_Weaver.py` | 60 | 367 |
| `Module1_Ingestor.py` | 52 | 266 |
| `Module6_WhyMLTranspiler.py` | 42 | 325 |
| `ConcurrencyChecker.py` | 28 | 166 |
| `import_classifier.py` | 20 | 111 |
| `exception_model.py` | 12 | 137 |
| `ir_schema.py` | 5 | 147 |
| `errors.py` | 1 | 46 |

Total: **2,174 `#@` lines** across 13 modules in the mirror —
substantial annotation work, mostly contract surface
(`requires`/`ensures`/`assigns` per function signature) rather than
loop invariants or body-level proofs.

---

## Supporting tooling (`bin/self-annotate-*`)

| Tool | Purpose |
|---|---|
| `bin/self-annotate-stub-gen.py` | Regenerate the mirror when `src/pycsl/<file>.py` changes |
| `bin/self-annotate-mirror-check.sh` | Verify signatures in `src/self-annotate/src/` match `src/pycsl/` (drift detection) |
| `bin/self-annotate-generate.sh` | Bulk regenerate the mirror set |
| `bin/run-self-annotation-suite.sh` | The CI gate — runs `pycsl <file>` on every module in the suite |

---

## CMMI framework mapping

Per [`projects/pycsl/PROJECT.md`](../projects/pycsl/PROJECT.md):

```yaml
# 9-system inventory
SY8 | SelfAnnotate | M | src/self-annotate/ | S4, S8

# squeeze_owners
S4: [SY8-SelfAnnotate]
S8: [SY6-PycslLib, SY8-SelfAnnotate]
```

The Squeeze coverage check (`bin/cmmi-audit.sh [C8.5]`) passes
because S4 has an owner. **The check verifies ownership, not
strength.** Strengthening S4 from "26/26 prove via `\trusted`" to
"26/26 prove via body verification" is engineering work tracked
under `src/self-annotate/plan-formal-*.md`, not under the CMMI
plan series.

---

## Gaps blocking deeper coverage

From the bucket A → bucket B → bucket C progression in the
coverage report, the named blockers are:

1. **Bucket A → full proof**: needs stdlib stubs for `isinstance`,
   set operations, and dict-membership with non-trivial
   postconditions. `ir_schema.py` is the next candidate.

2. **Bucket B → full proof**: needs `ast.NodeVisitor` modelling
   (PyCSL's function-call resolution doesn't follow it yet) →
   would require extending `src/pycsl_lib/` with `ast.*` stubs.

3. **Bucket C → full proof**: needs models for libcst / Lark /
   in-place AST mutation / recursive string emission. Some can be
   anchored to formal-semantics theorems
   (`Phase5b_Soundness.pycsl_soundness`,
   `Phase6h_CorrMain.wp_gen_correct`,
   `Phase6i_Soundness.why3_implements_wp_w_derived`) via
   `#@ proof rocq` citations — listed as "future PRs" in §2 Bucket
   C of the coverage report.

---

## Planning state (engineering work-items)

`src/self-annotate/` carries 4+ formal plans:

- [`src/self-annotate/plan-formal-01.md`](../src/self-annotate/plan-formal-01.md)
- [`src/self-annotate/plan-formal-02.md`](../src/self-annotate/plan-formal-02.md)
- [`src/self-annotate/plan-formal-03.md`](../src/self-annotate/plan-formal-03.md)
- [`src/self-annotate/plan-formal-04.md`](../src/self-annotate/plan-formal-04.md)
- [`src/self-annotate/plan-ghost-recommendation-01.md`](../src/self-annotate/plan-ghost-recommendation-01.md)

These outline the path from `\trusted` → body-verified per module.
They are engineering work-items, not CMMI work-items (per
[`projects/pycsl/CMMI-DONE.md`](../projects/pycsl/CMMI-DONE.md)'s
"what comes after" framing).

---

## How to watch this metric over time

`bin/cmmi-metrics-ingest.py --weekly` snapshots include per-system
contract-line counts. Once `bin/cmmi-qpm-charts.py` has ≥8
snapshots, the **L3-ceiling rate per system** chart (KPI 3) will
show SY8-SelfAnnotate trends. To track body-verification rate
specifically, a new KPI collector could be added to
`bin/cmmi-metrics-ingest.py`:

```python
# Heuristic: count `\trusted` blocks vs total #@ blocks per module
def _body_verified_rate(src_root: Path) -> float | None:
    ...
```

That collector is **not yet implemented** — see
[`docs/cmmi-for-humans.md`](cmmi-for-humans.md) Part 5
`bin/cmmi-metrics-ingest.py` for the existing collector set.

---

## TL;DR

| Metric | Value |
|---|---:|
| Suite modules | 26 |
| Pass rate | 26/26 (100%) |
| Body-verified | 1 (`errors.py`) |
| `\trusted` (surface-only) | 22 |
| Empty | 2 |
| Total `#@` lines in mirror | 2,174 |
| Squeeze S4 status (CMMI) | **satisfied at contract-surface level** |
| Squeeze S4 strengthening | engineering work, multi-quarter |

The framework makes the gap visible. Moving the dial from "1
body-verified" to "5 body-verified" is squeeze-strengthening
engineering work — tracked under
`src/self-annotate/plan-formal-*.md`, not under the CMMI plan
series.

---

## References

- [`src/self-annotate/coverage-report.md`](../src/self-annotate/coverage-report.md)
  — the authoritative per-module status table (canonical source for
  this status doc).
- [`bin/run-self-annotation-suite.sh`](../bin/run-self-annotation-suite.sh)
  — the live verifier.
- [`config/skills/csl-from-scratch/SKILL.md`](../config/skills/csl-from-scratch/SKILL.md)
  §0.5 — the Squeeze Strategy that defines S4.
- [`config/skills/pycsl-stdlib-coverage/SKILL.md`](../config/skills/pycsl-stdlib-coverage/SKILL.md)
  §9 — the growth criteria for adding modules to the suite.
- [`docs/cmmi-for-humans.md`](cmmi-for-humans.md) — the consolidated
  CMMI framework reference (Squeeze S4 binding in Part 2).
- [`projects/pycsl/PROJECT.md`](../projects/pycsl/PROJECT.md) —
  Squeeze ownership block.
- [`projects/pycsl/CMMI-DONE.md`](../projects/pycsl/CMMI-DONE.md)
  §"What 'done' does NOT mean" — explains why strengthening S4 is
  engineering work, not framework work.
