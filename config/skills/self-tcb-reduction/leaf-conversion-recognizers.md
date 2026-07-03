# Leaf-conversion recognizers & per-leaf triage (empirical, 2026-07-03)

Practical knowledge from converting the bottom-up DAG leaves (campaign 1273 → 1266). Read alongside
`SKILL.md`; this is the *how-to* for the individual stub conversions, and `giant-recursion.md` (repo
root) for the DAG strategy.

## 0. The two marker regimes (know which you're in)

- **STUB leaf** (already a `\trusted` stub in the mirror) → converting is a real **−1**. Porting the
  verbatim live body is **emitter-inert** (no `src/pycsl` change) ⇒ byte-diff is *trivially 0*; the
  only gate is the mirror type-check + proof. These are the count wins.
- **MISSING leaf** (not in the mirror) → adding it as a verified body is **±0** markers (it wasn't a
  marker). Worth doing only to unblock a parent (DAG progress), or when it needs a reusable recognizer
  that pays off elsewhere.

## 1. Triage a candidate BEFORE converting (saves revert cycles)

Check the live signature + body for these, in order — each maps to a known fix or a "defer":

| Signal | Fix | Cost |
|--------|-----|------|
| `Optional[str]` **return** | sentinel sweep: `-> str`, `return None`→`""`, callers `is not None`→truthiness (`is None`→`not x`) | byte-diff-0 if the values are never legitimately `""` |
| `Optional[str]` **param** | annotation `Optional[str]`→`str` — **runtime-inert** (byte-diff 0). Only if the body is truthiness-safe (`if not x` / `if x and`) and no VERIFIED caller passes a None-able value | trivial |
| reflects on an IR param (`expr.get("type")`) but param typed `Dict`/`Any` | annotate the param `"ExprIR"` (emitter-internal ⇒ byte-diff 0) | trivial |
| **set-valued** return/local (`-> Set[T]`, `x=set(); x|=…`) | set-local declaration — **DEFER** (not yet modelled) | blocked |
| reflects on **non-projectable** IR fields (BinOp `left`/`right`/`op`) | the emit_ir ADT has no BinOp — **DEFER** | blocked |
| **IR deep-copy / construction** in a recursion (`_subst_params`) | recursive emit_ir construction — **DEFER** | blocked |
| `else {}` fallback next to an emit_ir value | emit_ir/map union — **DEFER** (no clean sentinel) | blocked |
| calls a still-trusted stub (non-leaf) | not a leaf — convert the callee first | ordering |

If none of the "blocked/defer" rows fire and the recognizer rows are all in-stack, it converts.

## 2. The reusable recognizer stack (all byte-diff 0, most @mutable_state/emit_ir-gated)

Built across the campaign; each new leaf tends to need **≤1** *new* small piece now.

- **emit_ir reflection**: IR-node params → `emit_ir`; `_EMIT_IR_STR_ATTRS` (`.kind`/`.var`/…);
  node-LIST attrs → `args_of`; **subscript-receiver `.get`** (`a[i].get("name")` — receiver is an
  array element in the Call's `receiver` field, bare `func=="get"`; place the projection BEFORE the
  `"." not in func_name` bail in `_lower_dict_get_call`; element `.get("value")`→`value_of`, not the
  `svalue_of` sub-node; `_is_string_expr` recognises the string key so `== "s"` uses `str_eq_op`).
- **dict-literal `emit_ir` construction**: a method returning a `{"type":K}` node is `emit_ir`
  (`_returns_emit_ir` override in `_compute_return_type`, ahead of the `ann in ("dict",…)` branch).
- **method tuple-returns** `(emit_ir, string)`: `_infer_tuple_slot_type` (string-first — `_is_emit_ir_expr`
  over-claims str-attrs); `_refine_tuple_return_type` sets the func context during MAP-building (else the
  caller's unpack mistypes); `_collect_emit_ir_result_locals` types a direct call-unpack. Preamble:
  `use array.Array` forced for any @mutable_state module (emit_ir `args_of`).
- **constant-dict**: annotate a class-constant lookup table `Dict[str, str]` → a declared abstract
  `map int (option string)` (contents unmodelled — sound; `ensures True` needs only result TYPES).
- **local-dict-value-type** (Module5): a LOCAL dict literal with all-string values → `dict[_, str]`
  (subscript default `""`, not `0`). NOT @mutable_state-gated but byte-diff 0 (int dict locals inert).
- **`str(x)`-as-string**: `_is_string_expr` treats `str(...)` as string, so `str(x).lower()` →
  faithful `str_lower_op`.

## 3. Byte-diff principles (why many conversions are "free")

- Porting a **STUB** body to the mirror never touches `src/pycsl` → the corpus sweep is unaffected.
- A **param/return type annotation** change (`Optional[str]`→`str`, `Dict`→`"ExprIR"`) is *runtime-inert*
  — Python doesn't enforce annotations, and the emitter's emit-time behaviour is unchanged. Byte-diff 0.
- A **sentinel/truthiness caller sweep** is output-preserving iff the leaf's real values are never `""`
  (all the reflection leaves qualify — they return field names / type tags / kinds).
- **Always still run the byte-diff sweep** when an emitter recognizer (not just an annotation) changed —
  a new `_is_string_expr` arm etc. is *not* automatically inert.

## 4. Diagnosis recipe (fast leak localization)

```bash
rm -f <mirror>.mlw
python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl --no-proof --keep-mlw > /tmp/tc.txt 2>&1
# the LAST "expressions.mlw", line N is the real leak (earlier ones are warnings):
loc=$(grep -E 'expressions.mlw", line [0-9]+' /tmp/tc.txt | grep -vE Warning | tail -1 | grep -oE 'line [0-9]+' | head -1 | grep -oE '[0-9]+')
awk -v L=$loc 'NR<=L && /let expressionemissionmixin__/{n=$2} END{print n}' <mirror>.mlw   # the fn
sed -n "${loc}p" <mirror>.mlw                                                                # the expr
```
The lowered form names the gap: `int_to_string x` (x should be string), `contains_check k 0`
(undeclared set field), `(get_1 <hash>)` (unrecognized `.get` — often subscript-receiver), `None -> 0`
default on a string/emit_ir/seq map (wrong `_dv_missing_default`), `(lower_0 ())` (`.lower()` on an
unrecognized-string receiver), a `_union__<m>_N` type (Optional param/return not desugared).

## 5. Known OPEN gaps (next features, in rough leverage order)

1. **cross-collector string-local dependency** — `field = var[len("self."):]` where `var = node.var`:
   the slice recognizer reads `_string_local_vars`, but `var` is only in the *accumulating* set of
   `_collect_str_call_result_locals` during its own fixpoint. Blocks `_handle_arraylen_expr`. Needs the
   slice/str-attr checks to consult the in-progress set (a fixpoint refactor), not just `_string_local_vars`.
2. **set-local declaration** — a local `x = set(); x |= {…}` / a `-> Set[T]` return declared `int`.
   Blocks `_module_binding_names`, the quant-binder push/pop pair.
3. **BinOp-operand projection** — `ir.get("left")`/`.get("right")` (the emit_ir ADT has no BinOp arm).
   Blocks `_is_float_expr`.
4. **recursive emit_ir construction / deep-copy** — `_subst_params` (rebuilds an IR replacing Vars).
5. **`.get(k, <str default>)`→projection** — a 2-arg `.get` with a string default lowering opaque
   instead of `func_of`. The LAST gap on `_str_method_recv_and_tail`.

## 6. Efficiency rules learned the hard way

- **Do NOT batch-convert blindly** — most STUB leaves have *some* per-leaf blocker; a 9-way batch cost
  8 revert cycles for 2 wins. Triage each (§1) first; batch only the ones that pass triage.
- **Convert one, prove, commit** for anything with an emitter-recognizer change; the emitter-inert STUB
  ports can be batched safely (byte-diff trivial).
- When a leaf needs ≥2 new *deep* features (not in-stack recognizers), **defer it** and move on —
  diminishing returns. Record which feature it's waiting on (§5) so it's a bounded pickup later.

## 7. Cross-file conversion (2026-07-03 addendum)

Each mirror file (`expressions.py`, `functions.py`, `types.py`, …) is a SEPARATE self-annotate target:
verify it standalone with `pycsl.py src/self-annotate/src/module6_whyml/<file>.py --import-path src/pycsl`
(the OTHER files resolve from live `src/pycsl`). So a leaf's file dictates which command gates it.

- **Emitter-inert wins are file-local**: porting a STUB body in `functions.py`/`types.py` (no `src/pycsl`
  change) is byte-diff-trivial exactly as in `expressions.py`. Converted `_union_arm_whyml_type`
  (functions.py) this way — a LOCAL str→str dict + `.get`, handled by the local-dict-value-type feature.
- **Self-field leaves need the file's class to be a @mutable_state RECORD.** `ExpressionEmissionMixin`
  IS `@mutable_state @dataclass` with declared fields, so `self._field` membership/`.get`/subscript route.
  `TypeInferenceMixin` (types.py) is a PLAIN class → `target in self._ghost_list_vars` falls to opaque
  `contains_check … <int>`. Converting a self-field leaf there first needs the mirror class made a
  `@mutable_state @dataclass` with its `_ghost_*_vars`/etc. fields declared — a per-FILE prerequisite,
  not a per-leaf one. Blocks `_resolve_effective_ghost_type` (and other types.py self-field leaves).
- **Mis-diagnosis watch**: a "getattr-field `.get` fails" leak is usually a MISSING field declaration
  (an insertion no-op'd on a stale anchor), NOT an emitter gap — the mixin IS in `_record_types`
  case-insensitively. Always grep the mirror to confirm the field is actually declared before theorizing.
