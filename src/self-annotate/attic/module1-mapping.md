# Module1_Ingestor ↔ Formal-Semantics Lemma Mapping

**Status:** ⚠️ **Historical document.** Generated as part of
`plan-formal-05.md` Layer 4 rollout. The `#@ proof rocq:` /
`#@ proof lean:` proof-attribution directives this mapping was
designed around were swept on 2026-05-27 (see
`proof-to-axiom-from.md`). The text below is preserved as
historical context.

## Summary

**Module1 has no formal-semantics correspondent.** It performs pure
data extraction from Python source text via libCST: walk the CST,
collect `#@`-prefixed comments, group them by their target node
(FunctionDef, While, For, ClassDef, …), return a list of
`PyCSLContract` records. The output is a list of *raw strings*; the
parsing into `contract_expr` happens in Module2.

The formal semantics (`Phase1_AST.v`, `AST.lean`) starts from
`contract_expr` — already-parsed structure. The text-to-strings
extraction step has no inductive, no theorem, no record on the
proof side.

**Therefore:** no `#@ proof rocq:` / `#@ proof lean:` directives are
emitted on any Module1 method. Per the coverage-gap policy in
`plan-formal-05.md` ("do not fabricate theorem names"), this is the
honest classification.

## Methods (all coverage gaps)

| Python method | Role |
|---|---|
| `__init__` (both `Ingestor` and `IngestorProcessor`) | constructor |
| `visit_Module` | extract module-header `#@` lines |
| `_extract_contracts_from_node` | helper that pulls `#@` strings from a node's leading lines |
| `visit_ClassDef` / `leave_ClassDef` | class-scope tracking |
| `visit_FunctionDef` | attach `#@` strings to function nodes |
| `visit_While` / `visit_For` / `visit_With` | attach to loop / context-manager nodes |
| `visit_SimpleStatementLine` | attach to ghost statements |
| `visit_IndentedBlock` | attach to block scopes |
| `process` | top-level driver |

All methods carry only structural contracts (`#@ requires`, `#@ ensures`, `#@ assigns`) where applicable — no proof attribution.

## Verification

```bash
# No #@ proof directives expected; audit confirms emptiness.
grep -c "^\s*#@ proof " src/self-annotate/src/Module1_Ingestor.py
# Expected: 0
```

## Future work

A formal model of the libCST-extraction step would let Module1's
methods carry `#@ proof` lines. This is **out of scope** for the
`plan-formal-05.md` Layer 4 work — the trust chain's value lies in
the semantic modules (2, 3, 4, 5, 6), not in the textual ingest.
