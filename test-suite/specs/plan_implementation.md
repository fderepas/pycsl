# PyCSL Test Suite — Implementation Plan

*Derived from `test-suite/plan.md` (dual-oracle architecture),
`test-suite/annotations.md` (contract language reference), and
`test-suite/python_reference/` (CPython semantics).*

---

## 1. Goal

Build a **dual-oracle compliance test suite** that validates PyCSL's
formal mathematical models against CPython's runtime semantics. Every
test file is run through both:

- **Static Oracle (PyCSL):** Modules 1–6 → WhyML → Why3 + SMT solver.
- **Dynamic Oracle (CPython):** Contract-instrumented Python → runtime assertions.

Discrepancies between the two oracles surface soundness bugs, false
positives, and missing coverage.

---

## 2. Architecture Overview

```
test-suite/
├── annotations.md              # PyCSL annotation reference (exists)
├── plan.md                     # Strategic plan (exists)
├── plan_implementation.md      # This document
├── python_reference/           # CPython language reference (exists)
│
├── instrumenter/               # Phase 1: Contract-to-Python transpiler
│   ├── __init__.py
│   ├── csl_to_python.py        # Contract AST → Python expression translator
│   ├── instrumenter.py         # AST rewriter: injects runtime checks
│   └── test_instrumenter.py    # Unit tests for the instrumenter
│
├── corpus/                     # Phase 2: Test corpus
│   ├── imported/               # Symlinks or copies from tests/manually_annotated/
│   ├── edge_cases/             # Generated edge-case files (new)
│   └── negative/               # Expected-failure tests
│
├── runner/                     # Phase 3: Dual-execution harness
│   ├── __init__.py
│   ├── static_oracle.py        # Runs pycsl, parses per-goal output
│   ├── dynamic_oracle.py       # Runs instrumented file, captures assertions
│   ├── evaluator.py            # Applies truth table, classifies results
│   └── report.py               # Generates JSON + summary reports
│
├── reports/                    # Output: per-file JSON compliance reports
└── run_suite.py                # Entry point: orchestrates everything
```

---

## 3. Phase 1: The Contract-to-Python Instrumenter

### 3.1 Purpose

Transform an annotated `.py` file into an instrumented `.py` file where
every PyCSL contract is enforced as a runtime `assert`. The instrumented
file must be independently executable with standard CPython.

### 3.2 Module: `csl_to_python.py` — Contract Expression Translator

This module walks a Module2_Parser Contract AST node and produces a Python
expression string. It reuses the existing `Module2_Parser` AST node types.

#### Translation table (Contract AST → Python expression)

| Contract AST Node | Python Output | Notes |
|---|---|---|
| `Number(42)` | `42` | Direct |
| `Var("x")` | `x` | Direct |
| `FieldAccess("self", "f")` | `self.f` | Direct |
| `SubscriptAccess("arr", idx)` | `arr[<idx>]` | Recursive on index |
| `Result()` | `_pycsl_result_` | Sentinel variable |
| `Old(Var("x"))` | `_pycsl_old_x` | Snapshot variable |
| `Old(FieldAccess("self","f"))` | `_pycsl_old_self_f` | Snapshot variable |
| `Old(SubscriptAccess("a",i))` | `_pycsl_old_a[<i>]` | Snapshot of array (deep copy) |
| `At(expr, "L")` | `_pycsl_at_L_<expr_hash>` | Snapshot at label `L` |
| `ArrayLength("arr")` | `len(arr)` | Direct |
| `Valid("arr", n)` | `(len(arr) >= <n>)` | Runtime check |
| `Valid2D("a", i, j)` | `(0 <= <i> < len(a) and 0 <= <j> < len(a[<i>]))` | |
| `Length2D("a", m, n)` | `(len(a) >= <m> and all(len(a[_i]) >= <n> for _i in range(<m>)))` | |
| `Separated("a",na,"b",nb)` | `(a is not b)` | Identity check (Hoare model) |
| `Nothing()` | N/A | Used in assigns, not in expressions |
| `BinOp(l, "==>", r)` | `(not (<l>) or (<r>))` | Implication |
| `BinOp(l, "<==>", r)` | `((<l>) == (<r>))` | Biconditional |
| `BinOp(l, "and", r)` | `((<l>) and (<r>))` | |
| `BinOp(l, "or", r)` | `((<l>) or (<r>))` | |
| `BinOp(l, "==", r)` | `((<l>) == (<r>))` | |
| `BinOp(l, "!=", r)` | `((<l>) != (<r>))` | |
| `BinOp(l, op, r)` | `((<l>) <op> (<r>))` | `+`, `-`, `*`, `<`, `>`, `<=`, `>=` |
| `BinOp(l, "/", r)` | `((<l>) // (<r>))` | Contract `/` = integer division |
| `UnaryOp("not", e)` | `(not (<e>))` | |
| `UnaryOp("-", e)` | `(-(<e>))` | |
| `Forall("i", body)` | See §3.2.1 | Requires range extraction |
| `Exists("i", body)` | See §3.2.1 | Requires range extraction |

#### 3.2.1 Quantifier range extraction

Quantifiers need finite iteration bounds at runtime. The standard PyCSL
pattern is:

```
\forall i; lo <= i and i < hi ==> body
\exists i; lo <= i and i < hi and body
```

**Algorithm:**

1. Walk the quantifier body looking for a conjunction of the form
   `lo <= var and var < hi` (or permutations: `var >= lo`, `hi > var`, etc.).
2. Extract `lo` and `hi` as Python expressions.
3. Emit:
   - `\forall`: `all(<body_remainder>(i) for i in range(<lo>, <hi>))`
   - `\exists`: `any(<body_remainder>(i) for i in range(<lo>, <hi>))`
4. If no finite range can be extracted, emit a `# SKIP: unbounded quantifier`
   comment and `True` (conservative: never fails), logging a warning.

**Nested quantifiers:** Apply recursively. Inner quantifier bounds may
reference the outer variable (e.g., `\forall i; 0 <= i and i < n ==> \forall j; 0 <= j and j < i ==> ...`).

### 3.3 Module: `instrumenter.py` — AST Rewriter

This module uses Modules 1–3 to parse contracts, then rewrites the Python
AST to inject runtime checks.

#### Input/Output

- **Input:** Path to annotated `.py` file.
- **Output:** Instrumented `.py` source string (or written to file).

#### Rewriting rules by contract type

##### 3.3.1 Function preconditions (`#@ requires expr`)

```python
# Original:
#@ requires x > 0
def f(x):
    return x + 1

# Instrumented:
def f(x):
    assert (x > 0), "Precondition failed: requires x > 0"
    return x + 1
```

All `requires` clauses become `assert` statements at the top of the
function body, after any docstring.

##### 3.3.2 Function postconditions (`#@ ensures expr`)

Every `return` statement is rewritten to capture the value and check
postconditions before returning.

```python
# Original:
#@ ensures \result == x + 1
def f(x):
    return x + 1

# Instrumented:
def f(x):
    _pycsl_result_ = x + 1
    assert (_pycsl_result_ == x + 1), "Postcondition failed: ensures \\result == x + 1"
    return _pycsl_result_
```

For functions with multiple `return` paths, each `return` is rewritten
independently.

For functions with no explicit `return`, add `_pycsl_result_ = None`
before postcondition checks at the end of the body.

##### 3.3.3 `\old` expressions in postconditions

When `\old(expr)` appears in an `ensures` clause, snapshot the expression
at function entry:

```python
# Original:
#@ ensures self._value == \old(self._value) + amount
def increment(self, amount):
    self._value += amount
    return self._value

# Instrumented:
def increment(self, amount):
    _pycsl_old_self__value = self._value  # snapshot
    _pycsl_result_ = ...
    assert (_pycsl_result_._value == _pycsl_old_self__value + amount)
    ...
```

For `\old(arr[i])` where `arr` is a list, use `import copy` and
`_pycsl_old_arr = copy.copy(arr)` (shallow copy sufficient for `list[int]`).

##### 3.3.4 Frame conditions (`#@ assigns`)

| Assigns target | Runtime check |
|---|---|
| `\nothing` | Snapshot all mutable parameters at entry; assert unchanged at exit |
| `x` | Snapshot all params except `x`; assert unchanged at exit |
| `arr[lo..hi]` | After call: `assert arr[:lo] == _old_arr[:lo] and arr[hi:] == _old_arr[hi:]` |
| `self.field` | Snapshot all other fields; assert unchanged at exit |

**Implementation complexity:** For `\nothing`, we need to identify all mutable
parameters. Heuristic: parameters with type annotation `list` or that are
subscript-assigned in the body are mutable. If no annotation, treat all
non-`int` parameters as potentially mutable.

##### 3.3.5 Loop invariants (`#@ loop invariant expr`)

Loop invariants must be checked at three points:
1. **Before the loop** (initialization: invariant holds on entry).
2. **At the end of each iteration body** (preservation: invariant maintained).
3. **After the loop exits** (the invariant still holds at termination).

```python
# Original:
i = 0
#@ loop invariant 0 <= i and i <= n
while i < n:
    i += 1

# Instrumented:
i = 0
assert (0 <= i and i <= n), "Loop invariant init failed"
while i < n:
    i += 1
    assert (0 <= i and i <= n), "Loop invariant preservation failed"
assert (0 <= i and i <= n), "Loop invariant at exit failed"
```

For `for` loops over `range(...)`, the same pattern applies. The loop
variable `i` is in scope for the invariant check.

##### 3.3.6 Loop variants (`#@ loop variant expr`)

```python
# Original:
#@ loop variant n - i
while i < n:
    i += 1

# Instrumented:
_pycsl_variant_prev_ = n - i
assert (_pycsl_variant_prev_ >= 0), "Loop variant not non-negative at entry"
while i < n:
    i += 1
    _pycsl_variant_cur_ = n - i
    assert (_pycsl_variant_cur_ >= 0), "Loop variant negative"
    assert (_pycsl_variant_cur_ < _pycsl_variant_prev_), "Loop variant not decreasing"
    _pycsl_variant_prev_ = _pycsl_variant_cur_
```

##### 3.3.7 Class invariants (`#@ class invariant expr`)

Class invariants must hold at the entry and exit of every public method
(including `__init__` exit).

```python
# Original:
#@ class invariant self._n >= 0
class Counter:
    def __init__(self):
        self._n = 0
    def increment(self, amount):
        self._n += amount

# Instrumented:
class Counter:
    def _pycsl_check_invariant_(self):
        assert (self._n >= 0), "Class invariant failed: self._n >= 0"

    def __init__(self):
        self._n = 0
        self._pycsl_check_invariant_()  # check at __init__ exit

    def increment(self, amount):
        self._pycsl_check_invariant_()  # check at method entry
        self._n += amount
        self._pycsl_check_invariant_()  # check at method exit
```

##### 3.3.8 Labels and `\at` expressions

When `#@ label L` appears before a statement, and `\at(expr, L)` appears
in an `ensures` clause:

```python
# Original:
#@ ensures arr[0] == \at(arr[0], PRE) + 1
def increment_first(arr, n):
    #@ label PRE
    arr[0] = arr[0] + 1
    return 0

# Instrumented:
def increment_first(arr, n):
    _pycsl_at_PRE_arr_0 = arr[0]    # snapshot at label PRE
    arr[0] = arr[0] + 1
    _pycsl_result_ = 0
    assert (arr[0] == _pycsl_at_PRE_arr_0 + 1), "Postcondition failed"
    return _pycsl_result_
```

##### 3.3.9 `continue` inside loops with invariants

When a loop body contains `continue`, the invariant check must be
inserted **before** the `continue` statement as well:

```python
while i < n:
    if condition:
        i += 1
        assert invariant, "Loop invariant before continue"
        continue
    # ... rest of body ...
    assert invariant, "Loop invariant at end of iteration"
```

### 3.4 Integration with Modules 1–3

```python
from Module1_Ingestor import Module1_Ingestor
from Module2_Parser import Module2_Parser
from Module3_Weaver import Module3_Weaver

def instrument_file(source_path: str) -> str:
    with open(source_path) as f:
        source_code = f.read()

    # Reuse PyCSL's own frontend
    ingestor = Module1_Ingestor(source_code)
    extracted = ingestor.process()
    parser = Module2_Parser()
    weaver = Module3_Weaver(source_code, extracted, parser)
    annotated_ast = weaver.process()

    # Walk the annotated AST and produce instrumented source
    rewriter = InstrumenterRewriter(annotated_ast, source_code)
    return rewriter.generate()
```

### 3.5 Unit tests for the instrumenter

`test_instrumenter.py` should cover:

| Test | Input contract | Expected behavior |
|---|---|---|
| Simple precondition | `requires x > 0` | Assert at function entry |
| Postcondition with `\result` | `ensures \result == x + 1` | Return value captured |
| `\old` in postcondition | `ensures x == \old(x) + 1` | Snapshot at entry |
| `\forall` bounded | `ensures \forall i; 0<=i and i<n ==> a[i]>=0` | `all(...)` expression |
| `\exists` bounded | `ensures \exists i; 0<=i and i<n and a[i]==0` | `any(...)` expression |
| Implication `==>` | `requires x>0 ==> y>0` | `not ... or ...` |
| Loop invariant | `loop invariant i >= 0` | Assert at 3 points |
| Loop variant | `loop variant n - i` | Decreasing + non-negative |
| Class invariant | `class invariant self._n >= 0` | Entry+exit of every method |
| Frame `assigns \nothing` | `assigns \nothing` | Snapshot + compare |
| `\at` with label | `ensures a[0] == \at(a[0], L) + 1` | Snapshot at label |
| Multiple `return` paths | Function with `if/else` returns | Each path instrumented |
| Nested quantifier | `\forall i; ... ==> \forall j; ...` | Nested `all()` |
| Division `/` in contract | `ensures \result == x / 2` | Translates to `x // 2` |

---

## 4. Phase 2: Test Corpus Construction

### 4.1 Source 1: Imported from existing tests

Copy (or symlink) all annotated `.py` files from `tests/manually_annotated/`
into `test-suite/corpus/imported/`. These files already have `#@`
annotations and verified WhyML outputs.

**Current coverage from existing files:**

| Category | Files | Python Constructs (from python_reference/) |
|---|---|---|
| Basic control flow | 001–010 | `if`/`elif`/`else`, `while`, assignment, augmented assignment, `return` |
| Functions + contracts | 011–020 | Function definitions (§8.7), preconditions, postconditions |
| Class L2 (mutable records) | 021–030 | Class definitions (§8.7), `self.field` attribute access (§6.3.2), `__init__` |
| Class L3 (invariants) | 031–040 | Same as L2 + class-level invariants |
| Arrays (hoare) | 041–055 | Subscript access (§6.3.3), `for` over `range()` (§8.3), `continue` (§7.9) |
| Arrays (typed/store) | 056–075 | Same constructs + `\valid`, `\separated`, `\old(arr[i])` |
| Labels + `\at` | 076–080 | No new Python constructs; tests the `\at` contract feature |
| 2D matrices | 081–085 | Nested subscripts `a[i][j]`, nested `for` loops |
| Quantifiers | 086–091 | No new Python constructs; tests `\forall`/`\exists` contracts |

### 4.2 Source 2: Generated edge-case files

Each generated file must contain:
1. A function with `#@` annotations.
2. A `__main__` block with specific test calls covering the edge case.

#### 4.2.1 Category: Integer arithmetic semantics

These test the semantic gap between CPython and Why3/Alt-Ergo.

**Reference:** Python Language Reference §6.7 (Binary arithmetic operations):
> "The modulo operator always yields a result with the same sign as its
> second operand."
> "x == (x//y)*y + (x%y)"

| File | Code body | Contract | Semantic gap tested |
|---|---|---|---|
| `edge-int-mod-neg.py` | `return (-7) % 3` | `ensures \result == 2` | CPython mod sign = divisor sign; WhyML `mod` is Euclidean |
| `edge-int-floordiv-neg.py` | `return (-7) // 3` | `ensures \result + 1 == 0 - 2` | CPython `//` rounds toward -∞; C div truncates toward 0 |
| `edge-int-large.py` | `return x * x` where `x = 2**64` | `ensures \result == x * x` | CPython arbitrary precision; verify Why3 `int` is unbounded |
| `edge-int-identity.py` | `q = x // y; r = x % y; return q * y + r` | `ensures \result == x` | The fundamental identity `x == (x//y)*y + (x%y)` |

Note: `%` and `//` appear in the **code body**, not in contracts (since
contracts don't support them — see `annotations.md` §4).

#### 4.2.2 Category: Boolean coercion (truthiness)

**Reference:** Python Language Reference §6.12 (Boolean operations):
> "the following values are interpreted as false: False, None, numeric
> zero of all types, and empty strings and containers."

| File | Code body | Contract | Semantic gap tested |
|---|---|---|---|
| `edge-bool-int-nonzero.py` | `if x: return 1; else: return 0` | `requires x == 5; ensures \result == 1` | Non-zero int is truthy |
| `edge-bool-int-zero.py` | `if x: return 1; else: return 0` | `requires x == 0; ensures \result == 0` | Zero is falsy |
| `edge-bool-neg.py` | `if x: return 1; else: return 0` | `requires x + 1 == 0; ensures \result == 1` | Negative int is truthy |

These test whether Module6 correctly translates `if x:` to a WhyML
condition (should it be `if x <> 0` or `if x`?).

#### 4.2.3 Category: Short-circuit evaluation

**Reference:** Python Language Reference §6.12:
> "The expression `x and y` first evaluates x; if x is false, its value
> is returned; otherwise, y is evaluated."

| File | Code body | Contract | Semantic gap tested |
|---|---|---|---|
| `edge-short-and.py` | `if n > 0 and arr[0] > 0: return 1; return 0` | `requires n == 0; ensures \result == 0` | `arr[0]` must not be evaluated when `n == 0` |
| `edge-short-or.py` | `if n == 0 or arr[0] > 0: return 1; return 0` | `requires n == 0; ensures \result == 1` | `arr[0]` must not be evaluated when `n == 0` |

#### 4.2.4 Category: Negative tests (expected failures)

These test that both oracles correctly detect problems.

| File | Scenario | Expected Path A | Expected Path B |
|---|---|---|---|
| `neg-buggy-code.py` | Correct contract, buggy code: `ensures \result == x + 1` but body returns `x + 2` | Invalid | AssertionError |
| `neg-wrong-contract.py` | Wrong contract, correct code: `ensures \result == x + 2` but body returns `x + 1` | Invalid | AssertionError |
| `neg-precondition-violation.py` | Caller violates precondition in `__main__` | Valid (proof is conditional) | AssertionError |
| `neg-invariant-break.py` | Loop body breaks the invariant on one path | Invalid or Unknown | AssertionError |

#### 4.2.5 Category: Contract edge cases

| File | Feature tested | Specifics |
|---|---|---|
| `edge-nested-quantifier.py` | Nested `\forall` | `\forall i; ... ==> \forall j; 0<=j and j<i ==> ...` |
| `edge-multi-old.py` | Multiple `\old` in one ensures | `ensures arr[0]==\old(arr[1]) and arr[1]==\old(arr[0])` (swap) |
| `edge-multi-label.py` | `\at` with multiple labels | Two `#@ label` + ensures referencing both |
| `edge-class-inv-method.py` | Class invariant + method contracts | Invariant + requires + ensures + assigns on same method |
| `edge-pure-function.py` | `assigns \nothing` on complex function | Verify no mutation occurs |
| `edge-empty-contract.py` | Function with no `#@` annotations | Should pass trivially in both oracles |
| `edge-multiple-returns.py` | Function with 3+ return paths | All paths must satisfy postcondition |

---

## 5. Phase 3: Dual-Execution Runner

### 5.1 Module: `static_oracle.py`

```python
def run_static_oracle(test_file: str, memory_model: str = "hoare") -> StaticResult:
    """Run pycsl on the test file and parse per-goal results."""
    cmd = ["./pycsl", test_file, "--memory-model", memory_model]
    result = subprocess.run(cmd, capture_output=True, text=True)

    goals = []
    for line in result.stdout.splitlines():
        # Parse: "FuncName VCKind : Valid (0.01s, 42 steps)"
        match = re.match(r'(\S+)\s+(\S+)\s*:\s*(\w+)', line)
        if match:
            goals.append(Goal(
                function=match.group(1),
                kind=match.group(2),
                result=match.group(3)  # "Valid", "Unknown", "Invalid", "Timeout"
            ))

    return StaticResult(
        exit_code=result.returncode,
        goals=goals,
        all_valid=all(g.result == "Valid" for g in goals) and len(goals) > 0,
        stdout=result.stdout,
        stderr=result.stderr
    )
```

### 5.2 Module: `dynamic_oracle.py`

```python
def run_dynamic_oracle(test_file: str) -> DynamicResult:
    """Instrument and run the test file, capturing assertion results."""
    # Step 1: Instrument
    instrumented_source = instrument_file(test_file)
    instrumented_path = test_file.replace('.py', '_instrumented.py')
    with open(instrumented_path, 'w') as f:
        f.write(instrumented_source)

    # Step 2: Execute
    result = subprocess.run(
        ["python3", instrumented_path],
        capture_output=True, text=True, timeout=30
    )

    # Step 3: Parse assertion errors
    assertion_errors = []
    for line in result.stderr.splitlines():
        if "AssertionError" in line or "assert" in line.lower():
            assertion_errors.append(line.strip())

    return DynamicResult(
        exit_code=result.returncode,
        passed=(result.returncode == 0),
        assertion_errors=assertion_errors,
        stdout=result.stdout,
        stderr=result.stderr
    )
```

### 5.3 Module: `evaluator.py`

Applies the truth table per-function:

```python
def classify(static: StaticResult, dynamic: DynamicResult) -> Classification:
    if static.all_valid and dynamic.passed:
        return Classification.SUCCESS
    elif not static.all_valid and not dynamic.passed:
        return Classification.SUCCESS
    elif not static.all_valid and dynamic.passed:
        return Classification.FALSE_POSITIVE
    elif static.all_valid and not dynamic.passed:
        return Classification.SOUNDNESS_BUG
```

**SOUNDNESS_BUG** is the critical finding: PyCSL proved the code safe,
but CPython crashed. This indicates a bug in Module5 or Module6.

### 5.4 Module: `report.py`

Generates per-file JSON reports (stored in `test-suite/reports/`):

```json
{
  "file": "086-forall-all-nonneg.py",
  "timestamp": "2026-05-13T23:06:00Z",
  "memory_model": "hoare",
  "static_oracle": {
    "exit_code": 0,
    "goals": [
      {"function": "clamp_nonneg", "kind": "precondition", "result": "Valid"},
      {"function": "clamp_nonneg", "kind": "loop_invariant_init", "result": "Valid"},
      {"function": "clamp_nonneg", "kind": "postcondition", "result": "Valid"}
    ],
    "all_valid": true
  },
  "dynamic_oracle": {
    "exit_code": 0,
    "passed": true,
    "assertion_errors": []
  },
  "classification": "SUCCESS"
}
```

Plus an aggregate summary report:

```json
{
  "total": 91,
  "success": 85,
  "false_positive": 5,
  "soundness_bug": 0,
  "skipped": 1,
  "details": { ... }
}
```

---

## 6. Entry Point: `run_suite.py`

```python
#!/usr/bin/env python3
"""PyCSL Dual-Oracle Compliance Test Suite."""

import sys, os, json, glob

def main():
    corpus_dir = "test-suite/corpus"
    reports_dir = "test-suite/reports"

    test_files = sorted(glob.glob(f"{corpus_dir}/**/*.py", recursive=True))
    results = []

    for test_file in test_files:
        # Determine memory model from filename convention
        memory_model = detect_memory_model(test_file)

        # Path A: Static Oracle
        static = run_static_oracle(test_file, memory_model)

        # Path B: Dynamic Oracle
        dynamic = run_dynamic_oracle(test_file)

        # Classify
        classification = classify(static, dynamic)
        report = generate_report(test_file, static, dynamic, classification)
        results.append(report)

        # Save individual report
        save_report(report, reports_dir)

        # HALT on soundness bug
        if classification == Classification.SOUNDNESS_BUG:
            print(f"🚨 SOUNDNESS BUG in {test_file}")
            print(f"   Static: all goals Valid")
            print(f"   Dynamic: AssertionError")
            sys.exit(2)

    # Generate aggregate summary
    summary = generate_summary(results)
    save_summary(summary, reports_dir)
    print_summary(summary)

    sys.exit(0 if summary["soundness_bug"] == 0 else 2)
```

### Memory model detection

Files from `tests/manually_annotated/` encode the memory model in their
name:
- `061-typed-*` → `--memory-model typed`
- `071-store-*` → `--memory-model store`
- All others → `--memory-model hoare` (default)

---

## 7. Python Semantics Requiring Special Attention

Cross-referencing `test-suite/python_reference/` with PyCSL's pipeline,
the following CPython semantics require explicit test coverage because
they may diverge from Why3/SMT solver behavior:

### 7.1 Integer semantics

| CPython behavior (ref: `expressions.rst` §6.7) | WhyML/Why3 behavior | Risk |
|---|---|---|
| `int` is arbitrary precision | Why3 `int` is mathematical (unbounded) | ✅ Compatible |
| `//` rounds toward -∞ | WhyML `div` is Euclidean (rounds toward 0 for negatives) | ⚠️ **Divergence** |
| `%` result has sign of divisor | WhyML `mod` is Euclidean (always non-negative) | ⚠️ **Divergence** |
| `/` (true division) returns `float` | WhyML `/` is not used; PyCSL maps to `div` | N/A |

### 7.2 Boolean semantics

| CPython behavior (ref: `expressions.rst` §6.12) | WhyML behavior | Risk |
|---|---|---|
| `0`, `None`, empty containers are falsy | WhyML has no truthiness concept | ⚠️ **Divergence** if `if x:` not translated to `x <> 0` |
| `and`/`or` return operand values, not `True`/`False` | WhyML `&&`/`\|\|` return `bool` | Low risk (PyCSL only uses in conditions) |
| `and`/`or` are short-circuit | WhyML `&&`/`\|\|` are logical (no side effects) | ⚠️ **Divergence** if code depends on evaluation order |

### 7.3 Control flow

| CPython behavior (ref: `compound_stmts.rst` §8.2–8.3) | WhyML behavior | Risk |
|---|---|---|
| `while`/`else` clause (runs when condition becomes false) | No WhyML equivalent | Low (PyCSL doesn't support `else` on loops) |
| `for` iterates over arbitrary iterables | PyCSL only supports `for i in range(n)` | ✅ Scope restricted |
| `continue` skips rest of iteration | WhyML has no `continue` (desugared in IR) | Needs testing |
| `break` exits loop | Not currently supported by PyCSL | N/A |

### 7.4 Assignment semantics

| CPython behavior (ref: `simple_stmts.rst` §7.2) | WhyML behavior | Risk |
|---|---|---|
| Augmented assignment `x += e` | WhyML `x := !x + e` (ref cell update) | ✅ Compatible |
| Multiple assignment `a = b = expr` | Not supported by PyCSL IR | N/A |
| Tuple unpacking `a, b = b, a` | Not supported by PyCSL IR | N/A |

### 7.5 Class semantics

| CPython behavior (ref: `compound_stmts.rst` §8.7) | WhyML behavior | Risk |
|---|---|---|
| `self` is explicit parameter | WhyML methods receive `(self: type)` | ✅ Compatible |
| `__init__` returns `None` | WhyML constructor is a `let` that returns the record | Needs translation care |
| Inheritance | Not supported by PyCSL | N/A |
| `__dunder__` methods | Not supported by PyCSL | N/A |

---

## 8. Implementation Order

The phases must be implemented in dependency order:

### Step 1: `csl_to_python.py` — Contract expression translator

No dependencies beyond Module2_Parser's AST node types. Can be unit-tested
independently.

**Deliverables:**
- `translate(node: CSLNode) -> str` function
- Unit tests covering every AST node type
- Quantifier range extraction logic

### Step 2: `instrumenter.py` — AST rewriter

Depends on Step 1 + Modules 1–3.

**Deliverables:**
- `instrument_file(path: str) -> str` function
- Handles all 9 contract types (§3.3.1–3.3.9)
- Integration tests: instrument a known file, run it, verify exit code

### Step 3: Test corpus assembly

Depends on nothing (can be done in parallel with Steps 1–2).

**Deliverables:**
- Import existing annotated files into `corpus/imported/`
- Generate edge-case files into `corpus/edge_cases/`
- Generate negative tests into `corpus/negative/`

### Step 4: `static_oracle.py` + `dynamic_oracle.py`

Depends on Step 2 (for dynamic oracle) and the `pycsl` binary.

**Deliverables:**
- Static oracle: run pycsl, parse per-goal output
- Dynamic oracle: instrument + run + capture

### Step 5: `evaluator.py` + `report.py` + `run_suite.py`

Depends on Step 4.

**Deliverables:**
- Truth table classification
- Per-file JSON reports
- Aggregate summary
- Exit code 2 on soundness bugs

### Step 6: Validation

Run the complete suite. Triage results:
- **SUCCESS:** File passes both oracles. No action needed.
- **FALSE POSITIVE:** Document. May indicate solver timeout or overly-strict
  translation. Flag for PyCSL improvement.
- **SOUNDNESS BUG:** Investigate Module5/Module6 immediately.

---

## 9. Test File Conventions

Every test file in the corpus must follow these conventions:

1. **Filename:** `<NNN>-<category>-<name>.py` for imported files;
   `edge-<category>-<name>.py` or `neg-<category>.py` for generated files.

2. **Self-contained:** Each file must be independently executable with
   `python3 <file>`. No external imports beyond stdlib.

3. **`__main__` block:** Every file must have an `if __name__ == "__main__":`
   block that calls the annotated functions with concrete arguments
   exercising the contracts.

4. **Annotations:** All `#@` annotations must conform to
   `test-suite/annotations.md`.

5. **Memory model marker:** Files requiring non-default memory model must
   have a comment `# pycsl-memory-model: typed` or `# pycsl-memory-model: store`
   on the first line.

6. **Expected result marker (negative tests only):**
   `# pycsl-expected: false-positive` or `# pycsl-expected: both-fail`
   on the second line.

---

## 10. Dependencies and Prerequisites

| Dependency | Purpose | Install |
|---|---|---|
| Python 3.10+ | Runtime for instrumenter and test corpus | System |
| `libcst` | Module1_Ingestor (contract extraction) | `pip install libcst` |
| `lark` | Module2_Parser (contract parsing) | `pip install lark` |
| Why3 + Alt-Ergo / Z3 | Static oracle (formal verification) | System |
| `copy` (stdlib) | `\old` snapshot of mutable objects | Built-in |
| `ast` (stdlib) | AST manipulation for instrumenter | Built-in |
| `json` (stdlib) | Report generation | Built-in |
