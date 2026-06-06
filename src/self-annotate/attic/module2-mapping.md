# Module2_Parser ↔ Formal-Semantics Lemma Mapping

**Status:** ⚠️ **Historical document.** The `#@ proof rocq:` / `#@ proof lean:` proof-attribution directives this mapping was designed around were swept on 2026-05-27 (see `proof-to-axiom-from.md`). The text below is preserved as historical context.

Generated as part of `plan-formal-05.md` Layer 4 rollout. Each row
maps a Python method in `src/self-annotate/src/Module2_Parser.py`
to its corresponding inductive type / theorem in
`src/formal-semantics/{rocq,lean}/`.

**Lemma family**: AST construction. Module2 is the Python
implementation of the parse function from contract source text into
the `contract_expr` inductive of `Phase1_AST.v` (Coq) /
`ContractExpr` of `AST.lean` (Lean). The Lark-Transformer methods
(one per grammar production) are leaf-level constructor calls; the
high-value attribution is on the *entry points* that produce a
complete CSLNode tree.

**Naming convention**: qualnames use `Pycsl.Reference.Module2.<lemma>`.
Rocq uses snake_case (`contract_expr`, `stmt`); Lean uses
CamelCase (`ContractExpr`, `Stmt`).

## Methods with formal correspondence

| Python method | Rocq lemma / inductive | Lean lemma / inductive | Source file |
|---|---|---|---|
| `parse_contract` | `contract_expr` (inductive) | `ContractExpr` (inductive) | Phase1_AST.v / AST.lean |
| `parse_node_contracts` | `contract_expr` (inductive, list-of) | `ContractExpr` (inductive, list-of) | Phase1_AST.v / AST.lean |

## Coverage gaps (no `#@ proof` line emitted)

Module2 is dominated by leaf-level grammar handlers, none of which
have an independent formal theorem (they're constructors of the
inductive). These methods carry only structural contracts.

- **Dataclass declarations** (`Requires`, `Ensures`, `Assigns`,
  `BinOp`, `UnaryOp`, `Var`, `Number`, `Forall`, …, all ~70 CSLNode
  subclasses). These are plain Python dataclasses — they represent
  *constructors* of `contract_expr`, not theorems. No `#@ proof`
  attribution at the class level; the dataclass-as-IR-constructor
  pattern is documented in `src/self-annotate/README.md`.
- **Lark-Transformer methods** (`precondition`, `forall_expr`,
  `set_union_expr`, `mktuple_expr`, `proj_expr`, …, all ~120
  one-liner methods on `CSLTransformer`). Each method is a thin wrapper
  around a CSLNode constructor — collectively they implement the
  grammar→AST step. The umbrella attribution sits on `parse_contract`
  above.
- **Helpers**: `_csl_to_str`, `__init__`, etc.

## Verification

```bash
# Confirm each cited Rocq inductive exists.
for thm in contract_expr; do
    grep -l "Inductive $thm\b" src/formal-semantics/rocq/*.v \
      > /dev/null || echo "MISSING ROCQ: $thm"
done

# Confirm each cited Lean inductive exists.
for thm in ContractExpr; do
    grep -l "inductive $thm\b" src/formal-semantics/lean/PyCSL/*.lean \
      > /dev/null || echo "MISSING LEAN: $thm"
done
```
