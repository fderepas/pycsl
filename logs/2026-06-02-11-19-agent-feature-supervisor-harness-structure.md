# Agent harness structure — agent-feature-supervisor

Recorded before launching any agent, by `bin/agent-feature-supervisor`.

| Field | Value |
|---|---|
| Generated (local) | 2026-06-02-11-19 |
| Invocation | `./bin/agent-feature-supervisor --feature-file make-it-work.md --skip-gate` |
| Feature file | `make-it-work.md` |
| Run mode | gate-only (default): NO LLM agent launched; the verification gate runs and load-bearing phases halt human-needed; --skip-gate: gate skipped (parse + classify + acceptance only) |
| Configured LLM (`config/agents-config.json` → `model`) | `claude-sonnet-4.6` |
| Ollama endpoint (`llm-ollama-url`) | `http://192.168.1.111:11434` |

## 1. Potential agents and their roles

### 1.1 Executable agents this invocation

| Agent | Role | When it runs this invocation |
|---|---|---|
| **agent-feature-supervisor** | Feature-rollout Reconciliator (Extreme Rigor). Parses the plan's `## Implementation surface`, classifies target files against the load-bearing deny-list, evaluates each phase's `**Acceptance:**` claims, runs the gate, halts on first failure. **Does not write code.** Binds to the **L2 System Reconciliator** role in §1.2. | Always (this process) |
| **verification gate** | Not an LLM agent. Runs the project gate: `bin/cmmi-audit.sh`, `bin/doc-coherency.py`, `bin/run-reference-tests.sh`. Executes the per-level **Verifier** test plans. | Default mode, when no load-bearing hit and not `--skip-gate` |
| **coding-LLM delegate** | Executes the **Phase-10 Coder** role (§1.2): given one phase + its target-file contents, produces a unified diff. Inherits the supervisor's ER persona. | Only with `--allow-llm-delegation` AND no load-bearing hit; one delegate per open phase |

### 1.2 Specifier / Verifier / Reconciliator per level, and the Phase-10 leaf

Every level runs a **Specifier → Verifier → Reconciliator** (SVR) loop (§3); the
three MUST be distinct personas. The Unit level delegates to the **Phase-10
Coder + Validator** consensus loop. Source of these role assignments:
`config/skills/project-lifecycle/SKILL.md` §3 (RACI) + `references/task-details.md`
(T2–T7).

| Level | Specifier | Verifier | Reconciliator | Coder / Validator (leaf) |
|---|---|---|---|---|
| **L1 Business** | Business Analyst / Product Owner — BRD, system decomposition + coordination spec (`config/agents/business-analyst.md`) | UAT Test Engineer — UAT test plan | Reconciliator — diagnoses Specifier-fault vs Verifier-fault on UAT failure | — (delegates to L2) |
| **L2 System** | System Architect — SRS/SAD/ICD, component decomposition | System Test Engineer — system + integration test plan | Reconciliator — **agent-feature-supervisor binds here** | — (delegates to L3) |
| **L3 Component** | Technical Lead — HLD, module decomposition | Integration Test Engineer — component integration tests | Reconciliator | — (delegates to L4) |
| **L4 Module** | Software Engineer — MLD, unit decomposition | Module Test Engineer — module tests | Reconciliator | — (delegates to L5) |
| **L5 Unit** | Software Engineer — LLD, formal `#@` pre/post annotations | Unit Test Engineer — unit tests / proof obligations | Reconciliator | **Phase 10:** Coder implements the body in `src/`; Validator verifies (`pycsl --proof`). Coder–Validator consensus loop |

**Executable agents that realize these roles** (in `src/pycsl/agents/`):
- **Reconciliator engine:** `agent-reconcile.py` (diagnoses proof failures; the
  coordinator applies its recommendations via `agent-script-update.py`).
- **L5 Specifier (formal-contract authoring) pipeline:** `agent-english-writer`
  → `agent-contract-writer` → `agent-invariant-writer` / `agent-writer`;
  Rocq obligations via `agent-rocq-proof-writer`.
- **Phase-10 Coder:** the coding-LLM delegate above (§1.1), or `coordinator.py`'s
  annotate→prove→reconcile loop.
- **Meta-observability** (cross-level): `agent-meta-evaluator`,
  `agent-meta-monitor`, `agent-meta-reviewer`.

> Under **Profile-P (PyCSL)** the L4/L5 Specifier specs are auto-generated
> (`bin/cmmi-mod-index.py`) or the in-source `#@` contracts, and the Phase-10
> Coder step is a no-op (code already exists) — the Validator step is
> `pycsl --proof` + `bin/run-reference-tests.sh`.

## 2. Per-agent details (source, harness, LLM)

### agent-feature-supervisor (orchestrator)
- **Source:** `bin/agent-feature-supervisor` (this wrapper) → `src/pycsl/agents/agent-feature-supervisor.py`
- **Persona:** `config/agents/agent-feature-supervisor.md` (role: Feature-rollout Reconciliator; level_alignment L2–L5)
- **Harness:** in-process Python; gate dispatched via `run_gate()` (subprocess to the gate scripts). Exit-code convention extends `coordinator.py` (72/73) with 74 gate-fail / 75 human-needed / 76 rollback.
- **LLM:** none in default (gate-only) mode.

### verification gate
- **Source:** `run_gate()` in `src/pycsl/agents/agent-feature-supervisor.py`
- **Harness:** subprocess to `bin/cmmi-audit.sh`, `bin/doc-coherency.py`, `bin/run-reference-tests.sh`
- **LLM:** none.

### coding-LLM delegate (potential; `--allow-llm-delegation`)
- **Source:** `_delegate_phase()` / `_build_phase_prompt()` in `src/pycsl/agents/agent-feature-supervisor.py`
- **Prompt scaffold:** `config/skills/csl-from-scratch/references/coding-llm-prompt.md`, with the supervisor persona (`config/agents/agent-feature-supervisor.md`) prepended so the delegate inherits ER discipline.
- **Harness:** `src/pycsl/agents/llm_client.py` (`llm_generate`) — dispatches to either Ollama (`/api/generate`, `llm-ollama-url`) or the GitHub Copilot CLI, selected per `config/agents-config.json`.
- **LLM:** the configured `model` (see metadata table above); Ollama default tag is `gemma4:31b`, Copilot example `claude-opus-4.6`.

## 3. Loops (clearly stated)

- **This run — per-phase loop (agent-feature-supervisor):** for each phase in
  the Implementation surface → classify targets vs deny-list → (if delegation
  enabled and no deny hit) dispatch a coding-LLM delegate → evaluate the phase's
  acceptance claims → halt on first failure (no further phases).
- **Specifier → Verifier → Reconciliator (SVR) triplet, per level:**
  `Synchronize → Delegate → Sub-actors Work → Run Tests → Reconcile`.
  *Reconcile fires only if a test fails.* The Specifier, Verifier, and
  Reconciliator at a level MUST be distinct agents/personas. The
  agent-feature-supervisor binds to the **System-level Reconciliator** role.
  (Defined in `config/skills/project-lifecycle/SKILL.md` §4 + `references/task-details.md`.)
- **Reconciliation loop limit:** 3 consecutive failed reconciliations at the
  same level → escalate to SQA/EPG (`cmmi-glue` Workflow 3).
- **coordinator.py retry loop:** annotate → prove → reconcile → re-prove, up to
  `MAX_RETRIES` (exit 72); identical recommendation 3× in a row → loop-detected
  halt (exit 73, human needed).

## 4. Hierarchy (the level below)

Each level delegates to the level below; the lowest level delegates to Phase 10.

```
L1 Business
  └─ delegates to → L2 System            (agent-feature-supervisor binds here)
        └─ delegates to → L3 Component
              └─ delegates to → L4 Module
                    └─ delegates to → L5 Unit
                          └─ delegates to → Phase 10 (leaf): Coder + Validator
```

- A feature plan's Implementation surface spans **L2–L5** (Grammar/Module4
  through stub refresh + tests), per the supervisor persona's `level_alignment`.
- At each level the SVR triplet (§3) operates; a sub-actor fault at level N
  triggers reconciliation at level N−1, which may escalate back to level N.
- Phase 10 is the leaf: the Coder implements and the Validator confirms the
  contract (under Profile-P the Coder step is a no-op — code exists; the
  Validator step is `pycsl --proof` + `bin/run-reference-tests.sh`).

---
*Reference: `config/skills/project-lifecycle/references/feature-plan-submission.md`
(submission workflow) and `config/agents/skill-agents.md` (agent catalog).*
