# PyCSL Dual-Oracle Compliance Test Suite

A test suite that validates PyCSL's formal verification pipeline against CPython's runtime semantics. Each annotated Python file is run through two independent oracles and the results are cross-checked.

## Quick Start

```bash
# Run all tests (dynamic oracle only — no Why3 needed)
python3 test-suite/run_suite.py --dynamic-only

# Run both oracles (requires Why3 + Alt-Ergo)
python3 test-suite/run_suite.py

# Run specific files
python3 test-suite/run_suite.py test-suite/corpus/edge_cases/edge_003_result_basic.py
```

## How It Works

### The Two Oracles

| Oracle | What it does | Requires |
|--------|-------------|----------|
| **Static** | Runs PyCSL → WhyML → Why3/Alt-Ergo to formally prove contracts | `why3`, `alt-ergo` |
| **Dynamic** | Instruments Python source with `assert` statements, then executes it | Python 3 only |

### Verdict Classification

When both oracles run, their results are cross-checked:

| Static | Dynamic | Verdict | Meaning |
|--------|---------|---------|---------|
| PASS | PASS | **SUCCESS** | Contract is correct and provable |
| PASS | FAIL | **SOUNDNESS_BUG** ⚠️ | Prover says valid but runtime disagrees |
| FAIL | PASS | **FALSE_POSITIVE** | Prover can't prove it but it's correct at runtime |
| FAIL | FAIL | **EXPECTED_FAIL** | Both agree the contract is wrong |

When running with `--dynamic-only` or `--static-only`, verdicts are prefixed accordingly (e.g. `DYNAMIC_PASS`, `STATIC_FAIL`).

## Command-Line Options

```
python3 test-suite/run_suite.py [OPTIONS] [FILE ...]

positional arguments:
  FILE              Specific test files to run (default: all corpus files)

options:
  --dynamic-only    Skip the static oracle (no Why3 needed)
  --static-only     Skip the dynamic oracle
  --timeout N       Per-test timeout in seconds (default: 30)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests classified as expected |
| 1 | At least one oracle error |
| 2 | **Soundness bug detected** — static says PASS but dynamic says FAIL |

## Test Corpus

Tests live in `test-suite/corpus/` under three directories:

| Directory | Contents |
|-----------|----------|
| `imported/` | 56 files copied from `tests/manually_annotated/` |
| `edge_cases/` | 10 hand-crafted files targeting semantic edge cases (integer division, `\old`, quantifiers, implication, frame conditions, etc.) |
| `negative/` | 3 files with intentionally wrong contracts (expected to fail) |

### Adding a Test

1. Create a `.py` file with `#@` contract annotations in the appropriate corpus directory.
2. Include an `if __name__ == "__main__":` block that exercises the annotated functions.
3. If the `#@` annotations appear before the **first** statement in the file, add a dummy line (e.g. `_ = 0`) before them — this is a LibCST limitation where top-of-file comments are stored in the module header rather than a statement's leading lines.

## Project Layout

```
test-suite/
├── run_suite.py              # Entry point
├── instrumenter/
│   ├── csl_to_python.py      # Contract AST → Python expression translator
│   └── instrumenter.py       # AST rewriter injecting runtime assertions
├── runner/
│   ├── static_oracle.py      # Runs PyCSL/Why3 pipeline
│   ├── dynamic_oracle.py     # Instruments + executes Python files
│   ├── evaluator.py          # Cross-checks oracle results
│   └── report.py             # JSON + console report generator
├── corpus/
│   ├── imported/             # Tests from tests/manually_annotated/
│   ├── edge_cases/           # Semantic edge-case tests
│   └── negative/             # Expected-failure tests
├── reports/                  # Generated JSON reports
├── annotations.md            # PyCSL annotation language reference
├── plan.md                   # Original test plan + review
└── plan_implementation.md    # Detailed implementation plan
```

## Dependencies

- **Python 3.10+** with `libcst` and `lark` (same as PyCSL itself)
- **Why3 + Alt-Ergo** (only for the static oracle; not needed with `--dynamic-only`)
