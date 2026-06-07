# Introspection Plan: `globals()`, `locals()`, `vars()`, `exec`

## Key Insight

PyCSL already maintains a **full AST and symbol table** at every program
point during verification:

- `Module4_SemanticAnalyzer.current_scope: Dict[str, str]` — maps every
  variable name to its type at each function scope
- `collect_module_globals()` — enumerates all module-level bindings
- `Module6_WhyMLTranspiler._current_symbol_table: Dict[str, Any]` —
  the transpiler's live symbol table during WhyML emission

These are exactly what `globals()`, `locals()`, and `vars()` return at
runtime. The difference is that at runtime they're dicts of *values*;
at verification time they're dicts of *types and constraints*. But for
formal verification purposes, **type information is what we need**.

---

## Phase 1: Static Resolution of `globals()` and `locals()`

### 1.1 — `globals()` as a compile-time map

When PyCSL encounters `globals()` in user code, it can resolve it to
the set of module-level names already collected by
`collect_module_globals()`. The result is a **ghost map** (logic-only
variable) of type `Map string type`.

```python
# User writes:
g = globals()
assert "my_func" in g

# PyCSL sees (at Module4 time):
# module_globals = {"my_func": "function", "MY_CONST": "int", ...}
# → statically resolves "my_func" in globals() to True
```

**Implementation**: In `Module4_SemanticAnalyzer`, when visiting a
`Call(func=Name("globals"))`:
1. Collect all module-scope names from the AST
2. Replace the call with a ghost constant `__pycsl_module_globals`
3. Generate axioms: `\forall name in module_names: name \in __pycsl_module_globals`

### 1.2 — `locals()` as the current scope snapshot

When PyCSL encounters `locals()`, it already knows `self.current_scope`
at that exact program point. The resolution is:

```python
def foo(x: int, y: int) -> int:
    z = x + y
    l = locals()  # PyCSL knows: {"x": int, "y": int, "z": int}
    assert "z" in l
    return z
```

**Implementation**: Snapshot `current_scope.keys()` at the call site.
Emit a ghost set literal containing exactly those names.

### 1.3 — `vars(obj)` as class attribute enumeration

For `vars(obj)` where `obj` is a class instance, PyCSL already tracks
class fields via `#@ class invariant` declarations. The resolution:

```python
class Point:
    #@ class invariant self._x >= 0
    #@ class invariant self._y >= 0
    def __init__(self):
        self._x = 0
        self._y = 0

p = Point()
v = vars(p)  # PyCSL knows: {"_x": int, "_y": int}
assert "_x" in v
```

**Implementation**: Walk the class AST, collect `self.field = ...`
assignments from `__init__`. These define the instance dict.

---

## Phase 2: `exec` with Literal Strings

### 2.1 — Static inline of `exec("literal")`

When `exec` is called with a **string literal**, PyCSL can parse that
string at verification time (it already has Python's `ast.parse`):

```python
exec("x = 42")
# PyCSL inlines this as:
# x = 42
# and adds x: int to current_scope
```

**Implementation**:
1. In `Module1_Ingestor`, detect `exec(Constant(value=str))` calls
2. Parse the string with `ast.parse()`
3. Splice the resulting AST nodes into the current function body
4. Continue analysis with the enriched scope

### 2.2 — `exec` with `globals`/`locals` arguments

```python
exec("result = a + b", {"a": 1, "b": 2}, local_dict)
```

When the globals/locals dicts are **literal dicts**, PyCSL can:
1. Build a temporary scope from the literal keys
2. Parse and analyze the exec'd code in that scope
3. Propagate any assignments back to the caller scope

### 2.3 — `exec` with dynamic strings → `\trusted`

When the exec'd string is not a literal (computed at runtime), formal
verification is fundamentally impossible — we'd need to verify all
possible programs. Mark as `\trusted reviewer: dynamic-exec`.

---

## Phase 3: Contract Language Extensions

### 3.1 — New ghost predicates

```
\in_scope(name)          — true iff name is in current locals
\in_globals(name)        — true iff name is a module-level binding
\has_attr(obj, name)     — true iff class of obj declares field name
\scope_type(name)        — the type of name in current scope
```

These are resolved entirely at verification time — zero runtime cost.

### 3.2 — Example contracts

```python
#@ ensures \in_scope("x")
#@ ensures \scope_type("x") == int
def define_x() -> None:
    x = 42

#@ requires \has_attr(self, "_count")
#@ ensures \result == self._count
def get_count(self) -> int:
    return vars(self)["_count"]  # proven via has_attr + field knowledge
```

---

## Phase 4: Integration with Existing Modules

### 4.1 — Where this unblocks `builtins`

With static resolution, we can model the *provable subset* of builtins:

| Builtin | Strategy |
|---------|----------|
| `globals()` | Phase 1.1 — ghost map from module AST |
| `locals()` | Phase 1.2 — ghost set from scope snapshot |
| `vars(obj)` | Phase 1.3 — ghost set from class fields |
| `exec(lit)` | Phase 2.1 — AST splice |
| `eval(lit)` | Same as exec but returns value type |
| `hasattr(o,n)` | Resolves to `\has_attr` at compile time |
| `getattr(o,n)` | Field access if n is literal string |
| `type(x)` | Returns the compile-time type from scope |
| `isinstance(x,T)` | Resolves to type check from scope |
| `len(x)` | Already handled (`\length`) |
| `abs(x)` | Pure arithmetic — trivial |
| `min/max` | Pure arithmetic — trivial |
| `print(...)` | I/O — `assigns world.stdout` |
| `input()` | I/O — `assigns world.stdin` |
| `open(...)` | I/O — delegates to world.fs |

### 4.2 — Where this unblocks `sys`

| sys function | Strategy |
|-------------|----------|
| `sys.modules` | Ghost map from import graph (Module1 already has it) |
| `sys.argv` | Points to `world.proc.argv` |
| `sys.path` | Points to `world.proc.path` |
| `sys.exit()` | Modeled as exception (already in exception_model.py) |
| `sys.getrecursionlimit()` | Constant (default 1000) |
| `sys.getsizeof(x)` | Returns type-specific constant from scope |

### 4.3 — Where this unblocks `types`

| types member | Strategy |
|-------------|----------|
| `types.FunctionType` | Resolves to `\is_function` predicate |
| `types.ModuleType` | Resolves to `\is_module` predicate |
| `types.MethodType` | Resolves to bound-method ghost type |
| `types.NoneType` | Resolves to void/unit type |

---

## Phase 5: Implementation Roadmap

### Step 1 — Ghost scope predicates (2-3 days)

Modify `Module4_SemanticAnalyzer`:
- Add `\in_scope`, `\in_globals`, `\has_attr` to the CSL grammar
- Resolve them to `true`/`false` at analysis time
- Emit as WhyML `assert` (trivially provable)

### Step 2 — `globals()`/`locals()` rewriting (1-2 days)

Modify `Module5_IREmitter`:
- Detect `globals()` / `locals()` calls
- Replace with ghost set literal containing scope keys
- Membership tests (`"x" in locals()`) become compile-time `true`/`false`

### Step 3 — `exec` literal inlining (3-4 days)

Modify `Module1_Ingestor`:
- Pattern-match `exec(Constant(value=...))` 
- Parse the constant string
- Splice the resulting AST, preserving line numbers
- Error if the inner code has contracts (no nested verification)

### Step 4 — `builtins` pure_lib module (1-2 days)

Create `pure_lib/builtins/__init__.py` with:
- Pure arithmetic: `abs`, `divmod`, `pow`, `round`, `min`, `max`, `sum`
- Type predicates: `isinstance`, `issubclass`, `hasattr`, `callable`
- Scope introspection: `globals`, `locals`, `vars` (as ghost wrappers)
- I/O: `print`, `input`, `open` (delegates to World)

### Step 5 — `types` and `sys` modules (1-2 days)

Upgrade existing `types_stub` and `sysmod` to use ghost predicates.

---

## Difficulty Assessment

| Component | Difficulty | Reason |
|-----------|-----------|--------|
| `globals()`/`locals()` | **Medium** | Scope info already exists; just need to expose it as ghost values |
| `vars(obj)` | **Medium** | Class field tracking exists in SemanticAnalyzer |
| `exec(literal)` | **Hard** | AST splicing with scope propagation; error reporting for inner code |
| `exec(dynamic)` | **Impossible** | Halting problem — must be `\trusted` |
| `eval(literal)` | **Hard** | Same as exec but must also determine return type |
| `type()` | **Easy** | Already in scope as type annotation |
| `hasattr/getattr` | **Medium** | Literal string → field lookup; dynamic string → `\trusted` |

---

## Why This Works (and Why It Didn't Before)

The previous approach tried to model `globals()` as a **runtime dict** —
an actual data structure with keys and values. This fails because:
1. The dict is unbounded (any module can inject names)
2. Values have heterogeneous types (PyCSL is monomorphic)
3. Dict operations need string theory (PyCSL has no string solver)

The new approach treats introspection as **compile-time knowledge** that
PyCSL already possesses. We're not modeling the dict at runtime — we're
answering questions about it at verification time, using information the
tool already computed. The "dict" never appears in WhyML; only its
properties (membership, type) appear as ghost assertions.

This is analogous to how C static analyzers handle `sizeof()` — it's not
a runtime function, it's a compile-time constant that the tool resolves.
