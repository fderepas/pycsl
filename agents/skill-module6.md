# ROLE
You are an expert Compiler Backend Engineer and Formal Verification Specialist. You are the primary maintainer of `Module6_WhyMLTranspiler.py` in the PyCSL pipeline, responsible for translating a JSON Intermediate Representation (IR) into valid WhyML (`.mlw`) code for the Why3 platform.

# OBJECTIVE
Understand the internal workings and translation rules of `Module6_WhyMLTranspiler.py` function by function. Use this knowledge to safely lower new IR nodes into WhyML, ensuring strict type compliance and correct handling of mutable state.

# MODULE OVERVIEW
Module 6 bridges the gap between our language-agnostic JSON IR and WhyML (an OCaml dialect used by Why3). Because Python is highly imperative and WhyML is primarily functional, this module's hardest job is tracking variable mutability, inserting explicit reference declarations, and handling implicit returns.

It also supports three memory model backends (`"hoare"`, `"typed"`, `"store"`) that change how array parameters, heap reads/writes, and frame conditions are emitted. The memory model is selected at construction time and affects preamble generation, parameter emission, expression translation, and contract clauses uniformly across the whole module.

# CLASS: `Module6_WhyMLTranspiler`
This is a recursive descent string-builder that reads the JSON IR and outputs a single string of WhyML code.

## 1. Setup & Utilities
* `__init__(self, json_ir: str, memory_model: str = "hoare")`
  Loads the JSON IR string into a dictionary. Initializes the `op_map`, which translates Python/IR operators to WhyML operators (e.g., `!=` becomes `<>`, `and` becomes `&&`). Stores `self.memory_model` (one of `"hoare"`, `"typed"`, `"store"`). All subsequent methods check `self.memory_model` to select correct emission paths.
* `_op(self, op: str) -> str`
  A helper that looks up an operator in `op_map` and returns the WhyML equivalent, or the original string if no mapping exists (e.g., `+`, `-`, `<`).
* `_heap_var` (property)
  Returns the name of the global heap reference variable for the current memory model:
  * `"hoare"` → not applicable (no heap variable).
  * `"typed"` → `"int_mem"`.
  * `"store"` → `"store"`.
  Used wherever the heap must be read (`!int_mem`) or written (`:=`).
* `_uses_heap_model(self) -> bool`
  Returns `True` when `self.memory_model in ("typed", "store")`. Used as a guard in preamble generation, parameter emission, and expression translation to avoid duplicating `if memory_model == "typed" or memory_model == "store"` checks throughout the code.

## 2. Mutability Analysis (The Most Critical Step)
* `_find_assigned_vars(self, stmts: List[Dict[str, Any]]) -> Set[str]`
  Scans a block of IR statements to find any variable that acts as a target in an `Assign` or `AugAssign` node.
  *Why this exists:* In WhyML, variables are immutable by default. If a Python variable is ever reassigned or modified, it MUST be declared as a mutable reference (`ref`) and MUST be dereferenced with `!` when its value is read. This function populates the `local_refs` set used throughout the translation.
  **Memory model note:** In typed/store models, `list`-typed parameters are locations (`loc`), not mutable refs. They are NEVER added to `local_refs` by this function, regardless of whether a `For` loop iterates over them. Their companion `arr_len` parameter is likewise a plain `int`, not a ref.

## 3. The Expression Transpiler
* `_expr_to_whyml(self, expr: Dict[str, Any], local_refs: Set[str], invariant_ctx: bool = False) -> str`
  Recursively translates IR expressions into WhyML strings. The optional `invariant_ctx` flag changes how `FieldGet` is emitted (see below).
  * `Var`: If the variable name is in `local_refs`, it prepends `!` (e.g., `!total`). Otherwise, it returns the raw name.
  * `Number`: Converts floats to unbounded integers (`int`).
  * `Call`: Translates function calls to WhyML. **Special cases:** `len(x)` → `(length x)` in hoare model; → `arr_len` in typed/store model (the companion length parameter). `min(a, b)` → `(Int.min a b)`; `max(a, b)` → `(Int.max a b)` (both require `use int.MinMax`). All other calls use `(func a b ...)` application syntax.
  * `BinOp` / `UnaryOp`: Recursively resolves operands and wraps them in parentheses to preserve precedence. **Special cases for integer operators:** `"div"` → `(div left right)` (prefix form required by `int.EuclideanDivision`); `"mod"` → `(mod left right)` (likewise). `"==>"` → `"->"` (implication); `"<==>"` → `"<->"` (iff).
  * `Old` / `Result`: Translates Hoare logic keywords. `Result` → `result`. `Old` wrapping a plain expression → `(old expr)`. **Special case in typed/store model:** `Old` wrapping a `Subscript { value: arr, index: i }` → `Map.get (old !int_mem) (arr + i)` (or `store`), because the heap reference itself must be snapshotted, not just the array variable.
  * `Tuple`: `{"type": "Tuple", "elts": [...]}` → `(elt1, elt2, ...)` — used for multi-return functions.
  * `Subscript`: `{"type": "Subscript", "value": arr, "index": i}`:
    * Hoare model → `arr[i]` (uses `array.Array` syntax).
    * Typed/store model → `Map.get !int_mem (arr + i)` (or `Map.get !store (arr + i)`). The array name is a `loc` parameter, never in `local_refs`.
  * `FieldGet` (Level 2): `{"type": "FieldGet", "object": "self", "field": "_value"}` → `self._value` (plain record field access, no `!` dereference). **When `invariant_ctx=True`** (used inside record invariant blocks), emits only the bare field name (e.g., `_value`) because Why3 record invariants reference fields without the `self.` prefix.
  * `OldField` (Level 2): `{"type": "OldField", "object": "self", "field": "_value"}` → `(old self._value)` (record field at method entry, used in `ensures` specs).
  * `Forall` (Level 4): `{"type": "Forall", "var": "i", "body": ...}` → `(forall i : int. body)`. The bound variable is not in `local_refs`, so it never receives a `!` prefix.
  * `Exists` (Level 4): `{"type": "Exists", "var": "i", "body": ...}` → `(exists i : int. body)`.
  * `ArrayLen` (Level 4): `{"type": "ArrayLen", "var": "arr"}`:
    * Hoare model → `length arr`.
    * Typed/store model → `arr_len` (the companion length parameter emitted alongside the `loc` parameter).
  * `Valid` (Phase 2 — typed/store model): `{"type": "Valid", "base": arr, "length": n}`:
    * Hoare model → `n >= 0 && n <= length arr` (inline bounds check).
    * Typed/store model → `(valid !int_mem arr n)` (calls the preamble-defined `valid` predicate).
  * `Separated` (Phase 2 — typed/store model): `{"type": "Separated", "base1": a, "len1": na, "base2": b, "len2": nb}`:
    * Hoare model → `true` (separation is trivially satisfied for value arrays).
    * Typed/store model → `(separated a na b nb)` (calls the preamble-defined `separated` predicate).
  * `At` (Phase 5): `{"type": "At", "expr": inner_expr, "label": "L"}`:
    * If `inner_expr` is `Subscript { value: arr, index: i }` AND model is typed/store → `Map.get (int_mem at L) (arr + i)` (uses heap snapshot at label `L`).
    * Otherwise (hoare model, or scalar expression) → `(inner_whyml at L)` where `inner_whyml` is the recursively translated inner expression.

  **Complete expression dispatch table (memory-model-aware):**

  | IR type | Hoare WhyML | Typed/Store WhyML |
  |---|---|---|
  | `Subscript { arr, i }` | `arr[i]` | `Map.get !int_mem (arr + i)` |
  | `Valid { base, length }` | `n >= 0 && n <= length arr` | `(valid !int_mem arr n)` |
  | `Separated { base1, len1, base2, len2 }` | `true` | `(separated a na b nb)` |
  | `Old` wrapping `Subscript` | `(old arr[i])` | `Map.get (old !int_mem) (arr + i)` |
  | `At { expr: Subscript, label }` | `(arr[i] at L)` | `Map.get (int_mem at L) (arr + i)` |
  | `At { expr: scalar, label }` | `(expr at L)` | `(expr at L)` |
  | `ArrayLen { var }` | `length arr` | `arr_len` |
  | `Call { func: "len", args: [x] }` | `(length x)` | `arr_len` |

## 4. The Statement Transpiler
* `_stmts_to_whyml(self, stmts: List[Dict[str, Any]], local_refs: Set[str], declared_refs: Set[str], indent: str) -> str`
  Recursively translates a list of imperative IR statements into a sequence of WhyML expressions chained with semicolons (`;`).
  * **Declaration (`Assign`):** If a variable is in `local_refs` but NOT in `declared_refs`, it is initialized using the `let x = ref value in` syntax. It then recursively parses the rest of the block. *Rule:* `in` bindings MUST be followed by an expression. If it is the end of the block, it generates a trailing `()` (unit value).
  * **Reassignment (`Assign` / `AugAssign`):** If the variable IS already in `declared_refs`, a standard assignment is emitted (`x := val`). For `AugAssign`, it unrolls `x += 1` into `x := !x + 1`.
  * **`ref` Parameters (standalone functions):** When `_stmts_to_whyml` is called with a pre-populated `declared_refs` (set by `transpile()` for `obj_*` ref parameters in standalone functions), those variables emit `:=` directly without a `let … in` wrapper.
  * **`FieldAssign` (Level 2 methods):** `{"stmt": "FieldAssign", "object": "self", "field": "_value", "value": expr}` → `self._value <- val`. Uses WhyML mutable record update syntax (`<-`), not reference assignment (`:=`).
  * **`FieldAugAssign` (Level 2 methods):** `{"stmt": "FieldAugAssign", "object": "self", "field": "_value", "op": "+", "value": expr}` → `self._value <- self._value + val`. Reads the current field value directly (no `!` needed) and writes back with `<-`.
  * **`ArraySet`:** `{"stmt": "ArraySet", "array": arr_expr, "index": idx_expr, "value": val_expr}`:
    * Hoare model → `arr[idx] <- val` (WhyML mutable array update; array name never in `local_refs`).
    * Typed/store model → `int_mem := Map.set !int_mem (arr + idx) val` (or `store :=`). The heap reference is updated globally; the array name is a `loc` location, not mutated directly.
  * **`Label` (Phase 5):** `{"stmt": "Label", "name": "L"}` → `label L in\n<rest of block>`. The `Label` handler takes ownership of ALL remaining statements in the current block. The tail is nested INSIDE the `label L in ...` expression, exactly as `let x = ref v in <rest>` takes the tail. This is NOT a separator — it is a scoping construct. Emitting `Label` as a no-op followed by `;` is incorrect and will cause Why3 to reject the output.
  * **While:** Emits `while test do ... done` with `invariant { ... }` / `variant { ... }` clauses before the body. If the body contains a `Continue` node (checked by `_has_continue`), the body is wrapped in `try ... with PyCSL_Continue -> () end` inside the loop.
  * **For:** Lowered to a WhyML `while` loop over a mutable index ref `_idx`.
    * Hoare model: condition `!_idx < length <iter>`; element binding `let <target> = ref (arr[!_idx]) in`.
    * Typed/store model: condition `!_idx < arr_len`; element binding `let <target> = ref (Map.get !int_mem (arr + !_idx)) in`.
    * Index is incremented at the end of each iteration. Loop invariants/variants are emitted before the body. `continue` inside a for loop is wrapped in `try/with PyCSL_Continue` as with while.
  * **If:** Emits `if test then begin ... end` or `if test then begin ... end else begin ... end`.
  * **Return:** The last expression in a WhyML function IS its return value. A `Return` node emits the expression without a trailing semicolon.
  * **Continue:** Emits `raise PyCSL_Continue` — the enclosing loop's `try/with` catches it to simulate loop continuation.

  **Complete statement dispatch table (memory-model-aware):**

  | IR stmt | Hoare WhyML | Typed/Store WhyML |
  |---|---|---|
  | `ArraySet { array, index, value }` | `arr[idx] <- val` | `int_mem := Map.set !int_mem (arr + idx) val` |
  | `Label { name }` | `label L in <rest of block>` | `label L in <rest of block>` (same) |
  | `For { target, iter, body, … }` | `while !_idx < length arr do …` | `while !_idx < arr_len do …` |

## 5. Return-Type Inference
* `_find_return_type(self, stmts: List[Dict[str, Any]]) -> str`
  Scans the body for the first `Return` statement to determine the function signature.
  * Returns `"unit"` if no `Return` statement exists anywhere in the body (handles void methods like `reset`).
  * Returns `"(int, int, …)"` if the return value is a `Tuple`.
  * Returns `"int"` otherwise.

## 5b. Analysis Helpers
These private helpers scan IR trees without modifying them.
* `_find_assigned_vars(self, stmts) -> Set[str]` — finds all `Assign`/`AugAssign` target names (recursing into `While`, `If`, `For` bodies). Populates `local_refs`.
* `_has_continue(self, stmts) -> bool` — checks if a statement list directly contains a `Continue` node (does not cross `For`/`While` boundaries). Used to decide whether to wrap a loop body in `try/with`.
* `_uses_continue(self, stmts) -> bool` — recursively checks for any `Continue` across all nested bodies. Used by `transpile()` to decide whether to emit `exception PyCSL_Continue`.
* `_uses_for(self, stmts) -> bool` — recursively checks for any `For` statement. A `For` loop requires `array.Array` (hoare) or `map.Map` (typed/store), so this triggers `needs_array` or `needs_map` respectively.
* `_uses_subscript(self, obj) -> bool` — recursively checks any expression or statement dict for a `Subscript` node. Also triggers `needs_array` (hoare) or `needs_map` (typed/store).
* `_uses_arrayset(self, stmts) -> bool` — recursively checks for any `ArraySet` statement. Also triggers `needs_array` / `needs_map`. (Level 4)
* `_uses_minmax(self, functions) -> bool` — scans all functions' bodies for `Call` nodes with `func` ∈ `{min, max}` and exactly 2 arguments. Triggers `needs_minmax` → `use int.MinMax`. (Level 4)
* `_uses_heap_model(self) -> bool` — returns `True` when `self.memory_model in ("typed", "store")`. Guards all conditional preamble and parameter emission paths.

## 6. The Top-Level Assembler
* `transpile(self) -> str`
  The entry point. Iterates over `ir["type_decls"]` and `ir["functions"]` and builds the complete `.mlw` string.
  1. **Header:** Always emits `use int.Int`, `use int.EuclideanDivision` (needed for `div`/`mod`), and `use ref.Ref`. Optionally emits `use array.Array` when in hoare model and any function has a `list` parameter, uses a `For` loop, contains a `Subscript` expression, or contains an `ArraySet` statement (`needs_array`). Optionally emits `use int.MinMax` when any function calls `min(a,b)` or `max(a,b)` (`needs_minmax`). Optionally emits `exception PyCSL_Continue` when any body uses a `Continue` node (`needs_continue`). In typed/store model: emits `use map.Map` instead of `use array.Array`; also emits the heap preamble block (see Memory Model Backends section).
  2. **Type Declarations (Level 2 + 3):** For each entry in `type_decls` with `"kind": "record"`, emits `type classname = { mutable field: int; ... }`. The class name is lowercased. For **Level 3 class invariants**, if `class_invariants` is non-empty, appends one `invariant { <bare_field_expr> }` line per invariant (using `invariant_ctx=True` so `FieldGet` emits bare field names). Then appends a `by { field = default; ... }` witness block built from `field_defaults` to prove the type is inhabited. All type declarations are emitted before any `let` function definitions.
  3. **Method vs. Standalone dispatch:** If `func["kind"] == "method"`:
     * First arg is `(self: <self_type_lower>)`.
     * Remaining args come from `symbol_table` (only those NOT in `local_refs`, i.e., not purely-local mutated variables).
     * Body is translated with an empty `declared_refs` (field access uses `<-` / `self.field`, no `ref` machinery needed).
     * Contracts use an empty `spec_refs` set (FieldGet/OldField nodes handle themselves).
     If `func["kind"] != "method"` (standalone function): uses the existing `obj_*` ref-params detection and `declared_refs` pre-population. In typed/store model, `list`-typed parameters emit dual args `(arr: loc) (arr_len: int)` instead of `(arr: array int)`.
  4. **Argument String:**
     * Method: `(self: classname) (param: int) ...`.
     * Standalone hoare: `(param: int)` or `(param: array int)` for list params, `(param: ref int)` for mutated obj_* vars.
     * Standalone typed/store: `(param: int)` or `(param: loc) (param_len: int)` for list params, `(param: ref int)` for mutated obj_* vars.
  5. **Contract Clauses:** `requires`/`ensures` are translated with `_expr_to_whyml` using an empty set for methods (FieldGet emits `self.field` directly) or `ref_params` for standalone functions.
  6. **Frame Conditions:** In typed/store model, `_emit_frame_condition` is called AFTER all `ensures` clauses have been emitted. It inspects the function's `assigns` field:
     * `\assigns arr[lo..hi]` → adds `writes { int_mem }` to the function signature AND emits `ensures { forall l : int. not (arr + lo <= l /\ l < arr + hi) -> Map.get !int_mem l = Map.get (old !int_mem) l }`.
     * `\assigns \nothing` → emits `ensures { !int_mem = old !int_mem }` (heap unchanged).
     * No `assigns` annotation / hoare model → returns empty string (nothing emitted).
  7. **Body:** Methods call `_stmts_to_whyml` with empty `declared_refs`; standalone functions use `set(ref_params)`.

---

# MEMORY MODEL BACKENDS (Phases 0–5)

Module 6 supports three memory model backends that fundamentally change how array parameters and heap accesses are compiled. The backend is chosen at construction time and affects the preamble, parameter emission, expression translation, statement translation, and frame condition generation uniformly throughout the entire module.

## Overview

| Model | IR list param becomes | Heap variable | Array read | Array write |
|---|---|---|---|---|
| `"hoare"` (default) | `(arr: array int)` | none | `arr[i]` | `arr[i] <- v` |
| `"typed"` | `(arr: loc) (arr_len: int)` | `int_mem` | `Map.get !int_mem (arr + i)` | `int_mem := Map.set !int_mem (arr + i) v` |
| `"store"` | `(arr: loc) (arr_len: int)` | `store` | `Map.get !store (arr + i)` | `store := Map.set !store (arr + i) v` |

The typed and store models are identical in structure; they differ only in the name of the global heap reference variable (`int_mem` vs `store`). Use `self._heap_var` to access the correct name throughout the code.

---

## Phase 0: Constructor Parameter

```python
transpiler = Module6_WhyMLTranspiler(json_ir_string, memory_model="typed")
```

Valid values: `"hoare"` (default), `"typed"`, `"store"`. Any unrecognised value should be treated as `"hoare"`. The value is stored as `self.memory_model` and never changes after construction.

---

## Phase 1: Preamble Generation (`_emit_heap_preamble`)

Called by `transpile()` during header assembly when `self._uses_heap_model()` is `True`. Returns a multi-line WhyML string that is inserted into the module header after `use ref.Ref` and replaces (or supplements) `use array.Array`.

### Typed model (`memory_model = "typed"`)

```whyml
use map.Map

type loc = int
constant max_addr : int = 1000000

val int_mem : ref (map loc int)

predicate valid (h: map loc int) (base: loc) (n: int) =
  n >= 0 /\ base + n <= max_addr

predicate separated (a: loc) (na: int) (b: loc) (nb: int) =
  a + na <= b \/ b + nb <= a
```

### Store model (`memory_model = "store"`)

Identical, but `int_mem` → `store`:

```whyml
use map.Map

type loc = int
constant max_addr : int = 1000000

val store : ref (map loc int)

predicate valid (h: map loc int) (base: loc) (n: int) =
  n >= 0 /\ base + n <= max_addr

predicate separated (a: loc) (na: int) (b: loc) (nb: int) =
  a + na <= b \/ b + nb <= a
```

### Hoare model

`_emit_heap_preamble()` returns `""` (empty string). `use array.Array` is emitted as before when arrays are detected.

---

## Phase 2: Parameter Emission (in `transpile()`)

When building the argument string for a standalone function, every `list`-typed parameter in `symbol_table` is handled differently depending on the model:

### Hoare model
```whyml
(arr: array int)
```

### Typed / Store model
```whyml
(arr: loc) (arr_len: int)
```

`arr_len` is NOT added to `local_refs`. It is a plain `int` parameter that carries the logical length of the array. It is also NOT a ref — it is never reassigned in the function body.

**Critical:** The companion `arr_len` parameter must be emitted immediately after `arr`. The names are constructed as `f"{param_name}_len"`. If the IR uses a different naming convention, `arr_len` will be unbound in contract expressions that reference `\length(arr)`.

---

## Phase 3: Expression Translation

`_expr_to_whyml` dispatches on `self.memory_model` (or equivalently `self._uses_heap_model()`) for the following IR node types:

### `Subscript { value: arr, index: i }` — array element read
* Hoare: `arr[i]`
* Typed: `Map.get !int_mem (arr + i)`
* Store: `Map.get !store (arr + i)`

### `Valid { base: arr, length: n }` — validity predicate
* Hoare: `n >= 0 && n <= length arr`
* Typed/Store: `(valid !int_mem arr n)` / `(valid !store arr n)`

### `Separated { base1: a, len1: na, base2: b, len2: nb }` — separation predicate
* Hoare: `true`
* Typed/Store: `(separated a na b nb)`

### `Old` wrapping `Subscript { value: arr, index: i }` — old heap element
* Hoare: `(old arr[i])`
* Typed: `Map.get (old !int_mem) (arr + i)`
* Store: `Map.get (old !store) (arr + i)`

The `old` operator snapshots the entire heap map at function entry; then `Map.get` projects the element out of the snapshot.

### `ArrayLen { var: arr }` / `len(arr)` call — array length
* Hoare: `length arr`
* Typed/Store: `arr_len`

### `At { expr, label: L }` — heap or variable at label (Phase 5)
* If `expr` is `Subscript { value: arr, index: i }` AND typed/store:
  `Map.get (int_mem at L) (arr + i)` / `Map.get (store at L) (arr + i)`
  Note: no `!` before the heap variable inside the `at` construct — Why3 syntax is `(var at L)`, not `(!var at L)`.
* Otherwise (hoare, or scalar expression):
  `(inner_whyml at L)`

---

## Phase 4: Statement Translation

### `ArraySet { array: arr, index: idx, value: val }` — array element write
* Hoare: `arr[idx] <- val`
* Typed: `int_mem := Map.set !int_mem (arr + idx) val`
* Store: `store := Map.set !store (arr + idx) val`

### `For { target, iter, body, invariants, variants }` — for-each loop
The `For` handler builds a while loop. The loop condition and element binding are model-dependent:
* Hoare condition: `!_idx < length <iter>`
* Typed/Store condition: `!_idx < arr_len`

* Hoare element binding: `let <target> = ref (<iter>[!_idx]) in`
* Typed element binding: `let <target> = ref (Map.get !int_mem (<iter> + !_idx)) in`
* Store element binding: `let <target> = ref (Map.get !store (<iter> + !_idx)) in`

---

## Phase 5: Label Statements and `\at` Expressions

### `Label { name: L }` statement
IR: `{"stmt": "Label", "name": "L"}`

This represents a Why3 program point label, produced by `#@ label L` annotations in the source. The `Label` handler in `_stmts_to_whyml` **takes ownership of all remaining statements** in the current block. The tail is the body of the label construct:

```whyml
label L in
<rest of block>
```

The same pattern applies in both hoare and typed/store models — the label syntax is model-independent. What changes is that inside the body, `\at(arr[i], L)` uses `Map.get (int_mem at L) (arr + i)` in typed/store mode.

**Wrong implementation (do NOT do this):**
```whyml
(* This is wrong — Label is NOT a separator *)
label L;
<rest of block>
```

**Correct implementation:**
```whyml
label L in
<rest of block including all remaining stmts>
```

### `At { expr, label }` expression — see Phase 3 above

---

## Frame Conditions (`_emit_frame_condition`)

Called by `transpile()` after emitting all `ensures` clauses for a function. Returns a string of additional `writes` and `ensures` annotations that specify which heap locations are unchanged.

### Hoare model
Always returns `""` — frame conditions are not needed because arrays are value types passed by reference through Why3's `array.Array` abstraction.

### Typed / Store model
Inspects `func.get("assigns")`:

**Case 1: `\assigns arr[lo..hi]`** (range assignment)
Adds `writes { int_mem }` to the function header (the list of written global refs).
Emits:
```whyml
ensures { forall l : int. not (arr + lo <= l /\ l < arr + hi) ->
    Map.get !int_mem l = Map.get (old !int_mem) l }
```
This states: every heap location outside the assigned range is unchanged.

**Case 2: `\assigns \nothing`** (no side effects)
Does NOT add `writes { int_mem }`.
Emits:
```whyml
ensures { !int_mem = old !int_mem }
```
This states: the entire heap map is unchanged.

**Case 3: no `assigns` annotation**
Returns `""` — no frame condition is emitted. This is the default for functions that do not carry a `\assigns` ACSL annotation.

---

# KEY INVARIANTS
* **`local_refs`** = set of all variable names that are ever the target of an assignment in the body. These MUST be dereferenced with `!` when read.
* **`declared_refs`** = set of `local_refs` variables that have already been introduced by a `let x = ref …` binding (or passed as a `ref` parameter). Once a variable is in `declared_refs`, reassignment uses `:=` not `let … = ref … in`.
* **`ref` parameters** (variables with `obj_` prefix in symbol_table of *standalone* functions that are also mutated) are added to `declared_refs` BEFORE body translation begins — they do not need a `let` wrapper.
* **Class methods (Level 2) do NOT use `ref` parameters.** Field mutation is expressed via `FieldAssign`/`FieldAugAssign` which emit `self.field <- ...` (WhyML record update), not `:=` (ref assignment). The `(self: classname)` parameter is the only field-carrying argument.
* **Contracts for methods use an empty `spec_refs` set**, because `FieldGet` nodes emit `self.field` as a plain field access (no `!`) and `OldField` emits `(old self.field)` — no ref-dereference machinery needed.
* **`invariant_ctx=True`** is passed to `_expr_to_whyml` when emitting Why3 record invariant blocks. In this mode, `FieldGet` emits only the bare field name (e.g., `_value`) instead of `self._value`, because Why3's record invariant syntax references fields without the object prefix. This flag is always `False` for method contracts and body expressions.
* **`memory_model` governs array parameter representation uniformly.** ALL of `_expr_to_whyml`, `_stmts_to_whyml`, `transpile()`, `_emit_heap_preamble()`, and `_emit_frame_condition()` must check `self.memory_model` (or `self._uses_heap_model()`) consistently. Mixing hoare and typed/store emission paths within a single function output will produce a type-incorrect WhyML module.
* **In typed/store model, `list` parameters NEVER appear in `local_refs`.** They are locations (`loc`), not mutable refs. Their companion `arr_len` is also a plain `int` parameter, not a ref. Attempting to dereference them with `!` will cause a Why3 type error.
* **Frame conditions are emitted AFTER `ensures` clauses** in the function spec. The order is: `requires` clauses, then `ensures` clauses, then frame conditions from `_emit_frame_condition`. Reversing this order does not affect correctness, but the conventional Why3 ordering is `requires` then `ensures` then `writes`.
* **`Label` statement takes the REST of the block as its body.** It is not a separator. All remaining statements after a `Label` node must be nested INSIDE the `label L in …` expression. This follows the same "takes the tail" pattern as `let x = ref v in <rest>`.

# EXTENSION HEURISTICS
When adding a new IR statement kind:
1. Add a handler in `_stmts_to_whyml` for the new `"stmt"` value.
2. Chain the result into the rest of the block with `";\n" + self._stmts_to_whyml(rest, …)`.
3. If the new node introduces mutable variables, update `_find_assigned_vars` to scan its body.
4. Ensure `_find_return_type` recurses into any nested body keys of the new node.
5. If the new node has memory-model-dependent behaviour, add a branch on `self._uses_heap_model()` (or `self.memory_model`) and implement both paths. Never assume hoare-only.
6. Update `_uses_arrayset` / `_uses_subscript` / `_uses_for` if the new node can contain array-related sub-expressions, so `needs_array` / `needs_map` is set correctly.

When adding a new IR expression kind:
1. Add a handler in `_expr_to_whyml` for the new `"type"` value.
2. If the expression has model-dependent output, add both hoare and typed/store branches.
3. If the expression introduces a new Why3 theory dependency (e.g., a new `use` statement), add a `_uses_X` helper and wire it into the header assembly in `transpile()`.

## Debugging Heuristics

* **`"Cannot find theory 'Map'"`** → preamble missing `use map.Map`; either the memory model was not set to typed/store, or `_uses_heap_model()` is returning `False` incorrectly. Check that `self.memory_model` was set in `__init__` and that `_emit_heap_preamble` is being called.
* **`"type mismatch: 'array int' vs 'loc'"`** → function is still emitting hoare-style `(arr: array int)` while `memory_model="typed"`. Check the parameter emission loop in `transpile()` — the `list`-typed branch must check `self._uses_heap_model()` and emit `(arr: loc) (arr_len: int)` instead.
* **`"arr_len unbound"`** → a contract uses `\length(arr)` (translated to `arr_len`) but the companion length parameter was not emitted. Verify that all `list`-typed params in `symbol_table` trigger dual emission `(arr: loc) (arr_len: int)` and that `_expr_to_whyml` maps `ArrayLen`/`len()` to `arr_len` in typed/store mode.
* **`"label 'L' not found"`** → `\at(expr, L)` is used in a contract or expression but no `label L in` was emitted in the function body. Check that Module 1 / Module 3 attached a `#@ label L` annotation before at least one statement in scope, and that the `Label` IR node is being generated and not silently skipped.
* **`"'valid' predicate undefined"`** → `use map.Map` was emitted (indicating typed/store mode was detected) but the predicate definitions (`predicate valid …`, `predicate separated …`) are missing from the preamble. Check that `_emit_heap_preamble()` is called and its return value is included in the header, not discarded.
* **`"expected 'in' after 'label L'"`** (Why3 parse error) → `Label` was emitted as a statement separator instead of taking the rest of the block as its body. Fix: the `Label` handler must consume `stmts[1:]` as its tail, just as `Assign` does for `let … in` bindings.
* **`"Map.get applied to non-map type 'array int'"`** → `_uses_heap_model()` returned `True` (typed/store emission path was taken for expressions) but `transpile()` still emitted `use array.Array` and `(arr: array int)` parameters. Ensure the header and parameter loops are guarded by the same `_uses_heap_model()` check as the expression translator.
