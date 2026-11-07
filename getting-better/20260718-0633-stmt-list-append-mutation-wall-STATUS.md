# STATUS: list-append-mutation wall BROKEN + stmt family harvested (+14 this run)

The wall from `20260718-0633-stmt-list-append-mutation-wall.md` is **broken and built** (fable-adjudicated
BREAKABLE → spike → family build). Run 1075→1061 (−14) on branch ghost-assign-bc6, HEAD `d866a1b9`, ledger 3
(allowlist untouched, certs Phase2c/2d axiom-free), corpus byte-diff 0 throughout, suite validated by
DECOMPOSITION (the monolith wedges on stmt_control_flow under load — use per-file M5 proof + `_uses_stmt_ir`
inertness + observational fixtures 0893-0899, NOT the monolith).

## Capabilities built (reusable)
1. **Mutable-ref append convention** (`ref (seq stmt_ir)` + real `writes{ir_stmts}`) — the wall-break; `_uses_stmt_ir`-gated M5-only.
2. **Mutual-cons `stmt_list` ADT** (`SLNil|SLCons`) for recursive sub-bodies (Why3 rejects `seq stmt_ir` by positivity; `list` explodes size lemmas) + `seq_to_sl` materialization + bridge lemma; the `seq_to_sl` bridge proves via Alt-Ergo where Z3 explodes (best-of-N essential).
3. **build-up-dict** + **build-up-then-append** recognizers (local dict, conditional field, return/append).
4. **str-Constant recognizer** (`isinstance(v,Constant)&isinstance(v.value,str)`→`is_str`) + **option-field infra**.
5. **output-side slice-discrimination** (`_py_expr_to_ir(slice).get("type")=="Slice"` — the sound rewrite of the unmodelable input `isinstance(slice,ast.Slice)`; the ir_resolve.py:468-480 "gap" comment was STALE — `_is_emit_ir_val` already recognized recursive `_py_expr_to_ir(...)` calls).
6. **pyconst_val value-variant** (B bucket, feeds the constant leaves).

## CONVERTED (14): _py_stmt_pass/break/continue/return/while/if/for + _process_while/_process_if/_process_for + _py_stmt_annassign/expr/assert + _py_expr_subscript. stmt_ir ctors: SPass/SBreak/SContinue/SReturn(iropt)/SExpr/SAssign/SAssert + SWhile/SIf/SFor(recursive stmt_list).

## REMAINING stmt handlers — DEEP INTERDEPENDENT FRONTIER (each needs MULTIPLE builds; none sufficient alone). NOT cheap; a deliberate multi-build campaign (authorize-first).
- **`_py_stmt_augassign`** — DONE (commit 0c75dc40, 1061→1060): built `str_eq_op`(==self), SAugAssign/SFieldAugAssign/SArraySet ctors, `avalue_of` unified projector, output-side subscript rewrite. These are REUSABLE for assign below.
- **`_py_stmt_assign`** — now needs ONLY: SFieldAssign ctor (trivial, SFieldAugAssign clone) + `stmt.targets[0]` AST-list-HEAD access + **ast-list-walker** (Tuple `.elts` comprehension) + **symtab-membership** (`target.value.id in self._cur_func_symtab` — instance-state dict `in`) + **`raise PyCSLSemanticError`** (exception construction). str_eq_op/SArraySet now done. Still 3 distinct walls (list-head, ast-list-walker, symtab, raise).
- **`_py_stmt_delete`** — **ast-list-walker** (`for tgt in stmt.targets`) + getattr-heterogeneous-target + append-in-loop.
- **`_py_stmt_try`** — SExceptHandler ADT + loop-building-record-list + **ast-list-walker** (`h.type.elts` isinstance-filter + join).
- **`_py_stmt_with`** — WEAVE-INJECTED attrs (`csl_critical_mutex`, not in pure_ast `_NODE_SPEC`) + `_get_mutex_invariant_ir` stateful dep + `Seq.(++)` concat (extend) + SCriticalSection. Lowest priority (weave-attr boundary).
- **`_py_stmt_match`** — match-pattern ADT (big).
- **`_py_stmts_to_ir`** (dispatcher) + **`_py_op_to_str`** — `type()`-keyed dispatch (bucket-F).
- **`_emit_ghost_assign`** — CSL dataclass union, returns dict (not the append family).

## Two recurring leave-trusted-class walls gating most of the above:
- (i) **ast-list-walker**: `for x in node.elts/handlers/targets` + isinstance-filter over raw AST node-lists (blocks assign-Tuple, try, delete). Census bucket E — "not model-addressable without a live rewrite"; would need a fable review to confirm breakable (like the append wall was).
- (ii) **type()-keyed dispatch** (`_py_op_to_str`, `_py_stmts_to_ir`): bucket F.

## Next-run recommendation: build **augassign** (bounded, string-eq+SArraySet+synthetic-BinOp — also unlocks assign's self-FieldAssign + Subscript branches), THEN escalate the **ast-list-walker** wall via the fable cycle (report→review→build) — if breakable it unlocks assign-Tuple + try + delete. See [[stmt_append_wall_breakable]], [[frontier_exhaustion_map]].
