# self-tcb-reduction driver — backlog

Canonical count: `grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l` = **882** (drift 2, ledger 3).
(The 2026-07-27 `_parse_variant_def` 883→882 was reverted — the per-slot tuple-exception feature L3-tc-broke a Module5 importer mirror, §10c trap; 883 restored. Then 883→882 via `_gso_walk`, below.)

## WALKER-RECOGNIZER VEIN — `_gso_walk` CONVERTED (2026-07-27, commit 5121100f, 883→882)

The isolation-spike prediction ("recognizer-gated, one field-read off `_sa_walk`") is CONFIRMED and
worked: extended `recognize_sawalk`/`emit_sawalk_group` (`generic_fold.py`) with a fail-closed second
env-threaded pre-action shape — the GhostAssign ghost-string guard (`_match_gso_pre`) — reusing the
certified L1 `pyval`/`pydict` catamorphism (ledger 3, no new axiom). Shared walk group factored into
`_sa_walk_group_lines` (arrayset path byte-identical). Emits real spine readers on `node` + `slookup`
on `symtab` (non-vacuous), NOT the int-erased facade. Gate: whole-file proof SUCCESS; §10c all-7-importer
L3-tc OK; byte-diff 812==812 exit 0; vacuity clean; mutation PASS; mirror 52/52.

**Nearest remaining walker candidates — DEFERRED (≥2 stacked each):**
- `_union_c8_test_references_union_var` — the spike's "unbound `union_vars`" is a SYMPTOM of the WRONG
  recognizer (`_try_emit_any_all_fold` fallback), not a threading bug: the real body int-erases
  (`test: int`, `typeof_op 448` constant, `test_values_0 ()` nullary) AND the fold gets `int` where it
  wants `array int` — threading `union_vars` alone does NOT fix L3-tc. Sound path = `recognize_type_existence`
  extended with THREE stacked: `set`-typed carried (emitter hardcodes `(c: string)`) + a `name in <carried-set>`
  membership discriminant + reversed subject-first/carried-last param order. Research-grade for +1.
- `_cp_walk` — 2-param single-env arity generalization of `_sa_walk_group_lines` (NO sdict) + a ProofAssert
  cross-call guard matcher (`_contains_result(node.get("test"))`) + cross-call emission. ≥2 stacked, and
  touches the shared arrayset walk-group (byte-identical risk).
- The other ~54 residual (`_pb_stmt`/`_pb_expr`/`_cs_stmt`/`_cs_clause` dispatch-checkers; `_body_has_*`
  nested-closure `found=[False]` walks; `_noreturn_walk_stmts` inter-iteration state; `_stmt_is_noreturn_call`
  set-membership+`rsplit`; `_typeddict/_namedtuple_walk_*` `.items()`-key-dispatch + set/dict carried;
  `_union_c8_recognized_guard` flat multi-branch typed-node predicate) — each a DISTINCT bespoke recognizer
  extension or the `functions.py` `_build_method_*_map` research-grade BUILD family. Per
  [[frontier_exhaustion_map]]: bounded engineering, one +1-marker apiece, authorize per-shape.

## `Dict[str,Any]` VALUE-MODEL WALL = REFRAMED (recognizer-gated, NOT value-model floor) — 2026-07-27 ISOLATION SPIKE

**The value model is NOT the wall.** Decisive isolation datum: the built `pyval`/`pydict` model
lowers generic `.values()`/`.items()` dict walks NON-VACUOUSLY. Living proof = the ALREADY-CONVERTED
`_cs_descend`/`_pb_descend`/`_sa_walk`/`_contains_result`/`_body_has_return` in `core_ir_semantic.py`
emit `(v: pyval)`, `PDict/PList/PStr` spine walks, `values (d: pydict): list pyval`. A `Dict[str,Any]`
param does NOT intrinsically erase to `option int`.

**The residual is RECOGNIZER-GATED, not value-model-gated.** Each still-trusted walker int-erases
ONLY because no bespoke recognizer matches its exact structural shape → fall-through to the default
int-hash emitter. Three verbatim-port + emit + read isolation datums (all reverted clean):
- `_pb_stmt` (`.get("stmt")`-dispatch + list-field iteration) → `s: int`, `s_get_1 <hash>`, literals
  hashed, list-fields → vacuous `Array.make 1024 0`, `s.values()` → nullary `s_values_0 ()`. INT-ERASED.
- `_gso_walk` (compound pre-action `op!="=" and symtab.get(target)=="string"`, single raise) → `node: int`,
  `typeof_op 422` (isinstance vs a CONSTANT), `node_values_0 ()` nullary. INT-ERASED — ONE field-read
  different from the CONVERTED `_sa_walk`, but `recognize_sawalk._match_sa_pre` is tailored to sa_walk's
  exact two-raise nested-isinstance pre-action.
- `_union_c8_test_references_union_var` (2-param bool-existence) → recognizer FIRES, emits the CORRECT
  non-vacuous `exists _fk. ... self(a[_fk] union_vars)` postcondition, but L3-tc FAILS
  `unbound symbol 'union_vars'` — the env param isn't threaded into the generic-values-loop arm's spec.

**Composition (core_ir_semantic.py, 56 trusted):** every zero-build-reachable shape (pure-descend
`.values()` walkers, thin-fanout body walkers, 1-param `any()` bool-existence, sawalk env-threaded walker)
is ALREADY CONVERTED. The 56 residual each need a DISTINCT bespoke recognizer extension: env-param
threading (`_union_c8*` — the closest, the recognizer already emits the right spec), compound-pre-action
matcher (`_gso_walk`), stmt-dispatch+list-field recognizer (`_pb_stmt`/`_cs_stmt`/`_pb_expr`/`_cs_clause`),
nested-closure `found=[False]` mutable-cell support (`_body_has_raise`/`_body_has_diverging_construct`/
`_lemma_returns_value`), + set-membership/`rsplit`/`warn`/arithmetic secondaries. Each is a bounded
(+1-marker, low-yield) engineering extension of a SHARED emitter (`generic_fold.py`, not mirrored → 0 new
stubs) — but each carries the §10c ALL-importer-mirror L3-tc obligation. NOT a research-grade value-model
floor for the WALKER cluster.

**Still research-grade (the BUILD family):** `module6_whyml/functions.py` `_build_method_*_map`
(`Dict[str,List[Dict[str,Any]]]` build-and-return, 16-682 body lines) = genuinely ≥3-stacked
(heterogeneous-dict BUILD + collection-result + self-state maps). Large build, unchanged research-grade.

VERDICT: CERTIFIED-BOUNDARY at zero-build (0/3 sampled convert clean); reachable-with-existing-recognizers
frontier in core_ir_semantic is EXHAUSTED. Next lever (if funded): thread the env param through the
bool-existence generic-values-loop arm — the single smallest recognizer gap, closes `_union_c8*` +
possibly a sub-cluster of env-param existence walkers; measure-before-build + §10c all-importer L3-tc.

## PER-SLOT-TYPED EARLY-RETURN TUPLE EXCEPTION BUILT + `_parse_variant_def` CONVERTED (2026-07-27) — 883 -> 882

The 883 list-of-records "early-return tuple-exception BOUNDARY" was a REOPEN KEY, not a floor. Built
the DECISIVE gap #3 (per-slot-typed early-return tuple exception, `_tuple_return_exc`: all-int keeps
the legacy `Return_<arity>` byte-inert; a non-int tuple gets `Return_tuple_<arity>_<slot-tokens>`
declared in a post-map phase parallel to `_emit_union_return_exceptions`) + gaps #1 (str-call/seq-string
slot typing via the body's own `_collect_str_call_result_locals`/`_collect_array_elem_types`) and #2
(slot-aware empty-`[]`→`Seq.empty` raise value). Feature corpus byte-diff 0 (812/812); mutation-test
load-bearing; commits 872635f4 (feature) + 4ce8e418 (`_parse_variant_def`, whole-file proof SUCCESS,
`expect_op` gains the faithful monotonicity ensures). Full detail: `getting-better/parser-tokenstream-impl.md`.
Rest of the early-return refined-tuple cluster DEFERRED (independent secondary blockers): `_parse_datatype`
(seq-of-tuple element + `IrDatatypeDecl` ctor), `_parse_inductive*` (certified `rule_list` inductive for
emit_ir-in-tuple), `parse_rocq_assumptions_block` (splitlines/startswith-tuple/split string-op boundary),
pycsl.py `_why3_typecheck`/`_run_vacuity_gate`/`_dispatch_provers`/`_probe_one` (subprocess/I/O boundary).

## PARSER "PROOF-SCALE WALL" (888 terminus) = MISDIAGNOSIS, BROKEN (2026-07-26, Phase-2 SPIKE)

The `parser-tokenstream-impl.md` §EXPRESSION-GRAMMAR "solver-context-pollution proof-COST wall"
(the claim that converting `_parse_expr` drowns the clause callers' postconditions irreducibly) is
**refuted**. The callers' postcondition is `self.i >= \old(self.i)` (NOT `ensures True`); the prior
spike converted `_parse_expr` with only `ensures True` + the now-faithful `writes {self.i}`, which
HAVOCS the callers' monotonicity postcondition. DECISIVE isolation: the `ensures-true` and
`ensures-monotone` `.mlw` are byte-identical at 1448 lines except ONE `ensures` line, yet the former
drowns (104M steps) and the latter proves in 0.03s — same module, same bodies, same context. The
sound fix is the existing faithful-monotonicity precedent (`_parse_impl_rhs`/`advance`/`accept_op`):
**`_parse_expr` CONVERTED (888→887) under the STANDARD unmodified whole-file-proof gate**, no emitter/
gate/module/timelimit change. Full data + soundness argument: `getting-better/parser-proof-scale-impl.md`.
Residual expr-grammar members retain their OWN independent blockers (emit_ir variants / str_to_int /
class-valued ctor / irlist proof-cost) but the shared caller-monotonicity blocker is gone.

## CERTIFIED-BOUNDARY — Module-5 self-mut collector cluster (2026-07-25)

`frontend/Module5_IREmitter.py` `_collect_*` / `_synthesize_*` family (largest non-parser residual cluster).
Measured convert-or-BOUNDARY spike: **BOUNDARY**. Two structurally-disjoint members ported verbatim + run
under `--fun` whole-body proof both fail on the §3 value-model wall:

- `_collect_str_decode_locals` (generic-Any `.values()` walker → `Set[str]`): `StrSet.set` result model
  exists, but the heterogeneous dict is typed `int -> option.Option.option int`, so `node["target"]` cannot
  be a `string`. Wall = heterogeneous-`Dict[str,Any]` ∧ collection-result(Set).
- `_collect_2d_params` (IR `List[Dict]` loop → `sorted(Set[str])`): loop var typed `int -> option int`,
  cannot pass where a faithful IR node is expected + Set→List result. Same wall.

**Capability chain per member (≥2, typically ≥3, STACKED — no-stack rule ⇒ BOUNDARY):**
1. faithful heterogeneous-`Dict[str,Any]` value typing (V1 — the research-grade core, §3/§8/§9 of
   `value-model-wall-stand-alone.md`);
2. collection-result modelling (`Set[str]`/`List[str]` build-and-return; §8 B-comp set-algebra leg);
3. (ast-reflecting members `_collect_class_fields`, `_collect_union_arms`, `_synthesize_typeddict_functional`,
   `_synthesize_namedtuple_functional`, `_synthesize_overload_guard`) tuple-return-pyval + Python-`ast`-node
   construction + `type()`/`getattr` annotation reflection.

Reviewer artifact UPDATED: `value-model-wall-stand-alone.md` §10 (verbatim errors = frozen benchmark).
Unblock path: either the research-grade decoder-synthesis SOTA answer, OR a live-emitter retype to declared
`TypedDict` shapes (§9 route — a separate larger build). Do NOT re-open as a marker campaign.

## Standing residual (unchanged)
- V1 heterogeneous `Dict[str,Any]` value model — research-grade (external-reviewer report standing).
- Parser-primitives wall — separate track (`getting-better/parser-primitives-wall-impl.md`, driver-progress.log).

## Family-B parser clause batch DONE (2026-07-26) — count 903 -> 894 (9 conversions)
Reachable SIMPLE contract-clause `_parse_*` builders EXHAUSTED. 9 converted (function_variant,
ghost, footprint, mutex_invariant, shared, assigns_region, shared_state, touches_field,
depends_method). Banked reusable emitter capabilities: optfield `iropt_str` wrap, string-default
fill, explicit-`None`-arg → `IrSNone`. Full detail: getting-better/parser-tokenstream-impl.md.
Remaining parser trusted = two deferred veins: (1) family-B **list-append** (datatype/lock_order/
happy/act_block/for_block/compose_from/conforms_to/dotted_path_list/assigns_target/inductive*),
(2) the **expression-grammar cluster** (`_parse_membership`/`_parse_unary`/`_parse_atom*` — many
mutually-recursive ExprIR node kinds, co-land the emit_ir variants as an interconnected set). Both
are deliberate multi-node builds, not single-shot clause wins.
