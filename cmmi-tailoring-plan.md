# CMMI Tailoring Plan for PyCSL

## Context

`should-we-cmmi-or-not.md` concluded "yes, but tailored hard": adopt
the 13 CMMI-adjacent skills, but bridge to PyCSL's existing
artefacts rather than rebuild them, and apply per-system profiles
rather than uniform Profile L. The skills as shipped assume a
greenfield multi-developer team. PyCSL is a mature single-developer +
LLM-agent codebase with most CMMI artefacts already present in
disguise (normative reference docs, coherency CI gate, traceability
matrix, three-artefact stdlib discipline).

This plan tailors **10 skills** so they map onto PyCSL's existing
`src/` topology with **zero source duplication**: the
`projects/pycsl/BL/SY<N>-<Name>/` tree holds specifications and agent
definitions only; code stays in `src/<package>/`.

**Anchoring example.** On 2026-05-31 13:47:22, a `claude-sonnet-4.6`
annotation run emitted an L3-ceiling fallback on `itertools.cycle`
("iterator-sequence semantics cannot be expressed in the current
contract surface"). The annotator correctly stopped. No agent then
proposed a feature plan — that was the human noticing and writing
`missing-iter-feature.md`. The CMMI mapping says this is the
Specifier-Verifier-Reconciliator triplet at System level for
`SY3-Pycsl` (which owns the contract surface) failing to escalate.
`better-agent.md` is the Reconciliator design that closes this loop.

After tailoring, the System-level Verifier and Reconciliator for
`SY3-Pycsl` will be the existing `agent-stdlib-annotate` (extended
with gap detection per `better-agent.md` Phase 1) and the new
`agent-feature-supervisor`. The 13:47:22 incident is the negative
test for the tailored framework.

---

## The 5-level binding for PyCSL

The user fixed the level-to-artefact mapping in the prompt. The plan
locks it into the tailored skills:

| Level | Unit of work | PyCSL anchor | Spec artefact |
|---|---|---|---|
| **Business** | The project as a whole | "Generate a formally proven annotation system with the smallest TCB possible" — operational playbook in [`config/skills/csl-from-scratch/SKILL.md`](config/skills/csl-from-scratch/SKILL.md) | `projects/pycsl/BL/specifications/main.md` — short PyCSL preamble that **includes csl-from-scratch as the BL plan** |
| **System** | One of 9 packages | `src/<package>/` | `projects/pycsl/BL/SY<N>-<Name>/specifications/main.md` + PlantUML message sequence chart |
| **Component** | A directory inside a system | `src/<package>/<subdir>/` (e.g. `src/pycsl/module6_whyml/`) | `projects/pycsl/BL/SY<N>-<Name>/CO<M>-<Name>/specifications/main.md` + PlantUML diagram |
| **Module** | A single `.py` file | `src/<package>/<subdir>/<file>.py` | **Generated index** — list of public functions with line refs; **no hand-written content** |
| **Unit** | A function or method | A single `def` in a `.py` file | The function's **existing `#@` contract** in `src/`. No copy. |

**The key insight** that resolves "no duplication" with `src/`:

- L1 (BRD) = include of `config/skills/csl-from-scratch/SKILL.md`
  (the operational playbook for the whole `*CSL` family — PyCSL is its
  reference implementation) + a short PyCSL-specific preamble citing
  `README.md`. The BL spec doc is **not** new prose; it is a pointer
  to the canonical playbook plus the project-instance framing.
- L2 (SRS/SAD/ICD per system) = symlink/include of existing
  `docs/pycsl-*-reference.md` (for SY3-Pycsl) or each system's
  `__init__.py` docstring (for others).
- L3 (HLD per component) = symlink/include of relevant sections of
  `config/skills/pycsl-software-architecture/SKILL.md` and the
  per-component `__init__.py` docstring.
- L4 (MLD per module) = auto-generated index pointing into the `.py`
  file. The file IS the spec.
- L5 (LLD per unit) = the function's `#@` contract block. The
  contract IS the spec. Zero new files.

The 9 systems are fixed (user-provided):

| # | System | Profile | Notes |
|---|---|---|---|
| SY1 | FormalSemantics | L | Rocq + Lean proof corpus; soundness floor of trust chain |
| SY2 | Lean2Pycsl | M | Lean → PyCSL converter |
| SY3 | Pycsl | L | Core compiler; bug = unsound proof; ~22.9k LOC |
| SY4 | PyCSLBridge | S | Glue utilities |
| SY5 | PycslEmit | M | Emit pipeline |
| SY6 | PycslLib | M (→ L over time) | Stdlib stubs; wrong stub = silent unsoundness |
| SY7 | Rocq2Pycsl | M | Rocq → PyCSL converter |
| SY8 | SelfAnnotate | M | Agent orchestrator |
| SY9 | Skill2Rag | S | RAG indexer (already piloted) |

---

## BL → System decomposition via the Squeeze Strategy

Because `csl-from-scratch` is the BL plan, its §0.5 **Squeeze
Strategy** (S1–S9) is the BL-level *requirements set*. Every Squeeze
layer is a BL-level requirement that decomposes to one or more
Systems. This gives the System decomposition a completeness check:
**every Squeeze must be implemented by at least one System; every
System must implement at least one Squeeze.** Orphan Squeezes
indicate missing Systems; orphan Systems indicate scope creep.

| Squeeze (BL req.) | What it constrains | Owning System(s) |
|---|---|---|
| S1 — CSL contracts (`requires`/`ensures`) | Code satisfies the spec | SY3-Pycsl (parser, Module6 emission), SY6-PycslLib (stdlib stubs) |
| S2 — Formal semantics (Rocq + Lean) | WP calculus agrees with operational semantics | SY1-FormalSemantics |
| S3 — Reference tests + traceability matrix | Every grammar production has a passing test; no verdict drift | SY3-Pycsl (test-suite/), `test-suite/traceability-pycsl.md` |
| S4 — Self-annotation | Verifier satisfies its own contracts | SY8-SelfAnnotate |
| S5 — Dual-prover anchoring | Two proof kernels accept the same theorems | SY7-Rocq2Pycsl + SY2-Lean2Pycsl, plus `bin/cross-check-provers.sh` |
| S6 — IR schema validation | Module 5 → Module 6 boundary is machine-checkable | SY3-Pycsl (`src/pycsl/ir_schema.py`) |
| S7 — TCB tier inventory | Every trust assumption is named, tiered, tracked | SY1-FormalSemantics (`Print Assumptions`); cross-cutting |
| S8 — Real-world test cases | Contracts expressible on real programs | SY6-PycslLib, SY8-SelfAnnotate |
| S9 — Auto-trust tracking | Every escape hatch is a tracked bug | SY3-Pycsl (auto-trust counter), SY5-PycslEmit |

**Coverage check** (added to `cmmi-coherency-audit` as part of C8 —
see §5 below): every S<i> in the table above must name at least one
SY<j>; every SY<j> must appear in at least one S<i> row. Currently
SY4-PyCSLBridge does not implement a Squeeze directly — it is glue
that *enables* S1/S5/S8 by translating between the systems that own
them. The audit treats glue-only systems as supporting infrastructure
(reported but not flagged as orphan).

**Practical consequence for project planning.** When a Squeeze
layer is weak in PyCSL today (e.g. S5 — cross-prover cross-check is
partial; some axioms are not yet reconciled), the gap is a *BL-level
requirement deficit*, not a per-System bug. The Reconciliator for
the affected Systems (SY1 + SY2 + SY7) escalates to the BL Specifier
(the developer) for a feature-plan draft. Same shape as the
`itertools.cycle` incident, one level up.

---

## Cross-cutting tailoring rules (apply to every skill below)

Three new pre-approved deviations get added in identical form to
every skill's §6 Tailoring table. Call them collectively the
**PyCSL profile** (`Profile-P`). Each skill's §6 gets one line:

> **Profile-P (PyCSL-specific):** Single-developer CCB; source stays
> in `src/<package>/`, never under `BL/SY<N>-<Name>/src/`; L4 Module
> specs are generated indices, L5 Unit specs are the in-source `#@`
> contracts (no separate files); pre-approved per `cmmi-tailoring-plan.md`.

The plan-wide bindings (referenced by all 10 skills, declared once
in `projects/pycsl/PROJECT.md`):

```yaml
# projects/pycsl/PROJECT.md (excerpt)
profile: P
ccb: { members: [developer], self-approve: true }
source_location: src/<package>/     # NOT under BL/
spec_kind:
  L1: include config/skills/csl-from-scratch/SKILL.md   # canonical BL playbook
  L1_preamble: README.md                                  # PyCSL-instance framing
  L2: include docs/pycsl-*-reference.md (per system mapping)
  L3: include + section of config/skills/pycsl-software-architecture/SKILL.md
  L4: generated by bin/cmmi-mod-index.py (NEW — Phase 1 deliverable)
  L5: in-source #@ contracts (read-only mirror)
systems:
  - { id: SY1, name: FormalSemantics, src: src/formal-semantics, profile: L }
  - { id: SY2, name: Lean2Pycsl,      src: src/lean2pycsl,       profile: M }
  - { id: SY3, name: Pycsl,           src: src/pycsl,            profile: L }
  - { id: SY4, name: PyCSLBridge,     src: src/pycsl_bridge,     profile: S }
  - { id: SY5, name: PycslEmit,       src: src/pycsl_emit,       profile: M }
  - { id: SY6, name: PycslLib,        src: src/pycsl_lib,        profile: M }
  - { id: SY7, name: Rocq2Pycsl,      src: src/rocq2pycsl,       profile: M }
  - { id: SY8, name: SelfAnnotate,    src: src/self-annotate,    profile: M }
  - { id: SY9, name: Skill2Rag,       src: src/skill2rag,        profile: S }
```

---

## Per-skill tailoring

Each section below specifies what to add to that skill's `SKILL.md`
and (where needed) its `references/`. The pattern is:

- Append rows to existing tables (never rewrite).
- Add a single "PyCSL bindings" subsection where the skill's RACI or
  outputs need a concrete-rather-than-abstract anchor.
- Reference `projects/pycsl/PROJECT.md` for the Profile-P invariants.

---

### 1. `project-lifecycle` — the central orchestrator

This is the skill that defines the recursive level execution. Tailoring
must make the 9-system topology explicit and lock in spec-mirror
semantics.

**Changes to `config/skills/project-lifecycle/SKILL.md`:**

- §2.4 **Referenced systems** (NEW subsection): copy the 9-system
  table verbatim from `PROJECT.md`. Forward reference to the per-system
  spec dirs.
- §2.4 **BL plan binding** (NEW subsection): *"Under Profile-P, the
  Business-level operational playbook is
  [`config/skills/csl-from-scratch/SKILL.md`](../csl-from-scratch/SKILL.md).
  Its §0.5 Squeeze Strategy is the BL requirements set; its phases
  0–10 are the long-arc roadmap that the per-system execution cycles
  contribute to. The BL Specifier is the developer; the BL Verifier
  is the squeeze coverage check (C8 in `cmmi-coherency-audit`); the
  BL Reconciliator is the developer + `agent-feature-supervisor.py`."*
- §4.T2 (Execute Business Level) — append: *"Under Profile-P, T2 is
  satisfied by maintaining csl-from-scratch as the canonical BL plan
  and by running the per-Squeeze coverage check. The developer does
  not author a separate BRD; the BRD is `BL/specifications/main.md`
  which includes csl-from-scratch plus the PyCSL-instance preamble."*
- §4.T7 (Phase 10 leaf): add a paragraph — *"Under Profile-P, the
  Coder step is a no-op: code already exists in `src/<package>/`. The
  Validator step is `pycsl --proof` (per-function contract proof) +
  `bin/run-reference-tests.sh` (per-system regression). The
  Coder-Validator pair binds to the existing
  `coordinator.py:CoordinatorAgent` retry loop."*
- §4.T8 — append row:
  | Rule | Requirement |
  |---|---|
  | No source duplication | Under Profile-P, `BL/SY<N>-<Name>/src/` is never created; the spec mirror references `src/<package>/` via the `source_location` pointer in `PROJECT.md`. |
- §6 — append row per the Profile-P template above.
- §6 Pre-Approved Tailoring Profiles table — append **Profile P** row:
  | Profile | Levels | Execution Scope | Governance |
  |---|---|---|---|
  | P (PyCSL) | L1–L5 by system per `PROJECT.md` | T2 + T3 + per-system T4-T6 + T7=no-op + Phase 12 | Single-developer CCB |

**Changes to `config/skills/project-lifecycle/references/directory-hierarchy.md`:**

- Add **§7 Profile-P spec-mirror mode**: 5-line subsection stating that
  every level dir's `specifications/main.md` is a one-line include
  pointer (when an existing artefact covers it) or a generated index
  (L4). Source dirs at CO/MO/UN are never materialised; they live at
  `<src_root>` from `PROJECT.md`.

**Changes to `config/skills/project-lifecycle/references/tailoring-profiles.md`:**

- Add Profile P with selection criteria pointing to `PROJECT.md`.

---

### 2. `import-existing-code` — the entry point for the migration

This is what we *run* to scaffold the new tree. Tailoring pre-loads the
9-system inventory and the Profile-P deviation so the scaffolder
doesn't ask 30 questions.

**Changes to `config/skills/import-existing-code/SKILL.md`:**

- §2 **Scope** — append row to In-Scope: "Pre-tailored PyCSL profile
  with 9-system inventory pre-declared."
- §4.E (Entry Criteria) — add:
  - [ ] If `<project>` is `pycsl`, the 9-system inventory in
    `PROJECT.md` matches the contents of `src/`.
- §4.T Phase 0 — append: *"Under Profile-P, Phase 0 reads the 9-system
  table from `PROJECT.md` and creates 9 `BL/SY<N>-<Name>/` dirs with
  the standard subdirs but NO `src/` subdir."*
- §4.T Phase 1 — replace the 5-step retro-spec table with a Profile-P
  variant:
  | Step | Level | Action under Profile-P |
  |---|---|---|
  | 1.1 | L5 Unit | Inventory existing `#@` contracts in `src/<package>/` (read-only). No new files. |
  | 1.2 | L4 Module | Run `bin/cmmi-mod-index.py --system SY<N>` to generate per-module indices. |
  | 1.3 | L3 Component | For each top-level dir under `src/<package>/`, write a short `specifications/main.md` that includes the relevant pycsl-software-architecture section. |
  | 1.4 | L2 System | Write `specifications/main.md` as a one-line include of the canonical doc (e.g., for SY3, include `docs/pycsl-*-reference.md` triad). |
  | 1.5 | L1 Business | Write `BL/specifications/main.md` as an include of `config/skills/csl-from-scratch/SKILL.md` (the BL operational playbook) plus a 5–10 line PyCSL-instance preamble citing `README.md` and the 9-system table. The §0.5 Squeeze Strategy from csl-from-scratch IS the BL requirements set — do not re-author it. |
- §4 Phase 4 Compliance Audit — modify check P4.2 to accept the
  Profile-P pointer (`src/<package>/` from `PROJECT.md`) instead of
  requiring `BL/.../src/`. Modify P4.5 to verify L5 specs are present
  *in-source* (count `#@` contracts vs. count of `def`s per file).
- §6 — append Profile-P row.

**New deliverable referenced by this skill:**
- `bin/cmmi-mod-index.py` — generates the L4 Module index `.md`
  from a `.py` file (lists `def`s with line refs, lists imports,
  dumps any module docstring). Read-only with respect to `src/`.

---

### 3. `cmmi-agent-roles` — bind abstract roles to concrete agents

This skill currently lists abstract role aliases (Specifier, Verifier,
Reconciliator, Executing Agent, etc.). Tailoring binds each abstract
role at each level to a concrete persona file in `config/agents/` or
to a script in `src/pycsl/agents/`.

**Changes to `config/skills/cmmi-agent-roles/SKILL.md`:**

- §2.4 Abstract Role Aliases table — add a "PyCSL binding" column:

  | Alias | Semantics | PyCSL binding |
  |---|---|---|
  | Specifier | Defines what a level produces | L1: developer · L2: developer + `pycsl-software-architecture` skill · L3-L4: `agent-annotate.py` · L5: `agent-contract-writer.py` |
  | Verifier | Defines and runs the test plan | L1-L2: `bin/run-reference-tests.sh` · L3-L4: `pycsl --proof` · L5: `agent-meta-evaluator.py` |
  | Reconciliator | On test failure, diagnoses + routes | L1-L2: `agent-feature-supervisor.py` (per `better-agent.md`) · L3-L4: `agent-reconcile.py` · L5: `coordinator.py:CoordinatorAgent` (exit-73 loop-detection) |
  | Sending/Receiving Agent | Communication message endpoint | Any script in `src/pycsl/agents/` |

- §4.T step 4 (Select Governance roles) — add the Profile-P note: under
  single-developer CCB, the EPG and SQA roles collapse to the developer
  for everyday operations; full RACI is recorded but not enforced as a
  multi-person blocker.
- §6 — append Profile-P row.

**Changes to `config/skills/cmmi-agent-roles/references/role-catalog.md`:**

- Add a **PyCSL agent inventory** subsection listing each existing
  `src/pycsl/agents/agent-*.py` with the role(s) it fulfills. This
  serves as the binding table the persona-generator references.

**New deliverable: per-system persona files.** For each of the 9
systems, generate three persona stubs under
`projects/pycsl/BL/SY<N>-<Name>/specifications/agents/`:

- `specifier.md` — binds to the persona above for that system's level.
- `verifier.md` — binds to the verifier script.
- `reconciliator.md` — binds to the reconciliator for that system. For
  SY3-Pycsl, this is `agent-feature-supervisor.py` (the one that would
  have escalated the `itertools.cycle` incident).

These persona files are NOT in `config/agents/`. They are
**system-scoped bindings** under `BL/`. `config/agents/` stays as the
canonical persona catalog; `BL/.../agents/` is the per-system
assignment matrix.

---

### 4. `cmmi-documents` — generator for spec documents

This skill currently assumes documents are *generated* by the agent.
Under Profile-P, most L1-L3 docs are *symlinked* or *included* from
existing artefacts. Tailoring adds the include mechanism.

**Changes to `config/skills/cmmi-documents/SKILL.md`:**

- §4.T — add a new task before the existing T1: **T0 — Resolve
  Profile-P include directives.** When the requested document is
  L1-L3 and `PROJECT.md` declares `spec_kind: { L1: include README.md }`,
  emit a one-line include block instead of generating prose. The
  include block is a literal Markdown anchor:
  ```markdown
  <!-- pycsl-include: source=../../../README.md scope=L1-BRD -->
  ```
  A new `bin/cmmi-include-expand.py` resolves these anchors at view
  time (it does NOT copy content into the file; the include is
  resolved on render). This preserves single-source-of-truth.
- §4.O Outputs & Destinations — add: under Profile-P, generated L4
  Module indices land at
  `projects/pycsl/BL/SY<N>-<Name>/.../MO<P>-<Name>/specifications/main.md`
  via `bin/cmmi-mod-index.py`; the agent does not write L5 files at all.
- §6 — append Profile-P row. **Also extend the existing row** ("Fast-track
  or prototype project") to mention Profile-P inherits the simplified
  Extended ETVX (may omit Inputs row).

**No new references file required.** The include-expand mechanism is
documented in the SKILL.md body.

---

### 5. `cmmi-coherency-audit` — framework-wide audit

Currently audits all of `config/skills/` with 17 lens checks. Under
Profile-P, the 8 `pycsl-*` domain skills are exempt from §1-§6
structural checks (per should-we-cmmi-or-not.md §6 Rule 3), and a
new check C8 verifies the spec-mirror invariant.

**Changes to `config/skills/cmmi-coherency-audit/SKILL.md`:**

- §4.T Phase A — modify A2 (CMMI-documents lens) item 9: **append**
  to the existing "Non-CMMI skills" list: *"`pycsl-annotate`,
  `pycsl-doc-coherency`, `pycsl-docs`, `pycsl-exception-model`,
  `pycsl-how-to-develop`, `pycsl-software-architecture`,
  `pycsl-stdlib-coverage`, `pycsl-ub-catalog` — these are PyCSL
  domain skills under Profile-P; §1-§6 structural checks are N/A.
  Their coherency is enforced by `bin/doc-coherency.py --check`."*
- §4.T Phase C — add **C8: Spec-mirror invariant** (new check):
  > For each `projects/pycsl/BL/SY<N>-<Name>/` dir, verify:
  > 1. There is a corresponding `src/<package>/` per `PROJECT.md`.
  > 2. There is **no** `BL/SY<N>-<Name>/src/` subdir (Profile-P
  >    forbids in-tree source copies).
  > 3. Every `include:` anchor resolves (`bin/cmmi-include-expand.py
  >    --verify`).
  > 4. Each L4 Module index has fewer/equal entries than the actual
  >    `def` count in the corresponding `.py` (no spec drift).
  > 5. **Squeeze coverage** (BL → System completeness): every
  >    Squeeze S1–S9 from `config/skills/csl-from-scratch/SKILL.md` §0.5
  >    is listed against ≥1 System in the BL → System decomposition
  >    table in `BL/specifications/main.md` (or `PROJECT.md`'s
  >    `squeeze_owners:` block). Every non-glue System appears
  >    against ≥1 Squeeze. Glue-only Systems (currently SY4) are
  >    declared in a `glue_systems:` allow-list and reported but
  >    not flagged.
- §4.T Phase D2 — add to the report template: a "Profile-P invariant"
  section reporting C8 results.
- §4.V — add: *"Under Profile-P, exempt the 8 pycsl-* domain skills
  from A1-A4 lens checks; instead verify they appear in the canonical
  `pycsl-*` list and that `bin/doc-coherency.py --check` exits 0."*
- §6 — append Profile-P row. **Also extend §6**'s Profile-aware audit
  scope to add a P row:
  | Profile-P audit scope: skip A1-A4 for pycsl-* domain skills; run C8 | Project uses Profile-P tailoring | EPG Lead (= developer under single-dev CCB) |

**No new references file required.**

---

### 6. `cmmi-glue` — governance workflows

Four workflows (Tailoring, Change Control, SQA Audit & Non-Compliance
Escalation, Continuous Improvement). The genuine PyCSL win is
Workflow 3: the `itertools.cycle` incident was an implicit escalation
failure that Workflow 3 formalises.

**Changes to `config/skills/cmmi-glue/SKILL.md`:**

- §4.T Workflow 3 (SQA Audit & Non-Compliance Escalation) — add a
  Profile-P binding subsection: *"For PyCSL, the agent escalation path
  is `coordinator.py` exit codes 72/73 → `agent-meta-monitor.py`
  → `agent-feature-supervisor.py` (per `better-agent.md` Phase 1) →
  human review. The L3-ceiling fallback (`# cite:_note:` line) is a
  Workflow 3 *signal*; the supervisor's gap-aggregation is the
  *handler*. When a gap category passes the proposal threshold, the
  supervisor produces a `proposed-features/missing-<category>-feature.md`
  draft — that draft IS the formal SQA non-conformance report under
  Profile-P."*
- §4.T Workflow 2 (Change Control) — append: *"Under Profile-P single-
  developer CCB, the CCB is the developer + the baselined artefact
  itself (the changed file). Approval is the commit. The Change
  Control record is the commit message; the CR-ID is the commit SHA.
  No separate ticket system."*
- §4.T Workflow 4 (Continuous Improvement) — append: *"Under Profile-P,
  the metrics source is the existing `metrics/` directory (per the
  coordinator pipeline), not a separate metrics-store.json. The
  improvement loop reads `metrics/meta_reviewer/*.md` and feeds back
  into the per-system Verifier."*
- §6 — append Profile-P row. **Extend** the existing "Single-agent
  project" row to additionally permit "Profile-P self-CCB with commit
  SHA as CR-ID".

**No new references file required.**

---

### 7. `cmmi-metrics-collection` — KPI aggregation

Currently aggregates from 9 source skills into `metrics-store.json`.
Under Profile-P, the source is the existing `metrics/` tree.

**Changes to `config/skills/cmmi-metrics-collection/SKILL.md`:**

- §4.I Inputs — append: *"Under Profile-P, the canonical source is the
  existing `metrics/` tree populated by `coordinator.py`,
  `agent-meta-evaluator.py`, `agent-meta-monitor.py`, and
  `agent-meta-reviewer.py`. A new `bin/cmmi-metrics-ingest.py` reads
  those outputs and emits a per-system normalised view."*
- §4.O — clarify: the per-project store remains at
  `projects/pycsl/docs/metrics/metrics-store.json`; the **source data**
  in `metrics/` is not duplicated, only referenced via file pointers
  and per-system roll-up counts.
- §4.T — add a new task at the end: **T-N Per-system roll-up.** For
  each of the 9 systems, emit a row in the store with: proof-success
  rate (from `metrics/logs/`), agent retry count (from
  `metrics/monitor/`), reviewer findings count
  (from `metrics/reviewer/`), doc-coherency events
  (from `bin/doc-coherency.py` exit history).
- §5 — append PyCSL-specific KPIs:
  | KPI | Formula | Source |
  |---|---|---|
  | L3-ceiling rate per system | (`# cite:_note:` lines) / (functions touched) | `metrics/stdlib-gap-report.json` (Phase 1 of better-agent.md) |
  | Reconciliator escalation rate | (Workflow-3 escalations) / (proof failures) | `metrics/monitor/*.md` |
  | Spec-mirror drift events | C8 failures from coherency audit | `projects/pycsl/docs/audits/coherency-audit-*.md` |
- §6 — append Profile-P row.

**New deliverable:** `bin/cmmi-metrics-ingest.py` — reads
`metrics/` tree, emits per-system normalised JSON.

---

### 8. `cmmi-quantitative-mgmt` — Level-4 SPC

Currently requires ≥3 project runs for baselines. PyCSL has years of
informal runs but no normalised baselines. Tailoring defers full QPM
until 8+ weeks of normalised data accumulates.

**Changes to `config/skills/cmmi-quantitative-mgmt/SKILL.md`:**

- §4.E Entry Criteria — add: *"Under Profile-P, defer entry to QPM
  until `cmmi-metrics-ingest.py` has emitted ≥8 weekly snapshots."*
- §4.T — add a **Phase 0: Snapshot accumulation** that simply records
  the per-system KPIs weekly. No control charts until Phase 1 (after 8
  weeks).
- §5 — add a **PyCSL-priority charts** subsection:
  | Chart | Per-system metric | Why useful |
  |---|---|---|
  | Proof-success rate trend | `pycsl --proof` PASS / total | Detects WhyML regressions early |
  | Agent retry-count drift | `coordinator.py` retry count | Detects LLM model drift |
  | L3-ceiling rate trend | gap-report counts | Detects when a feature plan should drop |
  | Doc-coherency events / week | `bin/doc-coherency.py` exits | Detects normative-doc drift |
- §6 — append Profile-P row matching the snapshot-accumulation phase
  approach.

**No new bin/ tool required** — Phase 0 reads what
`cmmi-metrics-ingest.py` already emits.

---

### 9. `cmmi-process-level` — gap analysis

Classifies existing docs into the 5 levels. Tailoring pre-fills the
classification for PyCSL (since we know exactly which existing doc
covers which level).

**Changes to `config/skills/cmmi-process-level/SKILL.md`:**

- §4.I — add: *"Under Profile-P, the classification is pre-declared in
  `PROJECT.md`'s `spec_kind` table; gap analysis becomes a delta against
  that declared coverage."*
- §4.T — add **T0: Profile-P pre-classification.** Read the
  `spec_kind` block from `PROJECT.md`, mark each declared coverage as
  "present (mirrored)". Subsequent T-steps only audit what's missing
  *relative to the declared mirror*, not relative to a blank slate.
- §4.T existing T-steps — guard each with "skip if Profile-P pre-
  declaration covers this level".
- §4.O — gap report under Profile-P groups gaps by system, not by
  level. Output adds a per-system "missing-feature seed" — any system
  with ≥5 L3-ceiling notes gets a row pointing the Reconciliator at
  the `agent-feature-supervisor.py --propose-feature` command.
- §6 — append Profile-P row.

**Pre-classification table to embed in `PROJECT.md`:**

```yaml
spec_classification:
  L1:
    plan: config/skills/csl-from-scratch/SKILL.md   # the BL operational playbook
    preamble: README.md                              # PyCSL-instance framing
    requirements_set: csl-from-scratch §0.5 (Squeeze Strategy S1–S9)
  L2:
    SY3-Pycsl: [docs/pycsl-concrete-syntax-reference.md, docs/pycsl-static-semantics-reference.md, docs/pycsl-translational-reference.md]
    SY1-FormalSemantics: src/formal-semantics/README.md
    SY6-PycslLib: docs/stdlib-coverage.md
    (others): src/<package>/__init__.py docstring
  L3:
    SY3-Pycsl: config/skills/pycsl-software-architecture/SKILL.md
    (others): per-dir __init__.py docstring
  L4: bin/cmmi-mod-index.py output (auto)
  L5: in-source #@ contracts (auto)
```

---

### 10. `communication` — inter-agent messaging

Tailoring decides: do we use the file-based `message-queues/` substrate
defined by this skill, or stay on the existing `metrics/` substrate
the coordinator uses? Per should-we-cmmi-or-not.md §8 risk 3, two
substrates indefinitely is a bug.

**Decision: bridge, then sunset.**

- Phase 1: bridge `coordinator.py`'s log lines into
  `projects/pycsl/message-queues/<agent>/` (one-way mirror, no
  behaviour change).
- Phase 2 (after Workflow 3 escalation is wired in `cmmi-glue`):
  `agent-feature-supervisor.py` reads exclusively from the message-
  queue, not from `metrics/`.
- Phase 3 (after stability): retire the dual-write; `metrics/` becomes
  a derived view of the queue.

**Changes to `config/skills/communication/SKILL.md`:**

- §4.I — add: *"Under Profile-P, agent log lines from
  `src/pycsl/agents/coordinator.py` are mirrored into the queue via a
  new `bin/cmmi-msg-bridge.py` during the Phase 1 transition."*
- §4.O — add: under Profile-P, queue messages reference (do not copy)
  the original `metrics/logs/*.log` entries via a `source_uri` field.
- §4.T — add Phase 1 / Phase 2 / Phase 3 transition checklist.
- §6 — append Profile-P row. **Extend** the existing "Single-developer
  mode (PyCSL)" row (which the upstream digest already mentions) to
  reflect the bridge-then-sunset plan.

**New deliverable:** `bin/cmmi-msg-bridge.py` — one-way mirror from
`metrics/logs/` to `projects/pycsl/message-queues/`.

**One-line specifically for the `itertools.cycle` anchor**: the
13:47:22 GitHub Copilot Response message lands in
`projects/pycsl/message-queues/agent-stdlib-annotate/inbox/`. The
Reconciliator (`agent-feature-supervisor.py`) watches that queue.
This is what should have triggered the auto-draft of
`missing-iter-feature.md` and is the regression test for the tailored
framework.

---

## Critical files modified

This is the **diff surface** of the tailoring plan itself. None of
the changes touch `src/`.

**Skill files (10):**
- `config/skills/project-lifecycle/SKILL.md` (§2.4 NEW, §4.T7/T8/§6 append)
- `config/skills/project-lifecycle/references/directory-hierarchy.md` (§7 NEW)
- `config/skills/project-lifecycle/references/tailoring-profiles.md` (Profile P row)
- `config/skills/import-existing-code/SKILL.md` (§2/§4.E/§4.T Phase 0,1,4/§6)
- `config/skills/cmmi-agent-roles/SKILL.md` (§2.4 column add, §4.T step 4, §6)
- `config/skills/cmmi-agent-roles/references/role-catalog.md` (PyCSL inventory subsection)
- `config/skills/cmmi-documents/SKILL.md` (§4.T T0 NEW, §4.O, §6)
- `config/skills/cmmi-coherency-audit/SKILL.md` (§4.T A2, C8 NEW, D2, §4.V, §6)
- `config/skills/cmmi-glue/SKILL.md` (§4.T W2/W3/W4 Profile-P bindings, §6)
- `config/skills/cmmi-metrics-collection/SKILL.md` (§4.I/§4.O/§4.T T-N/§5/§6)
- `config/skills/cmmi-quantitative-mgmt/SKILL.md` (§4.E/§4.T Phase 0/§5/§6)
- `config/skills/cmmi-process-level/SKILL.md` (§4.I/§4.T T0/§4.O/§6)
- `config/skills/communication/SKILL.md` (§4.I/§4.O/§4.T Phase 1-3/§6)

**New scaffold files (one-time, generated by the import):**
- `projects/pycsl/PROJECT.md` — canonical bindings, profile, 9-system
  table.
- `projects/pycsl/BL/specifications/main.md` — short PyCSL-instance
  preamble + **include of `config/skills/csl-from-scratch/SKILL.md`**
  (the canonical BL operational playbook) + the BL → System decomposition
  table (Squeeze S1–S9 → owning Systems). Not new prose; a pointer +
  framing.
- `projects/pycsl/BL/SY<1..9>-<Name>/specifications/main.md` — L2 specs
  (each a one-line include).
- `projects/pycsl/BL/SY<1..9>-<Name>/specifications/agents/{specifier,verifier,reconciliator}.md`
  — per-system role bindings.
- `projects/pycsl/BL/SY<1..9>-<Name>/specifications/sequence.puml` —
  per-system PlantUML message sequence chart.
- `projects/pycsl/message-queues/` — initial queue layout.
- `projects/pycsl/docs/{audits,reports,metrics,diagrams}/.gitkeep` —
  reserved dirs.

**New tooling (5 small Python/bash scripts, all read-only with
respect to `src/`):**
- `bin/cmmi-mod-index.py` — L4 Module index generator (reads `.py`,
  emits `main.md`).
- `bin/cmmi-include-expand.py` — resolves `<!-- pycsl-include: ... -->`
  anchors at view time (and `--verify` for the C8 check).
- `bin/cmmi-metrics-ingest.py` — reads `metrics/` tree, emits per-
  system normalised JSON into `projects/pycsl/docs/metrics/`.
- `bin/cmmi-msg-bridge.py` — one-way mirror from `metrics/logs/` to
  `projects/pycsl/message-queues/`.
- `bin/cmmi-audit.sh` — wraps `cmmi-coherency-audit` C8 check and
  pre-existing `bin/doc-coherency.py`; intended for the
  `bin/run-reference-tests.sh` chain.

**Reused without modification:**
- `src/pycsl/agents/coordinator.py` — retry-loop binds to L5 Verifier.
- `src/pycsl/agents/agent-reconcile.py` — L3-L4 Reconciliator.
- `src/pycsl/agents/agent-meta-{evaluator,monitor,reviewer}.py` —
  metrics source.
- `bin/doc-coherency.py` — language-surface coherency (delegated to by
  `cmmi-coherency-audit` under Profile-P).
- `bin/run-reference-tests.sh` — System-level Verifier.
- `bin/stdlib-coverage-report.py` — feeds coverage delta into metrics.

---

## Execution order

The plan executes in 4 phases. Each phase is independently shippable.

### Phase A — Anchor the contract (1 day)

1. Write `projects/pycsl/PROJECT.md` with the 9-system table, profile
   bindings, and `spec_classification` block.
2. Write `projects/pycsl/BL/specifications/main.md`: short
   PyCSL-instance preamble + `<!-- pycsl-include: source=config/skills/csl-from-scratch/SKILL.md scope=L1-BL-plan -->`
   + the BL → System decomposition table mapping Squeeze S1–S9 to
   owning Systems. No new BL prose authored; csl-from-scratch IS
   the BL plan.
3. Create the 9 `BL/SY<N>-<Name>/` dirs with empty
   `requirements/`, `specifications/`, `tests/` subdirs.

After this phase, the tree exists but is bare. Nothing else touched.

### Phase B — Tailor the skills (2-3 days)

Apply all 13 skill-file edits listed above. Pure append-and-extend
operations against existing tables; no rewrites.

Run `bin/doc-coherency.py --check` afterwards to confirm no PyCSL-
domain skill was inadvertently damaged.

### Phase C — Build the 5 tools (3-4 days)

1. `bin/cmmi-mod-index.py` (smallest — 1 day).
2. `bin/cmmi-include-expand.py` with `--verify` mode (1 day).
3. `bin/cmmi-metrics-ingest.py` (1 day).
4. `bin/cmmi-msg-bridge.py` (½ day).
5. `bin/cmmi-audit.sh` (½ day — composition).

### Phase D — Run the import end-to-end (2 days)

1. `bin/agent-import.sh pycsl` (or invoke `import-existing-code`
   directly) — should now run without scaffolding source dirs and
   should produce per-system L2/L3 includes + L4 Module indices.
2. Run the framework audit: `bin/cmmi-audit.sh` — should report 0
   Critical findings.
3. Validate against the negative test: replay the 2026-05-31 13:47:22
   `itertools.cycle` incident through the tailored pipeline. The
   System-level Reconciliator (`agent-feature-supervisor.py`) should
   classify the gap as `iterator-semantics`, increment the per-
   category counter in `metrics/stdlib-gap-report.json`, and when
   threshold (≥5) is met, auto-draft a `missing-iter-feature.md` into
   `proposed-features/`. **Acceptance criterion for the whole
   tailoring**: that draft is recognisably similar in structure to
   the human-authored `missing-iter-feature.md`.

---

## Verification

End-to-end correctness checks for the tailoring:

1. **No source duplication.** `find projects/pycsl/BL -type d -name src`
   returns empty. The C8 check enforces this in CI.
2. **No L5 file generation.** `find projects/pycsl/BL -path '*/UN*-*'`
   returns empty (UN-level units are in-source `#@` contracts only;
   there are no `UN<N>-<Name>/` dirs at all under Profile-P).
3. **L4 indices reflect reality.** For each Module index, count of
   `def` entries equals count in the corresponding `.py` file
   (`bin/cmmi-mod-index.py --verify` mode).
4. **Includes resolve.** `bin/cmmi-include-expand.py --verify` returns
   0 for all `<!-- pycsl-include: ... -->` anchors.
5. **Doc coherency preserved.** `bin/doc-coherency.py --check` still
   passes (no regression from the skill edits).
6. **Framework audit clean.** `bin/cmmi-audit.sh` produces a report
   with 0 Critical and 0 Major findings.
7. **Regression test against 13:47:22 incident.** Replay the
   `itertools.cycle` annotation under the tailored pipeline; confirm
   the Reconciliator auto-drafts a `missing-iter-feature.md`-shaped
   proposal. This is the **acceptance criterion** the user asked for
   — agents should now spot what only the human spotted before.
8. **Single-developer CCB exercised.** Commit a small change to any
   tailored skill; verify the commit SHA appears as the CR-ID in the
   next coherency-audit report.
9. **Squeeze coverage complete.** `bin/cmmi-audit.sh` C8 step 5
   confirms every Squeeze S1–S9 (from `csl-from-scratch` §0.5) has
   ≥1 owning System and every non-glue System owns ≥1 Squeeze. A
   Squeeze with zero owners is a missing-System signal; a System
   with zero Squeezes (not on the glue allow-list) is scope creep.
10. **BL plan include resolves.** The `<!-- pycsl-include: ... -->`
    anchor in `BL/specifications/main.md` resolves to the current
    `config/skills/csl-from-scratch/SKILL.md`; if csl-from-scratch
    moves or is renamed, the audit flags the broken include.

The verification suite is captured in `bin/cmmi-audit.sh` so it can
be added to `bin/run-reference-tests.sh` as the final gate (after
`bin/doc-coherency.py`).

---

## What this plan does NOT do

- Does not modify any `src/<package>/` file.
- Does not generate any L5 (Unit) spec file — the `#@` contracts
  remain the sole Unit-level spec.
- Does not retrofit the 8 `pycsl-*` domain skills to CMMI §1-§6
  format (per should-we-cmmi-or-not.md §6 Rule 3).
- Does not implement `agent-feature-supervisor.py` — that's the
  `better-agent.md` Phase 3 deliverable. This plan only specifies the
  *binding* between the supervisor (when it exists) and the
  Reconciliator role.
- Does not migrate the coordinator's `metrics/`-based pipeline to the
  message-queue substrate in one go — that's the
  `communication` skill's Phase 1/2/3 transition.
- Does not run a baseline QPM — Phase 0 (snapshot accumulation)
  alone, until 8 weekly snapshots exist.

---

## References

- [`config/skills/csl-from-scratch/SKILL.md`](config/skills/csl-from-scratch/SKILL.md)
  — **the BL plan itself**. Its §0.5 Squeeze Strategy is the BL
  requirements set; its phases 0–10 are the long-arc roadmap. The
  BL `specifications/main.md` is an include of this skill plus a
  PyCSL-instance preamble, not separate prose.
- [`config/skills/csl-philosophy/SKILL.md`](config/skills/csl-philosophy/SKILL.md)
  — the family thesis csl-from-scratch operationalizes; referenced
  from the BL preamble for context.
- [`should-we-cmmi-or-not.md`](should-we-cmmi-or-not.md) — the
  recommendation envelope this plan instantiates.
- [`better-agent.md`](better-agent.md) — the Reconciliator design
  whose Phase 1 (gap detection) is the trigger the tailored
  Reconciliator role binds to.
- [`missing-iter-feature.md`](missing-iter-feature.md) — the
  human-authored canonical feature plan; the negative test for the
  tailored framework asks "would the Reconciliator have produced
  this?".
- `config/skills/project-lifecycle/SKILL.md` §4 — the recursive
  level execution this plan parameterises.
- `config/skills/import-existing-code/SKILL.md` — the scaffolder this
  plan pre-configures via `PROJECT.md`.
- `config/skills/pycsl-doc-coherency/SKILL.md` — the existing
  invariant that `cmmi-coherency-audit` delegates to under Profile-P.
- The agent log capture from 2026-05-31 13:47:22 (`itertools.cycle`
  L3-ceiling fallback) — the regression test the framework must
  catch after tailoring.
