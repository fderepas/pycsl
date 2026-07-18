from __future__ import annotations
from frontend import pure_ast as ast
import json
from typing import Any, Dict, List, Optional, Set, Tuple
from errors import PyCSLIRError
from ir_schema import IR_VERSION
from frontend.module5.memoization_rt import MemoizationRTMixin
from frontend.module5.construction_synth import ConstructionSynthMixin
from frontend.module_collect import collect_module_constants, collect_module_globals
from frontend.Module2_Parser import CSLNode, ContractWrapper, Requires, Ensures, LoopInvariant, LoopVariant, BinOp as CSLBinOp, UnaryOp as CSLUnaryOp, Var as CSLVar, Number as CSLNumber, Result as CSLResult, Old as CSLOld, Nothing, FieldAccess as CSLFieldAccess, FieldSubscript as CSLFieldSubscript, GlobalFieldSubscript as CSLGlobalFieldSubscript, Forall, Exists, ArrayLength, InGlobals, InScope, SubscriptAccess, AssignsRegion, Valid, Separated, At as CSLAt, Length2D, Valid2D, FunctionVariant, StringLiteral as CSLStringLiteral, CallExpr, IsSorted, ArrayEq, Permutation, Sum, CSLBool, CSLNone, CSLIn, CSLNotIn, CSLSlice, DictView, ForallItems, ChainedSubscript, GhostArraySetDecl, MkTupleExpr, FstExpr, SndExpr, ProjExpr, CtorTest, CtorPayload, StrConcatExpr, StrLengthExpr, StrSubExpr, GhostCopyExpr, GhostCopyRangeExpr, GhostMakeExpr, MapEmptyExpr, MapGetExpr, MapSetExpr, MapEqExpr, HasKeyExpr, MapRemoveExpr, SetEmptyExpr, SetAddExpr, SetRemoveExpr, SetMemExpr, SetUnionExpr, SetInterExpr, SetDiffExpr, SetCardExpr, SetSubsetExpr, SetEqExpr, NilExpr, ConsExpr, HdExpr, TlExpr, ListLengthExpr, NthExpr, MemExpr, AppendExpr, Act, Given, Complete, Disjoint
def mutable_state(cls): return cls
""  # pycsl
# gating fix (self-tcb-reduction, mirror-only shim): mark the JSON-IR emitter class
# @mutable_state so `node.attr` reads in its `_csl_*` handlers lower via the emit_ir
# ADT projection (`_lower_irnode_construction`), following the expr_ghost_collections.py
# precedent verbatim (fieldless mixin, no dummy field).
@mutable_state
class PyCSLToJSONEmitter(MemoizationRTMixin, ConstructionSynthMixin, ast.NodeVisitor):
    'Walks the Annotated AST and translates it into a JSON-serializable IR.'
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_Module(self, node: ast.Module) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _get_mutex_invariant_ir(self, mutex: str) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _fresh_var(self, prefix: str='_mem') -> str:
        return ""

    _CSL_HANDLERS: int = {CSLBinOp: '_csl_binop', CSLUnaryOp: '_csl_unaryop', CSLFieldAccess: '_csl_field_access', CSLFieldSubscript: '_csl_field_subscript', CSLGlobalFieldSubscript: '_csl_global_field_subscript', CSLVar: '_csl_var', CSLNumber: '_csl_number', CSLStringLiteral: '_csl_string', CSLBool: '_csl_bool', CSLNone: '_csl_none', CSLResult: '_csl_result', CSLOld: '_csl_old', Nothing: '_csl_nothing', Forall: '_csl_forall', ForallItems: '_csl_forall_items', Exists: '_csl_exists', ArrayLength: '_csl_array_length', InGlobals: '_csl_in_globals', InScope: '_csl_in_scope', SubscriptAccess: '_csl_subscript', AssignsRegion: '_csl_assigns_region', Valid: '_csl_valid', Separated: '_csl_separated', CSLAt: '_csl_at', Length2D: '_csl_length2d', Valid2D: '_csl_valid2d', ContractWrapper: '_csl_contract_wrapper', Requires: '_csl_contract_wrapper', Ensures: '_csl_contract_wrapper', LoopInvariant: '_csl_contract_wrapper', LoopVariant: '_csl_contract_wrapper', FunctionVariant: '_csl_function_variant', CallExpr: '_csl_call_expr', IsSorted: '_csl_is_sorted', ArrayEq: '_csl_array_eq', Permutation: '_csl_permutation', Sum: '_csl_sum', CSLIn: '_csl_in', CSLNotIn: '_csl_not_in', CSLSlice: '_csl_slice', ChainedSubscript: '_csl_chained_subscript', MkTupleExpr: '_csl_mktuple', FstExpr: '_csl_fst', SndExpr: '_csl_snd', ProjExpr: '_csl_proj', CtorTest: '_csl_ctor_test', CtorPayload: '_csl_ctor_payload', StrConcatExpr: '_csl_strconcat', StrLengthExpr: '_csl_str_length', StrSubExpr: '_csl_str_sub', GhostCopyExpr: '_csl_ghost_copy', GhostCopyRangeExpr: '_csl_ghost_copy_range', GhostMakeExpr: '_csl_ghost_make', MapEmptyExpr: '_csl_map_empty', MapGetExpr: '_csl_map_get', MapSetExpr: '_csl_map_set', MapEqExpr: '_csl_map_eq', HasKeyExpr: '_csl_has_key', MapRemoveExpr: '_csl_map_remove', SetEmptyExpr: '_csl_set_empty', SetAddExpr: '_csl_set_add', SetRemoveExpr: '_csl_set_remove', SetMemExpr: '_csl_set_mem', SetUnionExpr: '_csl_set_union', SetInterExpr: '_csl_set_inter', SetDiffExpr: '_csl_set_diff', SetCardExpr: '_csl_set_card', SetSubsetExpr: '_csl_set_subset', SetEqExpr: '_csl_set_eq', NilExpr: '_csl_nil', ConsExpr: '_csl_cons', HdExpr: '_csl_hd', TlExpr: '_csl_tl', ListLengthExpr: '_csl_list_length', NthExpr: '_csl_nth', MemExpr: '_csl_mem', AppendExpr: '_csl_append'}
    # self-tcb-reduction spike (csl-ast-as-emit_ir): param+return retyped `CSLNode`/`int`
    # -> `"ExprIR"` so the recursive dispatcher's signature is `emit_ir -> emit_ir`
    # (matches `_field_type_from_annotation_inst`'s `_irnode_ann_name` recognition and
    # `_symtype_to_whyml`'s param-side mapping). Stays \trusted (body unchanged) — this
    # is a signature-only retype, not a body conversion.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_to_ir(self, node: "ExprIR") -> "ExprIR":
        return {}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_binop(self, node: CSLBinOp) -> Dict[str, Any]:
        return {"type": "BinOp", "op": node.op,
                "left": self._csl_to_ir(node.left), "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_unaryop(self, node: CSLUnaryOp) -> Dict[str, Any]:
        return {"type": "UnaryOp", "op": node.op, "expr": self._csl_to_ir(node.expr)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_field_access(self, node: CSLFieldAccess) -> Dict[str, Any]:
        # no-more-int-2 Track 3: `self.f` is a FieldGet; `p.f` on a record-typed param is an
        # Attribute (routed through _handle_attribute_expr, which reads a record param directly).
        # 07-0903 W2: `\result.<field>` — field access on a record-returning function's
        # result. Carry a Result receiver so Module6 emits `result.<field_label>`.
        if node.object == "\\result":
            return {"type": "Attribute",
                    "object": {"type": "Result"}, "attr": node.field}
        if node.object != "self":
            return {"type": "Attribute",
                    "object": {"type": "Var", "name": node.object}, "attr": node.field}
        return {"type": "FieldGet", "object": node.object, "field": node.field}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_field_subscript(self, node: CSLFieldSubscript) -> Dict[str, Any]:
        return {"type": "Subscript",
                "value": {"type": "FieldGet", "object": "self", "field": node.field},
                "index": self._csl_to_ir(node.index)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_global_field_subscript(self, node: CSLGlobalFieldSubscript) -> Dict[str, Any]:
        return {"type": "Subscript",
                "value": {"type": "Attribute",
                          "object": {"type": "Var", "name": node.obj},
                          "attr": node.field},
                "index": self._csl_to_ir(node.index)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_var(self, node: CSLVar) -> Dict[str, Any]:
        return {"type": "Var", "name": node.name}

    # cleanup batch (no-more-int doctrine): `node` is a CSLNumber record whose `value`
    # field is `float` → `real`. The single-return construction `{"type": "Number",
    # "value": node.value}` lowers (expressions.py `_lower_irnode_construction` Number
    # branch) to `(IrNumF node.value)` — the NEW `IrNumF real` leaf reading node's real
    # field. Distinct from the int-literal `IrNum` (`_py_expr_name`'s `Number 0`). NO
    # dropped field, NO opaque val. Verbatim body port of the LIVE `_csl_number`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_number(self, node: CSLNumber) -> Dict[str, Any]:
        return {"type": "Number", "value": node.value}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_string(self, node: CSLStringLiteral) -> Dict[str, Any]:
        return {"type": "String", "value": node.value}

    # cleanup batch: `node` is a CSLBool record whose `value` field is `bool` → `int`
    # (bool-as-int convention). The single-return construction `{"type": "Bool",
    # "value": node.value}` lowers (expressions.py `_IRNODE_CTORS["Bool"]`) to the NEW
    # `IrBoolC int` leaf `(IrBoolC node.value)`, reading node's int field. NO dropped
    # field, NO opaque val. Verbatim body port of the LIVE `_csl_bool`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_bool(self, node: CSLBool) -> Dict[str, Any]:
        return {"type": "Bool", "value": node.value}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_none(self, node: CSLNone) -> Dict[str, Any]:
        return {"type": "None"}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_result(self, node: CSLResult) -> Dict[str, Any]:
        return {"type": "Result"}

    # isinstance-on-CSL-class recognizer (self-tcb-reduction M5): `node` is a CSLOld
    # record whose `expr` field is retyped `emit_ir` (Module2_Parser.py). The TRUE
    # branch `isinstance(node.expr, CSLFieldAccess)` lowers to `is_fieldget node.expr`
    # (CSLFieldAccess is modeled as IrFieldGet — its raw (object:str, field:str) shape),
    # via the `_CSL_CLASS_TO_IR_KIND` bare-class sibling of the ast.<Node> recognizer;
    # the `{"type":"OldField","object":node.expr.object,"field":node.expr.field}`
    # construction reads the two leaf strings via `fgobject_of`/`field_of`
    # (`_EMIT_IR_HANDLER_ATTR_PROJ["_csl_old"]`) and builds `IrOldField string string`.
    # The FALSE branch builds `IrOld (csl_to_ir node.expr)`. Verbatim body port of the
    # LIVE `_csl_old`; NO opaque val, NO dropped field.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_old(self, node: CSLOld) -> Dict[str, Any]:
        if isinstance(node.expr, CSLFieldAccess):
            return {"type": "OldField", "object": node.expr.object, "field": node.expr.field}
        return {"type": "Old", "expr": self._csl_to_ir(node.expr)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_nothing(self, node: Nothing) -> Dict[str, Any]:
        return {"type": "Nothing"}

    # optional-field builder (monomorphic-option ADTs): `node` is a Forall record
    # whose `body` field is `emit_ir` and whose `binder_type`/`domain` fields are
    # `option string`/`option emit_ir` (Module2_Parser.py retype). The mutable-dict-
    # conditional-add body `d = {..}; if getattr(node,F,None) is not None: d[F]=V;
    # return d` lowers (functions.py `_recognize_optfield_builder`, expressions.py
    # `_lower_quant_optfield`) to `(IrForall node.var (csl_to_ir node.body)
    # <iropt_str from binder_type> <iropt_ir mapping csl_to_ir over domain>)` — the
    # optionals READ from node's option fields and converted to the monomorphic
    # `iropt_str`/`iropt_ir` at the ctor arg (NO dropped field, NO opaque val).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_forall(self, node: Forall) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": "Forall", "var": node.var, "body": self._csl_to_ir(node.body)}
        if getattr(node, "binder_type", None) is not None:
            d["binder_type"] = node.binder_type
        if getattr(node, "domain", None) is not None:
            d["domain"] = self._csl_to_ir(node.domain)
        return d

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_forall_items(self, node: ForallItems) -> Dict[str, Any]:
        return {"type": "ForallItems", "key": node.key, "val": node.val,
                "map": node.coll, "body": self._csl_to_ir(node.body)}

    # optional-field builder (monomorphic-option ADTs): identical shape to
    # `_csl_forall` over the Exists node — lowers to `(IrExists node.var
    # (csl_to_ir node.body) <iropt_str> <iropt_ir>)`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_exists(self, node: Exists) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": "Exists", "var": node.var, "body": self._csl_to_ir(node.body)}
        if getattr(node, "binder_type", None) is not None:
            d["binder_type"] = node.binder_type
        if getattr(node, "domain", None) is not None:
            d["domain"] = self._csl_to_ir(node.domain)
        return d

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_array_length(self, node: ArrayLength) -> Dict[str, Any]:
        return {"type": "ArrayLen", "var": node.var}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_in_globals(self, node: InGlobals) -> Dict[str, Any]:
        return {"type": "InGlobals", "name": node.name}   # 07-1839 P2

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_in_scope(self, node: InScope) -> Dict[str, Any]:
        return {"type": "InScope", "name": node.name}     # 07-1839 P3

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_subscript(self, node: SubscriptAccess) -> Dict[str, Any]:
        if node.array == "\\result":
            return {"type": "Subscript",
                    "value": {"type": "Result"},
                    "index": self._csl_to_ir(node.index)}
        return {"type": "Subscript",
                "value": {"type": "Var", "name": node.array},
                "index": self._csl_to_ir(node.index)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_chained_subscript(self, node: ChainedSubscript) -> Dict[str, Any]:
        inner = {"type": "Subscript",
                 "value": {"type": "Var", "name": node.array},
                 "index": self._csl_to_ir(node.index1)}
        return {"type": "Subscript",
                "value": inner,
                "index": self._csl_to_ir(node.index2)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_assigns_region(self, node: AssignsRegion) -> Dict[str, Any]:
        return {"type": "AssignsRegion", "base": node.base,
                "low": self._csl_to_ir(node.low), "high": self._csl_to_ir(node.high)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_valid(self, node: Valid) -> Dict[str, Any]:
        return {"type": "Valid", "base": node.base, "length": self._csl_to_ir(node.length)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_separated(self, node: Separated) -> Dict[str, Any]:
        return {"type": "Separated", "base1": node.base1,
                "len1": self._csl_to_ir(node.length1),
                "base2": node.base2, "len2": self._csl_to_ir(node.length2)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_at(self, node: CSLAt) -> Dict[str, Any]:
        return {"type": "At", "expr": self._csl_to_ir(node.expr), "label": node.label}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_length2d(self, node: Length2D) -> Dict[str, Any]:
        return {"type": "Length2D", "base": node.base,
                "rows": self._csl_to_ir(node.rows), "cols": self._csl_to_ir(node.cols)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_valid2d(self, node: Valid2D) -> Dict[str, Any]:
        return {"type": "Valid2D", "base": node.base,
                "row": self._csl_to_ir(node.row), "col": self._csl_to_ir(node.col)}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_contract_wrapper(self, node: ContractWrapper) -> int:
        # tcb(M5) FREE-bucket census: BLOCKED, not free. `node.expr` doesn't type-check
        # against the abstract base `ContractWrapper` — it has NO dataclass fields (`class
        # ContractWrapper(CSLNode): pass`); `expr` is declared separately on each of the 4
        # concrete subclasses (Requires/Ensures/LoopInvariant/LoopVariant). `--fun` on the
        # naive passthrough body fails: "unbound function or predicate symbol
        # 'contractwrapper_expr'" — the self-annotate type model has no projector for a
        # field that lives only on subclasses of the declared param type. Unifying it would
        # need new infra (a union/sum discriminator over the 4 concrete types, or moving
        # `expr` onto the base class — a real Module2_Parser.py hierarchy change), which is
        # out of scope for this FREE-bucket increment. Left \trusted.
        return {}

    # optional-field ext (monomorphic-option ADTs): `node` is the imported
    # `FunctionVariant` record whose `expr` field is retyped `"ExprIR"` -> `emit_ir`
    # (Module2_Parser.py) and whose `ordering` is `Optional[str]` -> `option string`.
    # The TYPE-LESS base dict `{"expr": self._csl_to_ir(node.expr)}` + the truthiness-
    # guarded `if node.ordering: ir["ordering"] = node.ordering` lower (functions.py
    # `_recognize_functionvariant_builder` + expressions.py
    # `_lower_functionvariant_optfield`) to the new `IrFunctionVariant emit_ir iropt_str`
    # ctor (preamble.py `_emit_exprir_theory`): expr = `(self._csl_to_ir node.expr)`,
    # ordering = `match node.ordering with Some s -> IrSSome s | None -> IrSNone`
    # (`node.ordering` is a parser `expect_name()` token, never empty → truthiness =
    # presence). Verbatim body port of the LIVE `_csl_function_variant`
    # (Module5_IREmitter.py:661).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_function_variant(self, node: FunctionVariant) -> Dict[str, Any]:
        ir: Dict[str, Any] = {"expr": self._csl_to_ir(node.expr)}
        if node.ordering:
            ir["ordering"] = node.ordering
        return ir

    # variadic content-law comprehension (FABLE-sanctioned), batch 2: `node` is a CSL-AST
    # `CallExpr` record whose `args` field is retyped `List["ExprIR"]` (Module2_Parser.py)
    # -> an `array emit_ir` (the `MkTupleExpr.elts` precedent). `node.func` is the record's
    # `func: str` field (a plain string). The comprehension `[self._csl_to_ir(a) for a in
    # node.args]` lowers (module6_whyml/expressions.py `_content_comp` variadic branch) to
    # `(list_content_comp_N node.args)` : `irlist` carrying BOTH a length law AND a per-index
    # content law over the SHARED `emit_ir_disp__csl_to_ir` `val function` (one symbol per
    # dispatcher, FABLE condition 2). The return builds the new `IrCallN string irlist` ctor
    # (expressions.py `_IRNODE_CTORS["Call"]` + preamble.py `_emit_exprir_theory`). Verbatim
    # body port of the LIVE `_csl_call_expr` (Module5_IREmitter.py:667).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_call_expr(self, node: CallExpr) -> Dict[str, Any]:
        return {"type": "Call", "func": node.func,
                "args": [self._csl_to_ir(a) for a in node.args]}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_is_sorted(self, node: IsSorted) -> Dict[str, Any]:
        return {"type": "IsSorted", "base": node.base,
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_array_eq(self, node: ArrayEq) -> Dict[str, Any]:
        return {"type": "ArrayEq",
                "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_permutation(self, node: Permutation) -> Dict[str, Any]:
        return {"type": "Permutation",
                "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_sum(self, node: Sum) -> Dict[str, Any]:
        return {"type": "Sum", "base": node.base,
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_in(self, node: CSLIn) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_not_in(self, node: CSLNotIn) -> int:
        return {}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_slice(self, node: CSLSlice) -> Dict[str, Any]:
        return {"type": "SliceAccess",
                "value": {"type": "Var", "name": node.collection},
                "slice": {"type": "Slice",
                          "lower": self._csl_to_ir(node.low),
                          "upper": self._csl_to_ir(node.high),
                          "step": None}}

    # variadic content-law comprehension (FABLE-sanctioned): `node` is a MkTupleExpr
    # record whose `elts` field is retyped `List["ExprIR"]` (Module2_Parser.py) -> an
    # `array emit_ir`. The comprehension `[self._csl_to_ir(e) for e in node.elts]` lowers
    # (module6_whyml/expressions.py `_content_comp` variadic branch) to
    # `(list_content_comp_N node.elts)` : `irlist` carrying BOTH a length law AND a
    # per-index content law over the SHARED `emit_ir_disp__csl_to_ir` `val function`
    # (the get_x projection-comprehension precedent, extended to a recursive dispatcher).
    # The whole return builds the new `IrMkTupleN irlist` ctor
    # (expressions.py `_IRNODE_CTORS["MkTuple"]` + preamble.py `_emit_exprir_theory`).
    # The content law pins map STRUCTURE (per-index deterministic function of source), NOT
    # dispatcher value-semantics — honest labeling per FABLE condition 3.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_mktuple(self, node: MkTupleExpr) -> Dict[str, Any]:
        return {"type": "MkTuple", "elts": [self._csl_to_ir(e) for e in node.elts]}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_fst(self, node: FstExpr) -> Dict[str, Any]:
        return {"type": "FstExpr", "tuple": self._csl_to_ir(node.tuple_expr)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_snd(self, node: SndExpr) -> Dict[str, Any]:
        return {"type": "SndExpr", "tuple": self._csl_to_ir(node.tuple_expr)}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_proj(self, node: ProjExpr) -> int:
        return {}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_ctor_test(self, node: CtorTest) -> Dict[str, Any]:
        return {"type": "CtorTest", "var": node.var, "ctor": node.ctor}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_ctor_payload(self, node: CtorPayload) -> Dict[str, Any]:
        return {"type": "CtorPayload", "var": node.var, "ctor": node.ctor,
                "index": getattr(node, "index", 0)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_strconcat(self, node: StrConcatExpr) -> Dict[str, Any]:
        return {"type": "StrConcat", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_str_length(self, node: StrLengthExpr) -> Dict[str, Any]:
        return {"type": "StrLength", "string": self._csl_to_ir(node.string)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_str_sub(self, node: StrSubExpr) -> Dict[str, Any]:
        return {"type": "StrSub", "string": self._csl_to_ir(node.string),
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_ghost_copy(self, node: GhostCopyExpr) -> Dict[str, Any]:
        return {"type": "GhostCopy", "arr": node.arr}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_ghost_copy_range(self, node: GhostCopyRangeExpr) -> Dict[str, Any]:
        return {"type": "GhostCopyRange", "arr": node.arr,
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_ghost_make(self, node: GhostMakeExpr) -> Dict[str, Any]:
        return {"type": "GhostMake", "size": self._csl_to_ir(node.size),
                "default": self._csl_to_ir(node.default)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_map_empty(self, node: MapEmptyExpr) -> Dict[str, Any]:
        return {"type": "MapEmpty"}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_map_get(self, node: MapGetExpr) -> Dict[str, Any]:
        return {"type": "MapGet", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_map_set(self, node: MapSetExpr) -> Dict[str, Any]:
        return {"type": "MapSet", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key), "value": self._csl_to_ir(node.value)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_map_eq(self, node: MapEqExpr) -> Dict[str, Any]:
        return {"type": "MapEq", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_has_key(self, node: HasKeyExpr) -> Dict[str, Any]:
        return {"type": "HasKey", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_map_remove(self, node: MapRemoveExpr) -> Dict[str, Any]:
        return {"type": "MapRemove", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_empty(self, node: SetEmptyExpr) -> Dict[str, Any]:
        return {"type": "SetEmpty"}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_add(self, node: SetAddExpr) -> Dict[str, Any]:
        return {"type": "SetAdd", "set": self._csl_to_ir(node.set_expr),
                "elem": self._csl_to_ir(node.elem)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_remove(self, node: SetRemoveExpr) -> Dict[str, Any]:
        return {"type": "SetRemove", "set": self._csl_to_ir(node.set_expr),
                "elem": self._csl_to_ir(node.elem)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_mem(self, node: SetMemExpr) -> Dict[str, Any]:
        return {"type": "SetMem", "elem": self._csl_to_ir(node.elem),
                "set": self._csl_to_ir(node.set_expr)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_union(self, node: SetUnionExpr) -> Dict[str, Any]:
        return {"type": "SetUnion", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_inter(self, node: SetInterExpr) -> Dict[str, Any]:
        return {"type": "SetInter", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_diff(self, node: SetDiffExpr) -> Dict[str, Any]:
        return {"type": "SetDiff", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_card(self, node: SetCardExpr) -> Dict[str, Any]:
        return {"type": "SetCard", "set": self._csl_to_ir(node.set_expr),
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_subset(self, node: SetSubsetExpr) -> Dict[str, Any]:
        return {"type": "SetSubset", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_set_eq(self, node: SetEqExpr) -> Dict[str, Any]:
        return {"type": "SetEq", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_nil(self, node: NilExpr) -> Dict[str, Any]:
        return {"type": "Nil"}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_cons(self, node: ConsExpr) -> Dict[str, Any]:
        return {"type": "Cons", "head": self._csl_to_ir(node.head),
                "tail": self._csl_to_ir(node.tail)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_hd(self, node: HdExpr) -> Dict[str, Any]:
        return {"type": "Hd", "list": self._csl_to_ir(node.list_expr)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_tl(self, node: TlExpr) -> Dict[str, Any]:
        return {"type": "Tl", "list": self._csl_to_ir(node.list_expr)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_list_length(self, node: ListLengthExpr) -> Dict[str, Any]:
        return {"type": "ListLength", "list": self._csl_to_ir(node.list_expr)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_nth(self, node: NthExpr) -> Dict[str, Any]:
        return {"type": "Nth", "list": self._csl_to_ir(node.list_expr),
                "index": self._csl_to_ir(node.index)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_mem(self, node: MemExpr) -> Dict[str, Any]:
        return {"type": "Mem", "elem": self._csl_to_ir(node.elem),
                "list": self._csl_to_ir(node.list_expr)}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_append(self, node: AppendExpr) -> Dict[str, Any]:
        return {"type": "Append", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_list_to_ir(self, csl_list: List[CSLNode]) -> List[int]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _comprehension_generators_to_ir(self, generators: List[ast.comprehension]) -> List[int]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_op_to_str(self, op: ast.operator | ast.cmpop | ast.unaryop) -> str:
        return ""

    _PY_EXPR_HANDLERS: int = {ast.Name: '_py_expr_name', ast.Constant: '_py_expr_constant', ast.UnaryOp: '_py_expr_unaryop', ast.BinOp: '_py_expr_binop', ast.Compare: '_py_expr_compare', ast.BoolOp: '_py_expr_boolop', ast.Call: '_py_expr_call', ast.Tuple: '_py_expr_tuple', ast.Subscript: '_py_expr_subscript', ast.List: '_py_expr_list', ast.Attribute: '_py_expr_attribute', ast.Dict: '_py_expr_dict', ast.Set: '_py_expr_set', ast.ListComp: '_py_expr_listcomp', ast.SetComp: '_py_expr_setcomp', ast.DictComp: '_py_expr_dictcomp', ast.JoinedStr: '_py_expr_fstring', ast.IfExp: '_py_expr_ifexp', ast.Starred: '_py_expr_starred', ast.NamedExpr: '_py_expr_walrus', ast.Lambda: '_py_expr_lambda', ast.Slice: '_py_expr_slice'}
    # py-expr-structural-dep-wall-response.md piece 3: param+return retyped `int`
    # -> `"ExprIR"` (the `_csl_to_ir` precedent, line ~58) so the recursive
    # dispatcher's signature is `emit_ir -> emit_ir`, matching
    # `_field_type_from_annotation_inst`'s `_irnode_ann_name` recognition and
    # `_symtype_to_whyml`'s param-side mapping. Stays \trusted (body unchanged) —
    # signature-only retype, not a body conversion.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_to_ir(self, expr: "ExprIR") -> "ExprIR":
        return {}

    # _py_expr multi-branch batch (mini-M1): `expr` is a pure_ast Name node,
    # cross-file (ir_resolve.py `_resolve_pure_ast_param_records`) retyped from
    # the opaque `Any`->int fallback to the structurally-harvested `Name` record
    # (fields `id`:string, `ctx`:int). Verbatim body port of the LIVE
    # `_py_expr_name` (Module5_IREmitter.py:985) — a STRING-guarded 3-branch
    # dispatch on `expr.id` (`== "Ellipsis"` / `== "None"`). The 3 early-return
    # emit_ir literals travel through the pre-existing `Return_emit_ir` exception
    # (module6_whyml/statements.py `_wrap_body_with_return_catch`); each builds a
    # pre-existing ctor — IrNum 0 / IrNone / IrVar (reading `expr.id`) — NO new
    # emit_ir theory constructor.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_name(self, expr: ast.Name) -> "ExprIR":
        if expr.id == "Ellipsis":
            return {"type": "Number", "value": 0}
        if expr.id == "None":
            return {"type": "None"}
        return {"type": "Var", "name": expr.id}

    # pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): `expr` is a
    # pure_ast Constant node, cross-file (ir_resolve.py `_resolve_pure_ast_param_records`)
    # retyped from the opaque `Any`->int fallback to the structurally-harvested `Constant`
    # record whose `value` field is the NEW `pyconst_val` discriminated union (the missing
    # value-type-discrimination named in the resolver's historical "_py_expr_constant
    # blocked" note). Verbatim body port of the LIVE `_py_expr_constant`
    # (Module5_IREmitter.py:992). Each INPUT-side value-type test lowers to a `pyconst_val`
    # discriminant: `expr.value is None`->`is_pvnone`, `isinstance(expr.value, bool/str/
    # bytes/complex)`->`is_pvbool/is_pvstr/is_pvbytes/is_pvcomplex`, `expr.value is ...`
    # (Module5-collapsed to `== 0`)->`is_pvellipsis`; each value read projects via the total
    # `pv*_of` accessors (`pvstr_of`/`pvint_of`/`pvbool_of`-as-int/`pvreal_of`+`real_trunc`);
    # the bytes comprehension builds `IrListN (bytes_content_comp (pvbytes_of expr.value))`
    # (module6_whyml/expressions.py `_handle_isinstance`/the `is None` handler/`_pyconst_bytes_comp`
    # + preamble.py `_emit_exprir_theory`). Co-landed with the axiom-free Rocq+Lean
    # certificate (Phase2c_PyConstVal.v / PyConstVal.lean).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_constant(self, expr: ast.Constant) -> Dict[str, Any]:
        if expr.value is None:
            return {"type": "None"}
        if isinstance(expr.value, bool):
            return {"type": "Bool", "value": expr.value}
        if isinstance(expr.value, str):
            return {"type": "String", "value": expr.value}
        if isinstance(expr.value, bytes):
            # Per missing-bytes-struct-feature.md Phase 1: bytes
            # literals lower to ArrayLit of int (one element per
            # byte, 0..255). This lets the existing array-int
            # emission path absorb them, and b'\x00' * N composes
            # cleanly with the BinOp [default] * size → Array.make
            # handler in expressions.py.
            return {
                "type": "ArrayLit",
                "elts": [{"type": "Number", "value": b}
                         for b in expr.value],
            }
        if expr.value is ...:
            return {"type": "Number", "value": 0}
        if isinstance(expr.value, complex):
            return {"type": "Number", "value": int(expr.value.real)}
        return {"type": "Number", "value": expr.value}

    # non-list _py_expr_* batch (tier 1): `expr` is a pure_ast UnaryOp node,
    # cross-file (ir_resolve.py `_resolve_pure_ast_param_records`) retyped from
    # the opaque `Any`->int fallback to the structurally-harvested `UnaryOp`
    # record. Verbatim body port of the LIVE `_py_expr_unaryop`
    # (Module5_IREmitter.py:1017).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_unaryop(self, expr: ast.UnaryOp) -> int:
        return {"type": "UnaryOp", "op": self._py_op_to_str(expr.op),
                "expr": self._py_expr_to_ir(expr.operand)}

    # py-expr-structural-dep-wall-response.md spike: `expr` is a pure_ast BinOp
    # node, cross-file (ir_resolve.py `_resolve_pure_ast_param_records`) retyped
    # from the opaque `Any`->int fallback to the structurally-harvested `binop`
    # record (piece 1/2/3 — see ir_resolve.py). Verbatim body port of the LIVE
    # `_py_expr_binop` (Module5_IREmitter.py:1021).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_binop(self, expr: ast.BinOp) -> int:
        return {"type": "BinOp", "op": self._py_op_to_str(expr.op),
                "left": self._py_expr_to_ir(expr.left), "right": self._py_expr_to_ir(expr.right)}

    # _py_expr_compare increment (self-tcb-reduction M5, C-bucket): a RETURN-value expr
    # handler. A bespoke Module6 lowering (functions.py `_emit_py_expr_compare_bespoke`,
    # keyed on the method name under `_uses_stmt_ir`) emits it FAITHFULLY as the certified
    # `IrBinOp` ctor. `expr` param -> the typed `py_compare_node`; the ast-LIST-HEAD
    # accesses `expr.ops[0]` / `expr.comparators[0]` -> the opaque head readers
    # `compare_op0_ast` / `compare_comp0_ast` (the same shape as `_py_stmt_assign`'s
    # `stmt.targets[0]`); `expr.left` -> `compare_left_ast`. The op -> `py_op_to_str
    # (compare_op0_ast expr)` (`_py_op_to_str` stays \trusted), left/right ->
    # `_py_expr_to_ir`. No new ctor (reuses the certified IrBinOp). isinstance_op = 0.
    # Verbatim body port of the LIVE `_py_expr_compare`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_compare(self, expr: ast.Compare) -> int:
        return {"type": "BinOp", "op": self._py_op_to_str(expr.ops[0]),
                "left": self._py_expr_to_ir(expr.left),
                "right": self._py_expr_to_ir(expr.comparators[0])}

    # _py_expr_boolop increment (self-tcb-reduction M5, C-bucket): a RETURN-value expr
    # handler with a LEFT-FOLD. A bespoke Module6 lowering (functions.py
    # `_emit_py_expr_boolop_bespoke`, keyed on the method name under `_uses_stmt_ir`) emits
    # it FAITHFULLY: `isinstance(expr.op, ast.And)` -> `boolop_is_and expr`; `expr.values[0]`
    # -> `boolop_val0_ast`; the `for operand in expr.values[1:]: result = {BinOp,...}` LEFT-
    # FOLD -> the CONCRETE recursive `boolop_fold` over the `expr.values[1:]` irlist
    # (`boolop_rest_ast`), each operand re-lowered by the dispatcher and folded into a
    # left-nested certified IrBinOp tree — NOT an abstract length-only law (the fable vacuity
    # trap). No new ctor (reuses IrBinOp). isinstance_op = 0. Verbatim body port of the LIVE
    # `_py_expr_boolop`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_boolop(self, expr: ast.BoolOp) -> int:
        op_str = "and" if isinstance(expr.op, ast.And) else "or"
        result = self._py_expr_to_ir(expr.values[0])
        for operand in expr.values[1:]:
            result = {"type": "BinOp", "op": op_str, "left": result,
                      "right": self._py_expr_to_ir(operand)}
        return result

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_call(self, expr: ast.Call) -> int:
        return {}

    # variadic content-law comprehension (FABLE-sanctioned): `expr` is a pure_ast Tuple
    # node, cross-file (ir_resolve.py `_resolve_pure_ast_param_records`) retyped from the
    # opaque `Any`->int fallback to the structurally-harvested `Tuple` record whose `elts`
    # field is a List-of-ExprIR (`_PURE_AST_FIELD_TABLE["Tuple"]`) -> `array emit_ir`. The
    # comprehension `[self._py_expr_to_ir(e) for e in expr.elts]` lowers (expressions.py
    # `_content_comp` variadic branch) to `(list_content_comp_N expr.elts)` : `irlist`
    # with BOTH a length law AND a per-index content law over the SHARED
    # `emit_ir_disp__py_expr_to_ir` `val function` (one symbol per dispatcher, FABLE
    # condition 2). The return builds the new `IrMkTupleN` ctor
    # (expressions.py `_IRNODE_CTORS["Tuple"]`). Verbatim body port of the LIVE
    # `_py_expr_tuple` (Module5_IREmitter.py:1098).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_tuple(self, expr: ast.Tuple) -> Dict[str, Any]:
        return {"type": "Tuple", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}

    # output-side slice-discrimination (self-tcb-reduction M5): `expr` is a pure_ast
    # Subscript node. The LIVE `_py_expr_subscript` (Module5_IREmitter.py) was rewritten
    # from an INPUT-side `isinstance(node.slice, ast.Slice)` test — unmodellable (the
    # harvested pure_ast nodes are opaque records, no common discriminated union) — to the
    # SOUND OUTPUT-side form: lower the slice with the recursive dispatcher
    # `self._py_expr_to_ir(expr.slice)` (recognized as an `emit_ir` local via the
    # `_resolve_dotted_signature == "emit_ir"` recognizer in statements.py
    # `_collect_emit_ir_result_locals`, which types `slice_ir` as ExprIR), then
    # discriminate on the LOWERED slice's kind via `slice_ir.get("type") == "Slice"`. For
    # this @mutable_state mirror the compare lowers (by design, expressions.py ~2513) to the
    # already-proven `str_eq_op (kind_of slice_ir) "Slice"` output-side reflection; the
    # match-based `(is_slice slice_ir)` discriminant (`_KIND_DISCRIMINANT["Slice"]`, landed
    # this batch, preamble.py) is the driver-path (non-@mutable_state) sibling. Either way
    # the two arms build DISTINCT real ctors — `IrSliceAccess value slice_ir`
    # (`_IRNODE_CTORS["SliceAccess"]`) vs `IrSub value slice_ir` (`_IRNODE_CTORS["Subscript"]`),
    # ZERO isinstance_op. Verbatim body port of the LIVE (output-side) `_py_expr_subscript`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_subscript(self, expr: ast.Subscript) -> Dict[str, Any]:
        value = self._py_expr_to_ir(expr.value)
        slice_ir = self._py_expr_to_ir(expr.slice)
        if slice_ir.get("type") == "Slice":
            return {"type": "SliceAccess", "value": value, "slice": slice_ir}
        return {"type": "Subscript", "value": value, "index": slice_ir}

    # variadic content-law comprehension (FABLE-sanctioned), batch 2: `expr` is a pure_ast
    # List node, cross-file (ir_resolve.py `_resolve_pure_ast_param_records`) retyped from
    # the opaque `Any`->int fallback to the structurally-harvested `List` record whose `elts`
    # field is a List-of-ExprIR (`_PURE_AST_FIELD_TABLE["List"]`) -> `array emit_ir`. The
    # comprehension `[self._py_expr_to_ir(e) for e in expr.elts]` lowers (expressions.py
    # `_content_comp` variadic branch) to `(list_content_comp_N expr.elts)` : `irlist` with
    # BOTH a length law AND a per-index content law over the SHARED
    # `emit_ir_disp__py_expr_to_ir` `val function`. The return builds the new `IrListN
    # irlist` ctor (expressions.py `_IRNODE_CTORS["ArrayLit"]`). Verbatim body port of the
    # LIVE `_py_expr_list` (Module5_IREmitter.py:1112).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_list(self, expr: ast.List) -> Dict[str, Any]:
        return {"type": "ArrayLit", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}

    # isinstance-on-emit_ir batch (self-tcb-reduction M5): `expr` is a pure_ast
    # Attribute node, cross-file (ir_resolve.py `_resolve_pure_ast_param_records`)
    # retyped from the opaque `Any`->int fallback to the structurally-harvested
    # `Attribute` record (fields `value`:ExprIR, `attr`:string, `ctx`:int).
    # Verbatim body port of the LIVE `_py_expr_attribute` (Module5_IREmitter.py:1115).
    # The `isinstance(expr.value, ast.Name)` input-side type test on the ExprIR-typed
    # `value` child lowers to the emit_ir ADT discriminant `(is_var expr.value)`
    # (module6_whyml/expressions.py `_handle_isinstance` + `_AST_CLASS_TO_IR_KIND`),
    # `expr.value.id` to `(name_of expr.value)` (`_EMIT_IR_STR_ATTRS["id"]`), and the
    # `obj_ir = self._py_expr_to_ir(expr.value)` local to a `ref (IrOther "")` emit_ir
    # sentinel (statements.py `_collect_emit_ir_result_locals` emit_ir-returning-call
    # recognizer). Returns pre-existing IrFieldGet / IrAttr ctors — NO new theory ctor.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_attribute(self, expr: ast.Attribute) -> "ExprIR":
        if isinstance(expr.value, ast.Name) and expr.value.id == 'self':
            return {"type": "FieldGet", "object": "self", "field": expr.attr}
        obj_ir = self._py_expr_to_ir(expr.value)
        return {"type": "Attribute", "object": obj_ir, "attr": expr.attr}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_dict(self, expr: ast.Dict) -> int:
        return {}

    # variadic content-law comprehension (FABLE-sanctioned), batch 2: `expr` is a pure_ast
    # Set node, cross-file (ir_resolve.py `_resolve_pure_ast_param_records`) retyped from the
    # opaque `Any`->int fallback to the structurally-harvested `Set` record whose single
    # `elts` field is a List-of-ExprIR (`_PURE_AST_FIELD_TABLE["Set"]`) -> `array emit_ir`.
    # The comprehension `[self._py_expr_to_ir(e) for e in expr.elts]` lowers (expressions.py
    # `_content_comp` variadic branch) to `(list_content_comp_N expr.elts)` : `irlist` with
    # BOTH a length law AND a per-index content law over the SHARED
    # `emit_ir_disp__py_expr_to_ir` `val function`. The return builds the new `IrSetN irlist`
    # ctor (expressions.py `_IRNODE_CTORS["SetLit"]`). Verbatim body port of the LIVE
    # `_py_expr_set` (Module5_IREmitter.py:1126).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_set(self, expr: ast.Set) -> Dict[str, Any]:
        return {"type": "SetLit", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_listcomp(self, expr: ast.ListComp) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_setcomp(self, expr: ast.SetComp) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_dictcomp(self, expr: ast.DictComp) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_fstring(self, expr: ast.JoinedStr) -> int:
        return {}

    # _py_expr fixed-child batch (mini-M1): `expr` is a pure_ast IfExp node,
    # cross-file (ir_resolve.py `_resolve_pure_ast_param_records`) retyped from
    # the opaque `Any`->int fallback to the structurally-harvested `IfExp`
    # record. Verbatim body port of the LIVE `_py_expr_ifexp`
    # (Module5_IREmitter.py:1153) — 3 emit_ir children reuse the GENERIC
    # `IrTer3` ctor (module6_whyml/expressions.py `_IRNODE_CTORS["IfExpr"]`),
    # NO new emit_ir theory constructor.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_ifexp(self, expr: ast.IfExp) -> "ExprIR":
        return {"type": "IfExpr", "test": self._py_expr_to_ir(expr.test),
                "body": self._py_expr_to_ir(expr.body),
                "orelse": self._py_expr_to_ir(expr.orelse)}

    # _py_expr fixed-child batch (mini-M1): `expr` is a pure_ast Starred node,
    # cross-file (ir_resolve.py `_resolve_pure_ast_param_records`) retyped from
    # the opaque `Any`->int fallback to the structurally-harvested `Starred`
    # record. Verbatim body port of the LIVE `_py_expr_starred`
    # (Module5_IREmitter.py:1158) — 1 emit_ir child, new `IrStarred` ctor
    # (module6_whyml/preamble.py `_emit_exprir_theory`).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_starred(self, expr: ast.Starred) -> "ExprIR":
        return {"type": "Starred", "value": self._py_expr_to_ir(expr.value)}

    # isinstance-on-emit_ir batch (self-tcb-reduction M5): `expr` is a pure_ast
    # NamedExpr node, cross-file (ir_resolve.py `_resolve_pure_ast_param_records`)
    # retyped from the opaque `Any`->int fallback to the structurally-harvested
    # `NamedExpr` record (fields `target`:ExprIR, `value`:ExprIR). Verbatim body
    # port of the LIVE `_py_expr_walrus` (Module5_IREmitter.py:1161). The
    # `isinstance(expr.target, ast.Name)` input-side type test lowers to
    # `(is_var expr.target)` and `expr.target.id` to `(name_of expr.target)`; the
    # `target_name` string ternary + the new `IrNamedExpr` ctor complete it — NO
    # facade, NO isinstance_op.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_walrus(self, expr: ast.NamedExpr) -> "ExprIR":
        target_name = expr.target.id if isinstance(expr.target, ast.Name) else "_walrus"
        return {"type": "NamedExpr", "target": target_name,
                "value": self._py_expr_to_ir(expr.value)}

    # _py_expr_lambda increment (self-tcb-reduction M5, C-bucket): a RETURN-value expr
    # handler. A bespoke Module6 lowering (functions.py `_emit_py_expr_lambda_bespoke`,
    # keyed on the method name under `_uses_stmt_ir`) emits it FAITHFULLY: `expr` param ->
    # the typed `py_lambda_node`; the `[arg.arg for arg in expr.args.args]` param-name
    # projection -> the CONCRETE `lambda_param_names_prog (lambda_args_ast expr)` compaction
    # (`name_of` over the args irlist -> IrVar param-name nodes, NOT an abstract length-only
    # law); `expr.body` -> `lambda_body_ast` re-lowered by `_py_expr_to_ir`. Returns the new
    # gated `IrLambda <params irlist> <body>` emit_ir ctor (gated on `_uses_stmt_ir` so the
    # corpus emit_ir theory stays byte-identical). isinstance_op = 0. Verbatim body port of
    # the LIVE `_py_expr_lambda`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_lambda(self, expr: ast.Lambda) -> int:
        params = [arg.arg for arg in expr.args.args]
        return {"type": "Lambda", "params": params,
                "body": self._py_expr_to_ir(expr.body)}

    # optional-field ext (monomorphic-option ADTs): `expr` is the harvested pure_ast
    # `Slice` record (ir_resolve.py `_PURE_AST_FIELD_TABLE["Slice"]`), whose 3 ALL-
    # optional fields (`lower`/`upper`/`step`, `_OPTIONAL_FIELDS['Slice']`) are each an
    # `option emit_ir`. Each `self._py_expr_to_ir(expr.X) if expr.X else None` ternary
    # lowers (functions.py `_recognize_slice_builder` + expressions.py
    # `_lower_sliceN_optfield`) to the monomorphic `iropt_ir` `match expr.X with Some
    # _v -> IrOSome (self._py_expr_to_ir _v) | None -> IrONone`, and the return builds
    # the new `IrSliceN iropt_ir iropt_ir iropt_ir` ctor (preamble.py
    # `_emit_exprir_theory`) carrying ALL THREE bounds. Verbatim body port of the LIVE
    # `_py_expr_slice` (Module5_IREmitter.py:1171).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_slice(self, expr: ast.Slice) -> Dict[str, Any]:
        lower = self._py_expr_to_ir(expr.lower) if expr.lower else None
        upper = self._py_expr_to_ir(expr.upper) if expr.upper else None
        step = self._py_expr_to_ir(expr.step) if expr.step else None
        return {"type": "Slice", "lower": lower, "upper": upper, "step": step}

    _PY_STMT_HANDLERS: int = {ast.Assign: '_py_stmt_assign', ast.AugAssign: '_py_stmt_augassign', ast.Return: '_py_stmt_return', ast.While: '_py_stmt_while', ast.For: '_py_stmt_for', ast.If: '_py_stmt_if', ast.Continue: '_py_stmt_continue', ast.Assert: '_py_stmt_assert', ast.Raise: '_py_stmt_raise', ast.AnnAssign: '_py_stmt_annassign', ast.Expr: '_py_stmt_expr', ast.Try: '_py_stmt_try', ast.With: '_py_stmt_with', ast.Pass: '_py_stmt_pass', ast.Break: '_py_stmt_break', ast.Delete: '_py_stmt_delete'}
    _PY_OP_MAP: int = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.FloorDiv: 'div', ast.Mod: '%', ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>=', ast.USub: '-', ast.UAdd: '+', ast.Not: 'not', ast.Invert: '~', ast.In: 'in', ast.NotIn: 'not in', ast.Is: '==', ast.IsNot: '!=', ast.BitAnd: '&', ast.BitOr: '|', ast.BitXor: '^', ast.LShift: '<<', ast.RShift: '>>', ast.Pow: '**'}
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmts_to_ir(self, stmts: List[ast.stmt]) -> List[int]:
        return []

    # SGhostArraySet/SGhostAssign increment (self-tcb-reduction M5, C-bucket): a
    # RETURN-stmt-dict handler. A bespoke Module6 lowering (functions.py
    # `_emit_emit_ghost_assign_bespoke`, keyed on the method name under `_uses_stmt_ir`)
    # emits it FAITHFULLY: `ga` param -> the typed `py_ghost_node`; `isinstance(ga,
    # GhostArraySetDecl)` -> `ghost_is_arrayset ga` (the opaque CSL-class discriminant,
    # like symtab_mem); `ga.target`/`ga.op` -> string readers; `self._csl_to_ir(ga.index/
    # value)` -> `csl_to_ir (ghost_index_ast/ghost_value_ast ga)` (`_csl_to_ir` stays
    # \trusted); `getattr(ga,'declared_type','int')` -> `ghost_declared_type_ast ga` (the
    # default folded, like delete's getattr). Returns the REAL `SGhostArraySet` (target,
    # index, value) / `SGhostAssign` (target, value, op, ghost_type) ctor. isinstance_op =
    # 0. Verbatim body port of the LIVE `_emit_ghost_assign`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_ghost_assign(self, ga) -> int:
        if isinstance(ga, GhostArraySetDecl):
            return {"stmt": "GhostArraySet", "target": ga.target,
                    "index": self._csl_to_ir(ga.index),
                    "value": self._csl_to_ir(ga.value)}
        return {"stmt": "GhostAssign", "target": ga.target,
                "value": self._csl_to_ir(ga.value), "op": ga.op,
                "ghost_type": getattr(ga, 'declared_type', 'int')}

    # SAssign + str-Constant recognizer (C-bucket): SKIPPED this increment (not a clean
    # WHOLE-body port). The Name-target branch alone reuses SAssign (`target.id` -> name_of,
    # `value` -> py_expr_to_ir), and the Attribute/`=='self'` branch's string-eq is available
    # (`str_eq_op`), BUT the whole handler has FOUR more branches that need infra NOT built
    # here: (1) a `target.value.id in self._cur_func_symtab` MEMBERSHIP test (record/set
    # membership) feeding a second FieldAssign; (2) a `raise PyCSLSemanticError(...)` arm
    # (exception construction); (3) a Subscript branch splitting on `isinstance(slice_node,
    # ast.Slice)` into NEW ArraySet / ArraySliceSet ctors; (4) a Tuple branch with a
    # list-comprehension over `target.elts` into a NEW TupleUnpack ctor. Also `target =
    # stmt.targets[0]` indexes the `targets` LIST. A half-body (Name-only) port is a facade;
    # deferred until SFieldAssign + the membership/raise/ArraySet/TupleUnpack infra lands.
    # SFieldAssign/SArraySliceSet/STupleUnpack increment (self-tcb-reduction M5, C-bucket):
    # the biggest stmt handler — 5 target-shape branches. `ir_stmts` is a caller-visible
    # mutable `ref (seq stmt_ir)` param. A bespoke Module6 lowering (functions.py
    # `_emit_py_stmt_assign_bespoke`, keyed on the method name under `_uses_stmt_ir`) emits
    # it FAITHFULLY (the generic lowering int-erases the target dispatch, the symtab
    # membership, and the Tuple compaction):
    #   - `stmt` param -> the typed `py_assign_node`; `target = stmt.targets[0]` ->
    #     `assign_target0_ast stmt` (HEAD); `self._py_expr_to_ir(stmt.value)` ->
    #     `assign_value_ast stmt`.
    #   - Name (`is_var target`) -> SAssign; self-Attribute (`is_var (avalue_of target)` &&
    #     `str_eq_op (name_of (avalue_of target)) "self"`) -> SFieldAssign "self"; symtab-
    #     Attribute (... && `symtab_mem (name_of (avalue_of target))`, the opaque
    #     `target.value.id in self._cur_func_symtab` membership) -> SFieldAssign named-base;
    #     non-Name-Attribute (`not (is_var (avalue_of target))`) -> `raise PyCSLSemanticError`
    #     (the f-string message + `type().__name__` + kwargs are DROPPED — a raise takes only
    #     the exc NAME, and the raise path does not reach `ensures`); else -> no-op.
    #   - Subscript: slice (`is_slice (sindex_of target)`) -> SArraySliceSet with the
    #     sliceN_lower_of/sliceN_upper_of OPTIONAL bounds (lower defaults to IrNum 0); else
    #     -> SArraySet. The dead py<3.9 `ast.Index` unwrap is DROPPED.
    #   - Tuple (`is_mktuple target`) -> STupleUnpack (var_names_prog (elts_of target)) — the
    #     CONCRETE `[elt.id for elt in target.elts if isinstance(elt, ast.Name)]` compaction
    #     (`var_names_of` filter+project), NOT the abstract length-only law (the fable vacuity
    #     trap). isinstance_op = 0. Verbatim body port of the LIVE `_py_stmt_assign`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_assign(self, stmt: ast.Assign, ir_stmts: List[int]) -> None:
        target = stmt.targets[0]
        if isinstance(target, ast.Name):
            ir_stmts.append({"stmt": "Assign", "target": target.id, "value": self._py_expr_to_ir(stmt.value)})
        elif isinstance(target, ast.Attribute):
            if isinstance(target.value, ast.Name) and target.value.id == 'self':
                ir_stmts.append({"stmt": "FieldAssign", "object": "self", "field": target.attr,
                                 "value": self._py_expr_to_ir(stmt.value)})
            elif (isinstance(target.value, ast.Name)
                  and target.value.id in self._cur_func_symtab):
                ir_stmts.append({"stmt": "FieldAssign", "object": target.value.id,
                                 "field": target.attr,
                                 "value": self._py_expr_to_ir(stmt.value)})
            elif not (isinstance(target.value, ast.Name)):
                from errors import PyCSLSemanticError
                raise PyCSLSemanticError(
                    f"in-place field mutation `<{type(target.value).__name__} base>.{target.attr} = ...` "
                    f"is out of scope: rebuild the element.",
                    stage="ir-emit",
                    code="PYCSL-WHYML-PARAM-COLLECTION-MUT",
                )
        elif isinstance(target, ast.Subscript):
            array_ir = self._py_expr_to_ir(target.value)
            slice_node = target.slice
            if isinstance(slice_node, ast.Slice):
                lower_ir = (self._py_expr_to_ir(slice_node.lower)
                            if slice_node.lower else {"type": "Number", "value": 0})
                upper_ir = (self._py_expr_to_ir(slice_node.upper)
                            if slice_node.upper else None)
                ir_stmts.append({"stmt": "ArraySliceSet", "array": array_ir,
                                 "lower": lower_ir, "upper": upper_ir,
                                 "value": self._py_expr_to_ir(stmt.value)})
            else:
                index_ir = self._py_expr_to_ir(slice_node)
                ir_stmts.append({"stmt": "ArraySet", "array": array_ir,
                                 "index": index_ir, "value": self._py_expr_to_ir(stmt.value)})
        elif isinstance(target, ast.Tuple):
            targets = [elt.id for elt in target.elts if isinstance(elt, ast.Name)]
            ir_stmts.append({"stmt": "TupleUnpack", "targets": targets,
                             "value": self._py_expr_to_ir(stmt.value)})

    # SAugAssign/SFieldAugAssign/SArraySet increment (self-tcb-reduction M5, C-bucket):
    # `ir_stmts` is a caller-visible mutable `ref (seq stmt_ir)` param; the `stmt` param is
    # typed the `AugAssign` record (`_PURE_AST_FIELD_TABLE["AugAssign"]`: target/value
    # ExprIR, op int). The THREE-branch dispatch on the target shape lowers via the
    # isinstance-on-emit_ir recognizer (`isinstance(stmt.target, ast.Name/Attribute/
    # Subscript)` -> `is_var`/`is_attribute`/`is_sub stmt.target`, isinstance_op = 0):
    #   (1) Name: `.append({"stmt":"AugAssign","target":stmt.target.id,"op":self._py_op_to_str
    #       (stmt.op),"value":self._py_expr_to_ir(stmt.value)})` snocs `SAugAssign (name_of
    #       stmt.target) (py_op_to_str stmt.op) (py_expr_to_ir stmt.value)` — the new
    #       `SAugAssign string string emit_ir` ctor (target NAME via `name_of`, OP via the
    #       trusted `_py_op_to_str` string val, RHS via the dispatcher).
    #   (2) self-field: the guard `isinstance(stmt.target, ast.Attribute) and isinstance(
    #       stmt.target.value, ast.Name) and stmt.target.value.id == 'self'` lowers to
    #       `is_attribute stmt.target && is_var (avalue_of stmt.target) && str_eq_op (name_of
    #       (avalue_of stmt.target)) "self"`; the append snocs `SFieldAugAssign (name_of
    #       stmt.target) (py_op_to_str stmt.op) (py_expr_to_ir stmt.value)` — the new
    #       `SFieldAugAssign string string emit_ir` ctor (field NAME `stmt.target.attr` via
    #       `name_of`; the constant `object:"self"` is DROPPED, pinned by the guard).
    #   (3) subscript: the OUTPUT-side slice-discrimination (the d866a1b9 `_py_expr_subscript`
    #       precedent) — `slice_ir = self._py_expr_to_ir(stmt.target.slice)` (an emit_ir local,
    #       `stmt.target.slice` -> `sindex_of`), guard `not (slice_ir.get("type") == "Slice")`
    #       (-> `not (str_eq_op (kind_of !slice_ir) "Slice")`), then snocs the desugared
    #       `SArraySet (py_expr_to_ir (avalue_of stmt.target)) !slice_ir (IrBinOp (py_op_to_str
    #       stmt.op) !read_ir (py_expr_to_ir stmt.value))` — the new `SArraySet emit_ir emit_ir
    #       emit_ir` ctor, the inline `{"type":"BinOp",...}` value reusing IrBinOp. The
    #       `.value` disambiguation (self-field IrAttr object vs subscript IrSub array) is the
    #       unified `avalue_of` projector, scoped to this handler.
    # isinstance_op = 0. Verbatim body port of the LIVE `_py_stmt_augassign`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_augassign(self, stmt: ast.AugAssign, ir_stmts: List[int]) -> None:
        if isinstance(stmt.target, ast.Name):
            ir_stmts.append({"stmt": "AugAssign", "target": stmt.target.id,
                             "op": self._py_op_to_str(stmt.op), "value": self._py_expr_to_ir(stmt.value)})
        elif (isinstance(stmt.target, ast.Attribute) and
              isinstance(stmt.target.value, ast.Name) and
              stmt.target.value.id == 'self'):
            ir_stmts.append({"stmt": "FieldAugAssign", "object": "self", "field": stmt.target.attr,
                             "op": self._py_op_to_str(stmt.op), "value": self._py_expr_to_ir(stmt.value)})
        elif isinstance(stmt.target, ast.Subscript):
            # `c[k] op= v` — desugar to a subscript store of `(c[k]) op v` (the proven
            # ArraySet path). Output-side slice-discrimination (the `_py_expr_subscript`
            # precedent): lower the slice once and discriminate on the lowered kind; the
            # dead `ast.Index` unwrap (Python <3.9) is dropped (byte-identical on 3.9+).
            slice_ir = self._py_expr_to_ir(stmt.target.slice)
            if not (slice_ir.get("type") == "Slice"):
                read_ir = self._py_expr_to_ir(stmt.target)
                ir_stmts.append({
                    "stmt": "ArraySet",
                    "array": self._py_expr_to_ir(stmt.target.value),
                    "index": slice_ir,
                    "value": {"type": "BinOp", "op": self._py_op_to_str(stmt.op),
                              "left": read_ir, "right": self._py_expr_to_ir(stmt.value)}})

    # stmt-list-append-mutation wall (self-tcb-reduction M5, C-bucket): `ir_stmts` is a
    # caller-visible mutable `ref (seq stmt_ir)` param (the None-returning + `#@ assigns
    # ir_stmts` convention); `.append({"stmt":"Return","value":<opt>})` lowers to
    # `ir_stmts := Seq.snoc !ir_stmts (SReturn <iropt_ir>)` on the ref ITSELF, tag-preserving
    # (SReturn, never erased to 0). The OPTIONAL `value` — the `disp(stmt.value) if
    # stmt.value else None` ternary over `stmt.value : option emit_ir` — lowers via the
    # shared `_slice_bound_to_iropt_ir` recognizer to `IrOSome (py_expr_to_ir stmt.value)` /
    # `IrONone`. Enabled by the STATEMENT-node param resolution: the `Return` entry in
    # `_PURE_AST_FIELD_TABLE` (ir_resolve.py) types the `ast.Return` param as the `Return`
    # record with `value : option emit_ir`, and `SReturn` is retyped `SReturn iropt_ir`
    # (preamble.py stmt_ir theory). Verbatim body port of the LIVE `_py_stmt_return`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_return(self, stmt: ast.Return, ir_stmts: List[int]) -> None:
        ir_stmts.append({"stmt": "Return", "value": self._py_expr_to_ir(stmt.value) if stmt.value else None})

    # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): `ir_stmts` is a
    # caller-visible mutable `ref (seq stmt_ir)` param; `.append(self._process_while(
    # stmt))` snocs the `stmt_ir` value the (trusted) `_process_while` returns —
    # an `SWhile (py_expr_to_ir stmt.test) (seq_to_sl (py_stmts_to_ir stmt.body))`
    # (module6_whyml/statements.py append-of-call path + expressions.py
    # `_lower_stmt_ir_construction`) — onto the ref ITSELF, tag-preserving (SWhile,
    # never erased to 0), with a REAL `stmt_list` sub-body (seq_to_sl of the
    # dispatcher's seq, never SLNil-erased). Verbatim body port of the LIVE
    # `_py_stmt_while`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_while(self, stmt: ast.While, ir_stmts: List[int]) -> None:
        ir_stmts.append(self._process_while(stmt))

    # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): sibling of
    # `_py_stmt_while` — `ir_stmts` is a caller-visible mutable `ref (seq stmt_ir)`
    # param; `.append(self._process_for(stmt))` snocs the `SFor (py_expr_to_ir
    # stmt.iter) (seq_to_sl (py_stmts_to_ir stmt.body))` value the now-converted
    # `_process_for` returns (recognized `stmt_ir`-valued via the build-up-dict
    # recognizer's `_returns_stmt_ir`) onto the ref ITSELF, tag-preserving (SFor,
    # never erased to 0), with a REAL `stmt_list` sub-body (seq_to_sl of the
    # dispatcher's seq, never SLNil-erased). Verbatim body port of the LIVE
    # `_py_stmt_for`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_for(self, stmt: ast.For, ir_stmts: List[int]) -> None:
        ir_stmts.append(self._process_for(stmt))

    # SUB-BODY recursion (C-bucket): sibling of `_py_stmt_while` — snocs the
    # `SIf (py_expr_to_ir stmt.test) (seq_to_sl (py_stmts_to_ir stmt.body))
    # (seq_to_sl (py_stmts_to_ir stmt.orelse))` value `_process_if` returns onto
    # the `ref (seq stmt_ir)` param. Verbatim body port of the LIVE `_py_stmt_if`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_if(self, stmt: ast.If, ir_stmts: List[int]) -> None:
        ir_stmts.append(self._process_if(stmt))

    # stmt-list-append-mutation wall (self-tcb-reduction M5, C-bucket): a NULLARY sibling
    # of `_py_stmt_pass` — `ir_stmts` is a caller-visible mutable `ref (seq stmt_ir)` param;
    # `.append({"stmt":"Continue"})` lowers to `ir_stmts := Seq.snoc !ir_stmts SContinue` on
    # the ref ITSELF, tag-preserving (SContinue, never erased to 0). SContinue is ALREADY in
    # the certified stmt_ir ADT (Phase2d_StmtIR.v / StmtIR.lean) and `_STMT_IR_CTORS` — no
    # new ctor, no field-table entry (Continue has no fields). Verbatim body port of the
    # LIVE `_py_stmt_continue`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_continue(self, stmt: ast.Continue, ir_stmts: List[int]) -> None:
        ir_stmts.append({"stmt": "Continue"})

    # SAssert increment (self-tcb-reduction M5, C-bucket): `ir_stmts` is a caller-visible
    # mutable `ref (seq stmt_ir)` param. This is a BUILD-UP-THEN-APPEND: `ir_node` is bound
    # to the base `{"stmt":"Assert","test":self._py_expr_to_ir(stmt.test)}` node, then a
    # CONDITIONAL field-add `if stmt.msg and isinstance(stmt.msg, Constant) and isinstance(
    # stmt.msg.value, str): ir_node["msg"] = stmt.msg.value` attaches the optional message,
    # then `ir_stmts.append(ir_node)` snocs it. The `_recognize_stmt_append_builder`
    # (functions.py) folds these three statements into a single `ir_stmts.append({"stmt":
    # "Assert","test":..,"msg":stmt.msg})`, which `_lower_stmt_ir_node` lowers to
    # `ir_stmts := Seq.snoc !ir_stmts (SAssert (py_expr_to_ir stmt.test) <iropt_str>)` — the
    # new `SAssert emit_ir iropt_str` ctor (Phase2d_StmtIR.v / StmtIR.lean). The msg option
    # field lowers via the "assert_msg" child kind: `match stmt.msg with Some _m -> (if
    # is_str _m then IrSSome (value_of _m) else IrSNone) | None -> IrSNone` — the FAITHFUL
    # present-as-string-literal-Constant option (the compound guard collapses to is-Some &&
    # is_str, and `stmt.msg.value` projects via `value_of`, `IrStr v -> v`), tag-preserving
    # (SAssert, never erased to 0). isinstance_op = 0. Verbatim body port of the LIVE
    # `_py_stmt_assert`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_assert(self, stmt: ast.Assert, ir_stmts: List[int]) -> None:
        ir_node: Dict[str, Any] = {"stmt": "Assert", "test": self._py_expr_to_ir(stmt.test)}
        if stmt.msg and isinstance(stmt.msg, ast.Constant) and isinstance(stmt.msg.value, str):
            ir_node["msg"] = stmt.msg.value
        ir_stmts.append(ir_node)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_raise(self, stmt: ast.Raise, ir_stmts: List[int]) -> None:
        pass

    # SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): `ir_stmts` is a
    # caller-visible mutable `ref (seq stmt_ir)` param; the guard `isinstance(stmt.target,
    # ast.Name) and stmt.value is not None` lowers to `(is_var stmt.target) && (is-Some
    # stmt.value)` — the FAITHFUL option presence test on the OptExprIR `value` field (a
    # value-less annotation `x: T` is skipped, NON-vacuous). The guarded
    # `.append({"stmt":"Assign","target":stmt.target.id,"value":self._py_expr_to_ir(stmt.
    # value)})` snocs `SAssign (name_of stmt.target) (match stmt.value with Some _v ->
    # py_expr_to_ir _v | None -> IrOther "")` onto the ref — the new `SAssign string
    # emit_ir` ctor, target name projected via `name_of`, RHS via the option-unwrapped
    # dispatcher, tag-preserving (SAssign, never erased to 0). isinstance_op = 0. Verbatim
    # body port of the LIVE `_py_stmt_annassign`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_annassign(self, stmt: ast.AnnAssign, ir_stmts: List[int]) -> None:
        if isinstance(stmt.target, ast.Name) and stmt.value is not None:
            ir_stmts.append({"stmt": "Assign", "target": stmt.target.id,
                             "value": self._py_expr_to_ir(stmt.value)})

    # SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket): `ir_stmts` is a
    # caller-visible mutable `ref (seq stmt_ir)` param; the docstring-skip guard
    # `isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str)` — "value
    # is a string literal" — collapses to the emit_ir discriminant `(is_str stmt.value)`
    # (module6_whyml/expressions.py `_recognize_str_constant_guard`), because a
    # string-literal Constant lowers to exactly IrStr. On the docstring branch the early
    # `return` suppresses the append (lowered via `Return_void`); otherwise
    # `.append({"stmt":"Expr","value":self._py_expr_to_ir(stmt.value)})` snocs `SExpr
    # (py_expr_to_ir stmt.value)` onto the ref, tag-preserving (SExpr, never erased to 0).
    # isinstance_op = 0. Verbatim body port of the LIVE `_py_stmt_expr`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_expr(self, stmt: ast.Expr, ir_stmts: List[int]) -> None:
        # Skip bare string-literal expressions (docstrings) — no WhyML equivalent.
        if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            return
        ir_stmts.append({"stmt": "Expr", "value": self._py_expr_to_ir(stmt.value)})

    # SUB-BODY recursion (C-bucket): SKIPPED this increment (needs a distinct ADT).
    # `_py_stmt_try` builds a Try node with MULTIPLE sub-lists (body/orelse/finalbody
    # each lower via the mutual-cons stmt_list) BUT ALSO a `handlers` LIST-OF-RECORDS
    # built by a `for h in stmt.handlers: handlers.append({"exc_type":..,"name":..,
    # "body":..})` loop — a handler ADT (exc_type string, name string, body stmt_list)
    # beyond stmt_list, whose `exc_type` is computed via isinstance-over-AST +
    # `"|".join(...)` over `h.type.elts` (the pure_ast AST-node boundary). A later
    # increment adds an SExceptHandler record + the handler-list build loop, then STry.
    # STry + except_handler + handler_list increment (self-tcb-reduction M5, C-bucket):
    # `ir_stmts` is a caller-visible mutable `ref (seq stmt_ir)` param. This is the
    # record-list-building-loop handler: `handlers = []; for h in stmt.handlers:
    # handlers.append({rec}); ir_stmts.append({"stmt":"Try",...,"handlers":handlers,...})`.
    # A bespoke Module6 lowering (functions.py `_emit_py_stmt_try_bespoke`, keyed on the
    # method name under `_uses_stmt_ir`) emits it FAITHFULLY (the generic statement
    # lowering int-erases the accumulator loop end-to-end — the pre-feature facade was
    # `isinstance_op 0 0`x2, `Seq.snoc !handlers 0`, `join_1 0`, `SUnmodelledStmt_Try`):
    #   - `stmt` param -> the typed `py_try_node`; `stmt.handlers` -> `seq
    #     ast_excepthandler` (the `try_handlers_ast` AST reader). The accumulator
    #     `handlers` -> a REAL `ref (seq except_handler)` grown by `Seq.snoc` of a REAL
    #     `{ eh_exc_type; eh_name; eh_body }` record (NOT `Seq.snoc 0`).
    #   - `h.type and isinstance(h.type, ast.Name/Tuple)` on the option `h.type` ->
    #     `match eh_type_ast h with IrOSome t -> is_var t / is_mktuple t` (isinstance_op
    #     = 0); `h.type.id` -> `name_of t`; `h.name` -> `eh_name_ast h : iropt_str`.
    #   - the Tuple `"|".join(n.id for n in h.type.elts if isinstance(n, ast.Name))` ->
    #     the CONCRETE `pipe_join (elts_of t)` compaction (`var_names_of` filters `is_var`
    #     + projects `name_of` over the elts irlist, `join_pipe` inserts "|"), NOT a
    #     length-only abstract law (the fable's vacuity trap — GATE 0 proved observable).
    #   - the Try node -> the REAL `STry (seq_to_sl body) (seq_to_hl handlers)
    #     (seq_to_sl orelse) (seq_to_sl finalbody)` ctor with a REAL `handler_list`
    #     (NOT HLNil-erased). Co-landed with the axiom-free Rocq+Lean certificate.
    # Verbatim body port of the LIVE `_py_stmt_try`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_try(self, stmt: ast.Try, ir_stmts: List[int]) -> None:
        body_ir = self._py_stmts_to_ir(stmt.body)
        handlers = []
        for h in stmt.handlers:
            exc_type = None
            if h.type and isinstance(h.type, ast.Name):
                exc_type = h.type.id
            elif h.type and isinstance(h.type, ast.Tuple):
                exc_type = "|".join(
                    n.id for n in h.type.elts if isinstance(n, ast.Name))
            handlers.append({
                "exc_type": exc_type,
                "name": h.name,
                "body": self._py_stmts_to_ir(h.body)
            })
        ir_stmts.append({
            "stmt": "Try", "body": body_ir, "handlers": handlers,
            "orelse": self._py_stmts_to_ir(stmt.orelse),
            "finalbody": self._py_stmts_to_ir(stmt.finalbody)
        })

    # SCriticalSection increment (self-tcb-reduction M5, C-bucket): `ir_stmts` is a
    # caller-visible mutable `ref (seq stmt_ir)` param. The mutex/extend handler. A bespoke
    # Module6 lowering (functions.py `_emit_py_stmt_with_bespoke`, keyed on the method name
    # under `_uses_stmt_ir`) emits it FAITHFULLY (the generic lowering int-erases the
    # weave-injected mutex attrs to 0 — making the CriticalSection branch dead — and no-ops
    # the extend):
    #   - `mutex = getattr(stmt, 'csl_critical_mutex', None) or getattr(stmt,
    #     'csl_acquires', None)` reads WEAVE-INJECTED attrs (not in pure_ast) -> the opaque
    #     `csl_mutex_ast stmt : iropt_str` reader (the honest model of the runtime mutex
    #     attribute); `if mutex:` -> the is-Some test. isinstance_op = 0.
    #   - `body_ir = self._py_stmts_to_ir(stmt.body)` -> the dispatcher's `seq stmt_ir`.
    #   - mutex present (`IrSSome m`) -> `SCriticalSection m (seq_to_sl body_ir)
    #     (mutex_invariant_ir m) (mutex_invariant_ir m)` snoc'd onto ir_stmts (the new
    #     SCriticalSection ctor; `_get_mutex_invariant_ir` stays \trusted).
    #   - no mutex (`IrSNone`) -> `ir_stmts := !ir_stmts ++ body_ir`, the seq-CONCAT extend
    #     (`ir_stmts.extend(body_ir)`, a REAL caller-visible mutation under `writes {
    #     ir_stmts }`, NOT the generic no-op). Verbatim body port of the LIVE `_py_stmt_with`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_with(self, stmt: ast.With, ir_stmts: List[int]) -> None:
        mutex = (getattr(stmt, 'csl_critical_mutex', None) or
                 getattr(stmt, 'csl_acquires', None))
        body_ir = self._py_stmts_to_ir(stmt.body)
        if mutex:
            inv = self._get_mutex_invariant_ir(mutex)
            ir_stmts.append({
                "stmt": "CriticalSection", "mutex": mutex, "body": body_ir,
                "assume_invariant": inv, "prove_invariant": inv,
            })
        else:
            ir_stmts.extend(body_ir)

    # stmt-list-append-mutation wall (self-tcb-reduction M5, C-bucket): `ir_stmts` is a
    # caller-visible mutable `ref (seq stmt_ir)` param (the None-returning + `#@ assigns
    # ir_stmts` convention); `.append({"stmt":"Pass"})` lowers to `ir_stmts := Seq.snoc
    # !ir_stmts SPass` on the ref ITSELF — the SOUND in-place append (fable BREAKABLE
    # verdict), tag-preserving (SPass, never erased to 0). Verbatim body port of the LIVE
    # `_py_stmt_pass` (Module5_IREmitter.py:1434). Co-landed with the axiom-free Rocq+Lean
    # certificate (Phase2d_StmtIR.v / StmtIR.lean).
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_pass(self, stmt: ast.Pass, ir_stmts: List[int]) -> None:
        ir_stmts.append({"stmt": "Pass"})

    # stmt-list-append-mutation wall (self-tcb-reduction M5, C-bucket): a NULLARY sibling
    # of `_py_stmt_pass` — `ir_stmts` is a caller-visible mutable `ref (seq stmt_ir)` param
    # (the None-returning + `#@ assigns ir_stmts` convention); `.append({"stmt":"Break"})`
    # lowers to `ir_stmts := Seq.snoc !ir_stmts SBreak` on the ref ITSELF, tag-preserving
    # (SBreak, never erased to 0). SBreak is ALREADY in the certified stmt_ir ADT
    # (Phase2d_StmtIR.v / StmtIR.lean) and `_STMT_IR_CTORS` — no new ctor, no field-table
    # entry (Break has no fields). Verbatim body port of the LIVE `_py_stmt_break`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_break(self, stmt: ast.Break, ir_stmts: List[int]) -> None:
        ir_stmts.append({"stmt": "Break"})

    # SDelSubscript increment (self-tcb-reduction M5, C-bucket): `ir_stmts` is a
    # caller-visible mutable `ref (seq stmt_ir)` param. The LOOP-APPEND-TO-OUTER handler
    # `for tgt in stmt.targets: ir_stmts.append(<node(tgt)>)` — unlike try/match (a LOCAL
    # record-list accumulator), it `Seq.snoc`s DIRECTLY onto `ir_stmts` per element. A
    # bespoke Module6 lowering (functions.py `_emit_py_stmt_delete_bespoke`, keyed on the
    # method name under `_uses_stmt_ir`) emits it FAITHFULLY as a real `for i in
    # 0..Seq.length targets` loop (writes { ir_stmts }, invariant 0<=i<=len, variant
    # len-i):
    #   - `stmt` param -> the typed `py_delete_node`; `stmt.targets` -> `seq emit_ir`
    #     (the `del_targets_ast` AST reader).
    #   - `getattr(tgt, "slice", None)` -> `.slice` exists exactly on a Subscript, so the
    #     getattr-with-default folds into `is_sub tgt` (`slice_node = if is_sub tgt then
    #     IrOSome (sindex_of tgt) else IrONone`). The dead py<3.9 `ast.Index` unwrap is
    #     DROPPED (byte-identical on 3.9+, like augassign/subscript).
    #   - `isinstance(tgt, ast.Subscript)` -> `is_sub tgt`; `not isinstance(slice_node,
    #     ast.Slice)` -> `not (is_slice (sindex_of tgt))` (under the is_sub conjunct).
    #     isinstance_op = 0.
    #   - the subscript-delete appends a REAL `SDelSubscript (py_expr_to_ir (svalue_of
    #     tgt)) (py_expr_to_ir (sindex_of tgt))` (IrSub array + index projectors); every
    #     other target appends `SPass`.
    # Verbatim body port of the LIVE `_py_stmt_delete` (dead ast.Index branch dropped).
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_delete(self, stmt: ast.Delete, ir_stmts: List[int]) -> None:
        for tgt in stmt.targets:
            slice_node = getattr(tgt, "slice", None)
            if isinstance(tgt, ast.Subscript) and not isinstance(slice_node, ast.Slice):
                ir_stmts.append({
                    "stmt": "DelSubscript",
                    "array": self._py_expr_to_ir(tgt.value),
                    "index": self._py_expr_to_ir(slice_node),
                })
            else:
                ir_stmts.append({"stmt": "Pass"})

    # SMatch + match_case + match_case_list increment (self-tcb-reduction M5, C-bucket):
    # `ir_stmts` is a caller-visible mutable `ref (seq stmt_ir)` param. Sibling of
    # `_py_stmt_try` — the record-list-building-loop handler `cases = []; for case in
    # stmt.cases: cases.append({rec}); ir_stmts.append({"stmt":"Match",...})`. A bespoke
    # Module6 lowering (functions.py `_emit_py_stmt_match_bespoke`, keyed on the method
    # name under `_uses_stmt_ir`) emits it FAITHFULLY (the generic statement lowering
    # int-erases the accumulator loop):
    #   - `stmt` param -> the typed `py_match_node`; `stmt.cases` -> `seq ast_match_case`
    #     (the `match_cases_ast` AST reader). The accumulator `cases` -> a REAL `ref (seq
    #     match_case)` grown by `Seq.snoc` of a REAL `{ mc_pattern; mc_guard; mc_body }`
    #     record (NOT `Seq.snoc 0`).
    #   - `pattern_ir = self._match_pattern_to_ir(case.pattern)` -> `mc_pattern_ir _c` : a
    #     REAL emit_ir (the trusted pattern dispatcher, folded — NOT int-erased).
    #   - `guard_ir = self._py_expr_to_ir(case.guard) if case.guard else None` -> `match
    #     mc_guard_ast _c with IrONone -> IrONone | IrOSome g -> IrOSome (py_expr_to_ir g)`
    #     — the faithful optional guard (`iropt_ir`).
    #   - `body_ir = self._py_stmts_to_ir(case.body)` -> `seq_to_sl (py_stmts_to_ir
    #     (mc_body_ast _c))` (stmt_list).
    #   - the Match node -> the REAL `SMatch (py_expr_to_ir stmt.subject) (seq_to_mcl
    #     cases)` ctor with a REAL `match_case_list` (NOT MCNil-erased). isinstance_op = 0.
    # `_match_pattern_to_ir` stays \trusted (an opaque pattern dispatcher). Verbatim body
    # port of the LIVE `_py_stmt_match`.
    #@ requires True
    #@ ensures True
    #@ assigns ir_stmts
    def _py_stmt_match(self, stmt: Any, ir_stmts: List[int]) -> None:
        subject_ir = self._py_expr_to_ir(stmt.subject)
        cases = []
        for case in stmt.cases:
            pattern_ir = self._match_pattern_to_ir(case.pattern)
            guard_ir = self._py_expr_to_ir(case.guard) if case.guard else None
            body_ir = self._py_stmts_to_ir(case.body)
            cases.append({"pattern": pattern_ir, "guard": guard_ir, "body": body_ir})
        ir_stmts.append({"stmt": "Match", "subject": subject_ir, "cases": cases})

    # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): RETURNS a constructed
    # compound `{"stmt": "While", ...}` node, recognized (module6_whyml/functions.py
    # `_returns_stmt_ir`) as `stmt_ir`-typed and lowered (expressions.py
    # `_lower_stmt_ir_construction`) to `SWhile (py_expr_to_ir node.test)
    # (seq_to_sl (py_stmts_to_ir node.body))`. The `test` child → emit_ir (While.test
    # `_PURE_AST_FIELD_TABLE` "ExprIR"); the `body` sub-list → `seq stmt_ir` (the
    # trusted `_py_stmts_to_ir` dispatcher, retyped) materialized to `stmt_list` via
    # `seq_to_sl`. The `line`/`invariants`/`variants` keys are DROPPED (SWhile carries
    # test+body only), so their dict values (`getattr`/`_csl_list_to_ir`) are never
    # lowered. Verbatim body port of the LIVE `_process_while`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _process_while(self, node: ast.While) -> int:
        return {
            "stmt": "While",
            # §4.4 statement-level span (refactor.md B4a) — the loop's source line, so
            # the core can report IR-level loop-invariant errors with the same
            # "while loop at line N" context Module4 produced. Module6 ignores it.
            "line": getattr(node, "lineno", 0),
            "test": self._py_expr_to_ir(node.test),
            "invariants": self._csl_list_to_ir(getattr(node, 'csl_invariants', [])),
            "variants": self._csl_list_to_ir(getattr(node, 'csl_variants', [])),
            "body": self._py_stmts_to_ir(node.body)
        }

    # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): BUILDS its node dict
    # INCREMENTALLY (`target = ..; d = {"stmt":"For",..}; if isinstance(node.target,
    # ast.Tuple): d["tuple_targets"] = ..; return d`) rather than returning a dict
    # LITERAL. The BUILD-UP-DICT recognizer (module6_whyml/functions.py
    # `_recognize_stmtir_builder`) rewrites this to a single `Return` of the base
    # construction dict, so `_returns_stmt_ir` types the return `stmt_ir` and
    # `_lower_stmt_ir_construction` emits `SFor (py_expr_to_ir node.iter)
    # (seq_to_sl (py_stmts_to_ir node.body))` — the `iter` child → emit_ir (For.iter
    # `_PURE_AST_FIELD_TABLE` "ExprIR"); the `body` sub-list → `seq stmt_ir` (the
    # trusted `_py_stmts_to_ir` dispatcher, retyped) materialized to `stmt_list` via
    # `seq_to_sl`. The DROPPED fields — the `target` string (its `node.target.id`
    # /`isinstance(node.target, ast.Name)` prelude, the pure_ast AST-node boundary),
    # line/invariants/variants/lineno/allow_iteration_mutation, and the conditionally
    # added `tuple_targets` (its `isinstance(node.target, ast.Tuple)` guard + list-comp
    # over `node.target.elts`) — are never lowered (SFor = iter+body, the SWhile/SIf
    # precedent of keeping just the emitter-model-relevant children). SFor is ALREADY
    # in the certified stmt_ir ADT (Phase2d_StmtIR.v / StmtIR.lean) and the theory — no
    # new ctor. Verbatim body port of the LIVE `_process_for`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _process_for(self, node: ast.For) -> int:
        target = node.target.id if isinstance(node.target, ast.Name) else "_for_target"
        d: Dict[str, Any] = {
            "stmt": "For",
            "line": getattr(node, "lineno", 0),  # §4.4 statement-level span (refactor.md B4a)
            "target": target,
            "iter": self._py_expr_to_ir(node.iter),
            "invariants": self._csl_list_to_ir(getattr(node, 'csl_invariants', [])),
            "variants": self._csl_list_to_ir(getattr(node, 'csl_variants', [])),
            "body": self._py_stmts_to_ir(node.body),
            # UB-7.1 opt-in (#@ allow_iteration_mutation). Module 4
            # consults this when running `find_iteration_mutations`.
            "allow_iteration_mutation": bool(getattr(node, 'csl_allow_iteration_mutation', False)),
            "lineno": getattr(node, "lineno", 0),
        }
        # W2 char-iteration: a tuple loop target (`for i, ch in enumerate(s)`)
        # binds several names at once; keep them so Module6 can bind both the
        # index and the element (the single `target` collapses them to
        # `_for_target`, losing `i`/`ch`). Emitted ONLY for a tuple target, so a
        # plain `for x in …` dict stays byte-identical (the key is absent).
        if isinstance(node.target, ast.Tuple):
            d["tuple_targets"] = [
                e.id if isinstance(e, ast.Name) else "_" for e in node.target.elts]
        return d

    # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): RETURNS a constructed
    # compound `{"stmt": "If", ...}` node, lowered to `SIf (py_expr_to_ir node.test)
    # (seq_to_sl (py_stmts_to_ir node.body)) (seq_to_sl (py_stmts_to_ir node.orelse))`
    # — BOTH the body AND the orelse sub-lists materialized to `stmt_list`. Verbatim
    # body port of the LIVE `_process_if`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _process_if(self, node: ast.If) -> int:
        return {
            "stmt": "If",
            "test": self._py_expr_to_ir(node.test),
            "body": self._py_stmts_to_ir(node.body),
            "orelse": self._py_stmts_to_ir(node.orelse)
        }

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _match_pattern_to_ir(self, pattern: Any) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _scan_2d_in_expr(self, expr: int, param_names: int, result: int) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _scan_2d_in_stmt(self, stmt: int, param_names: int, result: int) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_2d_params(self, body_ir: List[int], param_names: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _field_type_from_annotation(annotation: Optional[ast.expr]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_type_from_annotation_inst(self, annotation: Optional[ast.expr], scope_name: str='') -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _mixin_field_type(type_str: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_typeddict_class(node: ast.ClassDef) -> bool:
        return False

    _GENERIC_BASE_NAMES = {'Generic'}
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_type_params(self, node) -> List[int]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _extract_generic_arg_names(slice_node) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_typevar_registry(self, node: ast.Module) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_typeddict_record(self, node: ast.ClassDef) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _typeddict_field_type(self, annotation: ast.expr, scope_name: str, total: bool) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _wrap_optional(self, inner: ast.expr, scope_name: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _synthesize_typeddict_functional(self, node: ast.Module) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_namedtuple_class(node: ast.ClassDef) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_namedtuple_record(self, node: ast.ClassDef) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _synthesize_namedtuple_functional(self, node: ast.Module) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_protocol_interface(self, node: ast.ClassDef) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _populate_protocol_conformance(self, node: ast.ClassDef) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_class_fields(self, node: ast.ClassDef) -> Tuple[List[int], int]:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _array_init_size(rhs: ast.expr) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _const_int_value(value: ast.expr) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_class_constants(self, node: ast.ClassDef, field_names: int) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _should_skip_method(self, node: ast.FunctionDef) -> bool:
        return False

    _UNION_ARM_TAGS = {'int', 'bool', 'str', 'bytes', 'float', 'list', 'dict', 'set'}
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_arm_tag(self, elt: ast.expr) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_union_arms(self, ann_expr: ast.expr) -> Optional[List[ast.expr]]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _normalize_union_annotation(self, ann_expr: ast.expr, scope_name: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_final_annotation(ann_expr: ast.expr) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _normalize_final_annotation(self, ann_expr: ast.expr) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_final_registry(self, module_node: ast.Module) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _normalize_literal_annotation(self, ann_expr: ast.expr, param_name: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _classify_literal_value(elt: ast.expr) -> int:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _m5_get_type_name_legacy(self, annotation: ast.expr) -> str:
        return ""

    _CALLABLE_SCALAR_TAGS = frozenset({'int', 'bool', 'str', 'float'})
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _encode_callable_annotation(self, annotation: ast.Subscript) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _callable_type_tag(self, node: ast.expr) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _m5_get_type_name(self, annotation: ast.expr, scope_name: str='', param_name: str='') -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _m5_get_dict_value_type(annotation: ast.expr) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _m5_get_dict_key_type(annotation: ast.expr) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_function_symbol_table(self, node: ast.FunctionDef) -> int:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_function_ir(self, node: ast.FunctionDef) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _detect_array_dimensions(self, func_ir: int) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_decode_call(ir: Any) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_str_decode_locals(self, body: Any) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _detect_seq_promotion(self, func_ir: int) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_overload_stub(node: ast.FunctionDef) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _synthesize_overload_guard(self, node: ast.FunctionDef) -> List[int]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _build_overload_param_guard(self, node: ast.FunctionDef) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _overload_type_name(ann: ast.AST) -> Optional[str]:
        return None


class Module5_IREmitter:
    'Consumes the validated AAST and outputs a JSON string.'
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, tree: ast.AST) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def generate_json(self, indent: int=2) -> str:
        return ""


