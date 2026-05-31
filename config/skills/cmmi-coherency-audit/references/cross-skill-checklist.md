# Cross-Skill Coherency Checklist

This reference defines the 7 cross-skill coherency checks (C1–C7) used by the
`cmmi-coherency-audit` skill in Phase C. Each check has a verification procedure,
pass/fail criteria, and evidence requirements.

---

## C1 — Cross-Reference Integrity

### Purpose

Verify that all skill-to-skill references resolve correctly and that no skill
is orphaned (unreferenced by any other skill or persona).

### Verification Procedure

1. For each SKILL.md, extract all references to other skills (by name or path).
2. For each reference, verify the target exists at `config/skills/<name>/SKILL.md`.
3. For each reference, verify the target skill's scope includes the claimed capability.
4. Build a reference graph: nodes = skills, edges = references.
5. Identify orphan nodes (skills with zero incoming edges from other skills AND zero incoming edges from persona `skills:` arrays).

### Pass Criteria

- Every skill reference resolves to an existing skill.
- Every skill has at least one incoming reference (from another skill or a persona).

### Evidence on Failure

- File, line number, and reference text that does not resolve.
- Name of orphan skill with zero incoming references.

---

## C2 — Term/Definition Consistency

### Purpose

Verify that shared terms are defined identically (or compatibly) across all
skills that use them.

### Controlled Terms

| Term | Primary Definition Source |
|---|---|
| Level 1 / Business | `cmmi-process-level` (artifact dimension), `project-lifecycle` (unit-of-work dimension) |
| Level 2 / System | `cmmi-process-level`, `project-lifecycle` |
| Level 3 / Component | `cmmi-process-level`, `project-lifecycle` |
| Level 4 / Module | `cmmi-process-level`, `project-lifecycle` |
| Level 5 / Unit | `project-lifecycle` (unit-of-work dimension) |
| System (unit of work) | `project-lifecycle/references/level-definitions.md` |
| Component (unit of work) | `project-lifecycle/references/level-definitions.md` |
| Module (unit of work) | `project-lifecycle/references/level-definitions.md` |
| Unit (unit of work) | `project-lifecycle/references/level-definitions.md` |
| Extended ETVX | `cmmi-documents` (canonical definition) |
| Configuration Item (CI) | `cmmi-glue`, `cmmi-documents` |
| NCR | `cmmi-glue/references/workflow-catalog.md` |
| Baseline | `cmmi-documents`, `cmmi-glue` |
| RACI | `cmmi-documents` (template definition) |

### Verification Procedure

1. For each controlled term, extract all definitions across all skills.
2. Compare definitions pairwise.
3. Flag any contradictions (incompatible definitions of the same term).
4. Compatible elaborations are acceptable (e.g., cmmi-process-level defines Level 2 by artifacts, project-lifecycle defines Level 2 by unit-of-work — these are complementary views, not contradictions).

### Pass Criteria

- No contradictory definitions exist for any controlled term.
- Terms used without definition in a skill are defined in at least one referenced skill.

### Evidence on Failure

- Term, skill A's definition, skill B's definition, and the contradiction.

---

## C3 — Entry→Exit Chain Validation

### Purpose

Verify that when skill A invokes skill B, A's pre-conditions satisfy B's entry
criteria, and B's exit criteria and outputs satisfy A's expected result.

### Known Invocation Chains

| Invoker | Phase/Task | Invoked Skill | Expected Output |
|---|---|---|---|
| project-lifecycle | Phase 1 | cmmi-process-level | Gap report |
| project-lifecycle | Phase 2 | cmmi-documents + cmmi-glue | Process docs + workflows |
| project-lifecycle | T2–T6 (all levels) | cmmi-documents | Specifications at levels 1–5 |
| project-lifecycle | T7 (Phase 10 — Code + Validate) | agent-project-structure | Directory structure |
| project-lifecycle | Phase 12 | cmmi-glue (Workflow 3) + cmmi-process-level + cmmi-metrics-collection (+ optional cmmi-coherency-audit when `config/skills/` changed) | Project SQA closure outputs + optional framework coherency report |
| cmmi-process-level | Remediation | cmmi-documents | Generated docs to fill gaps |
| cmmi-glue | Role lookup | cmmi-agent-roles | Role definitions |

### Verification Procedure

1. For each invocation chain, extract the invoker's pre-conditions at the invocation point.
2. Extract the invoked skill's ETVX Entry Criteria.
3. Verify that every entry criterion of the invoked skill is either:
   - Explicitly guaranteed by the invoker's pre-conditions, OR
   - Assumed to be satisfied by a prior phase/step.
4. Extract the invoked skill's ETVX Exit Criteria and Outputs.
5. Verify the invoker's post-invocation expectations match the invoked skill's outputs.

### Pass Criteria

- For every invocation chain, the invoked skill's entry criteria are satisfiable given the invoker's context.
- For every invocation chain, the invoked skill's outputs match the invoker's expectations.

### Evidence on Failure

- Invoker file/line, invoked skill file/line, and the unmet entry criterion or mismatched output.

---

## C4 — Output Path Agreement

### Purpose

Verify that skills producing outputs to the same directory use consistent naming
conventions and do not collide.

### Verification Procedure

1. Collect all output path patterns from all skills' ETVX Outputs sections.
2. Group by destination directory.
3. Within each directory, verify:
   - No two skills produce files with the same name pattern.
   - All non-exempt document outputs use the `projects/<project>/docs/` prefix convention.
   - Naming conventions are consistent (e.g., `gap-<app>-001.md`, `brd-<app>-001.md`).
4. Apply the following exemptions to the `projects/<project>/docs/` convention:
   - **Framework configuration outputs** (e.g., persona files under `config/agents/`)
   - **Runtime/messaging outputs** (e.g., message queues under `projects/<project>/message-queues/`)
   - **Source code and test outputs** (e.g., test suites under `tests/`)

   These outputs serve operational purposes distinct from document artifacts and follow their own path conventions.

### Pass Criteria

- No filename collisions between skills for the same output directory.
- All non-exempt document output paths follow the `projects/<project>/docs/` convention.

### Evidence on Failure

- Skill A's output path, skill B's output path, and the collision point.

---

## C5 — Document ID / Baseline ID Uniqueness

### Purpose

Verify that all document IDs and baseline IDs across the skill library are
unique and follow a consistent naming convention.

### Verification Procedure

1. Extract `document_id` from YAML frontmatter of every SKILL.md.
2. Extract `baseline_id` from YAML frontmatter or §1 of every SKILL.md.
3. Check for duplicates in each set.
4. Verify naming convention:
   - Document IDs for CMMI skills: `SKILL-CMMI-<CODE>-NNN` where `<CODE>` is a 3–5 letter code.
   - Document IDs for non-CMMI skills: `SKILL-<CODE>-NNN` where `<CODE>` may be any length and does not include the `CMMI` infix.
   - Baseline IDs: `BL-<CODE>-NNN` where `<CODE>` matches the document ID code.
5. Verify only explicitly exempt non-CMMI skills (agent-project-structure, polish-skill) may omit a baseline ID.

### Pass Criteria

- Zero duplicate document IDs.
- Zero duplicate baseline IDs.
- All IDs follow the naming convention (or are explicitly exempt).

### Evidence on Failure

- The duplicate ID value and the two (or more) skills that share it.

---

## C6 — README Drift

### Purpose

Verify that `README.md` accurately reflects the current state of the skill
library, persona pool, audit history, and practice area coverage.

### Verification Procedure

1. **Skill count:** Count directories in `config/skills/`. Compare to the number stated in the README.
2. **Skill list:** Verify every skill in `config/skills/` appears in the README's skill tables and vice versa.
3. **Dependency diagram:** Verify every edge in the README's dependency diagram corresponds to an actual skill→skill reference.
4. **Directory tree:** Verify the README's ASCII tree matches the actual filesystem structure.
5. **Practice area table:** For each CMMI practice area cited in any skill, verify it appears in the README's practice area table with the correct "Where Addressed" column.
6. **Audit section:** Verify the README's audit section references the latest audit reports in `projects/cmmi/docs/audits/`.
7. **Persona count:** Verify the stated persona count matches `config/agents/` contents.

### Pass Criteria

- All 7 sub-checks pass.

### Evidence on Failure

- The specific README claim, the actual filesystem state, and the discrepancy.

---

## C7 — Metric Framework Coherency

### Purpose

Verify that all KPIs defined in §5 of CMMI skills feed into a coherent
measurement system, with no orphan metrics.

### Verification Procedure

1. Collect all KPIs from §5 of every CMMI skill (name, formula, collection path).
2. Verify each KPI has a declared collection path.
3. Verify each KPI is tied to an organisational objective.
4. Check if `cmmi-glue` Workflow 4 (Continuous Improvement) references or is
   aware of metric sources from all skills.
5. Identify orphan metrics: KPIs defined in a skill but never consumed by any
   governance process or audit.

### Pass Criteria

- Every KPI has a collection path.
- Every KPI has an organisational objective.
- No orphan metrics exist (every metric is consumed by at least one governance workflow or audit).

### Evidence on Failure

- The orphan KPI name, the skill that defines it, and the missing consumer.

---

## Execution Summary Template

After running all 7 checks, record results in this format:

| Check | Pass/Fail | Findings Count | Highest Severity |
|---|---|---|---|
| C1 Cross-reference integrity | | | |
| C2 Term consistency | | | |
| C3 Entry→exit chain | | | |
| C4 Output path agreement | | | |
| C5 ID uniqueness | | | |
| C6 README drift | | | |
| C7 Metric framework coherency | | | |
| **Total** | | | |
