# Competency matrix — which skills each level/role needs

This is the **skill-to-role** companion of the RACI activity-to-role matrix in
`SKILL.md` §3. It declares, per execution level (L1–L5), which skills an agent
operating at that level must have in context. It is **declarative data**, not an
agent: `bin/agent-feature-supervisor` reads the fenced block below to resolve and
inject the right skills per phase (and logs the resolution in the
harness-structure record's `## 5` section for human review). See
[`feature-plan-submission.md`](feature-plan-submission.md)
§"Giving an agent its skills (context, not RAG)" for the delivery mechanism.

## How a phase is keyed

A feature-plan phase declares its level — and, optionally, its SVR/Phase-10
role — with line-leading tags:

```
### Phase N — <title>
**Level:** L5
**Role:** Validator
```

The resolver injects the union of three rows: the `*` row (every level), the
phase's `L<n>` row, and — if a `**Role:**` is given — the combined
`L<n>-<Role>` row. A phase with no `**Level:**` gets only `*`; a phase with no
`**Role:**` gets no role-specific skills.

## The matrix

Each line is `<key>: <skill>, <skill>, …` where `<key>` is `*` (all levels),
`L1`–`L5` (a level), or `L<n>-<Role>` (a level+role combination, e.g.
`L5-Validator`). Each `<skill>` is a directory under `config/skills/` (the
resolver inlines that skill's `SKILL.md`).

```
*:  project-lifecycle
L1: csl-philosophy
L2: csl-philosophy, pycsl-annotate, agent-stdlib-annotate
L3: pycsl-annotate, agent-stdlib-annotate
L4: pycsl-annotate, contract-writer, invariant-writer, agent-stdlib-annotate, acsl
L5: pycsl-annotate, contract-writer, invariant-writer, english-writer, pycsl-exception-model, agent-stdlib-annotate, acsl, pycsl-audit-pycsl-language
L5-Validator: rocq, rocq-prover, lean
```

## Role → reference-implementation agent

The matrix above says *which skills* a role needs; this block says *which concrete
agent* realizes that role in this project. It is the executable counterpart of the
abstract SVR / Phase-10 roles in `SKILL.md` §2–§4: the lifecycle loop is not just
described, it runs — `coordinator.py` drives the Unit-level
Synchronize→Delegate→Work→Test→Reconcile cycle over the agents below. This binding
is the **reference implementation** (Profile-P); other profiles substitute their own
actors (human Specifiers/Verifiers, other tools) for the same roles. The full
derivation is in repo-root [`agent-landscape.md`](../../../../agent-landscape.md).

```
# role (level / SVR / Phase-10)        →  agent under src/pycsl/agents/
L4-Decompose                           →  agent-splitter        # call graph + coordination spec (decomposition + callee-contract order)
L5-Specifier / Phase-10 Coder          →  agent-writer          # authors #@ contracts (via english-/contract-/invariant-writer)
L5-Specifier-Orchestrator              →  agent-annotate        # per-file dispatcher (single-fn direct vs multi-fn → splitter)
L5-Verifier / Phase-10 Validator       →  pycsl --proof         # executes the proof obligations; + agent-meta-evaluator (QA re-check)
L5-Reconciliator                       →  agent-reconcile       # diagnoses + routes (fault_class); does NOT repair
L5-ReworkExecutor (sub-actor)          →  agent-script-update   # applies the routed fix
CycleDriver (level execution task)     →  coordinator           # runs the L5 SVR loop per file; halts 72/73 + emits Workflow-3 NCR
SQA / PQA                              →  agent-meta-monitor, agent-meta-reviewer
FeatureGate (orthogonal L2 axis)       →  agent-feature-supervisor   # plan→gate rollout, not the per-file loop
```

**Independence constraint, satisfied by construction.** `SKILL.md` §4 requires the
Specifier, Verifier, and Reconciliator at a level to be *different* agents. Here they
are three distinct programs — `agent-writer` (Specifier), `pycsl` (Verifier),
`agent-reconcile` (Reconciliator) — so the constraint holds even though Profile-P
formally relaxes governance to a single-developer CCB.

## Rationale (the subtle knowledge)

- **`*` → `project-lifecycle`.** Every agent must understand the
  Synchronize→Delegate→Work→Test→Reconcile lifecycle and the submission
  contract, regardless of level.
- **L1 Business / L2 System → `csl-philosophy`.** The "why" (the squeeze
  strategy, what verification buys) is load-bearing for the agents that *shape*
  systems and decompose them; it is wasted detail at the leaf.
- **Low-level specifiers (L3–L5) → the `pycsl-annotate` family.** Agents that
  actually write `#@` contracts need the annotation language in full: the core
  `pycsl-annotate` skill, plus `contract-writer` / `invariant-writer` /
  `english-writer` (the 3-agent annotation pipeline) and `pycsl-exception-model`
  at the Unit level, where `requires`/`ensures`/`raises`/`loop invariant` are
  authored. L2 also gets `pycsl-annotate` because System-level phases in this
  project still author stub contracts.
- **ACSL reference (`acsl`) → L4 + L5 specifiers.** PyCSL's `#@` contract
  surface is an ACSL-family language; `acsl` is the upstream reference for the
  semantics of `requires`/`ensures`/`assigns`, loop invariants/variants,
  quantifiers, and `behavior`/`assumes`/`complete`/`disjoint`. Agents authoring
  module- (L4) and unit-level (L5) contracts benefit from the authoritative
  behavioral-spec semantics. (It is a C/Frama-C reference, not PyCSL syntax — use
  it for *meaning*, not literal `#@` form.)
- **`pycsl-audit-pycsl-language` → L5.** This audits that a *change to the PyCSL
  language itself* (grammar → validate → IR → WhyML, plus docs + corpus) is
  consistent end-to-end. It is a toolchain-development skill, not a
  contract-authoring one, so it does not fit the level model cleanly; it is keyed
  at L5 because Module2–6 / grammar change-phases land at the deepest
  implementation level. Phases that only author contracts will carry it as
  inert context.
- **Proof skills are role-scoped, not level-scoped.** `rocq` / `rocq-prover` /
  `lean` go to **`L5-Validator`** only — the low-level (Unit / Phase-10)
  **Validator**, who discharges proof obligations and writes `#@ proof rocq` /
  `#@ proof lean` citations when the SMT solvers cannot close a VC. They are
  *not* given to L5 specifiers/coders (who author the contracts, not the
  proofs) nor to higher levels — so a phase receives them only when tagged
  `**Level:** L5` **and** `**Role:** Validator`.

## Delivery (orthogonal to this matrix)

This matrix decides *which* skills a role needs; how they reach the agent is a
separate concern (`feature-plan-submission.md`):

- **Small / load-bearing** skills are inlined as **direct text** (deterministic,
  auditable — what reached the agent is in `## 5` of the harness log).
- **Large** reference corpora (e.g. the full `unix/` skill, `csl-philosophy`'s
  references) are candidates for **RAG** retrieval of the relevant slice rather
  than whole-file inlining. Until that is wired, prefer naming the *specific*
  `references/*.md` a phase needs over the whole skill.

## Changing the matrix

This file is a Configuration Item under `BL-LIFE-001`. Adding a skill or
re-keying a row is a Change Control action (`cmmi-glue` Workflow 2); record the
rationale. Authoring/auditing the mapping is a human (or one-shot agent) task —
the runtime resolver only *reads* this matrix, it does not infer it.
