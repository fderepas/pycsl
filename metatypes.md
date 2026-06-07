# Metatypes Plan: Modeling `types` Module via Compile-Time Type Tags

## Problem Statement

Python's `types` module exposes **runtime type descriptors**: objects
that represent the kind of entity (function, method, module, class,
coroutine, etc.). Code uses them for `isinstance` checks:

```python
import types

def is_method(obj):
    return isinstance(obj, types.MethodType)

def get_module_name(mod):
    if isinstance(mod, types.ModuleType):
        return mod.__name__
```

These seem to require a runtime type system — but PyCSL already **knows
the type of every expression** at verification time through its AST and
semantic analysis. The `types` module is just exposing information that
the verifier already possesses.

---

## Key Insight: Type Tags as Ghost Constants

Every Python value has a runtime `type()`. PyCSL already classifies
every variable into categories during `Module4_SemanticAnalyzer`:

| PyCSL internal classification | `types` equivalent |
|------------------------------|-------------------|
| `ast.FunctionDef` node | `types.FunctionType` |
| `ast.ClassDef` node | `type` (metaclass) |
| Class method (first param `self`) | `types.MethodType` |
| Module import | `types.ModuleType` |
| `None` literal / void return | `types.NoneType` |
| Lambda expression | `types.LambdaType` |
| Generator function (`yield`) | `types.GeneratorType` |
| Coroutine (`async def`) | `types.CoroutineType` |

We don't need to model these as runtime objects. We model them as
**integer tag constants** and resolve `isinstance(..., types.X)` to
compile-time boolean assertions.

---

## Phase 1: Type Tag Enumeration

### 1.1 — Define tag constants

```python
# In pure_lib/types_mod/__init__.py (or upgrade types_stub)

# Type tags — each is a unique integer identifying a metatype
TAG_NONE       = 0
TAG_INT        = 1
TAG_LIST       = 2
TAG_FUNCTION   = 3
TAG_METHOD     = 4
TAG_MODULE     = 5
TAG_CLASS      = 6
TAG_GENERATOR  = 7
TAG_COROUTINE  = 8
TAG_NAMESPACE  = 9
TAG_CODE       = 10
TAG_FRAME      = 11
TAG_TRACEBACK  = 12
TAG_BUILTIN    = 13
```

### 1.2 — Ghost function `\typeof(expr)`

Add a ghost (logic-only) function to the CSL language:

```
\typeof(x)   — returns the type tag of x (resolved at compile time)
```

In WhyML this becomes a ghost `val function typeof (x: int) : int`
that is axiomatized per-variable based on semantic analysis.

**Resolution rule** (in Module4/Module5):
- If `x` was declared as parameter `x: int` → `\typeof(x) = TAG_INT`
- If `x` was assigned from a function call → `\typeof(x)` = return type tag
- If `x` is `self` in a method → `\typeof(x) = TAG_CLASS`
- If `x` came from an import → `\typeof(x) = TAG_MODULE`

---

## Phase 2: Modeling `types.*Type` Members

### 2.1 — Type descriptor classes as tag comparisons

```python
# types.FunctionType is not a class — it's a tag
FunctionType = TAG_FUNCTION
MethodType   = TAG_METHOD
ModuleType   = TAG_MODULE
NoneType     = TAG_NONE
LambdaType   = TAG_FUNCTION   # Lambda IS a function
GeneratorType = TAG_GENERATOR
CoroutineType = TAG_COROUTINE
```

### 2.2 — `isinstance(x, types.FunctionType)` rewriting

When PyCSL encounters:
```python
isinstance(obj, types.FunctionType)
```

It rewrites this (in Module5 IR) to:
```
\typeof(obj) == TAG_FUNCTION
```

Which is then resolved at verification time:
- If `obj` is known to be a function (from the AST) → `true`
- If `obj` is known to be something else → `false`
- If `obj` is opaque (parameter without annotation) → remains symbolic

### 2.3 — Contract examples

```python
#@ requires \typeof(func) == FunctionType
#@ ensures \result == func
def identity_on_functions(func: int) -> int:
    """Only accepts function-typed values."""
    return func

#@ ensures \typeof(\result) == ModuleType
def import_module(name: int) -> int:
    """Returns a module."""
    return name
```

---

## Phase 3: Attribute Access on Type-Tagged Values

### 3.1 — `ModuleType.__name__`, `FunctionType.__name__`

Python objects have dunder attributes. For type-tagged values:

```python
mod.__name__    # Module name (string length in our model)
func.__name__   # Function name
func.__code__   # Code object (TAG_CODE)
```

Model these as **accessor ghost functions**:

```
\attr_name(x)     — length of __name__ attribute
\attr_module(x)   — tag of __module__ attribute
\attr_doc(x)      — length of __doc__ attribute
```

Resolved from the AST:
- `func.__name__` → length of the function's actual name string
- `mod.__name__` → length of the module's actual name

### 3.2 — `FunctionType.__code__` and `CodeType`

`types.CodeType` has attributes like `co_argcount`, `co_varnames`,
`co_consts`. PyCSL already knows these from the AST:

```python
def foo(a: int, b: int, c: int) -> int:
    x = a + b
    return x + c

# PyCSL knows:
# foo.__code__.co_argcount == 3
# foo.__code__.co_nlocals == 4  (a, b, c, x)
# foo.__code__.co_varnames == ["a", "b", "c", "x"]
```

Model as ghost constants generated per-function:
```
\code_argcount(foo) == 3
\code_nlocals(foo) == 4
```

---

## Phase 4: `types.SimpleNamespace`

`SimpleNamespace` is the one **concrete class** in `types` that users
instantiate. It's a dynamic attribute bag:

```python
ns = types.SimpleNamespace(x=1, y=2)
ns.z = 3
print(ns.x)  # 1
```

### Model as PyCSL class with dynamic fields

```python
""  # pycsl
#@ class invariant self._count >= 0
class SimpleNamespace:
    def __init__(self):
        self._count = 0

    #@ ensures self._count == \old(self._count) + 1
    #@ assigns self._count
    def set_attr(self, name: int, val: int) -> None:
        self._count = self._count + 1

    #@ requires self._count > 0
    #@ assigns \nothing
    def get_attr(self, name: int) -> int:
        return name
```

This is a size model — tracks how many attributes exist but not their
individual values. For full field tracking, needs a map type
(future enhancement, see Phase 6).

---

## Phase 5: `types.new_class` and `types.prepare_class`

These are metaclass factory functions:

```python
MyClass = types.new_class("MyClass", (Base,), {"metaclass": Meta})
```

### Strategy: Opaque with postconditions

```python
#@ requires name >= 0
#@ ensures \typeof(\result) == TAG_CLASS
#@ ensures \result >= 0
def new_class(name: int, bases: list) -> int:
    """Creates a new class. Result is a class-typed value."""
    return name
```

The key contract is `\typeof(\result) == TAG_CLASS` — callers know
they get a class back, enabling downstream `isinstance` resolution.

---

## Phase 6: Integration with PyCSL Pipeline

### 6.1 — Where type tags live in the pipeline

```
Module1 (Ingestor)
  → Parses AST, identifies FunctionDef / ClassDef / Import nodes

Module2 (Parser)
  → Extracts contracts; no type tag work here

Module3 (Weaver)
  → Attaches contracts to AST nodes

Module4 (SemanticAnalyzer)  ← TYPE TAGS RESOLVED HERE
  → current_scope already maps names to types
  → ADD: map names to type TAGS (int enum)
  → ADD: resolve isinstance(x, types.Y) to tag comparison
  → ADD: resolve \typeof(x) to concrete tag when known

Module5 (IREmitter)
  → Emit ghost constants for type tags
  → Emit axioms: \typeof(param_name) == TAG from annotation

Module6 (WhyMLTranspiler)
  → Translate tag comparisons to WhyML int equality
  → Tags are just integers — SMT handles them trivially
```

### 6.2 — What changes in each module

| Module | Change | Effort |
|--------|--------|--------|
| Module4 | Add `_type_tags: Dict[str, int]` alongside `current_scope` | 1 day |
| Module4 | Rewrite `isinstance(..., types.X)` to tag comparison | 1 day |
| Module5 | Emit `\typeof` as ghost `val` with per-variable axioms | 1 day |
| Module6 | No change — int equality already supported | 0 |
| CSL grammar | Add `\typeof` keyword | 0.5 day |

---

## Phase 7: `pure_lib/types_mod` Implementation

Upgrade `pure_lib/types_stub` to a full `pure_lib/types_mod`:

```python
# pure_lib/types_mod/__init__.py

# --- Type tag constants ---
NoneType     = 0
FunctionType = 3
LambdaType   = 3   # Same as FunctionType
MethodType   = 4
ModuleType   = 5
GeneratorType = 7
CoroutineType = 8
CodeType     = 10
FrameType    = 11
TracebackType = 12
BuiltinFunctionType = 13

# --- SimpleNamespace class ---
""  # pycsl
#@ class invariant self._count >= 0
class SimpleNamespace:
    ...

# --- new_class ---
#@ requires name >= 0
#@ ensures \result >= 0
def new_class(name: int, bases: list) -> int: ...

# --- prepare_class ---
#@ requires name >= 0
#@ ensures \result >= 0
def prepare_class(name: int, bases: list) -> int: ...

# --- resolve_bases ---
#@ requires \length(bases) >= 0
#@ ensures \result >= 0
def resolve_bases(bases: list) -> int: ...

# --- coroutine decorator ---
#@ requires func >= 0
#@ ensures \result == func
def coroutine(func: int) -> int: ...
```

---

## Why Integer Tags Work for SMT

SMT solvers excel at integer equality. By encoding Python's metatype
system as integer constants:

1. `isinstance(x, types.FunctionType)` becomes `typeof_x == 3` —
   trivial for Alt-Ergo
2. No need for subtyping/inheritance in the SMT theory
3. Tag dispatch (`if type(x) is int: ... elif type(x) is str: ...`)
   becomes integer case split
4. Mutually exclusive: `typeof_x == 3 → typeof_x ≠ 4` is free from
   distinctness

The type hierarchy (e.g., `MethodType` is-a `FunctionType`) can be
modeled with axioms:
```
axiom method_is_callable:
  \typeof(x) == TAG_METHOD ==> \is_callable(x)
axiom function_is_callable:
  \typeof(x) == TAG_FUNCTION ==> \is_callable(x)
```

This keeps everything in first-order integer logic — exactly what PyCSL
and Why3/Alt-Ergo handle well.

---

## Difficulty Assessment

| Component | Difficulty | Reason |
|-----------|-----------|--------|
| Tag constants | **Trivial** | Just integer definitions |
| `\typeof` ghost function | **Medium** | New CSL keyword + resolution in Module4 |
| `isinstance` rewriting | **Medium** | Pattern-match in Module4, emit as int == |
| `SimpleNamespace` class | **Easy** | Already have class pattern in pure_lib |
| `__code__` attributes | **Medium** | Need per-function ghost constants from AST |
| `new_class`/`prepare_class` | **Easy** | Opaque stubs with type tag postcondition |
| `types.MethodType(func, obj)` | **Hard** | Binding func to instance — needs closure model |
| Dynamic `type()` calls | **Hard** | When argument isn't statically known |

---

## Summary

Total estimated effort: **~5 days** for core (Phases 1-3, 6-7),
+3 days for advanced features (Phases 4-5, MethodType binding).

The approach re-uses the same philosophy as `introspect.md`:
**don't model runtime behavior — expose compile-time knowledge**.
PyCSL already knows every variable's type; we just surface that as
integer tags that SMT solvers handle trivially.
