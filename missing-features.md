# PyCSL Python Subset — Missing Features Plan

> Revision 4 (2026-05-19). Concrete implementation plan derived from
> inspecting the transpiler source and running the 31 failing reference
> tests. Adds decorator support (`@property`, `@dataclass`, `@v_args`,
> `@staticmethod`, `@classmethod`).

---

## 0. Current State

**Pipeline modules**: M1 (Ingestor) → M2 (Parser) → M3 (Weaver) →
M4 (SemanticAnalyzer) → M5 (IREmitter) → M6 (WhyMLTranspiler).

**Key files**:
- `src/pycsl/Module2_Parser.py` — contract expression grammar
- `src/pycsl/Module5_IREmitter.py` — Python AST → PyCSL IR
- `src/pycsl/Module6_WhyMLTranspiler.py` — IR → WhyML
- `src/pycsl/ir_schema.py` — IR node definitions

**Test suite**: 784 tests. 31 were failing; 30 now marked `pycsl-expected:
FAIL`, 1 fixed (0185 — while-loop invariant rewritten for NIA). This plan
addresses the underlying causes so the XFAIL markers can eventually be
removed.

---

## 1. Feature-by-Feature Analysis

### 1.1 `break` statement — ALREADY IMPLEMENTED

**Transpiler support**: Complete.
- M5 (`Module5_IREmitter.py:508-509`): emits `{"stmt":"Break"}`.
- M6 (`Module6_WhyMLTranspiler.py:1440-1444, 1556-1561`): wraps loops in
  `try … with PyCSL_Break -> () end` when `IRScanner.uses_break()` detects
  a break inside the body. `PyCSL_Break` is declared as an exception in the
  WhyML module header.

**Failing test 0177**: Uses `for i in range(100)` without loop invariant +
`assert i == 5` after the loop. Fails because:
1. `for` loop desugaring loses the binding of `i` after the loop.
2. No loop invariant → solver cannot establish postcondition.

**Failing test 0178**: Uses `for` + `continue` + assert — same root cause.

**Action**: Remove XFAIL from 0177/0178 if for-loop `i` binding and loop
annotations are fixed (depends on §1.5 below). Otherwise, keep XFAIL.

---

### 1.2 `match`/`case` — PARTIALLY IMPLEMENTED

**Transpiler support**: Scaffold exists but is buggy.
- M5 (`Module5_IREmitter.py:512-577`): emits `{"stmt":"Match"}` with
  pattern IR for `Value`, `Singleton`, `As`, `Or`, `Sequence`, `Wildcard`,
  `Capture` patterns.
- M6 (`Module6_WhyMLTranspiler.py:1811-1847`): lowers to `if/else if`
  chains via `_match_pattern_cond()`.

**Bug observed**: Match arms that `return` a value produce WhyML type
errors. Example (test 0199, wildcard pattern):
```whyml
if true then begin
  0         (* ← int, but WhyML expects () here *)
end
```
The transpiler emits the matched value as a bare expression instead of
wrapping it in a `return` or letting it flow to the function return.

**Tests failing (10)**: 0192 (Unknown/sat — tuple pattern), 0193 (no mlw —
guard), 0194 (type error — capture), 0196 (type error — as pattern),
0198 (type error — capture), 0199 (type error — wildcard), 0200
(Unknown/sat — value pattern), 0202 (timeout — sequence), 0203
(Unknown/sat — mapping), 0204 (scope error — class pattern).

**Root causes** (three distinct bugs):

| Bug | Tests | Fix |
|-----|-------|-----|
| Match arms returning values emit bare `int` instead of `return`-style let-binding | 0194, 0196, 0198, 0199 | M6: wrap match-arm value expressions in the surrounding `let result = … in` context |
| Pattern condition for tuple/value patterns produces unprovable VCs | 0192, 0200, 0203 | M6: `_match_pattern_cond` should decompose tuples into per-element equalities |
| Capture pattern rebinding emits `let y = …` in scope where `y` already exists | 0204 | M6: use `y := scrutinee` instead of `let y = …` for mutable bindings |

**Effort**: 1 week (fix the 3 bugs). Full pattern coverage (sequence,
mapping, class) would take 2–3 weeks more.

**Implementation plan**:

**Step M1** — Fix match-arm return value wrapping (M6):
- In `_handle_match_stmt()`, detect whether the match is in tail position
  (last statement before function return).
- If so, each arm should produce `result := <value>` rather than a bare
  expression.
- If not in tail position, each arm should be a statement block ending in
  `()` (unit).

**Step M2** — Fix tuple pattern decomposition (M6):
- `_match_pattern_cond("Tuple", scrutinee, pattern)` should emit:
  `(scrutinee[0] = pat_0) /\ (scrutinee[1] = pat_1) /\ …`
- Requires the tuple to be modelled as an array or as individual `let`
  bindings at the match entry point.

**Step M3** — Fix capture pattern scoping (M6):
- Capture patterns (`case n:`) should emit `n := scrutinee` (assignment to
  existing `ref`) rather than `let n = scrutinee` (shadowing declaration).

**Step M4** — Guard support (M6):
- Guard conditions (`case n if n > 5:`) should emit:
  `if (pattern_matches && guard) then arm else …`
- Currently the guard condition is likely dropped or mis-placed.

---

### 1.3 Class Dunders — PARTIALLY IMPLEMENTED

**Transpiler support**: Basic class infrastructure exists.
- M5: `visit_ClassDef` extracts `__init__` fields → WhyML record type.
  Methods are emitted with `kind="method"` and `self_type`.
- M6: Records become `type c = { mutable _v: int }`. Methods become
  standalone `let c__method (self: c) = …`.

**What works**: Simple classes with `__init__` and plain methods. The
record type and field access are generated correctly.

**What fails**: Operator dunders (`__add__`, `__getitem__`, `__mul__`,
etc.) and magic methods (`__getattr__`, `__setattr__`). Observed in
WhyML for test 0060:
```whyml
val get_0 () : int    (* C(6).get() → opaque abstract call *)
```
The call `C(6).get()` is not resolved to the method body. Instead, it
becomes an abstract `val` because constructor+method chaining
(`C(6).get()`) isn't handled.

**Tests failing (9)**: 0060 (instance methods), 0061 (generators on
class), 0076 (__getattr__/__setattr__), 0078 (descriptors), 0087
(isinstance), 0091 (__getitem__), 0092 (__add__/__mul__), 0146
(class attributes), 0211 (PEP 695 generics).

**Implementation plan**:

**Step C1** — Method call resolution (M6, 3 days):
- When `obj.method(args)` appears and `obj` is a known record type,
  inline the call as `type__method(obj, args)` instead of emitting an
  abstract `val`.
- Requires M5 to track which local variables have class types (already
  partially done via `self_type`).

**Step C2** — Constructor chaining (M5+M6, 2 days):
- `C(6).get()` → desugar to: `let _tmp = C__init(6) in C__get(_tmp)`.
- M5 must detect `ast.Call(func=ast.Attribute(value=ast.Call(...)))` and
  emit a temporary.

**Step C3** — Operator dunders (M6, 1 week):
- Map `a + b` to `type__add(a, b)` when `a` has a class type with
  `__add__`.
- Requires a dunder → WhyML function lookup table.
- Priority dunders: `__add__`, `__sub__`, `__mul__`, `__getitem__`,
  `__len__`, `__eq__`, `__lt__`.

**Step C4** — `isinstance` / `__instancecheck__` (M6, 2 days):
- `isinstance(x, T)` → always `true` when `x` is constructed from `T`.
- Model as `true` literal (safe overapproximation) or track types in a
  ghost variable.

**Total effort**: 2–3 weeks.

---

### 1.4 Closures / `nonlocal` — NOT IMPLEMENTED

**Transpiler support**: None.
- No `ast.Nonlocal` handling in M5.
- No free-variable analysis or closure capture.
- Lambda emits an abstract `val` with no body.

**Test failing**: 0182 (nonlocal binding).

**Implementation plan**:

**Step N1** — Scope analysis (M5, 3 days):
- Add a pre-pass that identifies free variables for each nested function
  definition.
- Record which variables are `nonlocal` and which are captured by closure.

**Step N2** — Closure environment (M5+M6, 1 week):
- Model closures as WhyML records containing captured variables:
  ```whyml
  type closure_env = { mutable captured_x: ref int }
  ```
- The outer function creates the record; the inner function receives it.

**Step N3** — Lambda lowering (M5+M6, 3 days):
- `lambda x: x + 1` → named function `_pycsl_lambda_N` with the lambda
  body, then reference by name at call sites.
- Pure lambdas (no mutable captures) can be emitted as `fun x -> x + 1`
  directly in WhyML.

**Total effort**: 2–3 weeks.

---

### 1.5 Slicing — PARTIALLY IMPLEMENTED

**Transpiler support**: Scaffold exists.
- M5 (`Module5_IREmitter.py:294-303, 381-385`): emits `SliceAccess` and
  `Slice` IR nodes.
- M6 (`Module6_WhyMLTranspiler.py:1267-1277, 1344-1358`): handles
  `SliceAccess` and declares `val array_slice`.

**What works**: The WhyML declares an abstract `val array_slice` function.
**What fails**: `array_slice` has no axiomatisation — `iter_length` return
value is unknown to the prover, so postconditions involving sliced arrays
are unprovable.

**Test failing**: 0151.

**Implementation plan**:

**Step S1** — Axiomatise `array_slice` (M6, 2 days):
- Add postconditions to the `val array_slice` declaration:
  ```whyml
  val array_slice (a: array int) (lo hi: int) : array int
    requires { 0 <= lo /\ lo <= hi /\ hi <= length a }
    ensures  { length result = hi - lo }
    ensures  { forall k. 0 <= k < hi - lo -> result[k] = a[lo + k] }
  ```

**Step S2** — Slice assignment (M5+M6, 3 days):
- `a[lo:hi] = b` → emit `for k = 0 to hi-lo-1 do a[lo+k] <- b[k] done`.
- Step slicing (`a[::2]`) remains out of scope.

**Total effort**: 1 week.

---

### 1.6 `except*` / `ExceptionGroup` — NOT IMPLEMENTED

**Transpiler support**: Regular try/except exists.
- M5 (`Module5_IREmitter.py:447-488`): emits `Try` / `Raise` for regular
  exception handling.
- M6 (`Module6_WhyMLTranspiler.py:1587-1645`): wraps body in
  `try … with PyCSL_Exception -> handler end`.
- No `ast.TryStar` (`except*`) handling.

**Test failing**: 0187 (ExceptionGroup).

**Implementation plan**:

**Step E1** — `except*` desugaring (M5, 1 week):
- `except*` splits an `ExceptionGroup` by type. In the formal model,
  desugar to a chain of `try/except` blocks that filter by exception type.
- This is a Python 3.11+ feature with complex semantics (unmatched
  exceptions propagate as a new group).

**Step E2** — Exception type discrimination (M6, 3 days):
- Currently the transpiler uses a single `PyCSL_Exception` for all
  exceptions. To support `except*`, we need typed exceptions:
  ```whyml
  exception PyCSL_ValueError of int
  exception PyCSL_TypeError of int
  ```
- Map Python exception class names to WhyML exception constructors.

**Total effort**: 2 weeks. Low priority — `except*` is rare in
verification-target code.

---

### 1.7 `eval()` — OUT OF SCOPE

**Transpiler support**: None (generic `ast.Call` fallback).

`eval()` executes arbitrary strings as Python code at runtime. This is
fundamentally incompatible with static verification — the code being
evaluated is not known at analysis time.

**Test failing**: 0217.

**Recommendation**: Keep `pycsl-expected: FAIL`. If a user's code uses
`eval()`, it must be wrapped in `#@ \trusted`. No transpiler change
needed.

---

### 1.8 Generators / `yield` / `async` — OUT OF SCOPE

**Transpiler support**: None.

Lazy evaluation (generators) and concurrent execution (async/await)
are fundamentally incompatible with Why3's eager, sequential execution
model.

**Tests failing**: 0061 (yield on class), 0099 (async generator),
0141 (generator + sum), 0175 (yield statement).

**Recommendation**: Keep `pycsl-expected: FAIL`. Abstract generator
calls via `\trusted` stubs in `data/lib_stubs/`.

---

### 1.9 `@staticmethod` — NOT IMPLEMENTED

**Transpiler support**: None — `@staticmethod` methods are silently
mis-handled.

**Current behaviour** (`Module5_IREmitter.py:694-778`):
- Line 696-701: Inside a class, M5 skips all dunder methods and
  `@property`-decorated methods.
- Line 776-778: All surviving methods get `kind="method"` and
  `self_type=ClassName` — including `@staticmethod` methods, which
  have no `self` parameter.
- Line 699-700: The decorator check only looks for `@property`;
  `@staticmethod` and `@classmethod` are not detected.

**Result in M6** (`Module6_WhyMLTranspiler.py:2600-2604`): When
`kind="method"`, M6 prepends `(self: classname)` to the parameter list
and sets `_current_self_type`. For a `@staticmethod` that has no `self`,
this produces a WhyML function with a spurious `self` parameter that is
never used, causing type errors or unprovable VCs at call sites.

**Example of the bug**:
```python
class Math:
    @staticmethod
    def add(a: int, b: int) -> int:
        return a + b
```
Currently emits:
```whyml
let math__add (self: math) (a: int) (b: int) : int = a + b
```
Should emit:
```whyml
let math__add (a: int) (b: int) : int = a + b
```

**Implementation plan**:

**Step SM1** — Detect `@staticmethod` in M5 (1 hour):
- In `visit_FunctionDef()`, after the `@property` check at line 699, add:
  ```python
  is_static = any(isinstance(d, ast.Name) and d.id == 'staticmethod'
                   for d in node.decorator_list)
  ```
- When `is_static` is true and we're inside a class, set
  `func_ir["kind"] = "static_method"` instead of `"method"`, and do
  **not** set `func_ir["self_type"]`.
- Still prefix the function name with the class name
  (`f"{self._current_class.lower()}__{node.name}"`).

**Step SM2** — Handle `kind="static_method"` in M6 (1 hour):
- In `_emit_function()` at line 2577-2604, add a branch:
  ```python
  is_static = func.get("kind") == "static_method"
  is_method = func.get("kind") == "method"
  ```
- When `is_static`: do NOT prepend `(self: type)`, do NOT set
  `_current_self_type`. Emit parameters exactly like a free function.

**Step SM3** — Handle `@classmethod` (bonus, 1 hour):
- Same pattern: detect `@classmethod` decorator → set
  `func_ir["kind"] = "class_method"`.
- In M6, `@classmethod` receives `cls` as first parameter. In WhyML,
  `cls` has no meaningful type (classes are not values in Why3). Model
  it as an `int` sentinel or simply drop it and treat the method as
  static.

**Step SM4** — Call-site resolution (M6, 2 hours):
- When `ClassName.static_method(args)` appears, resolve it to
  `classname__static_method(args)` without inserting a `self` argument.
- Requires checking `_module_func_names` for static method names.

**Total effort**: 1 day.

---

### 1.10 `@property` — SKIPPED (needs implementation)

**Transpiler support**: Actively skipped.
- M5 (`Module5_IREmitter.py:699-701`): Inside a class, any method
  decorated with `@property` is silently dropped — its body is never
  emitted to the IR. The agent pipeline (`agent-annotate.py:307-311`,
  `agent-splitter.py:88-89,576`) also skips `@property` methods for
  annotation.
- No `@name.setter` / `@name.deleter` handling exists anywhere.

**Consequence**: Property access `obj.x` falls through to field-level
`getattr_Type` / `setattr_Type` abstract stubs, which have no relation to
the property body. Contract-bearing property getters are therefore
invisible to verification.

**How `@property` works in Python**:
```python
class Circle:
    def __init__(self, r: int) -> None:
        self._r = r

    @property
    def radius(self) -> int:
        return self._r

    @radius.setter
    def radius(self, v: int) -> None:
        self._r = v
```
Accessing `c.radius` calls the getter; `c.radius = 5` calls the setter.

**WhyML modelling strategy**: Properties are pure accessor functions.
A getter can be modelled as a WhyML `function` (pure, total) returning
a field:
```whyml
function circle__radius (self: circle) : int = self._r
```
A setter is a regular `let` that mutates the record field:
```whyml
let circle__set_radius (self: circle) (v: int) : unit =
  self._r <- v
```
Call sites `obj.radius` and `obj.radius = v` must then resolve to the
getter/setter function instead of the generic `getattr`/`setattr` stubs.

**Implementation plan**:

**Step P1** — Stop skipping `@property` methods in M5 (2 hours):
- Remove the blanket `return` at line 699-701.
- Instead, detect the `@property` decorator and set:
  ```python
  func_ir["kind"] = "property_getter"
  func_ir["self_type"] = self._current_class
  ```
- Detect `@<name>.setter` by checking for `ast.Attribute` decorators:
  ```python
  if (isinstance(d, ast.Attribute) and d.attr == 'setter'):
      func_ir["kind"] = "property_setter"
  ```

**Step P2** — Emit property getter as pure function in M6 (2 hours):
- When `kind="property_getter"`, emit:
  ```whyml
  function type__propname (self: type) : int = <body>
  ```
  If the body is a simple field return (`return self._field`), inline
  as `self.field`. If the body is complex, fall back to a `let` function
  with a postcondition relating the result to fields.

**Step P3** — Emit property setter in M6 (2 hours):
- When `kind="property_setter"`, emit a `let` function that takes
  `self` and a value parameter, and mutates the underlying field.
- The setter method's second parameter (after `self`) becomes the value.

**Step P4** — Resolve `obj.prop` to getter/setter calls (M6, 3 hours):
- In attribute access (`FieldGet`), check if the field name matches a
  known property getter → emit `type__propname(obj)` instead of
  `getattr_type obj <hash>`.
- In attribute assignment, check for known property setter → emit
  `type__set_propname(obj, value)`.
- Build a lookup table `{(class, prop_name) → kind}` during type_decl
  emission.

**Step P5** — Update agent pipeline (1 hour):
- Remove the `is_property` skip in `agent-annotate.py:307-311` and
  `agent-splitter.py:576`.
- Allow property methods to be annotated with contracts.

**Total effort**: 2 days.

---

### 1.11 `@dataclass` — NOT IMPLEMENTED

**Transpiler support**: None.
- M5 `visit_ClassDef` (`Module5_IREmitter.py:643-692`) only extracts
  fields from explicit `__init__` bodies by walking `ast.Assign` /
  `ast.AnnAssign` nodes that target `self.*`.
- A `@dataclass` has no hand-written `__init__`; fields are declared as
  class-level annotations. M5 therefore finds zero fields and emits no
  `type_decl` record.
- No decorator check on the class node exists in `visit_ClassDef`.

**How `@dataclass` works in Python**:
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```
Python auto-generates `__init__(self, x, y)`, `__repr__`, `__eq__`, and
optionally `__hash__`, `__lt__` etc. (via `order=True`, `frozen=True`).

**Consequence**: A `@dataclass` class produces an empty record type `{}`
in WhyML, with no fields — all attribute access becomes abstract
`getattr`/`setattr` stubs. The auto-generated `__init__` is never seen
because M5 walks the AST (where no `__init__` exists), not the runtime
class.

**WhyML modelling strategy**: Extract fields from class-body
`ast.AnnAssign` nodes (e.g., `x: int`) and synthesise the same WhyML
record as if an `__init__` existed:
```whyml
type point = { mutable x: int; mutable y: int }
```
If `frozen=True`, emit immutable fields (no `mutable` prefix).

For `@dataclass(order=True)`, auto-generate comparison functions:
```whyml
function point__lt (a b: point) : bool = a.x < b.x \/ (a.x = b.x /\ a.y < b.y)
```

**Implementation plan**:

**Step DC1** — Detect `@dataclass` in `visit_ClassDef` (M5, 2 hours):
- Check `node.decorator_list` for:
  - `ast.Name(id='dataclass')` — bare `@dataclass`
  - `ast.Call(func=ast.Name(id='dataclass'))` — `@dataclass(...)` with
    arguments (extract `frozen`, `order`, `eq` keyword args)
  - `ast.Attribute(attr='dataclass')` — `dataclasses.dataclass`
- Set a flag `is_dataclass = True` and extract options.

**Step DC2** — Extract fields from class-body annotations (M5, 2 hours):
- When `is_dataclass` is true, scan `node.body` for `ast.AnnAssign`
  nodes at class level (not inside methods):
  ```python
  for stmt in node.body:
      if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
          fields.append({"name": stmt.target.id, "type": "int", "mutable": not frozen})
  ```
- Also extract default values from `stmt.value` if present.
- This replaces the current `__init__`-walking logic for dataclasses.

**Step DC3** — Handle `field()` defaults (M5, 1 hour):
- `x: int = field(default=0)` or `x: List[int] = field(default_factory=list)`.
- Extract the `default` keyword from `ast.Call` when the function is
  `field`.
- `default_factory` is runtime-only — model as unknown initial value.

**Step DC4** — Synthesise `__eq__` and `__lt__` (M6, 3 hours):
- When the type_decl has `dataclass_eq: true`, auto-emit:
  ```whyml
  function point__eq (a b: point) : bool = a.x = b.x /\ a.y = b.y
  ```
- When `dataclass_order: true`, auto-emit lexicographic comparison.
- Wire `a == b` and `a < b` to these functions when operands have the
  dataclass type (extends §1.3 Step C3 dunder dispatch).

**Step DC5** — Handle `frozen=True` (M6, 1 hour):
- Emit fields without `mutable` prefix.
- Any attempt to assign to a field of a frozen dataclass should be
  flagged as an error in M5 or M6, mirroring Python's
  `FrozenInstanceError`.

**Total effort**: 2 days.

**Note**: PyCSL's own codebase uses `@dataclass` extensively
(`Module1_Ingestor.py`, `Module2_Parser.py`, `ConcurrencyChecker.py`).
Supporting `@dataclass` is essential for self-annotation.

---

### 1.12 `@v_args` and Unknown Decorators — TRANSPARENT

**Transpiler support**: Decorators not in the known set cause silent
mis-handling.

**What `@v_args` is**: A decorator from the `lark` parsing library.
`@v_args(inline=True)` on a `Transformer` class changes how Lark passes
parsed tree children to transformer methods — children are passed as
positional arguments instead of as a list. It does **not** change the
function's signature from the perspective of formal verification.

**Where it appears**: `src/pycsl/Module2_Parser.py:433` —
`@v_args(inline=True)` decorates the `PyCSLTransformer` class. This is
in PyCSL's own source code, so it matters for self-annotation.

**Current behaviour**: When M5 encounters a class-level method inside a
`@v_args`-decorated class, it processes the class normally (the class
decorator is not checked). For function-level decorators, `@v_args` on a
method would be ignored (no check exists in `visit_FunctionDef` for
arbitrary decorators, and the method would proceed with `kind="method"`
as usual).

**General problem — unknown decorators**: The transpiler only recognises
`@property` (skip) in `visit_FunctionDef`. Any other decorator
(`@v_args`, `@lru_cache`, `@functools.wraps`, `@abstractmethod`,
`@override`, `@deprecated`, etc.) is silently ignored. This is usually
acceptable for decorators that don't change the function signature (the
body is still verifiable), but is incorrect for decorators that wrap or
replace the function (e.g., `@lru_cache` changes the return-value caching
semantics).

**WhyML modelling strategy**: Classify decorators into three categories:

| Category | Examples | Action |
|----------|----------|--------|
| **Transparent** (no semantic effect) | `@v_args`, `@abstractmethod`, `@override`, `@deprecated`, `@functools.wraps` | Ignore — verify the function body as-is |
| **Signature-changing** (handled) | `@staticmethod`, `@classmethod`, `@property` | Emit different IR `kind` (§1.9, §1.10) |
| **Behaviour-changing** (unsafe) | `@lru_cache`, `@retry`, custom wrappers | Emit `\trusted` warning or abstract stub |

**Implementation plan**:

**Step VA1** — Build a decorator classification table (M5, 1 hour):
- Add a module-level constant:
  ```python
  TRANSPARENT_DECORATORS = {
      'v_args', 'abstractmethod', 'override', 'deprecated',
      'functools.wraps', 'typing.overload',
  }
  SIGNATURE_DECORATORS = {
      'staticmethod', 'classmethod', 'property',
  }
  ```
- In `visit_FunctionDef`, after detecting `@property`/`@staticmethod`/
  `@classmethod`, check remaining decorators:
  - If in `TRANSPARENT_DECORATORS` → proceed normally.
  - If unknown → emit a warning in the IR: `func_ir["unknown_decorators"] = [...]`.

**Step VA2** — Handle class-level decorators in `visit_ClassDef` (M5, 1 hour):
- Check `node.decorator_list` for `@dataclass` (§1.11), `@v_args`, and
  others.
- Class-level `@v_args` → transparent, proceed normally.
- Unknown class decorators → emit warning in the type_decl.

**Step VA3** — Emit warnings for unknown decorators (M6, 30 minutes):
- When `func_ir["unknown_decorators"]` is non-empty, emit a WhyML
  comment: `(* WARNING: unknown decorator @xxx — verification assumes
  decorator is transparent *)`.
- Optionally: if the decorator is in a "known-unsafe" list, wrap the
  function body in `any { true }` (havoc) unless `\trusted` is set.

**Total effort**: Half a day.

**Note**: For self-annotation, the only decorator that matters is
`@v_args(inline=True)` on `PyCSLTransformer`. Since it's on a class
(not a method), it's already handled transparently. No code change is
strictly required for `@v_args` alone — but the general unknown-decorator
framework (Step VA1) is valuable for robustness.

---

## 2. Implementation Priority

| Priority | Feature | Effort | XFAIL tests unblocked | ROI |
|----------|---------|--------|----------------------|-----|
| **P0a** | `@staticmethod` (§1.9) | 1 day | 0 (no test yet) | **Highest** — trivial fix, unblocks class usage |
| **P0b** | `@property` (§1.10) | 2 days | 0 (no test yet) | **Highest** — unblocks property-based classes |
| **P0c** | `@dataclass` (§1.11) | 2 days | 0 (no test yet) | **Highest** — needed for self-annotation |
| **P0d** | Unknown decorators (§1.12) | ½ day | 0 | High — robustness for any decorated code |
| **P1** | match/case bug fixes (§1.2) | 1 wk | 10 | **High** — already partially works |
| **P2** | Slicing axioms (§1.5) | 1 wk | 1 | Medium |
| **P3** | Class method resolution (§1.3 C1-C2) | 1 wk | 5 | Medium |
| **P4** | Class operator dunders (§1.3 C3-C4) | 1 wk | 4 | Medium |
| **P5** | Closures / nonlocal (§1.4) | 2–3 wk | 1 | Low (1 test) |
| **P6** | `except*` (§1.6) | 2 wk | 1 | Low (1 test) |
| — | `eval()` (§1.7) | never | 1 | Out of scope |
| — | generators/async (§1.8) | never | 4 | Out of scope |

### Critical path

```
P0a (@staticmethod) ──┐
P0b (@property)     ──┤── all independent, do first (1 week total)
P0c (@dataclass)    ──┤
P0d (decorators)    ──┘
        │
        ▼
P1 (match) ──→ P3 (class methods) ──→ P4 (class dunders)
      │
      └──→ P2 (slicing)

P5 (closures) ← independent
P6 (except*) ← independent
```

**Note**: P0c (`@dataclass`) depends on P0a (`@staticmethod`) for
the shared decorator-detection infrastructure in M5. P0b (`@property`)
is independent.

---

## 3. Detailed Changes Per Module

### Module5_IREmitter.py

| Feature | Change | Lines affected |
|---------|--------|---------------|
| Decorator classification | Add `TRANSPARENT_DECORATORS` / `SIGNATURE_DECORATORS` constants | New (top of file) |
| `@staticmethod` detect | Check decorator list; set `kind="static_method"` | ~696-701, ~776-778 |
| `@classmethod` detect | Check decorator list; set `kind="class_method"` | ~696-701, ~776-778 |
| `@property` getter/setter | Stop skipping; set `kind="property_getter"` / `"property_setter"` | ~699-701 |
| `@dataclass` class detect | Check class decorator list; extract fields from class-body `AnnAssign` | ~643-692 |
| Unknown decorators | Emit `unknown_decorators` list in func IR | ~696-701 |
| match return value | Detect tail-position match; emit result assignment | ~512-577 |
| match guard | Thread guard condition into pattern IR | ~551-577 |
| Constructor chaining | Detect `ast.Call(func=ast.Attribute(value=ast.Call))` | ~261-291 |
| Closure scope | Add free-variable pre-pass | New code |
| Lambda | Named function extraction | ~377-380 |

### Module6_WhyMLTranspiler.py

| Feature | Change | Lines affected |
|---------|--------|---------------|
| `static_method` emit | Skip `self` param when `kind="static_method"` | ~2577-2628 |
| Static call resolution | `Class.method()` → `class__method()` without `self` | ~1290-1320 |
| `property_getter` emit | Emit as WhyML `function` (pure) | New |
| `property_setter` emit | Emit as `let` with field mutation | New |
| Property call resolution | `obj.prop` → `type__prop(obj)` | ~1002-1005 |
| `@dataclass` `__eq__`/`__lt__` | Auto-generate comparison functions | New |
| Unknown decorator warning | Emit WhyML comment for unrecognised decorators | New |
| match arm wrapping | Wrap arms in `result :=` or `()` | ~1811-1847 |
| match tuple decomposition | `_match_pattern_cond` → per-element equality | nearby |
| match capture scoping | `:=` instead of `let` | nearby |
| `array_slice` axioms | Add requires/ensures to `val array_slice` | ~1267-1277 |
| Method call inlining | `obj.method()` → `type__method(obj)` | ~1290-1320 |
| Operator dunder dispatch | `a + b` → `type__add(a, b)` for class types | ~1450+ |
| Typed exceptions | Multiple exception constructors | ~1587-1645 |

### Agent pipeline

| Feature | Change | File |
|---------|--------|------|
| `@property` annotation | Remove `is_property` skip | `agent-annotate.py:307-311` |
| `@property` splitting | Remove `is_property` filter | `agent-splitter.py:576` |

---

## 4. Test Recovery Forecast

| After | Tests passing | XFAIL removed | XFAIL remaining |
|-------|-------------|---------------|-----------------|
| Baseline | 753/784 | — | 0 |
| Current (markers added) | 784/784 | — | 30 |
| P0a-P0d done (decorators) | 784/784 | 0 | 30 |
| P1 done (match fixes) | 784/784 | ~7 | 23 |
| P1+P2 done (+slicing) | 784/784 | ~8 | 22 |
| P1+P2+P3 done (+class methods) | 784/784 | ~13 | 17 |
| P1-P4 done (+class dunders) | 784/784 | ~17 | 13 |
| P1-P6 done (all fixable) | 784/784 | ~19 | 11 |
| Theoretical max (no eval/gen/async) | 784/784 | ~25 | 5 |

The decorator features (P0a-P0d) don't unblock existing XFAIL tests
(no test uses `@property`/`@dataclass`/`@v_args`), but they are
prerequisites for self-annotation and for verifying real-world Python
code that uses these pervasive patterns.

The 5 permanently XFAIL tests use features genuinely incompatible with
Why3: `eval()` (0217), async generators (0099), `yield` (0061, 0141,
0175).

---

## 5. Previously Planned Features (from prior revision)

The following items from the prior version of this document remain valid
and are orthogonal to the test-recovery work above:

| # | Feature | Effort | Status |
|---|---------|--------|--------|
| 1 | `assert` → WhyML `check` | 1–2 d | Unchanged |
| 2 | `//` and `%` in contracts | 1 d | Unchanged |
| 3 | `True`/`False`/`None` in contracts | 1 d | Unchanged |
| 4 | `in`/`not in` in contracts | 1 d | Unchanged |
| 5 | Library stubs (`functools`, `itertools`) | 1–2 d each | Unchanged |
| 6 | Walrus operator `:=` | 3 d | Unchanged |
| 8 | Tuple unpacking | 1–2 d | Unchanged |

These are contract-grammar and IR improvements that don't affect the 31
failing tests (which all involve body-level Python features, not contract
syntax).

---

## Key files for implementation

- `src/pycsl/Module2_Parser.py` — EBNF grammar (contract extensions)
- `src/pycsl/Module3_Weaver.py` — AST annotation attachment
- `src/pycsl/Module5_IREmitter.py` — Python AST → IR
- `src/pycsl/Module6_WhyMLTranspiler.py` — IR → WhyML
- `src/pycsl/ir_schema.py` — IR node definitions
- `src/pycsl/agents/agent-annotate.py` — annotation agent
- `src/pycsl/agents/agent-splitter.py` — function splitter for annotation
- `data/lib_stubs/` — trusted library contracts
- `test-suite/corpus/python-reference/` — reference tests
- `test-suite/annotations.md` — annotation documentation
