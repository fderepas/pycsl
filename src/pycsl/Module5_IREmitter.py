from __future__ import annotations

import pure_ast as ast  # consume the same pure-Python tree Module3 builds
import json
from typing import Any, Dict, List, Optional, Set, Tuple
from errors import PyCSLIRError
from module5.memoization_rt import MemoizationRTMixin
from module5.construction_synth import ConstructionSynthMixin
from Module4_SemanticAnalyzer import collect_module_constants, collect_module_globals
from Module2_Parser import (
    CSLNode, ContractWrapper,
    Requires, Ensures, LoopInvariant, LoopVariant,
    BinOp as CSLBinOp, UnaryOp as CSLUnaryOp, Var as CSLVar,
    Number as CSLNumber, Result as CSLResult, Old as CSLOld, Nothing,
    FieldAccess as CSLFieldAccess, FieldSubscript as CSLFieldSubscript,
    Forall, Exists, ArrayLength, InGlobals, SubscriptAccess,
    AssignsRegion, Valid, Separated, At as CSLAt,
    Length2D, Valid2D, FunctionVariant, StringLiteral as CSLStringLiteral,
    CallExpr, IsSorted, ArrayEq, Permutation, Sum, CSLBool, CSLNone, CSLIn, CSLNotIn, CSLSlice, DictView, ForallItems,
    ChainedSubscript,
    GhostArraySetDecl,
    MkTupleExpr, FstExpr, SndExpr, ProjExpr, CtorTest, CtorPayload,
    StrConcatExpr, StrLengthExpr, StrSubExpr,
    GhostCopyExpr, GhostCopyRangeExpr, GhostMakeExpr,
    MapEmptyExpr, MapGetExpr, MapSetExpr, MapEqExpr, HasKeyExpr, MapRemoveExpr,
    SetEmptyExpr, SetAddExpr, SetRemoveExpr, SetMemExpr,
    SetUnionExpr, SetInterExpr, SetDiffExpr, SetCardExpr,
    SetSubsetExpr, SetEqExpr,
    NilExpr, ConsExpr, HdExpr, TlExpr, ListLengthExpr,
    NthExpr, MemExpr, AppendExpr,
)

class PyCSLToJSONEmitter(MemoizationRTMixin, ConstructionSynthMixin, ast.NodeVisitor):
    """Walks the Annotated AST and translates it into a JSON-serializable IR."""

    def __init__(self) -> None:
        self.program_ir = {"type_decls": [], "functions": []}
        self._current_class: Optional[str] = None
        # scc3.md Phase B: the current function's symbol table, set while building its
        # contracts so `_csl_in` can dispatch `x in S` on the collection's type (a set
        # → key membership, a list → positional `exists`). Empty outside that window.
        self._cur_func_symtab: Dict[str, Any] = {}
        self._fresh_var_counter: int = 0
        self._mutex_invariants_csl: Dict[str, Any] = {}  # mutex → CSLNode

    def visit_Module(self, node: ast.Module) -> None:
        """Emit module-level concurrency declarations into the top-level IR."""
        shared_decls = getattr(node, 'csl_shared_decls', [])
        mutex_invs = getattr(node, 'csl_mutex_invariants', {})
        lock_order = getattr(node, 'csl_lock_order', None)

        # Store CSL nodes so _get_mutex_invariant_ir can look them up later
        self._mutex_invariants_csl = dict(mutex_invs)

        if shared_decls:
            self.program_ir["shared_vars"] = [
                {"name": d.variable, "mutex": d.mutex}
                for d in shared_decls
            ]
        if mutex_invs:
            self.program_ir["mutex_invariants"] = {
                mutex: self._csl_to_ir(expr)
                for mutex, expr in mutex_invs.items()
            }
        if lock_order is not None:
            self.program_ir["lock_order"] = lock_order.order

        # module-constants-plan: module-level int constants (`K_IHDR = 0`) →
        # resolved to their literal in Module 6 (body and contract).
        module_consts = collect_module_constants(node)
        if module_consts:
            self.program_ir["module_constants"] = module_consts

        # inline.md Phase 1: module-level global object instances `g = C(...)`. Modeled
        # in Module 6 as a Why3 mutable-record global `let g : c = <ctor>`; the ctor
        # `value` reuses the record-construction lowering (`_call_record_constructor`).
        _class_names = {c.name for c in node.body if isinstance(c, ast.ClassDef)}
        # inline.md: also include names imported via `from X import Y` — they
        # may be classes defined in another module whose type_decl will be
        # injected later by _resolve_imported_classes.  collect_module_globals
        # filters out non-class uses anyway (must be a Call with that name).
        for stmt in node.body:
            if isinstance(stmt, ast.ImportFrom):
                for alias in stmt.names:
                    _class_names.add(alias.asname or alias.name)
        module_globals = collect_module_globals(node, _class_names)
        if module_globals:
            self.program_ir["module_globals"] = [
                {"name": nm, "class": call.func.id, "value": self._py_expr_to_ir(call)}
                for nm, call in module_globals.items()
            ]

        # collections-plan: synthesise record type_decls for module-level
        # `Name = namedtuple(...)` BEFORE visiting functions, so a `Name(...)`
        # construction resolves against `_record_types`.
        self._synthesize_namedtuple_records(node)

        # sum-types: `#@ datatype Name = C1 | C2(int) | …` → a variant type_decl, and a
        # constructor registry so a `C1` / `C2(x)` value and a `case C1()` pattern resolve.
        for dt in getattr(node, 'csl_datatypes', []):
            self.program_ir["type_decls"].append({
                "kind": "variant", "name": dt.name,
                # A5d: type parameters of a parametric datatype (`Option[T]`).
                "type_params": list(getattr(dt, "type_params", None) or []),
                "constructors": [{"name": c, "arity": len(tys), "payload": tys}
                                 for (c, tys) in dt.variants],
            })
            for (c, tys) in dt.variants:
                self.program_ir.setdefault("constructors", {})[c] = {
                    "type": dt.name, "arity": len(tys)}

        # inductive.md: `#@ inductive p(params): rule …` → a logic-level inductive
        # predicate. Each rule's Horn-clause body is an ordinary contract expr lowered
        # by Module 6; the IR carries name/signature/[(rule_name, clause_ir)].
        for ind in getattr(node, 'csl_inductives', []):
            self.program_ir.setdefault("inductive_decls", []).append({
                "name": ind.name,
                "signature": ind.signature,
                "rules": [(rname, self._csl_to_ir(rbody))
                          for (rname, rbody) in (ind.rules or [])],
                # inductive.md P2: mutually-inductive `with` group members.
                "members": [
                    {"name": mname, "signature": msig,
                     "rules": [(rn, self._csl_to_ir(rb)) for (rn, rb) in mrules]}
                    for (mname, msig, mrules) in (getattr(ind, 'members', None) or [])
                ],
            })

        self.generic_visit(node)

    def _get_mutex_invariant_ir(self, mutex: str) -> Optional[Dict[str, Any]]:
        """Return the IR form of the mutex invariant, or None if not declared."""
        csl_node = self._mutex_invariants_csl.get(mutex)
        if csl_node is None:
            return None
        return self._csl_to_ir(csl_node)

    def _fresh_var(self, prefix: str = "_mem") -> str:
        name = f"{prefix}_{self._fresh_var_counter}"
        self._fresh_var_counter += 1
        return name

    # --- 1. PyCSL Contract Serialization ---

    # Dispatch table: CSL node type → handler method name
    _CSL_HANDLERS: Dict[type, str] = {
        CSLBinOp:         "_csl_binop",
        CSLUnaryOp:       "_csl_unaryop",
        CSLFieldAccess:   "_csl_field_access",
        CSLFieldSubscript: "_csl_field_subscript",
        CSLVar:           "_csl_var",
        CSLNumber:        "_csl_number",
        CSLStringLiteral: "_csl_string",
        CSLBool:          "_csl_bool",
        CSLNone:          "_csl_none",
        CSLResult:        "_csl_result",
        CSLOld:           "_csl_old",
        Nothing:          "_csl_nothing",
        Forall:           "_csl_forall",
        ForallItems:      "_csl_forall_items",
        Exists:           "_csl_exists",
        ArrayLength:      "_csl_array_length",
        InGlobals:        "_csl_in_globals",
        SubscriptAccess:  "_csl_subscript",
        AssignsRegion:    "_csl_assigns_region",
        Valid:            "_csl_valid",
        Separated:        "_csl_separated",
        CSLAt:            "_csl_at",
        Length2D:         "_csl_length2d",
        Valid2D:          "_csl_valid2d",
        ContractWrapper:  "_csl_contract_wrapper",
        Requires:        "_csl_contract_wrapper",
        Ensures:         "_csl_contract_wrapper",
        LoopInvariant:   "_csl_contract_wrapper",
        LoopVariant:     "_csl_contract_wrapper",
        FunctionVariant:  "_csl_function_variant",
        CallExpr:         "_csl_call_expr",
        IsSorted:         "_csl_is_sorted",
        ArrayEq:          "_csl_array_eq",
        Permutation:      "_csl_permutation",
        Sum:              "_csl_sum",
        CSLIn:            "_csl_in",
        CSLNotIn:         "_csl_not_in",
        CSLSlice:         "_csl_slice",
        ChainedSubscript: "_csl_chained_subscript",
        # Ghost expression nodes
        MkTupleExpr:      "_csl_mktuple",
        FstExpr:          "_csl_fst",
        SndExpr:          "_csl_snd",
        ProjExpr:         "_csl_proj",
        CtorTest:         "_csl_ctor_test",
        CtorPayload:      "_csl_ctor_payload",
        StrConcatExpr:    "_csl_strconcat",
        StrLengthExpr:    "_csl_str_length",
        StrSubExpr:       "_csl_str_sub",
        GhostCopyExpr:      "_csl_ghost_copy",
        GhostCopyRangeExpr: "_csl_ghost_copy_range",
        GhostMakeExpr:      "_csl_ghost_make",
        MapEmptyExpr:     "_csl_map_empty",
        MapGetExpr:       "_csl_map_get",
        MapSetExpr:       "_csl_map_set",
        MapEqExpr:        "_csl_map_eq",
        HasKeyExpr:       "_csl_has_key",
        MapRemoveExpr:    "_csl_map_remove",
        SetEmptyExpr:     "_csl_set_empty",
        SetAddExpr:       "_csl_set_add",
        SetRemoveExpr:    "_csl_set_remove",
        SetMemExpr:       "_csl_set_mem",
        SetUnionExpr:     "_csl_set_union",
        SetInterExpr:     "_csl_set_inter",
        SetDiffExpr:      "_csl_set_diff",
        SetCardExpr:      "_csl_set_card",
        SetSubsetExpr:    "_csl_set_subset",
        SetEqExpr:        "_csl_set_eq",
        NilExpr:          "_csl_nil",
        ConsExpr:         "_csl_cons",
        HdExpr:           "_csl_hd",
        TlExpr:           "_csl_tl",
        ListLengthExpr:   "_csl_list_length",
        NthExpr:          "_csl_nth",
        MemExpr:          "_csl_mem",
        AppendExpr:       "_csl_append",
    }

    def _csl_to_ir(self, node: CSLNode) -> Dict[str, Any]:
        """Recursively translates PyCSL nodes into IR dictionaries."""
        handler_name = self._CSL_HANDLERS.get(type(node))
        if handler_name is None:
            raise PyCSLIRError(f"Unsupported CSL node: {type(node).__name__}", stage="ir-emit")
        return getattr(self, handler_name)(node)

    def _csl_binop(self, node: CSLBinOp) -> Dict[str, Any]:
        return {"type": "BinOp", "op": node.op,
                "left": self._csl_to_ir(node.left), "right": self._csl_to_ir(node.right)}

    def _csl_unaryop(self, node: CSLUnaryOp) -> Dict[str, Any]:
        return {"type": "UnaryOp", "op": node.op, "expr": self._csl_to_ir(node.expr)}

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

    def _csl_field_subscript(self, node: CSLFieldSubscript) -> Dict[str, Any]:
        # `self.<field>[i]` → Subscript of a FieldGet, reusing the existing
        # hoare subscript-of-field lowering (module6 `_handle_subscript`).
        return {"type": "Subscript",
                "value": {"type": "FieldGet", "object": "self", "field": node.field},
                "index": self._csl_to_ir(node.index)}

    def _csl_var(self, node: CSLVar) -> Dict[str, Any]:
        return {"type": "Var", "name": node.name}

    def _csl_number(self, node: CSLNumber) -> Dict[str, Any]:
        return {"type": "Number", "value": node.value}

    def _csl_string(self, node: CSLStringLiteral) -> Dict[str, Any]:
        return {"type": "String", "value": node.value}

    def _csl_bool(self, node: CSLBool) -> Dict[str, Any]:
        return {"type": "Bool", "value": node.value}

    def _csl_none(self, node: CSLNone) -> Dict[str, Any]:
        return {"type": "None"}

    def _csl_result(self, node: CSLResult) -> Dict[str, Any]:
        return {"type": "Result"}

    def _csl_old(self, node: CSLOld) -> Dict[str, Any]:
        # Old(FieldAccess) → OldField (flat node)
        if isinstance(node.expr, CSLFieldAccess):
            return {"type": "OldField", "object": node.expr.object, "field": node.expr.field}
        return {"type": "Old", "expr": self._csl_to_ir(node.expr)}

    def _csl_nothing(self, node: Nothing) -> Dict[str, Any]:
        return {"type": "Nothing"}

    def _csl_forall(self, node: Forall) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": "Forall", "var": node.var, "body": self._csl_to_ir(node.body)}
        # quantification.md: carry the typed/bounded binder only when present, so a
        # legacy `binder_type=None` quantifier yields a byte-identical IR dict.
        if getattr(node, "binder_type", None) is not None:
            d["binder_type"] = node.binder_type
        if getattr(node, "domain", None) is not None:
            d["domain"] = self._csl_to_ir(node.domain)
        return d

    def _csl_forall_items(self, node: ForallItems) -> Dict[str, Any]:
        # 07-1311 Q3: two-binder dict-items quantifier; Module6 lowers to a `match`.
        return {"type": "ForallItems", "key": node.key, "val": node.val,
                "map": node.coll, "body": self._csl_to_ir(node.body)}

    def _csl_exists(self, node: Exists) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": "Exists", "var": node.var, "body": self._csl_to_ir(node.body)}
        if getattr(node, "binder_type", None) is not None:
            d["binder_type"] = node.binder_type
        if getattr(node, "domain", None) is not None:
            d["domain"] = self._csl_to_ir(node.domain)
        return d

    def _csl_array_length(self, node: ArrayLength) -> Dict[str, Any]:
        return {"type": "ArrayLen", "var": node.var}

    def _csl_in_globals(self, node: InGlobals) -> Dict[str, Any]:
        return {"type": "InGlobals", "name": node.name}   # 07-1839 P2

    def _csl_subscript(self, node: SubscriptAccess) -> Dict[str, Any]:
        if node.array == "\\result":
            return {"type": "Subscript",
                    "value": {"type": "Result"},
                    "index": self._csl_to_ir(node.index)}
        return {"type": "Subscript",
                "value": {"type": "Var", "name": node.array},
                "index": self._csl_to_ir(node.index)}

    def _csl_chained_subscript(self, node: ChainedSubscript) -> Dict[str, Any]:
        inner = {"type": "Subscript",
                 "value": {"type": "Var", "name": node.array},
                 "index": self._csl_to_ir(node.index1)}
        return {"type": "Subscript",
                "value": inner,
                "index": self._csl_to_ir(node.index2)}

    def _csl_assigns_region(self, node: AssignsRegion) -> Dict[str, Any]:
        return {"type": "AssignsRegion", "base": node.base,
                "low": self._csl_to_ir(node.low), "high": self._csl_to_ir(node.high)}

    def _csl_valid(self, node: Valid) -> Dict[str, Any]:
        return {"type": "Valid", "base": node.base, "length": self._csl_to_ir(node.length)}

    def _csl_separated(self, node: Separated) -> Dict[str, Any]:
        return {"type": "Separated", "base1": node.base1,
                "len1": self._csl_to_ir(node.length1),
                "base2": node.base2, "len2": self._csl_to_ir(node.length2)}

    def _csl_at(self, node: CSLAt) -> Dict[str, Any]:
        return {"type": "At", "expr": self._csl_to_ir(node.expr), "label": node.label}

    def _csl_length2d(self, node: Length2D) -> Dict[str, Any]:
        return {"type": "Length2D", "base": node.base,
                "rows": self._csl_to_ir(node.rows), "cols": self._csl_to_ir(node.cols)}

    def _csl_valid2d(self, node: Valid2D) -> Dict[str, Any]:
        return {"type": "Valid2D", "base": node.base,
                "row": self._csl_to_ir(node.row), "col": self._csl_to_ir(node.col)}

    def _csl_contract_wrapper(self, node: ContractWrapper) -> Dict[str, Any]:
        return self._csl_to_ir(node.expr)

    def _csl_function_variant(self, node: FunctionVariant) -> Dict[str, Any]:
        ir: Dict[str, Any] = {"expr": self._csl_to_ir(node.expr)}
        if node.ordering:
            ir["ordering"] = node.ordering
        return ir

    def _csl_call_expr(self, node: CallExpr) -> Dict[str, Any]:
        return {"type": "Call", "func": node.func,
                "args": [self._csl_to_ir(a) for a in node.args]}

    def _csl_is_sorted(self, node: IsSorted) -> Dict[str, Any]:
        return {"type": "IsSorted", "base": node.base,
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_array_eq(self, node: ArrayEq) -> Dict[str, Any]:
        return {"type": "ArrayEq",
                "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_permutation(self, node: Permutation) -> Dict[str, Any]:
        return {"type": "Permutation",
                "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_sum(self, node: Sum) -> Dict[str, Any]:
        return {"type": "Sum", "base": node.base,
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_in(self, node: CSLIn) -> Dict[str, Any]:
        # scc3.md Phase B: a SET/dict collection has no positional order — `x in S` is
        # KEY membership, not a sequence search. Emit a raw `in` BinOp so Module 6's
        # `_emit_membership` lowers it to the clean `Map.get S x` test (e-matching-
        # friendly, no `Array.length` on a map). The collection name is read straight
        # off the CSL node (not via `_csl_to_ir`) so the list path below keeps its exact
        # `_fresh_var` allocation order → byte-identical. Lists/arrays / unknown types
        # fall through to the positional `exists`.
        # 07-1311 Q1.2: `x in range([lo,] hi)` is a direct integer-interval bound, NOT a
        # positional array search — desugar to `lo <= x and x < hi` (no `Array.length`).
        if isinstance(node.collection, CallExpr) and node.collection.func == "range":
            rargs = node.collection.args
            elt_ir = self._csl_to_ir(node.element)
            if len(rargs) == 1:
                lo_ir = {"type": "Number", "value": 0}
                hi_ir = self._csl_to_ir(rargs[0])
            else:
                lo_ir = self._csl_to_ir(rargs[0])
                hi_ir = self._csl_to_ir(rargs[1])
            return {"type": "BinOp", "op": "and",
                    "left": {"type": "BinOp", "op": "<=", "left": lo_ir, "right": elt_ir},
                    "right": {"type": "BinOp", "op": "<", "left": elt_ir, "right": hi_ir}}
        # 07-1311 Q3: dict views `d.keys()` / `d.values()` (`.items()` is the separate
        # two-binder form). `k in d.keys()` is key presence (≡ bare `k in d`); `v in
        # d.values()` is "v is stored under some key" — `exists _k. Map.get d _k = Some v`.
        if isinstance(node.collection, DictView):
            dv = node.collection
            elt_ir = self._csl_to_ir(node.element)
            coll_var = {"type": "Var", "name": dv.coll}
            if dv.kind == "keys":
                return {"type": "BinOp", "op": "in",
                        "left": elt_ir, "right": coll_var}
            if dv.kind == "values":
                kv = self._fresh_var("_dk")
                return {"type": "Exists", "var": kv,
                        "body": {"type": "MapValueIs",
                                 "map": dv.coll,
                                 "key": {"type": "Var", "name": kv},
                                 "value": elt_ir}}
            raise PyCSLIRError(
                f"`\\forall x in {dv.coll}.items()` (two-binder) is a 07-1311 follow-on; "
                f"use `.keys()`/`.values()` or the `\\forall k in {dv.coll};` key form")
        _coll_nm = getattr(node.collection, "name", None)
        # 07-0647-spec R10/S2.1: a `str` collection is NOT an array — `x in s` on a
        # string is substring containment, handled by Module6's `str_contains_op` (which
        # uses `string.String` and imports it). Desugaring it to the positional array
        # `exists … Array.length …` would use the wrong theory and leave `Array.length`
        # unbound. Defer to Module6 (as set/dict already do) by keeping the `in` BinOp.
        if _coll_nm is not None and self._cur_func_symtab.get(_coll_nm) in (
                "set", "dict", "frozenset", "str"):
            return {"type": "BinOp", "op": "in",
                    "left": self._csl_to_ir(node.element),
                    "right": self._csl_to_ir(node.collection)}
        # x in arr → ∃ v. 0 ≤ v ∧ v < length(arr) ∧ arr[v] == x
        mem_var = self._fresh_var("_mem")
        elt_ir = self._csl_to_ir(node.element)
        coll_ir = self._csl_to_ir(node.collection)
        coll_name = coll_ir.get("name", "_coll")
        return {
            "type": "Exists", "var": mem_var,
            "body": {"type": "BinOp", "op": "and",
                "left": {"type": "BinOp", "op": "and",
                    "left": {"type": "BinOp", "op": ">=",
                        "left": {"type": "Var", "name": mem_var},
                        "right": {"type": "Number", "value": 0}},
                    "right": {"type": "BinOp", "op": "<",
                        "left": {"type": "Var", "name": mem_var},
                        "right": {"type": "ArrayLen", "var": coll_name}}},
                "right": {"type": "BinOp", "op": "==",
                    "left": {"type": "Subscript",
                        "value": {"type": "Var", "name": coll_name},
                        "index": {"type": "Var", "name": mem_var}},
                    "right": elt_ir}}
        }

    def _csl_not_in(self, node: CSLNotIn) -> Dict[str, Any]:
        # x not in arr → ¬(x in arr)
        in_ir = self._csl_to_ir(CSLIn(node.element, node.collection))
        return {"type": "UnaryOp", "op": "not", "expr": in_ir}

    def _csl_slice(self, node: CSLSlice) -> Dict[str, Any]:
        return {"type": "SliceAccess",
                "value": {"type": "Var", "name": node.collection},
                "slice": {"type": "Slice",
                          "lower": self._csl_to_ir(node.low),
                          "upper": self._csl_to_ir(node.high),
                          "step": None}}

    # --- Ghost expression IR handlers ---

    def _csl_mktuple(self, node: MkTupleExpr) -> Dict[str, Any]:
        return {"type": "MkTuple", "elts": [self._csl_to_ir(e) for e in node.elts]}

    def _csl_fst(self, node: FstExpr) -> Dict[str, Any]:
        return {"type": "FstExpr", "tuple": self._csl_to_ir(node.tuple_expr)}

    def _csl_snd(self, node: SndExpr) -> Dict[str, Any]:
        return {"type": "SndExpr", "tuple": self._csl_to_ir(node.tuple_expr)}

    def _csl_proj(self, node: ProjExpr) -> Dict[str, Any]:
        return {"type": "ProjExpr", "tuple": self._csl_to_ir(node.tuple_expr),
                "index": int(node.index.value)}

    def _csl_ctor_test(self, node: CtorTest) -> Dict[str, Any]:
        return {"type": "CtorTest", "var": node.var, "ctor": node.ctor}

    def _csl_ctor_payload(self, node: CtorPayload) -> Dict[str, Any]:
        return {"type": "CtorPayload", "var": node.var, "ctor": node.ctor,
                "index": getattr(node, "index", 0)}

    def _csl_strconcat(self, node: StrConcatExpr) -> Dict[str, Any]:
        return {"type": "StrConcat", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_str_length(self, node: StrLengthExpr) -> Dict[str, Any]:
        return {"type": "StrLength", "string": self._csl_to_ir(node.string)}

    def _csl_str_sub(self, node: StrSubExpr) -> Dict[str, Any]:
        return {"type": "StrSub", "string": self._csl_to_ir(node.string),
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_ghost_copy(self, node: GhostCopyExpr) -> Dict[str, Any]:
        return {"type": "GhostCopy", "arr": node.arr}

    def _csl_ghost_copy_range(self, node: GhostCopyRangeExpr) -> Dict[str, Any]:
        return {"type": "GhostCopyRange", "arr": node.arr,
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_ghost_make(self, node: GhostMakeExpr) -> Dict[str, Any]:
        return {"type": "GhostMake", "size": self._csl_to_ir(node.size),
                "default": self._csl_to_ir(node.default)}

    def _csl_map_empty(self, node: MapEmptyExpr) -> Dict[str, Any]:
        return {"type": "MapEmpty"}

    def _csl_map_get(self, node: MapGetExpr) -> Dict[str, Any]:
        return {"type": "MapGet", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key)}

    def _csl_map_set(self, node: MapSetExpr) -> Dict[str, Any]:
        return {"type": "MapSet", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key), "value": self._csl_to_ir(node.value)}

    def _csl_map_eq(self, node: MapEqExpr) -> Dict[str, Any]:
        return {"type": "MapEq", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_has_key(self, node: HasKeyExpr) -> Dict[str, Any]:
        return {"type": "HasKey", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key)}

    def _csl_map_remove(self, node: MapRemoveExpr) -> Dict[str, Any]:
        return {"type": "MapRemove", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key)}

    def _csl_set_empty(self, node: SetEmptyExpr) -> Dict[str, Any]:
        return {"type": "SetEmpty"}

    def _csl_set_add(self, node: SetAddExpr) -> Dict[str, Any]:
        return {"type": "SetAdd", "set": self._csl_to_ir(node.set_expr),
                "elem": self._csl_to_ir(node.elem)}

    def _csl_set_remove(self, node: SetRemoveExpr) -> Dict[str, Any]:
        return {"type": "SetRemove", "set": self._csl_to_ir(node.set_expr),
                "elem": self._csl_to_ir(node.elem)}

    def _csl_set_mem(self, node: SetMemExpr) -> Dict[str, Any]:
        return {"type": "SetMem", "elem": self._csl_to_ir(node.elem),
                "set": self._csl_to_ir(node.set_expr)}

    def _csl_set_union(self, node: SetUnionExpr) -> Dict[str, Any]:
        return {"type": "SetUnion", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_set_inter(self, node: SetInterExpr) -> Dict[str, Any]:
        return {"type": "SetInter", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_set_diff(self, node: SetDiffExpr) -> Dict[str, Any]:
        return {"type": "SetDiff", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_set_card(self, node: SetCardExpr) -> Dict[str, Any]:
        return {"type": "SetCard", "set": self._csl_to_ir(node.set_expr),
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_set_subset(self, node: SetSubsetExpr) -> Dict[str, Any]:
        return {"type": "SetSubset", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_set_eq(self, node: SetEqExpr) -> Dict[str, Any]:
        return {"type": "SetEq", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_nil(self, node: NilExpr) -> Dict[str, Any]:
        return {"type": "Nil"}

    def _csl_cons(self, node: ConsExpr) -> Dict[str, Any]:
        return {"type": "Cons", "head": self._csl_to_ir(node.head),
                "tail": self._csl_to_ir(node.tail)}

    def _csl_hd(self, node: HdExpr) -> Dict[str, Any]:
        return {"type": "Hd", "list": self._csl_to_ir(node.list_expr)}

    def _csl_tl(self, node: TlExpr) -> Dict[str, Any]:
        return {"type": "Tl", "list": self._csl_to_ir(node.list_expr)}

    def _csl_list_length(self, node: ListLengthExpr) -> Dict[str, Any]:
        return {"type": "ListLength", "list": self._csl_to_ir(node.list_expr)}

    def _csl_nth(self, node: NthExpr) -> Dict[str, Any]:
        return {"type": "Nth", "list": self._csl_to_ir(node.list_expr),
                "index": self._csl_to_ir(node.index)}

    def _csl_mem(self, node: MemExpr) -> Dict[str, Any]:
        return {"type": "Mem", "elem": self._csl_to_ir(node.elem),
                "list": self._csl_to_ir(node.list_expr)}

    def _csl_append(self, node: AppendExpr) -> Dict[str, Any]:
        return {"type": "Append", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_list_to_ir(self, csl_list: List[CSLNode]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for c in csl_list:
            d = self._csl_to_ir(c)
            # Module3 tags act-desugared ensures with `act_name` for attribution;
            # carry it into the IR so Module6 can emit a `(* act NAME *)` comment.
            an = getattr(c, "act_name", None)
            if an is not None and isinstance(d, dict):
                d["act_name"] = an
            out.append(d)
        return out

    def _comprehension_generators_to_ir(self, generators: List[ast.comprehension]) -> List[Dict[str, Any]]:
        """Translate Python comprehension generators to IR."""
        return [
            {
                "target": gen.target.id if isinstance(gen.target, ast.Name) else "_comp_var",
                "iter": self._py_expr_to_ir(gen.iter),
                "ifs": [self._py_expr_to_ir(if_) for if_ in gen.ifs],
            }
            for gen in generators
        ]

    # --- 2. Python AST Serialization (Restricted Subset) ---
    def _py_op_to_str(self, op: ast.operator | ast.cmpop | ast.unaryop) -> str:
        return self._PY_OP_MAP.get(type(op), "?")

    # Dispatch table: Python AST expression type → handler method name
    _PY_EXPR_HANDLERS: Dict[type, str] = {
        ast.Name:       "_py_expr_name",
        ast.Constant:   "_py_expr_constant",
        ast.UnaryOp:    "_py_expr_unaryop",
        ast.BinOp:      "_py_expr_binop",
        ast.Compare:    "_py_expr_compare",
        ast.BoolOp:     "_py_expr_boolop",
        ast.Call:       "_py_expr_call",
        ast.Tuple:      "_py_expr_tuple",
        ast.Subscript:  "_py_expr_subscript",
        ast.List:       "_py_expr_list",
        ast.Attribute:  "_py_expr_attribute",
        ast.Dict:       "_py_expr_dict",
        ast.Set:        "_py_expr_set",
        ast.ListComp:   "_py_expr_listcomp",
        ast.SetComp:    "_py_expr_setcomp",
        ast.DictComp:   "_py_expr_dictcomp",
        ast.JoinedStr:  "_py_expr_fstring",
        ast.IfExp:      "_py_expr_ifexp",
        ast.Starred:    "_py_expr_starred",
        ast.NamedExpr:  "_py_expr_walrus",
        ast.Lambda:     "_py_expr_lambda",
        ast.Slice:      "_py_expr_slice",
    }

    def _py_expr_to_ir(self, expr: ast.expr) -> Dict[str, Any]:
        """Translates Python expressions into IR dictionaries."""
        handler_name = self._PY_EXPR_HANDLERS.get(type(expr))
        if handler_name is not None:
            return getattr(self, handler_name)(expr)
        return {"type": "UnknownPyExpr"}

    def _py_expr_name(self, expr: ast.Name) -> Dict[str, Any]:
        if expr.id in ("Ellipsis",):
            return {"type": "Number", "value": 0}
        if expr.id == "None":
            return {"type": "None"}
        return {"type": "Var", "name": expr.id}

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

    def _py_expr_unaryop(self, expr: ast.UnaryOp) -> Dict[str, Any]:
        return {"type": "UnaryOp", "op": self._py_op_to_str(expr.op),
                "expr": self._py_expr_to_ir(expr.operand)}

    def _py_expr_binop(self, expr: ast.BinOp) -> Dict[str, Any]:
        return {"type": "BinOp", "op": self._py_op_to_str(expr.op),
                "left": self._py_expr_to_ir(expr.left), "right": self._py_expr_to_ir(expr.right)}

    def _py_expr_compare(self, expr: ast.Compare) -> Dict[str, Any]:
        return {"type": "BinOp", "op": self._py_op_to_str(expr.ops[0]),
                "left": self._py_expr_to_ir(expr.left), "right": self._py_expr_to_ir(expr.comparators[0])}

    def _py_expr_boolop(self, expr: ast.BoolOp) -> Dict[str, Any]:
        op_str = "and" if isinstance(expr.op, ast.And) else "or"
        result = self._py_expr_to_ir(expr.values[0])
        for operand in expr.values[1:]:
            result = {"type": "BinOp", "op": op_str, "left": result, "right": self._py_expr_to_ir(operand)}
        return result

    def _py_expr_call(self, expr: ast.Call) -> Dict[str, Any]:
        if isinstance(expr.func, ast.Name):
            if expr.func.id == "deque":
                # collections-plan: `deque(...)` reduces to the list/array model. Lower
                # it to an empty array literal so it reuses the append/index/len
                # machinery verbatim (identical to `dq = []`). A seeded iterable is
                # modelled as empty (sound under-approximation); left-end ops
                # (appendleft/popleft) and pop are out of scope.
                return {"type": "ArrayLit", "elts": []}
            return {"type": "Call", "func": expr.func.id,
                    "args": [self._py_expr_to_ir(arg) for arg in expr.args]}
        elif isinstance(expr.func, ast.Attribute):
            parts: List[str] = []
            node = expr.func
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
                parts.reverse()
                return {"type": "Call", "func": ".".join(parts),
                        "args": [self._py_expr_to_ir(arg) for arg in expr.args]}
            receiver_ir = self._py_expr_to_ir(node)
            parts.reverse()
            return {"type": "Call", "func": ".".join(parts),
                    "args": [self._py_expr_to_ir(arg) for arg in expr.args],
                    "receiver": receiver_ir}
        return {"type": "UnknownPyExpr"}

    def _py_expr_tuple(self, expr: ast.Tuple) -> Dict[str, Any]:
        return {"type": "Tuple", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}

    def _py_expr_subscript(self, expr: ast.Subscript) -> Dict[str, Any]:
        value = self._py_expr_to_ir(expr.value)
        slice_node = expr.slice
        if isinstance(slice_node, ast.Index):
            slice_node = slice_node.value
        if isinstance(slice_node, ast.Slice):
            slice_ir = self._py_expr_to_ir(slice_node)
            return {"type": "SliceAccess", "value": value, "slice": slice_ir}
        index = self._py_expr_to_ir(slice_node)
        return {"type": "Subscript", "value": value, "index": index}

    def _py_expr_list(self, expr: ast.List) -> Dict[str, Any]:
        return {"type": "ArrayLit", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}

    def _py_expr_attribute(self, expr: ast.Attribute) -> Dict[str, Any]:
        if isinstance(expr.value, ast.Name) and expr.value.id == 'self':
            return {"type": "FieldGet", "object": "self", "field": expr.attr}
        obj_ir = self._py_expr_to_ir(expr.value)
        return {"type": "Attribute", "object": obj_ir, "attr": expr.attr}

    def _py_expr_dict(self, expr: ast.Dict) -> Dict[str, Any]:
        keys = [self._py_expr_to_ir(k) if k else {"type": "None"} for k in expr.keys]
        values = [self._py_expr_to_ir(v) for v in expr.values]
        return {"type": "DictLit", "keys": keys, "values": values}

    def _py_expr_set(self, expr: ast.Set) -> Dict[str, Any]:
        return {"type": "SetLit", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}

    def _py_expr_listcomp(self, expr: ast.ListComp) -> Dict[str, Any]:
        return {"type": "ListComp", "elt": self._py_expr_to_ir(expr.elt),
                "generators": self._comprehension_generators_to_ir(expr.generators)}

    def _py_expr_setcomp(self, expr: ast.SetComp) -> Dict[str, Any]:
        return {"type": "SetComp", "elt": self._py_expr_to_ir(expr.elt),
                "generators": self._comprehension_generators_to_ir(expr.generators)}

    def _py_expr_dictcomp(self, expr: ast.DictComp) -> Dict[str, Any]:
        return {"type": "DictComp", "key": self._py_expr_to_ir(expr.key),
                "value": self._py_expr_to_ir(expr.value),
                "generators": self._comprehension_generators_to_ir(expr.generators)}

    def _py_expr_fstring(self, expr: ast.JoinedStr) -> Dict[str, Any]:
        parts = []
        for v in expr.values:
            if isinstance(v, ast.Constant):
                parts.append({"type": "String", "value": str(v.value)})
            elif isinstance(v, ast.FormattedValue):
                parts.append(self._py_expr_to_ir(v.value))
            else:
                parts.append(self._py_expr_to_ir(v))
        return {"type": "FString", "parts": parts}

    def _py_expr_ifexp(self, expr: ast.IfExp) -> Dict[str, Any]:
        return {"type": "IfExpr", "test": self._py_expr_to_ir(expr.test),
                "body": self._py_expr_to_ir(expr.body),
                "orelse": self._py_expr_to_ir(expr.orelse)}

    def _py_expr_starred(self, expr: ast.Starred) -> Dict[str, Any]:
        return {"type": "Starred", "value": self._py_expr_to_ir(expr.value)}

    def _py_expr_walrus(self, expr: ast.NamedExpr) -> Dict[str, Any]:
        target_name = expr.target.id if isinstance(expr.target, ast.Name) else "_walrus"
        return {"type": "NamedExpr", "target": target_name,
                "value": self._py_expr_to_ir(expr.value)}

    def _py_expr_lambda(self, expr: ast.Lambda) -> Dict[str, Any]:
        params = [arg.arg for arg in expr.args.args]
        return {"type": "Lambda", "params": params,
                "body": self._py_expr_to_ir(expr.body)}

    def _py_expr_slice(self, expr: ast.Slice) -> Dict[str, Any]:
        lower = self._py_expr_to_ir(expr.lower) if expr.lower else None
        upper = self._py_expr_to_ir(expr.upper) if expr.upper else None
        step = self._py_expr_to_ir(expr.step) if expr.step else None
        return {"type": "Slice", "lower": lower, "upper": upper, "step": step}

    # Dispatch table: Python AST statement type → handler method name
    _PY_STMT_HANDLERS: Dict[type, str] = {
        ast.Assign:    "_py_stmt_assign",
        ast.AugAssign: "_py_stmt_augassign",
        ast.Return:    "_py_stmt_return",
        ast.While:     "_py_stmt_while",
        ast.For:       "_py_stmt_for",
        ast.If:        "_py_stmt_if",
        ast.Continue:  "_py_stmt_continue",
        ast.Assert:    "_py_stmt_assert",
        ast.Raise:     "_py_stmt_raise",
        ast.AnnAssign: "_py_stmt_annassign",
        ast.Expr:      "_py_stmt_expr",
        ast.Try:       "_py_stmt_try",
        ast.With:      "_py_stmt_with",
        ast.Pass:      "_py_stmt_pass",
        ast.Break:     "_py_stmt_break",
        ast.Delete:    "_py_stmt_delete",
    }

    # Dispatch table: Python AST operator type → operator string
    _PY_OP_MAP: Dict[type, str] = {
        ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "div",
        ast.Mod: "%",
        ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
        ast.USub: "-", ast.UAdd: "+", ast.Not: "not", ast.Invert: "~",
        ast.In: "in", ast.NotIn: "not in",
        ast.Is: "==", ast.IsNot: "!=",
        ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
        ast.LShift: "<<", ast.RShift: ">>", ast.Pow: "**",
    }

    def _py_stmts_to_ir(self, stmts: List[ast.stmt]) -> List[Dict[str, Any]]:
        ir_stmts: List[Dict[str, Any]] = []
        for stmt in stmts:
            for lname in getattr(stmt, 'csl_labels', []):
                ir_stmts.append({"stmt": "Label", "name": lname})
            for cp in getattr(stmt, 'csl_checkpoints', []):
                # `#@ assert P` / `#@ check P` — a real proof obligation before the
                # statement (distinct from the Python `assert` stmt, which is a no-op).
                pa = {"stmt": "ProofAssert", "kind": cp.kind,
                      "test": self._csl_to_ir(cp.expr)}
                origin = getattr(cp, "origin", None)
                if origin:                      # attribution for synthesized (e.g. HAPPY) checks
                    pa["origin"] = origin
                ir_stmts.append(pa)
            for ga in getattr(stmt, 'csl_ghost_assigns', []):
                ir_stmts.append(self._emit_ghost_assign(ga))
            handler_name = self._PY_STMT_HANDLERS.get(type(stmt))
            if handler_name is not None:
                result = getattr(self, handler_name)(stmt, ir_stmts)
            elif hasattr(ast, 'Match') and isinstance(stmt, ast.Match):
                self._py_stmt_match(stmt, ir_stmts)
            for ga in getattr(stmt, 'csl_trailing_ghost_assigns', []):
                ir_stmts.append(self._emit_ghost_assign(ga))
        return ir_stmts

    def _emit_ghost_assign(self, ga) -> Dict[str, Any]:
        """Build the IR dict for a ghost assignment (declaration or update). Shared by
        the leading (`csl_ghost_assigns`) and trailing (`csl_trailing_ghost_assigns`)
        emission loops."""
        if isinstance(ga, GhostArraySetDecl):
            return {"stmt": "GhostArraySet", "target": ga.target,
                    "index": self._csl_to_ir(ga.index),
                    "value": self._csl_to_ir(ga.value)}
        return {"stmt": "GhostAssign", "target": ga.target,
                "value": self._csl_to_ir(ga.value), "op": ga.op,
                "ghost_type": getattr(ga, 'declared_type', 'int')}

    def _py_stmt_assign(self, stmt: ast.Assign, ir_stmts: List[Dict[str, Any]]) -> None:
        target = stmt.targets[0]
        if isinstance(target, ast.Name):
            ir_stmts.append({"stmt": "Assign", "target": target.id, "value": self._py_expr_to_ir(stmt.value)})
        elif (isinstance(target, ast.Attribute) and
              isinstance(target.value, ast.Name) and
              target.value.id == 'self'):
            ir_stmts.append({"stmt": "FieldAssign", "object": "self", "field": target.attr,
                             "value": self._py_expr_to_ir(stmt.value)})
        elif isinstance(target, ast.Subscript):
            array_ir = self._py_expr_to_ir(target.value)
            slice_node = target.slice
            if isinstance(slice_node, ast.Index):
                slice_node = slice_node.value
            if isinstance(slice_node, ast.Slice):
                # `arr[lo:hi] = rhs` — slice (range) assignment. Lowered by
                # Module6 to a bounded `Array.blit` when rhs is array-typed.
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

    def _py_stmt_augassign(self, stmt: ast.AugAssign, ir_stmts: List[Dict[str, Any]]) -> None:
        if isinstance(stmt.target, ast.Name):
            ir_stmts.append({"stmt": "AugAssign", "target": stmt.target.id,
                             "op": self._py_op_to_str(stmt.op), "value": self._py_expr_to_ir(stmt.value)})
        elif (isinstance(stmt.target, ast.Attribute) and
              isinstance(stmt.target.value, ast.Name) and
              stmt.target.value.id == 'self'):
            ir_stmts.append({"stmt": "FieldAugAssign", "object": "self", "field": stmt.target.attr,
                             "op": self._py_op_to_str(stmt.op), "value": self._py_expr_to_ir(stmt.value)})
        elif isinstance(stmt.target, ast.Subscript):
            # collections-plan: `c[k] op= v` (subscript augmented assignment) was
            # silently dropped (no arm here). Desugar to a plain subscript store of
            # `(c[k]) op v` — reusing the proven ArraySet path (→ map_update_some for
            # a dict / Counter, Array.set for a list). Also fixes `arr[i] += v`.
            slice_node = stmt.target.slice
            if isinstance(slice_node, ast.Index):  # <3.9 compatibility
                slice_node = slice_node.value
            if not isinstance(slice_node, ast.Slice):
                read_ir = self._py_expr_to_ir(stmt.target)  # c[k] (read)
                ir_stmts.append({
                    "stmt": "ArraySet",
                    "array": self._py_expr_to_ir(stmt.target.value),
                    "index": self._py_expr_to_ir(slice_node),
                    "value": {"type": "BinOp", "op": self._py_op_to_str(stmt.op),
                              "left": read_ir, "right": self._py_expr_to_ir(stmt.value)}})

    def _py_stmt_return(self, stmt: ast.Return, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Return", "value": self._py_expr_to_ir(stmt.value) if stmt.value else None})

    def _py_stmt_while(self, stmt: ast.While, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append(self._process_while(stmt))

    def _py_stmt_for(self, stmt: ast.For, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append(self._process_for(stmt))

    def _py_stmt_if(self, stmt: ast.If, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append(self._process_if(stmt))

    def _py_stmt_continue(self, stmt: ast.Continue, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Continue"})

    def _py_stmt_assert(self, stmt: ast.Assert, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_node: Dict[str, Any] = {"stmt": "Assert", "test": self._py_expr_to_ir(stmt.test)}
        if stmt.msg and isinstance(stmt.msg, ast.Constant) and isinstance(stmt.msg.value, str):
            ir_node["msg"] = stmt.msg.value
        ir_stmts.append(ir_node)

    def _py_stmt_raise(self, stmt: ast.Raise, ir_stmts: List[Dict[str, Any]]) -> None:
        exc_ir: Dict[str, Any] = {"stmt": "Raise", "exc_type": None, "exc_value": None}
        if stmt.exc is not None:
            if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                exc_ir["exc_type"] = stmt.exc.func.id
                if stmt.exc.args:
                    exc_ir["exc_value"] = self._py_expr_to_ir(stmt.exc.args[0])
            elif isinstance(stmt.exc, ast.Name):
                exc_ir["exc_type"] = stmt.exc.id
        ir_stmts.append(exc_ir)

    def _py_stmt_annassign(self, stmt: ast.AnnAssign, ir_stmts: List[Dict[str, Any]]) -> None:
        if isinstance(stmt.target, ast.Name) and stmt.value is not None:
            ir_stmts.append({"stmt": "Assign", "target": stmt.target.id,
                             "value": self._py_expr_to_ir(stmt.value)})

    def _py_stmt_expr(self, stmt: ast.Expr, ir_stmts: List[Dict[str, Any]]) -> None:
        # Skip bare string-literal expressions (docstrings) — no WhyML equivalent.
        if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            return
        ir_stmts.append({"stmt": "Expr", "value": self._py_expr_to_ir(stmt.value)})

    def _py_stmt_try(self, stmt: ast.Try, ir_stmts: List[Dict[str, Any]]) -> None:
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

    def _py_stmt_with(self, stmt: ast.With, ir_stmts: List[Dict[str, Any]]) -> None:
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

    def _py_stmt_pass(self, stmt: ast.Pass, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Pass"})

    def _py_stmt_break(self, stmt: ast.Break, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Break"})

    def _py_stmt_delete(self, stmt: ast.Delete, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Pass"})  # model as no-op

    def _py_stmt_match(self, stmt: Any, ir_stmts: List[Dict[str, Any]]) -> None:
        subject_ir = self._py_expr_to_ir(stmt.subject)
        cases = []
        for case in stmt.cases:
            pattern_ir = self._match_pattern_to_ir(case.pattern)
            guard_ir = self._py_expr_to_ir(case.guard) if case.guard else None
            body_ir = self._py_stmts_to_ir(case.body)
            cases.append({"pattern": pattern_ir, "guard": guard_ir, "body": body_ir})
        ir_stmts.append({"stmt": "Match", "subject": subject_ir, "cases": cases})

    def _process_while(self, node: ast.While) -> Dict[str, Any]:
        return {
            "stmt": "While",
            "test": self._py_expr_to_ir(node.test),
            "invariants": self._csl_list_to_ir(getattr(node, 'csl_invariants', [])),
            "variants": self._csl_list_to_ir(getattr(node, 'csl_variants', [])),
            "body": self._py_stmts_to_ir(node.body)
        }

    def _process_for(self, node: ast.For) -> Dict[str, Any]:
        target = node.target.id if isinstance(node.target, ast.Name) else "_for_target"
        return {
            "stmt": "For",
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

    def _process_if(self, node: ast.If) -> Dict[str, Any]:
        return {
            "stmt": "If",
            "test": self._py_expr_to_ir(node.test),
            "body": self._py_stmts_to_ir(node.body),
            "orelse": self._py_stmts_to_ir(node.orelse)
        }

    def _match_pattern_to_ir(self, pattern: Any) -> Dict[str, Any]:
        """Translate a Python 3.10+ match pattern to IR."""
        if hasattr(ast, 'MatchValue') and isinstance(pattern, ast.MatchValue):
            return {"pattern": "Value", "value": self._py_expr_to_ir(pattern.value)}
        elif hasattr(ast, 'MatchSingleton') and isinstance(pattern, ast.MatchSingleton):
            if pattern.value is True:
                return {"pattern": "Value", "value": {"type": "Bool", "value": True}}
            elif pattern.value is False:
                return {"pattern": "Value", "value": {"type": "Bool", "value": False}}
            elif pattern.value is None:
                return {"pattern": "Value", "value": {"type": "None"}}
            return {"pattern": "Value", "value": {"type": "Number", "value": pattern.value}}
        elif hasattr(ast, 'MatchAs') and isinstance(pattern, ast.MatchAs):
            if pattern.name is None and pattern.pattern is None:
                return {"pattern": "Wildcard"}
            name = pattern.name if pattern.name else "_"
            if pattern.pattern:
                return {"pattern": "Capture", "name": name,
                        "inner": self._match_pattern_to_ir(pattern.pattern)}
            return {"pattern": "Capture", "name": name, "inner": None}
        elif hasattr(ast, 'MatchOr') and isinstance(pattern, ast.MatchOr):
            return {"pattern": "Or",
                    "alternatives": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
        elif hasattr(ast, 'MatchSequence') and isinstance(pattern, ast.MatchSequence):
            return {"pattern": "Sequence",
                    "elts": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
        elif hasattr(ast, 'MatchClass') and isinstance(pattern, ast.MatchClass):
            # sum-types: `case Ctor(p1, …):` — a constructor pattern with capture sub-patterns.
            ctor = pattern.cls.id if isinstance(pattern.cls, ast.Name) else "Unknown"
            return {"pattern": "Constructor", "ctor": ctor,
                    "captures": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
        return {"pattern": "Unknown"}

    def _scan_2d_in_expr(self, expr: Dict[str, Any], param_names: Set[str], result: Set[str]) -> None:
        """Recursively scan an IR expression dict for a[i][j] access patterns."""
        if not isinstance(expr, dict):
            return
        t = expr.get("type", "")
        if t == "Subscript":
            inner = expr.get("value", {})
            if inner.get("type") == "Subscript":
                root = inner.get("value", {})
                if root.get("type") == "Var" and root.get("name") in param_names:
                    # Exclude dict-style access (string indices) from 2D array detection
                    idx1 = inner.get("index", {})
                    idx2 = expr.get("index", {})
                    if idx1.get("type") != "String" and idx2.get("type") != "String":
                        result.add(root["name"])
            self._scan_2d_in_expr(inner, param_names, result)
            self._scan_2d_in_expr(expr.get("index", {}), param_names, result)
        elif t in ("BinOp",):
            self._scan_2d_in_expr(expr.get("left", {}), param_names, result)
            self._scan_2d_in_expr(expr.get("right", {}), param_names, result)
        elif t in ("UnaryOp",):
            self._scan_2d_in_expr(expr.get("expr", {}), param_names, result)
        elif t in ("Call",):
            for arg in expr.get("args", []):
                self._scan_2d_in_expr(arg, param_names, result)

    def _scan_2d_in_stmt(self, stmt: Dict[str, Any], param_names: Set[str], result: Set[str]) -> None:
        """Recursively scan an IR statement dict for a[i][j] access patterns."""
        s = stmt.get("stmt", "")
        if s == "ArraySet":
            arr = stmt.get("array", {})
            # a[i][j] = v  →  ArraySet(array=Subscript(Var(a), i), index=j, ...)
            if arr.get("type") == "Subscript":
                root = arr.get("value", {})
                if root.get("type") == "Var" and root.get("name") in param_names:
                    idx1 = arr.get("index", {})
                    idx2 = stmt.get("index", {})
                    if idx1.get("type") != "String" and idx2.get("type") != "String":
                        result.add(root["name"])
            self._scan_2d_in_expr(arr, param_names, result)
            self._scan_2d_in_expr(stmt.get("index", {}), param_names, result)
            self._scan_2d_in_expr(stmt.get("value", {}), param_names, result)
        elif s in ("Assign", "AugAssign", "Return"):
            self._scan_2d_in_expr(stmt.get("value", {}), param_names, result)
        elif s in ("While", "For"):
            self._scan_2d_in_expr(stmt.get("test", {}), param_names, result)
            for child in stmt.get("body", []):
                self._scan_2d_in_stmt(child, param_names, result)
        elif s == "If":
            self._scan_2d_in_expr(stmt.get("test", {}), param_names, result)
            for child in stmt.get("body", []):
                self._scan_2d_in_stmt(child, param_names, result)
            for child in stmt.get("orelse", []):
                self._scan_2d_in_stmt(child, param_names, result)

    def _collect_2d_params(self, body_ir: List[Dict[str, Any]],
                           param_names: Set[str]) -> List[str]:
        """Return sorted list of param names used as a[i][j] in the body IR."""
        result: Set[str] = set()
        for stmt in body_ir:
            self._scan_2d_in_stmt(stmt, param_names, result)
        return sorted(result)

    # --- 3. Main Traversal Hooks ---

    @staticmethod
    def _field_type_from_annotation(annotation: Optional[ast.expr]) -> str:
        """Lower a Python type annotation to the IR field-type tag.

        Bare names like `int`/`bool`/`str` are passed through (lowercased
        where appropriate). Parametric annotations recognise `List`/
        `Set`/`Dict`/`FrozenSet`/`Tuple` (head identifier, lowercased).
        `Optional[T]` and `Union[T, None]` unwrap to T. Everything else
        falls back to `int` (the legacy default)."""
        if annotation is None:
            return "int"
        if isinstance(annotation, ast.Name):
            name = annotation.id
            # Bare collection annotations on a field (`self.x: list`).
            # Mirrors the RHS-shape inference for plain assignments so an
            # annotated `array int` field resolves to "list" (→ `array int`
            # in the WhyML record), not the int default.
            if name in ("list", "tuple", "bytearray", "bytes"):
                return "list"
            if name == "dict":
                return "dict"
            if name in ("set", "frozenset"):
                return "set"
            if name in ("int", "bool", "str", "float"):
                return "int"
            # Unrecognised plain name — treat as int (e.g. user types).
            return "int"
        if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
            head = annotation.value.id
            if head == "Optional":
                inner = annotation.slice
                if isinstance(inner, ast.Subscript) and isinstance(inner.value, ast.Name):
                    return inner.value.id.lower()
                return "int"
            if head == "Union":
                inner = annotation.slice
                if isinstance(inner, ast.Tuple):
                    for elt in inner.elts:
                        if isinstance(elt, ast.Subscript) and isinstance(elt.value, ast.Name):
                            return elt.value.id.lower()
                return "int"
            return head.lower()
        return "int"

    @staticmethod
    def _mixin_field_type(type_str: str) -> str:
        """Map a `#@ shared_state`/`#@ touches_field` declared type to the record
        field type the type-decl emitter understands (the same coarsening used for
        __init__ fields): scalar/bool → `int`, containers keep their name."""
        t = (type_str or "int").strip()
        if t in ("list", "dict", "set", "frozenset", "tuple", "array", "string"):
            return "list" if t == "array" else t
        return "int"

    def _collect_class_fields(self, node: ast.ClassDef) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """Extract mutable fields and default values from __init__.

        Returns (fields, field_defaults) where fields is a list of
        {"name", "type", "mutable"} dicts and field_defaults maps
        field names to their initial int values. Type annotations on
        `self.x: T = ...` declarations (AnnAssign) are extracted via
        `_field_type_from_annotation`; plain assignments default to
        `int`.
        """
        fields: List[Dict[str, Any]] = []
        field_names_seen: Set[str] = set()
        field_defaults: Dict[str, int] = {}
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == '__init__':
                for stmt in ast.walk(child):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if (isinstance(target, ast.Attribute) and
                                    isinstance(target.value, ast.Name) and
                                    target.value.id == 'self' and
                                    target.attr not in field_names_seen):
                                # Infer type from RHS shape when no
                                # explicit annotation is present.
                                rhs = stmt.value
                                ftype = "int"
                                if isinstance(rhs, ast.Dict):
                                    ftype = "dict"
                                elif isinstance(rhs, ast.Set):
                                    ftype = "set"
                                elif isinstance(rhs, ast.List):
                                    ftype = "list"
                                elif isinstance(rhs, ast.Call) and isinstance(rhs.func, ast.Name):
                                    if rhs.func.id in ("set", "frozenset", "dict", "list"):
                                        ftype = rhs.func.id
                                fields.append({"name": target.attr, "type": ftype, "mutable": True})
                                field_names_seen.add(target.attr)
                                if isinstance(rhs, ast.Constant) and isinstance(rhs.value, (int, float)):
                                    field_defaults[target.attr] = int(rhs.value)
                                else:
                                    sz = self._array_init_size(rhs)
                                    if sz is not None:
                                        field_defaults[target.attr] = sz
                    elif isinstance(stmt, ast.AnnAssign):
                        if (isinstance(stmt.target, ast.Attribute) and
                                isinstance(stmt.target.value, ast.Name) and
                                stmt.target.value.id == 'self' and
                                stmt.target.attr not in field_names_seen):
                            ftype = self._field_type_from_annotation(stmt.annotation)
                            fields.append({"name": stmt.target.attr, "type": ftype, "mutable": True})
                            field_names_seen.add(stmt.target.attr)
                            if (stmt.value and isinstance(stmt.value, ast.Constant) and
                                    isinstance(stmt.value.value, (int, float))):
                                field_defaults[stmt.target.attr] = int(stmt.value.value)
                            elif stmt.value is not None:
                                sz = self._array_init_size(stmt.value)
                                if sz is not None:
                                    field_defaults[stmt.target.attr] = sz
        return fields, field_defaults

    @staticmethod
    def _array_init_size(rhs: ast.expr) -> Optional[int]:
        """Literal initial LENGTH of an array/list-valued RHS, else None.
        Recognises `bytearray(N)` / `list([0]*N)`-style calls, `[v] * N` /
        `N * [v]`, and a list/bytes literal. For a list/array FIELD this length
        is stored in `field_defaults` so record construction (`C()`) emits
        `Array.make <len> 0` (matching the field's `\\length` class invariant),
        rather than the int fallback `0`."""
        # bytearray(N) / bytes(N)
        if (isinstance(rhs, ast.Call) and isinstance(rhs.func, ast.Name)
                and rhs.func.id in ("bytearray", "bytes") and len(rhs.args) == 1):
            return PyCSLToJSONEmitter._const_int_value(rhs.args[0])
        # [v] * N  or  N * [v]
        if isinstance(rhs, ast.BinOp) and isinstance(rhs.op, ast.Mult):
            for a, b in ((rhs.left, rhs.right), (rhs.right, rhs.left)):
                if isinstance(a, ast.List):
                    n = PyCSLToJSONEmitter._const_int_value(b)
                    if n is not None:
                        return max(len(a.elts), 1) * n if a.elts else n
        # [e1, e2, ...]  /  b"..."
        if isinstance(rhs, ast.List):
            return len(rhs.elts)
        if isinstance(rhs, ast.Constant) and isinstance(rhs.value, bytes):
            return len(rhs.value)
        return None

    @staticmethod
    def _const_int_value(value: ast.expr) -> Optional[int]:
        """Return the int value of a constant expr (incl. unary -N), else None."""
        if isinstance(value, ast.Constant) and isinstance(value.value, int) \
                and not isinstance(value.value, bool):
            return int(value.value)
        if (isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub)
                and isinstance(value.operand, ast.Constant)
                and isinstance(value.operand.value, int)
                and not isinstance(value.operand.value, bool)):
            return -int(value.operand.value)
        return None

    def _collect_class_constants(self, node: ast.ClassDef,
                                 field_names: Set[str]) -> Dict[str, int]:
        """Collect class-body integer constants (`CAP = 64`, `O_EXCL = 128`).

        Only top-level `Name = <int literal>` / `Name: T = <int literal>`
        assignments in the class body are taken; names already used as
        instance fields (from __init__) are skipped. These let `self.CONST`
        lower to its literal in Module 6 instead of an opaque getattr.
        """
        constants: Dict[str, int] = {}
        for child in node.body:
            target: Optional[str] = None
            value: Optional[ast.expr] = None
            if (isinstance(child, ast.Assign) and len(child.targets) == 1
                    and isinstance(child.targets[0], ast.Name)):
                target = child.targets[0].id
                value = child.value
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                target = child.target.id
                value = child.value
            if target is None or value is None or target in field_names:
                continue
            iv = self._const_int_value(value)
            if iv is not None:
                constants[target] = iv
        return constants

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Collect fields from __init__, extract class invariants, record base
        classes, and emit a type_decl record.

        Inheritance (Layer B+C) is applied as a separate IR→IR pass
        (`_apply_inheritance` in pycsl.py) AFTER cross-module import resolution,
        so a base class defined in another module is available before the merge.
        Here we only record the base names in the type_decl.
        """
        self._current_class = node.name
        fields, field_defaults = self._collect_class_fields(node)
        # Capture both `class X(Base)` (ast.Name) and `class X(mod.Base)`
        # (ast.Attribute, e.g. `ast.NodeVisitor`) — for the dotted form we
        # record the attribute tail (`NodeVisitor`); cross-module resolution
        # (pycsl._resolve_imports) injects the named class from a module import.
        bases = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                bases.append(b.id)
            elif isinstance(b, ast.Attribute):
                bases.append(b.attr)
        # UB-7.2 — track presence of __hash__ / __eq__ so Module 6 can
        # emit the consistency goal in the preamble.
        method_names = {
            s.name for s in node.body if isinstance(s, ast.FunctionDef)
        }
        has_hash = "__hash__" in method_names
        has_eq = "__eq__" in method_names
        # Mixin composition (Tier 1). Record the composition at MODULE level (not on a
        # type_decl) so a method-only composer with no own fields stays an opaque
        # `type c = int` — its provided methods are cloned in as `(self: c)` functions
        # by `_apply_composition` (pycsl.py), no record needed unless it has real state.
        is_mixin = bool(getattr(node, 'csl_is_mixin', False))
        compose_from = list(getattr(node, 'csl_compose_from', []) or [])
        if compose_from:
            self.program_ir.setdefault("compositions", []).append(
                {"composer": node.name, "mixins": compose_from})
        # Stateful mixin (Tier-1 stateful composition): a `#@ mixin` whose methods
        # declare `#@ shared_state`/`#@ touches_field` fields but has no __init__ of
        # its own must still emit as a RECORD (not the opaque `type c = int`), so its
        # provided methods' `self.<field>` accesses type-check in isolation (S1
        # verify-once) and after they are cloned into the composer. Merge the declared
        # fields into `fields` (dedup by name; __init__ fields win).
        if is_mixin:
            seen = {f["name"] for f in fields}
            for m in node.body:
                if not isinstance(m, ast.FunctionDef):
                    continue
                for s in (list(getattr(m, 'csl_mixin_shared_state', []) or [])
                          + list(getattr(m, 'csl_touches_field', []) or [])):
                    if s.name in seen:
                        continue
                    seen.add(s.name)
                    fields.append({"name": s.name,
                                   "type": self._mixin_field_type(s.type_str),
                                   "mutable": True})
                    field_defaults.setdefault(s.name, 0)
        if fields or bases:
            class_invariants_ir = [self._csl_to_ir(inv.expr)
                                   for inv in getattr(node, 'csl_class_invariants', [])]
            field_witness = {f["name"]: field_defaults.get(f["name"], 0) for f in fields}
            constants = self._collect_class_constants(node, {f["name"] for f in fields})
            init_params, init_body = self._collect_init_construction(node)
            self.program_ir["type_decls"].append({
                "kind": "record", "name": node.name, "fields": fields,
                "class_invariants": class_invariants_ir, "field_defaults": field_witness,
                "has_hash": has_hash, "has_eq": has_eq,
                "is_unhashable": has_eq and not has_hash,
                "constants": constants, "bases": bases,
                "init_params": init_params, "init_body": init_body,
                "is_mixin": is_mixin, "compose_from": compose_from,
            })
        self.generic_visit(node)
        self._current_class = None

    def _should_skip_method(self, node: ast.FunctionDef) -> bool:
        """Return True if this method should be skipped (dunders, @property)."""
        if not self._current_class:
            return False
        if node.name.startswith('__') and node.name.endswith('__'):
            return True
        if any(isinstance(d, ast.Name) and d.id == 'property'
               for d in node.decorator_list):
            return True
        return False

    def _build_function_ir(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Build the core function IR dict (name, contracts, body)."""
        func_name = (f"{self._current_class.lower()}__{node.name}"
                     if self._current_class else node.name)
        symbol_table = {
            k: v for k, v in getattr(node, 'csl_symbol_table', {}).items()
            if k != 'self'
        }
        # scc3.md Phase B: expose this function's symbol table to `_csl_in` (built
        # below for contracts/body) so `x in S` dispatches on the collection type.
        self._cur_func_symtab = symbol_table
        return_annotation = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_annotation = node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return_annotation = str(node.returns.value)
            elif isinstance(node.returns, ast.Subscript):
                # Parametric annotations like `List[str]`, `Tuple[int, int]`,
                # `Dict[str, Any]`, `Optional[int]`. Capture the head identifier
                # (lower-cased so `List` → `list` matches Module6's existing
                # case-sensitive checks against the bare `list` annotation).
                if isinstance(node.returns.value, ast.Name):
                    head = node.returns.value.id
                    # `Optional[T]` reduces to T (we model `None` as `0`, so
                    # the optional-ness adds no type-level info Module6
                    # could use). Recurse into the inner type so
                    # `Optional[List[str]]` → `"list"`.
                    if head == "Optional":
                        inner = node.returns.slice
                        if isinstance(inner, ast.Name):
                            return_annotation = inner.id.lower()
                        elif isinstance(inner, ast.Subscript) and isinstance(inner.value, ast.Name):
                            return_annotation = inner.value.id.lower()
                        else:
                            return_annotation = "int"
                    elif head == "Union":
                        # `Union[T, None]` is equivalent to `Optional[T]`.
                        # General Union[T1, T2, …] collapses to int since
                        # Module6 has no sum-type model. Heuristic: pick
                        # the first non-None component.
                        inner = node.returns.slice
                        chosen = "int"
                        if isinstance(inner, ast.Tuple):
                            for elt in inner.elts:
                                if isinstance(elt, ast.Constant) and elt.value is None:
                                    continue
                                if isinstance(elt, ast.Name) and elt.id != "None":
                                    chosen = elt.id.lower()
                                    break
                                if isinstance(elt, ast.Subscript) and isinstance(elt.value, ast.Name):
                                    chosen = elt.value.id.lower()
                                    break
                        return_annotation = chosen
                    else:
                        return_annotation = head.lower()
        # Formal parameter names ONLY (excluding `self`). Distinct from
        # `symbol_table`, which Module4 also populates with local
        # variables, for-loop targets, and ghost vars. Module6's
        # parameter-mutation handling needs the unpolluted list to
        # decide which pre_decl_vars should be shadowed via
        # `let X = ref X in` (formal params) vs `let X = ref 0 in`
        # (other locals).
        formal_params = [a.arg for a in node.args.args if a.arg != 'self']
        # 1111-spec R7: positional default values (param name -> default IR), so a
        # cross-module call passing fewer args than the callee arity can fill the
        # missing trailing params from these defaults at the call site.
        param_defaults: Dict[str, Any] = {}
        _pos_args = node.args.args
        _defs = node.args.defaults
        if _defs:
            for _a, _d in zip(_pos_args[len(_pos_args) - len(_defs):], _defs):
                if _a.arg != 'self':
                    param_defaults[_a.arg] = self._py_expr_to_ir(_d)
        return {
            "name": func_name,
            "symbol_table": symbol_table,
            "param_defaults": param_defaults,
            # no-more-int-3 A1: dict var -> WhyML value type ν (string), for
            # string-valued dicts only (captured in Module4); int-valued dicts
            # have no entry and keep the `map int (option int)` path.
            "dict_value_types": dict(getattr(node, 'csl_dict_value_types', {})),
            "dict_key_types": dict(getattr(node, 'csl_dict_key_types', {})),
            "formal_params": formal_params,
            "return_annotation": return_annotation,
            "contracts": {
                "requires": self._csl_list_to_ir(getattr(node, 'csl_requires', [])),
                "ensures": self._csl_list_to_ir(getattr(node, 'csl_ensures', [])),
                "assigns": [self._csl_to_ir(t) for a in getattr(node, 'csl_assigns', []) for t in a.targets],
                "raises": [{"exc_type": r.exc_type, "condition": self._csl_to_ir(r.condition)}
                           for r in getattr(node, 'csl_raises', [])],
                # `no_exception E1, E2, ...` — list of exception names the
                # function commits to not raising. Phase 1 of the
                # NoException workplan; see exception_model.py for the
                # trigger table.
                "no_exception": list(getattr(node, 'csl_no_exception', []) or []),
                "no_exception_all": bool(getattr(node, 'csl_no_exception_all', False)),
            },
            "body": self._py_stmts_to_ir(node.body),
            "function_variants": self._csl_list_to_ir(getattr(node, 'csl_function_variants', [])),
            "diverges": getattr(node, 'csl_diverges', False),
            "trusted": getattr(node, 'csl_trusted', False),
            "abstract": getattr(node, 'csl_abstract', False),
            # 07-1143 R4: `#@ \preserves` opt-in (HAPPY trust boundary), surfaced in the
            # IR so `--soundness-report` can classify the function as Confinement-trusted.
            "preserves": getattr(node, 'csl_preserves', False),
            "lemma": getattr(node, 'csl_lemma', False),
            "uses": list(getattr(node, 'csl_uses', []) or []),
            # no-more-int Stage F: a memoizing decorator requires a referentially
            # transparent function (checked in _check_memoization_soundness).
            "memoized": self._is_memoized(node),
            "reviewer": getattr(node, 'csl_reviewer', ""),
            "bounded_int": getattr(node, 'csl_bounded_int', None),
            # §2.1.12 — proof citations from cross-validated Rocq+Lean
            # theorems. Module6 emits a Why3 `axiom` block in the
            # preamble for each entry; see docs/cross-validated-spec-sources.md.
            "proof": [
                {"prover": a.prover, "qualname": a.qualname}
                for a in getattr(node, 'csl_proof', [])
            ],
            # Mixin composition (Tier 1). `provides` lists the method names this
            # method is a provider for; `method_deps` are the declared
            # depends_method/requires_method interfaces (with their own contracts)
            # this method may call via `self.<m>(…)`. Module6 emits each dep as an
            # abstract `val` carrying its `ensures` so the provider verifies once
            # against it (S1); the Module4 composition pass (S2) discharges
            # provider ⊑ dependency. Empty for non-mixin methods → no effect.
            "provides": list(getattr(node, 'csl_provides', []) or []),
            "method_deps": [
                {"method": d["method"], "sig": d["sig"], "kind": d["kind"],
                 "requires": self._csl_list_to_ir(d["requires"]),
                 "ensures": self._csl_list_to_ir(d["ensures"])}
                for d in getattr(node, 'csl_method_deps', []) or []
            ],
            # Field classification (D1): names this mixin method declared it may touch.
            "shared_state": [{"name": s.name, "type": s.type_str}
                             for s in getattr(node, 'csl_mixin_shared_state', []) or []],
            "touches_field": [{"name": s.name, "type": s.type_str}
                              for s in getattr(node, 'csl_touches_field', []) or []],
        }

    def _detect_array_dimensions(self, func_ir: Dict[str, Any]) -> None:
        """Detect 2D and 1D array params from contracts and body access patterns."""
        symbol_table = func_ir["symbol_table"]
        # 0442.md B2 (no-more-int): `bytes`/`bytearray` are the byte-buffer array
        # class (`array int`), so they are 1-D array param candidates like `list`.
        candidate_params = {k for k, v in symbol_table.items()
                            if v in ("list", "Any", "bytes", "bytearray")}
        array2d: Set[str] = set()
        for req in func_ir["contracts"]["requires"]:
            if isinstance(req, dict) and req.get("type") == "Length2D":
                base = req.get("base")
                if base in candidate_params:
                    array2d.add(base)
        if candidate_params:
            array2d.update(self._collect_2d_params(func_ir["body"], candidate_params))
        if array2d:
            func_ir["array2d_params"] = sorted(array2d)
        array1d: Set[str] = set()
        for req in func_ir["contracts"]["requires"]:
            if isinstance(req, dict) and req.get("type") == "Valid":
                base = req.get("base")
                if base and base in candidate_params and base not in array2d:
                    array1d.add(base)
        # 07-1321 S4: a list/bytes/bytearray candidate that is the target of `+=`
        # (Python list/bytes extension → array concatenation) is array-typed too, even
        # without a `\valid` requires — otherwise `dst += src` mis-lowers to integer
        # `+` (an `array int` vs `int` type error). Routing it here sends it to the
        # array-extend path in `_handle_augassign_stmt`. (Faithful length-additive
        # concatenation is a documented follow-on; this removes the type error.)
        # Restrict to params DEFINITELY array-typed (`list`/`bytes`/`bytearray`),
        # excluding `Any`: an `Any`-typed int accumulator (`total += 1`) is also a `+=`
        # target and must NOT be reclassified as an array (that was the bug the `\valid`
        # gate guarded against).
        strict_array_cands = {k for k, v in symbol_table.items()
                              if v in ("list", "bytes", "bytearray")}

        def _collect_augextend(node, out):
            if isinstance(node, dict):
                if (node.get("stmt") == "AugAssign" and node.get("op") == "+"
                        and node.get("target") in strict_array_cands):
                    out.add(node["target"])
                for v in node.values():
                    _collect_augextend(v, out)
            elif isinstance(node, list):
                for x in node:
                    _collect_augextend(x, out)
        aug_ext: Set[str] = set()
        _collect_augextend(func_ir["body"], aug_ext)
        array1d |= (aug_ext - array2d)
        if array1d:
            func_ir["array1d_params"] = sorted(array1d)

    def _detect_seq_promotion(self, func_ir: Dict[str, Any]) -> None:
        """07-1705-rev4 P2 — the seq-promotion analysis (diagnostics only; no emission
        change). A `list`/`bytes`/`bytearray` variable is **seq-promoted** (must be
        modelled as `seq int`, a growable immutable value in a region-free ref) iff it is
        ever GROWN: the target of `+=` with a list RHS, or assigned `a + b` on lists. The
        mark propagates across `b = a` (representation must unify). A seq-promoted var
        that is also used in a 2-D context is a representation CONFLICT (rev4 §7) — a
        list cannot be both growable-seq and 2-D-array. Results are stored as IR metadata
        (`seq_promoted_vars`, `seq_promotion_conflicts`) for P3's lowering to consume;
        until P3 lands, the keys are inert and emission is byte-identical."""
        symbol_table = func_ir.get("symbol_table", {})
        list_vars = {k for k, v in symbol_table.items()
                     if v in ("list", "bytes", "bytearray")}
        # Locals assigned a list literal or a list-producing call are list-typed too
        # (the symbol table types them `Any`). Pre-pass to seed those.
        def _seed_list_vars(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign":
                    val = node.get("value", {})
                    if isinstance(val, dict):
                        if val.get("type") == "ArrayLit":
                            list_vars.add(node.get("target"))
                        elif (val.get("type") == "Call"
                              and val.get("func") in ("list", "sorted", "bytes", "bytearray")):
                            list_vars.add(node.get("target"))
                for v in node.values():
                    _seed_list_vars(v)
            elif isinstance(node, list):
                for x in node:
                    _seed_list_vars(x)
        _seed_list_vars(func_ir["body"])
        list_vars.discard(None)
        if not list_vars:
            return
        grown: Set[str] = set()
        edges: List[Tuple[str, str]] = []   # (target, source) for `b = a` unification

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                st = node.get("stmt")
                if (st == "AugAssign" and node.get("op") == "+"
                        and node.get("target") in list_vars):
                    grown.add(node["target"])
                elif st == "Assign":
                    tgt = node.get("target")
                    val = node.get("value", {})
                    if isinstance(val, dict):
                        if (val.get("type") == "BinOp" and val.get("op") == "+"
                                and tgt in list_vars):
                            for side in ("left", "right"):
                                s = val.get(side, {})
                                if (isinstance(s, dict) and s.get("type") == "Var"
                                        and s.get("name") in list_vars):
                                    grown.add(tgt)
                        if (val.get("type") == "Var" and tgt in list_vars
                                and val.get("name") in list_vars):
                            edges.append((tgt, val["name"]))
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for x in node:
                    walk(x)
        walk(func_ir["body"])

        # Unify representation across `b = a` edges: growth on either end ⇒ both seq.
        seq = set(grown)
        changed = True
        while changed:
            changed = False
            for t, s in edges:
                if (s in seq) != (t in seq):
                    seq.add(s); seq.add(t); changed = True

        if seq:
            func_ir["seq_promoted_vars"] = sorted(seq)
            # rev4 §7: a growable list cannot also be a 2-D array — flag the conflict.
            conflicts = seq & set(func_ir.get("array2d_params", []))
            if conflicts:
                func_ir["seq_promotion_conflicts"] = sorted(conflicts)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._should_skip_method(node):
            return
        func_ir = self._build_function_ir(node)
        self._detect_purity(func_ir)
        self._check_memoization_soundness(func_ir)
        self._detect_array_dimensions(func_ir)
        self._detect_seq_promotion(func_ir)   # 07-1705-rev4 P2 (diagnostics-only metadata)
        if getattr(node, 'csl_thread_entry', False):
            func_ir["thread_entry"] = True
            if "thread_entries" not in self.program_ir:
                self.program_ir["thread_entries"] = []
            self.program_ir["thread_entries"].append(func_ir["name"])
        if self._current_class:
            func_ir["kind"] = "method"
            func_ir["self_type"] = self._current_class
        self.program_ir["functions"].append(func_ir)
        self.generic_visit(node)

class Module5_IREmitter:
    """Consumes the validated AAST and outputs a JSON string."""
    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree

    def generate_json(self, indent: int = 2) -> str:
        emitter = PyCSLToJSONEmitter()
        emitter.visit(self.tree)
        return json.dumps(emitter.program_ir, indent=indent)
