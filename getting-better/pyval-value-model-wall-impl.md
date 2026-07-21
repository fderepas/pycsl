# pyval-value-model-wall-impl.md — implementation plan (spike PASSED; emission-refutation exit)

Synthesized from `pyval-value-model-wall.md` + `pyval-value-model-wall-response.md` (Gate R **CONFIRM**, one
refinement). The make-or-break MODELING spike is already PROVEN by the fable oracle
(`getting-better/pyval-oracle.mlw`, Z3 Valid, axiom-free). The impl make-or-break is now **EMISSION**: can the
tool emit that exact certified theory + a faithful dict build/read, gated + byte-inert?

## The CERTIFIED shape (emit EXACTLY this — from the proven oracle)
```
type pyval = PStr string | PInt int | PArr pyval_list | PMap (map string (option pyval)) | PNode pyval
with pyval_list = PNil | PCons pyval pyval_list
```
- **`PArr` MUST use bespoke `pyval_list` (PNil/PCons), NOT `seq pyval`** (Why3 rejects `seq` recursion as
  non-strictly-positive — the hard refinement). `PMap (map string (option pyval))` is ACCEPTED (positive codomain).
- **Structural mutual recursion, NO `variant` clause** (the `irlist`/`stmt_list` fold shape — Why3 emits no
  termination VC). `get = Map.get`. Reads are key-projection (no fold into map values needed for the frontier).
- **Node arm:** the oracle proved `PNode pyval`; if unifying with the certified `emit_ir` ADT reintroduces a
  positivity issue, KEEP `PNode pyval` (proven). Decide by typecheck.
- Axiom-free; the `size v >= 1` lemma needs a 3-line mutual-induction side-car (Coq+Lean) — but NO fold in the
  frontier requires `size`, so `size`+its lemma are cert-only (not emitted into VCs).

## Gate S — EMISSION make-or-break (re-confirm oracle, then first emit). Refutation exit.
1. Driver re-proves the oracle (`why3 prove -P z3 getting-better/pyval-oracle.mlw`) — must reproduce Valid + axiom-free.
2. Emit the `pyval` theory into `preamble.py` (gated on a NEW `_uses_pyval` signal) + a reference fixture that
   builds+reads a heterogeneous dict; `pycsl <fixture> --keep-mlw`; confirm the emitted theory TYPECHECKS.
   - PASS → build I1 fully.
   - REFUTE (the tool can't emit the strictly-positive bespoke variant, or the fixture won't typecheck/prove,
     or `_uses_pyval` can't gate byte-inertly) → CERTIFIED-BOUNDARY: the model is Why3-viable but EMISSION-walled.
     Record + stop; do NOT grind.

## Build increments (each driver-verified; COUPLING RULE §5: cert co-lands with the capability)
- **I1 — infra + cert + fixture (NO mirror conversion yet):**
  (a) `preamble.py::_emit_pyval_theory` gated on `_uses_pyval` — emits the certified variant (constructive).
  (b) dict-literal emitter: `{k: v}` where the values are heterogeneous → `map string (option pyval)` via
      `Map.set` chains, per-value tag (str-lit/str-var→`PStr`, int→`PInt`, list→`PArr` cons, nested-dict→`PMap`,
      IR-node→`PNode`). Gated on `_uses_pyval`.
  (c) typed readers: `d[k]` → `Map.get d k` projecting the arm.
  (d) **`src/formal-semantics/rocq/Phase2f_PyVal.v` + `lean/Phase2f_PyVal.lean`** — the variant + `size` +
      `size_pos` (3-line mutual induction), AXIOM-FREE (`Print Assumptions`/`#print axioms` = clean; ledger 3).
  (e) reference fixture `test-suite/corpus/pycsl-reference/09xx_pyval_heterogeneous_dict.mlw` (git add -f) that
      builds `{"pattern":lit,"ctor":var,"captures":[...]}` + reads each faithfully (non-vacuous; evil-twin).
  Gate: fixture PROVES; byte-diff-0 (gated on `_uses_pyval` ⇒ corpus-inert — the 767 baseline unchanged); ledger 3.
- **I2 — the make-or-break CONVERSION:** convert `_render_match_pattern` (mirror `stmt_control_flow.py`) — the
  simplest heterogeneous-dict build+read — to a verified body via the pyval model. Gate: whole-file proof
  SUCCESS (foreground), fidelity (mirror==live verbatim), count strictly down, MUTATION TEST (change a dict
  value tag → emitted .mlw changes), byte-diff-0.
- **I3+ cascade (follow-on):** the Dict-of-Dict collectors (`_collect_typevar_registry`/`_collect_type_params`/
  `_collect_class_fields`), then the giants (`_emit_ir_args_recv_ir` → `_is_emit_ir_expr`), then the 2
  faithfulness bugs (Bug 1 dict-literal already fixed; Bug 2 negative-slice). Each its own gated increment.

## Gate battery (per increment — driver-verifier FRESH)
Fidelity ∧ whole-file Why3 proof SUCCESS ∧ byte-diff-0 (gated on `_uses_pyval`; or M1 sanctioned-reset+reprove)
∧ ledger==3 (`Print Assumptions`/`#print axioms` on Phase2f) ∧ count strictly down ∧ non-vacuity (MUTATION TEST;
real pyval constructors, no int-hash/int-erasure). The cert co-lands in the SAME commit as the capability (§5).

## GATE-S OUTCOME — EMISSION **PASS** (2026-07-20); I1 LANDED

Gate S re-proved the oracle (Z3: 4 faithful reads Valid, evil twin Unknown, `size_pos` times out
as expected — it is the cert-only mutual-induction lemma) and then EMITTED the theory + a
heterogeneous dict build/read from a `.py` probe (`Dict[str, PyVal]` gate). Result: **PASS** — the
tool emits the certified strictly-positive bespoke variant + the faithful `map_update_some` build
(`… "ctor" (PStr arm_ctor) … "captures" (PArr (PCons (PStr "x") PNil))`) + the `Map.get` read, and it
**TYPECHECKS (L3-tc ✓)**. One emission bug found+fixed (the abstract-val insert point splits a
multi-line `type … | arm` — the `pyval` type is now emitted with INLINE arms so the block lands after
the whole mutual group). Mutation test faithful (`["x"]`→`7` flips `PArr (PCons …)`→`PInt 7`).

I1 built (all gated on `_uses_pyval`, corpus byte-diff-0 over 767 files):
- (a) `preamble.py::_emit_pyval_theory` + `_uses_pyval` + the `use` block.
- (b) `statements.py::_build_dict_literal_map` pyval branch + `expressions.py::_pyval_wrap` (per-value
  faithful tag: str→PStr, int→PInt, list→PArr cons, nested-dict→PMap, IR-node→PNode).
- (c) readers: `_dv_empty_default`/`_dv_missing_default` pyval + `_collect_pyval_read_locals` (a
  `v = d[k]` local is a pyval ref, not `ref 0`).
- (d) cert `rocq/Phase2f_PyVal.v` (25 goals, `Print Assumptions` all "Closed under the global
  context") + `lean/PyCSL/PyVal.lean` (`#print axioms`: only kernel propext/Quot.sound). Ledger 3.
- (e) fixture `test-suite/corpus/pycsl-reference/0918_pyval_heterogeneous_dict.mlw` — Z3: GoodFaithful
  Valid, both evil twins Unknown (non-vacuous). Fidelity mirror-check 52/52.

Next increment: **I2** (the make-or-break CONVERSION of `_render_match_pattern`) — count unchanged by
I1 (infra only), as expected.

## Honest costed scope
I1 (theory+emitter+readers+cert+fixture) is the foundation (the risky coupling unit). I2 is the first count cut.
I3+ is the cascade (the giants + collectors — the bulk of the yield). Multi-session; this run targets I1 + I2 +
as much of I3 as fits. Refutation exit at Gate S if EMISSION walls (the model is proven; the tool's emission is
the residual risk).

## I2 OUTCOME (2026-07-20) — pyval PAYOFF VALIDATED on real code; count cut GATED on the input-dispatch wall
Step 1 (KEY): a faithful witness of `_collect_typevar_registry`'s inner `{"bound": bound}` (bound: str), inner
annotated `Dict[str, PyVal]`, emitted through the LIVE tool:
- BEFORE (`Dict[str, Any]`): `map_update_some (const (None: option int)) "bound" bound` -> `map string (option
  int)`; the string `bound` forced into `option int` = HARD TYPE ERROR (int-erasure).
- AFTER (`Dict[str, PyVal]`): `map_update_some (const (None: option pyval)) "bound" (PStr bound)` -> `map string
  (option pyval)`, **L3-tc ✓**. String carried faithfully as `PStr bound`. Pyval fixes erasures (2)+(3). VALIDATED.
Step 2 (REFINE): full `_collect_typevar_registry` conversion is walled by a NON-pyval residual — the `for stmt in
node.body:` loop reads the module body via `stmts_of : emit_ir -> array int` (preamble.py:3930, OPAQUE), so the
input-side `isinstance(stmt, ast.Assign/Call/Name)` statement-dispatch is unmodellable. The pyval dict build lives
INSIDE that loop -> can't emit for the real fn until the input-dispatch wall breaks. SAME wall keeping
`_py_stmts_to_ir` (Module5_IREmitter.py:1070) trusted. Optional[str]-bound + TypeVar-detection are secondary
behind it. FALLBACK survey: every heterogeneous-dict build in the emitter is gated behind the SAME `node.body`
input-statement-dispatch wall, or is homogeneous. NO clean pyval-primary-wall stub exists.
=> Pyval is a REAL, certified, validated capability (banked) but converts 0 stubs ALONE. Banking a pyval count
cut requires FIRST breaking the INPUT-SIDE STATEMENT-DISPATCH wall (`node.body`/`stmts_of` opaque array int ->
typed pyast_stmt-dispatchable, extending ce71e3ab's class-body machinery). That is the NEXT wall (I3-pre).

## I3-pre OUTCOME (2026-07-20) — input-dispatch wall REFINE; the pyval count-cut chain FULLY PINNED
Module-body pyast_stmt dispatch PASSES (bounded, ~78 lines, reuses ce71e3ab pyast_stmt ADT + psl cons-list, NO new
ADT/cert, byte-inert): `_collect_typevar_registry` lowered to REAL typed dispatch — `node: ast.Module`->`py_module_node`,
`for stmt in node.body`->`psl_nth (module_body_ast node)` (arithmetic variant), `isinstance(stmt,ast.Assign)`->
`is_assign_node`, `call=stmt.value`->`stmt_value` (emit_ir projector). But it converts 0 stubs ALONE -> REVERTED
(non-vacuity; would leave count flat).
TRUE PREREQUISITE = the emit_ir CALL-INTERNALS value model (shared by ALL 5 module-body collectors:
_collect_typevar_registry, _synthesize_typeddict_functional, _synthesize_namedtuple_functional,
_synthesize_tuple_records, _collect_final_registry — all recognize `Name = Ctor(...)`):
  1. `call` emit_ir-local bridge — BUILDABLE (pre-scan enhancement: _collect_emit_ir_result_locals must see
     `call = stmt.value` is emit_ir before _pyast_stmt_locals populates).
  2. `isinstance(call.func, ast.Name)` + `call.func.id != "TypeVar"` — DEEP: emit_ir stores Call callee as a bare
     string `func_of : emit_ir -> string`, discarding the ast.Name/ast.Attribute NODE distinction. No `call.func`
     sub-node projector.
  3. `for kw in call.keywords` — DEEP: NO keyword-node model in emit_ir at all (no keywords_of, no keyword-node
     type, no .arg/.value projectors).
PINNED CHAIN for the pyval count cut on the collectors:
  pyval [DONE, certified] + Optional[str] [DONE] + module-body pyast_stmt dispatch [PROVEN bounded, ~78 lines] +
  emit_ir Call-internals model [DEEP — func-as-typed-node (is_name/id) + keyword-node list ADT + cert] = converge.
The Call-internals model is the terminal deep build. Spike it (fable oracle) before building.

---

## J1 GATE-S — emit_ir Call-internals value model: **PASS** (infra landed)

**Gate-S emission make-or-break: PASS.** Verified end-to-end against the live tool:

1. **Theory emission + typecheck (refute-cond 1): PASS.** `preamble.py::_emit_exprir_theory`
   now emits the standalone `kwval`/`keyword`/`keyword_list` types BEFORE the emit_ir sum,
   the `IrCallKw string keyword_list emit_ir int` ctor, its `kind_of` arm (`"Call"`, shared
   with IrCall/IrCallN — non-injective, sound), and the projectors (`call_keywords`,
   `kw_arg_of`/`kw_value_of`, `is_kwname`/`is_kwattr`/`kwname_id`/`kwattr_of`) — all gated on
   `_uses_call_kw`. A real `pycsl <fixture> --keep-mlw` on a `CallKw`-annotated mirror emits the
   FULL ~80-ctor emit_ir theory WITH the additions and **Why3 typechecks + the file PROVES**
   (Verification SUCCESS). The certified iteration form's TYPEABILITY was Gate-R confirmed
   (`callinternals-oracle.mlw` `extract_bound'vc` Valid + `callinternals-composition-probe.mlw`
   composes with the real `with irlist` ADT).
2. **Byte-inert gate (refute-cond 3): PASS.** `_uses_call_kw` fires only on the `CallKw`
   sentinel annotation (no corpus/mirror carries it). Full 767-file byte-diff sweep = **EMPTY**.
3. **Iteration-emission typing (refute-cond 2):** the lowered form typechecks (oracle-proven);
   the emitter-side *recognizer* that produces it from Python source (`Ctor(bound=B)` construction
   + `for kw in call.keywords` cons-list iteration) is the **J2/J3 conversion consumer** — it has
   no existing machinery to ride (unlike pyval's dict-literal path), and the task scopes the
   `_collect_typevar_registry` conversion to the next increment. J1 count UNCHANGED (infra),
   exactly the I1 precedent ("infra + cert + fixture; NO mirror conversion yet").

**Built:**
- `preamble.py`: `_uses_call_kw()` gate + the theory additions (standalone types, `IrCallKw`,
  `kind_of` arm, projectors) + `needs_array` wiring; `Module6_WhyMLTranspiler.py`: theory-emit
  trigger wired to `_uses_call_kw()`.
- Cert `rocq/Phase2g_CallKw.v` (18 goals, `Print Assumptions` all "Closed under the global
  context") + `lean/PyCSL/CallKw.lean` (`#print axioms` only propext/Quot.sound) — **axiom-free,
  ledger 3**. Model on Phase2f: (a) well-formed bespoke cons-list, (b) `kwlist_size`
  well-founded + tail strictly shorter, (c) KwName/KwAttr injective + `KwName s <> KwAttr t`
  (Name/Attribute never collapsed), (d) `extract_bound` faithful (variable projects as `Some v`,
  evil-twin wrong-value UNprovable).
- Fixture `test-suite/corpus/pycsl-reference/0919_call_keyword_internals.mlw` (0918 convention,
  `git add -f`): builds an `IrCallKw` with a `bound=` keyword + extracts via the emitted
  projectors; 5 GoodFaithful goals Z3-Valid, both evil twins (wrong value; Name/Attribute
  confusion) non-Valid (non-vacuous). Mutation test: `bound`→`notbound` flips `build_call`
  Valid→Timeout.

## J1 + J2/J3 OUTCOME (2026-07-21) — WALL BROKEN, first value-model count cut LANDED
- J1 (commit 27f898a0): emit_ir Call-internals model (kwval leaf + bespoke keyword_list + IrCallKw ctor +
  projectors call_keywords/kw_arg_of/kw_value_of/is_kwname/kwname_id/is_kwattr/kwattr_of) + Phase2g cert
  (axiom-free) + fixture 0919. Emission PASS, byte-diff 0, ledger 3. Infra (count unchanged).
- J2/J3 (commit b5bef284): CONVERTED `_collect_typevar_registry` — the CONVERGENCE of pyval + Optional[str] +
  module-body pyast_stmt dispatch + Call-internals. Count 1018->1017. FIRST realized count cut through the
  heterogeneous Dict[str,Any] value-model wall. Real lowering: is_assign_node / func_of "TypeVar" / keyword_list
  fold (kwl_len/kwl_nth, kw_arg_of "bound", is_kwname/kwname_id/is_kwattr/kwattr_of) / pyval nested store
  (map string (option (map string (option pyval))), PStr !bound). ZERO int-erasure. --fun SUCCESS (whole-file
  wedges on heavy Module5 -> --fun authoritative per ENV note: 234 VCs Valid). byte-diff 0 (twice). ledger 3.
  mirror-check 52/52 verbatim. mutation test PASS (not a facade). Sub-fix: IrCallKw size arm + arg0_of so
  size_arg0_dec lemma stays Valid.
- Banked reusable capabilities (module-body dispatch A + call/target bridge B) for the OTHER 4 collectors:
  _collect_final_registry (CLOSEST — needs pyast_stmt->psl body projector for nested `for cstmt in stmt.body` +
  self-field-list append), _synthesize_typeddict/namedtuple_functional (need multi-positional-arg projection
  call.args[i] [ADT carries only arg0/arity] + arg-substructure iteration + type_decls append),
  _synthesize_tuple_records (isinstance ast.Subscript + type_decls append). Each a follow-on increment.

## CASCADE MAP (2026-07-21) — sibling collectors are CONJUNCTIONS, not bounded follow-ons
_collect_typevar_registry converted because its ONLY walls were the 4 built capabilities. The siblings each need
MORE (measured, do-not-understate):
- _collect_final_registry: R1 (nested `.body` over a pyast_stmt LOCAL — `_pyast_bodyparams_for_tag` matches params
  only; need stmt_body projector + propagate _pyast_stmt_locals into nested loops) + R2 (`ast.walk(cstmt)`
  Call-iterator — opaque `ast_walk: pyast_stmt->psl` val + loop recognition) + R3 (self-field `seq pyval`
  list-append — `find_append_targets` backs appends with `array int`; pyval only does MAP stores today, no
  list-append precedent). ALL THREE new. ≥3-capability build.
- _collect_type_params: `type(tp).__name__` reflection + list-of-pyval append.
- _collect_class_fields: R2 (ast.walk) + more.
- _synthesize_typeddict/namedtuple_functional: multi-positional-arg projection (`call.args[i]` — IrCall ADT carries
  only arg0/arity) + arg-substructure iteration + type_decls append.
- _synthesize_tuple_records: isinstance ast.Subscript + type_decls append.
RECURRING reusable next-capabilities (broadest leverage): R2 ast.walk-opaque-projector (>=2 collectors), the
seq-pyval/list-of-heterogeneous-dict append (>=4 collectors, incl. type_decls.append), multi-arg projection (2).
Each collector = a multi-capability conjunction; NO bounded 1-piece follow-on. Next value-model count cuts require
a deliberate multi-capability build (build order: seq-pyval-append + ast.walk + nested-body-local, then converge).

## R3 SEQ-PYVAL SELF-FIELD APPEND (2026-07-21) — MODELING **PASS**, EMISSION **CERTIFIED-BOUNDARY** (terminal wall)
Gate S spiked R3 (the novel piece) MODELING-first (`scratchpad-r3-spike.mlw`, reverted after): a mutable record
field `final_registry : seq pyval`, `append` lowered to `self.final_registry <- snoc (old self.final_registry)
entry`, PMap 4-key dict as the entry. **Z3 result: all Valid, axiom-free** — `append_final'vc` (frame+effect),
`test_append_consequence'vc` (last elem = the PMap; `class` read-back = `Some (PStr cls)`), `test_two_appends'vc`
(sequential compose), `read_class_faithful`/`read_kind_literal` (heterogeneous read-back); evil twin
`evil_append_noop` (length-unchanged claim) Timeout=NOT Valid (non-vacuous). `use seq.Seq`+`snoc`; `seq pyval`
typechecks fine (pyval is a fully-defined concrete type; `seq` over it is positive OUTSIDE the recursive variant,
distinct from the `PArr (seq pyval)` positivity issue INSIDE it). NO `axiom`, NO abstract `val`. Reuses Phase2f.
=> R3 MODELING is a proven, durable, axiom-free capability (banked; NOT emitted this run).

**But R3 EMISSION is the terminal wall — two disjoint blockers, measured against the LIVE tool:**
1. **The existing self-field-list append is a FACADE (fresh-local shadow + int-erasure).** Emitting proc
   (`src/pycsl_lib/proc/__init__.py`, the only self-field `.append` precedent) shows `setenv`'s
   `self._env_keys.append(key)` lowering (proc `__init__.mlw`): the field is typed `mutable _env_keys: array int`
   (INT-ERASED; strings compared via `str_hash_op`), and the append emits `let self__env_keys = Array.make 1024 0`
   — a FRESH LOCAL that SHADOWS the field — then `self__env_keys[len] <- key`. The real `self._env_keys` field is
   NEVER written back (only `self._env_count <- +1` touches the record). So even the HOMOGENEOUS case does not
   faithfully mutate the field; the heterogeneous `seq pyval` case has NO machinery at all. Faithful self-field
   seq-pyval append = a from-scratch emission subsystem (rework `find_append_targets` + statements.py:~2981 to emit
   `self.f <- snoc self.f (PMap …)` on the RECORD field, typed `seq pyval`, routed through pyval not
   `Array.make 1024 0`/`str_hash_op`).
2. **The IREmitter mirror is DELIBERATELY FIELDLESS.** `PyCSLToJSONEmitter.__init__` is `pass`
   (`\trusted`, `assigns \nothing`); `_final_registry` is not a modeled field; the `@mutable_state` decorator on
   the mirror is an explicit "fieldless mixin, no dummy field" shim used only for `node.attr` emit_ir reads (see
   the class header comment). To assign `self._final_registry` a method needs `assigns self._final_registry` on a
   STATEFUL record with that mutable field + a class invariant (the proc/UnixInodeFileSystem shape). Retrofitting
   the fieldless 60-stub mirror to stateful changes `self`'s modeling across every method — invasive, no precedent,
   high byte-diff risk — far beyond the scoped "3 residual pieces."
VERDICT: per Gate-S refutation policy — R3 EMISSION is the terminal wall, so R1 (`stmt_body` nested-body-local
projector) and R2 (`ast_walk` opaque projector) were NOT built/ground (both are moot: even fully built, the
converged `_collect_final_registry` still cannot faithfully emit its `self._final_registry.append(dict)` sink).
REVERTED to clean; count unchanged (1015). Banked: the R3 MODELING cert (seq-pyval append, axiom-free) stays
available for a future session that FIRST builds the faithful self-field-list-mutation emission subsystem (unblocks
_collect_final_registry, _collect_type_params, _collect_class_fields, and the 3 `type_decls.append` synthesizers —
the >=4-collector leverage node). Build order for that session: (a) faithful self-field seq-append emission
(replace the shadow-local facade), (b) mirror-stateful retrofit OR a return-value refactor that avoids the
self-field sink, THEN R1+R2+converge.
