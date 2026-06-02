# Acceptance block syntax — reference for ER plan authors

> **Load when:** writing a `missing-*-feature.md` plan that the
> Extreme Rigor supervisor will evaluate.

The supervisor is `bin/agent-feature-supervisor`. Its ER mode runs
`**Acceptance:**` blocks inside `### Phase N` headers under
`## Implementation surface`. Each bullet is a command + predicate;
the supervisor executes the command and halts with a halt-report if
the predicate fails.

This document is the single source of truth for the bullet shapes
the parser accepts. The implementation lives in
`src/pycsl/agents/agent-feature-supervisor.py` (`_parse_acceptance`,
`_check_acceptance`, `_validate_acceptance_safety`).

## Bullet shapes

Each bullet starts with `- ` followed by the command in backticks
and a predicate:

```
- `command` exits N
- `command` stdout == `value`
- `command` stdout >= `N`
- `command` stdout matches `regex`
```

A trailing italic-paren comment `*(reason)*` is permitted and
ignored by the parser.

### `exits N`

Most common. Passes if the command's exit code equals `N`. Use
`exits 0` for "the command succeeds." Use `exits 1` for
"the command MUST report a non-zero exit" (e.g., a `grep` that
should find nothing). The supervisor sets `EXIT_HUMAN_NEEDED = 75`
for its own halts — don't confuse those with your acceptance
exits.

### `stdout == \`value\``

Strict equality on the stripped stdout. Useful for "must be empty"
(`stdout == \`\``) or "must be one number" patterns.

### `stdout >= N`

Parses stdout as an integer and asserts it's at least `N`. The
canonical pattern is `command | wc -l` paired with this predicate.

### `stdout matches \`regex\``

Python `re.search` against stdout. Use sparingly — exact-match
predicates are easier to debug. The regex is NOT anchored; use
`^` / `$` if you need full-line match.

## Plan-level keywords

### `**Status:** DONE`

Marks a phase as already completed. Behaviour:

- WITH an `**Acceptance:**` block: claims are re-evaluated each
  supervisor run. If they fail, the supervisor halts with
  `STATUS_FORGED` — the marker was a lie.
- WITHOUT an Acceptance block: `LEGACY_ACCEPTED`. Informational
  only — represents work done before ER, grandfathered. New
  closures should always carry Acceptance.

### `**Acceptance:** none — <reason>`

Explicit opt-out. Use for research/scoping phases whose
deliverables are not machine-checkable (e.g., "evaluate three
candidate approaches and pick one"). The `— <reason>` text is
mandatory; the supervisor logs it.

### Missing block (no `Status: DONE`, no `Acceptance:`)

Triggers `MISSING_ACCEPTANCE` halt. The plan is malformed; the
phase has no definition of done.

## What the supervisor REFUSES to execute

Acceptance claims must be read-only. The safety classifier
(`_validate_acceptance_safety`) halts with `CLAIM_REJECTED` if a
command contains:

- Mutation tokens: `rm`, `mv`, `dd`, `chmod`, `chown`
- Destructive git: `push`, `commit`, `rebase`, `clean`, `--hard`,
  `--force`
- Network egress: `curl`, `wget`, `gh api`, `gh pr`, `gh issue`
- Multi-statement separators: `;`, `&&`, `||`
- Output redirect: `> file`, `>> file`
- Command substitution: `` `cmd` ``, `$(cmd)`
- Process substitution: `<(cmd)`, `>(cmd)`

EXPLICITLY allowed (common safe idioms):

- Pipe `|`
- `2>&1`, `1>&2` (fd duplication)
- `< file` (input redirect — read-only)

If your acceptance idea needs a forbidden pattern, factor the
mutation into a separate explicit step (a `bin/*` script) and
have the acceptance claim invoke that script — keeping the
audit boundary visible.

## Canonical patterns

### "Source file X exists"

```
- `test -f path/to/file` exits 0
```

### "Reference test passes verification"

```
- `.venv/bin/python3 src/pycsl/pycsl.py path/to/test.py` exits 0
```

### "Audit step shows at least N body-verified entries"

```
- `bin/cmmi-audit.sh --quick 2>&1 | grep -c "\[VERIFIED\]"` stdout >= `N`
```

### "Source contains a particular annotation"

```
- `grep -q "proof rocq UnixFs.Struct" unix-filesystem/UnixInodeFileSystem.py` exits 0
```

### "No method in scope still carries `\trusted`"

```
- `grep -cE "(_read_inode|_write_inode).*\\\\trusted" unix-filesystem/UnixInodeFileSystem.py` stdout == `0`
```

### "Coq proofs still compile"

```
- `coqc -q unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v` exits 0
```

### "pytest harness passes"

```
- `.venv/bin/python3 -m pytest test-suite/agent-tests/test_supervisor_er.py -q` exits 0
```

## What ER catches that the gate doesn't

The verification gate (cmmi-audit, doc-coherency, reference-tests)
catches infrastructure regressions: did the test suite still pass?
ER catches *deliverable* regressions: did this phase actually
ship what it claimed? The two are independent. A plan can pass
the gate while shipping nothing of substance; ER closes that
loop.

Concrete example from the Phase 4 retrospective of
`missing-bytes-struct-feature.md`: the implementer (me) declared
Phase 4 complete with all gates green. Zero of the four target
methods had promoted to body-verified. The user had to ask
"what was not done?" to surface the gap. ER's acceptance check
would have caught it on the first run.

## Pointers

- **Implementation:**
  [`src/pycsl/agents/agent-feature-supervisor.py`](../../../src/pycsl/agents/agent-feature-supervisor.py)
- **Original ER design:**
  [`feature-supervisor-extreme-rigor.md`](../../../feature-supervisor-extreme-rigor.md)
- **Stdlib-grade ER discipline:**
  [`stdlib-extreme-rigor.md`](stdlib-extreme-rigor.md)
- **Test fixtures (positive + negative):**
  [`test-suite/agent-tests/er-fixtures/`](../../../test-suite/agent-tests/er-fixtures/)
- **Codified retrospective check:**
  [`bin/er-retrospective-check.sh`](../../../bin/er-retrospective-check.sh)
