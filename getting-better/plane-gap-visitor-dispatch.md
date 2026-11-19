# Plane gap: visitor dispatch and `__init__`-built records in `check-assigns-underdeclaration`

Measured at `3964201f` (main HEAD). No mirror or emitter source was edited. The only changes
are to the plane, `bin/check-assigns-underdeclaration.py`.

## The gap

The driver measured that the `\trusted` stub `PyCSLToJSONEmitter.visit_Module`
(`src/self-annotate/src/frontend/Module5_IREmitter.py`) declares a frame that leaves out
fields written through `self.generic_visit(node)`: `visit_FunctionDef -> _build_function_ir`
writes `_cur_func_name`, and `visit_ClassDef -> _collect_class_fields` writes `_m5_dc_unknown`.
A verified probe caller then PROVED a field unchanged across the call, while CPython changes
it. No plane flagged this, for two reasons:

1. **Callees were resolved by name, within one class.** The transitive and declared-callee
   arms only followed `self.<m>()` edges inside one class. The following were all invisible:
   NodeVisitor dispatch (`self.visit` / `self.generic_visit` / `super().visit`), handler
   tables (`getattr(self, self._T.get(t))(...)` in `_csl_to_ir`, `_py_expr_to_ir`,
   `_py_stmts_to_ir`, `_expr_to_whyml`), and calls from one mixin to another (a
   `\trusted` stub in mixin A for a method that really lives in mixin B: in the live file
   that `(A, m)` has no body, so the old arm saw no writes at all).
2. **`declared` meant class-level only.** Module 5 builds the record of a non-dataclass from
   the `self.<f> [: T] = ...` targets in `__init__` (live `_collect_class_fields`; lesson
   (g5)(i)). So every HOLE arm missed the whole record of classes like PyCSLToJSONEmitter
   (`_final_registry`, `program_ir`, `_fresh_var_counter`, `_m5_dc_unknown`) and
   Module6_WhyMLTranspiler (`ir`, ...).

## The plane change

- `_class_declared_fields` now includes `__init__` `self.<f>` (Ann)Assign targets by default.
  The direct, transitive and declared-callee arms all use it.
- **HOLE-DI.** These are declared-callee (HOLE-D) rows whose field is declared only in
  `__init__`. They get their own frozen baseline (`HOLE_DI_BASELINE`, 4 rows).
  `MAX_HOLE_D` stays at 0.
- **The dispatch arm (HOLE-V)** (`dispatch_rows`) over-approximates on every axis. A row may
  be spurious, but no real row is missed:
  - **Receiver family.** Callees resolve to `up*(D)` for every `D` in `down*(C)`, matched by
    class name across the whole live tree, so `ast.NodeVisitor` resolves to pure_ast's
    NodeVisitor.
  - **Visitor dispatch.** `generic_visit` reaches every family `visit_*` except the `mod`
    roots (`visit_Module` and the like are never children), plus `generic_visit`/`visit`
    overrides. `visit` reaches every `visit_*`. The library NodeVisitor/NodeTransformer
    `visit`/`generic_visit`/`visit_Constant` are modelled by these rules, not by their bodies.
  - **`getattr(self, e)` called.** A constant `e` gives that method. A for-loop over
    constants gives each one. A constant-prefixed `+`/f-string gives every method with that
    prefix. A local read from a class-level str-valued dict table gives the table's values.
    An unknown table falls back to every family method. Anything else also gives every family
    method. A `getattr(self, name)` that is never called is a field read, not an edge.
  - **References.** Any `self.<m>` load that names a family method is an edge.
  - **Container writes.** `self.f.append/extend/insert/pop/remove/clear/add/discard/update/
    setdefault/popitem(..)` counts as a write of `f`.
  - **Population.** Every mirror def with `#@ assigns`, `\nothing` and non-self clauses
    included. `__init__` is excluded, because its `self` is fresh.
- The ratchet is `HOLE_V_BASELINE`, a frozen map from `(file, class, method, field)` to
  `trusted`/`verified`. Any row outside it is red. A baseline row that stops firing is printed
  so it can be removed, and the baseline only shrinks. HOLE-V is a new population behind its
  own ratchet. No existing ceiling was raised.
- `--self-test-dispatch` takes a clause that names a record field reached ONLY through
  dispatch, drops that field, and requires HOLE-V to fire.
- The battery invokes the plane with `--transitive`, and `main` runs the dispatch arm on
  every invocation, so the battery picks the arm up without any edit to
  `bin/run-soundness-planes.sh`.

## Counts, before and after

| arm | before (HEAD plane) | after |
|---|---|---|
| direct TRAP / HOLE | 3 / 0 | 3 / 0 |
| transitive TRAP-T / HOLE-T | 157 / 0 | 157 / 0 |
| declared-callee HOLE-D / TRAP-D | 0 / 112 | 0 / 108, plus **HOLE-DI 4** (own baseline) |
| dispatch TRAP-V / HOLE-V | (did not exist) | **1945 / 33** (30 `\trusted`, 3 verified), own baseline |
| plane rc: default, `--transitive`, 3 self-tests | 0 | 0 |

TRAP-V has 1788 rows (across 222 methods) that the old transitive arm did not report. Each row
can have more than one cause, so the cause counts add up to more than 1788:

| cause | rows |
|---|---|
| receiver family | 1445 |
| dispatch | 347 |
| container mutators | 274 |
| combined | 44 |
| references | 35 |

1071 of these rows are on `\nothing` or non-self clauses, which were out of the old arms'
population.

## Census: the 33 HOLE-V rows (field omitted from the clause AND in the record)

"Verified consumers" counts the mirror methods in the SAME file (the same WhyML module, so the
same stub) whose bodies call the method and are not `\trusted`. "Emitted" means checked in the
emitted `.mlw` of a scratch copy (`--no-proof --no-typecheck --keep-mlw`).

| # | file | method | frame | missing record fields | cause | verified consumers | probe |
|---|---|---|---|---|---|---|---|
| 1 | statements.py | `StatementEmissionMixin._handle_return_stmt` | `\trusted`; emitted `writes` omits `_abstract_ops` | `_abstract_ops`, `_dict_locals`, `_get_return_raw_option`, `_quant_record_binders`, `_quant_scalar_binders` | family (live body is `ControlFlowStmtMixin._handle_return_stmt`) | 1 (`_handle_critical_section_stmt`, ensures True) | **FALSE PROOF REPRODUCED** (below) |
| 2 | stmt_control_flow.py | `ControlFlowStmtMixin._expr_to_whyml` | `\trusted` stub for ExpressionEmissionMixin's method; emitted `writes` omits all 3 | `_dict_locals`, `_quant_record_binders`, `_quant_scalar_binders` | family (+mutcall) | 4 (`_handle_while_stmt`, `_handle_if_stmt`, `_handle_match_stmt`, `_handle_return_stmt`) | no CPython witness: 39 calls, 0 net changes. The writes are `_push_quant_binder`/`_pop_quant_binder` pairs, which restore on the normal path. |
| 3 | stmt_control_flow.py | `ControlFlowStmtMixin._match_pattern_cond` | `\trusted`, `\nothing`; emitted val has NO `writes` | 12: `_comp_content_counter`, `_current_params`, `_current_self_type`, `_dict_locals`, `_frame_trigger_active`, `_func_return_type`, `_in_spec`, `_needs_array_init`, `_quant_record_binders`, `_quant_scalar_binders`, `_string_local_vars`, `_todict_arg_wants_pymap` | family (`-> _expr_to_whyml -> ...`) | 1 (`_handle_match_stmt`) | no CPython witness: 5 calls on a match program plus corpus 0240/0520/0531, 0 net changes. Pattern values are literals and dotted names, so the reachable writers are not realised. |
| 4 | Module5_IREmitter.py | `PyCSLToJSONEmitter.visit_Module` | `\trusted`; emitted `writes {_final_registry, _fresh_var_counter, program_ir}` | `_m5_dc_unknown` (and `_cur_func_name` as soon as it is declared, see negative test A) | dispatch (`generic_visit -> visit_ClassDef -> _collect_class_fields`) | 0 | the driver's probe; the fix is pending in its stack |
| 5 | Module5_IREmitter.py | `PyCSLToJSONEmitter.visit_FunctionDef` | `\trusted` | `_m5_dc_unknown` | dispatch | 0 | none: no consumer |
| 6 | statements.py | `StatementEmissionMixin._track_collection_metadata` | `\trusted`, `\nothing` | `_known_collection_elements`, `_known_collection_sizes`, `_record_array_locals` | family + mutcall | 0 | none: no consumer |
| 7-11 | Module6_WhyMLTranspiler.py | `transpile`, `_transpile_modular`, `_emit_prefunctions_infra`, `_render_callee_condition`, `_wrap_call_with_callee_raises_assert` | `\trusted` | `ir` (a container mutation of the IR mapping by a mixin, e.g. `_handle_dotted_call`; already a known TRAP_BASELINE item) | family | 0 (only `\trusted` callers) | none: no consumer |
| 12-14 | Module5_IREmitter.py | `_py_stmt_match`, `_py_stmt_try`, `_py_stmt_with` | VERIFIED (`assigns ir_stmts`) | `_fresh_var_counter` | dispatch (`_py_stmts_to_ir` table) | n/a | none needed: Module 6 widens the emitted frame (`_py_stmt_with ... writes { self._fresh_var_counter, ir_stmts }`), so the source clause is audit debt, not a soundness gap |

Rows 1-11 make up the 30 `\trusted` rows (field occurrences) and rows 12-14 the 3 verified
ones. Earlier iterations of the arm reported `_final_registry` rows for `visit_ClassDef`/
`visit_FunctionDef`. Those were removed as spurious, because `visit_Module` is never reachable
from `generic_visit`.

### HOLE-DI (4 rows, all VERIFIED callers, all `_fresh_var_counter`)

`_py_stmt_match -> _py_stmts_to_ir`, `_py_stmt_try -> _py_stmts_to_ir`,
`_py_stmt_with -> _get_mutex_invariant_ir`, `_py_stmt_with -> _py_stmts_to_ir`. These are the
same mechanism as rows 12-14: Module 6 widens the emitted `writes`, so they are source-clause
audit debt.

## The reproduced false proof (row 1)

- **Probe.** In a scratch copy of the mirror, a VERIFIED method was added to
  `StatementEmissionMixin` (`module6_whyml/statements.py`) right after the `\trusted`
  `_handle_return_stmt` stub:
  ```
  #@ requires True
  #@ ensures self._abstract_ops == \old(self._abstract_ops)
  #@ assigns <the callee's own clause>
  def _pgap_probe_ret(self, stmt, rest, local_refs, declared_refs, indent, in_loop) -> str:
      return self._handle_return_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
  ```
  The emitted `let` carries `ensures { (self._abstract_ops = (old self._abstract_ops)) }`,
  and the callee `val` has `writes { ... }` without `_abstract_ops`.
- **Command.** `pycsl.py --fun statementemissionmixin___pgap_probe_ret --keep-mlw
  --import-path src/pycsl <scratch>/probe_ret/module6_whyml/statements.py` ->
  **rc=0, "Verification SUCCESS"**.
- **CPython counterexample.** `cpython_frame_witness.py _handle_return_stmt _abstract_ops
  prog_ret.py` wraps the LIVE method on the facade and runs the live pipeline on
  `def f(x: int) -> int: return x ** 3`. The single call ADDS `py_pow` to `_abstract_ops`
  (`'val function py_pow (x: int) (y: int) : int requires { ... y >= 0 }'`).
- **Repro files** (scratchpad `.../0119d6ca-.../scratchpad/pgap/`): `probe_ret/` (the scratch
  mirror holding the probe), `probe_ret.log`, `cpython_frame_witness.py`, `prog_ret.py`.

This is a different mechanism from `visit_Module`. The stub sits in one mixin while the live
body sits in another, so the old arm looked up `(StatementEmissionMixin,
_handle_return_stmt)` in live `statements.py`, found no body, and saw no writes. Receiver-family
resolution is what catches it.

## Negative tests

- `--self-test-dispatch` -> rc 0. It drops `_fresh_var_counter` from
  `PyCSLToJSONEmitter._csl_append`'s clause (reached only through the `_CSL_HANDLERS` table),
  and HOLE-V fires.
- **A, scratch copy** (`scratchpad/pgap/negroot`): add
  `self._cur_func_name: str = ""` to the mirror `PyCSLToJSONEmitter.__init__`, which is the
  driver's scenario.
  - HEAD plane `--transitive`: rc 0, green.
  - New plane: rc 1, `HOLE-V 1 NEW row: visit_Module self._cur_func_name trusted dispatch`.
- **B, scratch copy**: drop `self._fresh_var_counter` from `visit_Module`'s clause.
  - HEAD plane: rc 0, green.
  - New plane: rc 1, `HOLE-T 1: visit_Module self._fresh_var_counter`. The transitive arm now
    sees the `__init__`-declared field.

## Known limits (the over-approximation is not total)

- Consumers are counted in the same mirror file only. Cross-module consumers of an imported
  boundary `val` were not enumerated.
- Container writes are recognised by method name on `self.f` only. Aliasing such as
  `x = self.f; x.append(...)` is not tracked, and neither is a callee mutating `self.f` passed
  as an argument. These are the same blind spots as the old arms.
- Nested functions and lambdas inside a method are walked as part of the method, which is
  sound.
