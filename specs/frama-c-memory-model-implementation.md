# Frama-C Memory Model — Implementation Guide

## Scope

This document maps the design in `frama-c-memory-model.md` to concrete code changes
across every `Module*.py` file in the PyCSL pipeline. Each section contains:

- The **current code** (with line references)
- The **exact change** (new dataclass, new grammar rule, new handler, etc.)
- **Example before/after** showing the WhyML difference

The implementation is structured in three phases matching the design document.

---

# Phase 0 — `\assigns` Region Syntax

## Module 2 — Parser (`Module2_Parser.py`)

### 0.1  New Dataclass (after line 91)

```python
@dataclass
class AssignsRegion(CSLNode):
    """Represents `arr[lo..hi]` inside an assigns clause."""
    base: str           # array parameter name
    low: CSLNode        # lower bound expression (inclusive)
    high: CSLNode       # upper bound expression (exclusive)
```

### 0.2  Grammar Change (lines 110–113)

Current:
```
assigns: "assigns" assigns_target
?assigns_target: expr_list
               | "\\nothing" -> nothing
```

New:
```
assigns: "assigns" assigns_target
?assigns_target: assigns_region_list
               | expr_list
               | "\\nothing" -> nothing

assigns_region_list: assigns_region ("," assigns_region)*
assigns_region: CNAME "[" expr ".." expr "]"
```

The `assigns_region` rule uses `CNAME "[" expr ".." expr "]"` which is LALR(1)-safe:
after `CNAME`, the parser sees `[`, which distinguishes this from a bare `CNAME` (var).
After the first `expr`, `..` (two dots) distinguishes it from `SubscriptAccess`'s `]`.

**Grammar conflict note:** The existing `subscript_access` rule is `CNAME "[" expr "]"`.
The `assigns_region` rule is `CNAME "[" expr ".." expr "]"`. Lark's LALR parser can
distinguish these because after the first `expr`, the lookahead is either `]`
(subscript_access) or `..` (assigns_region). However, `..` must be added as a terminal:

```
RANGE_OP: ".."
```

### 0.3  Transformer Method (after line 189)

```python
def assigns_region(self, name, low, high):
    return AssignsRegion(str(name), low, high)

def assigns_region_list(self, *regions):
    return list(regions)
```

### 0.4  `assigns` Transformer Update (lines 173–179)

Current:
```python
def assigns(self, target):
    if isinstance(target, Nothing):
        return Assigns([target])
    elif isinstance(target, list):
        return Assigns(target)
    else:
        return Assigns([target])
```

New — unchanged. The `assigns_region_list` transformer returns a `list`, which the
existing `isinstance(target, list)` branch handles. Each element is an `AssignsRegion`
node instead of a `Var` node, but `Assigns.targets` is typed `List[CSLNode]` which
accepts both.

---

## Module 4 — Semantic Analyzer (`Module4_SemanticAnalyzer.py`)

### 0.5  Import Update (line 6)

Add `AssignsRegion` to the import list:
```python
from Module2_Parser import (
    ..., AssignsRegion
)
```

### 0.6  `extract_variables` Extension (after line 48)

```python
elif isinstance(node, AssignsRegion):
    return {node.base} | extract_variables(node.low) | extract_variables(node.high)
```

### 0.7  `\assigns` Region Validation (new, in `visit_FunctionDef`, after line 167)

After validating `csl_assigns`, add:

```python
# Validate assigns regions: base must be a list-typed parameter
for ass in getattr(node, 'csl_assigns', []):
    for target in ass.targets:
        if isinstance(target, AssignsRegion):
            arr_type = self.current_scope.get(target.base)
            if arr_type is None:
                raise PyCSLSemanticError(
                    f"Assigns region references undefined variable '{target.base}' "
                    f"in {self.current_function_name}."
                )
            if arr_type not in ("list", "List", "Any"):
                raise PyCSLSemanticError(
                    f"Assigns region on non-list variable '{target.base}' "
                    f"(type '{arr_type}') in {self.current_function_name}."
                )
```

---

## Module 5 — IR Emitter (`Module5_IREmitter.py`)

### 0.8  Import Update (line 8)

Add `AssignsRegion` to the import:
```python
from Module2_Parser import (
    ..., AssignsRegion
)
```

### 0.9  `_csl_to_ir` Extension (after line 48, before the fallback)

```python
elif isinstance(node, AssignsRegion):
    return {
        "type": "AssignsRegion",
        "base": node.base,
        "low": self._csl_to_ir(node.low),
        "high": self._csl_to_ir(node.high)
    }
```

---

## Module 6 — WhyML Transpiler (`Module6_WhyMLTranspiler.py`)

### 0.10  Frame Condition Emission (Hoare model — no change)

In the Hoare model (current default), `AssignsRegion` nodes in the `assigns` contract
are silently ignored. No frame condition is emitted because value-semantic arrays cannot
alias. This preserves backward compatibility.

### 0.11  Frame Condition Emission (Typed model — Phase 2)

Deferred to Phase 2. Documented here for completeness:

For each function, after emitting `ensures` clauses, Module 6 scans the `assigns`
contract. If it contains `AssignsRegion` nodes, it generates:

```python
# In transpile(), after emitting ensures clauses:
assigns_list = contracts.get("assigns", [])
regions = [a for a in assigns_list if a.get("type") == "AssignsRegion"]
nothings = [a for a in assigns_list if a.get("type") == "Nothing"]

if nothings:
    out.append(f"    ensures  {{ !int_mem = old !int_mem }}")
elif regions:
    exclusions = []
    for r in regions:
        base = r["base"]
        lo = self._expr_to_whyml(r["low"], spec_refs)
        hi = self._expr_to_whyml(r["high"], spec_refs)
        exclusions.append(f"({base} + {lo} <= l < {base} + {hi})")
    neg = " /\\ ".join(f"not {e}" for e in exclusions)
    out.append(f"    writes   {{ int_mem }}")
    out.append(f"    ensures  {{ forall l: int. {neg}"
               f" -> Map.get !int_mem l = Map.get (old !int_mem) l }}")
```

---

# Phase 1 — `\valid` and `\separated` Predicates

## Module 2 — Parser (`Module2_Parser.py`)

### 1.1  New Dataclasses (after `AssignsRegion`)

```python
@dataclass
class Valid(CSLNode):
    """Represents `\\valid(arr, n)` — memory region is allocated."""
    base: str
    length: CSLNode

@dataclass
class Separated(CSLNode):
    """Represents `\\separated(a, na, b, nb)` — regions don't overlap."""
    base1: str
    length1: CSLNode
    base2: str
    length2: CSLNode
```

### 1.2  Grammar Additions (in the `?atom` rule, after line 141)

```
?atom: NUMBER -> number
     | "self" "." CNAME -> field_access
     | CNAME "[" expr ".." expr "]" -> assigns_region_atom   // only inside assigns
     | CNAME "[" expr "]" -> subscript_access
     | CNAME -> var
     | "\\result" -> result
     | "\\old" "(" expr ")" -> old_var
     | "\\length" "(" CNAME ")" -> array_length
     | "\\valid" "(" CNAME "," expr ")" -> valid_pred
     | "\\separated" "(" CNAME "," expr "," CNAME "," expr ")" -> separated_pred
     | "(" expr ")"
```

**LALR safety:** `\valid` and `\separated` begin with a unique backslash-keyword token,
making them unambiguous at the `?atom` level. No conflict with existing rules.

### 1.3  Transformer Methods

```python
def valid_pred(self, name, length):
    return Valid(str(name), length)

def separated_pred(self, name1, len1, name2, len2):
    return Separated(str(name1), len1, str(name2), len2)
```

---

## Module 4 — Semantic Analyzer (`Module4_SemanticAnalyzer.py`)

### 1.4  Import Update

Add `Valid`, `Separated` to the import list.

### 1.5  `extract_variables` Extensions

```python
elif isinstance(node, Valid):
    return {node.base} | extract_variables(node.length)
elif isinstance(node, Separated):
    return ({node.base1} | extract_variables(node.length1) |
            {node.base2} | extract_variables(node.length2))
```

### 1.6  Validation: `\valid` base must be `list`-typed

In `_validate_contract`, after checking variable scope (line 92), add:

```python
# Validate \valid and \separated base types
def _validate_predicate_bases(self, contract: CSLNode, context_name: str):
    """Recursively check that \valid and \separated reference list-typed params."""
    if isinstance(contract, Valid):
        arr_type = self.current_scope.get(contract.base)
        if arr_type not in ("list", "List", "Any", None):
            raise PyCSLSemanticError(
                f"\\valid base '{contract.base}' is not a list parameter "
                f"in {context_name}."
            )
    elif isinstance(contract, Separated):
        for base in (contract.base1, contract.base2):
            arr_type = self.current_scope.get(base)
            if arr_type not in ("list", "List", "Any", None):
                raise PyCSLSemanticError(
                    f"\\separated base '{base}' is not a list parameter "
                    f"in {context_name}."
                )
    elif isinstance(contract, BinOp):
        self._validate_predicate_bases(contract.left, context_name)
        self._validate_predicate_bases(contract.right, context_name)
    elif isinstance(contract, UnaryOp) or isinstance(contract, Old):
        self._validate_predicate_bases(contract.expr, context_name)
```

Call `_validate_predicate_bases` from `_validate_contract` after the scope check.

---

## Module 5 — IR Emitter (`Module5_IREmitter.py`)

### 1.7  Import Update

Add `Valid`, `Separated` to the import.

### 1.8  `_csl_to_ir` Extensions

```python
elif isinstance(node, Valid):
    return {
        "type": "Valid",
        "base": node.base,
        "length": self._csl_to_ir(node.length)
    }
elif isinstance(node, Separated):
    return {
        "type": "Separated",
        "base1": node.base1,
        "len1": self._csl_to_ir(node.length1),
        "base2": node.base2,
        "len2": self._csl_to_ir(node.length2)
    }
```

---

## Module 6 — WhyML Transpiler (`Module6_WhyMLTranspiler.py`)

### 1.9  `_expr_to_whyml` Extensions (in the expression translator, after `ArrayLen`)

**Hoare model (current):**
```python
elif t == "Valid":
    base = expr["base"]
    length = self._expr_to_whyml(expr["length"], local_refs, invariant_ctx)
    if self.memory_model == "hoare":
        # In Hoare model, valid means index is within array bounds
        return f"({length} >= 0 && {length} <= length {base})"
    else:
        return f"(valid !int_mem {base} {length})"

elif t == "Separated":
    if self.memory_model == "hoare":
        # In Hoare model, value-typed arrays are always disjoint
        return "true"
    else:
        b1, l1 = expr["base1"], self._expr_to_whyml(expr["len1"], local_refs, invariant_ctx)
        b2, l2 = expr["base2"], self._expr_to_whyml(expr["len2"], local_refs, invariant_ctx)
        return f"(separated {b1} {l1} {b2} {l2})"
```

---

# Phase 2 — Typed Memory Model Backend

This is the largest phase. It introduces a new code path in Module 6 and changes how
Module 5 emits IR for list-typed parameters.

## Module 5 — IR Emitter (`Module5_IREmitter.py`)

### 2.1  Conditional IR Emission (No Change)

Module 5 is **memory-model-agnostic**. It emits the same IR regardless of model:
- `Subscript` for reads, `ArraySet` for writes, `Call(len)` for length.

The memory model flag lives in Module 6 only. Module 5 does NOT know which backend
will consume its output.

**Rationale:** This preserves the clean pipeline separation. Module 5 lowers Python AST
to a language-agnostic IR. Module 6 decides how to translate that IR to WhyML based on
the memory model.

The one piece of information Module 5 carries forward is the **symbol table** — the
type of each parameter (`"list"`, `"int"`, etc.). Module 6 uses this to determine which
parameters are heap-backed.

---

## Module 6 — WhyML Transpiler (`Module6_WhyMLTranspiler.py`)

### 2.2  Constructor Change (line 7)

```python
def __init__(self, json_ir: str, memory_model: str = "hoare"):
    self.ir = json.loads(json_ir)
    self.memory_model = memory_model   # "hoare" | "typed" | "store"
    self.op_map = { ... }              # unchanged
```

### 2.3  Preamble Emission (in `transpile()`, lines 384–397)

Current:
```python
out = [
    "module PyCSL_Program",
    "  use int.Int",
    "  use int.EuclideanDivision",
    "  use ref.Ref",
]
if needs_array:
    out.append("  use array.Array")
```

New:
```python
out = [
    "module PyCSL_Program",
    "  use int.Int",
    "  use int.EuclideanDivision",
    "  use ref.Ref",
]

if self.memory_model == "hoare":
    if needs_array:
        out.append("  use array.Array")
elif self.memory_model in ("typed", "store"):
    out.append("  use map.Map")
    out.append("")
    out.append("  type loc = int")
    out.append("  constant max_addr : int = 1073741824")
    if self.memory_model == "typed":
        out.append("  val int_mem : ref (map loc int)")
    else:
        out.append("  val store : ref (map loc int)")
    out.append("")
    heap_name = "int_mem" if self.memory_model == "typed" else "store"
    out.append(f"  predicate valid (m: map loc int) (base: loc) (n: int) =")
    out.append(f"    n >= 0 /\\ base >= 0 /\\ base + n <= max_addr")
    out.append("")
    out.append(f"  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =")
    out.append(f"    a + na <= b \\/ b + nb <= a")
    out.append("")
```

### 2.4  Helper: Heap Variable Name

```python
@property
def _heap_var(self) -> str:
    """Returns the name of the mutable heap variable for the current model."""
    if self.memory_model == "typed":
        return "int_mem"
    elif self.memory_model == "store":
        return "store"
    raise ValueError(f"No heap variable in model '{self.memory_model}'")
```

### 2.5  Parameter Emission (in `transpile()`, lines 430–453)

Current (standalone function, lines 446–453):
```python
args = [v for v in symbol_table if v not in local_refs or v in ref_params]
args_str = " ".join([
    f"({arg}: ref int)" if arg in ref_params else
    f"({arg}: array int)" if symbol_table.get(arg) == "list" else
    f"({arg}: int)"
    for arg in args
])
```

New:
```python
args = [v for v in symbol_table if v not in local_refs or v in ref_params]

def _param_type(arg: str) -> str:
    if arg in ref_params:
        return f"({arg}: ref int)"
    if symbol_table.get(arg) == "list":
        if self.memory_model == "hoare":
            return f"({arg}: array int)"
        else:
            # Heap model: list → loc + length parameter
            return f"({arg}: loc) ({arg}_len: int)"
    return f"({arg}: int)"

args_str = " ".join(_param_type(arg) for arg in args)
```

For methods (lines 434–443), the same logic applies to the args after `(self: type)`.

### 2.6  Expression Translator Changes (in `_expr_to_whyml`)

#### 2.6.1  `Subscript` (line 191–194)

Current:
```python
elif t == "Subscript":
    value = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx)
    index = self._expr_to_whyml(expr["index"], local_refs, invariant_ctx)
    return f"{value}[{index}]"
```

New:
```python
elif t == "Subscript":
    value = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx)
    index = self._expr_to_whyml(expr["index"], local_refs, invariant_ctx)
    if self.memory_model == "hoare":
        return f"{value}[{index}]"
    else:
        # Heap model: arr[i] → Map.get !int_mem (arr + i)
        return f"(Map.get !{self._heap_var} ({value} + {index}))"
```

#### 2.6.2  `Call` — `len()` (line 179–180)

Current:
```python
if func_name == "len" and len(args) == 1:
    return f"(length {args[0]})"
```

New:
```python
if func_name == "len" and len(args) == 1:
    if self.memory_model == "hoare":
        return f"(length {args[0]})"
    else:
        # Heap model: len(arr) → arr_len (the shadow parameter)
        # args[0] is the WhyML for the array — strip ! if present
        arr_name = args[0].lstrip("!")
        return f"{arr_name}_len"
```

#### 2.6.3  `ArrayLen` (line 210–211)

Current:
```python
elif t == "ArrayLen":
    return f"(length {expr['var']})"
```

New:
```python
elif t == "ArrayLen":
    if self.memory_model == "hoare":
        return f"(length {expr['var']})"
    else:
        return f"{expr['var']}_len"
```

#### 2.6.4  `Old` — Generalised for Heap (line 164–166)

Current:
```python
elif t == "Old":
    e = self._expr_to_whyml(expr["expr"], local_refs, invariant_ctx)
    return f"(old {e})"
```

New:
```python
elif t == "Old":
    inner = expr["expr"]
    if self.memory_model != "hoare" and inner.get("type") == "Subscript":
        # \old(arr[i]) → Map.get (old !int_mem) (arr + i)
        value = self._expr_to_whyml(inner["value"], local_refs, invariant_ctx)
        index = self._expr_to_whyml(inner["index"], local_refs, invariant_ctx)
        return f"(Map.get (old !{self._heap_var}) ({value} + {index}))"
    e = self._expr_to_whyml(inner, local_refs, invariant_ctx)
    return f"(old {e})"
```

### 2.7  Statement Translator Changes (in `_stmts_to_whyml`)

#### 2.7.1  `ArraySet` (line 263–267)

Current:
```python
elif s_type == "ArraySet":
    array_expr = self._expr_to_whyml(stmt["array"], local_refs)
    index_expr = self._expr_to_whyml(stmt["index"], local_refs)
    val_expr = self._expr_to_whyml(stmt["value"], local_refs)
    code = f"{indent}{array_expr}[{index_expr}] <- {val_expr}"
```

New:
```python
elif s_type == "ArraySet":
    array_expr = self._expr_to_whyml(stmt["array"], local_refs)
    index_expr = self._expr_to_whyml(stmt["index"], local_refs)
    val_expr = self._expr_to_whyml(stmt["value"], local_refs)
    if self.memory_model == "hoare":
        code = f"{indent}{array_expr}[{index_expr}] <- {val_expr}"
    else:
        hv = self._heap_var
        code = (f"{indent}{hv} := Map.set !{hv} "
                f"({array_expr} + {index_expr}) {val_expr}")
```

#### 2.7.2  `For` loop desugaring (lines 317–359)

Current (line 332):
```python
while_parts = [f"{indent}while !{idx} < length {iter_expr} do"]
```

New:
```python
if self.memory_model == "hoare":
    while_parts = [f"{indent}while !{idx} < length {iter_expr} do"]
else:
    while_parts = [f"{indent}while !{idx} < {iter_expr}_len do"]
```

Current (line 342, element binding):
```python
while_parts.append(f"{inner_indent}  let {target} = ref ({iter_expr}[!{idx}]) in")
```

New:
```python
if self.memory_model == "hoare":
    while_parts.append(
        f"{inner_indent}  let {target} = ref ({iter_expr}[!{idx}]) in")
else:
    hv = self._heap_var
    while_parts.append(
        f"{inner_indent}  let {target} = ref "
        f"(Map.get !{hv} ({iter_expr} + !{idx})) in")
```

### 2.8  Frame Condition Generation (new method)

Add a new method to `Module6_WhyMLTranspiler`:

```python
def _emit_frame_condition(self, assigns_list: List[Dict[str, Any]],
                          spec_refs: Set[str]) -> List[str]:
    """Generate WhyML frame condition clauses from \assigns contracts.

    Returns a list of WhyML lines (writes + ensures) to append to the
    function specification.
    """
    if self.memory_model == "hoare":
        return []  # No frame condition needed in value-semantic model

    hv = self._heap_var
    regions = [a for a in assigns_list if a.get("type") == "AssignsRegion"]
    nothings = [a for a in assigns_list if a.get("type") == "Nothing"]

    if nothings:
        return [f"    ensures  {{ !{hv} = old !{hv} }}"]

    if not regions:
        # No assigns clause → conservative: function may modify anything
        return [f"    writes   {{ {hv} }}"]

    lines = [f"    writes   {{ {hv} }}"]
    exclusions = []
    for r in regions:
        base = r["base"]
        lo = self._expr_to_whyml(r["low"], spec_refs)
        hi = self._expr_to_whyml(r["high"], spec_refs)
        exclusions.append(f"({base} + {lo} <= l && l < {base} + {hi})")

    neg = " && ".join(f"(not {e})" for e in exclusions)
    lines.append(
        f"    ensures  {{ forall l: int. {neg}"
        f" -> Map.get !{hv} l = Map.get (old !{hv}) l }}"
    )
    return lines
```

Call this method in `transpile()`, after emitting `ensures` clauses (after line 470):

```python
# Frame condition from \assigns
frame_lines = self._emit_frame_condition(
    contracts.get("assigns", []), spec_refs
)
for fl in frame_lines:
    out.append(fl)
```

### 2.9  `needs_array` → Model-Aware Flag (lines 373–380)

Current:
```python
needs_array = has_list_param or \
            any(self._uses_for(body) for body in all_bodies) or \
            any(self._uses_subscript(body) for body in all_bodies) or \
            any(self._uses_arrayset(body) for body in all_bodies)
```

New:
```python
if self.memory_model == "hoare":
    needs_array = has_list_param or \
                any(self._uses_for(body) for body in all_bodies) or \
                any(self._uses_subscript(body) for body in all_bodies) or \
                any(self._uses_arrayset(body) for body in all_bodies)
else:
    needs_array = False  # Heap models use map.Map, not array.Array
```

---

# Phase 3 — `\old(arr[i])` Generalisation

## Module 2 — Parser

### 3.1  No Grammar Change

`\old(expr)` already accepts any expression including `SubscriptAccess(arr, i)`.
The parser produces `Old(SubscriptAccess("arr", Var("i")))`.

## Module 5 — IR Emitter

### 3.2  No Change

`_csl_to_ir` already handles `Old` wrapping any inner node:
```python
elif isinstance(node, CSLOld):
    if isinstance(node.expr, CSLFieldAccess):
        return {"type": "OldField", ...}
    return {"type": "Old", "expr": self._csl_to_ir(node.expr)}
```

For `Old(SubscriptAccess(...))`, this emits:
```json
{"type": "Old", "expr": {"type": "Subscript", "value": ..., "index": ...}}
```

## Module 6 — WhyML Transpiler

### 3.3  Already Handled

The `Old` handler added in Phase 2, section 2.6.4, checks for `inner.get("type") == "Subscript"`
and emits `Map.get (old !int_mem) (arr + i)`.

### 3.4  Test Case

Python:
```python
#@ requires \valid(arr, n)
#@ requires n >= 2
#@ ensures arr[0] == \old(arr[1])
#@ ensures arr[1] == \old(arr[0])
#@ assigns arr[0..2]
def swap_first_two(arr: list, n: int) -> int:
    tmp = arr[0]
    arr[0] = arr[1]
    arr[1] = tmp
    return 0
```

Typed model WhyML:
```whyml
let swap_first_two (arr: loc) (arr_len: int) (n: int) : int
  requires { valid !int_mem arr n }
  requires { n >= 2 }
  ensures  { Map.get !int_mem (arr + 0) = Map.get (old !int_mem) (arr + 1) }
  ensures  { Map.get !int_mem (arr + 1) = Map.get (old !int_mem) (arr + 0) }
  writes   { int_mem }
  ensures  { forall l: int. (not (arr + 0 <= l && l < arr + 2))
             -> Map.get !int_mem l = Map.get (old !int_mem) l }
=
  let tmp = ref (Map.get !int_mem (arr + 0)) in
  int_mem := Map.set !int_mem (arr + 0) (Map.get !int_mem (arr + 1));
  int_mem := Map.set !int_mem (arr + 1) !tmp;
  0
```

---

# Phase 4 — Store Model Backend

## Module 6 — WhyML Transpiler

### 4.1  No New Code Paths

The Store model reuses **all** Typed model code paths. The only difference is the
heap variable name (`store` vs `int_mem`), which is already abstracted via the
`_heap_var` property (section 2.4).

The preamble change (section 2.3) already handles `self.memory_model == "store"`:
it emits `val store : ref (map loc int)` instead of `val int_mem : ref (map loc int)`.

### 4.2  When to Use Store vs Typed

From the user's perspective:

```json
{"memory-model": "store"}
```

The generated WhyML is identical to the Typed model except:
- Preamble uses `val store` instead of `val int_mem`
- All `int_mem` references become `store`

The practical difference appears when multi-type arrays are added in the future:
the Typed model will use separate maps (`int_mem`, `float_mem`), while the Store
model uses a single `store` for everything.

---

# Phase 5 — `\at(expr, L)` Labels (Deferred)

This is documented for completeness. Implementation is deferred until Phases 1–4
are stable.

## Module 1 — Ingestor (`Module1_Ingestor.py`)

### 5.1  Label Extraction

Add a new visit hook for label annotations:

```python
def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> None:
    """Detect #@ label L annotations."""
    for line in node.leading_lines:
        if isinstance(line, cst.EmptyLine) and line.comment:
            comment_str = line.comment.value
            if comment_str.startswith("#@") and "label" in comment_str:
                clean = comment_str[2:].strip()
                # Parse: "label <NAME>"
                parts = clean.split()
                if len(parts) == 2 and parts[0] == "label":
                    pos = self.get_metadata(PositionProvider, node).start
                    self.extracted_nodes.append(
                        PyCSLContract(
                            node_type="Label",
                            node_name=parts[1],
                            line_number=pos.line,
                            contracts=[clean]
                        )
                    )
```

## Module 2 — Parser

### 5.2  Grammar Addition

```
?contract: ... | label_decl
label_decl: "label" CNAME

?atom: ...
     | "\\at" "(" expr "," CNAME ")" -> at_expr
```

### 5.3  Dataclasses

```python
@dataclass
class Label(CSLNode):
    name: str

@dataclass
class At(CSLNode):
    expr: CSLNode
    label: str
```

## Module 3 — Weaver

### 5.4  Label Attachment

Labels are attached to the **next** statement node in the AST body. The weaver must
track label nodes and attach them to the immediately following `ast.stmt`.

This requires a new attribute: `node.csl_labels: List[str]`.

## Module 5 — IR Emitter

### 5.5  IR Nodes

```python
# Label statement
{"stmt": "Label", "name": "L"}

# At expression
{"type": "At", "expr": ..., "label": "L"}
```

## Module 6 — WhyML Transpiler

### 5.6  WhyML Emission

```python
# Label:
code = f"{indent}label {stmt['name']} in"

# At expression (Typed/Store model):
# \at(arr[i], L) → Map.get (int_mem at L) (arr + i)
elif t == "At":
    label = expr["label"]
    inner = expr["expr"]
    if inner.get("type") == "Subscript" and self.memory_model != "hoare":
        value = self._expr_to_whyml(inner["value"], local_refs, invariant_ctx)
        index = self._expr_to_whyml(inner["index"], local_refs, invariant_ctx)
        return f"(Map.get ({self._heap_var} at {label}) ({value} + {index}))"
    else:
        e = self._expr_to_whyml(inner, local_refs, invariant_ctx)
        return f"({e} at {label})"
```

---

# Cross-Cutting Concerns

## Configuration (`agents-config.json`)

Add a new key:

```json
{
  "model": "claude-sonnet-4-20250514",
  "memory-model": "hoare",
  ...
}
```

## CLI (`pycsl` script)

The `pycsl` script must pass the `memory_model` flag to Module 6:

```python
# In pycsl:
memory_model = config.get("memory-model", "hoare")
m6 = Module6_WhyMLTranspiler(ir_json, memory_model=memory_model)
```

## Backward Compatibility

| Model | Behaviour |
|---|---|
| `"hoare"` (default) | Identical to current PyCSL. No heap, no frame conditions. All existing tests pass unchanged. |
| `"typed"` | New heap-based emission. Existing tests must be updated with `\valid`/`\separated` preconditions. |
| `"store"` | Same as `"typed"` but single heap variable. |

## Test Strategy

### Phase 0 Tests
- Parse `#@ assigns arr[0..n-1]` → `AssignsRegion("arr", Number(0), Var("n-1"))`.
- Verify M4 rejects `#@ assigns x[0..n]` when `x: int`.

### Phase 1 Tests
- Parse `#@ requires \valid(arr, n)` → `Valid("arr", Var("n"))`.
- Parse `#@ requires \separated(a, n, b, m)` → `Separated(...)`.
- Hoare model: `\valid` emits bounds check, `\separated` emits `true`.
- Typed model: both emit predicate applications.

### Phase 2 Tests
- `fill_and_read` example (from design doc): verify `\separated` + `\assigns` proves
  `list_b[0]` unchanged.
- Array sum: verify `Map.get`/`Map.set` chain produces correct WhyML.
- For-loop desugaring: verify `Map.get !int_mem (arr + !_idx)` emission.

### Phase 3 Tests
- `swap_first_two` example: verify `\old(arr[i])` → `Map.get (old !int_mem) (arr + i)`.

### Phase 4 Tests
- Rerun all Phase 2 tests with `memory_model="store"`, verifying `store` replaces
  `int_mem` everywhere.

---

# Summary: Files Changed per Phase

| Phase | M1 | M2 | M3 | M4 | M5 | M6 | Config |
|---|---|---|---|---|---|---|---|
| **0** `\assigns` regions | — | Grammar + dataclass + transformer | — | Import + extract_variables + validation | Import + `_csl_to_ir` | Frame condition method (deferred to P2) | — |
| **1** `\valid`/`\separated` | — | Grammar + 2 dataclasses + 2 transformers | — | Import + extract_variables + type validation | Import + `_csl_to_ir` | `_expr_to_whyml` (2 new cases) | — |
| **2** Typed model | — | — | — | — | — | Constructor, preamble, params, Subscript, Call(len), ArrayLen, Old, ArraySet, For, frame condition, needs_array | `memory-model` key |
| **3** `\old(arr[i])` | — | — | — | — | — | (Already in P2) | — |
| **4** Store model | — | — | — | — | — | (Already in P2 via `_heap_var`) | — |
| **5** `\at` labels | Label extraction | Grammar + 2 dataclasses | Label attachment | — | Label + At IR | Label + At emission | — |
