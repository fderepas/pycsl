# Bind the CMMI lifecycle loops to the refactored agents + close two coordinator gaps

> On approval, first copy this plan to repo-root `project-lifecycle-refactor.md`
> (plan-file convention), then execute.

## Context

`config/skills/project-lifecycle/` defines the recursive lifecycle **abstractly**:
roles (Specifier / Verifier / Reconciliator / Coder / Validator) and loops (the
5-step Synchronize→Delegate→Work→Test→Reconcile cycle, the "3 consecutive
failures → escalate via cmmi-glue Workflow 3" rule, the Phase-10 leaf, cross-level
reconciliation). Only **two** concrete agents are bound anywhere: `agent-feature-supervisor`
(the feature-gate axis, T7.1) and `pycsl --proof` (the Profile-P Validator, §6).

But `agent-landscape.md` (repo root) showed the agents we just refactored —
`coordinator.py`/`coordinator_loopdetect.py`, `agent-splitter`, `agent-annotate`,
`agent-writer` (+english/contract/invariant), `pycsl`, `agent-reconcile`,
`agent-script-update`, the `meta-*` trio — **already realize the L5 Unit SVR loop
exactly**, yet the skill never says so, and two loop rules it mandates have **no
executable backing**:

1. The **3-strike reconciliation limit → Workflow-3 escalation**: `coordinator.py`
   halts exit 72/73 and `cmmi-glue/SKILL.md:307` even names the chain
   (`coordinator exit 72/73 → agent-meta-monitor → agent-feature-supervisor → human`),
   but the coordinator emits **no NCR (Non-Conformance Report)** — the artifact
   Workflow 3 is defined around. The escalation signal is informal.
2. **Cross-level (L5→L4) reconciliation**: the skill says a Unit fault diagnosed as
   "Specifier fault" must escalate to the Module level to **re-decompose**
   (`level-definitions.md:320-332`). But `agent-reconcile` emits no fault class, so
   `coordinator` re-patches the same unit on every retry regardless — the L5→L4
   route documented in the lifecycle is never taken.

**Strategic move:** make the documented loops *executable and CMMI-conformant* by
(A) binding roles→agents in the skill (globally, with Profile-P examples) and (B)
closing the two gaps so the 3-strike and cross-level loops actually fire. Outcome:
the lifecycle skill stops being aspirational prose about the annotation pipeline and
becomes a traceable spec the running agents satisfy.

## Decisions (from clarifying questions)

- **Scope:** docs/skill refactor **+ close the two code gaps**.
- **Binding home:** **extend `references/competency-matrix.md`** — it already maps
  role/level→*skills*; add a role/level→*agent* binding alongside.
- **Profile scope:** **global with Profile-P examples** — cite the concrete agents in
  the generic loop text as the reference implementation, each with a "other profiles
  substitute their own actors" note. Preserve the abstract model's portability.

## Established ground truth (verified against the code)

- `reconcile.schema.json`: required `[language, author, recommendation, target]`;
  `target` enum `update-pycsl-scripts | error-in-annotations | unknown`;
  **`additionalProperties:false`** → adding a field REQUIRES a schema edit.
- `coordinator.py` (732 lines): halts **exit 72** (`MAX_RETRIES` exhausted) and
  **exit 73** (`consecutive_similar ≥ 3`, via `coordinator_loopdetect`). It calls
  `agent-annotate.py` as a subprocess (which itself fans out to `agent-splitter` when
  a file has >1 annotatable function) and **re-annotates fresh every attempt**.
- `cmmi-glue/SKILL.md:307` already binds the Workflow-3 escalation chain to
  `coordinator exit 72/73`; the NCR is the missing artifact.
- No `config/schemas/ncr.schema.json` exists yet.
- The independence constraint (S≠V≠R) is satisfied de-facto by distinct agents
  (`agent-writer` / `pycsl` / `agent-reconcile`) even though Profile-P formally
  relaxes it to single-developer CCB — worth recording.

---

## Part A — Skill refactor: bind the loops to agents

### A1. `references/competency-matrix.md` — add the role→agent binding (canonical home)
The matrix today resolves `<level>` / `<level>-<role>` → skills. Add a second,
parallel block mapping the **CMMI role realization** to the concrete agent, derived
from `agent-landscape.md`. New fenced block (same line-tag resolver style):
```
# role → reference-implementation agent (Profile-P; other profiles substitute)
L4-Decompose:    agent-splitter            # call-graph + coordination spec
L5-Specifier:    agent-writer (+ english/contract/invariant)   # authors #@ contracts
L5-Orchestrator: agent-annotate            # per-file specify dispatcher
L5-Verifier:     pycsl --proof             # executes the proof obligations
L5-Validator:    pycsl --proof + agent-meta-evaluator
L5-Reconciliator: agent-reconcile          # diagnoses + routes; does not repair
L5-ReworkExec:   agent-script-update       # the routed-to sub-actor
CycleDriver:     coordinator               # runs the L5 SVR loop per file
SQA/PQA:         agent-meta-monitor, agent-meta-reviewer
FeatureGate:     agent-feature-supervisor  # orthogonal L2 rollout axis
```
Add prose: (i) the binding is the **reference implementation** — non-PyCSL profiles
substitute their own actors; (ii) the independence-constraint note (distinct
agents); (iii) cite `agent-landscape.md` as the derivation.

### A2. `SKILL.md` — annotate the loop/role text with the reference agents
Edit additively (house style: imperative, binary, traceable — §"Writing Constraints"):
- **5-step SVR cycle** (lines 73–84) + **§3 RACI** / **References & Definitions**
  (123–129): after each role definition add a parenthetical
  "(reference impl: `agent-…`; other profiles substitute)".
- **T6 — Unit Level** (350–365): note the L5 cycle is realized by `coordinator.py`
  driving `agent-annotate`→`agent-splitter`→`agent-writer` (Specify), `pycsl`
  (Test), `agent-reconcile`→`agent-script-update` (Reconcile).
- **T7 — Phase-10 leaf** (367–377): bind Coder=`agent-writer` (authors contracts —
  the deliverable *is* the spec), Validator=`pycsl --proof` + `agent-meta-evaluator`.
  Keep the existing Profile-P "Coder is a no-op for existing code" note.
- **T8 — reconciliation loop limit** (line 410): bind to `coordinator` exit 73 +
  `coordinator_loopdetect` + the new NCR (Part B1) flowing into
  `cmmi-glue` Workflow 3 (cite `cmmi-glue/SKILL.md:307`).
- **T8 — cross-level reconciliation** (line 411): bind to the new fault-class routing
  (Part B2): Specifier-fault at L5 → `agent-splitter` re-decompose at L4.
- **§6 Profile-P bindings** (523–536): add a one-line pointer to the
  competency-matrix agent block as the worked Profile-P example.

### A3. `references/v-model-phases.md` + `task-details.md` — bind the leaf/consensus loops
- `v-model-phases.md` Phase-10 leaf (621–663) and reconciliation routing (97–105):
  add the reference-agent mapping + the NCR-on-3-strike termination artifact.
- `task-details.md` "Coder-Validator consensus loop" (222) and Phase-10 reconcile
  routing (219–233): bind the three fault routes to `agent-script-update` (sub-actor)
  / `agent-splitter` re-decompose (specifier) / Rocq-fallback-or-human (verifier).
- `level-definitions.md:320–332` (cross-level escalation): cite the concrete L5→L4
  realization.

> All Part-A edits are **additive parentheticals / notes** — the abstract model
> reads unchanged for profiles S/M/L. No role prose is deleted.

---

## Part B — Close the two code gaps

### B1. GAP 1 — `coordinator` exit-72/73 emits a Workflow-3 NCR artifact
The NCR is produced **by the coordinator** (deterministic governance artifact), not
by the LLM meta-reviewer, and must be emitted even if the reviewer LLM call fails.
- New `config/schemas/ncr.schema.json` (fields derived from
  `cmmi-glue/references/workflow-catalog.md:192-271`): `ncr_id`, `date_issued`,
  `issued_by` (=`coordinator`), `responsible_role`, `checkpoint`, `finding`,
  `gate_failed` (="Gate 1"), `evidence` (recurring recommendation, target, retry
  count, consecutive count, exit code, log paths), `severity`, `response_timeframe`,
  `escalation_path` (the `SKILL.md:307` chain string), `cap_placeholder`,
  `status` (="OPEN").
- New `coordinator.write_ncr(*, exit_code, annotated_file, recommendation, history,
  attempt, consecutive) -> Path`: builds the dict from loop state, validates via the
  existing `schema_validator.validate_or_warn(ncr, "ncr", …)`, writes
  `logs/NCR-<UTC-ts>-<stem>.md` (Markdown body + embedded fenced JSON, matching the
  timestamped-`.md` `logs/` convention so it is both human- and metric-ingestible).
- **Emit points:** the exit-72 block (`coordinator.py:587-600`) and the exit-73 block
  (`:623-637`), **before** the existing meta-reviewer call. `responsible_role` derives
  from the role→agent binding (A1): `error-in-annotations`→Specifier(`agent-writer`/
  `agent-splitter`); `update-pycsl-scripts`→sub-actor(`agent-script-update`).
- **Traceability:** the NCR `escalation_path` hard-codes the `SKILL.md:307` chain and
  the coordinator logs `"NCR-… emitted per cmmi-glue Workflow 3"`.
- **Exit-code contract preserved:** no new codes; emission is purely additive.

### B2. GAP 2 — cross-level (L5→L4) reconciliation routing
- **`agent-reconcile.py`**: add a 5th field `fault_class` ∈ `{specifier, verifier,
  sub-actor}` (`build_prompt` rubric + `required_keys` at `:312`); edit
  `reconcile.schema.json` (add to `properties` + `required`, keep
  `additionalProperties:false`). Map: *sub-actor* = unit body/annotation detail wrong;
  *specifier* = the file decomposition / callee-contract ordering is wrong (cannot be
  fixed in this unit alone); *verifier* = proof obligations mis-scoped (→ Rocq fallback
  or human; treat as sub-actor unless a third branch is wanted).
- **`coordinator`**: new `route_reconciliation(...)` inserted between
  `recommendation_history.append(...)` (`:646`) and `apply_recommendations(...)`
  (`:648`). Branch on `recommendation.get("fault_class", "sub-actor")` (default keeps
  current behavior, backward-compatible):
  - `sub-actor` → `apply_recommendations` (unchanged).
  - `specifier` → new `redecompose_at_l4(...)`: invoke `agent-splitter.py` as a
    subprocess on the file (the L4 actor revising decomposition / callee-contract
    order), logged like the rest of the loop; guard the next iteration's
    unconditional re-annotate (`:577`) so the re-decomposed artifact is the one proved
    (the escalation must be observable, not masked by the fresh re-annotate).
- **Ping-pong guard (bounded recursion, ER):** add per-file `redecompose_count`,
  cap `MAX_REDECOMPOSE = 2`; on exceed, halt through the **existing exit 73** (no new
  code) with NCR `finding="L5↔L4 ping-pong: re-decomposition exceeded N without
  convergence"`. Identical-recommendation streaks already trip the 3-strike;
  alternating faults are caught by this cap. (The `CMMI_AUDIT_NESTED` shell guard does
  NOT cover this Python path — this cap is its analogue.)
- Optional: fold `fault_class` into `coordinator_loopdetect.rec_key` to catch
  same-fault streaks earlier — separate, behavior-changing, re-run its unit tests.

---

## Critical files
- `config/skills/project-lifecycle/references/competency-matrix.md` — role→agent binding (A1).
- `config/skills/project-lifecycle/SKILL.md` — loop/role agent annotations (A2).
- `config/skills/project-lifecycle/references/{v-model-phases,task-details,level-definitions}.md` — leaf/consensus/cross-level binding (A3).
- `src/pycsl/agents/coordinator.py` — `write_ncr`, `route_reconciliation`, `redecompose_at_l4`, ping-pong cap (B1+B2).
- `src/pycsl/agents/agent-reconcile.py` + `config/schemas/reconcile.schema.json` — `fault_class` (B2).
- `config/schemas/ncr.schema.json` — NEW (B1).
- `agent-landscape.md` — cited as the binding's derivation (kept at repo root).

## Verification
- **Schema discipline:** `fault_class` lands in prompt + `required_keys` + schema
  atomically; coordinator defaults absent `fault_class`→`sub-actor` (no validation
  warnings on old outputs).
- **Tests** (`test-suite/agent-tests/`, currently 72 green — must stay green):
  - NEW `test_coordinator_ncr.py`: exit-72 and exit-73 each write an NCR that
    validates against `ncr.schema.json`; emitted even when the meta-reviewer is stubbed
    to fail; `escalation_path` matches the `SKILL.md:307` chain.
  - NEW `test_coordinator_routing.py`: `fault_class="specifier"` invokes the
    re-decompose path (mock `agent-splitter`), `"sub-actor"` invokes
    `apply_recommendations`; `redecompose_count` cap → exit 73 + ping-pong NCR.
  - EXTEND reconcile schema test: `fault_class` required + enum + still
    `additionalProperties:false`.
  - Re-run `test_coordinator_loopdetect.py` (unchanged unless the optional `rec_key`
    fold is taken).
- **End-to-end:** `CMMI_AUDIT_NESTED=1 timeout 120 .venv/bin/python3 -m pytest
  test-suite/agent-tests/ -q` → all green; a forced-failure corpus file through
  `coordinator.py` produces an NCR in `logs/` and halts exit 73.
- **Doc coherence:** `bin/doc-coherency.py` (if it covers skills) + manual grep that
  every agent named in `competency-matrix.md` exists under `src/pycsl/agents/`.
- **CMMI gate:** `CMMI_AUDIT_NESTED=1 timeout 300 bin/cmmi-audit.sh` unaffected.
- **ER spirit:** exit-code contract unchanged; recursion bounded; every binding
  traceable agent↔role↔`agent-landscape.md`; no abstract role prose deleted (S/M/L
  profiles read unchanged).

## Out of scope
- The `verifier`-fault third branch beyond routing to the existing Rocq-fallback/human.
- Moving `agent-landscape.md` into the skill tree (kept at root, cited).
- This is an agent/skill refactor, not a new PyCSL language feature → no
  `test-suite/corpus/pycsl-reference/` addition required.
