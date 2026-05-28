# PyCSL Concrete Syntax Reference

**Status:** Normative  
**Version:** 1.3  
**Source of truth:** This document is the canonical specification of PyCSL's
concrete syntax. It is derived from the implemented grammar in
`src/pycsl/Module2_Parser.py` and cross-referenced against
`test-suite/annotations.md` (paragraph numbering preserved).

**Scope:** This document specifies what strings are syntactically valid PyCSL
annotations. It does NOT define what the annotations mean (see
`pycsl-static-semantics-reference.md` for well-formedness rules and
`pycsl-translational-reference.md` for the translation to WhyML).

---

## 1. Annotation Embedding Syntax

_Corresponds to `annotations.md` §1._

### 1.1 Physical Annotation Line

PyCSL annotations are embedded in Python source files as single-line
comments beginning with `#@`:

```
annotation_line ::= INDENT "#@" SP directive ;
```

where:
- **INDENT** is zero or more whitespace characters (matching the
  indentation of the following Python construct).
- **SP** is one or more whitespace characters.
- **directive** is any production defined in §2.

Each `#@` line carries exactly one directive. Multiple directives on the
same construct require multiple `#@` lines.

### 1.2 Placement Rules

Annotations must appear on **leading lines** — that is, immediately before
(with no intervening blank lines or code) the Python construct they
annotate:

| Construct | Placement |
|-----------|-----------|
| Function/method | Before `def` line |
| Loop | Before `while` or `for` line |
| Class | Before `class` line (requires anchor — see §1.3) |
| Statement | Before the statement line |
| `with` block | Before `with` line |

### 1.3 Class-Level Anchor

Because Python's `ast` module does not attach leading comments to class
nodes, class-level annotations (§2.3) require a preceding anchor line:

```python
""  # pycsl
#@ class invariant self._value >= 0
class Counter:
    ...
```

The anchor is a string literal `""` followed by `# pycsl` (case-sensitive).
The ingestor (`Module1_Ingestor`) uses this marker to associate the
following `#@` lines with the class definition.

### 1.4 Interaction with Python

- `#@` lines are syntactically valid Python comments and are ignored by the
  Python interpreter.
- No nesting: a `#@` line cannot itself contain another `#` comment.
- Annotations are single-line only; there is no multi-line continuation
  syntax (no trailing `\`).
- Inline `#@` annotations (e.g., `x = 1  #@ ghost`) are NOT supported;
  the `#@` must be the first non-whitespace content on the line.

---

## 2. Directives

_Corresponds to `annotations.md` §2._

### 2.1 Function/Method Contracts

_Corresponds to `annotations.md` §2.1._

| §     | Directive | Production |
|-------|-----------|-----------|
| 2.1.1 | Precondition | `precondition ::= "requires" expr ;` |
| 2.1.2 | Postcondition | `postcondition ::= "ensures" expr ;` |
| 2.1.3 | Frame condition | `assigns ::= "assigns" assigns_target ;` |
| 2.1.4 | Function variant | `function_variant ::= "\variant" expr ;` |
| 2.1.5 | Structural variant | `function_variant_structural ::= "\variant" "(" expr "," CNAME ")" ;` |
| 2.1.6 | Diverges | `diverges_decl ::= "\diverges" ;` |
| 2.1.7 | Trusted | `trusted_decl ::= "\trusted" ;` |
| 2.1.8 | Bounded integers | `bounded_int_decl ::= "assumes" "bounded_int" "(" NUMBER ")" ;` |
| 2.1.9 | Raises | `raises_decl ::= "raises" CNAME "when" expr ;` |
| 2.1.10| Thread entry | `thread_entry_decl ::= "thread_entry" ;` |
| 2.1.11| _(reserved — the colon-separated `#@ proof rocq: <q>` provenance directive was removed 2026-05-27; the current `proof` directive at §2.1.12 is load-bearing and space-separated)_ |
| 2.1.12| Axiom from proof | `proof_decl ::= "proof" prover_id qualname ;` where `prover_id ::= "rocq" \| "lean"` and `qualname ::= CNAME ("." CNAME)*` |
| 2.1.13| No-exception | `no_exception_decl ::= "no_exception" ( "\all" \| CNAME ("," CNAME)* ) ;` |

### 2.1.13 No-exception (`no_exception E1, E2, …` / `no_exception \all`)

A function-level contract directive that turns implicit Python exceptions
into proof obligations. For each operation in the function body whose IR
shape can raise one of the named exceptions (see
`config/skills/pycsl-exception-model/SKILL.md` for the trigger table),
Module 6 emits a WhyML `assert { … }` immediately before the operation.

**Forms:**

- `#@ no_exception ZeroDivisionError` — a single exception.
- `#@ no_exception ZeroDivisionError, IndexError` — multiple, comma-separated.
- `#@ no_exception \all` — wildcard, expanding to the full Phase 1 set
  defined in `exception_model.KNOWN_EXCEPTIONS`. Requires the function's
  `raises { ... }` set to be empty.

Multiple `no_exception` lines on the same function union together.

**Placement.** Inside a `#@`-prefixed contract block, immediately before
the `def` line, intermixed freely with `requires`, `ensures`, `assigns`,
`raises`, `\variant`, `\diverges`, `\trusted`.

**Valid example:**

```python
#@ requires n != 0
#@ ensures \result == 256 // n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def divide_256(n: int) -> int:
    return 256 // n
```

**Invalid example (parser/semantic rejection):**

```python
#@ raises ZeroDivisionError when n == 0
#@ no_exception ZeroDivisionError    # contradicts the line above
def conflicted(n: int) -> int: ...
```

The exception name must be in `exception_model.KNOWN_EXCEPTIONS`;
unknown names are rejected with a clear error listing the known set.

**Conjunction rule:** Multiple `requires` lines are logically conjoined
(all must hold at entry). Multiple `ensures` lines are logically conjoined
(all must hold at exit).

**Companion-proof file layout** (project convention, not a grammar
rule). When a reference test `NNNN.py` ships hand-written external
proofs, they live under `test-suite/corpus/pycsl-reference/NNNN.proofs/`
in the following layout:

```
NNNN.py
NNNN.proofs/
  rocq/<file>.v       — Coq theorems; `Theorem <name> : …` per proof
  lean/<file>.lean    — Lean theorems; `theorem <name> : …` per proof
  README.md           — (optional) directory documentation
```

A `#@ proof rocq <qualname>` line is expected to match a theorem of
the same `<qualname>` inside `NNNN.proofs/rocq/`; likewise for Lean.
**Worked example:** `test-suite/corpus/pycsl-reference/0342.py`
(Euclidean GCD) with proofs under `0342.proofs/rocq/gcd.v` and
`0342.proofs/lean/Gcd.lean`.

#### §2.1.12 Proof Citation (`proof`) — Rocq + Lean as Cross-Validated Spec Sources

```ebnf
proof_decl ::= "proof" prover_id qualname ;
prover_id       ::= "rocq" | "lean" ;
qualname        ::= CNAME ("." CNAME)* ;
```

Imports a theorem proved in Rocq or Lean as a **Why3 axiom** in the
generated WhyML preamble. `proof` has semantic effect: the
`proof2why3` tool extracts the theorem statement, canonicalizes it,
and emits it as `axiom pycsl_axiom_<target>`.

**Cross-validation.** When both `#@ proof rocq <q>` and
`#@ proof lean <q>` appear for the same `pycsl_target` name, the
`proof2why3 cross-check` step verifies that both theorem statements have
equal canonical forms (alpha-normalized, AC-flattened, `nat`/`Nat` →
`int + ≥ 0`). This is the **"Rocq + Lean as Cross-Validated Spec
Sources"** pattern: two independent proof-assistant kernels must agree on
the specification before it enters the Why3 verification.

**Scope:** Module-level (placed before any function definition).

**Note:** No colon separator between `prover_id` and `qualname`:
`proof rocq Pycsl.Reference.Gcd.gcd_step`.

**Audit (`pycsl --audit-proof`):** The dotted `qualname`
`A.B.C.theorem_name` is enforced as a real namespace path. For Rocq,
the cited theorem must be declared inside `Module A. Module B.
Module C. ...` nesting; for Lean, inside `namespace A.B.C` (or
equivalent nested form). The audit parses each `.v` / `.lean` file in
the proof dir with a namespace-aware state machine — the bare name
greping the older shell script used is gone. Default proof dirs:
`<file>.proofs/rocq/` and `<file>.proofs/lean/` next to the Python
file. Override with `--rocq-proofs-path DIR` / `--lean-proofs-path
DIR`. The audit is independent of the WhyML emission and can be run
on a file that has no `#@ proof` directives (it then trivially
passes).

_Corresponds to `annotations.md` §2.1.12._

#### Examples

```python
#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
#@ \variant n
def factorial(n: int) -> int:
    if n == 0:
        return 1
    return n * factorial(n - 1)

#@ \trusted
def external_call(x: int) -> int:
    ...

#@ \diverges
def server_loop() -> None:
    while True:
        pass

#@ assumes bounded_int(32)
#@ requires x >= 0 and y >= 0
#@ ensures \result == x + y
def safe_add(x: int, y: int) -> int:
    return x + y

#@ raises ValueError when x < 0
#@ ensures \result >= 0
def checked_sqrt(x: int) -> int:
    ...
```

### 2.2 Loop Contracts

_Corresponds to `annotations.md` §2.2._

| §     | Directive | Production |
|-------|-----------|-----------|
| 2.2.1 | Loop invariant | `loop_invariant ::= "loop" "invariant" expr ;` |
| 2.2.2 | Loop variant | `loop_variant ::= "loop" "variant" expr ;` |
| 2.2.3 | Allow iteration mutation | `allow_iteration_mutation_decl ::= "allow_iteration_mutation" ;` |

#### Examples

```python
#@ loop invariant 0 <= i and i <= n
#@ loop variant n - i
while i < n:
    i = i + 1
```

```python
#@ allow_iteration_mutation
for x in arr:
    arr.append(x + 1)
    return
```

### 2.3 Class Contracts

_Corresponds to `annotations.md` §2.3._

| §     | Directive | Production |
|-------|-----------|-----------|
| 2.3.1 | Class invariant | `class_invariant ::= "class" "invariant" expr ;` |
| 2.3.2 | Allow finalizer | `allow_finalizer_decl ::= "allow_finalizer" ;` |

Must be preceded by the anchor `""  # pycsl` (see §1.3).

#### Example

```python
""  # pycsl
#@ class invariant self._balance >= 0
class Account:
    ...
```

```python
""  # pycsl
#@ class invariant self._n >= 0
#@ allow_finalizer
class WithFinalizer:
    def __init__(self) -> None:
        self._n: int = 0
    def __del__(self) -> None:
        self._n = 0
```

### 2.4 Program Point Annotations

_Corresponds to `annotations.md` §2.4._

| §     | Directive | Production |
|-------|-----------|-----------|
| 2.4.1 | Label | `label_decl ::= "label" CNAME ;` |
| 2.4.2 | Ghost assign | `ghost_assign ::= "ghost" CNAME "=" expr ;` |
| 2.4.2b | Typed ghost declaration | `ghost_typed_assign ::= "ghost" CNAME ":" ghost_type "=" expr ;` where `ghost_type ::= "int" \| "string" \| "array" \| "ghost_dict" \| "ghost_list" \| "ghost_set" \| "tuple2" \| "tuple3" \| "tuple4" ;` |
| 2.4.3 | Ghost augmented assign | `ghost_aug_assign ::= "ghost" CNAME GHOST_AUG_OP expr ;` |
| 2.4.4 | Critical section | `critical_decl ::= "critical" mutex_expr ;` |
| 2.4.5 | Acquires | `acquires_decl ::= "acquires" mutex_expr ;` |
| 2.4.6 | Releases | `releases_decl ::= "releases" mutex_expr ;` |

where:
```
GHOST_AUG_OP ::= "+=" | "-=" | "*=" ;
```

Ghost variables exist only in the verification model. They are erased at
extraction. They may be referenced in `loop invariant`, `requires`,
`ensures`, and `\variant` expressions.

#### Examples

```python
#@ label PRE
x = x + 1

#@ ghost count = 0
#@ ghost count += 1

#@ critical my_mutex
with lock:
    shared_var += 1
```

---

## 3. Expression Language

_Corresponds to `annotations.md` §3._

### 3.1 Atoms

_Corresponds to `annotations.md` §3.1._

The `atom` production defines the terminal and built-in expressions:

```
atom ::= NUMBER                                          (* §3.1.1  Integer literal      *)
       | ESCAPED_STRING                                  (* §3.1.14 String literal        *)
       | "True"                                          (* §3.1.18 Boolean true          *)
       | "False"                                         (* §3.1.18 Boolean false         *)
       | "None"                                          (* §3.1.19 None literal          *)
       | "self" "." CNAME                                (* §3.1.3  Field access          *)
       | "\result" "[" expr "]"                          (* §3.1.5b Result subscript      *)
       | "\is_sorted" "(" CNAME "," expr "," expr ")"   (* §3.1.15 Sorted predicate      *)
       | "\sum" "(" CNAME "," expr "," expr ")"          (* §3.1.16 Sum aggregate         *)
       | CNAME "(" expr_list ")"                         (* §3.1.17 Function call (args)  *)
       | CNAME "(" ")"                                   (* §3.1.17 Function call (no args) *)
       | CNAME "[" expr ":" expr "]"                     (* §3.1.20 Slice notation        *)
       | CNAME "[" expr "]" "[" expr "]"                 (* §3.1.4b Chained subscript     *)
       | CNAME "[" expr "]"                              (* §3.1.4  Subscript access      *)
       | CNAME                                           (* §3.1.2  Variable reference    *)
       | "\result"                                       (* §3.1.5  Return value          *)
       | "\old" "(" expr ")"                             (* §3.1.6  Old value             *)
       | "\length" "(" CNAME ")"                         (* §3.1.8  Array length          *)
       | "\valid" "(" CNAME "," expr ")"                 (* §3.1.9  Validity predicate    *)
       | "\separated" "(" CNAME "," expr ","
                           CNAME "," expr ")"            (* §3.1.10 Separation predicate  *)
       | "\at" "(" expr "," CNAME ")"                    (* §3.1.7  At label              *)
       | "\length2d" "(" CNAME "," expr "," expr ")"    (* §3.1.11 2D length             *)
       | "\valid2d" "(" CNAME "," expr "," expr ")"     (* §3.1.12 2D validity           *)
       | "(" expr ")"                                    (* Parenthesized expression      *)
       ;
```

**Ordering matters.** In the PEG/Lark parser, alternatives are tried
top-to-bottom. Longer prefixes must appear before shorter ones:

1. `CNAME "[" expr ":" expr "]"` (slice) before `CNAME "[" expr "]" "[" expr "]"` (chained)
2. `CNAME "[" expr "]" "[" expr "]"` (chained) before `CNAME "[" expr "]"` (single)
3. `CNAME "(" expr_list ")"` (call) before `CNAME` (bare variable)
4. `"\result" "[" expr "]"` (result subscript) before `"\result"` (bare result)

#### Atom Catalogue

| § | Syntax | AST Node | Description |
|---|--------|----------|-------------|
| 3.1.1 | `42`, `-1`, `0` | `Number` | Integer literal. Parsed by the `NUMBER` terminal (Lark's `INT` import). Negative integers are parsed as `UnaryOp("-", Number(n))`. |
| 3.1.2 | `x`, `n`, `total` | `Var` | Variable reference. Must match `CNAME` (letter or underscore, followed by letters, digits, or underscores). |
| 3.1.3 | `self.field` | `FieldAccess` | Class field access. The object is always the literal string `"self"`. |
| 3.1.4 | `arr[i]` | `SubscriptAccess` | Array element access. The array name is a `CNAME`; the index is an arbitrary `expr`. |
| 3.1.4b | `arr[i][j]` | `ChainedSubscript` | 2D array element access. The array name is a `CNAME`; both indices are arbitrary `expr`. Only two levels of chaining are supported (not 3D+). |
| 3.1.5 | `\result` | `Result` | Return value of the current function. Valid only in `ensures` clauses (checked by static semantics, not syntax). |
| 3.1.5b | `\result[i]` | `ResultSubscript` | Subscript into the return value. Parsed as a distinct atom with the `expr` index. |
| 3.1.6 | `\old(e)` | `Old` | Value of expression `e` at function entry. |
| 3.1.7 | `\at(e, L)` | `At` | Value of expression `e` at the program point labeled `L`. |
| 3.1.8 | `\length(arr)` | `ArrayLength` | Length of array `arr`. The argument is a `CNAME` (not an arbitrary expression). |
| 3.1.9 | `\valid(arr, n)` | `Valid` | Array `arr` has at least `n` allocated elements (`arr[0..n)` is valid). |
| 3.1.10 | `\separated(a, na, b, nb)` | `Separated` | Regions `a[0..na)` and `b[0..nb)` do not overlap. Both `a` and `b` are `CNAME`; `na` and `nb` are `expr`. |
| 3.1.11 | `\length2d(a, m, n)` | `Length2D` | Array `a` has `m` rows, each of length `n`. |
| 3.1.12 | `\valid2d(a, i, j)` | `Valid2D` | Index `(i, j)` is valid for 2D array `a`. |
| 3.1.13 | `\nothing` | `Nothing` | Empty assigns target. Only valid as an `assigns_target` (see §3.4), not as a general expression. |
| 3.1.14 | `"hello"` | `StringLiteral` | String literal. Parsed by Lark's `ESCAPED_STRING` terminal (double-quoted, with standard escapes). |
| 3.1.15 | `\is_sorted(a, lo, hi)` | `IsSorted` | Array `a[lo..hi)` is sorted in ascending order. |
| 3.1.16 | `\sum(a, lo, hi)` | `Sum` | Sum of array elements `a[lo..hi)`. |
| 3.1.17 | `f(x, y)` | `CallExpr` | Pure function call. The function name is a `CNAME`; arguments are a comma-separated `expr_list` (or empty for no-argument calls). |
| 3.1.18 | `True`, `False` | `CSLBool` | Boolean literals. |
| 3.1.19 | `None` | `CSLNone` | None literal. Maps to `0` in WhyML. |
| 3.1.20 | `arr[lo:hi]` | `CSLSlice` | Array slice. The array name is a `CNAME`; both bounds are `expr`. |
| 3.1.21 | `\empty_map` | `MapEmptyExpr` | Empty ghost dict literal. Returns a map where all keys are absent. No arguments. |
| 3.1.22 | `\map_get(d, k)` | `MapGetExpr` | Ghost dict get. Returns the value stored at key `k` in dict `d`, or 0 if absent. Both arguments are `expr`. |
| 3.1.23 | `\map_set(d, k, v)` | `MapSetExpr` | Ghost dict set. Returns a new dict with key `k` mapped to value `v`. All three arguments are `expr`. |
| 3.1.24 | `\map_remove(d, k)` | `MapRemoveExpr` | Ghost dict remove. Returns a new dict with key `k` set to absent. Both arguments are `expr`. |
| 3.1.25 | `\has_key(d, k)` | `HasKeyExpr` | Ghost dict membership. True iff key `k` is present in dict `d`. Both arguments are `expr`. |
| 3.1.26 | `\map_eq(d1, d2)` | `MapEqExpr` | Ghost dict extensional equality. True iff `d1` and `d2` agree on every key. Both arguments are `expr`. |

_Corresponds to `annotations.md` §11.2._

### 3.2 Operators (by precedence, lowest first)

_Corresponds to `annotations.md` §3.2._

Operator precedence is encoded by a cascading chain of non-terminals.
Each level delegates to the next-higher level for its operands, ensuring
that higher-precedence operators bind more tightly.

```
expr        ::= implication
              | quantifier ;

implication ::= logical_or
              | implication IMPL_OP ( logical_or | quantifier ) ;

logical_or  ::= logical_and
              | logical_or OR_OP ( logical_and | quantifier ) ;

logical_and ::= equality
              | logical_and AND_OP ( equality | quantifier ) ;

equality    ::= comparison
              | equality EQ_OP comparison ;

comparison  ::= membership
              | comparison COMP_OP membership ;

membership  ::= term
              | term "in" term
              | term "not" "in" term ;

term        ::= factor
              | term ADD_OP factor ;

factor      ::= unary
              | factor MUL_OP unary ;

unary       ::= UNARY_OP unary
              | atom ;
```

#### Operator Table

| § | Prec. | Operators | Token | Assoc. | AST Node |
|---|-------|-----------|-------|--------|----------|
| 3.2.1 | 1 (lowest) | `\forall v; body`, `\exists v; body`, `\exist v; body` | — | Right | `Forall`, `Exists` |
| 3.2.2 | 2 | `==>` (implies), `<==>` (iff) | `IMPL_OP` | Left | `BinOp` |
| 3.2.3 | 3 | `or` | `OR_OP` | Left | `BinOp` |
| 3.2.4 | 4 | `and` | `AND_OP` | Left | `BinOp` |
| 3.2.5 | 5 | `==`, `!=` | `EQ_OP` | Left | `BinOp` |
| 3.2.6 | 6 | `<`, `>`, `<=`, `>=` | `COMP_OP` | Left | `BinOp` |
| 3.2.6b | 6.5 | `in`, `not in` | — | Non-assoc. | `CSLIn`, `CSLNotIn` |
| 3.2.7 | 7 | `+`, `-` | `ADD_OP` | Left | `BinOp` |
| 3.2.8 | 8 | `*`, `//`, `/`, `%` | `MUL_OP` | Left | `BinOp` |
| 3.2.9 | 9 (highest) | `not`, unary `-`, unary `+` | `UNARY_OP` | Right (prefix) | `UnaryOp` |

**Notes:**
- `/` in contracts maps to WhyML `div` (Euclidean integer division), not
  Python's float division.
- `//` also maps to WhyML `div`.
- `%` maps to WhyML `mod`.
- `<==>` is a single token (biconditional / "if and only if").
- `in`/`not in` (§3.2.6b) are parsed as separate keywords, not as a
  single token. `not in` is distinguished from the unary `not` operator
  by the grammar structure: `term "not" "in" term` versus `"not" unary`.

### 3.3 Quantifiers

_Corresponds to `annotations.md` §3.3._

```
quantifier ::= "\forall" CNAME ";" expr
             | "\exists" CNAME ";" expr
             | "\exist"  CNAME ";" expr ;
```

**Parsing rules:**

1. The bound variable is always a `CNAME`.
2. The body extends **greedily** to the end of the expression (right-associative).
3. `\exist` (singular) is an alias for `\exists`.
4. Quantifiers may appear:
   - At the top level of an `expr`
   - As the right-hand side of `==>`, `and`, or `or` operators
5. Quantifiers may be nested:
   ```python
   #@ requires \forall i; \forall j; 0 <= i and i < j and j < n ==> arr[i] <= arr[j]
   ```
6. The bound variable is implicitly typed `int` in the WhyML output
   (determined by translational semantics, not syntax).

#### Examples

```python
#@ requires \forall i; 0 <= i and i < n ==> arr[i] >= 0
#@ ensures \exists j; 0 <= j and j < n and arr[j] == target
#@ loop invariant \forall k; 0 <= k and k < i ==> arr[k] <= arr[i]
```

### 3.4 Assigns Targets

_Corresponds to `annotations.md` §3.4._

```
assigns_target ::= assigns_region_list
                 | expr_list
                 | "\nothing" ;

assigns_region_list ::= assigns_region ( "," assigns_region )* ;
assigns_region      ::= CNAME "[" expr RANGE_OP expr "]" ;

expr_list ::= expr ( "," expr )* ;

RANGE_OP ::= ".." ;
```

| § | Syntax | AST Node | Description |
|---|--------|----------|-------------|
| 3.4.1 | `\nothing` | `Nothing` | No mutation allowed (pure function) |
| 3.4.2 | `x` | `Var` | Variable `x` may be mutated |
| 3.4.3 | `x, y` | `[Var, Var]` | Multiple variables may be mutated |
| 3.4.4 | `self.field` | `FieldAccess` | Class field may be mutated |
| 3.4.5 | `arr[lo..hi]` | `AssignsRegion` | Array region `arr[lo..hi)` may be mutated |

**Disambiguation:** The parser attempts to parse `assigns_region_list`
first (looking for `..`). If that fails, it falls back to `expr_list`.
This ensures that `arr[0..n]` is parsed as a region (not a subscript
with a range expression).

#### Examples

```python
#@ assigns \nothing
#@ assigns x
#@ assigns x, y, z
#@ assigns self._value
#@ assigns self._lo, self._hi
#@ assigns arr[0..n]
#@ assigns arr[0..n], brr[0..m]
```

---

## 4. Unsupported Constructs in Contracts

_Corresponds to `annotations.md` §4._

The following Python constructs are **not part of the grammar** and will
produce a parse error if used inside `#@` expressions:

| § | Construct | Reason | Alternative |
|---|-----------|--------|-------------|
| 4.1 | `len(...)` | Python built-in, not in spec logic | `\length(arr)` |
| 4.2 | List comprehensions | No grammar rule | Use `\forall` / `\exists` |
| 4.3 | `if`/`else` ternary | No grammar rule | Use `==>` (implication) |

**Formerly unsupported, now supported:**

| Construct | Added as | Reference |
|-----------|----------|-----------|
| `//` (floor division) | `MUL_OP` | §3.2, row 8 |
| `%` (modulo) | `MUL_OP` | §3.2, row 8 |
| `True` / `False` | `CSLBool` atom | §3.1, row 18 |
| `None` | `CSLNone` atom | §3.1, row 19 |
| `in`, `not in` | Membership operators | §3.2, row 6b |
| Function calls | `CallExpr` atom | §3.1, row 17 |

### 4.1 Pure Function Calls in Contracts

Functions annotated with `#@ assigns \nothing` (pure, side-effect-free)
may be called inside `requires`, `ensures`, and `loop invariant`
expressions. Syntactically, any `CNAME "(" expr_list ")"` or
`CNAME "(" ")"` is accepted. Eligibility constraints (no side effects,
not `\diverges`, must have `\variant` if recursive) are enforced by
static semantics, not by the grammar.

---

## 5. Memory Model Directives

_Corresponds to `annotations.md` §5._

The concurrent memory model (`--memory-model concurrent`) introduces
module-level directives that are parsed as part of the `contract`
production:

```
shared_decl          ::= "shared" CNAME "protected_by" mutex_expr
                       | "shared" CNAME ;

mutex_invariant_decl ::= "mutex_invariant" mutex_expr ":" expr ;

lock_order_decl      ::= "lock_order" mutex_expr ( "," mutex_expr )+ ;

mutex_expr           ::= CNAME "[" expr "]"   (* Subscripted mutex *)
                       | CNAME ;              (* Named mutex       *)
```

| § | Directive | Scope | Description |
|---|-----------|-------|-------------|
| 5.4.1 | `shared` | Module | Declares a shared variable, optionally with a protecting mutex |
| 5.4.2 | `mutex_invariant` | Module | Invariant that holds whenever the mutex is free |
| 5.4.3 | `lock_order` | Module | Total acquisition order to prevent deadlock |

Module-level declarations must be placed before any function definition
and attached to an anchor statement (e.g., `_ = 0  # anchor`).

#### Examples

```python
_ = 0  # anchor
#@ shared counter protected_by lock
#@ shared read_count protected_by rw_lock
#@ mutex_invariant lock: counter >= 0
#@ lock_order lock, rw_lock
```

---

## 6. Class Contract Syntax

_Corresponds to `annotations.md` §6._

This section describes the syntactic patterns for class contracts. The
semantics of class invariant checking (preservation at method boundaries,
witness generation) are defined in the static and translational semantics
documents.

### 6.1 Single Class Invariant

```python
""  # pycsl
#@ class invariant <expr>
class ClassName:
    ...
```

### 6.2 Multiple Stacked Invariants

```python
""  # pycsl
#@ class invariant <expr1>
#@ class invariant <expr2>
#@ class invariant <expr3>
class ClassName:
    ...
```

Each `class invariant` line is an independent conjunct. All must hold at
every method boundary.

### 6.3 Cross-Field Invariants

The invariant expression may reference multiple `self.field` names:

```python
""  # pycsl
#@ class invariant self._lo <= self._hi
class Interval:
    ...
```

### 6.4 Invariant with Method Contracts

Methods that mutate fields appearing in the invariant must have
sufficiently strong `requires` clauses:

```python
""  # pycsl
#@ class invariant self._balance >= 0
class Account:
    #@ requires amount >= 0 and amount <= self._balance
    #@ ensures self._balance == \old(self._balance) - amount
    #@ assigns self._balance
    def withdraw(self, amount: int) -> int:
        self._balance = self._balance - amount
        return self._balance
```

---

## 7. `\old` and `\at` Syntax

_Corresponds to `annotations.md` §7._

### 7.1 `\old(expr)`

```
old_expr ::= "\old" "(" expr ")" ;
```

References the value of `expr` at function entry. The argument is an
arbitrary expression (variable, field access, subscript, etc.).

```python
#@ ensures arr[0] == \old(arr[1])
#@ ensures self._value == \old(self._value) + amount
```

### 7.2 `\at(expr, L)`

```
at_expr ::= "\at" "(" expr "," CNAME ")" ;
```

References the value of `expr` at the program point labeled `L`.

```python
#@ label PRE
arr[0] = arr[0] + 1
#@ ensures arr[0] == \at(arr[0], PRE) + 1
```

---

## 8. Lexical Conventions

### 8.1 Terminals

The grammar uses the following terminal symbols, imported from Lark's
common grammar library:

```
CNAME          ::= ( LETTER | "_" ) ( LETTER | DIGIT | "_" )* ;
NUMBER         ::= DIGIT+ ;
ESCAPED_STRING ::= "\"" ( CHAR | ESCAPE )* "\"" ;
WS             ::= ( " " | "\t" | "\n" | "\r" )+ ;

LETTER ::= "a".."z" | "A".."Z" ;
DIGIT  ::= "0".."9" ;
CHAR   ::= (* any character except "\" and "\"" *) ;
ESCAPE ::= "\\" ( "\"" | "\\" | "/" | "b" | "f" | "n" | "r" | "t"
                | "u" HEX HEX HEX HEX ) ;
HEX    ::= DIGIT | "a".."f" | "A".."F" ;
```

### 8.2 Whitespace

All whitespace (`WS`) is ignored between tokens. The parser is
whitespace-insensitive within an annotation line.

### 8.3 Keywords and Backslash-Prefixed Identifiers

PyCSL uses two naming conventions:

1. **Plain keywords:** `requires`, `ensures`, `assigns`, `loop`,
   `invariant`, `variant`, `class`, `label`, `ghost`, `shared`,
   `mutex_invariant`, `lock_order`, `thread_entry`, `acquires`,
   `releases`, `critical`, `raises`, `when`, `assumes`, `bounded_int`,
   `and`, `or`, `not`, `in`, `True`, `False`, `None`, `self`,
   `protected_by`.

2. **Backslash-prefixed identifiers:** `\result`, `\old`, `\at`,
   `\length`, `\valid`, `\separated`, `\length2d`, `\valid2d`,
   `\nothing`, `\forall`, `\exists`, `\exist`, `\is_sorted`, `\sum`,
   `\variant`, `\diverges`, `\trusted`.

The backslash prefix avoids collision with Python identifiers and signals
that the name belongs to the specification logic.

### 8.4 Operator Tokens

```
IMPL_OP      ::= "==>" | "<==>" ;
OR_OP        ::= "or" ;
AND_OP       ::= "and" ;
EQ_OP        ::= "==" | "!=" ;
COMP_OP      ::= ">" | "<" | ">=" | "<=" ;
ADD_OP       ::= "+" | "-" ;
MUL_OP       ::= "*" | "//" | "/" | "%" ;
UNARY_OP     ::= "not" | "-" | "+" ;
RANGE_OP     ::= ".." ;
GHOST_AUG_OP ::= "+=" | "-=" | "*=" ;
```

**Disambiguation:** The token `not` is both a `UNARY_OP` and the first
keyword of `not in`. The grammar resolves this structurally: at the
`membership` level, `term "not" "in" term` is tried before falling
through to `unary`. At the `unary` level, `"not" unary` is a prefix
operator.

---

## 9. Complete Grammar (Normative)

_Corresponds to `annotations.md` §8._

This section contains the complete grammar in standard EBNF notation
(ISO 14977-inspired, using `::=` for rules, `|` for alternatives, `*`
for zero-or-more repetition, `+` for one-or-more, `?` for optional, and
`(* ... *)` for comments). This is the **normative** grammar — all
preceding sections are explanatory.

```ebnf
(* ============================================================ *)
(* PyCSL Concrete Syntax — Complete EBNF Grammar v1.0           *)
(* ============================================================ *)

(* --- Top-level -------------------------------------------- *)

start    ::= contract ;

contract ::= precondition
           | postcondition
           | assigns
           | loop_invariant
           | loop_variant
           | class_invariant
           | label_decl
           | function_variant
           | function_variant_structural
           | diverges_decl
           | trusted_decl
           | ghost_assign
           | ghost_aug_assign
           | raises_decl
           | bounded_int_decl
           | proof_decl
           | no_exception_decl
           | allow_finalizer_decl
           | allow_iteration_mutation_decl
           | shared_decl
           | thread_entry_decl
           | acquires_decl
           | releases_decl
           | critical_decl
           | mutex_invariant_decl
           | lock_order_decl ;

(* --- §2.1  Function/Method Contracts ---------------------- *)

precondition                ::= "requires" expr ;
postcondition               ::= "ensures" expr ;
assigns                     ::= "assigns" assigns_target ;
function_variant            ::= "\variant" expr ;
function_variant_structural ::= "\variant" "(" expr "," CNAME ")" ;
diverges_decl               ::= "\diverges" ;
trusted_decl                ::= "\trusted" ;
raises_decl                 ::= "raises" CNAME "when" expr ;
bounded_int_decl            ::= "assumes" "bounded_int" "(" NUMBER ")" ;
proof_decl             ::= "proof" prover_id qualname ;
prover_id                   ::= "rocq" | "lean" ;
qualname                    ::= CNAME ( "." CNAME )* ;

(* --- §2.2  Loop Contracts --------------------------------- *)

loop_invariant                 ::= "loop" "invariant" expr ;
loop_variant                   ::= "loop" "variant" expr ;
allow_iteration_mutation_decl  ::= "allow_iteration_mutation" ;

(* --- §2.3  Class Contracts -------------------------------- *)

class_invariant      ::= "class" "invariant" expr ;
allow_finalizer_decl ::= "allow_finalizer" ;

(* --- §2.1.13  No-exception (re-listed here for grammar completeness) *)
no_exception_decl ::= "no_exception" ( "\all" | CNAME ( "," CNAME )* ) ;

(* --- §2.4  Program Point Annotations ---------------------- *)

label_decl         ::= "label" CNAME ;
ghost_assign       ::= "ghost" CNAME "=" expr ;
ghost_typed_assign ::= "ghost" CNAME ":" ghost_type "=" expr ;
ghost_aug_assign   ::= "ghost" CNAME GHOST_AUG_OP expr ;

ghost_type ::= "int" | "string" | "array" | "ghost_dict"
             | "ghost_list" | "ghost_set"
             | "tuple2" | "tuple3" | "tuple4" ;

(* --- §3.4  Assigns Targets -------------------------------- *)

assigns_target      ::= assigns_region_list
                       | expr_list
                       | "\nothing" ;
assigns_region_list ::= assigns_region ( "," assigns_region )* ;
assigns_region      ::= CNAME "[" expr RANGE_OP expr "]" ;

(* --- §3.1–3.2  Expression Hierarchy ----------------------- *)

expr       ::= implication
             | "\forall" CNAME ";" expr
             | "\exists" CNAME ";" expr
             | "\exist"  CNAME ";" expr ;

implication ::= logical_or
              | implication IMPL_OP impl_rhs ;
impl_rhs    ::= logical_or
              | "\forall" CNAME ";" expr
              | "\exists" CNAME ";" expr
              | "\exist"  CNAME ";" expr ;

logical_or  ::= logical_and
              | logical_or OR_OP or_rhs ;
or_rhs      ::= logical_and
              | "\forall" CNAME ";" expr
              | "\exists" CNAME ";" expr
              | "\exist"  CNAME ";" expr ;

logical_and ::= equality
              | logical_and AND_OP and_rhs ;
and_rhs     ::= equality
              | "\forall" CNAME ";" expr
              | "\exists" CNAME ";" expr
              | "\exist"  CNAME ";" expr ;

equality    ::= comparison
              | equality EQ_OP comparison ;

comparison  ::= membership
              | comparison COMP_OP membership ;

membership  ::= term
              | term "in" term
              | term "not" "in" term ;

term        ::= factor
              | term ADD_OP factor ;

factor      ::= unary
              | factor MUL_OP unary ;

unary       ::= UNARY_OP unary
              | atom ;

(* --- §3.1  Atom ------------------------------------------- *)

atom ::= NUMBER
       | ESCAPED_STRING
       | "True"
       | "False"
       | "None"
       | "self" "." CNAME
       | "\result" "[" expr "]"
       | "\is_sorted" "(" CNAME "," expr "," expr ")"
       | "\sum" "(" CNAME "," expr "," expr ")"
       | CNAME "(" expr_list ")"
       | CNAME "(" ")"
       | CNAME "[" expr ":" expr "]"
       | CNAME "[" expr "]" "[" expr "]"
       | CNAME "[" expr "]"
       | CNAME
       | "\result"
       | "\old" "(" expr ")"
       | "\length" "(" CNAME ")"
       | "\valid" "(" CNAME "," expr ")"
       | "\separated" "(" CNAME "," expr "," CNAME "," expr ")"
       | "\at" "(" expr "," CNAME ")"
       | "\length2d" "(" CNAME "," expr "," expr ")"
       | "\valid2d" "(" CNAME "," expr "," expr ")"
       | "\empty_map"
       | "\map_get"    "(" expr "," expr ")"
       | "\map_set"    "(" expr "," expr "," expr ")"
       | "\map_remove" "(" expr "," expr ")"
       | "\has_key"    "(" expr "," expr ")"
       | "\map_eq"     "(" expr "," expr ")"
       | "(" expr ")" ;

expr_list ::= expr ( "," expr )* ;

(* --- §5.4  Concurrent Model Annotations ------------------- *)

shared_decl          ::= "shared" CNAME "protected_by" mutex_expr
                       | "shared" CNAME ;
thread_entry_decl    ::= "thread_entry" ;
acquires_decl        ::= "acquires" mutex_expr ;
releases_decl        ::= "releases" mutex_expr ;
critical_decl        ::= "critical" mutex_expr ;
mutex_invariant_decl ::= "mutex_invariant" mutex_expr ":" expr ;
lock_order_decl      ::= "lock_order" mutex_expr ( "," mutex_expr )+ ;

mutex_expr ::= CNAME "[" expr "]"
             | CNAME ;

(* --- §8  Operator Tokens ---------------------------------- *)

IMPL_OP      ::= "==>" | "<==>" ;
OR_OP        ::= "or" ;
AND_OP       ::= "and" ;
EQ_OP        ::= "==" | "!=" ;
COMP_OP      ::= ">" | "<" | ">=" | "<=" ;
ADD_OP       ::= "+" | "-" ;
MUL_OP       ::= "*" | "//" | "/" | "%" ;
UNARY_OP     ::= "not" | "-" | "+" ;
RANGE_OP     ::= ".." ;
GHOST_AUG_OP ::= "+=" | "-=" | "*=" ;

(* --- §8  Imported Terminals ------------------------------- *)

CNAME          ::= ( LETTER | "_" ) ( LETTER | DIGIT | "_" )* ;
NUMBER         ::= DIGIT+ ;
ESCAPED_STRING ::= '"' ( CHAR | ESCAPE )* '"' ;
```

---

## 10. Gap Analysis

This section documents discrepancies between the implemented grammar
(`Module2_Parser.py`), `annotations.md`, and this reference.

### 10.1 Grammar Features Not in `annotations.md`

| Feature | Grammar Rule | Status |
|---------|-------------|--------|
| `\result[i]` (result subscript) | `"\result" "[" expr "]" -> result_subscript` | **Undocumented.** The grammar accepts subscript access on `\result`, but `annotations.md` §3.1.5 only describes bare `\result`. Recommend adding §3.1.5b to `annotations.md`. |
| `mutex_expr` subscript (`lock[i]`) | `CNAME "[" expr "]" -> mutex_subscript` | **Undocumented.** Concurrent directives accept subscripted mutex names (e.g., `acquires locks[0]`), but `annotations.md` §2.4 only shows plain `CNAME` mutexes. |
| `GHOST_AUG_OP` includes `*=` | `"*=" in GHOST_AUG_OP` | **Partially documented.** `annotations.md` §2.4.3 mentions `+=`, `-=`, `*=` in the table but examples only show `+=`. |

### 10.2 LALR Parser Limitations

| Feature | Symptom | Workaround |
|---------|---------|------------|
| `not` as unary prefix on bare variable | `requires not x == 0` fails — LALR tokenizer interprets `not` as `CNAME` due to conflict with `not in` membership operator | Use parentheses: `requires not (x == 0)` |

This is an inherent LALR(1) ambiguity: the token `not` could begin either
the unary prefix `not expr` or the membership test `term not in term`.
The Lark parser resolves this by giving `CNAME` priority in certain
positions, causing `not` followed by a bare identifier to be misparsed.
When `not` is followed by `(`, the parser correctly recognizes it as a
unary operator.

### 10.3 `annotations.md` Features Not in Grammar

| Feature | annotations.md | Status |
|---------|---------------|--------|
| Chained subscript `arr[i][j]` | §3.1 only shows `arr[i]` (row 4) | **Now implemented.** Added as §3.1.4b in this reference. `annotations.md` should be updated. |
| Typed ghost declaration (`ghost x : T = e`) | §11.1 | **Added as §2.4.2b in v1.1.** Productions: `ghost_typed_assign`, `ghost_type`. |
| Ghost dict atoms (`\empty_map`, `\map_get`, `\map_set`, `\map_remove`, `\has_key`, `\map_eq`) | §11.2 | **Added as §3.1.21–3.1.26 in v1.1.** Corresponds to `MapEmptyExpr`…`MapEqExpr` in `Module2_Parser.py`. |
| Body-level data structures (`dict`, `set`, multi-arg `range`, `Optional[T]`, `Union[T, None]`, `sorted`/`any`/`all`) | §12 | **Body-code only — not part of annotation grammar.** Documented in `annotations.md` §12 and `pycsl-translational-reference.md` §T.14. The annotation grammar is unaffected. |

### 10.4 Normalization Notes (Lark → EBNF)

The following Lark-specific constructs were normalized to standard EBNF:

| Lark Construct | EBNF Equivalent | Notes |
|---------------|-----------------|-------|
| `?rule:` (inline rule) | Expanded in place | Lark's `?` suppresses the node in the parse tree; in EBNF, we use named productions |
| `-> alias` (tree alias) | Omitted | Aliases map to AST node constructors; not a grammar concern |
| `%import` | Terminal definitions reproduced inline | `CNAME`, `NUMBER`, `ESCAPED_STRING` |
| `%ignore WS` | Stated as prose rule (§8.2) | |

---

## Appendix A. AST Node Hierarchy

For reference, the complete hierarchy of CSL AST nodes defined in
`Module2_Parser.py`:

```
CSLNode (base)
├── ContractWrapper
│   ├── Requires          (§2.1.1)
│   ├── Ensures           (§2.1.2)
│   ├── LoopInvariant     (§2.2.1)
│   └── LoopVariant       (§2.2.2)
├── QuantifierNode
│   ├── Forall            (§3.2.1)
│   └── Exists            (§3.2.1)
├── SingleExprNode
│   ├── UnaryOp           (§3.2.9)
│   └── Old               (§3.1.6)
├── BinOp                 (§3.2.2–§3.2.8)
├── Var                   (§3.1.2)
├── Number                (§3.1.1)
├── StringLiteral         (§3.1.14)
├── Result                (§3.1.5)
├── Nothing               (§3.1.13)
├── FieldAccess           (§3.1.3)
├── SubscriptAccess       (§3.1.4)
├── ChainedSubscript      (§3.1.4b)
├── ArrayLength           (§3.1.8)
├── AssignsRegion         (§3.4.5)
├── Valid                 (§3.1.9)
├── Separated             (§3.1.10)
├── Length2D              (§3.1.11)
├── Valid2D               (§3.1.12)
├── At                    (§3.1.7)
├── IsSorted              (§3.1.15)
├── Sum                   (§3.1.16)
├── CallExpr              (§3.1.17)
├── CSLBool               (§3.1.18)
├── CSLNone               (§3.1.19)
├── CSLIn                 (§3.2.6b)
├── CSLNotIn              (§3.2.6b)
├── CSLSlice              (§3.1.20)
├── Assigns               (§2.1.3)
├── ClassInvariant        (§2.3.1)
├── Label                 (§2.4.1)
├── FunctionVariant       (§2.1.4, §2.1.5)
├── Diverges              (§2.1.6)
├── Trusted               (§2.1.7)
├── GhostAssignDecl       (§2.4.2, §2.4.3)
├── RaisesDecl            (§2.1.9)
├── BoundedIntDecl        (§2.1.8)
├── SharedDecl            (§5.4.1)
├── ThreadEntry           (§2.1.10)
├── Acquires              (§2.4.5)
├── Releases              (§2.4.6)
├── CriticalSection       (§2.4.4)
├── MutexInvariant        (§5.4.2)
└── LockOrder             (§5.4.3)
```

---

## Appendix B. Test Coverage Matrix

Every grammar production must have at least one test in
`test-suite/corpus/pycsl-reference/`. This table lists coverage status
(extracted from `test-suite/traceability-pycsl.md`):

| Production | Reference | Test IDs | Status |
|-----------|-----------|----------|--------|
| `precondition` | §2.1.1 | 0001, 0066, 0067 | ✅ PASS |
| `postcondition` | §2.1.2 | 0002, 0068, 0069 | ✅ PASS |
| `assigns` | §2.1.3 | 0003, 0070, 0071 | ✅ PASS |
| `function_variant` | §2.1.4 | 0049, 0156, 0157 | ✅ PASS |
| `function_variant_structural` | §2.1.5 | 0050 | ⚠️ XFAIL |
| `diverges_decl` | §2.1.6 | 0051, 0158, 0159 | ✅ PASS |
| `trusted_decl` | §2.1.7 | 0052, 0160, 0161 | ✅ PASS |
| `bounded_int_decl` | §2.1.8 | 0202, 0203, 0204 | ✅ PASS |
| `raises_decl` | §2.1.9 | 0205, 0206 | ✅ PASS |
| `thread_entry_decl` | §2.1.10 | 0250–0253, 0277 | ✅ PASS |
| `loop_invariant` | §2.2.1 | 0004, 0072, 0073 | ✅ PASS |
| `loop_variant` | §2.2.2 | 0005, 0074, 0075 | ✅ PASS |
| `class_invariant` | §2.3.1 | 0006, 0076, 0077, 0191–0193 | ✅ PASS |
| `label_decl` | §2.4.1 | 0007, 0078, 0079 | ✅ PASS |
| `ghost_assign` | §2.4.2 | 0207–0209 | ✅ PASS |
| `ghost_aug_assign` | §2.4.3 | 0207–0209 | ✅ PASS |
| `critical_decl` | §2.4.4 | 0250–0253, 0278 | ✅ PASS |
| `acquires_decl` | §2.4.5 | 0262–0266 | ✅ PASS |
| `releases_decl` | §2.4.6 | 0267–0271 | ✅ PASS |
| `NUMBER` | §3.1.1 | 0008, 0080, 0081 | ✅ PASS |
| `var` | §3.1.2 | 0009, 0082, 0083 | ✅ PASS |
| `field_access` | §3.1.3 | 0010 | ⚠️ XFAIL |
| `subscript_access` | §3.1.4 | 0011, 0084, 0085 | ✅ PASS |
| `chained_subscript` | §3.1.4b | 0018, 0019 | ✅ PASS |
| `result` | §3.1.5 | 0012, 0086, 0087 | ✅ PASS |
| `old_var` | §3.1.6 | 0013, 0088, 0089 | ✅ PASS |
| `at_expr` | §3.1.7 | 0014, 0090, 0091 | ✅ PASS |
| `array_length` | §3.1.8 | 0015, 0092, 0093 | ✅ PASS |
| `valid_pred` | §3.1.9 | 0016, 0094, 0095 | ✅ PASS |
| `separated_pred` | §3.1.10 | 0017, 0096, 0097 | ✅ PASS |
| `length2d_pred` | §3.1.11 | 0018 | ✅ PASS |
| `valid2d_pred` | §3.1.12 | 0019 | ✅ PASS |
| `nothing` | §3.1.13 | 0020, 0098, 0099 | ✅ PASS |
| `string_literal` | §3.1.14 | 0188–0190 | ✅ PASS |
| `is_sorted_expr` | §3.1.15 | 0197–0199 | ✅ PASS |
| `sum_expr` | §3.1.16 | 0197–0199 | ✅ PASS |
| `call_expr` | §3.1.17 | 0194–0196 | ✅ PASS |
| `true_lit` / `false_lit` | §3.1.18 | 0227, 0228 | ✅ PASS |
| `none_lit` | §3.1.19 | 0229 | ✅ PASS |
| `slice_access` | §3.1.20 | 0236, 0237 | ✅ PASS |
| Quantifiers | §3.2.1 | 0021, 0100, 0101 | ✅ PASS |
| `IMPL_OP` | §3.2.2 | 0022, 0102, 0103 | ✅ PASS |
| `OR_OP` | §3.2.3 | 0023, 0104, 0105 | ✅ PASS |
| `AND_OP` | §3.2.4 | 0024, 0106, 0107 | ✅ PASS |
| `EQ_OP` | §3.2.5 | 0025, 0108, 0109 | ✅ PASS |
| `COMP_OP` | §3.2.6 | 0026, 0110, 0111 | ✅ PASS |
| `in` / `not in` | §3.2.6b | 0230–0232 | ✅ PASS |
| `ADD_OP` | §3.2.7 | 0027, 0112, 0113 | ✅ PASS |
| `MUL_OP` | §3.2.8 | 0028, 0114, 0115 | ✅ PASS |
| `UNARY_OP` | §3.2.9 | 0029, 0116, 0117 | ✅ PASS |
| `assigns_region` | §3.4.5 | 0034, 0126, 0127 | ✅ PASS |
| `shared_decl` | §5.4.1 | 0250–0253, 0272–0276, 0280 | ✅ PASS |
| `mutex_invariant_decl` | §5.4.2 | 0250–0253, 0279 | ✅ PASS |
| `lock_order_decl` | §5.4.3 | 0257–0261 | ✅ PASS |
| `result_subscript` | §3.1.5b | — | ❌ No dedicated test |

---

## Appendix C. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-20 | Initial release. Grammar extracted from Module2_Parser.py (Lark EBNF), normalized to ISO 14977 EBNF, cross-referenced against annotations.md §1–§8 and traceability-pycsl.md. |
