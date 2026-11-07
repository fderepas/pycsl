# tree-walk-wall.md — the generic recursive `for v in node.values()` IR-tree existence-walk

**For review. State-of-the-art report on the highest-count wall on the self-tcb-reduction frontier.**

## 1. Global picture
PyCSL lowers annotated Python to WhyML, discharged by Why3/SMT. The self-annotation effort mirrors the live
emitter into `src/self-annotate/src/` and drives its `#@ \trusted` stub count DOWN by converting each stub to
a verified body under a fixed type-safety+frame contract, gated by three disjoint oracle planes (fidelity,
whole-file Why3 proof, corpus byte-diff-0). Count is **1027**; ledger is **3 axioms** (must stay 3). The
reachable-with-existing-machinery frontier is exhausted; every residual is an authorize-first build.

## 2. The wall — first seen
`core_ir_semantic.py` holds **7+ trusted bool-predicate stubs** that share ONE shape: a recursive walk over an
UNTYPED `Dict[str,Any]` IR tree that returns "does any node, at any depth, have `stmt`/`type` == K":
```python
def _body_has_raise(body) -> bool:
    found = [False]
    def walk(node):
        if found[0]: return
        if isinstance(node, dict):
            if node.get("stmt") == "Raise": found[0] = True; return
            for v in node.values(): walk(v)        # <-- the generic children recursion
        elif isinstance(node, list):
            for x in node: walk(x)
    walk(body); return found[0]
```
(also `_contains_result` [type=="Result"], `_body_has_return`, `_body_has_diverging_construct`
[stmt∈{While,For,CriticalSection} or type=="Call"], `_lemma_returns_value`, `_lemma_calls_trusted`, and
`_union_c8_test_references_union_var`). The load-bearing operation is **`for v in node.values()`** — iterate
ALL children of a node WITHOUT knowing its type — plus **unbounded-depth recursion** and a node **discriminant**.

## 3. The deeper truth — modeling choice, NOT a fundamental limit
The walked tree IS a typed value: it is the mutual **`stmt_ir`** (statements) + **`emit_ir`** (expressions) IR-node
ADT the emitter already builds and that is **already certified** (`Phase2d_StmtIR.v`/`.lean` with the mutual
`size_stmt`/`size_slist` measure; `Phase2c_PyConstVal.v` + the `emit_ir` `size`). So the tree, its node
discriminants (`stmt_kind_of`/`kind_of`), and a well-founded size measure ALL EXIST. What is missing is:
1. **A generic children-enumerator** `ir_children : node → list node` — the WhyML image of `node.values()`, a
   per-constructor match returning that node's sub-nodes (stmt sub-statements AND emit_ir expr children).
2. **A recursive existence-fold** `tree_has : (node → bool) → node → bool` (∨ over the node's children),
   terminating on the certified size measure (`variant { size node }`).
3. **Param retype**: the walker's untyped `body`/`node` param typed as the IR ADT (as the giants work retyped
   `node: ast.ClassDef` → `pyast_stmt`, commit ce71e3ab).
Then `for v in node.values()` → `ir_children`, `node.get("stmt")=="Raise"` → `stmt_kind_of node = "Raise"`,
the recursion → `tree_has`. Faithful, and the discriminant + size are reused from the certified ADTs.

## 4. SOTA lens
This is the **certified generic IR-tree fold** — the class the `_field_type_of` wall (skill §9) and the
`ast.walk` scoping (`ast-modeling-scope.md` §2/§5) circle. The precedent: the emitter already lowers
per-node-typed reads (`is_var`/`name_of`/psl-loop over `class_body_ast`). The NEW capability is generic
**depth-recursive** traversal with a **∨-existence** accumulator — not a bounded `for child in <psl>` loop
(commit ce71e3ab) but an unbounded descent. The mutual stmt_ir/emit_ir size measure (Phase2d) is exactly the
termination witness such a fold needs.

## 5. Honestly-costed routes
- **R1 (make-or-break, recommended): a `tree_has_kind : string → <ir> → bool` recursive existence-fold** over
  the certified stmt_ir/emit_ir mutual tree, with `variant { size }`, + an `ir_children` enumerator, + retype
  `_body_has_raise`'s `body` param to the IR ADT. Convert `_body_has_raise` (the SIMPLEST — a single
  `stmt_kind_of == "Raise"` predicate, bool result, no value extraction) end-to-end. This is the spike-checkable
  make-or-break: does a recursive ∨-fold over the mutual IR tree discharge its `variant`/`ensures True` and
  prove non-vacuously (an evil-twin tree WITHOUT a Raise must not satisfy it)?
- **R2 (cheap follow-ons, if R1 lands):** `_body_has_return`, `_body_has_diverging_construct`, `_contains_result`,
  `_lemma_returns_value`, `_lemma_calls_trusted` — the SAME fold parameterized by a different discriminant
  predicate (`stmt_kind_of ∈ {…}` / `kind_of == "Call"` / a value-carrying check). One fold, ~6 conversions.
- **Deferred:** value-EXTRACTING walks (`_lemma_returns_value` reads the Return's value; `_union_c8_test_
  references_union_var` compares names) may need a sub-node read on top of the existence-fold — assess per stub.

## 6. Honest limits + certificate
The `ir_children` enumerator + the recursive fold are a NEW WhyML shape's OPERATIONS over the EXISTING certified
ADTs — so the Phase2d/2c size/measure certificate likely EXTENDS (a `tree_has`-terminates + `ir_children`-size-
decreases lemma) rather than a wholly new Phase; verify it stays axiom-free (ledger 3). The hard part is the
mutual stmt_ir↔emit_ir descent's termination at full theory scale (the §5 E-matching-explosion risk the
`irlist`/`stmt_list` bespoke-cons work already navigated). This is a deliberate multi-piece build, but its yield
(~6 stubs from one fold) is the highest on the frontier.

## 7. The make-or-break question for review
Is a **recursive ∨-existence-fold `tree_has_kind` over the mutual certified stmt_ir/emit_ir tree, terminating on
the Phase2d `size` measure**, achievable as an axiom-free, byte-diff-0-gated increment that converts
`_body_has_raise` non-vacuously? Or does the mutual-recursion descent (a) fail to discharge its `variant` at full
theory scale, or (b) force a new axiom, or (c) hit a Why3 positivity/type wall on the `ir_children` enumerator?
An oracle run — a hand `.mlw` with a small mutual `stmt_ir`/`emit_ir`, an `ir_children`, a `tree_has_kind` with
`variant { size }`, and a driver proving `tree_has_kind "Raise" <tree-with-raise> = true` ∧ evil-twin
`<tree-without-raise> = false` — should CONFIRM or REFUTE before any emitter edit.
