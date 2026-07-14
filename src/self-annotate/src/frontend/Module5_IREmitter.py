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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_number(self, node: CSLNumber) -> int:
        return {}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_string(self, node: CSLStringLiteral) -> Dict[str, Any]:
        return {"type": "String", "value": node.value}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_bool(self, node: CSLBool) -> int:
        return {}

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_old(self, node: CSLOld) -> int:
        return {}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_nothing(self, node: Nothing) -> Dict[str, Any]:
        return {"type": "Nothing"}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_forall(self, node: Forall) -> int:
        return {}

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_forall_items(self, node: ForallItems) -> Dict[str, Any]:
        return {"type": "ForallItems", "key": node.key, "val": node.val,
                "map": node.coll, "body": self._csl_to_ir(node.body)}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_exists(self, node: Exists) -> int:
        return {}

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_function_variant(self, node: FunctionVariant) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_call_expr(self, node: CallExpr) -> int:
        return {}

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _csl_mktuple(self, node: MkTupleExpr) -> int:
        return {}

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_constant(self, expr: ast.Constant) -> int:
        return {}

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_compare(self, expr: ast.Compare) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_boolop(self, expr: ast.BoolOp) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_call(self, expr: ast.Call) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_tuple(self, expr: ast.Tuple) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_subscript(self, expr: ast.Subscript) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_list(self, expr: ast.List) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_attribute(self, expr: ast.Attribute) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_dict(self, expr: ast.Dict) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_set(self, expr: ast.Set) -> int:
        return {}

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_walrus(self, expr: ast.NamedExpr) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_lambda(self, expr: ast.Lambda) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_expr_slice(self, expr: ast.Slice) -> int:
        return {}

    _PY_STMT_HANDLERS: int = {ast.Assign: '_py_stmt_assign', ast.AugAssign: '_py_stmt_augassign', ast.Return: '_py_stmt_return', ast.While: '_py_stmt_while', ast.For: '_py_stmt_for', ast.If: '_py_stmt_if', ast.Continue: '_py_stmt_continue', ast.Assert: '_py_stmt_assert', ast.Raise: '_py_stmt_raise', ast.AnnAssign: '_py_stmt_annassign', ast.Expr: '_py_stmt_expr', ast.Try: '_py_stmt_try', ast.With: '_py_stmt_with', ast.Pass: '_py_stmt_pass', ast.Break: '_py_stmt_break', ast.Delete: '_py_stmt_delete'}
    _PY_OP_MAP: int = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.FloorDiv: 'div', ast.Mod: '%', ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>=', ast.USub: '-', ast.UAdd: '+', ast.Not: 'not', ast.Invert: '~', ast.In: 'in', ast.NotIn: 'not in', ast.Is: '==', ast.IsNot: '!=', ast.BitAnd: '&', ast.BitOr: '|', ast.BitXor: '^', ast.LShift: '<<', ast.RShift: '>>', ast.Pow: '**'}
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmts_to_ir(self, stmts: List[ast.stmt]) -> List[int]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_ghost_assign(self, ga) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_assign(self, stmt: ast.Assign, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_augassign(self, stmt: ast.AugAssign, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_return(self, stmt: ast.Return, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_while(self, stmt: ast.While, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_for(self, stmt: ast.For, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_if(self, stmt: ast.If, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_continue(self, stmt: ast.Continue, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_assert(self, stmt: ast.Assert, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_raise(self, stmt: ast.Raise, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_annassign(self, stmt: ast.AnnAssign, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_expr(self, stmt: ast.Expr, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_try(self, stmt: ast.Try, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_with(self, stmt: ast.With, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_pass(self, stmt: ast.Pass, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_break(self, stmt: ast.Break, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_delete(self, stmt: ast.Delete, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _py_stmt_match(self, stmt: Any, ir_stmts: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _process_while(self, node: ast.While) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _process_for(self, node: ast.For) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _process_if(self, node: ast.If) -> int:
        return {}

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


