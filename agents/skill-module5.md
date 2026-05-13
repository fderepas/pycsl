# ROLE
You are an expert Compiler Engineer specializing in Intermediate Representations (IR). You are the primary maintainer of `Module5_IREmitter.py` in the PyCSL (Python Contract Specification Language) pipeline.

# OBJECTIVE
Understand the internal workings of `Module5_IREmitter.py` function by function. Use this knowledge to safely add new Python AST nodes to the JSON IR schema without breaking the downstream `Module6_WhyMLTranspiler.py`.

# MODULE OVERVIEW
Module 5 acts as the bridge between Python's complex Abstract Syntax Tree (AAST) and a strict, language-agnostic JSON format. It recursively walks the Python AAST (which contains both standard Python nodes and woven PyCSL contract nodes) and lowers them into a simplified dictionary structure.

# CLASS 1: `PyCSLToJSONEmitter(ast.NodeVisitor)`
This is the core traversal engine. It uses the Visitor pattern to walk the Python AST. It maintains `_current_class` (set when visiting a `ClassDef`) so that method names and field translations are applied consistently. The output dictionary is `{"type_decls": [...], "functions": [...]}` — `type_decls` holds WhyML record definitions emitted once per class.

## PyCSL Contract Translators
These methods handle the custom Hoare logic nodes parsed by Lark (Module 2).
* `_csl_to_ir(self, node: CSLNode) -> Dict[str, Any]`
  Recursively translates PyCSL dataclass nodes into a generic `{"type": "...", ...}` dictionary. Supported nodes: `CSLBinOp`, `CSLUnaryOp`, `CSLVar`, `CSLNumber`, `CSLResult`, `CSLOld`, `Nothing`, and (Level 2) `CSLFieldAccess` → `{"type": "FieldGet", "object": "self", "field": "..."}`. `CSLOld` wrapping a `CSLFieldAccess` is flattened into `{"type": "OldField", "object": "self", "field": "..."}`. Container nodes (`Requires`, `Ensures`, `LoopInvariant`, `LoopVariant`) are transparently unwrapped — their inner `.expr` is passed recursively (so these nodes never appear in the output IR). Level 4 — Quantifiers and array contract nodes:
  - `Forall(var, body)` → `{"type": "Forall", "var": "<i>", "body": <ir_expr>}`
  - `Exists(var, body)` → `{"type": "Exists", "var": "<i>", "body": <ir_expr>}`
  - `ArrayLength(var)` → `{"type": "ArrayLen", "var": "<arr>"}`
  - `SubscriptAccess(array, index)` → `{"type": "Subscript", "value": {"type": "Var", "name": "<arr>"}, "index": <ir_expr>}`
  Returns `{"type": "UnknownCSL"}` for unknown nodes.
* `_csl_list_to_ir(self, csl_list: List[CSLNode]) -> List[Dict[str, Any]]`
  A helper method that applies `_csl_to_ir` across a list of contract expressions (e.g., a list of loop invariants).

## Python AST Translators
These methods handle the standard Python code (the actual implementation logic).
* `_py_op_to_str(self, op) -> str`
  Maps complex Python `ast.operator` (like `ast.Add`, `ast.Eq`, `ast.USub`) objects into simple string representations (`"+"`, `"=="`, `"-"`).
* `_py_expr_to_ir(self, expr: ast.expr) -> Dict[str, Any]`
  Recursively evaluates Python expression nodes (things that evaluate to a value). Supports: `ast.Name` (Variables), `ast.Constant` (Numbers), `ast.BinOp` (Math), `ast.UnaryOp` (Negation/Not), `ast.Compare` (Booleans), `ast.Call` (Function calls), `ast.Tuple`, `ast.Subscript` (array read → `{"type": "Subscript", "value": ..., "index": ...}`), `ast.List` literal (→ `{"type": "ArrayLit", "elts": [...]}`), and (Level 2) `ast.Attribute` for `self.field` access → `{"type": "FieldGet", "object": "self", "field": "<attr>"}`. Returns `{"type": "UnknownPyExpr"}` if an unsupported node is encountered.
* `_py_stmts_to_ir(self, stmts: List[ast.stmt]) -> List[Dict[str, Any]]`
  Iterates over a block of imperative Python statements. Dispatches to:
  * `ast.Assign` with `ast.Name` target → `{"stmt": "Assign", "target": name, ...}`
  * `ast.Assign` with `ast.Attribute` (self.x) target → `{"stmt": "FieldAssign", "object": "self", "field": "...", "value": ...}`
  * `ast.Assign` with `ast.Subscript` target (`arr[i] = v`) → `{"stmt": "ArraySet", "array": <ir_expr>, "index": <ir_expr>, "value": <ir_expr>}` (Level 4)
  * `ast.AugAssign` with `ast.Name` target → `{"stmt": "AugAssign", "target": name, ...}`
  * `ast.AugAssign` with `ast.Attribute` (self.x) target → `{"stmt": "FieldAugAssign", "object": "self", "field": "...", "op": ..., "value": ...}`
  * `ast.Return`, `ast.Continue`, `ast.Expr` (standalone calls) — handled inline
  * `ast.While` → delegates to `_process_while`
  * `ast.For` → delegates to `_process_for`
  * `ast.If` → delegates to `_process_if`
* `_process_while(self, node: ast.While) -> Dict[str, Any]`
  A dedicated handler for while loops. It translates the loop's test condition, extracts the custom `csl_invariants` and `csl_variants` attached by Module 3, and recursively calls `_py_stmts_to_ir` on the loop body. Schema: `{"stmt": "While", "test": ..., "invariants": [...], "variants": [...], "body": [...]}`.
* `_process_for(self, node: ast.For) -> Dict[str, Any]`
  A dedicated handler for for loops. Extracts the loop target name, the iterable expression, any `csl_invariants`/`csl_variants` (Module 3 does not annotate `for` nodes, so these default to `[]`), and the loop body. Schema: `{"stmt": "For", "target": "<name>", "iter": ..., "invariants": [...], "variants": [...], "body": [...]}`.
* `_process_if(self, node: ast.If) -> Dict[str, Any]`
  A dedicated handler for if/elif/else statements. Translates the test condition and recursively lowers the `body` and `orelse` statement lists. Schema: `{"stmt": "If", "test": ..., "body": [...], "orelse": [...]}`.

## Main Traversal Hooks
* `visit_ClassDef(self, node: ast.ClassDef) -> Any`
  Sets `self._current_class` to the class name. Before visiting methods, scans the `__init__` body for `self.x = ...` (plain `ast.Assign`) and `self.x: type = ...` (annotated `ast.AnnAssign`) assignments to collect field names and their literal initial values. Emits a `type_decls` record entry:
  ```json
  {
    "kind": "record",
    "name": "Counter",
    "fields": [{"name": "_value", "type": "int", "mutable": true}],
    "class_invariants": [{"type": "BinOp", "op": ">=", "left": {"type": "FieldGet", ...}, "right": {"type": "Number", ...}}],
    "field_defaults": {"_value": 0}
  }
  ```
  - `"class_invariants"`: list of IR expression dicts, one per `ClassInvariant` attached to the class node by Module 3 (Level 3). Empty list `[]` if no class invariants are present.
  - `"field_defaults"`: dict mapping field names to their literal `int` initialiser from `__init__`. Any field without a literal constant initialiser defaults to `0`. Used by Module 6 to emit the `by { field = default; ... }` Why3 witness block.
  Calls `generic_visit` to process all methods, then resets `_current_class` to `None`.
* `visit_FunctionDef(self, node: ast.FunctionDef) -> Any`
  The main entry point for the visitor. When inside a class (`_current_class` is set), dunder methods (e.g., `__init__`, `__str__`) and `@property`-decorated methods are silently skipped. For regular methods, the function name is prefixed with `<classname>__` (lowercased). It builds a complete IR package:
  1. `"name"`: e.g., `counter__increment`.
  2. `"symbol_table"`: injected by Module 4; excludes `self`; no `obj_*` fields (Level 2 uses record fields instead).
  3. `"contracts"`: `requires`/`ensures` using `FieldGet`/`OldField` nodes; `assigns` using `FieldGet` nodes.
  4. `"body"`: lowered statements with `FieldAssign`/`FieldAugAssign`/`FieldGet`.
  5. (methods only) `"kind": "method"` and `"self_type": ClassName`.
  Appends to `self.program_ir["functions"]`.

# CLASS 2: `Module5_IREmitter`
This is the public interface used by the CLI.
* `__init__(self, tree: ast.AST)`
  Accepts the semantically validated AAST from Module 4.
* `generate_json(self, indent: int = 2) -> str`
  Instantiates the `PyCSLToJSONEmitter`, triggers the visit on the root tree, and serializes the resulting `program_ir` dictionary into a formatted JSON string.

# HOW TO EXTEND THE IR (EXTENSION HEURISTICS)
When tasked with supporting a new Python feature (e.g., `if` statements):
1. **Identify the AST Node:** Determine the `ast` class (e.g., `ast.If`).
2. **Determine Node Type:** Is it a Statement (does something) or an Expression (returns a value)?
3. **Update the Emitter:**
   * If an Expression, add an `elif isinstance(expr, ast.NewNode):` block to `_py_expr_to_ir`.
   * If a Statement, add an `elif isinstance(stmt, ast.NewNode):` block to `_py_stmts_to_ir`.
4. **Define the JSON Schema:** Design a clean, minimal dictionary structure for it (e.g., `{"stmt": "If", "test": ..., "body": ..., "orelse": ...}`).
5. **Warn Downstream:** Remind the developer that any new IR node generated by Module 5 MUST also be handled by `Module6_WhyMLTranspiler.py`, or it will crash during WhyML generation.

# FRAMA-C MEMORY MODEL EXTENSIONS (Phases 0–5)

## New `_csl_to_ir` node types

The following CSL node types were added to `_csl_to_ir` as part of the Frama-C memory model implementation.

### `AssignsRegion(base, low, high)` — Phase 0
Emitted when Module 2 parses `\assigns arr[lo..hi]`. The `assigns` contract clause carries a list of these nodes.

IR output:
```json
{"type": "AssignsRegion", "base": {"type": "Var", "name": "arr"}, "low": <ir_expr>, "high": <ir_expr>}
```

### `Valid(base, length)` — Phase 1
Emitted for `\valid(arr, n)` in any contract position.

IR output:
```json
{"type": "Valid", "base": <ir_expr>, "length": <ir_expr>}
```

### `Separated(base1, len1, base2, len2)` — Phase 1
Emitted for `\separated(a, na, b, nb)` in any contract position.

IR output:
```json
{"type": "Separated", "base1": <ir_expr>, "len1": <ir_expr>, "base2": <ir_expr>, "len2": <ir_expr>}
```

### `At(expr, label)` — Phase 5
Emitted for `\at(expr, L)` in any contract position. The `label` field is a plain string (the label name).

IR output:
```json
{"type": "At", "expr": <ir_expr>, "label": "L"}
```

## New `_py_stmts_to_ir` behaviour — Label prepending (Phase 5)

After lowering each Python statement `stmt`, the method checks `stmt.csl_labels` (a `List[str]` attribute attached to `ast.stmt` nodes by Module 3's post-weaving pass). For each label `L` in `csl_labels`, a `Label` IR node is prepended to the output **before** the statement's own IR dict.

Schema:
```json
{"stmt": "Label", "name": "L"}
```

Example — if a Python statement `x = arr[0]` has `csl_labels = ["PRE"]`, the output will be:
```json
[
  {"stmt": "Label", "name": "PRE"},
  {"stmt": "Assign", "target": "x", "value": {"type": "Subscript", ...}}
]
```

## IR schema summary — Frama-C memory model nodes

| CSL Node | IR `"type"` | Key fields |
|---|---|---|
| `AssignsRegion(base, low, high)` | `"AssignsRegion"` | `base`, `low`, `high` |
| `Valid(base, length)` | `"Valid"` | `base`, `length` |
| `Separated(base1, len1, base2, len2)` | `"Separated"` | `base1`, `len1`, `base2`, `len2` |
| `At(expr, label)` | `"At"` | `expr`, `label` |
| (stmt) | `"Label"` | `name` |