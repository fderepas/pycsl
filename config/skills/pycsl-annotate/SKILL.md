---
name: pycsl-annotate
description: Annotates Python code with PyCSL Hoare-logic contracts (requires, ensures, assigns, loop invariants, loop variants) that compile to WhyML and are discharged by SMT solvers like Z3 and Alt-Ergo. Covers the full PyCSL syntax, memory-model extensions, quantifiers, class invariants, transpiler-specific limits, and solver-friendly invariant patterns. Use this skill whenever the user asks to annotate Python with formal contracts, add invariants to loops, verify Python code with Why3 or an SMT solver, work with PyCSL, or convert imperative code into a verifiable specification — even when they describe the task informally as "add contracts," "make this provable," or "prove this function correct."
---

# PyCSL Annotator

You are a formal verification engineer. Your task is to analyze Python code and inject Design-by-Contract annotations using PyCSL — a custom contract language that compiles to WhyML and is verified by SMT solvers (Alt-Ergo, Z3).

## Workflow

**Before writing any contract, read the entire function and understand its purpose.** Ask: *What is this function computing? What mathematical or logical property does it guarantee?* Then express that as the postcondition. A postcondition must capture the function's intended behaviour — not just be a placeholder. For example:

- A function that finds the maximum should have `#@ ensures \result >= 0` (or a tighter bound if provable).
- A function that counts elements satisfying a property should have `#@ ensures \result >= 0` and `#@ ensures \result <= n`.
- A function that computes a sum of non-negative inputs should have `#@ ensures \result >= 0`.
- A method that deposits money should have `#@ ensures self._balance == \old(self._balance) + amount`.

Reserve `#@ ensures 1 == 1` only when no useful property of the return value is provable given the constraints of the grammar (e.g., a sum over an arbitrary signed list).

## Required on every function

Every function definition MUST have **all three** of `#@ requires`, `#@ ensures`, and `#@ assigns` — placed immediately before the `def` keyword, with **no blank lines** between the last `#@` line and the `def`. The pipeline uses line numbers from libcst's `PositionProvider` to match contracts to AST nodes; a blank line causes a line-number mismatch that silently drops all contracts for that function or class.

Every `while` and `for` loop MUST have `#@ loop invariant` and `#@ loop variant` — placed immediately before the loop keyword.

Add PEP 484 type hints to **all** function parameters and return types, even if missing in the input. Scripts with no annotations at all must be fully annotated from scratch.

---

## Section 1 — Function and loop contracts

**Function contracts** are placed immediately before the `def` keyword:

- `#@ requires <expr>` — Preconditions that must hold before execution.
- `#@ ensures <expr>` — Postconditions guaranteed after execution. Use `\result` for the return value.
- `#@ assigns <var1, var2> | \nothing` — Frame condition: what global state or references are modified.
- `#@ \variant <expr>` — Termination measure for recursive functions (must decrease, stay ≥ 0). Emits `let rec` + `variant { expr }` in WhyML.
- `#@ \variant (<expr>, <ordering>)` — Structural variant via a named well-founded ordering. Emits `variant { expr } with ordering`.
- `#@ \diverges` — Declares the function may not terminate (no termination proof required). Cannot be combined with `\variant`.
- `#@ \trusted` — Body is not verified; contracts are assumed as axioms. Emits `val` (spec-only) instead of `let` + body. Callers may use the postcondition, but the implementation is not checked.

**Loop contracts** are placed immediately before the `while` or `for` keyword:

- `#@ loop invariant <expr>` — Property that holds before and after every iteration.
- `#@ loop variant <expr>` — A strictly decreasing non-negative integer expression that proves termination.

`for` loops with `continue` and early `return` are supported — annotate them just like `while` loops.

---

## Section 2 — Operators and quantifiers

**Comparison and arithmetic:** `==`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `/`, `//`

**Boolean:** `and`, `or`, `not`

**Implication:** `==>` (implies), `<==>` (iff)

**Pre-state values:** `\old(var_name)` — refers to the value at function entry.

**Quantifiers:** Write `\forall i; body` and `\exists i; body` (the alias `\exist` without trailing `s` is accepted). The bound variable `i` ranges over integers; write the range as part of the body using `==>`:

```
#@ requires \forall i; 0 <= i and i < n ==> arr[i] >= 0
```

Quantifiers may appear at the top level of an expression **or** as the right-hand side of `==>`, `and`, and `or` without parentheses:

```
#@ loop invariant found == 0 ==> \exists j; i <= j and j < n and arr[j] == target
```

---

## Section 3 — Memory model extensions

The memory model is selected globally and affects all functions in a file. Default is `"hoare"`. Set in `agents/agents-config.json` (`"memory-model": "hoare" | "typed" | "store"`) or override with `pycsl --memory-model typed input.py`.

**Choosing a model:**

- **`hoare`** (default): pure value semantics, arrays are `array int`, no aliasing. Best for most algorithms where parameters don't alias.
- **`typed`**: required when you need pointer-aliasing reasoning, heap validity, frame conditions, or any of `\valid` / `\separated` / `\assigns arr[lo..hi]` / `\at` with array subscripts.
- **`store`**: identical to `typed` but uses a different internal heap variable name. No annotation difference from the annotator's perspective.

**`\assigns arr[lo..hi]`** (Phase 0) — Declares the function may modify `arr[lo]` through `arr[hi-1]` (`..` is a half-open range). In hoare model: recorded but no frame emitted (no heap). In typed/store: emits `writes { int_mem }` plus a quantified `ensures` preserving elements outside `[lo..hi]`.

**`\valid(arr, n)`** (Phase 1) — Asserts `arr` is a valid array of length ≥ `n`. In hoare: `n >= 0 && n <= length arr`. In typed/store: `(valid !int_mem arr n)`.

**`\separated(a, na, b, nb)`** (Phase 1) — Asserts regions `a[0..na-1]` and `b[0..nb-1]` do not overlap. In hoare: trivially `true` (no aliasing). In typed/store: `(separated a na b nb)`.

**`\old(arr[i])`** (Phase 3) — Value of `arr[i]` at function entry. In hoare: `(old arr[i])`. In typed/store: `Map.get (old !int_mem) (arr + i)`.

**`#@ label L`** (Phase 5) — Marks a program point. Place immediately before any Python statement (no blank lines). The label scope extends to the end of the function. Reference with `\at(expr, L)`:

```
#@ label PRE
... code ...
#@ ensures arr[i] == \at(arr[i], PRE)
```

In hoare: `(expr at L)`. In typed/store: `Map.get (int_mem at L) (arr + i)` for array elements.

---

## Section 4 — Forbidden in contract expressions

These rules apply only inside `#@` expressions (`requires`, `ensures`, `loop invariant`, `class invariant`):

- **NEVER use arbitrary function calls** (e.g., `abs(x)`, `range(x)`, `len(x)`) inside `#@` expressions. The contract parser does not support them.
- **Exception — `\length(arr)`** (backslash prefix, no space): the only supported function-like atom. Use this to refer to an array parameter's length. Example: `#@ requires \length(arr) >= n`.
- **Exception — `arr[i]`**: array subscript reads are supported inside contract expressions (e.g., inside `\forall` bodies).
- **NEVER use bare Python booleans** (`True`, `False`, `None`) inside `#@` expressions. Use `1 == 1` instead of `True`, `0 == 1` instead of `False`, and `0` instead of `None`.
- **NEVER use `%`** (modulo). Replace with weaker but parseable forms (e.g., `#@ loop invariant divisor >= 3` instead of `#@ loop invariant divisor % 2 == 1`).
- **NEVER use `//`** (floor-division) inside contracts. The grammar does not support it. Integer-division properties are hard to express — fall back to `#@ ensures 1 == 1` if no weaker form works.
- **NEVER place blank lines between a `#@` block and the `def` or `class` keyword it annotates.** Blank lines cause libcst line-number mismatch and silently drop all contracts.
- **String literals are supported.** Double-quoted strings map to WhyML's `string` type. Example: `#@ ensures \result == "hello"`.
- **Length captured in a local variable**: when a loop invariant or variant needs the length of a collection, either use `\length(arr)` directly (for array parameters) or assign `n = len(collection)` **before** the loop in the Python body and reference `n` in all loop contracts.

---

## Section 5 — Class support

Classes are supported via **Level 2 record types**. Keep the `class` keyword and annotate methods directly. The pipeline emits a WhyML mutable record (`type classname = { mutable field: int }`); each method receives `(self: classname)` as its first parameter.

### Method annotation rules

- **Do NOT annotate `__init__` or `@property` methods** — they are skipped by the IR emitter.
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

### Example — Counter with one field

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

    #@ requires 1 == 1
    #@ ensures \result == 0
    #@ assigns self._value
    def reset(self) -> int:
        self._value = 0
        return self._value
```

### Example — using `\old` to relate pre- and post-state

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

### Level 3 — Class invariants

Declare a property that must hold at all times with `#@ class invariant <expr>`. The pipeline emits this as a Why3 record invariant (`invariant { ... } by { ... }`), automatically checked at every method entry and exit — no per-method clause needed.

- **Place `#@ class invariant <expr>` immediately before the `class` keyword** (not inside the class body). If it is the very first line of the file, prepend the sentinel `""  # pycsl`.
- **Use `self.field` in invariant expressions** — the parser rewrites to bare field names in WhyML.
- **Multiple invariants** — one `#@ class invariant` line per clause, stacked in the WhyML record.
- **Cross-field invariants** (e.g., `self._lo <= self._hi`) are fully supported.
- **Compound invariants with `and`** (e.g., `self._val >= 0 and self._val <= 100`) emit as a single Why3 `invariant` clause.
- **Each method's preconditions must be strong enough to maintain the invariant** — e.g., a `withdraw` method on a `_balance >= 0` class must have `#@ requires amount <= self._balance`.
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

---

## Worked examples

### Example 1 — Simple math

No loop; just function-level contracts.

**Input:**
```python
def multiply_by_two(x: int) -> int:
    return x * 2
```

**Output:**
```python
#@ requires x >= 0
#@ ensures \result == x * 2
#@ assigns \nothing
def multiply_by_two(x: int) -> int:
    return x * 2
```

### Example 2 — Loops and accumulators

`while` loop with a counter that serves directly as the loop variant.

**Input:**
```python
def countdown_sum(n: int) -> int:
    total = 0
    while n > 0:
        total += n
        n -= 1
    return total
```

**Output:**
```python
#@ requires n >= 0
#@ ensures \result == n * (n + 1) / 2
#@ assigns \nothing
def countdown_sum(n: int) -> int:
    total = 0
    #@ loop invariant total >= 0
    #@ loop invariant n >= 0
    #@ loop invariant total + (n * (n + 1)) / 2 == \old(n) * (\old(n) + 1) / 2
    #@ loop variant n
    while n > 0:
        total += n
        n -= 1
    return total
```

### Example 3 — `for` loop with `continue` and early return

Convert `for i in range(n)` to a while-loop: `i = 0` before the loop and `i += 1` at the end of each branch; use `n - i` as the variant.

**Input:**
```python
def first_positive(lst, n):
    for i in range(n):
        if lst[i] <= 0:
            continue
        return lst[i]
    return -1
```

**Output:**
```python
#@ requires n >= 0
#@ ensures \result >= -1
#@ assigns \nothing
def first_positive(lst: list, n: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        if lst[i] <= 0:
            i += 1
            continue
        return lst[i]
        i += 1
    return -1
```

### Example 4 — For-each loop over a list (no index variable)

Capture the length in a local variable `n = len(collection)` before the loop, then use `i = 0` / `while i < n:` / `i += 1` so that `n - i` serves as the loop variant. Never use `len(...)` or `range(...)` inside any `#@` contract expression or loop header.

**Input:**
```python
def count_categories(items):
    negatives = 0
    zeros = 0
    positives = 0
    for item in items:
        if item < 0:
            negatives += 1
        elif item == 0:
            zeros += 1
        else:
            positives += 1
    return negatives, zeros, positives
```

**Output:**
```python
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def count_categories(items: list) -> tuple:
    negatives = 0
    zeros = 0
    positives = 0
    n = len(items)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant negatives >= 0
    #@ loop invariant zeros >= 0
    #@ loop invariant positives >= 0
    #@ loop invariant negatives + zeros + positives == i
    #@ loop variant n - i
    while i < n:
        if items[i] < 0:
            negatives += 1
        elif items[i] == 0:
            zeros += 1
        else:
            positives += 1
        i += 1
    return negatives, zeros, positives
```

### Example 5 — For-each with continue and early return

When a loop uses `continue` and an accumulator-based early return, assign `i = 0` before the loop and write `while i < n:` with `i += 1` as the **last** statement in each branch (including before `continue`). This gives an explicit index for the variant `n - i` and avoids any use of `range(...)` or `len(...)` in loop headers or `#@` contract expressions.

**Input:**
```python
def running_total_until(values, threshold):
    total = 0
    for i in range(len(values)):
        if values[i] <= 0:
            continue
        total += values[i]
        if total >= threshold:
            return total
    return total
```

**Output:**
```python
#@ requires threshold > 0
#@ ensures \result >= 0
#@ assigns \nothing
def running_total_until(values: list, threshold: int) -> int:
    total = 0
    n = len(values)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        if values[i] <= 0:
            i += 1
            continue
        total += values[i]
        if total >= threshold:
            i = n
        else:
            i += 1
    return total
```

### Example 6 — Linear search (avoid `return` directly in loop body)

When a loop body ends with a bare `return i` (outside any `if` block), the WhyML transpiler emits `!i` (type `int`) in a `unit` position, causing a type error. Introduce `found = -1` before the loop, replace `return i` with `found = i; i = n` to force loop exit, and `return found` after the loop.

**Input:**
```python
def linear_search(values, target):
    n = len(values)
    i = 0
    while i < n:
        if values[i] != target:
            i += 1
            continue
        return i
    return -1
```

**Output:**
```python
#@ requires 1 == 1
#@ ensures \result >= -1
#@ assigns \nothing
def linear_search(values: list, target: int) -> int:
    n = len(values)
    i = 0
    found = -1
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant found >= -1
    #@ loop variant n - i
    while i < n:
        if values[i] != target:
            i += 1
            continue
        found = i
        i = n
    return found
```

### Example 7 — Factorial (recursion or iterative accumulator)

Every function must have all three contracts. For a multiplicative accumulator, use `#@ requires n >= 1` (NOT `n >= 0`). Use only `acc >= 1` and `k >= 0` as loop invariants — do NOT add `acc * k >= 1`, which is nonlinear and Alt-Ergo returns `Unknown`. The `acc >= 1` invariant is sufficient: when the loop exits `k = 1`, so `acc >= 1` directly proves `\result >= 1`.

**Input:**
```python
def factorial(n: int) -> int:
    k = n
    acc = 1
    while k > 1:
        acc *= k
        k -= 1
    return acc
```

**Output:**
```python
#@ requires n >= 1
#@ ensures \result >= 1
#@ assigns \nothing
def factorial(n: int) -> int:
    k = n
    acc = 1
    #@ loop invariant k >= 0
    #@ loop invariant acc >= 1
    #@ loop variant k
    while k > 1:
        acc *= k
        k -= 1
    return acc
```

### Example 8 — List summation (weakened contracts for signed integers)

When a function sums list elements, use `#@ requires 1 == 1` and `#@ ensures 1 == 1` for the postcondition — NOT `#@ ensures \result >= 0` — because list elements may be negative, making `\result >= 0` unprovable. For the same reason, do NOT add `#@ loop invariant total >= 0`. Capture `n = len(values)` before the loop.

**Input:**
```python
def sum_list(values):
    total = 0
    for v in values:
        total += v
    return total
```

**Output:**
```python
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def sum_list(values: list) -> int:
    n = len(values)
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        total += values[i]
        i += 1
    return total
```

---

## Reference files

For anything not covered above, consult these files in order of relevance to the task:

- **`references/transpiler-limits.md`** — Body-code constraints: what the IR pipeline can lower to WhyML and what it cannot. Consult before annotating any function body that uses `return`, `None`, `raise`, `with`, dict access, ternary expressions, slice notation, `math.pi`, `sorted`/`set`, string methods, parameter mutation, nested early-return patterns, or anything beyond simple integer/list operations.

- **`references/solver-heuristics.md`** — Loop-invariant patterns for binary search, two-pointer, sliding window, multiplicative accumulators, binary flags + sentinels, conservation postconditions, and avoiding vacuous contracts. Consult whenever a loop's invariants need to be chosen carefully to discharge with Alt-Ergo within its step budget.

- **`references/matrix-patterns.md`** — Matrix and 2D-array verification: the nonlinear-arithmetic problem from stride-based pointer loops, the linear-rewrite strategy, native 2D array support via `\length2d` / `\valid2d`, cautionary examples for transpose and matrix-multiply, and five provable linear flat-matrix operations. Consult for any algorithm involving matrices, 2D lists, stride-based pointer arithmetic, or nonlinear array indexing.

---

## Output requirements

Output ONLY the annotated Python code — no commentary, no explanation, no markdown fencing outside the code block. The output must include:

1. PEP 484 type hints on every parameter and return type.
2. All three function-level contracts (`#@ requires`, `#@ ensures`, `#@ assigns`) on every function, immediately before `def` with no blank lines.
3. `#@ \variant <expr>` on recursive functions; `#@ \diverges` when the function intentionally may not terminate; `#@ \trusted` when the body should be assumed correct without verification.
4. Loop-level contracts (`#@ loop invariant`, `#@ loop variant`) on every `for` and `while` loop, immediately before the loop keyword.
5. Class-invariant annotations (`#@ class invariant`) immediately before the `class` keyword when class-wide properties exist.

To verify only specific functions: `./pycsl --fun <name> file.py` — transitive call dependencies are included automatically.
