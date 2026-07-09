# Self-annotation status

PyCSL is a source-to-proof compiler: it reads Python and emits
formally verifiable WhyML. **Self-annotation** means turning PyCSL on
its own source code — the compiler proves properties of itself.  This
is the project's strongest correctness signal because it closes the
trust loop: the tool that checks everyone else is itself checked.

This document tracks how far that self-proof has progressed.

| | |
|---|---|
| **Last regenerated** | 2026-07-08 |
| **Metric** | **Function-level** `\trusted`-stub count (superseding the earlier module-level headline). Lower is better. |
| **Owning system** | SY8-SelfAnnotate (`src/self-annotate/`), per [`projects/pycsl/PROJECT.md`](../projects/pycsl/PROJECT.md) |
| **Live suite** | `bin/run-self-annotation-suite.sh` — **34/34 files proved, exit 0** |
| **Verifier mirror** | `src/self-annotate/src/` — a file-for-file copy of `src/pycsl/` with `#@` proof annotations layered on top |

---

## Headline

**The suite is genuinely green (34/34, full-file proofs), and the trusted core is down to `\trusted` = 1237 function-level stubs — with the `Dict[str, Any]` self-verification wall broken in practice.**

The metric has moved from the old module-level view ("26/26 modules
pass, 1 body-verified") to a **per-function** count: every emitter
method in the mirror is either a **body-verified** (`#@`-annotated,
verbatim-of-live, proved) function or a `\trusted` stub. Current
state (committed HEAD):

- **Body-verified functions: ~100** — the prover sees the real
  implementation and discharges its contracts. This is genuine proof
  and includes, as of 2026-07, several **generic `Dict[str, Any]`
  IR-walkers** proved via a certified catamorphic lowering (see the
  wall campaign below) — the class that was long considered
  research-grade.
- **`\trusted` stubs: 1237** — assumed contracts; the residual
  trusted core, dominated by the value-model / per-shape long tail.
- The gate is a **full-file proof** per mirror file (not `--fun`,
  which trusts siblings and can mask a leaky verified method — a
  masking hole found and closed 2026-07).

---

## Live suite output

```
$ bin/run-self-annotation-suite.sh
...
===============================
 Self-annotation: 34/34 proved
===============================
# exit 0
```

The suite proves each file **in full** (no `--fun` filter). Its file
list was corrected 2026-07 (7 stale top-level paths repointed to the
relocated `frontend/` mirror; the deleted `Module4_SemanticAnalyzer`
dropped), so it now exits 0 with **0 MISSING, 0 FAIL** — the first
genuinely-green run after a masked pre-existing breakage was repaired.
The suite is wired into `bin/run-reference-tests.sh` as a CI gate.

---

## The 2026-07 campaign — the `Dict[str, Any]` self-verification wall

The dominant residual blocker is that the emitter reads its own IR as
untyped `Dict[str, Any]`, which WhyML could not faithfully model. The
2026-07 effort **decomposed and largely resolved** this:

- **L1 — value modeling: SOLVED & CERTIFIED.** A concrete `pydict`
  universal-value type (interned constructor keys + Why3
  `compute_in_goal` proof-by-evaluation) clears the SMT pathologies on
  both Alt-Ergo and Z3, with an **axiom-free Rocq 8.20 + Lean 4.29
  certificate** (`Print Assumptions` = "Closed under the global
  context"; `#print axioms` = kernel-only). The **3-axiom trust ledger
  is held at 3** — no new axiom was added.
- **L2 — target-shape provability: PROVEN** (both provers) for the
  generic-walk and read+build shapes.
- **L3 — emitter code-generation: BROKEN IN PRACTICE.** A `GenericFold`
  recognizer + templater (`src/pycsl/module6_whyml/generic_fold.py`)
  emits the type-derived `walk`/`walk_dict`/`walk_list` catamorphism
  for a recognized generic-dict walk; **each instance is re-proved by
  Why3** (a template bug yields an unprovable instance, never a false
  proof → **no new trust**).

- **The non-fold traversal residual: ALSO broken (2026-07 traversal plan).**
  Beyond the bounded folds, the emitter's IR-traversal methods came in five
  non-fold shapes — **reconstruction** (functorial map), **value-dependent
  branching**, **short-circuit search**, **composed multi-algebra**, and
  **context-threading** (symbol tables). All five fall to the same
  recognizer+templater by **schema, not synthesis**: guard classification
  (semantic guards = unconstrained booleans, zero string theory), the
  functorial-map / option / bool algebras, traversal outlining, and an
  env-threaded fold over a certified string-keyed `sdict`.

**Converted (committed, each full-file "Verification SUCCESS", byte-diff 0,
no new axiom):** 9 IR-traversal methods — `find_named_expr_targets` (A-unit
ref) · `_collect_calls`/`find_calls_in_ir`/`collection_binder_kinds` (A-set)
· `_collect_assign_targets`/`_hp_collect_written` (A-unit grammar) ·
`_subst_type_in_ir` (reconstruction) · `find_return_type` (composed +
short-circuit) · `_sa_walk` (context-threading). **Count 1248 → 1237 over
the wall effort; the 3-axiom ledger held throughout** (two axiom-free
Rocq 8.20 + Lean 4.29 certificates: the `pydict` value model and the `sdict`
symbol-table pack — both re-verified `Print Assumptions`/`#print axioms`).

**Honest scaling economics (measured):** the structural census *over-counts*
convertible methods at every level — real complexity lives in the pre-action
/ composition / control-flow, not the walk shape — so the *capability* is
general but the *count* comes method-by-method. The `GenericFold` generator
now covers the IR-traversal frontier; the remaining `\trusted` is non-traversal
(I/O, hashing, generic-`Any` mutation) or the A-list/A-dict returned-collection
models. Full trace + the open-problem statement handed to external review:
`bigger-build.md`, `phase3.md`, `ir-traversal-residual-stand-alone*.md`,
`getting-better/tier3/wall-plan-v2-phase*.md`.

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
strength.** Strengthening S4 — driving the function-level `\trusted`
count down toward its irreducible floor by moving stubs to
body-verified — is engineering work tracked under `bigger-build.md` /
`phase3.md` and `getting-better/tier3/`, not under the CMMI plan
series.

---

## Gaps blocking deeper coverage

The residual `\trusted` core is dominated by **value-model and
per-shape blockers**, now precisely characterized by the 2026-07
census/decomposition:

1. **Generic `Dict[str, Any]` walkers** — the historically
   research-grade class. **Broken in practice** via the certified
   `pydict` model + `GenericFold` catamorphic lowering (above);
   converts method-by-method as each per-shape pre-action grammar is
   added (in-tuple guards, `isinstance` narrowings, nested field
   reads, by-return collection algebras).

2. **Composed / dependency-carrying walks** — methods that call
   sibling `\trusted` helpers, do variable-key context-map lookups
   (`symtab.get(node-key)`), short-circuit search, or compose multiple
   folds. Each needs a distinct bounded feature (a sibling-`val`
   interop model, a context-map value model, a short-circuit
   algebra) — not a free template slot.

3. **Collection-result modeling** — returned `list`/`dict` folds and
   string builders; A-set is done, A-list/A-dict await faithful
   returned-collection models. String-building tails route through a
   `doc` ADT to avoid SMT string theory.

Every new WhyML value shape must **co-land an axiom-free Rocq + Lean
certificate** (the coupling rule); the 3-axiom ledger is asserted in
CI via `Print Assumptions` / `#print axioms`.

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
| Suite files | 34 |
| Pass rate | **34/34 (100%), exit 0, full-file proofs** |
| Body-verified functions | **~100** |
| `\trusted` stubs (function-level) | **1237** |
| Trust ledger (Rocq 8.20 + Lean 4.29) | **3 axioms — held, axiom-free extensions** |
| `Dict[str,Any]` wall | **broken in practice** (certified catamorphic lowering; ≥4 generic-dict walkers self-proved) |

The metric is now the **per-function `\trusted` count** (lower is
better). Driving it down is body-verification work; the 2026-07
campaign moved the historically research-grade `Dict[str, Any]`
IR-walker class from `\trusted` to self-proved via a certified
lowering, with **no new trust axiom**. The remaining core is a long
tail of bounded per-shape features (tracked in `bigger-build.md` /
`phase3.md`), converted method-by-method.

---

## References

- `bigger-build.md` / `phase3.md` (repo root) — the live wall-campaign
  plans of record + execution ledgers (the current authoritative
  status of the `\trusted`-reduction work).
- `getting-better/tier3/` — the census, feasibility spikes, and
  per-phase verified findings of the 2026-07 wall campaign.
- `generic-dict-str-any-2.md` / `wall-plan-v2-phase2c-stand-alone.md`
  (repo root) — self-contained, external-reviewer problem statements.
- [`src/self-annotate/coverage-report.md`](../src/self-annotate/coverage-report.md)
  — the earlier per-module status table (module-level framing, now
  superseded by the function-level metric above).
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
