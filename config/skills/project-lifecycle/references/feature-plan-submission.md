# Submitting a feature plan to the verification gate

This reference defines how to submit an approved feature/change plan for
autonomous classification and acceptance checking via the
**`agent-feature-supervisor`**. It is the executable counterpart of the
human-readable plan: where a `/plan` document explains *what* and *why*, the
submission form encodes *machine-checkable definitions of done* the supervisor
re-runs on every invocation.

See `SKILL.md` §4 (T7) for where this sits in the lifecycle. The bullet grammar
is normatively defined in
[`config/skills/csl-from-scratch/references/acceptance-syntax.md`](../../csl-from-scratch/references/acceptance-syntax.md);
this doc covers the submission *workflow* and *document shape* and does not
restate that grammar in full.

## Command

```
./bin/agent-feature-supervisor --feature-file my-great-feature.md
./bin/agent-feature-supervisor --feature-file my-great-feature.md --skip-gate
```

- The wrapper delegates to `src/pycsl/agents/agent-feature-supervisor.py`.
- `--skip-gate` parses + classifies + evaluates acceptance only (dry run); it
  skips the `cmmi-audit`/`doc-coherency`/reference-test gate. Use it to validate
  that a plan is well-formed before committing to a full run.
- The supervisor is **gate-only**: it never autonomously edits load-bearing
  files (see "Load-bearing deny-list" below). It classifies, runs read-only
  acceptance claims, and halts with a machine report — a human (or a delegated
  coding session) does the actual edits.

> **Recursion guard.** Running the supervisor can re-enter the ER retrospective
> via the gate (`cmmi-audit`) and CPU-explode. Run it foreground with a timeout
> and `CMMI_AUDIT_NESTED=1` exported, e.g.
> `CMMI_AUDIT_NESTED=1 timeout 200 ./bin/agent-feature-supervisor --feature-file f.md --skip-gate`.

## Document shape (what the parser requires)

The parser (`parse_feature_plan`) extracts phases from the section that begins
with the level-2 heading **`## Implementation surface`** (everything until the
next `##` heading). Put all phases there.

1. **Phase headers** — `### Phase N — Title` (the separator may be `—`, `-`,
   `:`, or a space; `N` is an integer, an optional `.M` sub-number is allowed):

   ```
   ### Phase 0 — Class-level constants in the class IR
   ```

2. **Target files** — auto-detected from any backticked path in the phase body
   that contains a `/` or a file extension (e.g. `` `src/pycsl/Module5_IREmitter.py` ``,
   `` `test-suite/corpus/pycsl-reference/0440.py` ``). No explicit "files:" line
   is needed; just mention each edit/target path in backticks.

3. **Acceptance block** — **every open (non-DONE) phase MUST carry one**, or the
   supervisor halts `MISSING_ACCEPTANCE`. It is a line `**Acceptance:**` followed
   by `- ` bullets, each a command in backticks + one predicate:

   ```
   **Acceptance:**
   - `test -f test-suite/corpus/pycsl-reference/0440.py` exits 0
   - `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0440.py` exits 0
   ```

   Predicate shapes: `exits N` · `stdout == \`value\`` · `stdout >= \`N\`` ·
   `stdout matches \`regex\``. A trailing `*(comment)*` is allowed and ignored.

## Plan-level keywords

- `**Status:** DONE` (line-leading, inside a phase) — marks a completed phase.
  *With* an Acceptance block, its claims are re-evaluated every run (a failure
  halts `STATUS_FORGED` — the marker was a lie). *Without* one, the phase is
  `LEGACY_ACCEPTED` (informational, grandfathered).
- `**Acceptance:** none — <reason>` — explicit opt-out for research/scoping
  phases whose deliverable is not machine-checkable. The reason is mandatory.

## Acceptance claims must be read-only

The safety classifier (`_validate_acceptance_safety`) rejects (`CLAIM_REJECTED`)
any command containing mutation tokens (`rm`, `mv`, `dd`, `chmod`, `chown`),
destructive git (`push`, `commit`, `rebase`, `clean`, `--hard`, `--force`),
network egress (`curl`, `wget`, `gh api`, `gh pr`, `gh issue`), multi-statement
separators (`;`, `&&`, `||`), output redirects (`>`, `>>`), or command/process
substitution (`` `…` ``, `$(…)`, `<(…)`). Pipes `|`, fd duplication `2>&1`, and
input redirect `< file` are allowed. If a check needs a mutation, factor it into
a `bin/*` script and have the claim invoke that script.

## Load-bearing deny-list (gate-only halts)

Phases whose target files match
[`config/skills/agent-stdlib-annotate/references/load-bearing-files.md`](../../agent-stdlib-annotate/references/load-bearing-files.md)
— the parser/IR/emitter pipeline (`Module2`–`Module6`, `module6_whyml/*`,
`csl.lark`, `ir_schema.py`, `exception_model.py`, `formal-semantics/`, the
normative `docs/pycsl-*-reference.md`, etc.) — **always raise the `human-needed`
signal (exit 75)**. This is by design: incorrect edits to these files produce
silent unsoundness, so they are never edited autonomously. A feature that
legitimately changes the compiler core will therefore submit cleanly, have its
acceptance claims run, and then halt `human-needed` — which is the correct
signal that human implementation + review is required, not a defect in the plan.

## Exit codes

| Code | Meaning |
|---|---|
| 0  | All phases passed the gate / finished without action. |
| 74 | Gate failure (pytest, doc-coherency, reference tests, etc.). |
| 75 | Human-needed: load-bearing target, `MISSING_ACCEPTANCE`, `STATUS_FORGED`, `ACCEPTANCE_FAILED`, or `CLAIM_REJECTED`. |
| 76 | Rollback failure (per-phase git-tag restore) — v1 stub. |

A halt writes a report to
`metrics/feature-supervisor/<feature-stem>/halt-report.md` naming the failing
phase, claim, or load-bearing target.

## Worked example

```markdown
# My great feature — executable plan

## Implementation surface

### Phase 0 — Add the corpus fixture
Create `test-suite/corpus/pycsl-reference/0440.py` exercising the new behavior.
**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0440.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0440.py` exits 0

### Phase 1 — Scope the approach
Evaluate three lowering strategies and pick one.
**Acceptance:** none — research/scoping phase; deliverable is the chosen design, not a check.
```

Run `./bin/agent-feature-supervisor --feature-file my-great-feature.md`. Phase 0
fails until the fixture exists and verifies (acceptance *is* the definition of
done); Phase 1 is recorded as an explicit opt-out.

## Giving an agent its skills (context, not RAG)

When the supervisor **delegates** a phase to a coding LLM
(`--allow-llm-delegation` / `--allow-load-bearing`), the agent's context is
assembled as **direct text — there is no RAG retrieval** on this path. Each
delegate prompt is exactly:

1. the supervisor **persona** (`config/agents/agent-feature-supervisor.md`),
2. the **coding scaffold** (`config/skills/agent-stdlib-annotate/references/coding-llm-prompt.md`),
3. the **phase body** (`raw_body`) from the plan, and
4. the **verbatim contents of every target file** the phase lists.

(The RAG machinery — `rag-index`, `rag-top-k`, the nomic embeddings in
`agents-config.json` — feeds the *annotation* pipeline agents driven by
`coordinator.py`, **not** the feature-supervisor delegate.)

**Consequence:** an agent only "knows" a skill, exemplar, or reference doc if its
text is in the prompt. The plan naming a path in prose (`see config/skills/unix/`)
does **not** put that skill in front of the agent. To wire a skill in, **list it
as a target file in the phase** — its contents are then inlined. Mark it
read-only in prose so the delegate doesn't edit it:

```
### Phase N — <module>
… deliverable description …

**Reference (read-only context — do not modify; shows the pattern):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `…`
```

Guidance:

- **Pick skills per phase**, not globally — only the files relevant to that
  phase's deliverable, to keep the prompt focused. (Large exemplars like
  `unix-filesystem/UnixInodeFileSystem.py` belong only on the phases that model
  comparable state.)
- **Read-only references are still "targets"** to the parser, so they count
  toward the phase's target list and are deny-list-classified — but a normal
  skill/exemplar path is not load-bearing, so it adds no deny-list hit.
- **Verify what reached the agents:** the harness-structure log
  (`logs/<ts>-agent-feature-supervisor-harness-structure.md`) has a
  **`## 5. Skills & reference context`** section listing the always-injected
  files plus the skill/reference files the plan wires in — review it before a
  delegated run to confirm each phase carries the skills it needs.

### Role skills are auto-injected from the competency matrix

You do not have to hand-pick the *role-level* skills. Tag each phase with its
execution level:

```
### Phase N — <title>
**Level:** L5
```

The supervisor reads [`competency-matrix.md`](competency-matrix.md) — the
skill-to-role table (`*` = all levels, `L1`–`L5`, and `L<n>-<Role>`) — and
**auto-injects** the union of the `*` row, the phase's level row, and (if a
`**Role:**` tag is present) the `L<n>-<Role>` row into that phase's delegate
prompt (e.g. `*`→`project-lifecycle` for everyone; `L1`/`L2`→`csl-philosophy`;
`L3`–`L5`→the `pycsl-annotate` family). Add a `**Role:**` tag for role-specific
skills — e.g. `**Level:** L5` + `**Role:** Validator` is the *only* combination
that receives the proof skills (`rocq`/`rocq-prover`/`lean`), since only the
low-level Validator writes `#@ proof` citations. The resolution is recorded in
the harness log under **`### 5.1 Resolved per-phase competencies`** for review.

So there are two kinds of context per phase: **role skills** (declared once via
`**Level:**`, resolved from the matrix) and **task references** (the specific
exemplar/reference files you list as read-only targets, above). Use the matrix
for "what every L5 author should know"; use explicit reference targets for "the
exemplar *this* phase should imitate".

## Pointers

- Acceptance bullet grammar (source of truth): `config/skills/csl-from-scratch/references/acceptance-syntax.md`
- Load-bearing deny-list: `config/skills/agent-stdlib-annotate/references/load-bearing-files.md`
- Supervisor implementation: `src/pycsl/agents/agent-feature-supervisor.py`
- ER design rationale: `feature-supervisor-extreme-rigor.md`
