from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from module6_whyml.identifiers import op_translate, whyml_ident, stable_hash
from module6_whyml.struct_format import parse_format
from module6_whyml.expr_ghost_collections import GhostCollectionOpsMixin
from module6_whyml.expr_ghost_spec_ops import GhostSpecOpsMixin
# self-tcb-reduction T1.a (E-2): import the concrete ExprIR subclasses the handlers annotate, so
# `node: "UnaryOpExpr"` resolves to a record (fields `op`/`expr`), like the statement mirror's
# `stmt: AssignStmt`. The base `node: "ExprIR"` handlers use the emit_ir keystone instead.
from ir_schema import AtExpr, IfExprExpr, NamedExprExpr, OldExpr, UnaryOpExpr
def mutable_state(cls): return cls
""  # pycsl
# self-tcb-reduction T1.a: mark the expression mixin @mutable_state so the emit_ir ADT + the
# string/reflection recognizers fire for the un-`\trusted` `_handle_*_expr` bodies (the CF0 analog).
@mutable_state
@dataclass
class ExpressionEmissionMixin(GhostCollectionOpsMixin, GhostSpecOpsMixin):
    # State fields the ported expression handlers read (declared for @dataclass / @mutable_state).
    _all_record_fields: Set[str] = None
    _array_locals: Set[str] = None
    _class_constants: Dict[str, Dict[str, int]] = None
    _constructors: Dict[str, Any] = None
    _current_params: Set[str] = None
    _current_self_type: str = ""
    _emit_record_ctx: str = ""
    _lambda_locals: Set[str] = None
    _module_constants: Dict[str, str] = None
    _module_global_classes: Dict[str, str] = None
    _quant_record_binders: Dict[str, str] = None
    _quant_scalar_binders: Set[str] = None
    _record_locals: Set[str] = None
    _record_types: Dict[str, Any] = None
    _shared_var_names: Set[str] = None
    _todict_aliases: Dict[str, str] = None
    _current_symbol_table: Dict[str, str] = None
    _mutable_state_classes: Set[str] = None
    _ambiguous_fields: Set[str] = None
    _variant_types: Dict[str, str] = None
    _seq_value_types: Dict[str, str] = None
    _array_elem_types: Dict[str, str] = None
    _current_array1d_params: Set[str] = None
    # self-tcb-reduction T1.a: further state fields the ported expression handlers read.
    _in_spec: int = 0
    _value_semantic: int = 0
    _seq_locals: Set[str] = None
    _result_alias: str = ""
    _heap_var: str = ""
    _scope_must: Set[str] = None
    _scope_all: Set[str] = None
    _scope_params: Set[str] = None
    _scope_dyn_exec: int = 0
    'Expression-emission dispatch: every IR expression-shape `_handle_*_expr`\n    handler routed via `_EXPR_DISPATCH` on the facade, plus the orchestration\n    entrypoints (`_expr_to_whyml`, `_expr_to_whyml_string_ctx`) and the shared\n    helpers (`_to_bool`, `_coerce_*`, `_match_pattern_cond`, ...). Mixed into\n    Module6_WhyMLTranspiler. `_EXPR_DISPATCH` stays on the facade as a class\n    attribute — moving it would force a circular import.\n    '
    _BITWISE_FOLD_OPS = {'&': lambda a, b: a & b, '|': lambda a, b: a | b, '^': lambda a, b: a ^ b, '<<': lambda a, b: a << b, '>>': lambda a, b: a >> b, '**': lambda a, b: a ** b}
    _BITWISE_FN_NAMES = {'&': 'bit_and', '|': 'bit_or', '^': 'bit_xor', '<<': 'bit_lshift', '>>': 'bit_rshift', '**': 'py_pow'}

    # self-tcb-reduction T1.a: sibling stubs the ported expression handlers call cross-mixin.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _add_abstract_op(self, decl: str) -> None:
        return

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _is_emit_ir_expr(self, ir: "ExprIR") -> bool:
        return False
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _e(self, ir: Dict, lr: Set[str]) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _whyml_string_literal(self, s: str) -> str:
        """A Python string → its WhyML double-quoted string literal, backslash and
        double-quote escaped. Pure (`assigns \\nothing`). Extracted (07-03-refactor R5)
        from the duplicated inline escaper in `_handle_var_expr` / `_call_named_builtins`."""
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _to_bool(self, whyml_str: str, ir_expr: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _coerce_str_arg(whyml_str: str) -> str:
        return ""
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _array_coerce_arg(whyml_str: str) -> str:
        return ""
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _deref(self, expr: str) -> str:
        """Dereference a WhyML ref-typed operand: `x` → `!x` (idempotent — a leading
        `!` is normalized, not doubled). Used by the set/list/map handlers, where a
        collection operand may arrive already-dereffed."""
        return f"!{expr.lstrip('!')}" if expr.startswith("!") else expr

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _coerce_to_int(self, whyml_str: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _dv_empty_default(self, nu: Optional[str]) -> Optional[str]:
        return None
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _dv_missing_default(self, nu: str) -> str:
        """`None ->` placeholder for a dict subscript read (typed per ν; proven
        dead under `#@ no_exception KeyError`, the ambient default otherwise)."""
        if nu == "string":
            return '""'
        if nu and nu.startswith("seq "):
            # #15: `Dict[str, List[T]]` value (`seq string`/`seq int`) -> the empty seq default.
            return f"(Seq.empty: {nu})"
        if nu and nu.startswith("map "):
            inner_v = (nu.split("(option ", 1)[1].rsplit(")", 1)[0]
                       if "(option " in nu else "int")
            return f"(const (None: option {inner_v}))"
        return "0"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _dv_store_value(self, nu: Optional[str], val_expr: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _match_pattern_cond(self, pat: int, subject: str, local_refs: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_membership(self, op: str, expr: int, left: str, right: str, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_bitwise_or_power(self, op_char: str, expr: int, left: str, right: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _is_string_expr(self, ir: "ExprIR") -> bool:
        return False
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _is_float_expr(self, ir: "ExprIR") -> bool:
        return ""
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _str_operand_to_int(self, whyml_str: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_binop(self, expr: int, local_refs: int, invariant_ctx: bool=False, subst: int=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _iter_len_expr(self, ir: int, local_refs: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_len_call(self, expr: int, args: List[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_join_call(self, expr: int, args: List[str]) -> str:
        return ""
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_sum_call(self, expr: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _resolve_dotted_signature(self, func_name: str):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_dotted_call(self, func_name: str, args: List[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _coerce_dotted_args(self, args: List[str], param_types: List[str]) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _strip_outer_parens(s: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _frame_trigger_term(self, node: Any) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _dotted_ensures_suffix(self, result_ensures: List[int], n: int, param_types: List[str], field_spec: Optional[Any]=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_struct_call(self, expr: int, args: List[str], func_name: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_contract_logic_symbol(self, func_name: str, expr: int, args: List[str]) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_null_byte_lit(ir: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _linear_form(self, ir: int) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _static_width(self, lower_ir: int, upper_ir: int) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _match_field_decode_idiom(self, expr: int) -> Optional[tuple]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _recognize_field_decode_idiom(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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


    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _todict_recv_node_ir(self, recv_dotted: str) -> Dict[str, Any]:
        """The node IR for a dotted receiver (`self.types` → `Attribute(Var(self), types)`)."""
        parts = recv_dotted.split(".")
        node: Dict[str, Any] = {"type": "Var", "name": parts[0]}
        for p in parts[1:]:
            node = {"type": "Attribute", "object": node, "attr": p}
        return node

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_call_expr(self, expr: int, local_refs: int, invariant_ctx: bool=False, subst: int=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _content_string_method(self, expr: int, args: List[str], func_name: str, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_named_builtins(self, expr: int, args: List[str], func_name: str, local_refs: int=None, invariant_ctx: bool=False, subst: int=None) -> Optional[str]:
        return None

    _METATYPE_TAGS: Dict[str, str] = {'int': 'tag_int', 'bool': 'tag_int', 'str': 'tag_str', 'float': 'tag_float', 'list': 'tag_list', 'List': 'tag_list', 'dict': 'tag_dict', 'Dict': 'tag_dict', 'set': 'tag_dict', 'frozenset': 'tag_dict', 'object': 'tag_object'}
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_metatype_tags(self) -> None:
        pass
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _tag_of_value(self, x_ir: Dict[str, Any]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_none_ctor_for(self, x_ir: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_isinstance(self, expr: int) -> str:
        return ""
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _subst_params(self, ir: Any, arg_nodes: Dict[str, Any]) -> Any:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_record_constructor(self, args: List[str], func_name: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_bytes_methods(self, args: List[str], func_name: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _typeddict_field_access(self, value: int, index_ir: int, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _typeddict_record_literal(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _namedtuple_positional_access(self, value: int, index_ir: int, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_subscript(self, expr: int, local_refs: int, invariant_ctx: bool=False, subst: int=None) -> str:
        return ""
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_attribute_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
        if name in local_refs:
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _quant_binder_whyml(self, binder_type: Optional[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _push_quant_binder(self, var: Optional[str], binder_type: Optional[str]):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _pop_quant_binder(self, var: Optional[str], token) -> None:
        pass
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_label(self, record_lower: str, field: str) -> str:
        """WhyML label for a record field. Ambiguous names (shared by >1
        record, e.g. an inherited field) are qualified `<record>_<field>` to
        avoid Why3's global field-label collision; unique names stay bare."""
        base = whyml_ident(field)
        if field in getattr(self, "_ambiguous_fields", set()) and record_lower:
            return f"{whyml_ident(record_lower)}_{base}"
        return base
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_field_get_expr(self, node: "ExprIR", invariant_ctx: bool) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature
        if invariant_ctx:
            return self._field_label(self._emit_record_ctx, expr['field'])
        obj = expr['object']
        field = expr['field']
        # Class-body integer constant referenced as `self.CONST` → its literal.
        self_type = self._current_self_type
        if (obj == "self" and self_type
                and field in self._class_constants.get(self_type, {})):
            return f"({self._class_constants[self_type][field]})"
        decl_fields = self._all_record_fields
        if field in decl_fields:
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _fstring_str_part(self, pp: "ExprIR", local_refs: Set[str],
                          invariant_ctx: bool, subst: Dict[str, str]) -> str:
        """One segment of a MIXED (str/int) f-string in a @mutable_state class: a string
        segment passes through; an int/opaque segment is `int_to_string`-wrapped. Hoisted
        (07-03-refactor R2) from the `_sp` nested closure in `_handle_fstring_expr` so the
        segment logic types identically under proof mode and `--no-proof`."""
        w = self._expr_to_whyml(pp, local_refs, invariant_ctx, subst)
        return w if self._is_string_expr(pp) else f"(int_to_string {self._coerce_to_int(w)})"
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
        if (not self._in_spec and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
        # i-feel-good.md I-A/I-B: a ternary is a STRING expression when at least one arm is
        # string-typed and the other is string-or-`None` — emit the string arms directly (a
        # bare `""`/`"lit"` stays a WhyML string, a `None` arm → "" the absent sentinel), so
        # `arr.get("name","") if … else ""` and `d.get(k) if k else None` type-check as
        # string. @mutable_state-gated → the corpus int model is byte-identical.
        _ms = (getattr(self, "_current_self_type", None)
               in getattr(self, "_mutable_state_classes", set()))
        _b_str = self._is_string_expr(_bd)
        _o_str = self._is_string_expr(_od)
        _b_none = _bd.get("type") == "None"
        _o_none = _od.get("type") == "None"
        if _ms and (_b_str or _o_str) and (_b_str or _b_none) and (_o_str or _o_none):
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
        body = self._coerce_to_int(body)
        orelse = self._coerce_to_int(orelse)
        return f"(if {test} then {body} else {orelse})"
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_arraylen_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _module_binding_names(self) -> Set[str]:
        return ""
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _expr_to_whyml(self, expr: "ExprIR", local_refs: Set[str], invariant_ctx: bool=False, subst: Optional[Dict[str, str]]=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _expr_to_whyml_string_ctx(self, ir: "ExprIR", local_refs: int) -> str:
        return ""


