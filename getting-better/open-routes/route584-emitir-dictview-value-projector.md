# OPEN ROUTE #584 — THE DICT-VIEW `.get("value")` OF AN emit_ir NODE WHOSE `.value` IS NOT THE SUBSCRIPT ONE (Starred, NamedExpr, SliceAccess, MapSet) USES `_EMIT_IR_PROJ["value"]` = `svalue_of`
**Status: REPAIRED (driver run #6, executor u38, base bdab5f5f1 = int55, branch run6-u38, commits 79d02263b (repair) + the docs commit; annotations §7.584 / §7.585; the class repair also closes route #585). Mechanism: every reflection read on an emit_ir value is chosen by the receiver's CONSTRUCTOR — dict view `irget_value_of` / `irget_lower_of` / `irget_upper_of`, attribute view `iratt_<attr>_of` (per-constructor arms generated from the constructor table + ADT), opaque `val function` for a field no constructor carries as a node (`guard`, `c["pattern"]`, `lineno`, ...); the definitions are spliced into the emit_ir theory only when used. No axiom, no new ADT arm.** Opened as: Status: OPEN, Severity 1, pre-existing (found by run #6 executor u37 as finding F1 of route #583; false proofs at the int55 base and head). Witnesses witnesses-r583/u37/d01-d04 (FALSE proofs); d05 the Subscript control. See route583 doc F1. `_EMIT_IR_PROJ` also maps `guard` / `lower` / `upper` to `svalue_of` (unmeasured).

## Mechanism (base)
- Dict view: `_EMIT_IR_PROJ` mapped `value`, `guard`, `lower`, `upper` to `svalue_of` (`IrSub v _ -> v | _ -> IrOther ""`),
  used by `.get(k[, d])` (`_todict_emit_ir_projection`, `_lower_dict_get_call`), `x[k]` (subscript), the scoped
  `_match_field_decode_idiom` default; `c["pattern"]` read `svalue_of` too.
- Attribute view (`_handle_attribute_expr`, the emit_ir branch): after the string / list / scoped / 2-child tables, `.value`
  read `avalue_of` (IrAttr / IrSub only, route #583) and EVERY other attribute the `svalue_of` catch-all; the
  `.get("value") or .get("object")` idiom read `avalue_of`.
- So after a class test (`x.get("type") == "Starred"`, `x.kind == "SliceAccess"`, `isinstance(x, ast.Slice)`) the read is
  the sentinel `IrOther ""`, its kind is never `"Var"`, and `if ...: return 1` / `return 0` PROVED `\result == 0`.

## Repair (u38)
- `expressions.py`: `_EMIT_IR_PROJ` `value`/`lower`/`upper`/`guard` -> `irget_value_of` (Sub / Starred / NamedExpr /
  SliceAccess / MapSet; an Attribute WIRE node has `object`, not `value`), `irget_lower_of` / `irget_upper_of` (Slice,
  SliceN with its optional bounds), `irget_guard_of` (opaque); `c["pattern"]` -> `irget_pattern_of` (opaque); the scoped
  `_match_field_decode_idiom` `{}`-default read -> `irget_value_of`; the attribute catch-all -> `iratt_<attr>_of`
  (`_EMIT_IR_ATTR_ARMS`: one arm per constructor carrying the field as an emit_ir child, generated from the
  constructor table and the ADT, gated constructors keep their theory gate; `value` + the IrAttr object, `slice` + the
  IrSub index, `operand` = IrUnaryOp's child); an attribute with no arm is an opaque `val function iratt_<attr>_of`; the
  `.get("value") or .get("object")` idiom -> `iratt_value_of`. `_to_bool`'s always-present prefixes gain `(irget_` /
  `(iratt_` (behaviour unchanged, see FINDINGS T).
- `preamble.py`: one slot line after `svalue_of` in the FULL emit_ir theory. `Module6_WhyMLTranspiler.py::transpile`
  (twin `\trusted`): after the deferred-theory resolution, splice exactly the `irget_*` / `iratt_*` definitions the
  emitted text uses (none -> the slot line is deleted, byte-identical); the opaque-mirror deferral treats an
  `iratt_*` / `irget_*` use as a rich-accessor use. Proven lemma `size_irget_value_dec` (is_sub e -> size (irget_value_of
  e) < size e) keeps the Subscript recursion law the old read had.
- Mirror twins of every edited method are `\trusted` or absent (check-self-annotate-sync: 959 un-trusted mirror
  functions verbatim). No axiom (proof-axiom ledger 3), no new ADT arm.

## Witnesses (default model; `witnesses-r584/u38/` + `witnesses-r583/u37/`; each `__main__` run under CPython breaks the claim)
| witness | base bdab5f5f1 | HEAD |
|---|---|---|
| u37 d01-d04 dict `.get("value", {})` of Starred / MapSet / SliceAccess / NamedExpr | PROVED (false) | NOT PROVED (Timeout) |
| d11 `x["value"]`, d12 `.get("value")` no default (Starred) | PROVED (false) | NOT PROVED |
| a21-a24 `.value` of a node tested Starred / NamedExpr / SliceAccess / MapSet | PROVED (false) | NOT PROVED |
| u37 a05 `.slice` of `ast.Subscript`; s01 `.slice` of SliceAccess; s03 Subscript `.slice` vs `.value` | PROVED (false) | NOT PROVED |
| l03 / l04 `.lower` / `.upper` of Slice; l05 `isinstance(x, ast.Slice) and isinstance(x.lower, ast.Name)` | PROVED (false) | NOT PROVED |
| c21-c24 catch-all `.expr` (UnaryOp, Old), `.operand`, `.element` (CSLIn) | PROVED (false) | NOT PROVED |
| g01 dict `.get("guard", {})` after `.get("pattern") == "Or"` | PROVED (false) | NOT PROVED |
| u37 d05 Subscript dict value (control of the shape) | NOT PROVED | NOT PROVED |
| l01 / l02 dict `b = x.get("lower"/"upper", {})`, s02 dict `.get("slice", {})` | L3 type error (fail-closed) | L3 type error (unchanged) |
| f08 dict `.get("expr", {})` of Old | NOT PROVED (unmodelled key) | NOT PROVED |
28 false proofs at base, 0 at HEAD. Controls (corpus 9580-9584: dict Starred value, NamedExpr `.value`, `.slice` of
Subscript + SliceAccess, Slice `.lower`, Subscript dict value; two-sided bounds, several returns) PROVE at HEAD.
Corpus: 9550-9566 expected FAIL (all NOT PROVED at HEAD: postcondition Timeout, no type error), 9580-9584 PASS.

## Movers
- CORPUS byte-diff (own base sweep at bdab5f5f1 vs HEAD, both launched from the tree root, `bin/byte-diff-compare.py`
  once root `--new-source` the 22 new IDs, once pyref): root 12 MOVED, 0 GONE, 0 APPEARED -- 0748, 0880 (`svalue_of` ->
  `irget_value_of` under a Subscript test) and 9310, 9311, 9430-9435, 9440, 9441 (`avalue_of` -> `iratt_value_of`); M1:
  see EVIDENCE. pyref: 0 MOVED / GONE / APPEARED (2185/2185).
- MIRROR sweep (own base vs HEAD): 7 MOVED, 0 GONE, 0 APPEARED -- `module6_whyml/expressions` (dict-view and catch-all
  sites + defs), `frontend/Module5_IREmitter` (`avalue_of` -> `iratt_value_of`, `.slice` reads, 25 lines), `module6_whyml/
  statements` (2 sites: the attribute-receiver idiom and `.get("value")` under a Subscript|SliceAccess test -- the
  SliceAccess arm was itself a victim), `module6_whyml/types` (the idiom), `frontend/pure_ast` (`atom.lineno` /
  `atom.col_offset` in `_Parser._test_or_star_slice`: opaque), `module6_whyml/expr_ghost_collections` (`node.list`),
  `module6_whyml/expr_ghost_spec_ops` (`node.tuple`, `node.string`). stmt_control_flow, functions, core_ir_semantic,
  Module6_WhyMLTranspiler: unchanged. Whole-file proofs: expressions, statements, Module5, pure_ast OWED to the driver
  batch (driver decision); types / expr_ghost_collections / expr_ghost_spec_ops proved here; `--fun
  _parser__test_or_star_slice` (pure_ast) here: see EVIDENCE.

## FINDINGS (same family, measured, NOT repaired here -- the driver decided the scope)
- F-NODE (2-child / swap tables): `_EMIT_IR_NODE_ATTRS` routes `.dict/.key/.head/.tail/.left/.right/.lo/.hi/.size/.default`
  to IrBinOp's `left_of` / `right_of` (IrOther "" on every other constructor), and `_EMIT_IR_PROJ["index"]` = `sindex_of`
  (Subscript only): f01 `x.kind == "MapGet" and x.dict.kind == "Var"`, f02 HasKey `.key`, f03 Cons `.head`, f04 StrConcat
  `.left`, f05 ArrayEq dict `.get("left", {})`, f06 Nth dict `.get("index", {})` PROVE `\result == 0` at base AND HEAD
  (CPython 1). Repair direction: the same per-constructor arms (`_EMIT_IR_ATTR_ARMS` already lists them); it moves every
  mirror handler reading `.left` / `.right` (expressions, statements, ...), so it was left out of this landing.
- F-STR (string projectors): `_EMIT_IR_STR_ATTRS` / `_EMIT_IR_PROJ` string keys read one constructor family:
  f09 `.op` of UnaryOp, f10 dict `.get("op")` of UnaryOp, f11 `.name` of InGlobals, f12 `.var` of ArrayLen, f14 `.ctor`
  of CtorTest PROVE at base AND HEAD (CPython 1).
- T (truthiness): `_to_bool` lowers the truthiness of an always-present sub-node read (`svalue_of` / `avalue_of` / ... and
  now `irget_*` / `iratt_*`) to `true` inside a `@mutable_state` class: t01 `if x.get("value"):`, t02 `if x.value:`, t03
  `if x.get("guard"):` PROVE `\result == 1` at base AND HEAD (CPython 0 for an absent / None field).
- f07 (`.object` of a FieldGet, a string field in the real IR) PROVES at base and HEAD, but only for a faked receiver:
  CPython raises AttributeError on the real node, so it is not a false proof of the model's domain.

## EVIDENCE
