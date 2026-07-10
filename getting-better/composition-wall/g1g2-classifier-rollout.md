# G1/G2 classifier rollout — boundary-1 increment, measured floor (2026-07-10)

**Investment in boundary-1 (Dict[str,Any] composition wall), spike-first. Outcome: a real −2 + a reusable
general capability; the pure-classifier subclass is EXHAUSTED at 2.**

## Delivered
- **G1/G2 capability** (commit `46fec238`, byte-diff 0 over 763, ledger 3): `<recordvar>.get("k")` on a
  record-typed (TypedDict/dataclass) receiver → native field read (G1); str-typed record field vs string
  literal → `str_eq_op` (G2). Record-typed-receiver gate keeps plain `Dict[str,Any]` on the legacy op ⇒
  corpus-inert. The conversion recipe = runtime-inert TypedDict annotation (live+mirror identical).
- **2 conversions:** `emits_as_logic_symbol` (scc.py), `_val_is_bool` (types.py) — faithful, non-vacuous.
  `\trusted` 1234 → 1232.

## Rollout census (190 trusted dict-readers classified) — reach EXHAUSTED at 2
The pure single-level closed-key classifier subclass (no iteration / sibling call / self-state / nested-get
/ dynamic key) is a **doubleton**, both converted. The other 188:
- iteration (the large majority — every IR walker/scanner);
- sibling-emitter call (`_first_assign_kind`→`_rhs_yields_array`, etc.);
- `isinstance`/type-test on a pyval (needs an isinstance-on-pyval lowering feature);
- self-state read / dynamic key (`self._array_locals`/`_symbol_table` with computed keys);
- nested-`.get` into a list element.

## The honest edge — the next features (each a distinct small build, diminishing returns)
- **Option-of-record projection** — `_bool_ir_to_int_wrap` has `Optional[Dict[str,Any]]`; G1/G2 lower `.get`
  on a BARE record var, not through an `Optional`/union arm. The front-end resolves `Optional[TypedDict]` to
  `Optional[Any]`, GT1 drops the record arm, and the body proves VACUOUSLY (rejected + reverted). Extending
  G1 to option-of-record field reads unlocks this leaf (+ any Optional-param classifier).
- **isinstance-on-pyval**, **local-dict lookup keyed by a str param** — each a distinct recognizer for a
  small further slice.

**Verdict:** boundary-1's tractable pointwise-classifier piece is banked (−2, verified). The residual is
either the composition wall (research-grade, per the value-model-wall report) or a fan of distinct small
lowering features (Optional-of-record, isinstance-on-pyval, …), each ~1 method — diminishing returns.

---

## Next-feature reach census (2026-07-10) — the pointwise subclass is EXHAUSTED at −3

Censused whether the two named next features (isinstance-on-pyval, local-dict-str-key lowering) would unlock
a worthwhile PURE-classifier cluster BEFORE building either. **Verdict: ~0 — refuted.** The 4 candidates that
pass a crude pure-filter all have COMPOUNDING blockers, not the named feature:
- `_parse_why3_json` — a JSON stream parser (`JSONDecoder.raw_decode` while-loop); I/O, not modellable.
- `_resolve_runtime_config` — reads a config FILE + `json.load` + argparse; I/O, not modellable.
- `bases_closure` — a worklist transitive-closure (`while frontier: pop/extend` over a const dict); a graph
  algorithm, not a bounded lookup.
- `triggers_for` — `TRIGGERS.get(op_key, [])` where `op_key: Tuple[str, Optional[str]]` → `List[Trigger]`;
  a COMPOUND (tuple) key + list-of-record value, not a str-key lookup.

So building isinstance-on-pyval / local-dict-str-key lowering unlocks **~0** pure methods — the looks-eligible
candidates need JSON-I/O / worklist-closure / tuple-key-map / list-of-record models, each a distinct
compounding gap (or the composition wall). **The pointwise closed-key classifier subclass is fully exhausted
at −3** (G1/G2 ×2 + option-of-record ×1). The boundary-1 residual is now genuinely the composition wall
(research-grade, value-model-wall report §5) or these harder per-method gaps. No build (measure-before-build).
