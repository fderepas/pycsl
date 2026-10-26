# OPEN ROUTE #401 — A `\trusted` STUB'S `assigns \nothing` OVER A BODY THAT MUTATES ITS PARAMETER IN PLACE
**Status: OPEN, Severity 2 (TCB honesty; no exploited user-level false proof yet).** Found 2026-10-26 by executor e2 (run #3, side note), confirmed by the driver on main fbc034fee.

The mirror stub `src/self-annotate/src/frontend/pure_ast.py` `NodeTransformer.generic_visit` is `#@ \trusted` with
`#@ assigns \nothing`. Its live body (`src/pycsl/frontend/pure_ast.py`, class `NodeTransformer`) rewrites `node` IN PLACE:
`old_value[:] = new_values`, `delattr(node, field)`, `setattr(node, field, new_node)`. A trusted stub's declared frame is the
caller-side assumption verbatim (lesson g5), so every caller assumes the AST it passed is unchanged. Verified callers that
inherit the false frame: `frontend/desugar.py::desugar_chained_comparisons` and `frontend/exec_splice.py::splice_constant_exec`
(both `#@ assigns \nothing`, body `return _X().visit(tree)`).

Why no plane caught it: `bin/check-trusted-frame-honesty.py` compares a stub's frame with SELF writes in the live body; a write
through a PARAMETER (subscript-slice store, `setattr` / `delattr` on an argument) is outside its population (lesson u6: perturb
a member outside every "all N" population).

Repair: widen the frame-honesty plane to parameter writes (slice / item / attribute store, setattr / delattr, mutating method
calls on a parameter), census the population, then make each frame honest (declare the write; `assigns` on the parameter's
model) or record each as a ledgered deficit. Re-prove the mirror files whose emission moves.
