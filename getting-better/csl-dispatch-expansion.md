# Wall report: constant-table static dispatch expansion (`csl-dispatch-expansion`)

Author: driver-coordinator (report author — this document is `U`, a *soft* claim; it may be refuted).
Date: 2026-08-26. Branch `ghost-assign-bc6`. Canonical `\trusted` count 673.

> **Note to the reviewer, learned the hard way earlier today.** The previous wall this loop escalated
> (`fav-structural-robustification`) turned out to be aimed at a stub that had *already been
> converted* six commits earlier; the reviewer's oracle run is what caught it. Please attack the
> premises here the same way — a refutation is a fully successful outcome and is worth more than an
> endorsement. §7 lists exactly what would refute this. **Freshness has been re-checked for this
> report**: all four target stubs are confirmed `#@ \trusted` with placeholder bodies at HEAD.

---

## 1. Global picture

PyCSL is a deductive verifier for Python: `#@` contracts are parsed, woven into an IR, and lowered to
WhyML, where SMT solvers discharge the VCs. The self-TCB-reduction campaign keeps a *mirror* of
PyCSL's own compiler under `src/self-annotate/src/`, in which each function is either machine-proved
or marked `#@ \trusted` (a counted trust assumption). The metric is the `\trusted` count, kept honest
by three disjoint oracle planes — fidelity (mirror bodies are verbatim the live bodies), whole-file
Why3 proof, and corpus byte-inertness — plus a fixed 3-axiom ledger.

## 2. The wall

`src/pycsl/frontend/Module5_IREmitter.py` translates the woven AST into IR through four
**table-driven dispatchers**. All four are still `\trusted`:

```python
def _py_op_to_str(self, op) -> str:
    return self._PY_OP_MAP.get(type(op), "?")                       # 2 live LOC

def _csl_to_ir(self, node: CSLNode) -> Dict[str, Any]:              # 6 live LOC
    handler_name = self._CSL_HANDLERS.get(type(node))
    if handler_name is None:
        raise PyCSLIRError(f"Unsupported CSL node: {type(node).__name__}", stage="ir-emit")
    return getattr(self, handler_name)(node)

def _py_expr_to_ir(self, expr: ast.expr) -> Dict[str, Any]:         # 6 live LOC
    handler_name = self._PY_EXPR_HANDLERS.get(type(expr))
    if handler_name is not None:
        return getattr(self, handler_name)(expr)
    return {"type": "UnknownPyExpr"}
```

Two features make these look unconvertible, and the backlog has filed them for months under
"`_csl_to_ir` getattr-dispatch — review-gated giant decomposition, net-marker-negative":

1. **`type(node)` used as a dict key** — runtime type reflection.
2. **`getattr(self, handler_name)(node)`** — a method selected by a *string computed at runtime*.

## 3. The deeper truth — both tables are compile-time constants

Measured at HEAD:

| table | entries | key kinds | value kinds |
|---|---|---|---|
| `_CSL_HANDLERS` | 79 | all `Name`/`Attribute` | all string constants |
| `_PY_OP_MAP` | 26 | all `Name`/`Attribute` | all string constants |
| `_PY_EXPR_HANDLERS` | 23 | all `Name`/`Attribute` | all string constants |
| `_PY_STMT_HANDLERS` | 16 | all `Name`/`Attribute` | all string constants |

Every table is a class-level literal `Dict[type, str]` with no runtime mutation. So the set of
reachable handler names is **finite and known to the emitter**, which means

```
handler_name = TABLE.get(type(x)); getattr(self, handler_name)(x)
```

is *semantically identical* to a finite case split

```
match kind_of x with "BinOp" -> self._csl_binop x | "Var" -> self._csl_var x | ... end
```

This is not a new modeling idea — it is the **banked ast-pyval-VIEW device** the raw-AST cascade
already uses: `isinstance(n, _ast.<Cls>)` lowers to a synthetic `_type` **tag test** on the opaque
pyval view and `n.<attr>` to `pget_dyn` (`module6_whyml/functions.py:4530`, the
`_extract_ast_subscript` recognizer, explicitly annotated *"Ledger 3 (reuses pyval)"*). A
`TABLE.get(type(x))` over a constant table is the same shape as a chain of those tag tests.

**Claim: this build needs NO new certificate and NO new axiom.** It is an emitter recognizer. That is
the report's central, falsifiable claim.

## 4. Why the payoff is better than the backlog assumed

The backlog files this as a "TCB-giant decomposition, net-marker-negative" — i.e. splitting a huge
function into pieces that each need their own marker. That is a mis-description. These are **2-to-6
live-line functions**. Nothing is being decomposed; a constant table is being expanded.

Additionally, of the 75 distinct handler methods `_CSL_HANDLERS` names, **74 are already un-trusted
and verified in the mirror** — only `_csl_in` remains `\trusted`. So the expanded branches call
methods that already carry real, proved contracts.

## 5. The one member that is genuinely different: `_csl_to_ir`

`_csl_to_ir` is currently `\trusted`, hence emitted as an abstract `val`. That is *exactly* what
lets those 74 verified handlers call back into it with **no termination obligation**. Converting it
makes all 75 methods **mutually recursive**, requiring a `#@ \variant` descending CSL-node structure
across the whole cluster. That is a real risk and it does **not** follow from the other three
converting. It gets its own spike.

## 6. Proposed order (increasing risk), and the make-or-break spike

**Spike (Gate S), the whole build is gated on it:** convert **`_py_op_to_str`** alone. It is the
cleanest possible isolation of the capability — 2 live LOC, a 26-entry table, returns a plain `str`,
**non-recursive**, no `getattr` at all (the table value IS the result, not a method name). If the
constant-table + `type()` tag-test lowering cannot carry *this*, it cannot carry anything, and the
whole lever is a CERTIFIED-BOUNDARY.

Then, only if the spike passes: `_py_expr_to_ir` (adds `getattr` method dispatch, 23-way, has a
total fallback) -> `_py_stmts_to_ir` (adds `getattr(stmt, 'csl_labels', [])` raw-AST attribute reads
with defaults, and list accumulation) -> `_csl_to_ir` (adds the 79-way split, a `raise` on the
None branch, and the mutual-recursion variant of §5).

Gate battery unchanged: fidelity no worse than the HEAD baseline (2 DIVERGED / 3 drifted mirrors),
whole-file proof of `Module5_IREmitter.py` at 0 non-Valid, corpus byte-diff 0, ledger 3,
non-vacuity (the emitted body must really tag-test and really call the handlers — a fallback-only
facade that always returns `"?"` or `{"type": "UnknownPyExpr"}` is REJECTED).

## 7. What would refute this report

1. `_py_op_to_str` is converted and the emitted WhyML is a **facade** — e.g. it collapses to the
   `"?"` default without ever tag-testing. Gate C rejects it; the lever dies.
2. The pyval VIEW cannot express `type(op)` for **operator** nodes specifically. The certified
   `pyast_stmt` ADT (`Phase2e_PyAstStmt.v`) covers *statements* only
   (`PSAssign|PSAnnAssign|PSClassDef|PSFunctionDef|PSPass|PSExprEllipsis|PSOther`) — there is no
   certified operator variant. My claim is that the VIEW device does not need one because it is a
   tag test on an opaque pyval, not a certified ADT match. **If that is wrong, this build needs a new
   certificate and the cost estimate is wrong.** This is the single most important thing to check.
3. Expanding a 79-entry table produces an emission that tips `Module5_IREmitter.py`'s whole-file
   proof into E-matching saturation. (Note: `#@ verify_module` is NOT the rescue — refuted decisively
   in a prior window; isolating a razor-edge goal made it worse.)
4. One of the four targets turns out not to be `\trusted` at HEAD. *(Pre-checked: all four are
   trusted with placeholder bodies. Re-check anyway — this is exactly how the last wall died.)*
5. The tables are not as constant as §3 claims — e.g. something mutates `_CSL_HANDLERS` at runtime,
   or a key is not a plain class reference. Then the finite case split is unfaithful.
