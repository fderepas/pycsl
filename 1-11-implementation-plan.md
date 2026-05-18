# PyCSL — Detailed Implementation Plan for Items 1–11

> Generated 2026-05-18 from codebase analysis of M2 (parser), M3 (weaver), M4 (semantic
> analyzer), M5 (IR emitter), M6 (WhyML transpiler), and the test infrastructure.

---

## How to read this document

Each item has:

- **Summary** — what the feature does and why it matters.
- **Current state** — what already works in the pipeline (body code, partial IR, etc.).
- **Files to change** — exact source files, class/method names, and line-range context.
- **Step-by-step changes** — ordered instructions per module.
- **IR schema** — the JSON intermediate representation the feature produces.
- **WhyML output** — the target Why3 code.
- **Test plan** — what test files to add and where.
- **Dependencies** — links to other items.
- **Estimated effort** — in developer-days.

Module abbreviations: M1 = `Module1_Ingestor`, M2 = `Module2_Parser`,
M3 = `Module3_Weaver`, M4 = `Module4_SemanticAnalyzer`, M5 = `Module5_IREmitter`,
M6 = `Module6_WhyMLTranspiler`.

---

## Item 1 — `assert` statement → WhyML `check`

### Summary

Python `assert cond` should emit a WhyML `check { cond }` statement — a proof
obligation that the solver must discharge at that program point. Currently `ast.Assert`
is silently dropped.

### Current state

- M5 `_py_stmts_to_ir`: no handler for `ast.Assert` (falls through to implicit skip).
- M6 `_stmts_to_whyml`: no handler for an `"Assert"` IR node.
- WhyML `check { ... }` is a native construct; no extra `use` import needed.

### Files to change

| File | Method / Location | Change |
|------|-------------------|--------|
| `src/pycsl/Module5_IREmitter.py` | `_py_stmts_to_ir` (line ~332 area) | Add `elif isinstance(stmt, ast.Assert):` case |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_stmts_to_whyml` (line ~1298 area) | Add `elif s["stmt"] == "Assert":` case |

### Step-by-step

**M5 — `_py_stmts_to_ir`:**

1. After the `ast.If` handler (~line 333), add:

```python
elif isinstance(stmt, ast.Assert):
    ir_test = self._py_expr_to_ir(stmt.test)
    ir_node = {"stmt": "Assert", "test": ir_test}
    if stmt.msg and isinstance(stmt.msg, ast.Constant) and isinstance(stmt.msg.value, str):
        ir_node["msg"] = stmt.msg.value
    result.append(ir_node)
```

**M6 — `_stmts_to_whyml`:**

2. Add a handler for `"Assert"` before the `"While"` handler:

```python
elif s["stmt"] == "Assert":
    test_w = self._expr_to_whyml(s["test"], local_refs, spec_ctx=True)
    if "msg" in s:
        lines.append(f'{indent}check {{ [@expl:{s["msg"]}] {test_w} }}')
    else:
        lines.append(f'{indent}check {{ {test_w} }}')
```

Note: `spec_ctx=True` is needed because the condition inside `check { ... }` is a
specification context (boolean, not int-coerced).

### IR schema

```json
{"stmt": "Assert", "test": <ir_expr>, "msg": "<optional string>"}
```

### WhyML output

```whyml
check { condition }
check { [@expl:message] condition }
```

### Test plan

- Add `tests/to_annotate/070-assert-check.py`: a function with `assert x >= 0` and
  `assert total == n, "total must equal n"`.
- Verify `pycsl` produces WhyML with `check` statements and the solver discharges them.

### Dependencies

- None. This is self-contained.
- Item 9 extends this with the `[@expl:msg]` label (included above as optional).

### Estimated effort

1–2 days (including item 9's extension — see below).

---

## Item 2 — `//` and `%` in contract expressions

### Summary

Floor-division (`//`) and modulo (`%`) are forbidden in `#@` contract lines. They
already work in function bodies. Adding them to the M2 grammar unblocks modular
arithmetic in loop invariants and postconditions.

### Current state

- M2 grammar `MUL_OP`: only `"*" | "/"` (line 276). No `"//"` or `"%"`.
- M5 `_py_op_to_str`: maps `ast.FloorDiv` → `"div"`, `ast.Mod` → `"%"` (lines 133–134).
- M5 `_csl_to_ir`: `CSLBinOp` passes operator through unchanged (line 24–25). If the
  grammar produced `CSLBinOp(op="//", ...)` or `CSLBinOp(op="%", ...)`, M5 would emit
  `{"type":"BinOp","op":"//", ...}` or `{"type":"BinOp","op":"%", ...}`.
- M6 `_expr_to_whyml`: already handles `"div"` → `(div left right)` in spec context
  (line 569–573) and `"mod"` → `(mod left right)` (line 573–576).
- M6 `op_map`: `"/"` → `"div"`, `"%"` → `"mod"` (lines 25–27).

**Key insight:** M5 and M6 are already ready. Only M2 needs a grammar change.

### Files to change

| File | Method / Location | Change |
|------|-------------------|--------|
| `src/pycsl/Module2_Parser.py` | `PYCSL_GRAMMAR`, `MUL_OP` token (line 276) | Add `"//"` and `"%"` |
| `src/pycsl/Module2_Parser.py` | `PyCSLTransformer.factor` method | Ensure `//` maps to `BinOp(op="//")` |

### Step-by-step

**M2 — Grammar:**

1. Change `MUL_OP` (line 276) from:
   ```
   MUL_OP: "*" | "/"
   ```
   to:
   ```
   MUL_OP: "*" | "//" | "/" | "%"
   ```
   **Important:** `"//"` must appear before `"/"` so Lark's LALR tokenizer matches the
   longer token first.

2. The `PyCSLTransformer.factor` method (inherited from the generic `term`/`factor`
   pattern) already builds `BinOp(op=str(op), left, right)`. Operators `"//"` and `"%"`
   will flow through as `BinOp(op="//")` and `BinOp(op="%")`.

**M5 — No changes needed.** `_csl_to_ir` for `CSLBinOp` passes the operator string
through. `//` becomes `{"type":"BinOp","op":"//"}` in IR.

**M6 — Verify mapping.** `op_map` maps `"/"` → `"div"`. For `"//"`, we need to add a
mapping. Currently `"//"` would pass through unmapped, emitting `//` in WhyML (invalid).

3. Add to `op_map` (line ~25):
   ```python
   "//": "div",
   ```

   This makes `//` in contracts produce `div` in WhyML, same as `/` in contracts.
   (In Python semantics `//` and `/` on integers are both floor-division; Why3's `div`
   is Euclidean division. This is already the existing behavior for body code.)

### IR schema

```json
{"type": "BinOp", "op": "//", "left": <ir_expr>, "right": <ir_expr>}
{"type": "BinOp", "op": "%", "left": <ir_expr>, "right": <ir_expr>}
```

### WhyML output

```whyml
(div left right)
(mod left right)
```

### Test plan

- Add `tests/to_annotate/071-contract-divmod.py`: a function using `#@ ensures \result == n // 2`
  and `#@ loop invariant i % 2 == 0`.
- Verify parser accepts `//` and `%` in contracts and solver discharges the goals.

### Dependencies

None.

### Estimated effort

0.5 days.

---

## Item 3 — `True` / `False` / `None` literals in contracts

### Summary

The contract grammar forbids bare Python booleans; annotators must write `1==1` and
`0==1`. Adding `True`, `False`, `None` as grammar atoms removes the most common
source of agent annotation errors.

### Current state

- M2 grammar `atom` (lines 251–265): no rules for `True`, `False`, `None`.
- M2 CSL nodes: no `CSLBool` or `CSLNone` dataclass exists.
- M5 `_py_expr_to_ir`: `ast.Constant(True)` → `{"type":"Bool","value":true}` (line 150–151);
  `ast.Constant(None)` → `{"type":"None"}` (line 147–149). These handle body code.
- M6 `_expr_to_whyml`:
  - `Bool` → spec: `true`/`false`; body: `1`/`0` (lines 936–940).
  - `None` → `0` (lines 933–934).

**Key insight:** M5 and M6 already handle `Bool` and `None` IR nodes. We only need M2
to parse them and produce IR-compatible CSL nodes.

### Files to change

| File | Method / Location | Change |
|------|-------------------|--------|
| `src/pycsl/Module2_Parser.py` | CSL node definitions (~line 10) | Add `CSLBool` and `CSLNone` dataclasses |
| `src/pycsl/Module2_Parser.py` | `PYCSL_GRAMMAR`, `atom` rule (line 251) | Add `"True"`, `"False"`, `"None"` alternatives |
| `src/pycsl/Module2_Parser.py` | `PyCSLTransformer` class | Add `true_lit`, `false_lit`, `none_lit` methods |
| `src/pycsl/Module5_IREmitter.py` | `_csl_to_ir` | Add `CSLBool` and `CSLNone` handlers |

### Step-by-step

**M2 — Node definitions:**

1. Add after the existing CSL node classes:
```python
@dataclass
class CSLBool(CSLNode):
    value: bool

@dataclass
class CSLNone(CSLNode):
    pass
```

**M2 — Grammar:**

2. Add to the `atom` rule (line 251), before the `NUMBER` alternative:
```
     | "True" -> true_lit
     | "False" -> false_lit
     | "None" -> none_lit
```

**M2 — Transformer:**

3. Add methods:
```python
def true_lit(self): return CSLBool(True)
def false_lit(self): return CSLBool(False)
def none_lit(self): return CSLNone()
```

**M5 — `_csl_to_ir`:**

4. Add handlers after the `CSLNumber` case (line ~33):
```python
elif isinstance(node, CSLBool):
    return {"type": "Bool", "value": node.value}
elif isinstance(node, CSLNone):
    return {"type": "None"}
```

These produce the same IR nodes that M6 already handles.

**M6 — No changes needed.** `Bool` and `None` are already handled.

### IR schema

```json
{"type": "Bool", "value": true}
{"type": "Bool", "value": false}
{"type": "None"}
```

### WhyML output (in spec context)

```whyml
true
false
0
```

### Test plan

- Add `tests/to_annotate/072-contract-booleans.py`: functions with `#@ requires True`,
  `#@ ensures \result != None`, `#@ requires x > 0 or False`.
- Verify parser accepts them and WhyML is valid.

### Dependencies

None.

### Estimated effort

0.5 days.

---

## Item 4 — `in` / `not in` in contract expressions

### Summary

`x in arr` and `x not in arr` have no grammar rule in M2 contracts. Adding them
eliminates verbose existential workarounds in postconditions of search functions.

### Current state

- M2 grammar: no `in` / `not in` operator in any production.
- M5 `_py_op_to_str`: already maps `ast.In` → `"in"`, `ast.NotIn` → `"not in"` (line 136).
  Body `ast.Compare` nodes with these operators produce `BinOp` IR with `op: "in"`.
- M6 `_expr_to_whyml`: already handles `"in"` and `"not in"` operators in `BinOp`
  (lines 588–613):
  - Tuple RHS: expands to `||`-chained equality.
  - Other RHS: emits abstract `contains_check`.

**Key insight:** only the M2 contract grammar needs a new operator. M5 and M6 body
handling is complete. For contract expressions, `in`/`not in` should desugar to a
quantified existence check rather than relying on the body-level `contains_check`
abstraction.

### Files to change

| File | Method / Location | Change |
|------|-------------------|--------|
| `src/pycsl/Module2_Parser.py` | `PYCSL_GRAMMAR` | Add `in` / `not in` as comparison operators or a new precedence level |
| `src/pycsl/Module2_Parser.py` | CSL node definitions | Add `CSLIn` and `CSLNotIn` dataclasses |
| `src/pycsl/Module2_Parser.py` | `PyCSLTransformer` | Add transformer methods |
| `src/pycsl/Module5_IREmitter.py` | `_csl_to_ir` | Lower `CSLIn` → `Exists` IR; `CSLNotIn` → negated `Exists` |

### Step-by-step

**M2 — Node definitions:**

1. Add:
```python
@dataclass
class CSLIn(CSLNode):
    element: CSLNode
    collection: CSLNode

@dataclass
class CSLNotIn(CSLNode):
    element: CSLNode
    collection: CSLNode
```

**M2 — Grammar:**

2. Add a new precedence level between `equality` and `comparison`, or extend `comparison`:

```
?comparison: membership | comparison COMP_OP membership
?membership: term | term "in" term -> in_expr
           | term "not" "in" term -> not_in_expr
```

This avoids ambiguity with `"not"` as a unary operator (the two-token `"not" "in"`
sequence is unambiguous at this precedence level).

**M2 — Transformer:**

3. Add:
```python
def in_expr(self, element, collection): return CSLIn(element, collection)
def not_in_expr(self, element, collection): return CSLNotIn(element, collection)
```

**M5 — `_csl_to_ir`:**

4. Lower to quantified existence:
```python
elif isinstance(node, CSLIn):
    # x in arr → ∃ _i. 0 ≤ _i ∧ _i < length(arr) ∧ arr[_i] == x
    elt_ir = self._csl_to_ir(node.element)
    coll_ir = self._csl_to_ir(node.collection)
    coll_name = coll_ir.get("name", "_coll")
    return {
        "type": "Exists", "var": "_mem_i",
        "body": {"type": "BinOp", "op": "and",
            "left": {"type": "BinOp", "op": "and",
                "left": {"type": "BinOp", "op": ">=",
                    "left": {"type": "Var", "name": "_mem_i"},
                    "right": {"type": "Number", "value": 0}},
                "right": {"type": "BinOp", "op": "<",
                    "left": {"type": "Var", "name": "_mem_i"},
                    "right": {"type": "ArrayLen", "var": coll_name}}},
            "right": {"type": "BinOp", "op": "==",
                "left": {"type": "Subscript",
                    "value": {"type": "Var", "name": coll_name},
                    "index": {"type": "Var", "name": "_mem_i"}},
                "right": elt_ir}}
    }
elif isinstance(node, CSLNotIn):
    # x not in arr → ¬(x in arr) — wrap CSLIn result in negation
    in_ir = self._csl_to_ir(CSLIn(node.element, node.collection))
    return {"type": "UnaryOp", "op": "not", "expr": in_ir}
```

**M6 — No changes needed.** The desugared IR uses only `Exists`, `BinOp`, `Subscript`,
`ArrayLen`, `Var`, `Number`, and `UnaryOp` — all already handled.

### IR schema

Desugared to existing IR nodes (no new node type in the IR).

### WhyML output

```whyml
(* x in arr *)
(exists _mem_i : int. (0 <= _mem_i) && (_mem_i < length arr) && (arr[_mem_i] = x))

(* x not in arr *)
not (exists _mem_i : int. ...)
```

### Test plan

- Add `tests/to_annotate/073-contract-membership.py`: search function with
  `#@ ensures \result == -1 or target in values`.
- Verify parser accepts `in` / `not in` in contracts.

### Dependencies

None.

### Estimated effort

1 day.

---

## Item 5 — Missing library stubs (`functools`, `itertools`)

### Summary

Real-world Python code uses `functools.reduce`, `functools.partial`,
`itertools.chain`, `itertools.accumulate`, etc. Without stubs, calls produce
`UnknownPyExpr` in M5. `#@ \trusted` stubs let the prover reason about these
calls without verifying library internals.

### Current state

- `data/lib_stubs/` already has stubs for: `math`, `json`, `os`, `pathlib`, `csv`,
  `datetime`, `hashlib`, `multiprocessing`, `numpy`, `locale`, `collections`,
  `importlib`, `argparse`, `ast`, `dataclasses`, `lark`, `libcst`, `jsonschema`, `mcp`,
  `pytest`, and the pipeline modules themselves.
- `functools` and `itertools` are missing.
- `hashlib` and `multiprocessing` are already present (obsoleting the original plan's
  claim).

### Files to change

| File | Change |
|------|--------|
| `data/lib_stubs/functools.py` | New file — trusted stubs |
| `data/lib_stubs/itertools.py` | New file — trusted stubs |

### Step-by-step

**`data/lib_stubs/functools.py`:**

```python
#@ \trusted
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def reduce(function: int, iterable: list) -> int:
    """Apply function of two arguments cumulatively."""
    return 0

#@ \trusted
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def partial(func: int, *args: int) -> int:
    """Return a new partial object."""
    return 0

#@ \trusted
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def lru_cache(maxsize: int) -> int:
    """Decorator that caches function results."""
    return 0
```

**`data/lib_stubs/itertools.py`:**

```python
#@ \trusted
#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def chain(*iterables: list) -> list:
    """Chain multiple iterables."""
    return []

#@ \trusted
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def accumulate(iterable: list) -> list:
    """Running accumulation."""
    return []

#@ \trusted
#@ requires n >= 0
#@ ensures 1 == 1
#@ assigns \nothing
def combinations(iterable: list, n: int) -> list:
    """Return r-length combinations."""
    return []
```

Follow the existing pattern in `data/lib_stubs/math.py` for style conventions.

### IR schema

N/A — stubs are consumed by the pipeline as regular Python input.

### WhyML output

Trusted functions emit `val` declarations with assumed contracts.

### Test plan

- Add `tests/to_annotate/074-functools-usage.py`: function that calls `functools.reduce`.
- Verify pipeline does not produce `UnknownPyExpr` and generates valid WhyML.

### Dependencies

None. Independently parallelisable.

### Estimated effort

1 day for both stubs.

---

## Item 6 — Walrus operator `:=` (`ast.NamedExpr`)

### Summary

Python 3.8+ walrus operator `(x := expr)` appears in `while` guards and
comprehension filters. It returns a value AND assigns to a variable. This requires
a "pre-statement buffer" in M5 because the IR separates statements from expressions.

### Current state

- M5 `_py_expr_to_ir`: no handler for `ast.NamedExpr` (falls through to
  `UnknownPyExpr`).
- M6: no changes needed if desugaring is done in M5.

### Files to change

| File | Method / Location | Change |
|------|-------------------|--------|
| `src/pycsl/Module5_IREmitter.py` | `_py_expr_to_ir` | Add `ast.NamedExpr` handler |
| `src/pycsl/Module5_IREmitter.py` | `_py_stmts_to_ir` | Flush pre-statement buffer before each statement |
| `src/pycsl/Module5_IREmitter.py` | `PyCSLToJSONEmitter.__init__` | Add `_pre_stmts` buffer |

### Step-by-step

**M5 — New infrastructure (pre-statement buffer):**

1. In `PyCSLToJSONEmitter.__init__`, add:
```python
self._pre_stmts: list = []
```

2. In `_py_expr_to_ir`, add handler for `ast.NamedExpr`:
```python
elif isinstance(expr, ast.NamedExpr):
    # (x := val) → emit assignment as pre-statement, return Var(x)
    target_name = expr.target.id
    value_ir = self._py_expr_to_ir(expr.value)
    self._pre_stmts.append({"stmt": "Assign", "target": target_name, "value": value_ir})
    return {"type": "Var", "name": target_name}
```

3. In `_py_stmts_to_ir`, at the START of each statement iteration, flush:
```python
for stmt in stmts:
    # Flush any pre-statements from walrus operators
    if self._pre_stmts:
        result.extend(self._pre_stmts)
        self._pre_stmts.clear()
    # ... existing statement handling
```

4. Also flush after processing expressions that might contain walrus operators
   (e.g., `while` test, `if` test):
   - In `_process_while`: after `self._py_expr_to_ir(node.test)`, flush pre-stmts
     into the while body prefix.
   - In `_process_if`: after test expression, flush pre-stmts before the if.

**M5 — `_find_assigned_vars`:**

5. Must also scan expressions for `ast.NamedExpr` targets so the variable gets
   added to `local_refs`:
```python
# In _find_assigned_vars, add:
for node in ast.walk(stmt):
    if isinstance(node, ast.NamedExpr):
        assigned.add(node.target.id)
```

**M6 — No changes needed.** The desugared `Assign` + `Var` IR nodes are already handled.
The variable will be in `local_refs` and get `let x = ref ... in` / `!x` treatment.

### IR schema

No new IR node. Desugared to:
```json
[
  {"stmt": "Assign", "target": "x", "value": <ir_expr>},
  ... // subsequent code using {"type": "Var", "name": "x"}
]
```

### WhyML output

```whyml
let x = ref <value> in
...  (* uses !x *)
```

### Test plan

- Add `tests/to_annotate/075-walrus-operator.py`: function with
  `while (chunk := read_next()) > 0:` pattern.
- Verify the pre-statement buffer correctly hoists the assignment.

### Dependencies

None.

### Estimated effort

3 days (the pre-statement buffer is new infrastructure that must be carefully tested
with nested expressions — walrus inside walrus, walrus inside `and`/`or`, walrus
inside comprehensions).

### Risks

- Walrus inside `while` test: the assignment must be emitted BEFORE the loop, AND
  re-emitted at the end of each loop iteration (since the test is re-evaluated).
  This may require special handling in `_process_while` to duplicate the assignment.
- Walrus inside short-circuit `and`/`or`: the assignment may or may not execute
  depending on short-circuit evaluation. WhyML's `&&`/`||` also short-circuit, so
  the desugaring must preserve this — simply hoisting the assignment before the
  expression is INCORRECT for short-circuit cases.

---

## Item 7 — Slice notation `arr[lo:hi]` in function bodies

### Summary

`arr[lo:hi]`, `arr[:n]`, `arr[i:]` are common in sorting, partitioning, and
string-processing. This requires a new `Slice` IR node and WhyML ghost sub-array
emission.

### Current state

- M5 `_py_expr_to_ir` for `ast.Subscript`: only handles integer index (line ~208–215).
  If the slice is an `ast.Slice` object (not `ast.Index`), it's not handled.
- M6: no `Slice` IR node handler exists.

### Files to change

| File | Method / Location | Change |
|------|-------------------|--------|
| `src/pycsl/Module2_Parser.py` | `PYCSL_GRAMMAR`, `atom` | Add `CNAME "[" expr ".." expr "]"` for contract read-only views |
| `src/pycsl/Module2_Parser.py` | CSL nodes + transformer | Add `CSLSlice` node and transformer method |
| `src/pycsl/Module5_IREmitter.py` | `_py_expr_to_ir`, `ast.Subscript` case | Detect `ast.Slice` and emit `Slice` IR |
| `src/pycsl/Module5_IREmitter.py` | `_csl_to_ir` | Handle `CSLSlice` |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_expr_to_whyml` | Handle `Slice` IR node |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_stmts_to_whyml` | Handle `SliceAssign` if needed |

### Step-by-step

**M2 — Grammar (for contracts only):**

1. Add atom rule:
```
| CNAME "[" expr ".." expr "]" -> slice_access
```
(Using `..` to distinguish from existing subscript syntax `CNAME "[" expr "]"`.)

2. Add CSL node:
```python
@dataclass
class CSLSlice(CSLNode):
    base: str
    lo: CSLNode
    hi: CSLNode
```

3. Add transformer:
```python
def slice_access(self, base, lo, hi): return CSLSlice(str(base), lo, hi)
```

**M5 — Body expression (`_py_expr_to_ir`):**

4. In the `ast.Subscript` handler, add a branch for `ast.Slice`:
```python
elif isinstance(slice_node, ast.Slice):
    lo_ir = self._py_expr_to_ir(slice_node.lower) if slice_node.lower else {"type": "Number", "value": 0}
    hi_ir = self._py_expr_to_ir(slice_node.upper) if slice_node.upper else {"type": "ArrayLen", "var": base_name}
    return {"type": "Slice", "base": base_ir, "lo": lo_ir, "hi": hi_ir}
```

**M5 — CSL expression (`_csl_to_ir`):**

5. Add:
```python
elif isinstance(node, CSLSlice):
    return {"type": "Slice", "base": {"type": "Var", "name": node.base},
            "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}
```

**M6 — Expression handler:**

6. Add `Slice` handler:
```python
elif expr["type"] == "Slice":
    # Introduce a ghost sub-array — for now, model as abstract extraction
    base_w = self._expr_to_whyml(expr["base"], local_refs)
    lo_w = self._expr_to_whyml(expr["lo"], local_refs)
    hi_w = self._expr_to_whyml(expr["hi"], local_refs)
    self._add_abstract_op("val array_slice (a: array int) (lo: int) (hi: int) : array int")
    return f"(array_slice {base_w} {lo_w} {hi_w})"
```

For a proper verified implementation, the abstract `array_slice` would need an
axiom: `ensures { length result = hi - lo }` and
`ensures { forall k. 0 <= k < hi - lo -> result[k] = a[lo + k] }`.

### IR schema

```json
{"type": "Slice", "base": <ir_expr>, "lo": <ir_expr>, "hi": <ir_expr>}
```

### WhyML output

```whyml
(array_slice arr lo hi)
```

### Test plan

- Add `tests/to_annotate/076-slice-notation.py`: function using `arr[1:n]`.

### Dependencies

None.

### Estimated effort

1 week. The core change is straightforward, but the ghost sub-array axiom and its
interaction with the prover require careful tuning.

### Risks

- Slices used as assignment targets (`arr[lo:hi] = other`) require a separate
  `SliceAssign` statement type and are significantly harder. Recommend deferring
  slice-assignment to a follow-up.
- The `array_slice` abstract function breaks proof completeness — the prover cannot
  reason through the abstraction barrier. A full implementation would inline the
  quantified equality. This is the main complexity driver.

---

## Item 8 — Multi-return tuple unpacking (`a, b = f()`)

### Summary

`a, b = f()` where `f` returns a tuple is not handled — M5 only supports `Name`,
`Attribute`, and `Subscript` as assignment targets. Why3 has native tuple destructuring.

### Current state

- M5 `_py_stmts_to_ir` for `ast.Assign`: checks `isinstance(target, ast.Name)`,
  `isinstance(target, ast.Attribute)`, `isinstance(target, ast.Subscript)`.
  No `ast.Tuple` target case.
- M5 `_py_expr_to_ir`: already handles `ast.Tuple` as expression → `{"type":"Tuple","elts":[...]}` (line 206).
- M6 `_expr_to_whyml`: already handles `Tuple` → `(e1, e2, ...)` (line 799).
- M6 `_stmts_to_whyml`: no `TupleUnpack` handler.
- M6 `_find_assigned_vars`: no scan for tuple-target assignments.

### Files to change

| File | Method / Location | Change |
|------|-------------------|--------|
| `src/pycsl/Module5_IREmitter.py` | `_py_stmts_to_ir`, `ast.Assign` handler | Add `ast.Tuple` target case |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_stmts_to_whyml` | Add `TupleUnpack` handler |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_find_assigned_vars` | Scan for `TupleUnpack` targets |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_find_return_type` | Recurse into `TupleUnpack` bodies |

### Step-by-step

**M5 — `_py_stmts_to_ir`:**

1. In the `ast.Assign` handler, add after the `ast.Subscript` target case:
```python
elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
    target_names = []
    for elt in target.elts:
        if isinstance(elt, ast.Name):
            target_names.append(elt.id)
        else:
            target_names.append("_")  # unsupported sub-target
    value_ir = self._py_expr_to_ir(stmt.value)
    result.append({"stmt": "TupleUnpack", "targets": target_names, "value": value_ir})
```

**M6 — `_find_assigned_vars`:**

2. Add scan for `TupleUnpack`:
```python
elif s.get("stmt") == "TupleUnpack":
    for t in s["targets"]:
        if t != "_":
            assigned.add(t)
```

**M6 — `_stmts_to_whyml`:**

3. Add handler:
```python
elif s["stmt"] == "TupleUnpack":
    val_w = self._expr_to_whyml(s["value"], local_refs)
    names = s["targets"]
    # All targets are new local refs — use let destructuring
    # WhyML: let (a, b) = f() in ...
    names_w = ", ".join(names)
    # Mark each as declared ref
    for n in names:
        if n != "_" and n in local_refs:
            declared_refs.add(n)
    # If targets are mutable (in local_refs), need ref wrapping after destructure
    if any(n in local_refs for n in names if n != "_"):
        # Emit: let (_tmp_a, _tmp_b) = f() in let a = ref _tmp_a in let b = ref _tmp_b in ...
        tmp_names = [f"_tu_{n}" for n in names]
        tmp_w = ", ".join(tmp_names)
        line = f"{indent}let ({tmp_w}) = {val_w} in"
        rest_prefix = ""
        for orig, tmp in zip(names, tmp_names):
            if orig != "_" and orig in local_refs:
                rest_prefix += f"\n{indent}let {orig} = ref {tmp} in"
        lines.append(line + rest_prefix)
    else:
        lines.append(f"{indent}let ({names_w}) = {val_w} in")
```

**M6 — `_find_return_type`:**

4. Add recursion into any nested statements within `TupleUnpack` (though it has
   no nested body, so this is just defensive — ensure it doesn't break).

### IR schema

```json
{"stmt": "TupleUnpack", "targets": ["a", "b"], "value": <ir_expr>}
```

### WhyML output

```whyml
(* if a, b are immutable *)
let (a, b) = f () in ...

(* if a, b are mutable (reassigned later) *)
let (_tu_a, _tu_b) = f () in
let a = ref _tu_a in
let b = ref _tu_b in ...
```

### Test plan

- Add `tests/to_annotate/077-tuple-unpacking.py`: function that calls a
  tuple-returning function and unpacks the result.

### Dependencies

None.

### Estimated effort

1–2 days.

---

## Item 9 — `assert` with message → `check` with Why3 label

### Summary

Extension of item 1: when `assert cond, msg` is written, the message surfaces as a
Why3 `[@expl:<msg>]` label, making proof-failure messages human-readable.

### Current state

Already covered by the implementation of item 1 — the `msg` field is optional in
the IR schema and the M6 handler checks for it.

### Files to change

Same as item 1. No additional changes needed.

### Step-by-step

See item 1 — the `msg` handling is included in that implementation.

### IR schema

```json
{"stmt": "Assert", "test": <ir_expr>, "msg": "total must equal n"}
```

### WhyML output

```whyml
check { [@expl:total must equal n] (total = n) }
```

### Test plan

Included in item 1's test file.

### Dependencies

Item 1 (this is a sub-feature of item 1).

### Estimated effort

0 additional days (included in item 1).

---

## Item 10 — `match` statement (Python 3.10+)

### Summary

`match`/`case` (structural pattern matching) is increasingly used in modern Python.
WhyML has a native `match ... with | Pattern -> ... end` construct. This is the
largest item in the plan.

### Current state

- No `ast.Match` handling anywhere in the pipeline.
- M3: no contract attachment logic for match statements.
- M5: no handler in `_py_stmts_to_ir`.
- M6: no handler in `_stmts_to_whyml`.

### Files to change

| File | Method / Location | Change |
|------|-------------------|--------|
| `src/pycsl/Module5_IREmitter.py` | `_py_stmts_to_ir` | Add `ast.Match` handler |
| `src/pycsl/Module5_IREmitter.py` | New helper | `_match_pattern_to_ir` for each pattern kind |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_stmts_to_whyml` | Add `Match` handler |
| `src/pycsl/Module6_WhyMLTranspiler.py` | New helper | `_pattern_to_whyml` for pattern emission |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_find_assigned_vars` | Recurse into match cases |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_find_return_type` | Recurse into match cases |

### Step-by-step

**Phase 1 — Minimal match (literal and capture patterns only):**

**M5 — `_py_stmts_to_ir`:**

1. Add `ast.Match` handler:
```python
elif isinstance(stmt, ast.Match):
    subject_ir = self._py_expr_to_ir(stmt.subject)
    cases_ir = []
    for case in stmt.cases:
        pattern_ir = self._match_pattern_to_ir(case.pattern)
        guard_ir = self._py_expr_to_ir(case.guard) if case.guard else None
        body_ir = self._py_stmts_to_ir(case.body)
        cases_ir.append({"pattern": pattern_ir, "guard": guard_ir, "body": body_ir})
    result.append({"stmt": "Match", "subject": subject_ir, "cases": cases_ir})
```

2. Add `_match_pattern_to_ir` helper:
```python
def _match_pattern_to_ir(self, pattern):
    if isinstance(pattern, ast.MatchValue):
        return {"pattern": "Value", "value": self._py_expr_to_ir(pattern.value)}
    elif isinstance(pattern, ast.MatchCapture):
        return {"pattern": "Capture", "name": pattern.name}
    elif isinstance(pattern, ast.MatchAs):
        if pattern.pattern is None:  # wildcard _
            return {"pattern": "Wildcard"}
        inner = self._match_pattern_to_ir(pattern.pattern)
        return {"pattern": "As", "inner": inner, "name": pattern.name}
    elif isinstance(pattern, ast.MatchOr):
        return {"pattern": "Or", "patterns": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
    elif isinstance(pattern, ast.MatchSequence):
        return {"pattern": "Sequence", "patterns": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
    elif isinstance(pattern, ast.MatchMapping):
        return {"pattern": "Mapping"}  # stub — defer full support
    elif isinstance(pattern, ast.MatchClass):
        return {"pattern": "Class"}  # stub — defer full support
    else:
        return {"pattern": "Unknown"}
```

**M6 — `_stmts_to_whyml`:**

3. For Phase 1, lower `Match` to chained `if/elif/else`:
```python
elif s["stmt"] == "Match":
    subject_w = self._expr_to_whyml(s["subject"], local_refs)
    # Lower to if/elif chain for literal patterns
    # For capture patterns, bind the variable
    for i, case in enumerate(s["cases"]):
        pat = case["pattern"]
        if pat["pattern"] == "Value":
            val_w = self._expr_to_whyml(pat["value"], local_refs)
            cond = f"({subject_w} = {val_w})"
        elif pat["pattern"] in ("Wildcard", "Capture"):
            cond = "true"
        # ... emit if/elif/else structure
```

**Phase 2 — Native WhyML match (future):**

WhyML `match` works with algebraic data types, not integer patterns. For integer
subjects, the `if/elif` lowering is correct. Native `match` would require defining
WhyML ADTs for the match patterns, which is a multi-week extension.

### IR schema

```json
{
  "stmt": "Match",
  "subject": <ir_expr>,
  "cases": [
    {
      "pattern": {"pattern": "Value", "value": <ir_expr>},
      "guard": <ir_expr or null>,
      "body": [<ir_stmts>]
    },
    {
      "pattern": {"pattern": "Wildcard"},
      "guard": null,
      "body": [<ir_stmts>]
    }
  ]
}
```

### WhyML output (Phase 1 — if/elif lowering)

```whyml
if (subject = 1) then begin
  ... case 1 body ...
end else if (subject = 2) then begin
  ... case 2 body ...
end else begin
  ... wildcard body ...
end
```

### Test plan

- Add `tests/to_annotate/078-match-literals.py`: function using `match x:` with
  literal `case 1:`, `case 2:`, `case _:`.
- Verify lowering to if/elif produces valid WhyML.

### Dependencies

None.

### Estimated effort

- Phase 1 (literal + capture + wildcard patterns, if/elif lowering): 2 weeks.
- Phase 2 (sequence, mapping, class patterns, native WhyML match): additional 2–4 weeks.

### Risks

- Pattern guards (`case x if x > 0:`) add complexity to the if/elif lowering.
- Sequence/mapping/class patterns require Python runtime introspection that has no
  WhyML equivalent — these may need to be modeled as abstract predicates.

---

## Item 11 — Lambda functions

### Summary

`ast.Lambda` returns `UnknownPyExpr`. Lambda functions are used in `sorted()`,
`map()`, `filter()`, and as callbacks. WhyML supports anonymous functions via
`fun x -> e`.

### Current state

- M5 `_py_expr_to_ir`: no `ast.Lambda` handler.
- M6: no `Lambda` IR handler.
- M4 `SemanticAnalyzer`: no scope analysis for lambda bodies.

### Files to change

| File | Method / Location | Change |
|------|-------------------|--------|
| `src/pycsl/Module5_IREmitter.py` | `_py_expr_to_ir` | Add `ast.Lambda` handler |
| `src/pycsl/Module4_SemanticAnalyzer.py` | Scope analysis | Add lambda scope handling |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `_expr_to_whyml` | Add `Lambda` handler |
| `src/pycsl/Module6_WhyMLTranspiler.py` | `transpile()` header | May need `use` for function types |

### Step-by-step

**Phase 1 — Simple lambdas (pure, single expression):**

**M5 — `_py_expr_to_ir`:**

1. Add handler:
```python
elif isinstance(expr, ast.Lambda):
    params = [arg.arg for arg in expr.args.args]
    body_ir = self._py_expr_to_ir(expr.body)
    return {"type": "Lambda", "params": params, "body": body_ir}
```

**M4 — Scope analysis:**

2. Lambda parameters create a new inner scope. Add a visitor for `ast.Lambda` that
   pushes the lambda parameters onto the scope stack, validates the body, then pops.

**M6 — `_expr_to_whyml`:**

3. Add handler:
```python
elif expr["type"] == "Lambda":
    params = expr["params"]
    body_w = self._expr_to_whyml(expr["body"], local_refs)
    param_str = " ".join(f"({p}: int)" for p in params)
    return f"(fun {param_str} -> {body_w})"
```

**Phase 2 — Closures over mutable state (deferred):**

Lambdas that capture mutable variables from the enclosing scope require WhyML
closure types and are significantly harder to formalize. Recommend:
- Phase 1: support only pure lambdas (no captured mutable state).
- Phase 2: deferred until the formal semantics in `form/` is complete.

### IR schema

```json
{"type": "Lambda", "params": ["x", "y"], "body": <ir_expr>}
```

### WhyML output

```whyml
(fun (x: int) (y: int) -> (x + y))
```

### Test plan

- Add `tests/to_annotate/079-lambda-simple.py`: function using
  `sorted(arr, key=lambda x: -x)`.

### Dependencies

None, but Phase 2 depends on formal semantics work in `form/`.

### Estimated effort

- Phase 1 (pure lambdas): 1 week.
- Phase 2 (closures): multi-month research project.

### Risks

- WhyML's type system requires explicit function types. `fun x -> x + 1` has type
  `int -> int`, which must be inferred or declared. Currently the pipeline uses
  only `int`, `unit`, and tuple types. Adding function types requires changes to
  `_find_return_type` and the argument-string builder in `transpile()`.
- `sorted(arr, key=lambda x: -x)` requires that `sorted` itself be handled as a
  special form (currently abstracted), AND that the lambda be passed as a function
  argument — this needs higher-order function support in the WhyML emission.

---

## Cross-item dependency graph

```
Item 1 ← Item 9 (assert msg is a sub-feature of assert)

Item 2  (independent)
Item 3  (independent)
Item 4  (independent)
Item 5  (independent, parallelisable)
Item 6  (independent)
Item 7  (independent)
Item 8  (independent)
Item 10 (independent)
Item 11 (independent)
```

All items except 9→1 are independent and can be implemented in parallel.

## Recommended implementation order

| Priority | Items | Rationale |
|----------|-------|-----------|
| 1 (immediate) | 2, 3 | Grammar-only; 0.5 day each; zero risk |
| 2 (immediate) | 4 | Grammar + M5 desugaring; 1 day; M6 already ready |
| 3 (short-term) | 1+9, 8 | Small M5+M6 additions; 1–2 days each |
| 4 (short-term) | 5 | Stub files only; 1 day; parallelisable |
| 5 (medium-term) | 6 | New infrastructure (pre-stmt buffer); 3 days |
| 6 (medium-term) | 7 | Ghost sub-arrays; 1 week |
| 7 (long-term) | 10 | Phase 1 if/elif lowering; 2 weeks |
| 8 (long-term) | 11 | Phase 1 pure lambdas; 1 week; Phase 2 deferred |
