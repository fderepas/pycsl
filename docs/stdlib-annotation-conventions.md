# Stdlib stub annotation conventions

How to promote a `src/pycsl_lib/<module>.py` stub function from
L2 (trusted, no semantic content) to L4 (full contract) or L5
(L4 + reference test). Operationalizes the strategy in
[`.claude/plans/parsed-booping-ember.md`](../.claude/plans/parsed-booping-ember.md).

The stdlib stubs are **Tier 2 trust** (per `csl-from-scratch`
skill §11.1): PyCSL does not verify CPython's implementation. We
verify *programs that call stdlib* against the stub's
contract. A wrong contract on a trusted stub is therefore a
**soundness bug** — it can cause unsound conclusions about
correct-looking user code. Prefer being conservative.

---

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
contracts. Anything else (a constraint on inputs, a relationship
between inputs and outputs, a raises-clause) is semantic.

---

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

---

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

---

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

---

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

---

## Anti-patterns

- **Inventing a contract that isn't in the docs.** The
  `\cite` URL is your evidence trail. If the URL doesn't say
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

## References

- [`.claude/plans/parsed-booping-ember.md`](../.claude/plans/parsed-booping-ember.md)
  — the multi-quarter strategy this doc operationalizes.
- [`config/skills/csl-from-scratch/SKILL.md`](../config/skills/csl-from-scratch/SKILL.md)
  §11.1 — stdlib stubs methodology in the family playbook.
- [`bin/stdlib-coverage-report.py`](../bin/stdlib-coverage-report.py)
  — the coverage classifier.
- [`docs/stdlib-coverage.md`](stdlib-coverage.md) — current
  coverage matrix (auto-regenerated by `make stdlib-coverage`).
- [`docs/glossary/trusted-computing-base.md`](glossary/trusted-computing-base.md)
  — TCB tier definitions (stdlib stubs are Tier 2).
