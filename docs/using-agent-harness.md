# Using the agent harness (`bin/agent-feature-supervisor`)

How to drive the feature-rollout supervisor — the agent harness that takes an
approved, executable feature plan and either **verifies** it or **delegates its
phases to a coding LLM**, phase by phase, behind a proof gate.

- **Entry point:** `bin/agent-feature-supervisor` (a thin wrapper) →
  `src/pycsl/agents/agent-feature-supervisor.py`.
- **Plan format:** `## Implementation surface` with `### Phase N` headers and
  `**Acceptance:**` blocks. The bullet grammar is normative in
  [`config/skills/csl-from-scratch/references/acceptance-syntax.md`](../config/skills/csl-from-scratch/references/acceptance-syntax.md);
  the submission workflow is in
  [`config/skills/project-lifecycle/references/feature-plan-submission.md`](../config/skills/project-lifecycle/references/feature-plan-submission.md).

> **One-line recursion guard.** A full run can re-enter the ER retrospective via
> the gate and CPU-explode. Run foreground with a timeout and the nested guard:
> `CMMI_AUDIT_NESTED=1 timeout 300 bin/agent-feature-supervisor --feature-file f.md …`

## What one invocation does

In order — any step may halt the run:

1. **Records the harness structure** to `logs/<YYYY-MM-DD-HH-MM>-agent-feature-supervisor-harness-structure.md` (the agents/roles/loops/hierarchy that *could* run). First action, so it exists even on abort.
2. **Parses phases** from the plan's `## Implementation surface`.
3. **Classifies targets** against the load-bearing deny-list ([`config/skills/agent-stdlib-annotate/references/load-bearing-files.md`](../config/skills/agent-stdlib-annotate/references/load-bearing-files.md)).
4. **Completeness guard** — halts `MISSING_ACCEPTANCE` if an open phase has no `**Acceptance:**` block.
5. **Evaluates every acceptance claim** (re-runs the commands) → `PASS` / `FAIL` / `STATUS_VERIFIED` (for `**Status:** DONE` phases).
6. **Acts**, depending on flags (see Modes below): halt, verify-gate, or **delegate to a coding LLM**.
7. **Writes a halt-report** to `metrics/feature-supervisor/<plan-stem>/halt-report.md` on any halt.

## Flags

| Flag | Effect |
|---|---|
| `--feature-file <path>` | **Required.** The executable plan to run. |
| `--skip-gate` | Parse + classify + evaluate acceptance only; skip the verification gate. Useful for a dry run. |
| `--allow-llm-delegation` | Turn on coding-LLM delegation for **non-load-bearing** phases (off by default → gate-only v1). |
| `--allow-load-bearing` | Also delegate phases that touch **load-bearing** files. **Implies `--allow-llm-delegation`.** See the deep-dive below. |

## Modes

- **Verify-only (default).** No flags beyond `--feature-file`. The supervisor
  evaluates acceptance and (unless `--skip-gate`) runs the gate. It **never
  edits code.** If any open phase names a load-bearing file it halts
  `Human-needed`. This is the "a human/agent implements, the supervisor verifies"
  contract.
- **Delegation (`--allow-llm-delegation`).** For each open phase **not** touching
  a load-bearing file, the supervisor asks a coding LLM for a diff, applies it,
  runs the gate, and keeps it only if the gate passes (else rolls back).
- **Load-bearing delegation (`--allow-load-bearing`).** As above, but also for
  phases that touch load-bearing files. The deliberate, riskier mode below.

## `--allow-load-bearing` — what it actually does

By default the supervisor is **gate-only**: it refuses to autonomously edit
load-bearing files (the parser/IR/emitter pipeline — `Module2`–`Module6`,
`module6_whyml/*`, `csl.lark`, `ir_schema.py`, `exception_model.py`,
`formal-semantics/`, the three normative `docs/pycsl-*-reference.md`). Two guards
enforce this:

1. it **returns on acceptance failure** before reaching delegation, and
2. delegation is gated `and not deny_hits`.

`--allow-load-bearing` **lifts both guards** (and implies
`--allow-llm-delegation`):

- It does **not** halt on failing acceptance — those failing claims *are* the
  work to build, so it falls through to delegation. (A `CLAIM_REJECTED` — an
  unsafe acceptance command — still halts; that's a malformed plan, not work.)
- It lets delegation run on deny-listed phases instead of issuing the
  `Human-needed` halt.

It does **not** weaken the proof guarantee. Each delegated phase still goes
through the same safety pipeline (`_delegate_phase`):

1. **Tag** `HEAD` as `feature-<plan-stem>-phase-<N>-start` (the rollback point).
2. **Ask the LLM** for a unified diff for that phase (prompt = the phase body +
   current target-file contents + the coding-LLM scaffold + the supervisor's ER
   persona).
3. **`git apply`** the diff.
4. **Run the verification gate** (`cmmi-audit`, `doc-coherency`,
   reference tests).
5. **On gate failure → roll back** to the start tag (so no partial/bad edit
   survives) and **halt** on that phase.
6. **On success → keep** the edit and the tag (audit trail), continue to the
   next phase.

So the net contract is: **agents may *attempt* load-bearing edits, but only
edits that pass the full proof gate survive, and a surviving diff still requires
human review before merge.** The supervisor prints a red banner to that effect.

> **Why the deny-list still matters.** The gate catches *breakage* (a proof or
> test that fails). It does **not** catch every *subtle unsoundness* an LLM could
> introduce into the emitter (e.g. a change that makes VCs vacuously true). That
> residual risk is exactly why these files are on the deny-list and why
> `--allow-load-bearing` is opt-in and loud. **Review every surviving
> load-bearing diff before merging.**

## Choosing the LLM backend

The delegate model is resolved by `_delegate_model()`:

1. the `PYCSL_LLM_MODEL` environment variable, else
2. the `model` key in `config/agents-config.json`, else
3. `claude-sonnet-4.6`.

Routing (`llm_client.llm_generate`): a model name starting with `claude-` or
`gpt-` goes to the **GitHub Copilot CLI** (`copilot`); any other name is treated
as an **Ollama tag** and POSTed to the Ollama server at `OLLAMA_URL` (env, else
the `llm-ollama-url` config key).

Examples:

```sh
# Default: uses agents-config.json `model` (claude-sonnet-4.6) → Copilot CLI.
bin/agent-feature-supervisor --allow-load-bearing --feature-file plan.md

# Force a local Ollama coder model (pull a capable one first).
OLLAMA_URL=http://127.0.0.1:11434 PYCSL_LLM_MODEL=<coder-tag> \
  bin/agent-feature-supervisor --allow-load-bearing --feature-file plan.md
```

Prerequisites: for a `claude-*`/`gpt-*` model the **`copilot` CLI must be
installed and authenticated**; for an Ollama model the **server must be
reachable** and have the tag pulled.

## Exit codes

| Code | Meaning |
|---|---|
| 0 (`EXIT_OK`) | All phases passed / finished without action. |
| 74 (`EXIT_GATE_FAIL`) | Verification gate failed, or a delegated phase couldn't land a gate-green diff. |
| 75 (`EXIT_HUMAN_NEEDED`) | `MISSING_ACCEPTANCE`, `ACCEPTANCE_FAILED`, `STATUS_FORGED`, `CLAIM_REJECTED`, or a load-bearing target in verify-only mode. |
| 76 (`EXIT_ROLLBACK_FAIL`) | Per-phase git-tag rollback failed (v1 stub). |

The terminal output and the halt-report's `## What this means` section explain
which case fired (two exit-75 halts mean very different things — read the reason
string).

## Outputs

- **Harness-structure log:** `logs/<timestamp>-agent-feature-supervisor-harness-structure.md`.
- **Halt-report:** `metrics/feature-supervisor/<plan-stem>/halt-report.md` — parsed phases, deny-list hits, acceptance failures, next steps.
- **Rollback tags:** `feature-<plan-stem>-phase-<N>-start` (delete stale ones with `git tag -d`).

## The `**Status:** DONE` workflow

When a phase is finished and reviewed, mark it `**Status:** DONE` in the plan
(keep its `**Acceptance:**` block). Then:

- The supervisor **ignores DONE phases' targets** for deny-list classification —
  so a fully-DONE plan re-runs without a `Human-needed` halt.
- It still **re-verifies** each DONE phase's claims every run; a regression flips
  it to `STATUS_FORGED` (exit 75) — a lie-detector on the DONE marker.

This is the sign-off ritual: implement → verify green → review → mark DONE → the
plan becomes a standing regression guard.

## Worked example (the cross-file-inheritance rollout)

```sh
# Verify-only: all green but halts Human-needed (load-bearing targets named).
bin/agent-feature-supervisor --feature-file broad-cross-file-feature-exec.md
# → exit 75, reason Human-needed

# After review, phases marked **Status:** DONE → clean re-verify.
bin/agent-feature-supervisor --feature-file broad-cross-file-feature-exec.md --skip-gate
# → STATUS_VERIFIED ×5, exit 0
```

For an unbuilt plan you want agents to *implement*:

```sh
bin/agent-feature-supervisor --allow-load-bearing --feature-file 16-steps-exec.md
# parses phases → acceptance all FAIL (unbuilt) → delegates each phase to the
# LLM (gate + rollback) → halts on the first phase whose diff can't pass.
```

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `llm_generate raised: <urlopen error [Errno 111] Connection refused>` | An Ollama-routed model with no reachable server. Set `PYCSL_LLM_MODEL=claude-sonnet-4.6` (→ Copilot) or point `OLLAMA_URL` at a live server. |
| Delegated every phase but each "FAIL: llm refused or output had no diff block" | LLM returned prose, not a fenced ```diff. Tighten the phase body, or check the model/CLI auth. |
| `HALT — MISSING_ACCEPTANCE` | An open phase has no `**Acceptance:**` block — add one, or opt out with `**Acceptance:** none — <reason>`. |
| `HALT — CLAIM_REJECTED` | An acceptance command used a forbidden token (mutation/network/redirect). Make it read-only; move side effects into a `bin/*` script. |
| `Human-needed` even though everything passes | Verify-only mode + load-bearing targets. Either review + mark phases `**Status:** DONE`, or re-run with `--allow-load-bearing` to delegate. |
| Stale `feature-*-phase-*-start` tags | Left by delegation rollbacks; remove with `git tag -d <tag>`. |

## See also

- `config/skills/csl-from-scratch/references/acceptance-syntax.md` — acceptance bullet grammar (source of truth).
- `config/skills/project-lifecycle/references/feature-plan-submission.md` — plan submission workflow + lifecycle mapping.
- `config/skills/agent-stdlib-annotate/references/load-bearing-files.md` — the deny-list.
- `config/agents/agent-feature-supervisor.md` — the supervisor's ER persona.
- `feature-supervisor-extreme-rigor.md` — ER design rationale.
