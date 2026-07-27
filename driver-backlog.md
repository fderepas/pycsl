# self-tcb-reduction driver — backlog

Canonical count: `grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l` = **882** (drift 2, ledger 3).

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
