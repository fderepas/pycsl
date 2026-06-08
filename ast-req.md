# AST-REQ — Mapping `pure_lib/astmod` onto `src/pycsl/pure_ast.py`

**Date:** 2026-06-08  
**Status:** Superseded by `08-0350-spec-rev4.md`  
**Scope:** Replace the opaque `astmod` stub with contracts derived from the
real `pure_ast.py` implementation already used by the PyCSL toolchain.

> **Note:** This document is superseded by `08-0350-spec-rev4.md` which adds
> the P5 parser family (exec/eval/compile/ast.parse), explicit [TOOL]/[STDLIB]
> agent ownership, and the `literal_eval` soundness fix (§4.4).  Retain this
> file as historical context; the authoritative spec is rev4.

---

## 1  Context

The PyCSL toolchain contains a 3 775-line pure-Python reimplementation of the
standard library `ast` module (`src/pycsl/pure_ast.py`).  Every pipeline stage
already imports it:

| Consumer               | Key functions used                              |
|-------------------------|-------------------------------------------------|
| Module1_Ingestor        | `parse`, `comments`, `walk`, `iter_child_nodes` |
| Module3_Weaver          | `parse`, `walk`, `iter_child_nodes`, `NodeVisitor`, `unparse`, `literal_eval` |
| Module4_SemanticAnalyzer| `NodeVisitor`, `walk`, `iter_child_nodes`       |
| Module5_IREmitter       | `NodeVisitor`, `walk`, `iter_child_nodes`, `get_docstring`, `unparse`, `literal_eval` |
| import_classifier       | `parse`, `walk`, `iter_child_nodes`             |
| pycsl.py (driver)       | `parse`, `walk`                                 |
| ConcurrencyChecker      | `parse`, `walk`, `iter_child_nodes`, `dump`     |

Meanwhile, `pure_lib/astmod/__init__.py` is a stub that models every AST node
as an opaque non-negative `int` handle and every function as a trivial body.
This disconnect means:

* Formal tests can only assert non-negativity and identity — no structural
  properties of the real implementation are captured.
* User code that imports `ast` and calls `parse` / `walk` / `dump` cannot
  be verified beyond type compatibility.

## 2  Goal

Produce a `pure_lib/astmod` whose contracts are **faithful** to the behaviour
of `pure_ast.py` — close enough that:

1. Formal tests can assert **functional properties** (e.g. `dump(parse(s))`
   is deterministic, `copy_location` returns its first argument,
   `fix_missing_locations` and `increment_lineno` return the same node).
2. User programs that `import ast` and call the helpers can be verified
   against meaningful postconditions, not just `>= 0`.

This does **not** mean inlining or transpiling the 3 775-line implementation.
It means writing contracts that over-approximate the behaviour precisely
enough for formal proofs.

## 3  Function-by-function mapping

### 3.1  Already faithfully modelled (identity / projection)

These functions return one of their arguments unchanged.  The current stub
already captures this correctly.

| astmod stub         | pure_ast.py signature                   | Contract                              | Status  |
|---------------------|-----------------------------------------|---------------------------------------|---------|
| `copy_location`     | `copy_location(new_node, old_node)`     | `ensures \result == new_node`         | ✅ Done |
| `fix_missing_locations` | `fix_missing_locations(node)`       | `ensures \result == node`             | ✅ Done |
| `increment_lineno`  | `increment_lineno(node, n=1)`           | `ensures \result == node`             | ✅ Done |

### 3.2  Functions needing richer contracts

| astmod stub         | pure_ast.py signature                               | Actual behaviour                                          | Proposed contract enrichment                  | Blocked by |
|---------------------|------------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------|------------|
| `parse`             | `parse(source, filename="<unknown>", mode="exec", *, type_comments=False, feature_version=None)` | Returns a `Module`/`Expression`/`Interactive` AST node built by a recursive-descent parser | `ensures \result >= 0` (node handle). Add `mode` param; could assert different return type per mode once class typing lands. | Gap 6/7 (class fields/chaining) |
| `dump`              | `dump(node, annotate_fields=True, include_attributes=False, *, indent=None)` | Returns a string representation of the AST | Should return `str`. Currently returns `int` (string length proxy). | Gap 1 (str local binding) for callers |
| `literal_eval`      | `literal_eval(node_or_string)`                       | Safely evaluates Python literal expressions. Returns int/float/str/list/dict/... | Keep `int` return (value). Could add `ensures \result >= 0` only for numeric literals. Complex return types not modelable yet. | Gap 4 (list passing) |
| `unparse`           | `unparse(ast_obj)`                                   | Converts an AST back to source code string | Should return `str`. Currently returns `int`. | Gap 1 |
| `get_docstring`     | `get_docstring(node, clean=True)`                    | Returns the docstring `str` or `None` (modelled as 0) | Should return `str`. Currently returns `int`. | Gap 1 |
| `iter_fields`       | `iter_fields(node)`                                  | Yields `(fieldname, value)` pairs — a generator | Returns count of fields. Generator semantics not modelable. Keep count proxy. | Generators not supported |
| `iter_child_nodes`  | `iter_child_nodes(node)`                             | Yields child AST nodes — a generator | Same: keep count proxy. | Generators not supported |
| `walk`              | `walk(node)`                                         | BFS generator over all descendant nodes | Same: keep count proxy. `ensures \result >= 1` (node itself is always yielded). | Generators not supported |

### 3.3  Functions missing from astmod (present in `pure_ast.py`)

| pure_ast.py function  | Signature                                        | Behaviour                                | Priority | Action |
|------------------------|--------------------------------------------------|------------------------------------------|----------|--------|
| `comments`             | `comments(source)`                               | Tokenizes source, returns list of `Comment` objects with position info | P2 | Add stub: `ensures \result >= 0` (comment count) |
| `get_source_segment`   | `get_source_segment(source, node, *, padded=False)` | Extracts source text for a node | P3 | Add stub returning `str` (or int proxy) |
| `NodeVisitor`          | `class NodeVisitor` with `visit()` / `generic_visit()` | Visitor pattern base class — `visit()` dispatches to `visit_<Classname>` | P1 | **Critical** — 6 tool modules subclass it. Add class stub (blocked by Gap 6/7). |
| `NodeTransformer`      | `class NodeTransformer(NodeVisitor)` with `generic_visit()` that mutates the tree | In-place transformer subclass | P2 | Add class stub after NodeVisitor. |
| `Comment`              | `class Comment(lineno, col_offset, text, own_line, indent)` | Data class for source comments | P2 | Add class with int fields (lineno, col_offset, indent) + str field (text). |
| `PyCSLSyntaxError`     | `class PyCSLSyntaxError(SyntaxError)`            | Custom exception for unsupported syntax | P3 | Add exception class. Blocked by Gap 8 (raises). |
| `AST`                  | `class AST` with `_fields`, `_attributes`        | Base node class — all node types inherit from it | P1 | Add minimal class stub. Blocked by Gap 6/7. |
| `main`                 | `main(args=None)`                                | CLI entry point | Won't model | Not relevant for formal verification. |
| `_self_test`           | `_self_test(limit=None)`                         | Dev-only differential test | Won't model | Internal tooling. |

### 3.4  Node type classes (from `_NODE_SPEC`)

`pure_ast.py` dynamically generates ~90 AST node classes (`Module`,
`FunctionDef`, `BinOp`, `Constant`, …) from the `_NODE_SPEC` table.  The
tool uses `isinstance(node, ast.FunctionDef)` etc. extensively.

**Current blocker:** PyCSL class support (Gap 6 — class fields forced to int,
Gap 7 — field chaining lost through method calls) prevents modelling the
class hierarchy.  Once those gaps are resolved:

* A `class AST` base with `_fields` as an int (field count) could work.
* Leaf node stubs (`Module`, `FunctionDef`, `Constant`, …) would inherit
  from `AST` and declare field counts.
* `isinstance` checks are not currently modelable in WhyML but could be
  approximated with `\in_globals` once P4 (`\typeof`/`\subtag`) lands.

**Recommendation:** defer node-class modelling to a Phase 2, after Gap 6/7
resolution and `\typeof` introspection.

## 4  Transpiler gaps blocking this work

The following gaps (from `07-2333-req.md`) directly block faithful `astmod`
contracts:

| Gap | Title                           | Impact on astmod                                | Priority |
|-----|---------------------------------|-------------------------------------------------|----------|
| 1   | String local binding            | `dump`, `unparse`, `get_docstring` should return `str` but callers can't bind the result | P1 |
| 6   | Class invariants with str fields | `Comment` class has a `text: str` field         | P2 |
| 7   | Class field chaining            | `NodeVisitor.visit()` dispatches via field access | P2 |
| 8   | Exception declarations          | `PyCSLSyntaxError` needs `raises` in WhyML      | P3 |

## 5  Phased plan

### Phase 0 — Immediate (no gap resolution needed)

*Already done in commit `eb53368`.*

* 11 contracted functions with identity/non-negativity postconditions.
* All 11 VCs valid.

### Phase 1 — After Gap 1 resolution (str local binding)

1. Change `dump`, `unparse`, `get_docstring` return types from `int` to `str`.
2. Add `ensures \result == doc` for `get_docstring` when `clean=False`.
3. Add `comments` stub returning count (`int`).
4. Add `get_source_segment` stub returning `str`.
5. Update formal tests to use `str` assertions.

**Estimated VCs:** 15–18.

### Phase 2 — After Gap 6+7 resolution (class support)

1. Add `class AST` base stub with `_fields` field.
2. Add `class NodeVisitor` with `visit` and `generic_visit` methods.
3. Add `class NodeTransformer(NodeVisitor)` with mutating `generic_visit`.
4. Add `class Comment` with position fields and `text: str`.
5. Add selected node classes: `Module`, `FunctionDef`, `ClassDef`,
   `Constant`, `Name`, `BinOp`, `Assign`, `Return` (the most-used in tool).

**Estimated VCs:** 25–35.

### Phase 3 — After `\typeof`/`\subtag` (P4 introspection)

1. Model `isinstance(node, ast.FunctionDef)` checks.
2. Add `walk`/`iter_child_nodes` with richer postconditions (typed yield).
3. Full node hierarchy from `_NODE_SPEC` (generated stubs).

**Estimated VCs:** 50+.

## 6  Acceptance criteria

| Criterion                                              | Phase |
|--------------------------------------------------------|-------|
| `dump`, `unparse`, `get_docstring` return `str`        | 1     |
| `comments` and `get_source_segment` modelled           | 1     |
| `NodeVisitor` subclassable in verified user code       | 2     |
| `Comment` class with str `text` field usable           | 2     |
| `isinstance` checks on node types verifiable           | 3     |
| All formal tests pass after each phase                 | 0–3   |

## 7  References

* `src/pycsl/pure_ast.py` — 3 775-line pure-Python ast reimplementation
* `pure_lib/astmod/__init__.py` — current formal stub (11 functions)
* `pure_lib_test/formal_astmod.py` — current formal tests (11 tests, 24 VCs)
* `07-2333-req.md` — transpiler gaps blocking richer models
* `lib/ast.py` — CPython 3.14 `Lib/ast.py` reference source
* `lib/index.json` — registry entry: `ast → pure_lib: astmod`
