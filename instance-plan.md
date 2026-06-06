# Plan: `\instanceof` Contract Predicate for PyCSL

## Problem

When a `#@ \trusted` library stub returns an object (e.g., `argparse.ArgumentParser()`),
the contract currently says `#@ ensures True` — which conveys zero information
to the caller. We want to express that the result is an instance of a
specific class, e.g.:

```python
#@ ensures \instanceof(\result, ArgumentParser)
```

This lets downstream contracts reason about what type of object they receive,
enabling type-safe composition across library boundaries.

## Current State

- **No `\instanceof` predicate exists** anywhere in the PyCSL pipeline.
- PyCSL's type universe already supports multiple WhyML types — not just `int`:
  - `int` — default for unannotated, `int`, `bool`, `str`, `float`
  - `array int` — for `list` parameters and return types
  - `unit` — for `-> None` return types
  - Record types — for classes (`type classname = { mutable field: int }`)
  - `map int (option int)` — for body dicts, body sets, ghost_dicts
  - `ref string` — for ghost strings
  - `ref (list int)` — for ghost_lists
  - `ref (map int bool)` — for ghost_sets
  - `ref (int, int)` etc. — for ghost tuples
- Classes are already supported as WhyML mutable records, but there's no way
  to express "this value is an instance of class X" in a contract.
- The contract parser (Module2) supports: arithmetic, comparisons, booleans,
  `\result`, `\old`, `\length`, `\forall`/`\exists`, `\is_sorted`, `\sum`,
  pure function calls, ghost atoms. No type predicates.

## Design

### Option A: Phantom type tag (lightweight, no WhyML type change)

Introduce a **`\instanceof(\result, ClassName)`** contract atom that:

1. **Module2 (Parser)**: Add `instanceof_expr` grammar rule:
   ```
   instanceof_expr : "\\instanceof" "(" expr "," CNAME ")"
   ```
   Produces an IR node `{"type": "InstanceOf", "expr": ..., "class_name": "..."}`.

2. **Module4 (Semantic Analyzer)**: Validate that `\instanceof` only appears
   in `ensures` clauses. The class name is treated as an opaque identifier
   (no lookup required — library classes aren't defined in the user's code).

3. **Module5 (IR Emitter)**: Pass through `InstanceOf` nodes unchanged.

4. **Module6 (WhyML Transpiler)**: Emit `\instanceof(expr, C)` as a WhyML
   **predicate call**: `(is_C expr)`, where `is_C` is a declared abstract
   predicate. Auto-generate `predicate is_C (x: int) = true` (axiom) in the
   WhyML preamble for each class name used. Since trusted stubs are `val`
   declarations, the predicate is trivially assumed — it acts as documentation
   and a structural type constraint that downstream contracts can reference.

   ```whyml
   predicate is_argumentparser (x: int) = true
   val argumentparser (prog: int) ... : int
     ensures { is_argumentparser result }
   ```

5. **Lib/ stubs**: Update all object-returning stubs from `#@ ensures True`
   to `#@ ensures \instanceof(\result, ClassName)`.

**Pros**: Minimal pipeline changes. No WhyML type system changes. Predicates
compose (callers can write `#@ requires \instanceof(parser, ArgumentParser)`).

**Cons**: The predicate is trivially `true` — it adds documentation value but
no actual proof obligations. It's essentially a typed tag.

### Option B: WhyML abstract types (heavier, type-safe)

Instead of `int`, emit each library class as an **abstract WhyML type**:

```whyml
type argumentparser
val argumentparser (prog: int) ... : argumentparser
```

This makes `\instanceof` unnecessary — the type system enforces it. But it
requires significant changes to how the transpiler handles return types of
trusted stubs, and callers passing these objects would need compatible types.

**Pros**: True type safety. No runtime representation issues.

**Cons**: Major pipeline rework. All callers of library functions would need
type annotations that map to the abstract types. Composition between `int`
and abstract types requires casts or polymorphism.

### Recommendation: Option A

Option A is feasible with ~4 files changed and preserves backward compatibility.
Option B is a larger architectural change better suited for a future milestone.

## Implementation Todos (Option A)

### 1. Module2 — Add `\instanceof` to the grammar
File: `src/pycsl/Module2_Parser.py`
- Add grammar rule for `\instanceof(expr, CNAME)`
- Add transformer method to produce `InstanceOf` IR node

### 2. Module4 — Validate `\instanceof` usage
File: `src/pycsl/Module4_SemanticAnalyzer.py`
- Allow `InstanceOf` nodes in `ensures` and `requires` clauses
- Validate the expression inside is a valid contract expression

### 3. Module6 — Emit WhyML predicate
File: `src/pycsl/Module6_WhyMLTranspiler.py`
- Collect all class names used in `\instanceof` across the module
- Auto-generate `predicate is_<classname> (x: int) = true` in preamble
- Emit `(is_<classname> expr)` for `InstanceOf` nodes in contracts

### 4. Lib/ stubs — Update contracts
Files: `Lib/argparse.py`, `Lib/collections.py`, `Lib/dataclasses.py`,
       `Lib/datetime.py`, `Lib/subprocess.py`, `Lib/tempfile.py`,
       `Lib/urllib/request.py`, `Lib/pathlib.py`, `Lib/hashlib.py`
- Replace `#@ ensures True` with `#@ ensures \instanceof(\result, ClassName)`
  for all object-returning stubs

### 5. Tests — Verify end-to-end
- Add a test case that uses `\instanceof` in a contract
- Verify WhyML output includes the predicate declaration
- Verify the proof passes with Alt-Ergo/Z3

## Files to modify

| File | Change |
|------|--------|
| `src/pycsl/Module2_Parser.py` | Add `instanceof_expr` grammar rule + transformer |
| `src/pycsl/Module4_SemanticAnalyzer.py` | Allow `InstanceOf` in contract validation |
| `src/pycsl/Module6_WhyMLTranspiler.py` | Emit predicate decls + predicate calls |
| `Lib/*.py` (9 files) | Update `ensures` clauses |
| `tests/` (1 new test) | End-to-end test case |

## Open questions for review

1. Should `\instanceof` be allowed in `requires` too (for callers to
   assert they received a specific type), or only in `ensures`?
2. Should the predicate be `true` (axiomatic) or carry some structural
   info (e.g., tag field)?
3. Naming: `\instanceof` vs `\is_instance` vs `\typeof(\result) == ClassName`?
