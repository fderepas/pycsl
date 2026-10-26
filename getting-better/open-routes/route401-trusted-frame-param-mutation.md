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

## 2026-10-26 — executor f401: PLANE WIDENED, 61 + 7 FRAMES REPAIRED, RESIDUE LEDGERED (route stays OPEN on the model half)

**The arm.** `bin/check-trusted-frame-honesty.py` gained a PARAMETER-WRITE arm with its own ratchets (no existing
arm touched). Closure: `bin/lib_param_write_closure.py` (flow-sensitive aliases; calls resolved per receiver-class
context, incl. the `getattr(self, 'visit_' + ..., self.generic_visit)` dispatch idiom). Sentinel: the arm REFUSES if it
stops seeing `NodeTransformer.generic_visit` write `node`; population floor 1200 (measured 411 trusted + 904 converted).

**Census at dd8e572ad:** 70 of 411 `\trusted` stubs and 19 of 904 converted methods declare a frame omitting a
parameter their live body writes. **After:** trusted 9, converted 13 (ratchets `PARAM_TRUSTED_RATCHET = 9`,
`PARAM_CONVERTED_RATCHET = 13`), every residual pair NAMED in `KNOWN_PARAM_FRAME_DEFICITS` /
`KNOWN_CONVERTED_PARAM_FRAME_DEFICITS`:
- `NodeVisitor.visit` (`node`): `assigns node` makes it a receiver-writer for route #280's fixpoint, which refuses the
  converted `_Unparser.traverse` (`super().visit(node)`) and pure_ast stops emitting. That refusal is RIGHT — see the
  NEW FINDING below.
- the `local_refs` / `declared_refs` set parameters of the statement handlers (8 trusted, 13 converted): sets lower
  BY VALUE (`map int (option int)`); naming them trips PYCSL-METHOD-ARG-UNFRAMED (route #316) / the route #62 refusal.

**How `#@ assigns <param>` lowers (emit-and-grep):** `writes { p }` ONLY for a list parameter (emitted `array`). For an
AST-node / record / object parameter (an `int` handle whose field reads are `val function pycsl_getattr_*`, PURE in
the handle) and for set/dict parameters, the clause is SOURCE-HONEST AND MODEL-INERT: no `writes`, and a caller can still
prove a field of the argument unchanged. Counted by the third ratchet `PARAM_NOT_LOWERED_RATCHET = 86` (trusted 69,
converted 17). MISSING CAPABILITY (why the route stays open): a by-reference lowering for object handles (field-read
functions that depend on a heap the `writes` can name) and for set/dict parameters.

**Repairs.** 61 trusted stubs + 7 converted methods (`desugar_chained_comparisons`, `splice_constant_exec` (`tree`),
`_process_sertop_line` (`payloads_by_tag`), `_py_stmt_while/_for/_if` (`ir_stmts`), `_handle_match_stmt` (`stmt`))
now declare the honest parameter frame; bodies untouched (fidelity green). 12 of them lower (list params) and move 9 mirrors
(`writes { args | out | functions | funcs | pre | counter | tokens }`), all type-checking; the rest are byte-inert.

**NEW FINDING (self arm blind spot, not repaired here):** converted `_Unparser.traverse` declares `assigns \nothing`
and calls `super().visit(node)`, which dispatches back into `_Unparser.visit_*` and writes `self._source`. The SELF arm
cannot see it (the dispatch is a call through a local name, not `self.<m>()`), and `NodeVisitor.visit`'s own
`assigns \nothing` is false w.r.t. `self` under an `_Unparser` receiver. No current proof exploits it (`ensures True`),
but `_Unparser.visit`'s model believes `traverse` leaves `_source` empty.

**Gates (f401, commit a0e9f1734 + this note):** fidelity sync rc 0 (928 verbatim) / mirror-check rc 0 (53);
corpus byte-diff vs base worktree at dd8e572ad: root 2424/2424 0 MOVED/GONE/APPEARED rc 0, pyref 2186/2186 rc 0
(no `src/pycsl` change); mirror-emit-sweep 53/53, 9 MOVED (exactly the `writes { <list param> }` additions), all 9
`--no-proof` type-check; run-soundness-planes fast 61/61 rc 0; check-trusted-frame-honesty rc 0 (existing arms
unchanged 0/1, 0/93); `\trusted` lines 446 = base. Negative test: reverting `NodeTransformer.generic_visit` to
`assigns \nothing` makes the arm fail (UNNAMED offender, ratchet 10 > 9).
Whole-file proofs of MOVED mirrors, 0 non-Valid each: abstract_ops (20 goals), sertop (21), canonical (49),
ir_inline (367), preamble (222), Module3_Weaver (288), pycsl.py (743), Module6_WhyMLTranspiler (1764).
