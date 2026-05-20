# PyCSL Translational Semantics Reference

**Version:** 1.0  
**Date:** 2025-07-11  
**Status:** Normative  
**Source of truth:** `Module5_IREmitter.py`, `Module6_WhyMLTranspiler.py`,
`test-suite/annotations.md`

---

## §1  Introduction

### §1.1  Purpose

This document defines the translation function

$$\mathcal{T} : \text{AnnotatedPython} \to \text{WhyML}$$

that maps a valid Python program annotated with PyCSL contracts to a
Why3 WhyML module.  The function is **sound** in the following sense:

> If $\text{Why3} \vdash \mathcal{T}\llbracket P \rrbracket \;\textbf{Valid}$,
> then $P \models \text{Spec}(P)$.

Because Why3's WP calculus and type system are already formally defined
(Filliâtre & Paskevich, ESOP 2013; mechanized in Coq by Clochard et al.),
the soundness obligation reduces to proving that $\mathcal{T}$ is a
faithful translation — that is, the WhyML output has the same semantic
content as the original annotated Python.

### §1.2  Scope

This document covers:

- The complete translation of every PyCSL construct to WhyML
- All four memory models (Hoare, Typed, Store, Concurrent)
- Concrete before/after examples from the reference test suite
- A semi-formal soundness argument with trust boundaries

This document does **not** cover:

- Concrete syntax of PyCSL (see `pycsl-concrete-syntax-reference.md`)
- Static well-formedness rules (see `pycsl-static-semantics-reference.md`)
- Why3's internal WP calculus (see Why3 Reference Manual)
- SMT encoding of Why3 goals (delegated to Alt-Ergo, Z3, CVC5)

### §1.3  Architecture of $\mathcal{T}$

The implementation decomposes $\mathcal{T}$ into two composed functions:

$$\mathcal{T} = \mathcal{W} \circ \mathcal{I}$$

where:

| Component | Implementation | Role |
|-----------|----------------|------|
| $\mathcal{I}$ | `Module5_IREmitter.py` (881 lines) | AnnotatedPython → IR (JSON) |
| $\mathcal{W}$ | `Module6_WhyMLTranspiler.py` (3002 lines) | IR → WhyML text |

The **IR** is a JSON-like intermediate representation with typed nodes:
`Function`, `Class`, `While`, `For`, `Assign`, `Return`, `Assert`,
`Subscript`, `BinOp`, `Call`, `GhostAssign`, `Label`, etc.

This reference defines $\mathcal{T}$ directly (Python → WhyML), noting
where the IR boundary falls.

### §1.4  Notation

| Symbol | Meaning |
|--------|---------|
| $\mathcal{T}\llbracket \cdot \rrbracket$ | Full translation (module level) |
| $\mathcal{T}_f\llbracket \cdot \rrbracket$ | Function-level translation |
| $\mathcal{T}_s\llbracket \cdot \rrbracket$ | Statement translator |
| $\mathcal{T}_e\llbracket \cdot \rrbracket$ | Expression translator |
| $\tau(\cdot)$ | Type mapping (Python annotation → WhyML type) |
| `!x` | WhyML dereference of ref cell `x` |
| `x := v` | WhyML ref assignment |

---

## §T.1  Module-Level Translation

_Corresponds to `annotations.md` §1 and §9._

### §T.1.1  Module Structure

$$\mathcal{T}\llbracket \texttt{module } M \rrbracket =
  \texttt{module PyCSL\_Program} \; \{ \; \text{prelude} \; ; \;
  \text{helpers} \; ; \; \text{types} \; ; \;
  \mathcal{T}_f\llbracket \text{functions} \rrbracket \; \}
  \; \texttt{end}$$

Every PyCSL translation produces a single WhyML module named
`PyCSL_Program`.  The module body consists of four sections emitted
in order:

1. **Prelude** — `use` imports for Why3 theories
2. **Helpers** — Division/modulo wrappers, exception declarations
3. **Type declarations** — Record types for classes
4. **Functions** — All translated functions

**Implementation:** `_emit_preamble` (L2526), `_emit_type_decls` (L2589),
`_emit_function` (L2853).

### §T.1.2  Prelude (Theory Imports)

The prelude depends on the memory model and which features are used:

**Always emitted:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref
```

**Conditionally emitted:**

| Condition | Import |
|-----------|--------|
| Arrays used (Hoare/Concurrent) | `use array.Array` |
| 2D arrays used (Hoare/Concurrent) | `use matrix.Matrix` |
| `min()`/`max()` used | `use int.MinMax` |
| Strings used | `use string.String` |
| Bounded integers declared | `use mach.int.Int{N}` |
| Typed/Store memory model | `use map.Map` + type/predicate decls |

**Implementation:** `_emit_preamble_uses` (L2418–2459).

### §T.1.3  Memory Model Prelude

#### Hoare Model (default)

No additional declarations beyond the conditional imports above.

#### Typed Model

```whyml
  use map.Map
  type loc = int
  constant max_addr : int = 1073741824
  val ghost int_mem : ref (map loc int)

  predicate valid (m: map loc int) (base: loc) (n: int) =
    n >= 0 /\ base >= 0 /\ base + n <= max_addr

  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =
    a + na <= b \/ b + nb <= a
```

**Verified example (test 0080):**
```python
#@ ensures \result == 0
def test_zero_literal() -> int:
    return 0
```
→
```whyml
  use map.Map
  type loc = int
  constant max_addr : int = 1073741824
  val ghost int_mem : ref (map loc int)
  predicate valid (m: map loc int) (base: loc) (n: int) = ...
  predicate separated (a: loc) (na: int) (b: loc) (nb: int) = ...

  let test_zero_literal () : int
    ensures  { (result = 0) }
    writes   { int_mem }
  = 0
```

#### Store Model

Same structure as Typed, but the heap variable name is `store` instead
of `int_mem`.

#### Concurrent Model

Same as Hoare for local state, plus shared-state declarations
(see §T.7.4).

### §T.1.4  Helper Functions

#### Division and Modulo Wrappers

When floor division (`//`) or modulo (`%`) appear in function bodies,
helper functions are emitted to enforce the division-by-zero precondition:

```whyml
  let pycsl_div (x: int) (y: int) : int
    requires { [@expl:division by zero] y <> 0 }
    ensures { result = div x y }
  = div x y

  let pycsl_mod (x: int) (y: int) : int
    requires { [@expl:modulo by zero] y <> 0 }
    ensures { result = mod x y }
  = mod x y
```

When `ZeroDivisionError` is declared as a raised exception, the helpers
use `raises` instead of `requires`:

```whyml
  let pycsl_div (x: int) (y: int) : int
    ensures { result = div x y }
    raises { ZeroDivisionError -> y = 0 }
  = if y = 0 then raise ZeroDivisionError else div x y
```

**Note:** In specification contexts (requires/ensures), `//` and `%`
translate directly to `div` and `mod` without the wrapper.

**Implementation:** `_emit_preamble_helpers` (L2486–2524).

#### Exception Declarations

When the function body contains early returns or the function declares
`raises`, exception types are emitted:

```whyml
  exception Return int        (* early return with value *)
  exception Return_void       (* early return from void function *)
  exception ValueError        (* user-declared exception *)
  exception ZeroDivisionError (* division-by-zero exception *)
```

**Implementation:** `_emit_preamble_exceptions` (L2461–2484).

---

## §T.2  Function Translation

_Corresponds to `annotations.md` §2.1._

### §T.2.1  Basic Function

$$\mathcal{T}_f\llbracket
  \texttt{def f(x}_1\texttt{:}\,T_1\texttt{, ...)} \to R \texttt{:} \;
  \texttt{\#@ requires } P \;
  \texttt{\#@ ensures } Q \;
  \texttt{body}
\rrbracket$$

$$= \texttt{let f (x}_1\texttt{: } \tau(T_1)\texttt{) ... : } \tau(R) \;
  \texttt{requires \{} \mathcal{T}_e\llbracket P \rrbracket \texttt{\}} \;
  \texttt{ensures  \{} \mathcal{T}_e\llbracket Q \rrbracket \texttt{\}} \;
  \texttt{=} \;
  \mathcal{T}_s\llbracket \text{body} \rrbracket$$

**Verified example (test 0001):**
```python
#@ requires x >= 0
#@ ensures \result >= 0
def test_precondition(x: int) -> int:
    return x + 1
```
→
```whyml
  let test_precondition (x: int) : int
    requires { (x >= 0) }
    ensures  { (result >= 0) }
  =
    (x + 1)
```

### §T.2.2  Type Mapping $\tau$

| Python type | WhyML type | Notes |
|-------------|-----------|-------|
| `int` | `int` | Arbitrary precision |
| `bool` | `int` | `True` → `1`, `False` → `0` in body; `true`/`false` in spec |
| `str` | `int` | Strings hashed to integer |
| `float` | `int` | **Unsound** — no float theory |
| `list` | `array int` | Hoare/Concurrent model |
| `list` | `loc` + `_len` | Typed/Store model |
| `None` / `-> None` | `unit` | Return type for void functions |
| Class `C` | Record type `c` | Lowercase name |
| No annotation | `int` | Default |

### §T.2.3  Recursive Functions

When the call graph contains a cycle, `let rec` replaces `let`.
A `variant` clause is required for termination:

$$\mathcal{T}_f\llbracket \texttt{def f(...): \#@ variant V ...} \rrbracket
= \texttt{let rec f (...) : R} \;
  \texttt{variant \{} \mathcal{T}_e\llbracket V \rrbracket \texttt{\} with subterm} \;
  \texttt{= ...}$$

**Verified example (test 0050):**
```python
#@ requires n >= 0
#@ ensures \result >= 0
#@ variant n
def count_down(n: int) -> int:
    if n <= 0:
        return 0
    return count_down(n - 1) + 1
```
→
```whyml
  let rec count_down (n: int) : int
    requires { (n >= 0) }
    ensures  { (result >= 0) }
    variant  { n } with subterm
  =
    try
    if (n <= 0) then begin
      raise (Return 0)
    end else begin
      raise (Return ((count_down (n - 1)) + 1))
    end
    with Return r -> r end
```

**Note:** Early returns in recursive functions use the exception
mechanism (see §T.5.7).

### §T.2.4  Mutually Recursive Functions (SCC)

For strongly connected components (SCCs), the first function uses
`let rec` and subsequent functions use `and`:

```whyml
  let rec f (...) = ...
  and g (...) = ...
```

### §T.2.5  Pure (Logic) Functions

When the function body is a single expression with no mutation,
it is emitted as a `let function`:

```whyml
  let function f (x: int) (y: int) : int
    ensures  { (result = (x + y)) }
  =
    (x + y)
```

**Verified example (test 0020):**
```python
#@ ensures \result == x + y
def test_nothing(x: int, y: int) -> int:
    return x + y
```
→
```whyml
  let function test_nothing (x: int) (y: int) : int
    ensures  { (result = (x + y)) }
  =
    (x + y)
```

### §T.2.6  Trusted Functions (`\trusted`)

$$\mathcal{T}_f\llbracket \texttt{def f(...): \#@ \\trusted ...} \rrbracket
= \texttt{val f (...) : R requires \{...\} ensures \{...\}}$$

The keyword `val` declares the function signature with contracts but
**no body**.  The contracts are assumed as axioms — the function is
trusted, not verified.

### §T.2.7  Diverging Functions (`\diverges`)

The `diverges` keyword omits the termination obligation.  No `variant`
clause is emitted, and WhyML does not require a termination proof:

```whyml
  let f (...) : R
    diverges
  = ...
```

### §T.2.8  Exception-Raising Functions (`raises`)

$$\mathcal{T}_f\llbracket \texttt{\#@ raises E when cond} \rrbracket
= \texttt{raises \{ E ->} \mathcal{T}_e\llbracket \text{cond} \rrbracket \texttt{\}}$$

**Verified example (test 0206):**
```python
#@ ensures \result >= 0
#@ raises ValueError when n < 0
def checked_abs(n: int) -> int:
    if n < 0:
        raise ValueError
    return n
```
→
```whyml
  exception ValueError

  let checked_abs (n: int) : int
    ensures  { (result >= 0) }
    raises { ValueError -> (n < 0) }
  =
    if (n < 0) then begin
      raise ValueError
    end;
    n
```

**Implementation:** `_emit_contracts` (L2760–2795), `_emit_function`
(L2853–2911).

---

## §T.3  Loop Translation

_Corresponds to `annotations.md` §2.2._

### §T.3.1  While Loop

$$\mathcal{T}_s\llbracket
  \texttt{while C:} \;
  \texttt{\#@ loop invariant I} \;
  \texttt{\#@ loop variant V} \;
  \texttt{body}
\rrbracket$$

$$= \texttt{while } \mathcal{T}_e\llbracket C \rrbracket \texttt{ do} \;
  \texttt{invariant \{} \mathcal{T}_e\llbracket I \rrbracket \texttt{\}} \;
  \texttt{variant \{} \mathcal{T}_e\llbracket V \rrbracket \texttt{\}} \;
  \mathcal{T}_s\llbracket \text{body} \rrbracket \;
  \texttt{done}$$

**Verified example (test 0004):**
```python
#@ requires n >= 0
#@ ensures \result == n * (n - 1) // 2
def test_loop_invariant(n: int) -> int:
    s = 0
    i = 0
    #@ loop invariant s == i * (i - 1) // 2
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        s += i
        i += 1
    return s
```
→
```whyml
  let test_loop_invariant (n: int) : int
    requires { (n >= 0) }
    ensures  { (result = (div (n * (n - 1)) 2)) }
  =
    let s = ref 0 in
    let i = ref 0 in
    s := 0;
    i := 0;
    while (!i < n) do
      invariant { (!s = (div (!i * (!i - 1)) 2)) }
      invariant { ((0 <= !i) && (!i <= n)) }
      variant { (n - !i) }
      s := (!s + !i);
      i := (!i + 1)
    done;
    !s
```

**Key observations:**

1. **Mutable locals become refs:** `let s = ref 0 in` followed by
   `s := 0` (initialization).
2. **Dereference in expressions:** All reads of mutable locals use `!x`.
3. **Division in spec vs body:** `//` in `ensures` → `div` directly;
   `//` in body → `pycsl_div` wrapper.
4. **Multiple invariants:** Each `loop invariant` produces a separate
   `invariant { ... }` clause.

### §T.3.2  For-Range Loop (Desugaring)

$$\mathcal{T}_s\llbracket \texttt{for x in range(n): body} \rrbracket$$

$$= \texttt{let x = ref 0 in} \;
  \texttt{while !x < } \mathcal{T}_e\llbracket n \rrbracket \texttt{ do} \;
  \texttt{invariant \{ 0 <= !x /\textbackslash{} !x <= }
    \mathcal{T}_e\llbracket n \rrbracket \texttt{ \}} \;
  \texttt{variant \{ } \mathcal{T}_e\llbracket n \rrbracket
    \texttt{ - !x \}} \;
  \mathcal{T}_s\llbracket \text{body} \rrbracket \texttt{;} \;
  \texttt{x := !x + 1} \;
  \texttt{done}$$

The desugaring automatically injects:
- A **bounds invariant**: `0 <= !x /\ !x <= n`
- A **variant**: `n - !x`

User-supplied invariants are merged with the implicit bounds invariant.

**Implementation:** `_handle_for_stmt` (L1543–1630),
`_classify_iterable` (L1510–1541).

### §T.3.3  For-Each over Array

$$\mathcal{T}_s\llbracket \texttt{for x in arr: body} \rrbracket$$

$$= \texttt{let \_idx\_x = ref 0 in} \;
  \texttt{while !\_idx\_x < (length arr) do} \;
  \texttt{invariant \{ ... \}} \;
  \texttt{variant \{ (length arr) - !\_idx\_x \}} \;
  \texttt{let x = ref (!\_idx\_x) in} \;
  \mathcal{T}_s\llbracket \text{body} \rrbracket \texttt{;} \;
  \texttt{\_idx\_x := !\_idx\_x + 1} \;
  \texttt{done}$$

**Verified example (test 0208):**
```python
#@ requires \length(arr) > 0
#@ ensures \result >= 0
def count_positive(arr: list) -> int:
    c = 0
    #@ ghost total = 0
    #@ loop invariant 0 <= c and c <= _idx_i
    #@ loop invariant total == _idx_i
    #@ loop variant \length(arr) - _idx_i
    for i in arr:
        if arr[i] > 0:
            c += 1
    return c
```
→
```whyml
  let count_positive (arr: array int) : int
    requires { ((length arr) > 0) }
    ensures  { (result >= 0) }
  =
    let i = ref 0 in
    let c = ref 0 in
    c := 0;
    let ghost total = ref 0 in
    ghost total := 0;
    let _idx_i = ref 0 in
    while !_idx_i < (length arr) do
      invariant { ((0 <= !c) && (!c <= !_idx_i)) }
      invariant { (!total = !_idx_i) }
      variant { ((length arr) - !_idx_i) }
      let i = ref (!_idx_i) in
      if (arr[!i] > 0) then begin
        c := (!c + 1)
      end;
      _idx_i := !_idx_i + 1
    done;
    !c
```

**Key observation:** The synthetic index variable `_idx_i` is introduced;
user invariants may reference it.

### §T.3.4  For-Each over Generic Iterable

When the iterable is not recognized as an array or `range()`, abstract
operations are emitted:

```whyml
  val iter_length (x: int) : int
  val iter_get (x: int) (i: int) : int
```

These are trusted (uninterpreted) functions, creating a trust boundary.

### §T.3.5  Continue and Break

**Continue:** When the loop body contains `continue`, the body is wrapped
in a try/with block:

```whyml
  while ... do
    ...
    try
      ... body with continue raising PyCSL_Continue ...
    with PyCSL_Continue -> ()
    end
  done
```

**Break:** When the loop body contains `break`, the entire loop is wrapped:

```whyml
  try
    while ... do
      ... body with break raising PyCSL_Break ...
    done
  with PyCSL_Break -> ()
  end
```

---

## §T.4  Class Translation

_Corresponds to `annotations.md` §2.3 and §6._

### §T.4.1  Class → WhyML Record

$$\mathcal{T}\llbracket
  \texttt{class C:} \;
  \texttt{\#@ class invariant I} \;
  \texttt{\_\_init\_\_(self, ...): self.f}_1 = v_1 \ldots
\rrbracket$$

$$= \texttt{type c = \{ mutable f}_1\texttt{: int; ... \}} \;
  \texttt{invariant \{} \mathcal{T}_e\llbracket I \rrbracket \texttt{\}} \;
  \texttt{by \{ f}_1 \texttt{= 0; ... \}}$$

**Verified example (test 0006):**
```python
#@ class invariant self._value >= 0
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```
→
```whyml
  type counter = { mutable _value: int }
    invariant { (_value >= 0) }
    by { _value = 0 }

  let counter__increment (self: counter) (amount: int) : int
    requires { (amount >= 0) }
    ensures  { (self._value = ((old self._value) + amount)) }
  =
    self._value <- (self._value + amount);
    self._value
```

**Key observations:**

1. **Class name lowercased:** `Counter` → `counter`
2. **Fields are mutable:** `mutable _value: int`
3. **Invariant witness:** `by { _value = 0 }` provides a default
   witness proving the invariant is satisfiable.
4. **Methods become top-level:** `increment` → `counter__increment`
   with explicit `self: counter` parameter.
5. **Field mutation:** `self._value += amount` → `self._value <- ...`
6. **`\old` on fields:** `\old(self._value)` → `(old self._value)`

### §T.4.2  Constructor (`__init__`)

The constructor is translated like any method.  The class invariant
is implicitly a postcondition of the constructor (enforced by Why3's
type invariant mechanism — constructing a value of the record type
must satisfy the invariant).

### §T.4.3  Method Translation

Methods are emitted as top-level `let` functions with the naming
convention `classname__methodname`.  The `self` parameter has the
record type:

```whyml
  let classname__method (self: classname) (arg: int) : int = ...
```

**Implementation:** `_emit_type_decls` (L2589–2657).

---

## §T.5  Statement Translation ($\mathcal{T}_s$)

_Corresponds to `annotations.md` §2 (general flow)._

### §T.5.1  Variable Assignment

**First assignment (declaration):**

$$\mathcal{T}_s\llbracket x = e \rrbracket_{\text{first}}
= \texttt{let x = ref } \mathcal{T}_e\llbracket e \rrbracket
  \texttt{ in}$$

**Subsequent assignment (mutation):**

$$\mathcal{T}_s\llbracket x = e \rrbracket_{\text{later}}
= \texttt{x := } \mathcal{T}_e\llbracket e \rrbracket$$

**Verified example (test 0031):**
```python
#@ ensures \result == x + 1
def test_assigns_variable(x: int) -> int:
    y = x + 1
    return y
```
→
```whyml
  let test_assigns_variable (x: int) : int
    ensures  { (result = (x + 1)) }
  =
    let y = ref 0 in
    y := (x + 1);
    !y
```

**Implementation:** `_handle_assign_stmt` (L1372–1444).

### §T.5.2  Augmented Assignment

$$\mathcal{T}_s\llbracket x \mathrel{+}= e \rrbracket
= \texttt{x := !x + } \mathcal{T}_e\llbracket e \rrbracket$$

Similarly for `-=`, `*=`, `//=`, `%=`.

**Implementation:** `_handle_augassign_stmt` (L1939–1963).

### §T.5.3  Field Assignment

$$\mathcal{T}_s\llbracket \texttt{self.f = e} \rrbracket
= \texttt{self.f <- } \mathcal{T}_e\llbracket e \rrbracket$$

**Implementation:** `_handle_fieldassign_stmt` (L1965–1996).

### §T.5.4  Field Augmented Assignment

$$\mathcal{T}_s\llbracket \texttt{self.f += e} \rrbracket
= \texttt{self.f <- self.f + } \mathcal{T}_e\llbracket e \rrbracket$$

**Implementation:** `_handle_fieldaugassign_stmt` (L1998–2031).

### §T.5.5  Array Element Assignment

#### Hoare/Concurrent Model

$$\mathcal{T}_s\llbracket \texttt{arr[i] = e} \rrbracket
= \texttt{arr[}\mathcal{T}_e\llbracket i \rrbracket\texttt{] <- }
  \mathcal{T}_e\llbracket e \rrbracket$$

#### Typed/Store Model

$$\mathcal{T}_s\llbracket \texttt{arr[i] = e} \rrbracket
= \texttt{int\_mem := Map.set !int\_mem (arr + }
  \mathcal{T}_e\llbracket i \rrbracket\texttt{) }
  \mathcal{T}_e\llbracket e \rrbracket$$

**Verified example (test 0120):**
```python
#@ requires \length(arr) >= 1
#@ ensures arr[0] == 0
def test_assigns_elem(arr: list) -> None:
    arr[0] = 0
```
→
```whyml
  let test_assigns_elem (arr: array int) : unit
    requires { ((length arr) >= 1) }
    ensures  { (arr[0] = 0) }
  =
    arr[0] <- 0
```

**Implementation:** `_handle_array_set_stmt` (L1762–1811).

### §T.5.6  If-Else Statement

$$\mathcal{T}_s\llbracket \texttt{if C: S1 else: S2} \rrbracket
= \texttt{if } \mathcal{T}_e\llbracket C \rrbracket
  \texttt{ then begin } \mathcal{T}_s\llbracket S_1 \rrbracket
  \texttt{ end else begin } \mathcal{T}_s\llbracket S_2 \rrbracket
  \texttt{ end}$$

Conditions are coerced to boolean using `_to_bool()`.  In specification
contexts, Python boolean operators map directly to WhyML logical
connectives.  In body contexts, comparison results are wrapped in
`(if ... then 1 else 0)` when used as integer values.

**Implementation:** `_handle_if_stmt` (L1813–1854).

### §T.5.7  Return Statement

**Terminal return** (last statement in function):

$$\mathcal{T}_s\llbracket \texttt{return e} \rrbracket_{\text{tail}}
= \mathcal{T}_e\llbracket e \rrbracket$$

**Early return** (not the last statement, or inside a loop):

$$\mathcal{T}_s\llbracket \texttt{return e} \rrbracket_{\text{early}}
= \texttt{raise (Return } \mathcal{T}_e\llbracket e \rrbracket \texttt{)}$$

The function body is wrapped in:
```whyml
  try
    ... body ...
  with Return r -> r end
```

**Verified example (test 0102):**
```python
#@ ensures x >= 0 ==> \result == x
#@ ensures x < 0 ==> \result == 0 - x
def test_abs_impl(x: int) -> int:
    if x >= 0:
        return x
    else:
        return 0 - x
```
→
```whyml
  exception Return int

  let test_abs_impl (x: int) : int
    ensures  { ((x >= 0) -> (result = x)) }
    ensures  { ((x < 0) -> (result = (0 - x))) }
  =
    try
    if (x >= 0) then begin
      raise (Return x)
    end else begin
      raise (Return (0 - x))
    end
    with Return r -> r end
```

**Implementation:** `_handle_return_stmt` (L2033–2064).

### §T.5.8  Assert Statement

Python `assert` statements are runtime checks.  In the WhyML output
they are **skipped** (emitted as `()`), since PyCSL contracts are the
formal specification — Python asserts are not part of the verification
condition.

**Implementation:** `_stmts_to_whyml` (L2146–2150).

### §T.5.9  Raise Statement

$$\mathcal{T}_s\llbracket \texttt{raise E} \rrbracket
= \texttt{raise E}$$

Exception types must be pre-declared (see §T.1.4).

### §T.5.10  Try/Except Statement

$$\mathcal{T}_s\llbracket \texttt{try: S1 except E: S2} \rrbracket
= \texttt{try } \mathcal{T}_s\llbracket S_1 \rrbracket
  \texttt{ with E -> } \mathcal{T}_s\llbracket S_2 \rrbracket
  \texttt{ end}$$

Variables assigned in the try body are pre-declared as refs before the
`try` block to ensure they are in scope in the handler.

**Implementation:** `_handle_try_stmt` (L1632–1690).

### §T.5.11  Tuple Unpacking

$$\mathcal{T}_s\llbracket \texttt{a, b = f(x)} \rrbracket
= \texttt{let (\_t0, \_t1) = f x in} \;
  \texttt{a := \_t0; b := \_t1}$$

**Implementation:** `_handle_tuple_unpack_stmt` (L1722–1760).

### §T.5.12  Match/Case Statement

Match statements are translated to chained if/else:

$$\mathcal{T}_s\llbracket \texttt{match x: case p1: S1 case p2: S2 ...} \rrbracket$$
$$= \texttt{if } \text{cond}(p_1) \texttt{ then begin } \mathcal{T}_s\llbracket S_1 \rrbracket
  \texttt{ end else if } \text{cond}(p_2) \texttt{ then begin } \mathcal{T}_s\llbracket S_2 \rrbracket
  \texttt{ end ...}$$

Guards are combined with `&&`.

**Implementation:** `_handle_match_stmt` (L1856–1892).

---

## §T.6  Expression Translation ($\mathcal{T}_e$)

_Corresponds to `annotations.md` §3._

### §T.6.1  Literals

| Python/PyCSL | WhyML | Context | Notes |
|--------------|-------|---------|-------|
| Integer `n` | `n` | Both | Direct mapping |
| `True` | `true` | Spec | Boolean literal |
| `True` | `1` | Body | Integer encoding |
| `False` | `false` | Spec | Boolean literal |
| `False` | `0` | Body | Integer encoding |
| `None` | `0` | Both | Unit/zero encoding |
| String `"s"` | `hash("s") % 2^31` | Both | Hashed to integer |
| `[]` / Array literal | `(Array.make 1024 0)` | Body | Fixed-size default |
| `{}` / Dict literal | `(dict_new ())` | Body | Abstract operation |

**Implementation:** `_expr_to_whyml` (L1289–1341).

### §T.6.2  Variables

**In specification context (requires/ensures):**

$$\mathcal{T}_e\llbracket x \rrbracket_{\text{spec}}
= \texttt{!x} \quad \text{(ref dereferenced)}$$

**In body context:**

$$\mathcal{T}_e\llbracket x \rrbracket_{\text{body}}
= \texttt{!x} \quad \text{(ref dereferenced)}$$

Parameters (non-ref) are used directly without `!`.

**Implementation:** `_handle_var_expr` (L1012–1031).

### §T.6.3  Field Access

$$\mathcal{T}_e\llbracket \texttt{self.f} \rrbracket
= \texttt{self.f}$$

Record field access is direct — no dereference needed since `self` is
passed by reference in WhyML's record semantics.

**Implementation:** `_handle_field_get_expr` (L1033–1052).

### §T.6.4  Array/List Subscript Access

#### Hoare/Concurrent Model

$$\mathcal{T}_e\llbracket \texttt{arr[i]} \rrbracket
= \texttt{arr[}\mathcal{T}_e\llbracket i \rrbracket\texttt{]}$$

#### Typed/Store Model

$$\mathcal{T}_e\llbracket \texttt{arr[i]} \rrbracket
= \texttt{(Map.get !int\_mem (arr + }
  \mathcal{T}_e\llbracket i \rrbracket\texttt{))}$$

**Implementation:** `_handle_subscript` (L943–996).

### §T.6.5  Special Atoms

#### `\result`

$$\mathcal{T}_e\llbracket \texttt{\\result} \rrbracket = \texttt{result}$$

Used only in `ensures` clauses (enforced by static semantics §E1).

#### `\old(e)`

$$\mathcal{T}_e\llbracket \texttt{\\old(e)} \rrbracket
= \texttt{(old } \mathcal{T}_e\llbracket e \rrbracket \texttt{)}$$

Special case for field access:
$$\mathcal{T}_e\llbracket \texttt{\\old(self.f)} \rrbracket
= \texttt{(old self.f)}$$

**Verified example (test 0013):**
```python
#@ ensures arr[0] == \old(arr[1])
#@ ensures arr[1] == \old(arr[0])
def test_old_expr(arr: list) -> None:
    tmp = arr[0]
    arr[0] = arr[1]
    arr[1] = tmp
```
→
```whyml
  let test_old_expr (arr: array int) : unit
    ...
    ensures  { (arr[0] = (old arr[1])) }
    ensures  { (arr[1] = (old arr[0])) }
  = ...
```

**Implementation:** `_handle_old_expr` (L1086–1099).

#### `\at(e, L)`

$$\mathcal{T}_e\llbracket \texttt{\\at(e, L)} \rrbracket
= \texttt{(}\mathcal{T}_e\llbracket e \rrbracket \texttt{ at L)}$$

Special case for `\at(e, PRE)`:
$$\mathcal{T}_e\llbracket \texttt{\\at(e, PRE)} \rrbracket
= \texttt{(old } \mathcal{T}_e\llbracket e \rrbracket \texttt{)}$$

Typed/Store model with subscript:
$$\mathcal{T}_e\llbracket \texttt{\\at(arr[i], L)} \rrbracket
= \texttt{(Map.get (int\_mem at L) (arr + }
  \mathcal{T}_e\llbracket i \rrbracket\texttt{))}$$

**Implementation:** `_handle_at_expr` (L1101–1118).

#### `\length(arr)`

##### Hoare/Concurrent Model

$$\mathcal{T}_e\llbracket \texttt{\\length(arr)} \rrbracket
= \texttt{(length arr)}$$

##### Typed/Store Model

$$\mathcal{T}_e\llbracket \texttt{\\length(arr)} \rrbracket
= \texttt{arr\_len}$$

A sidecar variable holds the array length.

**Implementation:** `_handle_arraylen_expr` (L1163–1174).

#### `\valid(arr, n)`

##### Hoare/Concurrent Model

$$\mathcal{T}_e\llbracket \texttt{\\valid(arr, n)} \rrbracket
= \texttt{(n >= 0 \&\& n <= length arr)}$$

##### Typed/Store Model

$$\mathcal{T}_e\llbracket \texttt{\\valid(arr, n)} \rrbracket
= \texttt{(valid !int\_mem arr n)}$$

Uses the predicate declared in the typed model prelude.

**Implementation:** `_handle_valid_expr` (L1176–1187).

#### `\separated(a, na, b, nb)`

##### Hoare/Concurrent Model

$$\mathcal{T}_e\llbracket \texttt{\\separated(a, na, b, nb)} \rrbracket
= \texttt{true}$$

**Note:** In the Hoare model, arrays are separate by construction (each
is an independent WhyML array object), so separation is trivially true.

##### Typed/Store Model

$$\mathcal{T}_e\llbracket \texttt{\\separated(a, na, b, nb)} \rrbracket
= \texttt{(separated a na b nb)}$$

Uses the predicate declared in the typed model prelude.

**Implementation:** `_handle_separated_expr` (L1189–1202).

#### `\is_sorted(arr, lo, hi)`

$$\mathcal{T}_e\llbracket \texttt{\\is\_sorted(arr, lo, hi)} \rrbracket
= \texttt{(forall \_si : int. lo <= \_si /\textbackslash{} \_si < hi - 1 -> arr[\_si] <= arr[\_si + 1])}$$

**Implementation:** `_handle_issorted_expr` (L1232–1244).

#### `\sum(arr, lo, hi)`

$$\mathcal{T}_e\llbracket \texttt{\\sum(arr, lo, hi)} \rrbracket
= \texttt{(pycsl\_sum arr lo hi)}$$

A recursive sum function is defined in the prelude when needed.

**Implementation:** `_handle_sum_node_expr` (L1246–1258).

#### `\nothing`

$$\mathcal{T}_e\llbracket \texttt{\\nothing} \rrbracket$$

In the context of `assigns`, indicates that the function modifies no
heap state.  See §T.9 for how this affects frame conditions.

### §T.6.6  Binary Operators

| PyCSL (spec) | WhyML (spec) | PyCSL (body) | WhyML (body) |
|-------------|-------------|-------------|-------------|
| `a + b` | `(a + b)` | `a + b` | `(a + b)` |
| `a - b` | `(a - b)` | `a - b` | `(a - b)` |
| `a * b` | `(a * b)` | `a * b` | `(a * b)` |
| `a // b` | `(div a b)` | `a // b` | `(pycsl_div a b)` |
| `a % b` | `(mod a b)` | `a % b` | `(pycsl_mod a b)` |
| `a == b` | `(a = b)` | `a == b` | `(if a = b then 1 else 0)` |
| `a != b` | `(a <> b)` | `a != b` | `(if a <> b then 1 else 0)` |
| `a < b` | `(a < b)` | `a < b` | `(if a < b then 1 else 0)` |
| `a <= b` | `(a <= b)` | ... | ... |
| `a > b` | `(a > b)` | ... | ... |
| `a >= b` | `(a >= b)` | ... | ... |
| `a and b` | `(a /\ b)` | `a and b` | `(if a /\ b then 1 else 0)` |
| `a or b` | `(a \/ b)` | `a or b` | `(if a \/ b then 1 else 0)` |
| `not a` | `(not a)` | `not a` | `(if not a then 1 else 0)` |
| `a ==> b` | `(a -> b)` | — | — |

**Key distinction:** In specification contexts, operators map to logical
connectives.  In body contexts, comparison and boolean operators are
wrapped in `(if ... then 1 else 0)` to produce integer results.

**Array repeat:** `[0] * n` → `(Array.make n 0)`

**Implementation:** `_handle_binop` (L686–771).

### §T.6.7  Quantifiers

$$\mathcal{T}_e\llbracket \texttt{\\forall x; body} \rrbracket
= \texttt{(forall x : int. } \mathcal{T}_e\llbracket \text{body} \rrbracket \texttt{)}$$

$$\mathcal{T}_e\llbracket \texttt{\\exists x; body} \rrbracket
= \texttt{(exists x : int. } \mathcal{T}_e\llbracket \text{body} \rrbracket \texttt{)}$$

**Verified example (test 0021/0100):**
```python
#@ ensures \forall i; 0 <= i and i < n ==> arr[i] >= 0
def test_quantifiers(arr: list, n: int) -> None:
```
→
```whyml
    ensures  { (forall i : int. (((0 <= i) && (i < n)) -> (arr[i] >= 0))) }
```

**Note:** Quantified variables are always typed as `int`.

**Implementation:** `_expr_to_whyml` (L1289–1341, Forall/Exists cases).

### §T.6.8  Function Calls

$$\mathcal{T}_e\llbracket f(e_1, \ldots, e_n) \rrbracket
= \texttt{(f } \mathcal{T}_e\llbracket e_1 \rrbracket \ldots
  \mathcal{T}_e\llbracket e_n \rrbracket \texttt{)}$$

**Built-in call translations:**

| Python | WhyML |
|--------|-------|
| `len(arr)` | `(length arr)` |
| `min(a, b)` | `(min a b)` |
| `max(a, b)` | `(max a b)` |
| `abs(x)` | `(if x >= 0 then x else -x)` |
| `int(x)` | `x` (identity) |
| `bool(x)` | `(if x <> 0 then 1 else 0)` |
| `isinstance(x, T)` | `true` (always true, single type) |
| `hasattr(x, a)` | `true` |
| `sum(arr)` | `(pycsl_sum arr 0 (length arr))` |

**Implementation:** `_handle_call_expr` (L863–941).

### §T.6.9  Conditional Expression

$$\mathcal{T}_e\llbracket \texttt{a if C else b} \rrbracket
= \texttt{(if } \mathcal{T}_e\llbracket C \rrbracket
  \texttt{ then } \mathcal{T}_e\llbracket a \rrbracket
  \texttt{ else } \mathcal{T}_e\llbracket b \rrbracket \texttt{)}$$

**Implementation:** `_handle_ifexpr_expr` (L1120–1133).

### §T.6.10  Named Expression (Walrus Operator)

$$\mathcal{T}_e\llbracket \texttt{(x := e)} \rrbracket$$

If `x` is already a ref:
$$= \texttt{(begin x := } \mathcal{T}_e\llbracket e \rrbracket
  \texttt{; !x end)}$$

If `x` is new:
$$= \texttt{(let x = ref } \mathcal{T}_e\llbracket e \rrbracket
  \texttt{ in !x)}$$

**Implementation:** `_handle_named_expr_expr` (L1135–1147).

### §T.6.11  Lambda Expression

$$\mathcal{T}_e\llbracket \texttt{lambda x: e} \rrbracket
= \texttt{(fun x -> } \mathcal{T}_e\llbracket e \rrbracket \texttt{)}$$

**Implementation:** `_handle_lambda_expr` (L1260–1270).

### §T.6.12  Slice Access

$$\mathcal{T}_e\llbracket \texttt{arr[lo:hi]} \rrbracket
= \texttt{(array\_slice arr lo hi)}$$

Where `array_slice` is an abstract trusted operation.

**Implementation:** `_handle_slice_access_expr` (L1149–1161).

### §T.6.13  2D Array Operations

$$\mathcal{T}_e\llbracket \texttt{\\length2d(m, rows, cols)} \rrbracket
= \texttt{(m.rows = rows \&\& m.columns = cols)}$$

$$\mathcal{T}_e\llbracket \texttt{\\valid2d(m, r, c)} \rrbracket
= \texttt{(valid\_index m r c)}$$

$$\mathcal{T}_s\llbracket \texttt{m[r][c] = e} \rrbracket
= \texttt{set m r c } \mathcal{T}_e\llbracket e \rrbracket$$

**Implementation:** `_handle_length2d_expr` (L1204–1216),
`_handle_valid2d_expr` (L1218–1230).

### §T.6.14  F-Strings

F-strings are translated as integer hash values since strings are
represented as integers:

$$\mathcal{T}_e\llbracket \texttt{f"..."} \rrbracket = \text{hash}(\ldots)$$

**Implementation:** `_handle_fstring_expr` (L1053–1069).

---

## §T.7  Memory Models

_Corresponds to `annotations.md` §5._

### §T.7.1  Hoare Model (Default)

The Hoare model uses WhyML's native `ref` cells and `array` types.

| Concept | Representation |
|---------|---------------|
| Mutable local | `let x = ref v in` |
| Array parameter | `arr: array int` |
| Array access | `arr[i]` |
| Array mutation | `arr[i] <- v` |
| Array length | `(length arr)` |
| Separation | `true` (trivially separate) |

This is the simplest and most efficient model.  The `\valid` and
`\separated` predicates become trivial or are expressed directly in
terms of WhyML array operations.

### §T.7.2  Typed Model

The Typed model introduces a flat memory map for pointer-like reasoning.

| Concept | Representation |
|---------|---------------|
| Heap | `val ghost int_mem : ref (map loc int)` |
| Array base address | `arr : loc` |
| Array length | `arr_len : int` (sidecar) |
| Array access | `(Map.get !int_mem (arr + i))` |
| Array mutation | `int_mem := Map.set !int_mem (arr + i) v` |
| `\valid(arr, n)` | `(valid !int_mem arr n)` — predicate checking bounds |
| `\separated(a, na, b, nb)` | `(separated a na b nb)` — non-overlapping ranges |
| Frame condition | `ensures { forall l: int. ¬in_range(l) -> Map.get !int_mem l = Map.get (old !int_mem) l }` |

### §T.7.3  Store Model

Identical to the Typed model but with the heap variable named `store`
instead of `int_mem`.

### §T.7.4  Concurrent Model

The Concurrent model extends Hoare with shared state and mutex invariants.

#### Shared State Declarations

Module-level variables annotated as shared are emitted as `val` (global
mutable refs):

```whyml
  val counter : ref int
```

#### Mutex Invariants

```whyml
  predicate lock_counter_inv = (!counter >= 0)

  let _check_initial_lock_counter () : unit =
    assert { lock_counter_inv }
```

#### Critical Sections

$$\mathcal{T}_s\llbracket \texttt{critical m: body} \rrbracket$$

On entry (acquire semantics):
```whyml
  (* Havoc shared variables *)
  let _any_counter_0 = any int in
  counter := _any_counter_0;
  assume { lock_counter_inv };
```

On exit (release semantics):
```whyml
  assert { lock_counter_inv };
```

**Verified example (test 0250):**
```python
#@ shared counter
#@ mutex_invariant lock_counter: counter >= 0
#@ \diverges
#@ thread_entry
def worker() -> int:
    #@ critical lock_counter
    counter += 1
    return 0
```
→
```whyml
  val counter : ref int
  predicate lock_counter_inv = (!counter >= 0)
  let _check_initial_lock_counter () : unit =
    assert { lock_counter_inv }

  let worker () : int
    diverges
  =
    let _any_counter_0 = any int in
    counter := _any_counter_0;
    assume { lock_counter_inv };
    counter := !counter + 1;
    assert { lock_counter_inv };
    0
```

**Semantics:** The havoc+assume pattern models the fact that other threads
may have modified shared state arbitrarily, subject to the mutex
invariant.  The assert at exit proves that the critical section
maintains the invariant.

**Implementation:** `_emit_shared_state` (L2538–2583),
`_handle_critical_section_stmt` (L1894–1937).

---

## §T.8  Ghost and Label Translation

_Corresponds to `annotations.md` §2.4 and §7._

### §T.8.1  Ghost Variable Declaration

$$\mathcal{T}_s\llbracket \texttt{\#@ ghost x = e} \rrbracket
= \texttt{let ghost x = ref } \mathcal{T}_e\llbracket e \rrbracket
  \texttt{ in}$$

### §T.8.2  Ghost Variable Update

$$\mathcal{T}_s\llbracket \texttt{\#@ ghost x += e} \rrbracket
= \texttt{ghost x := !x + } \mathcal{T}_e\llbracket e \rrbracket$$

Similarly for `ghost x -= e`, `ghost x *= e`.

**Verified example (test 0207):**
```python
#@ requires n >= 0
#@ ensures \result == n
def count_to_n(n: int) -> int:
    i = 0
    #@ ghost count = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant count == i
    #@ loop variant n - i
    while i < n:
        #@ ghost count += 1
        i += 1
    return i
```
→
```whyml
  let count_to_n (n: int) : int
    requires { (n >= 0) }
    ensures  { (result = n) }
  =
    let i = ref 0 in
    i := 0;
    let ghost count = ref 0 in
    ghost count := 0;
    while (!i < n) do
      invariant { ((0 <= !i) && (!i <= n)) }
      invariant { (!count = !i) }
      variant { (n - !i) }
      ghost count := !count + 1;
      i := (!i + 1)
    done;
    !i
```

**Key observations:**

1. Ghost variables are declared with `let ghost` — they exist only
   for specification purposes and are erased at compilation.
2. Ghost updates use `ghost x := ...` — the `ghost` keyword tells
   Why3 the update has no computational effect.
3. Ghost variables can appear in loop invariants and ensures clauses.

**Implementation:** `_handle_ghost_assign_stmt` (L1692–1720).

### §T.8.3  Labels

$$\mathcal{T}_s\llbracket \texttt{\#@ label L} \rrbracket
= \texttt{label L in}$$

Labels mark program points for `\at(e, L)` expressions.

**Verified example (test 0014):**
```python
#@ ensures arr[0] == \old(arr[0]) + 2
def test_at_expr(arr: list) -> None:
    #@ label MID
    arr[0] = arr[0] + 1
    arr[0] = arr[0] + 1
```
→
```whyml
  let test_at_expr (arr: array int) : unit
    ...
    ensures  { (arr[0] = ((old arr[0]) + 2)) }
  =
    label MID in
    arr[0] <- (arr[0] + 1);
    arr[0] <- (arr[0] + 1)
```

**Implementation:** `_stmts_to_whyml` (L2107–2112).

---

## §T.9  Assigns Frame Translation

_Corresponds to `annotations.md` §3.4._

### §T.9.1  Frame Conditions

The `assigns` clause specifies which mutable state a function may modify.
The translation depends on the memory model.

#### Hoare/Concurrent Model

In the Hoare model, frame conditions are handled implicitly by WhyML's
type system — arrays and refs that are not passed as parameters cannot
be modified.  No explicit `writes` clause is emitted.

#### Typed/Store Model

$$\mathcal{T}\llbracket \texttt{\#@ assigns \\nothing} \rrbracket$$

$$= \texttt{ensures  \{ !int\_mem = old !int\_mem \}}$$

This states that the heap is unchanged.

$$\mathcal{T}\llbracket \texttt{\#@ assigns arr[lo..hi]} \rrbracket$$

$$= \texttt{writes   \{ int\_mem \}} \\
  \texttt{ensures  \{ forall l: int. not (arr + lo <= l < arr + hi)} \\
  \quad\texttt{-> Map.get !int\_mem l = Map.get (old !int\_mem) l \}}$$

This emits both a `writes` clause (declaring that the heap may change)
and a frame postcondition (asserting that all locations outside the
assigned region are unchanged).

### §T.9.2  Multiple Assigns Regions

When multiple regions are assigned, the frame condition excludes all
of them:

$$\forall l.\;\lnot\bigl(\text{in\_region}_1(l) \lor \text{in\_region}_2(l)
  \lor \ldots\bigr) \Rightarrow
  \text{Map.get}(!h, l) = \text{Map.get}(\text{old}\;!h, l)$$

**Implementation:** `_emit_frame_condition` (L2186–2220).

---

## §T.10  Soundness Argument

### §T.10.1  Axiomatization (Trust Base)

The following are assumed without proof and constitute the trust base
of the translation:

| Axiom | Source | Risk |
|-------|--------|------|
| Why3's WP calculus is sound | Filliâtre & Paskevich, ESOP 2013 | Low (mechanized in Coq) |
| Alt-Ergo / Z3 / CVC5 are correct | SMT solver implementations | Low (extensively tested) |
| `\trusted` function contracts | User-supplied axioms | **High** — not verified |
| Library stubs (`data/lib_stubs/`) | Hand-written contracts | **Medium** — not verified |
| Abstract operations (`val iter_length`, etc.) | Transpiler-generated | **Medium** — uninterpreted |
| Integer arithmetic is unbounded | Python semantics | Low (CPython uses bigints) |
| Python's `//` matches Euclidean `div` | Language semantics | **Note**: Python uses floored division, which differs from Euclidean for negative operands |

### §T.10.2  Preservation Lemmas

For each $\mathcal{T}$ rule, we argue informally that the translation
is faithful:

#### Expression Faithfulness

**Claim:** $\mathcal{T}_e$ preserves evaluation semantics.

- **Integer arithmetic:** `+`, `-`, `*` map directly.  WhyML integers
  are arbitrary-precision, matching Python's `int`.
- **Division:** `//` maps to Euclidean `div` (with caveat: Python uses
  floored division for negative operands — see §T.10.1).
- **Comparisons:** `==`, `!=`, `<`, `<=`, `>`, `>=` map to `=`, `<>`,
  `<`, `<=`, `>`, `>=` respectively.
- **Boolean operators:** `and`/`or`/`not` map to `/\`/`\/`/`not` in
  spec; to `(if ... then 1 else 0)` in body, preserving Python's
  int-bool duality.
- **Array access:** `arr[i]` maps to WhyML array indexing (Hoare) or
  `Map.get` (Typed/Store), both of which model random-access reads.

#### Statement Faithfulness

**Claim:** $\mathcal{T}_s$ preserves control flow.

- **Sequential composition:** Statements separated by `;` in WhyML.
- **Branching:** `if/else` maps directly to `if/then/else`.
- **Loops:** `while` maps directly with invariant/variant annotations.
- **For loops:** Desugared to `while` with explicit index — the index
  increment and bounds invariant faithfully model `range()` semantics.
- **Early return:** Modeled via exceptions (`raise Return v`), which is
  sound because WhyML exceptions have the same control-flow semantics
  as Python exceptions.

#### Contract Faithfulness

**Claim:** Contracts map one-to-one to WhyML pre/postconditions.

- Each `requires` → one `requires { ... }` clause
- Each `ensures` → one `ensures { ... }` clause
- Each `loop invariant` → one `invariant { ... }` clause
- Each `loop variant` → one `variant { ... }` clause
- Each `raises E when cond` → one `raises { E -> cond }` clause

No contracts are dropped or rewritten during translation.

#### Frame Faithfulness

**Claim:** `assigns` maps to WhyML writes + unchanged conditions.

- `assigns \nothing` → heap equality postcondition
- `assigns arr[lo..hi]` → `writes { int_mem }` + frame postcondition
  excluding the assigned region

### §T.10.3  Trust Boundaries

The following Python features are **not verified** and constitute the
boundary beyond which PyCSL provides no guarantees:

| Feature | Status | Reason |
|---------|--------|--------|
| Python GC / reference counting | Not modeled | WhyML has no GC theory |
| Floating-point arithmetic | Not supported | No float theory in translation |
| Integer overflow | Modeled as unbounded | Matches Python semantics |
| String operations | Hashed to int | Lossy — collisions possible |
| I/O (file, network, print) | Not modeled | Side effects beyond formal model |
| Dynamic typing / duck typing | Static types assumed | Annotation must provide types |
| Exceptions not declared in `raises` | Not tracked | Only declared exceptions modeled |
| `eval()`, `exec()`, `__import__` | Not supported | Dynamic code not analyzable |
| Generators, async/await, yield | Not supported | Not in formal model |
| Metaclasses, descriptors | Not supported | Not in formal model |

### §T.10.4  Relationship to Formal Semantics

The Rocq and Lean proofs in `src/formal-semantics/` mechanize the WP
calculus soundness for the core language subset (arithmetic, assignment,
sequencing, while loops, if/else).  These proofs establish that if the
WP calculus says a program satisfies its specification, then any concrete
execution of the program in the formal operational semantics also
satisfies the specification.

The translation $\mathcal{T}$ maps Python constructs into this verified
core.  Constructs outside the core (exceptions, classes, arrays) are
modeled using Why3's built-in theories, whose soundness is established
by the Why3 project itself.

---

## §T.11  Gap Analysis

### §T.11.1  Translation Gaps

| ID | Gap | Impact | Recommendation |
|----|-----|--------|----------------|
| G1 | Python floored division vs WhyML Euclidean division | For negative operands, `(-7) // 2` is `-4` in Python but `div (-7) 2 = -3` in WhyML | Add a `pycsl_floordiv` helper that matches Python semantics |
| G2 | String hashing is lossy | Two different strings may hash to the same integer | Document limitation; add `string.String` theory support |
| G3 | Boolean/int duality | `True + 1 = 2` in Python; in spec `true + 1` is a type error | The spec/body distinction handles this, but mixed use is fragile |
| G4 | `None` mapped to `0` | `None` and `0` are indistinguishable in WhyML | Use `option` type for nullable values |
| G5 | Array literals use fixed size 1024 | `[]` becomes `Array.make 1024 0` regardless of actual size | Use dynamic allocation or parametric size |
| G6 | Dict/Set/ListComp are abstract | `{}`, `[x for x in ...]`, `{k:v for ...}` use uninterpreted functions | Implement concrete dict/set theories |
| G7 | `isinstance` / `hasattr` always `true` | Single type system limitation | Support union types or tagged variants |
| G8 | For-each over non-array iterables | Uses abstract `iter_length` / `iter_get` | Provide concrete implementations per type |

### §T.11.2  Undocumented Features

The following translations are implemented in code but were not
specified in `test-suite/annotations.md`:

| Feature | Implementation | Note |
|---------|---------------|------|
| `\result[i]` | Subscript with Result base | Subscript access on return value |
| `bounded_int(N)` | `use mach.int.IntN` | Machine-width integers |
| Chained subscript `arr[i][j]` | Nested Subscript nodes | 2D array access pattern |
| Walrus operator `:=` | `_handle_named_expr_expr` | Python 3.8+ named expressions |
| F-string expressions | `_handle_fstring_expr` | Hashed to integer |
| `with` statement | `_handle_with_stmt` | Context manager protocol |
| `delete` statement | `_handle_delete_stmt` | Variable deletion |

### §T.11.3  Missing Translations

The following constructs appear in Python but have no translation:

| Construct | Status | Workaround |
|-----------|--------|------------|
| `class` inheritance | Not supported | Flatten class hierarchy |
| `@property`, `@staticmethod` | Not supported | Use plain methods |
| `*args`, `**kwargs` | Not supported | Use explicit parameters |
| `yield` / generators | Not supported | Use explicit loops |
| `async` / `await` | Not supported | Use concurrent model |
| `global` / `nonlocal` | Not supported | Use explicit parameter passing |
| List/dict comprehensions (concrete) | Abstract only | Use explicit loops |

---

## §T.12  Complete Method Index

### Module5 CSL Node Handlers

| Handler | CSL Node | IR Type |
|---------|----------|---------|
| `_csl_binop` | `CSLBinOp` | `BinOp` |
| `_csl_unaryop` | `CSLUnaryOp` | `UnaryOp` |
| `_csl_field_access` | `CSLFieldAccess` | `FieldGet` |
| `_csl_var` | `CSLVar` | `Var` |
| `_csl_number` | `CSLNumber` | `Number` |
| `_csl_string` | `CSLStringLiteral` | `String` |
| `_csl_bool` | `CSLBool` | `Bool` |
| `_csl_none` | `CSLNone` | `None` |
| `_csl_result` | `CSLResult` | `Result` |
| `_csl_old` | `CSLOld` | `Old` / `OldField` |
| `_csl_nothing` | `Nothing` | `Nothing` |
| `_csl_forall` | `Forall` | `Forall` |
| `_csl_exists` | `Exists` | `Exists` |
| `_csl_array_length` | `ArrayLength` | `ArrayLen` |
| `_csl_subscript` | `SubscriptAccess` | `Subscript` |
| `_csl_chained_subscript` | `ChainedSubscript` | Nested `Subscript` |
| `_csl_assigns_region` | `AssignsRegion` | `AssignsRegion` |
| `_csl_valid` | `Valid` | `Valid` |
| `_csl_separated` | `Separated` | `Separated` |
| `_csl_at` | `CSLAt` | `At` |
| `_csl_length2d` | `Length2D` | `Length2D` |
| `_csl_valid2d` | `Valid2D` | `Valid2D` |
| `_csl_contract_wrapper` | Requires/Ensures/LoopInvariant/LoopVariant | (wrapper) |
| `_csl_function_variant` | `FunctionVariant` | `FunctionVariant` |
| `_csl_call_expr` | `CallExpr` | `Call` |
| `_csl_is_sorted` | `IsSorted` | `IsSorted` |
| `_csl_sum` | `Sum` | `Sum` |
| `_csl_in` | `CSLIn` | `In` |
| `_csl_not_in` | `CSLNotIn` | `NotIn` |
| `_csl_slice` | `CSLSlice` | `Slice` |

### Module5 Python Statement Handlers

| Handler | Python AST | IR Statement |
|---------|-----------|-------------|
| `_py_stmt_assign` | `ast.Assign` | `Assign` / `FieldAssign` / `ArraySet` / `TupleUnpack` |
| `_py_stmt_augassign` | `ast.AugAssign` | `AugAssign` / `FieldAugAssign` |
| `_py_stmt_return` | `ast.Return` | `Return` |
| `_py_stmt_while` | `ast.While` | `While` |
| `_py_stmt_for` | `ast.For` | `For` |
| `_py_stmt_if` | `ast.If` | `IfElse` |
| `_py_stmt_continue` | `ast.Continue` | `Continue` |
| `_py_stmt_assert` | `ast.Assert` | `Assert` |
| `_py_stmt_raise` | `ast.Raise` | `Raise` |
| `_py_stmt_try` | `ast.Try` | `TryExcept` |
| `_py_stmt_with` | `ast.With` | `With` |
| `_py_stmt_pass` | `ast.Pass` | (skipped) |
| `_py_stmt_break` | `ast.Break` | `Break` |
| `_py_stmt_delete` | `ast.Delete` | `Delete` |

### Module6 Statement Handlers

| Handler | Line Range | IR → WhyML |
|---------|-----------|------------|
| `_handle_assign_stmt` | 1372–1444 | `Assign` → `let x = ref v in` / `x := v` |
| `_handle_while_stmt` | 1446–1508 | `While` → `while ... do ... done` |
| `_handle_for_stmt` | 1543–1630 | `For` → desugared `while` |
| `_handle_try_stmt` | 1632–1690 | `TryExcept` → `try ... with ... end` |
| `_handle_ghost_assign_stmt` | 1692–1720 | `GhostAssign` → `let ghost` / `ghost x :=` |
| `_handle_tuple_unpack_stmt` | 1722–1760 | `TupleUnpack` → `let (a, b) = ...` |
| `_handle_array_set_stmt` | 1762–1811 | `ArraySet` → `arr[i] <- v` / `Map.set` |
| `_handle_if_stmt` | 1813–1854 | `IfElse` → `if ... then ... else ...` |
| `_handle_match_stmt` | 1856–1892 | `Match` → chained `if/else` |
| `_handle_critical_section_stmt` | 1894–1937 | `Critical` → havoc+assume/assert |
| `_handle_augassign_stmt` | 1939–1963 | `AugAssign` → `x := !x op v` |
| `_handle_fieldassign_stmt` | 1965–1996 | `FieldAssign` → `self.f <- v` |
| `_handle_fieldaugassign_stmt` | 1998–2031 | `FieldAugAssign` → `self.f <- self.f op v` |
| `_handle_return_stmt` | 2033–2064 | `Return` → `v` / `raise (Return v)` |
| `_handle_expr_stmt` | 2066–2093 | `Expr` → expression as statement |
| `_stmts_to_whyml` | 2098–2184 | Dispatcher for all statement types |

### Module6 Expression Handlers

| Handler | Line Range | IR → WhyML |
|---------|-----------|------------|
| `_handle_binop` | 686–771 | `BinOp` → `(a op b)` |
| `_handle_len_call` | 773–804 | `len()` → `(length arr)` |
| `_handle_join_call` | 806–829 | `str.join()` → abstract |
| `_handle_sum_call` | 831–848 | `sum()` → `pycsl_sum` |
| `_handle_dotted_call` | 850–861 | `obj.method()` → abstract |
| `_handle_call_expr` | 863–941 | `Call` → `(f a b ...)` |
| `_handle_subscript` | 943–996 | `Subscript` → `arr[i]` / `Map.get` |
| `_handle_attribute_expr` | 997–1010 | `Attr` → `obj.field` |
| `_handle_var_expr` | 1012–1031 | `Var` → `!x` / `x` |
| `_handle_field_get_expr` | 1033–1052 | `FieldGet` → `self.f` |
| `_handle_fstring_expr` | 1053–1069 | F-string → hash |
| `_handle_unaryop_expr` | 1071–1084 | `UnaryOp` → `(- x)` / `(not x)` |
| `_handle_old_expr` | 1086–1099 | `Old` → `(old e)` |
| `_handle_at_expr` | 1101–1118 | `At` → `(e at L)` |
| `_handle_ifexpr_expr` | 1120–1133 | `IfExpr` → `(if c then a else b)` |
| `_handle_named_expr_expr` | 1135–1147 | Named expr → `(begin x := v; !x end)` |
| `_handle_slice_access_expr` | 1149–1161 | `Slice` → `(array_slice ...)` |
| `_handle_arraylen_expr` | 1163–1174 | `ArrayLen` → `(length arr)` |
| `_handle_valid_expr` | 1176–1187 | `Valid` → bounds check / `valid` predicate |
| `_handle_separated_expr` | 1189–1202 | `Separated` → `true` / `separated` predicate |
| `_handle_length2d_expr` | 1204–1216 | `Length2D` → dimension check |
| `_handle_valid2d_expr` | 1218–1230 | `Valid2D` → index validity |
| `_handle_issorted_expr` | 1232–1244 | `IsSorted` → `forall` quantification |
| `_handle_sum_node_expr` | 1246–1258 | `Sum` → `(pycsl_sum arr lo hi)` |
| `_handle_lambda_expr` | 1260–1270 | `Lambda` → `(fun x -> e)` |
| `_handle_setlit_expr` | 1272–1284 | `SetLit` → `(set_empty ())` |
| `_expr_to_whyml` | 1289–1341 | Main dispatcher for all expression types |

### Module6 Emission Functions

| Function | Line Range | Purpose |
|----------|-----------|---------|
| `_emit_preamble_uses` | 2418–2459 | Theory `use` imports |
| `_emit_preamble_exceptions` | 2461–2484 | Exception declarations |
| `_emit_preamble_helpers` | 2486–2524 | `pycsl_div` / `pycsl_mod` |
| `_emit_preamble` | 2526–2532 | Orchestrates prelude emission |
| `_emit_shared_state` | 2538–2583 | Concurrent model shared vars |
| `_emit_type_decls` | 2589–2657 | Record types for classes |
| `_emit_contracts` | 2760–2795 | requires/ensures/variant/diverges |
| `_emit_body_code` | 2797–2851 | Function body WhyML |
| `_emit_function` | 2853–2911 | Complete function emission |
| `_emit_frame_condition` | 2186–2220 | Assigns → writes + frame |

---

## §T.13  References

1. Filliâtre, J.-C. & Paskevich, A. (2013). *Why3 — Where Programs
   Meet Provers*. ESOP 2013. LNCS 7792.

2. Clochard, M. et al. (2018). *Instrumenting a weakest-precondition
   calculus for counterexample generation*. Journal of Logical and
   Algebraic Methods in Programming.

3. Baudin, P. et al. (2021). *ACSL: ANSI/ISO C Specification Language*.
   (Inspiration for PyCSL's annotation syntax.)

4. Leino, K.R.M. (2010). *Dafny: An Automatic Program Verifier for
   Functional Correctness*. LPAR 2010.

5. Why3 Reference Manual. https://why3.lri.fr/doc/

---

## Appendix A: Golden Output Gallery

The following are complete verified WhyML outputs generated by
`pycsl --keep-mlw` on reference tests.

### A.1  Basic Function (Test 0001)

**Input:**
```python
#@ requires x >= 0
#@ ensures \result >= 0
def test_precondition(x: int) -> int:
    return x + 1
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  let test_precondition (x: int) : int
    requires { (x >= 0) }
    ensures  { (result >= 0) }
  =
    (x + 1)

end
```

### A.2  While Loop with Invariant (Test 0004)

**Input:**
```python
#@ requires n >= 0
#@ ensures \result == n * (n - 1) // 2
def test_loop_invariant(n: int) -> int:
    s = 0
    i = 0
    #@ loop invariant s == i * (i - 1) // 2
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        s += i
        i += 1
    return s
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  let pycsl_div (x: int) (y: int) : int
    requires { [@expl:division by zero] y <> 0 }
    ensures { result = div x y }
  = div x y

  let pycsl_mod (x: int) (y: int) : int
    requires { [@expl:modulo by zero] y <> 0 }
    ensures { result = mod x y }
  = mod x y

  let test_loop_invariant (n: int) : int
    requires { (n >= 0) }
    ensures  { (result = (div (n * (n - 1)) 2)) }
  =
    let s = ref 0 in
    let i = ref 0 in
    s := 0;
    i := 0;
    while (!i < n) do
      invariant { (!s = (div (!i * (!i - 1)) 2)) }
      invariant { ((0 <= !i) && (!i <= n)) }
      variant { (n - !i) }
      s := (!s + !i);
      i := (!i + 1)
    done;
    !s

end
```

### A.3  Class with Invariant (Test 0006)

**Input:**
```python
#@ class invariant self._value >= 0
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  type counter = { mutable _value: int }
    invariant { (_value >= 0) }
    by { _value = 0 }

  let counter__increment (self: counter) (amount: int) : int
    requires { (amount >= 0) }
    ensures  { (self._value = ((old self._value) + amount)) }
  =
    self._value <- (self._value + amount);
    self._value

end
```

### A.4  Concurrent Model (Test 0250)

**Input:**
```python
#@ shared counter
#@ mutex_invariant lock_counter: counter >= 0
#@ \diverges
#@ thread_entry
def worker() -> int:
    #@ critical lock_counter
    counter += 1
    return 0
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  val counter : ref int
  predicate lock_counter_inv = (!counter >= 0)
  let _check_initial_lock_counter () : unit =
    assert { lock_counter_inv }

  let worker () : int
    diverges
  =
    let _any_counter_0 = any int in
    counter := _any_counter_0;
    assume { lock_counter_inv };
    counter := !counter + 1;
    assert { lock_counter_inv };
    0

end
```

### A.5  Exception with Raises (Test 0206)

**Input:**
```python
#@ ensures \result >= 0
#@ raises ValueError when n < 0
def checked_abs(n: int) -> int:
    if n < 0:
        raise ValueError
    return n
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref
  exception ValueError

  let checked_abs (n: int) : int
    ensures  { (result >= 0) }
    raises { ValueError -> (n < 0) }
  =
    if (n < 0) then begin
      raise ValueError
    end;
    n

end
```
