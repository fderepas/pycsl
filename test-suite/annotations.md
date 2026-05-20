# PyCSL Annotation Reference

This document normalizes the complete PyCSL contract annotation language
as implemented in the codebase (Module2_Parser EBNF grammar + Module5/6
transpilation). It is the authoritative source for writing test cases.

---

## 1. Annotation Syntax

All annotations are single-line Python comments starting with `#@`:

```python
#@ <directive> <expression>
```

Annotations must appear on the **leading lines** immediately before the
Python construct they annotate (function, class, loop, or statement).

---

## 2. Directives

### 2.1 Function/Method Contracts

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Precondition | `#@ requires <expr>` | Function/method | Must hold at entry |
| 2 | Postcondition | `#@ ensures <expr>` | Function/method | Must hold at exit |
| 3 | Frame condition | `#@ assigns <targets>` | Function/method | Only listed targets may be mutated |
| 4 | Function variant | `#@ \variant <expr>` | Function/method | Termination measure for recursive functions (must decrease, stay ≥ 0) |
| 5 | Structural variant | `#@ \variant (<expr>, <ordering>)` | Function/method | Termination via well-founded ordering |
| 6 | Diverges | `#@ \diverges` | Function/method | Function may not terminate (no termination proof required) |
| 7 | Trusted | `#@ \trusted` | Function/method | Body is not verified; contracts are assumed (axiom) |
| 8 | Bounded integers | `#@ assumes bounded_int(N)` | Function/method | Use `mach.int.IntN` types; auto-generates overflow VCs on `+`, `-`, `*` |
| 9 | Raises | `#@ raises ExcType when <cond>` | Function/method | Exceptional postcondition: exception raised only when `cond` holds |
| 10 | Thread entry | `#@ thread_entry` | Function/method | Marks function as a concurrent thread entry point; used with `--memory-model concurrent` |

Multiple `requires`/`ensures` lines are conjuncted (all must hold).

### 2.2 Loop Contracts

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Loop invariant | `#@ loop invariant <expr>` | `while`/`for` | Inductive property preserved each iteration |
| 2 | Loop variant | `#@ loop variant <expr>` | `while`/`for` | Termination measure (must decrease, stay ≥ 0) |

### 2.3 Class Contracts

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Class invariant | `#@ class invariant <expr>` | `class` | Must hold at every method boundary |

Placed on leading lines **before** the `class` keyword.

### 2.4 Program Point Annotations

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Label | `#@ label <NAME>` | Statement | Marks a program point for `\at` references |
| 2 | Ghost assign | `#@ ghost <name> = <expr>` | Statement | Declare or assign a ghost variable (first occurrence declares) |
| 3 | Ghost augmented assign | `#@ ghost <name> += <expr>` | Statement | Augmented assignment to ghost variable (`+=`, `-=`, `*=`) |
| 4 | Critical section | `#@ critical <mutex>` | `with` statement | Declares the `with lock:` block as a critical section for `<mutex>`; triggers havoc+assume+assert in WhyML |
| 5 | Acquires | `#@ acquires <mutex>` | `with` statement | Explicit mutex acquire annotation (equivalent to `critical`; use when naming the acquire point explicitly) |
| 6 | Releases | `#@ releases <mutex>` | `with` statement | Explicit mutex release annotation (marks the release point; informational in current WhyML output) |

Ghost variables exist only in the verification model (erased at extraction).
They can be referenced in `loop invariant`, `requires`, `ensures`, and `\variant` expressions.
The `#@ ghost` directive must appear on a leading line before a Python statement.

---

## 3. Expression Language

### 3.1 Atoms

| # | Syntax | AST Node | Meaning |
|---|---|---|---|
| 1 | `42`, `-1`, `0` | `Number` | Integer literal |
| 2 | `x`, `n`, `total` | `Var` | Variable reference |
| 3 | `self.field` | `FieldAccess` | Class field access |
| 4 | `arr[i]` | `SubscriptAccess` | Array element access |
| 5 | `\result` | `Result` | Return value (only in `ensures`) |
| 6 | `\old(<expr>)` | `Old` | Value of expression at function entry |
| 7 | `\at(<expr>, L)` | `At` | Value of expression at label `L` |
| 8 | `\length(arr)` | `ArrayLength` | Length of array `arr` |
| 9 | `\valid(arr, n)` | `Valid` | `arr[0..n)` is allocated |
| 10 | `\separated(a, na, b, nb)` | `Separated` | Regions `a[0..na)` and `b[0..nb)` don't overlap |
| 11 | `\length2d(a, m, n)` | `Length2D` | `a` has `m` rows each of length `n` |
| 12 | `\valid2d(a, i, j)` | `Valid2D` | `(i,j)` is a valid 2D index |
| 13 | `\nothing` | `Nothing` | Empty assigns target (pure function) |
| 14 | `"hello"` | `StringLiteral` | String literal (uses Why3 `string.String`) |
| 15 | `\is_sorted(arr, lo, hi)` | `IsSorted` | `arr[lo..hi)` is sorted ascending (pairwise adjacent) |
| 16 | `\sum(arr, lo, hi)` | `Sum` | Sum of `arr[lo..hi)` elements |
| 17 | `f(x, y)` | `CallExpr` | Pure function call in contract (see 4.1) |
| 18 | `True`, `False` | `CSLBool` | Boolean literal (`true` / `false` in WhyML) |
| 19 | `None` | `CSLNone` | None literal (maps to `0` in WhyML) |
| 20 | `arr[lo:hi]` | `CSLSlice` | Array slice (abstract `array_slice` function in WhyML) |

### 3.2 Operators (by precedence, lowest first)

| # | Precedence | Operators | AST | Python equivalent |
|---|---|---|---|---|
| 1 | 1 (lowest) | `\forall var; body`, `\exists var; body` | `Forall`, `Exists` | Quantifiers (no direct equivalent) |
| 2 | 2 | `==>` (implies), `<==>` (iff) | `BinOp` | `not a or b`, `a == b` |
| 3 | 3 | `or` | `BinOp` | `or` |
| 4 | 4 | `and` | `BinOp` | `and` |
| 5 | 5 | `==`, `!=` | `BinOp` | `==`, `!=` |
| 6 | 6 | `<`, `>`, `<=`, `>=` | `BinOp` | same |
| 6b | 6.5 | `in`, `not in` | `CSLIn`, `CSLNotIn` | membership test (desugared to `∃` quantifier) |
| 7 | 7 | `+`, `-` | `BinOp` | same |
| 8 | 8 | `*`, `//`, `/`, `%` | `BinOp` | `//` and `/` → WhyML `div`; `%` → WhyML `mod` |
| 9 | 9 (highest) | `not`, unary `-`, unary `+` | `UnaryOp` | same |

**Note:** `/` in contracts maps to WhyML `div` (Euclidean integer division),
not Python's float division.

**Division-by-zero guards:** When `//` or `%` appear in **program code**
(not in contracts), PyCSL wraps them in helper functions `pycsl_div` /
`pycsl_mod` that carry a `requires { y <> 0 }` precondition. This
generates an automatic division-by-zero proof obligation at each call
site. In contracts (requires/ensures/invariants), bare `div` / `mod`
are used (logic context, no VC needed).

### 3.3 Quantifiers

```python
#@ requires \forall i; 0 <= i and i < n ==> arr[i] >= 0
#@ ensures \exists j; 0 <= j and j < n and arr[j] == target
```

- Bound variable is always typed `int` in WhyML output.
- Body extends greedily to the end of the expression.
- Quantifiers can appear at top level or as RHS of `==>`, `and`, `or`.
- `\exist` (singular) is an accepted alias for `\exists`.
- Quantifiers may be nested.

### 3.4 Assigns Targets

| # | Syntax | Meaning |
|---|---|---|
| 1 | `\nothing` | No mutation allowed |
| 2 | `x` | Variable `x` may be mutated |
| 3 | `x, y` | Variables `x` and `y` may be mutated |
| 4 | `self.field` | Field may be mutated |
| 5 | `arr[lo..hi]` | Array region `arr[lo..hi)` may be mutated |

```python
#@ assigns \nothing
#@ assigns self._value
#@ assigns arr[0..n]
#@ assigns arr[0..n], brr[0..m]
```

---

## 4. NOT Supported in Contracts

The following Python constructs are **not valid** in `#@` expressions:

| # | Construct | Reason |
|---|---|---|
| 1 | `len(...)` | Use `\length(arr)` instead |
| 2 | ~~Function calls~~ | **Now supported** for pure functions (see Section 4.1) |
| 3 | List comprehensions | Not in grammar |
| 4 | `if`/`else` ternary | Not in grammar |

**Formerly unsupported, now supported:**
- `//` (floor division) and `%` (modulo) — added to grammar (see §3.2 row 8)
- `True` / `False` / `None` — added as atoms (see §3.1 rows 18–19)
- `in`, `not in` — added as membership operators (see §3.2 row 6b)

### 4.1 Pure Functions in Contracts

Functions annotated with `#@ assigns \nothing` (pure, side-effect-free) can
be called inside `#@ requires`, `#@ ensures`, and `#@ loop invariant`
expressions. The function must:

1. Have `#@ assigns \nothing` (no side effects)
2. Not be annotated with `#@ \diverges`
3. Have no mutable local variables (loop-free body: if/else + recursion + arithmetic)
4. Recursive functions must have a `#@ \variant` (termination proof)

Pure functions are emitted as WhyML `let function` (or `let rec function`),
making them usable in logical specifications.

```python
#@ ensures \result >= 0
#@ assigns \nothing
def abs_val(x: int) -> int:
    if x >= 0:
        return x
    return -x

#@ ensures \result == abs_val(a) + abs_val(b)
#@ assigns \nothing
def sum_abs(a: int, b: int) -> int:
    return abs_val(a) + abs_val(b)
```

Recursive pure functions:

```python
#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
#@ \variant n
def sum_to(n: int) -> int:
    if n == 0:
        return 0
    return n + sum_to(n - 1)

#@ requires n >= 0
#@ ensures \result == sum_to(n) * 2
#@ assigns \nothing
def double_sum(n: int) -> int:
    return sum_to(n) + sum_to(n)
```

---

## 5. Memory Models

PyCSL supports three memory models, selected via `--memory-model`:

| # | Model | Flag | Array semantics | Aliasing |
|---|---|---|---|---|
| 1 | Hoare (default) | `--memory-model hoare` | Value-typed (`array int`) | Not modeled (independent) |
| 2 | Typed | `--memory-model typed` | Heap-based (`map loc int`) | `\separated` needed |
| 3 | Store | `--memory-model store` | Single untyped heap | `\separated` needed |
| 4 | Concurrent | `--memory-model concurrent` | Value-typed shared vars + mutex invariants | Reduces to sequential WP via monitor-invariant pattern; shared vars declared with `#@ shared` |

### Hoare model
Arrays are independent value-typed entities. `arr[i] <- v` mutates only `arr`.
No aliasing is possible. `\separated` is trivially true.

### Typed model
Arrays are references (locations) into a global typed heap `int_mem : ref (map loc int)`.
`\valid(arr, n)` asserts the region is allocated.
`\separated(a, na, b, nb)` asserts disjoint regions.

### Store model
Single global untyped heap `store : ref (map loc int)`.
Same predicates as typed model but with a unified store.

### Concurrent model
Multithreaded programs using `threading.Lock` / `threading.RLock`. The
monitor-invariant pattern reduces concurrent verification to sequential WP proofs:

- Shared variables are emitted as module-level `val x : ref int` in WhyML.
- Critical section **entry**: havoc the shared variable, then `assume { mutex_inv }`.
- Critical section **exit**: `assert { mutex_inv }`.
- Thread entry functions containing `while True:` receive `diverges` in the WhyML spec.
- `lock_order` is required whenever any function acquires multiple mutexes simultaneously
  (nested `with` blocks holding two or more locks). It prevents deadlock by enforcing a
  total acquisition order.

Module-level declarations (`#@ shared`, `#@ mutex_invariant`, `#@ lock_order`) must be
placed before any function definition and attached to an anchor statement (`_ = 0  # anchor`).

---

## 6. Class Contract Patterns

### Level 2 — Mutable record types

```python
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

### Level 3 — Class invariants

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

The `""  # pycsl` marker on the line before `#@ class invariant` is
required by the ingestor for class-level annotations.

### Cross-field invariants

A class invariant may reference multiple fields. Mutating methods must
have `requires` clauses strong enough to *guard* the invariant — i.e.,
ensure that the invariant still holds after the method body executes.

```python
""  # pycsl
#@ class invariant self._lo <= self._hi
class Interval:
    def __init__(self):
        self._lo = 0
        self._hi = 0

    #@ requires lo <= self._hi
    #@ ensures self._lo == lo
    #@ assigns self._lo
    def set_lo(self, lo: int) -> None:
        self._lo = lo

    #@ requires hi >= self._lo
    #@ ensures self._hi == hi
    #@ assigns self._hi
    def set_hi(self, hi: int) -> None:
        self._hi = hi
```

The `requires lo <= self._hi` on `set_lo` *guards* the invariant: it
ensures `self._lo <= self._hi` is preserved after `self._lo = lo`.

### Multiple stacked invariants

A class may declare multiple `#@ class invariant` lines. Each is
checked independently at every method boundary.

```python
""  # pycsl
#@ class invariant self._size >= 0
#@ class invariant self._capacity > 0
#@ class invariant self._size <= self._capacity
class Buffer:
    def __init__(self):
        self._size = 0
        self._capacity = 10

    #@ requires self._size < self._capacity
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def push(self) -> None:
        self._size = self._size + 1
```

### Invariant-guarding preconditions

For a method that mutates a field appearing in the class invariant,
the `requires` clause must be strong enough that the invariant is
maintainable. This is the key design principle (inspired by Creusot
from Inria): WhyML record invariants are checked at construction and
method exit; the *precondition* must guarantee the method can
preserve them.

```python
""  # pycsl
#@ class invariant self._balance >= 0
class BankAccount:
    def __init__(self):
        self._balance = 0

    #@ requires amount >= 0
    #@ ensures self._balance == \old(self._balance) + amount
    #@ assigns self._balance
    def deposit(self, amount: int) -> int:
        self._balance = self._balance + amount
        return self._balance

    #@ requires amount >= 0
    #@ requires amount <= self._balance
    #@ ensures self._balance == \old(self._balance) - amount
    #@ assigns self._balance
    def withdraw(self, amount: int) -> int:
        self._balance = self._balance - amount
        return self._balance
```

`requires amount <= self._balance` on `withdraw` is the **guard**
that makes the invariant `self._balance >= 0` provable after the
subtraction.

### Invariant witness

The `by { ... }` witness in WhyML is auto-generated from `__init__`
literal assignments (e.g., `self._value = 0` → `_value = 0`). If the
auto-generated witness does not satisfy the invariant, the transpiler
tries fallback values (0, 1, -1) and picks one that works.

---

## 7. `\old` and `\at` Expressions

### `\old(expr)`
References the value of `expr` at function entry.

```python
#@ ensures arr[0] == \old(arr[1])
#@ ensures self._value == \old(self._value) + amount
```

### `\at(expr, L)`
References the value of `expr` at program point labeled `L`.

```python
#@ label PRE
arr[0] = arr[0] + 1
# ... later in ensures:
#@ ensures arr[0] == \at(arr[0], PRE) + 1
```

---

## 8. Complete Grammar (EBNF)

Extracted from `Module2_Parser.py` — this is the canonical grammar:

```ebnf
?start: contract

?contract: precondition | postcondition | assigns
         | loop_invariant | loop_variant | class_invariant | label_decl
         | function_variant | function_variant_structural
         | diverges_decl | trusted_decl

precondition:    "requires" expr
postcondition:   "ensures" expr
assigns:         "assigns" assigns_target
loop_invariant:  "loop" "invariant" expr
loop_variant:    "loop" "variant" expr
class_invariant: "class" "invariant" expr
label_decl:      "label" CNAME
function_variant:            "\variant" expr
function_variant_structural: "\variant" "(" expr "," CNAME ")"
diverges_decl:   "\diverges"
trusted_decl:    "\trusted"

?assigns_target: assigns_region_list | expr_list | "\nothing"

assigns_region_list: assigns_region ("," assigns_region)*
assigns_region:      CNAME "[" expr ".." expr "]"

?expr: implication
     | "\forall" CNAME ";" expr
     | "\exists" CNAME ";" expr
     | "\exist"  CNAME ";" expr

?implication: logical_or | implication IMPL_OP impl_rhs
?impl_rhs:   logical_or | "\forall"/"\exists"/"\exist" CNAME ";" expr

?logical_or:  logical_and | logical_or OR_OP or_rhs
?or_rhs:      logical_and | "\forall"/"\exists"/"\exist" CNAME ";" expr

?logical_and: equality | logical_and AND_OP and_rhs
?and_rhs:     equality | "\forall"/"\exists"/"\exist" CNAME ";" expr

?equality:    comparison | equality EQ_OP comparison
?comparison:  term | comparison COMP_OP term
?term:        factor | term ADD_OP factor
?factor:      unary | factor MUL_OP unary

?unary: UNARY_OP unary | atom

?atom: NUMBER | "self" "." CNAME | CNAME "[" expr "]" | CNAME
     | "\result" | "\old" "(" expr ")" | "\length" "(" CNAME ")"
     | "\valid" "(" CNAME "," expr ")"
     | "\separated" "(" CNAME "," expr "," CNAME "," expr ")"
     | "\at" "(" expr "," CNAME ")"
     | "\length2d" "(" CNAME "," expr "," expr ")"
     | "\valid2d" "(" CNAME "," expr "," expr ")"
     | "\is_sorted" "(" CNAME "," expr "," expr ")"
     | "\sum" "(" CNAME "," expr "," expr ")"
     | "(" expr ")"

IMPL_OP:  "==>" | "<==>"
OR_OP:    "or"
AND_OP:   "and"
EQ_OP:    "==" | "!="
COMP_OP:  ">" | "<" | ">=" | "<="
ADD_OP:   "+" | "-"
MUL_OP:   "*" | "/"
UNARY_OP: "not" | "-" | "+"
RANGE_OP: ".."

# Concurrent model annotations (--memory-model concurrent)
# These extend the ?contract rule:
shared_decl:          "shared" CNAME "protected_by" CNAME
                    | "shared" CNAME
mutex_invariant_decl: "mutex_invariant" CNAME ":" expr
lock_order_decl:      "lock_order" CNAME ("," CNAME)+
thread_entry_decl:    "thread_entry"
acquires_decl:        "acquires" CNAME
releases_decl:        "releases" CNAME
critical_decl:        "critical" CNAME
```

---

## 9. Pipeline Invocation

```bash
# Basic verification (default Hoare model, Alt-Ergo + Z3)
./pycsl test.py

# With specific memory model
./pycsl test.py --memory-model typed

# Keep generated WhyML for debugging
./pycsl test.py --keep-mlw

# Specific prover
./pycsl test.py -p "Alt-Ergo,2.6.2,"

# Verify only a specific function (and its transitive call-dependencies)
./pycsl test.py --fun foobar

# Verify multiple specific functions
./pycsl test.py --fun foobar --fun helper
```

### Exit codes

| # | Code | Meaning |
|---|---|---|
| 1 | `0` | All goals verified (Valid) |
| 2 | `1` | Verification failed, incomplete, or pipeline error |

### Multi-file imports

PyCSL automatically resolves `from ... import ...` statements. When the
imported module is a local `.py` file, its functions are extracted as trusted
stubs (contracts assumed, bodies not verified). The main file's functions
are then verified against those contracts.

```python
# dir2/file2.py
from dir1.file1 import double_int   # auto-resolved if dir1/file1.py exists

#@ ensures \result == 2 * x
def foobar(x: int) -> int:
    return double_int(x)             # proven using double_int's contract
```

```bash
./pycsl dir2/file2.py   # resolves dir1/file1.py, imports double_int as trusted
```

Supported import forms:
- `from mod import name`
- `from mod import a, b` (multiple names)
- `from mod import name as alias`
- `from mod import *` (wildcard — imports called functions, respects `__all__`)
- `import mod as alias` (calls via `alias.func(x)`)
- `import mod` (calls via `mod.func(x)` or `mod.sub.func(x)`)
- Relative imports (`from .mod import name`)

External modules (stdlib, third-party) that cannot be resolved to a local file
are silently skipped.

### Recursive import resolution (`--deep`)

By default, only the main file's direct imports are resolved. With `--deep`,
PyCSL recursively resolves imports in dependency files (transitive chain).
Circular imports are detected and skipped with a warning.

```bash
# Resolve transitive import chains: A→B→C
./pycsl --deep file.py
```

### Output parsing

With `split_vc`, each function produces multiple sub-goals. Output lines
contain per-goal results:

```
FunctionName VCkind : Valid (0.01s, 42 steps)
FunctionName VCkind : Unknown (timeout)
```

A function is fully verified only when **all** its sub-goals are `Valid`.

---

## 7. Supported Body Constructs

The following Python constructs in function bodies are transpiled to WhyML:

### 7.1 Assert Statement

```python
assert x > 0, "x must be positive"
```

Transpiles to:

```whyml
check { [@expl:x must be positive] (x > 0) }
```

The message string (if present) becomes a WhyML `@expl:` attribute.
If no message, `"assertion"` is used as default.

### 7.2 Tuple Unpacking

```python
a, b = divmod(x, y)
```

Transpiles to a `let` destructuring followed by ref assignments.

### 7.3 Walrus Operator (`:=`)

```python
y = (x := n + 1)
```

The named expression `(x := expr)` both assigns to `x` and evaluates to
the assigned value. In WhyML, this is emitted as a `begin ... end` block
with a side-effectful assignment.

### 7.4 Match Statement

```python
match status:
    case 200:
        result = "ok"
    case 404:
        result = "not found"
    case _:
        result = "unknown"
```

Lowered to an if/elif chain comparing the subject against each pattern value.
Wildcard (`_`) becomes the final `else` branch.

### 7.5 Lambda

```python
f = lambda x, y: x + y
```

Transpiles to an anonymous function:

```whyml
fun (x: int) (y: int) -> (x + y)
```

---

## 10. Concurrent Model Annotations

Used with `--memory-model concurrent`. Placed on **leading lines** before the
module body (module-level declarations) or before `with` statements (critical
section annotations).

### 10.1 Module-Level Declarations

| # | Directive | Syntax | Semantics |
|---|---|---|---|
| 1 | Protected shared variable | `#@ shared <var> protected_by <mutex>` | `<var>` is a shared global; every read/write must be inside a `#@ critical <mutex>` block (Module4 enforces this) |
| 2 | Unprotected shared variable | `#@ shared <var>` | `<var>` is shared but unprotected; ConcurrencyChecker warns, Module4 is lenient |
| 3 | Mutex invariant | `#@ mutex_invariant <mutex>: <expr>` | `<expr>` must hold whenever `<mutex>` is free; checked at critical section exit (`assert { mutex_inv }`) |
| 4 | Lock order | `#@ lock_order <m1>, <m2>, ...` | Total order on mutex acquisition; required when any function holds one mutex while acquiring another |

Module-level `#@ shared` and `#@ mutex_invariant` declarations must be placed
before any function definition. Use `_ = 0  # anchor` as the target Python
statement for leading-line module annotations.

### 10.2 Placement and Rules

- Unprotected writes/reads of a `#@ shared protected_by` variable outside a critical
  section raise `PyCSLSemanticError` (Module4).
- Nested acquisition of multiple mutexes requires `#@ lock_order` to prevent deadlock.
- `queue.Queue`, `threading.Lock`, `threading.RLock` are trusted thread-safe types and
  need no `#@ shared` annotation.
- A `#@ mutex_invariant` expression may only reference variables protected by that mutex.
- `#@ critical <mutex>` and `#@ acquires <mutex>` are equivalent in Module5/Module6:
  both generate a `CriticalSection` IR node that wraps the `with` body with
  havoc+assume/assert invariant pairs.
- `#@ releases <mutex>` is stored on the `with` node but does not currently generate
  extra WhyML. It is informational (documents the release point for manual protocols).

### 10.3 Minimal Example

```python
# pycsl-flags: --memory-model concurrent --no-proof
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 0
_ = 0  # anchor
import threading
lock_counter = threading.Lock()
counter = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        counter += 1
    return 0
```
