# Better agent — autonomous gap-driven feature loop for the stdlib annotator

## The gap (worked example)

The autonomous stdlib annotator (`bin/agent-stdlib-annotate`) currently
does one thing well: promote a stub from L2 → L4/L5 when the docstring
is expressible in the current contract surface. When the LLM hits a
gap, it correctly falls back to L3 + a `# cite:_note:` line documenting
why. From the run on 2026-05-31 13:47:22 against `itertools.cycle`:

> `cycle` has no documented preconditions (any iterable is valid,
> including empty), and the postcondition — "repeats the sequence
> indefinitely" — is an infinite-iterator semantic that lies outside
> the expressible contract surface. L3 ceiling is correct here per
> Rule 4 / Part 3.

The agent then moved on to the next stub.

That is the right *local* behaviour and the wrong *global* one. What
happened next was manual:

1. The human (you) read the log.
2. The human wrote [`missing-iter-feature.md`](missing-iter-feature.md) by
   hand — anchoring on `cycle`, sizing the gated stub surface (~50–80
   functions, 5–8 % of the total), proposing four design options, and
   recommending Option A (yield-set) as a 2-week first slice.
3. The human now has to drive that document through implementation,
   tests, and doc closure.

**The missing capability is the loop that turns the agent's per-stub
"L3 ceiling" notes into a queued feature proposal, and then supervises
the rollout end-to-end.** That loop is what this document specifies.
It is *not* an attempt to autonomously redesign the Hoare memory
model; it is a meta-agent that detects gap patterns, drafts plans,
runs verification gates, and updates documentation — leaving the
load-bearing design work to a human (or a coding LLM under human
review) at the moments that actually need judgement.

---

## Scope — what the upgraded agent does

Five capabilities, layered on top of the existing
`agent-stdlib-annotate` infrastructure:

| # | Capability | Trigger | Autonomy |
|---|---|---|---|
| 1 | **Gap detection** | `--all` run finishes | Fully autonomous |
| 2 | **Feature-plan proposal** | A gap category passes a configurable threshold (default ≥5 stuck functions) | Autonomous draft; human approves before any code lands |
| 3 | **Implementation supervisor** | Human-approved `missing-*-feature.md` doc dropped into a watch directory | Phase-gated, gate-validated, halts on first failure |
| 4 | **Test generation** | New contract atom lands from a feature | Autonomous; generates positive + negative reference tests |
| 5 | **Doc closure** | Verification gate green | Autonomous edits to the global plan, the §10 annotations table, and the three normative reference docs |

The current agent already does L2 → L4/L5 promotion. This upgrade
keeps that loop intact and adds the meta-loop that closes around it.

---

## Out of scope (deferred)

- Autonomous redesign of the Hoare memory model, the ghost-type
  registry, or any other load-bearing design decision.
- Autonomous editing of `src/pycsl/Module2_Parser.py`,
  `src/pycsl/module6_whyml/expressions.py`,
  `src/pycsl/module6_whyml/preamble.py`, or any other code surface
  that requires WhyML-encoding judgement.
- Autonomously firing the merge of a feature PR. The supervisor
  drives the verification gate; the merge is human.
- Cross-language feature work (Rocq/Lean axiom imports — that's
  `agent-rocq-proof-writer`'s territory).
- Replacing the existing per-module rollback policy in
  `agent-stdlib-annotate.py`; the upgrade extends it, does not
  replace it.

---

## Design

### Capability 1 — Gap detection

The existing agent already emits a `# cite:_note:` line whenever it
falls back to L3 ceiling. Detection is straightforward:

1. **Source signal.** Every L3-ceiling fallback is already a line of
   the form `# cite:_note: <human-readable reason>` in the rewritten
   stub. The reason is LLM-generated free text but follows a
   recognizable pattern (subject phrase + "cannot be expressed" / "is
   not representable" / "lies outside the contract surface").
2. **Classifier.** A small dispatcher inside the agent classifies each
   note into one of a fixed taxonomy:

   | Category | Trigger phrases |
   |---|---|
   | `iterator-semantics` | "iterator", "infinite", "yields", "lazy sequence" |
   | `regex-semantics` | "regex", "regular expression", "pattern match" |
   | `higher-order` | "callback", "function argument", "predicate function" |
   | `string-content` | "string contents", "format string", "encoding" |
   | `io-side-effect` | "file", "socket", "stream", "I/O" |
   | `non-deterministic` | "random", "time", "clock", "uuid" |
   | `unclassified` | none of the above match |

   When the heuristic misses (`unclassified`), the classifier calls
   the LLM with a single-prompt query (`llm_generate` with the
   existing client) to pick the best category — defaulting to
   `unclassified` if the LLM is uncertain.

3. **Aggregation.** Across a full `--all` run, the agent maintains a
   counter per category. The counter is dumped to
   `metrics/stdlib-gap-report.json` at the end of the run.

4. **Reporting.** A new `--detect-gaps` flag prints the table to
   stdout in addition to writing the JSON. With `--detect-gaps`
   alone (no `--all`), the agent re-scans the existing
   `src/pycsl_lib/` tree for already-present `# cite:_note:` lines
   rather than re-running the annotator — useful for understanding
   the current backlog without spending LLM budget.

The detection step writes no files other than the JSON report.
Safety perimeter: read-only with respect to source.

### Capability 2 — Feature-plan proposal

When a gap category passes a threshold (default `≥5` stuck functions,
configurable via `--proposal-threshold N`), the agent generates a
feature plan document.

1. **Template.** The plan template is
   [`missing-iter-feature.md`](missing-iter-feature.md) — its 12
   sections (gap, scope, design options, recommended design,
   concrete atoms, worked example post-feature, derived primitives,
   implementation surface, migration path, effort estimate, risks +
   fallbacks, suggested first PR, references) are the canonical
   shape. The template is stored as
   `config/skills/agent-stdlib-annotate/references/feature-plan-template.md`
   with `{{slot}}` placeholders.
2. **Anchor selection.** The agent picks the most-cited stuck
   function in the category (the one whose
   `# cite:_note:` was generated most often or whose docstring was
   the most explicit) as the anchor example. Falls back to the
   first stuck function alphabetically when no clear winner.
3. **Scope sizing.** The agent walks `src/pycsl_lib/` again with
   the same classifier and counts every stub whose `# cite:_note:`
   matches the category. That count + the percentage of total
   surface (denominator from `bin/stdlib-coverage-report.py`) lands
   in the "Quantitative impact" subsection.
4. **Design options.** The agent does **not** invent design
   options. Instead it queries the LLM with a structured prompt:
   *"Given gap category X and N stuck functions exemplified by Y,
   propose 3–4 design options ranked by cost vs. expressive
   power, mirroring the format of missing-iter-feature.md's
   Options A–D section."* The output is human-edit-ready prose,
   not a final design.
5. **Output path.** Drops the draft at
   `proposed-features/missing-<category>-feature.md` and marks
   it `STATUS: DRAFT — awaiting human approval`. The
   `proposed-features/` directory is new and tracked in git.
6. **Human approval gate.** A draft becomes a real plan only when
   a human moves it to repo root (matching the convention of
   `missing-iter-feature.md`) and changes `STATUS: DRAFT` to
   `STATUS: APPROVED`. The supervisor watches for this
   transition.

The agent does **not** auto-approve, auto-implement, or auto-merge.
The draft is a starting point for the human, not a finished plan.

### Capability 3 — Implementation supervisor

A new agent — `agent-feature-supervisor` — takes an approved
`missing-*-feature.md` doc and orchestrates the rollout. Its
contract:

1. **Read the phase table.** Every feature plan has an
   "Implementation surface" section structured as Phase 1 / Phase 2 /
   ... / Phase N. Each phase has a file table and an effort estimate.
   The supervisor parses the phase table to get a deterministic
   work-list.
2. **Per-phase orchestration.** For each phase:
   - The supervisor **does not write the code**. It opens a structured
     prompt to a coding LLM (Claude Code via the existing
     `llm_generate` wrapper) or signals "human-needed" for phases
     marked load-bearing (grammar surgery, WhyML emission,
     `module6_whyml/preamble.py` changes — see Safety perimeter
     below).
   - After the phase claims completion, the supervisor runs the
     verification gate (see below) and halts on first failure.
3. **Verification gate.** A fixed pipeline run after every phase:
   ```
   1. pytest -q tests/                       # unit tests green
   2. bin/run-reference-tests.sh             # corpus passes
   3. bin/doc-coherency.py --check           # docs in lockstep
   4. bin/stdlib-coverage-report.py --diff   # coverage moves the right way
   5. bin/agent-stdlib-annotate --dry-run --module <gap-category-anchor>
                                              # the previously-stuck
                                              # function now reaches L4
   ```
   Each step is run as a subprocess; non-zero exit halts the
   supervisor. The supervisor logs every gate run to
   `metrics/feature-supervisor/<feature-slug>/<phase-N>.log`.
4. **Rollback policy.** Mirrors the per-module rollback in
   `agent-stdlib-annotate.py:_apply_or_rollback`: any phase whose
   gate fails reverts the working-tree changes attributable to that
   phase via `git restore` against a per-phase tag (`feature-<slug>-phase-<N>-start`).
   The supervisor never force-pushes and never rewrites history.
5. **Halt and report.** On halt (gate failure, loop detection,
   human-needed signal), the supervisor writes a human-readable
   report to
   `metrics/feature-supervisor/<feature-slug>/halt-report.md` and
   exits with a non-zero code. The convention mirrors
   `coordinator.py`'s `EXIT_MAX_RETRIES=72` /
   `EXIT_LOOP_DETECTED=73` codes; the supervisor uses 74 (phase gate
   failure), 75 (human-needed signal raised), 76 (rollback failure).
6. **Loop detection.** If the same phase fails the same gate 3 times
   in a row with the same error pattern, the supervisor halts
   regardless of retry budget. Same pattern as `coordinator.py`
   exit 73.

### Capability 4 — Test generation

For each new contract atom that lands from a feature (detected by
diffing `src/pycsl/Module2_Parser.py` or
`src/pycsl/module6_whyml/expressions.py:_EXPR_DISPATCH` keys
before/after the feature), the supervisor generates a positive +
negative reference-test pair:

1. **Numbering convention.** Follows
   [`docs/stdlib-global-plan.md`](docs/stdlib-global-plan.md): 0500+
   for positive reference tests, 1500+ for negative tests. Per-module
   sub-blocks reserve 12-test ranges (e.g.
   `itertools` reserves 0540–0551 positive, 1540–1551 negative).
2. **Generation.** Each test file is generated by the LLM with the
   feature plan's worked example as the prompt context.
   Positive tests assert the stub's `ensures` clause; negative tests
   violate the `requires` clause and confirm `pycsl --proof` reports
   FAIL.
3. **Validation.** Every generated test is run through
   `pycsl --no-proof` (syntax + Module4) first, then through
   `pycsl --proof` to confirm PASS/FAIL behaviour matches the
   `# pycsl-expected:` marker in the test docstring.
4. **Numbering reservation.** The supervisor reads
   `test-suite/traceability-pycsl.md` to find the next free number
   in the appropriate block. The doc is updated in the same pass.

### Capability 5 — Doc closure

Once the verification gate is green and tests pass, the supervisor
performs the documentation closure:

1. **Bridge sentence in the global plan.** Appends a new bridge to
   `docs/stdlib-global-plan.md` Part 3 of the form: *"Now that
   `<category>` atoms exist (`\<atom1>`, `\<atom2>`, ...),
   functions previously stuck at L3 ceiling for this reason can
   reach L4 by using the new atoms in their `ensures` clause."*
   The bridge sentence is generated by the LLM with the worked
   example as context.
2. **Annotations table append.** Adds a row per new atom to
   `test-suite/annotations.md` §10, never renumbering existing
   rows.
3. **Version bumps in the three normative docs.** Bumps the
   `Version: N.M` line in:
   - `docs/pycsl-concrete-syntax-reference.md`
   - `docs/pycsl-static-semantics-reference.md`
   - `docs/pycsl-translational-reference.md`

   And appends the new atom's grammar production /
   well-formedness rule / translation rule to the appropriate
   section of each. The convention is captured in the
   [`pycsl-doc-coherency`](config/skills/pycsl-doc-coherency/SKILL.md)
   skill — the supervisor runs `bin/doc-coherency.py --check` as
   the final gate.
4. **Feature plan finalization.** Marks the original
   `missing-<category>-feature.md` with `STATUS: SHIPPED` and
   appends a coverage-delta line: *"Final coverage: itertools
   went from L2 12/12 to L4 12/12 (+1.1 percentage points
   overall L4+)."*

---

## Safety perimeter

Explicit list of what runs without human intervention and what halts
for review:

| Action | Autonomy |
|---|---|
| Read-only scan of `src/pycsl_lib/` for existing `# cite:_note:` lines | Autonomous |
| Run `bin/stdlib-coverage-report.py` | Autonomous |
| Classify gap notes into categories (heuristic + LLM fallback) | Autonomous |
| Aggregate counts and write `metrics/stdlib-gap-report.json` | Autonomous |
| Generate a draft `missing-<category>-feature.md` into `proposed-features/` with `STATUS: DRAFT` | Autonomous |
| Move a draft to repo root and flip `STATUS: APPROVED` | **Human only** |
| Edit `src/pycsl/Module2_Parser.py` (grammar productions) | **Human-needed signal raised**; supervisor delegates to coding LLM under human review |
| Edit `src/pycsl/module6_whyml/expressions.py` (`_EXPR_DISPATCH`) | **Human-needed signal raised** |
| Edit `src/pycsl/module6_whyml/preamble.py` (Why3 library declarations) | **Human-needed signal raised** |
| Generate reference tests in `test-suite/corpus/python-reference/stdlib/<module>/` | Autonomous (with `pycsl --proof` validation) |
| Edit `src/pycsl_lib/<module>.py` to promote stubs L2 → L4 | Autonomous — same boundary as today's `agent-stdlib-annotate` |
| Append rows to `test-suite/annotations.md` §10 | Autonomous |
| Bump `Version:` in the three normative docs | Autonomous |
| Run `bin/doc-coherency.py --check` as final gate | Autonomous |
| `git commit` after a green gate | **Human only** (supervisor stages files only) |
| `git push`, `gh pr create`, force-push, history rewrite | **Never** |

The supervisor stages files via `git add -p`-style targeted adds (no
`git add -A`). It writes a structured commit-message *draft* to
`metrics/feature-supervisor/<feature-slug>/commit-message.txt` and
halts; a human reviews the diff, edits the message, and runs
`git commit` manually.

---

## Two-agent split

Capability 1 (detection) and capability 2 (proposal) live as
extensions to the existing `agent-stdlib-annotate.py`. They share its
LLM client, its `_parse_llm_block` parser, and its
per-module rollback policy.

Capabilities 3–5 (supervision, test generation, doc closure) live in
a **new** `agent-feature-supervisor.py`. Reasons for the split:

1. **Different blast radius.** Detection is read-mostly (writes only
   the gap-report JSON and the draft plan). Supervision runs build /
   test pipelines, writes test files, edits version-stamped docs.
   A failure in supervision can leave the working tree in a partial
   state; detection cannot.
2. **Different invocation cadence.** Detection runs every time the
   annotator runs (cheap). Supervision runs only when a human
   approves a plan (rare, expensive).
3. **Different LLM patterns.** Detection uses one short prompt per
   stuck function (classification). Supervision uses long
   structured prompts per phase (code generation), and is the
   natural fit for the existing `coordinator.py` retry-loop
   pattern.
4. **Testability.** Detection is a pure function over an existing
   library tree — easy to unit-test. Supervision orchestrates
   subprocess runs and needs integration tests against a sandboxed
   working tree.

Both agents register in `config/agents-config.json` with their own
skill-retrieval queries.

---

## End-to-end loop

```
┌──────────────────────────────────────────────────────────────────┐
│  STEADY STATE: agent-stdlib-annotate --all                       │
│  ─────────────────────────────────────────                       │
│  For each stub in src/pycsl_lib/:                                │
│    • Currently at L2 → attempt L4/L5 promotion                   │
│    • If LLM hits a gap → emit # cite:_note:, stay at L3, move on │
│  Writes metrics/stdlib-gap-report.json                           │
│  Capability 1 — fully autonomous, read-only on the library      │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  GAP AGGREGATION                                                 │
│  ────────────────                                                │
│  Classify every # cite:_note: into a category                    │
│  Count per category                                              │
│  For each category with count ≥ --proposal-threshold (default 5):│
│    Emit proposed-features/missing-<category>-feature.md          │
│      STATUS: DRAFT                                               │
│  Capability 2 — autonomous draft, human approves                │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼  (human reads draft, edits if needed)
┌──────────────────────────────────────────────────────────────────┐
│  HUMAN APPROVAL                                                  │
│  ──────────────                                                  │
│  Human moves proposed-features/missing-X-feature.md → repo root  │
│  Human flips STATUS: DRAFT → STATUS: APPROVED                    │
│  This is the only gate that requires a human decision           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  SUPERVISED ROLLOUT (agent-feature-supervisor)                   │
│  ─────────────────────────────────────────────                   │
│  Parse Implementation Surface section into phases                │
│  For each phase:                                                 │
│    Mark phase start (git tag feature-X-phase-N-start)            │
│    For load-bearing files: raise human-needed signal, halt       │
│    Otherwise: delegate to coding LLM with phase-scoped prompt    │
│    Run verification gate (tests, corpus, doc-coherency, coverage)│
│    On gate failure: rollback phase, log, halt                    │
│  Capability 3 — phase-gated, gate-validated, no-merge          │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼  (per atom landed)
┌──────────────────────────────────────────────────────────────────┐
│  TEST GENERATION                                                 │
│  ────────────────                                                │
│  For each new contract atom (diff of Parser/EXPR_DISPATCH):      │
│    Reserve next free numbers in test-suite/traceability-pycsl.md │
│    Generate POS test (0500+) and NEG test (1500+)                │
│    Validate with pycsl --proof                                   │
│  Capability 4 — autonomous, validated against the prover       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼  (after the final phase gate goes green)
┌──────────────────────────────────────────────────────────────────┐
│  DOC CLOSURE                                                     │
│  ────────────                                                    │
│  Append bridge sentence to docs/stdlib-global-plan.md Part 3     │
│  Append row to test-suite/annotations.md §10                     │
│  Bump Version: in the three normative reference docs             │
│  Run bin/doc-coherency.py --check (final gate)                   │
│  Flip missing-<category>-feature.md to STATUS: SHIPPED           │
│  Append coverage-delta line                                      │
│  Stage all touched files, write commit-message draft, halt       │
│  Capability 5 — autonomous through the gate, human commits     │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  RE-RUN (closes the loop)                                        │
│  ────────────────────────                                        │
│  Next agent-stdlib-annotate --all run:                           │
│    Functions previously stuck at L3 in <category> now reach L4   │
│    Gap counter for <category> drops below threshold              │
│    No new draft emitted for this category                        │
│  Coverage report shows the ratchet click                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## Implementation surface

Phased delivery. Each phase is independently shippable and produces a
measurable improvement on its own.

### Phase 1 — Gap detection (~2 days)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-stdlib-annotate.py` | Add `--detect-gaps` flag. Extend `_parse_llm_block` to also extract `# cite:_note:` lines. Add `_classify_gap(note)` heuristic-then-LLM classifier. Aggregate per category. |
| `src/pycsl/agents/agent-stdlib-annotate.py` | At end of `--all` run, write `metrics/stdlib-gap-report.json`: `{category: count, examples: [func, ...], total: N}`. |
| `bin/agent-stdlib-annotate` | Document the new flag in the wrapper script's help. |
| `metrics/.gitignore` | Confirm `stdlib-gap-report.json` is tracked (the report is a real artefact, not transient). |

Ship as a standalone improvement: no new agent, no orchestration. Gap
visibility is a win on its own.

### Phase 2 — Feature-plan proposal (~3 days)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-stdlib-annotate.py` | Add `--propose-feature [category]` flag. When category counts pass threshold, generate draft. |
| `config/skills/agent-stdlib-annotate/references/feature-plan-template.md` (NEW) | The 12-section template extracted from `missing-iter-feature.md` with `{{slot}}` placeholders. |
| `proposed-features/.gitkeep` (NEW) | Reserve the directory. Generated drafts land here pending human approval. |
| `proposed-features/README.md` (NEW) | Documents the approval workflow (move file to repo root + flip STATUS). |

Tested by re-running against the current `itertools.cycle` log; the
expected output is a draft `missing-iter-feature.md` that reads
similar to the human-authored one. Soft validation only — the
human-authored doc remains canonical.

### Phase 3 — Supervisor scaffold (~5 days)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` (NEW) | Main supervisor agent. Parses Implementation Surface section; loops over phases; runs verification gate; logs to `metrics/feature-supervisor/`. |
| `config/agents/agent-feature-supervisor.md` (NEW) | Persona spec (responsibilities, scope, safety perimeter). |
| `config/agents-config.json` | Add `skill-feature-supervisor` key pointing at retrieval queries for `pycsl-how-to-develop`, `pycsl-doc-coherency`, `pycsl-stdlib-coverage`. |
| `bin/agent-feature-supervisor` (NEW) | Thin wrapper, mirrors `bin/agent-stdlib-annotate`. |
| `src/pycsl/agents/agent-feature-supervisor.py` | Reuse `coordinator.py`'s retry-loop pattern: exit codes 74/75/76 (extending the 72/73 convention). |

Initial scope: the supervisor only orchestrates the *verification
gate* and the *load-bearing-file detection*. It does not yet
delegate code generation to a coding LLM — that's Phase 3b. The
first version simply halts with "human-needed" on every phase. This
lets a human drive the rollout manually while the supervisor handles
the gate runs and the rollback bookkeeping.

### Phase 3b — Coding-LLM delegation (~3 days, optional)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` | For phases not marked load-bearing, generate a phase-scoped prompt and dispatch to `llm_generate`. Capture the output, apply via `git apply`, run the gate. |
| `config/skills/agent-stdlib-annotate/references/load-bearing-files.md` (NEW) | Explicit deny-list: `Module2_Parser.py`, `module6_whyml/expressions.py`, `module6_whyml/preamble.py`, `module6_whyml/types.py`. Phases touching these files always raise the human-needed signal. |

### Phase 4 — Test generation (~3 days)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` | Add `_generate_tests(new_atoms, anchor_module)` step. |
| `test-suite/traceability-pycsl.md` | Convention: reserve 12-test blocks per stdlib module (0540–0551 itertools positive, 1540–1551 negative). The supervisor reads and updates the table. |
| `test-suite/corpus/python-reference/stdlib/<module>/` | Where generated tests land. |

### Phase 5 — Doc closure (~2 days)

| File | Change |
|---|---|
| `src/pycsl/agents/agent-feature-supervisor.py` | Add `_close_docs(feature_slug, new_atoms, coverage_delta)` step. |
| Surgical-edit helpers | Use the same pattern as `agent-stdlib-annotate.py`'s line-anchored insertion: locate the §10 table header, append at the next line; locate `Version: N.M` and bump M; locate the Part 3 bridge anchor and append after it. |

---

## Critical files

### Deliverable
- `better-agent.md` (this document) — the upgrade design.

### Surface this plan describes (NOT modified by this plan)
- `src/pycsl/agents/agent-stdlib-annotate.py` — gets the
  `--detect-gaps` and `--propose-feature` flags.
- `src/pycsl/agents/agent-feature-supervisor.py` (NEW) — the
  supervisor agent.
- `config/agents/agent-feature-supervisor.md` (NEW) — persona spec.
- `config/agents-config.json` — adds `skill-feature-supervisor`.
- `bin/agent-feature-supervisor` (NEW) — thin wrapper.
- `proposed-features/` (NEW) — staging area for auto-generated plans
  awaiting human approval.
- `config/skills/agent-stdlib-annotate/references/feature-plan-template.md`
  (NEW) — extracted from `missing-iter-feature.md`.
- `config/skills/agent-stdlib-annotate/references/load-bearing-files.md`
  (NEW) — explicit deny-list for autonomous edits.

### Reused (no rewrite)
- `src/pycsl/agents/llm_client.py:llm_generate` — shared LLM
  dispatch.
- `src/pycsl/agents/coordinator.py` — the retry-loop /
  loop-detection / exit-code-convention pattern.
- `src/pycsl/agents/agent-stdlib-annotate.py:_parse_llm_block` —
  per-function LLM output parser; extended to also surface
  `# cite:_note:` lines.
- `bin/stdlib-coverage-report.py` — coverage delta computation
  before/after each feature.
- `bin/doc-coherency.py --check` — final gate before commit-message
  draft.
- `bin/run-reference-tests.sh` — corpus verification gate.

---

## Suggested first PR

To prove the loop flies before committing the full 13-day spend:

- **Phase 1 only**: gap detection + summary report.
- No proposal generation, no supervisor, no test generation.
- Concrete deliverable: `bin/agent-stdlib-annotate --detect-gaps`
  produces `metrics/stdlib-gap-report.json` and prints the
  category-count table to stdout.
- Re-running the same command after no library changes is
  idempotent.

Two-day deliverable. Validates the classifier on real data
(`itertools.cycle`, `re.finditer`, the existing
`# cite:_note:` corpus) before committing to anything orchestrational.

If the classifier categorizes the existing notes faithfully and the
report reads usefully, commit to Phase 2 (proposal). If the proposal
draft reads close to the human-authored
`missing-iter-feature.md`, commit to Phases 3–5.

---

## Effort estimate

| Phase | Effort | Cumulative |
|---|---|---|
| 1 — Gap detection | 2 d | 2 d |
| 2 — Feature-plan proposal | 3 d | 5 d |
| 3 — Supervisor scaffold (gate-only, no LLM delegation) | 5 d | 10 d |
| 3b — Coding-LLM delegation (optional) | 3 d | 13 d |
| 4 — Test generation | 3 d | 16 d |
| 5 — Doc closure | 2 d | 18 d |

Phases 1–3 alone (10 days) close 80 % of the loop: the human still
drives the *code* of every feature, but no longer drives the
*detection*, the *plan-drafting*, the *gate-running*, or the *doc
closure*. That's the bulk of the manual overhead today.

Phases 3b + 4 + 5 (8 days additional) make the loop fully
autonomous within its safety perimeter.

---

## Risks + fallbacks

- **Classifier false positives.** A `# cite:_note:` referencing
  iterators might be miscategorized as `string-content` if the LLM's
  reasoning sentence happens to mention strings. **Mitigation**:
  classifier always reports its top-2 candidate categories +
  confidence in the JSON report; a `--review-classifications` flag
  lets the human accept/reject each before aggregation drives the
  proposal threshold.
- **Proposal threshold drift.** Default `≥5` may be too eager
  (false-positive proposals waste reading time) or too lax (real
  patterns never cross). **Mitigation**: threshold is configurable;
  initial value tuned on the current snapshot (which has ≥10
  iterator notes — comfortably above 5).
- **Supervisor halts on every phase.** Phase 3 ships gate-only with
  no LLM delegation; in practice every phase raises "human-needed".
  That's *intentional* — the supervisor is doing the gate runs and
  the rollback bookkeeping that the human currently does by hand,
  even when the human writes the code. **Fallback**: if Phase 3b
  proves brittle, freeze on Phase 3 indefinitely — the gate-runner
  alone has real value.
- **Generated tests pass by accident.** A positive test that
  asserts `True` and a negative test that violates a missing
  precondition would both pass trivially. **Mitigation**: the test
  generator's prompt requires every test to explicitly assert the
  contract's `ensures` clause and to import the function it tests;
  the supervisor rejects generated tests that don't reference the
  target atom by name.
- **Doc-closure bumps the wrong section.** Surgical edits to
  long Markdown files are brittle. **Mitigation**: every closure
  step is followed by `bin/doc-coherency.py --check`; on failure,
  the supervisor reverts the edits and halts. Initial closure logic
  is anchor-comment-based (`<!-- AUTOGEN:itertools-bridge -->` for
  insertion points); the anchors are added to the docs once in
  Phase 5 setup.
- **Load-bearing deny-list drift.** A file becomes load-bearing
  after the deny-list was written, supervisor edits it
  autonomously, breaks the world. **Mitigation**: deny-list is a
  separate skill reference file under CCB; changes to it require
  review same as any other contract surface.
- **Two-agent coordination overhead.** The supervisor and the
  annotator both run `llm_generate` against the same Ollama / API
  endpoint. **Mitigation**: existing single-endpoint queue in
  `llm_client.py` already serializes; no new mechanism needed.

---

## References

- [`missing-iter-feature.md`](missing-iter-feature.md) — the
  human-authored plan that triggered this work, and the structural
  template for every auto-generated proposal.
- [`docs/stdlib-global-plan.md`](docs/stdlib-global-plan.md) Part 3 —
  the "L3 ceiling" convention that the detection step keys on; the
  closure step appends bridges here.
- [`docs/stdlib-annotation-conventions.md`](docs/stdlib-annotation-conventions.md) §Translation Rules — Rule 4 (side
  effects) defines the L3 ceiling that the agent currently respects.
- [`src/pycsl/agents/agent-stdlib-annotate.py`](src/pycsl/agents/agent-stdlib-annotate.py) — the existing
  annotator; gets the detection + proposal extensions.
- [`src/pycsl/agents/coordinator.py`](src/pycsl/agents/coordinator.py) — the precedent for the supervisor's
  retry-loop, loop-detection, and exit-code convention.
- [`config/skills/pycsl-stdlib-coverage/SKILL.md`](config/skills/pycsl-stdlib-coverage/SKILL.md) — the three-artefact
  discipline (`calls-english.md`, `calls-pycsl.md`, `src/pycsl_lib/`)
  that the supervisor must respect when promoting stubs.
- [`config/skills/pycsl-doc-coherency/SKILL.md`](config/skills/pycsl-doc-coherency/SKILL.md) — the doc-coherency
  invariant that the closure step preserves via
  `bin/doc-coherency.py --check`.
- The agent log capture from 2026-05-31 13:47:22 that motivated
  this doc — `itertools.cycle` correctly stopped at L3 per the
  conventions; this upgrade is the loop that turns that observation
  into the next feature, automatically.
