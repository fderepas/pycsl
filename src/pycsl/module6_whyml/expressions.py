from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from module6_whyml.identifiers import op_translate, whyml_ident, stable_hash, whyml_string_literal
from ir_schema import (
    expr_from_dict, _expr_from_dict_inner, OpaqueExpr, IR_TAG_ALIASES,
    NumberExpr, StringExpr, ResultExpr, NoneExpr, RawWhymlExpr, BoolExpr,
    UnknownPyExprExpr, SliceExpr, OldFieldExpr, StarredExpr, TupleExpr,
    ArrayLitExpr, ForallExpr, ExistsExpr, MapValueIsExpr, VarExpr, FieldGetExpr,
    DictLitExpr, ListCompExpr, SetCompExpr, DictCompExpr, ForallItemsExpr,
    SetAddExpr, SetRemoveExpr, SetMemExpr, NthExpr, MemExpr, ExprIR,
    MapSetExpr, SetCardExpr,
)

# Phase-B-expr: handlers migrated to accept a typed ExprIR node (rather than the
# wire dict). The `_expr_to_whyml` tail dispatch passes the typed `node` to these
# and the legacy dict to the rest; an OpaqueExpr (a node carrying extra
# attribution keys the class doesn't model, e.g. BinOp+act_name) is coerced to
# its typed class via `_expr_from_dict_inner` — safe because these handlers do
# not read attribution keys. Grows one handler at a time, byte-diff gated.
_TYPED_EXPR_HANDLERS = {
    "_handle_unaryop_expr",
    "_handle_old_expr",
    "_handle_at_expr",
    "_handle_named_expr_expr",
    "_handle_ifexpr_expr",
    # ghost-collection ops (map/set/list) — expr_ghost_collections.py
    "_handle_map_empty_expr",
    "_handle_map_get_expr",
    "_handle_map_set_expr",
    "_handle_map_eq_expr",
    "_handle_has_key_expr",
    "_handle_map_remove_expr",
    "_handle_set_empty_expr",
    "_handle_set_add_expr",
    "_handle_set_remove_expr",
    "_handle_set_mem_expr",
    "_handle_set_union_expr",
    "_handle_set_inter_expr",
    "_handle_set_diff_expr",
    "_handle_set_card_expr",
    "_handle_set_subset_expr",
    "_handle_set_eq_expr",
    "_handle_nil_expr",
    "_handle_cons_expr",
    "_handle_hd_expr",
    "_handle_tl_expr",
    "_handle_list_length_expr",
    "_handle_nth_expr",
    "_handle_mem_expr",
    "_handle_append_expr",
    # ghost spec ops (tuple/ctor/str/array) — expr_ghost_spec_ops.py
    "_handle_mktuple_expr",
    "_handle_fst_expr",
    "_handle_snd_expr",
    "_handle_proj_expr",
    "_handle_ctor_test_expr",
    "_handle_ctor_payload_expr",
    "_handle_strconcat_expr",
    "_handle_str_length_expr",
    "_handle_str_sub_expr",
    "_handle_ghost_copy_expr",
    "_handle_ghost_make_expr",
    # misc spec/expr handlers
    "_handle_fstring_expr",
    "_handle_attribute_expr",
    "_handle_subscript",
    "_handle_call_expr",
    "_handle_binop",
    "_handle_arrayeq_expr",
    "_handle_permutation_expr",
    "_handle_separated_expr",
    "_handle_valid2d_expr",
    "_handle_length2d_expr",
    "_handle_slice_access_expr",
    "_handle_arraylen_expr",
    "_handle_issorted_expr",
    "_handle_sum_node_expr",
    "_handle_ghost_copy_range_expr",
    "_handle_valid_expr",
    "_handle_setlit_expr",
    "_handle_lambda_expr",
    "_handle_in_globals_expr",
    "_handle_in_scope_expr",
}

# i-feel-good.md I-D: the ONE emit_ir reflection projection map + key classes, defined
# once and referenced by every reflection site (dotted `.get`, subscript `["k"]`, nested,
# and the string-typedness checks). A reflection key maps to its total projection over the
# `emit_ir` sum; string-valued keys yield a `string`, sub-node keys yield an `emit_ir`.
# ("field" is the FieldGet member-name — a string, routed like "attr"/"name".)
_EMIT_IR_PROJ = {
    "type": "kind_of", "name": "name_of", "attr": "name_of", "field": "name_of",
    "func": "func_of", "value": "svalue_of", "object": "object_of", "index": "sindex_of",
    "args": "args_of",   # resync-campaign.md R1: the args LIST → `array emit_ir`
    # cf6.md M1.1: match pattern/case keys — `pattern` (KIND) / `ctor` (NAME) are strings;
    # `captures` is a reflected node list (`args_of`); `body` is an OPAQUE stmt-list
    # (`stmts_of : → array int`); `guard` is a single node (`svalue_of`).
    "pattern": "kind_of", "ctor": "name_of", "captures": "args_of",
    # `alternatives` (an `Or` match-pattern's alternative sub-pattern LIST) joins the
    # node-list family on the same footing as `captures` — reflected `array emit_ir`,
    # no theory change. Reference lock: corpus 0893 (positive) / 0894 (negative twin).
    "alternatives": "args_of",
    # self-tcb-reduction (union/match cluster): the If-statement TEST sub-node
    # (`stmt.get("test", {})` in `_try_union_is_none_match`) → the opaque `test_of`
    # projector (emit_ir → emit_ir; see preamble.py). Byte-inert: no corpus program
    # nor other mirror reflects `.get("test")` on an emit_ir node.
    "test": "test_of",
    "body": "stmts_of", "guard": "svalue_of", "parts": "args_of", "elts": "args_of",
    "lower": "svalue_of", "upper": "svalue_of",   # 07-03-refactor R4: SliceExpr bound sub-nodes
    # tier3-p1 T3.1.2 (spike LAW 2): BinOp field projections — `op` is the operator
    # STRING (`op_of`); `left`/`right` are the SUB-NODES (`left_of`/`right_of`, → emit_ir).
    "op": "op_of", "left": "left_of", "right": "right_of",
    # orelse_of mini-M1: IfExpr's `orelse` (else sub-node) is UNAMBIGUOUS (used nowhere
    # else) → the table entry suffices. IfExpr's `body` (then sub-node) COLLIDES with the
    # If/For/While/Try stmt-list `body` (→ `stmts_of`, above); disambiguated at the
    # `.get(key, default)` call site by the default-argument shape (empty-dict `{}` default
    # → `body_of`; empty-list `[]`/no default → `stmts_of`), NOT here in the table.
    "orelse": "orelse_of",
}
# `pattern` is CONTEXT-DEPENDENT: SUBSCRIPT `c["pattern"]` → a sub-NODE (below); `.get("pattern")`
# → the KIND string (here). Different code paths read each tuple, so it appears in both.
_EMIT_IR_STR_KEYS = ("type", "name", "attr", "field", "func", "ctor", "pattern", "op")   # via `.get`
_EMIT_IR_NODE_KEYS = ("value", "object", "index", "pattern", "guard", "left", "right",
                      # self-tcb-reduction Layer-2: the method-call RECEIVER (`receiver_of`,
                      # over the certified IrMethodCall ctor) and the SliceAccess `slice`
                      # sub-node (`slice_of`) — so a local bound from `<emit_ir>.get("receiver")`
                      # / `.get("slice")` flow-types as emit_ir (the recognizer twin). Both are
                      # NEW keys read by 0 corpus programs and 0 other mirror handlers, so the
                      # flow-typing is byte-inert everywhere except the receiver recognizer.
                      # self-tcb-reduction (union/match cluster): the If-statement TEST
                      # sub-node — `test = stmt.get("test", {})` flow-types `test` as
                      # emit_ir so `test.get("op"/"left"/"right")` reflects (op_of/left_of/
                      # right_of). Read by 0 corpus programs / 0 other mirror handlers.
                      "receiver", "slice", "test")   # via subscript → node
# self-tcb-reduction T1.a: STRING-valued attribute reads on a base-`ExprIR` emit_ir node
# (`node.kind`/`node.var`/`node.op`/…, where the handler annotates `node: "ExprIR"` but accesses a
# concrete subclass's str field) → the discriminant/name projection. Non-listed attrs fall to the
# `svalue_of` sub-node default. @mutable_state-gated in `_handle_attribute_expr`/`_is_string_expr`.
# ghost-handler-cluster batch drain C: `arr` (GhostCopyExpr/GhostCopyRangeExpr's
# str-typed array-variable-name field, embedded directly — not through `self._e`,
# since it is not a sub-node in the wire format) joins the STRING-attr table on the
# same "reused projector, no theory change" footing as `var`/`base`/…; unambiguous
# (only these two subclasses declare `arr`, both at field position 1).
# ghost-handler-wall Q3a: `ctor` (CtorTestExpr/CtorPayloadExpr's str-typed
# constructor-tag field) joins the table on the same footing — unambiguous
# (only these two subclasses declare `ctor`, `_EMIT_IR_PROJ["ctor"]` already routes
# the legacy wire-dict `.get("ctor")` reflection through the same `name_of`).
_EMIT_IR_STR_ATTRS = {"kind": "kind_of", "var": "name_of", "op": "op_of",
                      "label": "name_of", "name": "name_of", "func": "func_of",
                      "base": "name_of", "base1": "name_of", "base2": "name_of",
                      "arr": "name_of", "ctor": "name_of",
                      # isinstance-on-emit_ir batch (self-tcb-reduction M5): `.id` on
                      # an already-lowered ExprIR child (`expr.value.id` in
                      # `_py_expr_attribute`) reads the IrVar name string — the same
                      # `name_of` projector `.var`/`.name` already route to (an
                      # IrVar's payload). Only fires when the receiver is emit_ir.
                      "id": "name_of",
                      # value-model campaign incr9: `.attr` on a BASE emit_ir node reads the
                      # IrAttr attr-name string (`name_of (IrAttr _ a) = a`) — the string-method
                      # receiver for `<emit_ir>.attr.lower()` (`_overload_type_name`). Byte-safe:
                      # the converted handlers that read `.attr` do so on a SPECIFIC `ast.Attribute`
                      # record (`expr.attr` record-field) or via the `bases_has_name` recognizer —
                      # never on a base `ExprIR` node — so no existing emission is perturbed.
                      "attr": "name_of"}
# 2-child-cluster mini-M1 (following the orelse_of precedent verbatim): SUB-NODE-valued
# attribute reads on a base-`ExprIR` emit_ir node for a 2-child ghost `ir_schema.ExprIR`
# dataclass (`MapGetExpr(dict, key)`, `HasKeyExpr(dict, key)`, `MapRemoveExpr(dict, key)`,
# `ConsExpr(head, tail)`) → the 1st declared dataclass field projects via `left_of`, the 2nd
# via `right_of` — REUSING IrBinOp's existing projectors + proven size-decrease lemmas
# (`preamble.py::_emit_exprir_theory`), not a new constructor. Each entry's position is
# UNAMBIGUOUS across every `ir_schema.ExprIR` subclass that declares it (`dict` is always the
# 1st field, `key` always the 2nd, across MapGetExpr/MapSetExpr/HasKeyExpr/MapRemoveExpr;
# `head`/`tail` only appear on ConsExpr) — unlike `elem`/`set`/`list`, whose position SWAPS
# between subclasses (`SetAddExpr(set, elem)` vs `SetMemExpr(elem, set)`; `NthExpr(list, ...)`
# vs `MemExpr(elem, list)`), so those are deliberately NOT added here (would need a
# per-subclass disambiguator, out of scope for this increment). Checked in
# `_handle_attribute_expr` before the `svalue_of` default, so `node.dict`/`node.key` (and
# `node.head`/`node.tail`) emit as DISTINCT terms instead of colliding on the single
# `svalue_of` catch-all.
# ghost-handler-cluster batch drain: `left`/`right` extend the same table. Every
# `ir_schema.ExprIR` subclass that declares BOTH names declares `left` immediately before
# `right` (verified across all 11: BinOpExpr, StrConcatExpr, ArrayEqExpr, PermutationExpr,
# MapEqExpr, SetUnionExpr, SetInterExpr, SetDiffExpr, SetSubsetExpr, SetEqExpr, AppendExpr) —
# `left` is always the 1st ExprIR-typed sub-node field, `right` always the 2nd (BinOpExpr's
# leading `op: str` is a string leaf, not a sub-node slot, so it does not perturb the
# left/right sub-node order). Position-unambiguous like `dict`/`key`/`head`/`tail` above.
# ghost-handler-cluster batch drain D (mini-M1, following left/right verbatim): `lo`/`hi`
# extend the same table. Every `ir_schema.ExprIR` subclass that declares BOTH names declares
# them at the SAME raw field position across all 5: IsSortedExpr, SumExpr, StrSubExpr,
# GhostCopyRangeExpr, SetCardExpr — `lo` is always field index 1 (right after a single
# leading field, str OR ExprIR-typed), `hi` always field index 2. Mapped by the SAME
# left_of/right_of pair (a 2-slot reuse, not a new constructor); the leading field (`base`/
# `arr`/`string`/`set`) is separately routed (str leaf → name_of, or left UNMAPPED to fall
# through to the `svalue_of` default) so no attr on a single node collides. `default`/`size`
# extend the table too: GhostMakeExpr's only 2 declared fields, `size` at index 0 → left_of,
# `default` at index 1 → right_of — the same 2-slot shape as dict/key, no 3rd field to route.
_EMIT_IR_NODE_ATTRS = {"dict": "left_of", "key": "right_of", "head": "left_of", "tail": "right_of",
                       "left": "left_of", "right": "right_of",
                       "lo": "left_of", "hi": "right_of",
                       "size": "left_of", "default": "right_of"}
# ghost-handler-wall Q2 (per-subtype swap family, oracle-proven BOUNDED —
# ghost-handler-wall-response.md §2, spiked axiom-free in gh-spike.mlw::
# Q1Projections h_faithful/h_swapped, both Valid at identical step counts).
# `elem`/`set`/`list`/`index` are deliberately NOT in `_EMIT_IR_NODE_ATTRS`
# above: their FIELD POSITION SWAPS across `ir_schema.ExprIR` subclasses
# (`SetAddExpr(set, elem)` vs `SetMemExpr(elem, set)`; `NthExpr(list, index)`
# vs `MemExpr(elem, list)`), so one global name->projector entry cannot
# faithfully serve both directions. The disambiguating key IS available: each
# of these handlers is dispatched on exactly ONE ExprIR subclass, and
# `_current_emitting_func` (set per-function in
# `functions.py::_emit_function`) already names the enclosing handler while
# its body is lowered. So the projector table here is keyed by (handler,
# attr), not by attr alone — and each per-handler sub-table is DERIVED from
# the subclass's OWN declared dataclass field order (idx0 -> left_of, idx1 ->
# right_of, the same 2-slot convention as dict/key, head/tail, left/right,
# lo/hi, size/default above), not hand-picked per attr name.
# ghost-handler-wall Q2 faithful-3rd-child re-do (map_set/set_card,
# ghost-handler-wall-response.md §2/§1.4, spiked axiom-free in
# gh-spike.mlw::Q1FaithfulThirdChild): idx2 -> `ter_thd_of`, the 3rd
# projector over the new GENERIC `IrTer3` constructor (preamble.py
# `_emit_exprir_theory`) — same idx0/idx1/idx2 schema-derived convention,
# extended by one slot. `MapSetExpr(dict, key, value)` and
# `SetCardExpr(set, lo, hi)` are the only 3-field ExprIR subclasses in the
# swap-family table, so idx0/idx1 route through `ter_fst_of`/`ter_snd_of`
# (NOT the shared left_of/right_of — a single node cannot be BOTH an IrBinOp
# and an IrTer3, so left_of/right_of would sentinel on an IrTer3-shaped node;
# ter_fst_of/ter_snd_of are the IrTer3-native equivalents).
_EMIT_IR_BASE_FIELDS = {f.name for f in dataclasses.fields(ExprIR)}


def _schema_swap_projectors(cls, slots: Tuple[str, ...] = ("left_of", "right_of")) -> Dict[str, str]:
    # `dataclasses.fields(cls)` includes INHERITED base-class fields (`kind`,
    # from `IRNode`) ahead of the subclass's own — exclude them so index 0/1/…
    # land on the subclass's OWN declared fields (`set`/`elem`, `elem`/`set`,
    # `list`/`index`, `elem`/`list`, `dict`/`key`/`value`, `set`/`lo`/`hi`),
    # matching the field order the report and the live handler bodies
    # actually read.
    _own = [f for f in dataclasses.fields(cls) if f.name not in _EMIT_IR_BASE_FIELDS]
    return {f.name: slots[i] for i, f in enumerate(_own) if i < len(slots)}


_EMIT_IR_HANDLER_SUBTYPE = {
    "_handle_set_add_expr": SetAddExpr,
    "_handle_set_remove_expr": SetRemoveExpr,
    "_handle_set_mem_expr": SetMemExpr,
    "_handle_nth_expr": NthExpr,
    "_handle_mem_expr": MemExpr,
}
# ghost-handler-wall Q2 faithful-3rd-child re-do: the two 3-field ghost
# handlers get their OWN 3-slot sub-table (idx0/idx1/idx2 -> ter_fst_of/
# ter_snd_of/ter_thd_of), kept separate from `_EMIT_IR_HANDLER_SUBTYPE`
# above (whose 2-slot subclasses must keep resolving through left_of/
# right_of — the ALREADY-faithful, byte-identical mapping for the swap
# family) so extending this table never perturbs the 2-child one.
_EMIT_IR_HANDLER_SUBTYPE_3 = {
    "_handle_map_set_expr": MapSetExpr,
    "_handle_set_card_expr": SetCardExpr,
}
_EMIT_IR_HANDLER_ATTR_PROJ = {
    _hname: _schema_swap_projectors(_hcls)
    for _hname, _hcls in _EMIT_IR_HANDLER_SUBTYPE.items()
}
_EMIT_IR_HANDLER_ATTR_PROJ.update({
    _hname: _schema_swap_projectors(_hcls, ("ter_fst_of", "ter_snd_of", "ter_thd_of"))
    for _hname, _hcls in _EMIT_IR_HANDLER_SUBTYPE_3.items()
})
# isinstance-on-CSL-class recognizer (self-tcb-reduction M5, _csl_old): `.object`/
# `.field` DOTTED reads on the emit_ir node `node.expr` (a CSLFieldAccess modeled as
# IrFieldGet — established by the enclosing `isinstance(node.expr, CSLFieldAccess)`
# guard). Both project to LEAF STRINGS via the FieldGet-specific `fgobject_of`/`field_of`
# — NOT the generic `object_of` (which is IrAttr's emit_ir SUB-node, the wrong type-class
# for FieldGet, risk-6 asymmetry). Scoped to `_csl_old` via `_current_emitting_func` so
# every other handler's `.object` (an IrAttr sub-node read) is unperturbed. Hand-specified
# (not `_schema_swap_projectors`-derived): these are cross-constructor string projectors,
# not the idx0/idx1 left_of/right_of dataclass-order convention.
_EMIT_IR_HANDLER_ATTR_PROJ.update({
    "_csl_old": {"object": "fgobject_of", "field": "field_of"},
})
# SAugAssign/SFieldAugAssign/SArraySet increment (self-tcb-reduction M5): the
# `_py_stmt_augassign` body reads THREE distinct sub-nodes/leaves off `stmt.target`
# (an emit_ir node whose concrete shape is pinned per-branch by an `isinstance`
# guard): `.value` — the self-field branch's Attribute OBJECT (IrAttr) AND the
# subscript branch's Subscript ARRAY (IrSub), unified by `avalue_of`; `.slice` — the
# subscript INDEX child (`sindex_of`, IrSub's 2nd arg); `.attr` — the self-field NAME
# string (`name_of`, which returns IrAttr's attr leaf). Scoped to `_py_stmt_augassign`
# via `_current_emitting_func` so every other handler's `.value` (the `svalue_of`
# subscript-only default) is unperturbed. `.id` stays the global `_EMIT_IR_STR_ATTRS`
# `name_of` (checked first).
_EMIT_IR_HANDLER_ATTR_PROJ.update({
    "_py_stmt_augassign": {"value": "avalue_of", "slice": "sindex_of",
                           "attr": "name_of"},
})
# value-model campaign increment 2 (P1 — SCOPED `.slice`→sindex_of for the annotation
# walkers): a type-annotation node's `.slice` is the type ARGUMENT (a Subscript's index
# child, `sindex_of`), NOT the `.value` head (`svalue_of`, the default). Global `.slice`
# has no entry, so it defaults to svalue_of — WRONG for `_typeddict_field_type`'s
# `Required[T].slice`(=T, not Required). SCOPED via `_current_emitting_func` (endswith
# match, line ~6262) so it fires ONLY inside this named mirror handler — corpus-guaranteed-
# inert (no corpus program defines it) and it does NOT perturb the existing `.slice`-readers
# (`_py_expr_subscript`, `_py_stmt_assign`, which pass `.slice` to `_py_expr_to_ir`, an
# emit_ir-local path).
_EMIT_IR_HANDLER_ATTR_PROJ.update({
    "_typeddict_field_type": {"slice": "sindex_of"},
})
# value-model campaign increment 5 (combined): P1-scoped `.slice`->sindex_of for the two
# converted Optional[str] annotation walkers. `_normalize_final_annotation`'s `Final[T].slice`
# and `_m5_get_dict_key_type`'s `Dict[K,V].slice` both read the type ARGUMENT (sindex_of),
# NOT the `.value` head. SCOPED via `_current_emitting_func` -> corpus/consumer-inert.
_EMIT_IR_HANDLER_ATTR_PROJ.update({
    "_normalize_final_annotation": {"slice": "sindex_of"},
    "_m5_get_dict_key_type": {"slice": "sindex_of"},
    "_m5_get_dict_value_type": {"slice": "sindex_of"},
})
# value-model campaign increment 10 (loop-over-irlist): the two legacy leaf resolvers read
# `inner = annotation.slice` (the `Union[...].slice` type-arg tuple) then `for elt in inner.elts`.
# `.slice`->sindex_of (P1) so `inner` is the tuple; `inner.elts`-> the IrMkTupleN irlist loop.
_EMIT_IR_HANDLER_ATTR_PROJ.update({
    "_m5_get_type_name_legacy": {"slice": "sindex_of"},
    "_field_type_from_annotation": {"slice": "sindex_of"},
})
# 7b (self-tcb-reduction L4b): `_collect_type_params`'s legacy `Generic[T]` branch reads
# `b.slice` (the Subscript type-arg, `sindex_of`) off a `for b in node.bases` emit_ir loop
# var — NOT the `.value` head. SCOPED via `_current_emitting_func` -> corpus-inert.
_EMIT_IR_HANDLER_ATTR_PROJ.update({
    "_collect_type_params": {"slice": "sindex_of"},
})
# V1 pyconst-dispatch (self-tcb-reduction M5, B-bucket): `_classify_literal_value`'s
# `v = elt.value` reads the CONSTANT-leaf VALUE off `elt` (an `ast.Constant` self-annotated
# as the emit_ir ADT, established by the enclosing `isinstance(elt, ast.Constant)` guard).
# `.value` on emit_ir defaults to `svalue_of` (the Subscript head sub-node, an emit_ir) —
# WRONG here: a Constant's value is a Python SCALAR, faithfully the `pyconst_val` projection
# `const_pyval_of elt`. SCOPED via `_current_emitting_func` so every other handler's `.value`
# (the `svalue_of` default) is unperturbed — corpus + every other mirror byte-identical.
_EMIT_IR_HANDLER_ATTR_PROJ.update({
    "_classify_literal_value": {"value": "const_pyval_of"},
})
# _const_int_value pyconst-dispatch (self-tcb-reduction M5, B-bucket): the UnaryOp OPERAND
# sub-node projector. `value.operand` (the `-N` inner node) reads the IrUnaryOp's operand
# emit_ir child, faithfully `unaryop_operand_of value` (the NEW axiom-free accessor). `.op`
# stays the GLOBAL `op_of` string-leaf (no scoped entry — the isinstance(value.op, ast.USub)
# recognizer wraps it as `unaryop_op_of` directly) and `.value` stays the GLOBAL `svalue_of`
# (the `int(value.value)` / `isinstance(value.value, int)` recognizers project it themselves).
# SCOPED via `_current_emitting_func` -> corpus + every other mirror byte-identical.
_EMIT_IR_HANDLER_ATTR_PROJ.update({
    "_const_int_value": {"operand": "unaryop_operand_of"},
})
# self-tcb-reduction Layer-2: SCOPED `.get(key)`-projectors for the method-receiver /
# slice recognizer `_match_field_decode_idiom`. `receiver`->receiver_of (the certified
# Layer-2 method-call receiver), `slice`->slice_of (an IrSliceAccess's slice sub-node),
# `lower`/`upper`/`step`->the IrSliceN optional-bound unwrappers (an ABSENT bound reads
# back the honest `IrNone` so the recognizer's `lower is None` / `step is not None`
# guards discriminate REAL presence). SCOPED via `_current_emitting_func` so the GLOBAL
# `lower`/`upper`->svalue_of (the R4 SliceExpr bound readers `_slice_array_or_opaque` /
# `_handle_slice_access_expr`, which pass bounds to the trusted int-param `_expr_to_whyml`)
# stay byte-identical. This is a `.get`-KEY table (distinct from `_EMIT_IR_HANDLER_ATTR_PROJ`,
# which scopes ATTRIBUTE reads); consulted at the dotted-`.get` emit_ir projection site.
_EMIT_IR_GET_KEY_PROJ_BY_FUNC = {
    "_match_field_decode_idiom": {
        "receiver": "receiver_of", "slice": "slice_of",
        "lower": "lower_of", "upper": "upper_of", "step": "step_of",
    },
    # self-tcb-reduction _field_type_of: the FieldGet-branch reads `attr_ir.get("object")`
    # / `attr_ir.get("field")` are the FieldGet LEAF STRINGS (`fgobject_of`/`field_of`) —
    # the object NAME and field NAME, NOT the generic emit_ir sub-node `object_of` (which
    # is the IrAttr receiver, the wrong type-class for FieldGet; risk-6 asymmetry). The
    # Attribute-branch `.get("value") or .get("object")` receiver read is handled WHOLESALE
    # by `_recognize_attr_receiver_idiom` (→ `avalue_of`), so it never hits this scope —
    # leaving these two entries to serve ONLY the FieldGet standalone reads. SCOPED via
    # `_current_emitting_func` so every other `.get("object")`/`.get("field")` is byte-inert.
    "_field_type_of": {"object": "fgobject_of", "field": "field_of"},
    # self-tcb-reduction _namedtuple_positional_access: `index_ir.get("value")` (NO default)
    # after a `type == "Number"` guard reads the Number leaf's INT payload (`num_of`), NOT
    # the `svalue_of` emit_ir sub-node. An empty scoped entry is enough — it makes
    # `_scoped2 is not None`, so the `.get("value")` disambiguation below routes to `num_of`
    # (no empty-dict default). Every other key falls through to the global table. SCOPED via
    # `_current_emitting_func` -> corpus/other-mirror byte-inert.
    "_namedtuple_positional_access": {},
    # self-tcb-reduction _typeddict_record_literal (cap-2): `expr.get("keys", [])` /
    # `expr.get("values", [])` on the DictLit emit_ir node project the two child irlists
    # (`dictlit_keys_of`/`dictlit_values_of`), NOT the opaque `expr_get_2 <hash>` list-
    # default facade. SCOPED via `_current_emitting_func` -> corpus/other-mirror inert.
    "_typeddict_record_literal": {"keys": "dictlit_keys_of", "values": "dictlit_values_of"},
}
# self-tcb-reduction Layer-2: SCOPED extra emit_ir-NODE keys for the recognizer's
# flow-typing. Globally `lower`/`upper`/`step` are NOT node keys (the R4 SliceExpr readers
# `_slice_array_or_opaque`/`_handle_slice_access_expr` read `sl.get("lower")` as a bare
# truthiness test / pass `sl["lower"]` to the trusted int-param `_expr_to_whyml`, and must
# stay byte-identical). But inside `_match_field_decode_idiom` a `lower_ir = sl.get("lower")`
# local IS an emit_ir sub-node (unwrapped from IrSliceN via `lower_of`, checked `is None`,
# passed to `_static_width(ExprIR)`). Scoped via `_current_emitting_func` so the flow-typing
# extension is confined to this recognizer.
_EMIT_IR_EXTRA_NODE_KEYS_BY_FUNC = {
    "_match_field_decode_idiom": ("lower", "upper", "step"),
}
# value-model campaign increment 5 (primitive a — faithful IrMkTupleN element access): a
# `Dict[K,V]` annotation slice lowers to an **`IrMkTupleN`** (the variadic tuple carrying the
# MODELLED `elts_of` irlist), NOT the binary `IrTuple`. So the typed `.elts` reads route to the
# modelled irlist: `is_mktuple` / `irlen (elts_of x)` / `irnth i (elts_of x)` (NOT `is_tuple`/
# `elt{i}_of`/opaque `args_of`, which are dead/vacuous on an IrMkTupleN). SCOPED to these
# handlers via `_current_emitting_func` -> corpus- and consumer-inert.
_MKTUPLE_ELTS_HANDLERS = ("_m5_get_dict_key_type", "_m5_get_dict_value_type",
                          "_m5_get_type_name_legacy", "_field_type_from_annotation",
                          # value-model-return-wall R1: `_extract_generic_arg_names`'s
                          # `Generic[T, U]` slice is the SAME variadic `IrMkTupleN` as a
                          # `Dict[K,V]` slice, so `isinstance(slice_node, ast.Tuple)` must
                          # lower to `is_mktuple` (the default `is_tuple` is dead-false on it)
                          # and `slice_node.elts` to the modelled `elts_of` irlist (real
                          # emit_ir elements → `name_of elt`). Same shape-checked lowering,
                          # name-scoped for corpus byte-inertness.
                          "_extract_generic_arg_names")
from module6_whyml.struct_format import parse_format
from module6_whyml.expr_ghost_collections import GhostCollectionOpsMixin
from module6_whyml.expr_ghost_spec_ops import GhostSpecOpsMixin


class ExpressionEmissionMixin(GhostCollectionOpsMixin, GhostSpecOpsMixin):
    """Expression-emission dispatch: every IR expression-shape `_handle_*_expr`
    handler routed via `_EXPR_DISPATCH` on the facade, plus the orchestration
    entrypoints (`_expr_to_whyml`, `_expr_to_whyml_string_ctx`) and the shared
    helpers (`_to_bool`, `_coerce_*`, `_match_pattern_cond`, ...). Mixed into
    Module6_WhyMLTranspiler. `_EXPR_DISPATCH` stays on the facade as a class
    attribute — moving it would force a circular import.
    """

    _BITWISE_FOLD_OPS = {
        "&": lambda a, b: a & b, "|": lambda a, b: a | b, "^": lambda a, b: a ^ b,
        "<<": lambda a, b: a << b, ">>": lambda a, b: a >> b, "**": lambda a, b: a ** b,
    }
    _BITWISE_FN_NAMES = {
        "&": "bit_and", "|": "bit_or", "^": "bit_xor",
        "<<": "bit_lshift", ">>": "bit_rshift", "**": "py_pow",
    }

    def _e(self, ir: Dict, lr: Set[str]) -> str:
        """Shorthand for _expr_to_whyml within ghost handlers."""
        return self._expr_to_whyml(ir, lr)

    def _whyml_string_literal(self, s: str) -> str:
        """A Python string → its WhyML double-quoted string literal, backslash and
        double-quote escaped. Pure (`assigns \\nothing`). Extracted (07-03-refactor R5)
        from the duplicated inline escaper in `_handle_var_expr` / `_call_named_builtins`."""
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    def _to_bool(self, whyml_str: str, ir_expr: Dict[str, Any]) -> str:
        """Coerce a WhyML expression to bool if it might be int.
        Comparison operators and bool literals are already bool.
        Calls to isinstance_check, hasattr_check are already bool.
        Other expressions (int) need `<> 0` coercion."""
        t = ir_expr.get("type", "")
        op = ir_expr.get("op", "")
        # self-tcb-reduction _typeddict_field_access (a): truthiness of a DOUBLED hval
        # `.get` read (`if self._record_types[sym].get("is_typeddict"):`) — the projected
        # value is an `hval` whose Python-truthiness is `hval_truthy`, NEVER the int `<> 0`
        # coercion (the DOUBLED read otherwise projects a `string`, and `<string> <> 0` is
        # an L3-tc type error). Re-lower the `.get` with the raw-hval flag, then apply
        # `hval_truthy`. Gated on a pyval `.get` receiver -> corpus/mirror byte-inert (no
        # `Dict[str, PyVal]` `.get` in a corpus condition).
        if (t == "Call" and getattr(self, "_last_hval_get_str", None) == whyml_str
                and getattr(self, "_last_hval_get_raw", None)):
            return f"(hval_truthy {self._last_hval_get_raw})"
        # `_compute_return_type` PATH(b): truthiness of an INLINE pyval `.get`
        # (`if func.get("abstract")`) is `hval_truthy`, NEVER the int `<> 0` coercion
        # (an hval has no int value -> `<hval> <> 0` is an L3-tc error). Per-method
        # scoped -> byte-inert for the corpus and every other mirror.
        if (self._emitting_compute_return_type()
                and self._expr_is_pyval(ir_expr if isinstance(ir_expr, dict) else {})):
            return f"(hval_truthy {whyml_str})"
        # opaque-nested-map-reader SPLIT form: truthiness of an inner-alias local
        # (`if _rt` / `_rt and …` where `_rt = getattr(self, "_record_types", {}).get(tag)`)
        # is membership of the OUTER key — `<base>_mem <tag> : bool` — not the int `<> 0`
        # coercion (the local has no int value; it aliases `record_types[tag]`).
        if t == "Var" and ir_expr.get("name") in getattr(self, "_opaque_selfmap_inner_aliases", {}):
            _osm = self._opaque_selfmap_inner_mem(ir_expr.get("name"), set(), False, None)
            if _osm is not None:
                return _osm
        # W8 capability (ii): truthiness of the `*vals: str` vararg param is Python
        # tuple truthiness — NON-EMPTINESS of the argument sequence. `not vals` is
        # exactly "no explicit values were passed", the guard the `at_name`/`at_bs`
        # predicates use to accept ANY token of the kind. The default int `<> 0`
        # coercion is a type error here (`seq string` vs `int`) and semantically
        # meaningless. Gated on `_vararg_str_param`.
        if (t == "Var" and ir_expr.get("name")
                and ir_expr.get("name") == getattr(self, "_vararg_str_param", None)):
            return f"(Seq.length {whyml_ident(ir_expr['name'])} > 0)"
        # self-tcb-reduction T1.a: `if subst:` on a dict/set param (an `Optional[Dict]` modeled as
        # `map` — None ≡ empty) is the present-guard before `name in subst`; a sound over-approx
        # for the type-safety+frame contract is `true` (the `in` does the real check). @mutable_state.
        if (t == "Var"
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and getattr(self, "_current_symbol_table", {}).get(ir_expr.get("name"))
                in ("dict", "set", "frozenset")):
            return "true"
        # self-tcb-reduction Tier-5 (union/match cluster): truthiness of a nested-map local
        # (`if not vinfo:` where vinfo : `map string (option hval)`) — a `map` has no int
        # value, so the default `<> 0` is a type error. Python's `not <empty map>` guards the
        # None-return; a sound over-approx for the type-safety+frame contract is `true` (the
        # real projection happens in the returned tuple). Gated on `_hvalmap_local_vars`.
        if t == "Var" and ir_expr.get("name") in getattr(self, "_hvalmap_local_vars", {}):
            return "true"
        # self-tcb-reduction Tier-5 (union/match cluster C4): truthiness of a pyval LOCAL
        # (`if payload and …` where payload : `hval` = `ctor.get("payload", [])`) is the
        # heterogeneous value's Python-truthiness — `hval_truthy`, NEVER the int `<> 0`
        # (an hval has no int value). Gated on `_pyval_locals`.
        if t == "Var" and ir_expr.get("name") in getattr(self, "_pyval_locals", set()):
            return f"(hval_truthy {whyml_ident(ir_expr['name'])})"
        # resync-campaign.md R1: `val_ir.get("args")` lowers to `(args_of …)` : `array emit_ir`
        # — a truthiness (`if not val_ir.get("args")` = "no args") is array-emptiness, never the
        # int `<> 0` coercion. @mutable_state emit_ir reflection only.
        if whyml_str.startswith("(args_of "):
            return f"(Array.length {whyml_str} <> 0)"
        # 07-03-refactor R4: `if <emit_ir sub-node>:` (an Optional[ExprIR] field, e.g.
        # `if sl.get("lower")`) is a present-guard; the sub-node is always-present in the model, so
        # `true` is a sound over-approx for the type-safety+frame contract. @mutable_state.
        if (getattr(self, "_current_self_type", None) in getattr(self, "_mutable_state_classes", set())
                and any(whyml_str.startswith(p) for p in
                        ("(svalue_of ", "(object_of ", "(sindex_of ", "(arg0_of "))):
            return "true"
        # cf6.md M1.6: `if existing_caps:` on an emit_ir-element ARRAY LOCAL is array-emptiness.
        if (t == "Var"
                and getattr(self, "_array_elem_types", {}).get(ir_expr.get("name")) == "emit_ir"):
            return f"(Array.length ({whyml_str}) <> 0)"
        # cf6.md M1.6: `if wb.strip():` — a STRING truthiness is non-emptiness. @mutable_state.
        if (getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and self._is_string_expr(ir_expr)):
            self._add_abstract_op(
                "val str_eq_op (a b: string) : bool\n"
                "    ensures { result <-> (a = b) }")
            return f'(not (str_eq_op {whyml_str} ""))'
        # Already boolean: comparisons, not, bool literals, isinstance
        if t == "BinOp" and op in ("==", "!=", "<", ">", "<=", ">=", "in", "not in"):
            return whyml_str
        if t == "BinOp" and op in ("and", "or") and self._in_spec:
            # In spec context, and/or use && / || which are already bool
            return whyml_str
        if t == "UnaryOp" and op == "not":
            return whyml_str
        # `\old(e)` / `e @label` is boolean iff its inner expression is — recurse so
        # `\old(x < 0)` is not int-coerced (it underlies `complete`/`disjoint`).
        if t in ("Old", "At"):
            return self._to_bool(whyml_str, ir_expr.get("expr", {}))
        if t == "Bool":
            # In body context, Bool emits 1/0 but we need true/false for formulas
            if whyml_str == "1":
                return "true"
            if whyml_str == "0":
                return "false"
            return whyml_str
        if t == "Call" and ir_expr.get("func", "") in ("isinstance", "hasattr", "any", "all"):
            # `any(...)`/`all(...)` lower to the bool-returning `any_1`/`all_1` vals — a
            # truthiness `if any(...)` / `not any(...)` must use them directly, never the
            # int `(… <> 0)` coercion (bool <> int type error). No corpus driver uses
            # `any`/`all` in a truthiness position, so this is byte-identical.
            return whyml_str
        # inductive.md: a predicate application `p(args)` is already a formula (Why3
        # `predicate`), not an int — never `<> 0`-coerce it (e.g. inside `and`/`or` in a
        # reflection inversion lemma `… or (n >= 2 and even(n - 2))`).
        if t == "Call" and ir_expr.get("func", "") in getattr(self, "_inductive_preds", set()):
            return whyml_str
        if t in ("Exists", "Forall", "Compare"):
            return whyml_str
        # Ghost set/map predicates already return bool — no <> 0 needed
        if t in ("SetMem", "SetSubset", "SetEq", "MapEq", "HasKey"):
            return whyml_str
        # Array locals can't be compared with <> 0; emit true (always allocated)
        if t == "Var":
            name = ir_expr.get("name", "")
            # self-ir-schema.md IR4: a seq-promoted list local (`seq_parts = []; .append`)
            # is truthy iff non-empty — `Seq.length x <> 0` (the seq counterpart of the
            # array-length truthiness). @mutable_state path (via _seq_locals membership).
            if (name in getattr(self, "_seq_locals", set())
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())):
                return f"(Seq.length {whyml_str} <> 0)"
            if name in self._array_locals:
                return "true"
            # no-more-int emitter L4c: a list/array-typed var (`array int`, e.g. the
            # `rest: List[...]` param) is truthy iff non-empty — `Array.length x <> 0`,
            # the faithful Python list-truthiness — not the int `x <> 0` (a type error
            # on an array). Keyed on the SAME signals that lower the var to `array int`
            # (`_current_array1d_params` or a `list`/`bytes`/`bytearray` symbol type), so
            # `Array.length` is well-typed exactly when they fire. Byte-identical: a
            # corpus `if <array_var>:` would otherwise emit the ill-typed `<> 0`, so none
            # exists to change.
            if (name in getattr(self, "_current_array1d_params", set())
                    or getattr(self, "_current_symbol_table", {}).get(name)
                    in ("list", "bytes", "bytearray")
                    # self-ir-schema.md IR4 / list-comp: a comprehension-bound array local
                    # (`shared_for_mutex`) is truthy iff non-empty — recognized via the
                    # element-type map (@mutable_state; empty for the corpus).
                    or name in getattr(self, "_array_elem_types", {})
                    # self-tcb-reduction (union/match cluster): an inline `array int` temp
                    # (`orelse = stmt.get("orelse", []) or []`, from `_collect_array_var_
                    # assigns`) is truthy iff non-empty — `if orelse:` before the else-arm
                    # `_stmts_to_whyml`. Keyed on the SAME set that let-binds it `array int`.
                    or name in getattr(self, "_inline_array_temps", set())):
                return f"(Array.length {whyml_str} <> 0)"
            # typed-ir-for-b-ceiling.md §13: a STRING var (`rest_code = self._stmts_
            # to_whyml(...)`) is truthy iff non-empty — `String.length s <> 0`, the
            # faithful Python str-truthiness, not the ill-typed int `s <> 0`. Keyed on
            # the same signals that lower the var to `string`; byte-identical (a corpus
            # `if <str_var>:` would otherwise emit the ill-typed `<> 0`, so none exists).
            if (name in getattr(self, "_string_local_vars", set())
                    or getattr(self, "_current_symbol_table", {}).get(name)
                    in ("str", "string")):
                if self._in_spec:
                    return f"(String.length {whyml_str} <> 0)"
                self._add_abstract_op(
                    "val str_length_op (s: string) : int\n"
                    "    ensures { result = (String.length s) }")
                return f"(str_length_op {whyml_str} <> 0)"
            # typed-ir §19: an emit_ir local (`if assume_inv:` on an `Optional[ExprIR]`)
            # is truthy iff present — modeled always-present (`true`), like the emit_ir
            # `is None` comparison; sound for the type-safety+frame contracts (both arms
            # type-check, no self-field write). Gated by the emit_ir tags.
            if (name in getattr(self, "_emit_ir_local_vars", set())
                    or self._is_emit_ir_expr(ir_expr)):
                return "true"
        # parser-vein gap-1b (Optional-truthiness-in-condition): an `Optional[OBJECT]`
        # `<e>` (a record-payload option — `_Tok`, NO `__bool__`) in a boolean condition
        # (`if <e>:`/`while <e>:`/`and`/`or`/`not <e>`) is Python-true iff `<e> is not
        # None` — the is-Some discriminant of its synthesized `_union_*` type. Never the
        # int `<> 0` coercion (a `_union_*` vs int L3-tc error, the observed
        # `_parse_qualname` `.mlw` failure). SCOPE: record-payload Some-arm only; an
        # `Optional[int]`/`Optional[str]` (falsy-zero/empty) union is a DIFFERENT rule,
        # DEFERRED by the record-payload gate in `_optional_object_union_none_ctor`.
        _none_ctor = self._optional_object_union_none_ctor(ir_expr)
        if _none_ctor is not None:
            return f"(match {whyml_str} with {_none_ctor} -> false | _ -> true end)"
        # Optional[str]-truthiness (dict-value-nu lever): `if nu:` / `nu and …` on an
        # `Optional[str]` (a `_union_*` with a single `str` Some-arm — the `Optional[str]`
        # PARAM lowering) is Python-true iff `nu is not None AND nu != ""`. Option-unwrap
        # to the string-emptiness test on the carried string, never the int `<> 0`
        # coercion (a `_union_*` vs int L3-tc error, the observed `_dv_store_value`
        # `.mlw` failure). Faithful (`Some "" ` stays falsy, like Python). Body context
        # only (`str_eq_op` is a program val). Corpus-inert: no corpus program takes the
        # truthiness of an `Optional[str]`.
        _ostr_ctor = self._optional_str_union_ctor(ir_expr)
        if _ostr_ctor is not None and not self._in_spec:
            self._add_abstract_op(
                "val str_eq_op (a: string) (b: string) : bool\n"
                "    ensures { result <-> (a = b) }")
            return (f'(match {whyml_str} with {_ostr_ctor} _s '
                    f'-> (not (str_eq_op _s "")) | _ -> false end)')
        # self-tcb-reduction (audit-report list-field truthiness): the truthiness of a
        # record ARRAY-typed FIELD access (`if self.<listfield>:` — a `List[...]`/tuple
        # field lowered to `array int`) is Python list-truthiness = NON-EMPTINESS,
        # `Array.length x <> 0`, never the int `x <> 0` coercion (an `array int` vs int
        # L3-tc type error — the observed `auditreport__exit_code` `.mlw` failure).
        # Byte-inert: a corpus `if self.<arrayfield>:` would ALSO emit the ill-typed
        # `<> 0` and fail L3-tc, so no passing corpus program can contain one. This is
        # the record-field counterpart of the array-VAR truthiness rule above.
        if t in ("Attribute", "FieldGet"):
            _ft = self._field_type_of(ir_expr)
            if _ft in ("list", "tuple"):
                return f"(Array.length ({whyml_str}) <> 0)"
        # Coerce int → bool
        return f"({whyml_str} <> 0)"

    def _optional_object_union_none_ctor(self, ir_expr: Dict[str, Any]) -> Optional[str]:
        """parser-vein gap-1b: the None-arm constructor name of `ir_expr`'s synthesized
        `_union_*` type WHEN that Optional wraps an OBJECT/record payload (a single
        `Some`-arm whose payload names a declared RECORD type, e.g. `Optional[_Tok]`),
        else None.

        Recognizes two condition-position shapes: a `Var` whose symbol-table type is a
        `_union_*` (an `Optional[OBJECT]` LOCAL read in a guard) and a same-class
        `self.<m>(...)` `Call` returning `Optional[OBJECT]` (a guard method, e.g.
        `accept_op`; its synthesized `-> Optional[τ]` return union is named `_union_<m>_<idx>`
        after the method scope, resolved here from `_variant_types`). The record-payload
        gate DEFERS `Optional[int]`/`Optional[str]` (falsy-value truthiness — a different
        rule) and any multi-`Some`-arm union (not a plain Optional)."""
        candidate_symtypes: List[str] = []
        t = ir_expr.get("type", "")
        if t == "Var":
            st = getattr(self, "_current_symbol_table", {}).get(ir_expr.get("name"))
            if isinstance(st, str) and st.startswith("_union_"):
                candidate_symtypes.append(st)
        elif t == "Call":
            func = ir_expr.get("func", "")
            if isinstance(func, str) and func.startswith("self."):
                # The method's `-> Optional[τ]` return union is synthesized (Module5) as
                # `_union_<safe(method)>_<idx>` after the method's own scope name. Resolve
                # it by that scope prefix (the cross-reference return-type map defaults a
                # union return to `int`, so it cannot serve this lookup).
                method_tail = func[len("self."):]
                safe = "".join(c if c.isalnum() else "_" for c in method_tail) or "anon"
                prefix = f"_union_{safe}_"
                for vname in getattr(self, "_variant_types", {}):
                    if (isinstance(vname, str) and vname.startswith(prefix)
                            and vname[len(prefix):].isdigit()):
                        candidate_symtypes.append(vname)
        for symtype in candidate_symtypes:
            none_ctor, some_ctors = self._union_ctors(symtype)
            # A plain Optional[τ] has exactly one Some-arm + the nullary None-arm.
            if none_ctor is None or len(some_ctors) != 1:
                continue
            # OBJECT/record-payload gate: the Some-arm's single payload names a declared
            # record type — never int/str/bool/float/list/dict (those carry falsy-value
            # truthiness, a rule this feature deliberately defers).
            cinfo = getattr(self, "_constructors", {}).get(some_ctors[0], {})
            payload = cinfo.get("payload", [])
            if len(payload) != 1 or payload[0] not in getattr(self, "_record_types", {}):
                continue
            return none_ctor
        return None

    @staticmethod
    def _coerce_str_arg(whyml_str: str) -> str:
        """Convert a WhyML string literal to an int hash for abstract val arguments."""
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(stable_hash(whyml_str))
        return whyml_str

    def _materialize_if_seq(self, whyml_str: str, arg_ir: "ExprIR") -> str:
        """L2 (os-bodyvc-spec): if `arg_ir` is a seq-promoted local Var, bridge it seq→array with
        `materialize` so it can flow into an `array int` slot (e.g. `bytes(parts)`,
        `_write_entry(p, slot, n, parts)`). The return-arr `materialize` val is `seq int -> array int`
        (length+element preserving), emitted on demand. Non-seq args are returned unchanged."""
        if (isinstance(arg_ir, dict) and arg_ir.get("type") == "Var"
                and arg_ir.get("name") in getattr(self, "_seq_locals", set())):
            self._materialize_bridge()
            return f"(materialize {whyml_str})"
        return whyml_str

    @staticmethod
    def _array_coerce_arg(whyml_str: str) -> str:
        """Coerce an arbitrary WhyML expression to an `array int`. Used
        when abstract vals (`any_1`, `all_1`, `sorted_1`, `list_new`)
        expect an array but the actual arg is an int — typically because
        the IR dropped an unsupported iterable shape (generator
        expression, comprehension, variadic *args) to a scalar. A
        length-1 placeholder array works because the abstract vals have
        no axioms about their input contents.

        Recognises explicit array-shaped expressions and leaves them
        alone: `Array.make ...`, `Array.get ...`, `sorted_1 ...`, bare
        identifiers we can't disambiguate (passed through; callers must
        ensure their type). For everything else, returns the placeholder."""
        stripped = whyml_str.strip()
        if stripped == "0":
            return "(Array.make 1 0)"
        # Already array-shaped — leave alone.
        if (stripped.startswith("(Array.make")
                or stripped.startswith("(Array.get")
                or stripped.startswith("(sorted_1 ")
                or stripped.startswith("(list_new ")
                or stripped.startswith("(any_1 ")
                or stripped.startswith("(all_1 ")):
            return whyml_str
        # Bare identifier or a dotted FIELD access (`self.fields`) — could be array-typed (callee's
        # responsibility); pass through. (Track C / cprobe: clobbering `self.fields` to a placeholder
        # severs it from its representation invariant, so a callee's array precondition can never
        # discharge from `0 <= self.fields[k] <= MAX`.)
        if stripped.replace("_", "").replace("!", "").replace(".", "").isalnum():
            return whyml_str
        # L2 sub-gap 2 (os-bodyvc-spec): a function application `(fn arg…)` or array-literal
        # `(let _alit = …)` in an array slot is an array-returning expression (e.g. `(pack16 x)`,
        # `(materialize !s)`, the `[..]` literal). Pass it through — clobbering it to a placeholder
        # discards the value, which breaks contract-composition round-trips
        # (`unpack(pack(x)) == x` lost `pack(x)` to `(Array.make 1 0)`). Only genuinely-scalar args
        # (`0`, a numeric `(a + b)`) still get the placeholder.
        if stripped.startswith("("):
            inner = stripped[1:].lstrip()
            head = inner.split(" ", 1)[0] if " " in inner else inner.rstrip(")")
            head_ok = head.lstrip("!").replace("_", "").replace(".", "").isalnum()
            if head and head_ok and not head.lstrip("!")[:1].isdigit():
                return whyml_str
        # Anything else (BinOp result, parenthesised int expression) —
        # coerce to placeholder since we can't recover the array.
        return "(Array.make 1 0)"

    def _deref(self, expr: str) -> str:
        """Dereference a WhyML ref-typed operand: `x` → `!x` (idempotent — a leading
        `!` is normalized, not doubled). Used by the set/list/map handlers, where a
        collection operand may arrive already-dereffed."""
        return f"!{expr.lstrip('!')}" if expr.startswith("!") else expr

    def _coerce_to_int(self, whyml_str: str) -> str:
        """Coerce any non-int WhyML expression to int for abstract val arguments.

        no-more-int A6: the `self`/record → int category was retired here — a
        corpus-wide audit found it fires 0 times now that record params/locals
        are handled by the record-aware dotted-call path (A2a/A2c), so the
        `self_to_int_<type>` abstract op is dead. The remaining categories are
        not erasure of a now-typed value: `array`/`map` are defensive
        placeholders that keep a genuinely-untyped collection flow from emitting
        an ill-typed operand where `int` is expected; `tuple`→hash and the
        `string`→hash fallback are the benign documented collapses (A7)."""
        # String literals → int hash
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(stable_hash(whyml_str))
        # Array-shaped expressions can't be passed where int is expected.
        # The array's contents have no axioms; coerce to 0 placeholder.
        stripped = whyml_str.strip()
        array_prefixes = ("(Array.make", "(Array.sub ", "(array_slice ", "(sorted_1 ",
                          "(list_new_arr ", "(any_1 ", "(all_1 ")
        for prefix in array_prefixes:
            if stripped.startswith(prefix):
                return "0"
        # Map-shaped expressions (body-set / body-dict updates) can't be
        # passed where int is expected — same placeholder.
        map_prefixes = ("(map_update_some ", "(map_update_none ",
                        "(const (None: option int)")
        for prefix in map_prefixes:
            if stripped.startswith(prefix):
                return "0"
        # Tuple literals (a, b, c) → hash to int
        if "," in whyml_str and whyml_str.startswith("(") and whyml_str.endswith(")"):
            return str(stable_hash(whyml_str))
        return whyml_str

    # ----- no-more-int F1: dict value-type (ν) dispatch, consolidated -----
    # A dict's value type ν ∈ {int (default), "string", "seq int", "map …"}
    # drives three emission decisions — the empty-map literal (first assignment),
    # the missing-key placeholder (subscript read), and the stored-value coercion
    # (subscript write). These were a parallel `if ν == … elif …` ladder
    # duplicated at each of the three sites; these helpers centralise that ladder.
    # Output is byte-identical to the former inline branches.

    def _dv_empty_default(self, nu: str) -> str:
        """Empty-map literal for a dict local's first assignment; `None` for an
        int dict (the caller keeps the `(const (None: option int))` it has)."""
        if nu == "string":
            return "(const (None: option string))"
        if nu == "hval":
            # hval-value-model-wall: a `Dict[str, PyVal]` heterogeneous dict is
            # `map string (option hval)`; the empty base is the everywhere-None map.
            return "(const (None: option hval))"
        if nu == "emit_ir":
            # self-tcb-reduction _typeddict_record_literal (cap-5): a `Dict[str, ExprIR]`
            # local (`kv = {}` mapping field-name -> value IR node) is `map string (option
            # emit_ir)`; the empty base is the everywhere-None map.
            return "(const (None: option emit_ir))"
        if nu == "seq int":
            return "(const (None: option (seq int)))"
        if nu and nu.startswith("map "):
            return f"(const (None: option ({nu})))"
        return ""

    def _dv_missing_default(self, nu: str) -> str:
        """`None ->` placeholder for a dict subscript read (typed per ν; proven
        dead under `#@ no_exception KeyError`, the ambient default otherwise)."""
        if nu == "string":
            return '""'
        if nu == "hval":
            # hval-value-model-wall: the missing-key default for a `Dict[str, PyVal]`
            # read — an `hval` sentinel (proven dead under `#@ no_exception KeyError`).
            return "(HInt 0)"
        if nu == "emit_ir":
            # cap-5: the missing-key default for a `Dict[str, ExprIR]` read — the emit_ir
            # absent sentinel `IrOther ""` (total; the `kv.get(fname)` fallback).
            return '(IrOther "")'
        if nu and nu.startswith("seq "):
            # #15: `Dict[str, List[T]]` value (`seq string`/`seq int`) -> the empty seq default.
            return f"(Seq.empty: {nu})"
        if nu and nu.startswith("map "):
            inner_v = (nu.split("(option ", 1)[1].rsplit(")", 1)[0]
                       if "(option " in nu else "int")
            return f"(const (None: option {inner_v}))"
        return "0"

    def _dv_store_value(self, nu: Optional[str], val_expr: str) -> str:
        """The value stored at `d[k] = val`: a `seq int` snapshots the array
        (ownership-discipline §3), a string/nested-map value passes through
        unhashed, otherwise int-coerce."""
        if nu == "seq int":
            self._add_abstract_op(
                "val function array_to_seq (a: array int) : seq int\n"
                "    ensures { Seq.length result = Array.length a }")
            return f"(array_to_seq {self._array_coerce_arg(val_expr)})"
        if nu == "string" or nu == "emit_ir" or (nu and nu.startswith("map ")):
            # cap-5: an emit_ir value (`kv[fname] = v`, v a value IR node) passes through
            # unhashed, like the string / nested-map cases.
            return val_expr
        return self._coerce_to_int(val_expr)

    def _pyval_wrap(self, v_ir: Dict[str, Any], local_refs=None) -> str:
        """hval-value-model-wall (self-tcb-reduction, Tier-5): wrap a heterogeneous
        dict-literal VALUE into its FAITHFUL `hval` constructor, tagged by IR kind —
        the make-or-break value tagging that keeps a string a string (no int-erasure).
        str-lit / str-var -> `HStr`; int -> `HInt`; list -> `HArr` over the bespoke
        `hval_list` cons; nested dict -> `HMap` (a `map string (option hval)` Map.set
        chain); an IR-node construction -> `HNode`. Recursive: list elements and nested
        map values are themselves wrapped, so the whole heterogeneous value tree lowers
        faithfully. Emitted only under the `_uses_pyval` gate (a `Dict[str, PyVal]`)."""
        if isinstance(v_ir, dict):
            t = v_ir.get("type")
            if t == "ArrayLit":
                acc = "HNil"
                for e in reversed(v_ir.get("elts", []) or []):
                    acc = f"(HCons {self._pyval_wrap(e, local_refs)} {acc})"
                return f"(HArr {acc})"
            if t == "DictLit":
                # R3: build the HMap carrier as an assoc list — PREPEND each
                # (key, hval) binding onto `PNil` (`hpairs = PNil | PCons key hval
                # hpairs`), NOT a `map_update_some` Map.set chain. The map carrier
                # was non-iterable; the assoc list makes the read (`pairs_get`) a
                # terminating structural fold. Distinct keys → prepend order is
                # observationally irrelevant.
                acc = "PNil"
                for k_ir, ve_ir in zip(v_ir.get("keys", []) or [],
                                       v_ir.get("values", []) or []):
                    k_low = self._expr_to_whyml(k_ir, local_refs)
                    acc = (f"(PCons {k_low} "
                           f"{self._pyval_wrap(ve_ir, local_refs)} {acc})")
                return f"(HMap {acc})"
            # an IR-node construction (`{"type": "Var", …}`) carries an emit_ir node.
            if self._is_emit_ir_expr(v_ir):
                return f"(HNode {self._expr_to_whyml(v_ir, local_refs)})"
            # a value that is ITSELF an `hval` — an hval local or a chained hval `.get`
            # (`{"bound": info.get("bound")}`) — embeds DIRECTLY (already tagged), NOT
            # re-wrapped as `HStr`/`HInt`. Gated on `_expr_is_pyval` -> corpus byte-inert.
            if self._expr_is_pyval(v_ir):
                return self._expr_to_whyml(v_ir, local_refs)
        low = self._expr_to_whyml(v_ir, local_refs)
        if self._is_string_expr(v_ir):
            return f"(HStr {low})"
        return f"(HInt {self._coerce_to_int(low)})"

    def _match_pattern_cond(self, pat: Dict[str, Any], subject: str, local_refs: Set[str]) -> str:
        """Generate a WhyML boolean condition for a match pattern."""
        kind = pat.get("pattern", "Unknown")
        if kind == "Wildcard":
            return "true"
        elif kind == "Value":
            val = self._expr_to_whyml(pat["value"], local_refs)
            return f"({subject} = {val})"
        elif kind == "Capture":
            if pat.get("inner"):
                return self._match_pattern_cond(pat["inner"], subject, local_refs)
            return "true"
        elif kind == "Or":
            alts = [self._match_pattern_cond(a, subject, local_refs) for a in pat.get("alternatives", [])]
            return " || ".join(alts) if alts else "true"
        return "true"

    def _emit_membership(self, op: str, expr: Dict[str, Any], left: str, right: str,
                          local_refs: Set[str], invariant_ctx: bool,
                          subst: Optional[Dict[str, str]]) -> str:
        """Emit `in` / `not in` against either an inline collection literal
        (Tuple/ArrayLit/SetLit), a body-level dict (match-based, since
        Why3 program code lacks decidable equality on `option int`), or a
        generic abstract `contains_check`."""
        negate = op == "not in"
        rhs = expr.get("right", {})
        # cap2 (self-tcb-reduction `_refine_tuple_return_type`): `_st.get(_k) in (None, "Any")`
        # where `_st` is a `map string (option string)` local — an OPTION-string membership.
        # `_st.get(_k)` is `Map.get !_st _k : option string`; the tuple mixes `None` (the option
        # is absent) with string literals (the option is `Some <lit>`). Lower to a faithful
        # option `match`, NOT the int-hash `= 0 || = <hash>` facade. Gated on the method ->
        # byte-inert for the corpus and every other mirror.
        if (not self._in_spec and self._emitting_refine_tuple_return_type()
                and rhs.get("type") in ("Tuple", "ArrayLit", "SetLit")):
            _lir = expr.get("left")
            _elts = rhs.get("elts", []) or []
            if (isinstance(_lir, dict) and _lir.get("type") == "Call"
                    and isinstance(_lir.get("func"), str)
                    and _lir.get("func").endswith(".get")
                    and (_lir.get("args") or []) and _elts
                    and all(isinstance(e, dict)
                            and e.get("type") in ("None", "String") for e in _elts)
                    and any(e.get("type") == "None" for e in _elts)):
                _recv = _lir["func"][:-len(".get")]
                if "." not in _recv:
                    _rw = self._expr_to_whyml({"type": "Var", "name": _recv},
                                              local_refs, invariant_ctx, subst)
                    _kw = self._expr_to_whyml(_lir["args"][0], local_refs,
                                              invariant_ctx, subst)
                    self._add_abstract_op(
                        "val str_eq_op (a: string) (b: string) : bool\n"
                        "    ensures { result <-> (a = b) }")
                    _strs = [e for e in _elts if e.get("type") == "String"]
                    _disj = (" || ".join(
                        f"(str_eq_op _mem_s {whyml_string_literal(e.get('value'))})"
                        for e in _strs) if _strs else "false")
                    _inner = (f"(match (Map.get {_rw} {_kw}) with "
                              f"None -> true | Some _mem_s -> ({_disj}) end)")
                    return f"(not {_inner})" if negate else _inner
        # self-tcb-reduction _typeddict_field_access (d): `<x> in rec_info["fields"]` /
        # `not in` where the rhs is a SUBSCRIPT on a pyval LOCAL (`rec_info["fields"]`, an
        # hval collection) -> faithful membership via `hval_str_mem` over the RAW hval (the
        # `HArr` of `HStr` field names), descending the real structure (non-vacuous), NOT
        # the opaque int-hashed `contains_check`. `left` is the raw native string needle.
        # Gated on `_pyval_locals` -> corpus/mirror byte-inert.
        if not self._in_spec and rhs.get("type") == "Subscript":
            _sv = rhs.get("value")
            if (isinstance(_sv, dict) and _sv.get("type") == "Var"
                    and _sv.get("name") in getattr(self, "_pyval_locals", set())):
                _pvm = whyml_ident(_sv.get("name"))
                _kir = rhs.get("index", {})
                _kw = self._expr_to_whyml(_kir, local_refs or set(), invariant_ctx, subst)
                _rawh = (f"(match {_pvm} with HMap m_mem -> "
                         f"(match pairs_get m_mem {_kw} with Some v_ -> v_ "
                         f"| None -> (HInt 0) end) | _ -> (HInt 0) end)")
                _mem = f"(hval_str_mem {_rawh} {left})"
                return f"(not {_mem})" if negate else _mem
        # self-tcb-reduction `_compute_return_type` PATH(b): DIRECT-self map membership
        # `K in self._record_types` / `K in getattr(self, "_variant_types", {})` -> the
        # membership reader `<base>_mem <K> : bool` (the direct-access twin of the
        # opaque-selfmap alias membership), NOT the int-hash `contains_check (str_hash_op
        # K) 0` facade. The outer key `K` may be a pyval `.get`/subscript
        # (`func['return_value_type']`), projected via `hstr_of`. Gated on the
        # `_compute_return_type` file -> byte-inert for the corpus and other mirrors.
        # self-tcb-reduction `_compute_return_type` PATH(b): the self-state guard
        # `getattr(self, "_current_self_type", None) in getattr(self,
        # "_mutable_state_classes", set())` -> `mutable_state_classes_mem
        # (current_self_type_of self) : bool` — a REAL self-parameterized membership
        # (the opaque set reader applied to the opaque current-self-type string), NOT the
        # input-blind `contains_check 0 0` facade. Gated on the `_compute_return_type`
        # file -> byte-inert for the corpus and other mirrors.
        if (not self._in_spec and self._uses_compute_return_type()
                and self._getattr_self_field(rhs) == "_mutable_state_classes"
                and self._getattr_self_field(expr.get("left", {})) == "_current_self_type"):
            _st = self._current_self_type or "functionemissionmixin"
            self._add_abstract_op(
                f"val current_self_type_of (self: {_st}) : string")
            self._add_abstract_op(
                "val function mutable_state_classes_mem (k: string) : bool")
            _mem = "(mutable_state_classes_mem (current_self_type_of self))"
            return f"(not {_mem})" if negate else _mem
        if not self._in_spec:
            _smb = self._self_map_field_base(rhs)
            if _smb:
                _kir = expr.get("left", {})
                _kw = self._expr_to_whyml(
                    _kir if isinstance(_kir, dict) else {}, local_refs or set(),
                    invariant_ctx, subst)
                if self._expr_is_pyval(_kir if isinstance(_kir, dict) else {}):
                    _kw = f"(hstr_of {_kw})"
                self._add_abstract_op(f"val function {_smb}_mem (k: string) : bool")
                _mem = f"({_smb}_mem {_kw})"
                return f"(not {_mem})" if negate else _mem
        # W8 capability (ii) — varargs-membership. `x in vals` where `vals` is the
        # `*vals: str` vararg parameter (a `seq string`) is a REAL membership test over
        # the actual argument sequence, NOT the opaque `contains_check (str_hash_op x)
        # vals` int-hash against an unconstrained constant. `seq_mem_str`'s `ensures`
        # DEFINES it as the existential `exists i. 0 <= i < length v /\ v[i] = x` — the
        # same shape as the already-established `str_contains_op` (a `val` fully pinned
        # by its postcondition, not an axiom): membership is not decidable in Why3's
        # string model, so it cannot be a `function`, but nothing about it is assumed
        # beyond its definition. In SPEC context the existential is emitted inline (a
        # program `val` is illegal in a formula). Gated on `_vararg_str_param` -> fires
        # for no corpus / pycsl_lib function.
        # W8 (ii, companion): `x in <alias>.<attr>` where the attribute is a resolved
        # module STRING-LIST constant (`_keyword.kwlist`) is a REAL membership over the
        # actual table — the same `seq_mem_str` as the vararg path, applied to a literal
        # `Seq.cons` chain of the table's contents. Replaces
        # `contains_check (str_hash_op x) (get_kwlist _keyword)`, which hashed the needle
        # and tested it against an opaque getter with no `ensures` at all. Gated on the
        # Module5-resolved map -> fires for no corpus / pycsl_lib program.
        _msl = getattr(self, "_module_str_list_constants", None)
        if _msl and not self._in_spec and rhs.get("type") in ("Attribute", "FieldGet"):
            _mo = rhs.get("object")
            _ma = rhs.get("attr") or rhs.get("field")
            _mname = (_mo.get("name") if isinstance(_mo, dict)
                      and _mo.get("type") == "Var" else _mo if isinstance(_mo, str)
                      else None)
            _mkey = "{}.{}".format(_mname, _ma) if (_mname and _ma) else None
            if _mkey in _msl:
                self._add_abstract_op(
                    "val seq_mem_str (x: string) (v: seq string) : bool\n"
                    "    ensures { result <-> (exists _mi: int. 0 <= _mi < Seq.length v\n"
                    "      /\\ Seq.get v _mi = x) }")
                _chain = "(Seq.empty: seq string)"
                for _e in reversed(_msl[_mkey]):
                    _chain = f"(Seq.cons {whyml_string_literal(_e)} {_chain})"
                _lcall = f"(seq_mem_str {left} {_chain})"
                return f"(not {_lcall})" if negate else _lcall
        _vap = getattr(self, "_vararg_str_param", None)
        if _vap is not None and rhs.get("type") == "Var" and rhs.get("name") == _vap:
            _vseq = whyml_ident(_vap)
            if self._in_spec:
                _form = (f"(exists _mi: int. 0 <= _mi < Seq.length {_vseq} "
                         f"/\\ Seq.get {_vseq} _mi = {left})")
                return f"(not {_form})" if negate else _form
            self._add_abstract_op(
                "val seq_mem_str (x: string) (v: seq string) : bool\n"
                "    ensures { result <-> (exists _mi: int. 0 <= _mi < Seq.length v\n"
                "      /\\ Seq.get v _mi = x) }")
            _mcall = f"(seq_mem_str {left} {_vseq})"
            return f"(not {_mcall})" if negate else _mcall
        # self-tcb-reduction WRITER class (`_build_param_list`): `v in local_refs` /
        # `arg in ghost_vars` / `v not in ghost_vars` where the RHS is one of the
        # `seq string`-modelled `Set[str]` params is a REAL sequence membership
        # (`seq_mem_str`), NOT the int-hash `contains_check`. The param is a plain
        # `seq string` value (not a `ref`), so no `!` deref. Gated on the method ->
        # byte-inert for the corpus and every other mirror.
        if (not self._in_spec and self._emitting_build_param_list()
                and rhs.get("type") == "Var"
                and rhs.get("name") in ("local_refs", "ghost_vars")):
            _bseq = whyml_ident(rhs["name"])
            if self._in_spec:
                _form = (f"(exists _mi: int. 0 <= _mi < Seq.length {_bseq} "
                         f"/\\ Seq.get {_bseq} _mi = {left})")
                return f"(not {_form})" if negate else _form
            self._add_abstract_op(
                "val seq_mem_str (x: string) (v: seq string) : bool\n"
                "    ensures { result <-> (exists _mi: int. 0 <= _mi < Seq.length v\n"
                "      /\\ Seq.get v _mi = x) }")
            _mcall = f"(seq_mem_str {left} {_bseq})"
            return f"(not {_mcall})" if negate else _mcall
        # set-value-model-wall (self-tcb-reduction, Tier-5): `x in s` / `x not in s`
        # where `s` is an emitter-local `Set[str]` value reads a PROGRAM BOOL over the
        # executable `set.SetApp[string]` clone — `StrSet.mem x !s` / `not (StrSet.mem
        # x !s)` — the faithful membership guard (NOT `contains_check (str_hash_op x)`
        # int-hash). `x` (`left`) is the raw native string element. NO set-non-membership
        # proof obligation is emitted (the guard is a bool, not an assert). Gated on
        # `_str_set_locals` -> corpus byte-inert.
        if (not self._in_spec and rhs.get("type") == "Var"
                and rhs.get("name") in getattr(self, "_str_set_locals", set())):
            safe_set = whyml_ident(rhs["name"])
            _mem = f"(StrSet.mem {left} !{safe_set})"
            return f"(not {_mem})" if negate else _mem
        # 7b (self-tcb-reduction L4b): `<x> in self.<CONST>` where `self.<CONST>` is a
        # class-body STRING-SET constant (`_GENERIC_BASE_NAMES = {"Generic"}`) lowers to a
        # FAITHFUL `str_eq_op` disjunction over the ACTUAL members — NOT a `contains_check`
        # of the set's int-hashed NAME (a facade invariant under the set's contents). A
        # mutation of the members (`{"Generic"}`->`{"Protocol"}`) flips the emitted literal.
        # Gated on the constant being recorded for the current class -> corpus-inert.
        _ssc_attr = None
        if (rhs.get("type") == "FieldGet" and rhs.get("object") == "self"):
            _ssc_attr = rhs.get("field")
        elif (rhs.get("type") == "Attribute" and isinstance(rhs.get("object"), dict)
                and rhs["object"].get("type") == "Var"
                and rhs["object"].get("name") == "self"):
            _ssc_attr = rhs.get("attr")
        if not self._in_spec and _ssc_attr is not None:
            _ssc = getattr(self, "_class_str_set_constants", {}).get(
                getattr(self, "_current_self_type", None), {})
            _members = _ssc.get(_ssc_attr)
            if _members:
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _checks = [f"(str_eq_op {left} {whyml_string_literal(m)})"
                           for m in _members]
                _disj = f"({' || '.join(_checks)})"
                return f"(not {_disj})" if negate else _disj
        # MODULE-CONST-DICT MEMBERSHIP (relaunch #8): `<s> in _UNARY` where `_UNARY` is a
        # module-level constant str->str dict lowers to the FAITHFUL `str_eq_op`
        # disjunction over the dict's ACTUAL KEYS — not the int-hashed
        # `contains_check (str_hash_op s) _UNARY`, which is a facade invariant under the
        # dict's contents (`_UNARY` itself emits as `val constant _UNARY : int`). This is
        # the exact twin of the class-body string-SET membership just above, over the
        # dict's key set, and it is what makes the const-dict LOOKUP's chain provably
        # total at every guarded site (`factor`'s `self.cur().string in _UNARY`).
        # Mutation-sensitive: perturb a key and the emitted literal moves. Gated on
        # `_const_dict_name` (a genuine module constant, not shadowed by a local/param).
        if not self._in_spec and rhs.get("type") == "Var":
            _cdm = self._const_dict_name(rhs.get("name"))
            _cdd = (getattr(self, "_module_const_dicts", {}) or {}).get(_cdm)
            if _cdd:
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _cdisj = "(" + " || ".join(
                    f"(str_eq_op {left} {whyml_string_literal(_kk)})"
                    for _kk in _cdd) + ")"
                return f"(not {_cdisj})" if negate else _cdisj
        # MODULE-CONST-PAIR-DICT MEMBERSHIP (relaunch #11): the exact twin of the
        # str->str branch above for the `str -> (str, int)` shape — `<s> in _BINOP`
        # lowers to the FAITHFUL `str_eq_op` disjunction over the dict's ACTUAL twelve
        # keys, not the int-hashed `contains_check (str_hash_op s) _BINOP` (a facade
        # invariant under the table's contents, since `_BINOP` itself emits as
        # `val constant _BINOP : int`). Mutation-sensitive: perturb a key and the emitted
        # literal moves. It is also what makes the companion tuple-unpack's chained ITE
        # provably total at every guarded site (`_binop`'s
        # `self.cur().string in _BINOP` loop guard).
        if not self._in_spec and rhs.get("type") == "Var":
            _cpm = self._const_pair_dict_name(rhs.get("name"))
            _cpd = (getattr(self, "_module_const_pair_dicts", {}) or {}).get(_cpm)
            if _cpd:
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _pdisj = "(" + " || ".join(
                    f"(str_eq_op {left} {whyml_string_literal(_e[0])})"
                    for _e in _cpd) + ")"
                return f"(not {_pdisj})" if negate else _pdisj
        # self-tcb-reduction giants (generic class-body lowering): `target in field_names`
        # — membership against the opaque `field_names` param (a `Set[str]`, int-modelled,
        # NOT a tracked dict/set local) — lowers to the abstract `ps_field_mem <target>`
        # predicate (the honest model of a runtime set membership, deciding the
        # skip-if-already-a-field branch). Gated on `_pyast_stmt_locals` (only set inside
        # the class-body giant's emission) + `field_names` being a plain opaque param ->
        # corpus-inert. `<target>` is already the carrier-projected string.
        if getattr(self, "_pyast_stmt_locals", None) and rhs.get("type") == "Var":
            _rn = rhs.get("name", "")
            _rt = self._current_symbol_table.get(_rn)
            if (_rn in self._formal_params and _rn not in self._dict_locals
                    and _rt not in ("set", "dict", "frozenset", "list", "str")):
                _pfm = f"(ps_field_mem {left})"
                return f"(not {_pfm})" if negate else _pfm
        # opaque-nested-map-reader: `k in <alias>` where <alias> aliases an opaque
        # instance map (`getattr(self, "_field", {})`, read via `alias[k]["lit"]`) →
        # the boundary reader `<base>_mem k : bool` (the honest model of a runtime
        # membership on an instance map populated ELSEWHERE — not int-hashed against
        # an int-erased `ref 0`). Registered by `_prescan_opaque_selfmap_aliases`.
        if rhs.get("type") == "Var":
            _base = getattr(self, "_opaque_selfmap_aliases", {}).get(rhs.get("name", ""))
            if _base:
                self._add_abstract_op(f"val function {_base}_mem (k: string) : bool")
                _mem = f"({_base}_mem {left})"
                return f"(not {_mem})" if negate else _mem
        if rhs.get("type") in ("Tuple", "ArrayLit", "SetLit"):
            elts = rhs.get("elts", [])
            if elts:
                # no-more-int leak fix: `sym in ("set","dict",...)` where `sym` is an
                # `Optional[str]` PARAM (a `_union_*` with a single `str` Some-arm) must
                # option-unwrap the union before comparing — an int-hash of the literals
                # against the raw union is a union-vs-int type error. Emit
                # `(match sym with Arm_i_0 s -> (str_eq_op s "set" || …) | _ -> false)`.
                # Gated on every collection element being a String literal (a genuine
                # Optional[str] narrowing) → corpus-inert (no corpus program compares an
                # Optional[str] param to a literal tuple).
                _lir0 = expr.get("left")
                _some = self._optional_str_union_ctor(_lir0)
                if (not self._in_spec and _some
                        and all(isinstance(e, dict) and e.get("type") == "String" for e in elts)):
                    self._add_abstract_op(
                        "val str_eq_op (a: string) (b: string) : bool\n"
                        "    ensures { result <-> (a = b) }")
                    _checks = []
                    for elt in elts:
                        elt_w = self._expr_to_whyml(elt, local_refs, invariant_ctx, subst)
                        _checks.append(f"(str_eq_op _s {elt_w})")
                    _disj = f"({' || '.join(_checks)})"
                    _inner = f"(match {left} with {_some} _s -> {_disj} | _ -> false end)"
                    return f"(not {_inner})" if negate else _inner
                # str-list-elements: `name in ('.', '..')` with a STRING `name` is a
                # disjunction of string equalities — route each to `str_eq_op` (content
                # equality) instead of the int-hash compare, so the operands stay `string`
                # (a string `name = <int hash>` is a type error). Int operands are
                # byte-identical (the `_coerce_str_arg` int-hash path below).
                left_is_str = self._is_string_expr(left_ir) if (left_ir := expr.get("left")) else False
                if not self._in_spec and left_is_str:
                    self._add_abstract_op(
                        "val str_eq_op (a: string) (b: string) : bool\n"
                        "    ensures { result <-> (a = b) }")
                    checks = []
                    for elt in elts:
                        elt_w = self._expr_to_whyml(elt, local_refs, invariant_ctx, subst)
                        checks.append(f"(str_eq_op {left} {elt_w})")
                    joined = f"({' || '.join(checks)})"
                    return f"(not {joined})" if negate else joined
                left_c = self._coerce_str_arg(left)
                checks = []
                for elt in elts:
                    elt_w = self._expr_to_whyml(elt, local_refs, invariant_ctx, subst)
                    checks.append(f"({left_c} = {self._coerce_str_arg(elt_w)})")
                joined = f"({' || '.join(checks)})"
                return f"(not {joined})" if negate else joined
        # Body-local dict OR set/dict-typed parameter OR self.<dict-field>
        rhs_is_map = False
        if rhs.get("type") == "Var":
            rname = rhs.get("name", "")
            if rname in self._dict_locals:
                rhs_is_map = True
            elif self._current_symbol_table.get(rname) in ("set", "dict", "frozenset"):
                rhs_is_map = True
            else:
                # §26: `k in X` where X aliases a self dict-field → membership on
                # `self.<field>` (the getattr-bound-local form of `k in self.<field>`).
                _alias = self._alias_self_field(rname)
                if _alias:
                    rhs_is_map = True
                    right = f"self.{self._field_label(getattr(self, '_current_self_type', None), _alias.split('.', 1)[1])}"
        if not rhs_is_map and rhs.get("type") in ("Attribute", "FieldGet"):
            ft = self._field_type_of(rhs)
            if ft in ("set", "dict", "frozenset"):
                rhs_is_map = True
        # typed-ir §15 (getattr) + faithful-string-op tail: `x in getattr(self, "<field>",
        # set())` on a `set`/`dict` self-field — the defensive-read form of `x in
        # self.<field>`. Rewrite `right` to the real `self.<field>` map so the string-key
        # `str_hash_op` membership below fires (was falling to opaque `contains_check`).
        if not rhs_is_map and rhs.get("type") == "Call":
            _gf = self._getattr_self_field(rhs)
            # self-tcb-reduction T1.a: also fire for a SET self-field (`getattr(self, "_seq_locals",
            # set())`), not only dict fields — mirrors the direct `x in self._set_field` path so the
            # string key gets `str_hash_op`-hashed instead of the opaque `contains_check`.
            _gf_coll = _gf and (
                self._self_field_dict_nu(f"self.{_gf}") is not None
                or self._field_type_of({"type": "Attribute",
                                        "object": {"type": "Var", "name": "self"},
                                        "attr": _gf}) in ("set", "dict", "frozenset"))
            if _gf_coll:
                rhs_is_map = True
                # the direct `self.<label>` field access (matching the non-getattr
                # `x in self._seq_locals` form), NOT a synthetic Attribute IR — which
                # lowers to the opaque `get_<field>` accessor.
                right = f"self.{self._field_label(getattr(self, '_current_self_type', None), _gf)}"
        # self-tcb-reduction T1.a: `x in self._method()` where the method returns a
        # `Set[str]`/`dict` (`name in self._module_binding_names()`) → map membership (the RHS
        # `right` is already the abstract-val call returning the map). @mutable_state.
        if not rhs_is_map and rhs.get("type") == "Call" and not self._getattr_self_field(rhs):
            _fn = rhs.get("func", "")
            if isinstance(_fn, str) and _fn.startswith("self."):
                _cls = getattr(self, "_current_self_type", None)
                _key = f"{_cls}__{_fn[len('self.'):]}" if _cls else _fn
                if getattr(self, "_module_method_return_types", {}).get(_key) in (
                        "map int (option int)", "set", "dict", "frozenset"):
                    rhs_is_map = True
        # nested-map.md: `k in self._nested_dict.get(k1, {})` — `.get` on a NESTED-dict field
        # returns the INNER map (its value_type is `map …`), so membership hashes the key into
        # it. The lowered `right` is already the inner-map match-expr. @mutable_state.
        if not rhs_is_map and rhs.get("type") == "Call":
            _fn = rhs.get("func", "")
            if isinstance(_fn, str) and _fn.endswith(".get"):
                _recv = _fn[:-len(".get")]
                _nu = self._self_field_dict_nu(_recv) if _recv.startswith("self.") else None
                if isinstance(_nu, str) and _nu.startswith(("map ", "seq ", "array ")):
                    rhs_is_map = True
        if rhs_is_map:
            # todict-reflection-plan.md R3: a STRING key into a `Set[str]`/`dict[str,_]`
            # (an int-keyed map) is hashed with `str_hash_op` — the read-side analogue of
            # the M.7 `.add` write (`self.f <- map_update_some … (str_hash_op k) …`), so
            # `field in self._all_record_fields` typechecks. Fires only when the key is a
            # string expr (an int key keeps the `_coerce_to_int` path) → byte-identical.
            # A STRING key into an int-keyed map (a `Set[str]` field, OR a body dict
            # `map _ (option int)`) is `str_hash_op`-hashed — the read-side analogue of the
            # M.7 `.add`. The subscript `d[k]` hashes the same way (`_lower_dict_get_call`),
            # so membership and subscript agree on the key type. Byte-identical (an int key
            # keeps `_coerce_to_int`). typed-ir-for-b-ceiling.md §9.
            _left_ir = expr.get("left", {})
            _str_keyed_lit = getattr(self, "_dict_key_types", {}).get(
                rhs.get("name", "") if rhs.get("type") == "Var" else "") == "string"
            # cleared-hash S4: a κ=string record dict/set FIELD map (`k in self.<field>`,
            # incl. the `x in getattr(self, "<field>", set())` defensive form) is
            # `map string (option ν)` — read the RAW native string key, matching the
            # field store/`.get`/subscript. Covers the direct Attribute/FieldGet receiver
            # and the getattr-rewritten `_gf` field.
            if not _str_keyed_lit:
                _mf = None
                if rhs.get("type") in ("Attribute", "FieldGet"):
                    _mo = rhs.get("object"); _ma = rhs.get("attr") or rhs.get("field")
                    if isinstance(_mo, dict) and _mo.get("type") == "Var" and _ma:
                        _mf = f"{_mo.get('name')}.{_ma}"
                    elif isinstance(_mo, str) and _ma:
                        _mf = f"{_mo}.{_ma}"
                elif rhs.get("type") == "Call":
                    _mgf = self._getattr_self_field(rhs)
                    if _mgf:
                        _mf = f"self.{_mgf}"
                if _mf is not None and self._self_field_dict_kappa(_mf) == "string":
                    _str_keyed_lit = True
            if _str_keyed_lit:
                # cleared-hash.md S3: the receiver map is `map string (option ν)`
                # (κ = string), so membership reads the RAW string key — native
                # `String.(=)`, no hash. `_coerce_to_int` would hash a string
                # LITERAL to an int (`stable_hash`), an int operand against a
                # `map string` map (a type error) and the very collision-opacity
                # this migration removes. A `str`-typed variable key passes
                # through `left` unchanged.
                left_c = left
            elif not self._in_spec and self._is_string_expr(_left_ir):
                self._add_abstract_op("val str_hash_op (s: string) : int")
                left_c = f"(str_hash_op {left})"
            else:
                left_c = self._coerce_to_int(left)
            arms = ("| Some _ -> false | None -> true" if negate
                    else "| Some _ -> true | None -> false")
            return f"(match Map.get ({right}) ({left_c}) with {arms} end)"
        # strings-plan Stage 2: `needle in haystack` for strings is substring containment, an
        # uninterpreted bool op over string operands (content witness deferred — see plan).
        if self._is_string_expr(rhs):
            # strings-plan Stage 4: the containment witness. `needle in haystack` holds iff
            # `needle` occurs as a contiguous substring at some position.
            # 07-0647-spec R10/S2.1: in SPEC context (requires/ensures) the op must be a
            # LOGIC term — a program `val` is illegal in a formula ("unbound symbol"). Emit
            # the existential directly (pure `string.String` logic, already imported). In a
            # body the `val str_contains_op` (uninterpreted bool) is used.
            if self._in_spec:
                form = (f"(exists _si: int. 0 <= _si /\\ "
                        f"_si + String.length {left} <= String.length {right} /\\ "
                        f"String.substring {right} _si (String.length {left}) = {left})")
                return f"(not {form})" if negate else form
            self._add_abstract_op(
                "val str_contains_op (haystack: string) (needle: string) : bool\n"
                "    ensures { result <->\n"
                "      (exists i: int. 0 <= i /\\\n"
                "        i + String.length needle <= String.length haystack /\\\n"
                "        String.substring haystack i (String.length needle) = needle) }")
            scall = f"(str_contains_op {right} {left})"
            return f"(not {scall})" if negate else scall
        # A string-typed LEFT (e.g. a G1 record string-field `val_ir.op`) reaching the
        # opaque `contains_check` fallback (the container is an int-modeled module
        # frozenset, not a string-key map) must be hashed into the int domain via
        # `str_hash_op` — `_coerce_str_arg` only folds a string *literal*, leaving a
        # non-literal string term type-clashing with `contains_check`'s int param. This
        # keeps the field READ (non-vacuous) while the frozenset membership stays opaque
        # (an orthogonal, pre-existing modeling limit — not a G2 string compare). Fires
        # only for a string left at the fallback → corpus-byte-inert.
        _left_ir = expr.get("left")
        _left_c = (self._str_operand_to_int(left)
                   if (_left_ir and self._is_string_expr(_left_ir))
                   else self._coerce_str_arg(left))
        self._add_abstract_op("val contains_check (x: int) (c: int) : bool")
        call = f"(contains_check {_left_c} {self._coerce_str_arg(right)})"
        return f"(not {call})" if negate else call

    def _emit_bitwise_or_power(self, op_char: str, expr: Dict[str, Any],
                                left: str, right: str) -> str:
        """Emit `&`/`|`/`^`/`<<`/`>>`/`**`. Constant-fold when both
        operands are literal ints; otherwise emit an abstract val call.
        Coerce array- or map-shaped operands to int (the abstract val is
        `int -> int -> int`) — Python `set | set` (treated by Module6 as
        bitwise on int) and similar shape-confused cases land here."""
        left_ir = expr.get("left", {})
        right_ir = expr.get("right", {})
        if (left_ir.get("type") == "Number" and right_ir.get("type") == "Number"
                and isinstance(left_ir.get("value"), int)
                and isinstance(right_ir.get("value"), int)):
            try:
                return str(self._BITWISE_FOLD_OPS[op_char](left_ir["value"], right_ir["value"]))
            except (ValueError, OverflowError):
                pass
        op_fn = self._BITWISE_FN_NAMES[op_char]
        # `val function` (Why3 idiom for "pure program + logic symbol"):
        # bit_and / bit_or / bit_xor / bit_lshift / bit_rshift / py_pow
        # are pure mathematical operations on int. `val function`
        # declares both a program-callable and a logical symbol, so
        # the body can call them AND `#@ proof rocq` axioms can
        # constrain them (axioms can only reference logical symbols).
        self._add_abstract_op(f"val function {op_fn} (x: int) (y: int) : int")
        return f"({op_fn} {self._coerce_to_int(left)} {self._coerce_to_int(right)})"

    # typed-ir-for-b-ceiling.md B-C1: the inline `{"type": K, …}` node kinds this
    # lowers to `exprir` constructors, and the payload field each constructor reads.
    _IRNODE_CTORS = {
        "Var":      ("IrVar", ["name"]),
        "Attribute": ("IrAttr", ["object", "attr"]),
        "String":   ("IrStr", ["value"]),
        "Number":   ("IrNum", ["value"]),
        "RawWhyml": ("IrRaw", ["whyml"]),
        # self-tcb-reduction spike (csl-ast-as-emit_ir): `IrBinOp string emit_ir emit_ir`
        # (preamble.py _emit_exprir_theory) already exists — wires the `{"type":"BinOp",
        # "op":..., "left":..., "right":...}` construction (Module5's `_csl_binop`) to it.
        "BinOp":    ("IrBinOp", ["op", "left", "right"]),
        # M5 FREE-bucket (_csl_field_subscript/_csl_global_field_subscript/
        # _csl_chained_subscript): `IrSub emit_ir emit_ir` and `IrFieldGet string
        # string` (preamble.py _emit_exprir_theory) already exist in the theory —
        # wire the `{"type":"Subscript", "value":…, "index":…}` and
        # `{"type":"FieldGet", "object":…, "field":…}` constructions to them.
        "Subscript": ("IrSub", ["value", "index"]),
        "FieldGet":  ("IrFieldGet", ["object", "field"]),
        # isinstance-on-CSL-class recognizer (self-tcb-reduction M5, _csl_old): wire the
        # two constructions of `_csl_old`. `{"type":"Old","expr":<emit_ir>}` -> `IrOld
        # emit_ir` (the wrapped sub-node); `{"type":"OldField","object":<str>,"field":
        # <str>}` -> `IrOldField string string` (the flat `\old(x.f)` node's two leaf
        # strings, read off the CSLFieldAccess-modeled-as-IrFieldGet node.expr via
        # `fgobject_of`/`field_of` — see `_EMIT_IR_HANDLER_ATTR_PROJ["_csl_old"]`).
        "Old":       ("IrOld", ["expr"]),
        "OldField":  ("IrOldField", ["object", "field"]),
        # post-m1-census.md spec-op batch mini-M1: wire the SPEC-OP family's inline
        # `{"type": K, ...}` constructions (Module5's `_csl_unaryop`/`_csl_at`/
        # `_csl_array_length`/`_csl_in_globals`/`_csl_in_scope`/`_csl_valid`/
        # `_csl_separated`/`_csl_length2d`/`_csl_valid2d`/`_csl_is_sorted`/
        # `_csl_array_eq`/`_csl_permutation`/`_csl_sum`/`_csl_assigns_region`/
        # `_csl_forall_items`) to the matching `emit_ir` ctors added alongside
        # IrBinOp/IrIfExpr/IrTer3 (preamble.py `_emit_exprir_theory`).
        "UnaryOp":       ("IrUnaryOp", ["op", "expr"]),
        # self-tcb-reduction family-B (membership run): `_parse_membership` builds
        # `CSLIn(element, collection)` / `CSLNotIn(element, collection)` — both children
        # are emit_ir expressions. Wired to the `IrCSLIn`/`IrCSLNotIn` two-emit_ir-child
        # ctors (preamble.py `_emit_exprir_theory`, `_uses_clause_ir`-gated → byte-inert).
        "CSLIn":         ("IrCSLIn", ["element", "collection"]),
        "CSLNotIn":      ("IrCSLNotIn", ["element", "collection"]),
        "At":            ("IrAt", ["expr", "label"]),
        "ArrayLen":      ("IrArrayLen", ["var"]),
        "InGlobals":     ("IrInGlobals", ["name"]),
        "InScope":       ("IrInScope", ["name"]),
        "Valid":         ("IrValid", ["base", "length"]),
        "Separated":     ("IrSeparated", ["base1", "len1", "base2", "len2"]),
        "Length2D":      ("IrLength2D", ["base", "rows", "cols"]),
        "Valid2D":       ("IrValid2D", ["base", "row", "col"]),
        "IsSorted":      ("IrIsSorted", ["base", "lo", "hi"]),
        "ArrayEq":       ("IrArrayEq", ["left", "right"]),
        "Permutation":   ("IrPermutation", ["left", "right"]),
        "Sum":           ("IrSum", ["base", "lo", "hi"]),
        "AssignsRegion": ("IrAssignsRegion", ["base", "low", "high"]),
        "ForallItems":   ("IrForallItems", ["key", "val", "map", "body"]),
        # post-m1-census.md map/set/list batch mini-M1: wire the MAP/SET/LIST
        # ghost-collection family's inline `{"type": K, ...}` constructions
        # (Module5's `_csl_map_empty`/`_csl_map_get`/`_csl_map_set`/`_csl_map_eq`/
        # `_csl_has_key`/`_csl_map_remove`/`_csl_set_empty`/`_csl_set_add`/
        # `_csl_set_remove`/`_csl_set_mem`/`_csl_set_union`/`_csl_set_inter`/
        # `_csl_set_diff`/`_csl_set_card`/`_csl_set_subset`/`_csl_set_eq`/`_csl_nil`/
        # `_csl_cons`/`_csl_hd`/`_csl_tl`/`_csl_list_length`/`_csl_nth`/`_csl_mem`/
        # `_csl_append`) to the matching `emit_ir` ctors added alongside the SPEC-OP
        # family (preamble.py `_emit_exprir_theory`).
        "MapEmpty":  ("IrMapEmpty", []),
        "MapGet":    ("IrMapGet", ["dict", "key"]),
        "MapSet":    ("IrMapSet", ["dict", "key", "value"]),
        "MapEq":     ("IrMapEq", ["left", "right"]),
        "HasKey":    ("IrHasKey", ["dict", "key"]),
        "MapRemove": ("IrMapRemove", ["dict", "key"]),
        "SetEmpty":  ("IrSetEmpty", []),
        "SetAdd":    ("IrSetAdd", ["set", "elem"]),
        "SetRemove": ("IrSetRemove", ["set", "elem"]),
        "SetMem":    ("IrSetMem", ["elem", "set"]),
        "SetUnion":  ("IrSetUnion", ["left", "right"]),
        "SetInter":  ("IrSetInter", ["left", "right"]),
        "SetDiff":   ("IrSetDiff", ["left", "right"]),
        "SetCard":   ("IrSetCard", ["set", "lo", "hi"]),
        "SetSubset": ("IrSetSubset", ["left", "right"]),
        "SetEq":     ("IrSetEq", ["left", "right"]),
        "Nil":       ("IrNil", []),
        "Cons":      ("IrCons", ["head", "tail"]),
        "Hd":        ("IrHd", ["list"]),
        "Tl":        ("IrTl", ["list"]),
        "ListLength": ("IrListLength", ["list"]),
        "Nth":       ("IrNth", ["list", "index"]),
        "Mem":       ("IrMem", ["elem", "list"]),
        "Append":    ("IrAppend", ["left", "right"]),
        # post-m1-census.md misc single-return batch mini-M1: wire the STRING/TUPLE/
        # GHOST + fieldless family's inline `{"type": K, ...}` constructions
        # (Module5's `_csl_fst`/`_csl_snd`/`_csl_ctor_test`/`_csl_ctor_payload`/
        # `_csl_strconcat`/`_csl_str_length`/`_csl_str_sub`/`_csl_ghost_copy`/
        # `_csl_ghost_copy_range`/`_csl_ghost_make`/`_csl_slice`/`_csl_none`/
        # `_csl_result`/`_csl_nothing`) to the matching `emit_ir` ctors added
        # alongside the MAP/SET/LIST family (preamble.py `_emit_exprir_theory`).
        # cleanup batch: `_csl_bool`'s `{"type":"Bool","value":node.value}` wires to the
        # new `IrBoolC int` ctor (preamble.py `_emit_exprir_theory`). `CSLBool.value` is a
        # `bool` record field lowering to `int` (bool-as-int convention), so the payload is
        # the int field read — `(IrBoolC node.value)`. `_csl_bool` is the ONLY handler that
        # constructs a "Bool" node, so this reroute is scoped to it.
        "Bool":     ("IrBoolC", ["value"]),
        "FstExpr":  ("IrFst", ["tuple"]),
        "SndExpr":  ("IrSnd", ["tuple"]),
        # self-tcb-reduction csl-family (_csl_proj): `{"type":"ProjExpr","tuple":emit_ir,
        # "index":int(node.index.value)}` -> the NEW `IrProj emit_ir int` leaf (preamble.py
        # _emit_exprir_theory, IrFst precedent). `tuple` is emit_ir (ProjExpr.tuple_expr
        # retyped "ExprIR"); `index` is the int literal read (IrCtorPayload's int-arg
        # precedent). Only `_csl_proj` constructs a "ProjExpr" node -> scoped to it.
        "ProjExpr": ("IrProj", ["tuple", "index"]),
        "CtorTest":    ("IrCtorTest", ["var", "ctor"]),
        "CtorPayload": ("IrCtorPayload", ["var", "ctor", "index"]),
        "StrConcat": ("IrStrConcat", ["left", "right"]),
        # self-tcb-reduction (parser _parse_atom): the recursive-descent atom rule
        # constructs the CSL AST class `StrConcatExpr(left, right)` for `s ^ t`
        # (`_parse_atom`); Module5's `_csl_strconcat` uses the "StrConcat" wire key
        # above, but the parser body names the class directly. Both children are
        # emit_ir; reuse the EXISTING base-theory `IrStrConcat` ctor (no new variant).
        "StrConcatExpr": ("IrStrConcat", ["left", "right"]),
        "StrLength": ("IrStrLength", ["string"]),
        "StrSub":    ("IrStrSub", ["string", "lo", "hi"]),
        "GhostCopy":      ("IrGhostCopy", ["arr"]),
        "GhostCopyRange": ("IrGhostCopyRange", ["arr", "lo", "hi"]),
        "GhostMake":      ("IrGhostMake", ["size", "default"]),
        "SliceAccess": ("IrSliceAccess", ["value", "slice"]),
        "Slice":       ("IrSlice", ["lower", "upper"]),
        "None":    ("IrNone", []),
        "Result":  ("IrResult", []),
        "Nothing": ("IrNothing", []),
        # _py_expr fixed-child batch (mini-M1): wire `_py_expr_starred`'s inline
        # `{"type":"Starred","value":…}` construction to the new `IrStarred`
        # ctor (preamble.py `_emit_exprir_theory`); wire `_py_expr_ifexp`'s
        # `{"type":"IfExpr","test":…,"body":…,"orelse":…}` to the EXISTING
        # generic `IrTer3` ctor (ghost-handler-wall Q2) — no new theory
        # constructor for the 3-child ternary, following the MapSetExpr/
        # SetCardExpr precedent verbatim.
        "Starred": ("IrStarred", ["value"]),
        "IfExpr":  ("IrTer3", ["test", "body", "orelse"]),
        # isinstance-on-emit_ir batch (self-tcb-reduction M5): wire `_py_expr_walrus`'s
        # inline `{"type":"NamedExpr","target":<str>,"value":<emit_ir>}` construction to
        # the new `IrNamedExpr string emit_ir` ctor (preamble.py `_emit_exprir_theory`)
        # — `target` is the assignment-target NAME string (the walrus body computes it as
        # a plain string via the `expr.target.id if … else "_walrus"` ternary), `value`
        # the emit_ir sub-node. A GENERIC name+child node, following IrStarred/IrGhostCopy;
        # no discriminant/projector (nothing reflects a NamedExpr node back).
        "NamedExpr": ("IrNamedExpr", ["target", "value"]),
        # variadic content-law comprehension (FABLE-sanctioned): wire `_csl_mktuple`'s
        # `{"type":"MkTuple","elts":[self._csl_to_ir(e) for e in node.elts]}` and
        # `_py_expr_tuple`'s `{"type":"Tuple","elts":[self._py_expr_to_ir(e) for e in
        # expr.elts]}` constructions to the new `IrMkTupleN irlist` ctor
        # (preamble.py `_emit_exprir_theory`). The single `elts` payload is itself an
        # `irlist` (the monomorphic cons-list mutually-recursive with emit_ir) — the
        # comprehension `[<disp>(e) for e in <array emit_ir>]` lowers (expressions.py
        # `_content_comp` variadic branch) to `(list_content_comp_N <elts>)` carrying the
        # length + per-index content law over the shared `emit_ir_disp__<disp>`. Both
        # MkTuple (CSL AST) and Tuple (pure_ast) produce the SAME variadic node;
        # `kind_of (IrMkTupleN ..) = "MkTuple"`.
        "MkTuple": ("IrMkTupleN", ["elts"]),
        "Tuple":   ("IrMkTupleN", ["elts"]),
        # variadic content-law comprehension (FABLE-sanctioned), batch 2: wire the
        # remaining elts/args-list-shaped tuple constructions to their OWN irlist ctors
        # (preamble.py `_emit_exprir_theory`). `_py_expr_list`'s `{"type":"ArrayLit",
        # "elts":[self._py_expr_to_ir(e) for e in expr.elts]}` -> `IrListN irlist`;
        # `_py_expr_set`'s `{"type":"SetLit","elts":[…]}` -> `IrSetN irlist`;
        # `_csl_call_expr`'s `{"type":"Call","func":node.func,"args":[self._csl_to_ir(a)
        # for a in node.args]}` -> `IrCallN string irlist` (func is the CallExpr record's
        # `func: str` field; args the shared-disp content-law comprehension). Each single
        # `elts`/`args` payload lowers (expressions.py `_content_comp` variadic branch) to
        # `(list_content_comp_N <src>)` carrying the length + per-index content law over the
        # shared `emit_ir_disp__<disp>`. Distinct ctor per node kind for clarity.
        "ArrayLit": ("IrListN", ["elts"]),
        "SetLit":   ("IrSetN", ["elts"]),
        "Call":     ("IrCallN", ["func", "args"]),
        # self-tcb-reduction family-B (parser clause parsers): wire the CSL-AST
        # CONTRACT-CLAUSE node constructions the recursive-descent `_ContractParser`
        # builds to the matching `emit_ir` ctors (preamble.py `_emit_exprir_theory`,
        # gated `_uses_clause_ir`). ProofDecl -> `IrProofDecl string string` (the two
        # LEAF-string fields `prover`/`qualname` of `_parse_proof`'s
        # `ProofDecl(prover=prover, qualname=qualname)`). Bound BY NAME off the class's
        # `__init__` field order in `_call_irnode_constructor`, so a payload/field-order
        # mismatch can never silently mis-bind. Corpus-inert: no corpus program declares
        # a @mutable_state class (the `_call_irnode_constructor` gate) nor constructs
        # these classes, so these entries never fire outside the parser mirror.
        "ProofDecl": ("IrProofDecl", ["prover", "qualname"]),
        # ClassInvariant -> `IrClassInvariant emit_ir` (the single EMIT_IR field `expr`
        # of `_parse_class_invariant`'s `ClassInvariant(self._parse_expr())`). The child
        # `self._parse_expr()` lowers to an emit_ir value (`_parse_expr -> "ExprIR"`), so
        # the ctor's emit_ir field is filled by the lowered argument, `_call_irnode_constructor`.
        "ClassInvariant": ("IrClassInvariant", ["expr"]),
        # RaisesDecl -> `IrRaisesDecl string emit_ir` (the LEAF-string `exc_type` +
        # the EMIT_IR `condition` of `_parse_raises`'s `RaisesDecl(exc, self._parse_expr())`).
        # `exc` is a string local (`self.expect_name()`, ProofDecl precedent), the condition
        # lowers to emit_ir; `_call_irnode_constructor` binds both by __init__ field order.
        "RaisesDecl": ("IrRaisesDecl", ["exc_type", "condition"]),
        # self-tcb-reduction family-B (_err-divergence run): the `#@ loop invariant <e>` /
        # `#@ loop variant <e>` node's single EMIT_IR child (`LoopInvariant(expr)` /
        # `LoopVariant(expr)`, `_parse_loop`). Same 1-emit_ir-child shape as ClassInvariant;
        # the child `self._parse_expr()` lowers to emit_ir. `_call_irnode_constructor` binds
        # the emit_ir field by __init__ order. Gated `_uses_clause_ir` (preamble) → byte-inert.
        "LoopInvariant": ("IrLoopInvariant", ["expr"]),
        "LoopVariant":   ("IrLoopVariant", ["expr"]),
        # self-tcb-reduction family-B (_err-divergence run): `#@ interface
        # ensures/requires/assigns <clause>` (`_parse_interface`). InterfaceClause carries
        # a LEAF-string `kind` + an EMIT_IR `payload` (the wrapped Ensures/Requires/Assigns
        # node — arms 1/2 build `Ensures(...)`/`Requires(...)`, arm 3 delegates to the
        # trusted `-> ExprIR` `_parse_assigns`). Ensures/Requires each wrap a single emit_ir
        # `expr`. `_call_irnode_constructor` binds by __init__ field order. Gated
        # `_uses_clause_ir` → byte-inert. The IrRaisesDecl(string+emit_ir) / IrClassInvariant
        # (emit_ir) precedents.
        "InterfaceClause": ("IrInterfaceClause", ["kind", "payload"]),
        "Ensures":  ("IrEnsures", ["expr"]),
        "Requires": ("IrRequires", ["expr"]),
        # self-tcb-reduction family-B (optional-field run): `#@ \variant <e>` /
        # `#@ \variant (<e>, <ordering>)` (`_parse_function_variant`). FunctionVariant
        # carries the required EMIT_IR `expr` + the OPTIONAL string `ordering`
        # (`Optional[str] = None`). The ADT ctor `IrFunctionVariant emit_ir iropt_str`
        # ALREADY exists (preamble, for the dict-based `_recognize_functionvariant_builder`),
        # so this needs NO preamble/kind_of/size change. The `ordering` slot is a
        # MONOMORPHIC-option `iropt_str` (see `_IRNODE_CTOR_OPTFIELDS`): a bound string arg
        # (the 2-arg `FunctionVariant(e, ordering)` form) wraps to `IrSSome <ordering>`; an
        # OMITTED field (the 1-arg `FunctionVariant(self._parse_expr())` form) is `IrSNone`,
        # faithful to `ordering=None`. The parser class-construction analog of the dict-based
        # `_lower_functionvariant_optfield` (which wraps an `option string` node field).
        "FunctionVariant": ("IrFunctionVariant", ["expr", "ordering"]),
        # self-tcb-reduction family-B (ghost run): `#@ ghost <name> <op> <e>` (opt.
        # `: <type>`) / `#@ ghost <name>[<i>] = <e>` (`_parse_ghost`). GhostAssignDecl
        # -> `IrGhostAssignDecl string emit_ir string string` (LEAF `target`, EMIT_IR
        # `value`, LEAF `op`, LEAF `declared_type`); the `declared_type: str = 'int'`
        # field is filled from its concrete string DEFAULT when omitted (see
        # `_IRNODE_CTOR_STRDEFAULTS`), else from the `declared_type=gtype` keyword.
        # GhostArraySetDecl -> `IrGhostArraySetDecl string emit_ir emit_ir` (LEAF
        # `target`, EMIT_IR `index`, EMIT_IR `value`). `_call_irnode_constructor` binds
        # by __init__ field order. Gated `_uses_clause_ir` (preamble) → byte-inert.
        "GhostAssignDecl": ("IrGhostAssignDecl", ["target", "value", "op", "declared_type"]),
        "GhostArraySetDecl": ("IrGhostArraySetDecl", ["target", "index", "value"]),
        # self-tcb-reduction family-B (footprint run): `#@ footprint <NAME>(<arg>)`
        # (`_parse_footprint`). Footprint -> `IrFootprint string emit_ir` (LEAF
        # `happy_name` + EMIT_IR `arg`). Same string-leaf + emit_ir-child shape as
        # RaisesDecl; `_call_irnode_constructor` binds by __init__ field order. Gated
        # `_uses_clause_ir` (preamble) → byte-inert.
        "Footprint": ("IrFootprint", ["happy_name", "arg"]),
        # self-tcb-reduction family-B (mutex run): `#@ mutex_invariant <M>: <EXPR>`
        # (`_parse_mutex_invariant`). MutexInvariant -> `IrMutexInvariant string emit_ir`
        # (LEAF `mutex` [from the trusted `-> str` `_parse_mutex_expr_str`] + EMIT_IR
        # `expr`). Same string-leaf + emit_ir-child shape as RaisesDecl/Footprint. Gated
        # `_uses_clause_ir` (preamble) → byte-inert.
        "MutexInvariant": ("IrMutexInvariant", ["mutex", "expr"]),
        # self-tcb-reduction family-B (optional-field run): `#@ shared <VAR>
        # [protected_by <MUTEX>]` (`_parse_shared`). SharedDecl -> `IrSharedDecl string
        # iropt_str` (LEAF `variable` + OPTIONAL string `mutex`, `Optional[str] = None`).
        # The `mutex` slot is a monomorphic `iropt_str` optfield: the `protected_by` branch
        # `SharedDecl(name, mutex)` (from the trusted `-> str` `_parse_mutex_expr_str`)
        # wraps to `IrSSome <mutex>`; the plain-`SharedDecl(name, None)` branch's EXPLICIT
        # None maps to `IrSNone` (via `none_arg_indices`). Gated `_uses_clause_ir` → byte-inert.
        "SharedDecl": ("IrSharedDecl", ["variable", "mutex"]),
        # self-tcb-reduction family-B (mixin-decl run): `#@ shared_state <name>: <type>`
        # (`_parse_shared_state`). SharedStateDecl -> `IrSharedStateDecl string string`
        # (two LEAF strings `name` + `type_str` [from the trusted `-> str`
        # `_parse_mixin_type`]). The IrProofDecl two-leaf-string precedent. Gated
        # `_uses_clause_ir` (preamble) → byte-inert.
        "SharedStateDecl": ("IrSharedStateDecl", ["name", "type_str"]),
        # self-tcb-reduction family-B (mixin-decl run): `#@ touches_field <name>: <type>`
        # (`_parse_touches_field`). TouchesFieldDecl -> `IrTouchesFieldDecl string string`
        # (two LEAF strings). The IrSharedStateDecl precedent. Gated `_uses_clause_ir`.
        "TouchesFieldDecl": ("IrTouchesFieldDecl", ["name", "type_str"]),
        # self-tcb-reduction family-B (mixin-decl run): `#@ depends_method/requires_method
        # <m>: <sig>` (`_parse_depends_method`). MethodDependencyDecl -> `IrMethodDependency
        # Decl string string string` (three LEAF strings `method`/`sig`/`kind`; `sig` from
        # the converted `-> str` `_parse_mixin_method_sig`, `kind` the method's param). The
        # IrProofDecl leaf-string precedent. Gated `_uses_clause_ir` → byte-inert.
        "MethodDependencyDecl": ("IrMethodDependencyDecl", ["method", "sig", "kind"]),
        # self-tcb-reduction family-B (LIST-append clause parsers): `#@ compose_from M1,
        # M2, …` / `#@ conforms_to P1, … ` / `#@ lock_order M1, …` (`_parse_compose_from`
        # / `_parse_conforms_to` / `_parse_lock_order`). Each wraps a SINGLE `list string`
        # field built by an `.append` loop (`ComposeFromDecl(mixins)` etc.) into the new
        # `IrComposeFromDecl (seq string)` / `IrConformsToDecl (seq string)` / `IrLockOrder
        # (seq string)` ctor. `_call_irnode_constructor` binds the `seq string` field to the
        # lowered list-local argument by __init__ field order. Gated `_uses_clause_ir` →
        # byte-inert. The IrProofDecl single-field precedent (here the field is a `list`, not
        # a leaf string, so NO size arm — the growable seq is not an emit_ir child).
        "ComposeFromDecl": ("IrComposeFromDecl", ["mixins"]),
        "ConformsToDecl": ("IrConformsToDecl", ["protocols"]),
        "LockOrder": ("IrLockOrder", ["order"]),
    }

    # self-tcb-reduction family-B (ghost run): per-ctor map of a payload slot to the
    # concrete STRING default of its class field (a `f: str = "<lit>"` dataclass field),
    # used to FILL an omitted required string slot in `_call_irnode_constructor` (Module5
    # `field_defaults` captures only int/float defaults). Faithful: the Python default
    # value is a compile-time constant, so an omitted `declared_type` IS the string "int".
    _IRNODE_CTOR_STRDEFAULTS = {
        "GhostAssignDecl": {"declared_type": "int"},
    }

    # self-tcb-reduction family-B (optional-field run): per-ctor map of payload slots
    # that are MONOMORPHIC-OPTION ADT fields (`iropt_str = IrSNone | IrSSome string`),
    # keyed by the class field name. In `_call_irnode_constructor`, a BOUND such field
    # wraps its lowered (bare-string) actual as `(IrSSome <v>)`; an UNBOUND (omitted,
    # defaulted-to-None) such field is `IrSNone` — instead of the required-field decline.
    # Faithful to a Python `Optional[str] = None` dataclass field: present token vs absent.
    _IRNODE_CTOR_OPTFIELDS = {
        "FunctionVariant": {"ordering": "iropt_str"},
        "SharedDecl": {"mutex": "iropt_str"},
    }

    # tier3-p1 T3.1.2: node kinds that have a match-based constructor discriminant in
    # the ADT theory (`is_<pred>`). A `.get("type") == K` test against one of these lowers
    # to the discriminant. Kinds NOT listed keep the `str_eq_op (kind_of …) K` path (still
    # sound). Bounded to the EXPR operator node this increment; extend per node-family.
    _KIND_DISCRIMINANT = {
        "BinOp": "is_binop",
        # tier3-p1 increment 2: complete the EXPR family. Each `K -> is_K` where the ADT
        # ctor's `kind_of` returns EXACTLY "K" (is_K <-> kind_of e = K on real nodes). Only
        # exact-tag matches are safe: `Tuple` is intentionally ABSENT (the ADT models a tuple
        # as IrTuple whose `kind_of` is "MkTuple", not "Tuple" — a `.get("type") == "Tuple"`
        # test would disagree with is_tuple, so it stays on the sound `kind_of` string path).
        "Var": "is_var", "Number": "is_num", "String": "is_str",
        "Subscript": "is_sub", "Attribute": "is_attribute", "Call": "is_call",
        "MkTuple": "is_tuple", "FieldGet": "is_fieldget",
        # output-side slice-discrimination (self-tcb-reduction M5, _py_expr_subscript):
        # `<emit_ir>.get("type") == "Slice"` lowers to `(is_slice <recv>)` — the SOUND
        # output-side rewrite of `_py_expr_subscript`'s input-side `isinstance(node.slice,
        # ast.Slice)`. `is_slice` (preamble.py) matches both slice ctors, agreeing with
        # `kind_of e = "Slice"` on every real node (the is_binop faithfulness law).
        "Slice": "is_slice",
        # relaunch #11: the IfExpr discriminant (`is_ifexpr`, preamble.py — the same
        # match-based bool as `is_binop`, excluding the `IrOther` catch-all). Needed by
        # the KIND-LOCAL flow so `_rhs_yields_map`'s ternary arm can discharge the
        # structural `variant { size val_ir }` through `size_ifexpr_body_dec` /
        # `size_ifexpr_orelse_dec`, which are stated over `is_ifexpr`.
        "IfExpr": "is_ifexpr",
    }

    # isinstance-on-emit_ir batch (self-tcb-reduction M5): map a Python AST node
    # class name (`ast.<Node>`) to the IR `type` tag `_py_expr_to_ir` produces for
    # it. A `isinstance(<emit_ir child>, ast.<Node>)` test (the Module5 `_py_expr_*`
    # handlers' input-side type test on an already-lowered ExprIR child) then lowers
    # to the emit_ir ADT constructor discriminant `(is_<kind> child)` via
    # `_KIND_DISCRIMINANT` (see `_handle_isinstance`). Only the entries whose target
    # kind has a discriminant are useful. `Slice` maps to the `is_slice` discriminant
    # (landed with the output-side slice-discrimination batch); the `_py_expr_to_ir`
    # lowering of an `ast.Slice` is `IrSliceN` (kind "Slice"), so an isinstance-on-emit_ir
    # test `isinstance(<lowered>, ast.Slice)` would lower to `(is_slice <lowered>)`.
    _AST_CLASS_TO_IR_KIND = {
        "Name": "Var", "Attribute": "Attribute", "Subscript": "Subscript",
        "Call": "Call", "Tuple": "MkTuple", "Slice": "Slice",
    }

    # isinstance-on-CSL-class recognizer (self-tcb-reduction M5): the SIBLING of
    # `_AST_CLASS_TO_IR_KIND` for a *CSL* AST class named as a BARE `Var` second arg
    # (`isinstance(node.expr, CSLFieldAccess)` in `_csl_old`), rather than the dotted
    # `ast.<Node>` form. Each CSL class maps to the `emit_ir` kind that models it, so
    # the test lowers to that kind's discriminant `(is_<kind> child)` via
    # `_KIND_DISCRIMINANT`. `CSLFieldAccess` (raw fields `object:str`, `field:str`) is
    # modeled as IrFieldGet — the ONLY constructor whose (string, string) shape matches
    # the raw AST node — so its discriminant is `is_fieldget` and the TRUE-branch
    # `.object`/`.field` reads project via `fgobject_of`/`field_of`. Single-kind (NOT
    # the multi-kind Attribute-or-FieldGet of `_csl_field_access`'s OUTPUT lowering:
    # `_csl_old` reads node.expr's RAW strings, it never calls `_csl_field_access`).
    _CSL_CLASS_TO_IR_KIND = {
        "CSLFieldAccess": "FieldGet",
    }

    # self-tcb-reduction giants (generic class-body lowering): map a Python AST
    # STATEMENT class name (`ast.Assign`) to the `pyast_stmt` ADT discriminant an
    # `isinstance(child, ast.<K>)` test lowers to (`is_assign_node child`, …), where
    # `child` is a `pyast_stmt`-typed class-body loop var. Faithful: on every real class
    # body child, `stmt_node_kind_of` = "K" iff `is_K_node` (the ADT faithfulness
    # lemmas). Gated on `child in _pyast_stmt_locals` -> corpus-inert.
    _AST_CLASS_TO_STMT_KIND = {
        "Assign": "is_assign_node", "AnnAssign": "is_annassign_node",
        "ClassDef": "is_classdef_node", "FunctionDef": "is_functiondef_node",
    }

    def _pyast_stmt_child_var(self, ir: Any) -> Optional[Dict[str, Any]]:
        """Return the `ir` if it is a `pyast_stmt`-typed class-body loop var
        (`child in _pyast_stmt_locals`), else None."""
        if (isinstance(ir, dict) and ir.get("type") == "Var"
                and ir.get("name") in getattr(self, "_pyast_stmt_locals", set())):
            return ir
        return None

    def _pyast_stmt_read(self, expr: Any, local_refs: Set[str],
                         invariant_ctx: bool = False,
                         subst: Optional[Dict[str, str]] = None) -> Optional[str]:
        """self-tcb-reduction giants (generic class-body lowering): lower a READ over a
        `pyast_stmt`-typed class-body loop var `child` to the ADT projector, else None:
          `child.value`            -> `(stmt_value child)`      (emit_ir)
          `child.target`           -> `(stmt_target0 child)`    (emit_ir, AnnAssign)
          `child.annotation`       -> `(stmt_annotation child)` (emit_ir)
          `child.name`             -> `(def_name child)`        (string)
          `child.targets[0]`       -> `(stmt_target0 child)`    (emit_ir)
          `len(child.targets)`     -> `(stmt_targets_len child)`(int)
          `child.targets[0].id` / `child.target.id`
                                   -> `(name_of (stmt_target0 child))`  (string, chained)
        Every emit reads the VERBATIM body shape (no name-key); a body change re-emits."""
        if not isinstance(expr, dict):
            return None
        t = expr.get("type")
        if t == "Attribute":
            obj = expr.get("object", {})
            attr = expr.get("attr")
            c = self._pyast_stmt_child_var(obj)
            if c is not None:
                cw = self._expr_to_whyml(c, local_refs, invariant_ctx, subst)
                if attr == "value":
                    return f"(stmt_value {cw})"
                if attr == "target":
                    return f"(stmt_target0 {cw})"
                if attr == "annotation":
                    return f"(stmt_annotation {cw})"
                if attr == "name":
                    return f"(def_name {cw})"
            # chained: `<emit_ir stmt-projector>.id` -> `(name_of <proj>)`
            inner = self._pyast_stmt_read(obj, local_refs, invariant_ctx, subst)
            if inner is not None and attr in _EMIT_IR_STR_ATTRS:
                return f"({_EMIT_IR_STR_ATTRS[attr]} {inner})"
            return None
        if t in ("Subscript", "SliceAccess"):
            val = expr.get("value", {})
            _sl = expr.get("index")
            _is0 = (isinstance(_sl, dict) and _sl.get("type") == "Number"
                    and _sl.get("value") in (0, 0.0))
            if (isinstance(val, dict) and val.get("type") == "Attribute"
                    and val.get("attr") == "targets" and _is0):
                c = self._pyast_stmt_child_var(val.get("object", {}))
                if c is not None:
                    cw = self._expr_to_whyml(c, local_refs, invariant_ctx, subst)
                    return f"(stmt_target0 {cw})"
            return None
        if t == "Call" and expr.get("func") == "len":
            cargs = expr.get("args") or []
            if (len(cargs) == 1 and isinstance(cargs[0], dict)
                    and cargs[0].get("type") == "Attribute"
                    and cargs[0].get("attr") == "targets"):
                c = self._pyast_stmt_child_var(cargs[0].get("object", {}))
                if c is not None:
                    cw = self._expr_to_whyml(c, local_refs, invariant_ctx, subst)
                    return f"(stmt_targets_len {cw})"
        return None

    def _tparam_local_var(self, ir: Any) -> Optional[Dict[str, Any]]:
        """L1 tparam reflection-node ADT: return `ir` if it is a `tparam`-typed
        type_params loop var (`tp in _tparam_locals`), else None."""
        if (isinstance(ir, dict) and ir.get("type") == "Var"
                and ir.get("name") in getattr(self, "_tparam_locals", set())):
            return ir
        return None

    def _tparam_read(self, expr: Any, local_refs: Set[str],
                     invariant_ctx: bool = False,
                     subst: Optional[Dict[str, str]] = None) -> Optional[str]:
        """L1 tparam reflection-node ADT (self-tcb-reduction, collector-family unlock):
        lower a READ over a `tparam`-typed type_params loop var `tp` to the certified
        projector, else None:
          `type(tp).__name__` -> `(tp_kind_of tp)`   (string, the kind discriminant)
          `tp.name`           -> `(tp_name tp)`       (string)
          `tp.bound`          -> `(tp_bound tp)`      (emit_ir sub-node)
        The bound sub-node's `isinstance`/`.id`/`.attr` dispatch reuses the existing
        emit_ir machinery (`_is_emit_ir_expr`(`tp.bound`) is True). Every emit reads the
        VERBATIM body shape; a body change re-emits."""
        if not isinstance(expr, dict):
            return None
        t = expr.get("type")
        # type(tp).__name__ -> tp_kind_of tp
        if t == "Attribute" and expr.get("attr") == "__name__":
            _inner = expr.get("object", {})
            if (isinstance(_inner, dict) and _inner.get("type") == "Call"
                    and _inner.get("func") == "type"):
                _cargs = _inner.get("args") or []
                if len(_cargs) == 1:
                    c = self._tparam_local_var(_cargs[0])
                    if c is not None:
                        cw = self._expr_to_whyml(c, local_refs, invariant_ctx, subst)
                        return f"(tp_kind_of {cw})"
        # tp.name -> tp_name tp ; tp.bound -> tp_bound tp
        if t == "Attribute":
            c = self._tparam_local_var(expr.get("object", {}))
            if c is not None:
                cw = self._expr_to_whyml(c, local_refs, invariant_ctx, subst)
                if expr.get("attr") == "name":
                    return f"(tp_name {cw})"
                if expr.get("attr") == "bound":
                    return f"(tp_bound {cw})"
        # 7a (self-tcb-reduction L4b): the LIVE `_collect_type_params` reads the tparam
        # via `getattr(tp, "name", None)` / `getattr(tp, "bound", None)` (the defensive
        # Call form), not the bare attribute. Lower the same certified projectors.
        _tpg = self._tparam_getattr_read(expr)
        if _tpg is not None:
            c, _field = _tpg
            cw = self._expr_to_whyml(c, local_refs, invariant_ctx, subst)
            if _field == "name":
                return f"(tp_name {cw})"
            if _field == "bound":
                return f"(tp_bound {cw})"
        return None

    def _tparam_getattr_read(self, expr: Any):
        """7a: if `expr` is `getattr(<tp>, "name"|"bound", <default>)` over a `tparam`
        loop var `tp`, return `(<tp-ir>, "name"|"bound")`; else None. The Call form the
        live `_collect_type_params` uses. Scoped via `_tparam_local_var` -> corpus-inert."""
        if not (isinstance(expr, dict) and expr.get("type") == "Call"
                and expr.get("func") == "getattr"):
            return None
        a = expr.get("args") or []
        if len(a) < 2:
            return None
        c = self._tparam_local_var(a[0])
        if c is None:
            return None
        if not (isinstance(a[1], dict) and a[1].get("type") == "String"):
            return None
        field = a[1].get("value")
        if field in ("name", "bound"):
            return (c, field)
        return None

    def _is_tparam_bound_read(self, ir: Any) -> bool:
        """L1: True iff `ir` is `tp.bound` over a `tparam` loop var — a `tp_bound`
        projector that yields an `emit_ir` sub-node, so the emit_ir isinstance/`.id`/
        `.attr` machinery treats it as an emit_ir expression."""
        if (isinstance(ir, dict) and ir.get("type") == "Attribute"
                and ir.get("attr") == "bound"
                and self._tparam_local_var(ir.get("object", {})) is not None):
            return True
        # 7a: the getattr Call form `getattr(tp, "bound", None)`.
        _tpg = self._tparam_getattr_read(ir)
        return _tpg is not None and _tpg[1] == "bound"

    def _keyword_var(self, ir: Any) -> Optional[Dict[str, Any]]:
        """Return `ir` if it is a `keyword`-typed keyword-list loop var (`kw in
        _keyword_locals`), else None."""
        if (isinstance(ir, dict) and ir.get("type") == "Var"
                and ir.get("name") in getattr(self, "_keyword_locals", set())):
            return ir
        return None

    def _keyword_value_term(self, ir: Any, local_refs: Set[str],
                            invariant_ctx: bool = False,
                            subst: Optional[Dict[str, str]] = None) -> Optional[str]:
        """If `ir` is `kw.value` over a keyword loop var, return the `kwval` term
        `(kw_value_of kw)`; else None. The subject the Name/Attribute isinstance +
        `.id`/`.attr` reads project from."""
        if (isinstance(ir, dict) and ir.get("type") == "Attribute"
                and ir.get("attr") == "value"):
            k = self._keyword_var(ir.get("object", {}))
            if k is not None:
                kw = self._expr_to_whyml(k, local_refs, invariant_ctx, subst)
                return f"(kw_value_of {kw})"
        return None

    def _keyword_read(self, expr: Any, local_refs: Set[str],
                      invariant_ctx: bool = False,
                      subst: Optional[Dict[str, str]] = None) -> Optional[str]:
        """J2/J3 convergence (Call-internals keyword iteration): lower a READ over a
        `keyword`-typed loop var `kw` to the certified projector, else None:
          `kw.arg`        -> `(kw_arg_of kw)`              (string)
          `kw.value`      -> `(kw_value_of kw)`            (kwval)
          `kw.value.id`   -> `(kwname_id (kw_value_of kw))`  (string, ast.Name.id)
          `kw.value.attr` -> `(kwattr_of (kw_value_of kw))` (string, ast.Attribute.attr)
        Every emit reads the VERBATIM body shape; a body change re-emits."""
        if not (isinstance(expr, dict) and expr.get("type") == "Attribute"):
            return None
        attr = expr.get("attr")
        obj = expr.get("object", {})
        # kw.arg
        k = self._keyword_var(obj)
        if k is not None and attr == "arg":
            kw = self._expr_to_whyml(k, local_refs, invariant_ctx, subst)
            return f"(kw_arg_of {kw})"
        if k is not None and attr == "value":
            kw = self._expr_to_whyml(k, local_refs, invariant_ctx, subst)
            return f"(kw_value_of {kw})"
        # kw.value.id / kw.value.attr — chained off the kwval subject
        _kwval = self._keyword_value_term(obj, local_refs, invariant_ctx, subst)
        if _kwval is not None:
            if attr == "id":
                return f"(kwname_id {_kwval})"
            if attr == "attr":
                return f"(kwattr_of {_kwval})"
        return None

    def _is_pyast_stmt_emit_ir_read(self, ir: Any) -> bool:
        """True iff `ir` is a `pyast_stmt` projector that yields an `emit_ir` sub-node
        (`child.value`/`child.target`/`child.annotation`/`child.targets[0]`) — so the
        emit_ir isinstance/`.id` machinery treats it as an emit_ir expression."""
        if not isinstance(ir, dict):
            return False
        t = ir.get("type")
        if t == "Attribute" and ir.get("attr") in ("value", "target", "annotation"):
            return self._pyast_stmt_child_var(ir.get("object", {})) is not None
        if t in ("Subscript", "SliceAccess"):
            val = ir.get("value", {})
            _sl = ir.get("index")
            _is0 = (isinstance(_sl, dict) and _sl.get("type") == "Number"
                    and _sl.get("value") in (0, 0.0))
            return bool(isinstance(val, dict) and val.get("type") == "Attribute"
                        and val.get("attr") == "targets" and _is0
                        and self._pyast_stmt_child_var(val.get("object", {})) is not None)
        return False

    def _emit_ir_receiver_of_type_get(self, ir: Any) -> Optional[Dict[str, Any]]:
        """If `ir` is a reflection of a node's discriminant — `<recv>.get("type")` (Call
        with a bare `.get` func / a `receiver` sub-node) or the `.type`/`.kind` attribute
        access — over an `emit_ir` receiver, return the RECEIVER's IR dict; else None."""
        if not isinstance(ir, dict):
            return None
        t = ir.get("type")
        if t == "Call":
            _args = ir.get("args") or []
            _k0 = _args[0] if _args else None
            if not (isinstance(_k0, dict) and _k0.get("type") == "String"
                    and _k0.get("value") == "type"):
                return None
            _rcv = ir.get("receiver")
            if isinstance(_rcv, dict) and self._is_emit_ir_expr(_rcv):
                return _rcv
            _fn = ir.get("func", "")
            if isinstance(_fn, str) and _fn.endswith(".get"):
                _recv_ir = {"type": "Var", "name": _fn[:-len(".get")]}
                if self._is_emit_ir_expr(_recv_ir):
                    return _recv_ir
            return None
        if t in ("Attribute", "FieldGet") and (ir.get("attr") or ir.get("field")) in ("type", "kind"):
            _obj = ir.get("object")
            if isinstance(_obj, dict) and self._is_emit_ir_expr(_obj):
                return _obj
        return None

    def _emit_ir_kind_discriminant(self, left_ir: Any, right_ir: Any) -> Optional[str]:
        """tier3-p1 T3.1.2 (spike LAW 1): lower `<emit_ir>.get("type") == "K"` to the
        constructor discriminant `(is_K <recv>)` when K names an ADT kind that has one.
        Returns the WhyML bool term, or None (fall through to the `kind_of` string test)."""
        if not (isinstance(right_ir, dict) and right_ir.get("type") == "String"):
            return None
        _pred = self._KIND_DISCRIMINANT.get(right_ir.get("value"))
        if _pred is None:
            return None
        _recv = self._emit_ir_receiver_of_type_get(left_ir)
        if _recv is None and isinstance(left_ir, dict) and left_ir.get("type") == "Var":
            # KIND-LOCAL DISCRIMINANT FLOW (relaunch #11): the guard may test a LOCAL that
            # was bound ONCE from `<emit_ir>.get("type", …)` (`t = val_ir.get("type", "")`
            # … `if t == "IfExpr":`) rather than the reflection inline. Same receiver, same
            # faithfulness law — see `statements._collect_kind_local_recv` for why the
            # string test is not merely slower but genuinely INSUFFICIENT for a structural
            # recursion's `variant { size … }`.
            _recv = (getattr(self, "_kind_local_recv", None) or {}).get(left_ir.get("name"))
        if _recv is None:
            # allow the reflected form on either side (`"K" == node.get("type")`)
            return None
        _rv = self._expr_to_whyml(_recv, set(), False, None)
        return f"({_pred} {_rv})"

    def _recognize_str_constant_guard(self, expr: Any, local_refs: Optional[Set[str]] = None) -> Optional[str]:
        """SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): collapse
        the `_py_stmt_expr` docstring-skip guard

            isinstance(V, ast.Constant) and isinstance(V.value, str)

        — where `V` is an already-lowered ExprIR child (`stmt.value`) — to the single
        emit_ir constructor DISCRIMINANT `(is_str V)`. The compound is "V is a
        string-literal Constant": a string-literal `ast.Constant` node lowers (via
        `_py_expr_to_ir`/`_py_expr_constant`) to EXACTLY `IrStr`, so on every REAL node the
        two input-side isinstance tests agree with `is_str` (the same faithfulness law
        `_KIND_DISCRIMINANT` relies on). `isinstance(V, ast.Constant)` ALONE has no
        discriminant (a Constant lowers to IrNum/IrStr/IrBool/… by value), so only the
        WHOLE `and`-compound — pinned by the inner `.value is str` — is collapsible.
        Returns the WhyML bool term, or None (fall through to the generic `&&` lowering).
        Triple-gated (op `and` + `_is_emit_ir_expr(V)` + the `ast.Constant`/`str` class
        names) → corpus-inert."""
        if not (isinstance(expr, dict) and expr.get("type") == "BinOp"
                and expr.get("op") == "and"):
            return None
        left = expr.get("left")
        right = expr.get("right")
        # left: isinstance(V, ast.Constant)
        if not (isinstance(left, dict) and left.get("type") == "Call"
                and left.get("func") == "isinstance"):
            return None
        largs = left.get("args") or []
        if len(largs) != 2:
            return None
        vexpr, lcls = largs[0], largs[1]
        if not (isinstance(lcls, dict) and lcls.get("type") == "Attribute"
                and isinstance(lcls.get("object"), dict)
                and lcls["object"].get("type") == "Var"
                and lcls["object"].get("name") == "ast"
                and lcls.get("attr") == "Constant"):
            return None
        if not self._is_emit_ir_expr(vexpr):
            return None
        # right: isinstance(V.value, str)
        if not (isinstance(right, dict) and right.get("type") == "Call"
                and right.get("func") == "isinstance"):
            return None
        rargs = right.get("args") or []
        if len(rargs) != 2:
            return None
        vval, rcls = rargs[0], rargs[1]
        if not (isinstance(rcls, dict) and rcls.get("type") == "Var"
                and rcls.get("name") == "str"):
            return None
        # `V.value` — the SAME child `V` with a `.value` attribute projection.
        if not (isinstance(vval, dict) and vval.get("type") == "Attribute"
                and vval.get("attr") == "value" and vval.get("object") == vexpr):
            return None
        _vw = self._expr_to_whyml(vexpr, local_refs or set(), getattr(self, "_in_spec", False), None)
        _pred = f"(is_str {_vw})"
        # Match the generic `and`-binop convention: a bare bool in spec context, the
        # int-coerced `(if b then 1 else 0)` in body context (Python and/or return int;
        # the `_to_bool` truthiness wrapper then appends `<> 0`).
        if getattr(self, "_in_spec", False):
            return _pred
        return f"(if {_pred} then 1 else 0)"

    def _recognize_none_constant_guard(self, expr: Any, local_refs: Optional[Set[str]] = None) -> Optional[str]:
        """value-model campaign incr8: collapse the compound

            isinstance(x, ast.Constant) and x.value is None

        — where `x` is an already-lowered ExprIR arm — to the single emit_ir constructor
        DISCRIMINANT `(is_none x)`. SYMMETRIC to `_recognize_str_constant_guard` (which handles
        the `.value is str` sibling): a `None`-literal `ast.Constant` lowers (via
        `_py_expr_constant`) to EXACTLY `{"type":"None"}` = `IrNone`, so on every REAL node the
        compound agrees with `is_none x` (the faithful match dispatch). `isinstance(x,
        ast.Constant)` ALONE has no discriminant (a Constant lowers to IrNum/IrStr/IrNone/… by
        value), so only the WHOLE `and`-compound — pinned by the inner `x.value is None` — is
        collapsible; this is the FAITHFUL alternative to the (impossible) pyconst_val narrowing,
        since the emit_ir arm carries no pyconst_val. Triple-gated (op `and` +
        `_is_emit_ir_expr(x)` + the `ast.Constant` class + the `.value is None` shape) →
        corpus-inert. Returns the WhyML bool term, or None (fall through to the generic `&&`)."""
        if not (isinstance(expr, dict) and expr.get("type") == "BinOp"
                and expr.get("op") == "and"):
            return None
        left = expr.get("left")
        right = expr.get("right")
        # left: isinstance(x, ast.Constant)
        if not (isinstance(left, dict) and left.get("type") == "Call"
                and left.get("func") == "isinstance"):
            return None
        largs = left.get("args") or []
        if len(largs) != 2:
            return None
        vexpr, lcls = largs[0], largs[1]
        if not (isinstance(lcls, dict) and lcls.get("type") == "Attribute"
                and isinstance(lcls.get("object"), dict)
                and lcls["object"].get("type") == "Var"
                and lcls["object"].get("name") == "ast"
                and lcls.get("attr") == "Constant"):
            return None
        if not self._is_emit_ir_expr(vexpr):
            return None
        # right: `x.value is None` — a BinOp (`is`/`==`) whose left is `x.value` (the SAME arm
        # `x` with a `.value` projection) and whose right is the `None` literal.
        if not (isinstance(right, dict) and right.get("type") == "BinOp"
                and right.get("op") in ("is", "==")):
            return None
        rl, rr = right.get("left"), right.get("right")
        if not (isinstance(rr, dict) and rr.get("type") == "None"):
            return None
        if not (isinstance(rl, dict) and rl.get("type") == "Attribute"
                and rl.get("attr") == "value" and rl.get("object") == vexpr):
            return None
        _vw = self._expr_to_whyml(vexpr, local_refs or set(), getattr(self, "_in_spec", False), None)
        _pred = f"(is_none {_vw})"
        if getattr(self, "_in_spec", False):
            return _pred
        return f"(if {_pred} then 1 else 0)"

    def _effective_emit_ir_node_keys(self) -> Tuple[str, ...]:
        """self-tcb-reduction Layer-2: the emit_ir sub-NODE keys in effect for the CURRENT
        handler — the global `_EMIT_IR_NODE_KEYS` plus any `_EMIT_IR_EXTRA_NODE_KEYS_BY_FUNC`
        entry scoped to `_current_emitting_func`. Keeps the `lower`/`upper`/`step` node-key
        extension confined to `_match_field_decode_idiom` (byte-inert elsewhere)."""
        _cef = getattr(self, "_current_emitting_func", None) or ""
        for _h, _extra in _EMIT_IR_EXTRA_NODE_KEYS_BY_FUNC.items():
            if _cef == _h or _cef.endswith("__" + _h):
                return _EMIT_IR_NODE_KEYS + tuple(_extra)
        return _EMIT_IR_NODE_KEYS

    def _is_emit_ir_expr(self, ir: Any) -> bool:
        """typed-ir-for-b-ceiling.md B-C2: True if `ir` lowers to the `emit_ir` sum — an
        inline `{"type": K}` construction, an ExprIR-valued record field read
        (`stmt.upper`), or an ExprIR-typed Var (param/local). Used to type `x is None`
        and other emit_ir-vs-int decisions. Gated by the ExprIR annotation tags."""
        if not isinstance(ir, dict):
            return False
        t = ir.get("type")
        # PYTHON-AST NODE CTOR FAMILY (increment 11): a pure_ast node CONSTRUCTION
        # (`_N("Name")(id=…, ctx=…)`) lowers to an `emit_ir` ADT application, so a local
        # bound from one is an emit_ir local — it must be PRE-DECLARED `ref (IrOther "")`
        # rather than `let`-bound immutable, or a body that REBUILDS it in a loop
        # (`node = _N("Attribute")(value=node, …)`, the dotted-name fold) emits a `:=`
        # against a non-ref and fails L3-tc. `self._fin(<ctor>, …)` / `self._fin_pos(…)`
        # are the parser's location-stamping wrappers and lower to their FIRST argument,
        # so they are transparent here. Gated on `_uses_pyast_parser` -> byte-inert.
        if t == "Call" and isinstance(ir.get("func"), str) and self._uses_pyast_parser():
            _f = ir["func"]
            if _f in ("self._fin", "self._fin_pos"):
                _a = (ir.get("args") or [None])[0]
                if isinstance(_a, dict) and self._is_emit_ir_expr(_a):
                    return True
            else:
                from frontend.ir_resolve import _PYAST_IRNODE_CTORS as _PYC
                if _f in _PYC:
                    return True
        # VARIABLE-CLASS-NAME CONSTRUCTION (relaunch #8): `n = _N(cls)(…)` builds a node
        # exactly as the literal-class form does, so the local is an emit_ir local and
        # must get the `ref (IrOther "")` pre-decl rather than the integer `ref 0` (which
        # its `:=` would then clash with). Recognized ONLY when the class-name local really
        # is a harvested two-literal ternary AND BOTH classes are family members — the same
        # condition under which the lowering itself produces an ADT application, so the
        # typing and the lowering can never disagree.
        if t == "ClassByNameCall" and self._uses_pyast_parser():
            _cbe = ir.get("class_expr") or {}
            _cbm = getattr(self, "_class_name_ternary_locals", {}) or {}
            _cbn = (_cbm.get(_cbe.get("name"))
                    if isinstance(_cbe, dict) and _cbe.get("type") == "Var" else None)
            if _cbn is not None:
                from frontend.ir_resolve import _PYAST_IRNODE_CTORS as _PYCB
                if _cbn[1] in _PYCB and _cbn[2] in _PYCB:
                    return True
        # self-tcb-reduction giants: a `pyast_stmt` emit_ir-yielding projector
        # (`child.value`/`child.target`/`child.targets[0]`) IS an emit_ir sub-node.
        if self._is_pyast_stmt_emit_ir_read(ir):
            return True
        # L1 tparam reflection-node ADT: `tp.bound` (a `tp_bound` projector over a tparam
        # loop var) IS an emit_ir sub-node, so its isinstance/`.id`/`.attr` reuse the
        # emit_ir machinery.
        if self._is_tparam_bound_read(ir):
            return True
        if t == "DictLit":
            for k in ir.get("keys", []):
                if isinstance(k, dict) and k.get("type") == "String" and k.get("value") == "type":
                    return True
            return False
        # self-tcb-reduction _field_type_of: a value-preserving `A or B` / `A and B`
        # over emit_ir operands (the `receiver = attr_ir.get("value") or
        # attr_ir.get("object") or {}` idiom) is itself an emit_ir node — the Lever-6
        # short-circuit at `_handle_binop` returns the SELECTED operand, an emit_ir
        # value. Each operand must be emit_ir OR the falsy empty-dict `{}` (the absent
        # sentinel, lowered to `IrOther ""`); at least ONE must be a real emit_ir node
        # (a pure `{} or {}` is not one). Gated on `_is_emit_ir_expr` of the operands →
        # a corpus `x or y` (int operands) never matches, so this is byte-inert.
        if t in ("BinOp", "BoolOp") and ir.get("op") in ("or", "and"):
            def _op_is_emit_ir_or_empty(o: Any) -> bool:
                return (self._is_emit_ir_expr(o)
                        or (isinstance(o, dict) and o.get("type") == "DictLit"
                            and not o.get("keys")))
            _lo = ir.get("left", {})
            _ro = ir.get("right", {})
            if (_op_is_emit_ir_or_empty(_lo) and _op_is_emit_ir_or_empty(_ro)
                    and (self._is_emit_ir_expr(_lo) or self._is_emit_ir_expr(_ro))):
                return True
            return False
        if t in ("Attribute", "FieldGet"):
            obj = ir.get("object", {})
            if isinstance(obj, dict) and obj.get("type") == "Var":
                rec = getattr(self, "_current_symbol_table", {}).get(obj.get("name", ""))
                rt = getattr(self, "_record_types", {}).get(rec)
                if rt:
                    # cf6.md M1.5: a field carrying a `value_type` (element type) is a COLLECTION
                    # (`List[ExprIR]` → `array emit_ir`), NOT a scalar node — `_irnode_ann_name`
                    # mis-tags `List[ExprIR]` as scalar `"ExprIR"`, so guard on the collection
                    # marker. A scalar `value: ExprIR` field has no value_type → still matched.
                    if ir.get("attr", "") in rt.get("field_value_types", {}):
                        return False
                    ft = rt.get("field_types", {}).get(ir.get("attr", ""))
                    return ft in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR", "emit_ir")
            # self-ir-schema.md IR2: `<emit_ir>.value` / `.target` (a StmtIR field access on
            # an emit_ir node, e.g. `body_stmts[-1].value`) is itself an emit_ir sub-node.
            # self-tcb-reduction T1.a: EXCLUDE node-LIST attrs (`.elts`/`.parts`/…) — those are
            # `array emit_ir` (`args_of`), NOT a scalar node, so they are collected as array locals.
            # value-model campaign: EXCLUDE STRING-LEAF attrs (`_EMIT_IR_STR_ATTRS`: `.id`/`.var`/
            # `.kind`/`.op`/`.name`/`.func`/…) — those route to a `string` projector (name_of/kind_of/
            # op_of/func_of), NOT an emit_ir sub-node projector, so `x = node.id` types `string` (a
            # str-returning `.id`-reader must NOT be a `_returns_emit_ir` local). Symmetric with
            # `_is_string_expr`'s `(attr in _EMIT_IR_STR_ATTRS)` string-leaf check at its Attribute
            # branch — the two recognizers now agree on what `<emit_ir>.<str-attr>` is.
            _at = ir.get("attr") or ir.get("field")
            if (_at not in ("elts", "parts", "args", "captures", "alternatives")
                    and _at not in _EMIT_IR_STR_ATTRS
                    and isinstance(obj, dict) and self._is_emit_ir_expr(obj)
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())):
                return True
            return False
        if t == "Var":
            if ir.get("name", "") in getattr(self, "_todict_aliases", {}):
                return True   # `arr = stmt.array.to_dict()` aliases an emit_ir node
            return getattr(self, "_current_symbol_table", {}).get(ir.get("name", "")) in (
                "ExprIR", "StmtIR", "IRNode", "ContractExprIR")
        # B-C5: an args-list ELEMENT `<emit_ir Call>.args[i]` / `(… or [{}])[i]` is an
        # emit_ir sub-node (arg0_of), so a local bound from it types as emit_ir (§19).
        if t in ("Subscript", "SliceAccess"):
            if self._emit_ir_args_recv_ir(ir.get("value", {})) is not None:
                return True
            if self._emit_ir_args_recv_ir(ir.get("value", {}), "elts") is not None:
                return True
            # value-model campaign incr5: a TYPED `<emit_ir>.elts[i]` element (the dict-type
            # walkers' IrMkTupleN irlist path) is an emit_ir sub-node (`irnth i (elts_of recv)`).
            if self._mktuple_elts_recv_ir(ir.get("value", {})) is not None:
                return True
            # self-ir-schema.md IR2 / seq-model-pivot.md SQ3: an element of an `array emit_ir`
            # OR `seq emit_ir` local (`body_stmts[-1]`) is an emit_ir node.
            _vv = ir.get("value", {})
            if (isinstance(_vv, dict) and _vv.get("type") == "Var"
                    and (getattr(self, "_array_elem_types", {}).get(_vv.get("name")) == "emit_ir"
                         or getattr(self, "_seq_value_types", {}).get(_vv.get("name")) == "emit_ir")):
                return True
            # §26: a projection-key subscript `<emit_ir>["value"/"object"/"index"]`
            # is an emit_ir sub-node (chaining, e.g. `arr["value"]["name"]`).
            # self-tcb-reduction T1.a: EXCLUDE subscript "object" — `expr['object']` is the object
            # NAME string (`name_of ∘ object_of`), not a sub-node (see `_handle_subscript`).
            _kir = ir.get("index", {})
            if (isinstance(_kir, dict) and _kir.get("type") == "String"
                    and _kir.get("value") in self._effective_emit_ir_node_keys()
                    and _kir.get("value") != "object"
                    and self._is_emit_ir_expr(ir.get("value", {}))):
                return True
        # item34.md CF1: `<x>.to_dict()` (no args) is an emit_ir node (to_dict is identity on
        # the typed IR) in a @mutable_state module.
        if (t == "Call" and isinstance(ir.get("func"), str)
                and ir["func"].endswith(".to_dict") and not ir.get("args")
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            return True
        # §26: a `.get("value"/"object"/"index")` on an emit_ir receiver is an emit_ir
        # sub-node (nested `.get` chaining, e.g. `arr.get("value").get("type")`).
        if t == "Call":
            _fn = ir.get("func")
            if isinstance(_fn, str) and _fn.endswith(".get"):
                _a = ir.get("args") or []
                # self-tcb-reduction _namedtuple_positional_access (gap-2b): inside a func
                # whose `.get("value")` is SCOPED (in `_EMIT_IR_GET_KEY_PROJ_BY_FUNC`) to the
                # Number-leaf INT payload (`num_of`, no empty-dict / str-literal default — see
                # the `_scoped_val` routing in `_lower_dict_get_call`), the read is an `int`,
                # NOT an emit_ir sub-node. Mirror that num_of routing here so the target local
                # is typed `int` (not pre-declared `ref (IrOther "")`). Byte-inert: `_scoped2`
                # only fires for the self-annotation emitter-method names.
                _cef2b = getattr(self, "_current_emitting_func", None) or ""
                _ent2b = next((_t for _h, _t in _EMIT_IR_GET_KEY_PROJ_BY_FUNC.items()
                               if _cef2b == _h or _cef2b.endswith("__" + _h)), None)
                # Only an EMPTY scoped entry (`{}`) is the num_of-value marker (added by
                # `_namedtuple_positional_access`). A NON-empty entry (e.g. `_field_type_of`'s
                # `{object,field}`) reads `.get("value")` via the receiver-IDIOM recognizer
                # (`X.get("value") or X.get("object")` -> `avalue_of`, an emit_ir sub-node),
                # so its operand MUST stay emit_ir — do NOT exclude it (that regressed
                # `_field_type_of`, whose `receiver` local then mistyped `int`).
                _routes_num = (_ent2b is not None and not _ent2b
                               and _a and isinstance(_a[0], dict)
                               and _a[0].get("value") == "value"
                               and not self._get_default_is_empty_dict(ir)
                               and not self._get_default_is_str_literal(ir))
                if (len(_a) >= 1 and isinstance(_a[0], dict)
                        and _a[0].get("type") == "String"
                        and _a[0].get("value") in self._effective_emit_ir_node_keys()
                        # self-tcb-reduction _typeddict_field_access (gap-1): a STRING-literal
                        # default (`index_ir.get("value", "")`) means the string-content read
                        # (`value_of`, a `string`), NOT the emit_ir sub-node -> not emit_ir.
                        and not self._get_default_is_str_literal(ir)
                        and not _routes_num
                        and self._is_emit_ir_expr({"type": "Var", "name": _fn[:-len(".get")]})):
                    return True
        # Lever 6: a `self.<method>(...)` / bare `<func>(...)` call whose DECLARED
        # return type is the emit_ir IR-node sum (an `-> ExprIR`/`StmtIR`/`IRNode`/
        # `ContractExprIR` annotation, which Module5 maps to "emit_ir" in
        # `_module_method_return_types`) IS an emit_ir node. This is what lets the
        # value-preserving `or`/`and` fire over structured operands — the
        # `_first_assign_value_ir(...) or _first_assign_value_ir(...)` fed to
        # `_try_local_decl_kind` from the verified `_handle_try_stmt`. Gated on the
        # emit_ir return type: no CORPUS method carries an ExprIR-family return
        # annotation (those types name the emitter's own AST/IR node classes), so
        # `_module_method_return_types[...] == "emit_ir"` never holds on corpus code —
        # this branch never fires there (byte-inert). Mirrors the `self.`-prefix key
        # mangling used by `_rhs_yields_map`/`_rhs_yields_array`.
        if t == "Call":
            _mfn = ir.get("func")
            if isinstance(_mfn, str):
                if _mfn.startswith("self."):
                    _mtail = _mfn[len("self."):]
                    _mcls = getattr(self, "_current_self_type", None)
                    _mkey = f"{_mcls}__{_mtail}" if _mcls else _mtail
                else:
                    _mkey = _mfn
                if getattr(self, "_module_method_return_types", {}).get(_mkey) == "emit_ir":
                    return True
        return False

    def _pyconst_val_field_read(self, ir: Any) -> Optional[Dict[str, Any]]:
        """pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): if `ir` reads
        a `pyconst_val`-typed record field (`expr.value` where `expr` is a Constant-record
        param whose harvested `value` field has type "PyConstVal", ir_resolve.py
        `_PURE_AST_FIELD_TABLE`), return `ir` itself (the field-read node, which lowers to
        the record projection); else None. Mirrors `_is_emit_ir_expr`'s Attribute branch —
        keyed on the param's record type in `_current_symbol_table` and the field's
        declared type in `_record_types[...]["field_types"]`. This is the discriminant a
        `_py_expr_constant`-style value-type test (`isinstance(expr.value, bool/str/int)` /
        `expr.value is None`) reflects on."""
        if not (isinstance(ir, dict) and ir.get("type") in ("Attribute", "FieldGet")):
            return None
        obj = ir.get("object", {})
        if not (isinstance(obj, dict) and obj.get("type") == "Var"):
            return None
        rec = getattr(self, "_current_symbol_table", {}).get(obj.get("name", ""))
        rt = getattr(self, "_record_types", {}).get(rec)
        if not rt:
            return None
        ft = rt.get("field_types", {}).get(ir.get("attr") or ir.get("field"))
        return ir if ft == "PyConstVal" else None

    def _optexprir_field_read(self, ir: Any) -> Optional[Dict[str, Any]]:
        """SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): if `ir`
        reads an `OptExprIR`-typed record field (`stmt.value` where `stmt` is an AnnAssign-
        record param whose harvested `value` field has type "OptExprIR" -> `option emit_ir`,
        ir_resolve.py `_PURE_AST_FIELD_TABLE`), return `ir` itself; else None. Sibling of
        `_pyconst_val_field_read`, keyed on the param's record type in
        `_current_symbol_table` and the field's declared "OptExprIR" tag. This is the
        discriminant a bare `stmt.value is not None` presence guard reflects on — the
        FAITHFUL option `is-Some` test (a real match, NOT the emit_ir always-present model),
        so the guarded append is non-vacuous (a value-less annotation `x: T` is skipped)."""
        if not (isinstance(ir, dict) and ir.get("type") in ("Attribute", "FieldGet")):
            return None
        obj = ir.get("object", {})
        if not (isinstance(obj, dict) and obj.get("type") == "Var"):
            return None
        rec = getattr(self, "_current_symbol_table", {}).get(obj.get("name", ""))
        rt = getattr(self, "_record_types", {}).get(rec)
        if not rt:
            return None
        _fld = ir.get("attr") or ir.get("field")
        ft = rt.get("field_types", {}).get(_fld)
        vt = rt.get("field_value_types", {}).get(_fld)
        # The harvested OptExprIR field lands as `{"type":"option","value_type":"emit_ir"}`
        # (ir_resolve.py `_harvest_node_spec_records`) -> field_types "option" +
        # field_value_types "emit_ir".
        return ir if (ft == "option" and vt == "emit_ir") else None

    @staticmethod
    def _is_number_dictlit(elt: Any) -> bool:
        """pyconst_val bytes comprehension: True iff `elt` is an inline `{"type":"Number",
        "value": …}` IR-node construction (a DictLit whose "type" key is the String
        "Number") — the per-byte `IrNum b` element of the bytes comprehension."""
        if not (isinstance(elt, dict) and elt.get("type") == "DictLit"):
            return False
        for k, v in zip(elt.get("keys", []), elt.get("values", [])):
            if (isinstance(k, dict) and k.get("type") == "String" and k.get("value") == "type"
                    and isinstance(v, dict) and v.get("type") == "String"
                    and v.get("value") == "Number"):
                return True
        return False

    def _pyconst_bytes_comp(self, node: Any, local_refs: Set[str], invariant_ctx: bool,
                            subst: Optional[Dict[str, str]]) -> Optional[str]:
        """pyconst_val bytes content-comprehension (self-tcb-reduction M5, B-bucket): lower
        `[{"type":"Number","value":b} for b in expr.value]` (one generator, no filter, a
        `pyconst_val`-typed `.value` source, a per-byte `IrNum` element) to
        `(bytes_content_comp (pvbytes_of expr.value))` : irlist. Returns None for any other
        shape (the caller then tries the generic comprehension paths). See preamble.py
        `bytes_content_comp`."""
        _d = node.to_dict()
        gens = _d.get("generators", []) or []
        if len(gens) != 1:
            return None
        g = gens[0]
        if g.get("ifs"):
            return None
        if not isinstance(g.get("target"), str):
            return None
        src_ir = g.get("iter", {})
        if self._pyconst_val_field_read(src_ir) is None:
            return None
        if not self._is_number_dictlit(_d.get("elt", {})):
            return None
        _srcw = self._expr_to_whyml(src_ir, local_refs or set(), invariant_ctx, subst)
        return f"(bytes_content_comp (pvbytes_of {_srcw}))"

    def _todict_recv_node_ir(self, recv_dotted: str) -> Dict[str, Any]:
        """The node IR for a dotted receiver (`self.types` → `Attribute(Var(self), types)`)."""
        parts = recv_dotted.split(".")
        node: Dict[str, Any] = {"type": "Var", "name": parts[0]}
        for p in parts[1:]:
            node = {"type": "Attribute", "object": node, "attr": p}
        return node

    @staticmethod
    def _getattr_self_field(recv: "ExprIR") -> str:
        """typed-ir-for-b-ceiling.md §14: if `recv` is `getattr(self, "<field>", …)`
        (a defensive self-field access) return the string `<field>`, else None."""
        if not (isinstance(recv, dict) and recv.get("type") == "Call"
                and recv.get("func") == "getattr"):
            return ""
        a = recv.get("args", [])
        if (len(a) >= 2 and isinstance(a[0], dict) and a[0].get("name") == "self"
                and isinstance(a[1], dict) and a[1].get("type") == "String"):
            return a[1].get("value")
        return ""

    def _alias_self_field(self, name: str) -> str:
        """§26: if `name` is a local bound from `getattr(self, "<field>", …)` on a
        dict/set self-field, return the dotted `self.<field>`; else None."""
        fld = getattr(self, "_getattr_self_dict_aliases", {}).get(name)
        return f"self.{fld}" if fld else ""

    def _iter_elem_class(self, iter_ir: "ExprIR") -> str:
        """self-ir-schema.md IR2: the record class of a comprehension iterable's ELEMENTS,
        for typing the loop var during element-type inference. `self.ir.get("shared_vars")`
        → "sharedvar"; None otherwise (the loop var stays untyped)."""
        if (isinstance(iter_ir, dict) and iter_ir.get("type") == "Call"
                and iter_ir.get("func") == "self.ir.get"):
            _a = iter_ir.get("args") or []
            if (_a and isinstance(_a[0], dict) and _a[0].get("type") == "String"
                    and _a[0].get("value") == "shared_vars"):
                return "sharedvar"
        # item34.md CF5: iterating a `string`-element name-collection (`for e in body_raised`,
        # `for tag in candidates`) binds the loop var to a `string` — so `handler_catches(base,
        # e)`/`whyml_ident(var)` type-check. Covers both the array-elem and seq-value maps.
        if (isinstance(iter_ir, dict) and iter_ir.get("type") == "Var"
                and (getattr(self, "_array_elem_types", {}).get(iter_ir.get("name")) == "string"
                     or getattr(self, "_seq_value_types", {}).get(iter_ir.get("name")) == "string")):
            return "str"
        return ""

    def _todict_emit_ir_projection(self, recv_dotted, key, local_refs, invariant_ctx, subst):
        node = self._todict_recv_node_ir(recv_dotted)
        if not self._is_emit_ir_expr(node): return None
        # B-C5: "func" projects to `func_of` (string); "value"/"index" to `svalue_of`/
        # `sindex_of` (emit_ir SUB-NODES — the reflecting handlers always pass them to
        # `_expr_to_whyml` or reflect further, never use them as a string).
        proj = _EMIT_IR_PROJ.get(key)
        if proj is None: return None
        return f"({proj} {self._expr_to_whyml(node, local_refs or set(), invariant_ctx, subst)})"

    def _emit_ir_args_recv_ir(self, arg_ir, key="args"):
        """B-C5: if `arg_ir` reads the "args" list of an emit_ir Call node — either the
        `<emit_ir>.get("args")` (Call) form OR the `<emit_ir>["args"]` (Subscript) form —
        return the receiver's emit_ir IR node, so `len(...)` lowers to `nargs_of` and
        `...[0]` to `arg0_of`. None otherwise.

        B-C6: `key` generalises this to any list-valued reflection key; `key="elts"`
        recognises a MkTuple node's `elts` list (routed to `elt{i}_of` by the caller)."""
        if not isinstance(arg_ir, dict):
            return None
        t = arg_ir.get("type")
        node = None
        # unwrap the defensive default `(<emit_ir>.get("args") or [{}])` — arg0_of already
        # returns IrOther "" for a non-Call, so the explicit `or <default>` is subsumed.
        if t == "BoolOp" and arg_ir.get("op") == "or":
            _vs = arg_ir.get("values", [])
            return self._emit_ir_args_recv_ir(_vs[0], key) if _vs else None
        if t == "BinOp" and arg_ir.get("op") == "or":
            return self._emit_ir_args_recv_ir(arg_ir.get("left", {}), key)
        if t == "Call":
            fn = arg_ir.get("func")
            if not (isinstance(fn, str) and fn.endswith(".get")):
                return None
            kir = (arg_ir.get("args") or [{}])[0]
            if not (isinstance(kir, dict) and kir.get("type") == "String"
                    and kir.get("value") == key):
                return None
            recv = fn[:-len(".get")]
            dotted = getattr(self, "_todict_aliases", {}).get(recv)
            node = (self._todict_recv_node_ir(dotted) if dotted
                    else {"type": "Var", "name": recv})
        elif t in ("Subscript", "SliceAccess"):
            kir = arg_ir.get("index", {})
            if not (isinstance(kir, dict) and kir.get("type") == "String"
                    and kir.get("value") == key):
                return None
            v = arg_ir.get("value", {})
            if isinstance(v, dict) and v.get("type") == "Var":
                dotted = getattr(self, "_todict_aliases", {}).get(v.get("name"))
                node = self._todict_recv_node_ir(dotted) if dotted else v
            else:
                node = v
        if node is None:
            return None
        return node if self._is_emit_ir_expr(node) else None

    def _mktuple_elts_recv_ir(self, arg_ir):
        """value-model campaign incr5: if `arg_ir` is a TYPED `<emit_ir>.elts` read AND we
        are emitting one of the dict-type walkers (`_MKTUPLE_ELTS_HANDLERS`), return the
        receiver emit_ir node — so `<recv>.elts[i]` lowers to `irnth i (elts_of recv)` and
        `len(<recv>.elts)` to `irlen (elts_of recv)`, the MODELLED IrMkTupleN irlist path
        (not the opaque `args_of`, and not `elt{i}_of` which projects only binary IrTuple ->
        `IrOther ""`). None otherwise. Scoped via `_current_emitting_func` (endswith match)
        so every corpus program and other-mirror handler emits byte-identically."""
        _cef = getattr(self, "_current_emitting_func", None) or ""
        if not any(_cef == h or _cef.endswith("__" + h) for h in _MKTUPLE_ELTS_HANDLERS):
            return None
        if not (isinstance(arg_ir, dict) and arg_ir.get("type") == "Attribute"
                and arg_ir.get("attr") == "elts"):
            return None
        recv = arg_ir.get("object", {})
        return recv if self._is_emit_ir_expr(recv) else None

    def _str_method_recv_and_tail(self, expr):
        """faithful-string-op.md §4: for a string-method call `recv.tail(args)`, return
        (receiver_ir, tail). Computed receiver → `expr['receiver']`; dotted simple-var
        form (`s.replace`, `func.rsplit`) → a Var IR for the part before the last '.'.
        A dotted MULTI-part receiver (`self.x.replace`) returns (None, None) — it falls
        through to the opaque path (no regression) rather than mis-reconstructing."""
        fn = expr.get("func", "")
        if expr.get("receiver") is not None:
            return expr["receiver"], fn
        if isinstance(fn, str) and "." in fn:
            recv, tail = fn.rsplit(".", 1)
            if "." not in recv:
                return {"type": "Var", "name": recv}, tail
            # value-model campaign incr9: a `<emit_ir-var>.<str-leaf-attr>.<method>()` receiver
            # (`ann.id.lower()`, `ann.attr.lower()` in `_overload_type_name`) — reconstruct the
            # string-leaf attribute read as its Attribute IR so `.lower()`/`.strip()` reaches the
            # faithful `str_lower_op`/`str_strip_op` path (else the whole dotted name is a vacuous
            # opaque nullary op). Gated on the 2-part shape + `<v>` typed `ExprIR` in the symbol
            # table + `<a>` a recognized `_EMIT_IR_STR_ATTRS` string-leaf → corpus-inert (no
            # corpus receiver is an emit_ir var) and inert for handlers that read a str-leaf on a
            # SPECIFIC record (not a base ExprIR var).
            _rparts = recv.split(".")
            # value-model campaign incr10: generalize to an N-part chain
            # (`elt.value.id.lower()`, `inner.value.id.lower()`) — the FIRST part is the emit_ir
            # var, the LAST is the string-leaf attr, the MIDDLE parts (`.value`) are emit_ir
            # sub-node projections. Reconstruct the whole nested Attribute IR so `.lower()`
            # reaches `str_lower_op (name_of (svalue_of …))`, not a vacuous opaque op.
            if len(_rparts) >= 2 and _rparts[-1] in _EMIT_IR_STR_ATTRS:
                _v = _rparts[0]
                if getattr(self, "_current_symbol_table", {}).get(_v) in (
                        "ExprIR", "StmtIR", "IRNode", "ContractExprIR"):
                    _node = {"type": "Var", "name": _v}
                    for _a in _rparts[1:]:
                        _node = {"type": "Attribute", "object": _node, "attr": _a}
                    return (_node, tail)
        return None, None

    def _split_call_recv_sep(self, call_ir):
        """faithful-string-op.md §3.4: if `call_ir` is `<string>.split(sep)` or
        `<string>.rsplit(sep, k)`, return (receiver_ir, sep_ir) [sep_ir may be None for a
        no-arg split]; else None. Used to lower `<split>[i]` to `str_split_elem_op`."""
        if not isinstance(call_ir, dict) or call_ir.get("type") != "Call":
            return None
        recv_ir, tail = self._str_method_recv_and_tail(call_ir)
        if tail not in ("split", "rsplit") or recv_ir is None:
            return None
        if not self._is_string_expr(recv_ir):
            return None
        return recv_ir, (call_ir.get("args") or [None])[0]

    def _split_comp_array_string(self, node, local_refs, invariant_ctx, subst):
        """faithful-string-op.md §3.4 (whole-list): a comprehension
        `[<str-elt> for t in <string>.split(sep) (if …)]` — a SINGLE generator over a
        `<string>.split(sep)`/`.rsplit` source whose element expression is itself
        string-typed once the target `t` is bound to a string — lowers to an OPAQUE
        `array string` (content unmodelled, `length >= 0` only: a sound under-approximation,
        exactly like `str_split_elem_op` for the element read). This is the whole-list
        counterpart of the split-ELEM path (`<split>[i]`): the split value AS a list of
        strings, so a `List[str]` return/local built by `[p.strip() for p in s.split(",")]`
        types faithfully instead of collapsing to the opaque int `list_comp`.

        Tightly gated on the split shape AND a string-valued element, so a non-split or
        int-element comprehension stays on the existing int/opaque path (byte-identical).
        M2-split-comp-return: tried BEFORE the @mutable_state opaque-length path (not just
        outside it) — a `.split(...)`-sourced comprehension under @mutable_state would
        otherwise mismatch (`list_comp_string` over the CF5 `seq string` split source vs the
        declared `array string`). None if not applicable."""
        _d = node.to_dict()
        _gens = _d.get("generators", []) or []
        if len(_gens) != 1:
            return None
        _g = _gens[0]
        _rs = self._split_call_recv_sep(_g.get("iter", {}))
        if _rs is None:
            return None
        _recv_ir, _sep_ir = _rs
        _tgt = _g.get("target")
        if not isinstance(_tgt, str):
            return None
        _elt = _d.get("elt", {})
        # Type the loop target as a string (the split yields string ELEMENTS) and require
        # the element expression to be string-valued under that binding — else the
        # comprehension is NOT `array string` (e.g. `[len(p) for p in s.split(sep)]` stays
        # int). Restore the symbol table afterwards (the comprehension itself is opaque).
        _symtab = getattr(self, "_current_symbol_table", None)
        _had = _symtab is not None and _tgt in _symtab
        _old = _symtab.get(_tgt) if _symtab is not None else None
        if _symtab is not None:
            _symtab[_tgt] = "str"
        try:
            _elt_str = self._is_string_expr(_elt)
        finally:
            if _symtab is not None:
                if _had:
                    _symtab[_tgt] = _old
                else:
                    _symtab.pop(_tgt, None)
        if not _elt_str:
            return None
        _recvw = self._expr_to_whyml(_recv_ir, local_refs or set(), invariant_ctx, subst)
        _sepw = (self._expr_to_whyml(_sep_ir, local_refs or set(), invariant_ctx, subst)
                 if _sep_ir is not None else '" "')
        self._add_abstract_op(
            "val str_split_op (s: string) (sep: string) : array string\n"
            "    ensures { Array.length result >= 0 }")
        return f"(str_split_op {_recvw} {_sepw})"

    def _is_literal_string_join(self, ir):
        """faithful-string-op.md §3.5: True if `ir` is `sep.join([s0, s1, …])` over a
        LITERAL list/tuple of STRING elements (receiver form) — the case
        `_handle_join_call` lowers to nested `str_concat_op` (a `string`)."""
        if not isinstance(ir, dict) or ir.get("type") != "Call":
            return False
        if ir.get("func") != "join" or ir.get("receiver") is None:
            return False
        a = (ir.get("args") or [{}])[0]
        if not isinstance(a, dict) or a.get("type") not in ("ArrayLit", "ListLit", "Tuple"):
            return False
        elts = a.get("elts", [])
        return bool(elts) and all(self._is_string_expr(e) for e in elts)

    _STR_VALUE_METHODS = ("replace", "lower", "upper", "strip", "lstrip", "rstrip")

    def _is_str_value_method(self, expr):
        """True if `expr` is a faithful string-VALUED method call on a string receiver
        (§3.1–3.3). Shared by `_is_string_expr` (typing) and `_handle_string_value_method`
        (lowering) so the two never disagree."""
        if not isinstance(expr, dict) or expr.get("type") != "Call":
            return False
        recv_ir, tail = self._str_method_recv_and_tail(expr)
        if tail not in self._STR_VALUE_METHODS or recv_ir is None:
            return False
        return self._is_string_expr(recv_ir)

    def _handle_string_value_method(self, expr, args, local_refs, invariant_ctx, subst):
        """faithful-string-op.md §3.1–3.3: lower `.replace`/`.lower`/`.upper`/`.strip`/
        `.lstrip`/`.rstrip` on a string receiver to a faithful `string`-typed abstract op
        with the STRONGEST SOUND length law (never over-claiming — the str_repr_op
        discipline). None if not applicable."""
        if not self._is_str_value_method(expr):
            return None
        recv_ir, tail = self._str_method_recv_and_tail(expr)
        # cleared-string RESIDUALS (items 1-2): CONSTANT-FOLD when the receiver (and,
        # for `.replace`, both arguments) are STRING LITERALS. Python's OWN str method
        # computes the exact result — content-faithful for the FULL Unicode semantics
        # (`"ß".upper()=="SS"`, `"HELLO".lower()=="hello"`), no abstract op, no soundness
        # risk. This is the honest way to give lower/upper/replace real content on the
        # literal case (the general symbolic case keeps the sound laws below).
        arg_irs = expr.get("args") or []
        def _lit(ir):
            return (ir.get("value") if isinstance(ir, dict) and ir.get("type") == "String"
                    else None)
        recv_lit = _lit(recv_ir) if isinstance(recv_ir, dict) else None
        if recv_lit is not None:
            if tail == "lower" and len(args) == 0:
                return self._whyml_string_literal(recv_lit.lower())
            if tail == "upper" and len(args) == 0:
                return self._whyml_string_literal(recv_lit.upper())
            if tail == "replace" and len(args) == 2:
                p_lit, r_lit = _lit(arg_irs[0]) if len(arg_irs) > 0 else None, \
                               _lit(arg_irs[1]) if len(arg_irs) > 1 else None
                if p_lit is not None and r_lit is not None:
                    return self._whyml_string_literal(recv_lit.replace(p_lit, r_lit))
        recv = self._expr_to_whyml(recv_ir, local_refs or set(), invariant_ctx, subst)
        # self-tcb-reduction WRITER class (`_build_param_list`): a pyval subscript receiver
        # (`func["self_type"]`) lowers to its hval; project the string carrier via `hstr_of`
        # before the faithful string op (`str_lower_op`). Gated -> byte-inert elsewhere.
        if (self._emitting_build_param_list()
                and isinstance(recv_ir, dict) and self._expr_is_pyval(recv_ir)):
            recv = f"(hstr_of {recv})"
        if tail == "replace" and len(args) == 2:
            # §3.1 + cleared-string RESIDUALS item 2: `val function` (DETERMINISTIC) with
            # the SOUND laws for CPython all-occurrences replace:
            #  (a) char-for-char (len pat = len rep) preserves length; general grow/shrink
            #      is length-free (never claim length preservation there);
            #  (b) NOT-CONTAINS identity: if `pat` occurs NOWHERE in `s`, result = s. Stated
            #      as the negation of the substring-existential the `in`/`not in` operator
            #      emits, so a driver `requires pat not in s` connects. Empty pat is
            #      auto-excluded (it "occurs" at every index) — matching CPython, whose
            #      empty-pat replace DIFFERS from Why3 `replaceall` (so we do NOT pin to it).
            # NB `old`/`new` are Why3 reserved keywords → params named `pat`/`rep`.
            self._add_abstract_op(
                "val function str_replace_op (s pat rep: string) : string\n"
                "    ensures { String.length pat = String.length rep"
                " -> String.length result = String.length s }\n"
                "    ensures { (forall _ri:int. 0 <= _ri ->"
                " _ri + String.length pat <= String.length s ->\n"
                "                 String.substring s _ri (String.length pat) <> pat)\n"
                "              -> result = s }")
            return f"(str_replace_op {recv} {args[0]} {args[1]})"
        if tail in ("lower", "upper") and len(args) == 0:
            # §3.2 + cleared-string RESIDUALS item 1: `val function` (DETERMINISTIC) so equal
            # receivers give equal results and `s.lower().lower() == s.lower()` proves.
            # Case folding is NOT length-preserving in Unicode ("ß".upper()=="SS"), so only
            # the non-emptiness lower bound is sound as a length law. IDEMPOTENCE (universal,
            # true of Python for ALL strings incl. Unicode) is encoded via a fresh
            # "already-folded" marker predicate (NO `axiom` keyword, NO self-reference): the
            # output is folded, and a folded input is a fixed point ⇒ f(f s)=f(s). Distinct
            # symbols for lower/upper ⇒ `s.lower()==s.upper()` stays UNKNOWN (no false
            # collapse). Full Unicode/ASCII per-char case-MAP on a SYMBOLIC string stays the
            # honest residual (only the literal case is content-mapped, by folding above).
            op = "str_lower_op" if tail == "lower" else "str_upper_op"
            marker = "str_is_lowerf" if tail == "lower" else "str_is_upperf"
            self._add_abstract_op(
                f"predicate {marker} string\n"
                f"  val function {op} (s: string) : string\n"
                "    ensures { String.length s >= 1 -> String.length result >= 1 }\n"
                f"    ensures {{ {marker} result }}\n"
                f"    ensures {{ {marker} s -> result = s }}")
            return f"({op} {recv})"
        if tail in ("strip", "lstrip", "rstrip") and len(args) <= 1:
            # §3.3: stripping only removes chars → result no longer than the input.
            self._add_abstract_op(
                "val str_strip_op (s: string) : string\n"
                "    ensures { String.length result <= String.length s }")
            return f"(str_strip_op {recv})"
        return None

    def _record_get_field(self, expr: Dict[str, Any]):
        """G1/G2 recognizer core (09-2223 pure-classifier increment): resolve a
        `<record-var>.get("<key>"[, default])` Call whose RECEIVER is a record-typed
        param/local (a `@dataclass`/`TypedDict` monomorphized to a native WhyML record)
        and whose literal KEY names a declared field of that record.

        Returns `(recv_name, field_label, field_type_tag)` — the receiver var name, the
        WhyML field label (`_field_label`, so `pure`→`py_pure`), and the field's IR type
        tag (`"str"`/`"bool"`/`"int"`/…) — or None if any gate fails. The record-typed-
        receiver gate is the whole point: it fires ONLY when `recv` is in
        `_current_record_var_classes` (records only, NEVER a plain `Dict[str,Any]`), so
        a generic dict `.get` keeps the legacy opaque `<recv>_get_N` op (corpus-inert).

        This is the FAITHFUL, NON-VACUOUS lowering: the record field IS read
        (`func.py_pure`), not dropped into an opaque `func_get_1 <hash>`."""
        if not isinstance(expr, dict):
            return None
        func_name = expr.get("func")
        if not (isinstance(func_name, str) and func_name.endswith(".get")):
            return None
        recv = func_name[:-len(".get")]
        # bare receiver only (`func.get`, not `self.foo.get` — the latter is the §12
        # self-field-dict path); a dotted receiver is never a record-typed VAR here.
        if not recv or "." in recv:
            return None
        args_ir = expr.get("args") or []
        if not args_ir:
            return None
        k0 = args_ir[0]
        if not (isinstance(k0, dict) and k0.get("type") == "String"):
            return None
        key = k0.get("value")
        # `_current_record_var_classes` (record locals + params) is the primary map;
        # fall back to `_record_param_classes` (populated at signature emission) so the
        # PRE-body string-local classification pass — which runs before the per-body
        # `_current_record_var_classes` is rebuilt — still resolves a record PARAM.
        cls = (getattr(self, "_current_record_var_classes", {}).get(recv)
               or getattr(self, "_record_param_classes", {}).get(recv))
        if not cls:
            return None
        rts = getattr(self, "_record_types", {})
        # `cls` is the record's WhyML name (`_current_record_var_classes` /
        # `_record_param_classes` store whyml_name), which may be a reserved-word-
        # mangled label (`Rec`→`py_rec`), so match on `whyml_name` first — a plain
        # `k.lower()` compare misses the `py_`-prefixed cases.
        rt = (rts.get(cls) or rts.get(str(cls).lower())
              or next((v for k, v in rts.items()
                       if v.get("whyml_name") == cls
                       or k.lower() == str(cls).lower()), None))
        if not rt:
            return None
        ftypes = rt.get("field_types", {})
        if key not in ftypes:
            return None
        label = self._field_label(rt.get("whyml_name", str(cls).lower()), key)
        return (recv, label, ftypes[key])

    def _option_record_get_field(self, expr: Dict[str, Any]):
        """option-of-record projection (boundary-1 G1 extension): resolve a
        `<optvar>.get("<key>"[, default])` Call whose RECEIVER is an
        `Optional[<record>]` param (registered in `_option_record_param_classes`
        by `_symtype_to_whyml`) and whose literal KEY names a declared field of
        that record.

        Returns `(recv, label, field_type_tag, none_default)` — the receiver var
        name, the WhyML field label, the field's IR type tag, and the WhyML term
        for the `None ->` match arm (the `.get`'s 2nd-arg default if a literal,
        else the field-type default). The caller emits
        `(match recv with Some _r -> _r.<label> | None -> <none_default> end)`:
        the field IS read from the `Some` arm (NON-VACUOUS), and — after the
        `if recv is None: return …` guard — the `None` arm is dead but present
        (total match). Gated on `_option_record_param_classes`, so it fires ONLY
        for an `Optional[<record>]` receiver → corpus-byte-inert."""
        if not isinstance(expr, dict):
            return None
        func_name = expr.get("func")
        if not (isinstance(func_name, str) and func_name.endswith(".get")):
            return None
        recv = func_name[:-len(".get")]
        if not recv or "." in recv:
            return None
        wn = getattr(self, "_option_record_param_classes", {}).get(recv)
        if not wn:
            return None
        args_ir = expr.get("args") or []
        if not args_ir:
            return None
        k0 = args_ir[0]
        if not (isinstance(k0, dict) and k0.get("type") == "String"):
            return None
        key = k0.get("value")
        rts = getattr(self, "_record_types", {})
        rt = next((v for v in rts.values() if v.get("whyml_name") == wn), None)
        if not rt:
            return None
        ftypes = rt.get("field_types", {})
        if key not in ftypes:
            return None
        label = self._field_label(wn, key)
        ftype = ftypes[key]
        # `None ->` arm default: the `.get`'s 2nd arg if it is a literal of the
        # matching kind, else the field-type zero. This arm is dead (the body
        # guards `if recv is None: return …`), so any well-typed default is sound;
        # the string default `""` / int `0` keep the match total and typed.
        none_default = '""' if ftype == "str" else "0"
        if len(args_ir) >= 2 and isinstance(args_ir[1], dict):
            d = args_ir[1]
            if ftype == "str" and d.get("type") == "String":
                none_default = f'"{d.get("value", "")}"'
            elif ftype in ("int", "bool") and d.get("type") in ("Number", "Bool"):
                _dv = d.get("value")
                none_default = str(int(_dv)) if isinstance(_dv, (int, float, bool)) else "0"
        return (recv, label, ftype, none_default)

    def _self_field_dict_nu(self, recv: str):
        """self-field-dict-reflection (typed-ir-for-b-ceiling.md §12): when `recv` is a
        `self.<field>` (or `<recordvar>.<field>`) naming a `dict`/`set`/`frozenset`
        record field, return the field's WhyML VALUE type ("string" for `dict[str, str]`,
        else "int"); None otherwise. Lets `self.<dict-field>.get(k)` read the real map."""
        if "." not in recv:
            return None
        obj, field = recv.rsplit(".", 1)
        rt_name = (self._current_self_type if obj == "self"
                   else getattr(self, "_current_record_var_classes", {}).get(obj))
        if not rt_name:
            return None
        rts = getattr(self, "_record_types", {})
        rt = (rts.get(rt_name) or rts.get(str(rt_name).lower())
              or next((v for k, v in rts.items() if k.lower() == str(rt_name).lower()), None))
        if not rt:
            return None
        ft = rt.get("field_types", {}).get(field)
        if ft not in ("dict", "set", "frozenset"):
            return None
        return rt.get("field_value_types", {}).get(field, "int")

    def _self_field_dict_kappa(self, recv: str):
        """cleared-hash S4: the KEY type κ of a record dict/set FIELD named by `recv`
        (a `self.<field>`/`<recordvar>.<field>`): "string" for a `dict[str, ν]` /
        `set[str]` / `frozenset[str]` field (`map string (option ν)`, native injective
        key), else "int" (`map int`, the legacy str_hash_op fallback); None when `recv`
        is not a dict/set/frozenset record field. The κ counterpart of the ν-returning
        `_self_field_dict_nu` — read and written raw everywhere so the field map's key
        stays type-consistent (a mismatch is a WhyML type error)."""
        if "." not in recv:
            return None
        obj, field = recv.rsplit(".", 1)
        rt_name = (self._current_self_type if obj == "self"
                   else getattr(self, "_current_record_var_classes", {}).get(obj))
        if not rt_name:
            return None
        rts = getattr(self, "_record_types", {})
        rt = (rts.get(rt_name) or rts.get(str(rt_name).lower())
              or next((v for k, v in rts.items() if k.lower() == str(rt_name).lower()), None))
        if not rt:
            return None
        ft = rt.get("field_types", {}).get(field)
        if ft not in ("dict", "set", "frozenset"):
            return None
        return rt.get("field_key_types", {}).get(field, "int")

    def _set_union_left_is_strfield(self, ir):
        """r1-setop I2 (self-tcb-reduction): True iff the LEFT set operand of a
        `<set> | {x}` UNION is a κ=string dict/set FIELD (`self.<f>`/`<rec>.<f>`), which
        lowers to a `map string (option int)` (field_key_types) — so the union must write
        the RAW native string element (no `str_hash_op`), matching the field's
        `.add`/membership/`.get` (a mismatch is a WhyML type error: `str_hash_op x : int`
        cannot index a `map string`). A bare Var operand (a @mutable_state method's set
        param/local, `map int`) returns False → keeps `str_hash_op` (byte-identical for
        the mirror's `local_refs | {target}` / `declared_refs.copy() | {target}`). Only a
        FIELD is genuinely `map string` under the current gating (a method set PARAM stays
        `map int` — the by-ref κ=string case is not @mutable_state-reachable; a `.copy()`
        of a string FIELD is blocked upstream on `.copy()` field-read modeling, so it is
        not recognized here — no working consumer)."""
        if not isinstance(ir, dict):
            return False
        if ir.get("type") in ("Attribute", "FieldGet"):
            _o = ir.get("object")
            _f = ir.get("field") or ir.get("attr")
            if isinstance(_o, str) and isinstance(_f, str):
                return self._self_field_dict_kappa(f"{_o}.{_f}") == "string"
        return False

    # stmt-list-append-mutation wall (C-bucket): the `{"stmt": K, …}` statement-node
    # kinds this lowers to `stmt_ir` constructors, and the payload field each reads
    # (as `(field, child-kind)`). A nullary node (Pass/Break/Continue) has no payload;
    # SExpr carries one MANDATORY emit_ir expr child (`"expr"`); SReturn carries the
    # OPTIONAL return value (`"opt"` → `iropt_ir`), faithful to `ast.Return.value` being
    # `option emit_ir` (the `disp(stmt.value) if stmt.value else None` ternary).
    # TAG-PRESERVING — never erased to `0` (fable Oracle 3).
    _STMT_IR_CTORS = {
        "Pass":     ("SPass", []),
        "Break":    ("SBreak", []),
        "Continue": ("SContinue", []),
        "Return":   ("SReturn", [("value", "opt")]),
        "Expr":     ("SExpr", [("value", "expr")]),
        # SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): the
        # assignment `{"stmt":"Assign","target":stmt.target.id,"value":self.
        # _py_expr_to_ir(stmt.value)}` (the `_py_stmt_annassign` append). `target` is a
        # bare STRING leaf — `stmt.target.id` projects via `name_of` (the "str" child kind
        # = the default `_expr_to_whyml` lowering). `value` is the RHS emit_ir; in
        # AnnAssign it is `self._py_expr_to_ir(<OptExprIR field>)` — the append is GUARDED
        # by `stmt.value is not None`, so the option is Some and the "opt_unwrap" child kind
        # unwraps it (`match <optfield> with Some _v -> disp _v | None -> IrOther ""`).
        "Assign":   ("SAssign", [("target", "str"), ("value", "opt_unwrap")]),
        # SAssert increment (self-tcb-reduction M5, C-bucket): the `assert test, msg`
        # statement (the `_py_stmt_assert` build-up-then-append, folded to a single
        # literal by `_recognize_stmt_append_builder`). `test` is the mandatory emit_ir
        # ("expr" child). `msg` is the OPTIONAL message string: the raw `stmt.msg`
        # (`option emit_ir`) field, lowered by the "assert_msg" child kind to `iropt_str`
        # — `IrSSome (value_of _m)` iff the msg is a Some string-literal Constant
        # (`is_str _m`), else `IrSNone`, faithful to the compound guard `stmt.msg and
        # isinstance(stmt.msg, Constant) and isinstance(stmt.msg.value, str)`.
        "Assert":   ("SAssert", [("test", "expr"), ("msg", "assert_msg")]),
        # SAugAssign/SFieldAugAssign/SArraySet increment (self-tcb-reduction M5,
        # C-bucket): the augmented-assignment statement nodes (the `_py_stmt_augassign`
        # three-branch dispatch). AugAssign carries the TARGET NAME (`stmt.target.id` ->
        # `name_of`, "str" child = the default `_expr_to_whyml`), the OP string
        # (`self._py_op_to_str(stmt.op)` -> the trusted `(py_op_to_str stmt.op)` call, "str"
        # child), and the RHS emit_ir (`self._py_expr_to_ir(stmt.value)`, "expr" child).
        # FieldAugAssign is the sibling for `self.f op= v`: `field` = `stmt.target.attr`
        # (-> `name_of`, "str" child), then op + value; the constant `object:"self"` key is
        # NOT in the payload (dropped — the `stmt.target.value.id == 'self'` guard pins it).
        # ArraySet is the desugaring of `c[k] op= v` to a subscript store of `(c[k]) op v`:
        # `array` (`self._py_expr_to_ir(stmt.target.value)`), `index` (the `slice_ir` local),
        # and `value` (the inline `{"type":"BinOp",...}` reusing `_IRNODE_CTORS["BinOp"]` ->
        # IrBinOp) — all "expr" children.
        "AugAssign":      ("SAugAssign", [("target", "str"), ("op", "str"),
                                          ("value", "expr")]),
        "FieldAugAssign": ("SFieldAugAssign", [("field", "str"), ("op", "str"),
                                               ("value", "expr")]),
        "ArraySet":       ("SArraySet", [("array", "expr"), ("index", "expr"),
                                         ("value", "expr")]),
        # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): the compound
        # statements carry their nested statement body/orelse LISTS. The `"expr"`
        # child (test/iter) lowers to a bare emit_ir; the `"stmtlist"` child
        # (body/orelse) is the `self._py_stmts_to_ir(node.body)` sub-list — a
        # `seq stmt_ir` (the trusted dispatcher's return) materialized to the pure
        # `stmt_list` an SWhile/SIf/SFor ctor carries via `(seq_to_sl <seq>)`.
        # NON-facade: `seq_to_sl` of a real (dispatcher-produced) seq, never a
        # literal SLNil. `_process_for`'s While-shaped body drops target/line/
        # invariants/variants (SFor carries iter + body only), the SWhile/SIf
        # precedent of keeping just the emitter-model-relevant children.
        "While":    ("SWhile", [("test", "expr"), ("body", "stmtlist")]),
        "If":       ("SIf", [("test", "expr"), ("body", "stmtlist"),
                             ("orelse", "stmtlist")]),
        "For":      ("SFor", [("iter", "expr"), ("body", "stmtlist")]),
    }

    def _is_stmt_ir_expr(self, ir: Any) -> bool:
        """stmt-list-append-mutation wall (C-bucket): True iff `ir` is a stmt_ir-VALUED
        expression — a subscript `p[i]` of a `ref (seq stmt_ir)` param (the element read
        `Seq.get !p i : stmt_ir`). The load-bearing read-back shape for the non-vacuity
        gate; corpus-inert (no corpus program has a stmt-seq-mut param)."""
        if not isinstance(ir, dict):
            return False
        if ir.get("type") == "Subscript":
            v = ir.get("value")
            return (isinstance(v, dict) and v.get("type") == "Var"
                    and v.get("name") in getattr(self, "_stmt_seq_mut_params", set()))
        return False

    def _stmt_ir_kind_reflection(self, expr: Dict[str, Any], local_refs: Set[str],
                                 invariant_ctx: bool,
                                 subst: Optional[Dict[str, str]]) -> Optional[str]:
        """stmt-list-append-mutation wall (C-bucket): lower `<stmt_ir>.get("stmt")` to
        `(stmt_kind_of <base>)` — the statement node's tag, the honest read-back the
        pre-feature integer-`0` erasure (fable Oracle 3) made impossible. Fires only when
        the receiver is a subscript of a stmt-seq-mut param → corpus-inert."""
        fn = expr.get("func", "")
        if fn != "get":
            return None
        args = expr.get("args") or []
        if not (args and isinstance(args[0], dict) and args[0].get("type") == "String"
                and args[0].get("value") == "stmt"):
            return None
        recv = expr.get("receiver")
        if not self._is_stmt_ir_expr(recv):
            return None
        base = self._expr_to_whyml(recv, local_refs, invariant_ctx, subst)
        return f"(stmt_kind_of {base})"

    def _lower_stmt_ir_node(self, node: Dict[str, Any], local_refs: Set[str],
                            invariant_ctx: bool = False,
                            subst: Optional[Dict[str, str]] = None) -> str:
        """stmt-list-append-mutation wall (C-bucket): lower a statement-node dict literal
        `{"stmt": "Pass"}` / `{"stmt": "Return", "value": <ternary>}` to its `stmt_ir`
        constructor (`SPass` / `(SReturn <iropt_ir>)` / `(SExpr <emit_ir>)`). The tag is
        PRESERVED by the constructor choice — the honest node identity the pre-feature
        `_coerce_to_int` erased to `0`. A `"opt"` child (SReturn's optional `value`) is
        lowered through `_slice_bound_to_iropt_ir` — the shared `disp(x) if x else None`
        ternary recognizer — to a real `iropt_ir` (`IrOSome`/`IrONone`); an `"expr"` child
        (SExpr's mandatory `value`) through `_expr_to_whyml` to a bare `emit_ir`. Only
        reached for a `{"stmt":K}` append to a stmt-seq-mut param, so it is corpus-inert by
        construction."""
        fields: Dict[str, Any] = {}
        for k, v in zip(node.get("keys", []) or [], node.get("values", []) or []):
            if isinstance(k, dict) and k.get("type") == "String":
                fields[k.get("value")] = v
        skind_ir = fields.get("stmt")
        skind = skind_ir.get("value") if isinstance(skind_ir, dict) else None
        ctor = self._STMT_IR_CTORS.get(skind)
        if ctor is None:
            # Fail CLOSED, loudly: an unmodelled statement kind must surface as a Why3
            # typecheck error, never be silently mislabelled to a wrong tag.
            return f'(SUnmodelledStmt_{skind})'
        cname, payload = ctor
        if not payload:
            return cname
        args = []
        for f, child_kind in payload:
            if f not in fields:
                return f'(SMissingChild_{skind}_{f})'
            if child_kind == "opt":
                args.append(self._slice_bound_to_iropt_ir(
                    fields[f], local_refs, invariant_ctx, subst))
            elif child_kind == "opt_unwrap":
                # SAssign + str-Constant recognizer (C-bucket): the RHS
                # `self._py_expr_to_ir(stmt.value)` where `stmt.value : option emit_ir`
                # (AnnAssign's OptExprIR field). The append is GUARDED by `stmt.value is
                # not None`, so the option is Some; unwrap it under a match and apply the
                # dispatcher — `(match <optfield> with Some _v -> disp _v | None -> IrOther
                # "")` — yielding the bare `emit_ir` the SAssign value child expects (NOT
                # the iropt_ir of SReturn). NON-facade: the option field is read from the
                # record and the Some arm applies the real dispatcher `_py_expr_to_ir`.
                args.append(self._opt_field_disp_unwrap(
                    fields[f], local_refs, invariant_ctx, subst))
            elif child_kind == "assert_msg":
                # SAssert increment (C-bucket): the OPTIONAL assert message. `fields[f]`
                # is the raw `stmt.msg` field read (`option emit_ir`). The `_py_stmt_assert`
                # guard `stmt.msg and isinstance(stmt.msg, Constant) and isinstance(stmt.msg
                # .value, str)` means "msg is a Some string-literal Constant"; a string
                # Constant lowers to exactly `IrStr`, so the compound guard collapses to
                # `is-Some && is_str (unwrapped)`, and `stmt.msg.value` (the string payload)
                # projects via `value_of` (`IrStr v -> v`). Lower to `iropt_str`:
                #   match <msg> with Some _m -> (if is_str _m then IrSSome (value_of _m)
                #                                 else IrSNone) | None -> IrSNone
                # NON-facade: the option field is read from the record, the Some arm applies
                # the real `is_str` discriminant + `value_of` projector; absent/non-string
                # msg is faithfully `IrSNone` (the guard's else — no append of a msg).
                msg_w = self._expr_to_whyml(
                    fields[f], local_refs, invariant_ctx, subst)
                args.append(
                    f"(match {msg_w} with Some _m -> "
                    f"(if is_str _m then IrSSome (value_of _m) else IrSNone) "
                    f"| None -> IrSNone end)")
            elif child_kind == "stmtlist":
                # SUB-BODY recursion (C-bucket): the sub-statement list
                # `self._py_stmts_to_ir(node.body)` is a `seq stmt_ir` (the trusted
                # dispatcher's return); materialize it to the pure `stmt_list` the
                # ctor carries via `(seq_to_sl <seq>)`. NON-facade: a real
                # materialization of the dispatcher's output, never a literal SLNil.
                inner = self._expr_to_whyml(
                    fields[f], local_refs, invariant_ctx, subst)
                args.append(f"(seq_to_sl {inner})")
            else:
                args.append(self._expr_to_whyml(
                    fields[f], local_refs, invariant_ctx, subst))
        return f"({cname} {' '.join(args)})"

    # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): the COMPOUND
    # statement kinds whose `_process_*` handler RETURNS a `{"stmt": K, ...}`
    # dict — routed through `_lower_stmt_ir_node` to their SWhile/SIf/SFor ctor.
    # The nullary/return/expr kinds are NOT here (they lower at the `.append`
    # site, never as a standalone construction), so a plain `{"stmt":"Pass"}`
    # elsewhere is untouched.
    _STMT_IR_COMPOUND_KINDS = frozenset({"While", "If", "For"})

    def _lower_stmt_ir_construction(self, expr: Dict[str, Any], local_refs: Set[str],
                                    invariant_ctx: bool,
                                    subst: Optional[Dict[str, str]]) -> Optional[str]:
        """SUB-BODY recursion (C-bucket): lower a COMPOUND statement-node dict
        construction `{"stmt": "While"/"If"/"For", ...}` (a `_process_*` return
        dict) to its `stmt_ir` constructor via `_lower_stmt_ir_node`. Returns None
        (→ the caller's next dict handler) for any other dict. Gated on
        @mutable_state (the emitter model) so it is corpus-inert."""
        if (getattr(self, "_current_self_type", None)
                not in getattr(self, "_mutable_state_classes", set())):
            return None
        skind = None
        for k, v in zip(expr.get("keys", []) or [], expr.get("values", []) or []):
            if (isinstance(k, dict) and k.get("type") == "String"
                    and k.get("value") == "stmt"
                    and isinstance(v, dict) and v.get("type") == "String"):
                skind = v.get("value")
                break
        if skind not in self._STMT_IR_COMPOUND_KINDS:
            return None
        return self._lower_stmt_ir_node(expr, local_refs, invariant_ctx, subst)

    def _lower_irnode_construction(self, expr: Dict[str, Any], local_refs: Set[str],
                                   invariant_ctx: bool,
                                   subst: Optional[Dict[str, str]]) -> Optional[str]:
        """typed-ir-for-b-ceiling.md B-C1: lower an inline IR-node dict literal
        `{"type": "Var", "name": e}` to the typed `exprir` constructor `(EVar <e>)`.
        A `"type"` key with a STRING-literal value names the kind; the remaining keys
        supply the constructor payload. A kind we don't model, or a construction
        missing a payload field, becomes `(EOther "<kind>")` — sound: reflection then
        yields the tag and `""`, never a false value. Gated on @mutable_state (the
        emitter model); returns None (→ the caller's map fallback) otherwise."""
        if getattr(self, "_current_self_type", None) not in getattr(
                self, "_mutable_state_classes", set()):
            return None
        keys = expr.get("keys", [])
        values = expr.get("values", [])
        if not keys or len(keys) != len(values):
            return None
        fields: Dict[str, Any] = {}
        for k, v in zip(keys, values):
            if not (isinstance(k, dict) and k.get("type") == "String"):
                return None
            fields[k.get("value")] = v
        kind_ir = fields.get("type")
        if not (isinstance(kind_ir, dict) and kind_ir.get("type") == "String"):
            return None
        kind = kind_ir.get("value")
        # optional-field builder (monomorphic-option ADTs): a quantifier
        # construction (`_csl_forall`/`_csl_exists`, merged by
        # `_recognize_optfield_builder`) lowers to `(IrForall var body <iropt_str>
        # <iropt_ir>)`, reading node's `option` binder fields and converting them
        # to the monomorphic option ADTs at the ctor arg. Handled BEFORE the
        # generic fixed-payload `_IRNODE_CTORS` path.
        if kind in getattr(self, "_QUANTIFIER_OPT_CTORS", {}):
            return self._lower_quant_optfield(kind, fields, local_refs,
                                              invariant_ctx, subst)
        # optional-field ext (monomorphic-option ADTs): the `_py_expr_slice`
        # construction (rewritten to the internal "SliceN" tag by functions.py
        # `_recognize_slice_builder`) lowers to `(IrSliceN <opt> <opt> <opt>)`,
        # each bound the ternary `disp(expr.X) if expr.X else None` converted to
        # the monomorphic `iropt_ir`. Handled BEFORE the generic `_IRNODE_CTORS`
        # path (whose "Slice" tag is the DISTINCT spec-side IrSlice).
        if kind == "SliceN":
            return self._lower_sliceN_optfield(fields, local_refs,
                                               invariant_ctx, subst)
        # optional-field ext (monomorphic-option ADTs): the TYPE-LESS
        # `_csl_function_variant` construction (rewritten to the internal
        # "FunctionVariant" tag by functions.py `_recognize_functionvariant_
        # builder`) lowers to `(IrFunctionVariant <expr> <iropt_str>)`.
        if kind == "FunctionVariant":
            return self._lower_functionvariant_optfield(fields, local_refs,
                                                        invariant_ctx, subst)
        # cleanup batch (no-more-int doctrine): a "Number" node whose `value` payload is
        # a float-typed field read (`_csl_number`'s `node.value`, `CSLNumber.value:
        # float` → the WhyML `real` field) lowers to the NEW `IrNumF real` leaf, NOT the
        # int `IrNum`. `_field_type_of` returns the "float" IR tag for such a field (the
        # record slot is a `real` in WhyML). An int-literal `value` (`_py_expr_name`'s
        # `{"type":"Number","value":0}`) is not a float field read → falls through to the
        # generic `IrNum int` path below. So the split is decided faithfully by the
        # payload's type, never dropped.
        if kind == "Number":
            _vfld = fields.get("value")
            if isinstance(_vfld, dict) and (
                    self._field_type_of(_vfld) in ("float", "real")
                    or self._is_float_expr(_vfld)):
                _vw = self._expr_to_whyml(_vfld, local_refs, invariant_ctx, subst)
                return f"(IrNumF {_vw})"
        ctor = self._IRNODE_CTORS.get(kind)
        if ctor is None:
            return f'(IrOther "{kind}")'
        cname, payload = ctor
        args = []
        for f in payload:
            if f not in fields:
                return f'(IrOther "{kind}")'
            _pv = self._project_pyconst_val_ctor_arg(
                fields[f], kind, f, local_refs, invariant_ctx, subst)
            if _pv is not None:
                args.append(_pv)
            else:
                args.append(self._expr_to_whyml(fields[f], local_refs, invariant_ctx, subst))
        return f"({cname} {' '.join(args)})"

    def _project_pyconst_val_ctor_arg(self, arg_ir: Any, kind: str, field: str,
                                      local_refs: Set[str], invariant_ctx: bool,
                                      subst: Optional[Dict[str, str]]) -> Optional[str]:
        """pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): a
        `_py_expr_constant`-style `{"type": "String"/"Number"/"Bool", "value": expr.value}`
        construction reads the `pyconst_val`-typed `.value` field in a VALUE position, but
        the target leaf constructor expects a scalar (`IrStr string` / `IrNum int` /
        `IrBoolC int`). Project the field read through the matching total accessor so the
        ctor arg is well-typed and value-faithful:

            String -> IrStr  (pvstr_of expr.value)                : string
            Number -> IrNum  (pvint_of expr.value)                : int
            Bool   -> IrBoolC (if pvbool_of expr.value then 1 else 0) : int (bool-as-int,
                     the pre-existing IrBoolC convention shared with `_csl_bool`)

        Returns the projected WhyML string, or None when the arg is not a pyconst_val
        `.value` read (the caller then lowers it generically). Corpus-inert: only fires on a
        pyconst_val field read, which the corpus never produces."""
        _is_pv_local = (isinstance(arg_ir, dict) and arg_ir.get("type") == "Var"
                        and arg_ir.get("name")
                        in getattr(self, "_pyconst_val_local_vars", set()))
        if field != "value" or (
                self._pyconst_val_field_read(arg_ir) is None and not _is_pv_local):
            return None
        # V1 pyconst-dispatch: the `value` arg is a pyconst_val record-field read OR a
        # pyconst_val LOCAL (`v`) — project it through the matching total accessor so the
        # `IrStr string`/`IrNum int`/`IrBoolC int` ctor arg is well-typed and value-faithful.
        _pvs = self._expr_to_whyml(arg_ir, local_refs, invariant_ctx, subst)
        _proj = {"String": "pvstr_of", "Number": "pvint_of"}.get(kind)
        if _proj is not None:
            return f"({_proj} {_pvs})"
        if kind == "Bool":
            return f"(if pvbool_of {_pvs} then 1 else 0)"
        return None

    def _inline_pyconst_dict_index(self, arg_ir: Any,
                                   elt_lower: Optional[Any]) -> Optional[str]:
        """INLINE CONST-DICT INDEX -> `pyconst_val` (relaunch #13, `closed_pattern`).

        `closed_pattern` builds its `MatchSingleton` value as

            _N("MatchSingleton")(value={"None": None, "True": True,
                                        "False": False}[s])

        — a dict LITERAL written at the use site and indexed by a local. The existing
        const-dict lowering (`_expr_to_whyml`'s `ClassByNameCall` arm) only handles a
        MODULE-LEVEL table, so this construction declined to the `matchSingleton_0 ()`
        facade and took the whole method with it. The table is a compile-time constant
        either way: an inline literal is if anything MORE static than a module global,
        because no other statement can rebind it.

        Lowered exactly like the module-level form — a chained `str_eq_op` ITE over the
        literal key set with the key `let`-bound so it is evaluated ONCE (the key
        expression may have an effect; `_CMP[self.advance().string]` is the precedent) —
        but producing `pyconst_val` arms instead of class-name strings.

        THE FALL-THROUGH is the same argument the module-level form records, and here it
        is even tighter. Python raises `KeyError` off the key set, and the model must not
        invent a value there; the emitted default is `PVNone`. At this site the miss is
        UNREACHABLE: the source guards the whole branch with `s in ("None", "True",
        "False")`, which lowers to the `str_eq_op` disjunction over *literally the same*
        three keys — the tuple and the dict share their key set character for character.

        FAIL-CLOSED on every axis: the arg must be a `Subscript` of a `DictLit`, every key
        a STRING literal, every value a `None` / `Bool` / `String` literal (the three
        shapes `pyconst_val` can carry without a model), and the dict non-empty. Anything
        else returns None and the caller declines the construction as before. Nothing in
        the corpus or any other mirror indexes an inline dict into a `pyconst_val` slot,
        so this is byte-inert outside `closed_pattern`."""
        if not (isinstance(arg_ir, dict) and arg_ir.get("type") == "Subscript"):
            return None
        _d = arg_ir.get("value")
        if not (isinstance(_d, dict) and _d.get("type") == "DictLit"):
            return None
        _ks, _vs = _d.get("keys") or [], _d.get("values") or []
        if not _ks or len(_ks) != len(_vs):
            return None
        _entries = []
        for _k, _v in zip(_ks, _vs):
            if not (isinstance(_k, dict) and _k.get("type") == "String"
                    and isinstance(_k.get("value"), str)):
                return None
            if not isinstance(_v, dict):
                return None
            _vt = _v.get("type")
            if _vt == "None":
                _entries.append((_k["value"], "PVNone"))
            elif _vt == "Bool":
                _entries.append((_k["value"],
                                 "(PVBool true)" if _v.get("value") else "(PVBool false)"))
            elif _vt == "String" and isinstance(_v.get("value"), str):
                _entries.append((_k["value"],
                                 f"(PVStr {whyml_string_literal(_v['value'])})"))
            else:
                return None
        _idx = arg_ir.get("index")
        if _idx is None:
            _idx = arg_ir.get("slice")
        if not isinstance(_idx, dict):
            return None
        self._add_abstract_op(
            "val str_eq_op (a: string) (b: string) : bool\n"
            "    ensures { result <-> (a = b) }")
        if elt_lower is None:
            return None
        _kx = elt_lower(_idx)
        _ch = "PVNone"
        for _kk, _vv in reversed(_entries):
            _ch = (f"(if (str_eq_op _pvk {whyml_string_literal(_kk)}) "
                   f"then {_vv} else {_ch})")
        return f"(let _pvk = {_kx} in {_ch})"

    def _lower_quant_optfield(self, kind: str, fields: Dict[str, Any],
                              local_refs: Set[str], invariant_ctx: bool,
                              subst: Optional[Dict[str, str]]) -> str:
        """optional-field builder (monomorphic-option ADTs): lower a merged
        `_csl_forall`/`_csl_exists` construction dict to
        `(IrForall var body <iropt_str> <iropt_ir>)`. The two OPTIONAL binder
        fields are read from node's `option`-typed record fields and CONVERTED to
        the monomorphic option ADTs at the ctor arg:

            binder_type (option string)  -> match .. with Some s -> IrSSome s
                                                        | None   -> IrSNone
            domain      (option emit_ir) -> match .. with Some d -> IrOSome (disp d)
                                                        | None   -> IrONone

        where `disp` is the recursive IR dispatcher `_csl_to_ir` applied to the
        unwrapped sub-node (the faithful `self._csl_to_ir(node.domain)`). An
        absent optional field (no conditional-add for it) defaults to the None
        ctor. NON-FACADE: every field is read from `node`; no dropped optional,
        no opaque val. A malformed domain value (not a dispatcher Call) fails
        closed to `IrOther`."""
        cname = self._QUANTIFIER_OPT_CTORS[kind]
        if "var" not in fields or "body" not in fields:
            return f'(IrOther "{kind}")'
        var_w = self._expr_to_whyml(fields["var"], local_refs, invariant_ctx, subst)
        body_w = self._expr_to_whyml(fields["body"], local_refs, invariant_ctx, subst)
        # binder_type -> iropt_str (raw `option string` field, no dispatcher)
        if "binder_type" in fields:
            bt_w = self._expr_to_whyml(fields["binder_type"], local_refs,
                                       invariant_ctx, subst)
            opt_str = (f"(match {bt_w} with Some _qs -> IrSSome _qs "
                       f"| None -> IrSNone end)")
        else:
            opt_str = "IrSNone"
        # domain -> iropt_ir (`option emit_ir` field; dispatcher applied inside Some)
        if "domain" in fields:
            dv = fields["domain"]
            if not (isinstance(dv, dict) and dv.get("type") == "Call"
                    and (dv.get("args") or [])):
                return f'(IrOther "{kind}")'
            arg_w = self._expr_to_whyml(dv["args"][0], local_refs,
                                        invariant_ctx, subst)
            # `_qd` is the match-bound sub-node (a plain immutable `emit_ir`), NOT
            # a ref-local — keep it OUT of local_refs so it lowers to bare `_qd`
            # (no `!` deref) as the dispatcher argument.
            disp_call = {"type": "Call", "func": dv.get("func"),
                         "args": [{"type": "Var", "name": "_qd"}]}
            disp_w = self._expr_to_whyml(disp_call, local_refs or set(),
                                         invariant_ctx, subst)
            opt_ir = (f"(match {arg_w} with Some _qd -> IrOSome {disp_w} "
                      f"| None -> IrONone end)")
        else:
            opt_ir = "IrONone"
        return f"({cname} {var_w} {body_w} {opt_str} {opt_ir})"

    def _slice_bound_to_iropt_ir(self, tern: Any, local_refs: Set[str],
                                 invariant_ctx: bool,
                                 subst: Optional[Dict[str, str]]) -> str:
        """optional-field ext (monomorphic-option ADTs): convert ONE
        `_py_expr_slice` bound — the ternary `disp(expr.X) if expr.X else None`
        (an `IfExpr` over an `option emit_ir` Slice record field) — to the
        monomorphic `iropt_ir`:

            match expr.X with Some _v -> IrOSome (disp _v) | None -> IrONone end

        where `disp` is the recursive IR dispatcher (`self._py_expr_to_ir`)
        applied to the UNWRAPPED sub-node `_v` (faithful to
        `self._py_expr_to_ir(expr.X)` when the option is `Some _v`), and `None`
        yields `IrONone` (the Python `None` bound). NON-FACADE: the option field
        is read from `expr` and both arms are real. A shape that slips past the
        recognizer's gate fails closed to `IrONone`."""
        if not (isinstance(tern, dict) and tern.get("type") == "IfExpr"):
            return "IrONone"
        body = tern.get("body")
        orelse = tern.get("orelse")
        if not (isinstance(orelse, dict) and orelse.get("type") == "None"):
            return "IrONone"
        if not (isinstance(body, dict) and body.get("type") == "Call"):
            return "IrONone"
        fn = body.get("func")
        if not (isinstance(fn, str)
                and fn.rsplit(".", 1)[-1] in self._IR_DISPATCHERS):
            return "IrONone"
        bargs = body.get("args") or []
        if len(bargs) != 1:
            return "IrONone"
        # `bargs[0]` is the `option emit_ir` field read `expr.X`; match on it raw.
        optfld_w = self._expr_to_whyml(bargs[0], local_refs or set(),
                                       invariant_ctx, subst)
        # `_v` is the match-bound sub-node (a plain immutable `emit_ir`), NOT a
        # ref-local — keep it OUT of local_refs so it lowers to bare `_v` (no `!`
        # deref) as the dispatcher argument.
        disp_call = {"type": "Call", "func": fn,
                     "args": [{"type": "Var", "name": "_v"}]}
        disp_w = self._expr_to_whyml(disp_call, local_refs or set(),
                                     invariant_ctx, subst)
        return (f"(match {optfld_w} with Some _v -> IrOSome {disp_w} "
                f"| None -> IrONone end)")

    def _opt_field_disp_unwrap(self, call: Any, local_refs: Set[str],
                               invariant_ctx: bool,
                               subst: Optional[Dict[str, str]]) -> str:
        """SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): lower the
        RHS `self._py_expr_to_ir(<OptExprIR field>)` — the SAssign value child, where the
        argument is an `option emit_ir` record field (`stmt.value`) and the enclosing
        append is GUARDED by `stmt.value is not None` — to the UNWRAPPED dispatcher
        application:

            match <optfield> with Some _v -> disp _v | None -> IrOther "" end

        The Some arm applies the recursive dispatcher (`self._py_expr_to_ir`) to the
        unwrapped sub-node `_v`; the None arm (dead under the is-Some guard, but required
        for totality) yields the neutral `IrOther ""`. Sibling of `_slice_bound_to_iropt_ir`
        but producing a BARE `emit_ir` (SAssign's value), not an `iropt_ir`. Fails closed to
        `IrOther ""` if the shape is not a single-arg dispatcher call."""
        if not (isinstance(call, dict) and call.get("type") == "Call"):
            return '(IrOther "")'
        fn = call.get("func")
        if not (isinstance(fn, str) and fn.rsplit(".", 1)[-1] in self._IR_DISPATCHERS):
            return '(IrOther "")'
        cargs = call.get("args") or []
        if len(cargs) != 1:
            return '(IrOther "")'
        optfld_w = self._expr_to_whyml(cargs[0], local_refs or set(),
                                       invariant_ctx, subst)
        disp_call = {"type": "Call", "func": fn,
                     "args": [{"type": "Var", "name": "_v"}]}
        disp_w = self._expr_to_whyml(disp_call, local_refs or set(),
                                     invariant_ctx, subst)
        return (f"(match {optfld_w} with Some _v -> {disp_w} "
                f'| None -> IrOther "" end)')

    def _lower_sliceN_optfield(self, fields: Dict[str, Any],
                               local_refs: Set[str], invariant_ctx: bool,
                               subst: Optional[Dict[str, str]]) -> str:
        """optional-field ext (monomorphic-option ADTs): lower the rewritten
        `_py_expr_slice` construction `{"type":"SliceN","lower":..,"upper":..,
        "step":..}` (ternaries inlined by `_recognize_slice_builder`) to
        `(IrSliceN <opt lower> <opt upper> <opt step>)`. Each bound is converted
        to `iropt_ir` by `_slice_bound_to_iropt_ir`, faithfully carrying the
        present/absent option (NO dropped field). A missing bound key (never the
        case for the real `_py_expr_slice`, whose dict always has all three)
        defaults to `IrONone`."""
        lo = self._slice_bound_to_iropt_ir(fields.get("lower"), local_refs,
                                            invariant_ctx, subst)
        hi = self._slice_bound_to_iropt_ir(fields.get("upper"), local_refs,
                                            invariant_ctx, subst)
        st = self._slice_bound_to_iropt_ir(fields.get("step"), local_refs,
                                           invariant_ctx, subst)
        return f"(IrSliceN {lo} {hi} {st})"

    def _lower_functionvariant_optfield(self, fields: Dict[str, Any],
                                        local_refs: Set[str], invariant_ctx: bool,
                                        subst: Optional[Dict[str, str]]) -> str:
        """optional-field ext (monomorphic-option ADTs): lower the rewritten
        TYPE-LESS `_csl_function_variant` construction
        `{"type":"FunctionVariant","expr":..,("ordering":..)}` to
        `(IrFunctionVariant <expr> <iropt_str>)`. `expr` is the required
        `self._csl_to_ir(node.expr)` sub-node (a bare emit_ir). `ordering` (when
        present) is the `node.ordering` `option string` field, converted to
        `iropt_str`:

            match node.ordering with Some s -> IrSSome s | None -> IrSNone

        `node.ordering` is a parser `expect_name()` token — NEVER the empty
        string — so `if node.ordering:` truthiness is exactly presence and this
        mapping is faithful. An absent `ordering` (no conditional-add) is
        `IrSNone`. NON-FACADE: every field read from `node`; no dropped optional,
        no opaque val. A missing `expr` fails closed to `IrOther`."""
        if "expr" not in fields:
            return '(IrOther "FunctionVariant")'
        expr_w = self._expr_to_whyml(fields["expr"], local_refs or set(),
                                     invariant_ctx, subst)
        if "ordering" in fields:
            ord_w = self._expr_to_whyml(fields["ordering"], local_refs or set(),
                                        invariant_ctx, subst)
            opt_str = (f"(match {ord_w} with Some _os -> IrSSome _os "
                       f"| None -> IrSNone end)")
        else:
            opt_str = "IrSNone"
        return f"(IrFunctionVariant {expr_w} {opt_str})"

    def _todict_routed_ir(self, recv_dotted: str, key: str) -> Dict[str, Any]:
        """todict-reflection-plan.md R1: the TYPED-field IR that `<recv>.get(key)`
        routes to, where `recv` aliases `<node>.to_dict()`. The literal key `"type"`
        → the node's `kind` tag; any other key → the same-named field. `recv_dotted`
        may be dotted (`stmt.array`) → a nested receiver."""
        field = "kind" if key == "type" else key
        parts = recv_dotted.split(".")
        node: Dict[str, Any] = {"type": "Var", "name": parts[0]}
        for p in parts[1:]:
            node = {"type": "Attribute", "object": node, "attr": p}
        return {"type": "Attribute", "object": node, "attr": field}

    def _record_elem_field_py_type(self, ir: Dict[str, Any]) -> Optional[str]:
        """W8 capability (iii): the DECLARED python type of a field projected off an
        element of an `array <record>` SELF-FIELD — either directly
        (`self.toks[self.i].string`) or through the record-typed local bound to such a
        read (`t = self.toks[self.i]` … `t.string`). Returns None for every other
        expression. `_record_array_fields` / `_record_field_elem_locals` are populated
        only inside a class with a `List[<record>]` field, so this is None (hence
        byte-inert) everywhere else."""
        if not isinstance(ir, dict) or ir.get("type") not in ("Attribute", "FieldGet"):
            return None
        attr = ir.get("attr") or ir.get("field")
        if not attr:
            return None
        base = ir.get("object")
        if not isinstance(base, dict):
            base = ir.get("value")
        if not isinstance(base, dict):
            return None
        ecls = None
        if base.get("type") == "Var":
            ecls = (getattr(self, "_record_field_elem_locals", None)
                    or {}).get(base.get("name", ""))
        elif base.get("type") == "Subscript":
            _bv = base.get("value")
            if isinstance(_bv, dict) and _bv.get("type") in ("FieldGet", "Attribute"):
                _ob = _bv.get("object") or _bv.get("value")
                if isinstance(_ob, dict):
                    _ob = _ob.get("name")
                if _ob == "self":
                    ecls = (getattr(self, "_record_array_fields", None)
                            or {}).get(_bv.get("field") or _bv.get("attr"))
        if ecls is None:
            return None
        return getattr(self, "_record_types", {}).get(ecls, {}).get(
            "field_types", {}).get(attr)

    def _func_ret_union_some_str(self) -> bool:
        """True when the CURRENT function's return type is a synthesized
        `_union_*` variant (an `Optional[...]`/`Union[...]`) that carries at
        least one arm whose payload lowers to WhyML `string`. Used to route a
        string ternary in such a function through the string-expression path so
        (i) its literal arms emit real WhyML strings (not the int-hash of `""`)
        and (ii) the whole ternary is recognized as string-typed and injected
        into the variant's string arm (`Arm_N_0 …`) at the return site.
        Fail-closed: a non-union return (every corpus ternary) returns False, so
        normal ternaries stay byte-identical."""
        frt = getattr(self, "_func_return_type", "") or ""
        if not frt.startswith("_union_"):
            return False
        vinfo = getattr(self, "_variant_types", {}).get(frt)
        if not vinfo:
            return False
        for ctor in vinfo.get("constructors", {}).values():
            if ctor.get("arity", 0) == 0:
                continue
            payload = ctor.get("payload", [])
            if payload and self._union_arm_whyml_type(payload[0]) == "string":
                return True
        return False

    def _is_string_expr(self, ir: Dict[str, Any]) -> bool:
        """True if an IR expression is string-typed: a literal, a string-producing op, or a
        `str`-typed variable. (strings-plan Stage 2 — used to route `+` to `concat`.)"""
        t = ir.get("type")
        # PYTHON-AST NODE CTOR FAMILY (relaunch #8): a 0-FIELD ASDL SINGLETON construction
        # is a STRING expression — `_N("NotIn")()` lowers to `"NotIn"`, its class-name (the
        # increment-10 rule), and so does the const-dict form `_N(_CMP[<k>])()`. Without
        # this a `seq` accumulator of such singletons (`comparison`'s `ops`) is classified
        # `seq int` and every appended class name is INT-HASHED — measured as
        # `Seq.snoc !ops 441879163`. Gated on `_uses_pyast_parser` -> byte-inert.
        if self._uses_pyast_parser() and not ir.get("args") and not ir.get("keywords"):
            _sing0 = set(self.ir.get("pyast_singleton_nodes", []) or [])
            if (t == "Call" and isinstance(ir.get("func"), str)
                    and ir["func"] in _sing0):
                return True
            if t == "ClassByNameCall":
                _ce0 = ir.get("class_expr") or {}
                if (isinstance(_ce0, dict) and _ce0.get("type") == "Subscript"
                        and isinstance(_ce0.get("value"), dict)
                        and _ce0["value"].get("type") == "Var"):
                    _cdn0 = self._const_dict_name(_ce0["value"].get("name"))
                    _cdt0 = (getattr(self, "_module_const_dicts", {}) or {}).get(_cdn0)
                    if _cdt0 and _sing0 and all(_v0 in _sing0 for _v0 in _cdt0.values()):
                        return True
        # W8 capability (iii): a `str` field projected off an `array <record>` SELF-FIELD
        # element (`self.toks[self.i].string`, or `t.string` on the record-typed local
        # bound to such a read) is STRING-typed. Without this the projection keeps the
        # default int typing and a `== "EOF"` comparison coerces it to int (L3-tc:
        # `This expression has type string, but is expected to have type int`).
        if self._record_elem_field_py_type(ir) == "str":
            return True
        # CARRIER-FIELD STRING ROUTING (L13 cursor-nest): `t.kind` where `t` is a mutable
        # `Optional[<dataclass>]` local is a read of the CARRIER RECORD's field, so it is
        # string-typed exactly when that field is. Without this the comparison
        # `t.kind == "IDENT"` keeps the default int typing and the literal is emitted as
        # its int HASH (measured: `... = 910842745`) against a now-string projection —
        # `has type int, but is expected to have type string`. Worse than the type error,
        # the pre-existing int-hash form was VALUE-BLIND: it compared opaque hashes.
        # Reuses `_union_local_field_projection`'s own fail-closed resolution, so it can
        # only fire where that projection also fires.
        # TERM CARRIER: a `string`-typed payload projection off a `term`-typed local
        # (`atom.name`, the unique-arm projection built in `_handle_attribute_expr`) is a
        # STRING read. Without this classification the `atom.name in _KNOWN_FN_HEADS`
        # membership keeps the int operand shape and rejects the projected string
        # (`has type string, but is expected to have type int`). Routing it through the
        # same `str_hash_op` coercion every other converted member of this nest already
        # uses for its module-level string-set membership keeps the treatment uniform.
        if (t == "Attribute" and isinstance(ir.get("object"), dict)
                and ir["object"].get("type") == "Var"
                and ir["object"].get("name") in getattr(self, "_term_local_vars", set())):
            _tsp = (getattr(self, "_term_adt_spec", None) or {}).get("ctors") or {}
            _own = [(cn, flds) for cn, flds in _tsp.items()
                    if any(fn == ir.get("attr") for fn, _w in flds)]
            if len(_own) == 1 and any(
                    fn == ir.get("attr") and _w == "string" for fn, _w in _own[0][1]):
                return True
        # cursor-nest `parse_atom`: the union-returning-sibling-CALL base is the same
        # string-valued read as the union LOCAL base directly below — `self.peek().kind`
        # is a `str` record field just as `t.kind` is. Without it the `== "COMMA"`
        # comparison falls to the int-hash model (`_rec_.token_kind = 1429053303`), a
        # string-vs-int type error AND the value-blind hash facade. One shared body: the
        # only difference is where the union type comes from.
        _ustr = None
        if (t == "Attribute" and isinstance(ir.get("object"), dict)
                and ir["object"].get("type") == "Call"):
            _ustr = self._sibling_call_union_type(ir["object"])
        if (t == "Attribute" and isinstance(ir.get("object"), dict)
                and (ir["object"].get("type") == "Var"
                     and ir["object"].get("name") in getattr(
                         self, "_optional_union_locals", set())
                     or _ustr)):
            _st = (_ustr if _ustr
                   else getattr(self, "_current_symbol_table", {}).get(
                       ir["object"].get("name")))
            _vi = getattr(self, "_variant_types", {}).get(_st) or {}
            for _cn, _c in (_vi.get("constructors") or {}).items():
                if _c.get("arity") != 1:
                    continue
                _pay = (_c.get("payload") or [None])[0]
                _rn = next((rn for rn in getattr(self, "_record_types", {})
                            if self._record_types[rn].get("whyml_name") == _pay
                            or rn == _pay), None)
                if _rn is not None and (self._record_types[_rn].get("field_types") or {}
                                        ).get(ir.get("attr")) in ("str", "string"):
                    return True
        # self-tcb-reduction WRITER class (`_build_param_list`): the `self._current_self_type`
        # read (`current_self_type_of self : string`) is STRING, so `f"(self:
        # {self._current_self_type})"` lowers via the all-string str_concat_op path. Gated ->
        # byte-inert elsewhere.
        if (t == "FieldGet" and ir.get("object") == "self"
                and ir.get("field") == "_current_self_type"
                and self._emitting_build_param_list()):
            return True
        # self-tcb-reduction `_compute_return_type` PATH(b): a DIRECT-self nested read
        # `self._record_types[K]["<lit>"]` / `self._variant_types[ann]["<lit>"]` is STRING
        # (its `<base>_<lit> : string` reader), so an f-string interpolating it lowers via
        # the all-string str_concat_op path. Gated inside `_self_map_field_base` on the
        # `_compute_return_type` file -> byte-inert elsewhere.
        if t == "Subscript":
            _idx3 = ir.get("index", {})
            _inner3 = ir.get("value", {})
            # self-tcb-reduction WRITER class (`_build_param_list`): `func["self_type"]` — a
            # STRING-literal subscript of the `func` pydict — reads a string VALUE (its hval
            # carrier projects via `hstr_of`), so `func["self_type"].lower()` reaches the
            # faithful `str_lower_op`. Gated -> byte-inert elsewhere.
            if (self._emitting_build_param_list()
                    and isinstance(_idx3, dict) and _idx3.get("type") == "String"
                    and self._expr_is_pyval(ir)):
                return True
            if (isinstance(_idx3, dict) and _idx3.get("type") == "String"
                    and isinstance(_inner3, dict) and _inner3.get("type") == "Subscript"
                    and self._self_map_field_base(_inner3.get("value", {}))):
                return True
            # `_compute_return_type` PATH(b): `<optmap-getter>["<lit>"]` (`_cmg["elem_whyml"]`)
            # reads a STRING value, so the f-string interpolating it lowers all-string.
            if (isinstance(_idx3, dict) and _idx3.get("type") == "String"
                    and isinstance(_inner3, dict) and _inner3.get("type") == "Var"
                    and _inner3.get("name") in getattr(self, "_optmap_getter_locals", set())):
                return True
        # resync-campaign.md R2: a ternary whose BOTH arms are string-typed is string (the
        # emitter's `(if _poly then "<decl A>" else "<decl B>") + "…ensures…"` concat). Both
        # arms must be string; @mutable_state (the emitter's string decls). Lever-7 extends the
        # gate: a both-arms-string ternary in an `Optional[str]`/`Union[…, str]`-returning
        # function (`_func_ret_union_some_str()`) is ALSO string-typed, so it injects into the
        # variant's string arm (`Arm_N_0 …`) at the return site instead of type-clashing the bare
        # ternary against the `_union_*` variant. Fail-closed on the union predicate → byte-inert.
        if (t == "IfExpr"
                and (getattr(self, "_current_self_type", None)
                     in getattr(self, "_mutable_state_classes", set())
                     or self._func_ret_union_some_str()
                     or self._emitting_compute_return_type()
                     or self._emitting_build_param_list())
                and self._is_string_expr(ir.get("body", {}))
                and self._is_string_expr(ir.get("orelse", {}))):
            return True
        # string-bool-op: a both-operands-string `or`/`and` is itself STRING (Python's
        # `a or b`/`a and b` return one of the operands, not a bool) — so it types as a
        # string local / return and routes `+`, `.lower()`, etc. through the string ops.
        # The `or` right arm may be `None` (`<get> or ""` idiom, right modeled as "").
        # Both operands must be string; a mixed/bool/int operand keeps the non-string
        # (bool/int) typing (additivity). Subsumes the earlier @mutable_state `or` branch.
        if (t == "BinOp" and ir.get("op") in ("and", "or")
                and self._is_string_expr(ir.get("left", {}))
                and (self._is_string_expr(ir.get("right", {}))
                     or (ir.get("op") == "or"
                         and isinstance(ir.get("right"), dict)
                         and ir["right"].get("type") == "None"))):
            return True
        if t == "Call":
            _fn = ir.get("func", "")
            # G2 (09-2223 pure-classifier increment): `<record-var>.get("<str-field>")` is
            # STRING-typed (its G1 lowering is the native `func.kind : string`), so a
            # comparison `func.get("kind") == "method"` routes through `str_eq_op` — a
            # faithful string content compare — instead of the unfaithful int-hash
            # `(func_get_1 …) <> 317966025`. Gated on the record-typed receiver + a `str`
            # field via `_record_get_field` (never a plain dict), so it is corpus-byte-inert.
            _rg = self._record_get_field(ir)
            if _rg is not None and _rg[2] == "str":
                return True
            # option-of-record projection (boundary-1 G1 extension): `<optvar>.get("<str-
            # field>")` on an `Optional[<record>]` receiver is STRING-typed (the Some arm
            # projects `_r.<label> : string`), so `optvar.get("type") == "Compare"` routes
            # through `str_eq_op`, not the int-hash. Gated on `_option_record_get_field`.
            _org = self._option_record_get_field(ir)
            if _org is not None and _org[2] == "str":
                return True
            # `str(x)` is string-typed (identity on a str, `int_to_string` on an int) — so a
            # `.lower()`/`.strip()` on it (`str(binder_type).lower()`) recognizes as a faithful
            # string-value method rather than falling to the opaque scalar op.
            if _fn == "str":
                return True
            # faithful-string-op.md §3.1–3.3: `.replace`/`.lower`/`.upper`/`.strip` on a
            # string receiver is itself string-typed, so a receiving local (`arr_name =
            # func.rsplit(".",1)[0].replace(".","_")`) types as a string local.
            if self._is_str_value_method(ir):
                return True
            # §3.5: a literal-string-list `sep.join([…])` is string (nested concat).
            if self._is_literal_string_join(ir):
                return True
            # list-comprehension-lowering.md L2: a general `sep.join(<string-array>)` is a
            # `string` (str_join_arr), so `"(" + ",".join(xs) + ")"` routes `+` to concat.
            if ((_fn == "join" or (isinstance(_fn, str) and _fn.endswith(".join")))
                    and self._join_arg_elem_is_string(
                        (ir.get("args") or [{}])[0] if ir.get("args") else {})):
                return True
            # typed-ir-for-b-ceiling.md §14: `getattr(self, "<field>", <default>).get(k)`
            # on a `dict[str,str]` field reads back a `string` — the getattr-defensive
            # form of the §12 self-field-dict get (func is bare `"get"` with a `getattr`
            # receiver, before the §14 rewrite).
            if _fn == "get":
                # subscript-receiver .get with a STRING key (`a[i].get("name")`/`.get("type")`) on an
                # emit_ir element → a string projection (name_of/kind_of/func_of/value_of), so a
                # `== "self"` comparison routes through str_eq_op. @mutable_state / emit_ir-gated.
                _grcv = ir.get("receiver")
                if isinstance(_grcv, dict) and self._is_emit_ir_expr(_grcv):
                    _gk = (ir.get("args") or [{}])[0]
                    # self-tcb-reduction (_is_null_byte_lit): a Number element's `.get("value")`
                    # there reads the INT payload (`num_of`), so it is NOT string-typed — the
                    # `== 0` comparison must stay an int `=`, not the mixed str_hash_op path.
                    # Scoped via `_current_emitting_func` → corpus/consumer-inert.
                    if (isinstance(_gk, dict) and _gk.get("type") == "String"
                            and _gk.get("value") in _EMIT_IR_STR_KEYS + ("value",)
                            and not (_gk.get("value") == "value"
                                     and (getattr(self, "_current_emitting_func", None) or "")
                                     .endswith("_is_null_byte_lit"))):
                        return True
                _gf = self._getattr_self_field(ir.get("receiver"))
                if _gf and self._self_field_dict_nu(f"self.{_gf}") == "string":
                    return True
                # `_compute_return_type` PATH(b): `getattr(self, "_dict_key_types"|
                # "_dict_value_types", {}).get(K)` reads a `map string (option string)`
                # self-field -> a STRING value (the `<base>_get : string` reader), so
                # `... == "string"` routes through str_eq_op and `_nu`/`_nu_arg` classify
                # as strings. Per-method scoped -> byte-inert elsewhere.
                if (self._emitting_compute_return_type()
                        and self._getattr_self_field(ir.get("receiver"))
                        in ("_dict_key_types", "_dict_value_types")):
                    return True
            if _fn.endswith(".get"):
                # item34.md CF5: `<handler>.get("exc_type")` — a 1-arg string-key `.get` on a
                # NON-emit_ir receiver reads a string scalar field (matches `_grecv_str`).
                _gargs = ir.get("args") or []
                if (len(_gargs) == 1 and isinstance(_gargs[0], dict)
                        and _gargs[0].get("type") == "String"
                        and getattr(self, "_current_self_type", None)
                        in getattr(self, "_mutable_state_classes", set())
                        and not self._is_emit_ir_expr(
                            {"type": "Var", "name": _fn[:-len(".get")]})):
                    return True
                # self-field-dict-reflection (typed-ir §12): `self.<dict[str,str]-field>
                # .get(k)` reads back a `string` (`option string` values), so `… == "s"`
                # routes through `str_eq_op`, not an int hash.
                if self._self_field_dict_nu(_fn[:-len(".get")]) == "string":
                    return True
                # self-tcb-reduction _infer_tuple_slot_type (cap-a): a `<param/local
                # dict[str,str]>.get(k)` read reads back a `string` — the map's `option
                # string` value type recorded in `_dict_value_types` (from a `Dict[str,str]`
                # param/local annotation). So `elt.get("type") == "Var"` and a `... or ""`
                # default route through `str_eq_op`/string-concat, never an int hash.
                # Corpus-inert: the only reference-corpus `Dict[str,str]` is a class-constant
                # table, never read via `.get` into a string comparison (measured).
                if getattr(self, "_dict_value_types", {}).get(
                        _fn[:-len(".get")]) == "string":
                    return True
                # §26: `X.get(k)` where X aliases a `dict[str,str]` self-field reads a string.
                _alias0 = self._alias_self_field(_fn[:-len(".get")])
                if _alias0 and self._self_field_dict_nu(_alias0) == "string":
                    return True
                _al = getattr(self, "_todict_aliases", {}).get(_fn[:-len(".get")])
                if _al is not None:
                    _kir = (ir.get("args") or [{}])[0]
                    if isinstance(_kir, dict) and _kir.get("type") == "String":
                        if self._is_emit_ir_expr(self._todict_recv_node_ir(_al)):
                            return _kir.get("value") in _EMIT_IR_STR_KEYS
                        return self._is_string_expr(
                            self._todict_routed_ir(_al, _kir.get("value")))
                # typed-ir-for-b-ceiling.md B-C3: `<emit_ir>.get("type"|"name"|"attr"|
                # "value")` projects to `kind_of`/`name_of`/`value_of` — all `string` —
                # so `node.get("type") == "Var"` routes through `str_eq_op`, not an int
                # hash. (`"object"` is emit_ir, not string → not matched here.)
                _rn = _fn[:-len(".get")]
                if self._is_emit_ir_expr({"type": "Var", "name": _rn}):
                    _kir = (ir.get("args") or [{}])[0]
                    if (isinstance(_kir, dict) and _kir.get("type") == "String"
                            and _kir.get("value") in _EMIT_IR_STR_KEYS):
                        return True
        if t == "String" or t in ("StrConcat", "StrSub"):
            return True
        if t == "Var":
            _vn = ir.get("name", "")
            # self-tcb-reduction T1.a: a collected string LOCAL (`var = node.var` → name_of) counts
            # as string even before its symbol-table type is set, so `var in self._seq_locals`
            # hashes the key. Byte-safe: `_string_local_vars` is empty outside @mutable_state.
            return (getattr(self, "_current_symbol_table", {}).get(_vn) == "str"
                    or _vn in getattr(self, "_string_local_vars", set()))
        # Indexing/slicing a string yields a string (s[i] is a 1-char string, s[a:b] a
        # substring) — both reuse str_sub_op in their handlers, so the *result* of such a
        # node is string-typed exactly when its base is. Required so `s[a:b] == t` routes to
        # the real string-equality bridge rather than the mixed int-hash fallback (0471).
        if t in ("Subscript", "SliceAccess"):
            # faithful-string-op.md §3.4: a split-element read `<string>.split(sep)[i]` is
            # a substring → string-typed, even though the split CALL itself is a list.
            if self._split_call_recv_sep(ir.get("value", {})) is not None:
                return True
            # §26: subscript-form emit_ir string-projection `<emit_ir>["type"/"name"/
            # "attr"/"func"]` (the string keys) → string, for `arr["value"]["name"]`.
            # cf6.md M1.3: EXCLUDE node keys — as a SUBSCRIPT `c["pattern"]` reads a sub-NODE,
            # not the kind string (only `.get("pattern")` is the kind).
            _kir = ir.get("index", {})
            if (isinstance(_kir, dict) and _kir.get("type") == "String"
                    and (_kir.get("value") in _EMIT_IR_STR_KEYS or _kir.get("value") == "object")
                    and (_kir.get("value") not in _EMIT_IR_NODE_KEYS or _kir.get("value") == "object")
                    and self._is_emit_ir_expr(ir.get("value", {}))):
                return True
            # list-comprehension-lowering.md L5/L6: a `self.<dict[str,str]-field>[k]` read
            # (`self._abstract_ops[k]`) or a string-element array-local index (`safe[i]`)
            # is a string.
            _v = ir.get("value", {})
            if isinstance(_v, dict):
                if _v.get("type") in ("Attribute", "FieldGet"):
                    _o = _v.get("object"); _f = _v.get("field") or _v.get("attr")
                    if isinstance(_o, str) and self._self_field_dict_nu(f"{_o}.{_f}") == "string":
                        return True
                if (_v.get("type") == "Var"
                        and getattr(self, "_array_elem_types", {}).get(_v.get("name")) == "string"):
                    return True
                # self-ir-schema.md IR3: `sv["name"]`/`sv["mutex"]` on a `sharedvar`-typed
                # comprehension loop var → the record's string field (used only for
                # element-type inference; the comprehension itself is opaque).
                if (_v.get("type") == "Var"
                        and getattr(self, "_current_symbol_table", {}).get(_v.get("name")) == "sharedvar"
                        and _kir.get("value") in ("name", "mutex")):
                    return True
                # self-tcb-reduction Tier-5 (union/match cluster C4): a Number-indexed read
                # of a pyval collection local (`payload[0]`, payload : `hval`) projects the
                # idx-th `HStr` as a `string` via `hval_nth_str`, so `payload[0] == arm_tag`
                # routes through `str_eq_op` (a real string compare), not the int hash.
                if (_v.get("type") == "Var"
                        and _v.get("name") in getattr(self, "_pyval_locals", set())
                        and isinstance(_kir, dict) and _kir.get("type") == "Number"):
                    return True
                # lever #1 sub-inc A cap (d): a subscript of a CALL whose registered
                # abstract-val return type is `array string` (`self._resolve_dotted_
                # signature(func)[0]`) projects a real STRING element (`subscript_get_str`),
                # so a `== "string"` comparison routes through `str_eq_op` (a faithful
                # string compare), not the int-hash `= 1776665034`. Name-gated on the
                # `array string` ret-type -> byte-inert for every non-`array string` call.
                if (_v.get("type") == "Call"
                        and self._resolve_dotted_signature(_v.get("func", ""))[0] == "array string"):
                    return True
            return self._is_string_expr(ir.get("value", {}))
        # `s + t` is a `BinOp(+)` node (string concatenation when both operands are
        # strings) — so a concat expression is itself string-typed. Required so e.g.
        # `len(s + t)` routes to str_length_op rather than the opaque iter_length.
        if t == "BinOp" and ir.get("op") == "+":
            return (self._is_string_expr(ir.get("left", {}))
                    and self._is_string_expr(ir.get("right", {})))
        # 10-1732-gap (Gap 2): a `Call` to a module function (incl. an injected
        # imported `\trusted` stub) declared `-> str` is itself string-typed. Required
        # so `len(g(s))` routes to str_length_op rather than the opaque iter_length.
        # Keyed on the SEPARATE `_module_method_return_annotations` map (Python
        # `return_annotation == "str"`), NOT `_module_method_return_types` — the latter
        # is a stripped map that leaves `-> str` callees as "int" (see the wiring note
        # in Module6_WhyMLTranspiler.transpile). A lookup MISS (builtin/unresolved name)
        # yields None != "str" → safe False (unchanged opaque path).
        if t == "Call":
            fn = ir.get("func", "")
            # 10-2300-spec-5: `chr(...)` yields a 1-char string (chr_op : ... -> string).
            # So `len(chr(b))`, `s + chr(b)`, `chr(b) == c`, and `chr(...)` as a subscript
            # base route through the real string bridges, not the opaque int fallback.
            # (`ord(...)` is int → default `False` below, no edit needed.)
            if fn == "chr":
                return True
            # no-more-int emitter L4: a `self.<m>(…)` call keys the return-annotation
            # map by the class-qualified name (`<self_type>__<m>`, as `_handle_dotted_
            # call` does), so a `str`-returning sibling emitter (`self._stmts_to_whyml`,
            # `self._expr_to_whyml`) is recognized as string — routing `s + <call>` to
            # concat. A bare call is keyed by its name (unchanged).
            ann = getattr(self, "_module_method_return_annotations", {})
            if fn.startswith("self."):
                tail = fn[len("self."):]
                cls = getattr(self, "_current_self_type", None)
                key = f"{cls}__{tail}" if cls else tail
            else:
                key = fn
            return ann.get(key) == "str"
        # todict-reflection-plan.md R3: in a @mutable_state class (the emitter model) an
        # f-string is string-typed — `_handle_fstring_expr` there lowers every f-string
        # (all-string OR mixed str/int via `int_to_string`) to a `string`. So a string
        # target's `code += f"…"` routes to `str_concat_op`. Gated on @mutable_state →
        # byte-identical for every other f-string.
        if t == "FString":
            return (bool(ir.get("parts"))
                    and (getattr(self, "_current_self_type", None)
                         in getattr(self, "_mutable_state_classes", set())
                         or self._emitting_compute_return_type()
                         or self._emitting_build_param_list()))
        # todict-reflection-plan.md: a record's `str`-typed FIELD read (`n.kind` on a
        # record-typed param/local, or `self.f`/`global.f`) is string-typed — so
        # `n.kind == "Var"` routes to `str_eq_op`, not the int-hash mismatch. self/
        # global/record-var via `_field_type_of`; a record-typed PARAM/local via the
        # symbol table + the record's `field_types`. A non-str/unknown field → False
        # (unchanged opaque path) → byte-identical outside genuine str-field reads.
        if t in ("Attribute", "FieldGet"):
            # J2/J3 convergence (Call-internals): the string-producing keyword/call reads
            # `kw.arg`, `kw.value.id`, `kw.value.attr` and `<emit_ir call>.func.id` are
            # `string`, so `kw.arg == "bound"` / `call.func.id == "TypeVar"` route through
            # `str_eq_op` (faithful content compare), not the int-hash. Corpus-inert.
            if t == "Attribute":
                _attr = ir.get("attr")
                _o = ir.get("object", {})
                # W8 capability (vi): `self.cur().string` projects a `str` field off a
                # RECORD-returning sibling call, so the comparison must route through
                # `str_eq_op` (faithful content compare) rather than collapsing the
                # projection to the legacy int hash. Same `_record_array_fields` gate as
                # the emission branch in `_handle_attribute_expr` → byte-inert elsewhere.
                if (isinstance(_o, dict) and _o.get("type") == "Call"
                        and isinstance(_o.get("func"), str)
                        and _o["func"].startswith("self.")
                        and getattr(self, "_record_array_fields", None)):
                    _crt = self._resolve_dotted_signature(_o["func"])[0]
                    for _rc, _ri in getattr(self, "_record_types", {}).items():
                        if _ri.get("whyml_name") == _crt:
                            if _ri.get("field_types", {}).get(_attr) in ("str", "string"):
                                return True
                            break
                # K2 convergence (self-tcb-reduction): `<pyast_stmt local>.name` projects
                # to `def_name` — the ClassDef/FunctionDef NAME, a `string` — so
                # `cstmt.name == "__init__"` routes through `str_eq_op` (faithful content
                # compare, not the int-hash) and a `"class": stmt.name` dict value wraps as
                # `PStr`, not `PInt`. `.target`/`.value`/`.annotation` project to emit_ir
                # (handled below via `_is_emit_ir_expr`), so ONLY `.name` is string here.
                if (_attr == "name"
                        and self._pyast_stmt_child_var(_o) is not None):
                    return True
                if (getattr(self, "_keyword_locals", None)
                        and _attr == "arg" and self._keyword_var(_o) is not None):
                    return True
                if (getattr(self, "_keyword_locals", None) and _attr in ("id", "attr")
                        and isinstance(_o, dict) and _o.get("type") == "Attribute"
                        and _o.get("attr") == "value"
                        and self._keyword_var(_o.get("object", {})) is not None):
                    return True
                if (_attr == "id" and isinstance(_o, dict)
                        and _o.get("type") == "Attribute" and _o.get("attr") == "func"
                        and isinstance(_o.get("object"), dict)
                        and _o["object"].get("type") == "Var"
                        and _o["object"].get("name")
                        in getattr(self, "_emit_ir_local_vars", set())):
                    return True
            ft = self._field_type_of(ir)
            # self-tcb-reduction T1.a: a STRING-valued emit_ir attr (`.kind`/`.var`/`.op`/…) reads a
            # discriminant/name string, so `inner.kind == "Subscript"` routes through `str_eq_op`.
            if ft is None and (ir.get("attr") or ir.get("field")) in _EMIT_IR_STR_ATTRS:
                _ko = ir.get("value") or ir.get("object")
                if isinstance(_ko, dict) and self._is_emit_ir_expr(_ko):
                    return True
            if ft is None:
                if t == "FieldGet":
                    _rn, _fl = ir.get("object"), ir.get("field")
                else:
                    _r = ir.get("value") or ir.get("object")
                    _rn = _r.get("name") if isinstance(_r, dict) else None
                    _fl = ir.get("attr")
                if isinstance(_rn, str):
                    _rt = getattr(self, "_current_symbol_table", {}).get(_rn)
                    if _rt and _rt in getattr(self, "_record_types", {}):
                        ft = self._record_types[_rt].get("field_types", {}).get(_fl)
            return ft in ("str", "string")
        return False

    def _is_float_expr(self, ir: "ExprIR") -> bool:
        """True if an IR expression is float-typed (no-more-int Stage D): a float literal,
        a `float`-typed Var, or float arithmetic. Routes ops to Why3 `real`."""
        t = ir.get("type")
        if t == "Number":
            return isinstance(ir.get("value"), float)
        if t == "Var":
            return getattr(self, "_current_symbol_table", {}).get(ir.get("name", "")) == "float"
        if t == "BinOp" and ir.get("op") in ("+", "-", "*", "/"):
            return (self._is_float_expr(ir.get("left", {}))
                    and self._is_float_expr(ir.get("right", {})))
        return False

    def _str_operand_to_int(self, whyml_str: str) -> str:
        """Map a string operand into the legacy int-hash domain. Used when a string is
        compared against a genuine int (e.g. an opaque `.decode()` result that PyCSL has no
        string model for): the comparison reverts to the pre-strings opaque int-equality
        rather than forcing a type-incorrect `str_eq_op`. A literal hashes directly; a
        non-literal string goes through an uninterpreted `str_hash_op`."""
        s = whyml_str.strip()
        if s.startswith('"') and s.endswith('"'):
            return str(stable_hash(whyml_str))
        self._add_abstract_op("val str_hash_op (s: string) : int")
        return f"(str_hash_op {whyml_str})"

    def _handle_binop(self, node: "ExprIR", local_refs: Set[str],
                      invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        # Phase-B-expr: typed signature. The body's deep, branchy child inspection
        # stays dict-based via the node's canonical dict view (byte-identical); the
        # handler does not read attribution keys, so the opaque-coerced node's
        # to_dict() is faithful for its purposes.
        expr = node.to_dict()
        raw_op = expr["op"]
        # #5 (pyval `or {}` / `or []` default, self-tcb-reduction Tier-5): `<pyval> or {}`
        # (the legacy `registry = self.f.get(k) or {}` default) lowers to a FAITHFUL
        # keep-if-map-else-empty projection over the heterogeneous carrier —
        #   (match <pyval> with PMap m_or -> <pyval> | _ -> PMap (const None))
        # — NOT the int-erased boolean `if (not (str_eq_op ...)) || ... then 1 else 0`
        # facade. The left operand is a `pyval` (a `.get` on a pyval self-field/local),
        # the right is an empty dict/list literal. Gated on the left being pyval-producing
        # (`_binop_left_is_pyval`) -> corpus byte-inert.
        if raw_op == "or" and not self._in_spec:
            _pd = self._recognize_pyval_or_default(expr, local_refs, invariant_ctx, subst)
            if _pd is not None:
                return _pd
            # _field_type_of: the `<emit_ir>.get("value") or <emit_ir>.get("object")
            # or {}` Attribute-receiver idiom -> `avalue_of <node>` (handled whole so the
            # `.get("object")` operand escapes the generic key projection). Byte-inert.
            _ar = self._recognize_attr_receiver_idiom(expr, local_refs, invariant_ctx, subst)
            if _ar is not None:
                return _ar
            # self-tcb-reduction (union/match cluster): `<emit_ir>.get("body"/"orelse", [])
            # or []` (`body = stmt.get("body", []) or []` in `_try_union_is_none_match`) — the
            # left projects the statement-list (`stmts_of`, an `array int` fed to
            # `_stmts_to_whyml`), and the right is the empty-list fallback. For a present
            # projected array the `or []` is a no-op; return the array so `body`/`orelse`
            # stay `array int`, NOT the int-truthiness collapse (`if <arr> <> 0 || … then 1
            # else 0`, an `array`-vs-`int` type error). Gated on a `.get(<stmt-list-key>)`
            # left + empty-list right -> corpus/other-mirror byte-inert.
            _lor, _ror = expr.get("left"), expr.get("right")
            if (isinstance(_ror, dict)
                    and _ror.get("type") in ("ArrayLit", "List", "ListLit", "MkList")
                    and not _ror.get("elts")
                    and isinstance(_lor, dict) and _lor.get("type") == "Call"
                    and isinstance(_lor.get("func"), str) and _lor["func"].endswith(".get")):
                _lga = _lor.get("args") or []
                if (_lga and isinstance(_lga[0], dict)
                        and _lga[0].get("type") == "String"
                        and _lga[0].get("value") in ("body", "orelse", "captures",
                                                     "args", "parts", "elts", "alternatives")):
                    _lw = self._expr_to_whyml(_lor, local_refs, invariant_ctx, subst)
                    return _lw
        # SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): the
        # `_py_stmt_expr` docstring-skip guard `isinstance(v, ast.Constant) and
        # isinstance(v.value, str)` (v an ExprIR child) collapses to `(is_str v)` — the
        # WHOLE `and`-compound, since `isinstance(v, ast.Constant)` alone has no
        # discriminant. Fires before the generic `&&` split (which would fail to lower the
        # bare Constant isinstance). Corpus-inert (triple-gated).
        if raw_op == "and":
            _sc = self._recognize_str_constant_guard(expr, local_refs)
            if _sc is not None:
                return _sc
            # value-model campaign incr8: the None sibling — `isinstance(x, ast.Constant) and
            # x.value is None` collapses to `(is_none x)` (the faithful IrNone discriminant, the
            # authorized alternative to the impossible pyconst_val narrowing). Same triple-gated
            # corpus-inert shape as the str guard.
            _nc = self._recognize_none_constant_guard(expr, local_refs)
            if _nc is not None:
                return _nc
        # tier3-p1 T3.1.2 (spike LAW 1): `<emit_ir node>.get("type") == "K"` (K a known ADT
        # constructor kind) lowers to the constructor DISCRIMINANT `(is_K node)` — a
        # match-based bool — instead of `str_eq_op (kind_of node) "K"`. This is the ONLY
        # guard shape under which the structural-recursion `variant { size node }` discharges
        # (the `kind_of e = "K"` test admits the IrOther "K" catch-all, which breaks the
        # size-decrease law). Gated on NOT @mutable_state: the self-annotate mirror keeps its
        # already-proven `kind_of` path (Phase 2 adopts `is_K`); a driver (no @mutable_state)
        # takes the discriminant. Corpus has no emit_ir → never fires → byte-identical.
        if (raw_op in ("==", "!=") and not self._in_spec
                and not getattr(self, "_mutable_state_classes", None)):
            _disc = self._emit_ir_kind_discriminant(expr.get("left"), expr.get("right"))
            if _disc is not None:
                return _disc if raw_op == "==" else f"(not {_disc})"
        # KIND-LOCAL DISCRIMINANT FLOW (relaunch #11) — the NARROW mirror carve-out to the
        # `not _mutable_state_classes` gate above. The mirror deliberately keeps the
        # already-proven `kind_of` string path; but for a STRUCTURALLY RECURSIVE emitter
        # method the string test is not merely a different lowering, it is INSUFFICIENT:
        # the injected `variant { size <p> }` needs `size (body_of p) < size p`, whose law
        # is stated over `is_ifexpr`, and `kind_of p = "IfExpr"` admits the `IrOther
        # "IfExpr"` catch-all for which the decrease is genuinely FALSE (measured: two
        # 30s/62M-step Timeouts on `_rhs_yields_map`'s ternary arm). So the carve-out is
        # gated on exactly the situation that needs it — the guard tests a LOCAL bound once
        # from `<p>.get("type", …)`, and `<p>` is THIS function's own variant measure —
        # and nowhere else. Corpus has no emit_ir → never fires → byte-identical.
        if (raw_op in ("==", "!=") and not self._in_spec
                and getattr(self, "_size_variant_param", None)):
            _l = expr.get("left")
            if (isinstance(_l, dict) and _l.get("type") == "Var"
                    and isinstance((getattr(self, "_kind_local_recv", None) or {}).get(
                        _l.get("name")), dict)):
                _kr = self._kind_local_recv[_l["name"]]
                _r = expr.get("right")
                if (_kr.get("type") == "Var"
                        and _kr.get("name") == self._size_variant_param
                        and isinstance(_r, dict) and _r.get("type") == "String"):
                    _pred2 = self._KIND_DISCRIMINANT.get(_r.get("value"))
                    if _pred2 is not None:
                        _rw = self._expr_to_whyml(_kr, local_refs, invariant_ctx, subst)
                        _disc2 = f"({_pred2} {_rw})"
                        return _disc2 if raw_op == "==" else f"(not {_disc2})"
        # sub-inc B (`_maybe_inject_union_return`): `<string> == <optstr-local>` — a `==`/
        # `!=` between a string-typed operand and an `option string`-returning-call local
        # (`arm_type == val_type`, `val_type = self._infer_return_value_type(val_ir)`).
        # After the guarding `if val_type is None: return val`, `val_type` is a `str`, so
        # the compare is a faithful string equality — option-UNWRAP the local and
        # `str_eq_op` (Python `str == None` is False, so the `None` arm is `false`, correct
        # even independent of the guard). Without this the string operand int-hashes
        # against the raw option (`str_hash_op arm_type = !val_type`, an `int`/`option`
        # type clash). Gated on `_option_str_return_vars` -> corpus/other-mirror byte-inert.
        if raw_op in ("==", "!=") and not self._in_spec:
            _osv = getattr(self, "_option_str_return_vars", set())
            _bl, _br = expr.get("left"), expr.get("right")
            _optv = _strv = None
            if (isinstance(_br, dict) and _br.get("type") == "Var"
                    and _br.get("name") in _osv and self._is_string_expr(_bl)):
                _optv, _strv = _br, _bl
            elif (isinstance(_bl, dict) and _bl.get("type") == "Var"
                    and _bl.get("name") in _osv and self._is_string_expr(_br)):
                _optv, _strv = _bl, _br
            if _optv is not None:
                _ov = f"!{whyml_ident(_optv.get('name'))}"
                _sw = self._expr_to_whyml(_strv, local_refs, invariant_ctx, subst)
                _chk = (f"(match {_ov} with Some _osv_s -> (str_eq_op {_sw} _osv_s) "
                        f"| None -> false end)")
                return _chk if raw_op == "==" else f"(not {_chk})"
        # [default] * size → Array.make size default
        if raw_op == "*" and expr["left"].get("type") == "ArrayLit":
            elts = expr["left"].get("elts", [])
            default_val = self._expr_to_whyml(elts[0], local_refs, invariant_ctx, subst) if elts else "0"
            size = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
            return f"(Array.make {size} {default_val})"
        # item34.md CF5: `[a] + [comp]` name-list concat (`[base] + [tag for … in body_raised
        # …]`) → `seq string`. Each arm is seq-ified via `_seq_operand` (an ArrayLit singleton
        # `snapshot`s; a comprehension over a seq is `list_comp_seq`), so the whole flow is
        # uniformly seq. @mutable_state; LEFT is a list literal / comprehension.
        if (raw_op == "+" and isinstance(expr.get("left"), dict)
                and expr["left"].get("type") in ("ArrayLit", "ListLit", "ListComp")
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _l = self._seq_operand(expr["left"], local_refs or set())
            _r = self._seq_operand(expr["right"], local_refs or set())
            self._add_abstract_op(
                "val array_concat (a b: seq string) : seq string\n"
                "    ensures { Seq.length result = Seq.length a + Seq.length b }")
            return f"(array_concat {_l} {_r})"
        left = self._expr_to_whyml(expr["left"], local_refs, invariant_ctx, subst)
        right = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
        # bool-as-int convention: PyCSL int-encodes bool (a `-> bool` function returns 0/1,
        # its contract reads `\result == 0 or 1`). So a Bool literal in `==`/`!=` is INT
        # equality (Python `True == 1`, `False == 0`) — emit it as 1/0 even in spec context,
        # else `\result == True` lowers to `result = true` (bool) which mismatches the int
        # `\result` ("term has type int, expected bool"). Fixes the formal-test idiom
        # `#@ ensures \result == True`.
        if raw_op in ("==", "!="):
            if expr["left"].get("type") == "Bool":
                left = "1" if expr["left"].get("value") else "0"
            if expr["right"].get("type") == "Bool":
                right = "1" if expr["right"].get("value") else "0"
        # pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): the Ellipsis
        # branch of `_py_expr_constant`, `expr.value is ...`. Module5 lowers the `...`
        # literal to `{"type":"Number","value":0}` and `ast.Is` to `==` (`_py_op_to_str`),
        # so the guard reaches here as `<pyconst_val field read> == <Number 0>`. Recognize
        # that shape -> `(is_pvellipsis expr.value)`, the faithful PVEllipsis singleton test
        # (NOT the meaningless pyconst_val=int comparison). Both arms reachable -> non-vacuous.
        # A `pyconst_val` is compared to a bare int literal ONLY in this Ellipsis check, so
        # the recognizer is unambiguous here; corpus-inert (no corpus pyconst_val).
        if raw_op in ("==", "!="):
            _pv_e = (self._pyconst_val_field_read(expr["left"])
                     or self._pyconst_val_field_read(expr["right"]))
            _num_side = (expr["right"] if self._pyconst_val_field_read(expr["left"])
                         else expr["left"])
            if (_pv_e is not None and isinstance(_num_side, dict)
                    and _num_side.get("type") == "Number" and _num_side.get("value") == 0):
                _pvs = self._expr_to_whyml(_pv_e, local_refs, invariant_ctx, subst)
                _chk = f"(is_pvellipsis {_pvs})"
                return _chk if raw_op == "==" else f"(not {_chk})"
        # typing-engagement ty1 / 25-1700-typing-spec-1 §1.2 C5: `x is None`
        # (BinOp `==`/`!=` with `None`) on a Union-typed variable lowers to a
        # constructor check against the nullary `Arm_<idx>_None` ctor, NOT `x=0`.
        if raw_op in ("==", "!=") and (
                expr["left"].get("type") == "None" or
                expr["right"].get("type") == "None"):
            # OPTIONAL-NODE / OPTIONAL-STRING CARRIER LOCAL (relaunch #11): `x is None` /
            # `x is not None` on an `iropt_ir` / `iropt_str` CARRIER local is the FAITHFUL
            # presence test — a `match` discriminant on the carrier's own absent arm, valid
            # in a program `if`. Without it the guard fell through to the "model the
            # optional as always-present" simplification below and emitted the LITERAL
            # `false` / `true` — a WRONG branch condition, not a coarse one (measured on
            # `_fstring_replacement`: `format_spec is None` became `false` and
            # `debug_text is not None` became `true`, so the model always took the
            # debug-text branch). Read the RAW deref, never the projecting value read.
            for _cset, _cnone in (("_iropt_ir_local_vars", "IrONone"),
                                  ("_iropt_str_local_vars", "IrSNone")):
                _cs = getattr(self, _cset, set())
                _cv = None
                for _side in (expr["left"], expr["right"]):
                    if (isinstance(_side, dict) and _side.get("type") == "Var"
                            and _side.get("name") in _cs):
                        _cv = _side.get("name")
                if _cv is not None:
                    _chk = (f"(match !{whyml_ident(str(_cv))} with {_cnone} -> true "
                            f"| _ -> false end)")
                    return _chk if raw_op == "==" else f"(not {_chk})"
            union_ctor = (self._union_none_ctor_for(expr["left"])
                          or self._union_none_ctor_for(expr["right"])
                          # cursor-nest `parse_atom`: same test, but on a union-returning
                          # sibling CALL used directly in the guard. See
                          # `_call_union_none_ctor` for why it lives here and not in
                          # `_union_none_ctor_for`.
                          or self._call_union_none_ctor(expr["left"])
                          or self._call_union_none_ctor(expr["right"]))
            if union_ctor is not None:
                var_side = expr["right"] if expr["left"].get("type") == "None" \
                    else expr["left"]
                var_str = self._expr_to_whyml(var_side, local_refs,
                                              invariant_ctx, subst)
                # tool-feature-5: for a MUTABLE Optional local (`x: Optional[τ] = None`,
                # a `ref _union_*`) the `is None` guard sits in a PROGRAM `if`, where
                # `(!x = Arm_i_None)` is ill-typed (Why3 has no derived `=` on the
                # algebraic type as a program bool). Emit the match-boolean discriminant
                # instead — valid in both program and logic context. Gated on the local
                # being a recognized Optional-union local, so union PARAMS (whose `is
                # None` in specs keeps the `=` form) are byte-identical.
                _vname = var_side.get("name") if isinstance(var_side, dict) else None
                if _vname in getattr(self, "_optional_union_locals", set()):
                    # The guard must inspect the RAW `ref _union_*` (`!x`), NOT the
                    # carrier-projecting read (giants read-projection) — `_expr_to_whyml`
                    # projects a union-local value read, which would strip the ctor the
                    # match discriminates on. Deref directly here.
                    _raw = f"!{whyml_ident(_vname)}"
                    chk = (f"(match {_raw} with {union_ctor} -> true "
                           f"| _ -> false end)")
                    return chk if raw_op == "==" else f"(not {chk})"
                # cursor-nest `_Parser.expect`: the SAME program-context problem the
                # `_optional_union_locals` branch above solves, one step out — a union
                # PARAM (`value: Optional[str]`) tested `is None` inside a PROGRAM `if`
                # also has no derived `=` on the algebraic type
                # (`No suitable match found for notation (=)`). The match-boolean
                # discriminant is valid in both contexts; restricted to `not self._in_spec`
                # so every SPEC-position `is None` on a union param keeps the `=` form
                # BYTE-IDENTICALLY (that is the form the comment above records as the
                # deliberate param behaviour, and it is well-typed in logic context).
                if not self._in_spec:
                    chk = (f"(match {var_str} with {union_ctor} -> true "
                           f"| _ -> false end)")
                    return chk if raw_op == "==" else f"(not {chk})"
                chk = f"({var_str} = {union_ctor})"
                return chk if raw_op == "==" else f"(not {chk})"
            # typed-ir-for-b-ceiling.md B-C2: `x is None` on an `emit_ir`-typed operand
            # (an `Optional[ExprIR]` field, e.g. `stmt.upper`) can't lower to `x = 0`
            # (emit_ir <> int). We model the optional as always-present — `is None` →
            # `false`, `is not None` → `true` — a SOUND simplification for the
            # type-safety+frame contracts we prove here (both `if` arms still type-check;
            # the arms write only locals, never self-fields, so the frame holds in both).
            # The faithful `option emit_ir` (a real `Some/None` match) is the follow-on
            # when a value-faithful `ensures` over an optional sub-node is needed. §9.
            _nn = expr["right"] if expr["left"].get("type") == "None" else expr["left"]
            # self-tcb-reduction Tier-5 (union/match cluster C5): `<local> is None` /
            # `is not None` on an OPTION-tuple local (`union_info = self._match_subject_
            # union_info(...)`, a real `option (τ...)`) is the FAITHFUL option presence
            # test — a `match … with None/Some` discriminant (valid in a program `if`,
            # unlike a derived `=` on the algebraic option). Both arms reachable (the
            # converted callee genuinely `return None`s or returns a tuple) → the guarded
            # unpack is NON-VACUOUS. Read the RAW `!x` (deref), NOT the projected read.
            if (isinstance(_nn, dict) and _nn.get("type") == "Var"
                    and _nn.get("name") in getattr(self, "_option_tuple_vars", {})):
                _ov = f"!{whyml_ident(_nn.get('name'))}"
                _chk = f"(match {_ov} with None -> true | Some _ -> false end)"
                return _chk if raw_op == "==" else f"(not {_chk})"
            # lever #1 sub-inc A cap (c): `<local> is None` / `is not None` on an
            # `option string`-returning-call local (`_rec = self._record_valued_expr_whyml_type
            # (...)`) is the FAITHFUL option presence test — a `match … None/Some` discriminant.
            # Both arms reachable (the resolver genuinely returns None or a `Some <string>`) ->
            # the guarded `return _rec` is NON-VACUOUS. Read the RAW `!x` (deref).
            if (isinstance(_nn, dict) and _nn.get("type") == "Var"
                    and _nn.get("name") in getattr(self, "_option_str_return_vars", set())):
                _ov = f"!{whyml_ident(_nn.get('name'))}"
                _chk = f"(match {_ov} with None -> true | Some _ -> false end)"
                return _chk if raw_op == "==" else f"(not {_chk})"
            # `_compute_return_type` PATH(b): `<local> is None`/`is not None` on an
            # option-of-map getter local (`_cmg = getattr(self, "_compound_map_getter",
            # None)`) is the FAITHFUL option presence test — a `match … None/Some`
            # discriminant. Both arms reachable -> the guarded `_cmg["elem_whyml"]` read is
            # NON-VACUOUS. Per-method scoped -> byte-inert elsewhere.
            if (isinstance(_nn, dict) and _nn.get("type") == "Var"
                    and _nn.get("name") in getattr(self, "_optmap_getter_locals", set())):
                _ov = f"!{whyml_ident(_nn.get('name'))}"
                _chk = f"(match {_ov} with None -> true | Some _ -> false end)"
                return _chk if raw_op == "==" else f"(not {_chk})"
            # option-of-record projection (boundary-1 G1 extension): `p is None` on an
            # `Optional[<record>]` param is the FAITHFUL option `None` test — a real
            # match, NOT the emit_ir always-present model. Both arms reachable (the
            # caller passes an arbitrary `option <record>`) → the field-reading Some arm
            # after the guard is NON-VACUOUS. Gated on `_option_record_param_classes`.
            if (isinstance(_nn, dict) and _nn.get("type") == "Var"
                    and _nn.get("name") in getattr(self, "_option_record_param_classes", {})):
                _ov = whyml_ident(_nn.get("name"))
                _chk = f"(match {_ov} with None -> true | Some _ -> false end)"
                return _chk if raw_op == "==" else f"(not {_chk})"
            # pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): a
            # `_py_expr_constant`-style `expr.value is None` value-type test — where the
            # non-None side is a `pyconst_val`-typed record-field read (`_pyconst_val_field_read`)
            # — is the FAITHFUL `is_pvnone` discriminant, NOT the emit_ir always-present model.
            # `is` lowers to `==` (Module5 `_py_op_to_str`, `ast.Is: "=="`), so `expr.value is
            # None` -> `(is_pvnone expr.value)` and `is not None` -> `(not (is_pvnone …))`.
            # Both arms reachable (a Constant's `.value` may or may not be PVNone) -> the guarded
            # branch is NON-VACUOUS. Faithful per the Phase2c_PyConstVal certificate: the
            # abstraction map sends Python `None` to PVNone and `is_pvnone` decides exactly it.
            # V1 pyconst-dispatch: the non-None side is a pyconst_val record-field read OR a
            # pyconst_val LOCAL (`v = elt.value`) — either way `v is None` is `is_pvnone v`.
            _pv_none = self._pyconst_val_field_read(_nn)
            if (_pv_none is None and isinstance(_nn, dict) and _nn.get("type") == "Var"
                    and _nn.get("name") in getattr(self, "_pyconst_val_local_vars", set())):
                _pv_none = _nn
            if _pv_none is not None:
                _pvs = self._expr_to_whyml(_pv_none, local_refs, invariant_ctx, subst)
                _chk = f"(is_pvnone {_pvs})"
                return _chk if raw_op == "==" else f"(not {_chk})"
            # SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): a bare
            # `stmt.value is not None` presence guard on an OptExprIR field (`option emit_ir`
            # — AnnAssign's optional RHS) is the FAITHFUL option `is-Some` test, NOT the
            # emit_ir always-present model below (which would collapse the guard to `true`
            # and append even for a value-less annotation `x: T`). `is` lowers to `==`
            # (Module5 `_py_op_to_str`), so `stmt.value is None` -> is-None and `is not
            # None` -> is-Some. Both arms reachable -> the guarded append is NON-VACUOUS.
            _oe_none = self._optexprir_field_read(_nn)
            if _oe_none is not None:
                _oes = self._expr_to_whyml(_oe_none, local_refs, invariant_ctx, subst)
                _chk = f"(match {_oes} with None -> true | Some _ -> false end)"
                return _chk if raw_op == "==" else f"(not {_chk})"
            # self-tcb-reduction Layer-2: inside the receiver/slice recognizer, an emit_ir
            # `is None` / `is not None` is a FAITHFUL IrSliceN optional-bound presence test,
            # NOT the always-present model below — `lower_of`/`upper_of`/`step_of` read back
            # the honest `IrNone` for an ABSENT bound, so `lower is None` -> `(<e> = IrNone)`
            # and `step is not None` -> `(<e> <> IrNone)`, both REACHABLE (a bound may be
            # present or absent) so the tuple-return path is LIVE (non-vacuous). Emitted as a
            # match-based discriminant (Why3 has no derived program `=` on the ADT). SCOPED
            # via `_current_emitting_func` so every other emit_ir `is None` (the always-present
            # model at the tail) stays byte-identical.
            _cef_none = getattr(self, "_current_emitting_func", None) or ""
            if (self._is_emit_ir_expr(_nn)
                    and any(_cef_none == _h or _cef_none.endswith("__" + _h)
                            for _h in _EMIT_IR_EXTRA_NODE_KEYS_BY_FUNC)):
                _es = self._expr_to_whyml(_nn, local_refs, invariant_ctx, subst)
                _chk = f"(match {_es} with IrNone -> true | _ -> false end)"
                return _chk if raw_op == "==" else f"(not {_chk})"
            if self._is_emit_ir_expr(_nn):
                return "false" if raw_op == "==" else "true"
            # cf6.md M1.6: `<tuple-local> is None` — a tuple value (`union_info =
            # self._match_subject_union_info(…)`) is always present in this model, so `is None`
            # → false / `is not None` → true (sound always-present; both `if` arms type-check).
            if (isinstance(_nn, dict) and _nn.get("type") == "Var"
                    and _nn.get("name") in getattr(self, "_ghost_tuple_vars", {})):
                return "false" if raw_op == "==" else "true"
            # i-feel-good.md I-B: `x is None`/`is not None` on a string-typed operand — an
            # `Optional[str]` local (the emitter's `self_field_name = None; … = <str>`).
            # Same sound always-present model (empty-string "" is the absent sentinel; both
            # `if` arms type-check). @mutable_state-gated → byte-identical elsewhere.
            if (self._is_string_expr(_nn)
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())):
                return "false" if raw_op == "==" else "true"
        op = op_translate(raw_op)
        # no-more-int Stage D: float arithmetic/comparison is over Why3 `real` (RealInfix
        # `+.`/`-.`/`*.`/`/.`/`<.`/…), not int. Both operands must be float; a mixed float/int
        # binop is out of scope (documented). Arithmetic in a body bridges through an abstract
        # `val` (the real ops are logic symbols); comparisons return bool and emit directly.
        _lf = self._is_float_expr(expr["left"])
        _rf = self._is_float_expr(expr["right"])
        if _lf or _rf:
            _FARITH = {"+": ("+.", "add"), "-": ("-.", "sub"),
                       "*": ("*.", "mul"), "/": ("/.", "div")}
            if raw_op in _FARITH and _lf and _rf:  # arithmetic: both operands float
                rop, nm = _FARITH[raw_op]
                if self._in_spec:
                    return f"({left} {rop} {right})"
                self._add_abstract_op(
                    f"val float_{nm}_op (a b: real) : real\n"
                    f"    ensures {{ result = (a {rop} b) }}")
                return f"(float_{nm}_op {left} {right})"
            # comparison/equality: either operand float (the other is `\result` or a real)
            _FCMP = {"<": "<.", "<=": "<=.", ">": ">.", ">=": ">=."}
            if raw_op in _FCMP:
                return f"({left} {_FCMP[raw_op]} {right})"
            if raw_op in ("==", "!="):
                eq = f"({left} = {right})"
                return eq if raw_op == "==" else f"(not {eq})"
        # G2 strings: lexicographic comparison `< <= > >=` on two strings. Why3's
        # `string.String` exposes the *predicates* `String.lt`/`String.le` (lexicographic
        # order). `s < t` → `str_lt_op s t` (a `val:bool` bridge tied by `ensures` to
        # `String.lt`); `s <= t` → `str_le_op`. `>`/`>=` reflect by swapping operands
        # (`s > t` ⇔ `t < s`, `s >= t` ⇔ `t <= s`). Like the Python comparison protocol the
        # body returns an int (the bool→int `if … then 1 else 0` of the float-compare path).
        # Both operands must be string-typed; a mixed str/int compare is out of scope here.
        if raw_op in ("<", "<=", ">", ">=") \
                and self._is_string_expr(expr["left"]) \
                and self._is_string_expr(expr["right"]):
            self._add_abstract_op(
                "val str_lt_op (a: string) (b: string) : bool\n"
                "    ensures { result <-> String.lt a b }")
            self._add_abstract_op(
                "val str_le_op (a: string) (b: string) : bool\n"
                "    ensures { result <-> String.le a b }")
            if raw_op == "<":
                cmp = f"(str_lt_op {left} {right})"
            elif raw_op == "<=":
                cmp = f"(str_le_op {left} {right})"
            elif raw_op == ">":
                cmp = f"(str_lt_op {right} {left})"
            else:  # ">="
                cmp = f"(str_le_op {right} {left})"
            if self._in_spec:
                return cmp
            return f"(if {cmp} then 1 else 0)"
        # G2 strings: repetition `s * n` / `n * s` on a string + int. The repeated string's
        # length is `n * String.length s` (canonicalize string-first regardless of operand
        # order — multiplication is commutative on the int factor). Bridged through a `val`
        # whose `ensures` pins only the length (the content is an opaque function of s, n).
        if raw_op == "*" and (
                (self._is_string_expr(expr["left"]) and not self._is_string_expr(expr["right"]))
                or (self._is_string_expr(expr["right"]) and not self._is_string_expr(expr["left"]))):
            if self._is_string_expr(expr["left"]):
                sstr, nstr = left, right
            else:
                sstr, nstr = right, left
            self._add_abstract_op(
                "val str_repeat_op (s: string) (n: int) : string\n"
                "    requires { n >= 0 }\n"
                "    ensures { String.length result = n * String.length s }")
            return f"(str_repeat_op {sstr} {nstr})"
        # G2 strings: `%`-formatting `s % x` produces SOME string — its content is NOT
        # modeled (faithful boundary). An honest abstract `val` pins only `length >= 0` (a
        # sound over-approximation), never the int `pycsl_mod`. Fires only for a string LHS.
        if raw_op == "%" and self._is_string_expr(expr["left"]):
            self._add_abstract_op(
                "val str_mod_op (s: string) (x: 'a) : string\n"
                "    ensures { String.length result >= 0 }")
            return f"(str_mod_op {left} {right})"
        # strings-plan Stage 2: `s + t` on strings is concatenation, not int addition. The
        # logic symbol `concat` is fine in a spec; in a program (body) context it is bridged
        # through an abstract `val` whose `ensures` ties the result to `concat` (same pattern
        # as `len`/`str_length_op`).
        # Both operands must be string-typed: `str + int` is not valid Python concatenation, so
        # a mixed `+` is left as int addition (legacy hash model).
        if raw_op == "+" and self._is_string_expr(expr["left"]) \
                and self._is_string_expr(expr["right"]):
            if self._in_spec:
                return f"(concat {left} {right})"
            self._add_abstract_op(
                "val str_concat_op (a: string) (b: string) : string\n"
                "    ensures { result = (concat a b) }\n"
                "    ensures { String.length result = String.length a + String.length b }")
            return f"(str_concat_op {left} {right})"
        # strings-plan Stage 2: string `==`/`!=` content equality. In a spec, polymorphic `=`
        # is fine (falls through below); in a program (body) context `=` on strings is not
        # usable, so bridge through `val str_eq_op : bool` (tied by `ensures` to `=`). Must
        # precede the int-coercion of `=`/`<>` below, which is only for the int-hash model.
        if raw_op in ("==", "!=") and not self._in_spec:
            # no-more-int leak fix: `sym == "str"` where `sym` is an `Optional[str]` PARAM
            # (a `_union_*` with a single `str` Some-arm) compared to a String literal must
            # option-unwrap the union — an int-hash of the literal against the raw union is
            # a union-vs-int type error. Emit
            # `(match sym with Arm_i_0 s -> str_eq_op s "str" | _ -> false)`. Gated on the
            # OTHER side being a String literal → corpus-inert.
            _lu = self._optional_str_union_ctor(expr.get("left"))
            _ru = self._optional_str_union_ctor(expr.get("right"))
            if _lu and expr.get("right", {}).get("type") == "String":
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _inner = f"(match {left} with {_lu} _s -> (str_eq_op _s {right}) | _ -> false end)"
                return _inner if raw_op == "==" else f"(not {_inner})"
            if _ru and expr.get("left", {}).get("type") == "String":
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _inner = f"(match {right} with {_ru} _s -> (str_eq_op _s {left}) | _ -> false end)"
                return _inner if raw_op == "==" else f"(not {_inner})"
            # cursor-nest `_Parser.expect`: the SAME faithful unwrap, widened from a String
            # LITERAL on the other side to any STRING-VALUED EXPRESSION (`t.value != value`,
            # where `t.value` is a union-local carrier projection and `value` is the
            # `Optional[str]` param). Without it the string side is `str_hash_op`-coerced
            # into the int model and compared to the raw union — the measured L3-tc error
            # `This expression has type _union_expect_1, but is expected to have type int`.
            #
            # The None arm is the FAITHFUL Python answer, not a convenience default:
            # `<str> == None` is False and `<str> != None` is True, which is exactly
            # `| _ -> false` under `==` and its negation under `!=`. So the lowering is
            # total and correct even where the caller has NOT narrowed — which matters
            # here, because the live guard narrows through a short-circuit `and`
            # (`value is not None and t.value != value`) that the C8 walk does not
            # recognize as a narrowing site.
            #
            # Placed AFTER the two literal branches, so every existing String-literal call
            # site keeps its byte-identical lowering; and requires the union side to be
            # unambiguous (`not _lu` / `not _ru`), so a union-vs-union compare still falls
            # through to the pre-existing path.
            if _lu and not _ru and self._is_string_expr(expr.get("right") or {}):
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _inner = f"(match {left} with {_lu} _s -> (str_eq_op _s {right}) | _ -> false end)"
                return _inner if raw_op == "==" else f"(not {_inner})"
            if _ru and not _lu and self._is_string_expr(expr.get("left") or {}):
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _inner = f"(match {right} with {_ru} _s -> (str_eq_op _s {left}) | _ -> false end)"
                return _inner if raw_op == "==" else f"(not {_inner})"
            # self-tcb-reduction Tier-5 (union/match cluster sub-increment 2): `ctor.get(
            # "arity") == 0` — exactly one operand is a pyval `.get` (an `hval`) and the
            # other is int-valued (not a String). Project the hval's int carrier via
            # `hint_of` and compare as ints. MUST precede the `_is_string_expr`
            # classification below, which defaults a pyval `.get` to `string` and would
            # wrongly `str_hash_op` the int field (the `str_hash_op ... : int` shape). Gated
            # on `_expr_is_pyval` (only the union/match hval files) + a non-string other side
            # -> corpus byte-inert.
            _lpv = self._expr_is_pyval(expr.get("left") or {})
            _rpv = self._expr_is_pyval(expr.get("right") or {})
            if _lpv != _rpv:
                _other = expr.get("right") if _lpv else expr.get("left")
                if not self._is_string_expr(_other if isinstance(_other, dict) else {}):
                    _pvw = left if _lpv else right
                    _otw = right if _lpv else left
                    eq = f"(hint_of {_pvw} = {_otw})"
                    return eq if raw_op == "==" else f"(not {eq})"
                # self-tcb-reduction `_compute_return_type` PATH(b): a pyval `.get` operand
                # (`func.get("return_value_type")` / `func.get("name")`) compared to a STRING
                # literal — project the hval's string carrier via `hstr_of` and compare as
                # strings (the faithful op, not the int-hash `= <hash>` facade). Gated on the
                # `_compute_return_type` file -> byte-inert for the corpus (no pyval operand)
                # and every other mirror.
                elif self._uses_compute_return_type():
                    self._add_abstract_op(
                        "val str_eq_op (a: string) (b: string) : bool\n"
                        "    ensures { result <-> (a = b) }")
                    _pvw = f"(hstr_of {left if _lpv else right})"
                    _otw = right if _lpv else left
                    eq = f"(str_eq_op {_pvw} {_otw})"
                    return eq if raw_op == "==" else f"(not {eq})"
            ls = self._is_string_expr(expr["left"])
            rs = self._is_string_expr(expr["right"])
            if ls and rs:
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                # hval-retype (self-tcb-reduction Tier-5): a pyval `.get` operand
                # (`info.get("whyml_name")`) is an `hval`, not a `string` — project its
                # string carrier via `hstr_of` before `str_eq_op` (which is string-typed).
                # Descends the real hval (non-vacuous). Gated on `_expr_is_pyval` -> inert.
                _leftw = (f"(hstr_of {left})"
                          if self._expr_is_pyval(expr["left"]) else left)
                _rightw = (f"(hstr_of {right})"
                           if self._expr_is_pyval(expr["right"]) else right)
                eq = f"(str_eq_op {_leftw} {_rightw})"
                return eq if raw_op == "==" else f"(not {eq})"
            if ls != rs:
                # Mixed string/int: a string compared against a genuine int (e.g. an opaque
                # decode result). Revert to legacy opaque int-equality by hashing the string
                # side, then fall through to the int `=`/`<>` path below.
                if ls:
                    left = self._str_operand_to_int(left)
                else:
                    right = self._str_operand_to_int(right)
        # In body context, coerce string literals in comparisons to int
        if not self._in_spec and op in ("=", "<>"):
            left = self._coerce_str_arg(left)
            right = self._coerce_str_arg(right)
        if op == "div":
            if raw_op == "/":
                # WL-02: Python `/` is TRUE division — it ALWAYS returns a float
                # (`5 / 2 == 2.5`, even for int operands). Lower to a REAL division:
                # lift both int operands via `from_int` and divide over the reals
                # (`/.`). The result is a `real`. A `/` result consumed at `int` type
                # fail-closes as a real-vs-int type error (never a silent integer
                # truncation) — consistent with the int/float-mixing boundary. Only
                # FLOOR division `//` (raw_op "div") stays integer below (WL-01).
                # (Both-float `/` was already handled by the float block above.)
                if self._in_spec:
                    return f"(from_int {left} /. from_int {right})"
                # Body: `from_int` is a logic symbol (unusable in a program/non-ghost
                # term), so the int→real lift AND the division are bundled into one
                # abstract `val` whose `ensures` pins the exact real value. The int
                # operands stay int program terms; `from_int`/`/.` live only in the
                # logical `ensures`.
                self._add_abstract_op(
                    "val float_truediv_op (a b: int) : real\n"
                    "    ensures { result = (from_int a /. from_int b) }")
                return f"(float_truediv_op {left} {right})"
            if self._in_spec:
                # WL-01: Python `//` is FLOORED division. Emit the sign-of-divisor
                # correction inline over the always-in-scope Euclidean `div`/`mod`
                # (bind operands once to avoid duplicating side-effect-free terms).
                return (f"(let __fd = {left} in let __fr = {right} in "
                        f"if mod __fd __fr <> 0 && __fr < 0 then div __fd __fr - 1 "
                        f"else div __fd __fr)")
            inner = f"(pycsl_div {left} {right})"
            return self._wrap_with_no_exception_assert(("binop", raw_op), [left, right], inner)
        if op == "mod":
            if self._in_spec:
                # WL-01: Python `%` has the sign of the DIVISOR (floored modulo).
                return (f"(let __fd = {left} in let __fr = {right} in "
                        f"if mod __fd __fr <> 0 && __fr < 0 then mod __fd __fr + __fr "
                        f"else mod __fd __fr)")
            inner = f"(pycsl_mod {left} {right})"
            return self._wrap_with_no_exception_assert(("binop", raw_op), [left, right], inner)
        if op in ("&&", "||"):
            # cf6.md M1.6: `<array> or []` (`pat.get("captures", []) or []`) is the redundant
            # empty-list default — the value IS the left array (`args_of pat`). @mutable_state.
            _rr = expr.get("right", {})
            if (op == "||" and not self._in_spec
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())
                    and isinstance(_rr, dict)
                    and _rr.get("type") in ("ListLit", "ListLiteral", "ArrayLit", "List")
                    and not (_rr.get("elements") or _rr.get("elts") or _rr.get("values"))
                    and left.startswith("(args_of ")):
                return left
            # item34.md CF5: Python `<str> or <str>` (`h.get("exc_type") or "PyCSL_Exception"`)
            # returns the FIRST truthy STRING — `if not (str_eq_op a "") then a else b`. Both
            # operands string-typed, not in spec. @mutable_state.
            # resync-campaign.md R2: the right arm may be `None` (`(…).lower() or None`) → "".
            _r_none = isinstance(expr.get("right"), dict) and expr["right"].get("type") == "None"
            if (op == "||" and not self._in_spec
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())
                    and self._is_string_expr(expr["left"])
                    and (self._is_string_expr(expr["right"]) or _r_none)):
                self._add_abstract_op(
                    "val str_eq_op (a b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _rv = '""' if _r_none else right
                return f'(if (not (str_eq_op {left} "")) then {left} else {_rv})'
            # string-bool-op: BOTH operands `string`-typed => faithful string ITE over
            # EMPTINESS (Python string truthiness is non-emptiness). `s or t` returns the
            # first operand when non-empty else the second; `s and t` returns the second
            # when the first is non-empty else the first. The result is itself `string`-
            # typed; used where a bool/int is expected it fails closed at Why3 type-check
            # (WL-02 — never a silent coercion). BODY only; in spec context `and`/`or`
            # remain the boolean &&/|| connectives (unchanged below). NOT @mutable_state-
            # gated: unblocks self-tcb free functions (`safe_exc_name`'s `… or name`).
            # Bool/int operands fall through UNCHANGED to the &&/|| path below (additivity).
            if (not self._in_spec
                    and self._is_string_expr(expr["left"])
                    and self._is_string_expr(expr["right"])):
                # `String.length` is a LOGIC symbol (illegal in a program body); bridge
                # emptiness through the `str_length_op` val (ensures = String.length).
                self._add_abstract_op(
                    "val str_length_op (s: string) : int\n"
                    "    ensures { result = (String.length s) }")
                if op == "||":
                    return (f"(if str_length_op {left} > 0 "
                            f"then {left} else {right})")
                return (f"(if str_length_op {left} > 0 "
                        f"then {right} else {left})")
            # Lever 6: value-preserving short-circuit `or`/`and` over STRUCTURED
            # (emit_ir) operands. Python `A or B` returns the SELECTED operand (A if A
            # is truthy, else B) — an emit_ir value — NOT the int-truthiness collapse
            # `if (A<>0)||(B<>0) then 1 else 0` (which type-fails an emit_ir callee).
            # This unblocks a verified caller passing `<emit_ir> or <emit_ir>` to a
            # callee that requires an emit_ir param (`_try_local_decl_kind` fed by
            # `_first_assign_value_ir(...) or _first_assign_value_ir(...)`). Truthiness
            # is FAITHFUL Python dict-truthiness: a dict is truthy iff non-empty, and
            # every real Module-5 IR node carries a non-empty `type` string while the
            # live falsy sentinel `{}` is the kind-less node — so `truthy e` ==
            # `kind_of e <> ""`. BODY context only (in spec, `and`/`or` stay the
            # boolean connectives below). Gated on BOTH operands being emit_ir; the
            # corpus has no emit_ir operand to an `and`/`or`, so int `or`/`and` output
            # is byte-identical (this branch never fires on corpus code). Uses the
            # existing `kind_of` (a definitional `let function`, both program+logic) and
            # the `str_eq_op` bridge (decidable string `=` for the program `if`); no new
            # ADT, no new axiom.
            if (not self._in_spec
                    and self._is_emit_ir_expr(expr["left"])
                    and self._is_emit_ir_expr(expr["right"])):
                self._add_abstract_op(
                    "val str_eq_op (a b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                if op == "||":
                    # `A or B`: A when A is truthy (present), else B.
                    return (f"(let __or_l = {left} in "
                            f'if (not (str_eq_op (kind_of __or_l) "")) '
                            f"then __or_l else {right})")
                # `A and B`: B when A is truthy (present), else A.
                return (f"(let __and_l = {left} in "
                        f'if (not (str_eq_op (kind_of __and_l) "")) '
                        f"then {right} else __and_l)")
            left_b = self._to_bool(left, expr["left"])
            right_b = self._to_bool(right, expr["right"])
            if self._in_spec:
                return f"({left_b} {op} {right_b})"
            # In body context, Python's and/or return int. Use if-then-else
            # to convert bool result back to int, avoiding abstract vals
            # that can't handle mixed bool/int args.
            return f"(if {left_b} {op} {right_b} then 1 else 0)"
        if raw_op in ("in", "not in"):
            return self._emit_membership(raw_op, expr, left, right, local_refs,
                                          invariant_ctx, subst)
        # item34.md CF4: `<set> | {x}` (set union with a set literal, e.g. the for-loop's
        # `local_refs | {target}`) is a set UNION — add each element to the map — not the int
        # `bit_or`. @mutable_state; the string key is `str_hash_op`-hashed (matching M.7).
        if (raw_op == "|"
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _rset = expr.get("right", {})
            if isinstance(_rset, dict) and _rset.get("type") in ("SetLit", "Set"):
                self._add_abstract_op(
                    "val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) "
                    ": map 'k (option 'v)\n"
                    "    ensures { result = Map.set m k (Some v) }")
                # r1-setop I2 (self-tcb-reduction): if the LEFT set operand is a κ=string
                # dict/set FIELD (`self.<f>`/`<rec>.<f>`) it lowers to a
                # `map string (option int)` (field_key_types) — so the union must write the
                # RAW native string element (no `str_hash_op`), matching that field's
                # `.add`/membership (a mismatch is a WhyML type error, as `str_hash_op x : int`
                # can't index a `map string`). A Var operand (a method set param/local, `map
                # int`) keeps `str_hash_op` → byte-identical for every non-string-field union
                # (the mirror's `local_refs | {target}` / `declared_refs.copy() | {target}`).
                _lstrfield = self._set_union_left_is_strfield(expr.get("left"))
                _acc = left
                for _e in _rset.get("elts", []):
                    _ew = self._expr_to_whyml(_e, local_refs, invariant_ctx, subst)
                    if _lstrfield and self._is_string_expr(_e):
                        _key = _ew
                    elif self._is_string_expr(_e):
                        self._add_abstract_op("val str_hash_op (s: string) : int")
                        _key = f"(str_hash_op {_ew})"
                    else:
                        _key = self._coerce_to_int(_ew)
                    _acc = f"(map_update_some {_acc} {_key} 0)"
                return _acc
        if raw_op in self._BITWISE_FN_NAMES:
            return self._emit_bitwise_or_power(raw_op, expr, left, right)
        if raw_op == "?":
            self._add_abstract_op("val unknown_op (x: int) (y: int) : int")
            return f"(unknown_op {left} {right})"
        return f"({left} {op} {right})"

    def _iter_len_expr(self, ir: Dict[str, Any], local_refs: Set[str]) -> Optional[str]:
        """A3 (bounded eager itertools): the WhyML length of an itertools/list
        expression, or None if not recognized. `len(list(X)) == len(X)` and
        `len(chain(x0, …, xk)) == Σ len(xi)` — a chain materializes to the
        concatenation, whose length is the sum of its operands' lengths (a
        bounded, sound model: lazy/infinite iterables are out of scope). Each
        operand's length is `Array.length` (or, recursively, another chain/list)."""
        if not isinstance(ir, dict) or ir.get("type") != "Call":
            return None
        fn = ir.get("func", "")
        fn_short = fn.rsplit(".", 1)[-1] if isinstance(fn, str) else ""
        args_ir = ir.get("args", [])
        if fn_short == "list" and len(args_ir) == 1:
            inner = self._iter_len_expr(args_ir[0], local_refs)
            if inner is not None:
                return inner
            return f"(Array.length {self._expr_to_whyml(args_ir[0], local_refs)})"
        def _operand_len(sub):
            p = self._iter_len_expr(sub, local_refs)
            return p if p is not None else f"(Array.length {self._expr_to_whyml(sub, local_refs)})"
        if fn_short == "chain":
            if not args_ir:
                return "0"
            return "(" + " + ".join(_operand_len(s) for s in args_ir) + ")"
        # A3-residual: `len(product(a, b, …)) == ∏ len`; `len(islice(it, n)) ==
        # min(len(it), n)` (inline min — no MinMax import). Bounded/eager only.
        if fn_short == "product":
            if not args_ir:
                return "1"   # empty product → the single empty tuple
            return "(" + " * ".join(_operand_len(s) for s in args_ir) + ")"
        if fn_short == "islice" and len(args_ir) == 2:
            it = _operand_len(args_ir[0])
            stop = self._expr_to_whyml(args_ir[1], local_refs)
            return f"(if {it} < {stop} then {it} else {stop})"
        return None

    def _handle_len_call(self, expr: Dict[str, Any], args: List[str]) -> str:
        """Handle len(x): constant fold literals, array length in hoare model, or abstract.
        (The `len(list(chain(…)))` itertools case is resolved earlier in
        `_handle_call_expr` via `_iter_len_expr`, before the inner args are lowered.)"""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        atype = arg_ir.get("type", "")
        # cap4/5 (self-tcb-reduction `_refine_tuple_return_type`): `len(slots)` / `len(_s)`
        # over a `seq string` refine list-comp local is `Seq.length`. Method-gated -> inert.
        if (atype == "Var" and arg_ir.get("name")
                in getattr(self, "_refine_str_comp_locals", set())):
            return f"(Seq.length {args[0]})"
        # nested-list-mutable.md: a matrix-routed (in-place inner-mutated int-leaf)
        # nested list `a` is a built-in `matrix int`. `len(a)` = `a.rows` (outer row
        # count); `len(a[i])` = `a.columns` (the rectangular per-row length). Emit the
        # Matrix record projections directly from the base name — the lowered `args[0]`
        # for `a[i]` is a matrix (rows aren't first-class), so it is NOT used here.
        # W8/W1: `len(self.<f>)` where `<f>` is an `array <record>` self-field (the
        # token cursor's `len(self.toks)`) is the ARRAY length — the opaque
        # `iter_length : int -> int` fallback mistypes against `array <record>`.
        # `_record_array_fields` is populated only for a `List[<record>]` record field
        # (@mutable_state / IR-node gated) → absent elsewhere, byte-inert.
        _raf = getattr(self, "_record_array_fields", None)
        if _raf and atype in ("FieldGet", "Attribute"):
            _fn = arg_ir.get("field") or arg_ir.get("attr")
            _ob = arg_ir.get("object")
            if isinstance(_ob, dict):
                _ob = _ob.get("name")
            if _fn in _raf and _ob == "self":
                return f"(Array.length {args[0]})"
        _a2d = getattr(self, "_array2d_params", set())
        if atype == "Var" and arg_ir.get("name") in _a2d:
            return f"({arg_ir['name']}.rows)"
        if atype == "Subscript":
            _mb = arg_ir.get("value", {})
            if (isinstance(_mb, dict) and _mb.get("type") == "Var"
                    and _mb.get("name") in _a2d):
                return f"({_mb['name']}.columns)"
        # W8 capability (ii): `len(vals)` on the `*vals: str` vararg param is the
        # length of the `seq string` argument sequence — `Seq.length`, not the opaque
        # `iter_length : int -> int` (which would also mistype). Gated on
        # `_vararg_str_param`.
        if (atype == "Var" and arg_ir.get("name")
                and arg_ir.get("name") == getattr(self, "_vararg_str_param", None)):
            return f"(Seq.length {whyml_ident(arg_ir['name'])})"
        # self-tcb-reduction _namedtuple_positional_access: `len(fields)` where `fields` is a
        # pyval-local hval COLLECTION (`fields = rec_info["fields"]`, an HArr) is the
        # hval-list length (`hval_len`), NOT the opaque `iter_length : int -> int` (which
        # mistypes against hval). Gated on `_pyval_locals` -> corpus/mirror byte-inert.
        if (atype == "Var" and arg_ir.get("name")
                and arg_ir.get("name") in getattr(self, "_pyval_locals", set())):
            return f"(hval_len {whyml_ident(arg_ir['name'])})"
        # §B′: len(d[k]) where d is a seq-valued dict (`Dict[_, List[int]]`) — the
        # read is a `seq int`, so its length is `Seq.length`.
        if atype == "Subscript":
            _b = arg_ir.get("value", {})
            if (isinstance(_b, dict) and _b.get("type") == "Var"
                    and getattr(self, "_dict_value_types", {}).get(_b.get("name", "")) == "seq int"):
                return f"(Seq.length {args[0]})"
            # nested-list.md S5: `len(a[i])` where `a` is a `List[List[τ]]` param
            # (`array (seq τ)`) — the inner read is a `seq τ`, so its length is
            # `Seq.length`, not the opaque `iter_length`. `args[0]` already carries
            # the lowered `a[i]` (`let _row = a[i] in Seq.get ..` NOT produced for a
            # bare inner read — the len arg is the inner Subscript `a[i]`, which
            # lowers to a plain `a[i]` Array.get). A `map`-element inner would need
            # a cardinality op (out of scope) → stays `iter_length`.
            if (isinstance(_b, dict) and _b.get("type") == "Var"
                    and getattr(self, "_list_nested_elem", {}).get(
                        _b.get("name", ""), "").startswith("seq ")):
                return f"(Seq.length {args[0]})"
            # nested-list §8 EXTENSION: `len(a[i][j])` (deeper than 2) — the inner
            # read `a[i][j]` is a `seq τ` (one level above the leaf), so its length
            # is `Seq.length`. Uses the recursive access-type (peel one container
            # per index level); byte-identical to the depth-2 branch above for the
            # `len(a[i])` case (both return `(Seq.length args[0])`), so only the
            # deeper chains are newly handled.
            _at = self._nested_access_type(arg_ir)
            if _at is not None and _at.startswith("seq "):
                return f"(Seq.length {args[0]})"
        # 07-1705-rev4 P3: len() of a seq-modelled (growable) list local is `Seq.length`.
        # A seq-promoted PARAM in a CONTRACT refers to its array entry value (so fall through
        # to Array.length there — the `not _in_spec` guard); but a seq-promoted LOCAL is always
        # a seq, including in loop invariants (return-arr.md follow-on: else `len(names_out) <= i`
        # in listdir's invariant wrongly resolves to the non-existent array counter `!X_len`).
        if atype == "Var" and arg_ir.get("name") in getattr(self, "_seq_locals", set()):
            _is_param = arg_ir.get("name") in set(getattr(self, "_formal_params", []))
            if not (_is_param and self._in_spec):
                return f"(Seq.length {args[0]})"
        if atype == "String" and isinstance(arg_ir.get("value"), str):
            return str(len(arg_ir["value"]))
        if atype == "Tuple":
            return str(len(arg_ir.get("elts", [])))
        if atype in ("ArrayLit", "SetLit"):
            return str(len(arg_ir.get("elts", [])))
        if atype == "DictLit":
            return str(len(arg_ir.get("keys", [])))
        if atype == "Var":
            vname = arg_ir.get("name", "")
            known = getattr(self, "_known_collection_sizes", {})
            # Don't constant-fold against the INITIAL size if the
            # variable is an append-target — its length grows at
            # runtime, so the static fold is unsound in invariants
            # (`len(entries) <= i` collapses to `0 <= i`).
            append_targets = getattr(self, "_current_append_targets", set())
            if vname in known and vname not in append_targets:
                return str(known[vname])
            if vname in append_targets:
                # Append-target len is tracked in a sidecar ref `X_len`.
                return f"!{vname}_len"
        if self._is_string_expr(arg_ir):
            # strings-plan: len() on ANY runtime-str expression (a str var, a concat
            # `s + t`, a slice `s[a:b]`, an index `s[i]`) is the Why3 string length —
            # not just a bare str var. In a spec the logic symbol `String.length` is used
            # directly; in a program (body) context that logic symbol is not allowed, so
            # bridge it through an abstract `val` whose `ensures` ties the program result
            # to `String.length` (and `args[0]` is the already-lowered string expression).
            if self._in_spec:
                return f"(String.length {args[0]})"
            self._add_abstract_op(
                "val str_length_op (s: string) : int\n"
                "    ensures { result = (String.length s) }")
            return f"(str_length_op {args[0]})"
        if self._value_semantic:
            var_name = arg_ir.get("name", "") if atype == "Var" else ""
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_inline_array_temps", set()) or
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict and var_name:
                # WL-06: bytes/bytearray are the τ-blessed `array int`-backed byte
                # buffer, so `len(b)` is `Array.length b` (the buffer length),
                # consistent with routing `b[i]` to `Array.get`. Otherwise a bounds
                # `requires i < len(b)` emitted the unbound `iter_length` stub.
                if (getattr(self, "_current_symbol_table", {}).get(var_name)
                        in ("list", "dict", "bytes", "bytearray")):
                    is_array = True
            if is_array:
                arg0 = f"({args[0]})" if args[0].startswith("!") else args[0]
                return f"(Array.length {arg0})"
            self._add_abstract_op("val iter_length (x: int) : int")
            return f"(iter_length {args[0]})"
        return f"{args[0].lstrip('!')}_len"

    def _handle_join_call(self, expr: Dict[str, Any], args: List[str],
                          local_refs=None, invariant_ctx=False, subst=None) -> str:
        """Handle str.join(iterable): pick join_array for arrays, join_1 otherwise."""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        # self-tcb-reduction WRITER class (`_build_param_list`): `" ".join(
        # self._param_type_str(arg, …) for arg in args)` — a join over a GENERATOR mapping a
        # string call over the `seq string` `args` local. The mapped sequence is a
        # `seq string` (length-only over-approx over the real `args` source, content
        # unmodeled — same faithful abstraction as the list-comp path), joined by
        # `str_join_seq`. Gated on the method -> corpus/other-mirror byte-inert.
        if (self._emitting_build_param_list()
                and arg_ir.get("type") in ("GenExp", "GeneratorExp", "ListComp")):
            _sepg = (self._expr_to_whyml(expr.get("receiver"), local_refs or set(),
                                         invariant_ctx, subst)
                     if expr.get("receiver") is not None else '" "')
            _ggens = arg_ir.get("generators", []) or []
            _gsrc = _ggens[0].get("iter", {}) if _ggens else {}
            _gsrcw = self._expr_to_whyml(
                _gsrc if isinstance(_gsrc, dict) else {}, local_refs or set(),
                invariant_ctx, subst)
            self._add_abstract_op(
                "val list_comp_refine_string (src: 'a) : seq string")
            self._add_abstract_op(
                "val str_join_seq (sep: string) (xs: seq string) : string\n"
                "    ensures { String.length result >= 0 }")
            return f"(str_join_seq {_sepg} (list_comp_refine_string {_gsrcw}))"
        # cap4/5 (self-tcb-reduction `_refine_tuple_return_type`): `", ".join(slots)` /
        # `", ".join(_s)` over a `seq string` refine list-comp local is `str_join_seq` (a
        # `string`). Method-gated -> corpus/other-mirror byte-inert.
        if (arg_ir.get("type") == "Var" and arg_ir.get("name")
                in getattr(self, "_refine_str_comp_locals", set())):
            _sepj = (self._expr_to_whyml(expr.get("receiver"), local_refs or set(),
                                         invariant_ctx, subst)
                     if expr.get("receiver") is not None else '" "')
            self._add_abstract_op(
                "val str_join_seq (sep: string) (xs: seq string) : string\n"
                "    ensures { String.length result >= 0 }")
            return f"(str_join_seq {_sepj} {args[0]})"
        # faithful-string-op.md §3.5: a LITERAL list/tuple of STRINGS joined by `sep`
        # lowers to nested `str_concat_op` (EXACT and faithful: `e0 ++ sep ++ e1 ++ …`),
        # not the opaque int `join_array`. `sep` is `expr['receiver']` (join reaches here
        # in the receiver form). A general/computed iterable stays on the int join below
        # (its faithful `string` model needs a `seq string` element model — deferred).
        _recv = expr.get("receiver")
        _at = arg_ir.get("type", "")
        if _recv is not None and _at in ("ArrayLit", "ListLit", "Tuple"):
            _elts = arg_ir.get("elts", [])
            if _elts and all(self._is_string_expr(e) for e in _elts):
                self._add_abstract_op(
                    "val str_concat_op (a: string) (b: string) : string\n"
                    "    ensures { result = (concat a b) }\n"
                    "    ensures { String.length result = String.length a"
                    " + String.length b }")
                _lr = local_refs or set()
                _sep = self._expr_to_whyml(_recv, _lr, invariant_ctx, subst)
                _ew = [self._expr_to_whyml(e, _lr, invariant_ctx, subst) for e in _elts]
                _acc = _ew[-1]
                for _k in range(len(_ew) - 2, -1, -1):
                    _acc = f"(str_concat_op {_ew[_k]} (str_concat_op {_sep} {_acc}))"
                return _acc
        # list-comprehension-lowering.md L2: a STRING-element array (a comprehension-bound
        # local like `tmp_names`, a `List[str]` field, a repeat/literal) joins to a `string`
        # — regardless of whether it is tracked as an `_array_locals` entry. Fires before the
        # int `is_array` path below. @mutable_state (the elem-type map is empty elsewhere).
        if self._join_arg_elem_is_string(arg_ir):
            _sep2 = (self._expr_to_whyml(_recv, local_refs or set(), invariant_ctx, subst)
                     if _recv is not None else '" "')
            # A seq-promoted (`.append`-grown) string list is a `seq string`, not `array
            # string` — use the seq-join variant (`lines = [f"…"]; lines.append(…)`).
            if (arg_ir.get("type") == "Var"
                    and arg_ir.get("name") in getattr(self, "_seq_locals", set())):
                self._add_abstract_op(
                    "val str_join_seq (sep: string) (xs: seq string) : string\n"
                    "    ensures { String.length result >= 0 }")
                return f"(str_join_seq {_sep2} {args[0]})"
            self._add_abstract_op(
                "val str_join_arr (sep: string) (xs: array string) : string\n"
                "    ensures { String.length result >= 0 }")
            return f"(str_join_arr {_sep2} {args[0]})"
        var_name = arg_ir.get("name", "") if arg_ir.get("type") == "Var" else ""
        is_array = (var_name in getattr(self, "_array_locals", set()) or
                    var_name in getattr(self, "_current_array1d_params", set()))
        if not is_array and var_name:
            if getattr(self, "_current_symbol_table", {}).get(var_name) in ("list", "dict"):
                is_array = True
        if not is_array:
            at = arg_ir.get("type", "")
            if at in ("ArrayLit", "ListLit", "ListComp"):
                is_array = True
            elif at == "BinOp" and arg_ir.get("op") == "*":
                for side in ("left", "right"):
                    if arg_ir.get(side, {}).get("type", "") in ("ArrayLit", "ListLit"):
                        is_array = True
        if not is_array and "Array.make" in args[0]:
            is_array = True
        if is_array:
            # list-comprehension-lowering.md L2: a STRING-element array joined by `sep` is a
            # `string` (general-iterable join — length ≥ 0 only; the exact literal-list join
            # is handled above). Element type from `_array_elem_types` (Var) or the literal
            # shape. @mutable_state-gated → the corpus's int `join_array` is byte-identical.
            if self._join_arg_elem_is_string(arg_ir):
                _sep = (self._expr_to_whyml(_recv, local_refs or set(), invariant_ctx, subst)
                        if _recv is not None else '" "')
                self._add_abstract_op(
                    "val str_join_arr (sep: string) (xs: array string) : string\n"
                    "    ensures { String.length result >= 0 }")
                return f"(str_join_arr {_sep} {args[0]})"
            self._add_abstract_op("val join_array (a: array int) : int")
            return f"(join_array {args[0]})"
        self._add_abstract_op("val join_1 (x: int) : int")
        return f"(join_1 {args[0]})"

    def _join_arg_elem_is_string(self, arg_ir) -> bool:
        """list-comprehension-lowering.md L2: does the join argument's array carry STRING
        elements? A Var → `_array_elem_types`; the literal comprehension/repeat/list forms →
        their element type. @mutable_state only (the map is empty elsewhere)."""
        if not isinstance(arg_ir, dict):
            return False
        t = arg_ir.get("type")
        if t == "Var":
            _n = arg_ir.get("name")
            # cap4/5 (self-tcb-reduction `_refine_tuple_return_type`): a `seq string` refine
            # list-comp local carries string elements (so `"(" + ",".join(slots) + ")"` routes
            # `+` to str_concat_op). Method-gated -> inert.
            if _n in getattr(self, "_refine_str_comp_locals", set()):
                return True
            if getattr(self, "_array_elem_types", {}).get(_n) == "string":
                return True
            if getattr(self, "_seq_value_types", {}).get(_n) == "string":
                return True
            # self-ir-schema.md IR4: a @mutable_state seq local (`seq_parts = []; .append`)
            # holds emitted CODE strings — join it as a string seq (str_join_seq). If it
            # were an int seq the WhyML would fail to type-check (loud, never silent).
            return (_n in getattr(self, "_seq_locals", set())
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set()))
        if t == "ListComp":
            return self._is_string_expr(arg_ir.get("elt", {}))
        if t in ("ArrayLit", "ListLit", "Tuple"):
            _e = (arg_ir.get("elts") or [None])[0]
            return bool(_e) and self._is_string_expr(_e)
        if t == "BinOp" and arg_ir.get("op") == "*":
            for side in ("left", "right"):
                s = arg_ir.get(side, {})
                if isinstance(s, dict) and s.get("type") in ("ArrayLit", "ListLit"):
                    _e = (s.get("elts") or [None])[0]
                    return bool(_e) and self._is_string_expr(_e)
        return False

    def _handle_sum_call(self, expr: Dict[str, Any]) -> str:
        """Handle sum(iterable): constant fold if all elements are known literals."""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        if arg_ir.get("type") == "ArrayLit":
            elts = arg_ir.get("elts", [])
            if all(e.get("type") == "Number" and isinstance(e.get("value"), (int, float))
                   for e in elts):
                return str(sum(int(e["value"]) for e in elts))
        if arg_ir.get("type") == "Var":
            vname = arg_ir.get("name", "")
            known_elems = getattr(self, "_known_collection_elements", {})
            known_sizes = getattr(self, "_known_collection_sizes", {})
            if vname in known_elems and vname in known_sizes:
                size = known_sizes[vname]
                elems = known_elems[vname]
                if all(i in elems for i in range(size)):
                    return str(sum(int(elems[i]) for i in range(size)))
        return ""

    def _resolve_dotted_signature(self, func_name: str):
        """Resolve a dotted call's `(ret_type, param_types, result_ensures, field_spec)`
        from the module method tables: `self.<m>(...)` and `<recordvar>.<m>(...)` look up
        the real declared signature + propagated result-only/param-referencing
        postconditions; a bare bytes-producing method (`encode`/`ljust`/…) returns
        `array int`. Default is `int` / no types / no ensures / no field_spec.

        `field_spec` is `None`, or `(receiver_expr, receiver_class, field_ensures)` when
        the callee has self-FIELD-referencing ensures (A2c): the call site then gives the
        abstract op a leading `(self: receiver_class)` parameter and passes
        `receiver_expr`, so `self.x` in the propagated clause binds to the receiver
        record. (Extracted from `_handle_dotted_call`.)"""
        ret_type = "int"
        param_types: List[str] = []
        result_ensures: List[Dict[str, Any]] = []
        field_spec: Optional[Any] = None
        if func_name.startswith("self."):
            # Method IR names are stored as "<class_lower>__<method>"
            # (Module5._build_function_ir), so a `self._emit_contracts` call
            # site has to be prefixed with the current class's lowercased
            # name to hit the lookup.
            method_tail = func_name[len("self."):]
            cls = self._current_self_type
            lookup_key = f"{cls}__{method_tail}" if cls else method_tail
            ret_type = self._module_method_return_types.get(lookup_key, "int")
            param_types = self._option_record_param_upgrade(
                lookup_key, self._module_method_param_types.get(lookup_key, []))
            # Propagate the callee's result-only postconditions onto the
            # stub (array length, slot bounds, …) so the caller can
            # discharge VCs on the returned value. Param-referencing clauses
            # (already renamed to the stub's x_i) propagate too — e.g.
            # `\array_eq(\result, data)`.
            result_ensures = (
                getattr(self, "_module_method_result_ensures", {}).get(lookup_key, [])
                + getattr(self, "_module_method_param_result_ensures", {}).get(lookup_key, []))
            # gap7-spec-rev2 P3: fold in void/mutating contract for `self.<m>()` too.
            _fe = getattr(self, "_module_method_field_result_ensures", {}).get(lookup_key, [])
            _foe = getattr(self, "_module_method_field_old_ensures", {}).get(lookup_key, [])
            _fpe = getattr(self, "_module_method_field_param_result_ensures", {}).get(lookup_key, [])
            _fppe = getattr(self, "_module_method_field_param_post_ensures", {}).get(lookup_key, [])
            _fpfe = getattr(self, "_module_method_field_param_frame_ensures", {}).get(lookup_key, [])
            _rfe = getattr(self, "_module_method_result_frame_ensures", {}).get(lookup_key, [])
            _w = getattr(self, "_module_method_writes", {}).get(lookup_key, [])
            field_ens = _fe + _foe + _fpe + _fppe
            if (field_ens or _w or _fpfe or _rfe) and cls:
                # `self.<m>()` called from a sibling method: the enclosing
                # method's own `self` is the receiver, typed as the class. The 5th slot
                # carries the OPT-IN quantified frame ensures (M4), lowered separately with
                # the Call-trigger so only they get a trigger (non-frame ensures stay bare).
                # The 6th slot carries the OPT-IN `\result`-referencing single-cell frame
                # (fd-import-boundary), lowered with `\result` bound to the val's `result`.
                field_spec = ("self", cls, field_ens, _w, _fpfe, _rfe)
        else:
            # `<recordvar>.method(...)` — resolve the receiver's class so the
            # callee's result-only `ensures` propagates to this call site,
            # exactly like `self.method(...)`. Without this the call lowered to a
            # bare abstract op with no `ensures`, so a driver function that
            # constructs an instance and calls a method could prove nothing
            # about the result.
            matched_instance = False
            rv_classes = getattr(self, "_current_record_var_classes", {})
            # no-inline.md Piece C: also resolve a method on a MODULE-GLOBAL instance
            # (`_filesystem.sys_write(...)`) so a non-inlined call uses the callee's contract
            # (return type + result-only ensures), not the abstract int default.
            gv_classes = getattr(self, "_module_global_classes", {})
            parts = func_name.split(".")
            if len(parts) == 2 and (parts[0] in rv_classes or parts[0] in gv_classes):
                cls = (rv_classes.get(parts[0]) or gv_classes.get(parts[0])).lower()
                lookup_key = f"{cls}__{parts[1]}"
                rens = getattr(self, "_module_method_result_ensures", {})
                prens = getattr(self, "_module_method_param_result_ensures", {})
                if (lookup_key in self._module_method_return_types
                        or lookup_key in rens or lookup_key in prens):
                    ret_type = self._module_method_return_types.get(lookup_key, "int")
                    param_types = self._module_method_param_types.get(lookup_key, [])
                    result_ensures = rens.get(lookup_key, []) + prens.get(lookup_key, [])
                    fens = getattr(self, "_module_method_field_result_ensures", {})
                    # gap7-spec-rev2: also fold in the void/mutating contract — self-field
                    # `\old`-relating ensures + the `writes` (assigns) set — so a statement-position
                    # `c.inc()` mutates `c` instead of lowering to an opaque no-op.
                    foens = getattr(self, "_module_method_field_old_ensures", {})
                    fpens = getattr(self, "_module_method_field_param_result_ensures", {})
                    fppens = getattr(self, "_module_method_field_param_post_ensures", {})
                    fpfens = getattr(self, "_module_method_field_param_frame_ensures", {})
                    rfens = getattr(self, "_module_method_result_frame_ensures", {})
                    mwrites = getattr(self, "_module_method_writes", {})
                    field_ens = (fens.get(lookup_key, []) + foens.get(lookup_key, [])
                                 + fpens.get(lookup_key, []) + fppens.get(lookup_key, []))
                    writes = mwrites.get(lookup_key, [])
                    frame_ens = fpfens.get(lookup_key, [])
                    result_frame_ens = rfens.get(lookup_key, [])
                    if field_ens or writes or frame_ens or result_frame_ens:
                        # `b.<m>()`: the receiver record `b` becomes the abstract op's leading
                        # `(self: cls)` parameter; `writes` frames the mutated self-fields.
                        field_spec = (parts[0], cls, field_ens, writes, frame_ens,
                                      result_frame_ens)
                    matched_instance = True
            if not matched_instance:
                # Bytes-producing methods return `array int` (a byte buffer),
                # not the default `int` — so a chain like
                # `name.encode('utf-8')[:30].ljust(30, b'\x00')` can flow into a
                # `struct.pack('>...30s', ...)` name field. (Gap 5 of
                # missing-pycsl-ir-features.md, handled by typing the opaque op.)
                method_tail_name = func_name.rsplit(".", 1)[-1]
                if method_tail_name in ("encode", "ljust", "rjust", "zfill"):
                    ret_type = "array int"
        return ret_type, param_types, result_ensures, field_spec

    # richer-contracts-bridge C1 (S-c1): certified predicates/functions from the
    # preamble pyval theory (`_pydict_theory_lines`) that a mirror `#@ ensures`
    # may apply to `\result`. Routed to a DIRECT application `(wf_ir result)` /
    # `(size result)` — NOT the opaque numbered `val wf_ir_1 (x0:int):int` the
    # unknown-call fallback would fabricate (which is unbound + wrongly int-typed).
    # The induction backing these facts is done ONCE in Rocq/Lean (Phase2c
    # `wf_ir_binds` / `size_pos`), so SMT only applies the predicate to the
    # constructor spine. Corpus-inert: no reference-corpus contract names these
    # (verified: byte-diff 0); if the pyval theory is not in scope the direct
    # application is a LOUD unbound-symbol error, never a false proof.
    _CERTIFIED_PYVAL_ARITY = {"wf_ir": 1, "wf_dict": 1, "size": 1, "size_list": 1,
                              "size_dict": 1,
                              # richer-contracts-bridge P2.1 (C2): the DEEP
                              # well-formedness family the substmap fold preserves
                              # (emitted by emit_substmap_group in wf-preservation
                              # mode; strengthens the certified shallow wf_ir).
                              "wf_ir_deep": 1, "wf_dict_deep": 1, "wf_list_deep": 1,
                              # richer-contracts-bridge P2.2 (C2): the set-fold
                              # leaf->empty relational predicate (v, r).
                              "setfold_leaf_empty": 2,
                              # richer-contracts-bridge P2.3 (C2): emitted-fragment
                              # grammar membership.
                              "in_emitted_fragment": 1, "frag_dict": 1,
                              "frag_list": 1}

    def _handle_dotted_call(self, func_name: str, args: List[str]) -> str:
        """Handle dotted method calls (x.method(...)): emit abstract val declaration."""
        # module-emission.md (§T.2.7m): a CROSS-MODULE `self.<m>(...)` call — the callee
        # lives in a DIFFERENT `#@ verify_module` group than the function currently being
        # emitted — is lowered to the callee's PROVEN interface contract via the Why3
        # `clone`-refinement interface module `<G>Sig`, NOT to an assumed abstract `val`
        # stub. The interface `val <fn>` carries the callee's real contract (proved by the
        # provider module's `'refn'vc`), so the caller gets a proven boundary with NO new
        # trust. Active only on the `_transpile_modular` path (`_verify_module_of` set);
        # default flat path leaves this dict empty → byte-identical.
        vmod_of = getattr(self, "_verify_module_of", None)
        if vmod_of and func_name.startswith("self.") and self._current_self_type:
            callee_whyml = whyml_ident(
                f"{self._current_self_type}__{func_name[len('self.'):]}")
            callee_group = vmod_of.get(callee_whyml)
            cur_group = getattr(self, "_current_emit_group", None)
            if callee_group is not None and callee_group != cur_group:
                # Resolve the callee's declared signature so the args are coerced to the
                # interface val's parameter types (the Sig `val` is emitted with the same
                # signature from the SAME maps).
                ret_type, param_types, _, _ = self._resolve_dotted_signature(func_name)
                n = len(args)
                while len(param_types) < n:
                    param_types.append("int")
                param_types = param_types[:n]
                coerced = self._coerce_dotted_args(args, param_types)
                sig_mod = f"{callee_group}Sig"
                return (f"({sig_mod}.{callee_whyml} "
                        + " ".join(["self"] + coerced) + ")").replace("  ", " ")
        # Stateful composition: when this is `self.<m>(...)` inside a composer and
        # `<self_type>__<m>` is a flattened provider (`_apply_composition`), call it
        # CONCRETELY — `(<self_type>__<m> self args)` — so the provider's full
        # state-mutating contract (`assigns self.f`, `ensures self.f == \old(...)`)
        # applies. The abstract-val lowering below drops `self` and self-field ensures
        # (the method-call contract gap), which is sound only for pure providers. A
        # mixin's own isolation method is NOT in `_composed_provider_methods`, so its
        # genuine dependency still resolves to the abstract `val`.
        if func_name.startswith("self.") and self._current_self_type:
            concrete = f"{self._current_self_type}__{func_name[len('self.'):]}"
            if concrete in getattr(self, "_composed_provider_methods", set()):
                _, c_param_types, _, _ = self._resolve_dotted_signature(func_name)
                while len(c_param_types) < len(args):
                    c_param_types.append("int")
                c_coerced = self._coerce_dotted_args(args, c_param_types[:len(args)])
                return f"({concrete} {' '.join(['self'] + c_coerced)})".rstrip()
        # W8 capability (ii) — VARARG PACKING on a same-class `self.<m>(...)` call.
        # Same rule as the module-function call site: when the callee's last formal is a
        # `*vals: str` vararg, the trailing positional arguments are packed into the
        # `seq string` the callee declares. Without it the arity/type of the emitted
        # application disagrees with the callee's real signature (`"+" 154401638` against
        # `(vals: seq string)`) and the file fails L3-tc. Gated on the callee having a
        # str-annotated vararg -> byte-identical for every corpus program.
        if func_name.startswith("self.") and self._current_self_type:
            _vk = whyml_ident(f"{self._current_self_type}__{func_name[len('self.'):]}")
            _van = getattr(self, "_module_method_vararg_str", {}).get(_vk)
            _vfp = getattr(self, "_module_method_formal_params", {}).get(_vk, [])
            if _van and _vfp and _vfp[-1] == _van:
                _vfixed = len(_vfp) - 1
                _vpacked = "(Seq.empty: seq string)"
                for _vt in reversed(args[_vfixed:]):
                    _vpacked = f"(Seq.cons {_vt} {_vpacked})"
                args = args[:_vfixed] + [_vpacked]
        # 1111-spec R7 (self-method extension): a same-class `self.<m>(...)` call that
        # passes FEWER positional args than the callee's arity fills the missing trailing
        # params from the callee's positional DEFAULTS, so the concrete/abstract
        # application is TOTAL — never a partial application (`self.expect_name()` on
        # `expect_name(self, val=None)` otherwise lowers to `(<c>__expect_name self)` of
        # type `string -> string`, an L3-tc error). Mirrors the module-function call path
        # (_handle_call_expr, "1111-spec R7"): keyed on the MANGLED callee name (the
        # `_module_method_*` maps' method key), a `None` default on a non-int param is
        # filled at its faithful zero (Gap 3), and a trailing param with NO default is
        # left as a shortfall (byte-identical to today's arity mismatch). Every corpus
        # program that already passes full arity is UNCHANGED (len(args) >= arity).
        if func_name.startswith("self.") and self._current_self_type:
            _dk = whyml_ident(f"{self._current_self_type}__{func_name[len('self.'):]}")
            _dfp = getattr(self, "_module_method_formal_params", {}).get(_dk, [])
            if _dfp and len(args) < len(_dfp):
                _ddefs = getattr(self, "_module_method_param_defaults", {}).get(_dk, {})
                _dptypes = getattr(
                    self, "_module_method_param_whyml_types", {}).get(_dk, {})
                for _nm in _dfp[len(args):]:
                    if _nm not in _ddefs:
                        break   # no default -> leave the shortfall (old behaviour)
                    _dir = _ddefs[_nm]
                    _pwt = _dptypes.get(_nm, "int")
                    if (isinstance(_dir, dict) and _dir.get("type") == "None"
                            and _pwt != "int"):
                        args = args + [{"string": '""', "real": "0.0"}.get(_pwt, "0")]
                    else:
                        args = args + [self._expr_to_whyml(_dir, set(), False, None)]
        safe_name = whyml_ident(func_name.replace(".", "_"))
        n = len(args)
        arity_name = f"{safe_name}_{n}"
        # When the call is `self.<method>(...)` on a method defined in the
        # same module, look up the real declared return type AND parameter
        # types so the abstract val matches the actual signature. Without
        # this, every `self.foo(...)` is abstracted as `val ... (xi: int)
        # ... : int`, mismatching downstream consumers when `<method>`
        # actually takes/returns array or map types.
        ret_type, param_types, result_ensures, field_spec = self._resolve_dotted_signature(func_name)
        # Pad / truncate param_types to match n (the abstract val arity
        # only sees the caller's actual arg count, not the IR's symbol
        # table size).
        while len(param_types) < n:
            param_types.append("int")
        param_types = param_types[:n]
        # Per missing-bytes-struct-feature.md Phase 1: infer
        # array-int args from the emitted WhyML expression's shape
        # for non-self calls (where module_method_param_types
        # lookup didn't supply types). Without this, calls like
        # `struct.unpack(fmt, entry_bytes)` where `entry_bytes`
        # comes from `(array_slice self.disk ...)` were declared
        # with all-int param types, mismatching the array-int call
        # site and causing Why3 to reject the file with
        # `array.Array.array int @rho but is expected to have
        # type int`.
        ARRAY_INT_PREFIXES = (
            "(Array.make ", "(Array.sub ", "(array_slice ", "(Array.make_init ",
            "(array_copy ", "(array_concat ",
        )
        for i, arg in enumerate(args):
            if param_types[i] != "int":
                continue   # Already typed (from self-method lookup)
            stripped = arg.strip()
            # THE EMPTY-LIST PLACEHOLDER IS NOT EVIDENCE OF AN ARRAY PARAM (statement
            # cluster, relaunch #7). `[]` lowers to the emitter's "no elements" stand-in
            # `(Array.make 1024 0)`, which matches `ARRAY_INT_PREFIXES` and therefore
            # inferred `array int` for a param the callee's own `val` already declared
            # `int` — and the FIRST `_add_abstract_op` text wins, so the two disagreed and
            # the file failed L3-tc. Skip it: the placeholder says "this argument was an
            # empty list literal", never "the callee takes an array".
            if stripped == "(Array.make 1024 0)":
                continue
            if any(stripped.startswith(p) for p in ARRAY_INT_PREFIXES):
                param_types[i] = "array int"
                continue
            # Bare identifier referring to a known array-int local
            # / param. Check the symbol table.
            if stripped.startswith("!"):
                ident = stripped[1:]
            else:
                ident = stripped
            if not ident.replace("_", "").isalnum():
                continue
            st = getattr(self, "_current_symbol_table", {})
            if (ident in getattr(self, "_current_array1d_params", set())
                    or st.get(ident) in ("list", "tuple", "bytes", "bytearray")
                    or ident in getattr(self, "_array_locals", set())):
                param_types[i] = "array int"
                continue
            # Lever 6: infer an `emit_ir` param for a forward-declared (cross-mixin,
            # not-locally-defined) self-method whose signature the local registry
            # can't supply — when the argument is an emit_ir-typed identifier (an
            # `ExprIR`/`StmtIR`/... param or local). This types the
            # `_try_local_decl_kind` -> `_rhs_yields_map(val_ir)` cross-mixin call
            # (val_ir : emit_ir) that would otherwise default to `int` and fail L3-tc.
            # Byte-inert: no CORPUS symbol is emit_ir-typed (those types name the
            # emitter's own AST/IR node classes), so this never fires on corpus code.
            if st.get(ident) in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR"):
                param_types[i] = "emit_ir"
            # self-tcb-reduction _infer_tuple_slot_type (cap-d): a bare `Dict[str,str]`
            # param/local arg (a `_dict_value_types` string codomain) is a `map <k>
            # (option <v>)`, so a cross-file `self.<m>(<dict>)` call — whose abstract-val
            # default-types every parameter `int` — types the abstract val's parameter as
            # that map, keeping the (dead-here) `self._is_string_expr(elt)` /
            # `self._is_emit_ir_expr(elt)` call type-safe against elt's raw-dict type.
            # Byte-inert: a map passed to an int-typed abstract stub was a prior L3-tc
            # error, so no corpus/other-mirror call emits this shape.
            if getattr(self, "_dict_value_types", {}).get(ident) == "string":
                param_types[i] = self._dict_param_whyml_type(
                    ident, getattr(self, "_dict_key_types", {}) or {},
                    getattr(self, "_dict_value_types", {}) or {})
        coerced = self._coerce_dotted_args(args, param_types)
        # W8 capability (vi): a call to a SAME-CLASS sibling method whose declared return
        # type is a RECORD lowers to the CONCRETE sibling application
        # `(<class>__<m> self args)`, not to a receiver-less abstract `val self_<m>_0 () :
        # <rec>`. The abstract route would be a FACADE: the stub has NO link to the
        # receiver, so `self.cur().kind` could not be related to `self.toks[self.i].kind`
        # and every projection off it degenerated to an opaque int getter. The concrete
        # application is SOUND because the callee is a same-file VERIFIED method (it is in
        # `_module_func_names`, i.e. its body and contract are emitted and proved here), so
        # the caller sees its real contract AND the class type-invariant guarantee.
        # Ordering (callee before caller) comes from `scc.find_self_method_calls`, which is
        # given the same record-return set. Gated by `_record_array_fields` (the (i)/(iii)
        # low-blast-radius gate) → corpus byte-identical.
        # `0`-reads-as-`None` repair: the SECOND admission route into this same concrete
        # lowering is the OPT-IN `#@ sibling_concrete` marker. `_record_array_fields` is a
        # PROXY gate (it happens to hold for `_Parser` because `toks: List[Token]` is a
        # List-of-record field) and it excludes `PyCSLToJSONEmitter`, whose
        # `_const_int_value` therefore degraded to the opaque int-returning
        # `self__const_int_value_1` — which is precisely why `iv = self._const_int_value(v)`
        # had to be tested `if (!iv <> 0)` as a stand-in for `is not None`, making a
        # LEGITIMATE class constant of 0 read as None. The marker is an explicit per-callee
        # opt-in, so it is corpus byte-inert BY CONSTRUCTION (no corpus program writes the
        # directive) rather than by a proxy argument, and `scc.find_self_method_calls`
        # ALREADY supplies the callee-before-caller ordering edge for marked callees
        # (scc.py:136) — no new ordering machinery.
        # `_union_*` joins the admissible return types on BOTH routes. Note this closes a
        # latent inconsistency rather than opening a new door: `_Parser.peek` already
        # lowers concretely through the `int` arm only because
        # `_module_method_return_types` MIS-RECORDS its union return as `int`.
        _concrete = whyml_ident(
            f"{self._current_self_type}__{func_name[len('self.'):]}"
        ) if (func_name.startswith("self.") and self._current_self_type) else ""
        if (_concrete
                and (getattr(self, "_record_array_fields", None)
                     or _concrete in getattr(self, "_sibling_concrete_methods", set()))
                and (ret_type in ("emit_ir", "int", "string")
                     or (isinstance(ret_type, str) and ret_type.startswith("_union_"))
                     # A LIST-RETURNING SIBLING IS THE SAME CASE. `array <t>` was missing
                     # from this allowlist, and the consequence is a LOST CONVERSION that
                     # NO gate sees: `_Parser._if_tail` / `_else_block` /
                     # `_import_as_names` are all CONVERTED and PROVEN, their `let` bodies
                     # are emitted, `check-untrusted-emitted` reports them as definitions —
                     # and every CALL SITE still went through the receiver-less abstract
                     # `val self__if_tail_0 : array emit_ir`, whose result is
                     # UNCONSTRAINED. So `if_stmt`'s `orelse` child was an ARBITRARY array
                     # rather than the parsed one, and the conversion bought the caller
                     # nothing. Same soundness argument as the other arms: the callee is a
                     # same-file VERIFIED method in `_module_func_names`, and
                     # `scc.find_self_method_calls` supplies the callee-before-caller
                     # ordering edge.
                     or (isinstance(ret_type, str) and ret_type.startswith("array "))
                     # A TUPLE-RETURNING SIBLING is the same case again. `_call_args`
                     # returns `(seq emit_ir, seq emit_ir)` — the pair of node lists — and
                     # without this arm its CONVERSION is immediately shadowed: the `let`
                     # is emitted and proved while `trailers` and `classdef` keep binding
                     # `args`/`keywords` from the UNCONSTRAINED `val self__call_args_1`.
                     # Same soundness argument as every other arm: the callee is a
                     # same-file VERIFIED method in `_module_func_names`, and
                     # `scc.find_self_method_calls` supplies the ordering edge.
                     or (isinstance(ret_type, str) and ret_type.startswith("(")
                         and ret_type.endswith(")") and "," in ret_type)
                     or ret_type in {_ri["whyml_name"]
                                     for _ri in getattr(self, "_record_types", {}).values()})):
            if _concrete in getattr(self, "_module_func_names", set()):
                return f"({_concrete} {' '.join(['self'] + coerced)})".rstrip()
        # A2c: a self-FIELD-referencing callee ensure (`\result == self.x`) is
        # bound by giving the abstract op a leading receiver parameter
        # `(self: <class>)` and passing the receiver record, so `self.x` in the
        # propagated clause resolves to the actual instance's field.
        receiver_param = ""
        writes_clause = ""
        if field_spec is not None:
            receiver_expr, receiver_class = field_spec[0], field_spec[1]
            receiver_param = f"(self: {receiver_class}) "
            coerced = [receiver_expr] + coerced
            # gap7-spec-rev2: a void/mutating method's `assigns self.f` → `writes { self.f }` on
            # the abstract op, so the call mutates the receiver's region (the `_dotted_ensures_suffix`
            # `\old(self.f)` clause then relates post- to pre-state, and the caller sees the change).
            writes_fields = field_spec[3] if len(field_spec) > 3 else []
            if writes_fields:
                # Why3 `writes` is COMMA-separated (a `;` is a syntax error — only shows with
                # multi-field writes like os.sys_write's disk+fd_offset+_mtime_ticks).
                writes_clause = "\n    writes { " + ", ".join(
                    f"self.{f}" for f in writes_fields) + " }"
        # allocator-frame plan §2.7 (scope-to-win): an OPT-IN `#@ sibling_concrete` callee
        # gets a CONCRETE `self.<m>()` lowering — `(<class>__<m> self args)` — so why3 uses
        # the real method's FULL contract AND its type (class) invariant guarantee on the
        # post-state (an abstract stub conveys neither). Restricted to MARKED callees so it
        # fires ONLY for cheap leaf writers whose guarantee the caller absorbs (the os bitmap
        # leaves) — NOT for heavy directory mutators (concrete-calling those surfaces their
        # expensive maintenance into the caller). Ordering (callee before caller) is supplied
        # by scc.find_self_method_calls. Default (no marker) → abstract stub, byte-identical.
        if (field_spec is not None and func_name.startswith("self.")
                and self._current_self_type):
            concrete_name = whyml_ident(
                f"{self._current_self_type}__{func_name[len('self.'):]}")
            if (concrete_name in getattr(self, "_module_func_names", set())
                    and concrete_name in getattr(self, "_sibling_concrete_methods", set())):
                return f"({concrete_name} {' '.join(coerced)})"
        # body-gate gap-1: lower the callee's `\result[i]` ensures against the
        # CALLEE's return type, not the caller's. A method returning `array int`
        # (e.g. `_read_inode`) whose ensures says `\result[0] == …` must lower
        # `\result[0]` to `result[0]` (Array.get, via the L0 path in
        # `_resolve_subscript`), NOT the opaque/unbound `subscript_get` it gets when
        # `_func_return_type` still holds the CALLER's type. Restore after.
        _saved_frt = getattr(self, "_func_return_type", "")
        self._func_return_type = ret_type
        ensures_suffix = self._dotted_ensures_suffix(result_ensures, n, param_types, field_spec)
        self._func_return_type = _saved_frt
        # self-tcb-reduction (_err-divergence): a `self.<m>(...)` call to a `-> NoReturn`
        # callee never returns normally. Model it faithfully: give the abstract op the
        # `ensures { false }` never-returns postcondition (justified by the callee's
        # unconditional-raise body — the same claim Module5/functions.py emit on the
        # callee's own def, NR1) and lower the CALL to `(let _ = <call> in absurd)`, so the
        # continuation is bottom-typed (`'a`) and a trailing `self._err(...)` in an
        # `-> ExprIR` clause parser (e.g. `_parse_loop`) type-checks against the emit_ir
        # arms. NOT a blanket massage of the CALLER's contract: the caller's real
        # postcondition still has to hold on every returning arm; only the raising arm is
        # discharged by the divergence. Gated on the noreturn set → byte-identical for every
        # module with no `-> NoReturn` method.
        _nr_callee = (
            func_name.startswith("self.") and self._current_self_type is not None
            and whyml_ident(f"{self._current_self_type}__{func_name[len('self.'):]}")
            in getattr(self, "_module_method_noreturn", set()))
        if _nr_callee:
            ensures_suffix = ensures_suffix + "\n    ensures { false }"
        if n == 0 and not receiver_param:
            self._add_abstract_op(f"val {arity_name} () : {ret_type}{ensures_suffix}")
            _call = f"({arity_name} ())"
            return f"(let _ = {_call} in absurd)" if _nr_callee else _call
        params = " ".join(f"(x{i}: {ptype})" for i, ptype in enumerate(param_types))
        params = f"{receiver_param}{params}".rstrip()
        self._add_abstract_op(f"val {arity_name} {params} : {ret_type}{writes_clause}{ensures_suffix}")
        _call = f"({arity_name} {' '.join(coerced)})"
        return f"(let _ = {_call} in absurd)" if _nr_callee else _call

    def _is_seq_arg(self, arg: str) -> bool:
        """True if a lowered arg is a `seq`-typed value (a seq local or a seq-producing op), so
        `_coerce_dotted_args` can bridge it to a `List[_]` (array) param via `materialize`.
        @mutable_state-gated (seq locals only exist there) -> corpus byte-identical.
        (seq<->array-coercion feature: enables converting emitter handlers that pass list-
        comprehension results to `List[_]` helper params, e.g. `_handle_call_expr`'s `args`.)"""
        if not getattr(self, "_mutable_state_classes", None):
            return False
        base = arg.strip().lstrip("!")
        if (base in getattr(self, "_seq_locals", set())
                or base in getattr(self, "_seq_value_types", {})):
            return True
        return arg.strip().startswith(("(list_comp_seq", "(seq_sub ", "(Seq."))

    def _option_record_param_upgrade(self, lookup_key: str,
                                     param_types: List[str]) -> List[str]:
        """`Optional[<record>]` PARAM RESOLUTION (lesson (ar), corrected — relaunch #8).

        `_build_method_param_types_map` renders a param whose Module5 symtype is
        `"option:<R>"` through `_symtype_to_whyml`, which collapses it to `int` — while
        `functions._param_type_str`, the producer of the callee's ACTUAL emitted `val`
        signature, renders the SAME param as the native `option <record>`. The two
        producers disagreed, and the registry was the one lying: a call site coercing
        against it believed the slot was int-typed and passed the record bare, measured as
        `This expression has type _tok, but is expected to have type option _tok`
        (`self.funcdef([], async_=True, start=t)`).

        Read the callee's own `symbol_table` straight off the IR (the same source both
        producers use) and restore the option type the emitted signature really declares.
        Only an entry the registry left as `int` is upgraded, only when the symtype really
        is `option:<R>` for a DECLARED record `R`, and only under @mutable_state — so the
        corpus and every non-emitter mirror stay byte-identical.

        NOTE (lesson (am), again): the original diagnosis blamed `_resolve_dotted_signature`
        for not resolving a synthesized `_union_*` param. Re-probing showed it resolves
        `_union_*` FINE; the actual defect was one level up and had two parts — a QUOTED
        forward reference `Optional["_Tok"]` synthesizes a union with the Some arm MISSING
        (`type _union_funcdef_10 = Arm_10_None`, silently), and the UNQUOTED spelling takes
        the `option:<R>` path instead, which the registry then int-collapsed."""
        if not getattr(self, "_mutable_state_classes", None) or not param_types:
            return param_types
        # ONLY WHEN THE CALL RESOLVES CONCRETELY. The registry is the SIGNATURE for an
        # abstract self-call avatar (`self__<m>_<n>`), so "correcting" it there just moves
        # the mismatch to the argument — measured: upgrading `_bool_ir_to_int_wrap`'s
        # `Optional[BoolWrapIRView]` param retyped the avatar to `option boolwrapirview`
        # while the call still passed a bare `emit_ir`, breaking stmt_control_flow's L3-tc.
        # It is only for a CONCRETE application, whose callee's real `val` is emitted by
        # `_param_type_str`, that the two producers can disagree at all. Same gate the
        # concrete lowering itself uses (`_handle_dotted_call`).
        _cn = whyml_ident(lookup_key)
        if not (_cn in getattr(self, "_module_func_names", set())
                and (getattr(self, "_record_array_fields", None)
                     or _cn in getattr(self, "_sibling_concrete_methods", set()))):
            return param_types
        _f = next((f for f in ((getattr(self, "ir", None) or {}).get("functions") or [])
                   if f.get("name") == lookup_key), None)
        if _f is None:
            return param_types
        _formal = list(_f.get("formal_params") or [])
        _st = _f.get("symbol_table") or {}
        if len(_formal) != len(param_types):
            return param_types
        out = list(param_types)
        for _i, _pn in enumerate(_formal):
            _ty = _st.get(_pn)
            if (out[_i] == "int" and isinstance(_ty, str)
                    and _ty.startswith("option:")):
                _rt = getattr(self, "_record_types", {}).get(_ty[len("option:"):])
                if _rt and _rt.get("whyml_name"):
                    out[_i] = f"option {_rt['whyml_name']}"
            # A `List["ExprIR"]`/`List[StmtIR]` param: `_param_type_str` emits
            # `array emit_ir` for it (Module5 records the element type `emit_ir` in
            # `param_list_flat_elem`), while this registry — built from the collapsed
            # `_symtype_to_whyml("list")` — still says `array int`. Same two-producer
            # disagreement as the option case above; restore the emitted shape so the
            # call site bridges its `seq emit_ir` with `materialize_emit_ir` instead of
            # the int `materialize`.
            elif (out[_i] == "array int"
                  and (_f.get("param_list_flat_elem") or {}).get(_pn) == "emit_ir"):
                out[_i] = "array emit_ir"
        return out

    def _coerce_dotted_args(self, args: List[str], param_types: List[str]) -> List[str]:
        """Coerce each dotted-call arg to its declared param type. The caller's arg may be
        int while the param expects array or map (e.g. an int from an abstract `get_*`
        accessor flowing into a `Set[T]` slot). (Extracted from `_handle_dotted_call`.)"""
        coerced: List[str] = []
        for arg, ptype in zip(args, param_types):
            if ptype == "int":
                # EMPTY-LIST PLACEHOLDER into an int-erased param (statement cluster,
                # relaunch #7). `[]` lowers to `(Array.make 1024 0)` — the emitter's "no
                # elements" stand-in, which is NOT an empty array but a 1024-long zero
                # one. Handing it to a param the callee's signature int-erases
                # (`self.funcdef([], async_=False)`: `decorators` is un-annotated, so the
                # `val` declares it `int`) is an L3-tc error, `array int @rho` vs `int`.
                # Substitute the int witness `0`. This is not a new erasure: the
                # placeholder is not `[]` either, and the callee is a `\trusted` `val`
                # with `ensures true`, so no property of the argument is provable on
                # either side. Gated on the EXACT placeholder literal, so a genuine array
                # flowing into an int param still fails LOUDLY.
                if arg.strip() == "(Array.make 1024 0)":
                    coerced.append("0")
                    continue
                coerced.append(self._coerce_to_int(arg))
            elif ptype == "array emit_ir" and arg.strip() == "(Array.make 1024 0)":
                # THE EMPTY-LIST PLACEHOLDER into a `List["ExprIR"]` param. `[]` lowers to
                # the emitter's `(Array.make 1024 0)` stand-in (lesson (ao)) — a 1024-long
                # ZERO array, and int-typed besides. `self.funcdef([], async_=True, …)`
                # really passes NO decorators, so the faithful value is the genuinely
                # EMPTY emit_ir array. Gated on the EXACT placeholder literal: any other
                # array actual still has to match the element type or fail LOUDLY.
                coerced.append('(Array.make 0 (IrOther ""))')
            elif ptype == "array emit_ir" and self._is_seq_arg(arg):
                # STATEMENT/EXPRESSION-LIST param (relaunch #8): a `seq emit_ir` actual
                # (a `decorators = []` + `.append(<node>)` accumulator) flowing into a
                # `List["ExprIR"]` param crosses seq->array through the SAME pointwise
                # `materialize_emit_ir` bridge the `-> List[<node>]` early-return uses —
                # a fresh array pinned element-by-element, so nothing is erased and no
                # axiom is added. Identical declaration text -> `_add_abstract_op` dedups.
                self._add_abstract_op(
                    "val materialize_emit_ir (s: seq emit_ir) : array emit_ir\n"
                    "    ensures { Array.length result = Seq.length s }\n"
                    "    ensures { forall i:int. 0 <= i < Seq.length s ->"
                    " result[i] = Seq.get s i }")
                coerced.append(f"(materialize_emit_ir {arg})")
            elif ptype in ("array int", "array string") and self._is_seq_arg(arg):
                # seq<->array coercion: a `seq`-typed arg (a list comprehension lowers to `seq`)
                # flowing into a `List[_]` (= `array _`) param is bridged seq->array via
                # `materialize`/`materialize_str`. @mutable_state-only detection (seq locals) ->
                # byte-identical for the corpus (`_is_seq_arg` is False without _mutable_state).
                if ptype == "array string":
                    self._materialize_str_bridge()
                    coerced.append(f"(materialize_str {arg})")
                else:
                    self._materialize_bridge()
                    coerced.append(f"(materialize {arg})")
            elif ptype == "array int":
                coerced.append(self._array_coerce_arg(arg))
            elif ptype == "map int (option int)":
                # No known int→map coercion. Use `const None` as a
                # placeholder empty map; the abstract val has no axioms
                # about its contents anyway.
                stripped = arg.strip()
                map_prefixes = ("(map_update_some ", "(map_update_none ",
                                "(const (None: option int)", "(Map.get ")
                if any(stripped.startswith(p) for p in map_prefixes):
                    coerced.append(arg)
                elif stripped.replace("_", "").replace("!", "").isalnum():
                    # Bare identifier — pass through; caller-side type
                    # must already match.
                    coerced.append(arg)
                else:
                    coerced.append("(const (None: option int))")
            elif isinstance(ptype, str) and ptype.startswith("option "):
                # `Optional[<record>]` PARAM (lesson (ar), relaunch #8). Two actuals reach
                # such a slot and both need lifting into the option:
                #   * an OMITTED optional argument, filled from the Python `None` default,
                #     which the int model lowers to the witness `0` -> the option's own
                #     `None`, the FAITHFUL value of that default (the same reasoning as the
                #     `_union_*` arm below);
                #   * a PRESENT record actual (`self.funcdef([], async_=True, start=t)`)
                #     -> `(Some <arg>)`.
                # The present case is gated on the actual being a bare `!x` / `x` whose
                # local the emitter itself pre-declared with THIS record's default literal
                # (`_record_field_elem_locals`), so an int-erased or differently-typed
                # actual is NOT re-tagged as a record — it falls through and fails LOUDLY.
                _pl = ptype[len("option "):].strip()
                _s = arg.strip()
                if _s in ("0", "(0)"):
                    coerced.append(f"(None: {ptype})")
                    continue
                _id = _s[1:] if _s.startswith("!") else _s
                _rl = getattr(self, "_record_field_elem_locals", {}) or {}
                _rn = _rl.get(_id)
                _rt = getattr(self, "_record_types", {}).get(_rn) if _rn else None
                if _id.isidentifier() and _rt and _rt.get("whyml_name") == _pl:
                    coerced.append(f"(Some {_s})")
                    continue
                coerced.append(arg)
            elif (isinstance(ptype, str) and ptype.startswith("_union_")
                  and arg.strip() in ("0", "(0)")):
                # cursor-nest `parse_atom`: an OMITTED optional argument
                # (`self.expect("RPAREN")` against `def expect(self, kind, value=None)`)
                # is filled with the Python `None` default, which the int model lowers to
                # the witness `0` — ill-typed against the param's `_union_*`
                # (`This expression has type int, but is expected to have type
                # _union_expect_1`). Substitute the union's own nullary None arm, which is
                # the FAITHFUL value of that default. Restricted to a literal `0` actual,
                # so a genuinely int-valued expression flowing into a union slot still
                # fails LOUDLY rather than being silently re-tagged as None.
                _vi = getattr(self, "_variant_types", {}).get(ptype) or {}
                _none = next((cn for cn, c in (_vi.get("constructors") or {}).items()
                              if c.get("arity") == 0 and "None" in cn), None)
                coerced.append(f"({_none} : {ptype})" if _none else arg)
            else:
                coerced.append(arg)
        return coerced

    @staticmethod
    def _strip_outer_parens(s: str) -> str:
        """Strip ONE matching outer paren pair if it wraps the whole string (else unchanged) —
        bares a lowered trigger term (`(slot_inode self.disk x0 k)` → `slot_inode self.disk x0 k`);
        a trigger pattern must be bare (Why3 mis-parses `[(t)]` → auto-trigger fallback)."""
        s = s.strip()
        if not (s.startswith("(") and s.endswith(")")):
            return s
        depth = 0
        for i, ch in enumerate(s):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return s[1:-1].strip() if i == len(s) - 1 else s
        return s

    def _frame_trigger_term(self, node: Any) -> Optional[Dict[str, Any]]:
        """For a frame conjunct `X == \\old(...)` (or `\\old(...) == X`) anywhere in `node`,
        return X's IR — the POST-state term to pin as the forall's E-matching trigger (first
        match, depth-first), else None."""
        if not isinstance(node, dict):
            return None
        if node.get("type") == "BinOp" and node.get("op") == "==":
            l, r = node.get("left"), node.get("right")
            l_old = isinstance(l, dict) and l.get("type") in ("Old", "OldField")
            r_old = isinstance(r, dict) and r.get("type") in ("Old", "OldField")
            if r_old and not l_old:
                return l
            if l_old and not r_old:
                return r
        for v in node.values():
            for c in (v if isinstance(v, list) else [v]):
                res = self._frame_trigger_term(c)
                if res is not None:
                    return res
        return None

    def _dotted_ensures_suffix(self, result_ensures: List[Dict[str, Any]], n: int,
                               param_types: List[str],
                               field_spec: Optional[Any] = None) -> str:
        """Render the propagated postconditions of a dotted callee as
        `\\n    ensures { … }` lines appended to its abstract `val`. Emitted in spec
        (boolean) context with the stub's positional params x0..x{n-1} registered as
        in-scope.

        `field_spec` (A2c) carries `(receiver_expr, receiver_class, field_ensures)` of
        self-FIELD clauses: these are rendered with `_current_self_type` set to the
        receiver class so the leading `(self: <class>)` op parameter binds `self.x` (and
        ambiguous field labels qualify correctly). (Extracted from `_handle_dotted_call`.)"""
        field_ensures = field_spec[2] if field_spec is not None else []
        frame_ensures = (field_spec[4] if field_spec is not None and len(field_spec) > 4
                         else [])
        result_frame_ensures = (field_spec[5] if field_spec is not None and len(field_spec) > 5
                                else [])
        if (not result_ensures and not field_ensures and not frame_ensures
                and not result_frame_ensures):
            return ""
        _prev_spec = self._in_spec
        _prev_params = self._current_params
        self._in_spec = True   # emit boolean formulas, not int-coerced
        # The stub's positional params are x0..x{n-1}; a propagated
        # param-referencing ensures (e.g. `\array_eq(result, x0)`) names
        # them, so register them as in-scope params — otherwise
        # `_handle_var_expr` would mistake `x_i` for an undeclared global
        # and emit a spurious `val constant x_i : int`.
        self._current_params = set(_prev_params) | {
            f"x{i}" for i in range(max(n, len(param_types)))}
        ensures_suffix = ""
        for e in result_ensures:
            w = self._expr_to_whyml(e, set(), invariant_ctx=True)
            ensures_suffix += f"\n    ensures {{ {w} }}"
        if field_ensures or frame_ensures or result_frame_ensures:
            _prev_self = self._current_self_type
            self._current_self_type = field_spec[1]   # receiver class
            for e in field_ensures:
                w = self._expr_to_whyml(e, set())
                ensures_suffix += f"\n    ensures {{ {w} }}"
            # M4: the OPT-IN quantified frame ensures — lowered with `_frame_trigger_active`
            # so the Forall handler pins a specific Call-trigger (`[slot_inode self.disk x0 k]`);
            # only these clauses get a trigger, so the others stay byte-identical.
            if frame_ensures or result_frame_ensures:
                _prev_ft = self._frame_trigger_active
                self._frame_trigger_active = True
                for e in frame_ensures:
                    w = self._expr_to_whyml(e, set())
                    ensures_suffix += f"\n    ensures {{ {w} }}"
                # fd-import-boundary: the `\result`-referencing single-cell frame. `\result`
                # lowers to the val's `result` keyword (its return value = the call result),
                # so binding is automatic. A self-field Subscript post-state term carries no
                # Call-trigger (the Forall handler only pins Call triggers), so Why3 auto-
                # triggers the single-cell frame — sound for the per-cell fd_open frame.
                for e in result_frame_ensures:
                    w = self._expr_to_whyml(e, set())
                    ensures_suffix += f"\n    ensures {{ {w} }}"
                self._frame_trigger_active = _prev_ft
            self._current_self_type = _prev_self
        self._current_params = _prev_params
        self._in_spec = _prev_spec
        return ensures_suffix

    def _handle_struct_call(
            self, expr: Dict[str, Any], args: List[str],
            func_name: str) -> Optional[str]:
        """Format-string-aware emission for `struct.pack` / `struct.unpack`.

        Per missing-bytes-struct-feature.md Phase 2. Returns the
        emitted WhyML expression, or None if the format string is
        dynamic / contains unsupported chars (caller falls back to
        the generic auto-trust path).
        """
        ir_args = expr.get("args", [])
        if not ir_args:
            return None
        fmt_ir = ir_args[0]
        if fmt_ir.get("type") != "String":
            return None   # Dynamic format string
        fmt = fmt_ir.get("value", "")
        # cleared-pack item 4 (UB-7.4b): NATIVE size/alignment ('@' prefix) is
        # platform-dependent — a standard-size size law or round-trip would be
        # UNSOUND (native alignment inserts padding). REJECT it with a clear
        # diagnostic rather than silently emit an opaque (but wrongly-sized) model.
        if isinstance(fmt, str) and fmt[:1] == "@":
            from errors import PyCSLSemanticError
            raise PyCSLSemanticError(
                f"struct format '{fmt}': native size/alignment ('@' prefix) is "
                f"unsupported (UB-7.4b). Native layout is platform-dependent, so "
                f"PyCSL cannot soundly model its size or round-trip. Use an explicit "
                f"standard-size byte-order prefix ('<', '>', '=', or '!').")
        parsed = parse_format(fmt)
        if parsed is None:
            return None   # Unsupported char in format

        slot_id = parsed.slot_id()
        # cleared-pack: a WHITELISTED scalar-int shape (single OR multi-slot,
        # signed OR unsigned) lowers to the FAITHFUL, guarded `Pycsl.Struct.Std`
        # family (`struct_{pack,unpack}_f<tag-join>`) — byte-codec-anchored
        # round-trip + size law + per-field in-range guard. A single fixed-bytes
        # `s` slot lowers to the array-identity family `struct_{pack,unpack}_fs<N>`.
        # All other shapes keep the opaque abstract `iN`/`i1a1` symbols
        # (documented boundary — incl. the legacy os shapes and float/native).
        faithful = parsed.faithful_slots()          # scalar shape or None
        faithful_tag = parsed.faithful_tag()        # tag-join or None
        bytes_n = parsed.faithful_bytes_slot()      # fixed-bytes N or None
        if func_name == "struct.unpack":
            # struct.unpack(fmt, data) → (t1, ..., tN)
            # Abstract: val struct_unpack_<slot_id> (fmt: int) (data: array int) : (t1, ..., tN)
            if parsed.arity == 0:
                ret_type = "unit"
            elif parsed.arity == 1:
                ret_type = parsed.slots[0]
            else:
                ret_type = "(" + ", ".join(parsed.slots) + ")"
            if faithful is not None:
                sym = f"struct_unpack_f{faithful_tag}"
            elif bytes_n is not None:
                sym = f"struct_unpack_fs{bytes_n}"
            else:
                sym = f"struct_unpack_{slot_id}"
            # `val function` — both program-callable and a logical
            # symbol the round-trip axiom can name.
            self._add_abstract_op(
                f"val function {sym} (fmt: int) (data: array int) : {ret_type}")
            # The fmt arg is a String literal → coerce to int hash;
            # the data arg should already be `array int`-shaped.
            fmt_arg = self._coerce_str_arg(args[0]) if args else "0"
            data_arg = args[1] if len(args) > 1 else "(Array.make 0 0)"
            return f"({sym} {fmt_arg} {data_arg})"

        if func_name == "struct.pack":
            # struct.pack(fmt, x1, ..., xN) → array int
            # Abstract: val struct_pack_<slot_id> (fmt: int) (x1: t1) ... (xN: tN) : array int
            # `*list` spread: PyCSL's IR may not expose individual
            # elements when the arg is Starred. If the actual arg
            # count after fmt doesn't match the format arity, we
            # bail out and let the dotted-call path auto-trust.
            value_args = args[1:]
            if len(value_args) != parsed.arity:
                return None
            if faithful is not None:
                sym = f"struct_pack_f{faithful_tag}"
            elif bytes_n is not None:
                sym = f"struct_pack_fs{bytes_n}"
            else:
                sym = f"struct_pack_{slot_id}"
            params = ["(fmt: int)"] + [
                f"(x{i}: {t})" for i, t in enumerate(parsed.slots)]
            self._add_abstract_op(
                f"val function {sym} {' '.join(params)} : array int")
            fmt_arg = self._coerce_str_arg(args[0]) if args else "0"
            # Coerce each value arg based on its slot type.
            coerced = []
            for arg, slot_t in zip(value_args, parsed.slots):
                if slot_t == "int":
                    coerced.append(self._coerce_to_int(arg))
                else:
                    coerced.append(arg)   # array int passed through
            return f"({sym} {fmt_arg} {' '.join(coerced)})"

        return None

    def _emit_contract_logic_symbol(self, func_name: str, expr: Dict[str, Any],
                                    args: List[str]) -> Optional[str]:
        """11-0632-spec-8 Part 2 (NARROW safety net, contract position only).

        An unknown applied symbol seen in CONTRACT/formula context (`_in_spec`) is a
        LOGIC predicate reference — emit it as a logic `predicate name argtypes`, NOT a
        program `val name_N (x0:int):int` (the latter is illegal in `ensures`/`requires`
        and mistyped against a `string`/`real` argument). Argument types are recovered
        from the enclosing stub's symbol table (`_current_symbol_table`) at the SAME
        py→WhyML mapping the rest of the emitter uses (`_symtype_to_whyml`: `str`→string,
        `float`→real, list/tuple/bytes→array int, default int). Returns the logic
        application `(name args)`, or None if the symbol is unsuitable for the logic path
        (then the caller keeps the program-`val` fallback).

        Faithfulness: the predicate carries NO axioms — it is an uninterpreted logic
        symbol that constrains nothing it should not. Part 1 (carrying the dependency's
        real `#@ inductive` decl) always WINS when it can: a propagated decl puts
        `func_name` in `_inductive_preds`, so this arm is never reached for it.
        """
        raw_args = expr.get("args", [])
        if len(raw_args) != len(args):
            return None
        # gap-9: if `func_name` is an imported `#@ inductive` predicate whose
        # RULE we deliberately did NOT cross (it carries a heavy `\exists`
        # trigger), recover its param types from the recorded dependency
        # signature so the opaque `predicate` decl has the RIGHT types (e.g.
        # `(array int) (string)` for `name_present(disk, name)`), not the
        # symbol-table-recovered `int` default (which mistypes `self.disk`).
        imported_sigs = getattr(self, "_imported_inductive_sigs", {}) or {}
        if func_name in imported_sigs:
            from module6_whyml.identifiers import whyml_ident as _wi
            sig_types = self._inductive_sig_whyml(imported_sigs[func_name])
            name = _wi(func_name)
            if sig_types:
                self._add_abstract_op(f"predicate {name} {sig_types}")
            else:
                self._add_abstract_op(f"predicate {name}")
            return f"({name} {' '.join(args)})" if args else name
        symtab = getattr(self, "_current_symbol_table", {}) or {}
        argtypes: List[str] = []
        for a_ir in raw_args:
            sym_t = None
            if isinstance(a_ir, dict) and a_ir.get("type") == "Var":
                sym_t = symtab.get(a_ir.get("name"))
            argtypes.append(self._symtype_to_whyml(sym_t))
        name = whyml_ident(func_name)
        if argtypes:
            self._add_abstract_op(
                f"predicate {name} {' '.join(f'({t})' for t in argtypes)}")
        else:
            self._add_abstract_op(f"predicate {name}")
        return f"({name} {' '.join(args)})" if args else name

    @staticmethod
    def _is_null_byte_lit(ir: Dict[str, Any]) -> bool:
        """True iff `ir` is the byte literal `b'\\x00'` — represented in the IR as an
        `ArrayLit` of a single `Number 0` (the bytes literal lowering)."""
        if ir.get("type") != "ArrayLit":
            return False
        elts = ir.get("elts", [])
        return (len(elts) == 1
                and elts[0].get("type") == "Number"
                and elts[0].get("value") == 0)

    def _linear_form(self, ir: Dict[str, Any]) -> Optional[Tuple[int, Dict[str, int]]]:
        """Evaluate an integer IR node to an AFFINE form (const, {var: coeff}) over
        `BinOp(+/-/*)` of `Number` and `Var` leaves. Returns None if any sub-term is
        non-affine (e.g. var*var, a Call, a Subscript). Used to compute the NULL-padded
        field WIDTH `upper - lower` as a literal even though both bounds carry the loop
        variable `i`: the difference cancels `i` and folds to the constant `30`, the
        SAME literal width the cross-validated `slot_name_byte_decode` /
        `field_to_str_round_trip` axioms key on."""
        t = ir.get("type")
        if t == "Number":
            v = ir.get("value")
            if isinstance(v, (int, float)) and float(v).is_integer():
                return (int(v), {})
            return None
        if t == "Var":
            return (0, {ir.get("name", ""): 1})
        if t == "BinOp":
            lf = self._linear_form(ir.get("left", {}))
            rf = self._linear_form(ir.get("right", {}))
            if lf is None or rf is None:
                return None
            (lc, lv), (rc, rv) = lf, rf
            op = ir.get("op")
            if op in ("+", "-"):
                sgn = 1 if op == "+" else -1
                out = dict(lv)
                for k, c in rv.items():
                    out[k] = out.get(k, 0) + sgn * c
                return (lc + sgn * rc, {k: c for k, c in out.items() if c != 0})
            if op == "*":
                # affine only if one side is a pure constant
                if not lv:
                    return (lc * rc, {k: lc * c for k, c in rv.items()})
                if not rv:
                    return (lc * rc, {k: rc * c for k, c in lv.items()})
            return None
        return None

    def _static_width(self, lower_ir: Dict[str, Any],
                      upper_ir: Dict[str, Any]) -> Optional[int]:
        """The field WIDTH `upper - lower` as a literal int, or None if it is not a
        constant (var-coefficients must all cancel)."""
        lf = self._linear_form(lower_ir)
        uf = self._linear_form(upper_ir)
        if lf is None or uf is None:
            return None
        (lc, lv), (uc, uv) = lf, uf
        diff_vars = dict(uv)
        for k, c in lv.items():
            diff_vars[k] = diff_vars.get(k, 0) - c
        if any(c != 0 for c in diff_vars.values()):
            return None
        return uc - lc

    def _match_field_decode_idiom(
            self, expr: Dict[str, Any]
    ) -> Optional[tuple]:
        """PURE STRUCTURAL match of the null-terminated-field NAME-decode idiom

            <arr>[<a>:<b>].split(b'\\x00')[0].decode('utf-8', errors='ignore')

        Returns `(slice_node, lower_ir, width)` when ALL five narrowness
        conditions (see `_recognize_field_decode_idiom`) hold, else None.

        Factored out so BOTH the value-lowering recognizer AND the
        local-VARIABLE typing pass key on the SAME shape: the recognizer
        lowers the matched value to a `field_to_str …` STRING term, so any
        local assigned this idiom must be declared a string-typed ref (never
        `ref 0 : ref int`). It performs NO emission (no `_expr_to_whyml`), so
        it is safe to call during the pre-declaration classification pass."""
        # (1) outer decode('utf-8', ...)
        if not isinstance(expr, dict):
            return None
        dargs = expr.get("args", [])
        if not dargs or dargs[0].get("type") != "String" \
                or dargs[0].get("value") != "utf-8":
            return None
        recv = expr.get("receiver")
        if not isinstance(recv, dict):
            return None
        # (2) receiver is Subscript[0]
        if recv.get("type") != "Subscript":
            return None
        idx = recv.get("index", {})
        if idx.get("type") != "Number" or idx.get("value") != 0:
            return None
        split_call = recv.get("value", {})
        # (3) ... over a `split(b'\x00')` Call
        if split_call.get("type") != "Call":
            return None
        sfunc = split_call.get("func", "")
        if not (sfunc == "split" or (isinstance(sfunc, str) and sfunc.endswith(".split"))):
            return None
        sargs = split_call.get("args", [])
        if len(sargs) != 1 or not self._is_null_byte_lit(sargs[0]):
            return None
        slice_node = split_call.get("receiver", {})
        # (4) ... whose receiver is a genuine `arr[a:b]` slice
        if slice_node.get("type") != "SliceAccess":
            return None
        sl = slice_node.get("slice", {})
        if sl.get("type") != "Slice" or sl.get("step") is not None:
            return None
        lower_ir = sl.get("lower")
        upper_ir = sl.get("upper")
        if lower_ir is None or upper_ir is None:
            return None
        # (5) statically-known field WIDTH (upper - lower), even though both bounds
        # carry the loop variable: the affine difference cancels it to the constant.
        width = self._static_width(lower_ir, upper_ir)
        if width is None or width <= 0:
            return None
        return (slice_node, lower_ir, width)

    def _recognize_field_decode_idiom(
            self, expr: Dict[str, Any], local_refs: Set[str],
            invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> Optional[str]:
        """FAITHFUL READ-NAME LOWERING (the narrow null-terminated-field recognizer).

        Match EXACTLY the on-disk fixed-width null-padded NAME-field decode idiom

            <arr>[<a>:<b>].split(b'\\x00')[0].decode('utf-8', errors='ignore')

        over a byte-array SLICE, and lower it to the genuine codec TERM

            (field_to_str <arr> <a> <b-a>)

        — the SAME abstract `field_to_str` symbol the cross-validated
        `field_to_str_round_trip` / `field_to_str_frame` / `slot_name_byte_decode`
        axioms constrain (declared `val function`, so it is program-callable). This is a
        faithful Python->WhyML lowering, NOT a `val`/assumed-ensures shim and NOT a new
        trust: `bytes[a:b].split(b'\\x00')[0].decode('utf-8', errors='ignore')` IS the
        bytes from `a` up to the first null within the `b-a`-byte window, read as a
        UTF-8 string — exactly `field_to_str`'s scan-to-first-null definition.

        NARROWNESS (provably corpus-confined): EVERY one of the following must hold, or
        the recognizer declines (returns None, leaving every other `.split`/`.decode`
        use on its existing path, byte-identical):
          1. the outer call is `decode` with first arg the string literal `'utf-8'`;
          2. its receiver is `Subscript[0]` (the `[0]` first split-part);
          3. over a `split` Call whose sole arg is the byte literal `b'\\x00'`;
          4. whose receiver is a `SliceAccess` (`arr[a:b]`, a genuine `[a:b]` slice);
          5. with a statically-known field WIDTH `b-a` (so the term carries the literal
             width the round-trip axiom keys on).
        Any other `split`/`decode` shape (non-`b'\\x00'` separator, non-`[0]` index,
        non-utf8 codec, non-slice receiver, dynamic width) is NOT matched."""
        m = self._match_field_decode_idiom(expr)
        if m is None:
            return None
        slice_node, lower_ir, width = m
        base = slice_node.get("value", {})
        arr = self._array_coerce_arg(
            self._expr_to_whyml(base, local_refs, invariant_ctx, subst))
        off = self._expr_to_whyml(lower_ir, local_refs, invariant_ctx, subst)
        # Genuine codec TERM — the abstract `field_to_str` symbol the axioms key on
        # (declared `val function` in preamble._AXIOM_FUNCTIONS, no ensures/shim).
        return f"(field_to_str {arr} {off} {width})"

    def _handle_call_expr(self, node: "ExprIR", local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature; deep body stays dict-based
        func_name = expr["func"]
        # PYTHON-AST NODE CTOR FAMILY (increment 10): a 0-FIELD ASDL SINGLETON
        # construction (`_N("Load")()`, `_N("Not")()`) lowers to its CLASS-NAME STRING.
        # A 0-field class carries no information beyond its own identity, so the name IS
        # its whole content — nothing is erased — and a 0-field WhyML record is not even
        # expressible. This is what unblocks the `ctx`/`op` slot of every
        # Starred/UnaryOp/BoolOp/Compare construction WITHOUT an enum type, a new ADT or
        # an axiom. The membership is read off the compiled file's OWN `_NODE_SPEC`
        # (`ir_resolve`, key `pyast_singleton_nodes`) and that key is absent from every
        # other file's IR -> corpus and every other mirror byte-identical.
        if (not expr.get("args") and not expr.get("keywords")
                and isinstance(func_name, str)
                and func_name in set(self.ir.get("pyast_singleton_nodes", []) or [])):
            return f'"{func_name}"'

        # L2 DISPATCH-EXPANSION: `self.<CONST>.get(type(x), "<default>")` over a class-body
        # TYPE-KEYED STRING table. MUST be tried before the `"." in func_name` dotted-call
        # dispatch further down, which otherwise collapses the whole lookup into one
        # opaque int-returning val. Fail-closed -> everything else is byte-identical.
        _tsg = self._class_type_str_table_get(expr, local_refs, invariant_ctx, subst)
        if _tsg is not None:
            return _tsg
        # stmt-list-append-mutation wall (C-bucket): `<stmt_ir>.get("stmt")` reflects the
        # statement node's TAG via `stmt_kind_of` — the read-back that OBSERVES the
        # appended node's identity (the non-vacuity gate). Fires only for a subscript of a
        # `ref (seq stmt_ir)` param → corpus-inert.
        _skr = self._stmt_ir_kind_reflection(expr, local_refs, invariant_ctx, subst)
        if _skr is not None:
            return _skr
        # G1 (09-2223 pure-classifier increment): `<record-var>.get("<field>"[, default])`
        # on a record-typed param/local reads the NATIVE record field, not the opaque
        # `<recv>_get_N <int-hash>` abstract op that drops the read (a vacuous/unfaithful
        # "proof"). Gated on the record-typed-receiver (`_current_record_var_classes`) — a
        # plain `Dict[str,Any]` receiver is NOT in that map, so it keeps the legacy opaque
        # op and stays corpus-byte-inert. The `.get`'s defensive default (a 2nd arg for the
        # absent-key case) is dropped: a declared field is always present in the record
        # model, so the field read is total (sound under `ensures True`, faithful for a
        # TypedDict whose key is declared).
        _rget = self._record_get_field(expr)
        if _rget is not None:
            _recv, _label, _ = _rget
            return f"{whyml_ident(_recv)}.{_label}"
        # option-of-record projection (boundary-1 G1 extension): `<optvar>.get("<field>")`
        # on an `Optional[<record>]` receiver projects the field from the `Some` arm —
        # `(match optvar with Some _r -> _r.<label> | None -> <default> end)`. The field
        # IS read (NON-VACUOUS); the `None` arm is dead under the body's `is None` guard
        # but present so the match is total. Gated on `_option_record_param_classes`
        # (only an Optional-of-record param) → corpus-byte-inert.
        _org = self._option_record_get_field(expr)
        if _org is not None:
            _orecv, _olabel, _oft, _odflt = _org
            return (f"(match {whyml_ident(_orecv)} with "
                    f"Some _r -> _r.{_olabel} | None -> {_odflt} end)")
        # typed-ir-for-b-ceiling.md B-C2: an INLINE `<node>.to_dict()` (no args) in a
        # @mutable_state method is IDENTITY on the typed IR — the node already IS its
        # `emit_ir` value — so lower to the receiver (the BOUND form is R1's alias).
        if (isinstance(func_name, str) and func_name.endswith(".to_dict")
                and not expr.get("args")
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _recv = func_name[:-len(".to_dict")]
            _parts = _recv.split(".")
            _rir = {"type": "Var", "name": _parts[0]}
            for _p in _parts[1:]:
                _rir = {"type": "Attribute", "object": _rir, "attr": _p}
            _rw = self._expr_to_whyml(_rir, local_refs, invariant_ctx, subst)
            # An emit_ir receiver (an ExprIR field / alias) → IDENTITY (it already IS its
            # emit_ir value). item34.md CF2: a record-typed receiver (`stmt.to_dict()` on an
            # `IfStmt`/`WhileStmt` record) is a CONVERSION to the reflectable emit_ir node —
            # an opaque abstract (content unmodeled; only the emit_ir TYPE matters).
            if self._is_emit_ir_expr(_rir):
                return _rw
            # self-tcb-reduction Tier-5 (union/match cluster C2): a `.to_dict()` whose
            # CALLEE slot wants the faithful heterogeneous `map string (option hval)`
            # (flag set by the arg-lowering in `_handle_call_expr`) projects the stmt
            # record to that pymap via the uninterpreted `stmt_to_pymap` — a SOUND
            # over-approx (the callee reads arbitrary hvals off the map) that CONSUMES
            # the real receiver (`_rw`, non-vacuous). Gated on the flag (corpus-absent
            # pymap param) -> byte-inert.
            if getattr(self, "_todict_arg_wants_pymap", False):
                self._add_abstract_op(
                    "val stmt_to_pymap (x: 'a) : map string (option hval)")
                return f"(stmt_to_pymap {_rw})"
            self._add_abstract_op("val to_emit_ir (x: 'a) : emit_ir")
            return f"(to_emit_ir {_rw})"
        # item34.md CF4: `<set/dict>.copy()` (`declared_refs.copy()`) is IDENTITY in the
        # immutable-map model (a Why3 `map` is a value) — return the receiver map. @mutable_state.
        if (isinstance(func_name, str) and func_name.endswith(".copy")
                and not expr.get("args")
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _cr = func_name[:-len(".copy")]
            _cp = _cr.split(".")
            _cir = {"type": "Var", "name": _cp[0]}
            for _p in _cp[1:]:
                _cir = {"type": "Attribute", "object": _cir, "attr": _p}
            return self._expr_to_whyml(_cir, local_refs, invariant_ctx, subst)
        # list-comprehension-lowering.md L7: `re.findall(pat, s)` → an abstract `array
        # string` (a list of matched substrings) with STRING args — modeled BEFORE the
        # generic arg-coercion (which would hash the pattern literal to int). Content
        # unmodeled (sound); only the type + `len` matter. @mutable_state-gated.
        if (isinstance(func_name, str) and func_name.endswith(".findall")
                and len(expr.get("args", [])) == 2
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _a = expr["args"]
            _p = self._expr_to_whyml(_a[0], local_refs or set(), invariant_ctx, subst)
            _s = self._expr_to_whyml(_a[1], local_refs or set(), invariant_ctx, subst)
            self._add_abstract_op("val findall_str (pat s: string) : array string")
            return f"(findall_str {_p} {_s})"
        # item34.md CF5: `<string>.split(sep)` (whole-list form, `exc.split("|")`) → a name
        # list, seq-ified at the source (`snapshot`) → `seq string`. @mutable_state + string
        # receiver. Distinct from the `<split>[i]` element form (`str_split_elem_op`).
        if (isinstance(func_name, str) and func_name.endswith(".split")
                and len(expr.get("args", [])) == 1
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and self._is_string_expr({"type": "Var", "name": func_name[:-len(".split")]})):
            _sep = self._expr_to_whyml(expr["args"][0], local_refs or set(), invariant_ctx, subst)
            _recvw = self._expr_to_whyml(
                {"type": "Var", "name": func_name[:-len(".split")]}, local_refs or set(),
                invariant_ctx, subst)
            self._add_abstract_op("val str_split_op (s sep: string) : array string")
            self._seq_snapshot_op()
            return f"(snapshot (str_split_op {_recvw} {_sep}))"
        # no-more-int: `x.__str__()` / `super().__str__()` returns a `string` (the Python
        # str dunder), not the opaque int the generic dotted-call assigns — so a `-> str`
        # method returning `super().__str__()` (errors.py `message`) type-checks. Faithful and
        # universal; byte-clean (no corpus driver calls `.__str__()`).
        if (isinstance(func_name, str)
                and (func_name == "__str__" or func_name.endswith(".__str__"))
                and not expr.get("args")):
            self._add_abstract_op("val str_dunder_op () : string")
            return "(str_dunder_op ())"
        # item34.md CF2: `IRScanner.<pred>(<stmt-list>)` (e.g. `ends_with_return`,
        # `has_early_return`) is a bool predicate over a `array int` stmt list — its abstract
        # takes `array int` (matching the `list_comp_stmts` arg), not the default int.
        # @mutable_state-gated (the corpus's IRScanner calls, if any, keep the int param).
        # self-tcb-reduction `_compute_return_type` PATH(b): `IRScanner.find_return_type`
        # returns a WhyML type STRING (`"int"`/`"array string"`/…), so its abstract must
        # yield `string` — the value `return_type` local is then a real `string` and every
        # `return_type == "int"` / `return_type.startswith("(")` / `"," in return_type` and
        # the f-strings interpolating it lower to the FAITHFUL str_eq_op/str_startswith_op/
        # str_contains_op/str_concat_op rather than the int-hash facade. Scoped to the
        # emitting method -> the other (trusted-stub) callers in this file are byte-inert.
        if (isinstance(func_name, str) and func_name == "IRScanner.find_return_type"
                and len(expr.get("args", [])) == 1
                and str(getattr(self, "_current_emitting_func", "") or "")
                .endswith("_compute_return_type")):
            _mname = whyml_ident("IRScanner_find_return_type")
            _aw = self._expr_to_whyml(expr["args"][0], local_refs or set(), invariant_ctx, subst)
            self._add_abstract_op(f"val {_mname} (l: array int) : string")
            return f"({_mname} {_aw})"
        if (isinstance(func_name, str) and func_name.startswith("IRScanner.")
                and len(expr.get("args", [])) == 1
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _tail = func_name[len("IRScanner."):]
            _mname = whyml_ident("IRScanner_" + _tail)
            _aw = self._expr_to_whyml(expr["args"][0], local_refs or set(), invariant_ctx, subst)
            # item34.md CF5 (uniform seq): `find_*`/`collect_*` return a NAME-collection —
            # modelled as an immutable, reassignable `seq string` (a `ref (array _)` can't be
            # rebound). The abstract yields a fresh `array string`; `snapshot` at the SOURCE
            # makes it `seq string` so every downstream use is uniformly seq (no array/seq
            # mix). The `has_*`/`ends_with_*`/`uses_*` predicates stay int (bool).
            if _tail.startswith("find_") or _tail.startswith("collect_"):
                self._add_abstract_op(f"val {_mname} (l: array int) : array string")
                self._seq_snapshot_op()
                return f"(snapshot ({_mname} {_aw}))"
            self._add_abstract_op(f"val {_mname} (l: array int) : int")
            return f"({_mname} {_aw})"
        # self-ir-schema.md IR1: `self.ir.get("shared_vars", [])` → the typed slice
        # `(ir_shared_vars self.ir)` : `array sharedvar` (an opaque array of shared-var
        # records with string `name`/`mutex` fields). Content unmodeled; only the element
        # TYPE matters (so the comprehension over it is `array string`). @mutable_state.
        if (isinstance(func_name, str) and func_name == "self.ir.get"
                and len(expr.get("args", [])) >= 1
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _k0 = expr["args"][0]
            if (isinstance(_k0, dict) and _k0.get("type") == "String"
                    and _k0.get("value") == "shared_vars"):
                self._add_abstract_op("val ir_shared_vars (ir: int) : array sharedvar")
                return "(ir_shared_vars 0)"
        # A3 (bounded itertools): resolve `len(list(chain(…)))` / `len(chain(…))`
        # to a sum of `Array.length` BEFORE lowering the inner args, so the
        # opaque `chain_*`/`list_new` abstract ops are never emitted.
        if func_name == "len" and len(expr.get("args", [])) == 1:
            # value-model campaign incr5: `len(<emit_ir>.elts)` in a dict-type walker →
            # `irlen (elts_of recv)` (the MODELLED IrMkTupleN element count, not the opaque
            # `iter_length (args_of …)`). Checked before the generic iter-len fallback.
            _mt = self._mktuple_elts_recv_ir(expr["args"][0])
            if _mt is not None:
                return (f"(irlen (elts_of "
                        f"{self._expr_to_whyml(_mt, local_refs or set(), invariant_ctx, subst)}))")
            # B-C5: `len(<emit_ir>.get("args"))` → `nargs_of` (Call arity).
            _ar = self._emit_ir_args_recv_ir(expr["args"][0])
            if _ar is not None:
                return (f"(nargs_of {self._expr_to_whyml(_ar, local_refs or set(), invariant_ctx, subst)})")
            _le = self._iter_len_expr(expr["args"][0], local_refs or set())
            if _le is not None:
                return _le
        # self-tcb-reduction Tier-5 (union/match cluster C2): resolve the callee's
        # param types so a `.to_dict()` argument whose CALLEE slot is the faithful
        # heterogeneous `map string (option hval)` (e.g.
        # `self._match_subject_union_info(stmt.to_dict())`) projects the stmt record to
        # that pymap (`stmt_to_pymap`) instead of the emit_ir identity (`to_emit_ir`).
        # Gated on a `map string (option hval)` param slot (corpus-absent) -> byte-inert.
        _pt_for_args: List[str] = []
        if isinstance(func_name, str) and "." in func_name:
            try:
                _, _pt_for_args, _, _ = self._resolve_dotted_signature(func_name)
            except Exception:
                _pt_for_args = []
        args = []
        for _ai, _airr in enumerate(expr["args"]):
            _want_pymap = (_ai < len(_pt_for_args)
                           and _pt_for_args[_ai] == "map string (option hval)")
            _saved_wp = getattr(self, "_todict_arg_wants_pymap", False)
            if _want_pymap:
                self._todict_arg_wants_pymap = True
            try:
                args.append(self._expr_to_whyml(_airr, local_refs, invariant_ctx, subst))
            finally:
                self._todict_arg_wants_pymap = _saved_wp

        # faithful-string-op.md §3.1–3.3: `.replace`/`.lower`/`.upper`/`.strip` on a
        # string receiver → a faithful `string`-typed op, BEFORE the generic dotted-call
        # fallback (which would emit an opaque int). Gated on a string receiver, so
        # `datetime.replace`/`dataclasses.replace` (non-string) stay on the opaque path.
        _svm = self._handle_string_value_method(expr, args, local_refs, invariant_ctx, subst)
        if _svm is not None:
            return _svm

        # FAITHFUL READ-NAME LOWERING (null-terminated byte-field decode recognizer).
        # Recognize the EXACT idiom `arr[a:b].split(b'\x00')[0].decode('utf-8', ...)`
        # over a byte-array slice and lower it to the genuine codec TERM
        # `field_to_str arr a (b-a)` — a faithful Python->WhyML lowering (same trust
        # class as lowering `+` to integer add), NOT a per-program trust / val-shim.
        # Must run BEFORE the generic `decode` -> opaque-int / decode_str_n paths.
        if func_name == "decode":
            fd = self._recognize_field_decode_idiom(expr, local_refs,
                                                    invariant_ctx, subst)
            if fd is not None:
                return fd

        # sum-types: an applied `#@ datatype` constructor (`Circle(5)`) builds the variant.
        if func_name in self._constructors:
            return f"({func_name} {' '.join(args)})" if args else func_name

        # inductive.md: an applied inductive predicate (`even(0)`, `wf(JArr(h, s))`)
        # is a logic-level predicate application — emit `(p args)` directly (raw args,
        # no int-coercion, no abstract op), exactly like a constructor application.
        if func_name in getattr(self, "_inductive_preds", set()):
            p = whyml_ident(func_name.lower())
            return f"({p} {' '.join(args)})" if args else p

        # Axiom-backing logic functions (`_AXIOM_FUNCTIONS`, e.g.
        # `dir_lookup`/`slot_inode`/`slot_name` for UnixFs.Dir): a contract call
        # is a raw logic application bound to the registry symbol — NO int
        # coercion (args keep their faithful array/int/string types) and NO
        # arity-suffixed abstract op. This is the risk-2 binding: it ties
        # `_dir_lookup`'s ensures and the `name_present` rule to the SAME symbols
        # the axiom constrains, so the citation constrains the REAL scan.
        if func_name in getattr(self, "_axiom_logic_funcs", set()):
            return f"({func_name} {' '.join(args)})" if args else func_name

        # missing-bytes-struct-feature.md Phase 2 — struct.pack /
        # struct.unpack get a format-string-aware abstract emission
        # before falling through to the generic dotted-call path.
        if func_name in ("struct.pack", "struct.unpack"):
            handled = self._handle_struct_call(expr, args, func_name)
            if handled is not None:
                return handled
            # fmt is dynamic / unsupported chars → fall through to
            # generic _handle_dotted_call (which auto-trusts).

        named = self._call_named_builtins(expr, args, func_name, local_refs,
                                          invariant_ctx, subst)
        if named is not None:
            return named
        # self-tcb-reduction (_canonical_preservation_ensures): `copy.deepcopy(<emit_ir>)`
        # is IDENTITY on an immutable emit_ir sub-node — the deep copy of an already-built
        # IR expression is that same expression (the emit_ir ADT is a pure immutable value,
        # so a structural copy is observationally equal). Lower it to its single argument,
        # NOT the opaque auto-trusted `copy_deepcopy_1` val (which would be unbound + wrongly
        # int-typed, breaking the emit_ir-typed `IrBinOp` slot it feeds). Gated on the method
        # sentinel → byte-inert for the corpus (which never calls `copy.deepcopy` in a
        # verified body under this scope) and every other mirror.
        _cef_dc = getattr(self, "_current_emitting_func", None) or ""
        if (func_name == "copy.deepcopy" and len(args) == 1
                and (_cef_dc == "_canonical_preservation_ensures"
                     or _cef_dc.endswith("___canonical_preservation_ensures"))):
            return args[0]
        if "." in func_name:
            # KEYWORD ACTUALS ON A DOTTED CALL (pyast ctor family, increment 13). Before
            # this, `_handle_dotted_call` received only the POSITIONAL args, so a keyword
            # actual was DROPPED ENTIRELY: `self.for_stmt(async_=False)` emitted
            # `(_parser__for_stmt self)` — a PARTIAL application of type
            # `int -> emit_ir`, which then ill-types wherever the result is used
            # (measured on `statement`'s one-element statement lists). Python binds
            # keywords BY NAME, so bind them into their formal POSITIONS from the callee's
            # declared `formal_params` and pass the completed positional list. Applied
            # only when EVERY keyword names a formal beyond the positional prefix and the
            # result is gap-free, so a partially-bound or unknown-keyword call is left
            # exactly as it is today (fail-closed, byte-identical). A callee with no
            # recorded formals is untouched, which is every corpus dotted call.
            if expr.get("keywords") and func_name.startswith("self."):
                _tail = func_name[len("self."):]
                _cls = self._current_self_type or ""
                _fpm = getattr(self, "_module_method_formal_params", {})
                # Two spellings are in use for this map's key — the RAW
                # `<self_type>__<method>` (`_resolve_dotted_signature`) and the
                # `whyml_ident`-normalised one (`_handle_dotted_call`'s R7 default fill).
                # Try both rather than guess.
                _formals = list(_fpm.get(f"{_cls}__{_tail}")
                                or _fpm.get(whyml_ident(f"{_cls}__{_tail}"))
                                or [])
                _kw = {k.get("arg"): k for k in expr["keywords"]
                       if isinstance(k, dict) and isinstance(k.get("arg"), str)}
                if (_formals and len(args) <= len(_formals)
                        and _kw and set(_kw) <= set(_formals[len(args):])):
                    _slots = list(args) + [None] * (len(_formals) - len(args))
                    for _i, _nm in enumerate(_formals):
                        if _i < len(args) or _nm not in _kw:
                            continue
                        _slots[_i] = self._expr_to_whyml(
                            _kw[_nm].get("value"), local_refs, invariant_ctx, subst)
                    # Gap-free prefix only: stop at the first unbound slot rather than
                    # emitting a hole.
                    _bound = []
                    for _v in _slots:
                        if _v is None:
                            break
                        _bound.append(_v)
                    # A gap-free prefix is enough — it does NOT have to reach the full
                    # arity. `self.funcdef([], async_=False)` against
                    # `funcdef(self, decorators, async_, start=None)` binds slots 0 and 1
                    # and leaves `start` unbound; requiring `len(_bound) == len(_formals)`
                    # threw the whole binding away and re-emitted the PARTIAL application
                    # `(_parser__funcdef self <decorators>)` of type `int -> int -> emit_ir`
                    # — the last blocker on `statement`. `_handle_dotted_call`'s R7 default
                    # fill completes the tail from `_module_method_param_defaults`
                    # (`start=None` -> its faithful zero), which is exactly Python's own
                    # rule. STILL FAIL-CLOSED: the prefix must actually cover every keyword,
                    # so a keyword sitting BEYOND the first gap can never be silently
                    # dropped (that erasure is what increment 13 repaired), and a prefix no
                    # longer than the positional args changes nothing.
                    _kwpos = [_formals.index(_nm) for _nm in _kw]
                    if (len(_bound) >= len(_formals)
                            or (len(_bound) > len(args) and _kwpos
                                and max(_kwpos) < len(_bound))):
                        args = _bound
            return self._handle_dotted_call(func_name, args)
        # WL-07: lower any EXPLICIT keyword args (`Point(x=1, y=2)`) so a record
        # constructor binds its fields by name. Empty for a keyword-free call
        # (byte-identical). A `**kwargs` splat was never captured in the IR.
        kwargs_map: Dict[str, str] = {
            kw["arg"]: self._expr_to_whyml(kw["value"], local_refs, invariant_ctx, subst)
            for kw in (expr.get("keywords") or [])
            if isinstance(kw, dict) and isinstance(kw.get("arg"), str)
        }
        # self-tcb-reduction family-B (optional-field run): positions / keyword names
        # whose RAW actual is the `None` literal (`{"type":"None"}`, which `_expr_to_whyml`
        # lowers to the int witness `0`). Used by `_call_irnode_constructor` to map an
        # EXPLICIT `None` bound to an `iropt_str` optfield slot (`SharedDecl(name, None)`)
        # to `IrSNone` — faithful to `mutex=None` — instead of the ill-typed `IrSSome 0`.
        none_arg_indices: Set[int] = {
            i for i, a in enumerate(expr.get("args") or [])
            if isinstance(a, dict) and a.get("type") == "None"
        }
        none_kwargs: Set[str] = {
            kw["arg"] for kw in (expr.get("keywords") or [])
            if isinstance(kw, dict) and isinstance(kw.get("arg"), str)
            and isinstance(kw.get("value"), dict) and kw["value"].get("type") == "None"
        }
        # NODE-CTOR (self-tcb-reduction): a CLASS construction of a CSL-AST node
        # (`BinOp(left, op, right)`) inside the emitter model lowers to the SAME
        # `emit_ir` ADT constructor the equivalent DICT construction
        # (`{"type": "BinOp", "op": …, "left": …, "right": …}`,
        # `_lower_irnode_construction`) already lowers to — `(IrBinOp op left right)`.
        # Without this the construction is a `binop` RECORD literal that cannot unify
        # with the `emit_ir`-typed sibling/return positions the recursive-descent
        # chain threads it through. The ctor payload order comes from the SHARED
        # `_IRNODE_CTORS` table; the actual args are bound BY NAME off the class's
        # positional `__init__` params (dataclass field order), so a mismatch between
        # the class's field order and the ctor's payload order can never silently
        # mis-bind. Gated on @mutable_state (the emitter model) → corpus byte-identical.
        # TERM-vs-emit_ir CTOR NAME COLLISION (cursor-nest `parse_atom`). `Var` names BOTH
        # an arm of the certified `term` inductive (`proof2why3.ir.Var`) and an entry in
        # the SHARED `_IRNODE_CTORS` table, so `Var(name=ident)` in a `-> Term` method was
        # lowering to the emit_ir `IrVar` — the WRONG ADT, caught as
        # `has type emit_ir, but is expected to have type term`. When the name is an arm of
        # THIS file's `_term_adt_spec`, the term constructor wins. That spec is computed
        # from the file's OWN imported dataclass list (`compute_term_adt_spec`), so
        # membership already means "this module's `Var` is the term arm"; a file that does
        # not import the Term union has no `_term_adt_spec` and is untouched.
        _tspec_ctors = (getattr(self, "_term_adt_spec", None) or {}).get("ctors") or {}
        if func_name in _tspec_ctors:
            _t_first = self._call_term_constructor(
                args, func_name, kwargs_map,
                raw_args=list(expr.get("args") or []),
                raw_kwargs={kw["arg"]: kw.get("value")
                            for kw in (expr.get("keywords") or [])
                            if isinstance(kw, dict) and isinstance(kw.get("arg"), str)},
                elt_lower=(lambda _n: self._expr_to_whyml(
                    _n, local_refs, invariant_ctx, subst)))
            if _t_first is not None:
                return _t_first
        adt = self._call_irnode_constructor(
            args, func_name, kwargs_map, none_arg_indices, none_kwargs,
            # PYTHON-AST NODE CTOR FAMILY (increment 13): the RAW keyword IR, needed for
            # an `iropt_ir` optional slot. By the time a kwarg reaches `kwargs_map` it has
            # already been lowered with the SENTINEL projection
            # (`match !value with Arm_9_0 _v -> _v | _ -> IrOther ""`), which models the
            # ABSENT value as a NODE — the erasure the option slot exists to prevent. The
            # raw node lets the slot re-lower it into `IrOSome`/`IrONone`.
            raw_kwargs={kw["arg"]: kw.get("value")
                        for kw in (expr.get("keywords") or [])
                        if isinstance(kw, dict) and isinstance(kw.get("arg"), str)},
            # INLINE CONST-DICT INDEX: the `pyconst_val` slot needs to lower the dict
            # literal's KEY EXPRESSION, which requires the deref environment
            # (`local_refs`) this frame has and the constructor does not. Same device
            # `_call_term_constructor` already uses one call above.
            elt_lower=(lambda _n: self._expr_to_whyml(
                _n, local_refs, invariant_ctx, subst)))
        if adt is not None:
            return adt
        # TERM CARRIER (L13): a term-ADT arm class construction lowers to the certified
        # inductive's constructor, not to the mutable int-erased dataclass record. Tried
        # BEFORE `_call_record_constructor` (which would otherwise win and emit the
        # record); fail-closed, so anything it declines still reaches the record path.
        tadt = self._call_term_constructor(
            args, func_name, kwargs_map,
            raw_args=list(expr.get("args") or []),
            raw_kwargs={kw["arg"]: kw.get("value")
                        for kw in (expr.get("keywords") or [])
                        if isinstance(kw, dict) and isinstance(kw.get("arg"), str)},
            elt_lower=(lambda _n: self._expr_to_whyml(
                _n, local_refs, invariant_ctx, subst)))
        if tadt is not None:
            return tadt
        rec = self._call_record_constructor(
            args, func_name, kwargs_map,
            {kw["arg"]: kw.get("value") for kw in (expr.get("keywords") or [])
             if isinstance(kw, dict) and isinstance(kw.get("arg"), str)})
        if rec is not None:
            return rec
        enc_lit = self._encode_string_literal(expr, local_refs, invariant_ctx, subst)
        if enc_lit is not None:
            return enc_lit
        bytes_call = self._call_bytes_methods(args, func_name)
        if bytes_call is not None:
            return bytes_call
        # str-list-elements: `bytes.decode(...)` produces a `str`. When the surrounding
        # assignment binds the result to a STRING-typed local (`self._decode_to_string`),
        # lower it to a string-returning val so the decoded `name` is a `string` (feeding
        # `seq string` / a string-typed consumer like sys_stat). Otherwise decode stays in
        # the legacy opaque INT model (byte-identical for every non-string-list caller).
        if func_name == "decode" and getattr(self, "_decode_to_string", False):
            n = len(args)
            arity_fn = f"decode_str_{n}"
            if n == 0:
                self._add_abstract_op(f"val {arity_fn} () : string")
                return f"({arity_fn} ())"
            params = " ".join(f"(x{i}: int)" for i in range(n))
            self._add_abstract_op(f"val {arity_fn} {params} : string")
            coerced = [self._coerce_to_int(a) for a in args]
            return f"({arity_fn} {' '.join(coerced)})"
        # richer-contracts-bridge C1 (S-c1): a certified predicate/function from the
        # preamble pyval theory (`_pydict_theory_lines`) applied in a `#@ ensures`
        # to `\result` — `wf_ir(\result)` / `size(\result)` — lowers to a DIRECT
        # application `(wf_ir result)` / `(size result)`, NOT the opaque numbered
        # `val <fn>_1 (x0:int):int` the unknown-call fallback fabricates (unbound +
        # wrongly int-typed, breaking the pyval-shaped `\result`). The induction is
        # done ONCE in Rocq/Lean (Phase2c `wf_ir_binds` / `size_pos`); SMT only
        # applies the predicate to the constructor spine. Corpus-inert (no reference
        # contract names these — byte-diff 0); a missing theory is a LOUD
        # unbound-symbol error, never a false proof.
        _cert_arity = self._CERTIFIED_PYVAL_ARITY.get(func_name)
        if (getattr(self, "_in_spec", False) and _cert_arity is not None
                and len(args) == _cert_arity):
            # M1 size-rename: the pyval measure is emitted as `pv_size` (it no longer
            # collides with the emit_ir `size`); the contract-facing name stays `size`
            # (user writes `size(\result)`), so translate ONLY the pyval measure symbol
            # here. size_list/size_dict keep their (non-colliding) names.
            _emit_name = "pv_size" if func_name == "size" else func_name
            return f"({_emit_name} {' '.join(args)})"
        safe_fn = whyml_ident(func_name)
        if (func_name not in local_refs
                and func_name not in self._current_params
                and safe_fn not in self._module_func_names):
            # 11-0632-spec-8 Part 2 (safety net, NARROW): in CONTRACT/formula
            # position (`_in_spec`), an unknown applied symbol is a LOGIC predicate
            # reference (a `present(filepath)`-shaped contract symbol whose decl did
            # NOT cross the import boundary — e.g. the dependency forgot to declare it,
            # or a shape Part 1 does not yet carry). A program `val …:int` is illegal
            # in `ensures`/`requires`, so emit a logic `predicate`/`function` instead,
            # with arg types recovered from the enclosing stub's symbol table (NOT the
            # int model). Part 1 always wins when it can supply the real decl (then
            # `func_name` is in `_inductive_preds` and this arm is never reached). This
            # fires ONLY in `_in_spec` AND while emitting a bodyless `val`/trusted-stub
            # contract (`_emitting_val_contract`) — body-position unannotated calls keep
            # the program `val` below, and a real `let` function whose `ensures`
            # references a symbol it ALSO program-calls (0386) keeps its program `val`.
            if (getattr(self, "_in_spec", False)
                    and getattr(self, "_emitting_val_contract", False)):
                logic = self._emit_contract_logic_symbol(func_name, expr, args)
                if logic is not None:
                    return logic
            # Unannotated callee: no signature is known, so the abstract op and
            # its args stay in the int model.
            coerced_args = [self._coerce_to_int(a) for a in args]
            n = len(coerced_args)
            arity_fn = f"{safe_fn}_{n}"
            if n == 0:
                self._add_abstract_op(f"val {arity_fn} () : int")
            else:
                self._add_abstract_op(
                    f"val {arity_fn} {' '.join(f'(x{i}: int)' for i in range(n))} : int")
            # Strict-propagation mode (workplan §1.4): an unannotated
            # callee called from a function with `no_exception` is
            # treated pessimistically. Default mode preserves backward
            # compat — ambient.
            inner = f"({arity_fn} {' '.join(coerced_args) if coerced_args else '()'})"
            return self._wrap_unannotated_call_with_strict_assert(inner)
        # 1111-spec R7 (no-more-int): if the call passes fewer args than the callee
        # arity, fill the missing trailing params from the callee's positional
        # defaults (lowered at the param's real type via R5 below) so the application
        # is total — never a partial application. A missing param with no default is a
        # hard error, not a silent partial application.
        formal_params = self._module_method_formal_params.get(func_name, [])
        # W8 capability (ii) — VARARG CALL-SITE PACKING. When the callee's last formal
        # is a `*vals: str` vararg, the call is VARIADIC: every trailing positional
        # argument is packed into the `seq string` the callee receives, so
        # `at_op("+", "-")` -> `(Seq.cons "+" (Seq.cons "-" (Seq.empty: seq string)))`
        # and `at_name()` -> the empty seq. This is what makes the membership
        # `seq_mem_str t.string vals` MEAN what Python means: the callee's `vals` is
        # provably the caller's literal list, so a caller-side mutation of the literals
        # changes the goal. Without it the fixed-arity check rejects the call outright.
        _va_name = getattr(self, "_module_method_vararg_str", {}).get(func_name)
        if _va_name and formal_params and formal_params[-1] == _va_name:
            _fixed = len(formal_params) - 1
            _tail = args[_fixed:]
            _packed = "(Seq.empty: seq string)"
            for _t in reversed(_tail):
                _packed = f"(Seq.cons {_t} {_packed})"
            args = args[:_fixed] + [_packed]
        # KEYWORD ARGUMENTS ON A MODULE-LEVEL CALL (relaunch #11) — a FAITHFULNESS repair.
        # `args` above is built from the POSITIONAL arguments only, and the trailing
        # parameters were then filled from the callee's DEFAULTS. A call that passes an
        # explicit KEYWORD therefore emitted the DEFAULT instead of the value the caller
        # wrote: `_merge_str_constants(values, drop_empty=False)` emitted
        # `_merge_str_constants … 1`, i.e. `True`. Measured with a probe (the same call
        # written positionally emits the real value), so this is a silent
        # wrong-argument lowering, not a missing feature. Python binds a keyword only to a
        # parameter no positional reached, so binding by name from `len(args)` onward is
        # exactly Python's rule; a parameter with neither a keyword nor a default still
        # raises the arity error below.
        _kwvals = {kw["arg"]: kw.get("value")
                   for kw in (expr.get("keywords") or [])
                   if isinstance(kw, dict) and isinstance(kw.get("arg"), str)}
        if formal_params and _kwvals and len(args) < len(formal_params):
            _bound_kw = 0
            for nm in formal_params[len(args):]:
                if nm not in _kwvals:
                    break
                args = args + [self._expr_to_whyml(_kwvals[nm], local_refs,
                                                   invariant_ctx, subst)]
                _bound_kw += 1
        if formal_params and len(args) < len(formal_params):
            defaults = self._module_method_param_defaults.get(func_name, {})
            for nm in formal_params[len(args):]:
                if nm in _kwvals:
                    args = args + [self._expr_to_whyml(_kwvals[nm], local_refs,
                                                       invariant_ctx, subst)]
                    continue
                if nm in defaults:
                    # 10-1732-gap (Gap 3, no-more-int): a `None` default on a non-int
                    # param lowers to the int-model sentinel `0`, which is ill-typed
                    # against a `string`/`real` param. Fill the param's FAITHFUL zero
                    # instead, keyed on the by-name WhyML param-type map (covers
                    # imported `\trusted` stubs, built from the same funcs_for_maps).
                    # Scope: str/real (R3); any other non-int type falls back to `0`
                    # (status quo, no worse than today — record/array/map deferred).
                    dflt_ir = defaults[nm]
                    pwt = getattr(self, "_module_method_param_whyml_types", {}).get(
                        func_name, {}).get(nm, "int")
                    if dflt_ir.get("type") == "None" and pwt != "int":
                        filled = {"string": '""', "real": "0.0"}.get(pwt, "0")
                    else:
                        filled = self._expr_to_whyml(dflt_ir, local_refs,
                                                     invariant_ctx, subst)
                    args = args + [filled]
                else:
                    from errors import PyCSLSemanticError
                    raise PyCSLSemanticError(
                        f"call to '{func_name}' passes {len(expr.get('args', []))} "
                        f"positional argument(s) but parameter '{nm}' has no default "
                        f"(arity {len(formal_params)}).")
        # Known module function (incl. an imported trusted stub). Coerce each arg to
        # the callee's REAL declared parameter type (1111-spec R5, no-more-int): a
        # `string` arg to a `string` param flows as a Why3 string, NOT an int hash; a
        # `list` arg to an `array int` param stays an array; etc. Without the
        # signature, fall back to the int model.
        param_types = self._module_method_param_types.get(func_name, [])
        # PYTHON-AST NODE CTOR FAMILY (relaunch #11), lesson (am) — TWO PRODUCERS, again,
        # this time on a MODULE-LEVEL function. `_module_method_param_types` is built from
        # the collapsed `_symtype_to_whyml("list")` and says `array int`, while
        # `functions._param_type_str` — the producer of the callee's ACTUAL emitted `val`
        # — renders a `List["ExprIR"]` param as `array emit_ir`. Coercing against the
        # registry bridged a `seq emit_ir` actual with the INT `materialize`
        # (`seq int -> array int`), an L3-tc error at `_merge_str_constants (materialize
        # !values)`. The method path already carries this repair inside
        # `_option_record_param_upgrade`; a module function reaches neither. Restore the
        # emitted shape from the SAME source both producers read.
        _mf = next((f for f in ((getattr(self, "ir", None) or {}).get("functions") or [])
                    if f.get("name") == func_name), None)
        if param_types and _mf is not None:
            _mfl = _mf.get("param_list_flat_elem") or {}
            _mformal = list(_mf.get("formal_params") or [])
            if _mfl and len(_mformal) == len(param_types):
                param_types = [
                    ("array emit_ir"
                     if (param_types[_i] == "array int"
                         and _mfl.get(_mformal[_i]) == "emit_ir")
                     else param_types[_i])
                    for _i in range(len(param_types))]
        if param_types:
            coerced_args = self._coerce_dotted_args(args, param_types[:len(args)])
        else:
            coerced_args = [self._coerce_to_int(a) for a in args]
        # wrong-lowering-to-fix.md §WL-05b: a callee that item-mutates a dict/set param
        # takes it as a caller-visible `ref (map …)`. At the call site the argument at
        # that position must be the BARE ref (the caller's local dict or its own
        # promoted param), NOT the dereferenced value `!d` — so the mutation escapes.
        # The fixpoint guarantees any Var landing here IS a ref (`_dict_locals` /
        # `_mutated_collection_params`). Empty map → untouched → byte-identical.
        _cmp = getattr(self, "_func_mutated_collection_params", {}).get(func_name)
        if _cmp:
            _cf = getattr(self, "_module_method_formal_params", {}).get(func_name, [])
            _arg_irs = expr.get("args", []) or []
            for _i, _a in enumerate(_arg_irs):
                if _i >= len(coerced_args) or _i >= len(_cf):
                    break
                if _cf[_i] in _cmp and isinstance(_a, dict) and _a.get("type") == "Var":
                    coerced_args[_i] = whyml_ident(_a.get("name", ""))
        # User-function call site. Look up the callee's raises summary;
        # if any clause names an exception the caller has committed to
        # avoid, prepend an assertion that the raises condition cannot
        # hold under the actual args.
        inner = f"({safe_fn} {' '.join(coerced_args) if coerced_args else '()'})"
        return self._wrap_call_with_callee_raises_assert(func_name, inner, args)

    def _content_string_method(self, expr: Dict[str, Any], args: List[str],
                               func_name: str, local_refs: Set[str],
                               invariant_ctx: bool,
                               subst: Optional[Dict[str, str]]) -> Optional[str]:
        """strings-plan Stage 3: content-aware `str` methods with a substring-based witness.

        `s.startswith(p)` / `s.endswith(p)` / `s.find(sub)` are lowered to abstract ops whose
        `ensures` relate the (int) result to `String.substring` over the *receiver as an
        operand*. Applies to ANY string-valued receiver — a simple `str`-typed name OR a
        derived string expression (`(a + b).startswith(a)`, `s[i:].startswith(p)`), lowered
        through `_str_method_recv_and_tail` (cleared-string.md S6). Only a MULTI-dot receiver
        (`self.name.startswith(…)`) or a non-string receiver falls through to the opaque
        baked-into-the-name predicate path. startswith/endswith keep the 0/1 int result (so
        control-flow / `\result ∈ {0,1}` uses are unaffected) and gain a
        `(result = 1) <-> <substring condition>` clause; find returns an index ≥ -1 with a
        found-index witness."""
        recv_ir, method = self._str_method_recv_and_tail(expr)
        if method not in ("startswith", "endswith", "find"):
            return None
        # Optional[str] receiver (dict-value-nu lever): `nu.startswith(p)` /
        # `nu.endswith(p)` where `nu` is an `Optional[str]` (a `_union_*` with a single
        # `str` Some-arm) — option-unwrap the receiver and apply the SAME faithful
        # substring op to the carried string, defaulting the None arm to 0 (Python guards
        # None before the call, e.g. `nu and nu.startswith(...)`). Never the opaque
        # `nu_startswith_1 <hash>` facade (receiver erased, literal int-hashed). Keeps the
        # 0/1 int result (a truthiness/control-flow use). Body context only. Corpus-inert:
        # no corpus program calls `.startswith`/`.endswith` on an `Optional[str]`.
        if (method in ("startswith", "endswith") and not self._in_spec
                and recv_ir is not None and not self._is_string_expr(recv_ir)):
            _octor = self._optional_str_union_ctor(recv_ir)
            if (_octor is not None and len(args) == 1
                    and self._is_string_expr(expr["args"][0])):
                _recv = self._expr_to_whyml(recv_ir, local_refs, invariant_ctx, subst)
                _p = args[0]
                if method == "startswith":
                    self._add_abstract_op(
                        "val str_startswith_op (s: string) (prefix: string) : int\n"
                        "    ensures { (result = 0) || (result = 1) }\n"
                        "    ensures { (result = 1) <->\n"
                        "      (String.length prefix <= String.length s /\\\n"
                        "       String.substring s 0 (String.length prefix) = prefix) }")
                    _sop = f"(str_startswith_op _s {_p})"
                else:
                    self._add_abstract_op(
                        "val str_endswith_op (s: string) (suffix: string) : int\n"
                        "    ensures { (result = 0) || (result = 1) }\n"
                        "    ensures { (result = 1) <->\n"
                        "      (String.length suffix <= String.length s /\\\n"
                        "       String.substring s (String.length s - String.length suffix)\n"
                        "         (String.length suffix) = suffix) }")
                    _sop = f"(str_endswith_op _s {_p})"
                return f"(match {_recv} with {_octor} _s -> {_sop} | _ -> 0 end)"
        if recv_ir is None or not self._is_string_expr(recv_ir):
            return None
        if len(args) != 1 or not self._is_string_expr(expr["args"][0]):
            return None
        r = self._expr_to_whyml(recv_ir, local_refs, invariant_ctx, subst)
        p = args[0]
        if method == "startswith":
            self._add_abstract_op(
                "val str_startswith_op (s: string) (prefix: string) : int\n"
                "    ensures { (result = 0) || (result = 1) }\n"
                "    ensures { (result = 1) <->\n"
                "      (String.length prefix <= String.length s /\\\n"
                "       String.substring s 0 (String.length prefix) = prefix) }")
            return f"(str_startswith_op {r} {p})"
        if method == "endswith":
            self._add_abstract_op(
                "val str_endswith_op (s: string) (suffix: string) : int\n"
                "    ensures { (result = 0) || (result = 1) }\n"
                "    ensures { (result = 1) <->\n"
                "      (String.length suffix <= String.length s /\\\n"
                "       String.substring s (String.length s - String.length suffix)\n"
                "         (String.length suffix) = suffix) }")
            return f"(str_endswith_op {r} {p})"
        # find — first-occurrence index, or -1
        self._add_abstract_op(
            "val str_find_op (s: string) (sub: string) : int\n"
            "    ensures { result >= -1 }\n"
            "    ensures { (result >= 0) ->\n"
            "      (result + String.length sub <= String.length s /\\\n"
            "       String.substring s result (String.length sub) = sub) }")
        return f"(str_find_op {r} {p})"

    def _try_emit_any_all_fold(self, func_name, expr, local_refs, invariant_ctx, subst):
        """genexp-erasure-wall R2b: `any(P(x) for x in it)` / `all(...)` -> a bounded,
        executable, iff-specified fold. Returns None to fall back to the oracle.

        Before this, BOTH planes lowered these to `val any_1 (a: array int) : bool` — an
        UNCONSTRAINED oracle applied to a fabricated `Array.make 1 0` — so the iterable and the
        predicate were both erased and the proof said nothing (wall-lessons (l)). The shape
        emitted here is the reviewer's `anyfold.mlw`, proven Valid on z3 AND Alt-Ergo with a
        positive driver and a working evil twin, axiom-free.

        Deliberately NARROW: exactly one generator, no `if` filters, an iterable that lowers to
        an `array int`, and a predicate that lowers to a boolean usable in BOTH the program body
        and the logic annotations. Anything else returns None and keeps the old behaviour, so
        this cannot perturb a shape it does not fully model."""
        arg_irs = expr.get("args") or []
        if len(arg_irs) != 1 or not isinstance(arg_irs[0], dict):
            return None
        comp = arg_irs[0]
        if comp.get("type") not in ("GenExp", "ListComp"):
            return None
        gens = comp.get("generators") or []
        if len(gens) != 1 or not isinstance(gens[0], dict):
            return None
        gen = gens[0]
        if gen.get("ifs"):
            return None                      # filtered comprehension — not modelled here
        target = gen.get("target")
        if not isinstance(target, str) or not target or target == "_comp_var":
            return None
        arr = self._expr_to_whyml(gen.get("iter") or {}, local_refs, invariant_ctx, subst)
        if not arr or not arr.strip() or arr.strip() == "0":
            return None                      # iterable itself erased — nothing to fold over
        arr = arr.strip()
        # cap5 (self-tcb-reduction `_refine_tuple_return_type`): a fold over an `array string`
        # refine list-comp local (`any(s != "int" for s in slots)` / `all(x != "int" for x in
        # _s)`) is typed `array string`, its predicate a FAITHFUL string comparison. Handled
        # by a dedicated builder (below), which lowers the predicate in the logic plane
        # (spec/invariant, polymorphic `<>`) and the program plane (loop body, `str_eq_op`)
        # separately. Method-gated + an `array string` refine iterable -> corpus/mirror inert.
        _it = gen.get("iter") or {}
        if (self._emitting_refine_tuple_return_type()
                and isinstance(_it, dict) and _it.get("type") == "Var"
                and _it.get("name") in getattr(self, "_refine_str_comp_locals", set())):
            return self._try_emit_refine_str_fold(
                func_name, comp, target, arr, local_refs, invariant_ctx, subst)
        # The predicate, with the bound variable substituted by the element read. `subst` is
        # exactly the emitter's binder-substitution channel, so the predicate is lowered ONCE
        # per position rather than pattern-matched.
        def _pred(elem: str) -> Optional[str]:
            sub = dict(subst or {})
            sub[target] = elem
            try:
                raw = self._expr_to_whyml(comp.get("elt") or {}, local_refs, invariant_ctx, sub)
            except Exception:
                return None
            if not raw or not raw.strip():
                return None
            raw = raw.strip()
            if elem not in raw:
                return None                  # bound variable did not survive -> erasure again
            return raw
        # The fold is a STANDALONE function over its own parameter `a` — substituting the
        # caller's array name would capture a variable that is not in scope there.
        _saved_ops = dict(self._abstract_ops)
        p_i = _pred("a[_fi]")
        p_k = _pred("a[_fk]")
        # `_expr_to_whyml` may register abstract ops as a side effect of lowering the
        # substituted element (it can read `a[_fi]` as an unknown name). Roll those back and
        # bail rather than emit a bogus `val constant a[_fi] : int`.
        if p_i is None or p_k is None:
            self._abstract_ops.clear()
            self._abstract_ops.update(_saved_ops)
            return None
        # Substituting a compound element expression where a NAME is expected makes the
        # emitter register it as an unknown constant (`val constant a[_fi] : int`). Drop those
        # specific artifacts — they are an artifact of the substitution, not of the predicate.
        # Any OTHER op the predicate genuinely needed is kept; if one appeared we cannot tell
        # whether it is well-formed inside the generated function, so bail instead.
        for _k in [k for k in self._abstract_ops if k not in _saved_ops]:
            if "[" in _k:
                del self._abstract_ops[_k]
            else:
                self._abstract_ops.clear()
                self._abstract_ops.update(_saved_ops)
                return None
        if func_name == "any":
            spec = "exists _fk. 0 <= _fk < Array.length a /\\ " + p_k
            inv = "exists _fk. 0 <= _fk < _fi /\\ " + p_k
            init, upd = "false", f"if {p_i} then _fr := true"
        else:
            spec = "forall _fk. 0 <= _fk < Array.length a -> " + p_k
            inv = "forall _fk. 0 <= _fk < _fi -> " + p_k
            init, upd = "true", f"if not ({p_i}) then _fr := false"
        # Name from the SPEC, so two identical folds share one definition.
        name = f"_{func_name}_fold_{stable_hash(spec) % 100000}"
        self._add_abstract_op(
            f"let function {name} (a: array int) : bool\n"
            f"    ensures {{ result <-> ({spec}) }}\n"
            f"  = let _fr = ref {init} in\n"
            f"    for _fi = 0 to Array.length a - 1 do\n"
            f"      invariant {{ !_fr <-> ({inv}) }}\n"
            f"      {upd}\n"
            f"    done; !_fr")
        return f"({name} {arr})"

    def _try_emit_refine_str_fold(self, func_name, comp, target, arr,
                                  local_refs, invariant_ctx, subst):
        """cap5 (self-tcb-reduction `_refine_tuple_return_type`): the `seq string` fold for
        `any(s != "int" for s in slots)` / `all(x != "int" for x in _s)`. Modeled as an
        abstract `val` whose `ensures` is the FAITHFUL string quantifier over the element
        predicate (the polymorphic logic `<>` — `a[_fk] <> "int"`, the seq mixfix Seq.get —
        legal in a spec on any type). Same satisfiable-spec pattern as `sorted_1`/`str_split_elem_op`:
        the ensures is a determinate, always-satisfiable property of `a`, so ASSUMING it is
        sound and NON-VACUOUS (it names the `"int"` literal — mutation-visible), unlike the
        old unconstrained `val any_1 (a: array int) : bool` oracle (predicate erased). A
        PROVEN `let function` body would need the `str_eq_op` program bridge (Why3 forbids
        `=`/`<>` on `string` in a program), which cannot be declared before a `let function`
        abstract op in the alphabetical block — hence the abstract-`val` form. Returns the
        fold call, or None to fall back to the oracle.

        The predicate is lowered ONCE in the LOGIC plane (`_in_spec=True`), with the element
        read (`a[_fk]`, the seq Seq.get mixfix) substituted for the bound variable and the
        target typed `string` so the `!=` routes to the polymorphic string disequality, not
        the int-hash. (A dotted `Seq.get` would be `whyml_ident`-mangled to `Seq_get`.)"""
        if getattr(self, "_string_local_vars", None) is None:
            self._string_local_vars = set()
        _elem = "a[_fk]"
        sub = dict(subst or {})
        sub[target] = _elem
        _sav_spec = self._in_spec
        _had = target in self._string_local_vars
        _saved_ops = dict(self._abstract_ops)
        self._in_spec = True
        self._string_local_vars.add(target)
        try:
            p_logic = self._expr_to_whyml(comp.get("elt") or {}, local_refs,
                                          invariant_ctx, sub)
        except Exception:
            p_logic = None
        finally:
            self._in_spec = _sav_spec
            if not _had:
                self._string_local_vars.discard(target)
        # Substituting the element read `a[_fk]` where a NAME is expected can register it as
        # an unknown constant (`val constant a[_fk] : int`); drop those substitution
        # artifacts. Any OTHER newly-registered op is unexpected (the logic predicate needs
        # none) — bail rather than emit it.
        for _k in [k for k in self._abstract_ops if k not in _saved_ops]:
            if "[" in _k:
                del self._abstract_ops[_k]
            else:
                self._abstract_ops.clear()
                self._abstract_ops.update(_saved_ops)
                return None
        if not p_logic or not p_logic.strip() or _elem not in p_logic:
            return None
        # The substituted `a[_fk]` survives `whyml_ident` mangling, but the `[]` mixfix is
        # AMBIGUOUS once both `array.Array` and `seq.Seq` are imported (Why3 resolves it to
        # Array.get). Rewrite it to the explicit `Seq.get a _fk` now the spec string is fully
        # built (the element token is unique, so the replace is exact).
        p_logic = p_logic.strip().replace(_elem, "(Seq.get a _fk)")
        if func_name == "any":
            spec = "exists _fk. 0 <= _fk < Seq.length a /\\ " + p_logic
        else:
            spec = "forall _fk. 0 <= _fk < Seq.length a -> " + p_logic
        name = f"strfold_{func_name}_{stable_hash(spec) % 100000}"
        self._add_abstract_op(
            f"val {name} (a: seq string) : bool\n"
            f"    ensures {{ result <-> ({spec}) }}")
        return f"({name} {arr})"

    def _call_named_builtins(self, expr: Dict[str, Any], args: List[str],
                             func_name: str, local_refs: Optional[Set[str]] = None,
                             invariant_ctx: bool = False,
                             subst: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Named builtins and built-in-method idioms: len / min / max / string-predicate
        methods / isinstance / set / sorted / any / all / dict / list / join /
        str|repr|int|bool|abs / sum / hasattr. Returns the WhyML string, or None to fall
        through to the generic call path. (Extracted verbatim from `_handle_call_expr`.)"""
        # no-more-int-3 A1 T1.2 (param-form) — `.get(k[, default])` on a
        # dict-typed Var receiver: faithful match against `Map.get`, NOT an
        # opaque `d_get_2` abstract op (which severs the result from the
        # receiver's contents). Returns the WhyML string, or None to fall
        # through to the generic dotted-call path (record-method `.get()` on
        # a class instance, a non-dict receiver, or a non-Var receiver).
        # typed-ir-for-b-ceiling.md §14: the `getattr(self, "<field>", <default>).get(k)`
        # idiom — the emitter's DEFENSIVE field access. The `.get`'s receiver is a
        # `getattr` Call, not a flat `self.<field>` name, so it would fall to the opaque
        # `get_1`. When the getattr names a DECLARED record dict/set field, rewrite the
        # receiver to `self.<field>` so `.get`/`.items`/… route to the real map field
        # (self-field dict reflection §12). Gated on @mutable_state → byte-identical.
        if (isinstance(func_name, str) and "." not in func_name
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _ga = self._getattr_self_field(expr.get("receiver"))
            if _ga and self._self_field_dict_nu(f"self.{_ga}") is not None:
                expr = dict(expr)
                expr["func"] = f"self.{_ga}.{func_name}"
                func_name = expr["func"]
                expr.pop("receiver", None)
        # `_compute_return_type` PATH(b): `getattr(self, "_dict_key_types"|
        # "_dict_value_types", {}).get(K)` reads a `map string (option string)` self-field
        # -> the opaque reader `<base>_get <K> : string` ("" for absent), NOT the int-erased
        # `get_1`. The key `K` may be the narrowed `option string` `_rv` -> unwrapped via a
        # `match … Some s -> s | None -> ""`. Per-method scoped -> byte-inert elsewhere.
        if (isinstance(func_name, str) and "." not in func_name
                and self._emitting_compute_return_type()):
            _dga = self._getattr_self_field(expr.get("receiver"))
            if _dga in ("_dict_key_types", "_dict_value_types"):
                _dgargs = expr.get("args") or []
                _kir = _dgargs[0] if _dgargs else {}
                _kw = self._expr_to_whyml(
                    _kir if isinstance(_kir, dict) else {}, local_refs or set(),
                    invariant_ctx, subst)
                if (isinstance(_kir, dict) and _kir.get("type") == "Var"
                        and _kir.get("name")
                        in getattr(self, "_option_str_return_vars", set())):
                    _kw = f"(match {_kw} with Some _s -> _s | None -> \"\" end)"
                _base = _dga.lstrip("_")
                self._add_abstract_op(f"val function {_base}_get (k: string) : string")
                return f"({_base}_get {_kw})"
        get_low = self._lower_dict_get_call(expr, args, func_name, local_refs,
                                            invariant_ctx, subst)
        if get_low is not None:
            return get_low
        if func_name == "len" and len(args) == 1:
            return self._handle_len_call(expr, args)
        if func_name in ("min", "max") and len(args) == 2:
            fn = "MinMax.min" if func_name == "min" else "MinMax.max"
            return f"({fn} {args[0]} {args[1]})"
        # strings-plan Stage 3: content-aware string methods on a simple `str`-typed
        # receiver. `s.startswith(p)`/`s.endswith(p)`/`s.find(sub)` get a substring-based
        # witness ensures (the receiver is lifted to an operand, unlike the opaque
        # baked-into-the-name predicates below, which apply to chained/non-str receivers).
        strm = self._content_string_method(expr, args, func_name, local_refs or set(),
                                           invariant_ctx, subst)
        if strm is not None:
            return strm
        # String predicate methods (`s.islower()`, `s.startswith(p)`, …) — model
        # as uninterpreted 0/1-valued ops, so a function that RETURNS the
        # predicate can prove `\result == 0 or \result == 1`. The value is not
        # related to the receiver (uninterpreted): design VCs on the predicate's
        # 0/1-ness or its control-flow consequence, not its concrete truth.
        if "." in func_name and func_name.rsplit(".", 1)[-1] in (
                "islower", "isupper", "isalpha", "isdigit", "isspace",
                "istitle", "isalnum", "isnumeric", "isdecimal",
                "isidentifier", "startswith", "endswith"):
            pname = whyml_ident(func_name.replace(".", "_")) + f"_{len(args)}"
            ens = "ensures { ((result = 0) || (result = 1)) }"
            if args:
                coerced = [self._coerce_to_int(a) for a in args]
                params = " ".join(f"(x{i}: int)" for i in range(len(args)))
                self._add_abstract_op(f"val {pname} {params} : int {ens}")
                return f"({pname} {' '.join(coerced)})"
            self._add_abstract_op(f"val {pname} () : int {ens}")
            return f"({pname} ())"
        # 07-0647-spec S3.2: a string predicate on a COMPUTED receiver
        # (`s[i].isdigit()`) arrives with a bare method `func` and the receiver in the
        # `receiver` field. The receiver MUST be passed as the first argument — emitting
        # a receiver-less `isdigit_0 ()` severs the result from the value tested (a silent
        # faithfulness violation). The op is still uninterpreted (0/1-valued).
        if (func_name in (
                "islower", "isupper", "isalpha", "isdigit", "isspace",
                "istitle", "isalnum", "isnumeric", "isdecimal",
                "isidentifier", "startswith", "endswith")
                and expr.get("receiver") is not None):
            recv = self._expr_to_whyml(expr["receiver"], local_refs, invariant_ctx, subst)
            # `args` are ALREADY lowered WhyML strings (set by `_handle_call_expr`); re-lowering
            # them via `_expr_to_whyml` crashes on the string (`'str' has no attribute
            # to_dict`). Exposed by self-annotating `<computed>.endswith(...)` (e.g.
            # `val_ir["func"].endswith(".to_dict")`); the corpus has no computed-receiver
            # isX/startswith/endswith, so this is byte-identical there.
            all_args = [recv] + list(args)
            pname = whyml_ident(func_name) + f"_{len(all_args)}"
            ens = "ensures { ((result = 0) || (result = 1)) }"
            # Each operand keeps its real type (the receiver of `s[i].isdigit()` is a
            # `string` char, not an int) — declare per-arg type variables so the
            # uninterpreted predicate accepts any operand types.
            params = " ".join(f"(x{i}: 'a{i})" for i in range(len(all_args)))
            self._add_abstract_op(f"val {pname} {params} : int {ens}")
            return f"({pname} {' '.join('(' + a + ')' for a in all_args)})"
        if func_name == "isinstance" and len(expr.get("args", [])) == 2:
            # 07-1839 P4: faithful metatype resolution — `subtag (\typeof x) T` (decided
            # from Γ's τ; base types via the subtag relation; symbolic at the `Any` tail).
            # Supersedes the old opaque `isinstance_check`.
            return self._handle_isinstance(expr, local_refs)
        if func_name == "getattr" and 2 <= len(expr.get("args", [])) <= 3:
            # `getattr(obj, name[, default])` — attribute access on an arbitrary object.
            # Sound lowering (additive; previously fell through to an opaque `getattr_N`
            # abstract val that mismatched on record-typed `self`):
            #  • If `obj` is a Var of a known record type and `name` is a string literal
            #    matching a declared field → emit the genuine record field access
            #    `obj.<field>` (lets `\result == self.f` postconditions prove).
            #  • Otherwise (the dynamic-config case `getattr(self, "_x", {})` where
            #    `_x` isn't a declared field) → emit the `default` argument directly.
            #    getattr DOES return default for an absent attribute, so this is sound;
            #    the actual runtime value is opaque to the prover (fails-safe: any
            #    contract depending on the real value fails to prove, never proves false).
            return self._lower_getattr(expr, args, local_refs, invariant_ctx, subst)
        if (func_name in ("set", "frozenset") and len(args) == 0
                and self._emitting_build_param_list()):
            # self-tcb-reduction WRITER class (`_build_param_list`): the method branch's
            # `set()` ref-params slot is modelled as the empty `seq string` (the same
            # sequence model as the else-branch comprehension result), so both return arms
            # agree on `(seq string, string)`. Gated -> byte-inert elsewhere.
            return "(Seq.empty: seq string)"
        if func_name in ("set", "frozenset") and len(args) == 0:
            # Body set: same `map int (option int)` model as body dicts.
            # Sets store `Some 0` for "present" keys, `None` for absent.
            return "(const (None: option int))"
        _cf5_ms = (getattr(self, "_current_self_type", None)
                   in getattr(self, "_mutable_state_classes", set()))
        if (func_name in ("set", "frozenset") and len(args) == 1 and _cf5_ms
                and expr.get("args") and isinstance(expr["args"][0], dict)
                and expr["args"][0].get("type") == "Call"
                and self._call_returns_seq_string(expr["args"][0].get("func", ""))):
            # item34.md CF5: `set(<seq string collection>)` is the same list (dedup unmodelled).
            return args[0]
        if (isinstance(func_name, str) and func_name.endswith(".get") and len(args) == 2
                and _cf5_ms and expr.get("args") and len(expr["args"]) == 2
                and isinstance(expr["args"][1], dict)
                and expr["args"][1].get("type") in ("ArrayLit", "ListLit", "List")
                and not self._is_emit_ir_expr(
                    {"type": "Var", "name": func_name[:-len(".get")]})):
            # item34.md CF5: `<handler>.get("body", [])` — list-default on a NON-emit_ir handler
            # dict → `array int` STMT-LIST (the `list_comp_stmts` node model consumed by
            # `find_assigned_vars`/`_stmts_to_whyml`). GATED off emit_ir receivers so
            # `val_ir.get("elts",[])` keeps its int-model `.get` path.
            _grecv = whyml_ident(func_name.replace(".", "_"))
            self._add_abstract_op(f"val {_grecv}_arr (k: string) : array int")
            return f"({_grecv}_arr {args[0]})"
        if (isinstance(func_name, str) and func_name.endswith(".get") and len(args) == 1
                and _cf5_ms and expr.get("args") and isinstance(expr["args"][0], dict)
                and expr["args"][0].get("type") == "String"
                and not self._is_emit_ir_expr(
                    {"type": "Var", "name": func_name[:-len(".get")]})):
            # item34.md CF5: `<handler>.get("exc_type")` — 1-arg string-key `.get` on a
            # non-emit_ir handler dict reads a string scalar field.
            _grecv = whyml_ident(func_name.replace(".", "_"))
            self._add_abstract_op(f"val {_grecv}_str (k: string) : string")
            return f"({_grecv}_str {args[0]})"
        if func_name == "sorted" and len(args) == 1:
            # item34.md CF5: `sorted(<seq string>)` → `seq string` (`sorted_seq`); the name
            # collections are seq. Dispatch on the arg being a seq-string local.
            _sa = expr.get("args", [{}])[0]
            if (_cf5_ms and isinstance(_sa, dict) and _sa.get("type") == "Var"
                    and _sa.get("name") in getattr(self, "_seq_locals", set())
                    and getattr(self, "_seq_value_types", {}).get(_sa.get("name")) == "string"):
                self._add_abstract_op("val sorted_seq (a: seq string) : seq string")
                return f"(sorted_seq !{whyml_ident(_sa['name'])})"
            # cleared-array.md S5 (spike-proven, S0-bis): `sorted(a)` over an
            # `array int` returns a permuted, sorted array with the SAME length.
            # The three facts are DEFINITIONAL `ensures` on the abstract `val`
            # (discharged where `sorted` is USED, NOT a global axiom):
            #   * `Array.length result = Array.length a`
            #   * adjacent sortedness — the exact formula `\is_sorted(result)`
            #     lowers to, so a driver's `\is_sorted(result)` matches directly;
            #   * `permut result a` — the SAME uninterpreted predicate
            #     `\permutation(result, a)` lowers to (arg order result,a), so a
            #     driver's `\permutation(result, a)` matches directly.
            # sortedness + permut + equal-length is satisfiable (a sorted
            # permutation always exists) → no vacuity; adding ensures is
            # monotone → cannot regress a prior opaque proof.
            self._add_abstract_op("predicate permut (a: array int) (b: array int)")
            self._add_abstract_op(
                "val sorted_1 (a: array int) : array int\n"
                "    ensures { Array.length result = Array.length a }\n"
                "    ensures { forall _si : int. 0 <= _si < Array.length result - 1 ->\n"
                "                result[_si] <= result[_si + 1] }\n"
                "    ensures { permut result a }")
            return f"(sorted_1 {self._array_coerce_arg(args[0])})"
        if func_name in ("any", "all") and len(args) == 1:
            # genexp-erasure-wall R2b: when the argument is a COMPREHENSION whose predicate
            # we can lower, emit a bounded, iff-specified fold instead of the unconstrained
            # oracle below. Falls back to the oracle for every shape it cannot handle.
            _fold = self._try_emit_any_all_fold(
                func_name, expr, local_refs, invariant_ctx, subst)
            if _fold is not None:
                return _fold
            # `any(iterable)` / `all(iterable)` over an array — abstract.
            # Unsupported iterable shapes (generator expressions etc.) get
            # dropped to `0` at the IR level; coerce that to an array
            # placeholder so the abstract val type-checks.
            self._add_abstract_op(
                f"val {func_name}_1 (a: array int) : bool")
            return f"({func_name}_1 {self._array_coerce_arg(args[0])})"
        if func_name == "dict" and len(args) == 0:
            # Body dict: empty `map int (option int)`. Parallel to
            # `\empty_map` (`_handle_map_empty_expr`).
            return "(const (None: option int))"
        if (func_name == "dict" and len(args) == 1
                and self._emitting_refine_tuple_return_type()):
            # self-tcb-reduction typed-self-field-WRITE cap (map-copy identity): `dict(symtab)`
            # where `symtab` is the projected `map string (option string)` symbol table is a
            # shallow COPY -> the value is identical to the source map (Why3 maps are pure/
            # immutable, so a copy is the identity). Emit the source map unchanged rather than
            # the int-erasing `dict_1` abstract. Gated on `_refine_tuple_return_type` -> inert.
            return args[0]
        if (func_name in ("defaultdict", "Counter", "OrderedDict")
                and func_name not in self._record_types):
            # collections-plan: the dict-family reduces to the empty
            # `map int (option int)`. The factory (`defaultdict(int)`) or
            # iterable (`Counter([...])`) arg is dropped — the missing-key
            # default IS the model's None→0, and a seeded iterable is modelled
            # as empty (a sound under-approximation: content that depends on
            # the seed fails to prove, never proves falsely). `OrderedDict`
            # insertion order is not modelled. The `not in _record_types` guard
            # lets a user-defined/imported class of the same name (e.g. corpus
            # 0441's `Counter`) fall through to `_call_record_constructor`.
            return "(const (None: option int))"
        if func_name == "list" and len(args) <= 1:
            # `list(X)` where X already lowered to an `array int` expression
            # (e.g. `list(reversed(xs))`) is the identity — pass it through.
            if args and args[0].lstrip("(").startswith(
                    ("array_rev ", "Array.", "array_slice ", "array_copy ")):
                return args[0]
            # `list(iterable)` semantics depend on the surrounding return
            # type. In a `List[T] -> array int` context, emit an abstract
            # array-returning val so the result type-checks at the
            # function boundary. Otherwise keep the legacy `int -> int`
            # shape (used as a counter/length hash in body-int contexts —
            # eg. `list(A) + list(B)` for Python list concatenation).
            if self._func_return_type == "array int":
                self._add_abstract_op("val list_new_arr (x: int) : array int")
                return f"(list_new_arr {args[0] if args else '0'})"
            self._add_abstract_op("val list_new (x: int) : int")
            return f"(list_new {args[0] if args else '0'})"
        if func_name in ("bytes", "bytearray") and len(args) <= 1:
            # 07-1321 S1: faithful bytes/bytearray construction. A bytes buffer is an
            # `array int` (no-more-int doctrine), and the constructor is LENGTH- and
            # ELEMENT-preserving so byte-packing functions can prove `\length(\result)`
            # and `\result[i]` postconditions — not merely type-correct. The argument
            # already lowers to an `array int` expression (array literal or array-typed
            # local), so it is passed through directly (NOT `_array_coerce_arg`, which
            # would clobber a `(let _alit = Array.make …)` literal to a placeholder).
            ctor = func_name
            if args:
                # WL-06d soundness: Python `bytes([...])`/`bytearray([...])` raises
                # `ValueError: bytes must be in range(0, 256)` if ANY source element is
                # outside [0,256). Model that ValueError as a PRECONDITION on the
                # constructor (the SAME way an IndexError bounds VC guards `b[i]`), so an
                # out-of-range element is FAIL-CLOSED (the range VC does not discharge)
                # instead of proving a false normal-return `\result[i] == <oor value>`.
                self._add_abstract_op(
                    f"val {ctor}_new (x: array int) : array int\n"
                    f"    requires {{ forall i:int. 0 <= i < Array.length x -> "
                    f"0 <= x[i] < 256 }}\n"
                    f"    ensures {{ Array.length result = Array.length x }}\n"
                    f"    ensures {{ forall i:int. 0 <= i < Array.length x -> "
                    f"result[i] = x[i] }}")
                # L2 (os-bodyvc-spec): a seq-promoted local (`parts = []; parts += …`) passed to
                # `bytes()` must materialize seq→array — `bytes_new` expects `array int`, the seq is
                # `seq int` (the `@rho` error). Reuses the return-arr materialize bridge, now at a
                # call-arg boundary (it already covers return boundaries).
                arg0 = self._materialize_if_seq(args[0], expr.get("args", [{}])[0])
                return f"({ctor}_new {arg0})"
            self._add_abstract_op(
                f"val {ctor}_empty () : array int\n"
                f"    ensures {{ Array.length result = 0 }}")
            return f"({ctor}_empty ())"
        if func_name == "json_mirror" and len(args) == 1:
            # no-more-int A4: `json_mirror(x)` over a recursive `#@ datatype Json`
            # is an abstract `json → json` op (`val function` — program-callable
            # AND constrainable by a logic axiom). The imported inductive lemma
            # `mirror_involution : forall x. json_mirror (json_mirror x) = x`
            # (proved by structural induction in Rocq/Lean) discharges
            # `mirror(mirror(x)) == x` — testing the bridge on an INDUCTIVE
            # property over a recursive datatype (vs the flat 0537–0539).
            self._add_abstract_op("val function json_mirror (x: json) : json")
            return f"(json_mirror {args[0]})"
        if func_name == "reversed" and len(args) == 1:
            # no-more-int A2b Gap 5: `reversed(xs)` models the reversed sequence
            # as an abstract `array int` op `array_rev` (a `val function` — both
            # program-callable and constrainable by a logic axiom). The
            # `permut (array_rev s) s` framing lemma (imported via `#@ proof`)
            # is what proves `\permutation(reversed(xs), xs)`; uncited, it stays
            # an opaque reversal. `list(reversed(xs))` passes the array through.
            self._add_abstract_op(
                "val function array_rev (a: array int) : array int")
            return f"(array_rev {self._array_coerce_arg(args[0])})"
        if func_name == "join" and len(args) == 1:
            return self._handle_join_call(expr, args, local_refs, invariant_ctx, subst)
        if func_name == "hash" and len(args) == 1:
            # G2 strings: `hash(s)` of a string routes to the existing `str_hash_op`
            # (an uninterpreted `string -> int`) — yielding an int usable as a dict/set
            # key, over a real Why3 string (no int-coercion). A non-string `hash(x)` keeps
            # the generic call fallback below.
            arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
            if self._is_string_expr(arg_ir):
                self._add_abstract_op("val str_hash_op (s: string) : int")
                return f"(str_hash_op {args[0]})"
        # 10-2300-spec-5: the `ord`/`chr` char<->int bridge. Handled here — BEFORE the
        # generic unannotated-callee path (which would declare `val ord_1 (x: int) : int`
        # and mis-type the 1-char STRING arg of `ord(name[i])`). `ord_op`/`chr_op` are
        # total abstract vals pinned by `string.Char`'s `code`/`chr`/`get` (no axiom).
        if func_name == "ord" and len(args) == 1:
            arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
            if self._is_string_expr(arg_ir):
                # string-codec Phase A': context-dependent lowering. In a CONTRACT
                # (logic context) `ord` MUST lower to the pure `string.Char` logic
                # form — `val ord_op` is a PROGRAM symbol and cannot appear in a
                # `requires`/`ensures`/axiom. In a body keep `ord_op` (a body cannot
                # apply a logic `function`); the two agree by `ord_op`'s ensures.
                # `args[0]` is the lowered 1-char string (e.g. `(str_sub_op name i 1)`).
                if self._in_spec:
                    # string-codec Phase A': `ord(s[i])` — the dominant codec form — must
                    # lower to `Char.code (Char.get s i)` DIRECTLY, not via the
                    # `Char.get (String.substring s i 1) 0` detour. The two are equal by
                    # `substring_get`, but the detour leaves the encoding precondition
                    # syntactically unequal to `field_to_str_round_trip`'s antecedent, so
                    # the axiom never instantiates and SMT falls back to extensionality on
                    # the string-equality goal → OOM (measured). The direct form makes the
                    # axiom apply in O(1) (~19k steps, Valid).
                    if (arg_ir.get("type") == "Subscript"
                            and self._is_string_expr(arg_ir.get("value", {}))):
                        base = self._expr_to_whyml(
                            arg_ir["value"], local_refs or set(), invariant_ctx, subst)
                        idx = self._expr_to_whyml(
                            arg_ir["index"], local_refs or set(), invariant_ctx, subst)
                        return f"(Char.code (Char.get {base} {idx}))"
                    return f"(Char.code (Char.get {args[0]} 0))"
                # BODY: `ord(s[i])` lowers to a dedicated `char_code_at s i` val whose
                # ensures is the SAME logic form a contract uses (`Char.code (Char.get
                # s i)`), NOT `ord_op (str_sub_op s i 1)`. The latter routes through
                # `String.substring`, so an encode loop's invariant `out[j] == Char.code
                # (Char.get name j)` only matches the assigned value via a `substring_get`
                # bridge that E-match-explodes (OOM, measured). The direct form matches
                # the invariant atom-for-atom — the body twin of the Phase A' spec rule.
                if (arg_ir.get("type") == "Subscript"
                        and self._is_string_expr(arg_ir.get("value", {}))):
                    base = self._expr_to_whyml(
                        arg_ir["value"], local_refs or set(), invariant_ctx, subst)
                    idx = self._expr_to_whyml(
                        arg_ir["index"], local_refs or set(), invariant_ctx, subst)
                    self._add_abstract_op(
                        "val char_code_at (s: string) (i: int) : int\n"
                        "    ensures { 0 <= result < 256 }\n"
                        "    ensures { result = Char.code (Char.get s i) }")
                    return f"(char_code_at {base} {idx})"
                self._add_abstract_op(
                    "val ord_op (c: string) : int\n"
                    "    ensures { 0 <= result < 256 }\n"
                    "    ensures { result = Char.code (Char.get c 0) }")
                return f"(ord_op {args[0]})"
            # non-string `ord(x)`: fall through (return None) — keep current behaviour.
        if func_name == "chr" and len(args) == 1:
            # string-codec Phase A': same context split as `ord` (logic form in a
            # contract, program `chr_op` in a body).
            if self._in_spec:
                return f"((Char.chr {args[0]}).contents)"
            self._add_abstract_op(
                "val chr_op (n: int) : string\n"
                "    ensures { String.length result = 1 }\n"
                "    ensures { result = (Char.chr n).contents }")
            return f"(chr_op {args[0]})"
        if func_name in ("str", "repr", "format", "int", "bool", "abs") and len(args) == 1:
            arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
            if arg_ir.get("type") == "Number" and func_name in ("int", "abs"):
                val = arg_ir.get("value")
                if isinstance(val, (int, float)):
                    return str(int(val) if func_name == "int" else abs(int(val)))
            if func_name == "int":
                # pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): the
                # complex branch of `_py_expr_constant`, `int(expr.value.real)`, truncates
                # the real part of a PVComplex `.value`. `expr.value.real` is a `.real`
                # attribute read on a `pyconst_val`-typed field -> the real projector
                # `(pvreal_of expr.value)`; `int(<real>)` is the Why3 `truncate`. So the
                # whole reads `(truncate (pvreal_of expr.value))` : int, feeding IrNum.
                if (isinstance(arg_ir, dict)
                        and arg_ir.get("type") in ("Attribute", "FieldGet")
                        and (arg_ir.get("attr") or arg_ir.get("field")) == "real"
                        and self._pyconst_val_field_read(arg_ir.get("object", {})) is not None):
                    _ow = self._expr_to_whyml(arg_ir.get("object", {}),
                                              local_refs or set(), invariant_ctx, subst)
                    return f"(real_trunc (pvreal_of {_ow}))"
                # const-reflection value model (self-tcb-reduction, Tier-5 value-model
                # wall): `int(<x>.value)` where <x> is an emit_ir CONSTANT node reads the
                # INT payload of its IrNum leaf -> `(num_of <x>)`, the FAITHFUL int
                # projector — NOT the opaque `get_value`/`svalue_of` sub-node projector
                # `_EMIT_IR_PROJ["value"]` picks (an emit_ir type error in an int context).
                # Gated on `_uses_const_reflect` -> corpus-inert.
                if (self._uses_const_reflect()
                        and isinstance(arg_ir, dict)
                        and arg_ir.get("type") == "Attribute"
                        and arg_ir.get("attr") == "value"
                        and self._is_emit_ir_expr(arg_ir.get("object", {}))):
                    _ow = self._expr_to_whyml(arg_ir.get("object", {}),
                                              local_refs or set(), invariant_ctx, subst)
                    return f"(num_of {_ow})"
                # typed-ir §18: `int(<str>)` (e.g. `int(ghost_type[-1])`) is a genuine
                # str→int conversion — an abstract `str_to_int` — not the int-identity.
                # Fires only for a string arg → byte-identical (an int arg is identity).
                if not self._in_spec and self._is_string_expr(arg_ir):
                    self._add_abstract_op("val str_to_int (s: string) : int")
                    return f"(str_to_int {args[0]})"
                return args[0]
            # G2 strings: `str(s)` / `format(s)` (no spec) of a string is the identity —
            # the same Why3 string, faithfully (mirrors the int identity above). `repr(s)`
            # is NOT identity (it adds quotes), so it is handled separately (str_repr_op).
            if func_name in ("str", "format") and self._is_string_expr(arg_ir):
                return args[0]
            # G2 strings: `repr(s)` of a string is an abstract string-valued op. Its content
            # transform is NOT modeled — Python adds 2 quotes ONLY for quote/escape-free
            # strings, so a `+2` *equality* length law would be UNSOUND. The only sound,
            # faithful length fact is the lower bound: `repr` of any str always carries at
            # least the two surrounding quote characters, so `length result >= 2`. No false
            # postcondition is emitted.
            if func_name == "repr" and self._is_string_expr(arg_ir):
                self._add_abstract_op(
                    "val str_repr_op (s: string) : string\n"
                    "    ensures { String.length result >= 2 }")
                return f"(str_repr_op {args[0]})"
            # str(<int>) value-model (self-tcb-reduction M6, fable-adjudicated
            # CHEAP-BREAKABLE): a `str()` of a NON-string arg (an int — the string arg is
            # the identity above) renders the int to its decimal string. Emit the FAITHFUL
            # `str_of_int : int -> string` (an ABSTRACT uninterpreted `val`, no `ensures`
            # → NOT a new axiom, ledger stays 3) instead of the int-erased `str_conv :
            # int -> int` — so the `str(stable_hash(...))` emitter string-helpers (which
            # return the decimal in a `-> str` slot) typecheck. Corpus-byte-diff-0:
            # `str_conv`/`str_of_int` are emitter-only (0 hits across all 767 corpus .mlw,
            # fable-confirmed). `format/bool/int/abs` keep the generic `*_conv` int model.
            if func_name == "str":
                self._add_abstract_op("val str_of_int (x: int) : string")
                return f"(str_of_int {args[0]})"
            # self-tcb-reduction (union/match cluster): `bool(<array-int local>)`
            # (`bool(true_branch_stmts)`, `true_branch_stmts = body if … else orelse`) is
            # Python list-truthiness = non-emptiness, `(if Array.length arr <> 0 then 1 else
            # 0)` (an int, feeding the `&& (… <> 0)` guard), NOT the `bool_conv (x:int):int`
            # which type-clashes an array arg. Gated on the arg being a known array-int local.
            if (func_name == "bool" and isinstance(arg_ir, dict)
                    and arg_ir.get("type") == "Var"
                    and (arg_ir.get("name") in getattr(self, "_inline_array_temps", set())
                         or arg_ir.get("name") in getattr(self, "_array_elem_types", {}))):
                return f"(if Array.length {args[0]} <> 0 then 1 else 0)"
            wf = whyml_ident(func_name)
            self._add_abstract_op(f"val {wf}_conv (x: int) : int")
            return f"({wf}_conv {args[0]})"
        if func_name == "sum" and len(args) == 1:
            result = self._handle_sum_call(expr)
            if result:
                return result
        if func_name == "hasattr":
            a0 = args[0] if args else "0"
            a1 = self._coerce_str_arg(args[1] if len(args) > 1 else "0")
            self_type = self._current_self_type
            if a0 == "self" and self_type:
                op = f"hasattr_check_{self_type}"
                self._add_abstract_op(f"val {op} (x: {self_type}) (a: int) : bool")
            else:
                op = "hasattr_check"
                self._add_abstract_op("val hasattr_check (x: int) (a: int) : bool")
            return f"({op} {a0} {a1})"
        if func_name == "exec":
            # 07-1839 P5a': a dynamic `exec` is a worst-case mutator (rev4 §8.4.2). In a
            # frame-checked model (typed/store) it WRITES the heap, so a narrow `assigns`
            # (e.g. `\nothing` → `ensures !heap = old !heap`) correctly fails — closing the
            # frame hole. In the value-semantic model `assigns` is not frame-checked, so an
            # opaque unit suffices (scope havoc is handled in P5a). Constant splice = P5b.
            code = args[0] if args else "0"
            if not self._value_semantic:
                hv = self._heap_var
                self._add_abstract_op(f"val exec_havoc (code: 'a) : unit writes {{ {hv} }}")
                return f"(exec_havoc {code})"
            self._add_abstract_op("val exec_stmt (code: 'a) : unit")
            return f"(exec_stmt {code})"
        if func_name in ("literal_eval", "ast.literal_eval") and len(expr.get("args", [])) == 1:
            # 07-1839 P5c: `literal_eval` of a CONSTANT literal is compile-time-knowable —
            # evaluate it with host `ast.literal_eval` (the source of truth) and emit the
            # ACTUAL value with its true type (faithful, rev4 §8.3). int/str handled; other
            # types (list/dict/float/bool) fall through to the opaque dynamic stub for now.
            arg0 = expr["args"][0]
            if isinstance(arg0, dict) and arg0.get("type") == "String":
                import ast as _hostast
                try:
                    v = _hostast.literal_eval(arg0.get("value", ""))
                    if isinstance(v, bool):
                        v = None  # defer bool (context-dependent true/false vs 1/0)
                    if isinstance(v, int):
                        return f"(- {abs(v)})" if v < 0 else str(v)
                    if isinstance(v, str):
                        return self._whyml_string_literal(v)
                except (ValueError, SyntaxError):
                    pass  # not a valid literal → opaque
            self._add_abstract_op("val literal_eval_op (s: 'a) : int")
            return f"(literal_eval_op {args[0] if args else '0'})"
        return None

    # ── 07-1839 P4: metatype tags + \subtag + isinstance ──────────────────────
    _METATYPE_TAGS = {"int": "tag_int", "bool": "tag_int", "str": "tag_str",
                      "float": "tag_float", "list": "tag_list", "List": "tag_list",
                      "dict": "tag_dict", "Dict": "tag_dict", "set": "tag_dict",
                      "frozenset": "tag_dict", "object": "tag_object"}

    # Literal int values for the on-demand `tag_*` logic functions (see
    # `_emit_metatype_tags`). In PROGRAM context Why3 rejects references to
    # logic `function` symbols ("Logical symbol tag_int is used in a non-ghost
    # context"), so `isinstance` lowered to a runtime int comparison inlines
    # these literals instead of naming the ghost `tag_*` functions.
    _TAG_LITERAL = {"tag_int": 0, "tag_str": 1, "tag_float": 2, "tag_list": 3,
                    "tag_dict": 4, "tag_record": 5, "tag_variant": 6,
                    "tag_object": 99}

    def _emit_metatype_tags(self) -> None:
        """Emit the tag constants + the `subtag` relation (P0-validated). Decision A:
        no `tag_bool` — bool collapses to `tag_int` (Γ has `τ(bool)=int`). subtag is
        reflexive + `b = object`; on-demand, so non-introspecting files stay identical."""
        for nm, v in (("tag_int", 0), ("tag_str", 1), ("tag_float", 2), ("tag_list", 3),
                      ("tag_dict", 4), ("tag_record", 5), ("tag_variant", 6),
                      ("tag_object", 99)):
            self._add_abstract_op(f"function {nm} : int = {v}")
        # `99` is `tag_object` inlined: the abstract-op block is emitted alphabetically,
        # so `subtag` must not reference `tag_object` by name (it would sort before it).
        # The `tag_*` functions are used only in goals (after all decls), so they are fine.
        self._add_abstract_op("predicate subtag (a b: int) = a = b \\/ b = 99")

    def _tag_of_type(self, t_name: str) -> str:
        """Tag for a *type name* (the 2nd arg of isinstance / a class / datatype).
        None ⇒ unknown target type (fully uninterpreted)."""
        if not t_name:
            return ""
        if t_name in self._METATYPE_TAGS:
            return self._METATYPE_TAGS[t_name]
        if t_name.lower() in getattr(self, "_record_types", {}):
            return "tag_record"
        if t_name in getattr(self, "_variant_types", {}):
            return "tag_variant"
        return ""

    def _tag_of_value(self, x_ir: Dict[str, Any]) -> str:
        """Tag of a *value* from Γ's τ (decision B: only a stable, concrete τ decides;
        `Any`/unstable/non-var → a free symbolic tag via `typeof_op`, so introspection on
        it stays unknown — never a wrong-decided)."""
        name = x_ir.get("name") if isinstance(x_ir, dict) and x_ir.get("type") == "Var" else None
        tag = self._tag_of_type(getattr(self, "_current_symbol_table", {}).get(name)) if name else ""
        if tag:
            return tag
        self._add_abstract_op("val function typeof_op (n: int) : int")
        return f"(typeof_op {sum(ord(c) for c in name) if name else 0})"

    def _sibling_call_union_type(self, x_ir: Any) -> Optional[str]:
        """The `_union_*` WhyML type of a `self.<m>(...)` sibling call, when that call
        resolves CONCRETELY (so the emitted expression really has the union type) — else
        None. Gated by the SAME two admission routes `_handle_dotted_call` uses for the
        concrete lowering (`_record_array_fields` or the opt-in `#@ sibling_concrete`),
        so it can never claim a union type for a call that actually lowered to the opaque
        int-returning avatar."""
        if not (isinstance(x_ir, dict) and x_ir.get("type") == "Call"):
            return None
        fn = x_ir.get("func")
        if not (isinstance(fn, str) and fn.startswith("self.")
                and getattr(self, "_current_self_type", None)):
            return None
        _concrete = whyml_ident(f"{self._current_self_type}__{fn[len('self.'):]}")
        if not (getattr(self, "_record_array_fields", None)
                or _concrete in getattr(self, "_sibling_concrete_methods", set())):
            return None
        if _concrete not in getattr(self, "_module_func_names", set()):
            return None
        # Read the return ANNOTATION, not `_resolve_dotted_signature` /
        # `_module_method_return_types`: that registry is WRONG for union returns — it
        # records `_parser__peek: int` although `peek` demonstrably emits
        # `: _union_peek_0`. The annotation map is the same source the union-local SEEDING
        # in statements.py already trusts, so the call site and the local typing cannot
        # disagree.
        _ann = getattr(self, "_module_method_return_annotations", {}).get(
            f"{self._current_self_type}__{fn[len('self.'):]}")
        return _ann if isinstance(_ann, str) and _ann.startswith("_union_") else None

    def _call_union_none_ctor(self, x_ir: Any) -> Optional[str]:
        """cursor-nest `parse_atom`: the nullary None arm of a union-returning sibling
        CALL used DIRECTLY in an `is None` guard rather than bound to a local
        (`if self.peek() is not None and self.peek().kind == "COMMA"`). Without it the
        call lowers to `(_parser__peek self 0) <> 0` — union-vs-int.

        Faithful to Python: `peek` is `assigns \nothing`, so evaluating it twice (exactly
        as the live body does) observes the same value both times.

        Deliberately kept OUT of `_union_none_ctor_for` and consumed by `_handle_binop`
        instead: `_union_none_ctor_for` has an UN-TRUSTED mirror counterpart, so §10.4
        would force a verbatim re-port, and the re-ported body's call to
        `_sibling_call_union_type` (which the mirror does NOT define) degraded to an
        int-returning auto-trusted val and broke the expressions mirror at L3-tc
        (`has type string -> option hval, but is expected to have type int`). Hosting it in
        the `\trusted`-mirrored `_handle_binop` keeps the fidelity plane at baseline with
        no new mirror stub — a smaller TCB than either alternative."""
        return (self._union_none_ctor_of_type(self._sibling_call_union_type(x_ir))
                if isinstance(x_ir, dict) and x_ir.get("type") == "Call" else None)

    def _union_none_ctor_of_type(self, utype: Optional[str]) -> Optional[str]:
        """The nullary `Arm_*_None` constructor of a named `_union_*` variant, or None."""
        if not utype:
            return None
        vinfo = getattr(self, "_variant_types", {}).get(utype)
        if not vinfo:
            return None
        for ctor_name, ctor in vinfo.get("constructors", {}).items():
            if ctor.get("arity") == 0 and "None" in ctor_name:
                return ctor_name
        return None

    def _union_none_ctor_for(self, x_ir: Dict[str, Any]) -> Optional[str]:
        """typing-engagement ty1 C5 — if `x_ir` is a Var whose symbol-table type
        is a synthesized `_union_*` variant that has a nullary `Arm_*_None`
        constructor, return that constructor name (so `x is None` lowers to a
        constructor check). Else None (caller falls back to `x = 0`)."""
        if not isinstance(x_ir, dict):
            return None
        # GAP #1c (self-tcb-reduction parser vein): spec-position `\result` on a
        # union return type. `\result != None` / `\result == None` in an `ensures`
        # of an `-> Optional[<object>]` method (return lowered to a `_union_*` with
        # a nullary `Arm_*_None`, e.g. `accept_op`) must lower to the is-None ctor
        # DISCRIMINANT on `result`, not the `(result <> 0)` int coercion (a
        # union-vs-int L3-tc error). `_union_none_ctor_for` on a `Var` reads the
        # symbol table; for `\result` the union type is the CURRENT function's
        # `_func_return_type` (set in functions.py before the body/spec are
        # lowered). Same nullary-None-ctor lookup as the Var branch below.
        if x_ir.get("type") == "Result":
            frt = getattr(self, "_func_return_type", "")
            if not isinstance(frt, str) or not frt.startswith("_union_"):
                return None
            vinfo = getattr(self, "_variant_types", {}).get(frt)
            if not vinfo:
                return None
            for ctor_name, ctor in vinfo.get("constructors", {}).items():
                if ctor.get("arity") == 0 and "None" in ctor_name:
                    return ctor_name
            return None
        if x_ir.get("type") != "Var":
            return None
        name = x_ir.get("name")
        symtype = getattr(self, "_current_symbol_table", {}).get(name)
        if not symtype or not isinstance(symtype, str) or not symtype.startswith("_union_"):
            return None
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        for ctor_name, ctor in vinfo.get("constructors", {}).items():
            if ctor.get("arity") == 0 and "None" in ctor_name:
                return ctor_name
        return None

    def _optional_str_union_ctor(self, x_ir: Any) -> Optional[str]:
        """no-more-int leak fix — if `x_ir` is a Var whose symbol-table type is a
        synthesized `_union_*` variant with EXACTLY ONE payload-carrying arm and that
        arm carries a `str` (i.e. the lowering of an `Optional[str]` parameter), return
        the Some-arm constructor name (e.g. `Arm_0_0`). Else None.

        A string comparison (`x == "s"` / `x in ("a","b")`) on such an operand must NOT
        int-hash the literals against the union (a union-vs-int type error); instead the
        caller option-unwraps: `(match x with Arm_0_0 s -> str_eq_op s "s" | _ -> false)`.
        Scoped to a NON-`_optional_union_locals` var (a param passed by value / an
        un-projected union) — a mutable Optional LOCAL is already carrier-projected on read
        by `_union_local_read_projection`, so its emitted operand is a `string`, not the raw
        union, and must not be re-matched here."""
        if not isinstance(x_ir, dict):
            return None
        symtype = None
        if x_ir.get("type") == "Call":
            # SHADOWED-SELFCALL REPAIR, the `Optional[str]`-return half (lesson (bc)
            # finding 1): `self._field_type_of(x) in ("list","tuple")` — a `self.<m>(...)`
            # SIBLING CALL whose declared return is `Optional[str]`. While the callee was
            # shadowed the abstract `val` returned `int` and the int-hash comparison
            # type-checked (badly); the moment the callee is marked `#@ sibling_concrete`
            # the concrete application hands back the REAL `_union_*` and the comparison
            # is Why3-REJECTED. `_sibling_call_union_type` returns the union type ONLY
            # when the call really lowers concretely (it is gated by the SAME two
            # admission routes `_handle_dotted_call` uses), so this can never claim a
            # union for a call that stayed abstract.
            symtype = self._sibling_call_union_type(x_ir)
        elif x_ir.get("type") == "Var":
            name = x_ir.get("name")
            if name in getattr(self, "_optional_union_locals", set()):
                return None
            symtype = getattr(self, "_current_symbol_table", {}).get(name)
        else:
            return None
        if not symtype or not isinstance(symtype, str) or not symtype.startswith("_union_"):
            return None
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        some_ctor: Optional[str] = None
        for ctor_name, ctor in vinfo.get("constructors", {}).items():
            payload = ctor.get("payload", [])
            if not payload:
                continue  # nullary None arm
            if len(payload) != 1 or payload[0] != "str":
                return None  # not a pure Optional[str] union
            if some_ctor is not None:
                return None  # more than one carrying arm — not Optional[str]
            some_ctor = ctor_name
        return some_ctor

    def _handle_isinstance(self, expr: Dict[str, Any], local_refs: Optional[Set[str]] = None) -> str:
        """`isinstance(x, T)` → `subtag (\\typeof x) T` (decision: \\subtag, not ==, so a
        base type like `object` decides true and a leaf≠leaf decides false). Decided when
        x has a concrete τ; symbolic at the `Any` tail; fully uninterpreted if T is an
        unknown type.

        value-model campaign incr5 (primitive b): `local_refs` is threaded from the call site
        so `isinstance(<x>, ast.<Node>)` where `<x>` is an emit_ir REF LOCAL (`k = ann.slice
        .elts[0]`) lowers to `is_var !k` (dereferenced), not the ill-typed `is_var k`. For a
        PARAM/attribute arg (not in `local_refs`) the emission is byte-identical to the prior
        `set()` — only a ref-local arg (the new dict-walker case) changes."""
        local_refs = local_refs or set()
        args_ir = expr.get("args", [])
        # isinstance-on-emit_ir batch (self-tcb-reduction M5): `isinstance(<emit_ir
        # child>, ast.<Node>)` — an input-side type test on an already-lowered ExprIR
        # child node (the Module5 `_py_expr_*` handlers' `isinstance(expr.value,
        # ast.Name)` shape) — lowers to the emit_ir ADT constructor DISCRIMINANT
        # `(is_<kind> child)`. arg1 is the AST class `ast.<Node>` (an Attribute with
        # object=Var("ast"), attr=<Node>). Double-gated on `_is_emit_ir_expr(arg0)`
        # AND the `ast.`-dotted second arg, so corpus programs (no emit_ir isinstance)
        # are byte-inert. Faithful: on every REAL node `_py_expr_to_ir` produces, the
        # child's `type` tag agrees with `is_<kind>` (the same law `_KIND_DISCRIMINANT`
        # relies on for `.get("type") == "K"`).
        _a0 = args_ir[0] if args_ir else None
        _a1 = args_ir[1] if len(args_ir) > 1 else None
        # TERM CARRIER: `isinstance(atom, Var)` on a `term`-typed local, where `Var` is an
        # ARM of this file's certified inductive, is the ADT constructor DISCRIMINANT —
        # `(match !atom with Var _ -> true | _ -> false end)`. Today it lowers to the
        # CONTENTLESS `(isinstance_op 0 0)`: BOTH arguments erased to 0, so the test is
        # independent of the value AND of the class — the purest possible facade, and the
        # `parse_atom_application` dispatch turns on it. The emit_ir sibling of this rule
        # is a few lines below (`is_<kind> child`); this is the same law one type-class
        # over, and it is EXACT rather than an approximation: on a `term` value the arm
        # IS the class.
        _tc = (getattr(self, "_term_adt_spec", None) or {}).get("ctors") or {}
        if (isinstance(_a0, dict) and _a0.get("type") == "Var"
                and _a0.get("name") in getattr(self, "_term_local_vars", set())
                and isinstance(_a1, dict) and _a1.get("type") == "Var"
                and _a1.get("name") in _tc):
            _ar = _a0["name"]
            _deref = (f"!{whyml_ident(_ar)}" if _ar in local_refs
                      else whyml_ident(_ar))
            _arity = len(_tc[_a1["name"]])
            _wild = " ".join(["_"] * _arity)
            _pat = f"{_a1['name']} {_wild}".rstrip()
            return f"(match {_deref} with {_pat} -> true | _ -> false end)"
        # self-tcb-reduction _typeddict_record_literal (cap-3): `isinstance(<emit_ir>, dict)`
        # — every reflected IR node IS a Python dict, so the test is always TRUE in the
        # reflection model. Emit the constant true (a provably-satisfied type guard; the real
        # discrimination is the conjoined `.get("type") == K` read of the same node). Gated on
        # an emit_ir arg0 + a bare `dict` builtin arg1 -> corpus/other-mirror inert.
        if (self._is_emit_ir_expr(_a0)
                and isinstance(_a1, dict) and _a1.get("type") == "Var"
                and _a1.get("name") == "dict"):
            # isinstance returns a BOOL discriminant everywhere (like `(is_var x)`); the
            # `not`/`&&`/`_to_bool` consumers expect a bool, so emit `true`, not the int `1`.
            return "true"
        # self-tcb-reduction Tier-5 (union/match cluster): `isinstance(<pyval-local>, dict)`
        # — a heterogeneous `hval` subject (`subj = stmt.get("subject", {})`) IS a Python
        # dict in the reflection model, so the guard is always TRUE (the real discrimination
        # is the conjoined `subj.get("type") == "Var"` read of the same value). Gated on a
        # pyval-local arg0 + a bare `dict` builtin arg1 -> corpus/other-mirror inert.
        if (isinstance(_a0, dict) and _a0.get("type") == "Var"
                and _a0.get("name") in getattr(self, "_pyval_locals", set())
                and isinstance(_a1, dict) and _a1.get("type") == "Var"
                and _a1.get("name") == "dict"):
            return "true"
        # self-tcb-reduction giants (generic class-body lowering): `isinstance(child,
        # ast.<K>)` where `child` is a `pyast_stmt`-typed class-body loop var lowers to
        # the ADT discriminant `(is_K_node child)`. Gated on `child in _pyast_stmt_locals`
        # AND the `ast.<K>` stmt-class second arg -> corpus-inert.
        if (self._pyast_stmt_child_var(_a0) is not None
                and isinstance(_a1, dict) and _a1.get("type") == "Attribute"
                and isinstance(_a1.get("object"), dict)
                and _a1["object"].get("type") == "Var"
                and _a1["object"].get("name") == "ast"
                and _a1.get("attr") in self._AST_CLASS_TO_STMT_KIND):
            _pred = self._AST_CLASS_TO_STMT_KIND[_a1["attr"]]
            _cv = self._expr_to_whyml(_a0, local_refs, getattr(self, "_in_spec", False), None)
            return f"({_pred} {_cv})"
        # 7b (self-tcb-reduction L4b): `isinstance(node, ast.ClassDef)` where `node` is a
        # `py_tparam_node` PARAM (the legacy `Generic[T]` branch guard) lowers to the opaque
        # runtime-kind bool `(is_classdef_of node)` — NOT `isinstance_op 0 0`. Gated on `node
        # in _current_tparam_node_params` AND `ast.ClassDef` -> corpus-inert.
        if (isinstance(_a0, dict) and _a0.get("type") == "Var"
                and _a0.get("name") in getattr(self, "_current_tparam_node_params", set())
                and isinstance(_a1, dict) and _a1.get("type") == "Attribute"
                and isinstance(_a1.get("object"), dict)
                and _a1["object"].get("type") == "Var"
                and _a1["object"].get("name") == "ast"
                and _a1.get("attr") == "ClassDef"):
            _nv = self._expr_to_whyml(_a0, local_refs, getattr(self, "_in_spec", False), None)
            return f"(is_classdef_of {_nv})"
        # J2/J3 convergence (Call-internals): `isinstance(kw.value, ast.Name/Attribute)`
        # over a keyword loop var lowers to the certified kwval discriminant `is_kwname` /
        # `is_kwattr` applied to `(kw_value_of kw)`. Double-gated on the keyword-value
        # subject AND the `ast.Name`/`ast.Attribute` second arg -> corpus-inert.
        if (getattr(self, "_keyword_locals", None)
                and isinstance(_a1, dict) and _a1.get("type") == "Attribute"
                and isinstance(_a1.get("object"), dict)
                and _a1["object"].get("type") == "Var"
                and _a1["object"].get("name") == "ast"
                and _a1.get("attr") in ("Name", "Attribute")):
            _kwval = self._keyword_value_term(
                _a0, local_refs, getattr(self, "_in_spec", False), None)
            if _kwval is not None:
                _kwpred = "is_kwname" if _a1["attr"] == "Name" else "is_kwattr"
                return f"({_kwpred} {_kwval})"
        # J2/J3 convergence (Call-internals): `isinstance(call.func, ast.Name)` — an
        # IrCall/IrCallKw callee is ALWAYS a bare Name string in the emit_ir model, so the
        # test is `is_call call` (true exactly when `call` is a call node). Gated on the
        # `<emit_ir call>.func` subject AND `ast.Name` -> corpus-inert.
        if (isinstance(_a0, dict) and _a0.get("type") == "Attribute"
                and _a0.get("attr") == "func"
                and isinstance(_a0.get("object"), dict)
                and _a0["object"].get("type") == "Var"
                and _a0["object"].get("name") in getattr(self, "_emit_ir_local_vars", set())
                and isinstance(_a1, dict) and _a1.get("type") == "Attribute"
                and isinstance(_a1.get("object"), dict)
                and _a1["object"].get("type") == "Var"
                and _a1["object"].get("name") == "ast"
                and _a1.get("attr") == "Name"):
            _cw = self._expr_to_whyml(_a0["object"], local_refs,
                                      getattr(self, "_in_spec", False), None)
            return f"(is_call {_cw})"
        if (isinstance(_a0, dict) and isinstance(_a1, dict)
                and _a1.get("type") == "Attribute"
                and isinstance(_a1.get("object"), dict)
                and _a1["object"].get("type") == "Var"
                and _a1["object"].get("name") == "ast"
                and self._is_emit_ir_expr(_a0)):
            _kind = self._AST_CLASS_TO_IR_KIND.get(_a1.get("attr"))
            _pred = self._KIND_DISCRIMINANT.get(_kind) if _kind else None
            # value-model campaign incr5 (primitive a): in a dict-type walker, `isinstance
            # (<slice>, ast.Tuple)` tests the VARIADIC `IrMkTupleN` slice → `is_mktuple` (the
            # global default `is_tuple` matches only binary `IrTuple`, so it is dead-false on a
            # `Dict[K,V]` slice). Scoped via `_current_emitting_func` → byte-inert elsewhere.
            if _kind == "MkTuple":
                _cef = getattr(self, "_current_emitting_func", None) or ""
                if any(_cef == h or _cef.endswith("__" + h) for h in _MKTUPLE_ELTS_HANDLERS):
                    _pred = "is_mktuple"
            if _pred:
                _av = self._expr_to_whyml(_a0, local_refs, getattr(self, "_in_spec", False), None)
                return f"({_pred} {_av})"
        # isinstance-on-CSL-class recognizer (self-tcb-reduction M5): the SIBLING form
        # where the second arg is a BARE `Var` naming a *CSL* AST class
        # (`isinstance(node.expr, CSLFieldAccess)` in `_csl_old`) instead of the dotted
        # `ast.<Node>`. Same faithful lowering: on every REAL node the child's `type`
        # tag agrees with `is_<kind>` (the `_CSL_CLASS_TO_IR_KIND` -> `_KIND_DISCRIMINANT`
        # chain). Double-gated on `_is_emit_ir_expr(arg0)` AND the class-name allow-list,
        # so a non-emit_ir isinstance (or one against an unlisted class) is byte-inert.
        if (isinstance(_a0, dict) and isinstance(_a1, dict)
                and _a1.get("type") == "Var"
                and _a1.get("name") in self._CSL_CLASS_TO_IR_KIND
                and self._is_emit_ir_expr(_a0)):
            _kind = self._CSL_CLASS_TO_IR_KIND.get(_a1.get("name"))
            _pred = self._KIND_DISCRIMINANT.get(_kind) if _kind else None
            if _pred:
                _av = self._expr_to_whyml(_a0, local_refs, getattr(self, "_in_spec", False), None)
                return f"({_pred} {_av})"
        # PYTHON-AST NODE CTOR FAMILY (relaunch #14): `isinstance(<emit_ir>, _N("<Cls>"))`
        # — the pure_ast parser's OWN class-by-name form of the two recognizers above
        # (`expr_stmt`'s `simple = 1 if isinstance(first, _N("Name")) else 0`). `_N` is the
        # parser's class factory, so the second argument is a CALL with one STRING literal
        # naming an ASDL class, not a dotted `ast.<Node>` nor a bare `Var`.
        #
        # THE LOWERING IS `kind_of`, NOT an `is_<kind>` discriminant: the `IrPy*` family
        # has no per-arm predicate, but `kind_of` is a DEFINED total function whose
        # `_PYAST_IRNODE_CTORS`-derived arms map each `IrPy<K>` to exactly the string
        # "<K>" (`_pyast_kind_of_arms`), and no other arm of the sum produces that string
        # for a family member's name. So `(str_eq_op (kind_of x) "<Cls>")` holds exactly
        # on the `IrPy<Cls>` arm — EXACT, not an approximation.
        #
        # DRIFT-PROOF AND FAIL-CLOSED: the admissible class names are read from
        # `_PYAST_IRNODE_CTORS` itself, so a member added or removed there moves this set
        # automatically and a class with no ctor arm (whose constructions still decline to
        # a facade) is NOT admitted here either. Gated additionally on
        # `_uses_pyast_parser` and on `_is_emit_ir_expr(arg0)`, so the corpus and every
        # other mirror are byte-identical.
        if (self._uses_pyast_parser()
                and isinstance(_a0, dict) and isinstance(_a1, dict)
                and _a1.get("type") == "Call" and _a1.get("func") == "_N"
                and not _a1.get("keywords")
                and len(_a1.get("args") or []) == 1
                and isinstance((_a1["args"][0] or {}), dict)
                and _a1["args"][0].get("type") == "String"
                and self._is_emit_ir_expr(_a0)):
            from frontend.ir_resolve import _PYAST_IRNODE_CTORS as _PYC5
            _cls5 = _a1["args"][0].get("value")
            if _cls5 in _PYC5:
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _av5 = self._expr_to_whyml(_a0, local_refs,
                                           getattr(self, "_in_spec", False), None)
                return f'(str_eq_op (kind_of {_av5}) {whyml_string_literal(_cls5)})'
        # const-reflection value model (self-tcb-reduction, Tier-5 value-model wall;
        # L1/L4a infra-witness): the two const-node isinstance recognisers, gated on
        # `_uses_const_reflect` (a file with an `isinstance(_, (int, float))` reflect) ->
        # corpus + every other mirror byte-identical.
        #  (A) `isinstance(<x>, ast.Constant)` where <x> is an emit_ir node lowers to the
        #      COMPOUND discriminant `(is_constant <x>)`. Faithful: a Constant lowers (via
        #      `_py_expr_constant`) to EXACTLY one of IrNum/IrNumF/IrStr/IrBoolC/IrNone, and
        #      `is_constant` matches exactly those leaves. `ast.Constant` is intentionally
        #      ABSENT from `_AST_CLASS_TO_IR_KIND` (a Constant is multi-leaf, not one kind),
        #      so ONLY the compound discriminant — not a single `is_K` — is faithful here.
        if (self._uses_const_reflect()
                and isinstance(_a1, dict) and _a1.get("type") == "Attribute"
                and isinstance(_a1.get("object"), dict)
                and _a1["object"].get("type") == "Var"
                and _a1["object"].get("name") == "ast"
                and _a1.get("attr") == "Constant"
                and self._is_emit_ir_expr(_a0)):
            _av = self._expr_to_whyml(_a0, local_refs, getattr(self, "_in_spec", False), None)
            return f"(is_constant {_av})"
        #  (B) `isinstance(<x>.value, (int, float))` — the tuple-of-types NUMERIC test on a
        #      const node's `.value` — lowers to `(is_num_or_float <x>)` (the numeric-leaf
        #      subset IrNum/IrNumF). arg0 is the `.value` Attribute on an emit_ir node; arg1
        #      is the `(int, float)` tuple literal.
        if (self._uses_const_reflect()
                and self._is_int_float_tuple(_a1)
                and isinstance(_a0, dict) and _a0.get("type") == "Attribute"
                and _a0.get("attr") == "value"
                and self._is_emit_ir_expr(_a0.get("object", {}))):
            _ow = self._expr_to_whyml(_a0.get("object", {}), local_refs,
                                      getattr(self, "_in_spec", False), None)
            return f"(is_num_or_float {_ow})"
        # pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): a
        # `_py_expr_constant`-style INPUT-side value-type test `isinstance(expr.value,
        # bool/str/int)` — where arg0 is a `pyconst_val`-typed record-field read
        # (`expr.value`, `_pyconst_val_field_read`) and arg1 is a BARE builtin type name
        # (`bool`/`str`/`int` as a `Var`) — lowers to the matching `pyconst_val` DISCRIMINANT
        # `(is_pvbool/is_pvstr/is_pvint expr.value)` (preamble.py `_emit_exprir_theory`).
        # Double-gated on `_pyconst_val_field_read(arg0)` AND the builtin-name allow-list, so
        # a non-pyconst_val isinstance (or one against a non-builtin) is byte-inert. Faithful:
        # on every REAL `ast.Constant` node the abstraction map sends a Python bool/str/int
        # `.value` to PVBool/PVStr/PVInt, and `is_pv*` decides exactly that variant (the
        # Phase2c_PyConstVal.v/PyConstVal.lean certificate's `is_pv*`↔isinstance agreement).
        _PV_BUILTIN_DISCRIM = {"bool": "is_pvbool", "str": "is_pvstr", "int": "is_pvint",
                               "bytes": "is_pvbytes", "complex": "is_pvcomplex"}
        if (isinstance(_a1, dict) and _a1.get("type") == "Var"
                and _a1.get("name") in _PV_BUILTIN_DISCRIM
                and (self._pyconst_val_field_read(_a0) is not None
                     or (isinstance(_a0, dict) and _a0.get("type") == "Var"
                         and _a0.get("name")
                         in getattr(self, "_pyconst_val_local_vars", set())))):
            # V1 pyconst-dispatch: arg0 is a pyconst_val record-field read OR a pyconst_val
            # LOCAL (`v = elt.value`, `const_pyval_of elt`) — either way the value-type test
            # `isinstance(v, bool/int/str)` is the pyconst_val discriminant `is_pv*`. A LOCAL
            # ref needs `local_refs` so it derefs to `!v` (a field read is param-rooted, so
            # `set()` — byte-identical to the pre-existing field-read path).
            _pv_lr = (local_refs if (isinstance(_a0, dict) and _a0.get("type") == "Var"
                                     and _a0.get("name")
                                     in getattr(self, "_pyconst_val_local_vars", set()))
                      else set())
            _av = self._expr_to_whyml(_a0, _pv_lr, getattr(self, "_in_spec", False), None)
            return f"({_PV_BUILTIN_DISCRIM[_a1['name']]} {_av})"
        # _const_int_value pyconst-dispatch (self-tcb-reduction M5, B-bucket): the three
        # UnaryOp/const isinstance tests inside `_const_int_value`, SCOPED via
        # `_current_emitting_func` so corpus + every other mirror stays byte-identical (the
        # `-N` int-literal extractor is the only reader of these forms). All axiom-free (the
        # accessors are total `let function`s over the existing IrUnaryOp ctor).
        _cef_ci = getattr(self, "_current_emitting_func", None) or ""
        if _cef_ci == "_const_int_value" or _cef_ci.endswith("___const_int_value"):
            # (i) `isinstance(value.value, int/bool)` / `isinstance(value.operand.value,
            #     int/bool)` -> the const leaf's pyconst_val discriminant on the OBJECT's
            #     `const_pyval_of` projection. Faithful: on a real ast.Constant the value's
            #     Python int/bool `.value` sends the leaf to PVInt/PVBool and `is_pvint`/
            #     `is_pvbool` decide exactly that variant (Phase2c_PyConstVal certificate).
            if (isinstance(_a1, dict) and _a1.get("type") == "Var"
                    and _a1.get("name") in ("int", "bool")
                    and isinstance(_a0, dict) and _a0.get("type") == "Attribute"
                    and _a0.get("attr") == "value"
                    and self._is_emit_ir_expr(_a0.get("object", {}))):
                _ow = self._expr_to_whyml(_a0["object"], local_refs,
                                          getattr(self, "_in_spec", False), None)
                _d = "is_pvint" if _a1["name"] == "int" else "is_pvbool"
                return f"({_d} (const_pyval_of {_ow}))"
            # (ii) `isinstance(value, ast.UnaryOp)` -> `is_unaryop value` (the NEW total
            #      discriminant, exactly the IrUnaryOp leaf — the `-N` unary node).
            if (isinstance(_a1, dict) and _a1.get("type") == "Attribute"
                    and isinstance(_a1.get("object"), dict)
                    and _a1["object"].get("type") == "Var"
                    and _a1["object"].get("name") == "ast"
                    and _a1.get("attr") == "UnaryOp"
                    and self._is_emit_ir_expr(_a0)):
                _uw = self._expr_to_whyml(_a0, local_refs,
                                          getattr(self, "_in_spec", False), None)
                return f"(is_unaryop {_uw})"
            # (iii) `isinstance(value.op, ast.USub)` -> the op STRING equals "-" (the
            #       `_py_op_to_str(ast.USub)` literal the live `_py_expr_unaryop` emits into
            #       IrUnaryOp's op field). arg0 is `.op` (a string leaf via `unaryop_op_of`
            #       on the object), arg1 is `ast.USub`.
            if (isinstance(_a1, dict) and _a1.get("type") == "Attribute"
                    and isinstance(_a1.get("object"), dict)
                    and _a1["object"].get("type") == "Var"
                    and _a1["object"].get("name") == "ast"
                    and _a1.get("attr") == "USub"
                    and isinstance(_a0, dict) and _a0.get("type") == "Attribute"
                    and _a0.get("attr") == "op"
                    and self._is_emit_ir_expr(_a0.get("object", {}))):
                _ow = self._expr_to_whyml(_a0["object"], local_refs,
                                          getattr(self, "_in_spec", False), None)
                return f'(str_eq_op (unaryop_op_of {_ow}) "-")'
        t_name = args_ir[1].get("name") if isinstance(args_ir[1], dict) else None
        t_tag = self._tag_of_type(t_name)
        if not t_tag:
            self._add_abstract_op("val isinstance_op (x: int) (t: int) : bool")
            return "(isinstance_op 0 0)"
        self._emit_metatype_tags()
        # In program (non-spec) context, `subtag` and the `tag_*` logic functions
        # are ghost symbols Why3 rejects inside an `if`/`while` condition
        # ("Logical symbol subtag/tag_int is used in a non-ghost context").
        # Lower to a runtime int equality on the value's type-tag discriminant,
        # inlining the tag's literal int on BOTH sides: `(<typeof x literal or
        # typeof_op call> = <T's tag literal>)` is a plain int `=` producing a
        # bool accepted in program `if`. In spec context the predicate form is
        # kept (it carries the sub-typing relation `a = b \/ b = 99`, exercising
        # the `object` base-type decision per corpus 0632).
        if not getattr(self, "_in_spec", False):
            lhs = self._tag_of_value(args_ir[0])
            if lhs in self._TAG_LITERAL:
                lhs = str(self._TAG_LITERAL[lhs])
            return f"({lhs} = {self._TAG_LITERAL[t_tag]})"
        return f"(subtag {self._tag_of_value(args_ir[0])} {t_tag})"

    @staticmethod
    def _get_default_is_empty_dict(expr: Dict[str, Any]) -> bool:
        """orelse_of mini-M1: True iff a `.get(key, default)` Call's SECOND arg is an
        empty-dict literal (`{}`, `DictLit` with no keys) — the shape an IfExpr's
        `.get("body", {})`/`.get("orelse", {})` uses. Used to disambiguate the emit_ir
        reflection key "body" (stmt-list `stmts_of` vs IfExpr scalar `body_of`) at the
        `.get` projection sites in `_lower_dict_get_call`. An empty-list `[]` default or
        no default at all (the If/For/While/Try `.get("body", [])` stmt-list shape) is
        NOT an empty dict, so it falls through to the table's `stmts_of` unchanged."""
        _dargs = expr.get("args") or []
        if len(_dargs) < 2:
            return False
        _default = _dargs[1]
        return (isinstance(_default, dict) and _default.get("type") == "DictLit"
                and not _default.get("keys"))

    @staticmethod
    def _get_default_is_str_literal(expr: Dict[str, Any]) -> bool:
        """self-tcb-reduction _typeddict_field_access (gap-1): True iff a `.get(key,
        default)` Call's SECOND arg is a STRING literal — the shape
        `index_ir.get("value", "")` uses after a `type == "String"` guard. A string
        default signals the receiver is a String IR node whose `value` is its STRING
        CONTENT (`value_of`), NOT the emit_ir `svalue` sub-node (`svalue_of`, the
        empty-dict-default / no-default shapes). Byte-inert (no corpus/other-mirror
        reflects an emit_ir `.get("value", "<str>")`)."""
        _dargs = expr.get("args") or []
        if len(_dargs) < 2:
            return False
        _d = _dargs[1]
        return isinstance(_d, dict) and _d.get("type") == "String"

    def _expr_is_pyval(self, e: Dict[str, Any]) -> bool:
        """K7/#5 (self-tcb-reduction Tier-5): True iff `e` produces a heterogeneous
        `hval` — a `_pyval_locals` Var, a `.get` on a `map string (option hval)`
        self-field, or a `.get` on an hval local. The value-typing predicate the
        `or`-default recognizer reuses to stay off int-erasure."""
        if not isinstance(e, dict):
            return False
        t = e.get("type")
        if t == "Var":
            return e.get("name") in getattr(self, "_pyval_locals", set())
        if t == "Call":
            fn = e.get("func", "")
            if isinstance(fn, str) and fn.endswith(".get"):
                recv = fn[:-len(".get")]
                if recv in getattr(self, "_pyval_locals", set()):
                    return True
                if self._self_field_dict_nu(recv) == "hval":
                    return True
                # union/match cluster C1b: a `.get` on a `Dict[str, PyVal]` param/local
                # (`_dict_value_types` codomain "hval") unwraps to an `hval`.
                if getattr(self, "_dict_value_types", {}).get(recv) == "hval":
                    return True
        # self-tcb-reduction _field_type_of: a subscript `self.<field>[k]` on a
        # `map string (option hval)` self-field produces an `hval` (unwrapped by the
        # `_handle_subscript` hval-map path), so a chained `.get(...)` on it is the
        # DOUBLED hval read. Mirrors the `.get`-on-hval-field case above.
        if t == "Subscript":
            _v = e.get("value")
            if isinstance(_v, dict) and _v.get("type") in ("Attribute", "FieldGet"):
                _vo = _v.get("object")
                _va = _v.get("attr") or _v.get("field")
                _dot = None
                if isinstance(_vo, dict) and _vo.get("type") == "Var" and _va:
                    _dot = f"{_vo.get('name')}.{_va}"
                elif isinstance(_vo, str) and _va:
                    _dot = f"{_vo}.{_va}"
                if _dot is not None and self._self_field_dict_nu(_dot) == "hval":
                    return True
            # self-tcb-reduction (union/match cluster): a subscript on a `map string
            # (option hval)` LOCAL (`vinfo["constructors"]`, `vinfo` an hval-map local)
            # unwraps to an `hval` — so a chained subscript `vinfo["constructors"][ctor]`
            # is the DOUBLED hval read (cap ii). The local twin of the self-field case.
            if (isinstance(_v, dict) and _v.get("type") == "Var"
                    and getattr(self, "_dict_value_types", {}).get(_v.get("name")) == "hval"):
                return True
        return False

    def _refine_func_symmap_reader(self, node: Any,
                                   local_refs: Optional[Set[str]],
                                   invariant_ctx: bool,
                                   subst: Optional[Dict[str, str]]) -> Optional[str]:
        """self-tcb-reduction typed-self-field-WRITE cap (func-field->string-map projector):
        `<func-param>.get("symbol_table"|"param_annotations")` on a `Dict[str, PyVal]` func
        param reads a nested `Dict[str, str]` symbol table -> the faithful reader
        `<field>_symmap_of (f: map string (option hval)) : map string (option string)` over
        the pyval func carrier (the banked opaque-self accessor cap is SELF-field-only; this
        is the func-PARAM-field twin). The result feeds the verified `_infer_tuple_slot_type`
        4th param (`map string (option string)`). Gated on `_refine_tuple_return_type` ->
        byte-inert for the corpus and every other mirror. None if the shape does not match."""
        if not self._emitting_refine_tuple_return_type():
            return None
        if not (isinstance(node, dict) and node.get("type") == "Call"):
            return None
        _fn = node.get("func") or ""
        if not (_fn == "get" or str(_fn).endswith(".get")):
            return None
        _args = node.get("args") or []
        if not (_args and isinstance(_args[0], dict) and _args[0].get("type") == "String"):
            return None
        _field = _args[0].get("value")
        # Only `symbol_table` projects to a total `map string (option string)` (read via
        # `.get`/subscript, passed to the verified `_infer_tuple_slot_type`). NOT
        # `param_annotations` — that one is ITERATED via `.items()`, which needs the finite
        # hval assoc-list carrier (`hval_as_map`/`hval_keys_get`), not a total map.
        if _field != "symbol_table":
            return None
        _rcv = node.get("receiver")
        if not (isinstance(_rcv, dict) and _rcv.get("type") == "Var"):
            # dotted-func form `func.get("symbol_table", {})` encodes the receiver in the
            # `func` string (`node["func"] == "func.get"`, receiver absent); recover the
            # receiver Var from the `<recv>.get` prefix. `<recv>` is a plain param name
            # (`func`), a `Dict[str, PyVal]` pydict — its value type is `hval`.
            _pref = _fn[:-len(".get")] if str(_fn).endswith(".get") else ""
            if _pref and "." not in _pref:
                _rcv = {"type": "Var", "name": _pref}
            else:
                return None
        _rw = self._expr_to_whyml(_rcv, local_refs or set(), invariant_ctx, subst)
        self._add_abstract_op(
            f"val function {_field}_symmap_of (f: map string (option hval)) "
            ": map string (option string)")
        return f"({_field}_symmap_of {_rw})"

    def _recognize_pyval_or_default(self, expr: Dict[str, Any],
                                    local_refs: Optional[Set[str]],
                                    invariant_ctx: bool,
                                    subst: Optional[Dict[str, str]]) -> Optional[str]:
        """#5 (pyval `or {}` / `or []` default, self-tcb-reduction Tier-5): recognize
        `<pyval> or {}` / `<pyval> or []` and lower it to the faithful
        keep-if-map-else-empty projection over the `pyval` carrier. Returns None (falls
        through to the generic boolean-`or` lowering) unless the left is pyval-producing
        and the right is an empty dict/list literal -> corpus byte-inert."""
        left = expr.get("left") or {}
        right = expr.get("right") or {}
        # typed-self-field-WRITE cap: `<func-param>.get("symbol_table"|"param_annotations")
        # or {}` projects to a `map string (option string)` symbol table (the func-field
        # twin of the banked opaque-self accessor). Gated on `_refine_tuple_return_type`.
        _sm = self._refine_func_symmap_reader(left, local_refs, invariant_ctx, subst)
        if _sm is not None:
            return _sm
        if not self._expr_is_pyval(left):
            return None
        _empty_default = (isinstance(right, dict)
                          and right.get("type") in ("DictLit", "ArrayLit")
                          and not right.get("keys") and not right.get("elts"))
        if not _empty_default:
            return None
        _lw = self._expr_to_whyml(left, local_refs or set(), invariant_ctx, subst)
        _empty = "(HMap PNil)"  # R3: empty HMap carrier is the empty assoc list
        return (f"(match {_lw} with HMap m_or -> {_lw} "
                f"| _ -> {_empty} end)")

    def _recognize_attr_receiver_idiom(self, expr: Dict[str, Any],
                                       local_refs: Optional[Set[str]],
                                       invariant_ctx: bool,
                                       subst: Optional[Dict[str, str]]) -> Optional[str]:
        """self-tcb-reduction _field_type_of: the Attribute-receiver extraction idiom
        `<emit_ir>.get("value") or <emit_ir>.get("object") [or {}]`. Module5 emits an
        Attribute's receiver under BOTH `value` (spec ctx) and `object` (body ctx), so
        the idiom takes whichever is present. Over the `emit_ir` sum this IS
        `avalue_of <node>` — the IrAttr∪IrSub unifier, which equals the IrAttr object
        sub-node (`object_of`) on an Attribute. Lowering the WHOLE or-chain as a unit
        keeps the `.get("object")` operand from reaching the generic key projection,
        which is what lets `_field_type_of`'s SEPARATE FieldGet-branch `.get("object")`
        scope to the leaf-string `fgobject_of` without a same-key type conflict. Gated on
        the receiver being emit_ir and the exact `value`/`object` key pair (on the same
        receiver) -> corpus byte-inert. Returns None (fall through) otherwise."""
        def _flatten_or(n: Any) -> List[Any]:
            if (isinstance(n, dict) and n.get("type") == "BinOp"
                    and n.get("op") == "or"):
                return _flatten_or(n.get("left", {})) + _flatten_or(n.get("right", {}))
            return [n]

        def _get_key_recv(n: Any) -> Optional[Tuple[str, str]]:
            if not (isinstance(n, dict) and n.get("type") == "Call"):
                return None
            _fn = n.get("func")
            if not (isinstance(_fn, str) and _fn.endswith(".get")):
                return None
            _a = n.get("args") or []
            if not (len(_a) == 1 and isinstance(_a[0], dict)
                    and _a[0].get("type") == "String"):
                return None
            return (_fn[:-len(".get")], _a[0].get("value"))

        ops = _flatten_or(expr)
        if (ops and isinstance(ops[-1], dict) and ops[-1].get("type") == "DictLit"
                and not ops[-1].get("keys")):
            ops = ops[:-1]
        if len(ops) != 2:
            return None
        kv0 = _get_key_recv(ops[0])
        kv1 = _get_key_recv(ops[1])
        if kv0 is None or kv1 is None:
            return None
        if kv0[0] != kv1[0] or kv0[1] != "value" or kv1[1] != "object":
            return None
        recv_ir = {"type": "Var", "name": kv0[0]}
        if not self._is_emit_ir_expr(recv_ir):
            return None
        _rw = self._expr_to_whyml(recv_ir, local_refs or set(), invariant_ctx, subst)
        return f"(avalue_of {_rw})"

    def _lower_dict_get_call(self, expr: Dict[str, Any], args: List[str],
                              func_name: str, local_refs: Optional[Set[str]],
                              invariant_ctx: bool,
                              subst: Optional[Dict[str, str]]) -> Optional[str]:
        """Lower `d.get(k[, default])` on a dict-typed Var receiver to a
        faithful WhyML `match Map.get <recv> <k> with | Some v_ -> v_ |
        None -> <default> end`. The receiver must be a SIMPLE Var bound to a
        dict-typed parameter or body-local — record-field dict receivers
        (`self.f.get(...)`) and computed receivers fall through to the
        generic dotted-call path (their κ is not tracked in
        `_dict_key_types`, so a faithful lowering could not type-check).

        WhyML `Map.get` is total (returns `None` for an absent key), so —
        unlike the subscript read `d[k]` — NO `assert { Map.get d k <> None }`
        is emitted: `dict.get` is the missing-key-tolerant form, and the
        `None -> default` arm is reachable (the body VC reflects this, so
        an `ensures \result == <literal>` claim about an arbitrary dict's
        value remains honestly unprovable — the faithful model, not a
        trusted lie)."""
        # subscript-receiver .get projection: `a[i].get("name")` — the receiver is an emit_ir
        # EXPRESSION (an array element `a[i]`, not a dotted Var), carried in the Call's `receiver`
        # field with `func == "get"`. Project over the lowered receiver (kind_of/name_of/…). Must run
        # BEFORE the `"." not in func_name` bail (func_name is bare "get" here). @mutable_state /
        # emit_ir-gated (`_is_emit_ir_expr` is False otherwise) → byte-identical for the corpus.
        if func_name == "get":
            _rcv = expr.get("receiver")
            if isinstance(_rcv, dict) and self._is_emit_ir_expr(_rcv):
                _kir = (expr.get("args") or [{}])[0]
                if isinstance(_kir, dict) and _kir.get("type") == "String":
                    _k = _kir.get("value")
                    # an element's `.get("value")` reads its SCALAR string (a leaf String/Number
                    # node's value, e.g. `args[1]["value"]` = the getattr field name) → value_of,
                    # not the sub-node svalue_of that `_EMIT_IR_PROJ["value"]` picks for chaining.
                    # orelse_of mini-M1: "body" is AMBIGUOUS — the If/For/While/Try stmt-list
                    # reader (`.get("body", [])`/no default → `stmts_of`, the table entry) vs an
                    # IfExpr's SCALAR then-branch (`.get("body", {})` → `body_of`). Disambiguate
                    # by the `.get` DEFAULT ARGUMENT shape: an empty-dict-literal `{}` default
                    # means the receiver is a ternary node, not a stmt-list container.
                    # self-tcb-reduction (_is_null_byte_lit): inside `_is_null_byte_lit`, an
                    # element's `.get("value")` reads a NUMBER leaf's INT payload (`num_of`),
                    # not the string `value_of` (which is "" for a Number → a vacuous value
                    # test). Scoped via `_current_emitting_func` → corpus/consumer-inert.
                    _proj = ("num_of" if (_k == "value"
                                 and (getattr(self, "_current_emitting_func", None) or "").endswith("_is_null_byte_lit"))
                             else "value_of" if _k == "value"
                             else "body_of" if (_k == "body" and self._get_default_is_empty_dict(expr))
                             else _EMIT_IR_PROJ.get(_k))
                    if _proj:
                        _rv = self._expr_to_whyml(_rcv, local_refs or set(),
                                                  invariant_ctx, subst)
                        return f"({_proj} {_rv})"
        # hval-retype (self-tcb-reduction Tier-5): the DOUBLED hval-map read
        # `info.get("field_types", {}).get(field)` — the OUTER `.get(field)` whose
        # RECEIVER is itself a pyval `.get` producing an `hval` (an `HMap`). Lower to a
        # nested `pairs_get` over the receiver's assoc-list carrier, projecting the leaf
        # `HStr` to an `option string` (the `Optional[str]` result). Descends the REAL
        # hval structure (non-vacuous), NOT the opaque `get_1` facade. When threaded into
        # an Optional[str] union return (`_get_return_raw_option`) the raw `option string`
        # is handed back for the caller's `Some/None` arm wrap; otherwise the scalar
        # `""`-defaulted string. Gated on a pyval `.get` receiver -> corpus/mirror inert.
        if func_name == "get":
            _rcv2 = expr.get("receiver")
            _a2 = expr.get("args") or []
            if (isinstance(_rcv2, dict) and self._expr_is_pyval(_rcv2)
                    and len(_a2) == 1):
                _rvw = self._expr_to_whyml(_rcv2, local_refs or set(),
                                           invariant_ctx, subst)
                _kw = self._expr_to_whyml(_a2[0], local_refs or set(),
                                          invariant_ctx, subst)
                # self-tcb-reduction _typeddict_field_access (a): stash the RAW `hval` form
                # of this DOUBLED read (the absent-key default `HInt 0` is falsy), computed
                # with the CORRECT local_refs (so ref locals like `!sym` deref right), so a
                # bool/if context (`_to_bool`) can apply `hval_truthy` to the raw value
                # instead of the string projection — WITHOUT re-lowering (which would lack
                # local_refs). Matched by string-equality of the projected result below.
                self._last_hval_get_raw = (
                    f"(match {_rvw} with HMap m_k8 -> "
                    f"(match pairs_get m_k8 {_kw} with Some v_ -> v_ "
                    f"| None -> (HInt 0) end) | _ -> (HInt 0) end)")
                _optstr = (f"(match {_rvw} with HMap m_k8 -> "
                           f"(match pairs_get m_k8 {_kw} with "
                           f"Some (HStr s) -> Some s | _ -> None end) "
                           f"| _ -> None end)")
                if getattr(self, "_get_return_raw_option", False):
                    return _optstr
                _res_str = f"(match {_optstr} with Some s -> s | None -> \"\" end)"
                self._last_hval_get_str = _res_str
                return _res_str
        # ghost-handler-wall Q3a (self-tcb-reduction, ghost-handler-wall-response.md
        # §Q3a/gh-spike.mlw::Q3Arity): a bare `.get("arity", <default>)` call (2 args)
        # whose receiver the tool cannot resolve to a concrete dict type — e.g. a
        # constructor-registry chain `X.get(ctor, {}).get("arity", 0)`, which the
        # generic unannotated-callee fallback would otherwise collapse to a bare,
        # UNCONSTRAINED opaque `get_2` shared by every other unresolved 2-arg `.get`
        # call in the file — is DOMAIN-KNOWN-NONNEGATIVE: an "arity" is a
        # constructor/argument COUNT, never negative, by the codebase's own registry
        # convention (populated from `len(payload)` / a literal >= 0 everywhere
        # `_constructors[...]["arity"]` is built). Keyed by the LITERAL KEY STRING
        # (not by handler/function identity — general and schema-driven; fires for
        # ANY `.get("arity", ...)` call the tool can't type, not one handler), this
        # gives the opaque getter its own DISTINCT abstract op with a genuine
        # `ensures { result >= 0 }` (an assumed, trusted-stub-shaped contract — same
        # footing as any other abstract `val`, and scoped OFF the shared `get_2` used
        # by unrelated `.get(...)` calls), so a downstream `Array.make <arity> ...`
        # (the WhyML lowering of Python's `[x] * arity`) discharges its `0 <= n`
        # precondition instead of failing on an unconstrained opaque int.
        if func_name == "get" and len(args) == 2:
            _k0 = (expr.get("args") or [None])[0]
            if isinstance(_k0, dict) and _k0.get("type") == "String" and _k0.get("value") == "arity":
                self._add_abstract_op(
                    "val get_arity_field (x0: int) (x1: int) : int\n"
                    "    ensures { result >= 0 }")
                return (f"(get_arity_field {self._coerce_to_int(args[0])} "
                        f"{self._coerce_to_int(args[1])})")
        if "." not in func_name:
            return None
        recv, method = func_name.rsplit(".", 1)
        if method != "get":
            return None
        if len(args) not in (1, 2):
            return None
        # opaque-nested-map-reader SPLIT form: `<inner-alias>.get("<lit>")` → the boundary
        # reader `<base>_<lit> <outer-key> : string` (the `.get` twin of the `<alias>["<lit>"]`
        # subscript below), keyed on the REAL outer key. Same reader the chained form uses.
        if recv in getattr(self, "_opaque_selfmap_inner_aliases", {}) and len(args) == 1:
            _k0 = (expr.get("args") or [None])[0]
            if isinstance(_k0, dict) and _k0.get("type") == "String":
                _osi = self._opaque_selfmap_inner_read(
                    recv, _k0.get("value", ""), local_refs or set(), invariant_ctx, subst)
                if _osi is not None:
                    return _osi
        # K7 (pyval-chained `.get`, self-tcb-reduction Tier-5): `.get` on a `pyval` LOCAL
        # (a chained read `registry = self.f.get(..); info = registry.get(k, {})`) lowers
        # to a REAL `PMap` match-projection over the heterogeneous carrier —
        #   (match <recv> with PMap m_k7 -> Map.get m_k7 <k> | _ -> None)
        # — NOT the opaque `registry_get_2 nm 0` facade. A 2-arg call with an empty-dict
        # `{}` default UNWRAPS the `option hval` to `hval` (the map-valued default
        # `HMap (const None)`); a 1-arg leaf call keeps the `option hval`. κ=string (the
        # `map string (option hval)` key), so the literal/Var key is read RAW (no
        # str_hash_op). Gated on `_pyval_locals` (populated only when a pyval self-field
        # feeds a `.get` chain) -> corpus byte-inert.
        if recv in getattr(self, "_pyval_locals", set()):
            _k = args[0]
            _empty = "(HMap PNil)"  # R3: empty HMap carrier is the empty assoc list
            if len(args) == 2:
                # `.get(k, {})` -> unwrap the option-hval to an hval. R3: the carrier
                # is the assoc list `hpairs`, so the lookup is the `pairs_get` fold.
                return (f"(match {recv} with HMap m_k7 -> "
                        f"(match pairs_get m_k7 {_k} with Some v_ -> v_ "
                        f"| None -> {_empty} end) | _ -> {_empty} end)")
            # `.get(k)` (leaf, no default) -> unwrap the option-pyval to a `pyval`, the
            # absent key defaulting to the `PInt 0` None-sentinel (consistent with the
            # K6 self-field `.get`; Python `dict.get(k)` returns None on a missing key).
            # An `hval` value (not `option hval`) so the read composes uniformly — e.g.
            # `{"bound": info.get("bound")}` embeds it via `_pyval_wrap`.
            _k7_leaf = (f"(match {recv} with HMap m_k7 -> "
                        f"(match pairs_get m_k7 {_k} with Some v_ -> v_ "
                        f"| None -> (HInt 0) end) | _ -> (HInt 0) end)")
            # self-tcb-reduction _namedtuple_positional_access: the leaf read is a RAW
            # `hval`. A bool/if context (`for k, v in ...: if v.get("is_namedtuple"):`)
            # must test its Python-truthiness via `hval_truthy`, NOT the `str_eq_op … ""`
            # STRING truthiness the generic `_to_bool` would apply (an hval is not a
            # string). Stash the raw form (string form == raw form here, since the read IS
            # the hval) so `_to_bool`'s string-equality match swaps in `hval_truthy`.
            self._last_hval_get_raw = _k7_leaf
            self._last_hval_get_str = _k7_leaf
            # union/match cluster: a STRING-consumed leaf (`var_name = subj.get("name")`,
            # the target is a string local) projects the `hval` to its `HStr` content via
            # `hstr_of` — a real `string` (map key / string tuple slot). Scoped to a
            # string-classified assign target -> byte-inert for the raw-hval consumers.
            if getattr(self, "_pyval_get_as_string", False):
                _proj = f"(hstr_of {_k7_leaf})"
                self._last_hval_get_str = _proj
                return _proj
            return _k7_leaf
        # §26: `X.get(k)` where X aliases a self dict-field → `self.<field>.get(k)`.
        _alias = self._alias_self_field(recv)
        if _alias:
            recv = _alias
            func_name = f"{_alias}.get"
        # module-const-dict-get: a module-level constant str->str dict
        # `OP_MAP = {"==":"=", ...}` read as `OP_MAP.get(k, default)` lowers to a
        # FAITHFUL chained string-valued if-then-else
        #   (if k = "==" then "=" else if k = "!=" then "<>" else ... else default)
        # — the exact `OP_MAP.get(op, op)` shape in `identifiers.op_translate`. The
        # result is `string`-typed: used where an int is expected it fails closed at
        # Why3 type-check (WL-02: never a silent value->int coercion). Requires an
        # EXPLICIT default (2 args); `.get(k)` without a default (None-returning) is
        # out of scope and falls through (fail-closed). A same-named local/param
        # shadows the module constant (checked first), so the recognizer fires only
        # on the genuine module-level name. In a body, string equality bridges through
        # the abstract `str_eq_op` (native `=` on strings is program-illegal, per the
        # `==` lowering); in a spec, polymorphic `=` is used directly.
        _mcd = getattr(self, "_module_const_dicts", {}).get(recv)
        _symtab0 = getattr(self, "_current_symbol_table", {}) or {}
        if (_mcd is not None and len(args) == 2
                and recv not in _symtab0
                and recv not in (local_refs or set())
                and recv not in self._current_params):
            k = args[0]
            chain = args[1]  # the caller's default is the rightmost `else`
            if self._in_spec:
                def _cmp(kk: str) -> str:
                    return f"({k} = {whyml_string_literal(kk)})"
            else:
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                def _cmp(kk: str) -> str:
                    return f"(str_eq_op {k} {whyml_string_literal(kk)})"
            for kk, vv in reversed(list(_mcd.items())):
                chain = (f"(if {_cmp(kk)} then {whyml_string_literal(vv)} "
                         f"else {chain})")
            return chain
        # compound-key const-map get: a module-const dict with a tuple key + list
        # value (`TRIGGERS`) read as `NAME.get(k, [])` lowers to the FAITHFUL defaulting
        # lookup over the opaque `map <key> (option (list <elem>))` constant:
        #   (match Map.get NAME k with Some l_ -> l_ | None -> Nil end)
        # The `[]` default is the empty list `Nil`; the returned term is `list <elem>`
        # (the getter's return type). Requires an EXPLICIT empty-list default (2 args)
        # and that `recv` is the genuine module constant (not shadowed by a local/param).
        # Fires only on a compound const dict → byte-identical for every corpus program.
        _mcc = getattr(self, "_module_const_compound_dicts", {}).get(recv)
        if (_mcc is not None and len(args) == 2
                and recv not in _symtab0
                and recv not in (local_refs or set())
                and recv not in self._current_params):
            _dargs = expr.get("args") or []
            if (len(_dargs) == 2 and isinstance(_dargs[1], dict)
                    and _dargs[1].get("type") == "ArrayLit"
                    and not _dargs[1].get("elts")):
                return (f"(match Map.get {whyml_ident(recv)} {args[0]} "
                        f"with Some l_ -> l_ | None -> Nil end)")
        # todict-reflection-plan.md R1: `d` aliases `node.to_dict()` — route
        # `d.get(key)` to the node's TYPED field (no dict materialized).
        _recv_dotted = getattr(self, "_todict_aliases", {}).get(recv)
        if _recv_dotted is not None:
            _kir = (expr.get("args") or [{}])[0]
            if isinstance(_kir, dict) and _kir.get("type") == "String":
                _proj = self._todict_emit_ir_projection(_recv_dotted, _kir.get("value"), local_refs, invariant_ctx, subst)
                if _proj is not None: return _proj
                return self._expr_to_whyml(
                    self._todict_routed_ir(_recv_dotted, _kir.get("value")),
                    local_refs or set(), invariant_ctx, subst)
        # typed-ir-for-b-ceiling.md B-C3: reflection over an `emit_ir`-typed receiver —
        # `node.get("type")` → `(kind_of node)`, `"name"`/`"attr"` → `(name_of node)`,
        # `"value"` → `(value_of node)`, `"object"` → `(object_of node)`. A total
        # projection over the sum, not a map read. Fires only when `recv` is emit_ir
        # (a param/local ExprIR); gated by the ExprIR tags → byte-identical.
        _recv_ir = {"type": "Var", "name": recv}
        if self._is_emit_ir_expr(_recv_ir):
            _kir = (expr.get("args") or [{}])[0]
            if isinstance(_kir, dict) and _kir.get("type") == "String":
                _k2 = _kir.get("value")
                # self-tcb-reduction Layer-2: a SCOPED `.get`-key projector override for the
                # receiver/slice recognizer (`receiver`/`slice`/`lower`/`upper`/`step`),
                # keyed by `_current_emitting_func` so the global bindings stay byte-inert.
                _cef2 = getattr(self, "_current_emitting_func", None) or ""
                _scoped2 = next(
                    (t for h, t in _EMIT_IR_GET_KEY_PROJ_BY_FUNC.items()
                     if _cef2 == h or _cef2.endswith("__" + h)), None)
                # self-tcb-reduction Layer-2: inside the scoped receiver/slice recognizer,
                # a `.get("value")` is AMBIGUOUS — `recv.get("value", {})` reads the
                # Subscript's ARRAY sub-node (`svalue_of`, signalled by the empty-dict
                # default), while `idx.get("value")` (no default, `!= 0`) reads a Number
                # leaf's INT payload (`num_of`). Disambiguated by the default-arg shape,
                # exactly like the `body`/`body_of` case below.
                # self-tcb-reduction _typeddict_record_literal (cap-3/4): a STRING-literal
                # default (`k.get("value", "")`) always reads the String node's CONTENT
                # (`value_of`), even inside a scoped func — so it must take PRIORITY over the
                # empty-dict/num_of disambiguation below (which is for the {}-default subscript
                # / no-default Number-index shapes). Without this exclusion the non-empty
                # scoped entry forces `num_of` (int), mistyping the string key insert.
                _scoped_val = None
                if (_scoped2 is not None and _k2 == "value"
                        and not self._get_default_is_str_literal(expr)):
                    _scoped_val = ("svalue_of" if self._get_default_is_empty_dict(expr)
                                   else "num_of")
                # self-tcb-reduction _typeddict_field_access (gap-1): `<emit_ir>.get("value",
                # "<str>")` (STRING default) reads a String IR node's CONTENT -> `value_of`
                # (a `string`), not the `svalue_of` sub-node. General (semantically the
                # string-content read) + byte-inert. Overrides the default table below.
                if _scoped_val is None and _k2 == "value" and self._get_default_is_str_literal(expr):
                    _scoped_val = "value_of"
                # orelse_of mini-M1: same "body" disambiguation as the subscript-receiver
                # site above — an empty-dict `{}` default routes to the IfExpr scalar
                # `body_of`, everything else keeps the table's `stmts_of`.
                # self-tcb-reduction (union/match cluster): `orelse` is AMBIGUOUS the same
                # way `body` is — an IfExpr's scalar else-node (`.get("orelse", {})`, empty-
                # dict default → `orelse_of`, the table entry) vs an If/For/While STATEMENT's
                # else STMT-LIST (`.get("orelse", [])`, list default → `stmts_of`, the array-
                # int stmt-list feeding `_stmts_to_whyml`). Disambiguate by the default-arg
                # shape, mirroring `body`/`body_of`. `_try_union_is_none_match` reads
                # `stmt.get("orelse", [])` (list default) → `stmts_of`.
                _proj = (_scoped_val or (_scoped2 or {}).get(_k2)
                         or ("body_of" if (_k2 == "body" and self._get_default_is_empty_dict(expr))
                             else "orelse_stmts_of" if (_k2 == "orelse"
                                                        and not self._get_default_is_empty_dict(expr))
                             else _EMIT_IR_PROJ.get(_k2)))
                if _proj:
                    _rv = self._expr_to_whyml(_recv_ir, local_refs or set(),
                                              invariant_ctx, subst)
                    return f"({_proj} {_rv})"
        symtab = getattr(self, "_current_symbol_table", {}) or {}
        recv_symtype = symtab.get(recv)
        is_dict = (recv_symtype == "dict"
                   or recv in getattr(self, "_dict_locals", set()))
        # self-field-dict-reflection: `self.<dict-field>.get(key)` reads the declared
        # record dict/set field via `Map.get self.<field> …` (not an opaque abstract).
        # `_self_field_dict_nu` returns the field's value type when `recv` is a
        # `dict`/`set`-typed record field, else None. typed-ir-for-b-ceiling.md §12.
        _field_nu = self._self_field_dict_nu(recv)
        if _field_nu is not None:
            _o, _f = recv.rsplit(".", 1)
            recv_whyml = self._expr_to_whyml(
                {"type": "FieldGet", "object": _o, "field": _f},
                local_refs or set(), invariant_ctx, subst)
            _kir = (expr.get("args") or [{}])[0]
            _kstr = isinstance(_kir, dict) and _kir.get("type") == "String"
            # cleared-hash S4: a κ=string field is `map string (option ν)` — read the
            # RAW native string key (no str_hash_op), matching the store/membership.
            if self._self_field_dict_kappa(recv) == "string":
                k = args[0]
            elif not self._in_spec and self._is_string_expr(_kir if isinstance(_kir, dict) else {}):
                self._add_abstract_op("val str_hash_op (s: string) : int")
                k = f"(str_hash_op {args[0]})"
            else:
                k = self._coerce_to_int(args[0])
            # #15: for a NESTED-collection value (`seq _`/`map _`), the explicit `[]`/`{}` default
            # is a type-generic empty that lowers to the WRONG shape (`array int` for `[]`); use the
            # ν-typed empty instead so the `None ->` arm matches the `Some v_` (inner seq/map).
            if (isinstance(_field_nu, str)
                    and _field_nu.startswith(("seq ", "map ", "array "))):
                default = self._dv_missing_default(_field_nu)
            else:
                default = args[1] if len(args) >= 2 else self._dv_missing_default(_field_nu)
            # LEVER F2: a 1-arg `.get` (no explicit default) whose `option ν` is being
            # threaded into an Optional[τ] union return — hand back the RAW `Map.get`
            # (`option ν`) so the caller wraps `Some`/`None` into the variant arms
            # (never the scalar `None -> <default>` unwrap that clashes at the slot).
            if getattr(self, "_get_return_raw_option", False) and len(args) == 1:
                return f"(Map.get {recv_whyml} {k})"
            return (f"(match Map.get {recv_whyml} {k} "
                    f"with | Some v_ -> v_ | None -> {default} end)")
        if not is_dict:
            return None
        # Receiver WhyML: a body-local dict is a `ref` (reads deref via `!`);
        # a dict parameter is a plain value. `_handle_var_expr` produces the
        # correct form for each.
        recv_whyml = self._expr_to_whyml({"type": "Var", "name": recv},
                                         local_refs or set(),
                                         invariant_ctx, subst)
        kappa = getattr(self, "_dict_key_types", {}).get(recv)
        nu = getattr(self, "_dict_value_types", {}).get(recv)
        # Key: pass through unhashed when κ = string; int-coerce otherwise
        # (matches the body subscript read path's key handling).
        k = args[0] if kappa == "string" else self._coerce_to_int(args[0])
        # Default: the user-provided arg if present, else the ν-typed missing
        # placeholder (parallel to the subscript read's `None ->` arm).
        if len(args) >= 2:
            default = args[1]
            # self-tcb-reduction Tier-5 (union/match cluster C1b): an explicit
            # `{}`/`[]`/`set()` default on an hval / nested-collection dict lowers to
            # the WRONG shape (int-map / `array int`), clashing with the `Some v_`
            # (inner hval/seq/map) arm. Use the ν-typed empty instead — the exact fix
            # the self-field-dict twin above applies. Byte-inert: only nu in
            # {hval, seq …, map …, array …} with an empty-collection literal default.
            if isinstance(nu, str) and (nu == "hval"
                    or nu.startswith(("seq ", "map ", "array "))):
                _dfir = (expr.get("args") or [None, None])[1]
                if (isinstance(_dfir, dict) and _dfir.get("type") in (
                        "DictLit", "SetLit", "ListLit", "ArrayLit", "List")
                        and not _dfir.get("keys") and not _dfir.get("elts")
                        and not _dfir.get("values")):
                    default = self._dv_missing_default(nu)
        else:
            default = self._dv_missing_default(nu)
        # LEVER F2 (see the self-field-dict twin above): thread the raw `option ν` into
        # an Optional[τ] union return instead of the scalar `None -> <default>` unwrap.
        if getattr(self, "_get_return_raw_option", False) and len(args) == 1:
            return f"(Map.get {recv_whyml} {k})"
        _res = (f"(match Map.get {recv_whyml} {k} "
                f"with | Some v_ -> v_ | None -> {default} end)")
        # self-tcb-reduction Tier-5 (union/match cluster sub-increment 2): a STRING-typed
        # target (`name = x_ir.get("name")`, `x_ir` a `Dict[str, PyVal]` param with hval
        # codomain) forces the `.get` leaf to project its `hval` to a `string` (`hstr_of`),
        # so the `name := <string>` typechecks — the map-param twin of the pyval-local `.get`
        # string projection above. Scoped to `_pyval_get_as_string` (a string-classified
        # assignment target) + an hval codomain -> corpus/other-mirror byte-inert.
        # cap1 (self-tcb-reduction `_refine_tuple_return_type`): `func.get("name", "")` on the
        # `Dict[str, PyVal]` func param (hval codomain) with a STRING-literal default is a
        # string read (`_nm` -> `"__" in _nm` / `_nm.split(...)` / self-type write). Project
        # the hval `Some`-arm via `hstr_of` INSIDE the match so BOTH arms are `string` — the
        # whole-match `hstr_of` (the `_pyval_get_as_string` path just below) cannot fix the
        # already-ill-typed hval-`Some` vs string-`None` arms. Gated on the method -> byte-inert
        # for the corpus and every other mirror. Runs BEFORE the `_pyval_get_as_string` path.
        if (nu == "hval" and self._emitting_refine_tuple_return_type()
                and len(args) >= 2 and self._get_default_is_str_literal(expr)):
            return (f"(match Map.get {recv_whyml} {k} "
                    f"with | Some v_ -> (hstr_of v_) | None -> {default} end)")
        if nu == "hval" and getattr(self, "_pyval_get_as_string", False):
            return f"(hstr_of {_res})"
        return _res

    def _const_dict_name(self, recv: str) -> Optional[str]:
        """`recv` names a genuine module-level constant str->str dict (in
        `_module_const_dicts`) NOT shadowed by a local/param/symtab entry."""
        if not isinstance(recv, str):
            return None
        if getattr(self, "_module_const_dicts", {}).get(recv) is None:
            return None
        symtab0 = getattr(self, "_current_symbol_table", {}) or {}
        if (recv in symtab0
                or recv in getattr(self, "_current_params", set())):
            return None
        return recv

    def _const_pair_dict_name(self, recv: str) -> Optional[str]:
        """`recv` names a genuine module-level constant `str -> (str, int)` PAIR dict
        (in `_module_const_pair_dicts`) NOT shadowed by a local/param/symtab entry.
        The pair-dict twin of `_const_dict_name`."""
        if not isinstance(recv, str):
            return None
        if getattr(self, "_module_const_pair_dicts", {}).get(recv) is None:
            return None
        symtab0 = getattr(self, "_current_symbol_table", {}) or {}
        if (recv in symtab0
                or recv in getattr(self, "_current_params", set())):
            return None
        return recv

    def _const_dict_value_seq(self, val_ir: Dict[str, Any],
                              local_refs: Set[str],
                              invariant_ctx: bool = False,
                              subst: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """module-const-dict READ -> a faithful `seq string` value (the return-slot
        shape for a `List[str]` function). Mirror-only const-dict theory (like the
        `.get(k, default)` chained-ITE just above): NO corpus program reads a
        module-const dict this way, so this is byte-inert by construction.

        Three shapes, each returning a `Seq.cons`-chain of the dict's own value
        literals (mutation-sensitive: perturb a key or value and the term moves):
          1. `list(<X>.values())` / `<X>.values()`  -> every value, in dict order.
          2. `[v for k, v in <X>.items() if <k> in <set>]` -> the values whose key
             passes the membership filter (`if (Map.get <set> "k0") then Seq.cons ...`).

        SHAPE-2 IDIOM ASSUMPTION (flagged): Module5 collapses a comprehension tuple
        target `(k, v)` to `_comp_var` (`frontend/Module5_IREmitter.py`), discarding
        which loop name binds the KEY vs the VALUE of `.items()`. This recognizer
        applies the standard `for k, v in d.items()` idiom — the COLLECTED var (in
        `elt`) is the value, the FILTERED var (tested `in <set>`) is the key. Exact
        for the sole consumer (`predicate_definitions`); a non-idiomatic swap
        (`[k for k, v in d.items() if v in s]`) would mis-model — see the reopening
        note in the report (preserve tuple-target names in Module5). Returns None
        (fail-closed to the existing lowering) on any deviation from these shapes."""
        if not isinstance(val_ir, dict):
            return None
        t = val_ir.get("type")
        # 1a. `list(<inner>)` wrapper -> unwrap.
        if t == "Call" and val_ir.get("func") == "list":
            _a = val_ir.get("args") or []
            if len(_a) == 1:
                return self._const_dict_value_seq(_a[0], local_refs, invariant_ctx, subst)
            return None
        # 1b. `<X>.values()` on a module-const dict.
        if t == "Call" and isinstance(val_ir.get("func"), str):
            _fn = val_ir["func"]
            if _fn.endswith(".values") and not (val_ir.get("args") or []):
                _cd = self._const_dict_name(_fn[:-len(".values")])
                if _cd is not None:
                    _mcd = self._module_const_dicts[_cd]
                    _expr = "Seq.empty"
                    for _vv in reversed(list(_mcd.values())):
                        _expr = f"(Seq.cons {whyml_string_literal(_vv)} {_expr})"
                    return _expr
            return None
        # 2. `[<v> for <(k,v)> in <X>.items() if <k> in <set>]`.
        if t == "ListComp":
            return self._const_dict_items_filter_seq(
                val_ir, local_refs, invariant_ctx, subst)
        return None

    def _const_dict_items_filter_seq(self, val_ir: Dict[str, Any],
                                     local_refs: Set[str],
                                     invariant_ctx: bool,
                                     subst: Optional[Dict[str, Any]]) -> Optional[str]:
        """Shape-2 helper (see `_const_dict_value_seq`): the membership-filtered
        `.items()` comprehension over a module-const dict -> a conditional
        `Seq.cons` chain. Fail-closed (None) unless the exact idiom matches."""
        _gens = val_ir.get("generators") or []
        if len(_gens) != 1:
            return None
        _g = _gens[0]
        _it = _g.get("iter") or {}
        if not (isinstance(_it, dict) and _it.get("type") == "Call"
                and isinstance(_it.get("func"), str)
                and _it["func"].endswith(".items")
                and not (_it.get("args") or [])):
            return None
        _cd = self._const_dict_name(_it["func"][:-len(".items")])
        if _cd is None:
            return None
        # elt must be a single loop var (the COLLECTED value, per the idiom).
        _elt = val_ir.get("elt") or {}
        if not (isinstance(_elt, dict) and _elt.get("type") == "Var"):
            return None
        _elt_var = _elt.get("name")
        # exactly one `<filter-var> in <set>` guard; filter-var is the KEY.
        _ifs = _g.get("ifs") or []
        if len(_ifs) != 1:
            return None
        _f = _ifs[0]
        if not (isinstance(_f, dict) and _f.get("type") == "BinOp"
                and _f.get("op") == "in"
                and isinstance(_f.get("left"), dict)
                and _f["left"].get("type") == "Var"):
            return None
        _key_var = _f["left"].get("name")
        if _key_var == _elt_var or _elt_var is None or _key_var is None:
            return None
        _set_w = self._expr_to_whyml(_f.get("right") or {}, local_refs or set(),
                                     invariant_ctx, subst)
        _mcd = self._module_const_dicts[_cd]
        # Build a LINEAR `let`-chain (tail bound once per element) rather than
        # inlining the accumulator into both `if` arms (which would duplicate the
        # tail 2^N times). `_cdf_i` names the tail after element i.
        _items = list(_mcd.items())
        _lets: List[str] = []
        _acc = "Seq.empty"
        for _i in range(len(_items) - 1, -1, -1):
            _kk, _vv = _items[_i]
            _memb = f"(Map.get {_set_w} {whyml_string_literal(_kk)})"
            _nm = f"_cdf_{_i}"
            _lets.append(
                f"let {_nm} = (if {_memb} then "
                f"(Seq.cons {whyml_string_literal(_vv)} {_acc}) else {_acc}) in")
            _acc = _nm
        return "(" + " ".join(_lets) + f" {_acc})"

    def _lower_getattr(self, expr: Dict[str, Any], args: List[str],
                       local_refs: Set[str], invariant_ctx: bool,
                       subst: Optional[Dict[str, str]]) -> str:
        """Lower `getattr(obj, name[, default])` — see the `getattr` branch in
        `_handle_call_expr`. Record-field access when the field is statically known;
        else the default (sound under-approximation)."""
        args_ir = expr.get("args", [])
        obj_ir = args_ir[0]
        name_ir = args_ir[1] if len(args_ir) > 1 else {}
        default_ir = args_ir[2] if len(args_ir) > 2 else {"type": "Number", "value": 0}
        # `_compute_return_type` PATH(b): `getattr(self, "_compound_map_getter", None)`
        # reads the opaque `Optional[Dict[str, str]]` self-field -> `compound_map_getter_of
        # self : option (map string (option string))` (the option-of-map reader), NOT the
        # folded `0` default. Per-method scoped -> byte-inert elsewhere.
        if (self._emitting_compute_return_type()
                and isinstance(obj_ir, dict) and obj_ir.get("name") == "self"
                and isinstance(name_ir, dict) and name_ir.get("type") == "String"
                and name_ir.get("value") == "_compound_map_getter"):
            _st = self._current_self_type or "functionemissionmixin"
            self._add_abstract_op(
                f"val compound_map_getter_of (self: {_st}) "
                ": option (map string (option string))")
            return "(compound_map_getter_of self)"
        # Resolve `obj` to a known record-typed Var and `name` to a string literal.
        if isinstance(obj_ir, dict) and obj_ir.get("type") == "Var":
            obj_name = obj_ir.get("name", "")
            st = getattr(self, "_current_symbol_table", {})
            obj_type = st.get(obj_name)
            if obj_type and obj_type.lower() in getattr(self, "_record_types", {}):
                rec_info = self._record_types[obj_type.lower()]
                fields = rec_info.get("fields", []) if isinstance(rec_info, dict) else []
                if isinstance(name_ir, dict) and name_ir.get("type") == "String":
                    attr = name_ir.get("value", "")
                    if attr in fields:
                        rec_lower = obj_type.lower()
                        return f"{whyml_ident(obj_name)}.{self._field_label(rec_lower, attr)}"
            # self-tcb-reduction _typeddict_record_literal (cap-1): `getattr(self,
            # "<field>", <default>)` on a MODELED self record-field (the defensive
            # self-field read) reads the REAL field, not the folded default — the same
            # native `self.<label>` form as a direct `self.<field>` access (§8943).
            # @mutable_state-gated (the self-annotation emission only) + only when the
            # name is a declared self field, so a corpus `getattr(self, "_x", d)` on an
            # UNMODELED field keeps the default fall-through -> byte-inert.
            if (obj_name == "self"
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())
                    and isinstance(name_ir, dict) and name_ir.get("type") == "String"
                    and name_ir.get("value") in getattr(self, "_all_record_fields", set())
                    and isinstance(default_ir, dict)
                    and default_ir.get("type") == "String"):
                return f"self.{self._field_label(self._current_self_type, name_ir['value'])}"
        # Dynamic-config / unknown-field path: emit the default. getattr returns
        # `default` for an absent attribute, so this is sound (the real runtime
        # value is opaque; any contract depending on it fails to prove).
        # For a NON-scalar default (dict/list/set literal) the lowered form is a
        # map/array, which would mismatch the enclosing local's int-typed `ref`
        # slot (first-assignment inference sees a `Call` RHS, not a collection
        # literal, so it can't promote the local to a dict/array). Coerce those
        # to an opaque `0` — the dict/list content is then unmodeled (a `.get`
        # chain on the result will not prove; fails-safe). A scalar int/bool
        # default passes through faithfully.
        if len(args_ir) <= 2:
            return "0"
        nt = default_ir.get("type") if isinstance(default_ir, dict) else ""
        if nt in ("DictLit", "ArrayLit", "SetLit", "Call"):
            return "0"
        return self._expr_to_whyml(default_ir, local_refs, invariant_ctx, subst)

    def _subst_params(self, ir: Any, arg_nodes: Dict[str, Any]) -> Any:
        """Deep-copy a value IR, replacing each `Var(param)` with its pre-lowered arg
        node (`RawWhyml`) — the IR-level value substitution used by parametrized record
        construction. Pure structural recursion over dict/list IR; leaves are returned
        as-is."""
        if isinstance(ir, dict):
            if ir.get("type") == "Var" and ir.get("name") in arg_nodes:
                return arg_nodes[ir["name"]]
            return {k: self._subst_params(v, arg_nodes) for k, v in ir.items()}
        if isinstance(ir, list):
            return [self._subst_params(x, arg_nodes) for x in ir]
        return ir

    def _init_value_free_names(self, ir: Any) -> Set[str]:
        """The set of `Var` names referenced in a constructor init_body value IR —
        the parameters an initialiser depends on. Used by `_call_record_constructor`
        to skip (keep the typed default for) a field whose initialiser references a
        param OUTSIDE a partial positional-prefix binding (WL-07 — a trailing
        omitted-with-default field), never emitting a bare unsubstituted param var."""
        out: Set[str] = set()
        if isinstance(ir, dict):
            if ir.get("type") == "Var" and isinstance(ir.get("name"), str):
                out.add(ir["name"])
            for v in ir.values():
                out |= self._init_value_free_names(v)
        elif isinstance(ir, list):
            for x in ir:
                out |= self._init_value_free_names(x)
        return out

    def _mixed_literal_reject_kind(self, elts: List[Dict[str, Any]]) -> Optional[str]:
        """WL-04g (wrong-lowering-to-fix.md §WL-04 mixed-element residual): return a
        human-readable KIND string for the first element of a list literal whose
        faithful type is NON-int — a `str` literal, a `float` `Number`, a `Tuple`, or
        a known record constructor `Call` — or None if every element is
        int-coercible (an int/bool literal, or an expression the model treats as int:
        a `Var`/`BinOp`/non-record `Call`/…).

        This is a FAIL-CLOSED guard called ONLY from the `ArrayLitExpr` int-coercion
        FALLBACK, i.e. AFTER the uniform non-int branches (all-str/all-float WL-04a,
        all-record WL-04c, all-equal-arity-tuple) have already claimed the
        homogeneous cases. So a non-int element surviving to here PROVES the literal
        is heterogeneous — a heterogeneous `array` has no faithful WhyML type and
        must be rejected (never int-coerced: a `str` would hash to a well-typed int
        and PROVE a false content claim; a `float`/record would ill-type). Returns
        None (→ the caller keeps the sound `array int` path, byte-identical) when the
        literal is all-int/bool/expression."""
        rec_types = getattr(self, "_record_types", {})
        for e in elts:
            if not isinstance(e, dict):
                continue
            et = e.get("type")
            if et == "String":
                return "str"
            if et == "Number" and isinstance(e.get("value"), float):
                return "float"
            if et == "Tuple":
                return "tuple"
            if et == "Call" and e.get("func") in rec_types:
                return f"record ({e.get('func')})"
        return None

    def _record_ctor_list_elem(self, elts: List[Dict[str, Any]]) -> Optional[str]:
        """WL-04c (wrong-lowering-to-fix.md §WL-04 record LITERAL residual): if EVERY
        element of a list literal is a full-arity constructor Call to the SAME known
        record whose constructor FAITHFULLY captures every field from a positional
        param, return the record CLASS NAME — so the literal builds `array <record>`
        with faithful element field content (each element the record literal
        `{ x = 1; y = 2 }`) and `a[i].field` projects the real field. Returns None
        (→ the caller keeps the int-coercion default / opaque path, fail-closed) for:
        an empty / non-Call element, a mixed-record literal, a keyword/under-arity
        call (`args` short of `init_params`), or a record whose constructor does NOT
        set every field from its params (e.g. a `@dataclass` with no explicit
        `__init__` — its ctor DROPS its args, a separate pre-existing gap, so its
        literal element is NOT content-faithful and must NOT be projected natively)."""
        if not elts:
            return None
        rec_types = getattr(self, "_record_types", {})
        rec_name: Optional[str] = None
        for e in elts:
            if not (isinstance(e, dict) and e.get("type") == "Call"):
                return None
            fn = e.get("func")
            if fn not in rec_types:
                return None
            if rec_name is None:
                rec_name = fn
            elif fn != rec_name:
                return None            # a mixed-record literal is out of scope
            info = rec_types[fn]
            fields = info.get("fields", [])
            init_params = info.get("init_params", [])
            covered = {en.get("field") for en in info.get("init_body", [])}
            # faithful iff the ctor sets every field from a positional param AND the
            # call provides full arity (so `_call_record_constructor` threads args).
            if not init_params or not set(fields) <= covered:
                return None
            # FULL ARITY, positionally OR by keyword. `_call_record_constructor`
            # threads BOTH (`kwargs_map`/`kwargs_ir`), and the class-by-name factory
            # `_N("alias")(name=…, asname=…)` is keyword-ONLY — under the old
            # positional-only test such a literal fell through to the WL-04g
            # heterogeneous-reject and the whole conversion failed closed. A call is
            # accepted iff the positional prefix plus the named keywords COVER every
            # `init_param` exactly once (no duplicate, no unknown name), which is the
            # same completeness `_call_record_constructor` needs to thread every field.
            _pos = e.get("args", []) or []
            _kwnames = [k.get("arg") for k in (e.get("keywords") or [])
                        if isinstance(k, dict) and k.get("arg")]
            if len(_pos) > len(init_params):
                return None
            _bound = list(init_params[:len(_pos)]) + list(_kwnames)
            if sorted(_bound) != sorted(init_params):
                return None
        return rec_name

    def _irlist_call_returns_emit_ir_array(self, fn: str) -> bool:
        """PYTHON-AST NODE CTOR FAMILY (relaunch #11): does the callee `fn` declare a
        return type that emits as `array emit_ir` — i.e. is its result a real NODE LIST
        the `arr_to_irlist` bridge may carry into an `irlist` payload slot? Resolved from
        the module's own return-type map (`self.<m>` self-calls are class-prefix mangled
        the way `_rhs_yields_map` does it), so a helper whose interface is int-erased or
        differently typed answers False and the construction DECLINES."""
        if not isinstance(fn, str) or not fn:
            return False
        _key = fn
        if fn.startswith("self."):
            _cls = getattr(self, "_current_self_type", None)
            _tail = fn[len("self."):]
            _key = f"{_cls}__{_tail}" if _cls else _tail
        _rt = (getattr(self, "_module_method_return_types", {}) or {}).get(_key)
        return _rt == "array emit_ir"

    def _call_returns_pyconst_val(self, fn: str) -> bool:
        """LITERAL-VALUE MODEL (relaunch #12): does the callee `fn` declare a return type
        that emits as `pyconst_val` — i.e. is its result a real Python LITERAL VALUE the
        `Constant.value` slot may carry? This is the gate on `_parse_number`, whose
        `-> "PyConstVal"` interface is the ONLY thing that makes the number-literal sites
        modellable at all. Resolved from the module's own return-type map (self-calls are
        class-prefix mangled the way `_irlist_call_returns_emit_ir_array` does it), so a
        helper whose interface is int-erased or differently typed answers False and the
        construction DECLINES fail-closed."""
        if not isinstance(fn, str) or not fn:
            return False
        _key = fn
        if fn.startswith("self."):
            _cls = getattr(self, "_current_self_type", None)
            _tail = fn[len("self."):]
            _key = f"{_cls}__{_tail}" if _cls else _tail
        _rt = (getattr(self, "_module_method_return_types", {}) or {}).get(_key)
        return _rt == "pyconst_val"

    def _call_returns_string(self, fn: str) -> bool:
        """Does the callee `fn` declare a `string` return type? The `string` twin of
        `_call_returns_pyconst_val`, resolved from the same module return-type map with the
        same self-call class-prefix mangling. Used by the `iropt_str` payload slot to admit
        a PRESENT string produced by a call (`_N("MatchAs")(pattern=p,
        name=self._capture_name("as"))` in `pattern`) as `(IrSSome …)`. Fail-closed: a
        callee whose interface is int-erased or otherwise typed answers False and the
        construction declines exactly as before."""
        if not isinstance(fn, str) or not fn:
            return False
        _key = fn
        if fn.startswith("self."):
            _cls = getattr(self, "_current_self_type", None)
            _tail = fn[len("self."):]
            _key = f"{_cls}__{_tail}" if _cls else _tail
        return (getattr(self, "_module_method_return_types", {}) or {}
                ).get(_key) == "string"

    def _call_irnode_constructor(self, args: List[str], func_name: str,
                                 kwargs_map: Optional[Dict[str, str]] = None,
                                 none_arg_indices: Optional[Set[int]] = None,
                                 none_kwargs: Optional[Set[str]] = None,
                                 raw_kwargs: Optional[Dict[str, Any]] = None,
                                 elt_lower: Optional[Any] = None
                                 ) -> Optional[str]:
        """NODE-CTOR (self-tcb-reduction): `C(a, b, c)` for a CSL-AST node class that the
        SHARED `_IRNODE_CTORS` table models → the `emit_ir` ADT application
        `(IrC <payload in ctor order>)`.

        The binding is BY NAME, never by position: the class's positional `__init__`
        params (`init_params`, captured by Module5 — for a `@dataclass` these ARE the
        declared fields in order) name the actuals, and `_IRNODE_CTORS[C]`'s payload list
        names the ctor's argument order. Every payload name must be supplied by a
        positional param or an explicit keyword, or the lowering DECLINES (returns None →
        the record-literal fallback), so a partial/renamed/extra-field construction can
        never silently drop or reorder a child.

        Gated on @mutable_state (the emitter model, `_current_self_type` in
        `_mutable_state_classes`) exactly like `_lower_irnode_construction`, so no corpus
        program — none of which declares a @mutable_state class — changes a byte.

        self-tcb-reduction (_canonical_preservation_ensures): ALSO fire when the emitting
        method is `_canonical_preservation_ensures` (an endswith-match on
        `_current_emitting_func`, the byte-inert method-sentinel pattern of the
        kind_of-tailoring / mktuple-elts caps). PyCSLWeaver is NOT @mutable_state, so the
        class-wide gate above would decline; the method sentinel confines the CSL-AST-node
        construction lowering to this one mirror method, keeping every corpus program (and
        every other mirror handler) byte-identical."""
        _cef = getattr(self, "_current_emitting_func", None) or ""
        _cpe_scope = (_cef == "_canonical_preservation_ensures"
                      or _cef.endswith("___canonical_preservation_ensures"))
        if (getattr(self, "_current_self_type", None) not in getattr(
                self, "_mutable_state_classes", set())) and not _cpe_scope:
            return None
        # self-tcb-reduction (_canonical_preservation_ensures): two CSL-AST node classes
        # this method constructs are NOT in the generic fixed-payload `_IRNODE_CTORS`
        # table — a `Forall` carries two OPTIONAL binder fields (var/body positional,
        # binder_type/domain defaulted None), and a `FieldSubscript` is the COMPOSITE
        # `self.<field>[i]`. Lower each to the EXISTING emit_ir ctors directly (no new ADT
        # leaf, no certificate change). Gated on the method sentinel → byte-inert for the
        # corpus and every other mirror.
        if _cpe_scope:
            if func_name == "Forall" and len(args) == 2:
                # Forall(var, body): binder_type/domain default None -> IrSNone / IrONone,
                # exactly the dict-path `_lower_quant_optfield` result. The ADT ctor is
                # `IrForall string emit_ir iropt_str iropt_ir`.
                return f"(IrForall {args[0]} {args[1]} IrSNone IrONone)"
            if func_name == "FieldSubscript" and len(args) == 2:
                # FieldSubscript(field, index) models `self.<field>[index]` -> the
                # subscript of the self-field: `IrSub (IrFieldGet "self" <field>) <index>`.
                # Faithful (the SAME shape the body path emits for `self.f[i]`), reusing the
                # existing IrSub / IrFieldGet ctors (no new leaf).
                return f'(IrSub (IrFieldGet "self" {args[0]}) {args[1]})'
        # PYTHON-AST NODE CTOR FAMILY (`_fin` recognizer vein, increment 9): the pure_ast
        # parser's node classes are looked up in their OWN table, consulted BEFORE the
        # shared CSL-AST one so a name that exists in both (the CSL and Python ASTs share
        # several spellings) resolves to the Python-AST arm inside the parser file and to
        # the CSL arm everywhere else. Gated on `_uses_pyast_parser` (the file defines
        # `_Parser._fin`) -> corpus and every other mirror byte-identical.
        ctor = None
        if self._uses_pyast_parser():
            from frontend.ir_resolve import _PYAST_IRNODE_CTORS as _PYC
            _pc = _PYC.get(func_name)
            if _pc is not None:
                ctor = (_pc[0], [_fn for _fn, _ty in _pc[1]])
        if ctor is None:
            ctor = self._IRNODE_CTORS.get(func_name)
        if ctor is None:
            return None
        # PYTHON-AST NODE CTOR FAMILY (increment 12): a family member's `init_params`
        # come from the STRUCTURAL `_NODE_SPEC` harvest (`ir_resolve`, key
        # `pyast_ctor_init_params`), NOT from a `_PURE_AST_FIELD_TABLE` record. Requiring
        # a record entry would drag the harvested record into every OTHER mirror that
        # mentions the same class — measured: adding `BoolOp` to the field table retyped
        # the `PEx_BoolOp` arm of Module5's `pyast_expr` ADT while the handler's own
        # signature stayed opaque, an L3-tc error behind an innocuous-looking byte diff.
        # The map is published only when the ctor payload's field names match
        # `_NODE_SPEC` exactly, so an ASDL drift makes the construction DECLINE.
        _pyast_params = (self.ir.get("pyast_ctor_init_params", {}) or {}).get(func_name)
        if _pyast_params is not None:
            init_params = list(_pyast_params)
        else:
            rec_info = getattr(self, "_record_types", {}).get(func_name)
            if not rec_info:
                return None
            init_params = rec_info.get("init_params", [])
        if len(args) > len(init_params):
            return None
        bound: Dict[str, str] = dict(zip(init_params, args))
        bound.update(kwargs_map or {})
        cname, payload = ctor
        # PYTHON-AST NODE CTOR FAMILY (increment 12): per-slot payload TYPES, for the
        # `irlist` variadic-child bridge below. Empty for a CSL-AST ctor (whose table
        # carries names only), so that path is unchanged.
        _irlist_slots: Dict[str, str] = {}
        if self._uses_pyast_parser():
            from frontend.ir_resolve import _PYAST_IRNODE_CTORS as _PYC2
            _pc2 = _PYC2.get(func_name)
            if _pc2 is not None:
                _irlist_slots = dict(_pc2[1])
        optfields = self._IRNODE_CTOR_OPTFIELDS.get(func_name, {})
        strdefaults = self._IRNODE_CTOR_STRDEFAULTS.get(func_name, {})
        # Fields whose actual is the EXPLICIT `None` literal — a positional None at index i
        # binds `init_params[i]`, a keyword `f=None` binds `f`. For an `iropt_str` optfield
        # slot such a field is `IrSNone` (faithful), NOT the ill-typed `IrSSome 0`.
        none_fields = {init_params[i] for i in (none_arg_indices or set())
                       if i < len(init_params)} | (none_kwargs or set())
        parts: List[str] = []
        for f in payload:
            if optfields.get(f) == "iropt_str":
                # Monomorphic-option `iropt_str` slot (an `Optional[str] = None` field):
                # an EXPLICIT-None or OMITTED field is `IrSNone` (faithful to the None
                # value/default); a BOUND string actual wraps to `(IrSSome <v>)` — NOT a
                # dropped child.
                if f in none_fields or f not in bound:
                    parts.append("IrSNone")
                else:
                    parts.append(f"(IrSSome {bound[f]})")
                continue
            if f not in bound and f in strdefaults:
                # A required string slot OMITTED at the call site → fill it from its
                # class field's concrete string default (a compile-time constant), NOT a
                # dropped child. Faithful to Python positional-default semantics.
                parts.append(f'"{strdefaults[f]}"')
                continue
            # Every REQUIRED ctor payload slot must be bound by the construction — an
            # unbound slot would mean a DROPPED child, which is exactly the facade this
            # build exists to avoid. Decline instead.
            if f not in bound:
                return None
            # PYTHON-AST NODE CTOR FAMILY (increment 12): an `irlist` payload slot — the
            # VARIADIC child list of a BoolOp/MatchOr/Tuple-shaped node. The construction
            # site supplies a `seq emit_ir` LOCAL (`values = [left]` + `.append` in the
            # operator-chain loop), so it crosses a seq->irlist boundary exactly as a
            # `-> List[<record>]` return crosses seq->array through `materialize_<rec>`.
            # `seq_to_irlist` is the same shape as those bridges: a fresh result pinned
            # POINTWISE by the ADT's own DEFINED `irlen`/`irnth`, so the list is EQUAL to
            # the seq and nothing is erased — no axiom, no new ADT. DECLINES (→ the whole
            # construction declines, fail-closed) unless the actual really is a `!<local>`
            # deref of a seq local KNOWN to carry emit_ir elements, so a slot can never be
            # filled with an int-erased or empty list.
            # PYTHON-AST NODE CTOR FAMILY (increment 13): an `iropt_ir` payload slot — a
            # node field that is genuinely OPTIONAL (`_OPTIONAL_FIELDS['Yield'] ==
            # ('value',)`: a bare `yield` really carries nothing). Modelling it as a bare
            # `emit_ir` would make the ABSENT value read as a NODE, which is the
            # None-reads-as-a-value erasure this campaign has repaired before. The three
            # shapes: an EXPLICIT/omitted None -> `IrONone`; an `Optional[ExprIR]` LOCAL,
            # which lesson (ab) makes a synthesized `_union_*` -> the arm projection into
            # `IrOSome`/`IrONone`; a plain present emit_ir expression -> `(IrOSome x)`.
            # Anything else DECLINES (fail-closed).
            if _irlist_slots.get(f) == "iropt_ir":
                if f in none_fields:
                    parts.append("IrONone")
                    continue
                # OPTIONAL-NODE LOCAL (relaunch #11): the actual is a local this file's
                # prescan classified as an `iropt_ir` LOCAL, so it ALREADY carries the
                # carrier value — bind its deref straight into the slot. No projection, no
                # sentinel: an absent optional child reads back as the honest `IrONone`.
                _rn0 = (raw_kwargs or {}).get(f)
                if (isinstance(_rn0, dict) and _rn0.get("type") == "Var"
                        and _rn0.get("name") in getattr(
                            self, "_iropt_ir_local_vars", set())):
                    parts.append(f"!{whyml_ident(str(_rn0['name']))}")
                    continue
                _rk = (raw_kwargs or {}).get(f)
                if isinstance(_rk, dict) and _rk.get("type") == "None":
                    parts.append("IrONone")
                    continue
                if isinstance(_rk, dict) and _rk.get("type") == "Var":
                    _oname = str(_rk.get("name"))
                    _osym = getattr(self, "_current_symbol_table", {}).get(_oname)
                    _oderef = ("!" if _oname in getattr(
                        self, "_optional_union_locals", set()) else "")
                    _oproj = self._union_read_iropt_ir_projection(
                        _osym, f"{_oderef}{whyml_ident(_oname)}")
                    if _oproj is not None:
                        parts.append(_oproj)
                        continue
                return None
            # PYTHON-AST NODE CTOR FAMILY (increment 15): an `iropt_str` payload slot —
            # a node field that is genuinely OPTIONAL and carries a STRING
            # (`_OPTIONAL_FIELDS['MatchStar'] == ('name',)`: a bare `*_` really carries NO
            # capture name). Modelling it as a plain `string` would make the ANONYMOUS star
            # read back as a capture named `""` — lesson (aq)'s measured erasure. The three
            # shapes mirror the `iropt_ir` slot exactly: an EXPLICIT/omitted None ->
            # `IrSNone`; an `Optional[str]` LOCAL (a synthesized `_union_*`, lesson (ab)) ->
            # the arm projection into `IrSSome`/`IrSNone`; a plain present string expression
            # -> `(IrSSome x)`. Anything else DECLINES (fail-closed).
            if _irlist_slots.get(f) == "iropt_str":
                if f in none_fields:
                    parts.append("IrSNone")
                    continue
                _rk = (raw_kwargs or {}).get(f)
                if isinstance(_rk, dict) and _rk.get("type") == "None":
                    parts.append("IrSNone")
                    continue
                if isinstance(_rk, dict) and _rk.get("type") == "Var":
                    _oname = str(_rk.get("name"))
                    _osym = getattr(self, "_current_symbol_table", {}).get(_oname)
                    _oderef = ("!" if _oname in getattr(
                        self, "_optional_union_locals", set()) else "")
                    _oproj = self._union_read_iropt_str_projection(
                        _osym, f"{_oderef}{whyml_ident(_oname)}")
                    if _oproj is not None:
                        parts.append(_oproj)
                        continue
                    # A plain STRING local/param (not an Optional union) is a PRESENT
                    # name — `(IrSSome v)`. Gated on the string classification so an
                    # int-erased actual can never be injected as a string.
                    if _osym in ("str", "string"):
                        parts.append(f"(IrSSome {bound[f]})")
                        continue
                    return None
                if isinstance(_rk, dict) and _rk.get("type") == "String":
                    parts.append(f"(IrSSome {bound[f]})")
                    continue
                # A PRESENT string produced by a CALL (relaunch #13): `pattern` builds
                # `_N("MatchAs")(pattern=p, name=self._capture_name("as"))`, and
                # `_capture_name`'s declared `-> str` makes the actual a genuine `string`.
                # `as`-patterns ALWAYS carry a capture name, so `IrSSome` is exact. Gated
                # on the callee's declared return type, so an int-erased helper still
                # declines the whole construction.
                if (isinstance(_rk, dict) and _rk.get("type") == "Call"
                        and self._call_returns_string(_rk.get("func", ""))):
                    parts.append(f"(IrSSome {bound[f]})")
                    continue
                return None
            if _irlist_slots.get(f) == "pyconst_val":
                # LITERAL-VALUE MODEL (relaunch #12): the `Constant.value` slot, now typed
                # with the CERTIFIED `pyconst_val` union rather than the bespoke two-arm
                # `irconst` it replaced (see preamble.py at the type's declaration). Each
                # shape maps to the arm the Rocq/Lean certificate pins it to, and ANY OTHER
                # shape DECLINES the whole construction, fail-closed: an unmodelled literal
                # is never mis-typed into some other arm.
                if f in none_fields:
                    parts.append("PVNone")
                    continue
                _rc = (raw_kwargs or {}).get(f)
                if isinstance(_rc, dict) and _rc.get("type") == "None":
                    parts.append("PVNone")
                    continue
                if isinstance(_rc, dict) and _rc.get("type") == "String":
                    parts.append(f"(PVStr {bound[f]})")
                    continue
                # THE BOOLEAN LITERAL (relaunch #13, `atom`'s `True`/`False` arms): the
                # certified `pyconst_val` has a DEDICATED `PVBool bool` arm, so a Python
                # `True` is `(PVBool true)` — NOT the int-encoded `PVInt 1` the leaf
                # `IrBoolC` convention uses. Reading it back through `pvbool_of` is exact.
                if isinstance(_rc, dict) and _rc.get("type") == "Bool":
                    parts.append("(PVBool true)" if _rc.get("value") else "(PVBool false)")
                    continue
                # THE ELLIPSIS LITERAL (relaunch #13, `atom`'s `...` arm): Module5 lowers
                # `...` to the integer ZERO, so the ONLY thing that tells it apart from a
                # literal `0` is the ADDITIVE `py_ellipsis` marker key `_py_expr_constant`
                # attaches. Mapped to the certificate's `PVEllipsis` singleton — the model
                # therefore does NOT claim `... == 0`, which the bare Number arm would.
                if (isinstance(_rc, dict) and _rc.get("type") == "Number"
                        and _rc.get("py_ellipsis")):
                    parts.append("PVEllipsis")
                    continue
                _pvd = self._inline_pyconst_dict_index(_rc, elt_lower)
                if _pvd is not None:
                    parts.append(_pvd)
                    continue
                # NOTE (relaunch #12): the `PVBool` and `PVEllipsis` arms were BUILT
                # AND MEASURED WORKING for `atom` (`value=True` -> `(PVBool true)`, not
                # `PVInt 1`; `value=...` -> `PVEllipsis`, read off an additive
                # `py_ellipsis` marker in `_py_expr_constant`, which is the ONLY thing
                # that can tell `...` apart from a literal `0` because Module5 lowers it
                # to the integer ZERO). Both were REVERTED WITH the `atom` spike — the
                # blocker there is TERMINATION, not value modelling (see the
                # [NO-ADVANCE VARIANT CYCLE] boundary on `atom`), and dead capability is
                # not left behind (lessons (az)/(bd)). They come back with `atom`.
                if isinstance(_rc, dict) and _rc.get("type") == "Var":
                    _cn = str(_rc.get("name"))
                    # OPTIONAL-STRING CARRIER (relaunch #11): the actual is an `iropt_str`
                    # carrier local (`debug_text`), read HERE under the Python guard
                    # `if debug_text is not None:` that has just proved it present. The
                    # slot needs a plain `string`, so project through the DEFINED total
                    # `iropt_str_val`; its `IrSNone` arm is the `""` default and is
                    # unreachable at this site.
                    if _cn in getattr(self, "_iropt_str_local_vars", set()):
                        parts.append(f"(PVStr (iropt_str_val !{whyml_ident(_cn)}))")
                        continue
                    if (_cn in getattr(self, "_string_local_vars", set())
                            or getattr(self, "_current_symbol_table", {}).get(_cn)
                            in ("str", "string")):
                        parts.append(f"(PVStr {bound[f]})")
                        continue
                if (isinstance(_rc, dict) and _rc.get("type") == "Call"
                        and isinstance(_rc.get("func"), str)
                        and self._call_returns_pyconst_val(_rc["func"])):
                    # THE NUMBER LITERAL (relaunch #12): `value=_parse_number(tok.string)`.
                    # `_parse_number` is a PURE TOTAL FUNCTION of the token text that
                    # returns an int, a float or a complex — three shapes the retired
                    # two-arm `irconst` could not express at all, which is why the number
                    # sites (`atom`, `_pattern_number`, `closed_pattern`) sat on a recorded
                    # [MODEL] boundary. Its declared `-> "PyConstVal"` interface makes the
                    # emitted `val` an UNINTERPRETED `string -> pyconst_val`, which is the
                    # honest abstraction: equal token texts give equal values, and nothing
                    # else is claimed in EITHER direction — the model never asserts two
                    # literals are equal, and never asserts they differ. No axiom.
                    parts.append(bound[f])
                    continue
                return None
            if _irlist_slots.get(f) == "seq string":
                # A STRING-LIST child (`Compare.ops` is `cmpop*`, a list of 0-FIELD
                # singletons, each carried as its class-name string; `MatchClass.kwd_attrs`
                # and `Global.names` are `identifier*`). The emit_ir group is emitted
                # mutable-FREE, so a pure `seq string` is a legal payload type — no new ADT
                # is needed (the `IrComposeFromDecl (seq string)` precedent). DECLINES
                # unless the actual really is a `!<local>` deref of a seq local KNOWN to
                # carry strings, so the slot can never be filled with an int-erased list.
                _rs = str(bound[f]).strip()
                # AN EMPTY LIST LITERAL IS A GENUINELY EMPTY STRING-LIST CHILD, not a
                # decline — the exact twin of the `irlist` slot's `ILNil` case just below,
                # on the same `(Array.make 1024 0)` placeholder literal (lesson (ao)).
                # `closed_pattern`'s class pattern `Ctor(p1, …)` really carries NO keyword
                # attributes: `_N("MatchClass")(…, kwd_attrs=[], kwd_patterns=[])`, and
                # `kwd_patterns` (an `irlist`) was already admitted this way while its
                # `seq string` twin declined and took the whole construction with it.
                # `Seq.empty` is the faithful value. Gated on the EXACT placeholder, so any
                # other actual still has to be a known string seq local, fail-closed.
                if _rs == "(Array.make 1024 0)":
                    parts.append("(Seq.empty: seq string)")
                    continue
                if not (_rs.startswith("!") and _rs[1:].isidentifier()
                        and _rs[1:] in getattr(self, "_seq_locals", set())
                        and getattr(self, "_seq_value_types", {}).get(
                            _rs[1:]) == "string"):
                    return None
                parts.append(_rs)
                continue
            if _irlist_slots.get(f) == "iroptlist":
                # OPTIONAL-ELEMENT CHILD LIST (relaunch #10): the `Dict.keys` slot. An
                # EMPTY list literal is a genuinely empty child list -> `IONil` (the same
                # reasoning as the `irlist` `ILNil` case below, on the same placeholder
                # literal). Otherwise the actual must be an `iropt_ir`-element seq LOCAL —
                # one the body really grew with a bare `None` append — else the whole
                # construction DECLINES, fail-closed. `seq_to_iroptlist` is the exact twin
                # of `seq_to_irlist`: a fresh result pinned POINTWISE by the carrier's own
                # DEFINED `iolen`/`ionth`, so nothing is erased (no axiom, no new leaf).
                _rawo = str(bound[f]).strip()
                if _rawo == "(Array.make 1024 0)":
                    parts.append("IONil")
                    continue
                if not (_rawo.startswith("!") and _rawo[1:].isidentifier()
                        and _rawo[1:] in getattr(self, "_iropt_seq_locals", set())):
                    return None
                self._add_abstract_op(
                    "val seq_to_iroptlist (s: seq iropt_ir) : iroptlist\n"
                    "    ensures { iolen result = Seq.length s }\n"
                    "    ensures { forall i:int. 0 <= i < Seq.length s ->"
                    " ionth i result = Seq.get s i }")
                parts.append(f"(seq_to_iroptlist {_rawo})")
                continue
            if _irlist_slots.get(f) == "irlist":
                _raw = str(bound[f]).strip()
                # AN EMPTY LIST LITERAL IS A GENUINELY EMPTY CHILD LIST, not a decline.
                # `Module(body=body, type_ignores=[])` really carries NO type-ignores, and
                # `[]` lowers to the emitter's placeholder `(Array.make 1024 0)` (lesson
                # (ao)) which is neither a seq local nor empty. `ILNil` is the faithful
                # value — the `irlist` ADT's own nil — so the slot is FILLED with the empty
                # list instead of the whole construction declining. Gated on the EXACT
                # placeholder literal: any other actual still has to be a real emit_ir seq
                # local or the construction declines, fail-closed as before.
                if _raw == "(Array.make 1024 0)":
                    parts.append("ILNil")
                    continue
                # AN `array emit_ir` PARAM is a real child list too (relaunch #8):
                # `funcdef(decorators: List["ExprIR"], …)` binds `decorator_list=decorators`
                # straight from the parameter, which is an ARRAY (not a seq local), so the
                # seq test below declined and the WHOLE construction fell back — dropping
                # every decorator with it. `arr_to_irlist` is the array twin of
                # `seq_to_irlist`: a fresh result pinned POINTWISE by the ADT's own DEFINED
                # `irlen`/`irnth`, so the list is EQUAL to the array and nothing is erased
                # (no axiom, no new ADT). Gated on the actual being a bare FORMAL PARAM that
                # Module5 typed `List[<IR-node>]` (`param_list_flat_elem == "emit_ir"`), so
                # an int-erased or differently-typed array cannot reach the slot.
                if (_raw.isidentifier()
                        and _raw in set(getattr(self, "_formal_params", []) or [])
                        and (getattr(self, "_param_list_flat_elem", {}) or {}
                             ).get(_raw) == "emit_ir"):
                    self._add_abstract_op(
                        "val arr_to_irlist (a: array emit_ir) : irlist\n"
                        "    ensures { irlen result = Array.length a }\n"
                        "    ensures { forall i:int. 0 <= i < Array.length a ->"
                        " irnth i result = a[i] }")
                    parts.append(f"(arr_to_irlist {_raw})")
                    continue
                # A CALL RESULT that is already an `array emit_ir` is a real child list
                # too (relaunch #11): `JoinedStr(values=_merge_str_constants(values,
                # drop_empty=False))` binds the slot from a helper declared
                # `-> "List[ExprIR]"`, whose abstract `val` really returns `array emit_ir`.
                # Without this the whole construction declined and the f-string's ENTIRE
                # value list was dropped. `arr_to_irlist` is the same pointwise-pinned
                # bridge the FORMAL-PARAM case above uses — no axiom, no new ADT. Gated on
                # the callee's DECLARED return type resolving to `array emit_ir`, so an
                # int-erased or differently-typed call can never fill the slot.
                _rl = (raw_kwargs or {}).get(f)
                if (isinstance(_rl, dict) and _rl.get("type") == "Call"
                        and isinstance(_rl.get("func"), str)
                        and self._irlist_call_returns_emit_ir_array(_rl["func"])):
                    self._add_abstract_op(
                        "val arr_to_irlist (a: array emit_ir) : irlist\n"
                        "    ensures { irlen result = Array.length a }\n"
                        "    ensures { forall i:int. 0 <= i < Array.length a ->"
                        " irnth i result = a[i] }")
                    parts.append(f"(arr_to_irlist {_raw})")
                    continue
                if not (_raw.startswith("!") and _raw[1:].isidentifier()
                        and _raw[1:] in getattr(self, "_seq_locals", set())
                        and _raw[1:] in getattr(self, "_emit_ir_seq_locals", set())):
                    return None
                self._add_abstract_op(
                    "val seq_to_irlist (s: seq emit_ir) : irlist\n"
                    "    ensures { irlen result = Seq.length s }\n"
                    "    ensures { forall i:int. 0 <= i < Seq.length s ->"
                    " irnth i result = Seq.get s i }")
                parts.append(f"(seq_to_irlist {_raw})")
                continue
            parts.append(bound[f])
        return f"({cname} {' '.join(parts)})"

    def _class_type_str_table_get(self, expr: Dict[str, Any], local_refs: Set[str],
                                  invariant_ctx: bool,
                                  subst: Optional[Dict[str, str]]) -> Optional[str]:
        """L2 DISPATCH-EXPANSION: lower `self.<CONST>.get(type(x), "<default>")` over a
        class-body TYPE-KEYED STRING table (`_PY_OP_MAP`, 26 entries) to the finite chain
        of type-tag tests the table actually denotes:

            (if str_eq_op (py_type_name_of x) "Add" then "+"
             else if str_eq_op (py_type_name_of x) "Sub" then "-"
             else … else "?")

        WHAT THIS REPLACES, and why it is a real TCB reduction rather than a reshuffle.
        Today the whole expression collapses to ONE opaque
        `val self__PY_OP_MAP_get_2 (x0: int) (x1: int) : int` — a lookup that is
        int-typed (so it cannot even feed the method's `-> str` return; measured as
        `has type int, but is expected to have type string`) AND completely invariant
        under the table's contents. Both the type extraction AND the table are assumed.
        After this, ONLY the type extraction is assumed: `py_type_name_of` is a total
        uninterpreted `val` naming the runtime class of a node — the same synthetic
        `_type` tag-test device already sanctioned for `_extract_ast_subscript`
        ("Ledger 3 (reuses pyval)", functions.py). The TABLE becomes concrete, so the
        result is now provably one of the table's actual values, and a caller that knows
        the tag knows the answer. NO axiom, NO certificate, ledger unchanged.

        ORDER IS LOAD-BEARING and is preserved from the source: a Python dict lookup
        takes the FIRST matching key, and duplicate VALUES do occur in the real table
        (`ast.Is: "=="` alongside `ast.Eq: "=="`), so the chain must be emitted in
        source order. Module 5 records the entries as an ordered list for exactly this.

        FAIL-CLOSED: requires a `self.<CONST>.get` whose `<CONST>` is a collected
        type-keyed table of the CURRENT class, exactly two actuals, the first a literal
        `type(<e>)` call and the second a STRING literal. Anything else returns None and
        keeps the existing opaque path."""
        fn = expr.get("func")
        if not (isinstance(fn, str) and fn.startswith("self.") and fn.endswith(".get")):
            return None
        const = fn[len("self."):-len(".get")]
        if "." in const or not const:
            return None
        _reg = (getattr(self, "ir", None) or {}).get("class_type_str_constants") or {}
        _cls = getattr(self, "_current_self_type", None)
        tbl = None
        for _cn, _tables in _reg.items():
            # `_current_self_type` is the FULLY-lowercased class name
            # (`pycsltojsonemitter`), while `whyml_ident` only lowers the first character
            # (`pyCSLToJSONEmitter`) — comparing through `whyml_ident` alone silently never
            # matches. Accept either spelling.
            if const in _tables and _cls in (whyml_ident(_cn), str(_cn).lower()):
                tbl = _tables[const]
                break
        if not tbl:
            return None
        args_ir = expr.get("args") or []
        if len(args_ir) != 2:
            return None
        a0, a1 = args_ir
        if not (isinstance(a0, dict) and a0.get("type") == "Call"
                and a0.get("func") == "type" and len(a0.get("args") or []) == 1):
            return None
        if not (isinstance(a1, dict) and a1.get("type") == "String"
                and isinstance(a1.get("value"), str)):
            return None
        subj = self._coerce_to_int(
            self._expr_to_whyml(a0["args"][0], local_refs, invariant_ctx, subst))
        self._add_abstract_op("val py_type_name_of (x: int) : string")
        self._add_abstract_op(
            "val str_eq_op (a: string) (b: string) : bool\n"
            "    ensures { result <-> (a = b) }")
        out = whyml_string_literal(a1["value"])
        for ent in reversed(tbl):
            if not (isinstance(ent, (list, tuple)) and len(ent) == 2):
                return None
            _k, _v = ent
            out = (f"(if str_eq_op (py_type_name_of {subj}) "
                   f"{whyml_string_literal(str(_k))} "
                   f"then {whyml_string_literal(str(_v))} else {out})")
        return out

    def _call_term_constructor(self, args: List[str], func_name: str,
                               kwargs_map: Optional[Dict[str, str]] = None,
                               raw_args: Optional[List[Any]] = None,
                               raw_kwargs: Optional[Dict[str, Any]] = None,
                               elt_lower: Optional[Any] = None
                               ) -> Optional[str]:
        """TERM CARRIER (L13 / cursor-nest): `BinOp(op, lhs, rhs)` for one of the term
        ADT's own arm classes lowers to the ADT APPLICATION `(BinOp op lhs rhs)` — the
        constructor of the CERTIFIED immutable `type term` the file already emits —
        instead of the imported-dataclass RECORD literal
        `{ binop_op = …; binop_lhs = …; rhs = … }`.

        Why the record is the wrong model, measured: the emitted `parser.mlw` carries BOTH
        representations of the same Python classes at once — the 9-constructor inductive
        `type term` AND `type binop = { mutable binop_op: string; mutable binop_lhs: int;
        mutable rhs: int }`. The record is MUTABLE (so it cannot unify with the immutable
        `term` a descent chain threads) and INT-ERASED in its child slots (so it is
        value-blind). The ADT is strictly the better model, not merely a different one.

        The payload order comes from `_term_adt_spec["ctors"][C]` (built by
        `compute_term_adt_spec` off the imported dataclass field list) — the SAME spec the
        `type term` declaration itself is emitted from, so the application can never
        disagree with the declaration. Actuals bind BY NAME off the class's positional
        `__init__` params, never by position, so a renamed or reordered field cannot
        silently mis-bind.

        FAIL-CLOSED on both axes:
          - every payload slot must be bound, or DECLINE (an unbound slot is a dropped
            child — the facade this whole build exists to avoid);
          - every slot's WhyML type must be `term` or `string`. The `list term` /
            `list string` slots (`App`, `Forall`, `Exists`) need the seq -> list
            reconciliation that is a SEPARATE, unbuilt capability, and the `int`/`bool`
            slots (`IntLit`, `BoolLit`) need literal coercion. Declining leaves the old
            record-literal path, which then fails LOUDLY at L3-tc — never a silent facade.

        Gated on `_term_adt_spec` being non-None AND `@mutable_state`, exactly like
        `_call_irnode_constructor`."""
        spec = getattr(self, "_term_adt_spec", None)
        if not spec:
            return None
        if (getattr(self, "_current_self_type", None) not in getattr(
                self, "_mutable_state_classes", set())):
            return None
        ctor_fields = (spec.get("ctors") or {}).get(func_name)
        if not ctor_fields:
            return None
        # TERM CARRIER cap-(4): `list term` joins the admissible slot types. It is
        # admitted ONLY through the fixed-arity tuple/list-LITERAL path below
        # (`_term_list_literal_slot`); every other actual shape still DECLINES, so the
        # `list string` binder slots (`Forall`/`Exists`) and the int/bool literal slots
        # (`IntLit`/`BoolLit`) are unchanged.
        if not all(wt in ("term", "string", "list term", "list string", "int", "bool")
                   for _fn, wt in ctor_fields):
            return None
        rec_info = getattr(self, "_record_types", {}).get(func_name)
        if not rec_info:
            return None
        init_params = rec_info.get("init_params", [])
        if len(args) > len(init_params):
            return None
        bound: Dict[str, str] = dict(zip(init_params, args))
        bound.update(kwargs_map or {})
        raw_bound: Dict[str, Any] = dict(zip(init_params, list(raw_args or [])))
        raw_bound.update(raw_kwargs or {})
        parts: List[str] = []
        for fn, _wt in ctor_fields:
            if fn not in bound:
                return None
            if _wt in ("list term", "list string"):
                lst = (self._term_list_literal_slot(raw_bound.get(fn), elt_lower)
                       if _wt == "list term" else None)
                if lst is None:
                    lst = self._term_list_seq_slot(raw_bound.get(fn), _wt)
                if lst is None:
                    return None
                parts.append(lst)
                continue
            if _wt in ("int", "bool"):
                lit = self._term_scalar_slot(_wt, raw_bound.get(fn), bound[fn])
                if lit is None:
                    return None
                parts.append(lit)
                continue
            parts.append(bound[fn])
        return f"({func_name} {' '.join(parts)})"

    def _term_list_seq_slot(self, raw: Any, wt: str = "list term") -> Optional[str]:
        """TERM CARRIER capability (4) PROPER: a RUNTIME-LENGTH `tuple(<seq local>)` bound
        to a `list term` constructor slot — `App(head=atom.name, args=tuple(args))` in
        `parse_atom_application`, `App(head="tuple", args=tuple(elts))` in `parse_atom` —
        lowers to `(seq_to_list_term !args 0)`.

        This is the half of capability (4) the fixed-arity `_term_list_literal_slot`
        cannot reach: the arity is not known at emission time, so there is no `Cons` chain
        to write. Today the same site lowers to the OPAQUE `tuple_1 : seq int -> int`,
        which int-erases the whole accumulator — a facade that silently drops every
        element's value.

        NO AXIOM AND NO ABSTRACT VAL. `seq_to_list_term` is a DEFINED, total, structurally
        terminating `let rec function` over Why3's own `seq.Seq` and `list.List`, both of
        which the file already `use`s wherever `type term` is emitted:

            let rec function seq_to_list_term (s: seq term) (i: int) : list term
              variant { Seq.length s - i }
              = if i >= Seq.length s then Nil
                else Cons (Seq.get s i) (seq_to_list_term s (i + 1))

        Its termination discharges from the recursive call's own guard (`i < Seq.length s`
        makes the variant positive and strictly decreasing), so it needs no precondition
        and is total on every input. The result is EXACTLY the seq's elements in order,
        which is precisely what the Python `tuple(<list>)` denotes — the conversion is
        faithful by construction, not an over-approximation.

        FAIL-CLOSED: the actual must be a literal `tuple(...)`/`list(...)` call over a
        single bare `Var` naming a recognized `seq` local. Anything else declines, and the
        old record path then fails LOUDLY at L3-tc. If the seq's elements were not in fact
        `term`-typed, `Seq.get s i` would not unify with the `list term` result — again a
        loud failure, never a silent int-erasure."""
        if not (isinstance(raw, dict) and raw.get("type") == "Call"
                and raw.get("func") in ("tuple", "list")):
            return None
        a = raw.get("args") or []
        if len(a) != 1 or not (isinstance(a[0], dict) and a[0].get("type") == "Var"):
            return None
        nm = a[0].get("name")
        if nm not in getattr(self, "_seq_locals", set()):
            return None
        # `list string` (`Forall`/`Exists` carry `binders: tuple(binders)`) is the SAME
        # bridge one element type over: `binders` accumulates as a `seq string`, the arm
        # declares `list string`. One converter per element type, both defined the same way.
        _elt = "string" if wt == "list string" else "term"
        if _elt == "string" and (getattr(self, "_seq_value_types", {}) or {}
                                 ).get(nm) not in ("string", "str"):
            # a seq whose element type is not KNOWN to be string never binds — declining
            # leaves the record path, which then fails loudly at L3-tc.
            return None
        _fn = f"seq_to_list_{_elt}"
        self._add_abstract_op(
            f"let rec function {_fn} (s: seq {_elt}) (i: int) : list {_elt}\n"
            "    variant { Seq.length s - i }\n"
            "  = if i >= Seq.length s then Nil\n"
            f"    else Cons (Seq.get s i) ({_fn} s (i + 1))")
        return f"({_fn} !{whyml_ident(nm)} 0)"

    def _term_scalar_slot(self, wt: str, raw: Any, lowered: str) -> Optional[str]:
        """TERM CARRIER: the `int` (`IntLit int`) and `bool` (`BoolLit bool`) payload
        slots of the certified inductive.

        `int`: the actual is passed through UNCHANGED, but only from a shape that is
        UNAMBIGUOUSLY int-valued at the source level — an integer literal, a unary
        `+`/`-` over one, or an `int(...)` conversion call (`IntLit(int(t.value))`, the
        live `parse_atom` shape). Anything else DECLINES, because the int model is
        exactly where a value-blind `str_hash_op`/`getattr_*` facade would slip in
        silently: it type-checks against `int` while carrying a hash instead of a value.

        `bool`: only the literals `True` / `False`, emitted as Why3 `true` / `false`.
        This slot CANNOT reuse the ordinary lowering — PyCSL models a Python bool as an
        INT (`True` -> `1`), and the inductive's arm is a genuine Why3 `bool`, so passing
        the ordinary lowering through would be an int-vs-bool type error. A non-literal
        bool declines rather than guessing a coercion."""
        if not isinstance(raw, dict):
            return None
        t = raw.get("type")
        if wt == "bool":
            if t == "Bool" and isinstance(raw.get("value"), bool):
                return "true" if raw["value"] else "false"
            return None
        if t == "Number" and isinstance(raw.get("value"), int):
            return lowered
        if (t == "UnaryOp" and raw.get("op") in ("-", "+")
                and isinstance(raw.get("operand"), dict)
                and raw["operand"].get("type") == "Number"
                and isinstance(raw["operand"].get("value"), int)):
            return lowered
        if t == "Call" and raw.get("func") == "int":
            return lowered
        return None

    def _term_list_literal_slot(self, raw: Any, elt_lower: Optional[Any]
                                ) -> Optional[str]:
        """TERM CARRIER cap-(4): a FIXED-ARITY tuple/list LITERAL bound to a `list term`
        constructor slot (`App(head="mod", args=(out, rhs))`) lowers to the Why3
        cons-list `(Cons out (Cons rhs Nil))` — the exact payload the certified
        inductive's `App string (list term)` arm declares.

        Why this is the faithful model and not a re-encoding: Python's `App.args` IS a
        tuple of `Term`s, and the emitted `type term` already spells that slot
        `list term`; `list.List` is already `use`d by every file that emits the
        inductive (the `flatten_arrow_chain` / `mk_arrow_chain` recognizer groups build
        and match `Cons`/`Nil` today). So this adds NO type, NO abstract val and NO
        axiom — it only lets an ORDINARY body reach a constructor arm the recognizers
        already reach.

        Deliberately NARROWER than the general seq -> `list term` reconciliation
        (L13 capability (4) proper, still unbuilt): that one has to materialise a
        RUNTIME-length accumulator (`tuple(<seq local>)`, needed by `parse_quant` /
        `parse_atom_application`). This handles only the case where the arity is
        SYNTACTICALLY known, which needs no `Init.init`, no length reasoning and no
        `Seq` bridge at all.

        FAIL-CLOSED on every axis — returns None (=> the whole term-ctor lowering
        declines, and the old record-literal path then fails LOUDLY at L3-tc, never
        silently):
          - the actual must be a literal `Tuple` / `ArrayLit` / `ListLit` node (a
            variable holding a list is NOT accepted — that is the seq case);
          - it must be non-empty (an empty literal would be `Nil`, which is
            representable, but no live body constructs one and admitting it would make
            the emptiness untestable);
          - EVERY element must be a plain `Var` naming a local in
            `self._term_local_vars`, i.e. a local this body pre-declared as `term`. An
            int-erased or string local can therefore never be consed into a `list term`.
        """
        if elt_lower is None:
            return None
        if not (isinstance(raw, dict)
                and raw.get("type") in ("Tuple", "ArrayLit", "ListLit")):
            return None
        elts = raw.get("elts")
        if not isinstance(elts, list) or not elts:
            return None
        _tlv = getattr(self, "_term_local_vars", set())
        for e in elts:
            if not (isinstance(e, dict) and e.get("type") == "Var"
                    and e.get("name") in _tlv):
                return None
        out = "Nil"
        for e in reversed(elts):
            out = f"(Cons {elt_lower(e)} {out})"
        return out

    def _bind_listfield_from_seq(self, rec_info: Dict[str, Any], fn: str,
                                 ent: Dict[str, Any],
                                 arg_nodes: Dict[str, Any],
                                 rec_name: str = "") -> Optional[str]:
        """tierA-listfield-impl.md: bind a LIST-valued record field from the list the
        construction site actually supplied, instead of the typed-default
        `Array.make 0 0` — which SILENTLY DROPS the caller's list (a facade hazard: a
        stub that type-checked around it would return a record with an empty list).

        `Ctor(a, b, my_list)` where `my_list` is a `seq`-typed list LOCAL and the field
        is `array emit_ir` lowers the field to
        `(Init.init (Seq.length !my_list) (fun _i -> Seq.get !my_list _i))` — the
        `seq -> array` reconciliation (a list local accumulates as `Seq.snoc`; a list
        record field lowers to `array`). `array.Init.init` is a DEFINED, stdlib-PROVEN
        `let` (why3 stdlib `array.mlw`: `ensures { result.length = n }` +
        `ensures { forall i. 0 <= i < n -> result[i] = f i }`), so the binding is
        faithful and adds NO axiom and NO abstract `val`. Its `n >= 0` precondition is
        discharged by seq.Seq's `length_nonnegative` axiom.

        Gated as narrowly as possible — ALL of:
          (1) the constructing method's class is `@mutable_state` (the emitter-model
              gate `_call_irnode_constructor` already uses; NO corpus program declares
              `@mutable_state`, so the corpus is byte-inert by construction);
          (2) the field is a `list` field whose ELEMENT type is either the `emit_ir`
              ADT or `string` (`field_value_types`) — dict/set/frozenset/tuple and
              every other element type keep the existing default path;
          (3) the field's `__init__` initialiser is the BARE positional param
              (`self.f = f`, the `@dataclass` / positional-`__init__` shape), and that
              param is BOUND at this call site;
          (4) the actual is a plain `!<local>` deref of a `seq`-typed list local
              (`_seq_locals`) whose ELEMENT TYPE AGREES with the field's: for an
              `emit_ir` field, the elements lowered to `emit_ir` ADT constructor
              applications (`_emit_ir_seq_locals`, recorded at the `.append` site
              because Module5's `seq_value_types` only ever tracks "string"); for a
              `string` field, `_seq_value_types[<local>] == "string"` (the existing
              L18 S1c-join all-sources-string marking). A seq of unknown element
              type NEVER binds.
        An EMPTY-literal actual (`NoExceptionDecl(exceptions=[])`) is not a `!<local>`
        deref, so it stays on the existing `Array.make 0 0` default path — unregressed.
        Returns None (→ the typed default) whenever any gate fails."""
        if getattr(self, "_current_self_type", None) not in getattr(
                self, "_mutable_state_classes", set()):
            return None
        if rec_info.get("field_types", {}).get(fn) != "list":
            return None
        _fvt = rec_info.get("field_value_types", {}).get(fn)
        if _fvt not in ("emit_ir", "string") and _fvt not in getattr(self, "_record_types", {}):
            return None
        v = ent.get("value")
        if not (isinstance(v, dict) and v.get("type") == "Var"):
            return None
        node = arg_nodes.get(v.get("name"))
        if not (isinstance(node, dict) and node.get("type") == "RawWhyml"):
            return None
        raw = str(node.get("whyml", "")).strip()
        if not (raw.startswith("!") and raw[1:].isidentifier()):
            return None
        lname = raw[1:]
        if lname not in getattr(self, "_seq_locals", set()):
            return None
        # ELEMENT-TYPE agreement between the field and the seq local — the binding is
        # only emitted when the seq is KNOWN to carry the field's element type.
        if _fvt == "emit_ir":
            if lname not in getattr(self, "_emit_ir_seq_locals", set()):
                return None
        elif _fvt in getattr(self, "_record_types", {}):
            # RECORD-ELEMENT list field (`Import.names : array alias`): the seq local is
            # filled by `names.append(self._dotted_as_name())`, whose callee RETURNS that
            # record, so the element types agree by construction. Gated on the seq local
            # being recorded as carrying THIS record (`_record_seq_locals`), so a seq of an
            # unknown element type still never binds.
            if _fvt != getattr(self, "_record_seq_locals", {}).get(lname):
                return None
        elif getattr(self, "_seq_value_types", {}).get(lname) != "string":
            return None
        if rec_name in getattr(self, "_list_element_record_types", set()):
            # PINNED (`List[<record>]`-element) record: its list field is emitted as the
            # PURE `seq <elem>` (see preamble `_emit_type_decls`), which is EXACTLY the
            # shape the seq local already has — bind it directly, no `Init.init`
            # seq->array reconciliation and no `array.Init` import.
            return raw
        self._needs_array_init = True
        # The `seq` is let-bound to a PURE value first: `Init.init`'s second argument
        # is a pure `int -> 'a`, and a `!ref` deref inside the lambda body is stateful
        # ("This function is stateful, it cannot be used as pure").
        _b = f"_lf_{lname}"
        return (f"(let {_b} = {raw} in "
                f"Init.init (Seq.length {_b}) (fun _i -> Seq.get {_b} _i))")

    def _call_record_constructor(self, args: List[str], func_name: str,
                                 kwargs_map: Optional[Dict[str, str]] = None,
                                 kwargs_ir: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """`C(...)` for a known record type → a WhyML record literal with per-field,
        type-correct values. Returns None only if `func_name` is not a known record
        type. (Extracted from `_handle_call_expr`.)

        base_op.md Tier A — parametrized construction: when `C(a, b)` is called with
        args matching `__init__`'s formals, each scalar field whose `__init__` body
        set it from those params (`init_body`, captured by Module5) is initialised by
        substituting the actual args for the params; all other fields keep their
        type-correct default. A 0-arg `C()`, an arity mismatch, or a non-scalar /
        non-param-dependent field all fall back to the default witness (sound).

        WL-07: `kwargs_map` (field-name -> lowered WhyML) carries EXPLICIT keyword
        arguments (`Point(x=1, y=2)`), bound BY NAME on top of the positional prefix
        — so both a positional, a keyword, and a mixed construction bind their fields
        faithfully (a keyword-omitted-with-default field keeps its default)."""
        if func_name not in self._record_types:
            return None
        rec_info = self._record_types[func_name]
        rec_lower = func_name.lower()
        field_types = rec_info.get("field_types", {})

        def _field_default(fn: str) -> str:
            # Per-type default so a driver constructing `C()` builds a
            # type-correct record. A list/array field defaults to an
            # `Array.make <len> 0` (len from field_defaults, captured by
            # Module5._array_init_size) so its `\length` invariant holds;
            # a dict/set field to the empty map; everything else to its
            # captured int (fallback 0).
            ft = field_types.get(fn, "int")
            if ft in ("list", "array"):
                if func_name in getattr(self, "_list_element_record_types", set()):
                    # PINNED record: the list field is the pure `seq <elem>` (preamble
                    # `_emit_type_decls`), so its type-correct empty default is `Seq.empty`,
                    # not an `Array.make`.
                    return "Seq.empty"
                return f"(Array.make {rec_info['defaults'].get(fn, 0)} 0)"
            if ft in ("dict", "set", "frozenset"):
                return "(const (None: option int))"
            if ft == "option":
                # An OMITTED option field's type-correct default is Why3's `None`, not the
                # int `0` — same faithfulness point as the literal-`None` keyword above.
                return "None"
            return f"{rec_info['defaults'].get(fn, 0)}"

        # Parametrized overrides: map each param-initialised scalar field to its
        # arg-substituted value. Only when the call arity matches `__init__`. The
        # already-lowered arg strings are spliced in via `RawWhyml` IR nodes (a value
        # substitution — `subst` is a variable-RENAME map, not a value-injection one).
        init_map: Dict[str, str] = {}
        init_params = rec_info.get("init_params", [])
        init_body = rec_info.get("init_body", [])
        # Positional-prefix binding: bind the first `len(args)` params from the
        # actual args and leave any trailing params UNBOUND (their fields keep the
        # typed default). Python's positional call semantics — a `@dataclass` /
        # positional `__init__` binds `f_i` from arg i, and a field WITH a default
        # whose arg is OMITTED keeps that default (WL-07). Requires
        # `len(args) <= len(init_params)`: a full call binds every param (the prior
        # exact-match behaviour, byte-identical); a PARTIAL call binds the provided
        # prefix (sound — a trailing defaulted field keeps its default instead of
        # the old all-defaults collapse, which would have proved a FALSE `.f0 == 0`
        # for a bound leading field); an OVER-arity call (a Python error) binds
        # nothing (all defaults — fail-closed, never a false full binding).
        kwargs_map = kwargs_map or {}
        if init_params and ((args and len(args) <= len(init_params)) or kwargs_map):
            # positional prefix binds init_params[0 .. len(args)-1] by position;
            # keyword args bind the same-named param on top (a Python call never
            # binds a param both positionally and by keyword — a TypeError — so no
            # conflict). A keyword naming a non-param is ignored (kept as default).
            arg_nodes = {init_params[i]: {"type": "RawWhyml", "whyml": args[i]}
                         for i in range(min(len(args), len(init_params)))}
            for _kwn, _kww in kwargs_map.items():
                if _kwn not in init_params:
                    continue
                # OPTION-TARGET keyword: when the field this keyword binds is genuinely
                # `option τ`, an `Optional`-union actual must be projected into `Some`/`None`,
                # not into its carrier with a sentinel. `kwargs_map` arrives ALREADY LOWERED
                # (that is why the raw IR is threaded in beside it): the lowered string is the
                # sentinel projection, which both mistypes against `option τ` and would model
                # an ABSENT value as the carrier's zero.
                _raw = (kwargs_ir or {}).get(_kwn)
                # OPTION-TARGET keyword, LITERAL-`None` case: `_N("arg")(annotation=None,
                # type_comment=None)` binds an option field from the `None` LITERAL. Lowered
                # generically it is the int `0` — which mistypes against `option τ` and, worse,
                # is the None-reads-as-zero erasure this campaign has repaired before. The
                # faithful value is Why3's own `None`.
                if (field_types.get(_kwn) == "option"
                        and isinstance(_raw, dict) and _raw.get("type") == "None"):
                    arg_nodes[_kwn] = {"type": "RawWhyml", "whyml": "None"}
                    continue
                if (field_types.get(_kwn) == "option"
                        and isinstance(_raw, dict) and _raw.get("type") == "Var"):
                    _sym = getattr(self, "_current_symbol_table", {}).get(_raw.get("name"))
                    _deref = ("!" if _raw.get("name") in getattr(self, "_optional_union_locals", set())
                              else "")
                    _opt = self._union_read_option_projection(
                        _sym, f"{_deref}{whyml_ident(str(_raw.get('name')))}")
                    if _opt is not None:
                        arg_nodes[_kwn] = {"type": "RawWhyml", "whyml": _opt}
                        continue
                arg_nodes[_kwn] = {"type": "RawWhyml", "whyml": _kww}
            for ent in init_body:
                fn = ent["field"]
                # A list/dict/set field keeps its typed default (array/map construction
                # over a param is out of Tier-A scope) — EXCEPT the narrowly gated
                # `List[ExprIR]`-from-`seq`-local binding of `_bind_listfield_from_seq`
                # (tierA-listfield-impl.md), which binds the caller's ACTUAL list instead
                # of fabricating the empty `Array.make 0 0` (a DROPPED-child facade).
                if field_types.get(fn, "int") in ("list", "array", "dict", "set", "frozenset"):
                    _lv = self._bind_listfield_from_seq(rec_info, fn, ent, arg_nodes,
                                                        func_name)
                    if _lv is not None:
                        init_map[fn] = _lv
                    continue
                # A field whose initialiser references a param OUTSIDE the bound
                # prefix (a trailing omitted-with-default field) keeps its typed
                # default — never a bare unsubstituted param var (ill-typed WhyML).
                free = self._init_value_free_names(ent["value"])
                if free and not (free <= set(arg_nodes.keys())):
                    continue
                init_map[fn] = self._expr_to_whyml(
                    self._subst_params(ent["value"], arg_nodes), set())

        field_inits = "; ".join(
            f"{self._field_label(rec_lower, fn)} = {init_map.get(fn, _field_default(fn))}"
            for fn in rec_info["fields"]
        )
        return f"{{ {field_inits} }}"

    # WL-06d P1-literal: encodings under which an ASCII code point IS the single
    # emitted byte. For a PURE-ASCII literal (every ord < 128) ascii / utf-8 /
    # latin-1 all agree byte[i] == ord(s[i]); a non-ASCII char is NOT modelled
    # (utf-8 is multi-byte, ascii raises) → the recognizer declines (opaque).
    _ENCODE_ASCII_NAMES = frozenset({
        "ascii", "us-ascii", "utf-8", "utf8", "u8", "latin-1", "latin1",
        "latin_1", "iso-8859-1", "iso8859-1", "l1", "8859",
    })

    def _encode_string_literal(self, expr, local_refs, invariant_ctx, subst):
        """WL-06d (P1-literal): constant-fold `"<ascii-literal>".encode([enc])` to the
        `array int` byte literal of its code points — EXACTLY like a `bytes` literal
        (WL-06b). So `"abc".encode()[0] == 97` PROVES, the byte-RANGE invariant
        `0 <= b[i] < 256` is derivable, and a FALSE content claim stays UNPROVEN.

        FAIL-CLOSED / opaque (returns None) unless ALL hold — so the general
        `.encode()` (a non-literal receiver, a non-ASCII byte, an unmodelled
        encoding) keeps the sound opaque `encode_N` val:
          - the method tail is `encode` and the receiver is a STRING LITERAL;
          - at most one positional arg, and if present it is a string literal
            naming an ASCII-agreeing encoding (`_ENCODE_ASCII_NAMES`);
          - every code point is ASCII (`ord < 128`) — so ascii/utf-8/latin-1 all
            emit byte == ord (a non-ASCII char is multi-byte in utf-8 / raises in
            ascii, so it is declined, not mis-lowered);
          - the literal is non-empty (an empty encode stays opaque)."""
        recv_ir, tail = self._str_method_recv_and_tail(expr)
        if tail != "encode" or not isinstance(recv_ir, dict):
            return None
        if recv_ir.get("type") != "String":
            return None
        s = recv_ir.get("value")
        if not isinstance(s, str) or s == "":
            return None
        arg_irs = expr.get("args") or []
        if len(arg_irs) > 1:
            return None
        if len(arg_irs) == 1:
            a0 = arg_irs[0]
            if not (isinstance(a0, dict) and a0.get("type") == "String"):
                return None
            enc = str(a0.get("value", "")).strip().lower().replace(" ", "")
            if enc not in self._ENCODE_ASCII_NAMES:
                return None
        if any(ord(c) >= 128 for c in s):
            return None
        alit_ir = {"type": "ArrayLit",
                   "elts": [{"type": "Number", "value": ord(c)} for c in s]}
        return self._expr_to_whyml(alit_ir, local_refs, invariant_ctx, subst)

    def _call_bytes_methods(self, args: List[str], func_name: str) -> Optional[str]:
        """Bytes-producing methods (`b.encode()`, `b.ljust()`, …) reach the generic path
        with no receiver dot in the IR func name. They return a byte buffer (`array int`),
        and any array-shaped operand (the receiver byte string, a slice) must stay
        `array int` so the result can flow into a `struct.pack('>...30s', …)` name field.
        Opaque — the byte content is not modeled. (Gap 5.) Returns None if not a bytes
        method. (Extracted from `_handle_call_expr`.)"""
        if func_name not in ("encode", "ljust", "rjust", "zfill"):
            return None
        n = len(args)
        arity_fn = f"{whyml_ident(func_name)}_{n}"
        _ARR = ("(Array.make", "(Array.sub ", "(array_slice ", "(sorted_1 ",
                "(struct_pack", "(encode_", "(ljust_", "(rjust_", "(zfill_",
                # 0442.md C1: a bytes literal (e.g. the `ljust(w, b'\\x00')` fill char)
                # lowers to `(let _alit = Array.make N v in …)` — an `array int`, not int.
                "(let _alit = Array.make")
        ptypes: List[str] = []
        cargs: List[str] = []
        for a in args:
            st = a.strip()
            is_arr = (any(st.startswith(p) for p in _ARR) or
                      st.lstrip("!").replace("_", "").isalnum() and
                      st.lstrip("!") in getattr(self, "_array_locals", set()))
            if is_arr:
                ptypes.append("array int")
                cargs.append(self._array_coerce_arg(a))
            else:
                ptypes.append("int")
                cargs.append(self._coerce_to_int(a))
        params = (" ".join(f"(x{i}: {t})" for i, t in enumerate(ptypes))
                  if n else "()")
        # 1009.md R2: `s.ljust(w[, fill])` / `rjust` / `zfill(w)` pad to AT LEAST
        # width `w` — Python returns the original when it is already longer — and `w`
        # is the first argument `x0`. Emit that length lower bound so a downstream
        # `\valid(name_bytes, 30)` (`Array.length >= 30`) discharges when fed a
        # `…ljust(30, b'\x00')`. (`encode`'s output length is genuinely unknown, so it
        # gets no bound: `>= 0` would be vacuous. Width must be an int operand.)
        length_ens = ""
        if func_name in ("ljust", "rjust", "zfill") and n >= 1 and ptypes[0] == "int":
            length_ens = "\n    ensures { Array.length result >= x0 }"
        self._add_abstract_op(f"val {arity_fn} {params} : array int{length_ens}")
        return f"({arity_fn} {' '.join(cargs) if cargs else '()'})"

    def _typeddict_field_access(self, value: Dict[str, Any],
                                index_ir: Dict[str, Any],
                                local_refs: Set[str],
                                invariant_ctx: bool,
                                subst: Optional[Dict[str, str]]) -> Optional[str]:
        """Lower `p["x"]` on a TypedDict-record-typed receiver to `p.x`.

        Per the two-plane spec §1.2 T5 and the core-agent hard rule
        (typing-global-impl.md §5, TY2): a string-literal subscript into a
        TypedDict-typed variable/field lowers to a record-field read. Returns
        None for non-TypedDict receivers OR a non-string-literal index (so the
        caller falls through to the existing array/dict/opaque paths — byte-
        identical for non-TypedDict drivers). The static plane is Interpreted
        (record-field read); the runtime plane is the plain-dict alias
        (Shimmed) — the runtime never sees this lowering (no blend)."""
        if index_ir.get("type") != "String":
            return None
        field_name = index_ir.get("value", "")
        if not isinstance(field_name, str) or not field_name:
            return None
        rec_name = None
        if value.get("type") == "Var":
            sym = getattr(self, "_current_symbol_table", {}).get(value.get("name", ""))
            if sym and sym in getattr(self, "_record_types", {}):
                if self._record_types[sym].get("is_typeddict"):
                    rec_name = sym
        if rec_name is None and value.get("type") in ("Attribute", "FieldGet"):
            ft = self._field_type_of(value)
            if ft and ft in getattr(self, "_record_types", {}):
                if self._record_types[ft].get("is_typeddict"):
                    rec_name = ft
        if rec_name is None:
            return None
        rec_info = self._record_types[rec_name]
        if field_name not in rec_info["fields"]:
            return None
        rec_lower = rec_info["whyml_name"]
        base = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
        return f"{base}.{self._field_label(rec_lower, field_name)}"

    def _typeddict_record_literal(self, expr: Dict[str, Any],
                                  local_refs: Set[str],
                                  invariant_ctx: bool,
                                  subst: Optional[Dict[str, str]]) -> Optional[str]:
        """Lower a `DictLit` in a TypedDict construction context to a record
        literal `{ x = v0; y = v1 }` (per the two-plane spec §1.3 T8 and the
        core-agent hard rule).

        The construction context is detected from `_func_return_type` (a
        `return {"x":1,"y":2}` in a `-> Point` function): if the return type
        is a known TypedDict record's whyml_name, the literal is matched
        field-by-field against the record's declared fields (in declaration
        order) and each value is lowered. Returns None for non-TypedDict
        construction contexts (byte-identical fallback to the empty-map stub).
        Why3 type-checks each field's value against the declared field type
        natively (T8/T9)."""
        frt = getattr(self, "_func_return_type", "")
        if not frt:
            return None
        rec_name = None
        for name, info in getattr(self, "_record_types", {}).items():
            if info.get("whyml_name") == frt and info.get("is_typeddict"):
                rec_name = name
                break
        if rec_name is None:
            return None
        rec_info = self._record_types[rec_name]
        rec_lower = rec_info["whyml_name"]
        keys = expr.get("keys", [])
        values = expr.get("values", [])
        # Build a key→value map (keys are String IR nodes per _py_expr_dict).
        kv: Dict[str, Dict[str, Any]] = {}
        for k, v in zip(keys, values):
            if isinstance(k, dict) and k.get("type") == "String":
                kv[k.get("value", "")] = v
        # T8/T9 (typeddict-twoplane-spec.md §1.3): every declared field must be
        # present (T9 — missing required key is a static error) AND no extra key
        # may be present (T9 — extra key is a static error). The default-filling
        # in the loop below is reserved for the `Point()` zero-arg construction
        # path (`_call_record_constructor`); the dict-literal path is a
        # fully-specified construction and must reject missing/extra keys.
        # GAP-001 (typing-engagement ty2): previously the missing field was
        # silently filled with its default, bypassing the T9 obligation.
        declared = set(rec_info["fields"])
        present = set(kv.keys())
        missing = [f for f in rec_info["fields"] if f not in present]
        extra = [k for k in present if k not in declared]
        if missing or extra:
            from errors import PyCSLSemanticError
            if missing:
                raise PyCSLSemanticError(
                    f"TypedDict construction is missing required key(s) "
                    f"{missing!r} (T9 / PEP 589 — a total=True TypedDict "
                    f"literal must provide every declared key).",
                    stage="whyml-emit")
            raise PyCSLSemanticError(
                f"TypedDict construction has extra key(s) "
                f"{extra!r} not declared on the TypedDict (T9 / PEP 589 — "
                f"a literal must not provide keys outside the declared set).",
                stage="whyml-emit")
        # Emit each declared field in declaration order. All declared fields
        # are present (missing/extra rejected above); each value is lowered
        # against its declared field type, and Why3 type-checks it natively
        # (T8 — typed construction).
        parts: List[str] = []
        for fname in rec_info["fields"]:
            v = kv.get(fname)
            val = self._expr_to_whyml(v, local_refs, invariant_ctx, subst)
            parts.append(f"{self._field_label(rec_lower, fname)} = {val}")
        return "{ " + "; ".join(parts) + " }"

    def _namedtuple_positional_access(self, value: Dict[str, Any],
                                      index_ir: Dict[str, Any],
                                      local_refs: Set[str],
                                      invariant_ctx: bool,
                                      subst: Optional[Dict[str, str]]) -> Optional[str]:
        """Lower `p[0]` on a NamedTuple-record-typed receiver to `p.<field at index 0>`.

        Per the two-plane spec §1.3 N5 and the core-agent hard rule
        (typing-global-impl.md §5, TY2): an integer-literal subscript into a
        NamedTuple-typed variable/field lowers to a record-field read of the
        field at that declaration index. Returns None for non-NamedTuple
        receivers OR a non-integer-literal index (so the caller falls through
        to the existing array/dict/opaque paths — byte-identical for non-
        NamedTuple drivers). The static plane is Interpreted (record-field
        read by index); the runtime plane is the plain-tuple alias (Shimmed) —
        the runtime never sees this lowering (no blend)."""
        if index_ir.get("type") != "Number":
            return None
        idx_val = index_ir.get("value")
        if not isinstance(idx_val, int) or idx_val < 0:
            return None
        rec_name = None
        if value.get("type") == "Var":
            sym = getattr(self, "_current_symbol_table", {}).get(value.get("name", ""))
            if sym and sym in getattr(self, "_record_types", {}):
                if self._record_types[sym].get("is_namedtuple"):
                    rec_name = sym
        if rec_name is None and value.get("type") in ("Attribute", "FieldGet"):
            ft = self._field_type_of(value)
            if ft and ft in getattr(self, "_record_types", {}):
                if self._record_types[ft].get("is_namedtuple"):
                    rec_name = ft
        # WL-04b (record residual): `a[i][k]` on a flat `List[Tuple[…]]` param — the
        # inner read `a[i]` is a namedtuple record (the synthesized `pytuple_<tags>`),
        # so the outer integer subscript `[k]` is its k-th positional slot. Hoist the
        # element read into a `let` (it may carry a body-context bounds-assert block).
        _wrap_let = False
        if (rec_name is None and value.get("type") == "Subscript"
                and isinstance(value.get("value"), dict)
                and value["value"].get("type") == "Var"):
            _nm = value["value"].get("name", "")
            # WL-04c: a record-array LOCAL (`a = [Pt(1,2), …]`) shares the WL-04b
            # `a[i][k]` slot path with a record-array PARAM.
            _rn = (getattr(self, "_record_array_params", {}).get(_nm)
                   or getattr(self, "_record_array_locals", {}).get(_nm))
            if _rn is not None:
                # `_rn` is the whyml_name; find the record class whose whyml_name matches.
                for _cls, _info in getattr(self, "_record_types", {}).items():
                    if _info.get("whyml_name") == _rn and _info.get("is_namedtuple"):
                        rec_name = _cls
                        _wrap_let = True
                        break
        if rec_name is None:
            return None
        rec_info = self._record_types[rec_name]
        fields = rec_info["fields"]
        if idx_val >= len(fields):
            return None
        field_name = fields[idx_val]
        rec_lower = rec_info["whyml_name"]
        base = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
        if _wrap_let:
            return f"(let _rec_ = {base} in _rec_.{self._field_label(rec_lower, field_name)})"
        return f"{base}.{self._field_label(rec_lower, field_name)}"

    @staticmethod
    def _peel_container(t: str) -> Optional[str]:
        """nested-list §8 EXTENSION: given the WhyML type `t` of a collection value,
        return the element type produced by indexing it ONCE. `array X`/`seq X` →
        X (one layer of outer parens stripped); `map κ (option ν)` → ν; a scalar
        (`int`/`string`/`real`) → None (no more indexing → opaque)."""
        t = t.strip()
        for pref in ("array ", "seq "):
            if t.startswith(pref):
                inner = t[len(pref):].strip()
                # strip ONE matching outer-paren layer, if the whole inner is wrapped.
                if inner.startswith("(") and inner.endswith(")"):
                    depth = 0
                    ok = True
                    for _ci, _ch in enumerate(inner):
                        if _ch == "(":
                            depth += 1
                        elif _ch == ")":
                            depth -= 1
                            if depth == 0 and _ci != len(inner) - 1:
                                ok = False
                                break
                    if ok:
                        inner = inner[1:-1].strip()
                return inner
        if t.startswith("map "):
            if "(option " in t:
                return t.split("(option ", 1)[1].rsplit(")", 1)[0].strip()
            return None
        return None

    def _nested_access_type(self, node: Any) -> Optional[str]:
        """nested-list §8 EXTENSION: the WhyML type of a nested-list access `node`
        (the value it evaluates to), for a chain rooted at a `_list_nested_elem`
        param. `Var(a)` (a nested-elem) → `array (<elem>)`; `Subscript(base, _)` →
        one container level peeled from `_nested_access_type(base)` (= the type of
        `base[idx]`). None if the chain is not a nested-list access, or once the
        peel bottoms out at a scalar (a read one level TOO deep). This drives the
        depth-generalized `a[i][j][k]` subscript lowering; the depth cap is
        inherited from the type recursion (`_list_nested_elem` is None past bound)."""
        if not isinstance(node, dict):
            return None
        if node.get("type") == "Var":
            _ne = getattr(self, "_list_nested_elem", {}).get(node.get("name", ""))
            if _ne is not None:
                return f"array ({_ne})"
            return None
        if node.get("type") == "Subscript":
            _bt = self._nested_access_type(node.get("value", {}))
            if _bt is None:
                return None
            return self._peel_container(_bt)
        return None

    def _opaque_selfmap_nested_read(self, expr: Dict[str, Any], local_refs: Set[str],
                                     invariant_ctx: bool,
                                     subst: Optional[Dict[str, str]]) -> Optional[str]:
        """Lower `<alias>[k]["<lit>"]` (opaque-nested-map read) to the boundary
        reader `<base>_<lit> <k> : string`, or None if the shape does not match.
        `<alias>` must be an opaque-selfmap alias local (see
        `_prescan_opaque_selfmap_aliases`); the outer index a string literal; the
        inner value the alias Var."""
        idx = expr.get("index", {})
        inner = expr.get("value", {})
        if not (isinstance(idx, dict) and idx.get("type") == "String"
                and isinstance(inner, dict) and inner.get("type") == "Subscript"):
            return None
        inner_val = inner.get("value", {})
        if not (isinstance(inner_val, dict) and inner_val.get("type") == "Var"):
            return None
        base = getattr(self, "_opaque_selfmap_aliases", {}).get(inner_val.get("name", ""))
        if not base:
            return None
        lit = whyml_ident(idx.get("value", ""))
        key = self._expr_to_whyml(inner.get("index", {}), local_refs, invariant_ctx, subst)
        self._add_abstract_op(f"val function {base}_{lit} (k: string) : string")
        return f"({base}_{lit} {key})"

    def _opaque_selfmap_inner_read(self, local: str, lit_raw: str, local_refs: Set[str],
                                   invariant_ctx: bool,
                                   subst: Optional[Dict[str, str]]) -> Optional[str]:
        """SPLIT-form inner-alias string projection: `<local>["<lit>"]` /
        `<local>.get("<lit>")` where <local> is an opaque-nested-map inner alias
        (`_rt = getattr(self, "_record_types", {}).get(tag)`) → the boundary reader
        `<base>_<lit> <outer-key> : string`, the SAME reader the chained
        `record_types[tag]["<lit>"]` form uses, keyed on the REAL outer key `tag`.
        None if <local> is not an inner alias."""
        _ent = getattr(self, "_opaque_selfmap_inner_aliases", {}).get(local)
        if not _ent:
            return None
        base, key_ir = _ent
        lit = whyml_ident(lit_raw)
        key = self._expr_to_whyml(key_ir, local_refs, invariant_ctx, subst)
        self._add_abstract_op(f"val function {base}_{lit} (k: string) : string")
        return f"({base}_{lit} {key})"

    def _opaque_selfmap_inner_mem(self, local: str, local_refs: Set[str],
                                  invariant_ctx: bool,
                                  subst: Optional[Dict[str, str]]) -> Optional[str]:
        """SPLIT-form inner-alias truthiness: `if <local>` / `<local> and …` where
        <local> is an opaque-nested-map inner alias → the membership reader
        `<base>_mem <outer-key> : bool` (does the outer key name an entry). None if
        <local> is not an inner alias."""
        _ent = getattr(self, "_opaque_selfmap_inner_aliases", {}).get(local)
        if not _ent:
            return None
        base, key_ir = _ent
        key = self._expr_to_whyml(key_ir, local_refs, invariant_ctx, subst)
        self._add_abstract_op(f"val function {base}_mem (k: string) : bool")
        return f"({base}_mem {key})"

    def _self_map_field_base(self, recv: Any) -> Optional[str]:
        """self-tcb-reduction `_compute_return_type` PATH(b): if `recv` refers to a
        FunctionEmissionMixin nested-map self-field DIRECTLY — `self.<field>` (FieldGet)
        or `getattr(self, "<field>", {})` (Call) — for one of the known opaque nested
        maps (`_record_types`/`_variant_types`), return the reader base (`<field>` with
        leading underscores stripped, e.g. `record_types`). The DIRECT-access twin of
        `_opaque_selfmap_aliases` (which requires an intermediate `X = getattr(...)`
        alias local). Gated on the `_compute_return_type` file -> byte-inert elsewhere."""
        if not self._uses_compute_return_type():
            return None
        fld: Optional[str] = None
        if isinstance(recv, dict):
            if recv.get("type") == "FieldGet" and recv.get("object") == "self":
                fld = recv.get("field")
            else:
                fld = self._opaque_selfmap_getattr_field(recv)
        if fld in ("_record_types", "_variant_types"):
            return fld.lstrip("_")
        return None

    def _self_field_nested_read(self, expr: Dict[str, Any], local_refs: Set[str],
                                invariant_ctx: bool,
                                subst: Optional[Dict[str, str]]) -> Optional[str]:
        """`<self-map-field>[K]["<lit>"]` (`self._record_types[ann]["whyml_name"]`,
        `self._variant_types[ann]["whyml_name"]`) -> the boundary reader
        `<base>_<lit> <K> : string` — the SAME reader `_opaque_selfmap_nested_read`
        uses for the alias form. The outer key `K` may be a pyval `.get`/subscript
        (`func['return_value_type']`), projected to its string carrier via `hstr_of`.
        None if the shape does not match a direct self-map-field nested read."""
        idx = expr.get("index", {})
        inner = expr.get("value", {})
        if not (isinstance(idx, dict) and idx.get("type") == "String"
                and isinstance(inner, dict) and inner.get("type") == "Subscript"):
            return None
        base = self._self_map_field_base(inner.get("value", {}))
        if not base:
            return None
        lit = whyml_ident(idx.get("value", ""))
        key_ir = inner.get("index", {})
        key = self._expr_to_whyml(key_ir, local_refs, invariant_ctx, subst)
        if self._expr_is_pyval(key_ir if isinstance(key_ir, dict) else {}):
            key = f"(hstr_of {key})"
        self._add_abstract_op(f"val function {base}_{lit} (k: string) : string")
        return f"({base}_{lit} {key})"

    @staticmethod
    def _negative_literal_index(index_ir: object) -> Optional[int]:
        """W8 (iv): `k > 0` iff `index_ir` is the negative integer literal `-k`.

        The Module-5 IR keeps a source `-1` as `UnaryOp('-', Number(1))`; a folded
        `Number(-1)` is accepted too. Anything else (a variable, an expression, `0`,
        a float) returns None and the caller keeps its existing lowering.
        """
        if not isinstance(index_ir, dict):
            return None
        val = None
        if (index_ir.get("type") == "UnaryOp" and index_ir.get("op") == "-"
                and isinstance(index_ir.get("expr"), dict)
                and index_ir["expr"].get("type") == "Number"):
            val = index_ir["expr"].get("value")
        elif index_ir.get("type") == "Number":
            raw = index_ir.get("value")
            if isinstance(raw, int) and not isinstance(raw, bool) and raw < 0:
                val = -raw
        if isinstance(val, int) and not isinstance(val, bool) and val > 0:
            return val
        return None

    def _handle_subscript(self, node: "ExprIR", local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature; deep body stays dict-based
        value = expr["value"]
        # opaque-nested-map-reader: `<alias>[k]["<lit>"]` where <alias> aliases an
        # opaque instance map (`getattr(self, "_field", {})`) → the boundary reader
        # `<base>_<lit> k : string` (the nested `record_types[tag]["whyml_name"]`
        # projection, keyed on the OUTER key `k`, returning a REAL string — not the
        # int-erased `subscript_get (subscript_get 0 tag) <hash>`). The reader
        # GENUINELY determines the branch value (a different `k` -> a different
        # opaque string). Registered by `_prescan_opaque_selfmap_aliases`.
        _osm = self._opaque_selfmap_nested_read(expr, local_refs, invariant_ctx, subst)
        if _osm is not None:
            return _osm
        # DIRECT-self nested read: `self._record_types[K]["whyml_name"]` /
        # `self._variant_types[ann]["whyml_name"]` -> `<base>_<lit> <K> : string` (the
        # non-alias twin of the reader above). Byte-inert off `_compute_return_type`.
        _dsn = self._self_field_nested_read(expr, local_refs, invariant_ctx, subst)
        if _dsn is not None:
            return _dsn
        # `_compute_return_type` PATH(b): `<optmap-getter>["<lit>"]` (`_cmg["elem_whyml"]`)
        # reads the inner `map string (option string)` of an `option (map ...)` getter local
        # -> unwrap the Some arm, read the literal key, unwrap the `option string` value
        # (`""` for None/absent). A REAL structural read (non-vacuous), not `subscript_get`.
        _cmi = expr.get("index", {})
        _cmv = expr.get("value", {})
        if (isinstance(_cmv, dict) and _cmv.get("type") == "Var"
                and _cmv.get("name") in getattr(self, "_optmap_getter_locals", set())
                and isinstance(_cmi, dict) and _cmi.get("type") == "String"):
            _cmn = f"!{whyml_ident(_cmv.get('name'))}"
            _cmk = self._expr_to_whyml(_cmi, local_refs, invariant_ctx, subst)
            return (f"(match {_cmn} with Some _m -> "
                    f"(match Map.get _m {_cmk} with Some _v -> _v | None -> \"\" end) "
                    f"| None -> \"\" end)")
        # opaque-nested-map-reader SPLIT form: `<inner-alias>["<lit>"]` → the boundary
        # reader `<base>_<lit> <outer-key> : string` (the split-binding twin of the
        # chained nested read above).
        _iv = expr.get("value", {})
        _ii = expr.get("index", {})
        if (isinstance(_iv, dict) and _iv.get("type") == "Var"
                and isinstance(_ii, dict) and _ii.get("type") == "String"):
            _osi = self._opaque_selfmap_inner_read(
                _iv.get("name", ""), _ii.get("value", ""), local_refs, invariant_ctx, subst)
            if _osi is not None:
                return _osi
        index = self._expr_to_whyml(expr["index"], local_refs, invariant_ctx, subst)
        # B-C5: `<emit_ir>.get("args")[0]` → `arg0_of` (the Call's first arg node).
        _ar0 = self._emit_ir_args_recv_ir(expr.get("value", {}))
        if _ar0 is not None and index == "0":
            return (f"(arg0_of {self._expr_to_whyml(_ar0, local_refs or set(), invariant_ctx, subst)})")
        # B-C6: `<emit_ir>["elts"][i]` (i in 0,1) → `elt{i}_of` — a MkTuple element
        # sub-node, for ghost_assign's ghost-dict `+=` branch `val_ir["elts"][0/1]`.
        _elt = self._emit_ir_args_recv_ir(expr.get("value", {}), "elts")
        if _elt is not None and index in ("0", "1"):
            return (f"(elt{index}_of {self._expr_to_whyml(_elt, local_refs or set(), invariant_ctx, subst)})")
        # value-model campaign incr5: a TYPED `<emit_ir>.elts[i]` read in a dict-type walker →
        # `irnth i (elts_of recv)` (the MODELLED IrMkTupleN element — a REAL node, unlike
        # `elt{i}_of` which projects binary IrTuple → `IrOther ""` on an IrMkTupleN).
        _mt = self._mktuple_elts_recv_ir(expr.get("value", {}))
        if _mt is not None:
            return (f"(irnth {index} (elts_of "
                    f"{self._expr_to_whyml(_mt, local_refs or set(), invariant_ctx, subst)}))")
        # §26: subscript-form emit_ir projection `<emit_ir>["value"/"name"/"type"/…]` →
        # the projection (mirrors the `.get` B-C3 routing), for `arr["value"]["name"]`.
        _kidx = expr.get("index", {})
        if (isinstance(_kidx, dict) and _kidx.get("type") == "String"
                and self._is_emit_ir_expr(value)):
            # cf6.md M1.3: SUBSCRIPT `c["pattern"]` reads the pattern SUB-NODE (`svalue_of`),
            # whereas `.get("pattern")` reads its KIND string — same key, different meaning at
            # different nesting. So subscript "pattern" projects to a NODE, not `kind_of`.
            _kv = _kidx.get("value")
            # self-tcb-reduction T1.a: SUBSCRIPT `expr['object']` is the object NAME string
            # (`FieldGet.object: str`) — the name of the object sub-node (`name_of ∘ object_of`),
            # distinct from `.get("object")` (a node). The only un-trusted subscript-"object" user is
            # `_handle_field_get_expr` (`obj == "self"`, `f"{obj}.{field}"`).
            if _kv == "object":
                _rv = self._expr_to_whyml(value, local_refs or set(), invariant_ctx, subst)
                return f"(name_of (object_of {_rv}))"
            _proj = "svalue_of" if _kv == "pattern" else _EMIT_IR_PROJ.get(_kv)
            if _proj:
                return f"({_proj} {self._expr_to_whyml(value, local_refs or set(), invariant_ctx, subst)})"
        # self-tcb-reduction _typeddict_field_access (b): a subscript `rec_info["whyml_name"]`
        # on a pyval LOCAL (`rec_info = self._record_types[rec_name]`, an `hval`) is the
        # DOUBLED hval read — project the `HStr` leaf to a `string` (the `whyml_name`/
        # scalar-string use). The `not in`-membership collection use (`rec_info["fields"]`)
        # is intercepted upstream by `_emit_membership` (which reads the RAW hval), so this
        # string projection only serves the scalar-string reads. κ=string RAW key. Gated on
        # `_pyval_locals` -> corpus/mirror byte-inert.
        if (isinstance(value, dict) and value.get("type") == "Var"
                and value.get("name") in getattr(self, "_pyval_locals", set())):
            _pv = whyml_ident(value.get("name"))
            _iir = expr.get("index", {})
            # self-tcb-reduction _namedtuple_positional_access: an INT-index subscript on a
            # pyval-local hval COLLECTION (`fields[idx_val]`, `fields` = an HArr) reads the
            # idx-th `HStr` as a `string` -> `hval_nth_str`. A String-KEY subscript
            # (`rec_info["whyml_name"]`) is the DOUBLED map read (`pairs_get`). Disambiguated
            # by the index IR node type.
            # self-tcb-reduction _namedtuple_positional_access: an INT-index subscript on a
            # pyval-local hval COLLECTION reads the idx-th `HStr` as a `string`
            # (`hval_nth_str`). Fires for a Number literal (`fields[0]`) OR any index into a
            # collection-consumed pyval local (`fields[idx_val]`, `idx_val` an int ref) —
            # `fields` ∈ `_pyval_coll_locals`, so the index is an int, never a string key.
            if ((isinstance(_iir, dict) and _iir.get("type") == "Number")
                    or value.get("name") in getattr(self, "_pyval_coll_locals", set())):
                return f"(hval_nth_str {_pv} {index})"
            # self-tcb-reduction _namedtuple_positional_access: when this String-key read
            # binds a COLLECTION-consumed pyval local (`fields = rec_info["fields"]`, flag
            # set by the assign binder), return the RAW `hval` value (`Some v_ -> v_`) so
            # the target types `hval` (for `hval_len`/`hval_nth_str`), NOT the HStr string
            # projection a string-consumed read (`rec_info["whyml_name"]`) needs.
            if getattr(self, "_pyval_get_raw_coll", False):
                return (f"(match {_pv} with HMap m_pvs -> "
                        f"(match pairs_get m_pvs {index} with Some v_ -> v_ "
                        f"| None -> (HMap PNil) end) | _ -> (HMap PNil) end)")
            return (f"(match {_pv} with HMap m_pvs -> "
                    f"(match pairs_get m_pvs {index} with Some (HStr _s) -> _s "
                    f"| _ -> \"\" end) | _ -> \"\" end)")
        # self-tcb-reduction (union/match cluster): a subscript whose BASE is itself an
        # hval-valued expression (`vinfo["constructors"][ctor_name]` — the inner
        # `vinfo["constructors"]` reads an `hval` HMap off the `map string (option hval)`
        # local `vinfo`) reads the key off that HMap carrier: `pairs_get (hval_as_map
        # <base>) <key>` -> the value `hval` (cap ii, the nested double-subscript). Gated
        # on `_expr_is_pyval(base)` being a Subscript -> corpus/mirror byte-inert.
        if (isinstance(value, dict) and value.get("type") == "Subscript"
                and self._expr_is_pyval(value)):
            _bh = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
            return (f"(match {_bh} with HMap m_pcii -> "
                    f"(match pairs_get m_pcii {index} with Some v_ -> v_ "
                    f"| None -> (HMap PNil) end) | _ -> (HMap PNil) end)")
        # §26: `X[k]` where X aliases a self dict-field → `Map.get self.<field> <k>` (the
        # getattr-bound-local read; `known_sizes[var_name]`). Mirrors the field-dict get.
        if isinstance(value, dict) and value.get("type") == "Var":
            _al = self._alias_self_field(value.get("name", ""))
            if _al:
                _fld = _al.split(".", 1)[1]
                _nu = self._self_field_dict_nu(_al)
                _recv = f"self.{self._field_label(getattr(self, '_current_self_type', None), _fld)}"
                _kir = expr.get("index", {})
                # cleared-hash S4: κ=string aliased field → RAW native string key.
                if self._self_field_dict_kappa(_al) == "string":
                    _key = index
                elif not self._in_spec and self._is_string_expr(_kir):
                    self._add_abstract_op("val str_hash_op (s: string) : int")
                    _key = f"(str_hash_op {index})"
                else:
                    _key = self._coerce_to_int(index)
                _dflt = '""' if _nu == "string" else "0"
                return f"(match Map.get {_recv} {_key} with | Some _v -> _v | None -> {_dflt} end)"
        # self-tcb-reduction _field_type_of: a subscript read `self.<field>[<key>]` on a
        # heterogeneous `map string (option hval)` self-field (`_record_types[gcls]`) —
        # UNWRAP the `option hval` to an `hval` (the missing-key default is the empty
        # `HMap PNil`), so a chained `.get("whyml_name")` (the DOUBLED hval read) descends
        # the REAL assoc-list structure instead of the opaque `get_1` facade. κ=string
        # (matching the field store/membership) → the RAW native string key. Gated on the
        # field being an hval map -> corpus byte-inert (no corpus `Dict[str, Any]` field).
        if (isinstance(value, dict) and value.get("type") in ("Attribute", "FieldGet")):
            _vo = value.get("object")
            _va = value.get("attr") or value.get("field")
            _dot = None
            if isinstance(_vo, dict) and _vo.get("type") == "Var" and _va:
                _dot = f"{_vo.get('name')}.{_va}"
            elif isinstance(_vo, str) and _va:
                _dot = f"{_vo}.{_va}"
            if _dot is not None and self._self_field_dict_nu(_dot) == "hval":
                _recv = self._expr_to_whyml(value, local_refs or set(), invariant_ctx, subst)
                if self._self_field_dict_kappa(_dot) == "string":
                    _key = index
                else:
                    self._add_abstract_op("val str_hash_op (s: string) : int")
                    _key = f"(str_hash_op {index})"
                return (f"(match Map.get {_recv} {_key} with "
                        f"| Some _v -> _v | None -> (HMap PNil) end)")
        # faithful-string-op.md §3.4: `<string>.split(sep)[i]` / `.rsplit(sep,k)[i]` → the
        # i-th piece — a substring of the receiver (str_split_elem_op). Length law only;
        # content unmodeled, so `[0]`/`[1]`/`[-1]` share the op (the bound holds for any i).
        _sp = self._split_call_recv_sep(expr.get("value", {}))
        if _sp is not None and not self._in_spec:
            _rcv, _sep = _sp
            _rcvw = self._expr_to_whyml(_rcv, local_refs or set(), invariant_ctx, subst)
            _sepw = (self._expr_to_whyml(_sep, local_refs or set(), invariant_ctx, subst)
                     if _sep is not None else '" "')
            self._add_abstract_op(
                "val str_split_elem_op (s sep: string) (i: int) : string\n"
                "    ensures { String.length result <= String.length s }")
            return f"(str_split_elem_op {_rcvw} {_sepw} {index})"
        # typing-engagement ty2 / 29-1700-typing-spec-5 §2.2 T5: a string-literal
        # subscript `p["x"]` on a TypedDict-record-typed receiver lowers to a
        # record-field read `p.x` (the core-agent hard rule). Non-TypedDict
        # receivers and non-literal indices fall through unchanged
        # (byte-identical). The static plane is Interpreted (record-field read);
        # the runtime plane is the plain-dict alias (Shimmed) — no blend.
        td_access = self._typeddict_field_access(value, expr.get("index", {}),
                                                  local_refs, invariant_ctx, subst)
        if td_access is not None:
            return td_access
        # typing-engagement ty2 / 30-1700-typing-spec-6 §2.2 N5: an integer-
        # literal subscript `p[0]` on a NamedTuple-record-typed receiver lowers
        # to a record-field read of the field at that declaration index (the
        # core-agent hard rule). Non-NamedTuple receivers and non-literal
        # indices fall through unchanged (byte-identical). The static plane is
        # Interpreted (record-field read by index); the runtime plane is the
        # plain-tuple alias (Shimmed) — no blend.
        nt_access = self._namedtuple_positional_access(value, expr.get("index", {}),
                                                       local_refs, invariant_ctx,
                                                       subst)
        if nt_access is not None:
            return nt_access
        # 07-1705-rev4 P3/P5: element read of a seq-modelled list local is `Seq.get` —
        # BODY context only (in a contract a seq-promoted param is the array entry value).
        if (isinstance(value, dict) and value.get("type") == "Var"
                and value.get("name") in getattr(self, "_seq_locals", set())
                and not self._in_spec):
            base = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)  # `!a`
            # self-tcb-reduction (union/match cluster): a negative LITERAL index `a[-k]`
            # on a seq local is Python's from-the-end read `a[len-k]` (`Seq.length !a -
            # k`) — the READ-side twin of the seq-store negative-index rewrite. Emitting
            # the literal `-k` was both unfaithful and unprovable (a negative Seq.get index
            # never discharges the bounds VC).
            _negk = self._negative_literal_index(expr.get("index", {}))
            if _negk is not None:
                index = f"(Seq.length {base} - {_negk})"
            return f"(Seq.get {base} {index})"
        # strings-plan Stage 2: s[i] on a str is the 1-char substring String.substring s i 1
        # (Why3 strings have no char type; a character is a length-1 string). Reuses the
        # str_sub_op bridge whose length lemma gives String.length result = 1 under bounds.
        if self._is_string_expr(value):
            vstr = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
            if self._in_spec:
                return f"(String.substring {vstr} {index} 1)"
            self._add_abstract_op(
                "val str_sub_op (s: string) (lo len: int) : string\n"
                "    ensures { result = (String.substring s lo len) }\n"
                "    ensures { (0 <= lo /\\ 0 <= len /\\ lo + len <= String.length s)"
                " -> String.length result = len }")
            return f"(str_sub_op {vstr} {index} 1)"
        # 07-0903 W1: `a[i][k]` where `a` is a list/array of tuples — the inner `a[i]` is
        # a tuple value (`Array.get`), so destructure its k-th component. Must precede the
        # 2-D matrix detection below (which would otherwise read `a` as a `matrix`).
        if (value.get("type") == "Subscript"
                and value.get("value", {}).get("type") == "Var"
                and value["value"]["name"] in getattr(self, "_tuple_array_locals", {})):
            _ta = self._tuple_array_locals[value["value"]["name"]]
            try:
                _tk = int(index)
            except ValueError:
                _tk = -1
            if 0 <= _tk < _ta:
                _elem = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
                _bind = ", ".join(f"_r{_tk}_" if j == _tk else "_" for j in range(_ta))
                return f"(let ({_bind}) = {_elem} in _r{_tk}_)"
        # \result[i] on a tuple return → let-destructure
        if value.get("type") == "Result" and hasattr(self, "_current_tuple_arity"):
            arity = self._current_tuple_arity
            if arity and arity > 0:
                try:
                    idx = int(index)
                except ValueError:
                    idx = -1
                if 0 <= idx < arity:
                    names = [f"_r{k}_" if k != idx else f"_r{idx}_" for k in range(arity)]
                    bindings = ", ".join(
                        names[k] if k == idx else "_" for k in range(arity)
                    )
                    return f"(let ({bindings}) = result in _r{idx}_)"
        # 0442.md C2: `p[i]` on a tuple-typed local (`p = mk(x)` where `mk` returns a
        # tuple) → destructure, not the abstract `subscript_get (x:int)` (a type error
        # against the `(int, …)` tuple). Arity is tracked in `_ghost_tuple_vars`.
        if value.get("type") == "Var":
            _tarity = getattr(self, "_ghost_tuple_vars", {}).get(value.get("name", ""), 0)
            if _tarity and _tarity > 0:
                try:
                    _idx = int(index)
                except ValueError:
                    _idx = -1
                if 0 <= _idx < _tarity:
                    _bind = ", ".join(f"_r{_idx}_" if k == _idx else "_"
                                      for k in range(_tarity))
                    _base = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
                    return f"(let ({_bind}) = {_base} in _r{_idx}_)"
        # nested-list.md S3 (+ §8/§9 EXTENSION: arbitrary depth): `a[i][j]` /
        # `a[i][j][k]` … where `a` is a `List[<container>]` param
        # (`array (seq τ)` / `array (map κ (option ν))`, see `_list_nested_elem`).
        # The inner read `a[i]` yields the PURE element collection, so the outer
        # `[j]`/`[key]` is a `Seq.get`/`Map.get` on it — NOT a second `Array.get`
        # nor the opaque `subscript_get`. The inner read is hoisted into a `let`
        # (it may carry its OWN body-context KeyError/IndexError assert block, which
        # cannot sit inside the outer read's application/assert). The element type
        # of `value` is computed RECURSIVELY (`_nested_access_type`) by peeling one
        # container level per index level, so `a[i][j][k]` composes `Seq.get` to the
        # type-recursion depth bound (MAX_NEST_DEPTH=4). `_inner` is lowered by a
        # recursive `_expr_to_whyml`, which re-enters this same block for the deeper
        # levels. Deeper than the type bound → `_nested_access_type` is None → the
        # opaque `subscript_get` fallback (documented depth residual). Byte-identical
        # to the former 2-level unfold for depth ≤2 (verified via corpus emission diff).
        _ne = self._nested_access_type(value) if value.get("type") == "Subscript" else None
        if _ne is not None and (_ne.startswith("seq ") or _ne.startswith("map ")):
            _inner = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)  # a[i]
            if _ne.startswith("seq "):
                _read = f"(Seq.get _row {index})"
                _wrapped = self._wrap_with_no_exception_assert(
                    ("subscript", "read"), [f"(Seq.length _row)", index], _read)
                return f"(let _row = {_inner} in {_wrapped})"
            if _ne.startswith("map "):
                # inner element is a `map κ (option ν)` (List[Dict[..]]): the outer
                # `[key]` reads that map. κ=string passes the key through native;
                # otherwise a string key is `str_hash_op`-hashed (int-keyed map),
                # matching the body-dict subscript convention.
                _inner_v = (_ne.split("(option ", 1)[1].rsplit(")", 1)[0]
                            if "(option " in _ne else "int")
                _idef = '""' if _inner_v == "string" else "0"
                _idx_ir = expr.get("index", {})
                if "map string" in _ne:
                    _k = index
                elif not self._in_spec and self._is_string_expr(_idx_ir):
                    self._add_abstract_op("val str_hash_op (s: string) : int")
                    _k = f"(str_hash_op {index})"
                else:
                    _k = self._coerce_to_int(index)
                _read = (f"(match Map.get _row {_k} "
                         f"with | Some v_ -> v_ | None -> {_idef} end)")
                _wrapped = self._wrap_with_no_exception_assert(
                    ("map_get", None), ["_row", _k], _read)
                return f"(let _row = {_inner} in {_wrapped})"
        # Detect 2D access: a[i][j] → Subscript(Subscript(Var(a), i), j)
        if (value.get("type") == "Subscript" and
                value.get("value", {}).get("type") == "Var" and
                value.get("value", {}).get("name") in getattr(self, "_array2d_params", set()) and
                value.get("value", {}).get("name") not in getattr(self, "_dict_locals", set())):
            base = value["value"]["name"]
            row = self._expr_to_whyml(value["index"], local_refs, invariant_ctx, subst)
            col = index
            return f"(get {base} {row} {col})"
        value_str = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
        # L0 (os-bodyvc-spec): `\result[i]` in a CONTRACT where the function returns `array int`
        # is a real `Array.get` (`result[i]`), not the opaque `subscript_get` — otherwise a value
        # postcondition over an array result (`\result[0]*256 + \result[1] == v`) can't even be
        # expressed, let alone proven. Spec context only (a logic term — no bounds-assert wrapper,
        # matching the hand-verified .mlw); opaque-typed reads still fall through to subscript_get.
        # WL-04a: widened from `array int` to ANY `array τ` return (`array string`,
        # `array real`, …), so `\result[0] == "a"` / `\result[0] == 1.5` on a
        # `-> List[str]` / `-> List[float]` return lowers to a native `Array.get`
        # (element-polymorphic), not the opaque `subscript_get`. Byte-identical for an
        # `array int` return (still matched by the `array ` prefix).
        if (self._in_spec and value.get("type") == "Result"
                and getattr(self, "_func_return_type", "").startswith("array ")):
            return f"({value_str}[{index}])"
        # L0′ (challenging-the-plan §4.1): `self.<array-field>[i]` in a contract/class-invariant is a
        # real `Array.get`, not the opaque (and, in a class invariant, unbound) `subscript_get` — so a
        # data-refinement coupling invariant `ginode[n] == unpack(self.disk[…])` can be expressed.
        # Spec context only, logic term (no bounds-assert wrapper). Needs `_current_self_type` set
        # during class-invariant emission (preamble L0′ part 1) for `_field_type_of` to resolve.
        if (self._in_spec and value.get("type") in ("Attribute", "FieldGet")
                and self._field_type_of(value) in ("list", "tuple", "bytes", "bytearray")):
            return f"({value_str}[{index}])"
        if self._value_semantic:
            # A1-residual nested-map: `d[ko][ki]` — the inner read `d[ko]`
            # yields a `map κi (option νi)` (the outer dict's nested-map value),
            # so the outer `[ki]` is itself a `Map.get`, not the opaque
            # `subscript_get`. `value` here is the inner Subscript `d[ko]`;
            # `value_str` is its already-lowered map expression.
            if value.get("type") == "Subscript":
                _ib = value.get("value", {})
                _nu = (getattr(self, "_dict_value_types", {}).get(_ib.get("name", ""))
                       if isinstance(_ib, dict) and _ib.get("type") == "Var" else None)
                # nested-map.md: `self._nested_field[ko][ki]` — the inner base is a self dict-field
                # whose value_type is itself a `map …` (nested dict), so the outer `[ki]` reads that
                # inner map. Parallel to the body-dict `d[ko][ki]` case above.
                if _nu is None and isinstance(_ib, dict) and _ib.get("type") in ("Attribute", "FieldGet"):
                    _o = _ib.get("object"); _f = _ib.get("field") or _ib.get("attr")
                    if isinstance(_o, str):
                        _nu = self._self_field_dict_nu(f"{_o}.{_f}")
                if _nu and _nu.startswith("map "):
                    _inner_v = (_nu.split("(option ", 1)[1].rsplit(")", 1)[0]
                                if "(option " in _nu else "int")
                    _idef = '""' if _inner_v == "string" else "0"
                    # inner key κi: a `map string` inner passes the key through; an int-keyed inner
                    # (`map int …`, incl. nested-map.md's str-keys-hashed convention) hashes a STRING
                    # key with `str_hash_op`, else int-coerces.
                    _idx_ir = expr.get("index", {})
                    if "map string" in _nu:
                        _k = index
                    elif not self._in_spec and self._is_string_expr(_idx_ir):
                        self._add_abstract_op("val str_hash_op (s: string) : int")
                        _k = f"(str_hash_op {index})"
                    else:
                        _k = self._coerce_to_int(index)
                    # `value_str` (the inner `d[ko]` read) lowers to a program
                    # `begin assert..; match.. end` block carrying its OWN
                    # KeyError assert — it cannot sit inside the outer read's
                    # `assert { … }` logic formula. Hoist it into a `let` so the
                    # outer assert + `Map.get` reference a plain logic term.
                    _read = (f"(match Map.get _nmap {_k} "
                             f"with | Some v_ -> v_ | None -> {_idef} end)")
                    _wrapped = self._wrap_with_no_exception_assert(
                        ("map_get", None), ["_nmap", _k], _read)
                    return f"(let _nmap = {value_str} in {_wrapped})"
            var_name = value.get("name", "") if value.get("type") == "Var" else ""
            index_ir = expr.get("index", {})
            if (var_name and index_ir.get("type") == "Number" and
                    isinstance(index_ir.get("value"), (int, float))):
                idx_val = int(index_ir["value"])
                known_elems = getattr(self, "_known_collection_elements", {})
                if var_name in known_elems and idx_val in known_elems[var_name]:
                    return known_elems[var_name][idx_val]
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_inline_array_temps", set()) or
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict and var_name:
                st = getattr(self, "_current_symbol_table", {})
                if st.get(var_name) in ("list", "bytes", "bytearray"):
                    # WL-06 FIX: a bytes/bytearray value is the τ-blessed
                    # `bytes=int†` array-int-backed buffer (`b : array int`), so a
                    # byte read `b[i]` must lower to a native `Array.get b i` (a
                    # coherent `int` byte read), NOT the opaque `subscript_get
                    # (x:int)(i:int):int` — which, applied to `array int`, is an
                    # `array int` vs `int` type error. Byte CONTENT stays opaque
                    # (a faithful `bytes` model is a documented follow-on); the read
                    # is now a sound, type-checking `int`.
                    is_array = True
                elif st.get(var_name) in ("dict", "set", "frozenset"):
                    is_dict = True
            # `self.<field>[k]` where the field is set/dict/array-typed.
            if not is_array and not is_dict and value.get("type") in ("Attribute", "FieldGet"):
                ft = self._field_type_of(value)
                if ft in ("set", "dict", "frozenset"):
                    is_dict = True
                elif ft in ("list", "tuple", "bytes", "bytearray"):
                    is_array = True
            if is_array:
                # arity2.md (2b): parenthesise a ref-bound array deref (`!x`)
                # before subscripting, else `!x[i]` parses as `!(x[i])`.
                arr_e = f"({value_str})" if value_str.startswith("!") else value_str
                length_expr = f"(Array.length {arr_e})"
                # W8 capability (iv): a NEGATIVE LITERAL index `a[-k]` is Python's
                # from-the-end read, i.e. `a[len(a) - k]`. Emitting the literal `-k`
                # was BOTH unfaithful (it is not element `-k` of anything) and
                # unprovable (a negative index can never discharge the array-bounds
                # VC). Only a syntactically-negative INTEGER LITERAL is rewritten —
                # a negative *value* in a variable is not statically recognisable and
                # keeps the old lowering (a documented residual, and the honest one:
                # a general run-time negative-index model needs a conditional read).
                _negk = self._negative_literal_index(expr.get("index", {}))
                if _negk is not None:
                    index = f"({length_expr} - {_negk})"
                inner = f"{arr_e}[{index}]"
                # no_exception IndexError → assert in_bounds before the read.
                return self._wrap_with_no_exception_assert(
                    ("subscript", "read"), [length_expr, index], inner)
            elif is_dict:
                # Body dict subscript read: `d[k]` →
                # `match Map.get !d k with Some v -> v | None -> 0 end`.
                # For body-local dicts, `value_str` already includes the
                # `!` deref because `_handle_var_expr` treats them as
                # refs. For `self.<dict-field>` accesses, no deref is
                # needed (record-field access is direct).
                dvar = value.get("name", "") if value.get("type") == "Var" else ""
                # no-more-int-3 A1 T1.2: a string KEY (κ) is passed through
                # unhashed (`map string …`); T1.1: a string VALUE reads back a
                # `string`, so the `None` arm is a typed placeholder (`""`) —
                # proven dead under `#@ no_exception KeyError` (faithful read),
                # the ambient default otherwise.
                # cleared-hash S4: a κ=string record dict/set FIELD (`self.<field>[k]`,
                # no `dvar`) is `map string (option ν)` — read the RAW native string key
                # (matching the field store/`.get`/membership); a mismatch is a type error.
                _fld_kappa = None
                if not dvar and value.get("type") in ("Attribute", "FieldGet"):
                    _ko = value.get("object"); _kf = value.get("field") or value.get("attr")
                    if isinstance(_ko, str):
                        _fld_kappa = self._self_field_dict_kappa(f"{_ko}.{_kf}")
                if (getattr(self, "_dict_key_types", {}).get(dvar) == "string"
                        or _fld_kappa == "string"):
                    k = index
                elif (not self._in_spec
                      and self._is_string_expr((expr.get("slice") or expr.get("index") or {}))):
                    # typed-ir-for-b-ceiling.md §9: a STRING key into an int-keyed body
                    # dict (`bitwise_ops = {"&": "bit_and", …}` → `map _ (option int)`) is
                    # `str_hash_op`-hashed — the SAME as the `in`-membership above, so both
                    # agree on the key type. Byte-identical (int key keeps `_coerce_to_int`).
                    self._add_abstract_op("val str_hash_op (s: string) : int")
                    k = f"(str_hash_op {index})"
                else:
                    k = self._coerce_to_int(index)
                # The missing-key placeholder is typed per ν (consolidated).
                default = self._dv_missing_default(
                    getattr(self, "_dict_value_types", {}).get(dvar))
                # list-comprehension-lowering.md L5: a self-field dict read
                # (`self._abstract_ops[k]`) has no `dvar`; its value type comes from the
                # record field → a `string` field defaults to "" (not the int `0`).
                if not dvar and value.get("type") in ("Attribute", "FieldGet"):
                    _o = value.get("object")
                    _f = value.get("field") or value.get("attr")
                    _fnu = (self._self_field_dict_nu(f"{_o}.{_f}")
                            if isinstance(_o, str) else None)
                    if _fnu == "string":
                        default = '""'
                    elif (isinstance(_fnu, str) and _fnu.startswith("map int (")
                          and _fnu.endswith(")")):
                        # nested-map.md: a NESTED-dict field read (`self._class_constants[k]`)
                        # yields the INNER map; the missing-key default is the empty inner map
                        # (`const None`), not the int `0`.
                        default = f"(const (None: {_fnu[len('map int ('):-1]}))"
                inner = f"(match Map.get {value_str} {k} with | Some v_ -> v_ | None -> {default} end)"
                # no_exception KeyError → assert has_key before the read.
                return self._wrap_with_no_exception_assert(
                    ("map_get", None), [value_str, k], inner)
            else:
                # lever #1 sub-inc A cap (d): a direct subscript of a CALL whose registered
                # abstract-val return type is `array string` (`self._resolve_dotted_signature
                # (func)[0]`) reads a real STRING element via an opaque, bounds-free
                # `subscript_get_str` over-approximation — NOT the int-hash-erasing
                # `subscript_get (x:int):int` (which collapses the downstream type-string
                # compare to an int-hash literal). Sound (the [0] is *some* string of the
                # resolver's returned tuple) and non-vacuous (it consumes the real
                # `array string` receiver and the index). Fires only for a Call receiver
                # whose ret-type resolves to `array string`; every other subscript is
                # byte-identical.
                if (isinstance(value, dict) and value.get("type") == "Call"
                        and self._resolve_dotted_signature(value.get("func", ""))[0] == "array string"):
                    self._add_abstract_op(
                        "val subscript_get_str (a: array string) (i: int) : string")
                    return f"(subscript_get_str {value_str} {self._coerce_to_int(index)})"
                self._add_abstract_op("val subscript_get (x: int) (i: int) : int")
                return f"(subscript_get {self._coerce_to_int(value_str)} {self._coerce_to_int(index)})"
        else:
            return f"(Map.get !{self._heap_var} ({value_str} + {index}))"

    def _handle_attribute_expr(self, node: "ExprIR", local_refs: Set[str],
                               invariant_ctx: bool, subst: Dict[str, str]) -> str:
        """Handle non-self attribute access: record field or abstract getter."""
        expr = node.to_dict()   # Phase-B-expr: typed signature; deep body stays dict-based
        obj_ir = expr.get("object", {})
        attr = expr.get("attr", "unknown")
        # 07-0903 W2: `\result.<field>` — field access on a record-returning function's
        # result. The WhyML result is the record value; emit `result.<field_label>`.
        if isinstance(obj_ir, dict) and obj_ir.get("type") == "Result":
            return f"result.{self._field_label(getattr(self, '_func_return_type', None), attr)}"
        # W8 (ii, token-kind concreteness): `_tokenize.OP` -> the CONCRETE int (55), read
        # from the real `tokenize`/`token` module at emission time (Module5 builds the
        # map). Replaces the opaque `(get_OP _tokenize)`, an unconstrained int that made
        # every kind comparison contentless and kind-disjointness inexpressible. Empty map
        # for every program that does not import those modules -> byte-inert.
        _tkc = getattr(self, "_token_kind_constants", None)
        if _tkc and isinstance(obj_ir, dict) and obj_ir.get("type") == "Var":
            _tkkey = "{}.{}".format(obj_ir.get("name"), attr)
            if _tkkey in _tkc:
                return "({})".format(_tkc[_tkkey])
        # W8 capability (vi) — PROJECTION OFF A SIBLING METHOD CALL. `self.cur().py_type`:
        # the base is a `self.<m>(...)` Call whose declared return type is a RECORD, so it
        # lowers (above) to the CONCRETE `(<class>__<m> self)`. The field read is then a
        # NATIVE record projection over that value, not the opaque `(get_py_type …)` getter
        # — which mistypes against `tok` and fails L3-tc. Same `_record_array_fields` gate
        # as (iii), so absent (hence byte-inert) everywhere else.
        if (isinstance(obj_ir, dict) and obj_ir.get("type") == "Call"
                and isinstance(obj_ir.get("func"), str)
                and obj_ir["func"].startswith("self.")
                and getattr(self, "_record_array_fields", None)):
            _crt = self._resolve_dotted_signature(obj_ir["func"])[0]
            if _crt in {_ri["whyml_name"]
                        for _ri in getattr(self, "_record_types", {}).values()}:
                _os = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
                return (f"(let _rec_ = {_os} in "
                        f"_rec_.{self._field_label(_crt, attr)})")
        # TERM CARRIER: `atom.name` on a `term`-typed local projects the payload of the
        # UNIQUE arm carrying that field — `(match !atom with Var _v0 -> _v0 | _ -> "")`.
        # Today it lowers to the opaque `(get_name !atom)`, an unconstrained int getter
        # that is both ill-typed against `term` and value-blind. Admitted ONLY when the
        # field name identifies EXACTLY ONE arm of the inductive, so the projection can
        # never be ambiguous; the other arms' default is UNREACHABLE wherever the caller
        # has narrowed with the `isinstance` discriminant above (the live
        # `parse_atom_application` shape), so the witness only has to type-check.
        if (isinstance(obj_ir, dict) and obj_ir.get("type") == "Var"
                and obj_ir.get("name") in getattr(self, "_term_local_vars", set())):
            _tspec = (getattr(self, "_term_adt_spec", None) or {}).get("ctors") or {}
            _owner = [(cn, flds) for cn, flds in _tspec.items()
                      if any(fn == attr for fn, _wt in flds)]
            if len(_owner) == 1:
                _cn, _flds = _owner[0]
                _idx = next(i for i, (fn, _w) in enumerate(_flds) if fn == attr)
                _wt = _flds[_idx][1]
                _binders = " ".join(f"_v{i}" if i == _idx else "_"
                                    for i in range(len(_flds)))
                _dflt = {"string": '""', "term": '(Unsupported "" "")',
                         "int": "0", "bool": "false", "list term": "Nil",
                         "list string": "Nil"}.get(_wt)
                if _dflt is not None:
                    _o = obj_ir["name"]
                    _d = (f"!{whyml_ident(_o)}" if _o in local_refs
                          else whyml_ident(_o))
                    return (f"(match {_d} with {_cn} {_binders} -> _v{_idx} "
                            f"| _ -> {_dflt} end)")
        # cursor-nest `parse_atom` — the UNION-return sibling of the branch just above.
        # `self.peek().kind` where `peek` returns `Optional[Token]`: project the union's
        # Some-arm carrier FIRST, then take the native record field off it. Without this
        # the base falls through to the opaque int-hash `get_kind`, which is value-blind
        # (it makes every kind comparison contentless — the exact facade wall-lessons (l)
        # describes). The `| _ -> <record default>` arm is UNREACHABLE wherever the caller
        # has guarded `is not None`, so the witness only has to type-check.
        if (isinstance(obj_ir, dict) and obj_ir.get("type") == "Call"
                and isinstance(obj_ir.get("func"), str)):
            _cu = self._sibling_call_union_type(obj_ir)
            if _cu:
                _os = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
                _proj = self._union_read_projection(_cu, _os)
                if _proj is not None:
                    _pay = next(
                        (c.get("payload", ["int"])[0]
                         for c in (getattr(self, "_variant_types", {})
                                   .get(_cu, {}).get("constructors", {}).values())
                         if c.get("arity") == 1), "int")
                    return (f"(let _rec_ = {_proj} in "
                            f"_rec_.{self._field_label(_pay, attr)})")
        # WL-04b (wrong-lowering-to-fix.md §WL-04 record residual): `a[i].field` on a
        # flat `List[<record>]` param (`a : array <record>`, registered in
        # `_record_array_params`) is a NATIVE record projection over the array read —
        # `(a[i]).<field-label>` — not the opaque `get_field` collapse. The element
        # read `a[i]` is hoisted into a `let` so a body-context bounds-assert block
        # (`begin assert…; a[i] end`, present under `#@ no_exception IndexError`) can
        # bind before the projection; in spec context `a[i]` is a plain `Array.get`.
        if isinstance(obj_ir, dict) and obj_ir.get("type") == "Subscript":
            _bv = obj_ir.get("value", {})
            if isinstance(_bv, dict) and _bv.get("type") == "Var":
                _nm = _bv.get("name", "")
                # WL-04c: a record-array LOCAL (`a = [Point(1,2), …]`, registered in
                # `_record_array_locals`) shares the WL-04b PARAM projection path.
                _wn = (getattr(self, "_record_array_params", {}).get(_nm)
                       or getattr(self, "_record_array_locals", {}).get(_nm))
                if _wn is not None:
                    _os = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
                    return f"(let _rec_ = {_os} in _rec_.{self._field_label(_wn, attr)})"
            # W8 capability (iii) — SELF-FIELD array-read PROJECTION. `self.toks[self.i]
            # .py_type` reads an element of an `array <record>` SELF-FIELD and projects a
            # field off it. Before this, only the PARAM/LOCAL record-array shapes above
            # reached the `_rec_` projector; a self-field base fell through to the opaque
            # `(get_<attr> …)` getter, which mistypes (`… has type tok, but is expected to
            # have type int`) and fails L3-tc. `_record_array_fields` (field -> element
            # record CLASS) is populated by `_emit_type_decls` only for a `List[<record>]`
            # record field, so this is absent — hence byte-inert — everywhere else.
            if (isinstance(_bv, dict)
                    and _bv.get("type") in ("FieldGet", "Attribute")):
                _raf = getattr(self, "_record_array_fields", None) or {}
                _ob = _bv.get("object") or _bv.get("value")
                if isinstance(_ob, dict):
                    _ob = _ob.get("name")
                _fn = _bv.get("field") or _bv.get("attr")
                _ecls = _raf.get(_fn) if _ob == "self" else None
                if _ecls is not None:
                    _wn = getattr(self, "_record_types", {}).get(_ecls, {}).get(
                        "whyml_name")
                    if _wn is not None:
                        _os = self._expr_to_whyml(obj_ir, local_refs,
                                                  invariant_ctx, subst)
                        return (f"(let _rec_ = {_os} in "
                                f"_rec_.{self._field_label(_wn, attr)})")
            # WL-04c: `\result[i].field` on a `-> List[<record>]` return (`_func_return_type
            # == "array <record>"`) — `\result[i]` is a native `Array.get` (widened in
            # `_handle_subscript` L0) and `.field` a native record projection over it.
            if isinstance(_bv, dict) and _bv.get("type") == "Result":
                _rt = getattr(self, "_func_return_type", "") or ""
                if _rt.startswith("array "):
                    _wn = _rt[len("array "):].strip()
                    if _wn in {i.get("whyml_name")
                               for i in getattr(self, "_record_types", {}).values()}:
                        _os = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
                        return f"(let _rec_ = {_os} in _rec_.{self._field_label(_wn, attr)})"
        # scc3.md Phase A: a quantifier-bound record var `o : C` (registered by
        # `_push_quant_binder`) — `o.field` is the record field, qualified via
        # `_field_label`, not an abstract `get_field` stub. (The class invariant is
        # already a Why3 type invariant on `c`, so the quantifier is sound.)
        if isinstance(obj_ir, dict) and obj_ir.get("type") == "Var":
            _vn = obj_ir.get("name", "")
            _qcls = self._quant_record_binders.get(_vn)
            if _qcls is not None:
                _cl = self._record_types[_qcls]["whyml_name"]
                # WL-04b: the binder may be RENAMED by `subst` (the content-faithful
                # comprehension rebinds its record target `p` → `_celt`); emit the
                # substituted WhyML name while looking the binder up under its
                # original name. `subst` is None/absent for every quantifier record
                # binder → byte-identical.
                _emit_vn = subst.get(_vn, _vn) if subst else _vn
                return f"{whyml_ident(_emit_vn)}.{self._field_label(_cl, attr)}"
            # inline.md Phase 1: a module-level global object `g : C` — `g.field` is the
            # global record's field (qualified via `_field_label`), not a `get_field` stub.
            _gcls = self._module_global_classes.get(_vn)
            if _gcls is not None and _gcls in self._record_types:
                _cl = self._record_types[_gcls]["whyml_name"]
                return f"{whyml_ident(_vn)}.{self._field_label(_cl, attr)}"
        if isinstance(obj_ir, str):
            return f"(get_{attr} {obj_ir})"
        if obj_ir.get("type") == "Var":
            var_name = obj_ir.get("name", "")
            # W8 capability (iii), LOCAL-BOUND variant: `t = self.toks[self.i]` then
            # `t.py_type`. Such a local is pre-declared as a record REF (see
            # `_collect_record_field_elem_locals`), so the projection is `(!t).<label>`.
            # Without it the read falls through to the opaque `(get_py_type !t)` getter
            # and fails L3-tc (`… has type tok, but is expected to have type int`).
            # `_record_field_elem_locals` is non-empty only inside a method of a class
            # with a `List[<record>]` field → byte-inert everywhere else.
            _rfe = getattr(self, "_record_field_elem_locals", None) or {}
            _ecls = _rfe.get(var_name)
            if _ecls is not None:
                _wn = getattr(self, "_record_types", {}).get(_ecls, {}).get("whyml_name")
                if _wn is not None:
                    return (f"(!{whyml_ident(var_name)})."
                            f"{self._field_label(_wn, attr)}")
            if var_name in self._record_locals:
                # B1.4 (b1-plan.md §10): an AMBIGUOUS field (shared by >1 record —
                # e.g. `target`/`value` across the imported Stmt dataclasses) is
                # declared as the qualified label `<record>_<field>`, so its access
                # must qualify too, else Why3 reports the bare name unbound. Resolve
                # the record type from the symbol table and qualify via `_field_label`
                # using the record's own whyml_name (the key may be CamelCase or
                # lowered). Non-ambiguous fields keep the exact bare form —
                # byte-identical for every existing (local-record) driver.
                _rt = getattr(self, "_record_types", {})
                _ot = getattr(self, "_current_symbol_table", {}).get(var_name)
                if attr in getattr(self, "_ambiguous_fields", set()) and _ot:
                    _key = _ot if _ot in _rt else (_ot.lower() if _ot.lower() in _rt else None)
                    if _key is not None:
                        _rl = _rt[_key].get("whyml_name", _ot.lower())
                        return f"{whyml_ident(var_name)}.{self._field_label(_rl, attr)}"
                # tcb(M5) spec-op batch mini-M1 (_csl_at): a NON-ambiguous field whose Python
                # name is a WhyML RESERVED WORD (e.g. `label` — `At.label`) is declared with
                # the `whyml_ident`-sanitized label (`py_label`, `_field_label`'s `base` for the
                # non-ambiguous case, preamble.py `_field_label` call at record-declaration
                # time). This bare fallback previously emitted the RAW `attr` unconditionally —
                # a latent mismatch that only a reserved-word field name can trigger (`attr` is
                # unchanged by `whyml_ident` for every existing non-reserved field, so this is
                # byte-identical elsewhere). Route through `whyml_ident` to match the
                # declaration.
                return f"{whyml_ident(var_name)}.{whyml_ident(attr)}"
        # self-ir-schema.md IR2: `<emit_ir>.value` / `.target` / … (a StmtIR field access on
        # an emit_ir node, e.g. `body_stmts[-1].value`) is an opaque emit_ir SUB-NODE —
        # `svalue_of` returns `IrOther ""` for a non-IrSub node (sound; content unmodeled),
        # so `… is not None` type-checks (always-present, §B-C4). @mutable_state-gated.
        # L1 tparam reflection-node ADT: in a tparam-collector function (not @mutable_state),
        # the bound sub-node `bnode = tp.bound` is a genuine emit_ir LOCAL whose `.id`/`.attr`
        # must still project via `name_of` (the isinstance already dispatches is_var/
        # is_attribute). Extend the @mutable_state gate to the emit_ir-local case, scoped to a
        # tparam-collector function (`_current_tparam_node_params` non-empty) -> corpus-inert
        # AND inert for every non-tparam mirror.
        _in_tparam_fn = bool(getattr(self, "_current_tparam_node_params", None))
        if (self._is_emit_ir_expr(obj_ir)
                and (getattr(self, "_current_self_type", None)
                     in getattr(self, "_mutable_state_classes", set())
                     or (_in_tparam_fn and isinstance(obj_ir, dict)
                         and obj_ir.get("type") == "Var"
                         and obj_ir.get("name")
                         in getattr(self, "_emit_ir_local_vars", set())))):
            _os = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
            # self-tcb-reduction T1.a: `<emit_ir>.kind` is the DISCRIMINANT (`kind_of`, a string),
            # not a sub-node — so `inner.kind == "Subscript"` routes through `str_eq_op`.
            if attr in _EMIT_IR_STR_ATTRS:
                return f"({_EMIT_IR_STR_ATTRS[attr]} {_os})"
            # self-tcb-reduction T1.a: a node-LIST attr (`node.elts`/`node.parts`/…) → the args
            # list (`args_of`, an `array emit_ir`), so `for elt in node.elts` iterates it.
            if attr in ("elts", "parts", "args", "captures", "alternatives"):
                return f"(args_of {_os})"
            # ghost-handler-wall Q2: a position-SWAPPING attr (`elem`/`set`/`list`/`index`)
            # is disambiguated by the ENCLOSING HANDLER, since a single global name entry
            # cannot serve both `SetAddExpr(set, elem)` and `SetMemExpr(elem, set)`
            # faithfully. Checked BEFORE the global `_EMIT_IR_NODE_ATTRS` table (which
            # deliberately excludes these names — see its comment); inert whenever
            # `_current_emitting_func` is not one of the five swap-family handlers, so
            # every other mirror/corpus emission is byte-identical.
            _cef = getattr(self, "_current_emitting_func", None) or ""
            for _hname, _projmap in _EMIT_IR_HANDLER_ATTR_PROJ.items():
                if attr in _projmap and (_cef == _hname or _cef.endswith("__" + _hname)):
                    return f"({_projmap[attr]} {_os})"
            # 2-child-cluster mini-M1: an unambiguous 2-child-dataclass sub-node attr
            # (`node.dict`/`node.key`/`node.head`/`node.tail`) → its DISTINCT left_of/right_of
            # projector, avoiding the svalue_of collision when a handler reads both children
            # of the SAME node (e.g. `_handle_map_get_expr`'s `node.dict` and `node.key`).
            if attr in _EMIT_IR_NODE_ATTRS:
                return f"({_EMIT_IR_NODE_ATTRS[attr]} {_os})"
            return f"(svalue_of {_os})"
        # CARRIER-FIELD PROJECTION (L13): `<optional-union local>.<field>` reads the
        # carrier record's field directly, instead of the opaque int-hash `get_<attr>`
        # (which is both ill-typed against a record carrier and value-blind).
        if (isinstance(obj_ir, dict) and obj_ir.get("type") == "Var"
                and obj_ir.get("name") in getattr(self, "_optional_union_locals", set())):
            _fp = self._union_local_field_projection(obj_ir["name"], attr)
            if _fp is not None:
                return _fp
        obj_str = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
        # cleared-array.md S2: in a SPEC/logic context (a contract or a
        # projection-comprehension content law), the abstract getter must be a
        # pure `val function` so it is usable in the `ensures` AND denotes ONE
        # deterministic value across every mention (the driver's `a[k].attr` and
        # the comprehension law reduce to the same `get_attr`). A body-only getter
        # stays the historical program `val` (byte-identical). Keep-longer dedup in
        # `_add_abstract_op` upgrades a same-file plain `val` in place → confined to
        # files that project a collapsed-int element in a contract (a NEW grammar
        # form) or via a projection comprehension. Sound: a field read is a
        # deterministic function of the (collapsed) element — a faithful refinement
        # that only removes spurious non-determinism, never adds a value claim.
        if getattr(self, "_in_spec", False):
            self._add_abstract_op(f"val function get_{attr} (x: int) : int")
        else:
            self._add_abstract_op(f"val get_{attr} (x: int) : int")
        return f"(get_{attr} {obj_str})"

    def _union_local_field_projection(self, name: str, attr: str) -> Optional[str]:
        """CARRIER-FIELD PROJECTION (L13 cursor-nest): `t.kind` where `t` is a mutable
        `Optional[<dataclass>]` local (`t = self.peek()`, `peek: -> Optional[Token]`)
        reads a FIELD OF THE CARRIER RECORD:
        `(match !t with Arm_0_0 _v -> _v.token_kind | _ -> <default> end)`.

        Without it the read falls through to the opaque int-hash getter
        `(get_kind <carrier projection>)`, whose `x: int` parameter rejects the now
        correctly-typed carrier — measured as `has type PyCSL_Program.token, but is
        expected to have type int`. That fallback was also VALUE-BLIND: `get_kind` is an
        uninterpreted `val`, so every comparison against it was a comparison of opaque
        int hashes rather than of the token's actual field.

        Fail-closed on every axis: single-Some-arm Optional unions only, a carrier that is
        a KNOWN record, and an `attr` that is genuinely one of that record's fields.
        Anything else returns None and keeps the historical path, so no read is silently
        re-pointed."""
        symtype = getattr(self, "_current_symbol_table", {}).get(name)
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        some_ctor = None
        some_pay = None
        for cn, c in vinfo.get("constructors", {}).items():
            if c.get("arity") == 1:
                if some_ctor is not None:
                    return None          # multi-Some union — out of scope
                some_ctor = cn
                _pay = c.get("payload") or []
                some_pay = _pay[0] if _pay else None
        if some_ctor is None or not some_pay:
            return None
        rec_name = next((rn for rn in getattr(self, "_record_types", {})
                         if self._record_types[rn].get("whyml_name") == some_pay
                         or rn == some_pay), None)
        if rec_name is None:
            return None
        rec = self._record_types[rec_name]
        if attr not in (rec.get("fields") or []):
            return None
        # `_field_label`'s first argument is the record's WHYML name (that is what the
        # ambiguous-field qualifier prefixes), NOT the Python class name. Passing
        # `rec_name` here emitted `_v._Tok_string` for `_Tok.string` while the DIRECT
        # read of the same field emitted `_tok_string` — an unbound symbol, and the last
        # thing standing between `Optional[<record>]` locals and a faithful lowering.
        label = self._field_label(rec.get("whyml_name") or rec_name, attr)
        ftype = (rec.get("field_types") or {}).get(attr, "int")
        default = {"str": '""', "string": '""', "real": "0.0",
                   "float": "0.0"}.get(ftype, "0")
        return (f"(match !{whyml_ident(name)} with {some_ctor} _v -> _v.{label} "
                f"| _ -> {default} end)")

    def _var_todict_alias(self, name: str, local_refs: Set[str],
                          subst: Optional[Dict[str, str]]) -> str:
        """If `name` is a `to_dict()` ALIAS (`_todict_aliases[name] == "self.types"`), rebuild the
        dotted attribute IR and re-emit it; else return `""` (no alias — a dotted alias emission is
        never empty). Extracted (07-03-refactor R1) as the ONE hard branch of `_handle_var_expr` —
        it carries the `_parts = alias.split(".")` seq-slice for-loop whose `variant {}` references a
        program `val` in a logic context (the R7 target), isolating it so the rest of var proves."""
        _al = getattr(self, "_todict_aliases", {}).get(name)
        if _al is None:
            return ""
        _parts = _al.split(".")
        _n: Dict[str, Any] = {"type": "Var", "name": _parts[0]}
        for _p in _parts[1:]:
            _n = {"type": "Attribute", "object": _n, "attr": _p}
        return self._expr_to_whyml(_n, local_refs, False, subst)

    def _union_local_read_projection(self, name: str) -> Optional[str]:
        """tool-feature-5 (giants read-projection): the carrier-projecting read of a
        mutable Optional-union local `name` (a `ref _union_*`): `(match !name with
        Arm_i_0 _v -> _v | _ -> <sentinel>)`, where the sentinel is the Some-arm carrier
        type's zero. None if `name` is not a single-Some-arm Optional union."""
        return self._union_read_projection(
            getattr(self, "_current_symbol_table", {}).get(name),
            f"!{whyml_ident(name)}")

    def _union_read_projection(self, symtype: Any, operand: str) -> Optional[str]:
        """The same carrier-projecting read, generalized from a NAMED local to an
        arbitrary already-lowered operand of a known `_union_*` type — so a
        union-returning sibling CALL used directly in a value position
        (`self.peek().kind`, the live `parse_atom` shape) projects its Some-arm carrier
        exactly as a union LOCAL does, instead of falling through to the opaque int-hash
        `get_kind` getter. Same single-Some-arm restriction and same sentinel table;
        `_union_local_read_projection` is now a thin wrapper over it, so the local and
        call cases can never drift apart."""
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        some_ctor = None
        some_pay = "int"
        for cn, c in vinfo.get("constructors", {}).items():
            if c.get("arity") == 1:
                if some_ctor is not None:
                    return None   # multi-Some union — out of scope
                some_ctor = cn
                _pay = c.get("payload") or []
                some_pay = _pay[0] if _pay else "int"
        if some_ctor is None:
            return None
        _sentinel = {"str": '""', "string": '""', "emit_ir": '(IrOther "")',
                     "real": "0.0", "float": "0.0"}.get(some_pay)
        if _sentinel is None:
            # RECORD CARRIER (L13 cursor-nest): an `Optional[<dataclass>]` local — the
            # `_Parser.peek() -> Optional[Token]` shape — carries a RECORD, not a scalar,
            # so the fallback `0` is ill-typed: measured as `has type int, but is expected
            # to have type PyCSL_Program.token` in the `| _ -> 0` arm. Use the record's own
            # default literal (the same type-appropriate-zero witness `_record_default_literal`
            # already builds for an `array <record>` `by` clause). The arm is UNREACHABLE
            # whenever the caller has guarded `x is not None`, so the witness only has to
            # type-check; it is never observed.
            _pay_rec = next((rn for rn in getattr(self, "_record_types", {})
                             if self._record_types[rn].get("whyml_name") == some_pay
                             or rn == some_pay), None)
            if _pay_rec is not None:
                _sentinel = self._record_default_literal(_pay_rec)
            else:
                _sentinel = "0"
        return (f"(match {operand} with {some_ctor} _v -> _v "
                f"| _ -> {_sentinel} end)")

    def _union_read_option_projection(self, symtype: Any, operand: str) -> Optional[str]:
        """The OPTION-TARGET twin of `_union_read_projection`: project a single-Some-arm
        `Optional`-union operand into a Why3 `option`, `(match <op> with Arm_i_0 _v -> Some _v
        | _ -> None end)`, instead of into the carrier with a sentinel.

        Needed wherever the TARGET is genuinely `option τ` rather than `τ` — a record field
        harvested from an `Optional[...]` declaration (`alias.asname` is `option string`).
        The sentinel projection is WRONG there twice over: it mistypes (`string` where
        `option string` is expected — the measured error), and it would silently model an
        ABSENT value as the empty string, which is exactly the None-reads-as-"" erasure the
        campaign has had to repair before."""
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        some_ctor = None
        for cn, c in vinfo.get("constructors", {}).items():
            if c.get("arity") == 1:
                if some_ctor is not None:
                    return None   # multi-Some union — out of scope
                some_ctor = cn
        if some_ctor is None:
            return None
        return f"(match {operand} with {some_ctor} _v -> Some _v | _ -> None end)"

    def _union_read_iropt_ir_projection(self, symtype: Any,
                                        operand: str) -> Optional[str]:
        """PYTHON-AST NODE CTOR FAMILY (increment 13): the `iropt_ir` twin of
        `_union_read_option_projection`. Projects a single-Some-arm `Optional`-union
        operand into the MONOMORPHIC option ADT the emit_ir theory uses for an optional
        child — `(match <op> with Arm_i_0 _v -> IrOSome _v | _ -> IrONone end)` — rather
        than into Why3's built-in `option` (which is the right target for a harvested
        RECORD field, and the wrong one for an ADT ctor slot). Returns None for a
        multi-Some union or a non-union operand, so the construction fails closed."""
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        some_ctor = None
        for cn, c in vinfo.get("constructors", {}).items():
            if c.get("arity") == 1:
                if some_ctor is not None:
                    return None   # multi-Some union — out of scope
                some_ctor = cn
        if some_ctor is None:
            return None
        return (f"(match {operand} with {some_ctor} _v -> IrOSome _v "
                f"| _ -> IrONone end)")

    def _union_read_iropt_str_projection(self, symtype: Any,
                                         operand: str) -> Optional[str]:
        """PYTHON-AST NODE CTOR FAMILY (increment 15): the `iropt_str` twin of
        `_union_read_iropt_ir_projection`. Projects a single-Some-arm `Optional[str]`-union
        operand into the MONOMORPHIC string-option ADT the emit_ir theory uses for an
        optional string child — `(match <op> with Arm_i_0 _v -> IrSSome _v | _ -> IrSNone
        end)`. Returns None for a multi-Some union or a non-union operand, so the
        construction fails closed."""
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        some_ctor = None
        for cn, c in vinfo.get("constructors", {}).items():
            if c.get("arity") == 1:
                if some_ctor is not None:
                    return None   # multi-Some union — out of scope
                some_ctor = cn
        if some_ctor is None:
            return None
        return (f"(match {operand} with {some_ctor} _v -> IrSSome _v "
                f"| _ -> IrSNone end)")

    def _handle_var_expr(self, node: "ExprIR", local_refs: Set[str],
                         subst: Optional[Dict[str, str]] = None) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature
        name = expr["name"]
        if subst and name in subst:
            name = subst[name]
        # todict-reflection-plan.md R1 (var-substitution): `d = node.to_dict()` binds
        # `d` as a full ALIAS of the typed node — so a bare `d` reference (e.g. passing
        # `d` to `self._expr_to_whyml(d)`, the emitter's recursive sub-expression
        # emission) lowers to the node itself. Complements the `d.get(key)` routing:
        # both the reflective reads AND the recursive re-emission see the typed node.
        _alias = self._var_todict_alias(name, local_refs, subst)
        if _alias:
            return _alias
        # body-gate gap-5: a scalar quantifier binder reads BARE (a bound logic var),
        # shadowing a same-named loop/local ref for the quantifier body's duration.
        if name in getattr(self, "_quant_scalar_binders", ()):
            return whyml_ident(name)
        if name in self._array_locals:
            return whyml_ident(name)
        if name in self._lambda_locals:
            return whyml_ident(name)
        if name in self._record_locals:
            return whyml_ident(name)
        if name in getattr(self, "_iropt_ir_local_vars", set()):
            # OPTIONAL-NODE LOCAL (relaunch #11): a VALUE read of an `iropt_ir` carrier
            # local where an `emit_ir` is required (`_subscript_item`'s `return lower`)
            # projects through the DEFINED total `iropt_val`. The two positions that must
            # NOT go through here are handled before ever reaching a Var read: an
            # `iropt_ir` PAYLOAD SLOT binds the carrier itself (`expressions.
            # _call_irnode_constructor`), and a carrier-to-carrier chained-assignment alias
            # copies it (`statements._handle_assign_stmt`) — so an absent optional child is
            # never turned into a present sentinel node.
            return f"(iropt_val !{whyml_ident(name)})"
        if name in getattr(self, "_optional_union_locals", set()):
            # tool-feature-5 (giants read-projection): a VALUE read of a mutable
            # Optional-union local `x` (a `ref _union_*`) projects the carrier of its
            # Some-arm (`match !x with Arm_i_0 _v -> _v | _ -> <sentinel>`) so `x` used as
            # its underlying τ (a string key, an emit_ir arg) type-checks. The `is None`
            # guard uses the RAW `!x` (handled in `_handle_binop`); the assignment TARGET
            # is not a read; so only value reads project. Sentinel picks the carrier's
            # zero (string "", emit_ir `IrOther ""`, real 0.0, else 0).
            _proj = self._union_local_read_projection(name)
            if _proj is not None:
                return _proj
        # K7 (pyval-chained `.get`, self-tcb-reduction Tier-5): a pyval chain local is
        # `let`-bound IMMUTABLE (single-assignment), so a read is the BARE name — never
        # the `!x` deref (which would type-clash: it is not a ref). Comes before the
        # `local_refs` deref so `return info` emits `info`, not `!info`. Gated -> inert.
        if name in getattr(self, "_pyval_locals", set()):
            return whyml_ident(name)
        if name in local_refs:
            return f"!{whyml_ident(name)}"
        # wrong-lowering-to-fix.md §WL-05b: an inner-mutated dict/set PARAM is a
        # `ref (map …)` (caller-visible mutation frame), so a bare read derefs it
        # (`!d`) — UNIFORMLY with the write site `d := map_update_some !d k v` and the
        # subscript read `Map.get !d k`. This is exactly the ref discipline the old
        # WL-05 lowering violated (the `d :=`/bare-`d` mix). Read-only params (not in
        # the set) keep the by-value bare read → byte-identical.
        if name in getattr(self, "_mutated_collection_params", set()):
            return f"!{whyml_ident(name)}"
        if name in self._current_params or name == "self":
            return whyml_ident(name) if name != "self" else name
        if name in self._shared_var_names:
            return f"!{whyml_ident(name)}"
        # module-constants-plan: a module-level int constant resolves to its literal,
        # in both body and contract (so e.g. `kinds[0] == K_IHDR` discharges). Comes
        # after the local/param/shared checks, so a same-named local correctly shadows
        # it. Replaces the opaque `val constant` for these names.
        if name in self._module_constants:
            _cv = self._module_constants[name]
            # 0442.md C5 (no-more-int): a string-literal constant folds to a real Why3
            # string literal, not an int hash; an int constant folds to its value.
            if isinstance(_cv, str):
                return self._whyml_string_literal(_cv)
            return f"({_cv})"
        # inline.md Phase 1: a bare reference to a module-level global object resolves to
        # its binding name (e.g. passing `acc` as an argument). After the local/param
        # checks so a same-named local shadows it.
        if name in getattr(self, "_module_global_classes", {}):
            return whyml_ident(name)
        # sum-types: a nullary `#@ datatype` constructor used as a value (`Red`).
        if name in self._constructors and self._constructors[name]["arity"] == 0:
            return name
        # 07-0647-spec S1.2: a bare class NAME used as a VALUE (e.g. the type argument
        # of `isinstance(x, C)`) must NOT reuse the record/variant TYPE name as its
        # opaque constant — `type c` and `val constant c` would collide (a kind/type
        # error). Give the value a distinct namespace.
        if name in self._record_types or name in getattr(self, "_variant_types", {}):
            csafe = f"_class_{whyml_ident(name)}"
            self._add_abstract_op(f"val constant {csafe} : int")
            return csafe
        safe = whyml_ident(name)
        self._add_abstract_op(f"val constant {safe} : int")
        return safe

    def _quant_binder_whyml(self, binder_type: str) -> str:
        """quantification.md: map a quantifier binder type to its WhyML sort.
        `None` ⇒ legacy `int` (emitted verbatim → byte-identical for every existing
        quantifier). Scalars map int→int / bool→bool / str→string / float→real; a
        declared `#@ datatype` or class name lowers to its Why3 type (lowercased,
        e.g. `Color`→`color`). Module 4 has already rejected an unresolved name."""
        if not binder_type:
            return "int"
        scalars = {"int": "int", "bool": "bool", "str": "string", "float": "real"}
        # 07-1311 Q4: collection-typed binders lower to their faithful WhyML sort.
        collections = {"list": "array int", "bytes": "array int",
                       "bytearray": "array int", "dict": "map int (option int)"}
        if binder_type in scalars:
            return scalars[binder_type]
        if binder_type in collections:
            return collections[binder_type]
        return whyml_ident(str(binder_type).lower())

    def _push_quant_binder(self, var: Optional[str], binder_type: Optional[str]):
        """scc3.md Phase A: register a quantifier-bound *record* var so `var.field`
        in the body lowers to the record field. No-op for scalar/datatype/None
        binders (only declared record classes have field access). Returns a restore
        token consumed by `_pop_quant_binder` (nesting/shadowing-safe)."""
        # 07-1311 Q4: a `dict`-typed binder is registered in `_dict_locals` (push/pop)
        # so `m[k]` in the body lowers to `Map.get m k`, not the abstract int subscript.
        if var and binder_type == "dict":
            dl = self._dict_locals
            had_d = var in dl
            dl.add(var)
            return ("dict", had_d)
        if not var or binder_type not in getattr(self, "_record_types", {}):
            # body-gate gap-5: register a scalar/None-typed binder so `_handle_var_expr`
            # reads it BARE (a logic var), shadowing any same-named `local_refs` member
            # (a loop var) for the duration of the quantifier body. No-op when var is None.
            if var:
                sb = self._quant_scalar_binders
                had_s = var in sb
                sb.add(var)
                return ("scalar", had_s)
            return ("noop", None)
        had = var in self._quant_record_binders
        prev = self._quant_record_binders.get(var)
        self._quant_record_binders[var] = binder_type
        return (had, prev)

    def _pop_quant_binder(self, var: Optional[str], token) -> None:
        kind, prev = token
        if kind == "noop":
            return
        if kind == "scalar":
            if not prev:            # was not already a scalar binder (nesting/shadowing)
                self._quant_scalar_binders.discard(var)
            return
        if kind == "dict":
            if not prev:                      # was not previously a dict local
                self._dict_locals.discard(var)
            return
        if kind:
            self._quant_record_binders[var] = prev
        else:
            self._quant_record_binders.pop(var, None)

    def _field_label(self, record_lower: str, field: str) -> str:
        """WhyML label for a record field. Ambiguous names (shared by >1
        record, e.g. an inherited field) are qualified `<record>_<field>` to
        avoid Why3's global field-label collision; unique names stay bare."""
        base = whyml_ident(field)
        if field in getattr(self, "_ambiguous_fields", set()) and record_lower:
            return f"{whyml_ident(record_lower)}_{base}"
        return base

    def _handle_field_get_expr(self, node: "ExprIR", invariant_ctx: bool) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature
        if invariant_ctx:
            return self._field_label(self._emit_record_ctx, expr['field'])
        obj = expr['object']
        field = expr['field']
        # self-tcb-reduction FunctionEmissionMixin WRITER class (`_build_param_list`):
        # the opaque-int self-field READS this signature builder makes — the symbol table
        # and the three source-ordered param sequences — are typed collections, NOT the
        # int-erased `getattr_functionemissionmixin self <hash>`. A Why3 `map` has no
        # iterable key-set and the body ITERATES these fields (`for arg in
        # self._formal_params`, the `{v for v in symbol_table …}` comprehension), so the
        # faithful model of what the method OBSERVES is the `seq string` of the keys/
        # elements. Each an uninterpreted `val <field>_of (self): seq string` (sound
        # over-approx, real structural descent). `_current_self_type` reads back the
        # string it wrote (effect-free write cap) as a `string`. Per-method scoped ->
        # byte-inert for the corpus and every other mirror.
        if obj == "self" and self._emitting_build_param_list():
            _bst = self._current_self_type or "functionemissionmixin"
            if field == "_current_symbol_table":
                self._add_abstract_op(
                    f"val current_symbol_table_of (self: {_bst}) : seq string")
                return "(current_symbol_table_of self)"
            if field == "_array2d_params":
                self._add_abstract_op(
                    f"val array2d_params_of (self: {_bst}) : seq string")
                return "(array2d_params_of self)"
            if field == "_current_array1d_params":
                self._add_abstract_op(
                    f"val current_array1d_params_of (self: {_bst}) : seq string")
                return "(current_array1d_params_of self)"
            if field == "_formal_params":
                self._add_abstract_op(
                    f"val formal_params_of (self: {_bst}) : seq string")
                return "(formal_params_of self)"
            if field == "_current_self_type":
                self._add_abstract_op(
                    f"val current_self_type_of (self: {_bst}) : string")
                return "(current_self_type_of self)"
        # Class-body integer constant referenced as `self.CONST` → its literal.
        self_type = self._current_self_type
        if (obj == "self" and self_type
                and field in self._class_constants.get(self_type, {})):
            return f"({self._class_constants[self_type][field]})"
        if field in self._all_record_fields:
            return f"{obj}.{self._field_label(self_type, field)}"
        hash_field = stable_hash(field)
        self_type = self._current_self_type
        if obj == "self" and self_type:
            name = f"getattr_{self_type}"
            self._add_abstract_op(f"val {name} (x: {self_type}) (f: int) : int")
        else:
            name = "getattr_2"
            self._add_abstract_op(f"val {name} (x: int) (f: int) : int")
            obj = self._coerce_to_int(obj)
        return f"({name} {obj} {hash_field})"

    def _fstring_str_part(self, pp: "ExprIR", local_refs: Set[str],
                          invariant_ctx: bool, subst: Dict[str, str]) -> str:
        """One segment of a MIXED (str/int) f-string in a @mutable_state class: a string
        segment passes through; an int/opaque segment is `int_to_string`-wrapped. Hoisted
        (07-03-refactor R2) from the `_sp` nested closure in `_handle_fstring_expr` so the
        segment logic types identically under proof mode and `--no-proof`."""
        w = self._expr_to_whyml(pp, local_refs, invariant_ctx, subst)
        if self._is_string_expr(pp):
            return w
        # `_compute_return_type` PATH(b): an `hval` interpolation (`f"int{bounded_int}"`,
        # `bounded_int = func.get("bounded_int")`) projects its int carrier via `hint_of`
        # before `int_to_string` (which is int-typed). Descends the real hval (non-vacuous).
        if self._expr_is_pyval(pp):
            return f"(int_to_string (hint_of {w}))"
        return f"(int_to_string {self._coerce_to_int(w)})"

    def _handle_fstring_expr(self, node: "ExprIR", local_refs: Set[str],
                              invariant_ctx: bool, subst: Dict[str, str]) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature; deep body stays dict-based
        parts = expr.get("parts", [])
        if not parts:
            return "0"
        # b14 B2: an f-string whose EVERY segment is string-typed (literal text and
        # `str`-typed interpolations) lowers to a faithful Why3 `string` concat chain
        # — the same `str_concat_op`/`concat` bridge as `s + t` (strings-plan Stage 2)
        # — instead of collapsing each segment to an int hash. A mixed f-string (any
        # int/opaque interpolation) keeps the legacy int-hash model below, so the
        # corpus that interpolates non-string values stays byte-identical.
        if all(self._is_string_expr(p) for p in parts):
            acc = self._expr_to_whyml(parts[0], local_refs, invariant_ctx, subst)
            # 07-03-refactor R2 (finish): a `for` over `parts[1:]` (array-emit_ir slice, R7) gets the
            # auto index-bound invariant so `parts[i]` discharges -- unlike the manual
            # `while i_part < n_parts` (bound in a local, no `Array.length` relation).
            for part in parts[1:]:
                p = self._expr_to_whyml(part, local_refs, invariant_ctx, subst)
                if self._in_spec:
                    acc = f"(concat {acc} {p})"
                else:
                    self._add_abstract_op(
                        "val str_concat_op (a: string) (b: string) : string\n"
                        "    ensures { result = (concat a b) }\n"
                        "    ensures { String.length result = String.length a + String.length b }")
                    acc = f"(str_concat_op {acc} {p})"
            return acc
        # todict-reflection-plan.md R3: in a @mutable_state class (the emitter model),
        # a MIXED str/int f-string (e.g. a gensym `f"__x_{n}"`) is still a STRING — the
        # int segments convert via `int_to_string`. So an emitter local bound to it types
        # as `string`. Gated on @mutable_state → byte-identical for every other f-string.
        if (not self._in_spec and (getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                or self._emitting_compute_return_type()
                or self._emitting_build_param_list())):
            self._add_abstract_op("val int_to_string (n: int) : string")
            self._add_abstract_op(
                "val str_concat_op (a: string) (b: string) : string\n"
                "    ensures { result = (concat a b) }\n"
                "    ensures { String.length result = String.length a + String.length b }")

            acc = self._fstring_str_part(parts[0], local_refs, invariant_ctx, subst)
            for pp in parts[1:]:
                acc = f"(str_concat_op {acc} {self._fstring_str_part(pp, local_refs, invariant_ctx, subst)})"
            return acc
        acc = self._coerce_str_arg(self._expr_to_whyml(parts[0], local_refs, invariant_ctx, subst))
        for part in parts[1:]:
            p = self._coerce_str_arg(self._expr_to_whyml(part, local_refs, invariant_ctx, subst))
            self._add_abstract_op("val str_concat (x: int) (y: int) : int")
            acc = f"(str_concat {acc} {p})"
        return acc

    def _handle_unaryop_expr(
        self,
        node: "UnaryOpExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. `node` is a UnaryOpExpr (op: str, expr: ExprIR).
        e = self._expr_to_whyml(node.expr, local_refs, invariant_ctx, subst)
        op = op_translate(node.op)
        if op == "+":
            return e
        if op == "~":
            # 0442.md C4: Python bitwise NOT on the int model is the two's-complement
            # identity `~x == -x - 1` (genuine int op, not a type-class leak).
            return f"((- {e}) - 1)"
        if op == "not":
            e = self._to_bool(e, node.expr.to_dict())
        return f"({op} {e})"

    def _handle_old_expr(
        self,
        node: "OldExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. `node` is an OldExpr (expr: ExprIR).
        inner = node.expr
        if not self._value_semantic and inner.kind == "Subscript":
            d = inner.to_dict()
            value = self._expr_to_whyml(d["value"], local_refs, invariant_ctx, subst)
            index = self._expr_to_whyml(d["index"], local_refs, invariant_ctx, subst)
            return f"(Map.get (old !{self._heap_var}) ({value} + {index}))"
        e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
        return f"(old {e})"

    def _handle_at_expr(
        self,
        node: "AtExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. `node` is an AtExpr (expr: ExprIR, label: str).
        label = node.label
        inner = node.expr
        if label == "PRE":
            e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
            return f"(old {e})"
        if inner.kind == "Subscript" and not self._value_semantic:
            d = inner.to_dict()
            value = self._expr_to_whyml(d["value"], local_refs, invariant_ctx, subst)
            index = self._expr_to_whyml(d["index"], local_refs, invariant_ctx, subst)
            return f"(Map.get ({self._heap_var} at {label}) ({value} + {index}))"
        e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
        return f"({e} at {label})"

    def _cf5_arr(self, d: "ExprIR") -> bool:
        """True if an IfExp arm `d` is a STRING-seq value (`.split(...)`, a list/comp literal,
        or a str-seq/str-array Var) — so a `<seq> if c else <seq>` IfExp emits each arm seq-ified
        rather than int-coerced. Hoisted (07-03-refactor R2) from the nested closure in
        `_handle_ifexpr_expr` so the arm predicate types consistently under proof mode."""
        if not isinstance(d, dict):
            return False
        _tt = d.get("type")
        if (_tt == "Call" and isinstance(d.get("func"), str)
                and d["func"].endswith(".split")):
            return True
        if _tt in ("ArrayLit", "ListLit", "ListComp"):
            return True
        if _tt == "Var":
            return (getattr(self, "_seq_value_types", {}).get(d.get("name")) == "string"
                    or getattr(self, "_array_elem_types", {}).get(d.get("name")) == "string")
        return False

    #@ requires_method _seq_operand: (self, val_ir: ExprIR, local_refs: set) -> str
    def _ifexpr_seq_arm(self, test: str, _bd: "ExprIR", _od: "ExprIR",
                        local_refs: Set[str]) -> str:
        """CF5: a ternary whose BOTH arms are `seq string` name-lists (`exc.split("|") if … else
        [exc]`) — emit each arm seq-ified (`_seq_operand`). Extracted (07-03-refactor R2/R1-pattern)
        as the ONE branch of `_handle_ifexpr_expr` that stays trusted (its `_seq_operand` result +
        `local_refs or set()` map-or don't yet lower cleanly), isolating it so the rest converts."""
        # 07-03-refactor: `_ifexpr_seq_arm` is only reached from the @mutable_state seq-arm where
        # `local_refs` is always a present Set, so `or set()` is a no-op (avoids the map-or lowering).
        return (f"(if {test} then {self._seq_operand(_bd, local_refs)} "
                f"else {self._seq_operand(_od, local_refs)})")

    def _handle_ifexpr_expr(
        self,
        node: "IfExprExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. IfExprExpr (test, body, orelse: ExprIR).
        test = self._expr_to_whyml(node.test, local_refs, invariant_ctx, subst)
        test = self._to_bool(test, node.test.to_dict())
        # 07-03-refactor R2: split the tuple-unpack into two assignments so each arm types as
        # emit_ir (via the `.to_dict()` recognizer) instead of the int tuple-unpack target.
        _bd = node.body.to_dict()
        _od = node.orelse.to_dict()
        body = self._expr_to_whyml(node.body, local_refs, invariant_ctx, subst)
        orelse = self._expr_to_whyml(node.orelse, local_refs, invariant_ctx, subst)
        # OPTION-PARAM GUARDED PROJECTION (relaunch #8): `start if start is not None else
        # self.cur()` over an `Optional[<record>]` PARAM. The ternary IS a Why3 `match` on
        # the option — `match start with Some _v -> _v | None -> <else> end` — which is
        # EXACTLY the source's meaning, TOTAL, and needs no default: the `None` arm is the
        # else-branch the source already supplies. Without it the true arm emits the bare
        # `start` (an `option _tok` where a `_tok` is wanted) and the assignment fails
        # L3-tc. FAIL-CLOSED: the test must be exactly `<p> != None` (Module5's spelling of
        # `is not None`) on the SAME param the true arm reads bare, and `<p>` must be a
        # registered `option <record>` param.
        _orpc = getattr(self, "_option_record_param_classes", {}) or {}
        _tst = node.test.to_dict()
        if (_bd.get("type") == "Var" and _bd.get("name") in _orpc
                and _tst.get("type") == "BinOp" and _tst.get("op") == "!="
                and isinstance(_tst.get("left"), dict)
                and _tst["left"].get("type") == "Var"
                and _tst["left"].get("name") == _bd.get("name")
                and isinstance(_tst.get("right"), dict)
                and _tst["right"].get("type") == "None"):
            return (f"(match {whyml_ident(str(_bd['name']))} with "
                    f"Some _v -> _v | None -> {orelse} end)")
        # i-feel-good.md I-A/I-B: a ternary is a STRING expression when at least one arm is
        # string-typed and the other is string-or-`None` — emit the string arms directly (a
        # bare `""`/`"lit"` stays a WhyML string, a `None` arm → "" the absent sentinel), so
        # `arr.get("name","") if … else ""` and `d.get(k) if k else None` type-check as
        # string. @mutable_state-gated → the corpus int model is byte-identical.
        _ms = (getattr(self, "_current_self_type", None)
               in getattr(self, "_mutable_state_classes", set()))
        # faithful-string-ternary (self-tcb-reduction): a `<str> if c else <str>` ternary in
        # a `-> str` function (`_func_return_type == "string"`) is ALSO a string expression
        # even outside a @mutable_state class — e.g. `BoolLit.pp`'s `"true" if self.value
        # else "false"`. Without this the string-literal arms fall to `_coerce_to_int` and
        # int-hash (`416353405`/`124643047`), a `string`-vs-`int` type clash at the return
        # slot. Keyed on the SAME declared-string signal that lowers the return slot to
        # `string`, so a string arm is well-typed exactly where it fires; corpus-byte-inert
        # (no non-@mutable_state `-> str` corpus function currently returns such a ternary).
        # Lever-7: also a string context when the enclosing function returns an
        # `Optional[str]`/`Union[…, str]` (`_func_ret_union_some_str()`), so the ternary's
        # literal `""` arm emits a real WhyML string (not the int-hash) before it is injected
        # into the variant's string arm at the return site. Fail-closed → normal ternaries
        # (non-union return) are byte-identical.
        _str_ctx = (_ms or (getattr(self, "_func_return_type", None) == "string")
                    or self._func_ret_union_some_str()
                    or self._emitting_compute_return_type()
                    or self._emitting_build_param_list())
        _b_str = self._is_string_expr(_bd)
        _o_str = self._is_string_expr(_od)
        _b_none = _bd.get("type") == "None"
        _o_none = _od.get("type") == "None"
        if _str_ctx and (_b_str or _o_str) and (_b_str or _b_none) and (_o_str or _o_none):
            if _b_none: body = '""'
            if _o_none: orelse = '""'
            return f"(if {test} then {body} else {orelse})"
        # item34.md CF1: the emit_ir analogue — `stmt.value.to_dict() if stmt.value is not
        # None else None` (an `Optional[ExprIR]` ternary) is an emit_ir expression; a `None`
        # arm → `(IrOther "")` (the emit_ir absent sentinel). @mutable_state.
        _b_ir = self._is_emit_ir_expr(_bd)
        _o_ir = self._is_emit_ir_expr(_od)
        if _ms and (_b_ir or _o_ir) and (_b_ir or _b_none) and (_o_ir or _o_none):
            if _b_none: body = '(IrOther "")'
            if _o_none: orelse = '(IrOther "")'
            return f"(if {test} then {body} else {orelse})"
        # item34.md CF5: a ternary whose BOTH arms are `seq string` name-lists (`exc.split("|")
        # if "|" in exc else [exc]`) — emit each arm seq-ified (`_seq_operand`), no int
        # coercion. @mutable_state.
        if _ms and self._cf5_arr(_bd) and self._cf5_arr(_od):
            return self._ifexpr_seq_arm(test, _bd, _od, local_refs)
        # self-tcb-reduction (union/match cluster): a ternary whose BOTH arms are mutable
        # array-local Vars (`true_branch_stmts = body if c else orelse`, `body`/`orelse`
        # the `array int` `stmts_of`/`orelse_stmts_of` reads) would ALIAS the two distinct
        # array regions into the result — Why3 forbids `if c then !a else !b` merging them.
        # Emit a fresh `Array.copy` of each arm so the result is a NEW region (read-only
        # downstream: `bool(...)` length + `ends_with_return(...)`). @mutable_state + both-
        # arm-array gated -> corpus/other-mirror byte-inert.
        def _is_arr_var(_d: Any) -> bool:
            return (isinstance(_d, dict) and _d.get("type") == "Var"
                    and (_d.get("name") in getattr(self, "_inline_array_temps", set())
                         or _d.get("name") in getattr(self, "_array_elem_types", {})))
        if _ms and _is_arr_var(_bd) and _is_arr_var(_od):
            return f"(if {test} then (Array.copy {body}) else (Array.copy {orelse}))"
        body = self._coerce_to_int(body)
        orelse = self._coerce_to_int(orelse)
        return f"(if {test} then {body} else {orelse})"

    def _handle_named_expr_expr(
        self,
        node: "NamedExprExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. NamedExprExpr (target: str, value: ExprIR).
        target = whyml_ident(node.target)
        v = self._expr_to_whyml(node.value, local_refs, invariant_ctx, subst)
        if target in local_refs:
            return f"(begin {target} := {v}; !{target} end)"
        local_refs.add(target)
        return f"(let {target} = ref {v} in !{target})"

    #@ requires_method _field_type_of: (self, attr_ir: ExprIR) -> str
    def _slice_array_or_opaque(self, node: "ExprIR", arr: str, sl: "ExprIR",
                               local_refs: Set[str], invariant_ctx: bool,
                               subst: Optional[Dict[str, str]]) -> str:
        """The array-source / opaque tail of `_handle_slice_access_expr`: `Array.sub` for a known
        array source (`_field_type_of(val) in list/tuple/…`), else the opaque `array_slice`.
        Extracted (07-03-refactor R4) as the trusted leaf — it calls `_field_type_of` (types.py),
        whose cross-file stub defaults to int, so the whole tail stays trusted while the seq/string
        slice cases in `_handle_slice_access_expr` convert."""
        lo = self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst) if sl.get("lower") else "0"
        hi = self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst) if sl.get("upper") else f"(Array.length {arr})"
        val = node.value.to_dict()
        is_array_src = False
        if val.get("type") in ("Attribute", "FieldGet"):
            if self._field_type_of(val) in ("list", "tuple", "bytes", "bytearray"):
                is_array_src = True
        elif val.get("type") == "Var":
            vn = val.get("name", "")
            if (vn in getattr(self, "_array_locals", set()) or
                    vn in getattr(self, "_current_array1d_params", set()) or
                    self._current_symbol_table.get(vn) == "list"
                    or vn in getattr(self, "_array_elem_types", {})):
                is_array_src = True
        if is_array_src:
            return f"(Array.sub {arr} ({lo}) (({hi}) - ({lo})))"
        self._add_abstract_op("val array_slice (a: array int) (lo: int) (hi: int) : array int")
        # 07-03-refactor: store the coerced arg in a fresh local (not a reassigned param) so `arr`
        # stays an immutable string param — else the `{arr}` interpolations lower to `!arr` (ref).
        _carr = self._array_coerce_arg(arr)
        return f"(array_slice {_carr} {lo} {hi})"

    def _handle_slice_access_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        arr = self._expr_to_whyml(node.value, local_refs, invariant_ctx, subst)
        sl = node.slice.to_dict()
        # seq-model-pivot.md SQ3: a slice of a seq local (`body_stmts[:-1]`) is a seq
        # sub-sequence (`seq_sub`) — a pure immutable value, NO `array_slice`/region. Content
        # opaque; the length law is conditional (sound). @mutable_state (via _seq_locals).
        _bv = node.value.to_dict()
        if (_bv.get("type") == "Var" and _bv.get("name") in getattr(self, "_seq_locals", set())):
            _slo = (self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst)
                    if sl.get("lower") else "0")
            _shi = (self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst)
                    if sl.get("upper") else f"(Seq.length {arr})")
            self._add_abstract_op(
                "val seq_sub (s: seq 'a) (lo hi: int) : seq 'a\n"
                "    ensures { 0 <= lo <= hi <= Seq.length s -> Seq.length result = hi - lo }")
            return f"(seq_sub {arr} {_slo} {_shi})"
        # strings-plan Stage 2: `s[a:b]` on a string is `String.substring s a (b-a)`. Spec
        # uses the logic symbol; body bridges through `str_sub_op` (and `str_length_op` for an
        # omitted upper bound), since `String.substring`/`String.length` aren't program values.
        if self._is_string_expr(node.value.to_dict()):
            slo = self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst) if sl.get("lower") else "0"
            if sl.get("upper"):
                shi = self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst)
            elif self._in_spec:
                shi = f"(String.length {arr})"
            else:
                self._add_abstract_op("val str_length_op (s: string) : int\n"
                                      "    ensures { result = (String.length s) }")
                shi = f"(str_length_op {arr})"
            slen = f"(({shi}) - ({slo}))"
            if self._in_spec:
                return f"(String.substring {arr} {slo} {slen})"
            # The length lemma is baked into the bridge's `ensures`: deriving
            # `String.length (substring s lo len) = len` from the substring theory makes the
            # SMT backend OOM for general (non-literal) args, but the fact is sound (cf. the
            # Stage-0 literal probe), so we supply it directly under its bounds guard.
            self._add_abstract_op(
                "val str_sub_op (s: string) (lo len: int) : string\n"
                "    ensures { result = (String.substring s lo len) }\n"
                "    ensures { (0 <= lo /\\ 0 <= len /\\ lo + len <= String.length s)"
                " -> String.length result = len }")
            return f"(str_sub_op {arr} {slo} {slen})"
        return self._slice_array_or_opaque(node, arr, sl, local_refs, invariant_ctx, subst)

    def _handle_arraylen_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self._value_semantic:
            var = node.var
            # 07-1705-rev4 P3/P5: `\length(a)` of a seq-modelled list — BODY context only.
            # In a pre/post-condition a seq-promoted *param* names the original `array int`
            # entry value (the body seq shadow is out of scope), so fall through to
            # `Array.length` there.
            # ...or inside a LOOP invariant/variant, where the body's local scope IS live
            # (`_in_loop_spec`, set by `_handle_for_stmt`/`_handle_while_stmt`). Excluding
            # loop clauses emitted `Array.length` on a `seq` — a LOUD type error, which is
            # exactly what blocked writing a termination variant for a `for`-over-list
            # conversion whose accumulator is seq-promoted.
            if var in getattr(self, "_seq_locals", set()) and (
                    not self._in_spec or getattr(self, "_in_loop_spec", False)):
                deref = "!" if var in local_refs else ""
                return f"(Seq.length {deref}{whyml_ident(var)})"
            if var == "\\result":
                return f"(Array.length {getattr(self, '_result_alias', None) or 'result'})"
            if var.startswith("self."):
                field = var[len("self."):]
                # Mirror `_handle_field_get_expr`: in a type/class invariant
                # the record fields are bare; in a method contract `self`
                # is an in-scope parameter.
                ref = field if invariant_ctx else f"self.{field}"
                return f"(Array.length {ref})"
            # An array LOCAL (`out = [0]*n`) is bound as a plain `Array.make` mutable
            # array, NOT a ref — so it is referenced BARE even when it also appears in
            # `local_refs` (mirrors `_handle_var_expr`'s `_array_locals` rule). Without
            # this guard `\length(out)` in a loop invariant emitted `Array.length !out`,
            # a deref of a non-ref → typecheck failure (`len(out)` and subscript `out[i]`
            # were already correct via `_handle_var_expr`; only this `\length` path wasn't).
            deref = ("!" if (var in local_refs
                             and var not in getattr(self, "_array_locals", set()))
                     else "")
            return f"(Array.length {deref}{var})"
        return f"{node.var}_len"

    def _module_binding_names(self) -> Set[str]:
        """07-1839 P2: statically-declared module-level names — the sound lower bound for
        `\\in_globals` (functions, module-global object instances, module constants, and
        classes). The world is OPEN beyond this (import/exec), so a name's absence here is
        *unknown*, never decided-false."""
        ir = getattr(self, "ir", {})
        names: Set[str] = {f.get("name") for f in ir.get("functions", [])}
        names |= set(getattr(self, "_module_global_classes", {}))
        names |= set(getattr(self, "_module_constants", {}))
        names |= {c.get("name") for c in ir.get("classes", []) if isinstance(c, dict)}
        names.discard(None)
        return names

    def _handle_in_globals_expr(self, node: "ExprIR", local_refs: Set[str],
                                invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> str:
        """07-1839 P2: `\\in_globals(name)` — three-valued, true-only lower bound.
        decided-true (→ `true`) for a declared module binding; UNKNOWN otherwise → an
        uninterpreted bool (`in_globals_op`), so it is neither provably true nor false
        (open world: import/exec may inject the name). The unsound decided-false direction
        is never emitted."""
        name = node.name
        if name in self._module_binding_names():
            return "true"
        self._add_abstract_op("val function in_globals_op (n: int) : bool")
        return f"(in_globals_op {sum(ord(c) for c in name)})"

    def _handle_in_scope_expr(self, node: "ExprIR", local_refs: Set[str],
                              invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> str:
        """07-1839 P3: `\\in_scope(name)` — three-valued via definite-assignment.
        decided-true (→ `true`) if `name` is assigned on all paths (param or top-level
        assignment before any branch/return); decided-false (→ `false`) if `name` is
        neither a param nor assigned anywhere; UNKNOWN (conditionally assigned) → an
        uninterpreted bool. A dynamic exec havocs the binding set, so the decided-false
        direction is withheld afterwards (decision C)."""
        name = node.name
        if name in getattr(self, "_scope_must", set()):
            return "true"
        if (not getattr(self, "_scope_dyn_exec", False)
                and name not in getattr(self, "_scope_all", set())
                and name not in getattr(self, "_scope_params", set())):
            return "false"
        self._add_abstract_op("val function in_scope_op (n: int) : bool")
        return f"(in_scope_op {sum(ord(c) for c in name)})"

    def _handle_valid_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        length = self._expr_to_whyml(node.length, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"({length} >= 0 && {length} <= Array.length {base})"
        return f"(valid !{self._heap_var} {base} {length})"

    def _handle_separated_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self._value_semantic:
            return "true"
        b1 = node.base1
        l1 = self._expr_to_whyml(node.len1, local_refs, invariant_ctx, subst)
        b2 = node.base2
        l2 = self._expr_to_whyml(node.len2, local_refs, invariant_ctx, subst)
        return f"(separated {b1} {l1} {b2} {l2})"

    def _handle_length2d_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        rows = self._expr_to_whyml(node.rows, local_refs, invariant_ctx, subst)
        cols = self._expr_to_whyml(node.cols, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"({base}.rows = {rows} && {base}.columns = {cols})"
        return "true"

    def _handle_valid2d_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        row = self._expr_to_whyml(node.row, local_refs, invariant_ctx, subst)
        col = self._expr_to_whyml(node.col, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"(valid_index {base} {row} {col})"
        return "true"

    # ---- cleared-array.md S1–S4: content-faithful comprehensions ----------
    def _comp_elt_pure_int(self, elt: Any, free: Set[str],
                           getters: Optional[Set[str]] = None,
                           user_funcs: Optional[Set[str]] = None) -> bool:
        """True iff `elt` is a PURE, total `int`-valued expression the emitter
        lowers to a logic term built only from:
          * variables (collected into `free`),
          * integer literals,
          * the total arithmetic operators `+ - *` (identity / arithmetic),
          * cleared-array.md S2 — FIELD PROJECTIONS `e.attr` on a liftable `e`
            (the attr NAMES are collected into `getters`), and
          * cleared-array item 1 — CALLS `g(e, …)` to a module function already
            emitted as a pure `let function` (a logic symbol), with liftable int
            args (the callee names are collected into `user_funcs`, gating the
            deferred late-emission of the content-law `val`).

        Division / modulo are excluded (partiality — ZeroDivisionError semantics
        must not leak into a logic `ensures`); calls / subscripts / comparisons /
        booleans are excluded (not guaranteed pure-int logic terms).

        Projection soundness: in the int-collapsed list model a source element is
        an `int`, so `e.attr` lowers to the abstract getter `get_attr : int → int`
        (`_handle_attribute_expr`). That getter is a DETERMINISTIC read of the
        (collapsed) element, so `result[i] = get_attr(src[i])` is a faithful
        re-expression of `a[i].attr` — the SAME `get_attr` a driver's own
        `\result[i] == a[i].attr` lowers to. The lift only holds once every such
        getter is emitted as a pure `val function` (done by `_content_comp` via
        the collected `getters` set), so the two mentions denote one value.
        Conservative: any unrecognised node ⇒ not liftable."""
        if not isinstance(elt, dict):
            return False
        t = elt.get("type")
        if t == "Var":
            free.add(elt.get("name", ""))
            return True
        if t == "Number":
            return isinstance(elt.get("value"), int)
        if t == "BinOp":
            if elt.get("op") not in ("+", "-", "*"):
                return False
            return (self._comp_elt_pure_int(elt.get("left", {}), free, getters, user_funcs)
                    and self._comp_elt_pure_int(elt.get("right", {}), free, getters, user_funcs))
        if t == "UnaryOp":
            if elt.get("op") not in ("-", "+"):
                return False
            return self._comp_elt_pure_int(
                elt.get("operand", elt.get("value", {})), free, getters, user_funcs)
        if t == "Call":
            # cleared-array item 1: `g(args)` where `g` is a module function ALREADY
            # emitted as a pure `let function` (a logic symbol usable in `ensures`),
            # and every arg is itself a liftable pure-int term over the target. The
            # callee is a total function (`assigns \nothing`, non-diverging → `pure`)
            # so `result[i] = g(src[i])` is sound. Requires the `user_funcs`
            # accumulator (only `_content_comp` opts in) — else a bare call is not
            # liftable, keeping the whitelist byte-identical for other callers.
            if user_funcs is None:
                return False
            fn = elt.get("func")
            if not isinstance(fn, str) or "." in fn:
                return False
            if whyml_ident(fn) not in getattr(self, "_emitted_logic_funcs", set()):
                return False
            args = elt.get("args", []) or []
            # keyword/starred args are not plain positional terms → not liftable.
            if elt.get("keywords") or elt.get("kwargs") or elt.get("starargs"):
                return False
            for a in args:
                if not self._comp_elt_pure_int(a, free, getters, user_funcs):
                    return False
            user_funcs.add(whyml_ident(fn))
            return True
        if t in ("Attribute", "FieldGet"):
            # cleared-array.md S2 projection. The base must itself be a liftable
            # collapsed-int term (the loop target, or a projection/arithmetic over
            # it); the attr is an int-collapsed getter. Requires the `getters`
            # accumulator (only `_content_comp` passes it) — otherwise a bare
            # projection is NOT liftable (keeps the arithmetic-only whitelist
            # byte-identical for callers that don't opt in).
            if getters is None:
                return False
            attr = elt.get("attr") or elt.get("field")
            base = elt.get("object")
            if base is None or not isinstance(attr, str) or not attr:
                return False
            if not self._comp_elt_pure_int(base, free, getters, user_funcs):
                return False
            getters.add(attr)
            return True
        return False

    def _lift_target_seq_index(self, idx_ir: Any, target: str, row_expr: str,
                               capfree: Set[str]) -> Optional[str]:
        """nested-list §8/§9 EXTENSION (target-dependent comprehension index).
        Lift a comprehension index `f(x)` that DEPENDS on the loop target `x`
        (a `seq τ`) to a pure int logic term over `row_expr` (the per-index source
        read `src[i]`), or None if it does not soundly lift. The sound grammar:
          * integer literals,
          * `len(x)` (the target's length) → `Seq.length row_expr`,
          * captured int free-vars `c` (≠ target; collected into `capfree` → extra
            val params),
          * the total operators `+ - *` and unary `- +` over the above.
        Every leaf is total and pure; `Seq.length` is a Why3 stdlib logic symbol —
        so `result[i] = Seq.get (src[i]) (f(src[i]))` is a faithful re-expression
        of `x[f(x)]` (the SAME term the driver's `\\result[i] == a[i][f(a[i])]`
        lowers to). A `g(x)` call over the seq, a non-`len` seq operation, or a
        bare `x` used as an int index do NOT lift → None (kept opaque)."""
        if not isinstance(idx_ir, dict):
            return None
        t = idx_ir.get("type")
        if t == "Number":
            v = idx_ir.get("value")
            if not isinstance(v, int):
                return None
            return f"({v})" if v < 0 else str(v)
        if t == "Var":
            nm = idx_ir.get("name", "")
            if nm == target:
                return None            # a bare seq target is not an int index
            capfree.add(nm)
            return whyml_ident(nm)
        if t == "BinOp":
            if idx_ir.get("op") not in ("+", "-", "*"):
                return None
            _l = self._lift_target_seq_index(idx_ir.get("left", {}), target,
                                             row_expr, capfree)
            _r = self._lift_target_seq_index(idx_ir.get("right", {}), target,
                                             row_expr, capfree)
            if _l is None or _r is None:
                return None
            return f"({_l} {idx_ir.get('op')} {_r})"
        if t == "UnaryOp":
            if idx_ir.get("op") not in ("-", "+"):
                return None
            _o = self._lift_target_seq_index(
                idx_ir.get("operand", idx_ir.get("value", {})), target,
                row_expr, capfree)
            if _o is None:
                return None
            return f"(- {_o})" if idx_ir.get("op") == "-" else _o
        if t == "Call":
            # only `len(x)` where x IS the loop target lifts (→ Seq.length of the
            # per-index row). Any other call over the seq stays opaque.
            fn = idx_ir.get("func")
            _args = idx_ir.get("args", []) or []
            if (fn == "len" and len(_args) == 1
                    and isinstance(_args[0], dict)
                    and _args[0].get("type") == "Var"
                    and _args[0].get("name") == target):
                return f"(Seq.length {row_expr})"
            return None
        return None

    def _nested_subscript_comp(self, op_name, gen: Dict[str, Any], target: str,
                               elt: Any, src_ir: Any, local_refs: Set[str],
                               subst: Optional[Dict[str, str]],
                               invariant_ctx: bool) -> Optional[str]:
        """nested-list.md S4: content law for `[x[k] for x in a]` where `a` is a
        `List[<container>]` param (`array (seq τ)` / `array (map κ (option ν))`)
        and the element is a subscript `x[k]` of the loop target. Returns the
        abstract-val application, or None if the shape is not this projection
        (falls through to the generic / opaque path).

        The result is `array <inner>` where <inner> is the seq's element (or the
        dict value ν). The per-index content law
            result[i] = Seq.get (src[i]) k        (seq source)
            result[i] = match Map.get (src[i]) key with Some v -> v | None -> d end   (map source)
        re-expresses `a[i][k]` with the SAME inner read a driver's own
        `\result[i] == a[i][k]` lowers to (see `_handle_subscript` S3) — sound,
        no new axiom (definitional `ensures`; Seq/Map read laws are Why3 stdlib)."""
        if not (isinstance(src_ir, dict) and src_ir.get("type") == "Var"):
            return None
        _ne = getattr(self, "_list_nested_elem", {}).get(src_ir.get("name", ""))
        if _ne is None:
            return None
        # element must be exactly `x[k]` — a subscript OF the loop target.
        if not (isinstance(elt, dict) and elt.get("type") == "Subscript"):
            return None
        _ev = elt.get("value", {})
        if not (isinstance(_ev, dict) and _ev.get("type") == "Var"
                and _ev.get("name") == target):
            return None
        idx_ir = elt.get("index", {})
        # the index must NOT reference the loop target (it is a captured
        # constant/param `k` / a literal); a target-dependent index is out of
        # scope. For a seq source the index is a pure-int term (validated +
        # free-var-collected via `_comp_elt_pure_int`); for a map source it is a
        # String key literal (target-independent by construction).
        # captured index free-vars (`k`, `key`) become EXTRA parameters of the
        # abstract val (a module-level `val` cannot see the enclosing function's
        # params otherwise). Each maps to (whyml_name, whyml_type); the call site
        # passes the same vars. Restricted to vars whose lowering is a bare ident
        # (no `!`-deref) so the decl param name == the term in `idxw`.
        _extra: List[Tuple[str, str]] = []   # (name, whyml_type)
        binder = "_ci"
        # nested-list §8/§9 EXTENSION: a TARGET-DEPENDENT seq index `x[f(x)]` where
        # `f(x)` lifts to a pure int term over `len(x)` (`_lift_target_seq_index`);
        # None keeps the constant-index path below. The per-index row is `src[_ci]`.
        _tgt_seq_idx: Optional[str] = None
        if _ne.startswith("seq "):
            _idxfree = set()
            _const_ok = (self._comp_elt_pure_int(idx_ir, _idxfree)
                         and target not in _idxfree)
            if _const_ok:
                for _fv in sorted(_idxfree):
                    _fvw = self._expr_to_whyml({"type": "Var", "name": _fv},
                                               local_refs or set(), invariant_ctx, subst)
                    if _fvw != whyml_ident(_fv):
                        return None        # ref-deref / renamed → out of scope
                    _extra.append((_fvw, "int"))
            else:
                # target-dependent: lift `f(x)` over `len(x)` + captured int params.
                _capfree: Set[str] = set()
                _tgt_seq_idx = self._lift_target_seq_index(
                    idx_ir, target, f"(src[{binder}])", _capfree)
                if _tgt_seq_idx is None:
                    return None            # unliftable index → opaque
                for _fv in sorted(_capfree):
                    _fvw = self._expr_to_whyml({"type": "Var", "name": _fv},
                                               local_refs or set(), invariant_ctx, subst)
                    if _fvw != whyml_ident(_fv):
                        return None
                    _extra.append((_fvw, "int"))
        elif _ne.startswith("map "):
            if not (isinstance(idx_ir, dict) and idx_ir.get("type") in ("String", "Var")):
                return None
            if idx_ir.get("type") == "Var":
                if idx_ir.get("name") == target:
                    return None
                _kv = idx_ir.get("name", "")
                _kvw = self._expr_to_whyml({"type": "Var", "name": _kv},
                                           local_refs or set(), invariant_ctx, subst)
                if _kvw != whyml_ident(_kv):
                    return None
                _extra.append((_kvw, "string" if "map string" in _ne else "int"))
        srcw = self._expr_to_whyml(src_ir, local_refs or set(), invariant_ctx, subst)
        srca = self._array_coerce_arg(srcw)
        n = getattr(self, "_comp_content_counter", 0)
        self._comp_content_counter = n + 1
        op = f"list_content_comp_{n}"
        idxw = None
        if _tgt_seq_idx is None:
            # constant / captured index: lower it in spec context (a
            # target-dependent index is already lifted as `_tgt_seq_idx`).
            saved_in_spec = self._in_spec
            self._in_spec = True
            try:
                idxw = self._expr_to_whyml(idx_ir, local_refs or set(), True, subst)
            finally:
                self._in_spec = saved_in_spec
        if _ne.startswith("seq "):
            res_elem = _ne[len("seq "):]
            _sidx = _tgt_seq_idx if _tgt_seq_idx is not None else idxw
            read = f"(Seq.get (src[{binder}]) {_sidx})"
        elif _ne.startswith("map "):
            # ν = the option's inner type; the missing-key default is typed per ν.
            res_elem = (_ne.split("(option ", 1)[1].rsplit(")", 1)[0]
                        if "(option " in _ne else "int")
            _dflt = '""' if res_elem == "string" else "0"
            # κ=string passes the key through native; else int-coerce (spec context).
            _key = idxw if "map string" in _ne else self._coerce_to_int(idxw)
            read = (f"(match Map.get (src[{binder}]) {_key} "
                    f"with | Some v_ -> v_ | None -> {_dflt} end)")
        else:
            return None
        _pdecl = "".join(f" ({nm}: {ty})" for nm, ty in _extra)
        decl = (
            f"val {op} (src: array ({_ne})){_pdecl} : array ({res_elem})\n"
            f"    ensures {{ Array.length result = Array.length src }}\n"
            f"    ensures {{ forall {binder} : int. 0 <= {binder} < Array.length src ->\n"
            f"                result[{binder}] = {read} }}")
        self._add_abstract_op(decl)
        _cargs = "".join(f" {nm}" for nm, _ in _extra)
        return f"({op} {srca}{_cargs})"

    # variadic content-law comprehension (FABLE-sanctioned): the recursive IR dispatchers
    # whose call over the loop target is the recognized element shape. ONE shared
    # `emit_ir_disp__<disp>` `val function` per dispatcher (FABLE §6 condition 2) — the
    # method name after the last dot, leading underscore stripped, keyed here.
    _IR_DISPATCHERS = ("_csl_to_ir", "_py_expr_to_ir")

    def _disp_call_over_target(self, elt: Any, target: str) -> Optional[str]:
        """Return the dispatcher method name if `elt` is a bare recursive-dispatcher call
        `self.<disp>(<Var target>)` over the loop target (`<disp>` in `_IR_DISPATCHERS`),
        else None. The single argument must be exactly the loop target (an unmodified
        per-element map), so the emitted content law `nth i = <disp>(src[i])` is faithful."""
        if not (isinstance(elt, dict) and elt.get("type") == "Call"):
            return None
        fn = elt.get("func")
        if not isinstance(fn, str):
            return None
        disp = fn.rsplit(".", 1)[-1]
        if disp not in self._IR_DISPATCHERS:
            return None
        args = elt.get("args") or []
        if len(args) != 1:
            return None
        a0 = args[0]
        if not (isinstance(a0, dict) and a0.get("type") == "Var"
                and a0.get("name") == target):
            return None
        return disp

    def _record_of_receiver(self, obj: Any) -> Optional[Dict[str, Any]]:
        """The `_record_types` record dict for a receiver `Var` (self / module-global /
        record-var / record-param / imported-record-param), or None. Mirrors the class
        resolution in `_field_type_of`, but returns the whole record so callers can read
        `field_types` / `field_value_types`."""
        if not (isinstance(obj, dict) and obj.get("type") == "Var"):
            return None
        recv = obj.get("name")
        rts = getattr(self, "_record_types", {})
        wn = None
        if recv == "self":
            wn = self._current_self_type
        else:
            gcls = getattr(self, "_module_global_classes", {}).get(recv)
            if gcls in rts:
                return rts[gcls]
            rvcls = getattr(self, "_current_record_var_classes", {}).get(recv)
            if rvcls in rts:
                return rts[rvcls]
            wn = (getattr(self, "_record_param_classes", {}).get(recv)
                  or getattr(self, "_current_symbol_table", {}).get(recv))
        if not wn:
            return None
        if wn in rts:
            return rts[wn]
        for k, v in rts.items():
            if v.get("whyml_name") == wn or k.lower() == str(wn).lower():
                return v
        return None

    def _src_is_array_emit_ir(self, src_ir: Any) -> bool:
        """True iff the comprehension source `src_ir` lowers to an `array emit_ir`: a
        record field of type `list`/`tuple` with element value_type `emit_ir` (a
        `List[ExprIR]` field — `node.elts` on a MkTupleExpr / `expr.elts` on the harvested
        pure_ast Tuple), an emit_ir node-LIST attr (`.elts`/`.parts`/`.args`/`.captures`
        via `args_of`), or an `array emit_ir` local. This is the type-safety guard on the
        variadic op (the op takes `array emit_ir`); anything else falls through."""
        if not isinstance(src_ir, dict):
            return False
        t = src_ir.get("type")
        if t in ("Attribute", "FieldGet"):
            attr = src_ir.get("attr") or src_ir.get("field")
            obj = src_ir.get("object") or src_ir.get("value") or {}
            # emit_ir node-list attr → `(args_of <emit_ir>)` : `array emit_ir`
            if attr in ("elts", "parts", "args", "captures", "alternatives") and self._is_emit_ir_expr(obj):
                return True
            # record `List[ExprIR]` field → `array emit_ir`
            rt = self._record_of_receiver(obj)
            if rt is not None:
                if (rt.get("field_value_types", {}).get(attr) in ("emit_ir", "ExprIR")
                        and rt.get("field_types", {}).get(attr) in ("list", "tuple")):
                    return True
            return False
        if t == "Var":
            return getattr(self, "_array_elem_types", {}).get(src_ir.get("name")) == "emit_ir"
        return False

    def _variadic_content_comp(self, g: Dict[str, Any], target: str, elt: Any,
                               src_ir: Any, local_refs: Set[str], invariant_ctx: bool,
                               subst: Optional[Dict[str, str]]) -> Optional[str]:
        """variadic content-law comprehension (FABLE-sanctioned, `variadic-content-law-wall
        -response.md`): lower `[self.<disp>(t) for t in <array emit_ir>]` — the emitter's
        variadic-tuple body — to `(list_content_comp_N <src>)` : `irlist` carrying
        BOTH a length law AND a per-index content law over a SHARED, per-dispatcher
        `emit_ir_disp__<disp>` `val function`. Returns the op application, or None to fall
        through. @mutable_state-gated (the emitter model) → corpus byte-inert.

        The law pins map STRUCTURE — `nth i result` is a deterministic function
        (`emit_ir_disp__<disp>`) of `src[i]` — NOT dispatcher value-semantics; honest per
        FABLE §6 condition 3. The content law is NON-VACUOUS (strictly stronger than the
        length-only facade the reverted attempt used): a non-functional hostile (unequal
        outputs on equal source elements) is refuted for every interpretation of the fresh
        `val function` (FABLE §2/§5). BOTH conjuncts are ALWAYS emitted (FABLE §6 cond 1);
        the op NEVER degrades to length-only."""
        if getattr(self, "_current_self_type", None) not in getattr(
                self, "_mutable_state_classes", set()):
            return None
        if g.get("ifs"):
            return None
        disp = self._disp_call_over_target(elt, target)
        if disp is None:
            return None
        if not self._src_is_array_emit_ir(src_ir):
            return None
        srcw = self._expr_to_whyml(src_ir, local_refs or set(), invariant_ctx, subst)
        srca = self._array_coerce_arg(srcw)
        # FABLE §6 condition 2: ONE shared symbol per DISPATCHER, reused across every site
        # (dedup by name in `_add_abstract_op`). Restores the get_x-style cross-site
        # observability the projection precedent has.
        sym = "emit_ir_disp__" + disp.lstrip("_")
        self._add_abstract_op(f"val function {sym} (e: emit_ir) : emit_ir")
        n = getattr(self, "_comp_content_counter", 0)
        self._comp_content_counter = n + 1
        op = f"list_content_comp_{n}"
        # FABLE §6 condition 1: BOTH conjuncts (length + per-index content law), always.
        # The result carrier is the MONOMORPHIC `irlist` (IrMkTupleN's payload — NOT the
        # polymorphic `list emit_ir`, whose library axioms explode the emit_ir size-decrease
        # lemmas; see preamble.py `_emit_exprir_theory`). `irlen`/`irnth` are its length/nth.
        decl = (
            f"val {op} (src: array emit_ir) : irlist\n"
            f"    ensures {{ irlen result = Array.length src }}\n"
            f"    ensures {{ forall _ci : int. 0 <= _ci < Array.length src ->\n"
            f"                irnth _ci result = (let _celt = src[_ci] in {sym} _celt) }}")
        self._add_abstract_op(decl)
        return f"({op} {srca})"

    def _content_comp(self, node: "ExprIR", local_refs: Set[str],
                      invariant_ctx: bool,
                      subst: Optional[Dict[str, str]]) -> Optional[str]:
        """cleared-array.md S1–S4 + S2. Emit a CONTENT-faithful comprehension for
        a supported element shape, or return None to fall through to the opaque
        length-only path. Supported: ONE generator whose target is a plain name,
        an `array int` source (NOT a seq local — the seq comprehension path owns
        those), and an element that lowers to a pure-int logic term over the
        target ONLY — identity, `+ - *` arithmetic, or FIELD PROJECTIONS `x.attr`
        (and arithmetic over them). A filter (`if`) keeps ONLY the sound length
        bound."""
        # self-tcb-reduction WRITER class (`_build_param_list`): its `args = [v for v in
        # self._formal_params if v not in ghost_vars]` iterates a `seq string` source, not an
        # `array int` — leave it to the `seq string` list-comp path (`list_comp_refine_string`).
        if self._emitting_build_param_list():
            return None
        _d = node.to_dict()
        gens = _d.get("generators", []) or []
        if len(gens) != 1:
            return None
        g = gens[0]
        target = g.get("target")
        if not isinstance(target, str):
            return None
        src_ir = g.get("iter", {})
        # The seq comprehension path (mutable-state, `_seq_locals`) is left
        # untouched — its result must stay a reassignable `seq` value.
        if (isinstance(src_ir, dict) and src_ir.get("type") == "Var"
                and src_ir.get("name") in getattr(self, "_seq_locals", set())):
            return None
        elt = _d.get("elt", {})
        # variadic content-law comprehension (FABLE-sanctioned): a comprehension
        # `[self.<disp>(t) for t in <array emit_ir>]` whose element is a RECURSIVE IR
        # DISPATCHER call (`_csl_to_ir`/`_py_expr_to_ir`, emit_ir -> emit_ir) over the
        # loop target — the emitter's `_csl_mktuple`/`_py_expr_tuple` variadic-tuple body.
        # Lowers to an `irlist` op carrying BOTH a length law AND a per-index content
        # law over a SHARED, per-dispatcher `emit_ir_disp__<disp>` `val function` (the
        # get_x projection-comprehension precedent extended to a dispatcher; FABLE §6).
        # Tried FIRST (before the pure-int/nested paths, which its `array emit_ir` source
        # never matches). @mutable_state-gated → corpus byte-inert.
        if not g.get("ifs"):
            _variadic = self._variadic_content_comp(g, target, elt, src_ir,
                                                    local_refs, invariant_ctx, subst)
            if _variadic is not None:
                return _variadic
        # nested-list.md S4: the subscript-projection comprehension
        # `[x[k] for x in a]` over a `List[List[τ]]` / `List[Dict[..]]` source
        # `a` (`array (seq τ)` / `array (map κ (option ν))`). The loop target `x`
        # IS the inner collection, so `x[k]` is a faithful `Seq.get`/`Map.get`.
        # This LIFTS the cleared-array subscript-projection boundary (which stayed
        # opaque only because nested lists used to collapse to `array int`).
        if not g.get("ifs"):
            _nested = self._nested_subscript_comp(op_name=None, gen=g, target=target,
                                                  elt=elt, src_ir=src_ir,
                                                  local_refs=local_refs, subst=subst,
                                                  invariant_ctx=invariant_ctx)
            if _nested is not None:
                return _nested
        free: Set[str] = set()
        getters: Set[str] = set()
        user_funcs: Set[str] = set()
        if not self._comp_elt_pure_int(elt, free, getters, user_funcs):
            return None
        # The element may reference the loop target ONLY (no captured locals —
        # they are not parameters of the abstract `val`).
        if free - {target}:
            return None
        srcw = self._expr_to_whyml(src_ir, local_refs or set(), invariant_ctx, subst)
        srca = self._array_coerce_arg(srcw)
        # WL-04b (wrong-lowering-to-fix.md §WL-04 record residual): a projection
        # comprehension `[p.x for p in a]` over a flat `List[<record>]` source `a`
        # (`array <record>`, registered in `_record_array_params`) types its content
        # helper's `src` param as `array <record>` and lowers the projected element
        # NATIVELY (`(src[i]).x`, via the record binder) — NOT the opaque `get_x`
        # over a collapsed int. So a driver's own `\result[k] == a[k].x` (also
        # native) and the content law denote the SAME value (0769/0770 prove; the
        # false twin 0771 stays UNPROVEN). A non-record source keeps `array int`
        # (byte-identical). An IDENTITY element (`[p for p in a]`, whose result would
        # be `array <record>`) is out of the projection scope → fall back to opaque.
        _src_elem_cls: Optional[str] = None
        _src_type = "array int"
        if (isinstance(src_ir, dict) and src_ir.get("type") == "Var"):
            _wn = getattr(self, "_record_array_params", {}).get(src_ir.get("name", ""))
            if _wn is not None:
                if elt.get("type") in ("Var",):
                    return None          # identity over records — not a projection
                for _cls, _info in self._record_types.items():
                    if _info.get("whyml_name") == _wn:
                        _src_elem_cls = _cls
                        _src_type = f"array {_wn}"
                        break
        n = getattr(self, "_comp_content_counter", 0)
        self._comp_content_counter = n + 1
        op = f"list_content_comp_{n}"
        has_if = bool(g.get("ifs"))
        if has_if and _src_elem_cls is not None:
            # WL-04d (wrong-lowering-to-fix.md §WL-04 FILTERED record residual): a
            # FILTERED projection comprehension `[p.x for p in a if <cond(p)>]` over a
            # flat `List[<record>]` source `a` (`array <record>`). The result LENGTH is
            # data-dependent (`0 <= len <= len(a)`), so NO exact length / per-index
            # content law is claimed; the sound faithful law is the length BOUND plus a
            # membership+predicate+projection existential (each result element is the
            # projected field of SOME source record that passed the filter). This
            # replaces the prior hard TYPEERR (the opaque `list_comp` int returned where
            # `array int` was expected). Falls back to the length-bound-only law if the
            # predicate does not lift to a pure-bool term over the target.
            return self._filter_record_proj_law(
                op, g, target, elt, _src_elem_cls, srca, local_refs, subst)
        if has_if:
            # cleared-array.md S4 + item 4: a filtered comprehension keeps the
            # SOUND length bound; when the element is the IDENTITY (`x`) and the
            # filter predicate `cond` lifts to a pure-bool logic term over the
            # target, ADD the content-SUBSET law — each surviving element satisfies
            # `cond` AND appears in `src` (its source index is lost, so this is the
            # honest fact, not a per-index content law).
            subset = self._filter_subset_law(op, g, target, elt, free,
                                             local_refs, subst)
            if subset is not None:
                self._add_abstract_op(subset)
            else:
                self._add_abstract_op(
                    f"val {op} (src: array int) : array int\n"
                    f"    ensures {{ Array.length result <= Array.length src }}")
            return f"({op} {srca})"
        # Lower the element with the loop target rebound to the per-index source
        # read `src[i]` (via a fresh scalar binder `_celt = src[i]`), in logic
        # context. The result is a pure int term over `_celt`.
        binder = "_ci"
        celt = "_celt"
        new_subst = dict(subst or {})
        new_subst[target] = celt
        sb = self._quant_scalar_binders
        had_celt = celt in sb
        # WL-04b: for a record source, register the loop target as a RECORD binder
        # (renamed to `_celt` via `new_subst`) so `p.x` lowers to `_celt.x` (native
        # projection), not the opaque `get_x _celt`. For a scalar source, keep the
        # scalar-binder registration (byte-identical).
        _rec_tok = None
        if _src_elem_cls is not None:
            _rec_tok = self._push_quant_binder(target, _src_elem_cls)
        else:
            sb.add(celt)
        saved_in_spec = self._in_spec
        self._in_spec = True
        try:
            eltw = self._expr_to_whyml(elt, local_refs or set(), True, new_subst)
        finally:
            self._in_spec = saved_in_spec
            if _rec_tok is not None:
                self._pop_quant_binder(target, _rec_tok)
            elif not had_celt:
                sb.discard(celt)
        # cleared-array.md S2: the element was lowered with `_in_spec = True`
        # (above), so each projected `x.attr` already registered its getter as a
        # pure `val function get_attr` (see `_handle_attribute_expr`) — usable in
        # this content-law `ensures` and denoting one value with a driver's own
        # `a[k].attr`. The collected `getters` set gated the lift in
        # `_comp_elt_pure_int`; no extra registration is needed here.
        decl = (
            f"val {op} (src: {_src_type}) : array int\n"
            f"    ensures {{ Array.length result = Array.length src }}\n"
            f"    ensures {{ forall {binder} : int. 0 <= {binder} < Array.length src ->\n"
            f"                result[{binder}] = (let {celt} = src[{binder}] in {eltw}) }}")
        if user_funcs:
            # cleared-array item 1: the content law references a USER `let function`
            # (`result[i] = g(src[i])`). That `val` must be declared AFTER `g`, so it
            # cannot go in the early abstract-op block (which precedes all functions).
            # Defer it, anchored to the function whose body holds the comprehension;
            # `_insert_late_content_ops` splices it in just before that function.
            using = getattr(self, "_current_emitting_func", None)
            self._late_content_ops.append((op, decl, using))
        else:
            self._add_abstract_op(decl)
        return f"({op} {srca})"

    def _comp_cond_pure_bool(self, cond: Any, free: Set[str],
                             getters: Optional[Set[str]] = None,
                             user_funcs: Optional[Set[str]] = None) -> bool:
        """cleared-array item 4. True iff a filter predicate `cond` lowers to a
        PURE, total BOOLEAN logic term: a comparison (`< <= > >= == !=`) of
        pure-int subterms, or an `and`/`or`/`not` combination of such. Free
        variables are collected into `free` (checked ⊆ {target} by the caller).
        Conservative — any other shape ⇒ not liftable (keep length-only).

        WL-04d: when `getters`/`user_funcs` accumulators are supplied (the
        record-source filtered-projection path), a comparison operand may be a
        FIELD PROJECTION `p.attr` (attr names collected into `getters`) — so a
        predicate `p.x > 0` over a `List[<record>]` source lifts. Default None
        keeps the arithmetic-only whitelist byte-identical for existing callers."""
        if not isinstance(cond, dict):
            return False
        t = cond.get("type")
        if t == "BinOp":
            op = cond.get("op")
            if op in ("and", "or"):
                return (self._comp_cond_pure_bool(cond.get("left", {}), free,
                                                  getters, user_funcs)
                        and self._comp_cond_pure_bool(cond.get("right", {}), free,
                                                      getters, user_funcs))
            if op in ("<", "<=", ">", ">=", "==", "!="):
                return (self._comp_elt_pure_int(cond.get("left", {}), free,
                                                getters, user_funcs)
                        and self._comp_elt_pure_int(cond.get("right", {}), free,
                                                    getters, user_funcs))
            return False
        if t == "UnaryOp":
            if cond.get("op") in ("not",):
                return self._comp_cond_pure_bool(
                    cond.get("operand", cond.get("value", {})), free,
                    getters, user_funcs)
            return False
        return False

    def _filter_subset_law(self, op: str, gen: Dict[str, Any], target: str,
                           elt: Any, free: Set[str], local_refs: Set[str],
                           subst: Optional[Dict[str, str]]) -> Optional[str]:
        """cleared-array item 4. When a filtered comprehension's ELEMENT is the
        identity (`x`) and every filter predicate `cond` lifts to a pure-bool
        logic term over the target ONLY, emit the SOUND content-subset law: each
        surviving element satisfies `cond` AND appears in `src` (source index
        lost). Returns the full `val` decl, or None to keep the length-only bound.

        Soundness: with an identity element, every `result[i]` IS some `src[j]`
        that passed the filter, so both conjuncts hold; no per-index content claim
        is made (the surviving elements are compacted, not at their source
        indices)."""
        # Element must be the loop target itself (so result elements ∈ src).
        if not (isinstance(elt, dict) and elt.get("type") == "Var"
                and elt.get("name") == target):
            return None
        ifs = gen.get("ifs") or []
        if not ifs:
            return None
        cfree: Set[str] = set()
        for c in ifs:
            if not self._comp_cond_pure_bool(c, cfree):
                return None
        # The predicate may reference the loop target ONLY.
        if cfree - {target}:
            return None
        binder = "_ci"
        celt = "_celt"
        new_subst = dict(subst or {})
        new_subst[target] = celt
        sb = self._quant_scalar_binders
        had_celt = celt in sb
        sb.add(celt)
        saved_in_spec = self._in_spec
        self._in_spec = True
        try:
            conds = [self._expr_to_whyml(c, local_refs or set(), True, new_subst)
                     for c in ifs]
        finally:
            self._in_spec = saved_in_spec
            if not had_celt:
                sb.discard(celt)
        condw = " /\\ ".join(f"({c})" for c in conds)
        return (
            f"val {op} (src: array int) : array int\n"
            f"    ensures {{ Array.length result <= Array.length src }}\n"
            f"    ensures {{ forall {binder} : int. 0 <= {binder} < Array.length result ->\n"
            f"                (let {celt} = result[{binder}] in {condw})\n"
            f"                /\\ (exists _cj : int. 0 <= _cj < Array.length src /\\\n"
            f"                     result[{binder}] = src[_cj]) }}")

    def _filter_record_proj_law(self, op: str, gen: Dict[str, Any], target: str,
                                elt: Any, src_elem_cls: str, srca: str,
                                local_refs: Set[str],
                                subst: Optional[Dict[str, str]]) -> str:
        """WL-04d (wrong-lowering-to-fix.md §WL-04 FILTERED record residual). Emit
        the faithful lowering of a FILTERED projection comprehension
        `[p.x for p in a if <cond(p)>]` over a flat `List[<record>]` source `a`
        (`array <record>`, `src_elem_cls` its class). The result is `array int`
        (the projected field). The RESULT LENGTH is data-dependent, so NO exact
        length / per-index content law is claimed; the sound faithful law is:

          * the length BOUND `Array.length result <= Array.length src` (the filter
            only removes elements), and
          * a membership+predicate+projection EXISTENTIAL: for each result index i,
            there EXISTS a source index j such that the record `src[j]` passed the
            predicate AND `result[i]` equals its projected field — every output came
            from some retained input (Python semantics), an honest under-approximation
            (the source index is lost to compaction, so no order/index law is made).

        From this the filter CONSEQUENCE transfers to the projected result whenever
        the predicate constrains the projected field (`[p.x for p in a if p.x > 0]`
        yields only positive elements). The element and predicate are lowered
        NATIVELY over the record binder (`(src[j]).field`), the SAME projection a
        driver's own `\\result[i]` / field read lowers to — sound, no new axiom
        (definitional `ensures`; Array read law is Why3 stdlib). SMT spike:
        test-suite/corpus/conformance/spikes/wl04d_filtered_record_proj_spike.mlw
        (Valid on Alt-Ergo AND Z3; the length-equality / per-index false twins NOT
        entailed).

        If the predicate does NOT lift to a pure-bool logic term over the record
        target ONLY, fall back to the length-bound-only law (still sound, still
        `array int` — never the prior TYPEERR)."""
        _wn = self._record_types[src_elem_cls]["whyml_name"]
        binder = "_ci"       # result index (forall)
        jbinder = "_cj"      # source index (exists)
        celt = "_celt"       # = src[_cj], the retained record
        new_subst = dict(subst or {})
        new_subst[target] = celt
        ifs = gen.get("ifs") or []
        # The predicate lifts iff every `if` clause is a pure-bool term (record
        # field projections allowed via `cgetters`) over the loop target ONLY.
        cfree: Set[str] = set()
        cgetters: Set[str] = set()
        cond_ok = bool(ifs)
        for c in ifs:
            if not self._comp_cond_pure_bool(c, cfree, cgetters):
                cond_ok = False
                break
        if cond_ok and (cfree - {target}):
            cond_ok = False
        # Lower the element (and, if it lifts, the predicate) NATIVELY over the
        # record binder: `p` is registered as a record of class `src_elem_cls` and
        # renamed to `_celt` via `new_subst`, so `p.field` → `_celt.<label>`.
        _rec_tok = self._push_quant_binder(target, src_elem_cls)
        saved_in_spec = self._in_spec
        self._in_spec = True
        try:
            eltw = self._expr_to_whyml(elt, local_refs or set(), True, new_subst)
            condws = ([self._expr_to_whyml(c, local_refs or set(), True, new_subst)
                       for c in ifs] if cond_ok else [])
        finally:
            self._in_spec = saved_in_spec
            self._pop_quant_binder(target, _rec_tok)
        if cond_ok:
            condw = " /\\ ".join(f"({c})" for c in condws)
            decl = (
                f"val {op} (src: array {_wn}) : array int\n"
                f"    ensures {{ Array.length result <= Array.length src }}\n"
                f"    ensures {{ forall {binder} : int. 0 <= {binder} < Array.length result ->\n"
                f"                exists {jbinder} : int. 0 <= {jbinder} < Array.length src /\\\n"
                f"                  (let {celt} = src[{jbinder}] in ({condw})\n"
                f"                   /\\ result[{binder}] = ({eltw})) }}")
        else:
            # predicate did not lift → keep the SOUND length bound only (never the
            # prior TYPEERR; still `array int` so a `-> List[int]` return type-checks).
            decl = (
                f"val {op} (src: array {_wn}) : array int\n"
                f"    ensures {{ Array.length result <= Array.length src }}")
        self._add_abstract_op(decl)
        return f"({op} {srca})"

    def _lift_comp_elt(self, elt: Any, target: str, celt: str,
                       local_refs: Set[str],
                       subst: Optional[Dict[str, str]]) -> str:
        """Lower a comprehension element/key/value with the loop `target` rebound
        to the per-source scalar binder `celt` (`= src[i]`), in logic context.
        Shared by the list / dict / set content-comp laws."""
        new_subst = dict(subst or {})
        new_subst[target] = celt
        sb = self._quant_scalar_binders
        had = celt in sb
        sb.add(celt)
        saved = self._in_spec
        self._in_spec = True
        try:
            return self._expr_to_whyml(elt, local_refs or set(), True, new_subst)
        finally:
            self._in_spec = saved
            if not had:
                sb.discard(celt)

    def _dict_content_comp(self, node: "ExprIR", local_refs: Set[str],
                           invariant_ctx: bool,
                           subst: Optional[Dict[str, str]]) -> Optional[str]:
        """cleared-array item 3. Content-faithful DICT comprehension
        `{x: v(x) for x in a}` → a `map int (option int)` with the per-source
        membership law `Map.get result (src[i]) = Some (<v[x:=src[i]]>)`.

        Guards (return None to keep the opaque `dict_comp` otherwise):
          * ONE generator, plain-name target, NO filter, `array int` source;
          * KEY is the IDENTITY (the loop target). This is the soundness pin: a
            non-injective key would make the per-source law unsound (Python keeps
            the LAST colliding write), but an identity key means every collision
            maps to the SAME key AND — since the value is a deterministic function
            of that key — the SAME value, so insertion order is irrelevant;
          * VALUE lifts to a pure-int logic term over the target only.
        The law is an under-approximation of the domain (says nothing about keys
        NOT in src), hence sound."""
        _d = node.to_dict()
        gens = _d.get("generators", []) or []
        if len(gens) != 1:
            return None
        g = gens[0]
        target = g.get("target")
        if not isinstance(target, str) or g.get("ifs"):
            return None
        src_ir = g.get("iter", {})
        if (isinstance(src_ir, dict) and src_ir.get("type") == "Var"
                and src_ir.get("name") in getattr(self, "_seq_locals", set())):
            return None
        key = _d.get("key", {})
        val = _d.get("value", {})
        # KEY must be the identity (loop target) — the soundness pin above.
        if not (isinstance(key, dict) and key.get("type") == "Var"
                and key.get("name") == target):
            return None
        free: Set[str] = set()
        getters: Set[str] = set()
        if not self._comp_elt_pure_int(val, free, getters):
            return None
        if free - {target}:
            return None
        srcw = self._expr_to_whyml(src_ir, local_refs or set(), invariant_ctx, subst)
        srca = self._array_coerce_arg(srcw)
        n = getattr(self, "_comp_content_counter", 0)
        self._comp_content_counter = n + 1
        op = f"dict_content_comp_{n}"
        binder = "_ci"
        celt = "_celt"
        valw = self._lift_comp_elt(val, target, celt, local_refs, subst)
        self._add_abstract_op(
            f"val {op} (src: array int) : map int (option int)\n"
            f"    ensures {{ forall {binder} : int. 0 <= {binder} < Array.length src ->\n"
            f"                Map.get result (src[{binder}]) "
            f"= Some (let {celt} = src[{binder}] in {valw}) }}")
        return f"({op} {srca})"

    def _set_content_comp(self, node: "ExprIR", local_refs: Set[str],
                          invariant_ctx: bool,
                          subst: Optional[Dict[str, str]]) -> Optional[str]:
        """cleared-array item 3. Content-faithful SET comprehension
        `{f(x) for x in a}` → a `map int (option int)` (present = `Some 0`, the set
        model) with the membership law `Map.get result (<f[x:=src[i]]>) = Some 0`
        — every produced element is present. Sound under-approximation of the set
        (says nothing about ABSENT elements). Guards: ONE generator, plain-name
        target, NO filter, `array int` source, element lifts to a pure-int term
        over the target only."""
        _d = node.to_dict()
        gens = _d.get("generators", []) or []
        if len(gens) != 1:
            return None
        g = gens[0]
        target = g.get("target")
        if not isinstance(target, str) or g.get("ifs"):
            return None
        src_ir = g.get("iter", {})
        if (isinstance(src_ir, dict) and src_ir.get("type") == "Var"
                and src_ir.get("name") in getattr(self, "_seq_locals", set())):
            return None
        elt = _d.get("elt", {})
        free: Set[str] = set()
        getters: Set[str] = set()
        if not self._comp_elt_pure_int(elt, free, getters):
            return None
        if free - {target}:
            return None
        srcw = self._expr_to_whyml(src_ir, local_refs or set(), invariant_ctx, subst)
        srca = self._array_coerce_arg(srcw)
        n = getattr(self, "_comp_content_counter", 0)
        self._comp_content_counter = n + 1
        op = f"set_content_comp_{n}"
        binder = "_ci"
        celt = "_celt"
        eltw = self._lift_comp_elt(elt, target, celt, local_refs, subst)
        self._add_abstract_op(
            f"val {op} (src: array int) : map int (option int)\n"
            f"    ensures {{ forall {binder} : int. 0 <= {binder} < Array.length src ->\n"
            f"                Map.get result (let {celt} = src[{binder}] in {eltw}) "
            f"= Some 0 }}")
        return f"({op} {srca})"

    def _handle_issorted_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        lo = self._expr_to_whyml(node.lo, local_refs, invariant_ctx, subst)
        hi = self._expr_to_whyml(node.hi, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"(forall _si : int. {lo} <= _si /\\ _si < {hi} - 1 -> {base}[_si] <= {base}[_si + 1])"
        return "true"

    def _handle_arrayeq_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        """`\\array_eq(a, b)` — extensional array content equality:
        same length and equal element at every index. Emitted as an
        explicit quantified formula (rather than the `array_eq`
        predicate) so the SMT solver sees the per-index goal directly and
        can E-match it against `Array.blit`/`Array.sub` content
        postconditions (the predicate layer did not auto-unfold)."""
        a = self._expr_to_whyml(node.left, local_refs, invariant_ctx, subst)
        b = self._expr_to_whyml(node.right, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return (f"((Array.length {a} = Array.length {b}) /\\ "
                    f"(forall _ae : int. 0 <= _ae /\\ _ae < Array.length {a} "
                    f"-> {a}[_ae] = {b}[_ae]))")
        return "true"

    def _handle_permutation_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        """`\\permutation(a, b)` — `a` is a permutation of `b` (same multiset).
        Lowers to an UNINTERPRETED `predicate permut` (no-more-int A2b Gap 1):
        unlike `\\array_eq`, permutation is not first-order expressible, so it is
        NOT unfolded — a proof-assistant-imported axiom (`#@ proof`, stage 4) is
        what constrains `permut`. Here the operator is just plumbed: a spec-only
        relation over two `array int` values."""
        a = self._expr_to_whyml(node.left, local_refs, invariant_ctx, subst)
        b = self._expr_to_whyml(node.right, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            self._add_abstract_op("predicate permut (a: array int) (b: array int)")
            return f"(permut {a} {b})"
        return "true"

    def _handle_sum_node_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        lo = self._expr_to_whyml(node.lo, local_refs, invariant_ctx, subst)
        hi = self._expr_to_whyml(node.hi, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"(pycsl_sum {base} {lo} {hi})"
        return "0"

    def _handle_lambda_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        params = node.params
        body = self._expr_to_whyml(node.body, local_refs, invariant_ctx, subst)
        param_str = " ".join(f"({whyml_ident(p)}: int)" for p in params) if params else "()"
        return f"(fun {param_str} -> {body})"

    def _handle_setlit_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        elts = node.elts
        # Empty set literal: `map int (option int)` initialised to None.
        if not elts:
            return "(const (None: option int))"
        # Non-empty set literal `{a, b, c}`: chain map_update_some on an
        # empty base. Each element is marked present with value 0.
        # `Map.set` directly would be a logic-function call rejected as
        # ghost; the program-val wrapper sidesteps that.
        # list-comprehension-lowering.md L5: polymorphic decl in a @mutable_state module
        # (unifies with a string-valued dict field); fixed in the corpus → byte-identical.
        _poly = getattr(self, "_mutable_state_classes", None)
        self._add_abstract_op(
            ("val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) "
             ": map 'k (option 'v)\n" if _poly else
             "val map_update_some (m: map int (option int)) (k: int) (v: int) "
             ": map int (option int)\n")
            + "    ensures { result = Map.set m k (Some v) }")
        result = "(const (None: option int))"
        for elt in elts:
            elt_w = self._coerce_to_int(self._expr_to_whyml(
                elt, local_refs, invariant_ctx, subst))
            result = f"(map_update_some {result} {elt_w} 0)"
        return result

    def _tdrl_hval_field_proj(self, arg: Any, local_refs: Set[str],
                              invariant_ctx: bool,
                              subst: Optional[Dict[str, str]]) -> Optional[str]:
        """self-tcb-reduction _typeddict_record_literal (cap-6/7): the RAW hval projection
        of a `<pyval-local>["<key>"]` subscript (`rec_info["fields"]`, an `HArr` of field
        names) — the `HMap`/`pairs_get` chain that descends the REAL structure, the SAME
        form the `_typeddict_field_access (d)` membership recognizer emits. Returns None
        unless the arg is a subscript on a `_pyval_locals` receiver."""
        if not (isinstance(arg, dict) and arg.get("type") == "Subscript"):
            return None
        _sv = arg.get("value")
        if not (isinstance(_sv, dict) and _sv.get("type") == "Var"
                and _sv.get("name") in getattr(self, "_pyval_locals", set())):
            return None
        _pvm = whyml_ident(_sv.get("name"))
        _kw = self._expr_to_whyml(arg.get("index", {}), local_refs or set(),
                                  invariant_ctx, subst)
        return (f"(match {_pvm} with HMap m_mem -> "
                f"(match pairs_get m_mem {_kw} with Some v_ -> v_ "
                f"| None -> (HInt 0) end) | _ -> (HInt 0) end)")

    def _tdrl_present_map_term(self, node: Any) -> Optional[str]:
        """cap-6/7: the real `present` map term. `present = set(kv.keys())` is modelled as
        the `kv` map itself, so a Var read of a collected `present` local dereferences to
        that `map string (option emit_ir)` ref (`!present`). Returns None otherwise."""
        if not (isinstance(node, dict) and node.get("type") == "Var"):
            return None
        _nm = node.get("name")
        if _nm in getattr(self, "_tdrl_present_locals", set()):
            return f"!{whyml_ident(_nm)}"
        return None

    def _tdrl_declared_hval_term(self, node: Any) -> Optional[str]:
        """cap-6/7: the real `declared` hval term. `declared = set(rec_info["fields"])` is
        modelled as that fields hval, so a Var read of a collected `declared` local
        dereferences to the `hval` ref (`!declared`). Returns None otherwise."""
        if not (isinstance(node, dict) and node.get("type") == "Var"):
            return None
        _nm = node.get("name")
        if _nm in getattr(self, "_tdrl_hval_locals", set()):
            return f"!{whyml_ident(_nm)}"
        return None

    def _tdrl_overapprox_comp(self, expr: Dict[str, Any], local_refs: Set[str],
                              invariant_ctx: bool,
                              subst: Optional[Dict[str, str]]) -> Optional[str]:
        """cap-6/7: a `[<v> for <v> in <src> if <v> not in <container>]` raise-branch
        comprehension (`missing`/`extra`) -> `(typeddict_str_overapprox <hval> <map>)`,
        the SOUND over-approx reader that CONSUMES the real iterated hval collection AND
        the real `present` kv-domain map (so no term is input-blind). Fail-closed (None)
        unless the exact single-generator single-`not in`-filter shape matches and BOTH a
        real hval and a real map term are recovered from the iter/filter sub-nodes."""
        _gens = expr.get("generators") or []
        if len(_gens) != 1:
            return None
        _g = _gens[0]
        _iter = _g.get("iter") or {}
        _ifs = _g.get("ifs") or []
        if len(_ifs) != 1:
            return None
        _f = _ifs[0]
        if not (isinstance(_f, dict) and _f.get("type") == "BinOp"
                and _f.get("op") == "not in"):
            return None
        _container = _f.get("right") or {}
        # the kv-domain map term (`present`) is whichever of iter / filter-container is a
        # collected present local.
        _map_term = (self._tdrl_present_map_term(_iter)
                     or self._tdrl_present_map_term(_container))
        # the iterated hval collection: `rec_info["fields"]` (subscript projection) when
        # the iter is the fields subscript, else the `declared` hval local (in `extra`,
        # where the iter is `present` and the filter-container is `declared`).
        _hval_term = (self._tdrl_hval_field_proj(_iter, local_refs, invariant_ctx, subst)
                      or self._tdrl_declared_hval_term(_iter)
                      or self._tdrl_declared_hval_term(_container))
        if _map_term is None or _hval_term is None:
            return None
        return f"(typeddict_str_overapprox {_hval_term} {_map_term})"

    def _tdrl_raise_consumer_read(self, expr: Any, local_refs: Set[str],
                                  invariant_ctx: bool,
                                  subst: Optional[Dict[str, str]]) -> Optional[str]:
        """self-tcb-reduction _typeddict_record_literal (cap-6/7): lower the four
        raise-branch consumers. They feed ONLY the `if missing or extra: raise` guard —
        the returned record depends solely on the faithful `kv.get(fname)` — so a SOUND
        OVER-APPROX is permitted, BUT every emitted term must READ a real input (the
        `rec_info` hval or the `kv` map), never an input-blind `kv_keys_0 ()`/`set_1`
        facade (Gate-C). Fail-closed (None) so nothing else in the method is perturbed."""
        if not isinstance(expr, dict):
            return None
        t = expr.get("type")
        # (a) set(rec_info["fields"]) -> the real fields hval;
        # (b) set(kv.keys())         -> the real kv map.
        if t == "Call" and expr.get("func") in ("set", "frozenset"):
            _a = expr.get("args") or []
            if len(_a) == 1 and isinstance(_a[0], dict):
                _arg = _a[0]
                _hv = self._tdrl_hval_field_proj(_arg, local_refs, invariant_ctx, subst)
                if _hv is not None:
                    return _hv
                # set(kv.keys()) -> the kv map itself (its domain IS the key set).
                _fn = _arg.get("func") if _arg.get("type") == "Call" else None
                if (isinstance(_fn, str) and _fn.endswith(".keys")
                        and not (_arg.get("args") or [])):
                    _recv = _fn[:-len(".keys")]
                    if getattr(self, "_dict_value_types", {}).get(_recv) == "emit_ir":
                        return f"!{whyml_ident(_recv)}"
        # (c)/(d) the missing/extra comprehensions.
        if t == "ListComp":
            return self._tdrl_overapprox_comp(expr, local_refs, invariant_ctx, subst)
        return None

    def _expr_to_whyml(self, expr: "Union[Dict[str, Any], ExprIR]", local_refs: Set[str],
                       invariant_ctx: bool = False,
                       subst: Optional[Dict[str, str]] = None) -> str:
        """Recursively translates an expression dictionary into a WhyML string.
        When invariant_ctx is True, FieldGet emits bare field names (for record invariants).
        subst: optional name substitution dict applied before local_refs lookup (e.g. for-loop vars)."""
        # Phase-B-expr: accept a typed ExprIR (Phase-A sum) or the legacy wire
        # dict. Normalize to a typed node once; converted kinds dispatch by
        # isinstance below; un-converted kinds fall through to the legacy dict
        # body (`node.to_dict()`). Byte-identical at every kind conversion.
        if not expr: return ""
        node = expr_from_dict(expr) if isinstance(expr, dict) else expr
        # TIER3-P1 fail-closed boundary (`triage-ranked-tcb-tier3.md` Phase-1 prereq):
        # the eleven upstream/out-of-registry tags (`ir_schema.IR_TAG_ALIASES`) are
        # normalized to a canonical registry tag by Module 5 at emission; none may reach
        # the emitter as a raw `OpaqueExpr` to be lowered inside `raw`. If one does, the
        # front-end violated its normalization contract (docs/ir.md §9.5) — this is a
        # bug, never a faithful lowering. Assert the boundary rather than silently
        # emitting the "" fall-through. (Unreachable on well-formed IR: Module 6 only
        # ever consumes Module-5 IR, which never carries these tags — so this is
        # emission-inert / byte-diff 0.)
        if isinstance(node, OpaqueExpr) and node.kind in IR_TAG_ALIASES:
            raise AssertionError(
                f"tier3-p1 fail-closed: upstream alias tag '{node.kind}' reached the "
                f"emitter un-normalized (Module 5 must emit its canonical form "
                f"'{IR_TAG_ALIASES[node.kind]}'); an Opaque node must never lower "
                f"inside `raw`")
        # --- typed fast-paths (E2: leaf kinds) ---
        if isinstance(node, NumberExpr):
            v = node.value
            if isinstance(v, float) and not float(v).is_integer():
                return repr(v)
            if isinstance(v, float):
                return f"{int(v)}.0"
            return str(int(v))
        if isinstance(node, RawWhymlExpr):
            return node.whyml
        if isinstance(node, StringExpr):
            return whyml_string_literal(node.value)
        if isinstance(node, ResultExpr):
            return getattr(self, "_result_alias", None) or "result"
        if isinstance(node, NoneExpr):
            return "0"
        if isinstance(node, BoolExpr):
            if self._in_spec: return "true" if node.value else "false"
            return "1" if node.value else "0"
        if isinstance(node, UnknownPyExprExpr):
            return "0"
        if isinstance(node, SliceExpr):
            return "0"
        if isinstance(node, OldFieldExpr):
            _of_rec = (self._current_self_type if node.object == "self"
                       else (getattr(self, "_current_record_var_classes", {}).get(node.object, "") or "").lower() or None)
            return f"(old {node.object}.{self._field_label(_of_rec, node.field)})"
        if isinstance(node, StarredExpr):
            return self._expr_to_whyml(node.value, local_refs, invariant_ctx, subst)
        if isinstance(node, TupleExpr):
            # V1 pyconst-dispatch (self-tcb-reduction M5, B-bucket): inside
            # `_classify_literal_value` the return tuple's MIDDLE slot is the Python constant
            # VALUE — a DIRECT bare `None`/`True`/`False` literal element, faithfully the
            # `PVNone`/`PVBool` variant (NOT the int 0/1). A DIRECT `NoneExpr`/`BoolExpr` tuple
            # element is UNAMBIGUOUS: the IrBoolC ctor's `value` bool is nested inside a DictLit
            # (`{"type":"Bool","value":True}`), never a direct tuple element, so it stays the
            # int the `IrBoolC` payload expects. Method-gated via `_current_emitting_func` ->
            # corpus + every other tuple byte-identical.
            _cef_t = getattr(self, "_current_emitting_func", None) or ""
            if (_cef_t == "_classify_literal_value"
                    or _cef_t.endswith("___classify_literal_value")):
                elts = []
                for e in node.elts:
                    if isinstance(e, NoneExpr):
                        elts.append("PVNone")
                    elif isinstance(e, BoolExpr):
                        elts.append("(PVBool true)" if e.value else "(PVBool false)")
                    else:
                        elts.append(self._expr_to_whyml(e, local_refs, invariant_ctx, subst))
                return f"({', '.join(elts)})"
            elts = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst) for e in node.elts]
            return f"({', '.join(elts)})"
        # --- legacy dict body (un-converted kinds) ---
        expr = node.to_dict()
        t = expr["type"]

        # self-tcb-reduction giants (generic class-body lowering): a READ over a
        # `pyast_stmt`-typed class-body loop var lowers to the ADT projector chain.
        # Gated on `child in _pyast_stmt_locals` -> inert for every other expression.
        if getattr(self, "_pyast_stmt_locals", None):
            _psr = self._pyast_stmt_read(expr, local_refs, invariant_ctx, subst)
            if _psr is not None:
                return _psr
        # L1 tparam reflection-node ADT: a READ over a `tparam`-typed type_params loop var
        # lowers to the certified tparam projector chain. Gated on `tp in _tparam_locals`
        # -> inert for every other expression.
        if getattr(self, "_tparam_locals", None):
            _tpr = self._tparam_read(expr, local_refs, invariant_ctx, subst)
            if _tpr is not None:
                return _tpr
        # J2/J3 convergence (Call-internals keyword iteration): a READ over a `keyword`-
        # typed loop var lowers to the certified keyword projectors.
        if getattr(self, "_keyword_locals", None):
            _kwr = self._keyword_read(expr, local_refs, invariant_ctx, subst)
            if _kwr is not None:
                return _kwr
        # self-tcb-reduction _typeddict_record_literal (cap-6/7): the four raise-branch
        # consumers (`declared = set(rec_info["fields"])`, `present = set(kv.keys())`,
        # `missing`/`extra` comprehensions) lower to typed readers that CONSUME the real
        # `rec_info` hval + the `kv` map — a SOUND OVER-APPROX (they feed only the raise
        # guard; the returned record depends solely on the faithful `kv.get(fname)`) that
        # stays non-vacuous per Gate-C. Gated on `_current_emitting_func` -> inert.
        if (getattr(self, "_current_emitting_func", None) or "").endswith(
                "_typeddict_record_literal"):
            _tdr = self._tdrl_raise_consumer_read(expr, local_refs, invariant_ctx, subst)
            if _tdr is not None:
                return _tdr
        # J2/J3 convergence (Call-internals): `<emit_ir call>.func.id` — the emit_ir model
        # collapses a call's callee to its Name-id STRING (`func_of`), so `.func.id` is
        # exactly `func_of call` (the trailing `.id` on the id-string is identity). Gated
        # on the `<emit_ir local>.func.id` chain -> corpus-inert.
        if (t == "Attribute" and expr.get("attr") == "id"
                and isinstance(expr.get("object"), dict)
                and expr["object"].get("type") == "Attribute"
                and expr["object"].get("attr") == "func"):
            _co = expr["object"].get("object", {})
            if (isinstance(_co, dict) and _co.get("type") == "Var"
                    and _co.get("name") in getattr(self, "_emit_ir_local_vars", set())):
                _cw = self._expr_to_whyml(_co, local_refs, invariant_ctx, subst)
                return f"(func_of {_cw})"

        # Simple literals and trivial 1-3-line branches — kept inline
        if t == "Number":
            v = expr["value"]
            # no-more-int Stage D: a float literal is a Why3 `real` constant (was
            # truncated to int — the unsound float collapse). Why3 reals need a decimal
            # point: `1.5`, `2.0`.
            if isinstance(v, float) and not float(v).is_integer():
                return repr(v)
            if isinstance(v, float):
                return f"{int(v)}.0"
            return str(int(v))
        # Pre-lowered WhyML passthrough — used to splice an already-emitted argument
        # string into a value IR (parametrized record construction, base_op.md Tier A).
        if t == "RawWhyml": return expr["whyml"]
        if t == "String":
            # strings-plan Stage 1: a string literal is a real Why3 string. Where an int is
            # required (an abstract-op arg, a dict key), `_coerce_to_int` hashes it back, so
            # int-contexts keep working; string-typed contexts now get a real `"..."`.
            # `whyml_string_literal` escapes raw newlines/tabs/control bytes (Why3 rejects
            # them with "illegal character in string") — `";\n"` lowers to `";\\n"`.
            return whyml_string_literal(expr["value"])
        if t == "Result":   return getattr(self, "_result_alias", None) or "result"
        if t == "None":     return "0"
        if isinstance(node, ArrayLitExpr):
            elts = expr.get("elts", [])
            # 07-0903 W1 (no-more-int): a list/array of tuples lowers to a faithful
            # `array (t0, …)` — each element is a Why3 tuple, NOT collapsed to an int.
            # Homogeneous fixed-arity tuples only (the directory/(key,value) shape);
            # a mixed-arity literal is still rejected (no single element type).
            tuple_elts = [e for e in elts if isinstance(e, dict) and e.get("type") == "Tuple"]
            if tuple_elts:
                arities = {len(e.get("elts", [])) for e in tuple_elts}
                if len(tuple_elts) != len(elts) or len(arities) != 1:
                    from errors import PyCSLSemanticError
                    raise PyCSLSemanticError(
                        "array/list with mixed or non-tuple elements alongside tuples is "
                        "not supported: a faithful `array (tuple)` needs one uniform "
                        "element type. Use a uniform list of equal-arity tuples.")
                n = len(elts)
                # Each element is a Why3 tuple value `(a, b, …)` — no int coercion.
                lowered = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst)
                           for e in elts]
                inner = f"let _alit = Array.make {n} ({lowered[0]}) in"
                sets = "; ".join(f"_alit[{i}] <- {lowered[i]}" for i in range(1, n))
                if sets:
                    inner += f" {sets};"
                return f"({inner} _alit)"
            if elts:
                n = len(elts)
                # WL-04c (wrong-lowering-to-fix.md §WL-04 record LITERAL residual): a
                # LIST-LITERAL whose elements are ALL full-arity constructor Calls to
                # the SAME content-faithful record (`[Point(1, 2), Point(3, 4)]`) builds
                # `array <record>` with each element the FAITHFUL record literal
                # (`{ x = 1; y = 2 }` via `_call_record_constructor`) — NOT the opaque
                # int-coercion collapse. So `a[i].field` on the local (registered as a
                # record-array local in `_track_collection_metadata`) / `\result[i].field`
                # on a `-> List[R]` return projects the real field. A non-faithful
                # record (e.g. a `@dataclass` whose ctor drops its args) is NOT matched
                # → keeps the fail-closed opaque path. This is the construction analog of
                # the WL-04b flat `List[<record>]` PARAMETER element.
                _rec_elem = self._record_ctor_list_elem(elts)
                if _rec_elem is not None:
                    lowered = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst)
                               for e in elts]
                    sets = "; ".join(f"_alit[{i}] <- {lowered[i]}" for i in range(1, n))
                    inner = f"let _alit = Array.make {n} ({lowered[0]}) in"
                    if sets:
                        inner += f" {sets};"
                    return f"({inner} _alit)"
                # WL-04a (wrong-lowering-to-fix.md §WL-04 list-literal residual): a
                # LIST-LITERAL whose elements are ALL string literals (resp. ALL float
                # `Number`s) is realized at the FAITHFUL element type — `array string`
                # (resp. `array real`) — NOT the hashed-int/truncated collapse. This is
                # the construction analog of the WL-04 param fix (`array string`/`array
                # real` param element): a `List[str]`/`List[float]` LOCAL or a direct
                # `return [...]` now type-checks against a str/float use site. An all-`int`/
                # all-`bool` literal keeps the `array int` path below (byte-identical);
                # a mixed / non-scalar literal keeps the int-coercion default (documented).
                _all_str = all(isinstance(e, dict) and e.get("type") == "String"
                               for e in elts)
                _all_float = all(isinstance(e, dict) and e.get("type") == "Number"
                                 and isinstance(e.get("value"), float) for e in elts)
                if _all_str or _all_float:
                    lowered = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst)
                               for e in elts]
                    sets = "; ".join(f"_alit[{i}] <- {lowered[i]}" for i in range(1, n))
                    inner = f"let _alit = Array.make {n} ({lowered[0]}) in"
                    if sets:
                        inner += f" {sets};"
                    return f"({inner} _alit)"
                # WL-04g (wrong-lowering-to-fix.md §WL-04 mixed-element residual):
                # a HETEROGENEOUS list literal has NO faithful `array τ` element
                # type — Python lists are heterogeneous, a WhyML `array` is
                # HOMOGENEOUS. Every UNIFORM non-int shape (all-str/all-float via
                # WL-04a, all-record via WL-04c, all-equal-arity-tuple above) has
                # already been claimed; so reaching this int-coercion fallback with
                # ANY element whose faithful type is non-int (a `str` literal, a
                # `float` Number, a `Tuple`, or a known record constructor) means
                # the literal is genuinely MIXED. The int-coercion default is UNSAFE
                # on such a literal: a `str` element HASHES to a WELL-TYPED int
                # (`[1, "x"]` emits `array int` with `a[1] = 976090257`, so
                # `a[1] == 976090257` PROVES — a claim FALSE of real Python where
                # `a[1]` is the string `"x"`: severity-1 UNSOUND), and a `float` /
                # record element ill-types the `array int` (silent TYPEERR / broken
                # emission). FAIL CLOSED with a clear diagnostic instead. A uniform
                # all-int / all-bool / expression literal is NOT flagged (stays
                # `array int`, byte-identical).
                _mix = self._mixed_literal_reject_kind(elts)
                if _mix is not None:
                    from errors import PyCSLSemanticError
                    raise PyCSLSemanticError(
                        f"heterogeneous list literal (contains a {_mix} element "
                        f"mixed with other element types) has no faithful WhyML "
                        f"`array` element type: a Python list is heterogeneous but "
                        f"a WhyML `array` is homogeneous. Coercing the non-int "
                        f"element to an int would be unsound (a str hashes to a "
                        f"well-typed int; a float/record ill-types). Use a "
                        f"homogeneous list, a Tuple (fixed-arity heterogeneous "
                        f"slots), or a record/@dataclass for heterogeneous fields.")
                # Build a concrete `array int` of the literal's elements:
                # `(let _alit = Array.make N e0 in _alit[1] <- e1; …; _alit)`.
                e0 = self._coerce_to_int(
                    self._expr_to_whyml(elts[0], local_refs, invariant_ctx, subst))
                sets = "; ".join(
                    f"_alit[{i}] <- {self._coerce_to_int(self._expr_to_whyml(e, local_refs, invariant_ctx, subst))}"
                    for i, e in enumerate(elts) if i > 0)
                inner = f"let _alit = Array.make {n} ({e0}) in"
                if sets:
                    inner += f" {sets};"
                return f"({inner} _alit)"
            return "(Array.make 1024 0)"
        if t == "ClassByNameCall":
            # VARIABLE-CLASS-NAME CONSTRUCTION (relaunch #8): `_N(cls)(<children>)` where
            # `cls` is a LOCAL holding a ternary of two class-name literals
            # (`cls = "TryStar" if is_star else "Try"`). The construction really is a
            # choice between TWO node classes with the SAME children, so the faithful
            # lowering is the same choice, made at the CONSTRUCTOR:
            #     (if <test> then (IrPyTryStar …) else (IrPyTry …))
            # Both arms are built through the ORDINARY node-ctor path
            # (`_handle_call_expr` on a synthesized literal-class Call), so the by-name
            # payload binding, the option slots and the fail-closed decline all apply
            # unchanged. If either arm declines, or the local is not a recognized
            # class-name ternary, this returns the scalar `0` — EXACTLY what the
            # `UnknownPyExpr` catch-all emitted before, so nothing that used to work
            # changes shape.
            _ce = expr.get("class_expr") or {}
            # CONST-DICT CLASS NAME (relaunch #8): `_N(_UNARY[t.string])()` — a 0-FIELD
            # ASDL SINGLETON whose CLASS is chosen by a module-const-dict lookup. A
            # singleton carries no information beyond its own identity, so its faithful
            # model is its class-name STRING (increment 10's rule); the lookup therefore
            # lowers to the chained string ITE over the dict's ACTUAL entries — the same
            # construction `<X>.get(k, default)` already uses, mutation-sensitive in both
            # key and value. The tail is the EMPTY STRING, which is not an ASDL class name:
            # off the dict's key set Python raises `KeyError`, and the model must not name
            # a WRONG class there. It is also UNREACHABLE at every site the source guards
            # with `<k> in <X>` — that guard now lowers to the exact `str_eq_op`
            # disjunction over the same key set. FAIL-CLOSED: no args/keywords (a real
            # singleton), a genuine module-const dict, and EVERY value must be a
            # `_NODE_SPEC` 0-field singleton, else this declines to the pre-existing `0`.
            if (not expr.get("args") and not expr.get("keywords")
                    and isinstance(_ce, dict) and _ce.get("type") == "Subscript"
                    and isinstance(_ce.get("value"), dict)
                    and _ce["value"].get("type") == "Var"):
                _cdn = self._const_dict_name(_ce["value"].get("name"))
                _cdt = (getattr(self, "_module_const_dicts", {}) or {}).get(_cdn)
                _sing = set(self.ir.get("pyast_singleton_nodes", []) or [])
                if _cdt and _sing and all(_vv in _sing for _vv in _cdt.values()):
                    self._add_abstract_op(
                        "val str_eq_op (a: string) (b: string) : bool\n"
                        "    ensures { result <-> (a = b) }")
                    _kx = self._expr_to_whyml(
                        _ce.get("slice") or _ce.get("index") or {},
                        local_refs, invariant_ctx, subst)
                    # BIND THE KEY ONCE. The key expression can have an EFFECT —
                    # `_CMP[self.advance().string]` in `comparison` advances the cursor —
                    # and the chain mentions it once per entry, so inlining it would move
                    # the cursor N times. A `let` makes the emitted term evaluate it
                    # exactly once, as Python does.
                    _ch = '""'
                    for _kk, _vv in reversed(list(_cdt.items())):
                        _ch = (f"(if (str_eq_op _cdk {whyml_string_literal(_kk)}) "
                               f"then {whyml_string_literal(_vv)} else {_ch})")
                    return f"(let _cdk = {_kx} in {_ch})"
            # CONST-PAIR-DICT CLASS NAME, LOCAL form (relaunch #11): `_N(opname)()` in
            # `_binop`, where `opname` is a STRING LOCAL bound by the tuple-unpack
            # `opname, prec = _BINOP[self.cur().string]` of a module-const `str ->
            # (str, int)` PAIR dict. The class is chosen at RUN TIME from the table, and
            # the local ALREADY HOLDS the faithful chained-ITE over the table's own first
            # components (see `_const_pair_dict_unpack_projs`) — so the faithful lowering
            # of the construction is the LOCAL'S OWN READ: a 0-FIELD ASDL SINGLETON
            # carries no information beyond its own identity, and its model in this family
            # IS its class-name string (the rule the sibling const-dict form above states).
            # No new dispatch, no candidate chain: the choice was already made, faithfully,
            # where the table was read.
            # FAIL-CLOSED on every axis: no args and no keywords (a real singleton), the
            # class expression a bare `Var` that this file's prescan classified as a
            # pair-dict slot-0 local, and EVERY first component of that dict a
            # `_NODE_SPEC` 0-field singleton — else this falls through to the pre-existing
            # scalar `0`, exactly what `UnknownPyExpr` emitted before.
            if (not expr.get("args") and not expr.get("keywords")
                    and isinstance(_ce, dict) and _ce.get("type") == "Var"):
                _cpl = getattr(self, "_const_pair_dict_str_locals", None) or {}
                _pdn = _cpl.get(_ce.get("name"))
                _pdt = (getattr(self, "_module_const_pair_dicts", {}) or {}).get(_pdn)
                _sing2 = set(self.ir.get("pyast_singleton_nodes", []) or [])
                if _pdt and _sing2 and all(_e[1] in _sing2 for _e in _pdt):
                    return self._expr_to_whyml(_ce, local_refs, invariant_ctx, subst)
            # VARIABLE-CLASS-NAME, PARAMETER form (relaunch #10): `_N(kind)(names=names)`
            # in `global_stmt`, where `kind` is a `str` FORMAL PARAMETER — the caller
            # passes the literal "Global" or "Nonlocal". There is no ternary local to
            # read, so the class is chosen at RUN TIME; the faithful lowering is the same
            # choice, made at the CONSTRUCTOR, over the family members the construction
            # could possibly name.
            #
            # THE CANDIDATE SET IS DERIVED FROM THE TABLE, NEVER HAND-WRITTEN: exactly
            # those `_PYAST_IRNODE_CTORS` entries whose payload FIELD-NAME SET equals the
            # construction's KEYWORD set. That is what keeps this drift-proof — add or
            # remove a family member and the chain follows automatically, and an ASDL
            # drift that changes a field name drops the member out of the set.
            #
            # THE TAIL IS `IrOther <kind>`, and it is EXACT rather than a fallback:
            # `kind_of (IrOther k) = k`, so off the candidate set the model says "a node
            # whose kind is precisely this string" — it never names a WRONG class. (In
            # Python that path raises `KeyError`; it is unreachable from every call site,
            # which passes a literal.)
            #
            # FAIL-CLOSED on every axis: the pure_ast parser file, a class expression that
            # is a bare FORMAL PARAMETER (a LOCAL is the ternary form below, unchanged),
            # KEYWORDS ONLY (so the field set is unambiguous — no positional binding), a
            # NON-EMPTY candidate set, and every arm must lower to a REAL application of
            # its own ADT constructor. Anything else falls through to the ternary path and
            # then to the pre-existing scalar `0`.
            if (self._uses_pyast_parser()
                    and isinstance(_ce, dict) and _ce.get("type") == "Var"
                    and _ce.get("name") in set(getattr(self, "_formal_params", []) or [])
                    and not expr.get("args") and expr.get("keywords")):
                from frontend.ir_resolve import _PYAST_IRNODE_CTORS as _PYC4
                _want = {_k.get("arg") for _k in expr["keywords"]}
                _cands = sorted(_cn for _cn, (_c4, _p4) in _PYC4.items()
                                if {_fn for _fn, _ty in _p4} == _want)
                _arms2: List[Tuple[str, str]] = []
                for _cn in _cands:
                    _syn2 = {"type": "Call", "func": _cn, "args": [],
                             "keywords": list(expr["keywords"])}
                    _lw2 = self._handle_call_expr(
                        expr_from_dict(_syn2), local_refs, invariant_ctx, subst)
                    _ct2 = _PYC4[_cn][0]
                    if not (isinstance(_lw2, str) and _lw2.startswith(f"({_ct2} ")):
                        _arms2 = []
                        break
                    _arms2.append((_cn, _lw2))
                if _arms2:
                    self._add_abstract_op(
                        "val str_eq_op (a: string) (b: string) : bool\n"
                        "    ensures { result <-> (a = b) }")
                    _kw2 = self._expr_to_whyml(_ce, local_refs, invariant_ctx, subst)
                    _chain2 = "(IrOther _cnk)"
                    for _cn, _lw2 in reversed(_arms2):
                        _chain2 = (f"(if (str_eq_op _cnk {whyml_string_literal(_cn)}) "
                                   f"then {_lw2} else {_chain2})")
                    return f"(let _cnk = {_kw2} in {_chain2})"
            _cnt = getattr(self, "_class_name_ternary_locals", {}) or {}
            _ent = (_cnt.get(_ce.get("name"))
                    if isinstance(_ce, dict) and _ce.get("type") == "Var" else None)
            if _ent is None:
                return "0"
            _test_ir, _cls_a, _cls_b = _ent
            _arms = []
            for _cn in (_cls_a, _cls_b):
                _syn = {"type": "Call", "func": _cn,
                        "args": list(expr.get("args") or [])}
                if expr.get("keywords"):
                    _syn["keywords"] = list(expr["keywords"])
                _lw = self._handle_call_expr(
                    expr_from_dict(_syn), local_refs, invariant_ctx, subst)
                # A DECLINED construction falls back to the record-literal / opaque
                # paths, which is exactly what this recognizer exists to avoid — accept
                # only a real ADT application of the named constructor.
                _ctor = None
                if self._uses_pyast_parser():
                    from frontend.ir_resolve import _PYAST_IRNODE_CTORS as _PYC3
                    _pc3 = _PYC3.get(_cn)
                    _ctor = _pc3[0] if _pc3 else None
                if not (_ctor and isinstance(_lw, str)
                        and _lw.startswith(f"({_ctor} ")):
                    return "0"
                _arms.append(_lw)
            _c = self._to_bool(
                self._expr_to_whyml(_test_ir, local_refs, invariant_ctx, subst),
                _test_ir or {})
            return f"(if {_c} then {_arms[0]} else {_arms[1]})"
        if t in ("UnknownPyExpr", "GenExp"):
            # genexp-erasure-wall R2a parity: before R2a a generator expression had no Module-5
            # handler and arrived here as `UnknownPyExpr`, lowering to the scalar `0` (which
            # `_array_coerce_arg` then turned into a placeholder array). R2a gives it a real IR
            # node, so it must fall to the SAME scalar here or every existing genexp site
            # changes shape — e.g. the emitter's own `sum(ord(c) for c in name)` in
            # `_handle_in_globals_expr` started emitting `sum_1` with no argument at all
            # (`int -> int`, L3-tc failure, caught by the mirror-wide sweep). The faithful
            # bounded fold is introduced at the any/all call site (R2b), which intercepts
            # BEFORE this fallback; everywhere else GenExp stays exactly as inert as it was.
            return "0"
        if t == "Slice":    return "0"
        if t == "OldField":
            _of_rec = (self._current_self_type if expr['object'] == "self"
                       else (getattr(self, "_current_record_var_classes", {}).get(expr['object'], "") or "").lower() or None)
            return f"(old {expr['object']}.{self._field_label(_of_rec, expr['field'])})"
        if t == "Starred":  return self._expr_to_whyml(expr.get("value", {}), local_refs, invariant_ctx, subst)
        if t == "Bool":
            if self._in_spec: return "true" if expr.get("value") else "false"
            return "1" if expr.get("value") else "0"
        if t == "Tuple":
            elts = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst) for e in expr.get("elts", [])]
            return f"({', '.join(elts)})"
        if isinstance(node, ForallExpr):
            bty = self._quant_binder_whyml(expr.get("binder_type"))
            saved = self._push_quant_binder(expr.get("var"), expr.get("binder_type"))
            body = self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)
            # M4: when lowering an opt-in `#@ propagate_frame` quantified frame
            # (`_frame_trigger_active`), pin a SPECIFIC trigger on the post-state term X of
            # `X == \old(X)` — but ONLY when X is a function APPLICATION (a decode like
            # `slot_inode self.disk x0 k`), whose trigger fires on `slot_inode` terms alone,
            # not on raw `self.disk[i]` bounds reads. Bare the term (Why3 mis-parses `[(t)]`).
            trig = ""
            if getattr(self, "_frame_trigger_active", False):
                tt = self._frame_trigger_term(expr['body'])
                if isinstance(tt, dict) and tt.get("type") == "Call":
                    _tl = self._expr_to_whyml(tt, local_refs, invariant_ctx, subst)
                    trig = f" [{self._strip_outer_parens(_tl)}]"
            self._pop_quant_binder(expr.get("var"), saved)
            return f"(forall {node.var} : {bty}{trig}. {body})"
        if isinstance(node, ExistsExpr):
            bty = self._quant_binder_whyml(expr.get("binder_type"))
            saved = self._push_quant_binder(expr.get("var"), expr.get("binder_type"))
            body = self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)
            self._pop_quant_binder(expr.get("var"), saved)
            return f"(exists {node.var} : {bty}. {body})"
        if isinstance(node, ForallItemsExpr):
            # 07-1311 Q3: `\forall k, v in d.items(); P` → over the map+option model,
            # `forall k. match Map.get d k with Some v -> P | None -> true end`. The value
            # `v` is bound by the match; the key `k` (int) by the outer forall. Register
            # the map binder so a nested `d2[k]` in the body still lowers correctly.
            key, val = expr["key"], expr["val"]
            body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
            return (f"(forall {key} : int. match Map.get ({expr['map']}) ({key}) with "
                    f"| Some {val} -> {body} | None -> true end)")
        if isinstance(node, MapValueIsExpr):
            # 07-1311 Q3: `\exists k. d[k] = Some v` — the value-membership witness for
            # `\forall v in d.values(); …`. A pure logic term over the `map`+`option` model.
            key = self._expr_to_whyml(expr["key"], local_refs, invariant_ctx, subst)
            val = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx, subst)
            return f"(Map.get ({expr['map']}) ({key}) = Some ({val}))"
        if isinstance(node, DictLitExpr):
            # typing-engagement ty2 / 29-1700-typing-spec-5 §2.2 T8: a dict
            # literal `{"x": 1, "y": 2}` in a TypedDict construction context
            # (the enclosing function/assignment target is a TypedDict record)
            # lowers to a record literal `{ x = 1; y = 2 }`. The static plane
            # is Interpreted (record-literal type-checking); the runtime plane
            # is the plain-dict alias (Shimmed) — no blend. Non-TypedDict dict
            # literals fall through to the existing empty-map stub (byte-
            # identical).
            td_lit = self._typeddict_record_literal(expr, local_refs,
                                                    invariant_ctx, subst)
            if td_lit is not None:
                return td_lit
            # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): a COMPOUND
            # statement-node construction `{"stmt": "While"/"If"/"For", ...}`
            # (the `_process_while`/`_process_if`/`_process_for` RETURN dict)
            # lowers to its `stmt_ir` constructor `(SWhile <test> (seq_to_sl
            # <body>))` — the sub-body list materialized to `stmt_list`. Only the
            # compound kinds are hooked here (nullary/return/expr appends still
            # lower at the `.append` site); gated on @mutable_state (emitter model)
            # so every other dict literal (and the whole corpus) is byte-identical.
            stmt_node = self._lower_stmt_ir_construction(
                expr, local_refs, invariant_ctx, subst)
            if stmt_node is not None:
                return stmt_node
            # typed-ir-for-b-ceiling.md B-C1: an inline IR-node construction
            # `{"type": "Var", "name": e}` lowers to the typed `exprir` constructor
            # `(EVar <e>)`, not a heterogeneous map — so it unifies with a real ExprIR
            # field at a sibling that takes both. Gated on @mutable_state (the emitter
            # model); byte-identical for every other dict literal.
            irnode = self._lower_irnode_construction(expr, local_refs, invariant_ctx, subst)
            if irnode is not None:
                return irnode
            # Body dict literal: empty `map int (option int)`. Non-empty
            # dict literals would need element-by-element `Map.set` but
            # are currently uncommon enough to fall through to empty.
            # TODO: handle `{k1: v1, k2: v2}` by chaining Map.set.
            return "(const (None: option int))"
        if isinstance(node, ListCompExpr):
            # pyconst_val bytes content-comprehension (self-tcb-reduction M5, B-bucket):
            # `[{"type":"Number","value":b} for b in expr.value]` — the bytes-literal branch
            # of `_py_expr_constant` — iterates a `pyconst_val`-typed `.value` field (a
            # PVBytes byte sequence) building one `IrNum b` per byte. Lowers to
            # `(bytes_content_comp (pvbytes_of expr.value))` : irlist, the per-byte content
            # law (preamble.py `bytes_content_comp` val: `irnth i result = IrNum (Seq.get s
            # i)` + exact length). NON-FACADE: a real content law over the real byte payload,
            # not an opaque length-only stub. Tried FIRST (its pyconst_val source matches no
            # other comprehension path). Corpus-inert: only a pyconst_val source triggers it.
            _pv_bytes = self._pyconst_bytes_comp(node, local_refs, invariant_ctx, subst)
            if _pv_bytes is not None:
                return _pv_bytes
            # cleared-array.md S1–S4: FIRST try the CONTENT-faithful path for a
            # simple, sound element shape (identity / pure-int arithmetic over the
            # loop target, over an `array int` source). Emits a per-instance
            # `list_content_comp_<n>` val carrying `Array.length result = len src`
            # /\ `forall i. result[i] = <elt[target:=src[i]]>` (or a length bound
            # for a filter). Falls through to the opaque length-only path below for
            # every unliftable element shape (seq/stmt-list/emit_ir/string/call/
            # projection with captures) — DOCUMENTED, never a false content claim.
            _content = self._content_comp(node, local_refs, invariant_ctx, subst)
            if _content is not None:
                return _content
            # faithful-string-op.md §3.4 (whole-list) / M2-split-comp-return: a
            # `[<str-elt> for t in <string>.split(sep)]` comprehension is a faithful
            # `array string` (opaque, length >= 0) — the whole-list counterpart of the
            # split-ELEM path. Tried BEFORE the @mutable_state opaque-length path below:
            # under @mutable_state, `<string>.split(sep)` used as a bare expression lowers
            # to a `seq string` (CF5, `snapshot`-wrapped) for REASSIGNABLE-list use, but a
            # comprehension whose SOURCE is directly a `.split(...)` call needs the
            # materialized `array string` shape (matches an `array string`-typed return/
            # local) — `list_comp_string` over the CF5 `seq string` source would leave a
            # seq/array mismatch at the declared type. Tightly gated on the split shape +
            # string element (`_split_comp_array_string`), so a non-split / int
            # comprehension is unaffected and falls through unchanged (byte-identical) —
            # for a non-@mutable_state class this is the same call the tail branch used to
            # make (pure reordering, no behavior change); the corpus has no @mutable_state
            # classes, so this is corpus-byte-inert either way.
            _split_arr = self._split_comp_array_string(node, local_refs, invariant_ctx, subst)
            if _split_arr is not None:
                return _split_arr
            # list-comprehension-lowering.md L1: a comprehension `[elt for t in src (if …)]`
            # → an abstract array of the ELEMENT type with a length law (`= len src` with no
            # filter, `<= len src` with an `if`). Content is unmodeled (sound under-approx —
            # like str_split_elem_op); only the type + length matter for the emitter's
            # `ensures True` + frame contracts. @mutable_state-gated → the corpus's opaque
            # `list_comp` path is byte-identical.
            # cap4/cap5 (self-tcb-reduction `_refine_tuple_return_type`): the three
            # comprehensions of the tuple-slot dispatcher —
            #   slots  = [_infer_tuple_slot_type(e, …) for e in elts]   (elt -> string)
            #   _names = [e.get("name") if … else None for e in elts]   (string-or-None)
            #   _s     = [_slot_role.get(n, "int") for n in _names]      (map .get -> string)
            # are all `array string` abstractions (length law over the source, content
            # unmodeled — same faithful over-approx as `str_split_elem_op`). Enter the same
            # opaque-array-of-<et> path even though FunctionEmissionMixin is opaque-int (not
            # @mutable_state); `_et` is forced "string" just below. Gated on the method ->
            # byte-inert for the corpus and every other mirror.
            if (getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())
                    or self._emitting_refine_tuple_return_type()
                    or self._emitting_build_param_list()):
                _d = node.to_dict()
                _elt = _d.get("elt", {})
                _gens = _d.get("generators", []) or []
                # IR2: bind each generator target to its iterable's element class (e.g. a
                # `sharedvar` for `sv in self.ir.get("shared_vars")`) so the element expr
                # `sv["name"]` is typed. Restored after inference (the comprehension is opaque).
                _symtab = getattr(self, "_current_symbol_table", None)
                _saved = {}
                if _symtab is not None:
                    for _g in _gens:
                        _ec = self._iter_elem_class(_g.get("iter", {}))
                        _tv = _g.get("target")
                        if _ec and isinstance(_tv, str):
                            _saved[_tv] = _symtab.get(_tv)
                            _symtab[_tv] = _ec
                # a `.to_dict()` element is an emit_ir node (to_dict is identity on the typed IR).
                _elt_todict = (isinstance(_elt, dict) and _elt.get("type") == "Call"
                               and isinstance(_elt.get("func"), str)
                               and _elt["func"].endswith(".to_dict"))
                if self._emitting_refine_tuple_return_type():     _et = "string"
                elif self._is_string_expr(_elt):                  _et = "string"
                elif _elt_todict or self._is_emit_ir_expr(_elt):  _et = "emit_ir"
                else:                                             _et = "int"
                for _tv, _old in _saved.items():
                    if _old is None: _symtab.pop(_tv, None)
                    else: _symtab[_tv] = _old
                _src = _gens[0].get("iter", {}) if _gens else {}
                _has_if = any(g.get("ifs") for g in _gens)
                _srcw = self._expr_to_whyml(_src, local_refs or set(), invariant_ctx, subst)
                # seq-model-pivot.md SQ4: `[s.to_dict() for s in <stmt-list>]` re-materialises a
                # STMT LIST — the plumbing type is `array int` (what `_stmts_to_whyml` consumes),
                # so this comprehension produces `array int` (opaque) to unify with it, over a
                # seq OR array source.
                if _elt_todict:
                    _sc = "seq 'a" if (isinstance(_src, dict) and _src.get("type") == "Var"
                                       and _src.get("name") in getattr(self, "_seq_locals", set())) else "array 'a"
                    self._add_abstract_op(f"val list_comp_stmts (src: {_sc}) : array int")
                    return f"(list_comp_stmts {_srcw})"
                # seq-model-pivot.md SQ4: over a SEQ iterable → the seq-variant comprehension
                # (`seq 'a → seq <τ>`), so the result is a pure reassignable value.
                _src_seq = (isinstance(_src, dict) and _src.get("type") == "Var"
                            and _src.get("name") in getattr(self, "_seq_locals", set()))
                # cap4/5 (self-tcb-reduction `_refine_tuple_return_type`): the three
                # tuple-slot comprehensions are `seq string` abstractions (an immutable,
                # reassignable list model) over a source that may be int (`elts` is
                # `_first_tuple_return_elts`'s opaque int stub) OR `seq string` (`_s`'s source
                # is the `_names` comprehension result). A polymorphic-source variant
                # (`src: 'a`) tolerates both (content unmodeled, length unconstrained — the
                # same faithful over-approx as str_split_elem_op). Method-gated -> corpus/
                # other-mirror byte-inert.
                if (self._emitting_refine_tuple_return_type()
                        or self._emitting_build_param_list()):
                    # `_build_param_list` reuses the `seq string` list-comp abstraction for
                    # `args = [v for v in self._formal_params if v not in ghost_vars]` — a
                    # length-only over-approx (content unmodeled) over the real `seq string`
                    # `formal_params_of self` source (non-vacuous). Method-gated -> inert.
                    self._add_abstract_op(
                        "val list_comp_refine_string (src: 'a) : seq string")
                    return f"(list_comp_refine_string {_srcw})"
                _coll = "seq" if _src_seq else "array"
                _len = "Seq.length" if _src_seq else "Array.length"
                _op = f"list_comp_{'seq_' if _src_seq else ''}{_et}" + ("_filt" if _has_if else "")
                _law = "<=" if _has_if else "="
                self._add_abstract_op(
                    f"val {_op} (src: {_coll} 'a) : {_coll} {_et}\n"
                    f"    ensures {{ {_len} result {_law} {_len} src }}")
                return f"({_op} {_srcw})"
            # M2-split-comp-return: the split-shape comprehension is now tried earlier
            # (right after `_content_comp`, before this @mutable_state branch) — see the
            # comment there. Anything reaching this point is a non-split (or non-string-
            # element) comprehension: opaque int `list_comp`.
            self._add_abstract_op("val list_comp (x: int) : int")
            return "(list_comp 0)"
        if isinstance(node, SetCompExpr):
            # self-tcb-reduction WRITER class (`_build_param_list`): the ref-params
            # comprehension `{v for v in symbol_table if v in local_refs and
            # v.startswith("obj_")}` is a `seq string` FILTER over the symbol-table sequence
            # — the elements kept are drawn from `symbol_table` (a member of the source), so
            # the abstract op's `ensures` states exactly that (a satisfiable, non-vacuous
            # over-approx; content-of-filter unmodeled, like `str_split_elem_op`). The op
            # takes the source AND the membership set AND the prefix literal so every data
            # input the filter reads (`symbol_table`, `local_refs`, `"obj_"`) is referenced —
            # no erased param, mutation-visible. Gated -> byte-inert elsewhere.
            if self._emitting_build_param_list():
                _d = node.to_dict()
                _gens = _d.get("generators", []) or []
                _src = _gens[0].get("iter", {}) if _gens else {}
                _srcw = self._expr_to_whyml(
                    _src if isinstance(_src, dict) else {}, local_refs or set(),
                    invariant_ctx, subst)
                _mems: List[str] = []
                _prefixes: List[str] = []

                def _scan_filter(_n: Any) -> None:
                    if isinstance(_n, dict):
                        if (_n.get("type") in ("BinOp", "Compare")
                                and _n.get("op") in ("in", "not in")):
                            _r = _n.get("right", {})
                            _mems.append(self._expr_to_whyml(
                                _r if isinstance(_r, dict) else {}, local_refs or set(),
                                invariant_ctx, subst))
                        if (_n.get("type") == "Call"
                                and isinstance(_n.get("func"), str)
                                and _n["func"].endswith(".startswith")):
                            _a = (_n.get("args") or [{}])[0]
                            if isinstance(_a, dict) and _a.get("type") == "String":
                                _prefixes.append(self._whyml_string_literal(_a.get("value", "")))
                        for _v in _n.values():
                            _scan_filter(_v)
                    elif isinstance(_n, list):
                        for _v in _n:
                            _scan_filter(_v)
                for _g in _gens:
                    _scan_filter(_g.get("ifs", []) or [])
                _mem_args = "".join(f" (m{_i}: seq string)" for _i in range(len(_mems)))
                _pre_args = "".join(f" (p{_i}: string)" for _i in range(len(_prefixes)))
                self._add_abstract_op(
                    f"val set_comp_seq_str (src: seq string){_mem_args}{_pre_args} : seq string\n"
                    "    ensures { forall _i:int. 0 <= _i < Seq.length result ->\n"
                    "      (exists _j:int. 0 <= _j < Seq.length src"
                    " /\\ Seq.get src _j = Seq.get result _i) }")
                return (f"(set_comp_seq_str {_srcw}"
                        + "".join(f" {m}" for m in _mems)
                        + "".join(f" {p}" for p in _prefixes) + ")")
            # cleared-array item 3: content-faithful set comprehension (membership
            # law) for a pure-int element over an `array int` source; opaque
            # otherwise (DOCUMENTED — never a false content claim).
            _sc = self._set_content_comp(node, local_refs, invariant_ctx, subst)
            if _sc is not None:
                return _sc
            self._add_abstract_op("val set_comp (x: int) : int")
            return "(set_comp 0)"
        if isinstance(node, DictCompExpr):
            # cleared-array item 3: content-faithful dict comprehension (per-source
            # membership law) for an IDENTITY key + pure-int value over an `array
            # int` source; opaque otherwise (DOCUMENTED).
            _dc = self._dict_content_comp(node, local_refs, invariant_ctx, subst)
            if _dc is not None:
                return _dc
            self._add_abstract_op("val dict_comp (x: int) : int")
            return "(dict_comp 0)"

        # Non-standard-signature handlers — called explicitly
        if isinstance(node, VarExpr):      return self._handle_var_expr(node, local_refs, subst)
        if isinstance(node, FieldGetExpr): return self._handle_field_get_expr(node, invariant_ctx)

        # All other types via uniform-quad-signature dispatch
        handler = self._EXPR_DISPATCH.get(t)
        if handler:
            if handler in _TYPED_EXPR_HANDLERS:
                tn = node if not isinstance(node, OpaqueExpr) else _expr_from_dict_inner(node.raw)
                return getattr(self, handler)(tn, local_refs, invariant_ctx, subst)
            return getattr(self, handler)(expr, local_refs, invariant_ctx, subst)
        return ""

    def _expr_to_whyml_string_ctx(self, ir: Dict[str, Any], local_refs: Set[str]) -> str:
        """Emit a ghost string expression in string context (handles StrConcat, StringLiteral, ghost string vars)."""
        t = ir.get("type")
        if t == "StrConcat":
            l = self._expr_to_whyml_string_ctx(ir["left"], local_refs)
            r = self._expr_to_whyml_string_ctx(ir["right"], local_refs)
            # Why3 string.String exports 'concat' (not '^' / 'String.(^)', which is unbound) —
            # mirror _handle_strconcat_expr; `String.(^)` here made any `^` in a spec context
            # (check/ensures comparison) emit an unbound symbol.
            return f"(concat {l} {r})"
        if t == "String":
            # Mirror `_expr_to_whyml`'s String case — escape control chars/newlines
            # (this ghost-string-ctx path previously emitted the raw value with NO
            # escaping at all, so a `"` or `\` in a spec-context string would also
            # have produced invalid WhyML).
            return whyml_string_literal(ir.get("value", ""))
        if t == "Var":
            name = ir.get("name", "")
            safe = whyml_ident(name)
            if name in self._ghost_string_vars:
                return f"!{safe}"
            return safe
        # Fall back to generic emit for any other expression
        return self._expr_to_whyml(ir, local_refs)

