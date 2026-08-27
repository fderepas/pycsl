from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from module6_whyml.identifiers import whyml_ident, safe_exc_name
from module6_whyml.ir_scanner import IRScanner

from ir_schema import (
    IfStmt, WhileStmt, ForStmt, TryStmt, MatchStmt, ReturnStmt,
)


class ControlFlowStmtMixin:
    """Control-flow statement handlers — `while` / `for` / `if` / `try` / `match`
    / `return` — plus their private helpers (`_classify_iterable`,
    `_first_assign_value_ir`, `_try_local_decl_kind`).

    Extracted verbatim from `StatementEmissionMixin` (Part B move 3e, mirroring
    the expressions.py split). `StatementEmissionMixin` inherits this mixin, so
    the handlers resolve via MRO through the facade's `_STMT_HANDLERS` table and
    recurse back into the core `self._stmts_to_whyml` / `self._expr_to_whyml`
    (which stay in `StatementEmissionMixin`)."""

    def _handle_while_stmt(self, stmt: WhileStmt, rest: List[Dict[str, Any]],
                            local_refs: Set[str], declared_refs: Set[str],
                            indent: str, in_loop: bool) -> str:
        _test_d = stmt.test.to_dict()
        test = self._expr_to_whyml(_test_d, local_refs)
        test = self._to_bool(test, _test_d)
        _body_d = [s.to_dict() for s in stmt.body]
        has_cont = IRScanner.has_continue(_body_d)
        has_direct_ret = IRScanner.has_direct_return(_body_d)

        loop_indent = (indent + "  ") if has_direct_ret else indent
        inner_indent = loop_indent + "  "

        body_str = self._stmts_to_whyml(
            _body_d, local_refs, declared_refs.copy(), inner_indent, in_loop=True)

        loop_code = f"{loop_indent}while {test} do\n"
        self._in_spec = True
        invariants_w = stmt.invariants
        n_inv_w = len(invariants_w)
        i_inv_w = 0
        while i_inv_w < n_inv_w:
            inv = invariants_w[i_inv_w]
            inv_str = self._expr_to_whyml(inv, local_refs)
            loop_code += f"{inner_indent}invariant {{ {inv_str} }}\n"
            i_inv_w += 1
        variants_w = stmt.variants
        n_var_w = len(variants_w)
        i_var_w = 0
        while i_var_w < n_var_w:
            var = variants_w[i_var_w]
            var_str = self._expr_to_whyml(var, local_refs)
            loop_code += f"{inner_indent}variant {{ {var_str} }}\n"
            i_var_w += 1
        self._in_spec = False
        if has_cont:
            loop_code += f"{inner_indent}try\n"
            loop_code += body_str + "\n"
            loop_code += f"{inner_indent}with PyCSL_Continue -> () end\n"
        else:
            loop_code += body_str + "\n"
        loop_code += f"{loop_indent}done"

        has_break = IRScanner.uses_break(_body_d)
        if has_break:
            loop_code = (f"{loop_indent}try\n{loop_code}\n"
                         f"{loop_indent}with PyCSL_Break -> () end")

        if has_direct_ret and not in_loop:
            rest_code = self._stmts_to_whyml(
                rest, local_refs, declared_refs, indent + "  ", in_loop)
            inner = loop_code
            if rest_code:
                inner += ";\n" + rest_code
            return (f"{indent}try\n{inner}\n"
                    f"{indent}with Return r -> r end")

        code = loop_code
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _classbody_psl_recv(self, iter_ir: Dict[str, Any]) -> Optional[str]:
        """self-tcb-reduction giants (generic class-/module-body lowering): if `iter_ir`
        is `<p>.body` where `<p>` is a `py_classdef_node`- OR `py_module_node`-typed param,
        return the iterated psl TERM (`class_body_ast <recv>` / `module_body_ast <recv>`);
        else None. J2/J3 generalized the original class-body recognizer to module bodies —
        both read the SAME shared `psl` cons-list, differing only in the projector."""
        if not (isinstance(iter_ir, dict) and iter_ir.get("type") == "Attribute"
                and iter_ir.get("attr") == "body"):
            return None
        obj = iter_ir.get("object", {})
        if not (isinstance(obj, dict) and obj.get("type") == "Var"):
            return None
        nm = obj.get("name")
        if nm in getattr(self, "_current_pyast_classdef_params", set()):
            return f"(class_body_ast {whyml_ident(nm)})"
        if nm in getattr(self, "_current_pyast_module_params", set()):
            return f"(module_body_ast {whyml_ident(nm)})"
        # K2 convergence (self-tcb-reduction, R1 nested-body dispatch): `<x>.body`
        # where `<x>` is a `pyast_stmt` LOCAL (an outer class-/module-body loop var,
        # e.g. `for cstmt in stmt.body` inside `for stmt in module_node.body`) reads
        # the local's `.body` psl via the `stmt_body` projector. The local is bound as
        # a `ref` by the enclosing loop, so its receiver term is `!<ident>`. Scoped via
        # `_pyast_stmt_locals` (populated only inside a class-/module-body loop) ->
        # corpus + every non-emitter mirror byte-identical.
        if nm in getattr(self, "_pyast_stmt_locals", set()):
            return f"(stmt_body !{whyml_ident(nm)})"
        return None

    def _tparam_iter_recv(self, iter_ir: Dict[str, Any]) -> Optional[str]:
        """L1 tparam reflection-node ADT (self-tcb-reduction, collector-family unlock): if
        `iter_ir` is `<node>.type_params` where `<node>` is a `py_tparam_node`-typed param,
        return the iterated tparam_list TERM `(type_params_of <node>)`; else None. The
        `class_body_ast`/`.body` precedent — a modelled cons-list, not the opaque int
        fallback. Scoped via `_current_tparam_node_params` -> corpus-inert.

        7a (self-tcb-reduction L4b): ALSO recognizes `for tp in <tparams>` where
        `<tparams>` is a LOCAL bound from `getattr(<node>,"type_params",None) or []` (the
        live `_collect_type_params` indirection) — a pure ALIAS for `(type_params_of
        <node>)` (an AST node always HAS a `.type_params` list, so the `or []` default is
        semantically inert). Scoped via `_tparam_list_aliases` -> corpus-inert."""
        if (isinstance(iter_ir, dict) and iter_ir.get("type") == "Var"
                and iter_ir.get("name") in getattr(self, "_tparam_list_aliases", {})):
            return self._tparam_list_aliases[iter_ir["name"]]
        if not (isinstance(iter_ir, dict) and iter_ir.get("type") == "Attribute"
                and iter_ir.get("attr") == "type_params"):
            return None
        obj = iter_ir.get("object", {})
        if not (isinstance(obj, dict) and obj.get("type") == "Var"):
            return None
        nm = obj.get("name")
        if nm in getattr(self, "_current_tparam_node_params", set()):
            return f"(type_params_of {whyml_ident(nm)})"
        return None

    def _tparam_bases_recv(self, iter_ir: Dict[str, Any]) -> Optional[str]:
        """7b (self-tcb-reduction L4b): if `iter_ir` is `<node>.bases` where `<node>` is a
        `py_tparam_node` param, return the node WhyML ident (so `for b in node.bases` reads
        `bases_of <node>`); else None. Scoped via `_current_tparam_node_params` ->
        corpus-inert."""
        if not (isinstance(iter_ir, dict) and iter_ir.get("type") == "Attribute"
                and iter_ir.get("attr") == "bases"):
            return None
        obj = iter_ir.get("object", {})
        if (isinstance(obj, dict) and obj.get("type") == "Var"
                and obj.get("name") in getattr(self, "_current_tparam_node_params", set())):
            return whyml_ident(obj["name"])
        return None

    def _prescan_tparam_list_aliases(self, body_stmts: List[Dict[str, Any]]) -> Dict[str, str]:
        """7a (self-tcb-reduction L4b): collect locals bound from `getattr(<node>,
        "type_params", None) or []` where `<node>` is a `py_tparam_node`-typed param.
        Each such local is a pure ALIAS for the tparam_list TERM `(type_params_of
        <node>)` — the assignment emits NOTHING and `for tp in <local>` iterates the
        modelled list. Returns {} for every function with no such binding (byte-inert).
        Recurses into nested blocks (the binding may sit in a branch)."""
        tp_params = getattr(self, "_current_tparam_node_params", set())
        aliases: Dict[str, str] = {}
        if not tp_params:
            return aliases

        def _visit(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign" and isinstance(node.get("target"), str):
                    v = node.get("value")
                    term = self._getattr_type_params_or_default(v, tp_params)
                    if term is not None:
                        aliases[node["target"]] = term
                for _k in ("body", "orelse", "finalbody", "handlers"):
                    _c = node.get(_k)
                    if isinstance(_c, list):
                        _visit(_c)
            elif isinstance(node, list):
                for _s in node:
                    _visit(_s)

        _visit(body_stmts)
        return aliases

    def _getattr_type_params_or_default(self, v: Any,
                                        tp_params: Set[str]) -> Optional[str]:
        """7a: if `v` is `getattr(<node>,"type_params",None) or []` (or the bare
        `getattr(<node>,"type_params",None)`) where node in tp_params, return the term
        `(type_params_of <node>)`; else None."""
        if not isinstance(v, dict):
            return None
        # peel an `or []` / `or {}` default (semantically inert for a real node list).
        if v.get("type") == "BinOp" and v.get("op") == "or":
            return self._getattr_type_params_or_default(v.get("left"), tp_params)
        if v.get("type") == "Call" and v.get("func") == "getattr":
            a = v.get("args") or []
            if (len(a) >= 2 and isinstance(a[0], dict) and a[0].get("type") == "Var"
                    and a[0].get("name") in tp_params
                    and isinstance(a[1], dict) and a[1].get("type") == "String"
                    and a[1].get("value") == "type_params"):
                return f"(type_params_of {whyml_ident(a[0]['name'])})"
        return None

    def _pyast_walk_recv(self, iter_ir: Dict[str, Any]) -> Optional[str]:
        """K2 convergence (self-tcb-reduction, R2 ast.walk dispatch): if `iter_ir` is
        `ast.walk(<x>)` where `<x>` is a `pyast_stmt` LOCAL (an enclosing class-/module-
        body loop var), return the iterated psl TERM `(ast_walk !<x>)`; else None.
        `ast.walk` recursively enumerates a node's descendants — modelled as the opaque
        `ast_walk` psl (a faithful over-approximation; the loop only isinstance-dispatches
        + reads projectors over each element). Scoped via `_pyast_stmt_locals` ->
        corpus + every non-emitter mirror byte-identical."""
        if not (isinstance(iter_ir, dict) and iter_ir.get("type") == "Call"):
            return None
        if iter_ir.get("func") not in ("ast.walk", "walk"):
            return None
        args = iter_ir.get("args") or []
        if len(args) != 1:
            return None
        a0 = args[0]
        if (isinstance(a0, dict) and a0.get("type") == "Var"
                and a0.get("name") in getattr(self, "_pyast_stmt_locals", set())):
            return f"(ast_walk !{whyml_ident(a0['name'])})"
        return None

    def _keyword_iter_recv(self, iter_ir: Dict[str, Any],
                           local_refs: Set[str]) -> Optional[str]:
        """J2/J3 convergence (Call-internals keyword iteration): if `iter_ir` is
        `<call>.keywords` where `<call>` is an emit_ir value (an `_emit_ir_local_vars`
        local, e.g. `call = stmt.value`), return the WhyML emit_ir receiver term; else
        None. Gated on `_uses_call_kw` (the whole keyword model). The iterated list is
        `call_keywords <recv>`."""
        if not self._uses_call_kw():
            return None
        if not (isinstance(iter_ir, dict) and iter_ir.get("type") == "Attribute"
                and iter_ir.get("attr") == "keywords"):
            return None
        obj = iter_ir.get("object", {})
        if (isinstance(obj, dict) and obj.get("type") == "Var"
                and obj.get("name") in getattr(self, "_emit_ir_local_vars", set())):
            return self._expr_to_whyml(obj, local_refs)
        return None

    def _hval_items_recv(self, iter_ir: Dict[str, Any]) -> Optional[str]:
        """self-tcb-reduction _namedtuple_positional_access: if `iter_ir` is a `.items()`
        call over an hval-typed dict self-field — either the dotted `self.<field>.items()`
        OR the defensive `getattr(self, "<field>", {}).items()` form — return the dotted
        `self.<field>` (whose `_self_field_dict_nu` == "hval"); else None. Gated on
        `_value_semantic` + a resolvable hval self-field -> corpus/other-mirror inert."""
        if not (self._value_semantic and isinstance(iter_ir, dict)
                and iter_ir.get("type") == "Call"):
            return None
        _f = iter_ir.get("func")
        _recv = None
        if isinstance(_f, str) and _f.endswith(".items"):
            _recv = _f[:-len(".items")]
        elif _f == "items":
            _rcv = iter_ir.get("receiver")
            _fld = self._getattr_self_field(_rcv) if isinstance(_rcv, dict) else ""
            if _fld:
                _recv = f"self.{_fld}"
        if _recv and "." in _recv and self._self_field_dict_nu(_recv) == "hval":
            return _recv
        return None

    def _hval_items_local_recv(self, iter_ir: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """self-tcb-reduction Tier-5 (union/match cluster C3): if `iter_ir` is `.items()`
        over an hval-valued LOCAL/param expression (`vinfo.get("constructors", {}).items()`
        — the `.items` receiver is a pyval `.get` producing a nested `hval`), return that
        receiver IR (so the caller views it via `hval_as_map`); else None. Gated on
        `_value_semantic` + a pyval `.items` receiver -> corpus/other-mirror inert."""
        if not (self._value_semantic and isinstance(iter_ir, dict)
                and iter_ir.get("type") == "Call"):
            return None
        _if = iter_ir.get("func")
        _irecv = None
        if isinstance(_if, str) and _if.endswith(".items"):
            _irecv = {"type": "Var", "name": _if[:-len(".items")]}
        elif _if == "items":
            _irecv = iter_ir.get("receiver")
        # cap1 (self-tcb-reduction `_refine_tuple_return_type`): the `.items()` receiver may
        # be `<pyval-get> or {}` — `(func.get("param_annotations") or {}).items()`, an `or`
        # BinOp whose LEFT is the pyval `.get` and RIGHT an empty dict literal. Unwrap to the
        # pyval-get left so `_expr_is_pyval` sees the real hval receiver. Gated on the method
        # -> byte-inert for the corpus and every other mirror.
        if (isinstance(_irecv, dict) and _irecv.get("type") in ("BinOp", "BoolOp")
                and _irecv.get("op") == "or"
                and self._emitting_refine_tuple_return_type()):
            _r = _irecv.get("right")
            if (isinstance(_r, dict) and _r.get("type") == "DictLit"
                    and not (_r.get("keys") or _r.get("values"))):
                _irecv = _irecv.get("left")
        if isinstance(_irecv, dict) and self._expr_is_pyval(_irecv):
            return _irecv
        return None

    def _zip_irlist_recv(self, iter_ir: Dict[str, Any]):
        """self-tcb-reduction _typeddict_record_literal (cap-3): if `iter_ir` is
        `zip(<irlist-local>, <irlist-local>)` (both args a Var bound to a DictLit child
        irlist — `_irlist_local_vars`), return the pair `(keys_ir, values_ir)` of the
        two arg IR nodes; else None. Feeds the faithful dual-emit_ir tuple-unpack (`for
        k, v in zip(keys, values)`): the loop runs `min(irlen keys, irlen values)` and
        binds `k = irnth i keys` / `v = irnth i values` (both emit_ir). Gated on a
        @mutable_state self + two irlist-local args -> corpus/other-mirror inert."""
        if (getattr(self, "_current_self_type", None)
                not in getattr(self, "_mutable_state_classes", set())):
            return None
        if not (isinstance(iter_ir, dict) and iter_ir.get("type") == "Call"
                and iter_ir.get("func") == "zip"):
            return None
        _a = iter_ir.get("args") or []
        _il = getattr(self, "_irlist_local_vars", set())
        if (len(_a) == 2 and isinstance(_a[0], dict) and _a[0].get("type") == "Var"
                and _a[0].get("name") in _il
                and isinstance(_a[1], dict) and _a[1].get("type") == "Var"
                and _a[1].get("name") in _il):
            return (_a[0], _a[1])
        return None

    def _str_lit_seq_elts(self, iter_ir: Dict[str, Any]):
        """The String-elt IR list if `iter_ir` is an ALL-string tuple/list/array literal
        — either DIRECT (`for k in ("body", "orelse")`) or a Var bound to one
        (`_str_literal_seq_locals`, `for prefix in array_prefixes`) — else None. Drives the
        faithful `seq string` materialisation in `_classify_iterable` (and the loop-target
        string-retyping in `_handle_for_stmt`)."""
        t = iter_ir.get("type")
        if t in ("Tuple", "ArrayLit", "ListLit"):
            elts = iter_ir.get("elts", [])
            if elts and all(isinstance(e, dict) and e.get("type") == "String"
                            and isinstance(e.get("value"), str) for e in elts):
                return elts
            return None
        if t == "Var":
            return getattr(self, "_str_literal_seq_locals", {}).get(iter_ir.get("name"))
        return None

    def _classify_iterable(self, iter_ir: Dict[str, Any],
                            local_refs: Set[str], idx: str) -> Tuple[str, str, bool]:
        """Classify a For loop's iterable. Returns (len_expr, elem_expr, is_range).
        Side-effect: sets self._for_idx_init to the initial counter value
        (default "0"; for `range(start, stop)`, the `start` expression).
        """
        self._for_idx_init = "0"
        self._pyast_loop_variant_len = None
        self._for_iter_materialize = None
        self._for_target_is_pyval = False
        self._for_items_hval_map = None
        # hval-retype (self-tcb-reduction Tier-5): `for info in <pyval-field>.values()`
        # (the `_field_type_for`/`_field_type_of` record-registry scan over
        # `self._record_types.values()`, retyped to `map string (option hval)`) iterates
        # an abstract-but-hval-TYPED over-approximation — each `info` is a real `hval`, so
        # the body's `info.get("whyml_name")` / `info.get("field_types").get(field)` lower
        # to the certified K7 `pairs_get` projections (NOT the int-erased `info_get_str`
        # facade). The iterator itself is abstract (a native Why3 `map` is not finitely
        # iterable), but the ELEMENT structure is real. `_for_target_is_pyval` tells
        # `_handle_for_stmt` to tag the loop var `_pyval_locals` for the body's duration.
        # Gated on a pyval self-field `.values()` receiver -> corpus + other mirrors inert.
        if (self._value_semantic and iter_ir.get("type") == "Call"
                and isinstance(iter_ir.get("func"), str)
                and iter_ir.get("func").endswith(".values")):
            _recv = iter_ir.get("func")[:-len(".values")]
            if self._self_field_dict_nu(_recv) == "hval" and "." in _recv:
                _obj, _fld = _recv.rsplit(".", 1)
                _mapw = self._expr_to_whyml(
                    {"type": "FieldGet", "object": _obj, "field": _fld},
                    local_refs)
                # hval_values_len/get are declared in the hval theory block
                # (_emit_pyval_theory) so they are always in scope on every emission path.
                self._for_target_is_pyval = True
                self._pyast_loop_variant_len = f"(hval_values_len {_mapw})"
                return (f"(hval_values_len {_mapw})",
                        f"(hval_values_get {_mapw} !{idx})", False)
        # self-tcb-reduction _namedtuple_positional_access: the `.items()` twin — `for k, v
        # in <hval-field>.items()` iterates the same over-approx (bound `hval_values_len`,
        # value `hval_values_get`); the KEY binding (an arbitrary `string`, `hval_keys_get`)
        # is emitted by `_handle_for_stmt`'s tuple binder. Here we only return the VALUE
        # element (the value target is the pyval loop var). Stash the map WhyML so the
        # tuple binder can build the key read. Gated on a pyval self-field `.items()`
        # receiver -> corpus/other-mirror inert.
        _items_recv = self._hval_items_recv(iter_ir)
        if _items_recv is not None:
            _obj, _fld = _items_recv.rsplit(".", 1)
            _mapw = self._expr_to_whyml(
                {"type": "FieldGet", "object": _obj, "field": _fld},
                local_refs)
            self._for_target_is_pyval = True
            self._for_items_hval_map = _mapw
            self._pyast_loop_variant_len = f"(hval_values_len {_mapw})"
            return (f"(hval_values_len {_mapw})",
                    f"(hval_values_get {_mapw} !{idx})", False)
        # self-tcb-reduction Tier-5 (union/match cluster C3): `.items()` over an hval-valued
        # LOCAL — `for ctor_name, ctor in vinfo.get("constructors", {}).items()`. The `.items`
        # RECEIVER is a pyval `.get` producing a nested `hval` (an `HMap`); view it as its
        # `map string (option hval)` carrier via `hval_as_map`, then iterate the SAME
        # over-approx (`hval_values_len`/`hval_values_get`, KEY via `hval_keys_get` in
        # `_handle_for_stmt`). Gated on `_value_semantic` + a pyval `.items` receiver ->
        # corpus/other-mirror byte-inert.
        _items_local = self._hval_items_local_recv(iter_ir)
        if _items_local is not None:
            _hv = self._expr_to_whyml(_items_local, local_refs)
            _mapw = f"(hval_as_map {_hv})"
            self._for_target_is_pyval = True
            self._for_items_hval_map = _mapw
            self._pyast_loop_variant_len = f"(hval_values_len {_mapw})"
            return (f"(hval_values_len {_mapw})",
                    f"(hval_values_get {_mapw} !{idx})", False)
        # self-tcb-reduction Tier-5 (union/match cluster, `_maybe_inject_union_return`): a
        # bare `for ctor_name in <pyval-dict-local>` iterates the dict's KEYS (Python dict
        # iteration yields keys). View the hval-LOCAL as its `map string (option hval)`
        # carrier via `hval_as_map`, bound `hval_values_len`, element `hval_keys_get ...
        # !idx` (a real `string` key per iteration), NOT the opaque `iter_length`/`iter_get`
        # int fallback. Scoped to a bare-Var pyval-local that is NOT a collection/list-read
        # local (`_pyval_coll_locals` = HArr sequences, which iterate as ELEMENTS) ->
        # corpus/other-mirror byte-inert (no corpus loop bare-iterates a pyval dict local).
        if (self._value_semantic and iter_ir.get("type") == "Var"
                and iter_ir.get("name") not in getattr(self, "_pyval_coll_locals", set())
                and self._expr_is_pyval(iter_ir)):
            _hv = self._expr_to_whyml(iter_ir, local_refs)
            _mapw = f"(hval_as_map {_hv})"
            self._pyast_loop_variant_len = f"(hval_values_len {_mapw})"
            return (f"(hval_values_len {_mapw})",
                    f"(hval_keys_get {_mapw} !{idx})", False)
        # self-tcb-reduction _typeddict_record_literal (cap-6/7 completion): the field-emit
        # loop `for fname in rec_info["fields"]` iterates the hval collection (`rec_info`'s
        # `"fields"` HArr of HStr names) as an ordered SEQUENCE — bound `hval_len <proj>`,
        # element `hval_nth_str <proj> !idx` (a real `string` per iteration, the certified
        # `_namedtuple_positional_access` hval-sequence view), NOT the opaque
        # `iter_length`/`iter_get` int fallback (which mis-projects `"fields"` as a scalar
        # string). Scoped to `_typeddict_record_literal` + a `_pyval_locals` subscript
        # receiver -> corpus/other-mirror byte-inert.
        if ((getattr(self, "_current_emitting_func", None) or "").endswith(
                "_typeddict_record_literal")
                and iter_ir.get("type") == "Subscript"
                and isinstance(iter_ir.get("value"), dict)
                and iter_ir["value"].get("type") == "Var"
                and iter_ir["value"].get("name") in getattr(self, "_pyval_locals", set())):
            _proj = self._tdrl_hval_field_proj(iter_ir, local_refs, False, None)
            if _proj is not None:
                self._pyast_loop_variant_len = f"(hval_len {_proj})"
                return (f"(hval_len {_proj})",
                        f"(hval_nth_str {_proj} !{idx})", False)
        # self-tcb-reduction giants (generic class-body lowering): `for child in
        # <classdef>.body` over a `py_classdef_node` param iterates the MODELLED
        # `class_body_ast node` psl cons-list — bound `psl_len (class_body_ast node)`,
        # element `psl_nth !idx (class_body_ast node)` (a real `pyast_stmt` per iteration),
        # NOT the opaque `iter_length`/`iter_get`/`get_body` int fallback. Sets
        # `_pyast_loop_variant_len` so `_handle_for_stmt` emits the arithmetic
        # invariant+variant (this class is not @mutable_state). Scoped via
        # `_current_pyast_classdef_params` -> corpus-inert.
        _cbw = self._classbody_psl_recv(iter_ir)
        if _cbw is not None:
            self._pyast_loop_variant_len = f"(psl_len {_cbw})"
            return (f"(psl_len {_cbw})", f"(psl_nth !{idx} {_cbw})", False)
        # K2 convergence (self-tcb-reduction, R2 ast.walk dispatch): `for sub in
        # ast.walk(<pyast_stmt local>)` iterates the opaque `ast_walk` psl — bound
        # `psl_len (ast_walk !cstmt)`, element `psl_nth !idx (ast_walk !cstmt)` (a real
        # `pyast_stmt` per iteration), NOT the opaque `iter_length`/`iter_get` int
        # fallback. Sets `_pyast_loop_variant_len` (arithmetic termination variant, this
        # class is not @mutable_state). Scoped via `_pyast_walk_recv` -> corpus-inert.
        _awr = self._pyast_walk_recv(iter_ir)
        if _awr is not None:
            self._pyast_loop_variant_len = f"(psl_len {_awr})"
            return (f"(psl_len {_awr})", f"(psl_nth !{idx} {_awr})", False)
        # L1 tparam reflection-node ADT: `for tp in <node>.type_params` over a
        # `py_tparam_node` param iterates the MODELLED `type_params_of node` tparam_list —
        # bound `tpl_len (type_params_of node)`, element `tpl_nth !idx (type_params_of
        # node)` (a real `tparam` per iteration), NOT the opaque `iter_length`/`iter_get`
        # int fallback. Sets `_pyast_loop_variant_len` (arithmetic termination variant;
        # this mirror class is not @mutable_state). Scoped via `_tparam_iter_recv` ->
        # corpus-inert.
        _tpr = self._tparam_iter_recv(iter_ir)
        if _tpr is not None:
            self._pyast_loop_variant_len = f"(tpl_len {_tpr})"
            return (f"(tpl_len {_tpr})", f"(tpl_nth !{idx} {_tpr})", False)
        # 7b (self-tcb-reduction L4b): `for b in <node>.bases` over a `py_tparam_node` param
        # iterates the MODELLED `bases_of node` emit_ir irlist — bound `irlen (bases_of
        # node)`, element `irnth !idx (bases_of node)` (a real emit_ir base per iteration, so
        # the body's `isinstance(b, ast.Subscript)`/`b.value`/`b.slice` reflect faithfully),
        # NOT the opaque `iter_length`/`iter_get`/`get_bases` int fallback. Scoped via
        # `_tparam_bases_recv` -> corpus-inert.
        _tbr = self._tparam_bases_recv(iter_ir)
        if _tbr is not None:
            self._pyast_loop_variant_len = f"(irlen (bases_of {_tbr}))"
            return (f"(irlen (bases_of {_tbr}))",
                    f"(irnth !{idx} (bases_of {_tbr}))", False)
        # J2/J3 convergence (Call-internals keyword iteration): `for kw in <call>.keywords`
        # over an emit_ir `call` local iterates the certified `keyword_list` — bound
        # `kwl_len (call_keywords call)`, element `kwl_nth !idx (call_keywords call)` (a real
        # `keyword` per iteration), NOT the opaque `iter_length`/`iter_get`. Scoped via
        # `_keyword_iter_recv` (an emit_ir recv whose `.keywords` is read) -> corpus-inert.
        _kwr = self._keyword_iter_recv(iter_ir, local_refs)
        if _kwr is not None:
            _kwl = f"(call_keywords {_kwr})"
            self._pyast_loop_variant_len = f"(kwl_len {_kwl})"
            return (f"(kwl_len {_kwl})", f"(kwl_nth !{idx} {_kwl})", False)
        # value-model campaign incr10 (loop-over-irlist): `for elt in <emit_ir>.elts` in an
        # annotation resolver iterates the MODELLED IrMkTupleN irlist — bound `irlen (elts_of
        # recv)`, element `irnth !idx (elts_of recv)` (a real emit_ir per iteration), NOT the
        # opaque `iter_length`/`iter_get` fallback. Scoped via `_mktuple_elts_recv_ir` (the
        # dict/legacy resolvers) → corpus-inert. The element type is registered emit_ir by
        # `_handle_for_stmt` so the body's `isinstance(elt, …)`/`elt.id` lower faithfully.
        _mt_recv = self._mktuple_elts_recv_ir(iter_ir)
        if _mt_recv is not None:
            _recv_w = self._expr_to_whyml(_mt_recv, local_refs)
            return (f"(irlen (elts_of {_recv_w}))",
                    f"(irnth !{idx} (elts_of {_recv_w}))", False)
        # self-tcb-reduction _typeddict_record_literal (cap-3): `for k, v in zip(keys,
        # values)` over two DictLit-child irlists. The loop runs `min(irlen keys, irlen
        # values)` (Python zip stops at the shorter); the per-iteration `k`/`v` bindings
        # (`irnth !idx keys` / `irnth !idx values`, both emit_ir) are emitted by the
        # `_bind_lines` `_is_zip_irlists` branch, NOT the single `elem_expr`. The min length
        # is an arithmetic termination variant (`_pyast_loop_variant_len`).
        _zip_recv = self._zip_irlist_recv(iter_ir)
        if _zip_recv is not None:
            _kw = self._expr_to_whyml(_zip_recv[0], local_refs)
            _vw = self._expr_to_whyml(_zip_recv[1], local_refs)
            _min = f"(if (irlen {_kw}) <= (irlen {_vw}) then (irlen {_kw}) else (irlen {_vw}))"
            self._pyast_loop_variant_len = _min
            return (_min, "(IrOther \"\")", False)
        # L18 S1 (split-as-for-iterable): `for part in <string>.split(sep)` /`.rsplit`
        # iterates the faithful `str_split_op … : array string` (NOT the opaque
        # `iter_length`/`iter_get`+`_coerce_to_int` int fallback below). The split array
        # is MATERIALISED ONCE as a `let` (recorded in `_for_iter_materialize`, emitted by
        # `_handle_for_stmt`) so the loop bound `Array.length arr` and the element read
        # `arr[!idx]` hit the SAME array — a plain `val str_split_op` re-evaluated twice
        # yields two distinct arrays and the element-bounds VC would not connect. The
        # element `arr[i]` is a substring → the loop target is a string local (registered
        # for the body in `_handle_for_stmt` + by `_collect_str_call_result_locals`). Gated
        # on `_value_semantic` + the exact `.split`/`.rsplit`-on-string shape → corpus-inert.
        _ssr = self._split_call_recv_sep(iter_ir) if self._value_semantic else None
        if _ssr is not None:
            _recv_ir, _sep_ir = _ssr
            _recvw = self._expr_to_whyml(_recv_ir, local_refs)
            _sepw = (self._expr_to_whyml(_sep_ir, local_refs)
                     if _sep_ir is not None else '" "')
            self._add_abstract_op(
                "val str_split_op (s: string) (sep: string) : array string\n"
                "    ensures { Array.length result >= 0 }")
            _sv = f"_split{idx}"
            self._for_iter_materialize = (_sv, f"(str_split_op {_recvw} {_sepw})")
            # Arithmetic termination variant: the counter runs 0..Array.length _sv,
            # incrementing by 1 (a pure LOGIC `Array.length`, legal in a `variant` term),
            # so `_handle_for_stmt` emits `invariant { 0 <= !idx }` + `variant { len - !idx }`
            # (this mirror class is not @mutable_state, so it has no variant otherwise).
            self._pyast_loop_variant_len = f"(Array.length {_sv})"
            return (f"Array.length {_sv}", f"{_sv}[!{idx}]", False)
        # faithful for-over-literal (self-tcb-reduction): `for k in ("body", "orelse")` /
        # `for prefix in array_prefixes` — a for-loop over an ALL-string tuple/list literal
        # (the emitter's OWN unmodeled Python literal), either DIRECT or via a Var bound to
        # one. Materialise it ONCE as a real `seq string` (a `Seq.cons` chain over the
        # literal's String elements, recorded in `_for_iter_materialize` and emitted as a
        # `let` wrapping the loop), then iterate faithfully — bound `Seq.length _seqlit` (a
        # pure LOGIC term, legal in the `variant` clause), element `Seq.get _seqlit !idx` (a
        # real `string` per iteration, so the body's `k in d` / `stripped.startswith(k)` route
        # through the faithful string ops). NOT the opaque `iter_length`/`iter_get` int
        # fallback (which int-erases the literal to `0` and leaves `variant` unbound).
        # Cert-free (Why3 Seq theory). Gated on an all-string literal → corpus-inert.
        _slit = self._str_lit_seq_elts(iter_ir) if self._value_semantic else None
        if _slit:
            _sv = f"_seqlit{idx}"
            _seq = "(Seq.empty: seq string)"
            for _e in reversed(_slit):
                _ew = self._expr_to_whyml(_e, local_refs)
                _seq = f"(Seq.cons {_ew} {_seq})"
            self._for_iter_materialize = (_sv, _seq)
            self._pyast_loop_variant_len = f"(Seq.length {_sv})"
            return (f"(Seq.length {_sv})", f"(Seq.get {_sv} !{idx})", False)
        is_range = (iter_ir.get("type") == "Call" and
                    iter_ir.get("func") == "range")
        if is_range and len(iter_ir.get("args", [])) == 1:
            bound = self._expr_to_whyml(iter_ir["args"][0], local_refs)
            return bound, f"!{idx}", True
        if is_range and len(iter_ir.get("args", [])) == 2:
            # `range(start, stop)` — initialise the idx at `start` and loop
            # while `!idx < stop`. The loop variable IS the idx.
            start = self._expr_to_whyml(iter_ir["args"][0], local_refs)
            stop = self._expr_to_whyml(iter_ir["args"][1], local_refs)
            self._for_idx_init = start
            return stop, f"!{idx}", True
        # G2 strings: `for c in s` over a string visits each 1-char substring once. The
        # bound is `str_length_op s` (= `String.length s`) and the element is the length-1
        # substring `str_sub_op s !idx 1`. Faithful: a string is a real Why3 string, the
        # loop count equals its length. Must precede the opaque `iter_length`/`iter_get`.
        if (iter_ir.get("type") == "Var" and self._value_semantic
                and getattr(self, "_current_symbol_table", {}).get(iter_ir.get("name", "")) == "str"):
            iter_expr = self._expr_to_whyml(iter_ir, local_refs)
            self._add_abstract_op(
                "val str_length_op (s: string) : int\n"
                "    ensures { result = (String.length s) }")
            self._add_abstract_op(
                "val str_sub_op (s: string) (lo len: int) : string\n"
                "    ensures { result = (String.substring s lo len) }\n"
                "    ensures { (0 <= lo /\\ 0 <= len /\\ lo + len <= String.length s)"
                " -> String.length result = len }")
            return (f"(str_length_op {iter_expr})",
                    f"(str_sub_op {iter_expr} !{idx} 1)", False)
        if iter_ir.get("type") == "Var" and self._value_semantic:
            var_name = iter_ir.get("name", "")
            iter_expr = self._expr_to_whyml(iter_ir, local_refs)
            # growable-list: iterating a seq-promoted var (e.g. a `.append`-ed
            # param being iterated over itself) reads through the `ref seq`
            # model — `iter_expr` is `!arr` (deref → seq int), so length/element
            # use `Seq.length`/`Seq.get`, NOT the array `Array.length`/subscript
            # (which would type-clash against the seq).
            if var_name in getattr(self, "_seq_locals", set()):
                return f"(Seq.length {iter_expr})", f"(Seq.get {iter_expr} !{idx})", False
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_current_array1d_params", set()) or
                # self-ir-schema.md IR4: a comprehension-bound array local
                # (`for var in shared_for_mutex`) iterates via `Array.length`/`arr[i]`.
                var_name in getattr(self, "_array_elem_types", {}))
            if not is_array and not is_dict:
                if getattr(self, "_current_symbol_table", {}).get(var_name) in ("list", "dict"):
                    is_array = True
            if is_array:
                return f"Array.length {iter_expr}", f"{iter_expr}[!{idx}]", False
            self._add_abstract_op("val iter_length (x: int) : int")
            self._add_abstract_op("val iter_get (x: int) (i: int) : int")
            return f"(iter_length {iter_expr})", f"(iter_get {iter_expr} !{idx})", False
        # `for x in self.<method>(...)` / `for x in <fn>(...)` where the
        # callee returns `array int`. Without this branch the iter
        # expression is `array int` but `iter_length`/`iter_get` are
        # declared `(x: int) : ...`, producing an `array int` vs `int`
        # type mismatch at the for-loop expansion.
        if (iter_ir.get("type") == "Call"
                and self._value_semantic):
            fn = iter_ir.get("func", "")
            ret_type = "int"
            if fn.startswith("self."):
                method_tail = fn[len("self."):]
                cls = self._current_self_type
                lookup_key = f"{cls}__{method_tail}" if cls else method_tail
                ret_type = self._module_method_return_types.get(lookup_key, "int")
            else:
                # Bare-name function call — check the module-level map
                # directly. Covers both class-prefixed names (when called
                # without `self.`) and free functions.
                ret_type = self._module_method_return_types.get(fn, "int")
            if ret_type == "array int":
                iter_expr = self._expr_to_whyml(iter_ir, local_refs)
                return f"Array.length {iter_expr}", f"{iter_expr}[!{idx}]", False
        # self-tcb-reduction T1.a: a slice/subscript of a `seq` local (`for _p in _parts[1:]`,
        # `_parts = s.split(".")`) iterates via `Seq.length`/`Seq.get` (the slice is a seq).
        # @mutable_state-gated → byte-identical for the corpus.
        if (self._value_semantic
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and iter_ir.get("type") in ("SliceAccess", "Subscript")):
            _base = iter_ir.get("value")
            _bn = _base.get("name") if isinstance(_base, dict) and _base.get("type") == "Var" else None
            if _bn and (_bn in getattr(self, "_seq_locals", set())
                        or getattr(self, "_seq_value_types", {}).get(_bn)):
                # 07-03-refactor R7: iterate the BASE seq from `lo` (`Seq.get parts idx`, idx from
                # lo) rather than materialising the slice as `seq_sub parts lo hi`. This keeps the
                # loop bound + variant as `Seq.length parts` — a pure LOGIC function usable in the
                # `variant {}` clause — instead of the program `val seq_sub`, which is unbound in a
                # logic term. Element bounds fall straight out of `idx < Seq.length parts`.
                _base_expr = self._expr_to_whyml(_base, local_refs)
                _sl = iter_ir.get("slice") or {}
                self._for_idx_init = (self._expr_to_whyml(_sl.get("lower"), local_refs)
                                      if isinstance(_sl, dict) and _sl.get("lower") else "0")
                return (f"(Seq.length {_base_expr})", f"(Seq.get {_base_expr} !{idx})", False)
            # 07-03-refactor R2: a `[lo:]` slice of an array-`emit_ir` local (`for pp in parts[1:]`,
            # `parts` from `expr.get("parts")`) iterates WITHOUT materialising the slice: run the
            # counter from `lo` up to `Array.length parts`, reading `parts[idx]` (emit_ir). The
            # element bounds fall straight out of the loop condition `idx < Array.length parts`
            # (unlike a `parts[lo+idx]` offset, whose bounds VC the invariant doesn't expose).
            if (iter_ir.get("type") == "SliceAccess" and _bn
                    and getattr(self, "_array_elem_types", {}).get(_bn) == "emit_ir"):
                _base_expr = self._expr_to_whyml(_base, local_refs)
                _sl = iter_ir.get("slice") or {}
                self._for_idx_init = (self._expr_to_whyml(_sl.get("lower"), local_refs)
                                      if isinstance(_sl, dict) and _sl.get("lower") else "0")
                return (f"Array.length {_base_expr}", f"{_base_expr}[!{idx}]", False)
        # self-tcb-reduction WRITER class (`_build_param_list`): `for arg in
        # self._formal_params` iterates the `seq string` source-ordered parameter sequence
        # (`formal_params_of self`) — use `Seq.length`/`Seq.get` (a real `string` element per
        # iteration), NOT the opaque int `iter_length`/`iter_get`. Gated -> byte-inert.
        if (self._emitting_build_param_list()
                and iter_ir.get("type") == "FieldGet"
                and iter_ir.get("object") == "self"
                and iter_ir.get("field") == "_formal_params"):
            # `formal_params_of self` is an OPAQUE `val : seq string` returning an
            # ARBITRARY seq per call, so re-reading it in the loop bound AND the element
            # read makes `Seq.length (formal_params_of self)` UNSTABLE across iterations —
            # the loop's termination VC then has no fixed measure and Alt-Ergo saturates
            # (E-matching flood, 31M steps). Materialise the seq ONCE as a stable local
            # `let _fp = formal_params_of self in` wrapping the whole loop (L18 S1
            # `_for_iter_materialize`), so the bound `Seq.length _fp` and the element
            # `Seq.get _fp !idx` reference the SAME fixed value, and carry the arithmetic
            # termination variant `Seq.length _fp - !idx` (a pure LOGIC term, legal in a
            # `variant`; the counter increments by 1 and is bounded by the loop condition,
            # so it strictly decreases and stays >= 0 — SMT-trivial). Gated on
            # `_emitting_build_param_list` -> byte-inert for the corpus and other mirrors.
            iter_expr = self._expr_to_whyml(iter_ir, local_refs)
            self._for_iter_materialize = ("_fp", iter_expr)
            self._pyast_loop_variant_len = "(Seq.length _fp)"
            return "(Seq.length _fp)", f"(Seq.get _fp !{idx})", False
        if not self._value_semantic:
            iter_expr = self._expr_to_whyml(iter_ir, local_refs)
            return f"{iter_expr}_len", f"Map.get !{self._heap_var} ({iter_expr} + !{idx})", False
        iter_expr = self._coerce_to_int(self._expr_to_whyml(iter_ir, local_refs))
        self._add_abstract_op("val iter_length (x: int) : int")
        self._add_abstract_op("val iter_get (x: int) (i: int) : int")
        return f"(iter_length {iter_expr})", f"(iter_get {iter_expr} !{idx})", False

    def _string_char_iter(self, iter_ir: Dict[str, Any], target: str,
                          tuple_targets: Optional[List[str]],
                          local_refs: Set[str]) -> Optional[Tuple[str, Optional[str], str, bool]]:
        """W2 — recognise character-level iteration over a STRING and return
        `(operand, idx_name, ch_name, is_tuple)`, else None. Two shapes:
          - `for i, ch in enumerate(s)` (tuple target, `is_tuple=True`): binds the
            index `i` and the 1-char string `ch = str_sub_op s !idx 1`. This case
            needs the dedicated dual-binding while-loop (`enumerate` is not a
            length-yielding iterable in `_classify_iterable`).
          - `for ch in s` (single target, `is_tuple=False`): `_classify_iterable`'s
            G2 branch already binds `ch = str_sub_op s !idx 1`; here we only report
            it so the caller can type `ch` as a string (so `ch == "("` routes through
            `str_eq_op`, not the int-hash).
        A char is a 1-char `str_sub_op` string; NO char type, NO new theory. Gated on
        `_value_semantic` and a string-typed operand → inert for the store model and
        any non-string iterable (byte-identical corpus)."""
        if iter_ir.get("type") == "Call" and iter_ir.get("func") == "enumerate":
            args = iter_ir.get("args", []) or []
            if (len(args) == 1 and isinstance(args[0], dict)
                    and self._is_string_expr(args[0])
                    and tuple_targets and len(tuple_targets) == 2):
                operand = self._expr_to_whyml(args[0], local_refs)
                return (operand, tuple_targets[0], tuple_targets[1], True)
        if (iter_ir.get("type") == "Var" and not tuple_targets
                and getattr(self, "_current_symbol_table", {}).get(
                    iter_ir.get("name", "")) == "str"):
            operand = self._expr_to_whyml(iter_ir, local_refs)
            return (operand, None, target, False)
        return None

    def _enumerate_seq_recv(self, iter_ir: Dict[str, Any],
                            tuple_targets: Optional[List[str]]) -> Optional[Tuple[Dict[str, Any], bool]]:
        """self-tcb-reduction (union/match cluster): recognise `for i, x in
        enumerate(<seq-string local>)` (`for i, ctor_name in enumerate(other_ctors)`).
        Return `(seq_ir, elem_is_str)` — the seq-Var IR node and whether its element type
        is `string` (`_seq_value_types == "string"`) — else None. The loop binds the index
        `i = !idx` (int) and the element `x = Seq.get !<seq> !idx` (string), with an
        arithmetic `Seq.length` variant. Gated on `_value_semantic`, a single
        `enumerate(<Var>)` arg, a 2-tuple target, and the Var being a seq local ->
        corpus/other-mirror byte-inert."""
        if not (self._value_semantic and isinstance(iter_ir, dict)
                and iter_ir.get("type") == "Call" and iter_ir.get("func") == "enumerate"):
            return None
        _a = iter_ir.get("args") or []
        if not (len(_a) == 1 and isinstance(_a[0], dict) and _a[0].get("type") == "Var"
                and tuple_targets and len(tuple_targets) == 2):
            return None
        _nm = _a[0].get("name", "")
        if _nm not in getattr(self, "_seq_locals", set()):
            return None
        _elem_str = getattr(self, "_seq_value_types", {}).get(_nm) == "string"
        return (_a[0], _elem_str)

    def _handle_for_stmt(self, stmt: ForStmt, rest: List[Dict[str, Any]],
                          local_refs: Set[str], declared_refs: Set[str],
                          indent: str, in_loop: bool) -> str:
        target = stmt.target
        safe_target = whyml_ident(target)
        iter_ir = stmt.iter.to_dict()
        idx = f"_idx_{safe_target}"
        _body_d = [s.to_dict() for s in stmt.body]
        has_direct_ret = IRScanner.has_direct_return(_body_d)
        loop_indent = (indent + "  ") if has_direct_ret else indent
        inner_indent = loop_indent + "  "

        tuple_targets = getattr(stmt, "tuple_targets", None)
        str_ci = (self._string_char_iter(iter_ir, target, tuple_targets, local_refs)
                  if self._value_semantic else None)
        # self-tcb-reduction (union/match cluster): `for i, x in enumerate(<seq local>)`.
        enum_seq = self._enumerate_seq_recv(iter_ir, tuple_targets)
        # W2: extra loop-bound names (a tuple target binds i AND ch) + typing the
        # char binding as a string so its `== "("` guards route through str_eq_op.
        extra_locals: Set[str] = set()
        saved_str_locals = None
        if str_ci is not None:
            _op, _idx_name, _ch_name, _is_tuple = str_ci
            extra_locals = {n for n in (_idx_name, _ch_name) if n and n != "_"}
            saved_str_locals = getattr(self, "_string_local_vars", set())
            self._string_local_vars = set(saved_str_locals) | {_ch_name}
        elif enum_seq is not None:
            # enumerate(<seq>) binds the index i (int) and the element x. Both tuple
            # targets are in scope for the body; a string-element seq types x as string.
            _en_extra = {t for t in (tuple_targets or []) if t and t != "_"}
            extra_locals = _en_extra
            if enum_seq[1]:   # string-element seq -> the element target is a string local
                saved_str_locals = getattr(self, "_string_local_vars", set())
                _en_elem = tuple_targets[1] if tuple_targets and len(tuple_targets) == 2 else None
                self._string_local_vars = set(saved_str_locals) | (
                    {_en_elem} if _en_elem and _en_elem != "_" else set())

        body_local = local_refs | {target} | extra_locals
        body_declared = declared_refs.copy() | {target} | extra_locals
        # value-model campaign incr10 (loop-over-irlist): when iterating a `<emit_ir>.elts`
        # IrMkTupleN irlist, the target `elt` binds a real `irnth`-projected emit_ir NODE, so
        # register it `ExprIR` in the symbol table for the loop body's duration → its
        # `isinstance(elt, …)`/`elt.id`/`elt.value` reads lower faithfully (is_var/name_of/…),
        # not the opaque int path. Restored after the body. Scoped to the mktuple iterables.
        _saved_symtype = _MISSING = object()
        # self-tcb-reduction giants: a class-body psl loop binds `child` to a real
        # `pyast_stmt` per iteration — register it in `_pyast_stmt_locals` (and symbol
        # table type "PyAstStmt") for the body's duration so the body's `isinstance(child,
        # ast.Assign)` / `child.value` / `child.targets[0]` lower to the ADT discriminants
        # and projectors, not the opaque int path. Restored after the body.
        # K2 convergence (self-tcb-reduction): a `for sub in ast.walk(<pyast_stmt local>)`
        # loop ALSO binds `sub` to a real `pyast_stmt` per iteration, so it registers the
        # loop var in `_pyast_stmt_locals` exactly like a `.body` psl loop (so the body's
        # `isinstance(sub, ast.AnnAssign)` / `sub.target` / `sub.annotation` reads lower to
        # the ADT discriminants + projectors, not the opaque int path).
        _is_classbody = (self._classbody_psl_recv(iter_ir) is not None
                         or self._pyast_walk_recv(iter_ir) is not None)
        # J2/J3 convergence: a keyword_list loop binds `kw` to a real `keyword` per
        # iteration — register it in `_keyword_locals` (+ symbol type "Keyword") so the
        # body's `kw.arg` / `kw.value` / `isinstance(kw.value, ast.Name)` / `kw.value.id`
        # lower to the certified keyword projectors, not the opaque int path.
        _is_kwbody = self._keyword_iter_recv(iter_ir, local_refs) is not None
        # L1 tparam reflection-node ADT: a tparam_list loop binds `tp` to a real `tparam`
        # per iteration — register it in `_tparam_locals` (+ symbol type "TParam") so the
        # body's `type(tp).__name__` / `tp.name` / `tp.bound` lower to the certified tparam
        # projectors, not the opaque int path.
        _is_tparambody = self._tparam_iter_recv(iter_ir) is not None
        # L18 S1: a `for part in <string>.split(sep)`/`.rsplit` loop binds `part` to a real
        # substring (`arr[!idx]`) per iteration → register it symbol-type "str" for the
        # body's duration so the body's `":" in part` / `part.split(":")[-1].strip()` lower
        # through the faithful string ops, not the opaque int path. Restored after the body.
        _is_splitbody = (self._value_semantic
                         and self._split_call_recv_sep(iter_ir) is not None)
        # self-tcb-reduction Tier-5 (union/match cluster, `_maybe_inject_union_return`): a
        # bare `for ctor_name in <pyval-dict-local>` binds `ctor_name` to a real dict KEY
        # `string` (`hval_keys_get`) per iteration → register it symbol-type "str" for the
        # body's duration so `val.startswith(ctor_name)` / `"None" in ctor_name` lower via
        # the faithful `str_startswith_op` / `str_contains_op`, not the opaque int path.
        # Restored after the body. Gated identically to the `_classify_iterable` recognizer
        # (a bare-Var pyval-local that is NOT a collection/list-read local) -> corpus inert.
        _is_pyval_keys = (self._value_semantic and iter_ir.get("type") == "Var"
                          and not tuple_targets
                          and iter_ir.get("name")
                          not in getattr(self, "_pyval_coll_locals", set())
                          and self._expr_is_pyval(iter_ir))
        # faithful for-over-literal (self-tcb-reduction): a `for prefix in <str-literal local>`
        # loop binds `prefix` to a real `string` (`Seq.get`) per iteration → register it
        # symbol-type "str" for the body's duration so `stripped.startswith(prefix)` lowers
        # via the faithful `str_startswith_op`, not the opaque int path. Restored after body.
        _is_strseqlit = (self._value_semantic and not tuple_targets
                         and self._str_lit_seq_elts(iter_ir) is not None)
        # hval-retype (self-tcb-reduction Tier-5): `for info in <pyval-field>.values()`
        # binds `info` to a real `hval` per iteration — register it in `_pyval_locals`
        # for the body's duration so `info.get("whyml_name")` /
        # `info.get("field_types").get(field)` lower to the certified K7 `pairs_get`
        # projections, not the int-erased `info_get_str` facade. Restored after the body.
        # Gated on a pyval self-field `.values()` receiver -> corpus/other-mirror inert.
        _is_pyval_values = (
            self._value_semantic and iter_ir.get("type") == "Call"
            and isinstance(iter_ir.get("func"), str)
            and iter_ir.get("func").endswith(".values")
            and self._self_field_dict_nu(iter_ir.get("func")[:-len(".values")]) == "hval")
        # self-tcb-reduction _namedtuple_positional_access: the `.items()` twin — `for k, v
        # in <hval-field>.items()` binds `k` to an arbitrary `string` (`hval_keys_get`) and
        # `v` to a real `hval` (`hval_values_get`). Register the VALUE target `v`
        # (tuple_targets[1]) in `_pyval_locals` for the body so `v.get("whyml_name")` /
        # `v.get("is_namedtuple")` lower via the certified `pairs_get`/`hval_truthy`, not the
        # int-erased facade. Gated on a pyval self-field `.items()` receiver -> corpus inert.
        _is_pyval_items = ((self._hval_items_recv(iter_ir) is not None
                            or self._hval_items_local_recv(iter_ir) is not None)
                           and tuple_targets and len(tuple_targets) == 2)
        _items_val_target = tuple_targets[1] if _is_pyval_items else None
        # cap1 value-string `.items()` variant (self-tcb-reduction `_refine_tuple_return_type`):
        # `for _k, _ty in (func.get("param_annotations") or {}).items()` binds the VALUE `_ty`
        # to a real `string` (`hstr_of (hval_values_get ...)`), NOT an `hval` — the map codomain
        # is a Python type-annotation string stored into a `map string (option string)` symbol
        # table (`_st[_k] = _ty`). Register `_ty` symbol-type "str" (not `_pyval_locals`). Gated
        # on the method -> byte-inert (every other `.items()` value binds an `hval` as before).
        _items_val_str = bool(_is_pyval_items
                              and self._emitting_refine_tuple_return_type())
        _saved_items_val_symtype = _MISSING
        if _is_pyval_items:
            # both tuple components are in scope for the body (key `string`, value `hval`).
            _items_extra = {t for t in tuple_targets if t and t != "_"}
            body_local = body_local | _items_extra
            body_declared = body_declared | _items_extra
        # self-tcb-reduction _typeddict_record_literal (cap-3): `for k, v in zip(keys,
        # values)` binds BOTH tuple components as immutable emit_ir (`irnth`-projected).
        # Register both symbol types "ExprIR" for the body's duration so `isinstance(k,
        # dict)` / `k.get("type")` / `k.get("value","")` / the `kv[...] = v` insert lower
        # via the emit_ir machinery (kind_of/value_of), not the opaque int path. Restored
        # after the body. Gated on `_zip_irlist_recv` -> corpus/other-mirror inert.
        _is_zip_irlists = (self._zip_irlist_recv(iter_ir) is not None
                           and tuple_targets and len(tuple_targets) == 2)
        _saved_zip_symtypes: Dict[str, Any] = {}
        if _is_zip_irlists:
            _zip_extra = {t for t in tuple_targets if t and t != "_"}
            body_local = body_local | _zip_extra
            body_declared = body_declared | _zip_extra
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                for _zt in _zip_extra:
                    _saved_zip_symtypes[_zt] = _st.get(_zt, _MISSING)
                    _st[_zt] = "ExprIR"
        _saved_pyval_member = None
        _saved_pyval_val_member = None
        _saved_for_pyval_flag = getattr(self, "_for_target_is_pyval", False)
        # The element `let` binding (`_loop_var_bindings`) is emitted DURING body
        # emission — before `_classify_iterable` runs — so set the immutable-bind flag
        # here (pre-body) too, else the loop var stays `ref hval` and the K7 `match info`
        # projection type-clashes against a `ref`.
        self._for_target_is_pyval = _is_pyval_values or _saved_for_pyval_flag
        if _is_pyval_values:
            if not hasattr(self, "_pyval_locals"):
                self._pyval_locals = set()
            _saved_pyval_member = target in self._pyval_locals
            self._pyval_locals.add(target)
        if (_is_pyval_items and _items_val_target and _items_val_target != "_"
                and _items_val_str):
            # value-string variant: register `_ty` as a `string` local (symbol-type "str"),
            # NOT a pyval hval — its `hstr_of`-projected binding is a real string.
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_items_val_symtype = _st.get(_items_val_target, _MISSING)
                _st[_items_val_target] = "str"
        elif _is_pyval_items and _items_val_target and _items_val_target != "_":
            if not hasattr(self, "_pyval_locals"):
                self._pyval_locals = set()
            _saved_pyval_val_member = _items_val_target in self._pyval_locals
            self._pyval_locals.add(_items_val_target)
        # self-tcb-reduction Tier-5 (union/match cluster sub-increment 2): the KEY target of
        # a pyval `.items()` loop (`for ctor_name, ctor in ...`) is bound to a real `string`
        # (`hval_keys_get`), so register its symbol type "str" for the body's duration — the
        # body's `"None" in ctor_name` then lowers via the faithful `str_contains_op`, not the
        # opaque int `contains_check`. Restored after the body. Corpus-inert (pyval `.items()`
        # is emitter-internal only).
        _saved_pyval_key_symtype = _MISSING
        _items_key_target = tuple_targets[0] if _is_pyval_items else None
        if _is_pyval_items and _items_key_target and _items_key_target != "_":
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_pyval_key_symtype = _st.get(_items_key_target, _MISSING)
                _st[_items_key_target] = "str"
        # self-tcb-reduction (union/match cluster): the ELEMENT target of a string-element
        # `enumerate(<seq>)` loop (`ctor_name` in `for i, ctor_name in enumerate(other_ctors)`)
        # is a real `string` (`Seq.get`), so register its symbol type "str" for the body's
        # duration — the body's `f"{ctor_name} {bind}"` / `"None" in ctor_name` then lower via
        # the faithful string ops, not `int_to_string`/`contains_check`.
        _saved_enum_elem_symtype = _MISSING
        _enum_elem_target = (tuple_targets[1]
                             if (enum_seq is not None and enum_seq[1] and tuple_targets
                                 and len(tuple_targets) == 2) else None)
        if _enum_elem_target and _enum_elem_target != "_":
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_enum_elem_symtype = _st.get(_enum_elem_target, _MISSING)
                _st[_enum_elem_target] = "str"
        if _is_classbody:
            self._pyast_stmt_locals.add(target)
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_symtype = _st.get(target, _MISSING)
                _st[target] = "PyAstStmt"
        elif _is_tparambody:
            self._tparam_locals.add(target)
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_symtype = _st.get(target, _MISSING)
                _st[target] = "TParam"
        elif _is_kwbody:
            if not hasattr(self, "_keyword_locals"):
                self._keyword_locals = set()
            self._keyword_locals.add(target)
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_symtype = _st.get(target, _MISSING)
                _st[target] = "Keyword"
        elif self._mktuple_elts_recv_ir(iter_ir) is not None:
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_symtype = _st.get(target, _MISSING)
                _st[target] = "ExprIR"
        # 7b (self-tcb-reduction L4b): `for b in <node>.bases` binds `b` to a real emit_ir
        # base per iteration — register it symbol-type "ExprIR" so the body's
        # `isinstance(b, ast.Subscript)` / `b.value` / `b.value.id` / `b.slice` lower via
        # the emit_ir machinery (is_sub / svalue_of / name_of / sindex_of), not the opaque
        # int path.
        elif self._tparam_bases_recv(iter_ir) is not None:
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_symtype = _st.get(target, _MISSING)
                _st[target] = "ExprIR"
        elif _is_splitbody:
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_symtype = _st.get(target, _MISSING)
                _st[target] = "str"
        elif _is_pyval_keys:
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_symtype = _st.get(target, _MISSING)
                _st[target] = "str"
        elif _is_strseqlit:
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                _saved_symtype = _st.get(target, _MISSING)
                _st[target] = "str"
        inner_body = self._stmts_to_whyml(
            _body_d, body_local, body_declared, inner_indent, True)
        if (_saved_symtype is not _MISSING or _is_classbody or _is_kwbody
                or _is_tparambody or _is_splitbody or _is_pyval_keys or _is_strseqlit
                or self._mktuple_elts_recv_ir(iter_ir) is not None
                or self._tparam_bases_recv(iter_ir) is not None):
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                if _saved_symtype is _MISSING:
                    _st.pop(target, None)
                else:
                    _st[target] = _saved_symtype
        if _is_classbody:
            self._pyast_stmt_locals.discard(target)
        if _is_tparambody:
            self._tparam_locals.discard(target)
        if _is_kwbody:
            self._keyword_locals.discard(target)
        if _is_pyval_values and _saved_pyval_member is False:
            self._pyval_locals.discard(target)
        if (_is_pyval_items and _items_val_target and _items_val_target != "_"
                and _items_val_str):
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                if _saved_items_val_symtype is _MISSING:
                    _st.pop(_items_val_target, None)
                else:
                    _st[_items_val_target] = _saved_items_val_symtype
        elif (_is_pyval_items and _items_val_target and _items_val_target != "_"
                and _saved_pyval_val_member is False):
            self._pyval_locals.discard(_items_val_target)
        if _is_pyval_items and _items_key_target and _items_key_target != "_":
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                if _saved_pyval_key_symtype is _MISSING:
                    _st.pop(_items_key_target, None)
                else:
                    _st[_items_key_target] = _saved_pyval_key_symtype
        if _enum_elem_target and _enum_elem_target != "_":
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                if _saved_enum_elem_symtype is _MISSING:
                    _st.pop(_enum_elem_target, None)
                else:
                    _st[_enum_elem_target] = _saved_enum_elem_symtype
        if _is_zip_irlists and _saved_zip_symtypes:
            _st = getattr(self, "_current_symbol_table", None)
            if _st is not None:
                for _zt, _sv in _saved_zip_symtypes.items():
                    if _sv is _MISSING:
                        _st.pop(_zt, None)
                    else:
                        _st[_zt] = _sv
        self._for_target_is_pyval = _saved_for_pyval_flag
        if not inner_body:
            inner_body = f"{inner_indent}()"
        if saved_str_locals is not None:
            self._string_local_vars = saved_str_locals

        has_cont = IRScanner.has_continue(_body_d)
        if str_ci is not None and str_ci[3]:
            # W2 tuple char-iteration: bound is `String.length s`; the counter runs
            # 0..len, the element is the 1-char `str_sub_op s !idx 1`. Bypasses
            # `_classify_iterable` (enumerate is not a length iterable there).
            self._for_idx_init = "0"
            self._add_abstract_op(
                "val str_length_op (s: string) : int\n"
                "    ensures { result = (String.length s) }")
            len_expr, elem_expr, is_range = f"(str_length_op {str_ci[0]})", None, False
        elif enum_seq is not None:
            # self-tcb-reduction (union/match cluster): `for i, x in enumerate(<seq>)` — the
            # bound is `Seq.length !seq`; the counter runs 0..len, the index i = !idx and the
            # element x = `Seq.get !seq !idx` (bound in `_bind_lines`). Bypasses
            # `_classify_iterable` (enumerate is not a length iterable there). The
            # @mutable_state arithmetic `Seq.length - !idx` variant (below) discharges
            # termination — a pure LOGIC term, legal in a `variant`.
            self._for_idx_init = "0"
            # reset the OUTER loop's structural variant (this loop bypasses
            # `_classify_iterable`, which is where it is normally cleared) so the
            # @mutable_state arithmetic `Seq.length - !idx` variant fires instead of a
            # stale `hval_values_len` term.
            self._pyast_loop_variant_len = None
            _enw = self._expr_to_whyml(enum_seq[0], local_refs)
            len_expr, elem_expr, is_range = f"(Seq.length {_enw})", None, False
        else:
            len_expr, elem_expr, is_range = self._classify_iterable(iter_ir, local_refs, idx)

        while_parts = [f"{loop_indent}while !{idx} < {len_expr} do"]
        # seq-model-pivot.md SQ5: a @mutable_state for-loop (the emitter's `for var in
        # shared_for_mutex`) carries the index bound + a decreasing variant so the element
        # read's `0 <= idx` and the loop's termination discharge (the `idx < len` upper bound
        # is the loop condition). @mutable_state-gated → the corpus for-loops are byte-identical.
        # W2: any character-level string iteration (single `for ch in s` OR the
        # tuple `for i, ch in enumerate(s)`) supplies its own arithmetic variant
        # below, so the @mutable_state block must not ALSO emit one (Why3 forbids
        # multiple `variant` clauses) — and its `str_length_op` variant term would
        # be illegal in a logic clause anyway.
        _str_char = str_ci is not None
        # self-tcb-reduction giants: the class-body psl loop carries an ARITHMETIC
        # termination variant `psl_len (class_body_ast node) - !idx` (a pure LOGIC
        # function, legal in a variant term) + the `0 <= !idx` invariant. This class
        # is not @mutable_state, so without this the loop would have no variant.
        # Gated on `_pyast_loop_variant_len` (set only for the psl loop) -> inert elsewhere.
        _psl_len = getattr(self, "_pyast_loop_variant_len", None)
        if _psl_len is not None and not _str_char:
            while_parts.append(f"{inner_indent}invariant {{ 0 <= !{idx} }}")
            while_parts.append(f"{inner_indent}variant {{ {_psl_len} - !{idx} }}")
        elif (getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and not _str_char):
            while_parts.append(f"{inner_indent}invariant {{ 0 <= !{idx} }}")
            while_parts.append(f"{inner_indent}variant {{ {len_expr} - !{idx} }}")
        # W2: character-level string iteration carries an ARITHMETIC termination
        # variant — the LOGIC `String.length s` (not the program `str_length_op`,
        # which is illegal in a variant term) strictly bounds the counter, and the
        # counter increments by 1 each iteration, so `String.length s - !idx`
        # decreases and stays >= 0 (SMT-trivial integer subtraction; no structural
        # measure). Gated on `str_ci` → inert for every non-string loop.
        if _str_char:
            _slen = f"(String.length {str_ci[0]})"
            while_parts.append(f"{inner_indent}invariant {{ 0 <= !{idx} <= {_slen} }}")
            while_parts.append(f"{inner_indent}variant {{ {_slen} - !{idx} }}")
        inv_subst = {target: idx} if is_range else None
        inv_refs = local_refs | {idx}
        self._in_spec = True
        # A LOOP invariant/variant is a spec context, but unlike a function pre/post the
        # BODY's local scope is live inside it: a seq-promoted LOCAL's shadow is in scope,
        # so `\length(<seq local>)` must be `Seq.length`, not `Array.length`. Without this
        # flag `_handle_arraylen_expr`'s `not self._in_spec` guard excludes loop clauses and
        # emits `Array.length` on a `seq` — a LOUD type error, never a silent wrong value,
        # which is why no currently-green file can depend on the old behaviour.
        self._in_loop_spec = True
        invariants_f = stmt.invariants
        n_inv_f = len(invariants_f)
        i_inv_f = 0
        #@ loop invariant 0 <= i_inv_f and i_inv_f <= n_inv_f
        #@ loop invariant self._havoc_counter >= \old(self._havoc_counter)
        #@ loop variant n_inv_f - i_inv_f
        while i_inv_f < n_inv_f:
            inv = invariants_f[i_inv_f]
            inv_str = self._expr_to_whyml(inv, inv_refs, subst=inv_subst)
            while_parts.append(f"{inner_indent}invariant {{ {inv_str} }}")
            i_inv_f += 1
        variants_f = stmt.variants
        n_var_f = len(variants_f)
        i_var_f = 0
        #@ loop invariant 0 <= i_var_f and i_var_f <= n_var_f
        #@ loop invariant self._havoc_counter >= \old(self._havoc_counter)
        #@ loop variant n_var_f - i_var_f
        while i_var_f < n_var_f:
            var_ir = variants_f[i_var_f]
            var_str = self._expr_to_whyml(var_ir, inv_refs, subst=inv_subst)
            while_parts.append(f"{inner_indent}variant {{ {var_str} }}")
            i_var_f += 1
        self._in_spec = False
        self._in_loop_spec = False

        def _bind_lines(bind_indent: str) -> List[str]:
            # W2 tuple char-iteration binds BOTH the index (i := the counter) and
            # the 1-char string (ch := str_sub_op s !idx 1). Every other loop binds
            # the single `elem_expr` — byte-identical.
            if str_ci is not None and str_ci[3]:
                _op, _idx_name, _ch_name, _ = str_ci
                self._add_abstract_op(
                    "val str_sub_op (s: string) (lo len: int) : string\n"
                    "    ensures { result = (String.substring s lo len) }\n"
                    "    ensures { (0 <= lo /\\ 0 <= len /\\ lo + len <= String.length s)"
                    " -> String.length result = len }")
                lines: List[str] = []
                if _idx_name and _idx_name != "_":
                    lines.append(f"{bind_indent}let {whyml_ident(_idx_name)} = ref !{idx} in")
                if _ch_name and _ch_name != "_":
                    lines.append(f"{bind_indent}let {whyml_ident(_ch_name)} = "
                                 f"ref (str_sub_op {_op} !{idx} 1) in")
                return lines
            # self-tcb-reduction (union/match cluster): `for i, x in enumerate(<seq>)` binds
            # the index i = ref !idx (int) and the element x = ref (Seq.get !seq !idx) (the
            # seq's element type). Gated on `enum_seq` -> corpus/other-mirror inert.
            if enum_seq is not None:
                _enw = self._expr_to_whyml(enum_seq[0], body_local)
                _it, _et = tuple_targets[0], tuple_targets[1]
                _elines: List[str] = []
                if _it and _it != "_":
                    _elines.append(f"{bind_indent}let {whyml_ident(_it)} = ref !{idx} in")
                if _et and _et != "_":
                    _elines.append(f"{bind_indent}let {whyml_ident(_et)} = "
                                   f"ref (Seq.get {_enw} !{idx}) in")
                return _elines
            # self-tcb-reduction _namedtuple_positional_access: an hval `.items()` loop
            # binds BOTH tuple components — the KEY (an arbitrary `string`, `hval_keys_get`,
            # IMMUTABLE) and the VALUE (a real `hval`, `elem_expr` = `hval_values_get`,
            # IMMUTABLE so the body's `match v with HMap ...` matches an `hval`). Gated on
            # `_is_pyval_items` -> corpus/other-mirror inert.
            if _is_pyval_items:
                _mapw = getattr(self, "_for_items_hval_map", None)
                _kt, _vt = tuple_targets[0], tuple_targets[1]
                _lines: List[str] = []
                if _kt and _kt != "_" and _mapw is not None:
                    # the KEY is a mutable `ref string` (in `body_declared`, so its reads
                    # deref `!k`) — the VALUE is an immutable pyval `hval` (read bare).
                    _lines.append(f"{bind_indent}let {whyml_ident(_kt)} = "
                                  f"ref (hval_keys_get {_mapw} !{idx}) in")
                if _vt and _vt != "_":
                    # cap1 value-string variant: bind the VALUE `_ty` to a real `string`
                    # (`hstr_of (hval_values_get ...)`) — a mutable `ref string` (in
                    # `body_declared`, so body reads deref `!_ty`), NOT an immutable `hval`.
                    _vexpr = (f"ref (hstr_of {elem_expr})" if _items_val_str
                              else f"({elem_expr})")
                    _lines.append(f"{bind_indent}let {whyml_ident(_vt)} = {_vexpr} in")
                return _lines
            # cap-3: `for k, v in zip(keys, values)` binds BOTH tuple components to the
            # idx-th element of each irlist (`irnth !idx keys` / `irnth !idx values`, both
            # IMMUTABLE emit_ir so the body's `match k with ...`/kind_of projections match
            # an `emit_ir`, not a `ref`). Gated on `_is_zip_irlists` -> corpus inert.
            if _is_zip_irlists:
                _zr = self._zip_irlist_recv(iter_ir)
                _kw = self._expr_to_whyml(_zr[0], body_local)
                _vw = self._expr_to_whyml(_zr[1], body_local)
                _kt, _vt = tuple_targets[0], tuple_targets[1]
                # both are mutable `ref emit_ir` (in `body_declared`, so body reads deref
                # `!k`/`!v`) — `irnth` returns a real emit_ir per iteration.
                _lines2: List[str] = []
                if _kt and _kt != "_":
                    _lines2.append(f"{bind_indent}let {whyml_ident(_kt)} = "
                                   f"ref (irnth !{idx} {_kw}) in")
                if _vt and _vt != "_":
                    _lines2.append(f"{bind_indent}let {whyml_ident(_vt)} = "
                                   f"ref (irnth !{idx} {_vw}) in")
                return _lines2
            # hval-retype (self-tcb-reduction Tier-5): a pyval `.values()` loop var
            # binds an IMMUTABLE `hval` (`let info = <elem>`, no `ref`) so the body's
            # K7 `match info with HMap ...` projection matches an `hval` (not a `ref hval`).
            # Gated on `_for_target_is_pyval` (set by `_classify_iterable`) -> inert.
            if getattr(self, "_for_target_is_pyval", False):
                return [f"{bind_indent}let {safe_target} = ({elem_expr}) in"]
            return [f"{bind_indent}let {safe_target} = ref ({elem_expr}) in"]

        if has_cont:
            while_parts.append(f"{inner_indent}try")
            while_parts.extend(_bind_lines(inner_indent + "  "))
            while_parts.append(inner_body)
            while_parts.append(f"{inner_indent}with PyCSL_Continue -> () end;")
        else:
            while_parts.extend(_bind_lines(inner_indent))
            while_parts.append(inner_body + ";")

        while_parts.append(f"{inner_indent}{idx} := !{idx} + 1")
        while_parts.append(f"{loop_indent}done")
        has_break = IRScanner.uses_break(_body_d)
        while_code = "\n".join(while_parts)

        if has_break:
            while_code = (f"{loop_indent}try\n{while_code}\n"
                          f"{loop_indent}with PyCSL_Break -> () end")

        idx_init = self._for_idx_init
        if self._bounded_int:
            idx_decl = f"{loop_indent}let {idx} = ref ({idx_init} : int{self._bounded_int}) in\n{while_code}"
        else:
            idx_decl = f"{loop_indent}let {idx} = ref {idx_init} in\n{while_code}"
        # L18 S1: materialise the split iterable ONCE as a `let` wrapping the loop, so the
        # loop bound `Array.length arr` and the element `arr[!idx]` reference the SAME array.
        _mat = getattr(self, "_for_iter_materialize", None)
        if _mat is not None:
            _mv, _mexpr = _mat
            idx_decl = f"{loop_indent}let {_mv} = {_mexpr} in\n{idx_decl}"

        if has_direct_ret and not self._has_early_ret and not in_loop:
            rest_code = self._stmts_to_whyml(
                rest, local_refs, declared_refs, indent + "  ", in_loop)
            inner = idx_decl
            if rest_code:
                inner += ";\n" + rest_code
            func_ret = self._func_return_type
            if func_ret == "unit":
                return (f"{indent}try\n{inner}\n"
                        f"{indent}with Return_void -> () end")
            return (f"{indent}try\n{inner}\n"
                    f"{indent}with Return r -> r end")
        else:
            full_code = idx_decl
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if rest_code:
                return full_code + ";\n" + rest_code
            return full_code

    def _first_assign_value_ir(self, var: str,
                                stmts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """First `Assign` RHS IR for `var` anywhere in `stmts` (recursing into
        nested blocks/handlers), or `{}` if none. Used to type the pre-declared
        ref of a try-body local."""
        for stmt in stmts:
            if stmt.get("stmt") == "Assign" and stmt.get("target") == var:
                return stmt.get("value", {}) or {}
            for key in ("body", "orelse", "finalbody"):
                if isinstance(stmt.get(key), list):
                    r = self._first_assign_value_ir(var, stmt[key])
                    if r:
                        return r
            for h in stmt.get("handlers", []):
                r = self._first_assign_value_ir(var, h.get("body", []))
                if r:
                    return r
        return {}

    def _try_local_decl_kind(self, val_ir: Dict[str, Any]) -> str:
        """Reduced `_first_assign_kind` (IR-only, no val-string side effects)
        for a try-body local's pre-declaration: `record` | `dict` | `array_string`
        | `default`."""
        vt = val_ir.get("type", "")
        # cap4/5 (self-tcb-reduction `_refine_tuple_return_type`): a try-body local
        # first-assigned a list COMPREHENSION (`slots = [_infer_tuple_slot_type(…) for e
        # in elts]`) is a `seq string` — pre-declare `ref (Seq.empty : seq string)`, not the
        # integer `ref 0` (which int-clashes the `:=`). An immutable `seq` (not a mutable
        # `array`) so the ref is freely reassignable (no Why3 region alias). Method-gated.
        if vt == "ListComp" and self._emitting_refine_tuple_return_type():
            return "seq_string"
        if vt == "Call" and val_ir.get("func", "") in self._record_types:
            return "record"
        if (vt in ("DictLit", "SetLit")
                or (vt == "Call" and val_ir.get("func") in ("dict", "set", "frozenset"))
                or self._rhs_yields_map(val_ir)):
            return "dict"
        return "default"

    def _callee_raised_direct(self, node: Any) -> Set[str]:
        """Exceptions that calls anywhere within `node` may raise via the
        callee's declared `#@ raises` contracts, WITHOUT regard to any
        enclosing try/except in `node`. Walks every `Call`, looks the
        function up in the module raises registry, unions declared names."""
        registry = getattr(self, "_module_func_raises", {}) or {}
        out: Set[str] = set()

        def walk(n: Any) -> None:
            if isinstance(n, dict):
                if n.get("type") == "Call":
                    fn = n.get("func", "")
                    for rc in registry.get(fn, []):
                        exc = rc.get("exc_type")
                        if exc:
                            out.add(exc)
                for v in n.values():
                    walk(v)
            elif isinstance(n, (list, tuple)):
                for v in n:
                    walk(v)

        walk(node)
        return out

    def _callee_raised_in(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Callee-declared exceptions (via `#@ raises`) that ESCAPE the
        given statement list — i.e. raised by some call but not caught by
        an enclosing `try/except` in the same list. Mirrors
        `IRScanner.collect_escaping_exceptions` but for callee raises, so a
        function's emitted `raises {}` summary excludes what its own
        handlers catch. Hierarchy-aware: `except OSError` removes a
        callee's FileNotFoundError from the escaping set."""
        from exception_model import handler_catches
        registry = getattr(self, "_module_func_raises", {}) or {}
        escaping: Set[str] = set()
        for stmt in stmts:
            if not isinstance(stmt, dict):
                continue
            if stmt.get("stmt") == "Try":
                inner = self._callee_raised_in(stmt.get("body", []))
                handler_bases: Set[str] = set()
                for h in stmt.get("handlers", []):
                    exc = h.get("exc_type")
                    if exc:
                        for ep in exc.split("|"):
                            ep = ep.strip()
                            if ep:
                                handler_bases.add(ep)
                    escaping |= self._callee_raised_in(h.get("body", []))
                escaping |= {
                    e for e in inner
                    if not any(handler_catches(b, e) for b in handler_bases)
                }
                continue
            # Non-Try statement: any call here (in its test/value/etc.)
            # escapes unconditionally; recurse structurally for nested
            # blocks (if/while/for bodies) which carry their own scoping.
            for key, val in stmt.items():
                if key in ("body", "orelse", "handlers"):
                    if isinstance(val, list):
                        escaping |= self._callee_raised_in(val)
                else:
                    escaping |= self._callee_raised_direct(val)
        return escaping

    def _handle_try_stmt(self, stmt: TryStmt, rest: List[Dict[str, Any]],
                          local_refs: Set[str], declared_refs: Set[str],
                          indent: str, in_loop: bool) -> str:
        body_stmts = [s.to_dict() for s in stmt.body]
        handlers = stmt.handlers
        try_assigned = IRScanner.find_assigned_vars(body_stmts)
        n_ha = len(handlers)
        i_ha = 0
        while i_ha < n_ha:
            h = handlers[i_ha]
            try_assigned |= IRScanner.find_assigned_vars(h.get("body", []))
            i_ha += 1
        pre_decls = ""
        sorted_assigned = sorted(try_assigned)
        n_sa = len(sorted_assigned)
        i_sa = 0
        # Pre-declare each try-body local as an outer ref so it stays in scope
        # across `try … with … end`. The ref's initial value must MATCH the
        # local's eventual type, else Why3 rejects the `:=`. A bare `ref 0`
        # (int) breaks a record/dict local constructed inside the `try`:
        #   - record / array locals are immutable `let X = {…}` bindings, not
        #     refs — skip the pre-decl and let the body bind them (works when
        #     the local is used within the try body, as the `check_code`
        #     analyzer is; a record local that escapes into a handler/after the
        #     try is unsupported — but that was already a type error).
        #   - dict locals are `map int (option int)` — pre-declare the empty map
        #     so `data = literal_eval(…)` / `d = {}` inside a try type-check.
        while i_sa < n_sa:
            var = sorted_assigned[i_sa]
            safe_var = whyml_ident(var)
            if safe_var not in declared_refs:
                kind = self._try_local_decl_kind(
                    self._first_assign_value_ir(var, body_stmts)
                    or self._first_assign_value_ir(
                        var, [s for h in handlers for s in h.get("body", [])]))
                if kind == "record":
                    pass  # let-bound inside the body; no outer ref
                elif kind == "seq_string":
                    # cap4/5 (self-tcb-reduction `_refine_tuple_return_type`): a `seq string`
                    # comprehension local pre-declares the empty string seq so its `:=` (from
                    # `list_comp_refine_string`) type-checks and stays reassignable.
                    pre_decls += (f"{indent}let {safe_var} = "
                                  f"ref (Seq.empty : seq string) in\n")
                    declared_refs.add(safe_var)
                elif kind == "dict":
                    pre_decls += (f"{indent}let {safe_var} = "
                                  f"ref (const (None: option int)) in\n")
                    declared_refs.add(safe_var)
                else:
                    pre_decls += f"{indent}let {safe_var} = ref 0 in\n"
                    declared_refs.add(safe_var)
            i_sa += 1
        body_str = self._stmts_to_whyml(body_stmts, local_refs, declared_refs.copy(), indent + "  ", in_loop)
        if not body_str:
            body_str = f"{indent}  ()"
        if handlers:
            from exception_model import handler_catches
            # Concrete exception tags that can actually escape the try body
            # (raises inside, minus what nested trys catch). A handler
            # `except OSError:` must produce a Why3 `with` arm for EACH such
            # tag it catches (OSError itself + every modelled subclass that
            # the body raises), because Why3 matches exception arms by exact
            # tag — there is no subtyping at the `with` level.
            body_raised = set(
                IRScanner.collect_escaping_exceptions(body_stmts))
            # A call inside the try body to a function that DECLARES
            # `raises { E -> ... }` can raise E, even though there is no
            # literal `raise E` statement here (the os wrappers: a wrapper's
            # try body calls `sys_open`, which raises FileNotFoundError via
            # its contract). Pull those callee-declared exceptions in so the
            # handler expansion covers them.
            body_raised |= self._callee_raised_in(body_stmts)
            body_raised = sorted(body_raised)

            code = f"{pre_decls}{indent}try\n{body_str}\n"
            n_h = len(handlers)
            i_h = 0
            first_handler = True
            already_matched: Set[str] = set()
            # Why3 requires `try BODY with Exc1 -> h1 | Exc2 -> h2 end` —
            # only the first arm uses `with`, subsequent arms use `|`.
            # Emitting separate `with` clauses produces a syntax error.
            while i_h < n_h:
                h = handlers[i_h]
                exc = h.get("exc_type") or "PyCSL_Exception"
                # A `|`-separated handler (`except (A, B):`) is the union of
                # its parts; each part is a base whose closure we expand.
                raw_parts = (exc.split("|") if "|" in exc else [exc])
                handler_body = self._stmts_to_whyml(
                    h.get("body", []), local_refs, declared_refs.copy(),
                    indent + "  ", in_loop)
                if not handler_body:
                    handler_body = f"{indent}  ()"
                # Build the concrete set of tags this handler matches:
                #   - each base part itself (so a literal `raise OSError`
                #     or a base never raised in the body still matches, and
                #     the arm is never empty -> no Why3 syntax error);
                #   - every body-raised tag that is a subclass of a part.
                arm_tags: List[str] = []
                seen_local: Set[str] = set()
                for part in raw_parts:
                    base = part.strip()
                    if not base:
                        continue
                    candidates = [base] + [
                        e for e in body_raised if handler_catches(base, e)]
                    for tag in candidates:
                        if tag in already_matched or tag in seen_local:
                            continue  # earlier arm already consumes this tag
                        seen_local.add(tag)
                        arm_tags.append(tag)
                # Sanitize for WhyML: leading-underscore aliases like
                # `_FooError` must match the sanitized preamble declaration.
                for tag in arm_tags:
                    ep = safe_exc_name(tag)
                    connector = "with" if first_handler else "|"
                    code += f"{indent}{connector} {ep} -> \n{handler_body}\n"
                    first_handler = False
                already_matched |= seen_local
                i_h += 1
            code += f"{indent}end"
        else:
            code = f"{pre_decls}{body_str}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _try_union_is_none_match(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                  local_refs: Set[str], declared_refs: Set[str],
                                  indent: str, in_loop: bool) -> Any:
        """typing-engagement ty1 C5 — detect `if x is None:` / `if x is not None:`
        where `x` is a Union-typed variable, and lower to a constructor-pattern
        `match` (Why3 forbids `=` on algebraic types in a program `if`). Returns
        the match code string, or None if the pattern does not apply (caller falls
        back to the normal `if` lowering)."""
        test = stmt.get("test", {})
        if not isinstance(test, dict) or test.get("type") != "BinOp":
            return None
        op = test.get("op")
        if op not in ("==", "!="):
            return None
        left, right = test.get("left", {}), test.get("right", {})
        var_node = None
        is_none = False
        if left.get("type") == "None" and right.get("type") == "Var":
            var_node = right
            is_none = True
        elif right.get("type") == "None" and left.get("type") == "Var":
            var_node = left
            is_none = True
        if not is_none or not var_node:
            return None
        var_name = var_node.get("name")
        symtype = getattr(self, "_current_symbol_table", {}).get(var_name)
        if not symtype or not isinstance(symtype, str) or not symtype.startswith("_union_"):
            return None
        # tool-feature-5: a MUTABLE Optional local (`x: Optional[τ] = None`) is a
        # `ref _union_*`. The value-narrowing match here (which SHADOWS `x` with the
        # projected carrier) is for immutable union PARAMS — it is both ill-typed
        # (`match x` vs the ref `match !x`) and unsound (narrowing a reassignable ref)
        # for a mutable local. Fall through to the ordinary `if` lowering, whose test
        # lowers to the match-boolean discriminant `(match !x with Arm_i_None -> true |
        # _ -> false)` (expressions.py) with `x` staying a ref in both branches.
        if var_name in getattr(self, "_optional_union_locals", set()):
            return None
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        none_ctor = None
        other_ctors = []
        for ctor_name, ctor in vinfo.get("constructors", {}).items():
            if ctor.get("arity") == 0 and "None" in ctor_name:
                none_ctor = ctor_name
            else:
                other_ctors.append(ctor_name)
        if none_ctor is None:
            return None
        body = stmt.get("body", []) or []
        orelse = stmt.get("orelse", []) or []
        body_str = self._stmts_to_whyml(body, local_refs, declared_refs.copy(),
                                        indent + "    ", in_loop)
        if not body_str.strip():
            body_str = f"{indent}    ()"
        orelse_str = self._stmts_to_whyml(orelse, local_refs, declared_refs.copy(),
                                          indent + "    ", in_loop) if orelse else ""
        if not orelse_str.strip():
            orelse_str = f"{indent}    ()"
        var_safe = whyml_ident(var_name)
        if op == "==":
            true_body, false_body = body_str, orelse_str
            true_is_none = True   # `if x is None:` — True branch is the None arm
        else:
            true_body, false_body = orelse_str, body_str
            true_is_none = False  # `if x is not None:` — True branch is non-None
        # C5 (GAP-001): on the False branch of `if x is None:` the variable
        # `x` narrows from `Union[A, None]` to the non-None arm's carrier type
        # `A`. Why3 has no path-condition narrowing, so we lower the False
        # branch as a constructor match that binds the carrier value and
        # SHADOWS `x` with it: `| Arm_0_0 v -> let x = v in <false_body> end`.
        # The match has exactly one arm per non-None constructor (no wildcard)
        # so Why3's exhaustiveness check confirms the narrowing is total.
        #
        # `rest` handling: when the True branch returns (so `rest` is
        # unreachable there), `rest` is inlined into the FALSE arm(s) so the
        # narrowed `x` is in scope. When the True branch does not return,
        # `rest` runs on both branches and is appended after the match.
        true_branch_stmts = body if true_is_none else orelse
        true_returns = bool(true_branch_stmts) and IRScanner.ends_with_return(
            true_branch_stmts)
        # Build the None arm.
        none_arm = f"{indent}  | {none_ctor} ->\n{true_body}"
        # Build the non-None arms (with carrier projection).
        non_none_arms: List[str] = []
        for i, ctor_name in enumerate(other_ctors):
            ctor_info = vinfo["constructors"][ctor_name]
            ctor_payload = ctor_info.get("payload", [])
            # The bound carrier variable. Reuse the original variable name
            # so a downstream `return x` resolves to the projected carrier.
            bind = var_safe if len(other_ctors) == 1 else f"{var_safe}_{i}"
            arm_pat = f"{ctor_name} {bind}" if ctor_payload else ctor_name
            # Project `x` to the carrier on EVERY non-None arm so `x` is
            # narrowed to `A` (C5). `let x = bind in <false_body>`.
            if ctor_payload:
                non_none_arms.append(
                    f"{indent}  | {arm_pat} ->\n"
                    f"{indent}    let {var_safe} = {bind} in\n"
                    f"{false_body}")
            else:
                non_none_arms.append(f"{indent}  | {arm_pat} ->\n{false_body}")
        # Decide where `rest` goes.
        if true_returns and rest:
            rest_str = self._stmts_to_whyml(
                rest, local_refs, declared_refs,
                indent + "    ", in_loop)
            if true_is_none:
                # `==`: True (None) returns → `rest` runs on the False
                # (non-None) branch. Inline `rest` into the LAST non-None
                # arm (after the projected body). Earlier non-None arms
                # must return independently or the match is non-exhaustive.
                if non_none_arms:
                    last = non_none_arms[-1]
                    non_none_arms[-1] = last + f";\n{rest_str}"
            else:
                # `!=`: True (non-None) returns → `rest` runs on the False
                # (None) branch. Inline `rest` into the None arm. `x` is the
                # variant on this arm (no projection — it IS None).
                none_arm = f"{indent}  | {none_ctor} ->\n{true_body};\n{rest_str}"
            arms = [none_arm] + non_none_arms
            code = (f"{indent}match {var_safe} with\n" + "\n".join(arms) +
                    f"\n{indent}  end")
            return code
        # True branch does not return (or no rest): `rest` runs on both
        # branches — append after the match. The non-None arms still project
        # `x` to the carrier for the False-branch body.
        arms = [none_arm] + non_none_arms
        code = (f"{indent}match {var_safe} with\n" + "\n".join(arms) +
                f"\n{indent}  end")
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs,
                                                indent, in_loop)
        return code

    def _handle_if_stmt(self, stmt: IfStmt, rest: List[Dict[str, Any]],
                        local_refs: Set[str], declared_refs: Set[str],
                        indent: str, in_loop: bool) -> str:
        # typing-engagement ty1 / 25-1700-typing-spec-1 §1.2 C5: `if x is None:`
        # on a Union-typed variable lowers to a constructor-pattern `match`
        # (Why3 does not allow `=` on algebraic types in a program `if`).
        # `_try_union_is_none_match` does deep dict inspection of the test
        # expression (BinOp/None/Var shape); pass the round-tripped dict so the
        # helper's dict-based inspection stays byte-identical (expressions.py
        # is Phase B+ scope — not yet on typed ExprIR).
        union_match = self._try_union_is_none_match(stmt.to_dict(), rest, local_refs,
                                                    declared_refs, indent, in_loop)
        if union_match is not None:
            return union_match
        _test_d = stmt.test.to_dict()
        test = self._expr_to_whyml(_test_d, local_refs)
        test = self._to_bool(test, _test_d)
        body = [s.to_dict() for s in stmt.body]
        orelse = [s.to_dict() for s in stmt.orelse]
        body_str = self._stmts_to_whyml(body, local_refs, declared_refs.copy(), indent + "  ", in_loop)
        if not body_str:
            body_str = f"{indent}  ()"
        body_returns = IRScanner.ends_with_return(body)
        if orelse:
            orelse_str = self._stmts_to_whyml(orelse, local_refs, declared_refs.copy(), indent + "  ", in_loop)
            if not orelse_str:
                orelse_str = f"{indent}  ()"
            code = (f"{indent}if {test} then begin\n{body_str}\n"
                    f"{indent}end else begin\n{orelse_str}\n{indent}end")
            if body_returns and IRScanner.ends_with_return(orelse):
                return code
        elif body_returns and rest:
            rest_str = self._stmts_to_whyml(rest, local_refs, declared_refs, indent + "  ", in_loop)
            if not rest_str:
                rest_str = f"{indent}  ()"
            return (f"{indent}if {test} then begin\n{body_str}\n"
                    f"{indent}end else begin\n{rest_str}\n{indent}end")
        else:
            stripped = body_str.rstrip()
            last_line = stripped.split('\n')[-1].strip() if stripped else ""
            body_returns_value = (last_line.startswith("(") and
                                  not last_line.startswith("()") and
                                  "raise " not in last_line and
                                  # self-tcb-reduction (_err-divergence): a body ending in
                                  # `absurd` (a `-> NoReturn` `self._err(...)` call, lowered
                                  # to `(let _ = <call> in absurd)`) DIVERGES — like a
                                  # `raise` it is not a value-returning arm. Route it to the
                                  # no-else `if test then begin <body> end` form (the `'a`
                                  # of `absurd` unifies with the implicit `()`), NOT the
                                  # value-if whose `else 0` would force an `int` type.
                                  not last_line.endswith("absurd)") and
                                  "<-" not in last_line and
                                  ":=" not in last_line and
                                  "subscript_set" not in last_line)
            if body_returns_value:
                code = (f"{indent}if {test} then begin\n{body_str}\n"
                        f"{indent}end else begin\n{indent}  0\n{indent}end")
            else:
                code = f"{indent}if {test} then begin\n{body_str}\n{indent}end"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _pattern_has_constructor(self, pat: Dict[str, Any]) -> bool:
        """True if `pat` is a constructor pattern, or an `Or` whose alternatives
        include one — the signal to use Why3's native `match` (A5c)."""
        p = pat.get("pattern")
        if p == "Constructor":
            return True
        if p == "Or":
            return any(self._pattern_has_constructor(a)
                       for a in pat.get("alternatives", []))
        return False

    def _render_match_pattern(self, pat: Dict[str, Any], top: bool = False) -> str:
        """Render a match pattern as a Why3 match-arm pattern, recursively (A5c).
        Nested constructors parenthesize (`Wrap (A n)`); or-patterns join with `|`
        (`Red | Green`); captures bind their name, wildcards/`_` stay `_`. `top`
        suppresses the outer parens on a constructor (an arm head is `Ctor a b`,
        a nested sub-pattern is `(Ctor a b)`)."""
        p = pat.get("pattern")
        if p == "Wildcard":
            return "_"
        if p == "Capture":
            nm = pat.get("name", "_")
            return "_" if nm == "_" else whyml_ident(nm)
        if p == "Value":
            return self._expr_to_whyml(pat["value"], set())
        if p == "Or":
            return " | ".join(self._render_match_pattern(a, top)
                              for a in pat.get("alternatives", []))
        if p == "Constructor":
            sub = [self._render_match_pattern(cp) for cp in pat.get("captures", [])]
            body = pat["ctor"] + ("".join(" " + s for s in sub) if sub else "")
            if top or not sub:
                return body
            return f"({body})"
        return "_"

    def _match_subject_union_info(self, stmt: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any]]]:
        """typing-engagement ty1 C9 — if the match subject is a `Var` whose
        symbol-table entry is a synthesized `_union_*` variant, return
        (subject_var_name, variant_info) so a `case int():` / `case str():`
        pattern can be lowered to the variant's constructor (`Arm_0_0 v`).
        Returns None for non-Union subjects (byte-identical fallback)."""
        subj = stmt.get("subject", {})
        if not isinstance(subj, dict) or subj.get("type") != "Var":
            return None
        var_name = subj.get("name")
        symtype = getattr(self, "_current_symbol_table", {}).get(var_name)
        if not symtype or not isinstance(symtype, str) or not symtype.startswith("_union_"):
            return None
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        return var_name, vinfo

    def _union_ctor_for_arm_tag(self, vinfo: Dict[str, Any], arm_tag: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Find the (ctor_name, ctor_info) of the variant constructor whose
        payload tag matches `arm_tag` (e.g. `int` → `Arm_0_0`). Returns None
        if no constructor carries that arm type."""
        for ctor_name, ctor in vinfo.get("constructors", {}).items():
            payload = ctor.get("payload", [])
            if payload and payload[0] == arm_tag:
                return ctor_name, ctor
        return None

    def _handle_match_stmt(self, stmt: MatchStmt, rest: List[Dict[str, Any]],
                           local_refs: Set[str], declared_refs: Set[str],
                           indent: str, in_loop: bool) -> str:
        subject = self._expr_to_whyml(stmt.subject, local_refs)
        cases = stmt.cases
        # typing-engagement ty1 / 25-1700-typing-spec-1 §1.3 C9: a `match` on a
        # Union-typed value must lower to a constructor-pattern match over the
        # synthesized variant's constructors (`Arm_0_0 v -> ...`), NOT against
        # the bare type name (`int -> ...`). A `case int():` pattern on a
        # `Union[int, str]` subject is rewritten to the variant's `int`-armed
        # constructor with a bound carrier, so Why3's native exhaustiveness
        # check fires on a missing arm. (GAP-002.)
        # `_match_subject_union_info` does deep dict inspection of the subject;
        # pass the round-tripped dict (expressions.py is Phase B+ scope).
        union_info = self._match_subject_union_info(stmt.to_dict())
        if union_info is not None:
            _uvar, uinfo = union_info
            for c in cases:
                pat = c["pattern"]
                if pat.get("pattern") != "Constructor":
                    continue
                ctor_name = pat.get("ctor", "")
                # `case int():` / `case str():` — map the type name to the
                # variant's constructor for that arm.
                match = self._union_ctor_for_arm_tag(uinfo, ctor_name)
                if match is not None:
                    arm_ctor, arm_ctor_info = match
                    # Bind the carrier to a fresh local so the arm body can
                    # use it; if the case captured a name, reuse it.
                    existing_caps = pat.get("captures", []) or []
                    if existing_caps:
                        bind_name = self._render_match_pattern(existing_caps[0])
                    else:
                        bind_name = f"_u_{arm_ctor}"
                    # Rewrite the pattern to the variant constructor with the
                    # bound carrier. The carrier is positional.
                    new_pat = {"pattern": "Constructor", "ctor": arm_ctor,
                               "captures": [{"pattern": "Capture",
                                             "name": bind_name}]}
                    c["pattern"] = new_pat
        # sum-types: a constructor-pattern match over a `#@ datatype` lowers to a real Why3
        # `match … with` (so Why3 checks exhaustiveness), not the value-pattern if-chain.
        # A5c: route to the native match if ANY arm involves a constructor — directly
        # or inside an `Or` pattern (`case Red() | Green():`).
        if any(self._pattern_has_constructor(c["pattern"]) for c in cases):
            # A5c: a Why3 `match` arm cannot carry a boolean guard, so a guarded
            # arm (`case Ctor(x) if g`) becomes `<pat> -> if g then <body> else
            # <fall-through>`, where the fall-through is the catch-all (wildcard)
            # body — the case a guard failure falls through to. The wildcard
            # body is computed once. (Guarded arms without a wildcard catch-all
            # fall through to `()` — documented boundary; Python guarded matches
            # need a catch-all to be exhaustive anyway.)
            wildcard_body = None
            for c in cases:
                if c["pattern"].get("pattern") == "Wildcard":
                    wb = self._stmts_to_whyml(c.get("body", []), local_refs,
                                              declared_refs.copy(), indent + "    ", in_loop)
                    wildcard_body = wb if wb.strip() else f"{indent}    ()"
                    break
            arms: List[str] = []
            for c in cases:
                pat = c["pattern"]
                body_str = self._stmts_to_whyml(c.get("body", []), local_refs,
                                                declared_refs.copy(), indent + "    ", in_loop)
                if not body_str.strip():
                    body_str = f"{indent}    ()"
                # A5c: render the pattern recursively — nested constructors
                # (`Wrap (A n)`) and or-patterns (`Red | Green`) included.
                arm = self._render_match_pattern(pat, top=True)
                guard = c.get("guard")
                if guard:
                    guard_str = self._to_bool(
                        self._expr_to_whyml(guard, local_refs), guard)
                    fb = wildcard_body if wildcard_body is not None else f"{indent}    ()"
                    body_str = (f"{indent}    if {guard_str} then begin\n{body_str}\n"
                                f"{indent}    end else begin\n{fb}\n{indent}    end")
                arms.append(f"{indent}  | {arm} ->\n{body_str}")
            code = f"{indent}match {subject} with\n" + "\n".join(arms) + f"\n{indent}  end"
            if rest:
                code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            return code
        lines = []
        n_cases = len(cases)
        i_case = 0
        while i_case < n_cases:
            c = cases[i_case]
            pat = c["pattern"]
            guard = c.get("guard")
            body_stmts = c.get("body", [])
            body_str = self._stmts_to_whyml(body_stmts, local_refs, declared_refs.copy(),
                                             indent + "  ", in_loop)
            if not body_str:
                body_str = f"{indent}  ()"
            cond = self._match_pattern_cond(pat, subject, local_refs)
            if guard:
                guard_str = self._expr_to_whyml(guard, local_refs)
                guard_str = self._to_bool(guard_str, guard)
                cond = f"({cond} && {guard_str})" if cond != "true" else guard_str
            if i_case == 0:
                lines.append(f"{indent}if {cond} then begin")
            elif cond == "true":
                lines.append(f"{indent}end else begin")
            else:
                lines.append(f"{indent}end else if {cond} then begin")
            lines.append(body_str)
            i_case += 1
        lines.append(f"{indent}end")
        code = "\n".join(lines)
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _thread_optional_return(self, val_ir: Any,
                                local_refs: Set[str]) -> Optional[str]:
        """LEVER F2: thread an `option string` return VALUE — a 1-arg `.get` on a
        `map _ (option string)`, a bare `None`, or an `IfExpr` built from those — into
        the function's Optional[str] `_union_*` return: `Some v` → the string Some-arm
        `(Arm_N_0 v)`, `None` → the nullary `_None` arm. This replaces the scalar
        `None -> 0` unwrap the plain `.get` lowering picks (an int default that clashes
        with the string Some-branch at the union return slot). Returns the union-typed
        WhyML term, or None (fail-closed) when the return type is not a single-string-arm
        Optional union, or the value is not one of the threadable shapes."""
        if not isinstance(val_ir, dict):
            return None
        func_ret = getattr(self, "_func_return_type", "")
        if not (isinstance(func_ret, str) and func_ret.startswith("_union_")):
            return None
        none_ctor, some_ctors = self._union_ctors(func_ret)
        if none_ctor is None or len(some_ctors) != 1:
            return None
        some_ctor = some_ctors[0]
        vinfo = getattr(self, "_variant_types", {}).get(func_ret) or {}
        payload = vinfo.get("constructors", {}).get(some_ctor, {}).get("payload", [])
        if not payload or self._union_arm_whyml_type(payload[0]) != "string":
            return None
        return self._thread_optional_return_rec(
            val_ir, local_refs, none_ctor, some_ctor)

    def _thread_optional_return_rec(self, val_ir: Any, local_refs: Set[str],
                                    none_ctor: str, some_ctor: str) -> Optional[str]:
        """Recursive core of `_thread_optional_return`: `None`, a 1-arg `.get` (raw
        `option string`), and an `IfExpr` over those. Any other shape → None (fail-closed)."""
        if not isinstance(val_ir, dict):
            return None
        t = val_ir.get("type")
        if t == "None":
            return none_ctor
        # lever #1 sub-inc A cap (c): a bare `return <local>` where the local is an
        # `option string`-returning-call result (`_rec = self._record_valued_expr_whyml_type
        # (...)`, tracked in `_option_str_return_vars`) threads the raw `option string` into
        # the Optional[str] union arms — `Some v` -> the string Some-arm `(Arm_N_0 v)`, `None`
        # -> the nullary `_None` arm. Preserves None-propagation instead of the scalar default.
        if (t == "Var"
                and val_ir.get("name") in getattr(self, "_option_str_return_vars", set())):
            _ov = f"!{whyml_ident(val_ir['name'])}"
            return (f"(match {_ov} with | Some v_ -> {some_ctor} v_ "
                    f"| None -> {none_ctor} end)")
        if t == "IfExpr":
            _then = self._thread_optional_return_rec(
                val_ir.get("body"), local_refs, none_ctor, some_ctor)
            _else = self._thread_optional_return_rec(
                val_ir.get("orelse"), local_refs, none_ctor, some_ctor)
            if _then is None or _else is None:
                return None
            _test_ir = val_ir.get("test", {})
            _test = self._to_bool(
                self._expr_to_whyml(_test_ir, local_refs), _test_ir)
            return f"(if {_test} then {_then} else {_else})"
        # hval-retype (self-tcb-reduction Tier-5): the doubled hval read
        # `info.get("field_types", {}).get(field)` returned as `Optional[str]` — the outer
        # `.get(field)` has func bare "get" with a pyval `.get` RECEIVER. `_get_return_raw_option`
        # makes `_lower_dict_get_call` hand back the raw `option string` (a real nested
        # `pairs_get` + `HStr` projection over `info`); wrap it into the union arms.
        _chained_pyval = (t == "Call" and val_ir.get("func") == "get"
                          and isinstance(val_ir.get("receiver"), dict)
                          and self._expr_is_pyval(val_ir.get("receiver"))
                          and len(val_ir.get("args") or []) == 1)
        if ((t == "Call" and isinstance(val_ir.get("func"), str)
                and val_ir["func"].endswith(".get")
                and len(val_ir.get("args") or []) == 1) or _chained_pyval):
            _prev = getattr(self, "_get_return_raw_option", False)
            self._get_return_raw_option = True
            try:
                raw = self._expr_to_whyml(val_ir, local_refs)
            finally:
                self._get_return_raw_option = _prev
            # The flag fires only on a resolvable dict `.get`; if the receiver was not
            # a tracked map the lowering falls back to its scalar form (no `Map.get`
            # prefix) — reject then (fail-closed) rather than mis-wrap a scalar. The
            # chained hval read hands back a `(match <hval> ... -> Some s | ... None)`
            # raw `option string` (starts with "(match ") — accept that too.
            if raw.startswith("(Map.get ") or (_chained_pyval and raw.startswith("(match ")):
                return (f"(match {raw} with | Some v_ -> {some_ctor} v_ "
                        f"| None -> {none_ctor} end)")
            return None
        return None

    def _maybe_inject_union_return(self, val: str, val_ir: Any) -> str:
        """typing-engagement ty1 §0/§2.2 C2 — if the function's return type is a
        synthesized `_union_*` variant, auto-inject the return value into the
        first arm whose payload type matches the value's type. If the value is
        already a constructor application (starts with `Arm_`), leave it. If no
        arm matches, leave the value (Why3 will flag the type error)."""
        func_ret = getattr(self, "_func_return_type", "")
        if not func_ret or not func_ret.startswith("_union_"):
            return val
        vinfo = getattr(self, "_variant_types", {}).get(func_ret)
        if not vinfo:
            return val
        constructors = vinfo.get("constructors", {})
        if not constructors:
            return val
        # If the value is already a constructor application, don't re-wrap.
        for ctor_name in constructors:
            if val.startswith(ctor_name):
                return val
        # GAP-004 (O3): `return None` from a function whose declared return type
        # is a synthesized `_union_*` variant (= `Optional[X]` = `Union[X, None]`)
        # must inject into the variant's nullary `Arm_*_None` constructor. None is
        # always assignable to Optional[X] (spec clause O3, optional-twoplane-spec
        # §1.1); without this arm the bare `0` (the Python-None singleton model)
        # type-clashes against the variant. Symmetric to the int-arm injection
        # below; fires BEFORE the type-based arm search so a None-typed return
        # never falls through to the lossy `int` fallback.
        if isinstance(val_ir, dict) and val_ir.get("type") == "None":
            for ctor_name, ctor in constructors.items():
                if ctor.get("arity") == 0 and "None" in ctor_name:
                    return ctor_name
        # Determine the value's WhyML type and find a matching arm.
        val_type = self._infer_return_value_type(val_ir)
        if val_type is None:
            return val
        for ctor_name, ctor in constructors.items():
            if ctor.get("arity") == 0:
                continue
            payload = ctor.get("payload", [])
            if not payload:
                continue
            arm_type = self._union_arm_whyml_type(payload[0])
            if arm_type == val_type:
                return f"({ctor_name} {val})"
        return val

    def _infer_return_value_type(self, val_ir: Any) -> Optional[str]:
        """Infer the WhyML type of a return value IR node for Union injection."""
        if not isinstance(val_ir, dict):
            return None
        # W8 capability (v): a RECORD-VALUED return (`return self.toks[idx]` /
        # `return self.advance()` / a record-typed local) resolves to the record's
        # Why3 type, so it is injected into the Optional variant's RECORD arm.
        # Gated on the `List[<record>]`-field machinery -> None (byte-inert)
        # everywhere else, so it may run first without perturbing any other shape.
        _rec = self._record_valued_expr_whyml_type(val_ir)
        if _rec is not None:
            return _rec
        t = val_ir.get("type")
        if t in ("Number", "BinOp") or t == "UnaryOp":
            # self-tcb-reduction _typeddict_record_literal (cap-6/7 completion): a string
            # `+` concatenation return (`return "{ " + "; ".join(parts) + " }"`) is a
            # STRING value — it must wrap into the Optional variant's string arm
            # (`Arm_N_0 <concat>`), not fall through as int (no int arm exists -> the bare
            # string type-clashes the `_union_*`). Mirrors the FString/`_is_string_expr`
            # path; only BinOp is re-checked (Number/UnaryOp are always int). Byte-inert:
            # a corpus union function with an unwrapped string-BinOp return would already
            # fail L3-tc, so none exists (the wrap fires for no corpus program).
            if t == "BinOp" and self._is_string_expr(val_ir):
                return "string"
            return "int"
        if t == "String":
            return "string"
        if t == "Bool":
            return "int"
        if t == "Var":
            name = val_ir.get("name", "")
            symtab = getattr(self, "_current_symbol_table", {})
            symtype = symtab.get(name)
            if symtype:
                return self._union_arm_whyml_type(symtype) \
                    if not symtype.startswith("_union_") else symtype
            return "int"
        if t == "Call":
            func = val_ir.get("func", "")
            if isinstance(func, str):
                if func in ("len", "int", "abs", "ord"):
                    return "int"
                if func in ("str",):
                    return "string"
                # value-model campaign incr5 (Optional-return-of-CALL wrapping): a string-
                # returning METHOD call (`self._m5_get_type_name_legacy(...)`) resolves to
                # "string" via the callee's declared signature, so `return self._m(...)` from
                # an Optional[str] function wraps into the variant's string-arm ctor (`Arm_N_0
                # <call>`), like a string LITERAL — previously it fell through to None
                # (unwrapped) and Why3 rejected the bare string against the `_union_*` variant.
                # Only the string case is added; int/other calls are unperturbed.
                if self._resolve_dotted_signature(func)[0] == "string":
                    return "string"
        # value-model campaign incr7 (primitive #1 — generalized string-return wrapping): ANY
        # string-typed return VALUE (a `name_of` attribute read `return elt.id`, a string
        # ternary `return "a" if c else elt.id`, an f-string / string concat) wraps into the
        # Optional-variant string-arm (`Arm_N_0 <val>`), mirroring the literal/String case and
        # the incr5 string-CALL case. Reuses `_is_string_expr` (the emitter's string-typedness
        # oracle). Reached ONLY for a union-returning function (via `_maybe_inject_union_return`)
        # and only wraps when a matching string arm exists, so non-union / non-string returns
        # (and every corpus function) are unperturbed. Placed last so the explicit int/Var/Call
        # cases above still win (e.g. a `+` string-concat is FString/handled there, not here).
        if self._is_string_expr(val_ir):
            return "string"
        return None

    def _union_arm_whyml_type(self, tag: str) -> str:
        """Map a Union arm IR type tag to its WhyML type string."""
        m = {"int": "int", "bool": "int", "str": "string", "float": "real",
             "list": "array int", "bytes": "array int", "bytearray": "array int",
             # set/frozenset: faithful StrSet `map string bool` (see the twin in
             # functions.py / preamble._VPAY) — was the int-keyed map that
             # int-hashed a string membership key. `dict` stays on the int model.
             "dict": "map int (option int)", "set": "map string bool",
             "frozenset": "map string bool", "tuple": "array int",
             # self-tcb-reduction giants: an `Optional[ast.expr]` local's Some-arm
             # carries the already-lowered emit_ir sub-node.
             "emit_ir": "emit_ir"}
        if tag in m:
            return m[tag]
        # W8 capability (v): a RECORD-class arm tag (`Optional[_Tok]` -> the arm
        # tag `_Tok`) resolves to that record's Why3 type, so the return-value
        # injection below can match a record-valued `return` against the arm.
        _rt = getattr(self, "_record_types", {}).get(tag)
        if _rt and _rt.get("whyml_name"):
            return _rt["whyml_name"]
        return "int"

    def _record_valued_expr_whyml_type(self, val_ir: Any) -> Optional[str]:
        """W8 capability (v): the Why3 record type of a RECORD-VALUED expression,
        for the three shapes the token cursor returns from an `Optional[<record>]`
        method; None for everything else.

        * `self.<field>[i]`  — an element of an `array <record>` self-field
          (`return self.toks[idx]`, proof2why3 `peek`);
        * `self.<m>(...)`    — a same-class sibling call DECLARED `-> <RecordClass>`
          (`return self.advance()`, `accept_op`/`accept_kw`);
        * `t`                — a local bound to either of the above.

        All three are gated on `_record_array_fields` / `_record_field_elem_locals`
        / a record-valued entry in `_module_method_return_types`, which are
        populated only inside a class carrying a `List[<record>]` field — so this
        is None (hence byte-inert) everywhere else.
        """
        if not isinstance(val_ir, dict):
            return None
        _recs = getattr(self, "_record_types", {}) or {}
        _wns = {v.get("whyml_name") for v in _recs.values() if isinstance(v, dict)}
        t = val_ir.get("type")
        if t == "Subscript":
            _b = val_ir.get("value")
            if isinstance(_b, dict) and _b.get("type") in ("FieldGet", "Attribute"):
                _o = _b.get("object") or _b.get("value")
                if isinstance(_o, dict):
                    _o = _o.get("name")
                if _o == "self":
                    _ecls = (getattr(self, "_record_array_fields", None) or {}).get(
                        _b.get("field") or _b.get("attr"))
                    if _ecls and _ecls in _recs:
                        return _recs[_ecls]["whyml_name"]
            return None
        if t == "Var":
            _ecls = (getattr(self, "_record_field_elem_locals", None) or {}).get(
                val_ir.get("name", ""))
            if _ecls and _ecls in _recs:
                return _recs[_ecls]["whyml_name"]
            return None
        if t == "Call":
            _f = val_ir.get("func", "")
            if isinstance(_f, str) and _f.startswith("self."):
                _cls = getattr(self, "_current_self_type", None)
                _key = f"{_cls}__{_f[len('self.'):]}" if _cls else _f[len("self."):]
                _rt = getattr(self, "_module_method_return_types", {}).get(_key)
                if _rt in _wns:
                    return _rt
            return None
        return None

    def _handle_return_stmt(
        self,
        stmt: ReturnStmt,
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        """Reads self._has_early_ret, self._func_return_type, self._array_locals (no writes)."""
        val_ir = stmt.value.to_dict() if stmt.value is not None else None
        use_raise = in_loop or self._has_early_ret
        func_ret_peek = self._func_return_type
        if val_ir is None:
            val = "()"
        elif (val_ir.get("type") == "Var"
              and val_ir.get("name") in getattr(self, "_pyval_seq_locals", set())):
            # K4 (local/return-position seq-pyval, self-tcb-reduction Tier-5): the
            # function's declared return is `seq hval`, so a `return fields` where
            # `fields` is the `seq hval` local returns the seq DIRECTLY (`!fields`) —
            # NOT the `materialize` (seq int -> array int) bridge, which drops the pyval
            # carrier. Gated on `_pyval_seq_locals` -> byte-inert.
            val = f"!{whyml_ident(val_ir['name'])}"
        elif (val_ir.get("type") == "Var"
              and val_ir.get("name") in getattr(self, "_seq_locals", set())):
            # 07-1705-rev4 P4: returning a seq-modelled (growable) list local where the
            # function's declared return is `array int` (a `list`) crosses the seq→array
            # boundary — materialise to a FRESH array (legal: bound at the return slot,
            # never rebound into a regioned ref). Reuses the faithful `materialize` bridge.
            # ELEMENT-TYPE FIDELITY: a `string`-element list (declared return `array string`)
            # must use the STRING materialize bridge — `materialize` is `seq int -> array int`
            # and would type-clash on a `seq string` payload. This mirrors the early/in-loop
            # `Return_seq_str` path (below) for the TAIL (non-raise) return; without it, a
            # string-list function whose only normal exit is the tail return (e.g. os.listdir
            # once its failure paths raise OSError instead of `return []`) wrongly emits the
            # int `materialize` and fails L3 type-check.
            if self._func_return_type == "array string":
                self._materialize_str_bridge()
                val = f"(materialize_str !{whyml_ident(val_ir['name'])})"
            elif (self._func_return_type.startswith("array ")
                  and self._func_return_type != "array int"
                  and self._func_return_type != "array real"
                  and " " not in self._func_return_type[len("array "):]):
                # RECORD-ELEMENT FIDELITY (the third bridge, beside `materialize` and
                # `materialize_str`): a `-> List[<record>]` function whose only normal exit
                # is the tail return of a seq-modelled accumulator
                # (`names.append(_N("alias")(...)); return names`) crosses the same
                # seq->array boundary with a RECORD payload, and the int bridge type-clashes
                # (`seq py_alias` vs `seq int`) exactly as it does for the string payload.
                # The bridge is emitted per ELEMENT TYPE, with the same fresh-result /
                # no-region-link shape and the same two pointwise postconditions as the two
                # existing bridges, so the array is EQUAL to the seq and nothing is erased.
                # Gated on a declared `array <single-token-non-scalar>`: `array int`,
                # `array real` and `array string` (handled above) all keep their existing
                # emission, so every corpus driver is byte-identical.
                # The bridge VAL itself is declared by `_emit_function` (it cannot be
                # declared from here: this body's own mirror models `_add_abstract_op`'s
                # argument as a hashed int, so a COMPUTED declaration string cannot be
                # passed). Here we only name it.
                _elem = self._func_return_type[len("array "):]
                val = "(materialize_" + _elem + " !" + whyml_ident(val_ir["name"]) + ")"
            else:
                self._materialize_bridge()
                val = f"(materialize !{whyml_ident(val_ir['name'])})"
        else:
            if val_ir.get("type") == "Var" and val_ir.get("name") in self._array_locals:
                # `exception Return int` can't carry an array, so on the
                # raise-Return int path we collapse the value to 0
                # (lossy but at least type-correct). When the function
                # actually returns `array int` (slot+signal path) or at
                # function level (no raise), the array variable IS the
                # value — keep its name.
                if use_raise and func_ret_peek != "array int":
                    val = "0"
                else:
                    val = whyml_ident(val_ir["name"])
            else:
                val = self._expr_to_whyml(val_ir, local_refs)
        # typing-engagement ty1 / 25-1700-typing-spec-1 §0/§2.2 C2: if the
        # function's return type is a synthesized `_union_*` variant and the
        # returned value is NOT already a constructor application, auto-inject
        # it into the first arm whose payload type matches (the injection
        # wrapper per arm). This lets `def f() -> Optional[int]: return x+x`
        # type-check (the int return is wrapped as `Arm_<idx>_0 (x+x)`).
        # LEVER F2: thread an `option string` value (`.get(k)` / None / IfExpr thereof)
        # into the Optional[str] union arms BEFORE the generic arm injection — the raw
        # option preserves None-propagation instead of the scalar `None -> 0` default.
        _threaded = self._thread_optional_return(val_ir, local_refs)
        if _threaded is not None:
            val = _threaded
        else:
            val = self._maybe_inject_union_return(val, val_ir)
        if use_raise:
            func_ret = self._func_return_type
            if func_ret.startswith("option ("):
                # Optional-tuple return: the built-in `option (τ...)` carries either
                # `Some (a,b,c)` (a `return (a,b,c)`) or `None` (a `return None`),
                # through the dedicated `Return_opttuple_<arity>` exception. Faithful
                # to Python's `Optional[Tuple]` — `None` and `(0,…)` stay DISTINCT
                # (the raw-tuple `Return_<arity>` path had to collapse `None` to a bare
                # int and could not represent the absent case). The tuple value is
                # lowered directly from `val_ir` (no `_coerce_to_int`, no union arm).
                suffix = func_ret[len("option "):].replace("(", "").replace(")", "").replace(" ", "").replace(",", "_")
                if val_ir is not None and val_ir.get("type") == "Tuple":
                    tup = self._expr_to_whyml(val_ir, local_refs)
                    return f"{indent}raise (Return_opttuple_{suffix} (Some {tup}))"
                return f"{indent}raise (Return_opttuple_{suffix} None)"
            if func_ret == "unit":
                return f"{indent}raise Return_void"
            # V1 pyconst-dispatch (self-tcb-reduction M5, B-bucket): a tuple return whose refined
            # type carries a `pyconst_val` slot (only `_classify_literal_value`'s
            # `(string, pyconst_val, emit_ir)`) uses a DEDICATED payload-typed exception
            # `Return_tup_<slots>` — NOT the shared homogeneous `Return_<arity>` (whose payload is
            # `(int,...,int)`; reusing it would both mis-type the slots AND collide with every
            # corpus 3-tuple return). The MIDDLE (`pyconst_val`) slot is coerced to its value:
            # a `None` literal -> PVNone, a `True`/`False` literal -> `PVBool true/false`, the
            # pyconst_val local `v` -> `!v`. slot0/slot2 lower normally (string / emit_ir ctor).
            # Gated on `"pyconst_val" in func_ret` -> corpus + every other mirror byte-identical
            # (no pyconst_val tuple return there). This branch emits a WhyML-SOURCE STRING (no
            # pyconst_val value handled in Python), so its own lowering in the giants is inert.
            if func_ret.startswith("(") and "pyconst_val" in func_ret:
                _suffix = (func_ret.replace("(", "").replace(")", "")
                           .replace(" ", "").replace(",", "_"))
                return f"{indent}raise (Return_tup_{_suffix} {val})"
            arity = self._current_tuple_arity
            if arity > 0:
                # Tuple return: use the dedicated Return_<arity> exception
                # so the whole tuple value carries through. Do NOT call
                # _coerce_to_int — for tuple-shaped strings that would hash
                # the whole tuple to a single int.
                return f"{indent}raise (Return_{arity} {val})"
            if func_ret == "array int":
                # return-arr.md: array-returning functions with early/in-loop returns carry the
                # value through an IMMUTABLE seq (Why3 forbids a mutable `array int` exception
                # payload); the `with Return_seq s -> materialize s` catch rebuilds the array.
                # `_seq_init_expr` turns a list literal into a Seq.cons chain and bridges any
                # other array-typed RHS (array-local, etc.) with `snapshot`.
                self._materialize_bridge()
                if val_ir is None:
                    seq_val = "Seq.empty"
                elif (val_ir.get("type") == "Var"
                      and val_ir.get("name") in getattr(self, "_seq_locals", set())):
                    seq_val = f"!{whyml_ident(val_ir['name'])}"
                else:
                    seq_val = self._seq_init_expr(val_ir, local_refs)
                return f"{indent}raise (Return_seq {seq_val})"
            if func_ret == "array string":
                # str-list-elements: a STRING-element list returns its growable `seq string`
                # through `Return_seq_str`; the catch materializes it to `array string`. An
                # empty-list return (`return []`) carries the polymorphic `Seq.empty`.
                self._materialize_str_bridge()
                if val_ir is None:
                    seq_val = "Seq.empty"
                elif (val_ir.get("type") == "Var"
                      and val_ir.get("name") in getattr(self, "_seq_locals", set())):
                    seq_val = f"!{whyml_ident(val_ir['name'])}"
                else:
                    seq_val = self._seq_init_expr(val_ir, local_refs)
                return f"{indent}raise (Return_seq_str {seq_val})"
            if func_ret == "array emit_ir":
                # THE STATEMENT-LIST CARRIER: an `array emit_ir` return travels as an
                # immutable `seq emit_ir` through `Return_seq_ir`; the catch materializes
                # it back. An empty-list return (`return []`) carries `Seq.empty`, which is
                # the FAITHFUL empty statement list — not a dropped child.
                if val_ir is None:
                    seq_val = "Seq.empty"
                elif (val_ir.get("type") == "Var"
                      and val_ir.get("name") in getattr(self, "_seq_locals", set())):
                    seq_val = f"!{whyml_ident(val_ir['name'])}"
                elif (isinstance(val_ir, dict)
                      and val_ir.get("type") in ("ArrayLit", "ListLit")
                      and not val_ir.get("elts")):
                    seq_val = "Seq.empty"
                else:
                    # `_seq_init_expr`, NOT `_seq_operand` — matching the two sibling arms
                    # exactly. Measured (lesson (ww)): `_seq_operand` is not modelled in
                    # this method's own MIRROR, so calling it introduced an abstract
                    # `self__seq_operand_2 (x0: emit_ir) (x1: int) : int` whose int return
                    # ill-typed against the string being built — a clean-looking byte diff
                    # that failed L3-tc.
                    seq_val = self._seq_init_expr(val_ir, local_refs)
                return f"{indent}raise (Return_seq_ir {seq_val})"
            if func_ret == "string":
                # 10-1732-gap Gap 1: a `string`-returning function with an early/in-loop
                # return raises `Return_str <string>` (caught by the `with Return_str r -> r`
                # arm). `val` is already the lowered string expression — no int coercion.
                # self-tcb-reduction (union/match cluster): a `return None` in a `string`-
                # returning function (the sentinel `_try_union_is_none_match` uses to signal
                # "pattern does not apply") lowers to the empty string `Return_str ""` — the
                # None-singleton `0` (an int) type-clashes with the `string` payload. Byte-
                # inert: a corpus `-> str` function that `return None` would already FAIL
                # L3-tc on the old `Return_str 0`, so none exists in the passing corpus.
                if val_ir is None or (isinstance(val_ir, dict)
                                      and val_ir.get("type") == "None"):
                    return f'{indent}raise (Return_str "")'
                return f"{indent}raise (Return_str {val})"
            if func_ret == "emit_ir":
                # Return_emit_ir infra: an emit_ir-returning function's early/in-loop
                # return raises `Return_emit_ir <emit_ir>` (caught by the `with
                # Return_emit_ir r -> r` arm, statements.py::_wrap_body_with_return_catch).
                # `val` is already the lowered emit_ir constructor expression (e.g. `(IrAttr
                # ... ...)`) — no int coercion, mirroring the Return_str arm above.
                return f"{indent}raise (Return_emit_ir {val})"
            if func_ret == "term":
                # TERM CARRIER (L13 cursor-nest): a `term`-returning method's early/in-loop
                # return raises the dedicated `Return_term <term>` (caught by the
                # `with Return_term r -> r` arm). `val` is already the lowered term
                # expression — the certified ADT application `(BinOp op l r)` or a sibling
                # call — so no int coercion, exactly the `Return_emit_ir` arm's shape.
                return f"{indent}raise (Return_term {val})"
            if func_ret.startswith("_union_"):
                # value-model campaign incr5 (primitive c): a synthesized-union (`Optional[X]`)
                # early/in-loop return raises its dedicated `Return_<variant>` exception
                # (caught by `_wrap_body_with_return_catch`). `val` is already the injected
                # variant value (`_maybe_inject_union_return` wrapped it as `Arm_N_0 <v>` /
                # `Arm_N_None`) — no int coercion, mirroring the Return_str/Return_emit_ir arms.
                return f"{indent}raise (Return_{func_ret} {val})"
            # Array-returning functions with early returns CANNOT use the
            # straightforward `raise (Return arr)` shape — Why3 forbids
            # `array int` in exception payloads (mutable types), and the
            # `ref (array int)` + signal workaround triggers Why3's
            # region/linearity tracking (`Array.make` in the body becomes
            # "prohibits further usage of _ret_array_slot"). Workaround
            # at the source level: `\trusted` the affected functions so
            # Module6 emits `val` (spec-only) instead of `let` + body.
            # See docs/self-annotate-layer2-queue.md class M for the
            # design analysis.
            # int return path: an array-typed val here is structurally
            # incompatible — `Return int` can't carry it. Collapse to 0
            # (matches the pre-existing lossy behaviour).
            if (val_ir and val_ir.get("type") == "Var"
                    and val_ir.get("name") in self._array_locals):
                val = "0"
            elif val == "()":
                val = "0"
            elif val == "true":
                val = "1"
            elif val == "false":
                val = "0"
            else:
                val = self._bool_ir_to_int_wrap(val, val_ir)
            val = self._coerce_to_int(val)
            return f"{indent}raise (Return {val})"
        # Optional-tuple TAIL (non-raise) return: mirror the raise-path option wrap
        # for a function whose only exits are tail returns (`Some (a,b,c)` / `None`).
        if self._func_return_type.startswith("option ("):
            if val_ir is not None and val_ir.get("type") == "Tuple":
                return f"{indent}(Some {self._expr_to_whyml(val_ir, local_refs)})"
            if val_ir is None or val_ir.get("type") == "None":
                return f"{indent}None"
        # W8 (vii): TAIL-return bool→int coercion. A `-> bool` Python function lowers to
        # a WhyML `int`-returning `let` (Python `bool` is modelled as `int` throughout —
        # `bool` params, `bool` fields and the early/in-loop `raise (Return …)` path above
        # all coerce). The tail (non-raise) return was the ONE position that did not, so
        # `def f(x: int) -> bool: return x == 55` emitted `let f (x: int) : int = (x = 55)`
        # and failed L3 type-check. Applies the SAME normalization as the raise path
        # (literal True/False → 1/0, bool-source IR → `if … then 1 else 0`) and only when
        # the function's WhyML return type is `int`, so unit/string/array/record/union
        # returns are untouched. Byte-inert on the corpus: no corpus or pycsl_lib function
        # declares `-> bool`, and an int-returning function whose tail value is a bool-source
        # expression was ill-typed WhyML before this (it could not have been emitting).
        # IDEMPOTENCE GUARD: some Compare lowerings (the string relational ops
        # `str_lt_op`/`str_le_op`, corpus 0477-0480) already emit the int form
        # `(if … then 1 else 0)`; re-wrapping would produce `(if (if … then 1 else 0)
        # then 1 else 0)` (ill-typed AND a corpus byte-diff). Skip when the lowered
        # value is already an int-coerced conditional.
        if (self._func_return_type == "int"
                and not (val.startswith("(if ") and val.endswith(" then 1 else 0)"))):
            if val == "true":
                val = "1"
            elif val == "false":
                val = "0"
            else:
                val = self._bool_ir_to_int_wrap(val, val_ir)
        return f"{indent}{val}"
