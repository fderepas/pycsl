---
name: pycsl-data-formats
description: The five data formats that flow through the PyCSL compiler pipeline. Covers PyCSLContract (Module1 output), CSLNode AST (Module2 output), annotated ast.AST with csl_* fields (Module3 output), JSON IR dict structure (Module5 output), and WhyML text (Module6 output). Use when reading or writing pipeline stage boundaries.
---

# PyCSL Data Formats

Each of the five data formats below is the output of one pipeline module and the input of the next. Understanding these formats is essential for debugging pipeline failures or extending the compiler.

---

## Format 1 — `PyCSLContract` (output of Module1)

Defined in `src/pycsl/Module1_Ingestor.py`.

```python
@dataclass
class PyCSLContract:
    node_type: str         # 'FunctionDef' | 'While'
    node_name: str         # function name, e.g. 'add_positive', or '<while_loop>'
    line_number: int       # source line where the annotated node starts
    contracts: List[str]  # raw #@ strings stripped of the '#@' prefix
                           # e.g. ["requires n > 0", "ensures result > 0"]
```

Module1 uses LibCST's `PositionProvider` to find `#@` comments in the CST and attach them to the immediately following `FunctionDef` or `While` node.

After Module2 runs, `contracts` is replaced in-place with `List[CSLNode]` (parsed trees). Until Module2, `contracts` is always `List[str]`.

---

## Format 2 — `CSLNode` AST (output of Module2)

Defined in `src/pycsl/Module2_Parser.py`. Parsed by Lark LALR from the `csl.lark` grammar.

### Class hierarchy

```
CSLNode                          (base dataclass)
  ContractWrapper                (base for top-level contract kinds)
    Requires(expr: CSLNode)
    Ensures(expr: CSLNode)
    LoopInvariant(expr: CSLNode)
    LoopVariant(expr: CSLNode)
  Assigns(targets: List[CSLNode])
  QuantifierNode
    Forall(vars, domain, body: CSLNode)
    Exists(vars, domain, body: CSLNode)
  SingleExprNode
    UnaryOp(op: str, operand: CSLNode)
    Old(expr: CSLNode)              # \old(x) — pre-state value
  BinOp(left: CSLNode, op: str, right: CSLNode)
  Name(id: str)
  Lit(value)                        # integer or boolean literal
  Call(func: str, args: List[CSLNode])
  Subscript(value: CSLNode, index: CSLNode)
  Attribute(value: CSLNode, attr: str)
  Tuple(elts: List[CSLNode])
```

Module2 raises `PyCSLParseError` (from `errors.py`) on grammar failure.

---

## Format 3 — Annotated `ast.AST` (output of Module3)

Module3 (Weaver) runs Python's standard `ast.parse()` on the source, then walks the AST and injects extra attributes derived from the `PyCSLContract` list.

### Injected fields on `ast.FunctionDef` / `ast.AsyncFunctionDef`

| Field | Type | Content |
|-------|------|---------|
| `csl_requires` | `List[CSLNode]` | Parsed `Requires` nodes |
| `csl_ensures` | `List[CSLNode]` | Parsed `Ensures` nodes |
| `csl_assigns` | `List[CSLNode]` | Parsed `Assigns` nodes |
| `csl_trusted` | `bool` | True if `#@ \trusted` present |
| `csl_bounded_int` | `int \| None` | Bit-width from `#@ \bounded_int N` |

### Injected fields on `ast.While` / `ast.For`

| Field | Type | Content |
|-------|------|---------|
| `csl_loop_invariants` | `List[CSLNode]` | Parsed `LoopInvariant` nodes |
| `csl_loop_variants` | `List[CSLNode]` | Parsed `LoopVariant` nodes |

Nodes without any `#@` annotation have these fields set to empty lists / `False` / `None`.

Module4 (`SemanticAnalyzer`) validates this AST — it raises `PyCSLSemanticError` for ill-typed contracts (e.g., `\old` used outside a postcondition).

---

## Format 4 — JSON IR (output of Module5)

Module5 (`IREmitter`) walks the annotated `ast.AST` and produces a JSON string. The structure is validated by `validate_ir()` in `ir_schema.py` before serialisation.

### Top-level keys

```json
{
  "module_name": "my_module",
  "functions": [...],
  "classes": [...],
  "imports": [...],
  "globals": [...]
}
```

### Per-function dict (inside `"functions"`)

```json
{
  "name": "add_positive",
  "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
  "return_type": "int",
  "body": [...],
  "requires": [...],
  "ensures": [...],
  "assigns": [...],
  "loop_invariants": [],
  "loop_variants": [],
  "trusted": false,
  "memory_model": "hoare",
  "bounded_int": null
}
```

### Statement and expression dicts

Every node has a `"type"` key indicating its kind:

```
Statement types: Assign, AugAssign, Return, If, While, For, Assert, Pass, Expr
Expression types: BinOp, UnaryOp, Call, Subscript, Attribute, Name, Lit,
                  Tuple, List, Dict, Forall, Exists, Old, Len, Sum, IsSorted
```

Example `BinOp` expression:
```json
{"type": "BinOp", "left": {"type": "Name", "id": "a"}, "op": "+", "right": {"type": "Lit", "value": 1}}
```

`validate_ir()` raises `PyCSLIRError` if required top-level or per-function keys are absent.

---

## Format 5 — WhyML text (output of Module6)

WhyML is the input language for Why3. PyCSL produces a `.mlw` file.

### Structure

```whyml
module MyModule

  use int.Int
  use array.Array
  (* … additional use declarations … *)

  let add_positive (a : int) (b : int) : int
    requires { a > 0 }
    requires { b > 0 }
    ensures  { result > 0 }
  =
    a + b

end
```

### Key WhyML conventions used by PyCSL

| Python construct | WhyML equivalent |
|-----------------|-----------------|
| `==` | `=` |
| `!=` | `<>` |
| `//` | `div` |
| `%` | `mod` |
| `and` | `&&` |
| `or` | `\|\|` |
| `not` | `not` |
| `==>` | `->` (implication) |
| `<==>` | `<->` (equivalence) |
| `\old(x)` | `(old x)` |
| `\forall x` | `forall x` |
| `\exists x` | `exists x` |
| Array read `a[i]` (hoare) | `a[i]` |
| Array write `a[i] = v` (hoare) | `a <- a[i <- v]` |
| Mutable ref `x` (typed/store) | `!x` |

WhyML identifiers must start with lowercase, contain no dots, and avoid Why3 reserved words. Module6 applies `_whyml_ident()` to sanitise all Python names.
