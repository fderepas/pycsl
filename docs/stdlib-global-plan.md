# Python stdlib annotation — global plan (strategy + operational playbook)

Single source of truth for the multi-quarter effort to bring
`src/pycsl_lib/` up from "typed + trusted-marked" to "full
contract + reference tests" against the official Python docs.

**Who reads this doc**: both humans (planning + ratchet
tracking) AND the `bin/agent-stdlib-annotate` agent (system
prompt). The agent uses Part 2 for per-function translation;
Part 1 and Part 3 inform priority order and the L3-ceiling
rule for filesystem/syscall modules.

---

# Part 1 — Strategy framing

## Squeeze position

The PyCSL family operates under the Squeeze Strategy
(`config/skills/csl-from-scratch/SKILL.md` §0.5). This plan
adds a new squeeze layer, **S8′ (stdlib-coverage)**, under the
existing S8 (real-world tests). Mechanical gate: the
**coverage-report tool** at `bin/stdlib-coverage-report.py`
classifies every stub function as
{L1 typed | L2 trusted | L3 partial | L4 full | L5 tested}
and fails CI on regression (`make stdlib-coverage` wired into
`make self-annotate-verify`).

Without this gate, the work is invisible. PR #N adds 30
contracts; PR #N+5 silently removes 10 by refactoring;
coverage drifts. The gate makes the work countable.

## Current state (baseline taken 2026-05-31)

- Stub dir: `src/pycsl_lib/` (35 `.py` files, 23 stdlib modules).
- ~1066 functions across 25 modules.
- Baseline depth: 0 L1, ~698 L2, ~291 L3, ~73 L4, ~4 L5.
- Overall L4+%: **~6.8%** (will rise as the agent works).
- 4 functions at L5: `math.{ceil, floor, sqrt, gcd}` (the
  Phase-1 spike).

## Multi-quarter trajectory

### Phase 0 — Coverage gate (foundation, ~1 week — DONE)

Already landed:
- `bin/stdlib-coverage-report.py` (scanner + `--gen-doc`).
- `docs/stdlib-coverage.md` (auto-regenerated).
- `make stdlib-coverage` target.
- Wired into `make self-annotate-verify`.

### Phase 1 — Convention + worked example (~1 week — DONE)

Already landed:
- This doc (synthesized from the original conventions doc).
- 4 worked examples on `math.py`: sqrt, gcd, floor, ceil.
- 8 reference tests under
  `test-suite/corpus/python-reference/stdlib/math/`.

### Phase 2 — Core modules (~6-8 weeks — IN PROGRESS)

Module priority is the skill's order, refined by where
contracts are most expressible:

| # | Module | Effort | Why this slot |
|---|---|---|---|
| 1 | `math` | 1 wk | Done in Phase 1 (template). Continue with remaining ~58 functions. |
| 2 | `os.path` | 1 wk | Path-arithmetic contracts; sub-package, ~40 fns |
| 3 | `json` | 0.5 wk | Tiny surface (~6 public fns) |
| 4 | `re` | 1 wk | Pattern-match semantics need a model; some functions stay at L3 |
| 5 | `collections` | 1.5 wk | `OrderedDict`, `defaultdict`, `Counter`, `deque` — invariants on class shape |
| 6 | `itertools` | 1 wk | Pure generators; clean ensures |
| 7 | `typing` | 1 wk | Type-level functions; many at `\trusted reviewer:` no-spec |
| 8 | `pathlib` | 1 wk | Wrapping `os.path` (so #2 unblocks this) |
| 9 | `string` ops | 0.5 wk | Already partially tested via `str_methods` |
| 10 | `argparse` | 0.5 wk | Already has class invariants; finish them |

End of Phase 2 target: top 10 modules at L4/L5. Coverage tool
reports ~60% L4+ across the stubbed set.

### Phase 3 — Remaining stdlib modules (~4-6 weeks)

Tier-2 modules: `os` (1278L, huge), `sys`, `subprocess`,
`shutil`, `hashlib`, `datetime`, `dataclasses`, `functools`,
`locale`, `multiprocessing`, `threading`, `textwrap`, `csv`,
`ast`, `importlib`.

`os` is the biggest cost. Many functions deal with the
filesystem (side effects), so contracts are weaker — `ensures
True` + `assigns <fs>` is the most we can say. Accept that
~30% of `os` stays at L3, not L4.

Threading / multiprocessing are out-of-scope for the Hoare
memory model; mark them `\trusted reviewer: out-of-scope-mm`
and skip in the coverage gate.

### Phase 4 — Third-party stretch (separate planning)

The skill's §11.3 ("third-party library stubs") is the next
mountain. Defer to its own plan; not in this strategy. Stretch
target: requests, numpy (already 617L typed), pydantic. Each
takes its own quarter.

## Mechanical gates summary

| Gate | What it catches | Where |
|---|---|---|
| `make stdlib-coverage` | Annotation-depth regression (any module's L4+ % drops) | New target |
| `make self-annotate-verify` | Stub-import drift via MANIFEST sha256 | Already exists |
| `bin/run-reference-tests.sh` | Stub contracts must be satisfiable by callers | Already exists; new tests added |
| Negative tests | Contract violations correctly rejected | Each annotated function adds one PASS + one FAIL test (numbered 0500+ / 1500+ for negative) |

## Risks + fallbacks

- **Stdlib doc ambiguity**: many `os` / `subprocess` functions
  have side effects whose contracts can't be fully expressed
  in the Hoare model. Fallback: accept L3 (partial) as the
  ceiling for that module; track the L3 count in the coverage
  doc so it's visible.
- **Contract correctness on trusted stubs**: a wrong `ensures`
  is a soundness bug. Mitigation: every L4 contract gets at
  least one PASS test AND one NEG test (a caller that violates
  the contract should fail to verify). Negative tests
  numbered 1500+.
- **Effort underestimate**: math+os.path+json+re alone is
  ~3.5 weeks; the full Phase 2 (top 10) is ~8 weeks; full
  stdlib is ~6 months. If schedule slips, prioritize: math,
  os.path, json, collections, itertools — these unblock the
  most real-world Python.
- **CPython version drift**: target a pinned CPython (3.16-alpha
  per `MANIFEST.toml` line 8). Don't try to track upstream
  master. Re-pin once per CPython minor release.

## Out of scope (deferred)

- Annotated `cpython/Lib/` (we don't verify CPython itself;
  only the stub surface that PyCSL programs see).
- Third-party libraries (numpy, requests, pydantic) — see
  skill §11.3, its own planning effort.
- Verifying threading/multiprocessing in the concurrent memory
  model — separate work item (concurrent mm is not yet
  production-ready; see audit-plan.md).
- C-extension boundary (`ctypes`, `cffi`) — stay denied.

---

# Part 2 — Per-function operational playbook

The stdlib stubs are **Tier 2 trust** (per `csl-from-scratch`
skill §11.1): PyCSL does not verify CPython's implementation. We
verify *programs that call stdlib* against the stub's
contract. A wrong contract on a trusted stub is therefore a
**soundness bug** — it can cause unsound conclusions about
correct-looking user code. Prefer being conservative.

## Annotation levels (mechanical definitions)

The coverage scanner (`bin/stdlib-coverage-report.py`) reads
each function's `#@` directive block and classifies it:

| Level | Definition |
|-------|------------|
| **L1 typed** | function present, no `#@ \trusted` directly above |
| **L2 trusted** | `#@ \trusted` only — or with placeholder `ensures \result >= 0` / `requires True` |
| **L3 partial** | `#@ \trusted` + at least one semantic `requires` OR `ensures` |
| **L4 full** | `#@ \trusted` + at least one semantic `ensures` AND one of: (a) at least one semantic `requires`, or (b) a `# cite:` marker (deliberate review against the docs — functions that accept any input still qualify) |
| **L5 tested** | L4 + a reference test under `test-suite/corpus/python-reference/stdlib/<module>/` whose filename contains the function name |

"Semantic" means *not* `requires True`, *not* `ensures \result
>= 0` on an `int`-returning mock, *not* `ensures \result == 0`
on a side-effect function. Those are type-shape mocks, not
contracts. Anything else (a constraint on inputs, a
relationship between inputs and outputs, a raises-clause) is
semantic.

## The pattern (canonical example)

```python
#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/math.html#math.sqrt
#@ requires x >= 0
#@ ensures \result >= 0
#@ ensures \result * \result <= x
#@ ensures (\result + 1) * (\result + 1) > x
def sqrt(x: int) -> int:
    """Mock: return the square root of x.

    Real Python's math.sqrt raises ValueError when x < 0. This
    stub models the non-negative branch only; callers that pass
    a negative x fail to verify (which is the desired behavior).
    """
    return 0
```

Six required ingredients:

1. **`#@ \trusted reviewer: python-stdlib`** — the named reviewer
   tag (not bare `#@ \trusted`). Supports per-reviewer audit
   grouping; matches the skill's Tier-2 prescription.
2. **`# cite: <URL>`** — the Python doc page the contract is
   derived from. One line, immediately after the `\trusted`
   marker. Note: this is a regular Python comment (`#`), not a
   `#@` directive — the PyCSL parser's grammar restricts the
   directive set, and the cite line is read by the coverage
   scanner directly (it's part of the contract block but not
   part of the PyCSL contract language). Future maintainers
   can re-derive the contract by following the link; reviewers
   can spot-check the translation.
3. **`#@ requires <bool>`** — preconditions translated from the
   doc's "Raises" / "Parameters must satisfy" prose. When the
   doc only says "Returns X if condition, raises Y otherwise",
   the `requires` captures the "if condition" half; the raises
   branch is out of scope (we model the success path only,
   per §11.1 of the skill).
4. **`#@ ensures <bool>`** — postconditions translated from
   the doc's "Return" prose. Multiple `ensures` lines allowed
   and encouraged when one clause covers shape (`\result >=
   0`) and another covers semantics (`\result * \result ==
   x`).
5. **Type-correct mock body** — return a sentinel of the
   appropriate type (e.g. `return 0` for `int`, `return ""`
   for `str`). The mock body is never executed during
   verification; only the contract matters.
6. **Docstring with one-line summary + caveat** — `"Mock:
   <doc summary>."` followed by any rationale about what
   branch of the spec the stub models.

## Translation rules

### Rule 1 — When the doc says "Raises X if Y"

The `Y` becomes a `requires` clause (PyCSL models the
non-raising path). Example: `math.sqrt(x)` doc says "Raises
ValueError if x is negative" → `#@ requires x >= 0`.

PyCSL does not currently model exceptions in stub contracts.
A future extension (Phase 4 of the skill) would add
`#@ raises ValueError when x < 0`; for now, encode as
`requires`.

### Rule 2 — When the doc says "Returns X such that Y"

The `Y` becomes an `ensures` clause. Example: `math.gcd(a,
b)` doc says "Returns the greatest common divisor" →
`#@ ensures \result >= 0` and `#@ ensures \result <= a` and
`#@ ensures \result <= b` (when `a > 0` and `b > 0`).

If the relation is too rich to express in WhyML (e.g.,
"returns a sorted version of the list"), express the **shape
invariants** that ARE expressible (e.g., `\result.length ==
input.length`) and add a comment `# cite:_note: doc semantics
exceed expressible contract surface` near the docstring.

### Rule 3 — When the doc is ambiguous

Prefer weaker postconditions. A wrong `ensures` lets the
verifier accept user code that's actually wrong (soundness
bug). A weaker `ensures` rejects more user code but never
accepts bad code (incompleteness, not unsoundness).

### Rule 4 — Side effects

For functions with filesystem / network / random side
effects (most of `os`, `subprocess`, `shutil`), the
postcondition cap is "the function returns; the side effect
happens." That's expressible as:

```python
#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/os.html#os.remove
#@ ensures True
#@ assigns \nothing   // or `assigns <fs>` if a ghost fs variable exists
```

These are **L3 ceiling** modules — accept that. The
coverage doc tracks L3 separately so the ceiling is
visible. Don't fake L4 by adding a vacuous `requires`.

### Rule 5 — Class methods

A `class C` stub with methods carries a class invariant:

```python
class ArgumentParserObj:
    #@ class invariant self._arg_count >= 0

    #@ \trusted reviewer: python-stdlib
    # cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument
    #@ requires name != ""
    #@ ensures self._arg_count == \old(self._arg_count) + 1
    def add_argument(self, name: str) -> int:
        ...
```

The invariant is part of the trust contract and counts toward L4.

## Reference test discipline

A function reaches L5 only when a test exists at
`test-suite/corpus/python-reference/stdlib/<module>/`. The
filename must contain the function name as a substring. Two
tests per L5 function:

- **Positive test** — caller provides valid inputs, expects the
  function's `ensures` clauses to hold downstream. Numbered in
  the `0500–0999` range.
- **Negative test** — caller violates the function's `requires`
  clauses, expects verification to fail. Numbered in the
  `1500+` range.

The positive test is the *capability* claim ("PyCSL can
verify code that uses this stdlib function"). The negative
test is the *soundness* claim ("PyCSL correctly rejects code
that misuses this stdlib function").

### Positive-test template (`math/sqrt_returns_nonneg_proves.py`)

```python
"""Test 0500 — math.sqrt: caller exploits non-negative result."""
# pycsl-expected: PASS
import math

#@ requires x >= 0
#@ ensures \result >= 0
def square_root_is_nonneg(x: int) -> int:
    return math.sqrt(x)
```

### Negative-test template (`math/sqrt_requires_nonneg_fails.py`)

```python
"""Test 1500 — math.sqrt: caller violates `requires x >= 0`."""
# pycsl-expected: FAIL
import math

#@ ensures \result >= 0
def root_of_anything(x: int) -> int:
    # No `requires x >= 0` here, so sqrt's precondition is
    # not provable at the call site.
    return math.sqrt(x)
```

## Workflow per function

Per function being promoted (typically L2 → L4 or L3 → L4):

1. **Read the official Python doc page**. Note the exact URL.
2. **Edit `src/pycsl_lib/<module>.py`**. Replace the bare
   `#@ \trusted` with the six-ingredient block. Don't add
   bodies — the existing `return 0` (or similar) is correct.
3. **Add the positive reference test** under
   `test-suite/corpus/python-reference/stdlib/<module>/`. Pick
   the next available 0500+ ID.
4. **Add the negative reference test**. Pick the next
   available 1500+ ID. Confirm `pycsl-expected: FAIL` is in
   the header.
5. **Run `make stdlib-coverage`**. Confirm the L4 (or L5)
   count for that module ticks up by one.
6. **Run the new tests**: `bash bin/run-reference-tests.sh
   --start-at 0500 --stop-at 0500` (or similar).
7. **Confirm 26/26 PROVED unchanged**: `bash
   bin/run-self-annotation-suite.sh`.

When all checks pass, commit. The commit message should cite
the doc URL and the L-level delta:

```
stdlib: math.sqrt L2 → L5 (cite docs.python.org/3/library/math.html#math.sqrt)
```

## Anti-patterns

- **Inventing a contract that isn't in the docs.** The
  `# cite:` URL is your evidence trail. If the URL doesn't say
  it, don't write it.
- **Over-strong `ensures` on ambiguous docs.** If the doc
  says "returns a non-negative integer", write
  `#@ ensures \result >= 0`, not `#@ ensures \result > 0`. The
  weaker contract is sound; the stronger is a soundness bug
  waiting for the doc edge case.
- **Skipping the negative test.** Without it, a wrong
  `requires` won't be caught (the verifier silently accepts
  the bad caller). The negative test is the soundness check.
- **Renaming a function in the stub to "match Python better".**
  The stub's function name must match the real Python name
  exactly — that's how the import classifier finds it.
- **Mixing the placeholder pattern with semantic clauses.**
  Once you write a real `ensures`, delete the placeholder
  `#@ ensures \result >= 0` next to it. Reviewers reading the
  block shouldn't have to figure out which clause is real.

---

# Part 3 — Where strategy meets per-function decisions

Use these bridges when the per-function rules in Part 2
under-determine an answer and the strategy in Part 1 has the
extra context.

## When to stop at L3 instead of pushing to L4

Part 2 Rule 4 says "side-effect functions cap at L3."
Part 1 says "accept that ~30% of `os` stays at L3."
Together: if you're annotating an `os` / `subprocess` /
`shutil` / `socket` function whose docstring describes a
filesystem, network, or process-spawning side effect, the
correct level is **L3 with `# cite:` + `ensures True` +
`assigns \nothing`** (or `assigns <abstract_fs>` if the
module already declares one). Do NOT invent a precondition
just to satisfy the L4 `requires`-side of the definition —
that's a soundness bug per Rule 3.

## Module-order priority for `--all` runs

When the agent runs `bin/agent-stdlib-annotate --all`, it
walks modules in alphabetical order (the coverage scanner's
default). Strategically, the user wants Phase 2's top-10
order: math → os.path → json → re → collections → itertools
→ typing → pathlib → string → argparse. The agent doesn't
re-sort — it goes alphabetically. If you (the user) want a
specific order, run per-module: `--module math`, then
`--module os.path`, etc., rather than `--all`. This is
deliberate: ordering is a human decision; the agent is
agnostic.

## Effort vs. depth trade-off per module

If `bin/stdlib-coverage-report.py --module <name>` shows
zero L3+ functions to start with, that module is fresh
ground — promoting takes longer (every function from L2).
If it already shows L3+, those have at least partial
content; the agent can refine the existing block rather
than write from scratch. This is why
`agent-stdlib-annotate.py:_build_prompt` includes the
current annotation block in the LLM context (line 348):
the LLM should refine, not rebuild.

## Soundness vs completeness preference (cross-cutting)

Strategy Risk 2 ("wrong `ensures` is a soundness bug") and
Part 2 Rule 3 ("prefer weaker postconditions") express the
same constraint. When in doubt:

- **Soundness > Completeness**. A weaker contract means more
  PyCSL programs fail to verify (false negatives we tolerate).
  A wrong-stronger contract means PyCSL incorrectly accepts
  wrong programs (false positives — soundness violations).
- **Test soundness with the negative test**. The 1500+
  negative test exercises the soundness claim ("PyCSL rejects
  a caller that violates `requires`"). If the negative test
  passes when it should fail, the `requires` clause is too
  weak — strengthen it.

## When to add a new module to `data/lib_stubs/` ordering

If a non-stubbed stdlib module shows up in real verification
work (a `# pycsl-expected: PASS` test imports it and PyCSL
fails on the import classifier), that's a Phase 2 / Phase 3
escalation signal. Add the module at the end of the
appropriate phase's priority list with a one-line rationale
(e.g., "needed by `examples/foo/`"). The strategy ratchet
documents *when* new modules entered scope and *why*.

---

# References

- [`.claude/plans/parsed-booping-ember.md`](../.claude/plans/parsed-booping-ember.md)
  — the synthesis plan this doc was generated from
  (Q&A-style; superseded by this doc).
- [`config/skills/csl-from-scratch/SKILL.md`](../config/skills/csl-from-scratch/SKILL.md)
  §11.1 — stdlib stubs methodology in the family playbook.
- [`config/skills/csl-from-scratch/references/phases-trust-discipline.md`](../config/skills/csl-from-scratch/references/phases-trust-discipline.md)
  — Phase 9 detailed treatment of stdlib coverage as a
  squeeze layer.
- [`docs/stdlib-annotation-conventions.md`](stdlib-annotation-conventions.md)
  — Part 2 lives here as a standalone human-reference doc
  (this file embeds + augments it).
- [`bin/stdlib-coverage-report.py`](../bin/stdlib-coverage-report.py)
  — the coverage classifier.
- [`docs/stdlib-coverage.md`](stdlib-coverage.md) — current
  coverage matrix (auto-regenerated by `make stdlib-coverage`).
- [`docs/glossary/trusted-computing-base.md`](glossary/trusted-computing-base.md)
  — TCB tier definitions (stdlib stubs are Tier 2).
- [`bin/agent-stdlib-annotate`](../bin/agent-stdlib-annotate) +
  [`src/pycsl/agents/agent-stdlib-annotate.py`](../src/pycsl/agents/agent-stdlib-annotate.py)
  — the agent that consumes this doc as its system prompt.
- [`config/agents/agent-stdlib-annotate.md`](../config/agents/agent-stdlib-annotate.md)
  — the agent's specification document.
