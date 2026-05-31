# PROJECT.md — PyCSL CMMI project charter

**Document ID:** PROJ-PYCSL-001
**Profile:** P (PyCSL-specific tailoring — see `cmmi-tailoring-plan.md`)
**Status:** Active
**Effective date:** 2026-05-31
**Source code location:** `src/<package>/` (never under `BL/SY<N>-<Name>/src/`)
**Import method:** `import-existing-code` (under Profile-P)

---

## Charter

Generate a formally proven annotation system with the smallest TCB
(Trusted Code Base) possible. The operational playbook is
[`config/skills/csl-from-scratch/SKILL.md`](../../config/skills/csl-from-scratch/SKILL.md).
PyCSL is the reference implementation of that family-wide playbook.

The BL requirements set is `csl-from-scratch` §0.5 Squeeze Strategy
(S1–S9). The BL → System decomposition table in
[`BL/specifications/main.md`](BL/specifications/main.md) names the
owning System(s) for each Squeeze.

---

## CCB

Single-developer CCB. Pre-approved per `should-we-cmmi-or-not.md` §9
and `cmmi-tailoring-plan.md` cross-cutting rules.

```yaml
ccb:
  members: [developer]
  self_approve: true
  cr_id_format: git-commit-sha
```

---

## 9-System inventory

| # | System | Profile | Source location | Squeezes implemented |
|---|---|---|---|---|
| SY1 | FormalSemantics | L | `src/formal-semantics/` | S2, S7 |
| SY2 | Lean2Pycsl | M | `src/lean2pycsl/` | S5 |
| SY3 | Pycsl | L | `src/pycsl/` | S1, S3, S6, S9 |
| SY4 | PyCSLBridge | S | `src/pycsl_bridge/` | (glue) |
| SY5 | PycslEmit | M | `src/pycsl_emit/` | S9 |
| SY6 | PycslLib | M (→ L over time) | `src/pycsl_lib/` | S1, S8 |
| SY7 | Rocq2Pycsl | M | `src/rocq2pycsl/` | S5 |
| SY8 | SelfAnnotate | M | `src/self-annotate/` | S4, S8 |
| SY9 | Skill2Rag | S | `src/skill2rag/` | (operational) |

```yaml
glue_systems: [SY4-PyCSLBridge, SY9-Skill2Rag]
```

`SY4-PyCSLBridge` is glue: it translates between Systems that own
Squeezes. `SY9-Skill2Rag` is operational infrastructure (RAG indexer
over `config/skills/`). Neither implements a Squeeze directly. The
C8 coverage check treats both as supporting infrastructure
(reported but not flagged as orphan).

---

## Squeeze ownership (BL → System mapping)

| Squeeze | csl-from-scratch §0.5 | Owning System(s) |
|---|---|---|
| S1 | CSL contracts (`requires`/`ensures`) | SY3-Pycsl, SY6-PycslLib |
| S2 | Formal semantics (Rocq + Lean) | SY1-FormalSemantics |
| S3 | Reference tests + traceability | SY3-Pycsl (`test-suite/`, `traceability-pycsl.md`) |
| S4 | Self-annotation | SY8-SelfAnnotate |
| S5 | Dual-prover anchoring | SY2-Lean2Pycsl + SY7-Rocq2Pycsl + `bin/check-proof-crosscheck.sh` |
| S6 | IR schema validation | SY3-Pycsl (`src/pycsl/ir_schema.py`) |
| S7 | TCB tier inventory | SY1-FormalSemantics + cross-cutting |
| S8 | Real-world test cases | SY6-PycslLib + SY8-SelfAnnotate |
| S9 | Auto-trust tracking | SY3-Pycsl (auto-trust counter) + SY5-PycslEmit |

The `cmmi-coherency-audit` C8 step 5 enforces:
- Every S<i> has ≥1 owning System listed above.
- Every System (except those in `glue_systems`) appears in ≥1
  S<i> row.

```yaml
squeeze_owners:
  S1: [SY3-Pycsl, SY6-PycslLib]
  S2: [SY1-FormalSemantics]
  S3: [SY3-Pycsl]
  S4: [SY8-SelfAnnotate]
  S5: [SY2-Lean2Pycsl, SY7-Rocq2Pycsl]
  S6: [SY3-Pycsl]
  S7: [SY1-FormalSemantics]
  S8: [SY6-PycslLib, SY8-SelfAnnotate]
  S9: [SY3-Pycsl, SY5-PycslEmit]
```

---

## Spec-kind bindings (no source duplication)

```yaml
spec_kind:
  L1:
    plan: config/skills/csl-from-scratch/SKILL.md       # the BL playbook
    preamble: README.md                                  # PyCSL framing
    requirements_set: csl-from-scratch §0.5 (Squeeze Strategy S1–S9)
  L2:
    SY1-FormalSemantics: [src/formal-semantics/README.md]
    SY2-Lean2Pycsl:      [src/lean2pycsl/__init__.py]      # docstring as L2
    SY3-Pycsl:           [docs/pycsl-concrete-syntax-reference.md,
                          docs/pycsl-static-semantics-reference.md,
                          docs/pycsl-translational-reference.md]
    SY4-PyCSLBridge:     [src/pycsl_bridge/__init__.py]    # docstring as L2
    SY5-PycslEmit:       [src/pycsl_emit/__init__.py]      # docstring as L2
    SY6-PycslLib:        [docs/stdlib-coverage.md, docs/stdlib-global-plan.md]
    SY7-Rocq2Pycsl:      [src/rocq2pycsl/__init__.py]      # docstring as L2
    SY8-SelfAnnotate:    [src/self-annotate/README.md]
    SY9-Skill2Rag:       [src/skill2rag/__init__.py]       # docstring as L2
  L3:
    SY3-Pycsl: config/skills/pycsl-software-architecture/SKILL.md
    default: per-dir __init__.py docstring (auto-discovered)
  L4: bin/cmmi-mod-index.py output (auto-generated, never hand-edited)
  L5: in-source #@ contracts (auto-discovered; not materialised as files)
```

L2 source files that don't exist yet (e.g. per-system `README.md`
under `src/<package>/`) are tracked as gaps by
`cmmi-process-level` under Profile-P; not blockers for project
acceptance because each system has at least one __init__.py
docstring as a fallback.

---

## Verification gates

| Gate | Command | Required for |
|---|---|---|
| Doc coherency (language surface) | `bin/doc-coherency.py --check` | Every commit touching `docs/` or `config/skills/pycsl-*/` |
| Spec-mirror invariant + Squeeze coverage | `bin/cmmi-audit.sh` | Every commit touching `config/skills/cmmi-*/` or `projects/pycsl/` |
| Reference corpus | `bin/run-reference-tests.sh` | Every commit touching `src/pycsl/` or `test-suite/` |

`bin/cmmi-audit.sh` composes the C1–C8 checks from
`cmmi-coherency-audit` with the existing `bin/doc-coherency.py`
gate.

---

## Bridge schedule (Follow-up #2 Item 3.1 — communication Phase 2)

Daily bridge runs mirror `metrics/logs/*.log` into
`projects/pycsl/message-queues/<agent>/inbox-from-logs/*.json`.
Volume bounded by `--max-age-days 30` (default). The queue itself
is NOT git-tracked (see `.gitignore`); only the `.gitkeep` marker
under `projects/pycsl/message-queues/` is.

**Cron entry (manual setup, not in repo):**

```cron
0 5 * * * cd ~/git/pycsl && bin/cmmi-bridge-daily.sh >> metrics/cron.log 2>&1
```

Runs daily at 05:00 local time, one hour before the weekly snapshot.
Uses `flock` to prevent overlapping runs.

**Dual-write window for Item 3.4 cutover:** the 2-week clock that
gates the supervisor reader switch (per
`cmmi-tailoring-plan-follow-up-2.md` Item 3.4) started on
**2026-05-31** (first real bridge run). Earliest cutover: 2026-06-14.

---

## Snapshot schedule (Item 4.1A — cmmi-quantitative-mgmt Phase 0)

Weekly per-system KPI snapshots accumulate in
`projects/pycsl/docs/metrics/metrics-store.json` until ≥8 snapshots
exist; then Phase 1B (control-chart generation via
`bin/cmmi-qpm-charts.py`) becomes possible.

**Cron entry (manual setup, not in repo):**

```cron
0 6 * * 1 cd ~/git/pycsl && bin/cmmi-weekly-snapshot.sh >> metrics/cron.log 2>&1
```

Runs Mondays at 06:00 local time. The wrapper uses `flock` to
prevent concurrent runs. Exits non-zero on failure so cron alerts
the developer.

**Current snapshot count:** see
`bin/cmmi-audit.sh [QPM]` output (added once Item 4.1B lands).

**Operational check:** the snapshot is *not* automatically gated.
If cron fails for 8+ days, the gap surfaces as a stale-snapshot
warning in the next `bin/cmmi-audit.sh` run.

---

## Tailoring deviations (recorded for the audit trail)

| Deviation | Rationale | Authority | Reference |
|---|---|---|---|
| Source stays in `src/`, never under `BL/.../src/` | "No duplication with Python code in src/" — user requirement | Developer (CCB) | `cmmi-tailoring-plan.md` §"Cross-cutting tailoring rules" |
| L4 Module specs auto-generated, never hand-authored | The `.py` file IS the spec; generating indices avoids drift | Developer (CCB) | `cmmi-tailoring-plan.md` §"The 5-level binding" |
| L5 Unit specs are in-source `#@` contracts, no `UN<N>-<Name>/` dirs created | The contract IS the spec; zero new files | Developer (CCB) | `cmmi-tailoring-plan.md` §"The 5-level binding" |
| BL plan = include of `csl-from-scratch`, not new prose | csl-from-scratch IS the operational playbook for the *CSL family | Developer (CCB) | `cmmi-tailoring-plan.md` §"BL → System decomposition" |
| 8 `pycsl-*` domain skills exempt from CMMI §1-§6 retrofit | Domain skills, not process skills; coherency enforced by `bin/doc-coherency.py` | Developer (CCB) | `should-we-cmmi-or-not.md` §6 Rule 3 |
| Single-developer CCB; commit SHA = CR-ID | Self-CCB pre-approved | Developer (CCB) | `should-we-cmmi-or-not.md` §8 risk 5 |

---

## References

- [`../../cmmi-tailoring-plan.md`](../../cmmi-tailoring-plan.md) — the
  tailoring plan this charter instantiates.
- [`../../should-we-cmmi-or-not.md`](../../should-we-cmmi-or-not.md) — the
  recommendation envelope.
- [`../../better-agent.md`](../../better-agent.md) — the Reconciliator
  design (`agent-feature-supervisor.py`) for SY3-Pycsl L3-ceiling
  escalations.
- [`../../missing-iter-feature.md`](../../missing-iter-feature.md) — the
  canonical feature plan; regression test for the framework.
- [`../../config/skills/csl-from-scratch/SKILL.md`](../../config/skills/csl-from-scratch/SKILL.md) —
  the BL operational playbook.
