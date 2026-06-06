# Real-World Modeling Patterns (from rclpy verification)

Load when annotating production code (not toy examples) — especially
class hierarchies, IntEnum-style parameters, or call sites that hit
transpiler bugs. The patterns below were discovered during formal
verification of the ROS 2 `rclpy` library (97 goals, 6 files, 100%
proof rate).

## File-level anchors

Every annotated file needs a sentinel line near the top so pycsl can
detect the annotation style:

- **`_ = 0  # anchor`** — for files without classes (standalone functions)
- **`""  # pycsl`** — for files with classes (class-centric models)

## Modeling complex classes as simplified models

Real-world classes often have 20+ methods and deep inheritance. PyCSL
verification targets a *model* of the class, not the full implementation:

1. Identify the **state fields** that carry safety-critical invariants
   (e.g., `_active`, `_count`, `_nanoseconds`)
2. Write a **class invariant** over those fields
3. Model only the **methods that mutate** invariant fields + key query
   methods
4. Use `#@ \trusted` for methods that call C extensions or external code

## Enum-as-integer modeling

Python `IntEnum` values should be modeled as plain `int` parameters with
range preconditions:

```python
#@ requires policy == 0 or policy == 1   # KEEP_ALL=0, KEEP_LAST=1
```

This keeps contracts in the integer domain that SMT solvers handle
efficiently.

## Transpiler workarounds (must know)

See [`transpiler-limits.md`](transpiler-limits.md) §12 for confirmed transpiler bugs:

- **TR-BUG-1 (float precision):** Large constants (>2^53) lose precision.
  Use `< 2^63` instead of `<= 2^63-1`.
- **TR-BUG-2 (purity bug):** Functions with `#@ raises` but no local
  variables are emitted as pure (`let function`) and Why3 rejects them
  as effectful. Add at least one local-variable assignment to force
  `let` (mutable) emission. *Especially important for `no_exception`
  interprocedural propagation* — when a callee with
  `raises { E -> P }` is invoked from a `no_exception E` caller,
  Module 6 wraps the call in `try ... with E -> absurd end`, which
  requires the callee to be effectful. Worked example:
  `test-suite/corpus/pycsl-reference/0383.py` (the local `m = n` is
  the TR-BUG-2 dodge).

## `no_exception` interprocedural-call patterns

When a function callable from `no_exception` contexts has any
`#@ raises` clause, follow this template:

```python
#@ requires True
#@ ensures \result == 256 / n
#@ raises ZeroDivisionError when n == 0
#@ assigns \nothing
def maybe_raise(n: int) -> int:
    m = n               # ← TR-BUG-2 dodge: force mutable emission
    if m == 0:
        raise ZeroDivisionError
    return 256 // m
```

The caller can then claim `no_exception ZeroDivisionError` and
discharge the propagated assertion via its own precondition:

```python
#@ requires n != 0
#@ ensures \result == 256 / n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def safe_caller(n: int) -> int:
    return maybe_raise(n)   # ← Module 6 wraps with try/with E -> absurd
```

## Simple class invariants (the trivial-prove pattern)

For pure data-carrier classes whose fields are non-negative integers,
the simplest provable invariant is `self.<field> >= 0`. This is the
seed pattern for self-annotation:

```python
#@ class invariant self.line >= 0
class PyCSLError(Exception):
    def __init__(self, message: str, *, filename: str = "",
                 line: int = 0, stage: str = "") -> None:
        super().__init__(message)
        self.filename = filename
        self.line = line
        self.stage = stage
```

PyCSL emits the invariant as a WhyML type invariant on the record;
the proof obligation is trivially valid because `line` only receives
a `: int = 0` default-or-caller-supplied value. Worked example:
`src/pycsl/errors.py` (the self-annotation suite seed —
`bin/run-self-annotation-suite.sh` proves it end-to-end).
