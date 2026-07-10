# Reader-census 2026-07-10 — whole-body feasibility over model-addressable readers

*Executed under the self-tcb-reduction loop (measure-before-build, §10.1/§10.2). Each candidate: port
the live body verbatim into its mirror stub + the fixed `#@ requires True / ensures True / assigns F`
contract, run the WHOLE-BODY proof (`--fun`), classify, revert. Every conversion verdict was checked
against ALL gates (the census's `--fun`-only pass is INSUFFICIENT — it misses fidelity; see `_is_float_expr`).*

## Result: 1 standalone -1 banked; the rest are the composition-wall/no-more-int family

| Method | File | Verdict | -1? | Blocker |
|---|---|---|---|---|
| `_is_float_expr` | expressions.py | **CONVERTED** (commit `6700e417`) | **yes** | clean — kind/op/name/left/right accessors + `size` variant, non-vacuous |
| `_is_string_expr` | expressions.py | VALUE-GAP | no | emit_ir ADT has no IfExpr **else-arm accessor**: `ir.get("orelse",{})` → opaque `ir_get_2 <hash>` (`int`) not `emit_ir`, so recursing `_is_string_expr` on it type-fails (`int` vs `emit_ir`). FIRST of several — 238-line body also does `or`-chains, `ir["right"].get("type")`, `_field_type_of` calls, `_record_types[…]["field_types"]` nested-dict reads. NOT a lone fix. |
| `_callable_tag_to_whyml` | functions.py | VALUE-GAP (A) | no | `getattr(self,"_record_types",{})[tag]["whyml_name"]` nested `Dict[str,Dict]` → `int` placeholder; string return mismatches. |
| `_callable_whyml_arrow` | functions.py | VALUE-GAP (B) | no | `[self._callable_tag_to_whyml(t) for t in arg_tags]` list-comp over a string-returning method → opaque `list_comp 0` (`int`); `parts = whyml_args + [whyml_ret]` becomes `int + array int`. |
| `_rhs_yields_array` | types.py | VALUE-GAP (A) | no | `val_ir.get("type","")` on `Dict[str,Any]` binds `ref 0` (`int`); `t == "Var"` mismatches string. |
| `_rhs_yields_map` | types.py | VALUE-GAP (A) | no | same `.get("type","")`→int collapse. |
| `_field_type_of` | types.py | VALUE-GAP (C) | no | `attr_ir.get("value") or attr_ir.get("object") or {}` — the `or {}` empty-dict default ill-types against `option int`-valued `Map.get`. |
| `_first_assign_kind` | types.py | VALUE-GAP (A) | no | same `.get("type","")`→int collapse. |

## The three named gaps (all bounded, none a lone win)

- **Gap A** — `Dict[str,Any]` IR-param `.get("type")` collapses to `int`. Fix: closed-key **TypedDict view**
  on the param (the `ValIRBoolView`/`BoolWrapIRView` pattern that already converted `_val_is_bool` /
  `_bool_ir_to_int_wrap`). Unlocks `_rhs_yields_array`, `_rhs_yields_map`, `_first_assign_kind`,
  `_callable_tag_to_whyml` (~4 methods).
- **Gap B** — list-comp over a string-returning method → opaque int. Fix: element-type inference picks
  `array string` when the callee returns `string`. Unlocks `_callable_whyml_arrow`.
- **Gap C** — `x or {}` empty-dict default vs `option int`. Fix: `or`-chain empty-dict arm → option `None`.
  Unlocks `_field_type_of`.
- **emit_ir IfExpr else-arm accessor** — a small ADT extension (`orelse_of`, like `left_of`/`right_of`);
  the FIRST gap in `_is_string_expr` but that method needs the full Gap-A/C set too, so the accessor
  alone converts nothing (facade — do not land alone).

## Takeaway
The model-addressable-reader frontier has ONE free -1 (`_is_float_expr`, banked); every other reader
probed bottoms out in Gap A/B/C — the same `Dict[str,Any]`-monomorphization family as the composition
wall. The next real yield is a FEATURE build (Gap A TypedDict-view is the highest-leverage: ~4 methods),
not more lone conversions.
