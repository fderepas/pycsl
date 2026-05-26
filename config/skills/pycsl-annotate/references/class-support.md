# Class Support

Classes are supported via **Level 2 record types**. Keep the `class` keyword and annotate methods directly. The pipeline emits a WhyML mutable record (`type classname = { mutable field: int }`); each method receives `(self: classname)` as its first parameter.

## Method annotation rules

- **Do NOT annotate `__init__` or `@property` methods** — they are skipped by the IR emitter.
- **Copy `__init__` verbatim**: When a class has an `__init__` method, copy every statement in its body exactly as written in the input source (e.g., `self._y = 100`). NEVER remove, move, or add any statements to `__init__`. The contracts for the *next* method must appear AFTER `__init__`'s last body statement, followed by a blank line, then the `#@` annotation block, then that method's `def`.
- **Consistent `#@` indentation inside class bodies**: Every `#@` annotation line immediately before a `def` inside a class must be indented to EXACTLY the same column as that `def` keyword (4 spaces for a top-level class). NEVER mix zero-indented and 4-space-indented `#@` lines within the same annotation block.
- **NEVER duplicate any statement**: When rewriting or annotating a method body, emit each statement exactly once. In particular, NEVER write two `return` statements with the same value back-to-back, NEVER duplicate an assignment such as `self._y -= n`, and NEVER define the same method name more than once in the same class body.
- **Use `self.field` syntax directly in `#@` contracts** — the parser accepts `FieldAccess` nodes natively.
- **Use `\old(self.field)` in `ensures`** to refer to the field at method entry: `#@ ensures self._balance == \old(self._balance) + n` emits `(old self._balance)`.
- **Each method must have all three contracts** (`#@ requires`, `#@ ensures`, `#@ assigns`) immediately before its `def`.
- **`#@ assigns self._field`** (or `\nothing` for pure read-only methods) is the correct frame syntax.
- **Eliminate all default argument values** (e.g., change `def f(self, x: int = 0)` to `def f(self, x: int)`).
- **Class names auto-lowercase**: WhyML requires lowercase function names; the pipeline auto-lowercases the prefix (e.g., `Counter.increment` → `counter__increment`). Python convention already satisfies this.
- **NEVER use `with` context managers** inside an annotated method body. The IR pipeline has no handler for `ast.With`, so the entire block body is silently dropped. Replace `with <ctx>: <body>` with the raw `<body>` statements directly.
- **Mixed files** (class + standalone functions) are supported. Standalone functions emit as plain `let f (args) : type` with no `self` parameter.
- **Multi-field records** work automatically: every `self.x = ...` in `__init__` becomes a `mutable x: int` field.
- **Pure read-only methods** are valid: `FieldGet` nodes emit `self.field` as plain record access with no `<-`.

## Example — Counter with one field

```python
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ requires self._value >= 0
    #@ ensures \result >= 0
    #@ assigns self._value
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value

    #@ requires True
    #@ ensures \result == 0
    #@ assigns self._value
    def reset(self) -> int:
        self._value = 0
        return self._value
```

## Example — using `\old` to relate pre- and post-state

```python
class Ledger:
    def __init__(self):
        self._balance = 0

    #@ requires n >= 0
    #@ ensures self._balance == \old(self._balance) + n
    #@ assigns self._balance
    def deposit(self, n: int) -> int:
        self._balance += n
        return self._balance
```

## Level 3 — Class invariants

Declare a property that must hold at all times with `#@ class invariant <expr>`. The pipeline emits this as a Why3 record invariant (`invariant { ... } by { ... }`), automatically checked at every method entry and exit — no per-method clause needed.

- **Place `#@ class invariant <expr>` immediately before the `class` keyword** (not inside the class body). If it is the very first line of the file, prepend the sentinel `""  # pycsl`.
- **Use `self.field` in invariant expressions** — the parser rewrites to bare field names in WhyML.
- **Multiple invariants** — one `#@ class invariant` line per clause, stacked in the WhyML record.
- **Cross-field invariants** (e.g., `self._lo <= self._hi`) are fully supported.
- **Compound invariants with `and`** (e.g., `self._val >= 0 and self._val <= 100`) emit as a single Why3 `invariant` clause.
- **Each method's preconditions must be strong enough to maintain the invariant.** For methods that **add** a parameter to an invariant-guarded field (e.g., `self._n += amount` where `#@ class invariant self._n >= 0`), you MUST write `#@ requires amount >= 0` — **never** `#@ requires True`. For methods that **subtract** (e.g., `self._balance -= amount` where `_balance >= 0`), you MUST write `#@ requires amount <= self._balance`. See also the critical rule in Section 4.
- **`by` witness** is auto-generated from `__init__` assignments. No manual work required.
- **Do NOT use `//`, `%`, or `len(...)`** in `#@ class invariant` (same restrictions as `requires`/`ensures`).
- **Two classes in one file** each get their own independent `#@ class invariant`.

```python
""  # pycsl
#@ class invariant self._value >= 0
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    #@ assigns self._value
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```

## Example — Two classes, each with its own invariant

This example shows the correct structure when two classes each have an `__init__`, a mutating method, and a read-only getter. Key rules demonstrated:
- `__init__` bodies are copied verbatim (no annotation, no changes to body statements).
- All `#@` lines within a class are indented exactly 4 spaces (same as the `def` they precede).
- No statement is duplicated; each method appears exactly once.

```python
""  # pycsl
#@ class invariant self._x >= 0
class Up:
    def __init__(self):
        self._x = 0

    #@ requires n >= 0
    #@ ensures \result == \old(self._x) + n
    #@ assigns self._x
    def inc(self, n: int) -> int:
        self._x += n
        return self._x

    #@ requires True
    #@ ensures \result == self._x
    #@ assigns \nothing
    def get(self) -> int:
        return self._x


#@ class invariant self._y >= 0
class Down:
    def __init__(self):
        self._y = 100

    #@ requires n >= 0
    #@ requires n <= self._y
    #@ ensures \result == \old(self._y) - n
    #@ assigns self._y
    def dec(self, n: int) -> int:
        self._y -= n
        return self._y

    #@ requires True
    #@ ensures \result == self._y
    #@ assigns \nothing
    def get(self) -> int:
        return self._y
```
