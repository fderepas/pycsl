# Agent landscape — how the operational agents map to the CMMI lifecycle roles

This reconciles the **concrete agent topology** (the annotation pipeline and the
coordinator retry loop) with the **role model** in
`config/skills/project-lifecycle/` (the Specifier → Verifier → Reconciliator
triplet per level L1–L5, plus the Phase-10 Coder + Validator leaf, and the
skill-to-role competency matrix). The short version: the per-file annotation
machinery is a faithful, running instance of the lifecycle's **Unit-level (L5)
SVR cycle**, and `agent-feature-supervisor` is a separate **System-level (L2)
Reconciliator** on the orthogonal *feature-rollout* axis.

## 1. The operational hierarchies (ground truth)

**Annotation pipeline (per file):**
```
agent-annotate.py
├── single-function path — direct LLM call using the pycsl-annotate skill
└── multi-function path — delegates to:
    └── agent-splitter.py — call-graph analysis, topological sort (bottom-up)
        └── agent-writer.py — per-function annotation (3-agent pipeline)
            ├── agent-english-writer.py   — English spec of the function
            ├── agent-contract-writer.py  — requires / ensures / assigns
            └── agent-invariant-writer.py — loop invariants & variants
```

**Coordinator loop (per file, up to 10 retries):**
```
coordinator.py
├── agent-annotate.py       → annotated .py in tests/annotated/
├── pycsl (proof)           → exit 0 = pass, exit 1 = fail
│   (if fail)
├── agent-reconcile.py      → diagnosis + recommendation JSON
├── agent-script-update.py  → applies the fix (via MCP)
├── agent-meta-evaluator.py → QA re-check
└── (retry, ≤10)
```

## 2. The lifecycle vocabulary (recap)

Per `project-lifecycle/SKILL.md`: each specification level (L1 Business, L2
System, L3 Component, **L4 Module**, **L5 Unit**) runs
**Synchronize → Delegate → Sub-actors Work → Run Tests → Reconcile**, driven by
a triplet that **must be three distinct agents** (§4 "Independence
constraint"):

- **Specifier** — produces the spec (and a *coordination spec*: interfaces,
  ordering, shared invariants).
- **Verifier** — defines the test plan and **executes** it.
- **Reconciliator** — on a test failure, **diagnoses and routes** the fault to
  the Specifier, Verifier, or sub-actor. "The Reconciliator routes; it does not
  repair." (§2.5)

At the Unit leaf, delegation goes to **Phase 10: Coder + Validator**. And the
**reconciliation loop limit** (§4 T8): *"if the same level fails reconciliation
3 consecutive times without resolution, escalate to SQA/EPG via cmmi-glue
Workflow 3."*

## 3. Level mapping for PyCSL annotation

| Lifecycle unit-of-work | PyCSL artifact | Driven by |
|---|---|---|
| **Module (L4)** | a Python **file** | `agent-annotate.py` (per file) |
| **Unit (L5)** | a **function / method** | `agent-writer.py` (per function) |

A key collapse: in annotation work the *deliverable is the spec* — there is no
separate "implementation," because the `#@` contracts **are** the product. So
the lifecycle's **Specifier** and Phase-10 **Coder** are the *same* concrete
agent here (the contract author), and **Verifier** and Phase-10 **Validator**
collapse onto the prover.

## 4. The core mapping — concrete agent → lifecycle role

| Lifecycle role (L4→L5 / Phase-10) | Concrete agent(s) | Why |
|---|---|---|
| **L4→L5 decomposition + coordination spec** | `agent-splitter.py` | Builds the call graph, Tarjan-SCCs it, topo-sorts leaves-first, and threads callee contracts as context — exactly the "coordination spec" (interfaces, ordering, shared invariants) the Specifier owns. |
| **Specifier (L5 Unit) / Phase-10 Coder** | `agent-writer.py` + its sub-pipeline (`agent-english-writer` → `agent-contract-writer` → `agent-invariant-writer`) | Authors the unit's spec: the English semantics, then `requires`/`ensures`/`assigns`, then loop invariants/variants. The deliverable (contracts) is both the spec and the artifact. |
| **Specifier-side orchestrator** | `agent-annotate.py` | Owns producing a file's spec; chooses single-function (direct) vs multi-function (delegate to splitter→writer). It *drives* specification; it does not author or verify. |
| **Verifier (L5 Unit) / Phase-10 Validator** | `pycsl --proof` | Executes the "test plan" — discharges the proof obligations the contracts induce. exit 0 = pass, exit 1 = fail. |
| ↳ deferred-VC Validator (low level only) | `agent-rocq-proof-writer.py` (Rocq/Lean) | When SMT can't close a goal, the Validator writes a `#@ proof rocq/lean` obligation. Matches the **`L5-Validator`** row of the competency matrix (`rocq`, `rocq-prover`, `lean`). |
| **Reconciliator (L5 Unit)** | `agent-reconcile.py` | On a proof failure, diagnoses the cause and emits a recommendation JSON — it **routes** the fault. It does not repair (lifecycle §2.5). |
| ↳ re-work executor (the routed-to "sub-actor") | `agent-script-update.py` | Applies the recommended fix. In lifecycle terms it is the responsible party correcting its output after the Reconciliator routes the fault — *not* the Reconciliator itself. |
| **SQA / PQA (process audit + escalation)** | `agent-meta-evaluator` (QA re-check), `agent-meta-monitor` (operational health), `agent-meta-reviewer` (human-readable report on halt) | The "objectively evaluate processes" practice; the meta-reviewer's halt report is the Workflow-3 escalation artifact. |
| **Level-cycle driver (the SVR loop itself)** | `coordinator.py` | Runs Synchronize→Delegate→Work→Test→Reconcile per file, with the retry loop. |

## 5. The coordinator loop *is* the Unit-level SVR cycle

Reading the coordinator loop through the lifecycle:

| Lifecycle step | Coordinator action |
|---|---|
| Synchronize (Specifier + coordination spec) | `agent-splitter` computes call-graph order + callee-contract context |
| Delegate / Work (Specifier authors) | `agent-annotate` → `agent-writer` produce the contracts |
| Run the test plan (Verifier) | `pycsl --proof` |
| Reconcile (diagnose + route) | `agent-reconcile` → routes to `agent-script-update` (re-work) |
| Re-run tests / QA | `pycsl` again + `agent-meta-evaluator` |
| **Reconciliation loop limit** | **`coordinator` exit 73** when `agent-reconcile` yields the *same recommendation 3× in a row* |

That last row is an exact correspondence: the lifecycle's *"same level fails
reconciliation 3 consecutive times → escalate to SQA/EPG (Workflow 3)"* is
implemented by coordinator's loop-detection (extracted into
`coordinator_loopdetect.py`), which halts exit 73 = **human-needed** and fires
`agent-meta-reviewer` (the SQA escalation report). Exit 72 (max retries) is the
same escalation on a different trigger.

**Independence constraint, satisfied by construction:** Specifier
(`agent-writer`), Verifier (`pycsl`), and Reconciliator (`agent-reconcile`) are
three genuinely different agents — the lifecycle's "S, V, R must be distinct
personas" rule holds without anyone enforcing it.

## 6. Two axes — annotation vs feature rollout

`agent-feature-supervisor` is **not** part of the per-file annotation loop. It
runs on the orthogonal **feature-rollout axis**: it takes an approved
`missing-*-feature.md` plan and drives it through the verification gate
phase-by-phase. Its persona binds it to the **System-level (L2) Reconciliator**
role (it parses plans whose surface spans L2–L5), and it is *gate-only* — it
routes/halts, it does not author code (the Reconciliator-routes-not-repairs rule
again, one level up). When it does delegate (`--allow-llm-delegation` /
`--allow-load-bearing`), the delegate plays the **Phase-10 Coder**.

The two axes share the **competency matrix**
(`project-lifecycle/references/competency-matrix.md`), which routes skills to
roles by level: `*`→`project-lifecycle` (everyone), L1/L2→`csl-philosophy`,
L3–L5→the `pycsl-annotate` family, and **`L5-Validator`→`rocq`/`lean`** (proof
skills only for the low-level Validator). The supervisor injects these per
phase; the annotation agents load them from the same skills directory.

## 7. Refinement of the "specifier≈annotate, verifier≈writer" intuition

The intuition is *directionally* right — `agent-annotate` is on the
Specifier side — but the precise fit is:

- **Specifier = `agent-writer`** (it *authors* the contracts). `agent-annotate`
  is the Specifier-side **orchestrator/dispatcher** (it owns producing a file's
  spec and chooses how to decompose), and `agent-splitter` is the
  **decomposition + coordination-spec** step. So "low-level specifier" is the
  `annotate → splitter → writer` chain, with `writer` as the authoring core.
- **Verifier = `pycsl` (the prover)**, *not* `agent-writer`. `agent-writer`
  writes the spec; it never checks it. The thing that "defines and executes the
  test plan" is the proof engine. (Mapping the Verifier to `agent-writer` would
  put authoring and checking in the same agent, violating the independence
  constraint — which the real architecture correctly avoids.)

## 8. Observations & gaps

- **The architecture already realizes the lifecycle** at L5 without anyone
  having wired it deliberately — strong evidence the role model is a good fit,
  and a reason to keep the agents independent (don't let `agent-writer` start
  self-verifying).
- **`agent-infer-invariants.py`** is a Specifier-side helper (invariant
  inference) feeding the `agent-invariant-writer` stage.
- **No explicit Cross-level reconciliation** (lifecycle §4: a Unit fault routing
  *up* to the Module level) exists as code — the coordinator reconciles within a
  file. A file-level (L4) reconciliator that re-decomposes when many units fail
  would close that gap.
- **Profile-P note:** for *already-existing* code the Phase-10 Coder is a no-op
  and the Validator is `pycsl --proof` + `run-reference-tests.sh`; for
  *annotation* work the "Coder" is real (it produces the contracts), which is
  why `agent-writer` carries the Coder role here.

---
*References: `config/skills/project-lifecycle/SKILL.md` (§2.5, §3 RACI, §4 T8),
`references/competency-matrix.md`, `references/task-details.md`, and the agents
under `src/pycsl/agents/` (`agent-*.py`, `coordinator.py`,
`coordinator_loopdetect.py`).*
