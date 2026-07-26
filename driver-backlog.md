# self-tcb-reduction driver — backlog

Canonical count: `grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l` = **908** (drift 2, ledger 3).

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
