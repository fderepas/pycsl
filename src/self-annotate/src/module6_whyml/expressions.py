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
    # self-tcb-reduction _typeddict_record_literal (cap-1): the current function's
    # declared return type (live: functions.py sets it per emitted function). Modeled
    # as a string self-field so `getattr(self, "_func_return_type", "")` reads the real
    # `string`, not the folded "" default — the construction-context disambiguator.
    _func_return_type: str = ""
    _lambda_locals: Set[str] = None
    _module_constants: Dict[str, str] = None
    _module_global_classes: Dict[str, str] = None
    _quant_record_binders: Dict[str, str] = None
    _quant_scalar_binders: Set[str] = None
    _record_locals: Set[str] = None
    _record_types: Dict[str, Any] = None
    # self-tcb-reduction _namedtuple_positional_access (WL-04b/c): the record-array
    # PARAM/LOCAL name→whyml_name maps (live: functions.py `__init__`), modeled as
    # string→string dict self-fields so `getattr(self, "_record_array_params",
    # {}).get(_nm)` reads the real `map string (option string)`.
    _record_array_params: Dict[str, str] = None
    _record_array_locals: Dict[str, str] = None
    _shared_var_names: Set[str] = None
    _todict_aliases: Dict[str, str] = None
    _current_symbol_table: Dict[str, str] = None
    _mutable_state_classes: Set[str] = None
    _ambiguous_fields: Set[str] = None
    _getattr_self_dict_aliases: Dict[str, str] = None
    # self-tcb-reduction Tier-5 (union/match cluster sub-increment 2): `_variant_types`
    # (symtype -> variant-metadata sub-dict, a heterogeneous `Dict[str, Any]`) is annotated
    # `Dict[str, Dict[str, PyVal]]` so the emitter types it as the faithful nested `map string
    # (option (map string (option hval)))` — thus `_variant_types.get(symtype)` reads a real
    # `map string (option hval)` vinfo whose `.get("constructors", {}).items()` descends the
    # actual structure (NOT the int-erased facade). Matches the `stmt_control_flow.py` mirror's
    # retype of the SAME emitter field. The two already-converted key-membership readers
    # (`_tag_of_type`, `_handle_var_expr`'s `name in _variant_types`) survive: a `mem` test over
    # a differently-VALUED map is value-type-agnostic. Emitter-internal, corpus-absent -> the
    # reference corpus + every other mirror byte-identical. Live: Module6_WhyMLTranspiler.__init__.
    _variant_types: Dict[str, Dict[str, PyVal]] = None
    _seq_value_types: Dict[str, str] = None
    _array_elem_types: Dict[str, str] = None
    _current_array1d_params: Set[str] = None
    # self-tcb-reduction T1.a: further state fields the ported expression handlers read.
    _in_spec: int = 0
    _value_semantic: int = 0
    _mutated_collection_params: Set[str] = None
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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

    # str(<int>) value-model increment (self-tcb-reduction M6, C-bucket): now that
    # `str(<int>)` lowers to the faithful `str_of_int : int -> string` (expressions.py
    # value-model fix), this `-> str` helper ports body-faithfully: a quoted-literal arg
    # is rendered to its `str(stable_hash(...))` decimal string, else returned unchanged.
    # isinstance_op = 0, assigns nothing. Verbatim body port of the LIVE `_coerce_str_arg`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _coerce_str_arg(whyml_str: str) -> str:
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(stable_hash(whyml_str))
        return whyml_str
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _deref(self, expr: str) -> str:
        """Dereference a WhyML ref-typed operand: `x` → `!x` (idempotent — a leading
        `!` is normalized, not doubled). Used by the set/list/map handlers, where a
        collection operand may arrive already-dereffed."""
        return f"!{expr.lstrip('!')}" if expr.startswith("!") else expr

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _coerce_to_int(self, whyml_str: str) -> str:
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(stable_hash(whyml_str))
        stripped = whyml_str.strip()
        array_prefixes = ("(Array.make", "(Array.sub ", "(array_slice ", "(sorted_1 ",
                          "(list_new_arr ", "(any_1 ", "(all_1 ")
        for prefix in array_prefixes:
            if stripped.startswith(prefix):
                return "0"
        map_prefixes = ("(map_update_some ", "(map_update_none ",
                        "(const (None: option int)")
        for prefix in map_prefixes:
            if stripped.startswith(prefix):
                return "0"
        if "," in whyml_str and whyml_str.startswith("(") and whyml_str.endswith(")"):
            return str(stable_hash(whyml_str))
        return whyml_str
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _match_pattern_cond(self, pat: int, subject: str, local_refs: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    # str(<int>) value-model increment (self-tcb-reduction M6, C-bucket): now that
    # `str(<int>)` lowers to `str_of_int : int -> string`, a quoted-literal string operand
    # hashes to its decimal `str(stable_hash(...))`; a non-literal goes through the
    # uninterpreted `str_hash_op`. isinstance_op = 0. Verbatim body port of the LIVE
    # `_str_operand_to_int`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _str_operand_to_int(self, whyml_str: str) -> str:
        s = whyml_str.strip()
        if s.startswith('"') and s.endswith('"'):
            return str(stable_hash(whyml_str))
        self._add_abstract_op("val str_hash_op (s: string) : int")
        return f"(str_hash_op {whyml_str})"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _handle_binop(self, expr: int, local_refs: int, invariant_ctx: bool=False, subst: int=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._current_params, self._current_self_type, self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _handle_dotted_call(self, func_name: str, args: List[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _coerce_dotted_args(self, args: List[str], param_types: List[str]) -> List[str]:
        return []

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _strip_outer_parens(s: str) -> str:
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _frame_trigger_term(self, node: Any) -> Optional[Dict[str, Any]]:
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._current_params, self._current_self_type, self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_null_byte_lit(ir: "ExprIR") -> bool:
        """True iff `ir` is the byte literal `b'\\x00'` — represented in the IR as an
        `ArrayLit` of a single `Number 0` (the bytes literal lowering)."""
        if ir.get("type") != "ArrayLit":
            return False
        elts = ir.get("elts", [])
        return (len(elts) == 1
                and elts[0].get("type") == "Number"
                and elts[0].get("value") == 0)

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
    def _static_width(self, lower_ir: "ExprIR", upper_ir: "ExprIR") -> Optional[int]:
        return None

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    #@ no_inline
    def _match_field_decode_idiom(self, expr: "ExprIR") -> Optional[tuple]:
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

    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _recognize_field_decode_idiom(self, expr: "ExprIR", local_refs: Set[str], invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> Optional[str]:
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
    def _alias_self_field(self, name: str) -> str:
        """§26: if `name` is a local bound from `getattr(self, "<field>", …)` on a
        dict/set self-field, return the dotted `self.<field>`; else None."""
        fld = getattr(self, "_getattr_self_dict_aliases", {}).get(name)
        return f"self.{fld}" if fld else ""


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
    #@ assigns self._current_params, self._current_self_type, self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _handle_call_expr(self, expr: int, local_refs: int, invariant_ctx: bool=False, subst: int=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _content_string_method(self, expr: int, args: List[str], func_name: str, local_refs: int, invariant_ctx: bool, subst: int) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_none_ctor_for(self, x_ir: Dict[str, PyVal]) -> Optional[str]:
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _handle_isinstance(self, expr: int) -> str:
        return ""
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _subst_params(self, ir: Any, arg_nodes: Dict[str, Any]) -> Any:
        if isinstance(ir, dict):
            if ir.get("type") == "Var" and ir.get("name") in arg_nodes:
                return arg_nodes[ir["name"]]
            return {k: self._subst_params(v, arg_nodes) for k, v in ir.items()}
        if isinstance(ir, list):
            return [self._subst_params(x, arg_nodes) for x in ir]
        return ir

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _call_record_constructor(self, args: List[str], func_name: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_bytes_methods(self, args: List[str], func_name: str) -> Optional[str]:
        return None

    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _typeddict_field_access(self, value: "ExprIR", index_ir: "ExprIR", local_refs: Set[str], invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> Optional[str]:
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

    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _typeddict_record_literal(self, expr: "ExprIR", local_refs: Set[str], invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> Optional[str]:
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
        kv: Dict[str, Dict[str, Any]] = {}
        for k, v in zip(keys, values):
            if isinstance(k, dict) and k.get("type") == "String":
                kv[k.get("value", "")] = v
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
        parts: List[str] = []
        for fname in rec_info["fields"]:
            v = kv.get(fname)
            val = self._expr_to_whyml(v, local_refs, invariant_ctx, subst)
            parts.append(f"{self._field_label(rec_lower, fname)} = {val}")
        return "{ " + "; ".join(parts) + " }"

    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _namedtuple_positional_access(self, value: "ExprIR", index_ir: "ExprIR", local_refs: Set[str], invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> Optional[str]:
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _handle_subscript(self, expr: int, local_refs: int, invariant_ctx: bool=False, subst: int=None) -> str:
        return ""
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _handle_attribute_expr(self, expr: int, local_refs: int, invariant_ctx: bool, subst: int) -> str:
        return ""
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._quant_record_binders
    def _push_quant_binder(self, var: Optional[str], binder_type: Optional[str]):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._quant_record_binders, self._quant_scalar_binders
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
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _handle_fstring_expr(self, node: "ExprIR", local_refs: Set[str],
                              invariant_ctx: bool, subst: Dict[str, str]) -> str:
        # re-trusted: _handle_fstring_expr — `getattr(self, "_current_self_type", None) in
        # getattr(self, "_mutable_state_classes", set())` reflection leak, value-model-gapped
        # (self-scalar getattr-default collapses to int-0 vs string-keyed set) (see generic-dict-str-and.md)
        return ""
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _handle_ifexpr_expr(
        self,
        node: "IfExprExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # re-trusted: _handle_ifexpr_expr — `getattr(self, "_current_self_type", None) in
        # getattr(self, "_mutable_state_classes", set())` reflection leak, value-model-gapped
        # (self-scalar getattr-default collapses to int-0 vs string-keyed set) (see generic-dict-str-and.md)
        return ""
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
            if var in getattr(self, "_seq_locals", set()) and not self._in_spec:
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
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
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _expr_to_whyml(self, expr: "ExprIR", local_refs: Set[str], invariant_ctx: bool=False, subst: Optional[Dict[str, str]]=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec, self._quant_record_binders, self._quant_scalar_binders
    def _expr_to_whyml_string_ctx(self, ir: "ExprIR", local_refs: int) -> str:
        return ""


