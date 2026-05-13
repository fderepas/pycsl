# Frama-C–Inspired Memory Model for PyCSL

## Context

PyCSL currently uses a **value-semantic** array model: each `list`-typed parameter is
emitted as an independent `array int` in Why3. Mutations to `arr` are local and cannot
affect any other array parameter. This model cannot express **heap aliasing** — the case
where two parameters `list_a` and `list_b` refer to the same underlying memory.

This document designs a Frama-C WP–style memory model for PyCSL. It covers three areas:

1. Making the heap **global and implicit** (the programmer never mentions it)
2. Introducing first-class predicates: `\valid`, `\separated`, `\assigns`, `\old`, `\at`
3. Providing three **parameterised memory model backends**: Hoare, Typed, Store

The design is concrete: every PyCSL annotation maps to a specific Why3 emission, and
every module in the pipeline (M1–M6) has its changes enumerated.

---

## Part 1 — A Global Implicit Heap

### 1.1 Design Principle

In Frama-C WP, the C heap is a collection of typed memory stores maintained as ghost
global state. The programmer never mentions the heap in ACSL annotations — the WP
calculus threads it automatically through the verification conditions. The same principle
applies here:

- **The Python programmer** writes `arr[i]`, `arr[i] = v`, `\forall i; arr[i] >= 0`.
- **Module 6** translates these into heap-indexed WhyML expressions.
- **The heap variable** appears only in the generated `.mlw` file, never in `#@` contracts.

### 1.2 The Heap in Why3

Why3 supports mutable module-level variables via `val`. The heap is declared as a global
mutable reference in the generated WhyML preamble:

```whyml
module PyCSL
  use int.Int
  use int.EuclideanDivision
  use ref.Ref
  use map.Map
  use map.MapEq

  (* --- Memory model preamble --- *)
  type loc = int                              (* an address in the heap *)
  val mem : ref (map loc int)                 (* the single global heap *)

  predicate valid (m: map loc int) (base: loc) (n: int) =
    n >= 0 /\ base >= 0 /\ base + n <= max_addr

  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =
    a + na <= b \/ b + nb <= a

  constant max_addr : int = 1073741824        (* 2^30, arbitrary bound *)
  (* --- End memory model preamble --- *)
```

### 1.3 Translation Rules

| Python / PyCSL | Current WhyML (value-semantic) | New WhyML (heap model) |
|---|---|---|
| `arr: list` parameter | `(arr: array int)` | `(arr: loc) (arr_len: int)` |
| `arr[i]` read | `arr[!i]` | `Map.get !mem (arr + !i)` |
| `arr[i] = v` write | `arr[!i] <- v` | `mem := Map.set !mem (arr + !i) v` |
| `len(arr)` | `length arr` | `!arr_len` (explicit length param) |
| `n = len(arr)` | `let n = ref (length arr)` | `let n = ref arr_len` |
| `\length(arr)` in contract | `length arr` | `arr_len` |
| `arr[i]` in contract | `arr[i]` | `Map.get !mem (arr + i)` |
| `\forall i; arr[i] >= 0` | `forall i:int. arr[i] >= 0` | `forall i:int. Map.get !mem (arr + i) >= 0` |

### 1.4 Key Invariant: Implicit Lifting

The programmer writes Python with `#@` contracts that mention `arr[i]` and `len(arr)`.
They never write `mem`, `loc`, or `Map.get`. The translation from surface syntax to heap
operations is performed entirely by Module 6. This is the exact analogue of Frama-C WP's
implicit heap threading: the ACSL annotation `list_a[i]` is compiled by the WP calculus
into a read from the typed memory store — the Frama-C user never sees it.

### 1.5 Module-by-Module Changes for Part 1

**Module 1 (Ingestor):** No changes. Annotations are extracted as raw strings.

**Module 2 (Parser):** No changes for Part 1. The grammar already supports `arr[i]` via
`SubscriptAccess` and `\length(arr)` via `ArrayLength`. The parser is agnostic to the
memory model backend.

**Module 3 (Weaver):** No changes. Annotations are woven into the AST by line number.

**Module 4 (Semantic Analyzer):** Minor changes:
- `list`-typed parameters now carry two symbols: `arr` (loc) and `arr_len` (int).
- Scope validation must accept `arr_len` as an implicitly-generated name.

**Module 5 (IR Emitter):**
- `list`-typed parameters emit two entries in the symbol table:
  `{"arr": "loc", "arr_len": "int"}`.
- `len(arr)` calls emit `{"type": "HeapLen", "base": "arr"}` → resolves to `arr_len`.
- `arr[i]` reads emit `{"type": "HeapGet", "base": "arr", "index": ...}`.
- `arr[i] = v` writes emit `{"stmt": "HeapSet", "base": "arr", "index": ..., "value": ...}`.

**Module 6 (WhyML Transpiler):** The largest changes:
- Emits the heap preamble (`type loc`, `val mem`, predicates).
- `list`-typed parameters become `(arr: loc) (arr_len: int)`.
- `HeapGet` → `Map.get !mem (arr + idx)`.
- `HeapSet` → `mem := Map.set !mem (arr + idx) val`.
- `HeapLen` → `arr_len` (direct reference to the length parameter).
- Frame condition: for each function, emits an `ensures` clause preserving all heap
  cells not in the `\assigns` set (see Part 2).
- New flag: `memory_model` (enum: `hoare | typed | store`) controls emission.

---

## Part 2 — First-Class Predicates

### 2.1 Overview

These five predicates form the specification language for heap-aware contracts:

| Predicate | ACSL (Frama-C) | PyCSL Syntax | Meaning |
|---|---|---|---|
| Validity | `\valid(p + (0..n-1))` | `\valid(arr, n)` | `arr[0]..arr[n-1]` are allocated |
| Separation | `\separated(p+(0..n), q+(0..m))` | `\separated(a, n, b, m)` | Regions don't overlap |
| Frame | `assigns p[0..n-1]` | `assigns arr[0..n-1]` | Only this region is modified |
| Pre-state | `\old(e)` | `\old(e)` | Value of `e` at function entry |
| Label | `\at(e, L)` | `\at(e, L)` | Value of `e` at program point `L` |

### 2.2 `\valid(arr, n)` — Memory Validity

**Semantics:** Asserts that the memory region `[arr, arr+n)` is allocated and in-bounds.
In Frama-C, `\valid(p)` checks that `p` points to a single valid cell; `\valid(p + (0..n-1))`
checks a range. For PyCSL, we simplify to a two-argument form: `\valid(arr, n)` means
"the first `n` cells starting at `arr` are valid".

**Grammar addition (Module 2):**
```
?atom: ...
     | "\\valid" "(" CNAME "," expr ")" -> valid_pred
```

**Dataclass:**
```python
@dataclass
class Valid(CSLNode):
    base: str
    length: CSLNode
```

**IR (Module 5):**
```json
{"type": "Valid", "base": "arr", "length": {"type": "Var", "name": "n"}}
```

**WhyML emission (Module 6):**
```whyml
(* In requires clause: *)
requires { valid !mem arr n }

(* Where `valid` is defined in the preamble as: *)
predicate valid (m: map loc int) (base: loc) (n: int) =
  n >= 0 /\ base >= 0 /\ base + n <= max_addr
```

**Semantic validation (Module 4):** `base` must be a `list`-typed parameter (or a
derived loc). `length` must be a variable in scope or a numeric constant.

### 2.3 `\separated(a, na, b, nb)` — Region Disjointness

**Semantics:** Asserts that memory regions `[a, a+na)` and `[b, b+nb)` do not overlap.
This is the PyCSL analogue of ACSL's `\separated(a + (0..na-1), b + (0..nb-1))`.

When the regions are guaranteed disjoint, writing to one cannot affect the other. This
is the key enabler for modular reasoning about aliasing.

**Grammar addition (Module 2):**
```
?atom: ...
     | "\\separated" "(" CNAME "," expr "," CNAME "," expr ")" -> separated_pred
```

**Dataclass:**
```python
@dataclass
class Separated(CSLNode):
    base1: str
    length1: CSLNode
    base2: str
    length2: CSLNode
```

**IR (Module 5):**
```json
{"type": "Separated", "base1": "a", "len1": ..., "base2": "b", "len2": ...}
```

**WhyML emission (Module 6):**
```whyml
requires { separated arr_a na arr_b nb }

(* Where `separated` is defined in the preamble as: *)
predicate separated (a: loc) (na: int) (b: loc) (nb: int) =
  a + na <= b \/ b + nb <= a
```

**N-ary separation:** With `k` array parameters, the programmer must state
`k*(k-1)/2` pairwise separation predicates. For `k=2` this is one clause. For `k=3`,
three. This is the same cost as in Frama-C. A syntactic shorthand could be added later:
`\separated(a, na, b, nb, c, nc)` expanding to all pairwise combinations.

### 2.4 `\assigns` — Frame Condition (Extended)

**Current state:** PyCSL already has `#@ assigns \nothing` and `#@ assigns self._field`.
These are syntactic markers that Module 6 currently ignores when generating WhyML. In the
heap model, `\assigns` becomes semantically meaningful: Module 6 must generate an
explicit frame condition ensuring all heap cells **not** in the assigned set are
preserved.

**Extended syntax:**

```python
#@ assigns \nothing                     # function does not modify the heap
#@ assigns arr[0..n-1]                  # function may modify arr[0] through arr[n-1]
#@ assigns arr[0..n-1], brr[0..m-1]    # two regions may be modified
#@ assigns self._field                  # (class) field mutation (existing)
```

**Grammar addition (Module 2):**
```
?assigns_target: expr_list
               | "\\nothing" -> nothing
               | assigns_region ("," assigns_region)* -> assigns_regions
assigns_region: CNAME "[" expr ".." expr "]"
```

**Dataclass:**
```python
@dataclass
class AssignsRegion(CSLNode):
    base: str
    low: CSLNode
    high: CSLNode
```

**WhyML emission (Module 6):**

For `#@ assigns arr[0..n-1]`:
```whyml
writes   { mem }
ensures  { forall l: int. not (arr <= l < arr + n)
           -> Map.get !mem l = Map.get (old !mem) l }
```

For `#@ assigns \nothing`:
```whyml
ensures  { !mem = old !mem }
```

For `#@ assigns arr[0..n-1], brr[0..m-1]`:
```whyml
writes   { mem }
ensures  { forall l: int.
             not (arr <= l < arr + n) /\ not (brr <= l < brr + m)
             -> Map.get !mem l = Map.get (old !mem) l }
```

**This is the central value proposition.** The programmer writes `#@ assigns arr[0..n-1]`.
Module 6 automatically generates the universally-quantified frame condition. This is
exactly what Frama-C WP does: the `\assigns` clause is compiled into a frame lemma that
the SMT solver uses to prove non-interference.

### 2.5 `\old(expr)` — Pre-State Values (Generalised)

**Current state:** PyCSL already supports `\old(self._field)` in `ensures` clauses,
emitted as `(old self._field)` in WhyML. This works because Why3's `old` keyword
captures the value of an expression at function entry.

**Extension:** In the heap model, `\old(arr[i])` must emit `Map.get (old !mem) (arr + i)`.
The `old` wraps the heap reference, not the subscript expression.

**Grammar:** No change needed — `\old(expr)` already accepts any expression, including
`SubscriptAccess`. The change is in Module 6's emission.

**Current emission:**
```whyml
(* \old(self._field) → *)
(old self._field)
```

**New emission for heap model:**
```whyml
(* \old(arr[i]) → *)
(Map.get (old !mem) (arr + i))

(* \old(arr[i]) == arr[i] when \separated ensures arr is not modified → *)
(* The solver derives this from the frame condition *)
```

**Why this matters:** `\old(arr[i])` is essential for expressing the semantics of
in-place mutation. For example, a `swap` function needs:

```python
#@ ensures arr[\old(i)] == \old(arr[j])
#@ ensures arr[\old(j)] == \old(arr[i])
```

### 2.6 `\at(expr, L)` — Label-Based State Snapshots

**Semantics:** Returns the value of `expr` at program point `L`. This is the most
powerful temporal operator. In Frama-C:

```c
/*@ ensures \at(list_a[0], Pre) != \at(list_a[0], Post); */
```

In Why3, this is supported via label references:

```whyml
label L in
(* ... code ... *)
assert { (mem at L)[arr + 0] = 42 }
```

**Implementation:** This is the most complex predicate. It requires:

1. **Module 2:** New grammar rule:
   ```
   ?atom: ...
        | "\\at" "(" expr "," CNAME ")" -> at_expr
   ```

2. **Module 2 dataclass:**
   ```python
   @dataclass
   class At(CSLNode):
       expr: CSLNode
       label: str
   ```

3. **Module 5 IR:**
   ```json
   {"type": "At", "expr": ..., "label": "L"}
   ```

4. **Module 6:**
   - Emit `label L in` at the corresponding program point.
   - Emit `(mem at L)` instead of `!mem` when inside an `\at(_, L)` context.

5. **Module 3 (Weaver):** Must support label annotations in the Python source:
   ```python
   #@ label L
   arr[0] = 42
   #@ assert \at(arr[0], L) == \old(arr[0])
   ```

**Complexity assessment:** `\at` is the highest-cost predicate to implement. It requires
label tracking across the pipeline (M1 → M2 → M3 → M5 → M6), label emission in WhyML,
and careful scoping. It should be implemented last, after `\valid`, `\separated`, and
`\assigns` are stable.

**Phased approach:**
- **Phase 1:** Support only `\old(expr)` (function entry) and `\at(expr, Pre)` as a synonym.
- **Phase 2:** Support `\at(expr, LoopEntry)` for loop invariants referencing the state
  at loop entry.
- **Phase 3:** Full arbitrary label support.

---

## Part 3 — Parameterised Memory Model

### 3.1 Design Principle

Frama-C WP offers four memory model backends. The choice does not change the annotation
language (ACSL) — it changes the **shape of the generated proof obligations**. The same
design applies to PyCSL: the `#@` contracts are identical regardless of the backend. Only
Module 6's WhyML emission changes.

The memory model is selected via a configuration flag:

```json
{
  "memory-model": "typed"
}
```

Or per-file via a pragma:
```python
#@ memory_model typed
```

### 3.2 Hoare Model — No Heap (Current Behaviour)

**When to use:** Functions that operate on scalar parameters only, or functions where
all array parameters are known to be independent (no aliasing possible by construction).

**Heap representation:** None. Each `list`-typed parameter remains a value-typed
`array int` exactly as PyCSL works today.

**Translation:**

| Construct | WhyML emission |
|---|---|
| `arr: list` parameter | `(arr: array int)` |
| `arr[i]` read | `arr[!i]` |
| `arr[i] = v` write | `arr[!i] <- v` |
| `len(arr)` | `length arr` |
| `\valid(arr, n)` | `n >= 0 /\ n <= length arr` (trivially true) |
| `\separated(a, na, b, nb)` | `true` (always disjoint — different values) |
| `\assigns arr[0..n-1]` | (no frame condition needed — value semantics) |
| `\old(arr[i])` | `(old arr[!i])` |
| Frame condition | Automatic — value parameters can't alias |

**Preamble:**
```whyml
module PyCSL
  use int.Int
  use int.EuclideanDivision
  use ref.Ref
  use array.Array
  (* No heap declarations *)
```

**Pros:**
- Zero annotation overhead. Identical to current PyCSL behaviour.
- Proof obligations are small and fast for SMT solvers.
- `\separated` is trivially true (value semantics guarantee disjointness).

**Cons:**
- Cannot model aliasing. If `list_a is list_b` in the caller, the Hoare model gives
  **unsound** results — the postcondition may assert properties that do not hold.
- Not suitable for functions that must reason about shared mutable state.

**Soundness note:** The Hoare model is sound **if and only if** every function call site
passes distinct array arguments. This is an implicit non-aliasing assumption that is
not verified. Adding `\separated` preconditions (even if trivially true) serves as
documentation that the assumption exists.

### 3.3 Typed Model — One Map per Type (Default)

**When to use:** General-purpose default. Handles aliasing correctly for same-type
parameters. Suitable for most Python programs that operate on integer arrays.

**Heap representation:** One global mutable map per Python type. Since PyCSL currently
supports only `int` elements, a single map suffices:

```whyml
type loc = int
val int_mem : ref (map loc int)     (* heap for int values *)
```

If `float` or other element types were added in the future, each would get its own map:

```whyml
val float_mem : ref (map loc float)
```

**Translation:**

| Construct | WhyML emission |
|---|---|
| `arr: list` parameter | `(arr: loc) (arr_len: int)` |
| `arr[i]` read | `Map.get !int_mem (arr + !i)` |
| `arr[i] = v` write | `int_mem := Map.set !int_mem (arr + !i) v` |
| `len(arr)` | `arr_len` |
| `\valid(arr, n)` | `valid !int_mem arr n` |
| `\separated(a, na, b, nb)` | `separated a na b nb` |
| `\assigns arr[0..n-1]` | `ensures { forall l. not (arr<=l<arr+n) -> Map.get !int_mem l = Map.get (old !int_mem) l }` |
| `\old(arr[i])` | `Map.get (old !int_mem) (arr + i)` |

**Preamble:**
```whyml
module PyCSL
  use int.Int
  use int.EuclideanDivision
  use ref.Ref
  use map.Map

  type loc = int

  constant max_addr : int = 1073741824

  val int_mem : ref (map loc int)

  predicate valid (m: map loc int) (base: loc) (n: int) =
    n >= 0 /\ base >= 0 /\ base + n <= max_addr

  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =
    a + na <= b \/ b + nb <= a
```

**Example — fill and read back:**

Python:
```python
#@ requires \valid(list_a, n)
#@ requires \valid(list_b, n)
#@ requires \separated(list_a, n, list_b, n)
#@ requires n >= 1
#@ ensures \result == \old(list_b[0])
#@ assigns list_a[0..n-1]
def fill_and_read(list_a: list, list_b: list, n: int) -> int:
    list_a[0] = 42
    return list_b[0]
```

Generated WhyML (Typed model):
```whyml
let fill_and_read (list_a: loc) (list_a_len: int)
                  (list_b: loc) (list_b_len: int) (n: int) : int
  requires { valid !int_mem list_a n }
  requires { valid !int_mem list_b n }
  requires { separated list_a n list_b n }
  requires { n >= 1 }
  ensures  { result = Map.get (old !int_mem) (list_b + 0) }
  writes   { int_mem }
  ensures  { forall l: int. not (list_a <= l < list_a + n)
             -> Map.get !int_mem l = Map.get (old !int_mem) l }
= int_mem := Map.set !int_mem (list_a + 0) 42;
  Map.get !int_mem (list_b + 0)
```

The solver derives `list_b[0]` is unchanged from `\separated` + the frame condition.

**Pros:**
- Handles same-type aliasing correctly.
- The frame condition is auto-generated from `\assigns` (no manual heap threading).
- Proof obligations are moderate size — a single `map` theory.
- Close to Frama-C's `Typed` model in expressiveness.

**Cons:**
- Cannot model cross-type aliasing (e.g., a `float` and an `int` overlapping in
  memory). This is irrelevant for Python but matters in C.
- Every `list` parameter adds a `_len` shadow parameter (mild signature bloat).
- `Map.get`/`Map.set` chains can be slower for SMT solvers than direct `array` theory.

### 3.4 Store Model — Single Untyped Byte Array (Full Generality)

**When to use:** When maximum generality is needed, or when the program mixes types
in a single memory region (e.g., a struct-of-arrays flattened into a single buffer).

**Heap representation:** A single global map from addresses to a universal value type:

```whyml
type loc = int
type value = int                    (* all values flattened to int *)
val store : ref (map loc value)
```

**Translation:** Identical to the Typed model, but using `store` instead of `int_mem`.
When multiple element types are added, they are all projected into/from `int` via
encoding functions.

**Preamble:**
```whyml
module PyCSL
  use int.Int
  use int.EuclideanDivision
  use ref.Ref
  use map.Map

  type loc = int

  constant max_addr : int = 1073741824

  val store : ref (map loc int)

  predicate valid (m: map loc int) (base: loc) (n: int) =
    n >= 0 /\ base >= 0 /\ base + n <= max_addr

  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =
    a + na <= b \/ b + nb <= a
```

**Key difference from Typed:** In the Store model, two arrays of different logical
types share the same `store`. Writing to `float_arr[0]` can alias `int_arr[0]` if
they happen to point to the same address. The `\separated` predicate is the **only**
defence against unintended aliasing.

**Pros:**
- Maximum generality. Can model any memory layout, including C-style unions.
- Single map simplifies the Why3 theory stack.
- If Python later gains typed arrays (`array.array('f', ...)`), the Store model handles
  mixed-type memory correctly.

**Cons:**
- Proof obligations are harder — the solver cannot use type information to prune aliasing.
- All values are encoded as `int`, losing type structure (Z3/Alt-Ergo cannot use
  type-disjointness lemmas).
- Requires `\separated` on **every** pair of parameters, even those of different types
  (which the Typed model handles for free).

### 3.5 Comparison Table

| Property | Hoare | Typed | Store |
|---|---|---|---|
| Heap representation | None (value types) | One `map` per type | Single `map` |
| Aliasing support | ❌ Unsound | ✅ Same-type only | ✅ Full |
| `\separated` needed | No (always true) | Yes (same-type pairs) | Yes (all pairs) |
| Frame condition | Automatic (value) | Auto from `\assigns` | Auto from `\assigns` |
| Proof difficulty | Easy | Moderate | Hard |
| SMT solver load | Low | Medium | High |
| Annotation burden | None | Low–Medium | Medium–High |
| Default for PyCSL | Legacy mode | **Recommended default** | Advanced mode |

### 3.6 Model Selection in Module 6

Module 6 uses a `memory_model` flag (set from `agents-config.json` or per-file pragma)
to control emission:

```python
class Module6_WhyMLTranspiler:
    def __init__(self, json_ir: str, memory_model: str = "hoare"):
        self.memory_model = memory_model  # "hoare" | "typed" | "store"
        # ...

    def transpile(self) -> str:
        if self.memory_model == "hoare":
            return self._transpile_hoare()
        elif self.memory_model == "typed":
            return self._transpile_typed()
        elif self.memory_model == "store":
            return self._transpile_store()
```

The `_transpile_hoare()` method is essentially the current `transpile()`. The typed
and store methods share most of the logic but differ in preamble emission and expression
translation for heap operations.

---

## Implementation Roadmap

### Phase 0 — Prerequisite: `\assigns` region syntax (Low cost)
- Module 2: Add `assigns_region` grammar rule (`arr[lo..hi]`).
- Module 5: Emit `AssignsRegion` IR nodes.
- Module 6 (Hoare model): Ignore region annotations (frame is implicit).
- This is backward-compatible — `#@ assigns \nothing` continues to work.

### Phase 1 — `\valid` and `\separated` predicates (Medium cost)
- Module 2: Add `valid_pred` and `separated_pred` grammar atoms.
- Module 4: Validate that `base` names are `list`-typed parameters.
- Module 5: Emit `Valid` and `Separated` IR nodes.
- Module 6 (Hoare model): Emit trivial predicates (validity check on `length`, separation always true).
- Module 6 (Typed model): Emit heap-based predicates.
- **Tests:** Write functions with explicit `\valid` / `\separated` preconditions. Verify
  under both Hoare (trivially valid) and Typed (solver must prove from `\separated`).

### Phase 2 — Typed memory model backend (High cost)
- Module 6: Implement `_transpile_typed()`.
  - Preamble: `type loc`, `val int_mem`, predicates.
  - Parameter translation: `list` → `loc` + `_len`.
  - Expression translation: `HeapGet` / `HeapSet`.
  - Frame condition generation from `\assigns` regions.
- Module 5: Emit `HeapGet` / `HeapSet` IR nodes (conditionally, based on memory model).
- **Tests:** The `fill_and_read` example above. Verify that `\separated` + `\assigns`
  together prove `list_b[0]` is unchanged.

### Phase 3 — `\old(arr[i])` generalisation (Medium cost)
- Module 6 (Typed model): Emit `Map.get (old !int_mem) (arr + i)` for `\old(arr[i])`.
- **Tests:** `swap(arr, i, j)` with postcondition `arr[i] == \old(arr[j])`.

### Phase 4 — Store model backend (Medium cost)
- Module 6: Implement `_transpile_store()`. Identical to Typed but with a single `store`.
- **Tests:** Same tests as Phase 2, verified under Store model.

### Phase 5 — `\at(expr, L)` labels (High cost, deferred)
- Module 2: Grammar for `\at(expr, L)` and `#@ label L`.
- Module 3: Attach label annotations to AST nodes.
- Module 5: Emit `Label` and `At` IR nodes.
- Module 6: Emit `label L in` and `(mem at L)`.
- **Tests:** Multi-step array algorithms with intermediate assertions.

---

## Relationship to Frama-C Architecture

| Frama-C Component | PyCSL Analogue | Role |
|---|---|---|
| ACSL annotations | `#@` contracts | Surface specification language |
| Frama-C kernel (normalisation) | Module 1 + Module 3 | Extract and attach contracts |
| ACSL parser | Module 2 | Parse contract expressions to AST |
| WP calculus (wp plugin) | Module 5 + Module 6 | Generate verification conditions |
| Memory model (Hoare/Typed/Store) | Module 6 backend flag | Controls VC shape |
| Why3 (proof discharge) | `why3 prove` | SMT solving |
| Alt-Ergo / Z3 / CVC5 | Alt-Ergo | Decision procedure |

The key architectural insight is that **Module 6 plays the role of Frama-C's WP plugin**.
It takes the annotated program (via IR) and generates verification conditions (as WhyML)
that encode the proof obligations. The memory model selection determines how heap
operations are encoded in those VCs.

In Frama-C, the WP calculus is a standalone computation that generates first-order logic
goals. In PyCSL, Module 6 generates WhyML (an intermediate program language), and Why3's
own VC generator produces the final first-order goals. This is a two-stage process where
Frama-C has one stage — but the end result is the same: a set of SMT goals that encode
the program's correctness.

---

## Open Questions

1. **Should the `\assigns` frame condition use `old` or snapshot labels?**
   In Frama-C, `\assigns` is implicitly relative to `Pre` (function entry). Using `old`
   is correct for this. But for loop `\assigns`, the frame is relative to the loop entry
   — this requires `\at(_, LoopEntry)` or an implicit loop label.

2. **How should the length parameter `arr_len` interact with `\length(arr)`?**
   Option A: `\length(arr)` emits `arr_len` (a constant). Option B: `\length(arr)` emits
   a heap read from a separate length-store (allowing `realloc`-style length changes).
   Option A is simpler and sufficient for Python's fixed-size-at-call-time semantics.

3. **Should Module 4 enforce `\separated` exhaustiveness?**
   When a function has `k` `list`-typed parameters and uses the Typed/Store model, should
   Module 4 emit a warning if not all `k*(k-1)/2` pairs have `\separated` preconditions?
   This would catch the common error of forgetting a separation clause.

4. **What about nested arrays (list of lists)?**
   The current model assumes `list` → `array int` (flat integer array). A `list[list]`
   would require a two-level indirection: the outer array contains `loc` values pointing
   to inner arrays. This is expressible in the Store model but not in the Typed model
   (which has only one map type). Deferring to a future phase.
