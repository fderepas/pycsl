# Wall: filtered-map comprehension over an AST-node-list (gates assign-Tuple / try / delete)

**Status:** state-of-the-art wall statement (U). Awaiting an INDEPENDENT fable review with an oracle artifact.
**Base loop:** self-tcb-reduction of the PyCSL self-annotation mirror (`src/self-annotate/src/`), branch ghost-assign-bc6, HEAD d0aa378e, count 1060, ledger 3.
**Author:** driver (may be tainted — the fable reviewer must independently CONFIRM/REFUTE from the repo + oracle, NOT from this prose).

## 1. The stubs this wall gates (partial — each also needs OTHER builds)
Three trusted M5 handlers iterate a Python-AST **node-list field** with an isinstance-filter + string projection:
- `_py_stmt_assign` (Tuple branch, live :1323): `targets = [elt.id for elt in target.elts if isinstance(elt, ast.Name)]` → a **list of strings**, then `{"stmt":"TupleUnpack","targets":targets,...}`.
- `_py_stmt_try` (live :1397-1403): `for h in stmt.handlers: ... "|".join(n.id for n in h.type.elts if isinstance(n, ast.Name))` → per-handler a **joined string**.
- `_py_stmt_delete` (live :1440): `for tgt in stmt.targets: getattr(tgt,'slice',...) + isinstance(...)` → appends per target.
(NOTE: none of the three FULLY converts on this wall alone — assign also needs targets[0]-list-head + symtab-membership + `raise`; try also needs a SExceptHandler ADT + a list-of-records build; delete also needs the loop-append. This wall is a NECESSARY, not sufficient, enabler. Adjudicate the wall on its own terms.)

## 2. The claim to adjudicate (CONFIRM or REFUTE with an oracle artifact)
**CLAIM A (the shape):** the core is `[x.<strfield> for x in <ast_node_list_field> if isinstance(x, ast.Name)]` — a FILTERED MAP over a harvested AST-node-list field (e.g. `ast.Tuple.elts`, `ast.ExceptHandler` tuple `.elts`), projecting a string off the Name-typed elements, collecting a `seq string` (or `String.concat "|"` of it).

**CLAIM B (why it is hard today):** the structural/pure_ast mode harvests each AST node as an OPAQUE record; a `.elts` field is a list of HETEROGENEOUS nodes (Name/Starred/Attribute/…), and `isinstance(x, ast.Name)` on a list element has no discriminant (the census bucket-E "generic AST-node-list walker" boundary). The existing content-law comprehension (`list_content_comp_N`, expressions.py ~6372, FABLE-sanctioned) handles `[dispatch(e) for e in elts]` (a MAP producing `emit_ir`, no filter, uniform dispatcher) — but NOT a filter + a string projection off a per-element discriminant.

## 3. The question for fable (Gate R)
1. **CONFIRM or REFUTE** that this filtered-map-to-string-seq is NOT expressible with current machinery — with an INDEPENDENT oracle artifact (write a tiny `.mlw` modeling `[x.id for x in elts if is_var x]` over a `seq emit_ir` producing a `seq string`, run `why3 prove`; or emit a 2-line PyCSL program with such a comprehension and grep the generated WhyML for `isinstance_op`/failure). State exactly where it breaks.
2. **Is this a CERTIFIED-BOUNDARY or a BREAKABLE wall?** Specifically: can the content-law comprehension be EXTENDED to a *filtered* map with a per-element discriminant (`is_var`) + a string projection (`name_of`), producing a `seq string` with a sound content law (length + per-index value), WITHOUT (a) a new axiom, (b) perturbing the corpus byte-diff, (c) the heterogeneous-`.elts` element type defeating the model? Consider: is a `seq emit_ir` element list with `is_var`/`name_of` projections enough, or does the filter (dropping non-Name elements) make the output length data-dependent in a way the abstract content-law op cannot pin non-vacuously?
3. If BREAKABLE: sketch the make-or-break SPIKE (one comprehension, e.g. assign-Tuple's `targets`, lowered to a real `seq string` with a NON-VACUOUS content law — a driver that observes a specific element's projected string, plus an evil-twin that must stay unproven).

## 4. Constraints the fix must honor (base-loop L)
Fixed contract shape (`requires True/ensures True/assigns <frame>`); 3-axiom ledger (`proof_axiom_allowlist.py`) unchanged; any new value shape co-lands an AXIOM-FREE `src/formal-semantics/` certificate (the `Phase2c/2d` precedent); corpus byte-diff 0; non-vacuity via an OBSERVATIONAL driver (`--check-vacuity` is INSUFFICIENT here — see the append wall's finding). The content-law comprehension precedent (`list_content_comp_N`, both-conjuncts length+per-index law) is the model to extend, if breakable.
