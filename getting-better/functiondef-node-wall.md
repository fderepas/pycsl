# Wall: FunctionDef-node methods vacuously erase (need `py_functiondef_node` typed model)

**Status:** OPEN (Phase-2 wall, driver-detected 2026-08-17). Spike-gated.

## The wall
7 `\trusted` Module5 mirror stubs take an `ast.FunctionDef` param:
`_should_skip_method`, `_build_function_symbol_table`, `_build_function_ir`, `visit_FunctionDef`,
`_is_overload_stub`, `_synthesize_overload_guard`, `_build_overload_param_guard`.

When ported verbatim, the emitter lowers `node: ast.FunctionDef` to `node: int` (generic erasure —
no typed FunctionDef model) and every guard to an UNINTERPRETED `val` stub that DOES NOT TAKE THE
NODE: `val node_name_startswith_1 (x0:int):int` (only the `'__'` hash), `val get_decorator_list
(x:int):int`, `isinstance(stmt, ast.Pass)` -> `isinstance_op 0 0` (a CONSTANT). Result: the body
reads only arbitrary stubs => `ensures True` holds for ANY body => **Gate-C non-vacuity VIOLATION
(facade)**. `_should_skip_method` PROVED this way and was REVERTED (aeaa6f0d -> 5584b5dd).

## The fix (proposed)
A `py_functiondef_node` opaque-but-typed model PARALLEL to the working `py_classdef_node`
(`preamble.py:6235` `val function class_bases_ast (n: py_classdef_node): irlist` +
`class_body_ast: psl` — these TAKE the node and return structured types really iterated, so
`_is_namedtuple_class`/`_is_protocol_class` convert NON-vacuously).

Needs NEW accessors (py_classdef_node has no name accessor):
- `val function func_name_ast (n: py_functiondef_node) : string`  (node.name)
- `val function func_decorator_list_ast (n: py_functiondef_node) : irlist`  (node.decorator_list)
- `val function func_body_ast (n: py_functiondef_node) : psl`  (node.body)
- param-typing recognizer: type a `_m5` method's `node: ast.FunctionDef` param as
  `py_functiondef_node` (parallel to the tag-driven `for x in param.body` typing at
  preamble.py:6658-6686 which handles ClassDef/Module).
- string ops on `func_name_ast node`: `node.name.startswith('__')`/`endswith('__')` ->
  `str_startswith (func_name_ast node) "__"` etc. (CHECK the faithful string-op vocabulary exists).

Non-vacuity requirement: every guard accessor MUST take the node (`func_name_ast node`, not a
node-free literal stub). Confirm by emitting the `.mlw` and grepping that the guards are
`let function`/`val function` applied to `node`.

## Payoff
Up to 7 stubs; tractable first cluster = `_should_skip_method`, `_is_overload_stub`,
`_build_overload_param_guard`, `_synthesize_overload_guard`. `_build_function_ir`/
`_build_function_symbol_table`/`visit_FunctionDef` are large/stateful (later).

## Make-or-break spike (Gate S)
Build the minimal `py_functiondef_node` + the 3 accessors + the param-typing recognizer, port
`_should_skip_method` with REAL node-taking accessors, emit, GREP-confirm the guards take `node`
(non-vacuous), typecheck. PASS -> whole-file prove + build the cluster. REFUTE (string ops missing /
param-typing infeasible / erases anyway) -> CERTIFIED-BOUNDARY.

## Risk
Touches shared `preamble.py` theory => ripples all changed-emission giants (must re-prove) + the
byte-diff must stay 0 (gate the new theory on a `_uses_py_functiondef_node()` sentinel so it emits
ONLY where a FunctionDef-node method is present — the corpus stays inert).

---
## RESOLVED: BROKEN (2026-08-17, commit 9ad91d65, 711->710)
Spike PASSED, build landed. `py_functiondef_node` + func_name_ast/func_decorator_list_ast/
decorator_has_name + m5_current_class_present, gated on `_uses_py_functiondef_node`. `_should_skip_method`
CONVERTED non-vacuously (guards take node). 4/4 changed-emission mirrors whole-file SUCCESS, corpus
byte-diff 0, ledger 3. BANKED MODEL for the cluster follow-ons. NOTE `m5_current_class_present` is a
nullary opaque state-reader (sound, symtab_mem precedent) — a fidelity refinement (thread self) is
possible but not a blocker; the substantive dunder+@property guards are faithful/node-taking.

FOLLOW-ONS (need INCREMENTAL model extension, NOT free): `_is_overload_stub` needs `func_body_ast: psl`
+ stmt-kind discrimination (ast.Pass / Expr+Constant+Ellipsis over node.body[0]); `_build_overload_param_guard`
/`_synthesize_overload_guard` need param/args accessors. Each is a mini-build with its own non-vacuity check
(emit + grep the guards take the node) — measure-first, do NOT assume cheap.

## FOLLOW-ON _is_overload_stub: TRACTABLE but CERTIFICATE-FLAGGED (2026-08-17)
Spike PASSED technically (non-vacuous body: `decorator_has_name_or_attr_prog "overload" (func_decorator_list_ast node)`
+ `m5sl_nth 0 (func_body_ast node)` discrimination, L3-tc ✓, byte-inert). BUT it introduced a BESPOKE
`m5_body_stmt = M5Pass|M5ExprEllipsis|M5OtherStmt` variant ADT with NO src/formal-semantics certificate.
COUPLING-RULE VIOLATION (§10.5): the parallel `pyast_stmt` stmt ADT carries Phase2e_PyAstStmt.v/.lean
(axiom-free, Print-Assumptions-audited). `pyast_stmt`'s existing kinds (PSAssign/PSAnnAssign/PSClassDef/
PSFunctionDef/PSOther) CANNOT discriminate Pass vs Expr-Ellipsis (both -> PSOther), so reuse doesn't work
without extension. => REVERTED (back to 710). _is_overload_stub needs a DELIBERATE CERTIFIED build:
either (a) extend pyast_stmt + Phase2e with PSPass/PSExprEllipsis (reuses cert framework, ripples all
_uses_pyast_stmt giants), or (b) bespoke m5_body_stmt + a NEW Phase2-style certificate + Print-Assumptions
audit + §10.9 adversarial review. FLAGGED risky brick (trust-base change) — not an autonomous auto-land.
