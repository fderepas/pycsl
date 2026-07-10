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

## Widened batch (9 more readers across types.py/functions.py/core_ir_semantic.py) — 0 convertible

| Method | file | mirror≟live sig | Verdict | Class |
|---|---|---|---|---|
| `_call_return_whyml_type` | types.py | yes | VALUE-GAP | A — `rmap.get(fn)` → `int` val vs `string` return arm |
| `_field_type_for` | types.py | yes | VALUE-GAP | A — `info.get("field_types",{}).get(field)` → `int` vs `string` |
| `_resolve_effective_ghost_type` | types.py | yes | VALUE-GAP | A — `str_concat`/`subscript_get` typed `int` vs f-string arm |
| `_has_dynamic_exec` | functions.py | NO (live `Dict`, mirror `int`) | TIMEOUT | walker — `while stack … stack.extend(node.values())` heap-DFS, 30s/goal unproven |
| `_returns_string_seq` | functions.py | NO (live `List[Dict]`) | VALUE-GAP | A + nested `def rec` closure → opaque `py_rec_1` |
| `_first_tuple_return_elts` | functions.py | NO (live `List[Dict]`) | VALUE-GAP | A + recursive-return-type (`int` vs `array int` elts) |
| `_callable_tag_to_whyml` | functions.py | yes | VALUE-GAP | A (re-confirmed: `record_types[tag]["whyml_name"]`) |
| `_lemma_returns_value` | core_ir_semantic.py | yes | TIMEOUT | closure — variant-less recursive nested `walk`, termination VC unprovable |
| `_body_has_return` | core_ir_semantic.py | yes | TIMEOUT | closure — identical variant-less `walk` shape |

## Takeaway (both batches, 17 readers probed)
The model-addressable-reader frontier has exactly ONE free -1 (`_is_float_expr`, banked); ALL 16 other
readers bottom out in one of:
- **Gap A** — `Dict[str,Any].get`/dict-subscript lowered to an `int`-typed opaque val, colliding with a
  `string`/union return arm. Dominant (≈8 methods). Fix = faithful `.get`→`string`/union-typed accessor
  (the closed-key TypedDict-view monomorphization, `ValIRBoolView` pattern). **Highest leverage.**
- **Recursive nested-`walk` closure, variant-less** — #8/#9 (and the core_ir_semantic AST-walker family,
  64 stubs). Fix = emit the nested `def walk(node)` closure with a structural `variant { size node }`
  (as the hand-written `let rec` lemma pack in the same .mlw already does). A DISTINCT bounded feature;
  but those walkers ALSO read generic dicts (Gap A) + do by-ref-set mutation (§10.3 hard class), so the
  variant alone won't convert them — necessary, not sufficient.
- **Unbounded heap-walk** (`while stack`) — #4, genuinely hard (leave-trusted class).

The next real yield is a FEATURE build. **Gap A** (faithful dict-`.get` lowering / TypedDict-view) is
confirmed the highest-leverage single feature — it unblocks ≈4 readers outright (#1,#2,#3,#7) and is a
prerequisite for the List[Dict] ones (#5,#6). No more lone conversions remain in this frontier.

## SPIKE (2026-07-10) — the "Gap A = one feature = 4 methods" projection is REFUTED

Spiked `_call_return_whyml_type` (the flat-`Dict[str,str]` cluster member) to whole-body proof. Finding:
**"Gap A" is NOT one feature — it splinters into ≥4 independent sub-gaps, and field-typing alone
converts nothing.**

- **A1 — self-field string-dict typing** (BUILT + VERIFIED in the spike): decorating the mirror
  `TypeInferenceMixin` `@dataclass` (NOT `@mutable_state` — that pulls the emit_ir ADT and hits the
  09-2223 M1 `size` two-theory collision) + declaring `_module_method_return_types: Dict[str, str]`
  types the field faithfully as `map string (option string)` and binds `rmap` to it. **Works.** But it
  is a **facade alone** (no-unused-facade): it converts zero methods by itself.
- **A4 — option-return mapping** (NOT built): `return rmap.get(fn)` where the method returns
  `Optional[str]` lowers the `Map.get … : option string` with a `None -> 0` **int** default instead of
  mapping the option to the `Optional[str]` return union (`Some v → Arm_0 v | None → Arm_None`). First
  failure (`types.mlw:218 int vs string`).
- **A3 — unmodeled string ops** (NOT built, partly HARD): `fn.rpartition(".")` → opaque `fn_rpartition_1`
  (unmodeled); this poisons everything downstream — `obj`/`method` become `int`, so the f-string key
  `str_concat`s and `.lower()` (`cls_lower_0 ()`) all fall opaque. `str.rpartition` is genuine
  string-library work (search-on-last-sep), not a recognizer tweak.
- **A2 — param `Dict[str,Any]` → TypedDict view** (the `ValIRBoolView` pattern): needed by
  `_rhs_yields_array`/`_rhs_yields_map` (param-dict `.get("type")`), separate from A1.
- **nested-dict** (`_record_types[…]["field_types"][field]`): needed by `_field_type_for`,
  `_callable_tag_to_whyml`; distinct again.

**Per-method sub-feature requirement (measured, not projected):**

| Method | needs (beyond A1) |
|---|---|
| `_call_return_whyml_type` | A4 + A3(`rpartition`,`.lower`,f-string-key) |
| `_field_type_for` | nested-dict iteration + A4 |
| `_callable_tag_to_whyml` | nested-dict subscript + string-literal returns |
| `_rhs_yields_array/_map` | A2 (param TypedDict-view) + Set-membership + A1 |

**Verdict (first pass):** the reader frontier has NO cheap bounded feature left that yields ≥1
conversion. Gap A is a splinter of 4–5 sub-features; converting even ONE cluster method
(`_call_return_whyml_type`) needs A1 + A4 + `str.rpartition` modeling.

## PROBE CORRECTION (2026-07-10, `rpartition-probe.mlw`) — A3 is NOT a wall; the method IS convertible

The "needs `str.rpartition` modeling → string wall" pessimism was WRONG. The self-annotation contract is
**type-safety+frame only** (`ensures True`) — `rpartition` needs NO semantics, only a TYPE-CORRECT val.
Hand-wrote the exact shape of `_call_return_whyml_type` (`rpartition-probe.mlw`): field as
`map string (option string)` (A1) + `val str_rpartition_op (s sep: string) : (string, string, string)`
(A3, no axiom — analogous to the existing `val str_split_op : array string`) + `.lower()` + f-string-key
concat + the A4 option→return-union mapping (`Some v -> Arm_str v | None -> Arm_none`, no int-0 default).

**`call_return_whyml_type'vc` → Valid (Alt-Ergo, 0.04s, 6 steps).** Ledger untouched (0 axioms — the
`val`s are uninterpreted, characterized by nothing; type-safety only).

**Corrected verdict:** `_call_return_whyml_type` is **CONVERTIBLE via 3 bounded recognizers**:
- **A1** — `@dataclass` + `Dict[str,str]` field decl (mirror-only scaffold; BUILT+verified in the spike).
- **A3** — recognize `x.rpartition(sep)` → emit `str_rpartition_op` val + a 3-string-tuple unpack
  (the `str_split_op` pattern; a bounded expression recognizer, no axiom).
- **A4** — when a `map _ (option ν)` `.get(k)` result flows to an `Optional[ν]` return, map the option to
  the return union instead of unwrapping with an int-0 default (a bounded return/option-lowering fix).

None is a string wall; none touches the live emitter's corpus output (mirror-gated); ledger stays 3. The
frontier is NOT floored — it needs a bounded 3-recognizer build for a real −1 (and A1/A4 are reusable
across the flat-`Dict[str,str]` cluster; A2/nested-dict remain separate for the param-dict members).
