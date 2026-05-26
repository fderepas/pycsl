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
| 11 | Proof attribution | `#@ proof <rocq\|lean>: <qualname>` | Function/method | Informational. Records that the function's contract was derived from theorem `<qualname>` in the named formalism. Accepted and ignored by Why3 — emitted by `pycsl-bridge`, not by humans. May appear multiple times (one per source theorem). |
| 12 | Axiom from proof | `#@ axiom_from <rocq\|lean> <qualname>` | Module-level | Imports a Rocq or Lean theorem as a Why3 axiom in the preamble. When both `rocq` and `lean` directives name the same `pycsl_target`, the `proof2why3 cross-check` tool verifies their canonical forms agree before emission ("Rocq + Lean as Cross-Validated Spec Sources"). See §2.1.12 below. |

Multiple `requires`/`ensures` lines are conjuncted (all must hold).

#### §2.1.12 Axiom from Proof (`axiom_from`) — Rocq + Lean as Cross-Validated Spec Sources

```python
#@ axiom_from rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ axiom_from lean Pycsl.Reference.Gcd.gcd_divides_a
```

Imports a Rocq or Lean theorem as a **Why3 axiom** in the generated WhyML
preamble. Unlike `#@ proof` (§2.1.11, informational only), `#@ axiom_from`
has real semantic effect: Alt-Ergo/Z3 may use the imported axiom to
discharge obligations that SMT alone cannot handle.

**Cross-validation.** When both a `rocq` and a `lean` directive reference
the same `pycsl_target` name, the `proof2why3 cross-check` tool
extracts both theorem statements, converts them to a canonical IR form
(alpha-normalized, AC-flattened, `nat`/`Nat` → `int + ≥ 0`), and verifies
equality. This is the **"Rocq + Lean as Cross-Validated Spec Sources"**
pattern: two independent proof assistants must agree on the specification
before it enters the Why3 verification.

**Scope:** Module-level (placed before any function definition).

**WhyML emission:** `Module6_WhyMLTranspiler` calls `proof2why3 emit` for
each `axiom_from` directive, producing an `axiom pycsl_axiom_<target> : …`
block in the preamble.

**Cross-check statuses:**

| Status | Meaning |
|---|---|
| `reconciled` | Both Rocq and Lean present, canonical forms equal |
| `rocq-only` | Only Rocq statement found (warning emitted) |
| `lean-only` | Only Lean statement found (warning emitted) |
| `disagreement` | Both present but canonical forms differ (**pipeline halts**) |

**Worked example:** `test-suite/corpus/pycsl-reference/0342.py` (Euclidean
GCD) with proofs under `0342.proofs/{rocq,lean}/`.

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

---

## 11. Ghost Variable Types

Ghost variables are erased at extraction and live only in the verification model.
Use typed declarations to control the WhyML type of a ghost variable:

```python
#@ ghost <name> : <type> = <expr>
```

Untyped ghost declarations (`#@ ghost <name> = <expr>`) default to `int`.

> **Terminology**: For definitions of *ghost code*, *ghost state*, *witness*, *ghost lowering*,
> and related concepts, see [`docs/glossary/`](../docs/glossary/README.md).

### 11.1 Typed Ghost Declarations

| # | Type keyword | WhyML type | Initial value | Update syntax |
|---|---|---|---|---|
| 1 | `int` (default) | `ref int` | any int expr | `ghost x = e`, `ghost x += e` |
| 2 | `string` | `ref string` | `"..."` or `s ^ "..."` | `ghost s = s ^ "chunk"` |
| 3 | `array` | `array int` (not a ref) | `\copy(arr)` or `\make(n, v)` | `ghost snap[i] = e` |
| 4 | `ghost_dict` | `ref (map int (option int))` | `\empty_map` | `ghost d = \map_set(d, k, v)` |
| 5 | `ghost_list` | `ref (list int)` | `\nil` | `ghost l = \cons(x, l)` |
| 6 | `ghost_set` | `ref (map int bool)` | `\set_empty` | `ghost s = \set_add(s, e)` |
| 7 | `tuple2` | `ref (int, int)` | `\mktuple(a, b)` | `ghost p = \mktuple(a, b)` |
| 8 | `tuple3` | `ref (int, int, int)` | `\mktuple(a, b, c)` | `ghost t = \mktuple(a, b, c)` |
| 9 | `tuple4` | `ref (int, int, int, int)` | `\mktuple(a, b, c, d)` | `ghost q = \mktuple(a, b, c, d)` |

### 11.2 Ghost Expression Atoms

**Tuples:**
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\mktuple(e1, e2, ...)` | Construct a tuple (2–4 elements) |
| 2 | `\fst(t)` | First component of a tuple2 |
| 3 | `\snd(t)` | Second component of a tuple2 |
| 4 | `\proj(t, i)` | i-th component (i must be an integer literal) |

**Strings:**
| # | Syntax | Meaning |
|---|---|---|
| 1 | `s ^ t` | String concatenation (Why3 `concat s t` — not `String.(^)`) |
| 2 | `"literal"` | String literal |
| 3 | `\str_length(s)` | String length (`String.length !s`) |
| 4 | `\str_sub(s, lo, hi)` | Substring from `lo` to `hi` (`String.substring !s lo (hi-lo)`) |

**Ghost arrays** (hoare model only):
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\copy(arr)` | Snapshot of an existing array |
| 2 | `\make(n, v)` | Fresh array of length `n` filled with `v` |
| 3 | `ghost snap[i] = e` | In-place element update (`ghost_array_set`) |

**Ghost dicts** (backed by `map int (option int)`):
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\empty_map` | Empty map (all keys absent: `const (None: option int)`) |
| 2 | `\map_get(d, k)` | Get value for key k; returns 0 if absent (`match Map.get !d k with \| Some v -> v \| None -> 0 end`) |
| 3 | `\map_set(d, k, v)` | `Map.set !d k (Some v)` |
| 4 | `\map_eq(d1, d2)` | Extensional equality |
| 5 | `#@ ghost d += \mktuple(k, v)` | Shorthand for `Map.set !d k (Some v)` (augmented assign) |
| 6 | `\has_key(d, k)` | True iff key k is present (`Map.get !d k <> None`). Safe even when 0 is a valid stored value |
| 7 | `\map_remove(d, k)` | Remove key k (set to absent: `Map.set !d k None`) |

**Ghost lists** (backed by Why3 `list int`):
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\nil` | Empty list |
| 2 | `\cons(x, l)` | Prepend element |
| 3 | `\hd(l)` | Head element |
| 4 | `\tl(l)` | Tail |
| 5 | `\list_length(l)` | Length |
| 6 | `\nth(l, i)` | i-th element |
| 7 | `\mem(x, l)` | Membership test |
| 8 | `\append(l1, l2)` | Concatenation |
| 9 | `#@ ghost l += x` | Prepend shorthand: `ghost l := Cons x !l` |

**Ghost sets** (backed by `map int bool`):
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\set_empty` | Empty set |
| 2 | `\set_add(s, x)` | Add element |
| 3 | `\set_remove(s, x)` | Remove element |
| 4 | `\set_mem(x, s)` | Membership test |
| 5 | `\set_card(s, lo, hi)` | Cardinality over integer range `[lo, hi)` |
| 6 | `\set_union(s1, s2)` | Functional union (λ k → s1[k] ∨ s2[k]) |
| 7 | `\set_inter(s1, s2)` | Functional intersection |
| 8 | `\set_diff(s1, s2)` | Functional set difference |
| 9 | `\set_subset(s1, s2)` | s1 ⊆ s2 (predicate) |
| 10 | `\set_eq(s1, s2)` | s1 = s2 extensionally |
| 11 | `#@ ghost s += x` | Add shorthand: `Map.set !s x true` |

### 11.3 Required Why3 `use` Declarations

The PyCSL preamble scanner auto-detects which ghost types are in use and emits the
appropriate `use` declarations. No manual configuration is needed.

| Ghost type | Why3 library added |
|---|---|
| `string` | `use string.String` |
| `array` | `use array.Array` (hoare/concurrent only) |
| `ghost_dict` | `use map.Map`, `use map.Const`, `use option.Option` |
| `ghost_set` | `use map.Map`, `use map.Const` |
| `ghost_list` | `use list.List`, `use list.Length`, `use list.NthNoOpt`, `use list.Mem`, `use list.Append` |

### 11.4 Validation Rules (Negative Constraints)

Module4 enforces the following semantic constraints on ghost variable usage:

| # | Constraint | Error class |
|---|---|---|
| 1 | `\proj(t, expr)` — index must be an integer literal, not a variable | Module4 semantic error |
| 2 | `\proj(t, i)` — index `i` must be within the arity of the declared tuple type (no Module4 check; Why3 rejects at type checking) | Why3 type error |
| 3 | `#@ ghost s += expr` where `s` is a `string` ghost — augmented assignment not supported on strings; use `ghost s = s ^ expr` instead | Module4 semantic error |
| 4 | Augmented-assign ops (`+=`, `-=`, `*=`) on ghost string variables: always rejected regardless of the value expression | Module4 semantic error |

### 11.5 Ghost Position: Trailing-Block Ghosts

A `#@ ghost` annotation may appear as the **last line in a loop or if body** (no following
Python statement in that scope). The annotation lives in the `IndentedBlock.footer` of the
libcst CST. Module1 detects it there and records it as a `TrailingSimpleStatement` contract.
Module3 attaches it to the last statement in the block as `csl_trailing_ghost_assigns`.
Module5 emits the ghost IR **after** that last statement, so it appears at the end of the
loop body in the generated WhyML.

```python
#@ ghost count = 0
#@ loop invariant count == i
while i < n:
    i += 1
    #@ ghost count = i    ← trailing ghost: emitted as last statement in loop body
```

Generated WhyML (inside the while body):
```whyml
i := !i + 1;
ghost count := !i
```

**Constraint:** A trailing ghost that is a *first declaration* (variable not yet declared
before the block) generates `let ghost x = ref val in ()`, which is valid WhyML but gives
`x` an empty scope. Declare ghost variables before the loop to ensure they are in scope
for loop invariants.

### 11.6 Ghost Array `\copy_range`

`\copy_range(arr, lo, hi)` creates a new ghost array containing `arr[lo..hi-1]`.
Lowers to `(Array.sub arr lo (hi - lo))` in Why3.

```python
#@ ghost snap : array = \copy_range(arr, 0, n)
#@ loop invariant \forall j; 0 <= j and j < i ==> snap[j] == arr[j]
```

| Syntax | Why3 emission | Why3 `use` |
|---|---|---|
| `\copy_range(arr, lo, hi)` | `(Array.sub arr lo (hi - lo))` | `use array.Array` (auto) |

**Preconditions** (enforced by Why3's `Array.sub`):
- `0 <= lo`
- `0 <= hi - lo` (i.e., `lo <= hi`)
- `lo + (hi - lo) <= Array.length arr` (i.e., `hi <= Array.length arr`)

These appear as Why3 sub-goals when the ghost is declared. Provide a `requires` or
`loop invariant` that establishes the bounds before the declaration point.

### 11.7 Memory-Model Parity for Ghost Array Snapshots

Ghost arrays (`array` type) and the operators `\copy`, `\copy_range`, and `\make`
are available **only under `hoare` and `concurrent` memory models**.

Under `typed` and `store` models, array parameters are lowered to `loc` (integer
pointer) in the generated WhyML. `Array.copy` and `Array.sub` expect `array int`, not
`loc`, so any ghost array declaration emitted under these models would be type-incorrect
in Why3.

**Restriction summary:**

| Ghost operation | `hoare` | `concurrent` | `typed` | `store` |
|---|---|---|---|---|
| `\copy(arr)` | ✓ | ✓ | ✗ | ✗ |
| `\copy_range(arr, lo, hi)` | ✓ | ✓ | ✗ | ✗ |
| `\make(n, v)` | ✓ | ✓ | ✗ | ✗ |

For snapshot-style reasoning under `typed`/`store`, use `\old(arr[i])` or quantify
over `\old` values in postconditions instead of ghost arrays.

The `--memory-model hoare` flag is the default; it can also be specified explicitly
via `# pycsl-flags: --memory-model hoare` in the source file.

### 11.8 Ghost String `\str_sub` Proof Pattern

`\str_sub(s, lo, hi)` lowers to `String.substring !s lo (hi - lo)` in Why3 (function
`substring` from `string.String`).

**Key axiom** (from Why3 `string.String`):
```
axiom substring_length: forall s i x.
  x >= 0 && 0 <= i < length s ->
    if i + x > length s then length(substring s i x) = length s - i
    else length(substring s i x) = x
```

**Provable loop invariant pattern** — prefix length:
```python
#@ ghost s : string = ""
#@ loop invariant \str_length(s) == i
#@ loop invariant i > 0 ==> \str_length(\str_sub(s, 0, i)) == i
#@ loop variant n - i
while i < n:
    #@ ghost s = s ^ "x"
    i = i + 1
```

The invariant `i > 0 ==> \str_length(\str_sub(s, 0, i)) == i` is discharged by
Alt-Ergo directly from `substring_length` and the `\str_length(s) == i` invariant.

**Constraints:**
- `\str_sub` is valid in loop invariants and `ensures` when the string is in scope.
- `lo >= 0`, `hi >= lo`, `hi <= \str_length(s)` must be guaranteed (either by a
  prior `requires` clause or by combining with another loop invariant).
- Ghost string variables declared inside the function body are **not** in scope for
  `ensures` clauses. Use `\str_sub` directly inside loop invariants instead.

| # | 11.8.1 | `\str_sub` prefix length proof | Test 0329 |

### 11.9 Ghost Dict `\map_remove` and Option-Type Design

Ghost dicts use `map int (option int)` internally. A stored value of 0 is **present** (Some 0),
not absent. `\has_key(d, k)` returns true if and only if `Map.get !d k <> None`.

`\map_remove(d, k)` sets key k to `None` (absent). After remove, `\has_key(d, k)` is false and
`\map_get(d, k)` returns 0 (the default for absent keys).

**Provable loop invariant pattern** — add-then-remove key 0, store 0 at key 1:
```python
#@ ghost d : ghost_dict = \empty_map
#@ loop invariant i > 0 ==> \has_key(d, 1)
#@ loop invariant i > 0 ==> \map_get(d, 1) == 0
#@ loop variant n - i
while i < n:
    #@ ghost d = \map_set(d, 0, i + 1)
    #@ ghost d = \map_remove(d, 0)
    #@ ghost d = \map_set(d, 1, 0)
    i = i + 1
```

The invariant `i > 0 ==> \has_key(d, 1)` is provable because `\map_set(d, 1, 0)` stores
`Some 0`, and `Some 0 <> None`. This was impossible under the old sentinel-0 design where
storing 0 was indistinguishable from "absent".

**WhyML emission for `\map_remove`:**
`\map_remove(d, k)` → `(Map.set {d_ref} {k} None)`

| # | Syntax | Why3 emission |
|---|---|---|
| 11.9.1 | `\map_remove(d, k)` | `Map.set !d k None` |

| # | 11.9.1 | Ghost dict `\map_remove` + option-type proof | Test 0330 |
