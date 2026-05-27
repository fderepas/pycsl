from __future__ import annotations

import json
from typing import Dict, Any, Optional, Set, List, Tuple

from module6_whyml.ir_scanner import IRScanner
from module6_whyml.identifiers import (
    OP_MAP,
    WHYML_RESERVED,
    whyml_ident,
    safe_mutex_name,
    op_translate,
)
from module6_whyml.scc import (
    compute_sccs,
    find_calls_in_ir,
    sort_functions_by_scc,
)


class Module6_WhyMLTranspiler:
    """Reads the JSON IR and transpiles it into valid WhyML (.mlw) syntax."""
    
    def __init__(self, json_ir: str, memory_model: str = "hoare") -> None:
        self.ir = json.loads(json_ir)
        self.memory_model = memory_model   # "hoare" | "typed" | "store"
        self._abstract_ops: Dict[str, str] = {}  # Abstract val declarations: name → full decl string
        self._record_types: Dict[str, Any] = {}  # class_name_lower → {fields: [...], defaults: {...}}
        self._shared_var_names: Set[str] = set()  # Module-level shared variable names (concurrent model)
        self._havoc_counter: int = 0             # Counter for unique havoc variable names
        self._in_spec: bool = False              # True when emitting contracts (no div-by-zero VCs)
        # Per-function state — reset per function via `_reset_function_state`;
        # initialised here so they're always defined and accessing them
        # before the first reset is safe.
        self._bounded_int: Optional[int] = None
        self._array2d_params: Set[str] = set()
        self._current_array1d_params: Set[str] = set()
        self._current_params: Set[str] = set()
        self._current_symbol_table: Dict[str, Any] = {}
        self._array_locals: Set[str] = set()
        self._dict_locals: Set[str] = set()
        self._record_locals: Set[str] = set()
        self._lambda_locals: Set[str] = set()
        self._current_self_type: Optional[str] = None
        self._func_return_type: str = "int"
        self._current_tuple_arity: int = 0
        self._has_early_ret: bool = False
        self._for_idx_init: str = "0"
        # Whole-module state — populated by `transpile()` before any
        # function emission; initialised empty so type-check passes and
        # accidental early access yields a clean empty default.
        self._all_record_fields: Set[str] = set()
        self._module_func_names: Set[str] = set()
        self._module_method_return_types: Dict[str, str] = {}
        self._module_method_param_types: Dict[str, List[str]] = {}
        self._auto_trusted_array_returns: List[str] = []
        self._auto_trusted_tuple_returns: List[str] = []
        self._auto_trusted_map_returns: List[str] = []
        self._auto_trusted_set_op: List[str] = []

    @property
    def _heap_var(self) -> str:
        """Returns the name of the mutable heap variable for the current model."""
        if self.memory_model == "typed":
            return "int_mem"
        elif self.memory_model == "store":
            return "store"
        raise ValueError(f"No heap variable in Hoare model")

    # Dispatch table for _expr_to_whyml: maps IR type string → method name.
    # All dispatched methods use the uniform quad signature (expr, local_refs, invariant_ctx, subst).
    # Non-standard-signature handlers (Var, FieldGet) are called explicitly before this dict.
    _EXPR_DISPATCH: Dict[str, str] = {
        "BinOp":        "_handle_binop",
        "Call":         "_handle_call_expr",
        "Subscript":    "_handle_subscript",
        "Attribute":    "_handle_attribute_expr",
        "FString":      "_handle_fstring_expr",
        "UnaryOp":      "_handle_unaryop_expr",
        "Old":          "_handle_old_expr",
        "At":           "_handle_at_expr",
        "IfExpr":       "_handle_ifexpr_expr",
        "NamedExpr":    "_handle_named_expr_expr",
        "SliceAccess":  "_handle_slice_access_expr",
        "ArrayLen":     "_handle_arraylen_expr",
        "Valid":        "_handle_valid_expr",
        "Separated":    "_handle_separated_expr",
        "Length2D":     "_handle_length2d_expr",
        "Valid2D":      "_handle_valid2d_expr",
        "IsSorted":     "_handle_issorted_expr",
        "Sum":          "_handle_sum_node_expr",
        "Lambda":       "_handle_lambda_expr",
        "SetLit":       "_handle_setlit_expr",
        # Ghost expression types
        "MkTuple":      "_handle_mktuple_expr",
        "FstExpr":      "_handle_fst_expr",
        "SndExpr":      "_handle_snd_expr",
        "ProjExpr":     "_handle_proj_expr",
        "StrConcat":    "_handle_strconcat_expr",
        "StrLength":    "_handle_str_length_expr",
        "StrSub":       "_handle_str_sub_expr",
        "GhostCopy":      "_handle_ghost_copy_expr",
        "GhostCopyRange": "_handle_ghost_copy_range_expr",
        "GhostMake":      "_handle_ghost_make_expr",
        "MapEmpty":     "_handle_map_empty_expr",
        "MapGet":       "_handle_map_get_expr",
        "MapSet":       "_handle_map_set_expr",
        "MapEq":        "_handle_map_eq_expr",
        "HasKey":       "_handle_has_key_expr",
        "MapRemove":    "_handle_map_remove_expr",
        "SetEmpty":     "_handle_set_empty_expr",
        "SetAdd":       "_handle_set_add_expr",
        "SetRemove":    "_handle_set_remove_expr",
        "SetMem":       "_handle_set_mem_expr",
        "SetUnion":     "_handle_set_union_expr",
        "SetInter":     "_handle_set_inter_expr",
        "SetDiff":      "_handle_set_diff_expr",
        "SetCard":      "_handle_set_card_expr",
        "SetSubset":    "_handle_set_subset_expr",
        "SetEq":        "_handle_set_eq_expr",
        "Nil":          "_handle_nil_expr",
        "Cons":         "_handle_cons_expr",
        "Hd":           "_handle_hd_expr",
        "Tl":           "_handle_tl_expr",
        "ListLength":   "_handle_list_length_expr",
        "Nth":          "_handle_nth_expr",
        "Mem":          "_handle_mem_expr",
        "Append":       "_handle_append_expr",
    }

    def _add_abstract_op(self, decl: str) -> None:
        """Register an abstract val declaration, deduplicating by name+arity.
        Different arities for the same function get unique names (e.g., stmt_get, stmt_get_2)."""
        parts = decl.split()
        if len(parts) >= 2 and parts[0] == "val":
            if parts[1] == "constant":
                name = parts[2] if len(parts) > 2 else decl
            else:
                name = parts[1]
        else:
            name = decl
        if name not in self._abstract_ops:
            self._abstract_ops[name] = decl
        else:
            # If same name, same declaration → skip
            if self._abstract_ops[name] == decl:
                return
            # Different arity → store under name_N key
            # Count params in existing and new
            existing = self._abstract_ops[name]
            existing_params = existing.count("(x")
            new_params = decl.count("(x")
            if new_params != existing_params:
                # Store under arity-suffixed key
                arity_key = f"{name}_{new_params}"
                self._abstract_ops[arity_key] = decl
            else:
                # Same arity but different declaration — keep longer
                if len(decl) > len(existing):
                    self._abstract_ops[name] = decl

    def _to_bool(self, whyml_str: str, ir_expr: Dict[str, Any]) -> str:
        """Coerce a WhyML expression to bool if it might be int.
        Comparison operators and bool literals are already bool.
        Calls to isinstance_check, hasattr_check are already bool.
        Other expressions (int) need `<> 0` coercion."""
        t = ir_expr.get("type", "")
        op = ir_expr.get("op", "")
        # Already boolean: comparisons, not, bool literals, isinstance
        if t == "BinOp" and op in ("==", "!=", "<", ">", "<=", ">=", "in", "not in"):
            return whyml_str
        if t == "BinOp" and op in ("and", "or") and self._in_spec:
            # In spec context, and/or use && / || which are already bool
            return whyml_str
        if t == "UnaryOp" and op == "not":
            return whyml_str
        if t == "Bool":
            # In body context, Bool emits 1/0 but we need true/false for formulas
            if whyml_str == "1":
                return "true"
            if whyml_str == "0":
                return "false"
            return whyml_str
        if t == "Call" and ir_expr.get("func", "") in ("isinstance", "hasattr"):
            return whyml_str
        if t in ("Exists", "Forall", "Compare"):
            return whyml_str
        # Ghost set/map predicates already return bool — no <> 0 needed
        if t in ("SetMem", "SetSubset", "SetEq", "MapEq", "HasKey"):
            return whyml_str
        # Array locals can't be compared with <> 0; emit true (always allocated)
        if t == "Var":
            name = ir_expr.get("name", "")
            if name in self._array_locals:
                return "true"
        # Coerce int → bool
        return f"({whyml_str} <> 0)"

    @staticmethod
    def _coerce_str_arg(whyml_str: str) -> str:
        """Convert a WhyML string literal to an int hash for abstract val arguments."""
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(hash(whyml_str) % 2147483647)
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
        # Bare identifier — could be array-typed (callee's
        # responsibility); pass through.
        if stripped.replace("_", "").replace("!", "").isalnum():
            return whyml_str
        # Anything else (BinOp result, parenthesised int expression) —
        # coerce to placeholder since we can't recover the array.
        return "(Array.make 1 0)"

    def _coerce_to_int(self, whyml_str: str) -> str:
        """Coerce any non-int WhyML expression to int for abstract val arguments."""
        # String literals → int hash
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(hash(whyml_str) % 2147483647)
        # Array-shaped expressions can't be passed where int is expected.
        # The array's contents have no axioms; coerce to 0 placeholder.
        stripped = whyml_str.strip()
        array_prefixes = ("(Array.make", "(array_slice ", "(sorted_1 ",
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
            return str(hash(whyml_str) % 2147483647)
        # Record self → convert to int via abstract op
        self_type = self._current_self_type
        if whyml_str == "self" and self_type:
            conv_name = f"self_to_int_{self_type}"
            self._add_abstract_op(f"val {conv_name} (x: {self_type}) : int")
            return f"({conv_name} self)"
        return whyml_str


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

    _BITWISE_FOLD_OPS = {
        "&": lambda a, b: a & b, "|": lambda a, b: a | b, "^": lambda a, b: a ^ b,
        "<<": lambda a, b: a << b, ">>": lambda a, b: a >> b, "**": lambda a, b: a ** b,
    }
    _BITWISE_FN_NAMES = {
        "&": "bit_and", "|": "bit_or", "^": "bit_xor",
        "<<": "bit_lshift", ">>": "bit_rshift", "**": "py_pow",
    }

    def _emit_membership(self, op: str, expr: Dict[str, Any], left: str, right: str,
                          local_refs: Set[str], invariant_ctx: bool,
                          subst: Optional[Dict[str, str]]) -> str:
        """Emit `in` / `not in` against either an inline collection literal
        (Tuple/ArrayLit/SetLit), a body-level dict (match-based, since
        Why3 program code lacks decidable equality on `option int`), or a
        generic abstract `contains_check`."""
        negate = op == "not in"
        rhs = expr.get("right", {})
        if rhs.get("type") in ("Tuple", "ArrayLit", "SetLit"):
            elts = rhs.get("elts", [])
            if elts:
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
        if not rhs_is_map and rhs.get("type") in ("Attribute", "FieldGet"):
            ft = self._field_type_of(rhs)
            if ft in ("set", "dict", "frozenset"):
                rhs_is_map = True
        if rhs_is_map:
            left_c = self._coerce_to_int(left)
            arms = ("| Some _ -> false | None -> true" if negate
                    else "| Some _ -> true | None -> false")
            return f"(match Map.get ({right}) ({left_c}) with {arms} end)"
        self._add_abstract_op("val contains_check (x: int) (c: int) : bool")
        call = f"(contains_check {self._coerce_str_arg(left)} {self._coerce_str_arg(right)})"
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
        self._add_abstract_op(f"val {op_fn} (x: int) (y: int) : int")
        return f"({op_fn} {self._coerce_to_int(left)} {self._coerce_to_int(right)})"

    def _handle_binop(self, expr: Dict[str, Any], local_refs: Set[str],
                      invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        raw_op = expr["op"]
        # [default] * size → Array.make size default
        if raw_op == "*" and expr["left"].get("type") == "ArrayLit":
            elts = expr["left"].get("elts", [])
            default_val = self._expr_to_whyml(elts[0], local_refs, invariant_ctx, subst) if elts else "0"
            size = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
            return f"(Array.make {size} {default_val})"
        left = self._expr_to_whyml(expr["left"], local_refs, invariant_ctx, subst)
        right = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
        op = op_translate(raw_op)
        # In body context, coerce string literals in comparisons to int
        if not self._in_spec and op in ("=", "<>"):
            left = self._coerce_str_arg(left)
            right = self._coerce_str_arg(right)
        if op == "div":
            return f"(div {left} {right})" if self._in_spec else f"(pycsl_div {left} {right})"
        if op == "mod":
            return f"(mod {left} {right})" if self._in_spec else f"(pycsl_mod {left} {right})"
        if op in ("&&", "||"):
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
        if raw_op in self._BITWISE_FN_NAMES:
            return self._emit_bitwise_or_power(raw_op, expr, left, right)
        if raw_op == "?":
            self._add_abstract_op("val unknown_op (x: int) (y: int) : int")
            return f"(unknown_op {left} {right})"
        return f"({left} {op} {right})"

    def _handle_len_call(self, expr: Dict[str, Any], args: List[str]) -> str:
        """Handle len(x): constant fold literals, array length in hoare model, or abstract."""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        atype = arg_ir.get("type", "")
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
            if vname in known:
                return str(known[vname])
        if self.memory_model in ("hoare", "concurrent"):
            var_name = arg_ir.get("name", "") if atype == "Var" else ""
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict and var_name:
                if getattr(self, "_current_symbol_table", {}).get(var_name) in ("list", "dict"):
                    is_array = True
            if is_array:
                return f"(Array.length {args[0]})"
            self._add_abstract_op("val iter_length (x: int) : int")
            return f"(iter_length {args[0]})"
        return f"{args[0].lstrip('!')}_len"

    def _handle_join_call(self, expr: Dict[str, Any], args: List[str]) -> str:
        """Handle str.join(iterable): pick join_array for arrays, join_1 otherwise."""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
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
            self._add_abstract_op("val join_array (a: array int) : int")
            return f"(join_array {args[0]})"
        self._add_abstract_op("val join_1 (x: int) : int")
        return f"(join_1 {args[0]})"

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

    def _handle_dotted_call(self, func_name: str, args: List[str]) -> str:
        """Handle dotted method calls (x.method(...)): emit abstract val declaration."""
        safe_name = whyml_ident(func_name.replace(".", "_"))
        n = len(args)
        arity_name = f"{safe_name}_{n}"
        # When the call is `self.<method>(...)` on a method defined in the
        # same module, look up the real declared return type AND parameter
        # types so the abstract val matches the actual signature. Without
        # this, every `self.foo(...)` is abstracted as `val ... (xi: int)
        # ... : int`, mismatching downstream consumers when `<method>`
        # actually takes/returns array or map types.
        ret_type = "int"
        param_types: List[str] = []
        if func_name.startswith("self."):
            # Method IR names are stored as "<class_lower>__<method>"
            # (Module5._build_function_ir), so a `self._emit_contracts` call
            # site has to be prefixed with the current class's lowercased
            # name to hit the lookup.
            method_tail = func_name[len("self."):]
            cls = self._current_self_type
            lookup_key = f"{cls}__{method_tail}" if cls else method_tail
            ret_type = self._module_method_return_types.get(lookup_key, "int")
            param_types = self._module_method_param_types.get(lookup_key, [])
        # Pad / truncate param_types to match n (the abstract val arity
        # only sees the caller's actual arg count, not the IR's symbol
        # table size).
        while len(param_types) < n:
            param_types.append("int")
        param_types = param_types[:n]
        # Coerce each arg based on its declared param type. The caller's
        # arg may be int while the param expects array or map (e.g. when
        # the int came from an abstract `get_*` accessor returning int
        # but the receiver method declares the slot as `Set[T]`).
        coerced: List[str] = []
        for arg, ptype in zip(args, param_types):
            if ptype == "int":
                coerced.append(self._coerce_to_int(arg))
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
            else:
                coerced.append(arg)
        if n == 0:
            self._add_abstract_op(f"val {arity_name} () : {ret_type}")
            return f"({arity_name} ())"
        params = " ".join(f"(x{i}: {ptype})" for i, ptype in enumerate(param_types))
        self._add_abstract_op(f"val {arity_name} {params} : {ret_type}")
        return f"({arity_name} {' '.join(coerced)})"

    def _handle_call_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        func_name = expr["func"]
        args = [self._expr_to_whyml(a, local_refs, invariant_ctx, subst) for a in expr["args"]]

        if func_name == "len" and len(args) == 1:
            return self._handle_len_call(expr, args)
        if func_name in ("min", "max") and len(args) == 2:
            fn = "MinMax.min" if func_name == "min" else "MinMax.max"
            return f"({fn} {args[0]} {args[1]})"
        if func_name == "isinstance" and len(args) == 2:
            type_arg = self._coerce_to_int(args[1])
            self_type = self._current_self_type
            if args[0] == "self" and self_type:
                op = f"isinstance_check_{self_type}"
                self._add_abstract_op(f"val {op} (x: {self_type}) (t: int) : bool")
            else:
                op = "isinstance_check"
                self._add_abstract_op("val isinstance_check (x: int) (t: int) : bool")
            return f"({op} {args[0]} {type_arg})"
        if func_name in ("set", "frozenset") and len(args) == 0:
            # Body set: same `map int (option int)` model as body dicts.
            # Sets store `Some 0` for "present" keys, `None` for absent.
            return "(const (None: option int))"
        if func_name == "sorted" and len(args) == 1:
            # Abstract `sorted` over an array — returns a permuted array.
            # We don't model the sortedness invariant here; callers that
            # need it should use `\is_sorted` in contracts.
            self._add_abstract_op(
                "val sorted_1 (a: array int) : array int")
            return f"(sorted_1 {self._array_coerce_arg(args[0])})"
        if func_name in ("any", "all") and len(args) == 1:
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
        if func_name == "list" and len(args) <= 1:
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
        if func_name == "join" and len(args) == 1:
            return self._handle_join_call(expr, args)
        if func_name in ("str", "repr", "int", "bool", "abs") and len(args) == 1:
            arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
            if arg_ir.get("type") == "Number" and func_name in ("int", "abs"):
                val = arg_ir.get("value")
                if isinstance(val, (int, float)):
                    return str(int(val) if func_name == "int" else abs(int(val)))
            if func_name == "int":
                return args[0]
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
        if "." in func_name:
            return self._handle_dotted_call(func_name, args)
        if func_name in self._record_types and len(args) == 0:
            rec_info = self._record_types[func_name]
            field_inits = "; ".join(
                f"{fn} = {rec_info['defaults'].get(fn, 0)}" for fn in rec_info["fields"]
            )
            return f"{{ {field_inits} }}"
        coerced_args = [self._coerce_to_int(a) for a in args]
        safe_fn = whyml_ident(func_name)
        if (func_name not in local_refs
                and func_name not in self._current_params
                and safe_fn not in self._module_func_names):
            n = len(coerced_args)
            arity_fn = f"{safe_fn}_{n}"
            if n == 0:
                self._add_abstract_op(f"val {arity_fn} () : int")
            else:
                self._add_abstract_op(
                    f"val {arity_fn} {' '.join(f'(x{i}: int)' for i in range(n))} : int")
            return f"({arity_fn} {' '.join(coerced_args) if coerced_args else '()'})"
        return f"({safe_fn} {' '.join(coerced_args) if coerced_args else '()'})"

    def _handle_subscript(self, expr: Dict[str, Any], local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        value = expr["value"]
        index = self._expr_to_whyml(expr["index"], local_refs, invariant_ctx, subst)
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
        if self.memory_model in ("hoare", "concurrent"):
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
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict and var_name:
                st = getattr(self, "_current_symbol_table", {})
                if st.get(var_name) == "list":
                    is_array = True
                elif st.get(var_name) in ("dict", "set", "frozenset"):
                    is_dict = True
            # `self.<field>[k]` where the field is set/dict-typed.
            if not is_array and not is_dict and value.get("type") in ("Attribute", "FieldGet"):
                ft = self._field_type_of(value)
                if ft in ("set", "dict", "frozenset"):
                    is_dict = True
            if is_array:
                return f"{value_str}[{index}]"
            elif is_dict:
                # Body dict subscript read: `d[k]` →
                # `match Map.get !d k with Some v -> v | None -> 0 end`.
                # For body-local dicts, `value_str` already includes the
                # `!` deref because `_handle_var_expr` treats them as
                # refs. For `self.<dict-field>` accesses, no deref is
                # needed (record-field access is direct).
                k = self._coerce_to_int(index)
                return f"(match Map.get {value_str} {k} with | Some v_ -> v_ | None -> 0 end)"
            else:
                self._add_abstract_op("val subscript_get (x: int) (i: int) : int")
                return f"(subscript_get {self._coerce_to_int(value_str)} {self._coerce_to_int(index)})"
        else:
            return f"(Map.get !{self._heap_var} ({value_str} + {index}))"

    def _handle_attribute_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                               invariant_ctx: bool, subst: Dict[str, str]) -> str:
        """Handle non-self attribute access: record field or abstract getter."""
        obj_ir = expr.get("object", {})
        attr = expr.get("attr", "unknown")
        if isinstance(obj_ir, str):
            return f"(get_{attr} {obj_ir})"
        if obj_ir.get("type") == "Var":
            var_name = obj_ir.get("name", "")
            if var_name in self._record_locals:
                return f"{whyml_ident(var_name)}.{attr}"
        obj_str = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
        self._add_abstract_op(f"val get_{attr} (x: int) : int")
        return f"(get_{attr} {obj_str})"

    def _handle_var_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                         subst: Optional[Dict[str, str]] = None) -> str:
        name = expr["name"]
        if subst and name in subst:
            name = subst[name]
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
        safe = whyml_ident(name)
        self._add_abstract_op(f"val constant {safe} : int")
        return safe

    def _handle_field_get_expr(self, expr: Dict[str, Any], invariant_ctx: bool) -> str:
        if invariant_ctx:
            return expr['field']
        obj = expr['object']
        field = expr['field']
        safe_field = whyml_ident(field)
        decl_fields = self._all_record_fields
        if field in decl_fields:
            return f"{obj}.{safe_field}"
        hash_field = hash(field) % 2147483647
        self_type = self._current_self_type
        if obj == "self" and self_type:
            name = f"getattr_{self_type}"
            self._add_abstract_op(f"val {name} (x: {self_type}) (f: int) : int")
        else:
            name = "getattr_2"
            self._add_abstract_op(f"val {name} (x: int) (f: int) : int")
            obj = self._coerce_to_int(obj)
        return f"({name} {obj} {hash_field})"

    def _handle_fstring_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                              invariant_ctx: bool, subst: Dict[str, str]) -> str:
        parts = expr.get("parts", [])
        if not parts:
            return "0"
        acc = self._coerce_str_arg(self._expr_to_whyml(parts[0], local_refs, invariant_ctx, subst))
        n_parts = len(parts)
        i_part = 1
        while i_part < n_parts:
            part = parts[i_part]
            p = self._coerce_str_arg(self._expr_to_whyml(part, local_refs, invariant_ctx, subst))
            self._add_abstract_op("val str_concat (x: int) (y: int) : int")
            acc = f"(str_concat {acc} {p})"
            i_part += 1
        return acc

    def _handle_unaryop_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        e = self._expr_to_whyml(expr["expr"], local_refs, invariant_ctx, subst)
        op = op_translate(expr["op"])
        if op == "+":
            return e
        if op == "not":
            e = self._to_bool(e, expr["expr"])
        return f"({op} {e})"

    def _handle_old_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        inner = expr["expr"]
        if self.memory_model not in ("hoare", "concurrent") and inner.get("type") == "Subscript":
            value = self._expr_to_whyml(inner["value"], local_refs, invariant_ctx, subst)
            index = self._expr_to_whyml(inner["index"], local_refs, invariant_ctx, subst)
            return f"(Map.get (old !{self._heap_var}) ({value} + {index}))"
        e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
        return f"(old {e})"

    def _handle_at_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        label = expr["label"]
        inner = expr["expr"]
        if label == "PRE":
            e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
            return f"(old {e})"
        if inner.get("type") == "Subscript" and self.memory_model not in ("hoare", "concurrent"):
            value = self._expr_to_whyml(inner["value"], local_refs, invariant_ctx, subst)
            index = self._expr_to_whyml(inner["index"], local_refs, invariant_ctx, subst)
            return f"(Map.get ({self._heap_var} at {label}) ({value} + {index}))"
        e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
        return f"({e} at {label})"

    def _handle_ifexpr_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        test = self._expr_to_whyml(expr["test"], local_refs, invariant_ctx, subst)
        test = self._to_bool(test, expr["test"])
        body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
        orelse = self._expr_to_whyml(expr["orelse"], local_refs, invariant_ctx, subst)
        body = self._coerce_to_int(body)
        orelse = self._coerce_to_int(orelse)
        return f"(if {test} then {body} else {orelse})"

    def _handle_named_expr_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        target = whyml_ident(expr["target"])
        v = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx, subst)
        if target in local_refs:
            return f"(begin {target} := {v}; !{target} end)"
        local_refs.add(target)
        return f"(let {target} = ref {v} in !{target})"

    def _handle_slice_access_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        arr = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx, subst)
        sl = expr["slice"]
        lo = self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst) if sl.get("lower") else "0"
        hi = self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst) if sl.get("upper") else f"(Array.length {arr})"
        self._add_abstract_op("val array_slice (a: array int) (lo: int) (hi: int) : array int")
        # If `arr` is an int expression (e.g. `str_conv s` for a string
        # parameter being sliced), coerce to a placeholder array so the
        # abstract val type-checks. Module6 has no model for string
        # slicing through `array_slice`; the slice is treated as opaque.
        arr = self._array_coerce_arg(arr)
        return f"(array_slice {arr} {lo} {hi})"

    def _handle_arraylen_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self.memory_model in ("hoare", "concurrent"):
            var = expr['var']
            deref = "!" if var in local_refs else ""
            return f"(Array.length {deref}{var})"
        return f"{expr['var']}_len"

    def _handle_valid_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        length = self._expr_to_whyml(expr["length"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"({length} >= 0 && {length} <= Array.length {base})"
        return f"(valid !{self._heap_var} {base} {length})"

    def _handle_separated_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self.memory_model in ("hoare", "concurrent"):
            return "true"
        b1 = expr["base1"]
        l1 = self._expr_to_whyml(expr["len1"], local_refs, invariant_ctx, subst)
        b2 = expr["base2"]
        l2 = self._expr_to_whyml(expr["len2"], local_refs, invariant_ctx, subst)
        return f"(separated {b1} {l1} {b2} {l2})"

    def _handle_length2d_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        rows = self._expr_to_whyml(expr["rows"], local_refs, invariant_ctx, subst)
        cols = self._expr_to_whyml(expr["cols"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"({base}.rows = {rows} && {base}.columns = {cols})"
        return "true"

    def _handle_valid2d_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        row = self._expr_to_whyml(expr["row"], local_refs, invariant_ctx, subst)
        col = self._expr_to_whyml(expr["col"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"(valid_index {base} {row} {col})"
        return "true"

    def _handle_issorted_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        lo = self._expr_to_whyml(expr["lo"], local_refs, invariant_ctx, subst)
        hi = self._expr_to_whyml(expr["hi"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"(forall _si : int. {lo} <= _si /\\ _si < {hi} - 1 -> {base}[_si] <= {base}[_si + 1])"
        return "true"

    def _handle_sum_node_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        lo = self._expr_to_whyml(expr["lo"], local_refs, invariant_ctx, subst)
        hi = self._expr_to_whyml(expr["hi"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"(pycsl_sum {base} {lo} {hi})"
        return "0"

    def _handle_lambda_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        params = expr.get("params", [])
        body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
        param_str = " ".join(f"({whyml_ident(p)}: int)" for p in params) if params else "()"
        return f"(fun {param_str} -> {body})"

    def _handle_setlit_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        elts = expr.get("elts", [])
        # Empty set literal: `map int (option int)` initialised to None.
        if not elts:
            return "(const (None: option int))"
        # Non-empty set literal `{a, b, c}`: chain map_update_some on an
        # empty base. Each element is marked present with value 0.
        # `Map.set` directly would be a logic-function call rejected as
        # ghost; the program-val wrapper sidesteps that.
        self._add_abstract_op(
            "val map_update_some (m: map int (option int)) (k: int) (v: int) "
            ": map int (option int)\n"
            "    ensures { result = Map.set m k (Some v) }")
        result = "(const (None: option int))"
        for elt in elts:
            elt_w = self._coerce_to_int(self._expr_to_whyml(
                elt, local_refs, invariant_ctx, subst))
            result = f"(map_update_some {result} {elt_w} 0)"
        return result

    # --- Ghost expression handlers ---

    def _e(self, ir: Dict, lr: Set[str]) -> str:
        """Shorthand for _expr_to_whyml within ghost handlers."""
        return self._expr_to_whyml(ir, lr)

    def _handle_mktuple_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        parts = ", ".join(self._e(e, lr) for e in expr.get("elts", []))
        return f"({parts})"

    def _handle_fst_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(expr["tuple"], lr)
        safe_t = t.lstrip("!")
        return f"(let (x_, _) = !{safe_t} in x_)" if t.startswith("!") else f"(let (x_, _) = {t} in x_)"

    def _handle_snd_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(expr["tuple"], lr)
        safe_t = t.lstrip("!")
        return f"(let (_, y_) = !{safe_t} in y_)" if t.startswith("!") else f"(let (_, y_) = {t} in y_)"

    def _handle_proj_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(expr["tuple"], lr)
        idx = int(expr.get("index", 0))
        # Infer arity from ghost_tuple_vars; fall back to idx+1 (minimum valid)
        var_name = expr.get("tuple", {}).get("name", "") if isinstance(expr.get("tuple"), dict) else ""
        arity = self._ghost_tuple_vars.get(var_name, max(2, idx + 1))
        slots = ["_"] * arity
        if idx < arity:
            slots[idx] = "z_"
        pattern = ", ".join(slots)
        t_deref = f"!{t.lstrip('!')}" if t.startswith("!") else t
        return f"(let ({pattern}) = {t_deref} in z_)"

    def _handle_strconcat_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._expr_to_whyml_string_ctx(expr["left"], lr)
        r = self._expr_to_whyml_string_ctx(expr["right"], lr)
        # Why3 string.String exports 'concat' (not '^' or 'String.(^)')
        return f"(concat {l} {r})"

    def _handle_str_length_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._expr_to_whyml_string_ctx(expr["string"], lr)
        return f"(String.length {s})"

    def _handle_str_sub_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._expr_to_whyml_string_ctx(expr["string"], lr)
        lo = self._e(expr["lo"], lr)
        hi = self._e(expr["hi"], lr)
        return f"(String.substring {s} {lo} ({hi} - {lo}))"

    def _handle_ghost_copy_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        return f"(Array.copy {expr['arr']})"

    def _handle_ghost_copy_range_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        lo = self._e(expr["lo"], lr)
        hi = self._e(expr["hi"], lr)
        return f"(Array.sub {expr['arr']} {lo} ({hi} - {lo}))"

    def _handle_ghost_make_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        n = self._e(expr["size"], lr)
        v = self._e(expr["default"], lr)
        return f"(Array.make {n} {v})"

    def _handle_map_empty_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        # option-type design: absent keys map to None
        return "(const (None: option int))"

    def _handle_map_get_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        d = self._e(expr["dict"], lr)
        k = self._e(expr["key"], lr)
        d_r = f"!{d.lstrip('!')}" if d.startswith("!") else d
        return f"(match Map.get {d_r} {k} with | Some v_ -> v_ | None -> 0 end)"

    def _handle_map_set_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        d = self._e(expr["dict"], lr)
        k = self._e(expr["key"], lr)
        v = self._e(expr["value"], lr)
        d_r = f"!{d.lstrip('!')}" if d.startswith("!") else d
        return f"(Map.set {d_r} {k} (Some {v}))"

    def _handle_map_eq_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        r_r = f"!{r.lstrip('!')}" if r.startswith("!") else r
        # Why3 forall uses '.' as body separator, not ','
        return f"(forall k_: int. Map.get {l_r} k_ = Map.get {r_r} k_)"

    def _handle_has_key_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        # option-type design: key is present iff its value is Some (not None)
        d = self._e(expr["dict"], lr)
        k = self._e(expr["key"], lr)
        d_r = f"!{d.lstrip('!')}" if d.startswith("!") else d
        return f"(Map.get {d_r} {k} <> None)"

    def _handle_map_remove_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        d = self._e(expr["dict"], lr)
        k = self._e(expr["key"], lr)
        d_r = f"!{d.lstrip('!')}" if d.startswith("!") else d
        return f"(Map.set {d_r} {k} None)"

    def _handle_set_empty_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        # Why3: map.Const exports 'const', not 'Map.const'
        return "(const false)"

    def _handle_set_add_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._e(expr["set"], lr)
        e = self._e(expr["elem"], lr)
        s_r = f"!{s.lstrip('!')}" if s.startswith("!") else s
        return f"(Map.set {s_r} {e} true)"

    def _handle_set_remove_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._e(expr["set"], lr)
        e = self._e(expr["elem"], lr)
        s_r = f"!{s.lstrip('!')}" if s.startswith("!") else s
        return f"(Map.set {s_r} {e} false)"

    def _handle_set_mem_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        e = self._e(expr["elem"], lr)
        s_ir = expr["set"]
        s_t = s_ir.get("type", "") if isinstance(s_ir, dict) else ""
        if s_t in ("SetUnion", "SetInter", "SetDiff"):
            # Functional set (lambda int -> bool) — use direct application, not Map.get
            s = self._e(s_ir, lr)
            return f"({s} {e})"
        s = self._e(s_ir, lr)
        s_r = f"!{s.lstrip('!')}" if s.startswith("!") else s
        return f"(Map.get {s_r} {e})"

    def _handle_set_union_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        r_r = f"!{r.lstrip('!')}" if r.startswith("!") else r
        v = "_k_su"
        # Use parenthesised parameter for validity in both program and spec contexts
        return f"(fun ({v}: int) -> (Map.get {l_r} {v}) || (Map.get {r_r} {v}))"

    def _handle_set_inter_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        r_r = f"!{r.lstrip('!')}" if r.startswith("!") else r
        v = "_k_si"
        return f"(fun ({v}: int) -> (Map.get {l_r} {v}) && (Map.get {r_r} {v}))"

    def _handle_set_diff_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        r_r = f"!{r.lstrip('!')}" if r.startswith("!") else r
        v = "_k_sd"
        return f"(fun ({v}: int) -> (Map.get {l_r} {v}) && not (Map.get {r_r} {v}))"

    def _handle_set_card_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._e(expr["set"], lr)
        lo = self._e(expr["lo"], lr)
        hi = self._e(expr["hi"], lr)
        s_r = f"!{s.lstrip('!')}" if s.startswith("!") else s
        return f"(set_card {s_r} {lo} {hi})"

    def _handle_set_subset_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        r_r = f"!{r.lstrip('!')}" if r.startswith("!") else r
        v = "_k_ss"
        return f"(forall {v}: int, Map.get {l_r} {v} -> Map.get {r_r} {v})"

    def _handle_set_eq_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        r_r = f"!{r.lstrip('!')}" if r.startswith("!") else r
        v = "_k_se"
        # Why3 forall uses '.' as body separator, not ','
        return f"(forall {v}: int. Map.get {l_r} {v} = Map.get {r_r} {v})"

    def _handle_nil_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        return "Nil"

    def _handle_cons_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        h = self._e(expr["head"], lr)
        t = self._e(expr["tail"], lr)
        t_r = f"!{t.lstrip('!')}" if t.startswith("!") else t
        return f"(Cons {h} {t_r})"

    def _handle_hd_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["list"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        return f"(match {l_r} with | Cons h_ _ -> h_ | Nil -> absurd end)"

    def _handle_tl_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["list"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        return f"(match {l_r} with | Cons _ t_ -> t_ | Nil -> absurd end)"

    def _handle_list_length_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["list"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        # Why3 list.Length theory exports 'length', not 'List.length'
        return f"(length {l_r})"

    def _handle_nth_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["list"], lr)
        i = self._e(expr["index"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        # Why3 list.NthNoOpt exports 'nth: int -> list 'a -> 'a' (partial, axioms nth_cons_0/nth_cons_n)
        return f"(nth {i} {l_r})"

    def _handle_mem_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        e = self._e(expr["elem"], lr)
        l = self._e(expr["list"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        # Why3 list.Mem exports 'mem', not 'List.mem'
        return f"(mem {e} {l_r})"

    def _handle_append_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = f"!{l.lstrip('!')}" if l.startswith("!") else l
        r_r = f"!{r.lstrip('!')}" if r.startswith("!") else r
        # Why3 list.Append exports '(++)', not 'List.(++)'
        return f"({l_r} ++ {r_r})"

    def _expr_to_whyml(self, expr: Dict[str, Any], local_refs: Set[str],
                       invariant_ctx: bool = False,
                       subst: Optional[Dict[str, str]] = None) -> str:
        """Recursively translates an expression dictionary into a WhyML string.
        When invariant_ctx is True, FieldGet emits bare field names (for record invariants).
        subst: optional name substitution dict applied before local_refs lookup (e.g. for-loop vars)."""
        if not expr: return ""
        t = expr["type"]

        # Simple literals and trivial 1-3-line branches — kept inline
        if t == "Number": return str(int(expr["value"]))
        if t == "String":
            escaped = expr["value"].replace('\\', '\\\\').replace('"', '\\"')
            return str(hash(f'"{escaped}"') % 2147483647)
        if t == "Result":   return "result"
        if t == "None":     return "0"
        if t == "ArrayLit": return "(Array.make 1024 0)"
        if t == "UnknownPyExpr": return "0"
        if t == "Slice":    return "0"
        if t == "OldField": return f"(old {expr['object']}.{expr['field']})"
        if t == "Starred":  return self._expr_to_whyml(expr.get("value", {}), local_refs, invariant_ctx, subst)
        if t == "Bool":
            if self._in_spec: return "true" if expr.get("value") else "false"
            return "1" if expr.get("value") else "0"
        if t == "Tuple":
            elts = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst) for e in expr.get("elts", [])]
            return f"({', '.join(elts)})"
        if t == "Forall":
            return f"(forall {expr['var']} : int. {self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)})"
        if t == "Exists":
            return f"(exists {expr['var']} : int. {self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)})"
        if t == "DictLit":
            # Body dict literal: empty `map int (option int)`. Non-empty
            # dict literals would need element-by-element `Map.set` but
            # are currently uncommon enough to fall through to empty.
            # TODO: handle `{k1: v1, k2: v2}` by chaining Map.set.
            return "(const (None: option int))"
        if t == "ListComp":
            self._add_abstract_op("val list_comp (x: int) : int")
            return "(list_comp 0)"
        if t == "SetComp":
            self._add_abstract_op("val set_comp (x: int) : int")
            return "(set_comp 0)"
        if t == "DictComp":
            self._add_abstract_op("val dict_comp (x: int) : int")
            return "(dict_comp 0)"

        # Non-standard-signature handlers — called explicitly
        if t == "Var":      return self._handle_var_expr(expr, local_refs, subst)
        if t == "FieldGet": return self._handle_field_get_expr(expr, invariant_ctx)

        # All other types via uniform-quad-signature dispatch
        handler = self._EXPR_DISPATCH.get(t)
        if handler:
            return getattr(self, handler)(expr, local_refs, invariant_ctx, subst)
        return ""

    def _track_collection_metadata(self, target: str, val_ir: Dict[str, Any]) -> None:
        """Update _known_collection_sizes/_elements for constant-folding of len/sum/index."""
        vt = val_ir.get("type", "")
        if vt in ("ArrayLit", "Tuple"):
            elts = val_ir.get("elts", [])
            self._known_collection_sizes[target] = len(elts)
            elem_map = {i: str(int(e["value"])) for i, e in enumerate(elts)
                        if e.get("type") == "Number" and isinstance(e.get("value"), (int, float))}
            if elem_map:
                self._known_collection_elements[target] = elem_map
        elif vt == "String" and isinstance(val_ir.get("value"), str):
            self._known_collection_sizes[target] = len(val_ir["value"])
        elif vt == "DictLit":
            keys = val_ir.get("keys", [])
            self._known_collection_sizes[target] = len(keys)
            elem_map = {}
            for k, v in zip(keys, val_ir.get("values", [])):
                if (k.get("type") == "Number" and isinstance(k.get("value"), (int, float)) and
                        v.get("type") == "Number" and isinstance(v.get("value"), (int, float))):
                    elem_map[int(k["value"])] = str(int(v["value"]))
            if elem_map:
                self._known_collection_elements[target] = elem_map
        elif vt == "SetLit":
            elts = val_ir.get("elts", [])
            unique_vals = {int(e["value"]) if (e.get("type") == "Number" and
                           isinstance(e.get("value"), (int, float))) else id(e)
                           for e in elts}
            self._known_collection_sizes[target] = len(unique_vals)

    _BOOL_BINOPS = frozenset({
        "==", "!=", "<", "<=", ">", ">=", "is", "is not", "in", "not in",
    })

    @staticmethod
    def _val_is_bool(val_ir: Dict[str, Any]) -> bool:
        """RHS expression is bool-typed in Python — needs `if … then 1 else 0`
        when stored into a WhyML `int` slot."""
        vt = val_ir.get("type", "")
        if vt in ("Compare", "BoolOp"):
            return True
        if vt == "UnaryOp" and val_ir.get("op") == "not":
            return True
        if vt == "BinOp" and val_ir.get("op") in Module6_WhyMLTranspiler._BOOL_BINOPS:
            return True
        return False

    def _first_assign_kind(self, val: str, val_ir: Dict[str, Any]) -> str:
        """Classify a first-declaration RHS into one of: record, lambda,
        array, slice, dict, bounded_int, default. Drives the `let X = …`
        shape selection in `_handle_assign_stmt`."""
        vt = val_ir.get("type", "")
        if vt == "Call" and val_ir.get("func", "") in self._record_types:
            return "record"
        if vt == "Lambda":
            return "lambda"
        if vt == "SliceAccess":
            return "slice"
        if (val.startswith("(Array.make") or val == "(Array.make 1024 0)"
                or val.startswith("(sorted_1 ")):
            return "array"
        if vt == "Call" and val_ir.get("func", "").startswith("self."):
            method_tail = val_ir["func"][len("self."):]
            cls = self._current_self_type
            lookup = f"{cls}__{method_tail}" if cls else method_tail
            if self._module_method_return_types.get(lookup) == "array int":
                return "array"
        # Body dict/set: recognise both legacy abstract-val emission and
        # the new `map.Map (option int)` form, plus IR-level signals so
        # detection doesn't depend on val-string shape.
        if (val.startswith("(dict_new")
                or val.startswith("(const (None: option int)")
                or val.startswith("(map_update_some ")
                or val.startswith("(map_update_none ")
                or vt in ("DictLit", "SetLit")
                or (vt == "Call" and val_ir.get("func") in ("dict", "set", "frozenset"))):
            return "dict"
        # RHS is (or contains) a Var bound to a set/dict-typed parameter.
        # Detect the bare Var case and the IfExpr/BinOp wrappers whose
        # leaves yield map-typed values (e.g. `inner_held = held | {x}
        # if mutex else held`).
        if self._rhs_yields_map(val_ir):
            return "dict"
        if self._bounded_int:
            return "bounded_int"
        return "default"

    def _rhs_yields_array(self, val_ir: Dict[str, Any]) -> bool:
        """Parallel of `_rhs_yields_map` for `array int`-typed RHS.
        True for list/tuple-typed param Vars, list-typed self-fields,
        and Calls to functions known to return `array int`."""
        if not isinstance(val_ir, dict):
            return False
        t = val_ir.get("type", "")
        if t == "Var":
            name = val_ir.get("name", "")
            if name in self._array_locals or name in self._current_array1d_params:
                return True
            if self._current_symbol_table.get(name) in ("list", "tuple"):
                return True
            return False
        if t in ("Attribute", "FieldGet"):
            return self._field_type_of(val_ir) in ("list", "tuple")
        if t == "Call":
            fn = val_ir.get("func", "")
            if fn.startswith("self."):
                tail = fn[len("self."):]
                cls = self._current_self_type
                key = f"{cls}__{tail}" if cls else tail
            else:
                key = fn
            return self._module_method_return_types.get(key) == "array int"
        return False

    def _rhs_yields_map(self, val_ir: Dict[str, Any]) -> bool:
        """Heuristic: does this RHS IR yield a `map int (option int)`
        value? True for set/dict-typed param Vars, IfExpr branches that
        do, BinOp `|`/`&` between map-typed sides (Python set ops),
        Subscript-read on a dict-typed self-field, or a Call to a
        function declared `-> Set[T]` / `-> Dict[K, V]` (looked up via
        the module-level return-type map)."""
        if not isinstance(val_ir, dict):
            return False
        t = val_ir.get("type", "")
        if t == "Var":
            name = val_ir.get("name", "")
            if name in self._dict_locals:
                return True
            if self._current_symbol_table.get(name) in ("set", "dict", "frozenset"):
                return True
            return False
        if t in ("Attribute", "FieldGet"):
            return self._field_type_of(val_ir) in ("set", "dict", "frozenset")
        if t == "Call":
            fn = val_ir.get("func", "")
            # `self.<method>(...)` — apply class-prefix mangling.
            if fn.startswith("self."):
                tail = fn[len("self."):]
                cls = self._current_self_type
                key = f"{cls}__{tail}" if cls else tail
            else:
                key = fn
            return self._module_method_return_types.get(key) == "map int (option int)"
        if t == "IfExpr":
            return (self._rhs_yields_map(val_ir.get("body", {}))
                    or self._rhs_yields_map(val_ir.get("orelse", {})))
        if t == "BinOp" and val_ir.get("op") in ("|", "&", "^", "-"):
            # Python set union/intersection/xor/difference syntax. If
            # either operand is map-typed, the result is too.
            return (self._rhs_yields_map(val_ir.get("left", {}))
                    or self._rhs_yields_map(val_ir.get("right", {})))
        return False

    def _emit_first_assign(self, kind: str, indent: str, safe_target: str, target: str,
                           val: str, val_ir: Dict[str, Any]) -> str:
        """Emit the `let X = …` line for a first declaration of `target`,
        updating the locals-tracking sets as a side effect."""
        if kind == "record":
            self._record_locals.add(target)
            return f"{indent}let {safe_target} = {val} in\n"
        if kind == "lambda":
            self._lambda_locals.add(target)
            return f"{indent}let {safe_target} = {val} in\n"
        if kind in ("array", "slice"):
            self._array_locals.add(target)
            return f"{indent}let {safe_target} = {val} in\n"
        if kind == "dict":
            self._dict_locals.add(target)
            return f"{indent}let {safe_target} = ref {val} in\n"
        if kind == "bounded_int":
            return f"{indent}let {safe_target} = ref ({val} : int{self._bounded_int}) in\n"
        if self._val_is_bool(val_ir):
            val = f"(if {val} then 1 else 0)"
        return f"{indent}let {safe_target} = ref {val} in\n"

    def _emit_array_local_reassign(self, target: str, safe_target: str, indent: str,
                                    val_ir: Dict[str, Any], local_refs: Set[str]) -> str:
        """Reassigning an array-local (declared via `let arr = (Array.make
        1024 0) in`, NOT a ref) — emitting `arr := val` is invalid because
        `arr` isn't a `ref`. Model the reassignment as "reset the length
        counter, then append each new element" so subsequent appends fill
        from index 0. Only handles literal RHS shapes; other shapes
        (method calls etc.) fall through to a no-op (soundness depends on
        the caller treating the array as opaque after this point —
        typically handled by `\\trusted` upstream)."""
        len_name = f"{safe_target}_len"
        if val_ir.get("type") != "ArrayLit":
            return f"{indent}()"
        parts: List[str] = [f"{indent}{len_name} := 0"]
        for elt in val_ir.get("elts", []):
            elt_str = self._expr_to_whyml(elt, local_refs)
            parts.append(
                f"{indent}{safe_target}[!{len_name}] <- {self._coerce_to_int(elt_str)}")
            parts.append(f"{indent}{len_name} := !{len_name} + 1")
        return ";\n".join(parts)

    def _handle_assign_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                             local_refs: Set[str], declared_refs: Set[str],
                             indent: str, in_loop: bool) -> str:
        target = stmt["target"]
        safe_target = whyml_ident(target)
        val_ir = stmt.get("value", {})
        vt = val_ir.get("type", "")
        self._track_collection_metadata(target, val_ir)

        val = self._expr_to_whyml(stmt["value"], local_refs)
        # Tuple/Set literals can't be stored in int refs; use 0 as placeholder
        if vt in ("Tuple", "SetLit"):
            val = "0"

        # Assignment to a module-level shared variable (always a ref, never re-declared)
        if target in self._shared_var_names:
            code = f"{indent}{whyml_ident(target)} := {val}"
            if rest:
                code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            return code

        if target not in declared_refs:
            declared_refs.add(target)
            kind = self._first_assign_kind(val, val_ir)
            code = self._emit_first_assign(kind, indent, safe_target, target, val, val_ir)
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if not rest_code:
                rest_code = f"{indent}()"
            return code + rest_code

        if target in self._array_locals:
            code = self._emit_array_local_reassign(
                target, safe_target, indent, val_ir, local_refs)
            if rest:
                code += ";\n" + self._stmts_to_whyml(
                    rest, local_refs, declared_refs, indent, in_loop)
            return code
        if self._val_is_bool(val_ir):
            val = f"(if {val} then 1 else 0)"
        code = f"{indent}{safe_target} := {val}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_while_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                            local_refs: Set[str], declared_refs: Set[str],
                            indent: str, in_loop: bool) -> str:
        test = self._expr_to_whyml(stmt["test"], local_refs)
        test = self._to_bool(test, stmt["test"])
        has_cont = IRScanner.has_continue(stmt.get("body", []))
        has_direct_ret = IRScanner.has_direct_return(stmt.get("body", []))

        loop_indent = (indent + "  ") if has_direct_ret else indent
        inner_indent = loop_indent + "  "

        body_str = self._stmts_to_whyml(
            stmt["body"], local_refs, declared_refs.copy(), inner_indent, in_loop=True)

        loop_code = f"{loop_indent}while {test} do\n"
        self._in_spec = True
        invariants_w = stmt.get("invariants", [])
        n_inv_w = len(invariants_w)
        i_inv_w = 0
        while i_inv_w < n_inv_w:
            inv = invariants_w[i_inv_w]
            inv_str = self._expr_to_whyml(inv, local_refs)
            loop_code += f"{inner_indent}invariant {{ {inv_str} }}\n"
            i_inv_w += 1
        variants_w = stmt.get("variants", [])
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

        has_break = IRScanner.uses_break(stmt.get("body", []))
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

    #@ requires 1 == 1
    #@ ensures \result[2] == 0 or \result[2] == 1
    #@ assigns self._abstract_ops
    def _classify_iterable(self, iter_ir: Dict[str, Any],
                            local_refs: Set[str], idx: str) -> Tuple[str, str, bool]:
        """Classify a For loop's iterable. Returns (len_expr, elem_expr, is_range).
        Side-effect: sets self._for_idx_init to the initial counter value
        (default "0"; for `range(start, stop)`, the `start` expression).
        """
        self._for_idx_init = "0"
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
        if iter_ir.get("type") == "Var" and self.memory_model in ("hoare", "concurrent"):
            var_name = iter_ir.get("name", "")
            iter_expr = self._expr_to_whyml(iter_ir, local_refs)
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_current_array1d_params", set()))
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
                and self.memory_model in ("hoare", "concurrent")):
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
        if self.memory_model not in ("hoare", "concurrent"):
            iter_expr = self._expr_to_whyml(iter_ir, local_refs)
            return f"{iter_expr}_len", f"Map.get !{self._heap_var} ({iter_expr} + !{idx})", False
        iter_expr = self._coerce_to_int(self._expr_to_whyml(iter_ir, local_refs))
        self._add_abstract_op("val iter_length (x: int) : int")
        self._add_abstract_op("val iter_get (x: int) (i: int) : int")
        return f"(iter_length {iter_expr})", f"(iter_get {iter_expr} !{idx})", False

    #@ requires 1 == 1
    #@ ensures self._havoc_counter >= \old(self._havoc_counter)
    #@ assigns self._in_spec, self._abstract_ops, self._havoc_counter
    def _handle_for_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                          local_refs: Set[str], declared_refs: Set[str],
                          indent: str, in_loop: bool) -> str:
        target = stmt["target"]
        safe_target = whyml_ident(target)
        iter_ir = stmt["iter"]
        idx = f"_idx_{safe_target}"
        has_direct_ret = IRScanner.has_direct_return(stmt.get("body", []))
        loop_indent = (indent + "  ") if has_direct_ret else indent
        inner_indent = loop_indent + "  "

        body_local = local_refs | {target}
        body_declared = declared_refs.copy() | {target}
        inner_body = self._stmts_to_whyml(
            stmt.get("body", []), body_local, body_declared, inner_indent, True)
        if not inner_body:
            inner_body = f"{inner_indent}()"

        has_cont = IRScanner.has_continue(stmt.get("body", []))
        len_expr, elem_expr, is_range = self._classify_iterable(iter_ir, local_refs, idx)

        while_parts = [f"{loop_indent}while !{idx} < {len_expr} do"]
        inv_subst = {target: idx} if is_range else None
        inv_refs = local_refs | {idx}
        self._in_spec = True
        invariants_f = stmt.get("invariants", [])
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
        variants_f = stmt.get("variants", [])
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

        if has_cont:
            while_parts.append(f"{inner_indent}try")
            while_parts.append(f"{inner_indent}  let {safe_target} = ref ({elem_expr}) in")
            while_parts.append(inner_body)
            while_parts.append(f"{inner_indent}with PyCSL_Continue -> () end;")
        else:
            while_parts.append(f"{inner_indent}let {safe_target} = ref ({elem_expr}) in")
            while_parts.append(inner_body + ";")

        while_parts.append(f"{inner_indent}{idx} := !{idx} + 1")
        while_parts.append(f"{loop_indent}done")
        has_break = IRScanner.uses_break(stmt.get("body", []))
        while_code = "\n".join(while_parts)

        if has_break:
            while_code = (f"{loop_indent}try\n{while_code}\n"
                          f"{loop_indent}with PyCSL_Break -> () end")

        idx_init = self._for_idx_init
        if self._bounded_int:
            idx_decl = f"{loop_indent}let {idx} = ref ({idx_init} : int{self._bounded_int}) in\n{while_code}"
        else:
            idx_decl = f"{loop_indent}let {idx} = ref {idx_init} in\n{while_code}"

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

    def _handle_try_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                          local_refs: Set[str], declared_refs: Set[str],
                          indent: str, in_loop: bool) -> str:
        body_stmts = stmt.get("body", [])
        handlers = stmt.get("handlers", [])
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
        while i_sa < n_sa:
            var = sorted_assigned[i_sa]
            safe_var = whyml_ident(var)
            if safe_var not in declared_refs:
                pre_decls += f"{indent}let {safe_var} = ref 0 in\n"
                declared_refs.add(safe_var)
            i_sa += 1
        body_str = self._stmts_to_whyml(body_stmts, local_refs, declared_refs.copy(), indent + "  ", in_loop)
        if not body_str:
            body_str = f"{indent}  ()"
        if handlers:
            code = f"{pre_decls}{indent}try\n{body_str}\n"
            n_h = len(handlers)
            i_h = 0
            first_handler = True
            # Why3 requires `try BODY with Exc1 -> h1 | Exc2 -> h2 end` —
            # only the first handler uses `with`, subsequent handlers
            # (and additional alternatives within a `|`-separated
            # exc_type) use `|`. Emitting separate `with` clauses for
            # each handler produces a syntax error.
            while i_h < n_h:
                h = handlers[i_h]
                exc = h.get("exc_type") or "PyCSL_Exception"
                exc_parts = exc.split("|") if "|" in exc else [exc]
                n_ep = len(exc_parts)
                i_ep = 0
                while i_ep < n_ep:
                    ep = exc_parts[i_ep].strip()
                    handler_body = self._stmts_to_whyml(
                        h.get("body", []), local_refs, declared_refs.copy(), indent + "  ", in_loop)
                    if not handler_body:
                        handler_body = f"{indent}  ()"
                    connector = "with" if first_handler else "|"
                    code += f"{indent}{connector} {ep} -> \n{handler_body}\n"
                    first_handler = False
                    i_ep += 1
                i_h += 1
            code += f"{indent}end"
        else:
            code = f"{pre_decls}{body_str}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _resolve_effective_ghost_type(self, target: str, op: str, ghost_type: str) -> str:
        """Infer ghost type for augmented-assign from tracked declaration sets.

        Augmented-assign IR nodes carry ghost_type='int' (the grammar default)
        because the transformer does not propagate declared_type.  Override from
        the sets that are populated when the declaration was first seen.
        """
        if ghost_type == "int" and op != "=":
            if target in self._ghost_list_vars:
                return "ghost_list"
            if target in self._ghost_set_vars:
                return "ghost_set"
            if target in self._ghost_dict_vars:
                return "ghost_dict"
            if target in self._ghost_tuple_vars:
                return f"tuple{self._ghost_tuple_vars[target]}"
            if target in self._ghost_string_vars:
                return "string"
        return ghost_type

    def _emit_new_ghost_ref(self, safe_target: str, target: str, binding: str,
                             rest: List[Dict[str, Any]], local_refs: Set[str],
                             declared_refs: Set[str], indent: str, in_loop: bool) -> str:
        """Emit `let ghost safe_target {binding} in rest` for a new ghost declaration."""
        declared_refs.add(target)
        local_refs.add(target)
        rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        if not rest_code:
            rest_code = f"{indent}()"
        return f"{indent}let ghost {safe_target} {binding} in\n{rest_code}"

    def _handle_ghost_assign_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        target = stmt["target"]
        safe_target = whyml_ident(target)
        op = stmt.get("op", "=")
        ghost_type = self._resolve_effective_ghost_type(target, op, stmt.get("ghost_type", "int"))
        is_new = target not in declared_refs

        if ghost_type == "string":
            self._ghost_string_vars.add(target)
            val = self._expr_to_whyml_string_ctx(stmt["value"], local_refs | {target})
            if is_new:
                return self._emit_new_ghost_ref(safe_target, target, f"= ref ({val})",
                                                rest, local_refs, declared_refs, indent, in_loop)
            code = f"{indent}ghost {safe_target} := {val}"
        elif ghost_type in ("tuple2", "tuple3", "tuple4"):
            self._ghost_tuple_vars[target] = int(ghost_type[-1])
            val = self._expr_to_whyml(stmt["value"], local_refs | {target})
            if is_new:
                return self._emit_new_ghost_ref(safe_target, target, f"= ref {val}",
                                                rest, local_refs, declared_refs, indent, in_loop)
            code = f"{indent}ghost {safe_target} := {val}"
        elif ghost_type == "array":
            self._ghost_array_vars.add(target)
            # Ghost arrays are direct array values (not refs); add to _array_locals
            # so subscript access in invariants emits arr[i] not subscript_get arr i
            self._array_locals.add(target)
            val = self._expr_to_whyml(stmt["value"], local_refs | {target})
            if is_new:
                return self._emit_new_ghost_ref(safe_target, target, f"= {val}",
                                                rest, local_refs, declared_refs, indent, in_loop)
            code = f"{indent}ghost {safe_target} <- {val}"
        elif ghost_type == "ghost_dict":
            self._ghost_dict_vars.add(target)
            if op == "+=" and not is_new:
                val_ir = stmt["value"]
                if val_ir.get("type") == "MkTuple" and len(val_ir.get("elts", [])) == 2:
                    k = self._e(val_ir["elts"][0], local_refs)
                    v = self._e(val_ir["elts"][1], local_refs)
                    code = f"{indent}ghost {safe_target} := (Map.set !{safe_target} {k} (Some {v}))"
                else:
                    val = self._expr_to_whyml(stmt["value"], local_refs | {target})
                    code = f"{indent}ghost {safe_target} := {val}"
            else:
                val = self._expr_to_whyml(stmt["value"], local_refs | {target})
                if is_new:
                    return self._emit_new_ghost_ref(safe_target, target, f"= ref {val}",
                                                    rest, local_refs, declared_refs, indent, in_loop)
                code = f"{indent}ghost {safe_target} := {val}"
        elif ghost_type == "ghost_list":
            self._ghost_list_vars.add(target)
            val = self._expr_to_whyml(stmt["value"], local_refs | {target})
            if is_new:
                # Annotate Nil with type to allow Why3 to infer list int for unused vars
                init_val = f"({val}: list int)" if val == "Nil" else val
                return self._emit_new_ghost_ref(safe_target, target, f"= ref {init_val}",
                                                rest, local_refs, declared_refs, indent, in_loop)
            if op == "+=":
                code = f"{indent}ghost {safe_target} := (Cons {val} !{safe_target})"
            else:
                code = f"{indent}ghost {safe_target} := {val}"
        elif ghost_type == "ghost_set":
            self._ghost_set_vars.add(target)
            val = self._expr_to_whyml(stmt["value"], local_refs | {target})
            if is_new:
                return self._emit_new_ghost_ref(safe_target, target, f"= ref {val}",
                                                rest, local_refs, declared_refs, indent, in_loop)
            if op == "+=":
                code = f"{indent}ghost {safe_target} := (Map.set !{safe_target} {val} true)"
            else:
                code = f"{indent}ghost {safe_target} := {val}"
        else:
            # Default: int ghost (existing behaviour)
            val = self._expr_to_whyml(stmt["value"], local_refs | {target})
            if is_new:
                if self._bounded_int:
                    binding = f"= ref ({val} : int{self._bounded_int})"
                else:
                    binding = f"= ref {val}"
                return self._emit_new_ghost_ref(safe_target, target, binding,
                                                rest, local_refs, declared_refs, indent, in_loop)
            if op == "=":
                code = f"{indent}ghost {safe_target} := {val}"
            elif op == "+=":
                code = f"{indent}ghost {safe_target} := !{safe_target} + {val}"
            elif op == "-=":
                code = f"{indent}ghost {safe_target} := !{safe_target} - {val}"
            elif op == "*=":
                code = f"{indent}ghost {safe_target} := !{safe_target} * {val}"
            else:
                code = f"{indent}ghost {safe_target} := {val}"

        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_ghost_array_set_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                      local_refs: Set[str], declared_refs: Set[str],
                                      indent: str, in_loop: bool) -> str:
        arr = whyml_ident(stmt["target"])
        idx = self._expr_to_whyml(stmt["index"], local_refs)
        val = self._expr_to_whyml(stmt["value"], local_refs)
        # Why3 array element assignment: a[i] <- v
        code = f"{indent}{arr}[{idx}] <- {val}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _expr_to_whyml_string_ctx(self, ir: Dict[str, Any], local_refs: Set[str]) -> str:
        """Emit a ghost string expression in string context (handles StrConcat, StringLiteral, ghost string vars)."""
        t = ir.get("type")
        if t == "StrConcat":
            l = self._expr_to_whyml_string_ctx(ir["left"], local_refs)
            r = self._expr_to_whyml_string_ctx(ir["right"], local_refs)
            return f"(String.(^) {l} {r})"
        if t == "String":
            raw = ir.get("value", "")
            return f'"{raw}"'
        if t == "Var":
            name = ir.get("name", "")
            safe = whyml_ident(name)
            if name in self._ghost_string_vars:
                return f"!{safe}"
            return safe
        # Fall back to generic emit for any other expression
        return self._expr_to_whyml(ir, local_refs)

    def _handle_tuple_unpack_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        targets = stmt["targets"]
        val_whyml = self._expr_to_whyml(stmt["value"], local_refs)
        safe_targets = [whyml_ident(t) for t in targets]
        val_ir = stmt.get("value", {})
        if val_ir.get("type") == "Call":
            func_name = val_ir.get("func", "")
            nargs = len(val_ir.get("args", []))
            safe_fn = whyml_ident(func_name)
            arity_fn = f"{safe_fn}_{nargs}"
            if arity_fn in self._abstract_ops:
                tuple_ret = "(" + ", ".join(["int"] * len(targets)) + ")"
                if nargs == 0:
                    self._abstract_ops[arity_fn] = f"val {arity_fn} () : {tuple_ret}"
                else:
                    params = " ".join(f"(x{i}: int)" for i in range(nargs))
                    self._abstract_ops[arity_fn] = f"val {arity_fn} {params} : {tuple_ret}"
        elif val_ir.get("type") == "Subscript":
            # `a, b = arr[i]` — the default `subscript_get` returns `int`,
            # which doesn't match the tuple pattern on the LHS. Emit a
            # dedicated `subscript_get_t<arity>` returning an N-tuple of
            # ints, and override the `val_whyml` to use it.
            n_targets = len(targets)
            sg_fn = f"subscript_get_t{n_targets}"
            tuple_ret = "(" + ", ".join(["int"] * n_targets) + ")"
            self._add_abstract_op(
                f"val {sg_fn} (x: int) (i: int) : {tuple_ret}")
            inner = self._expr_to_whyml(val_ir.get("value", {}), local_refs)
            idx = self._expr_to_whyml(val_ir.get("index", {}), local_refs)
            val_whyml = f"({sg_fn} {self._coerce_to_int(inner)} {self._coerce_to_int(idx)})"
        tmp_names = [f"_tu_{t}" for t in safe_targets]
        pattern = ", ".join(tmp_names)
        lines = [f"{indent}let ({pattern}) = {val_whyml} in"]
        n_tu = len(tmp_names)
        i_tu = 0
        while i_tu < n_tu:
            tmp = tmp_names[i_tu]
            st = safe_targets[i_tu]
            if st in local_refs:
                lines.append(f"{indent}{st} := {tmp};")
            else:
                local_refs.add(st)
                lines.append(f"{indent}let {st} = ref {tmp} in")
            i_tu += 1
        code = "\n".join(lines)
        if rest:
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            stripped = code.rstrip()
            # If the last line is `let ... in`, the rest is that `let`'s
            # body — no `;` separator (Why3 syntax). If the last line
            # already ends with `;` (e.g. `x := tmp;`), no additional `;`
            # is needed either — would produce a `;;` artifact. Only
            # statements ending in something else (rare here) need `;`.
            if stripped.endswith(" in") or stripped.endswith(";"):
                code += "\n" + rest_code
            else:
                code += ";\n" + rest_code
        return code

    def _field_type_for(self, obj: str, field: str) -> Optional[str]:
        """Resolve `<obj>.<field>` (both as raw strings, the IR shape
        used by `_handle_fieldset_stmt`) to the field's declared type
        tag, or None if the obj/field doesn't match a known record."""
        if obj != "self":
            return None
        cls = self._current_self_type
        if not cls:
            return None
        for info in self._record_types.values():
            if info.get("whyml_name") == cls:
                return info.get("field_types", {}).get(field)
        return None

    def _field_type_of(self, attr_ir: Dict[str, Any]) -> Optional[str]:
        """Resolve `self.<field>` to its declared IR type tag, or None if
        the target is not a self-field access. Accepts both shapes:
        `Attribute(value=Var(self), attr=F)` and `FieldGet(object='self',
        field=F)` (Module5 uses both for different contexts).

        Lookup goes through `_record_types`, keyed by class name; the
        whyml_name matches `_current_self_type` (lowercased)."""
        if attr_ir.get("type") == "Attribute":
            receiver = attr_ir.get("value", {})
            if not (receiver.get("type") == "Var" and receiver.get("name") == "self"):
                return None
            field_name = attr_ir.get("attr")
        elif attr_ir.get("type") == "FieldGet":
            if attr_ir.get("object") != "self":
                return None
            field_name = attr_ir.get("field")
        else:
            return None
        cls = self._current_self_type
        if not cls or not field_name:
            return None
        for info in self._record_types.values():
            if info.get("whyml_name") == cls:
                return info.get("field_types", {}).get(field_name)
        return None

    def _handle_array_set_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                local_refs: Set[str], declared_refs: Set[str],
                                indent: str, in_loop: bool) -> str:
        arr = stmt["array"]
        if arr.get("type") == "Var":
            var_name = arr.get("name", "")
            if var_name in getattr(self, "_dict_locals", set()):
                known_sizes = getattr(self, "_known_collection_sizes", {})
                if var_name in known_sizes:
                    known_sizes[var_name] = known_sizes[var_name] + 1
                else:
                    known_sizes[var_name] = 1
        if (arr.get("type") == "Subscript" and
                arr.get("value", {}).get("type") == "Var" and
                arr.get("value", {}).get("name") in getattr(self, "_array2d_params", set()) and
                arr.get("value", {}).get("name") not in getattr(self, "_dict_locals", set())):
            base = arr["value"]["name"]
            row_expr = self._expr_to_whyml(arr["index"], local_refs)
            col_expr = self._expr_to_whyml(stmt["index"], local_refs)
            val_expr = self._expr_to_whyml(stmt["value"], local_refs)
            code = f"{indent}set {base} {row_expr} {col_expr} {val_expr}"
        else:
            array_expr = self._expr_to_whyml(arr, local_refs)
            index_expr = self._expr_to_whyml(stmt["index"], local_refs)
            val_expr = self._expr_to_whyml(stmt["value"], local_refs)
            if self.memory_model in ("hoare", "concurrent"):
                var_name = arr.get("name", "") if arr.get("type") == "Var" else ""
                is_dict = var_name in getattr(self, "_dict_locals", set())
                is_array = not is_dict and (
                    var_name in getattr(self, "_array2d_params", set()) or
                    var_name in getattr(self, "_array_locals", set()) or
                    var_name in getattr(self, "_current_array1d_params", set()))
                if not is_array and not is_dict and var_name:
                    st = getattr(self, "_current_symbol_table", {})
                    if st.get(var_name) == "list":
                        is_array = True
                    elif st.get(var_name) in ("dict", "set", "frozenset"):
                        is_dict = True
                # `self.<field>[k] = v` where <field> is set/dict-typed.
                # Resolve via the record-type table; treat as a body-dict
                # write on the field reference. Module5 emits self-field
                # access as `FieldGet` in body context (alongside the
                # `Attribute` shape used elsewhere); accept both.
                self_field_name: Optional[str] = None
                arr_type = arr.get("type")
                if not is_array and not is_dict and arr_type in ("Attribute", "FieldGet"):
                    ft = self._field_type_of(arr)
                    if ft in ("set", "dict", "frozenset"):
                        is_dict = True
                        self_field_name = (arr.get("attr") if arr_type == "Attribute"
                                            else arr.get("field"))
                if is_array:
                    val_expr = self._coerce_to_int(val_expr)
                    code = f"{indent}{array_expr}[{index_expr}] <- {val_expr}"
                elif is_dict:
                    # Body dict subscript write: `d[k] = v`. `Map.set` is a
                    # pure logic function and Why3 refuses to assign its
                    # result back to a non-ghost ref ("ghost modification
                    # in non-ghost variable"). Wrap it in a program-level
                    # abstract val `map_update_some` whose contract is
                    # the equivalent `Map.set` semantics.
                    self._add_abstract_op(
                        "val map_update_some (m: map int (option int)) (k: int) (v: int) "
                        ": map int (option int)\n"
                        "    ensures { result = Map.set m k (Some v) }")
                    k = self._coerce_to_int(index_expr)
                    v = self._coerce_to_int(val_expr)
                    if self_field_name is not None:
                        # `self.<field>[k] = v` — record-field assignment.
                        # Why3 syntax: `self.field <- new_value`.
                        safe_field = whyml_ident(self_field_name)
                        code = (f"{indent}self.{safe_field} <- "
                                f"map_update_some self.{safe_field} {k} {v}")
                    else:
                        safe_name = whyml_ident(var_name) if var_name else array_expr.lstrip("!")
                        code = f"{indent}{safe_name} := map_update_some !{safe_name} {k} {v}"
                else:
                    self._add_abstract_op("val subscript_set (x: int) (i: int) (v: int) : unit")
                    code = (f"{indent}subscript_set {self._coerce_to_int(array_expr)} "
                            f"{self._coerce_to_int(index_expr)} {self._coerce_to_int(val_expr)}")
            else:
                hv = self._heap_var
                code = (f"{indent}{hv} := Map.set !{hv} "
                        f"({array_expr} + {index_expr}) {val_expr}")
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_if_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                        local_refs: Set[str], declared_refs: Set[str],
                        indent: str, in_loop: bool) -> str:
        test = self._expr_to_whyml(stmt["test"], local_refs)
        test = self._to_bool(test, stmt["test"])
        body = stmt.get("body", [])
        orelse = stmt.get("orelse", [])
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

    def _handle_match_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                           local_refs: Set[str], declared_refs: Set[str],
                           indent: str, in_loop: bool) -> str:
        subject = self._expr_to_whyml(stmt["subject"], local_refs)
        cases = stmt.get("cases", [])
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

    def _handle_critical_section_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                       local_refs: Set[str], declared_refs: Set[str],
                                       indent: str, in_loop: bool) -> str:
        mutex = stmt["mutex"]
        body_stmts = stmt["body"]
        assume_inv = stmt.get("assume_invariant")
        prove_inv = stmt.get("prove_invariant")
        safe_mutex = safe_mutex_name(mutex)
        shared_for_mutex = [
            sv["name"] for sv in self.ir.get("shared_vars", [])
            if sv.get("mutex") == mutex
        ]
        let_bindings: List[str] = []
        seq_parts: List[str] = []
        if assume_inv and shared_for_mutex:
            for var in shared_for_mutex:
                safe_var = whyml_ident(var)
                tmp = f"_any_{safe_var}_{self._havoc_counter}"
                self._havoc_counter += 1
                let_bindings.append(f"{indent}let {tmp} = any int in")
                seq_parts.append(f"{indent}{safe_var} := {tmp}")
            seq_parts.append(f"{indent}assume {{ {safe_mutex}_inv }}")
        elif assume_inv:
            self._in_spec = True
            inv_str = self._expr_to_whyml(assume_inv, local_refs)
            self._in_spec = False
            seq_parts.append(f"{indent}assume {{ {inv_str} }}")
        body_code = self._stmts_to_whyml(body_stmts, local_refs, declared_refs, indent, in_loop)
        if body_code:
            seq_parts.append(body_code)
        if prove_inv and shared_for_mutex:
            seq_parts.append(f"{indent}assert {{ {safe_mutex}_inv }}")
        elif prove_inv:
            self._in_spec = True
            inv_str = self._expr_to_whyml(prove_inv, local_refs)
            self._in_spec = False
            seq_parts.append(f"{indent}assert {{ {inv_str} }}")
        if not seq_parts:
            seq_parts = [f"{indent}()"]
        inner = ";\n".join(seq_parts)
        code = ("\n".join(let_bindings) + "\n" + inner) if let_bindings else inner
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_augassign_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        target = stmt["target"]
        safe_target = whyml_ident(target)
        val = self._expr_to_whyml(stmt["value"], local_refs)
        raw_op = stmt["op"]
        op = op_translate(raw_op)
        bitwise_ops = {"&": "bit_and", "|": "bit_or", "^": "bit_xor",
                       "<<": "bit_lshift", ">>": "bit_rshift", "**": "py_pow"}
        # Detect array-typed targets so `+=` on a list lowers to array-concat,
        # not integer add. Python `lines += [...]` extends the list; emitting
        # `lines := !lines + rhs` produces a `array int` vs `int` type error
        # at Why3.
        array_target = (
            target in self._array_locals
            or target in self._array2d_params
            or target in self._current_array1d_params
        )
        if raw_op in bitwise_ops:
            op_fn = bitwise_ops[raw_op]
            self._add_abstract_op(f"val {op_fn} (x: int) (y: int) : int")
            code = f"{indent}{safe_target} := ({op_fn} !{safe_target} {val})"
        elif raw_op == "+" and array_target:
            # Python `lines += other` extends the list in place. Module6
            # declares array locals as non-ref (`let lines = Array.make ... in`)
            # and uses `lines[i] <- v` for element writes, so `:= !lines + rhs`
            # is doubly wrong (no `:=`/deref on non-ref arrays, and integer
            # add on arrays). Emit an abstract `array_extend` with unit
            # return type — the side effect on `dst` is opaque to Why3 but
            # the call type-checks.
            self._add_abstract_op(
                "val array_extend (dst: array int) (src: array int) : unit")
            code = f"{indent}array_extend {safe_target} {val}"
        else:
            code = f"{indent}{safe_target} := !{safe_target} {op} {val}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_fieldassign_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        obj = stmt["object"]
        field = stmt["field"]
        val = self._expr_to_whyml(stmt["value"], local_refs)
        if val == "true":
            val = "1"
        elif val == "false":
            val = "0"
        safe_field = whyml_ident(field)
        decl_fields = self._all_record_fields
        if field in decl_fields:
            # Coerce RHS to the field's declared WhyML type. Without
            # this, `self.<list-field> <- <int-returning-call>` (e.g.
            # `self._lock_order <- get_order(...)` where get_order is
            # abstract `int -> int` but the field is `array int`)
            # type-mismatches. Apply the matching coercion helper per
            # field type.
            ftype = self._field_type_for(obj, field)
            if ftype in ("list", "tuple"):
                val = self._array_coerce_arg(val)
            elif ftype in ("set", "dict", "frozenset"):
                # Map-typed field: keep map-shaped values, otherwise
                # use empty map. (Same pragma as `_handle_dotted_call`.)
                stripped = val.strip()
                map_prefixes = ("(map_update_some ", "(map_update_none ",
                                "(const (None: option int)", "(Map.get ")
                if not any(stripped.startswith(p) for p in map_prefixes):
                    if not stripped.replace("_", "").replace("!", "").isalnum():
                        val = "(const (None: option int))"
            code = f"{indent}{obj}.{safe_field} <- {val}"
        else:
            hash_field = hash(field) % 2147483647
            self_type = self._current_self_type
            if obj == "self" and self_type:
                self._add_abstract_op(f"val setattr_{self_type} (x: {self_type}) (f: int) (v: int) : unit")
                code = f"{indent}setattr_{self_type} {obj} {hash_field} {self._coerce_to_int(val)}"
            else:
                self._add_abstract_op("val setattr_3 (x: int) (f: int) (v: int) : unit")
                code = f"{indent}setattr_3 {self._coerce_to_int(obj)} {hash_field} {self._coerce_to_int(val)}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_fieldaugassign_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        obj = stmt["object"]
        field = stmt["field"]
        val = self._expr_to_whyml(stmt["value"], local_refs)
        op = op_translate(stmt["op"])
        safe_field = whyml_ident(field)
        decl_fields = self._all_record_fields
        if field in decl_fields:
            code = f"{indent}{obj}.{safe_field} <- {obj}.{safe_field} {op} {val}"
        else:
            hash_field = hash(field) % 2147483647
            self_type = self._current_self_type
            if obj == "self" and self_type:
                getter = f"getattr_{self_type}"
                setter = f"setattr_{self_type}"
                self._add_abstract_op(f"val {getter} (x: {self_type}) (f: int) : int")
                self._add_abstract_op(f"val {setter} (x: {self_type}) (f: int) (v: int) : unit")
                code = f"{indent}{setter} {obj} {hash_field} (({getter} {obj} {hash_field}) {op} {self._coerce_to_int(val)})"
            else:
                self._add_abstract_op("val getattr_2 (x: int) (f: int) : int")
                self._add_abstract_op("val setattr_3 (x: int) (f: int) (v: int) : unit")
                obj_str = self._coerce_to_int(obj)
                code = f"{indent}setattr_3 {obj_str} {hash_field} ((getattr_2 {obj_str} {hash_field}) {op} {self._coerce_to_int(val)})"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _bool_ir_to_int_wrap(self, val: str, val_ir: Optional[Dict[str, Any]]) -> str:
        """If val_ir denotes a bool-typed IR expression, wrap val with
        an int coercion `(if X then 1 else 0)`. Mirrors the bool-source
        detection in _to_bool() so a `return isinstance(x, T)` style
        statement doesn't raise a bool inside `exception Return int`.

        Literal Bool atoms are handled by the caller's `val == "true"/"false"`
        branches and intentionally not detected here."""
        if val_ir is None:
            return val
        t = val_ir.get("type", "")
        op = val_ir.get("op", "")
        is_bool_source = (
            (t == "Compare")
            or (t == "BoolOp" and op in ("and", "or"))
            or (t == "UnaryOp" and op == "not")
            or (t == "BinOp" and op in ("==", "!=", "<", ">", "<=", ">=", "in", "not in"))
            or (t == "Call" and val_ir.get("func", "") in (
                "isinstance", "hasattr", "any", "all"))
            or (t in ("Exists", "Forall", "SetMem", "SetSubset", "SetEq",
                      "MapEq", "HasKey"))
        )
        if is_bool_source:
            return f"(if {val} then 1 else 0)"
        return val

    def _handle_return_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        """Reads self._has_early_ret, self._func_return_type, self._array_locals (no writes)."""
        val_ir = stmt.get("value")
        use_raise = in_loop or self._has_early_ret
        func_ret_peek = self._func_return_type
        if val_ir is None:
            val = "()"
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
        if use_raise:
            func_ret = self._func_return_type
            if func_ret == "unit":
                return f"{indent}raise Return_void"
            arity = self._current_tuple_arity
            if arity > 0:
                # Tuple return: use the dedicated Return_<arity> exception
                # so the whole tuple value carries through. Do NOT call
                # _coerce_to_int — for tuple-shaped strings that would hash
                # the whole tuple to a single int.
                return f"{indent}raise (Return_{arity} {val})"
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
        return f"{indent}{val}"

    def _handle_expr_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        val = stmt.get("value", {})
        if val.get("type") == "Call":
            func = val.get("func", "")
            if func.endswith(".append") and self.memory_model in ("hoare", "concurrent"):
                arr_name = func.rsplit(".", 1)[0].replace(".", "_")
                safe_arr = whyml_ident(arr_name)
                arg = self._expr_to_whyml(val["args"][0], local_refs)
                arg = self._coerce_to_int(arg)
                len_ref = f"{safe_arr}_len"
                code = f"{indent}{safe_arr}[!{len_ref}] <- {arg};\n{indent}{len_ref} := !{len_ref} + 1"
            elif (func.endswith((".add", ".discard", ".remove"))
                  and self.memory_model in ("hoare", "concurrent")):
                # Body-level set/dict method calls. Sets and dicts share
                # the `_dict_locals` tracking and `map int (option int)`
                # model. Use program-level wrappers (see comment on
                # `map_update_some`) — `Map.set` is logic-only and Why3
                # rejects direct `:= Map.set ...` on non-ghost refs.
                method = func.rsplit(".", 1)[1]
                obj_name = func.rsplit(".", 1)[0]
                if obj_name in getattr(self, "_dict_locals", set()):
                    safe_obj = whyml_ident(obj_name)
                    arg_ir = (val.get("args") or [{}])[0]
                    arg = self._coerce_to_int(self._expr_to_whyml(arg_ir, local_refs))
                    if method == "add":
                        # set.add(x) — mark key present with Some 0.
                        self._add_abstract_op(
                            "val map_update_some (m: map int (option int)) (k: int) (v: int) "
                            ": map int (option int)\n"
                            "    ensures { result = Map.set m k (Some v) }")
                        code = f"{indent}{safe_obj} := map_update_some !{safe_obj} {arg} 0"
                    else:
                        # set.discard(x) / set.remove(x) / del d[k] — clear the key.
                        self._add_abstract_op(
                            "val map_update_none (m: map int (option int)) (k: int) "
                            ": map int (option int)\n"
                            "    ensures { result = Map.set m k None }")
                        code = f"{indent}{safe_obj} := map_update_none !{safe_obj} {arg}"
                else:
                    expr_str = self._expr_to_whyml(val, local_refs)
                    code = f"{indent}let _ = {expr_str} in ()"
            else:
                expr_str = self._expr_to_whyml(val, local_refs)
                code = f"{indent}let _ = {expr_str} in ()"
        else:
            expr_str = self._expr_to_whyml(val, local_refs)
            code = f"{indent}let _ = {expr_str} in ()"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _stmts_to_whyml(self, stmts: List[Dict[str, Any]], local_refs: Set[str], declared_refs: Set[str], indent: str, in_loop: bool = False) -> str:
        """Recursively translates imperative statements into WhyML strings."""
        if not stmts: return ""

        stmt = stmts[0]
        rest = stmts[1:]
        code = ""
        s_type = stmt["stmt"]

        if s_type == "Label":
            # `label L in <rest>` — scopes over the entire remaining block
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if not rest_code:
                rest_code = f"{indent}()"
            return f"{indent}label {stmt['name']} in\n{rest_code}"

        elif s_type == "GhostAssign":
            return self._handle_ghost_assign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "GhostArraySet":
            return self._handle_ghost_array_set_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Assign":
            return self._handle_assign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "TupleUnpack":
            return self._handle_tuple_unpack_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "AugAssign":
            return self._handle_augassign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "FieldAssign":
            return self._handle_fieldassign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "FieldAugAssign":
            return self._handle_fieldaugassign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "ArraySet":
            return self._handle_array_set_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)


        elif s_type == "While":
            return self._handle_while_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Return":
            return self._handle_return_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Continue":
            # Raise the continue exception caught by the enclosing For loop's try/with
            return f"{indent}raise PyCSL_Continue"

        elif s_type == "Assert":
            # Python assert statements are runtime checks, not proof obligations.
            # Skip them in WhyML — the pycsl annotations define the proof goals.
            code = f'{indent}()'

        elif s_type == "Raise":
            exc_type = stmt.get("exc_type", "PyCSL_Exception")
            return f"{indent}raise {exc_type}"

        elif s_type == "If":
            return self._handle_if_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "For":
            return self._handle_for_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Expr":
            return self._handle_expr_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Try":
            return self._handle_try_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Pass":
            code = f"{indent}()"

        elif s_type == "Break":
            # WhyML doesn't have break; model as exception
            code = f"{indent}raise PyCSL_Break"

        elif s_type == "Match":
            return self._handle_match_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "CriticalSection":
            return self._handle_critical_section_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        # Chain sequence of statements with semicolons
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)

        return code

    def _emit_frame_condition(self, assigns_list: List[Dict[str, Any]],
                              spec_refs: Set[str]) -> List[str]:
        """Generate WhyML frame condition lines from \\assigns contracts.

        In the Hoare model: no frame condition (value-semantic arrays can't alias).
        In typed/store models: emits `writes` + quantified `ensures` for unchanged locations.
        Returns a list of WhyML lines to append after the function's `ensures` clauses.
        """
        if self.memory_model in ("hoare", "concurrent"):
            return []

        hv = self._heap_var
        regions = [a for a in assigns_list if a.get("type") == "AssignsRegion"]
        nothings = [a for a in assigns_list if a.get("type") == "Nothing"]

        if nothings:
            return [f"    ensures  {{ !{hv} = old !{hv} }}"]

        if not regions:
            return [f"    writes   {{ {hv} }}"]

        lines = [f"    writes   {{ {hv} }}"]
        exclusions = []
        for r in regions:
            base = r["base"]
            lo = self._expr_to_whyml(r["low"], spec_refs)
            hi = self._expr_to_whyml(r["high"], spec_refs)
            exclusions.append(f"({base} + {lo} <= l && l < {base} + {hi})")

        neg = " && ".join(f"(not {e})" for e in exclusions)
        lines.append(
            f"    ensures  {{ forall l: int. {neg}"
            f" -> Map.get !{hv} l = Map.get (old !{hv}) l }}"
        )
        return lines

    @staticmethod
    def _build_witness_str(field_names: List[str], vals: Dict[str, Any]) -> str:
        """Build a WhyML record literal witness string."""
        return "; ".join(f"{fn} = {vals.get(fn, 0)}" for fn in field_names)

    def _check_witness_vals(self, vals: Dict[str, Any], invs: List[Any], field_names: List[str]) -> bool:
        """Quick sanity check: evaluate invariant with witness values."""
        for inv_ir in invs:
            try:
                expr = self._expr_to_whyml(inv_ir, set(), invariant_ctx=True)
                test_expr = expr
                for fn in field_names:
                    test_expr = test_expr.replace(fn, str(vals.get(fn, 0)))
                test_expr = (test_expr.replace("=", "==")
                             .replace("!==", "!=")
                             .replace("<==", "<=")
                             .replace(">==", ">="))
                if not eval(test_expr):  # noqa: S307
                    return False
            except (NameError, SyntaxError, TypeError, ValueError, ZeroDivisionError):
                pass
        return True

    def _param_type_str(self, arg: str, ref_params: Set[str], array2d_params: Set[str],
                        array1d_params: Set[str], symbol_table: Dict[str, Any],
                        int_type: str) -> str:
        """Return the WhyML parameter type string for a standalone function argument."""
        safe = whyml_ident(arg)
        if arg in ref_params:
            return f"({safe}: ref {int_type})"
        if arg in array2d_params:
            return f"({safe}: matrix {int_type})"
        symtype = symbol_table.get(arg)
        # `Set[T]` / `Dict[K, V]` / `FrozenSet[T]` parameters are
        # modelled as `map int (option int)` (parallel to body-level
        # dicts). Must come before the `list` branch since dict/set
        # share the map model, not the array model.
        if symtype in ("set", "dict", "frozenset"):
            return f"({safe}: map int (option int))"
        if arg in array1d_params or symtype == "list":
            if self.memory_model in ("hoare", "concurrent"):
                return f"({safe}: array {int_type})"
            return f"({safe}: loc) ({safe}_len: int)"
        if symtype == "str":
            return f"({safe}: {int_type})"
        return f"({safe}: {int_type})"

    # ------------------------------------------------------------------
    # transpile() Phase A — collect record field names
    # ------------------------------------------------------------------

    def _collect_record_fields(self, type_decls: List[Dict[str, Any]]) -> Set[str]:
        """Collect all declared record field names for FieldGet resolution."""
        fields: Set[str] = set()
        n = len(type_decls)
        i = 0
        while i < n:
            td = type_decls[i]
            if td["kind"] == "record":
                flds = td.get("fields", [])
                nf = len(flds)
                j = 0
                while j < nf:
                    fields.add(flds[j]["name"])
                    j += 1
            i += 1
        return fields

    # ------------------------------------------------------------------
    # transpile() Phase B — scan preamble needs
    # ------------------------------------------------------------------

    def _scan_preamble_needs(self, functions: List[Dict[str, Any]],
                             all_bodies: List[Any]) -> Dict[str, Any]:
        """Scan all function bodies once to collect feature flags for preamble emission."""
        has_list_param = any(
            v in ("list", "dict")
            for func in functions
            for v in func.get("symbol_table", {}).values()
        )
        needs_matrix = any(func.get("array2d_params") for func in functions)
        if self.memory_model in ("hoare", "concurrent"):
            needs_array = (
                has_list_param
                or any(IRScanner.uses_for(body) for body in all_bodies)
                or any(IRScanner.uses_subscript(body) for body in all_bodies)
                or any(IRScanner.uses_arrayset(body) for body in all_bodies)
                or any(IRScanner.uses_array_lit(body) for body in all_bodies)
                or any(IRScanner.uses_ghost_type(body, {"array"}) for body in all_bodies)
            )
        else:
            needs_array = False
        needs_minmax = any(IRScanner.uses_minmax(body) for body in all_bodies)
        needs_continue = any(IRScanner.uses_continue(body) for body in all_bodies)
        needs_break = any(IRScanner.uses_break(body) for body in all_bodies)
        needs_return_exc = False
        needs_return_void = False
        tuple_return_arities: Set[int] = set()
        n = len(functions)
        i = 0
        while i < n:
            func = functions[i]
            has_ret = IRScanner.has_in_loop_return(func["body"]) or IRScanner.has_early_return(func["body"])
            if has_ret:
                ret_type = IRScanner.find_return_type(func["body"])
                if ret_type == "unit":
                    needs_return_void = True
                elif ret_type.startswith("(") and "," in ret_type:
                    # Tuple return — needs a dedicated Return_<arity> exception
                    # so the value carries through; the plain `exception Return int`
                    # would force `_coerce_to_int` to hash the whole tuple.
                    tuple_return_arities.add(ret_type.count(",") + 1)
                else:
                    needs_return_exc = True
            i += 1
        needs_string = any(IRScanner.uses_ghost_type(body, {"string"}) for body in all_bodies)
        needs_map_ghost = any(IRScanner.uses_ghost_type(body, {"ghost_dict", "ghost_set"}) for body in all_bodies)
        needs_ghost_dict = any(IRScanner.uses_ghost_type(body, {"ghost_dict"}) for body in all_bodies)
        # Body-level Python dicts are modelled as `ref (map int (option int))`
        # (parallel to ghost dicts). Triggered by:
        #   - `find_array_and_dict_vars` detecting any `d = {}` / `d = dict()`
        #     / `d = {k: v}` / `s = set()` / `s = {a, b}` in the body.
        #   - inline set/dict literals (e.g. `held | {mutex}`) or
        #     `.add()`/`.discard()`/`.remove()` method calls anywhere in
        #     the IR — these emit `map_update_some` / `map_update_none`
        #     into the abstract-val block, which requires `use map.Map`
        #     and `use option.Option` in the preamble.
        needs_body_dict = False
        for body in all_bodies:
            _arr, body_dicts = IRScanner.find_array_and_dict_vars(body)
            if body_dicts or IRScanner.uses_inline_set_or_dict_ops(body):
                needs_body_dict = True
                break
        needs_list_ghost = any(IRScanner.uses_ghost_type(body, {"ghost_list"}) for body in all_bodies)
        needs_sum = any(IRScanner.uses_sum(func) for func in functions)
        needs_set_card = any(IRScanner.uses_set_card(func) for func in functions)
        needs_divmod = any(IRScanner.uses_divmod(body) for body in all_bodies)
        bounded_sizes = {func["bounded_int"] for func in functions if func.get("bounded_int")}
        user_exceptions: Set[str] = set()
        n2 = len(all_bodies)
        i2 = 0
        while i2 < n2:
            user_exceptions |= IRScanner.collect_user_exceptions(all_bodies[i2])
            i2 += 1
        return {
            "needs_array": needs_array,
            "needs_matrix": needs_matrix,
            "needs_minmax": needs_minmax,
            "needs_continue": needs_continue,
            "needs_break": needs_break,
            "needs_return_exc": needs_return_exc,
            "needs_return_void": needs_return_void,
            "needs_body_dict": needs_body_dict,
            "tuple_return_arities": tuple_return_arities,
            "needs_string": needs_string,
            "needs_map_ghost": needs_map_ghost,
            "needs_ghost_dict": needs_ghost_dict,
            "needs_list_ghost": needs_list_ghost,
            "needs_sum": needs_sum,
            "needs_set_card": needs_set_card,
            "needs_divmod": needs_divmod,
            "bounded_sizes": bounded_sizes,
            "user_exceptions": user_exceptions,
        }

    # ------------------------------------------------------------------
    # transpile() Phase C — emit module preamble (use / exceptions / helpers)
    # ------------------------------------------------------------------

    def _emit_preamble_uses(self, needs: Dict[str, Any]) -> List[str]:
        """Phase A: emit module header and `use` declarations for libraries."""
        out = [
            "module PyCSL_Program",
            "  use int.Int",
            "  use int.EuclideanDivision",
            "  use ref.Ref",
        ]
        sorted_bsz = sorted(needs["bounded_sizes"])
        n = len(sorted_bsz)
        i = 0
        while i < n:
            out.append(f"  use mach.int.Int{sorted_bsz[i]}")
            i += 1
        if needs["needs_string"]:
            out.append("  use string.String")
        if self.memory_model in ("hoare", "concurrent"):
            if needs["needs_matrix"]:
                out.append("  use matrix.Matrix")
            if needs["needs_minmax"]:
                out.append("  use int.MinMax")
            if needs["needs_map_ghost"] or needs.get("needs_body_dict"):
                out.append("  use map.Map")
                out.append("  use map.Const")
            if needs["needs_ghost_dict"] or needs.get("needs_body_dict"):
                # Body-level Python dicts are modelled as
                # `ref (map int (option int))` (parallel to ghost dicts);
                # `None` marks absent keys.
                out.append("  use option.Option")
            # `array.Array` MUST be imported AFTER `map.Map` — both
            # provide a `([])` operator, and when both are in scope the
            # later import wins. With map.Map imported last, `arr[i]` on
            # an `array int` is mis-resolved to `Map.get`, producing
            # "expected 'mu -> 'mu1, got array int @rho" type errors.
            # See ConcurrencyChecker (which combines body-set ops with
            # array-typed function parameters).
            if needs["needs_array"]:
                out.append("  use array.Array")
            if needs["needs_list_ghost"]:
                out.append("  use list.List")
                out.append("  use list.Length")
                out.append("  use list.NthNoOpt")
                out.append("  use list.Mem")
                out.append("  use list.Append")
        else:
            out.append("  use map.Map")
            if needs["needs_list_ghost"]:
                out.append("  use list.List")
                out.append("  use list.Length")
                out.append("  use list.NthNoOpt")
                out.append("  use list.Mem")
                out.append("  use list.Append")
            if needs["needs_minmax"]:
                out.append("  use int.MinMax")
            out.append("")
            out.append("  type loc = int")
            out.append("  constant max_addr : int = 1073741824")
            hv = self._heap_var
            out.append(f"  val ghost {hv} : ref (map loc int)")
            out.append("")
            out.append(f"  predicate valid (m: map loc int) (base: loc) (n: int) =")
            out.append(f"    n >= 0 /\\ base >= 0 /\\ base + n <= max_addr")
            out.append("")
            out.append(f"  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =")
            out.append(f"    a + na <= b \\/ b + nb <= a")
            out.append("")
        return out

    def _emit_preamble_exceptions(self, needs: Dict[str, Any]) -> List[str]:
        """Phase B: emit exception type declarations."""
        out: List[str] = []
        if needs["needs_continue"]:
            out.append("")
            out.append("  exception PyCSL_Continue")
        if needs["needs_break"]:
            out.append("")
            out.append("  exception PyCSL_Break")
        if needs["needs_return_exc"]:
            out.append("")
            out.append("  exception Return int")
        if needs["needs_return_void"]:
            out.append("")
            out.append("  exception Return_void")
        for arity in sorted(needs.get("tuple_return_arities", set())):
            # Tuple returns: each arity gets its own exception carrying the
            # full tuple, avoiding the int-hash collapse the plain `Return int`
            # would force via `_coerce_to_int`.
            parts = ", ".join(["int"] * arity)
            out.append("")
            out.append(f"  exception Return_{arity} ({parts})")
        sorted_exc = sorted(needs["user_exceptions"])
        n = len(sorted_exc)
        i = 0
        while i < n:
            out.append(f"  exception {sorted_exc[i]}")
            i += 1
        return out

    def _emit_preamble_helpers(self, needs: Dict[str, Any]) -> List[str]:
        """Phase C: emit helper lemmas, pycsl_sum, pycsl_div, pycsl_mod function bodies."""
        out: List[str] = []
        if needs.get("needs_list_ghost"):
            # axiom mem_head: base case of mem — makes \mem(x, \cons(x, l)) proofs tractable
            # without recursive unfolding. This is the head-match case of mem's definition,
            # so it is mathematically sound to assume it as an axiom.
            out.append("")
            out.append("  axiom mem_head : forall x: int, l: list int. mem x (Cons x l)")
        if needs["needs_sum"]:
            out.append("")
            out.append("  let rec function pycsl_sum (a: array int) (lo hi: int) : int")
            out.append("    requires { 0 <= lo }")
            out.append("    requires { hi <= Array.length a }")
            out.append("    variant { hi - lo }")
            out.append("  = if lo >= hi then 0 else a[lo] + pycsl_sum a (lo + 1) hi")
            out.append("")
            out.append("  let rec lemma pycsl_sum_snoc (a: array int) (lo hi: int) : unit")
            out.append("    requires { 0 <= lo <= hi <= Array.length a }")
            out.append("    variant { hi - lo }")
            out.append("    ensures { hi > lo -> pycsl_sum a lo hi = pycsl_sum a lo (hi - 1) + a[hi - 1] }")
            out.append("  = if lo < hi - 1 then pycsl_sum_snoc a (lo + 1) hi")
        if needs["needs_set_card"]:
            out.append("")
            out.append("  let rec function set_card (s: map int bool) (lo hi: int) : int")
            out.append("    requires { lo <= hi }")
            out.append("    variant { hi - lo }")
            out.append("  = if lo >= hi then 0")
            out.append("    else (if Map.get s lo then 1 else 0) + set_card s (lo + 1) hi")
            out.append("")
            out.append("  let rec lemma set_card_add_hi (s: map int bool) (lo hi: int) : unit")
            out.append("    requires { lo <= hi }")
            out.append("    variant { hi - lo }")
            out.append("    ensures { set_card (Map.set s hi true) lo (hi + 1) = set_card s lo hi + 1 }")
            out.append("  = if lo < hi then set_card_add_hi s (lo + 1) hi")
        if needs["needs_divmod"]:
            out.append("")
            if "ZeroDivisionError" in needs["user_exceptions"]:
                out.append("  let pycsl_div (x: int) (y: int) : int")
                out.append("    raises { ZeroDivisionError -> y = 0 }")
                out.append("    ensures { y <> 0 /\\ result = div x y }")
                out.append("  = if y = 0 then raise ZeroDivisionError else div x y")
                out.append("")
                out.append("  let pycsl_mod (x: int) (y: int) : int")
                out.append("    raises { ZeroDivisionError -> y = 0 }")
                out.append("    ensures { y <> 0 /\\ result = mod x y }")
                out.append("  = if y = 0 then raise ZeroDivisionError else mod x y")
            else:
                out.append("  let pycsl_div (x: int) (y: int) : int")
                out.append("    requires { [@expl:division by zero] y <> 0 }")
                out.append("    ensures { result = div x y }")
                out.append("  = div x y")
                out.append("")
                out.append("  let pycsl_mod (x: int) (y: int) : int")
                out.append("    requires { [@expl:modulo by zero] y <> 0 }")
                out.append("    ensures { result = mod x y }")
                out.append("  = mod x y")
        return out

    # §2.1.12 — registry of hand-curated axiom bodies for `#@ proof`
    # qualnames. MVP step before `proof2why3` extraction lands (see
    # docs/cross-validated-spec-sources.md). Each entry's body is the canonical statement that
    # the paired Rocq + Lean theorems establish — cross-checked
    # manually for the MVP, automatically via the cross-check
    # pipeline in v1.
    _AXIOM_REGISTRY: Dict[str, str] = {
        # Pycsl.Reference.Gcd — Euclidean GCD properties.
        # Cross-validated by 0342.proofs/rocq/gcd.v + 0342.proofs/lean/Gcd.lean.
        "Pycsl.Reference.Gcd.gcd_result_nonneg":
            "forall a b : int. 0 <= gcd a b",
        "Pycsl.Reference.Gcd.gcd_result_positive":
            "forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> gcd a b > 0",
        "Pycsl.Reference.Gcd.gcd_divides_a":
            "forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod a (gcd a b) = 0",
        "Pycsl.Reference.Gcd.gcd_divides_b":
            "forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod b (gcd a b) = 0",
        "Pycsl.Reference.Gcd.gcd_0":
            "forall a : int. a >= 0 -> gcd a 0 = a",
        "Pycsl.Reference.Gcd.gcd_step":
            "forall a b : int. b > 0 -> gcd a b = gcd b (mod a b)",
        "Pycsl.Reference.Gcd.gcd_greatest":
            "forall a b k : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> "
            "k > 0 -> mod a k = 0 -> mod b k = 0 -> k <= gcd a b",
    }

    # Functions that an axiom block needs declared. Looked up by qualname
    # prefix; declarations emitted once each when any matching axiom fires.
    _AXIOM_FUNCTIONS: Dict[str, str] = {
        "Pycsl.Reference.Gcd.": "function gcd (a : int) (b : int) : int",
    }

    def _emit_preamble_axioms(self, ir: Dict[str, Any]) -> List[str]:
        """Emit Why3 function decls + axioms for `#@ proof` cites.

        Scans every function in the program IR for `proof` entries.
        Dedups by qualname (Rocq + Lean cite the same target). Emits
        each axiom under a sanitized name `pycsl_axiom_<...>` and
        records the prover provenance in a Why3 comment.
        """
        seen_qualnames: Set[str] = set()
        for func in ir.get("functions", []):
            for entry in func.get("proof", []):
                seen_qualnames.add(entry["qualname"])
        if not seen_qualnames:
            return []

        # Pair each qualname with the registry entry; halt if any
        # unknown — failure is at transpile time.
        out: List[str] = []
        # Declare backing functions once each (e.g. `function gcd`).
        declared_fns: Set[str] = set()
        for qn in sorted(seen_qualnames):
            for prefix, fn_decl in self._AXIOM_FUNCTIONS.items():
                if qn.startswith(prefix) and fn_decl not in declared_fns:
                    out.append(f"  {fn_decl}")
                    declared_fns.add(fn_decl)
        if declared_fns:
            out.append("")

        # Emit each axiom. Comment records the prover pairing.
        for qn in sorted(seen_qualnames):
            if qn not in self._AXIOM_REGISTRY:
                raise PyCSLIRError(
                    f"#@ proof {qn}: not in Module6 axiom registry. "
                    f"Either add the axiom body to _AXIOM_REGISTRY or run "
                    f"`proof2why3 emit` (when available — see "
                    f"docs/cross-validated-spec-sources.md)."
                )
            axiom_name = "pycsl_axiom_" + qn.replace(".", "_")
            body = self._AXIOM_REGISTRY[qn]
            # Provers cite this qualname — for the MVP we record both
            # under one cite. v1 emits the canonical-hash status from
            # the cross-check manifest.
            out.append(f"  (* {qn} — cross-validated Rocq + Lean *)")
            out.append(f"  axiom {axiom_name} : {body}")
        out.append("")
        return out

    def _emit_preamble(self, needs: Dict[str, Any]) -> List[str]:
        """Emit the WhyML module header: use declarations, exception types, helper functions."""
        out = self._emit_preamble_uses(needs)
        out += self._emit_preamble_exceptions(needs)
        out += self._emit_preamble_helpers(needs)
        out += self._emit_preamble_axioms(self.ir)
        out.append("")
        return out

    # ------------------------------------------------------------------
    # transpile() Phase D — emit concurrent-model shared state
    # ------------------------------------------------------------------

    def _emit_shared_state(self) -> List[str]:
        """Emit shared variable declarations and mutex invariant predicates (concurrent model)."""
        out: List[str] = []
        shared_vars = self.ir.get("shared_vars", [])
        mutex_invariants_ir = self.ir.get("mutex_invariants", {})
        if shared_vars:
            self._shared_var_names = {sv["name"] for sv in shared_vars}
            out.append("  (* --- shared state (concurrent model) --- *)")
            n = len(shared_vars)
            i = 0
            while i < n:
                sv = shared_vars[i]
                safe_name = whyml_ident(sv["name"])
                out.append(f"  val {safe_name} : ref int")
                i += 1
            out.append("")
        if mutex_invariants_ir:
            sorted_mi = sorted(mutex_invariants_ir.items())
            n = len(sorted_mi)
            i = 0
            while i < n:
                mutex, inv_ir = sorted_mi[i]
                safe_mutex = safe_mutex_name(mutex)
                self._in_spec = True
                inv_str = self._expr_to_whyml(inv_ir, set())
                self._in_spec = False
                out.append(f"  predicate {safe_mutex}_inv = {inv_str}")
                i += 1
            out.append("")
            sorted_mi2 = sorted(mutex_invariants_ir.items())
            n2 = len(sorted_mi2)
            i2 = 0
            while i2 < n2:
                mutex2, _ = sorted_mi2[i2]
                safe_mutex2 = safe_mutex_name(mutex2)
                out.append(f"  let _check_initial_{safe_mutex2} () : unit =")
                out.append(f"    assert {{ {safe_mutex2}_inv }}")
                out.append("")
                i2 += 1
        return out

    # ------------------------------------------------------------------
    # transpile() Phase E — emit type declarations
    # ------------------------------------------------------------------

    def _emit_type_decls(self, type_decls: List[Dict[str, Any]]) -> Tuple[List[str], Set[str]]:
        """Emit record type declarations. Returns (lines, declared_types)."""
        out: List[str] = []
        declared_types: Set[str] = set()
        n = len(type_decls)
        i = 0
        while i < n:
            td = type_decls[i]
            if td["kind"] == "record":
                type_name = td["name"].lower()
                declared_types.add(type_name)
                self._record_types[td["name"]] = {
                    "whyml_name": type_name,
                    "fields": [f["name"] for f in td["fields"]],
                    "field_types": {f["name"]: f.get("type", "int") for f in td["fields"]},
                    "defaults": td.get("field_defaults", {}),
                }
                field_strs = []
                fields = td["fields"]
                nf = len(fields)
                j = 0
                while j < nf:
                    f = fields[j]
                    prefix = "mutable " if f.get("mutable") else ""
                    ftype = f['type']
                    # Map Python-level type tags to WhyML types.
                    # `set`/`dict`/`frozenset` → `map int (option int)`
                    # (body-set/body-dict model). `list`/`tuple` →
                    # `array int`. Everything else collapses to `int`.
                    if ftype in ("set", "dict", "frozenset"):
                        ftype = "map int (option int)"
                    elif ftype in ("list", "tuple"):
                        ftype = "array int"
                    elif ftype == "string":
                        ftype = "int"
                    elif ftype != "int" and not ftype.startswith(("array ", "map ", "ref ")):
                        # Unrecognised tag (user-defined class etc.) —
                        # fall back to int rather than emitting an
                        # unbound type symbol.
                        ftype = "int"
                    field_strs.append(f"{prefix}{f['name']}: {ftype}")
                    j += 1
                out.append(f"  type {type_name} = {{ {'; '.join(field_strs)} }}")
                class_invs = td.get("class_invariants", [])
                if class_invs:
                    self._in_spec = True
                    n_inv = len(class_invs)
                    i_inv = 0
                    while i_inv < n_inv:
                        inv = class_invs[i_inv]
                        inv_str = self._expr_to_whyml(inv, set(), invariant_ctx=True)
                        out.append(f"    invariant {{ {inv_str} }}")
                        i_inv += 1
                    self._in_spec = False
                    defaults = td.get("field_defaults", {})
                    field_names = [f["name"] for f in td["fields"]]
                    witness_vals = {fn: defaults.get(fn, 0) for fn in field_names}
                    if not self._check_witness_vals(witness_vals, class_invs, field_names):
                        combos = [
                            {fn: 0 for fn in field_names},
                            {fn: 1 for fn in field_names},
                            {fn: 10 for fn in field_names},
                        ]
                        nc = len(combos)
                        ic = 0
                        while ic < nc:
                            combo = combos[ic]
                            if self._check_witness_vals(combo, class_invs, field_names):
                                witness_vals = combo
                                break
                            ic += 1
                    out.append(f"    by {{ {self._build_witness_str(field_names, witness_vals)} }}")
                out.append("")
            i += 1
        return out, declared_types

    # ------------------------------------------------------------------
    # transpile() Phase G — topological sort via SCC
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # transpile() Phase H — emit one function block (and helpers)
    # ------------------------------------------------------------------

    def _reset_function_state(self, func: Dict[str, Any],
                               body_stmts: List[Dict[str, Any]]) -> Tuple[Set[str], Set[str]]:
        """Reset all per-function instance variables. Returns (local_refs, ghost_vars)."""
        self._bounded_int = func.get("bounded_int")
        symbol_table = func.get("symbol_table", {})
        local_refs = IRScanner.find_assigned_vars(body_stmts)
        local_refs -= self._shared_var_names
        ghost_vars = IRScanner.find_ghost_vars(body_stmts)
        self._current_params = (
            (set(symbol_table.keys()) | local_refs | ghost_vars) - self._shared_var_names
        )
        self._array_locals = set()
        self._dict_locals = set()
        self._lambda_locals = set()
        self._record_locals = set()
        self._ghost_string_vars: Set[str] = set()
        self._ghost_array_vars: Set[str] = set()
        self._ghost_dict_vars: Set[str] = set()
        self._ghost_list_vars: Set[str] = set()
        self._ghost_set_vars: Set[str] = set()
        self._ghost_tuple_vars: Dict[str, int] = {}  # name → arity (2, 3, or 4)
        self._known_collection_sizes = {}
        self._known_collection_elements = {}
        self._current_symbol_table = symbol_table
        # Formal-parameter names ONLY — Module5 exposes this as a
        # distinct field because `symbol_table` is polluted with loop
        # targets and locals.
        self._formal_params: Set[str] = set(func.get("formal_params", []))
        self._current_array1d_params = set(func.get("array1d_params", []))
        self._array2d_params = set(func.get("array2d_params", []))
        return local_refs, ghost_vars

    def _build_param_list(self, func: Dict[str, Any],
                           local_refs: Set[str],
                           ghost_vars: Set[str]) -> Tuple[Set[str], str]:
        """Compute WhyML parameter string. Returns (ref_params, args_str).
        Mutates self._current_self_type."""
        is_method = func.get("kind") == "method"
        bounded_int = func.get("bounded_int")
        int_type = f"int{bounded_int}" if bounded_int else "int"
        symbol_table = self._current_symbol_table
        array2d_params = self._array2d_params
        array1d_params = self._current_array1d_params

        if is_method:
            self._current_self_type = func["self_type"].lower()
            param_parts = [f"(self: {self._current_self_type})"]
            for arg in symbol_table:
                if arg in local_refs or arg in ghost_vars:
                    continue
                safe = whyml_ident(arg)
                if arg in array2d_params:
                    param_parts.append(f"({safe}: matrix {int_type})")
                elif symbol_table.get(arg) in ("set", "dict", "frozenset"):
                    param_parts.append(f"({safe}: map int (option int))")
                elif arg in array1d_params or symbol_table.get(arg) == "list":
                    if self.memory_model in ("hoare", "concurrent"):
                        param_parts.append(f"({safe}: array {int_type})")
                    else:
                        param_parts.append(f"({safe}: loc) ({safe}_len: int)")
                else:
                    param_parts.append(f"({safe}: {int_type})")
            return set(), " ".join(param_parts)
        else:
            self._current_self_type = None
            ref_params = {v for v in symbol_table if v in local_refs and v.startswith("obj_")}
            # Formal parameters stay in `args` even if mutated in the
            # body — they get promoted to refs inside _emit_body_code
            # via shadowing (`let a = ref a in`). Without this, params
            # that are tuple-unpack targets (e.g., `a, b = b, a % b`)
            # silently disappear from the WhyML signature.
            #
            # Use `_formal_params` (unpolluted) not `symbol_table`
            # (which Module4 also fills with for-loop targets and
            # AnnAssign locals — those must NOT appear in the
            # function signature).
            args = [v for v in self._formal_params if v not in ghost_vars]
            args_str = " ".join(
                self._param_type_str(arg, ref_params, array2d_params, array1d_params,
                                     symbol_table, int_type)
                for arg in args
            )
            return ref_params, args_str

    # ------------------------------------------------------------------
    # VC classification — Task 7b
    # ------------------------------------------------------------------

    @staticmethod
    def _is_linear_expr(expr: Any) -> bool:
        """Return True iff *expr* is a linear-arithmetic IR expression.

        An expression is linear if it contains only:
          - Integer/boolean constants
          - Variable references
          - Arithmetic: +, - (binary and unary)
          - Comparisons: <, <=, >, >=, ==, !=
          - Logical: and, or, not
          - Multiplication by a constant (one operand is Num/Constant)
          - \\result, \\old(v) references

        An expression is NOT linear if it contains:
          - Function calls (Call nodes)
          - Division, modulo (/, //, %)
          - Multiplication of two non-constant sub-expressions
          - Float literals, string literals
          - Subscript, attribute access
        """
        def _check(e: Any) -> bool:
            if e is None:
                return True
            if not isinstance(e, dict):
                return True
            t = e.get("type", "")

            # Constants
            # Integer/boolean constants — "Number" is the IR type from Module5.
            # Values may be int, bool, or float (e.g. 0.0); accept all numeric types.
            if t in ("Num", "Number", "Constant", "Int"):
                val = e.get("value", e.get("n", 0))
                return isinstance(val, (int, float, bool))

            # Variable references (including \result, \old)
            if t in ("Name", "Var", "Result", "OldVar", "OldName"):
                return True

            if t == "BinOp":
                op = e.get("op", "")
                left = e.get("left")
                right = e.get("right")
                if op in ("+", "-", "<", "<=", ">", ">=", "==", "!=",
                          "and", "or", "==>", "<==>"):
                    return _check(left) and _check(right)
                if op == "*":
                    _CONST = ("Num", "Number", "Constant", "Int")
                    left_const = isinstance(left, dict) and left.get("type") in _CONST
                    right_const = isinstance(right, dict) and right.get("type") in _CONST
                    if left_const:
                        return _check(right)
                    if right_const:
                        return _check(left)
                    return False   # non-constant * non-constant
                return False       # /, //, % — not linear

            if t == "UnaryOp":
                op = e.get("op", "")
                # Module5 uses "expr" key for UnaryOp child (not "operand")
                if op in ("-", "not", "~"):
                    return _check(e.get("expr") or e.get("operand"))
                return False

            # \old(x) ghost references — treat as linear
            if t in ("Old", "OldExpr"):
                return _check(e.get("expr"))

            # Anything else (Call, Subscript, Attribute, Lambda, …)
            return False

        return _check(expr)

    @staticmethod
    def _is_linear_vc(ensures_exprs: List[Any],
                      requires_exprs: Optional[List[Any]] = None) -> bool:
        """Return True iff this VC (ensures + requires) is linear-arithmetic.

        A VC is linear if every ensures clause and every requires clause
        is a linear-arithmetic expression (see _is_linear_expr).

        Linear VCs are candidates for direct omega proofs in Lean 4
        (via `LinearArithVC.prf`) without routing through Why3/Alt-Ergo.
        """
        exprs = list(ensures_exprs or []) + list(requires_exprs or [])
        return all(Module6_WhyMLTranspiler._is_linear_expr(e) for e in exprs)

    def _emit_contracts(self, contracts: Dict[str, Any], spec_refs: Set[str],
                         func_variants: List[Any], func_diverges: bool,
                         func_exceptions: Set[str]) -> List[str]:
        """Emit requires/ensures/assigns/variant/raises lines.
        Toggles self._in_spec around emission."""
        lines: List[str] = []
        self._in_spec = True

        requires_exprs = contracts.get("requires", [])
        ensures_exprs  = contracts.get("ensures", [])

        for req in requires_exprs:
            lines.append(f"    requires {{ {self._expr_to_whyml(req, spec_refs)} }}")
        for ens in ensures_exprs:
            # Tag linear ensures with a comment so the runner can classify VCs.
            # Linear VCs are candidates for omega proofs in Lean 4 (Task 7).
            lin_tag = " (* linear *)" if self._is_linear_vc([ens], requires_exprs) else ""
            lines.append(f"    ensures  {{ {self._expr_to_whyml(ens, spec_refs)} }}{lin_tag}")
        for fl in self._emit_frame_condition(contracts.get("assigns", []), spec_refs):
            lines.append(fl)
        for fv in func_variants:
            v_expr = self._expr_to_whyml(fv["expr"], spec_refs)
            if fv.get("ordering"):
                lines.append(f"    variant  {{ {v_expr} }} with {fv['ordering']}")
            else:
                lines.append(f"    variant  {{ {v_expr} }}")
        if func_diverges:
            lines.append("    diverges")

        raises_contracts = contracts.get("raises", [])
        if raises_contracts:
            for rc in raises_contracts:
                cond_str = self._expr_to_whyml(rc["condition"], spec_refs)
                lines.append(f"    raises {{ {rc['exc_type']} -> {cond_str} }}")
            declared_exc = {rc["exc_type"] for rc in raises_contracts}
            for exc in sorted(func_exceptions - declared_exc):
                lines.append(f"    raises {{ {exc} }}")
        elif func_exceptions:
            lines.append(f"    raises {{ {', '.join(sorted(func_exceptions))} }}")

        self._in_spec = False
        return lines

    def _collect_array_var_assigns(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Post-pass to `IRScanner.find_array_and_dict_vars`: variables
        assigned to `self.<method>(...)` calls where <method> returns
        `array int` should also be tracked as arrays. The static
        IRScanner can't see this without the cross-method return-type
        map (built in `transpile()`)."""
        found: Set[str] = set()
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                if isinstance(val, dict) and val.get("type") == "Call":
                    fn = val.get("func", "")
                    if fn.startswith("self."):
                        tail = fn[len("self."):]
                        cls = self._current_self_type
                        key = f"{cls}__{tail}" if cls else tail
                        ret = self._module_method_return_types.get(key)
                        if ret == "array int":
                            tgt = s.get("target", "")
                            if tgt:
                                found.add(tgt)
            for k in ("body", "orelse"):
                if k in s:
                    found |= self._collect_array_var_assigns(s[k])
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found |= self._collect_array_var_assigns(h.get("body", []))
        return found

    def _collect_dict_var_assigns(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Post-pass for body-dict / body-set local detection: variables
        whose RHS yields a `map int (option int)` value (via map-typed
        param Var, IfExpr branches, BinOp `|`/`&`/`-` between map-typed
        sides, etc.). Used to exclude them from the integer `ref 0`
        pre-declaration path."""
        found: Set[str] = set()
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                if isinstance(val, dict) and self._rhs_yields_map(val):
                    tgt = s.get("target", "")
                    if tgt:
                        found.add(tgt)
            for k in ("body", "orelse"):
                if k in s:
                    found |= self._collect_dict_var_assigns(s[k])
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found |= self._collect_dict_var_assigns(h.get("body", []))
        return found

    def _wrap_body_with_return_catch(self, body_code: str, return_type: str) -> str:
        """Wrap a function body with the `try ... with Return r -> r end`
        catch when early-returns can fire. Picks the right Return arm
        based on return type (unit / tuple_N / int). Array returns are
        intentionally not wrappable here — see `_handle_return_stmt` and
        the Class M auto-trust path."""
        arity = self._current_tuple_arity
        if return_type == "unit":
            return f"    try\n{body_code}\n    with Return_void -> () end"
        if arity > 0:
            return f"    try\n{body_code}\n    with Return_{arity} r -> r end"
        if return_type == "array int":
            return body_code
        return f"    try\n{body_code}\n    with Return r -> r end"

    def _emit_body_code(self, func: Dict[str, Any], body_stmts: List[Dict[str, Any]],
                         local_refs: Set[str], ghost_vars: Set[str], ref_params: Set[str],
                         is_method: bool, return_type: str) -> str:
        """Build the WhyML body code string with pre-declared ref variables.
        Mutates self._array_locals, self._has_early_ret."""
        bounded_int = func.get("bounded_int")
        append_targets = IRScanner.find_append_targets(body_stmts)
        # `_has_early_ret` gates the `try ... with Return r -> r end` wrap.
        # Module6 emits `raise (Return ...)` whenever `in_loop` is true at a
        # Return site, not only when `has_early_return` would catch it (an
        # Early-return that lives strictly inside a Try-body for instance
        # is missed by has_early_return because has_direct_return doesn't
        # recurse into Try). Unify the flag so the wrap is always present
        # when any raise-Return path is reachable.
        self._has_early_ret = (
            IRScanner.has_early_return(body_stmts)
            or IRScanner.has_in_loop_return(body_stmts)
        )
        body_array_vars, body_dict_vars = IRScanner.find_array_and_dict_vars(body_stmts)
        body_array_vars |= self._collect_array_var_assigns(body_stmts)
        body_dict_vars |= self._collect_dict_var_assigns(body_stmts)
        body_lambda_vars = IRScanner.find_lambda_vars(body_stmts)
        body_record_vars = IRScanner.find_record_vars(body_stmts, self._record_types)

        pre_decl_vars: Set[str] = {
            v for v in local_refs
            if v not in ghost_vars
            and v not in ref_params
            and v not in body_array_vars
            and v not in body_dict_vars
            and v not in body_lambda_vars
            and v not in body_record_vars
        }

        if is_method:
            initial_declared = {whyml_ident(v) for v in pre_decl_vars}
        else:
            initial_declared = set(ref_params) | {whyml_ident(v) for v in pre_decl_vars}

        body_code = self._stmts_to_whyml(
            body_stmts,
            local_refs | {f"{t}_len" for t in append_targets},
            initial_declared,
            "    ",
        )

        pfx = f"(0 : int{bounded_int})" if bounded_int else "0"
        # Formal parameters that are mutated in the body need their
        # entry value preserved when we promote them to refs. Shadow
        # with `let a = ref a in`; otherwise `let a = ref 0 in` would
        # silently zero out the parameter at function entry. Use the
        # unpolluted `_formal_params` set (not `_current_symbol_table`,
        # which also contains for-loop targets and ghost vars — those
        # are NOT bound at function entry and shadowing them with
        # `let X = ref X in` produces unbound-symbol errors).
        for var in sorted(pre_decl_vars):
            safe_var = whyml_ident(var)
            init = safe_var if var in self._formal_params else pfx
            body_code = f"    let {safe_var} = ref {init} in\n{body_code}"

        for tgt in sorted(append_targets):
            safe_tgt = whyml_ident(tgt)
            body_code = f"    let {safe_tgt}_len = ref {pfx} in\n{body_code}"
            if tgt not in local_refs and tgt not in ref_params:
                body_code = f"    let {safe_tgt} = Array.make 1024 0 in\n{body_code}"
                self._array_locals.add(tgt)

        if not body_code.strip():
            body_code = "    ()"
        if self._has_early_ret:
            body_code = self._wrap_body_with_return_catch(body_code, return_type)
        return body_code

    def _compute_return_type(self, func: Dict[str, Any], body_stmts: List[Dict[str, Any]]) -> str:
        """Compute the WhyML return type for one function, applying the
        `List[T] → array int`, `Set[T]`/`Dict[K, V]` → `map int (option int)`,
        and bounded-int overrides."""
        bounded_int = func.get("bounded_int")
        return_type = IRScanner.find_return_type(body_stmts)
        ann = func.get("return_annotation")
        if ann == "list" and return_type == "int":
            return_type = "array int"
        elif ann in ("set", "dict", "frozenset") and return_type == "int":
            return_type = "map int (option int)"
        if bounded_int and return_type == "int":
            return_type = f"int{bounded_int}"
        return return_type

    def _should_auto_trust_map_return(
            self, func: Dict[str, Any], func_trusted: bool) -> bool:
        """Class M sub-case for set/dict-typed returns. Functions declared
        `-> Set[T]` / `-> Dict[K, V]` with early returns inside `if`
        branches emit `raise (Return (map_update_some ...))` which Why3
        rejects because `Return int` can't carry a `map int (option int)`
        payload. Auto-trust so the body is skipped and the contract alone
        is emitted. Tracked in `self._auto_trusted_map_returns`."""
        if func_trusted:
            return False
        return func.get("return_annotation") in ("set", "dict", "frozenset")

    def _collect_map_typed_locals(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Single static pre-pass: find every body-local variable
        whose first assignment yields a map. Used by
        `_should_auto_trust_set_op` because the body-emission-time
        `_dict_locals` tracker isn't populated yet."""
        result: Set[str] = set()
        def walk(items: List[Dict[str, Any]]) -> None:
            for s in items:
                if s.get("stmt") == "Assign":
                    tgt = s.get("target", "")
                    if tgt and self._rhs_yields_map(s.get("value", {})):
                        result.add(tgt)
                for k in ("body", "orelse"):
                    if k in s:
                        walk(s[k])
                if s.get("stmt") == "While":
                    walk(s.get("body", []))
                if s.get("stmt") == "For":
                    walk(s.get("body", []))
                if s.get("stmt") == "Try":
                    walk(s.get("body", []))
                    for h in s.get("handlers", []):
                        walk(h.get("body", []))
        walk(stmts)
        return result

    def _test_contains_map(self, expr: Any, map_locals: Set[str]) -> bool:
        """Recursively check whether `expr` (an If/while test) contains
        a map-typed OR array-typed subexpression. Walks through
        UnaryOp(not, ...), BoolOp(and/or, ...), Compare wrappers —
        anywhere a collection could be used as a bool would trigger
        the `(X <> 0)` problem."""
        if not isinstance(expr, dict):
            return False
        if (expr.get("type") == "Var" and expr.get("name") in map_locals):
            return True
        if self._rhs_yields_map(expr) or self._rhs_yields_array(expr):
            return True
        for v in expr.values():
            if isinstance(v, dict):
                if self._test_contains_map(v, map_locals):
                    return True
            elif isinstance(v, list):
                for item in v:
                    if self._test_contains_map(item, map_locals):
                        return True
        return False

    def _has_set_op_on_map(self, obj: Any, map_locals: Optional[Set[str]] = None) -> bool:
        """Detect any IR shape that combines a map-typed value with an
        int-typed operation, anywhere in the subtree. Triggers when:

        - **Set operator**: `BinOp(|/&/^/-)` with a map operand. Python
          set union/intersect/xor/diff lower to `bit_or`/... typed
          `int -> int -> int`, mismatched against the map.
        - **For-iteration**: `For` whose iter expression yields a map.
          WhyML maps don't have a natural iteration model (they're
          functions, not collections); `iter_length`/`iter_get` are
          typed `int -> int`.
        - **Truthiness**: `If` whose test is a map-typed Var / field
          / call. Python `if d:` lowers to `(X <> 0)` which can't
          compare a map to int.

        There is no clean reduction to int because the map semantics
        are lost in any of these shapes; the only sound option is to
        auto-trust the enclosing function."""
        if map_locals is None:
            map_locals = set()
        def yields_map(node: Any) -> bool:
            if (isinstance(node, dict) and node.get("type") == "Var"
                    and node.get("name") in map_locals):
                return True
            return self._rhs_yields_map(node)
        if isinstance(obj, dict):
            t = obj.get("type", "")
            # Set operator on a map operand.
            if t == "BinOp" and obj.get("op") in ("|", "&", "^", "-"):
                if yields_map(obj.get("left", {})) or yields_map(obj.get("right", {})):
                    return True
            # `for x in map_val:` — iter expression is a map.
            if obj.get("stmt") == "For":
                if yields_map(obj.get("iter", {})):
                    return True
            # `if map_val:` / `if not map_val:` / `if X and map_val:` —
            # any map-typed subexpression appearing in an If test needs
            # auto-trust because Python truthiness on a map lowers to
            # `(M <> 0)` which Why3 rejects.
            if obj.get("stmt") == "If":
                if self._test_contains_map(obj.get("test", {}), map_locals):
                    return True
            for v in obj.values():
                if self._has_set_op_on_map(v, map_locals):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if self._has_set_op_on_map(item, map_locals):
                    return True
        return False

    def _should_auto_trust_set_op(
            self, body_stmts: List[Dict[str, Any]], func_trusted: bool) -> bool:
        """Auto-trust functions whose body uses a map-typed value in
        an int-typed context (set operators, for-loop iteration, or
        truthiness check). PyCSL lowers these to abstract vals typed
        in int, which type-mismatch against the `map int (option int)`
        operand. The semantics are unrecoverable from this lowering;
        auto-trust skips the body and emits a contract-only `val`.
        Tracked in `self._auto_trusted_set_op`."""
        if func_trusted:
            return False
        # Pre-scan: identify body-locals first-assigned from a
        # map-yielding RHS, so the recursive check can recognise
        # iter/test/operand vars beyond just self-fields and params.
        map_locals = self._collect_map_typed_locals(body_stmts)
        return self._has_set_op_on_map(body_stmts, map_locals)

    def _should_auto_trust_array_return(
            self, func: Dict[str, Any], body_stmts: List[Dict[str, Any]],
            return_type: str, func_trusted: bool) -> bool:
        """Class M workaround: array-returning functions with early returns
        cannot be cleanly wrapped — Why3 forbids carrying `array int` in
        exception payloads, and the `ref (option (array int))` slot pattern
        is rejected by Why3's region/linearity tracking when the function
        body uses `Array.make`. Force-trust such functions so the body is
        skipped and only the contract is emitted. See
        `docs/self-annotate-layer2-queue.md` class M for the full design."""
        if func_trusted or return_type != "array int":
            return False
        return (IRScanner.has_early_return(body_stmts)
                or IRScanner.has_in_loop_return(body_stmts))

    def _should_auto_trust_tuple_return(
            self, body_stmts: List[Dict[str, Any]], return_type: str,
            func_trusted: bool) -> bool:
        """Class O workaround: tuple-returning functions whose return Tuple
        has at least one array-typed slot. Module6 emits the function
        signature as homogeneous `(int, int, ...)` even when one element is
        `List[T]` (→ `array int`) and others are int. Auto-trust until
        per-slot type inference lands."""
        if func_trusted or not (return_type.startswith("(") and "," in return_type):
            return False
        array_vars, _dict_vars = IRScanner.find_array_and_dict_vars(body_stmts)
        array_vars |= self._collect_array_var_assigns(body_stmts)

        def _tuple_return_has_array_slot(stmts: List[Dict[str, Any]]) -> bool:
            for s in stmts:
                if s.get("stmt") == "Return":
                    val = s.get("value", {})
                    if isinstance(val, dict) and val.get("type") == "Tuple":
                        for elt in val.get("elts", []):
                            if (isinstance(elt, dict)
                                    and elt.get("type") == "Var"
                                    and elt.get("name") in array_vars):
                                return True
                for k in ("body", "orelse"):
                    if k in s and _tuple_return_has_array_slot(s[k]):
                        return True
                if s.get("stmt") == "Try":
                    for h in s.get("handlers", []):
                        if _tuple_return_has_array_slot(h.get("body", [])):
                            return True
            return False
        return _tuple_return_has_array_slot(body_stmts)

    def _emit_function(self, func: Dict[str, Any], scc_info: Dict[str, tuple]) -> List[str]:
        """Emit one WhyML let/val function block. Returns the list of output lines."""
        name = whyml_ident(func["name"])
        body_stmts = func["body"]
        is_method = func.get("kind") == "method"

        local_refs, ghost_vars = self._reset_function_state(func, body_stmts)
        ref_params, args_str = self._build_param_list(func, local_refs, ghost_vars)

        return_type = self._compute_return_type(func, body_stmts)
        # `_func_return_type` is read by `_handle_return_stmt` to pick
        # the right Return exception (int / array / tuple); set it AFTER
        # the `List[T] → array int` override so the array-Return slot
        # path fires.
        self._func_return_type = return_type
        self._current_tuple_arity = (
            return_type.count(",") + 1 if return_type.startswith("(") else 0
        )

        func_variants = func.get("function_variants", [])
        func_diverges = func.get("diverges", False)
        func_trusted = func.get("trusted", False)
        if self._should_auto_trust_map_return(func, func_trusted):
            func_trusted = True
            self._auto_trusted_map_returns = (
                self._auto_trusted_map_returns + [func["name"]])
        if self._should_auto_trust_array_return(func, body_stmts, return_type, func_trusted):
            func_trusted = True
            self._auto_trusted_array_returns = (
                self._auto_trusted_array_returns + [func["name"]])
        if self._should_auto_trust_tuple_return(body_stmts, return_type, func_trusted):
            func_trusted = True
            self._auto_trusted_tuple_returns = (
                self._auto_trusted_tuple_returns + [func["name"]])
        if self._should_auto_trust_set_op(body_stmts, func_trusted):
            func_trusted = True
            self._auto_trusted_set_op = (
                self._auto_trusted_set_op + [func["name"]])

        func_pure = func.get("pure", False)
        is_recursive = IRScanner.is_recursive(name, body_stmts)
        use_rec = bool(func_variants) or is_recursive
        can_emit_as_logic = func_pure and not local_refs and not is_method

        _scc_idx, _pos_in_scc, _scc_size = scc_info.get(func["name"], (0, 0, 1))
        is_and_clause = _pos_in_scc > 0 and not func_trusted and not can_emit_as_logic

        lines: List[str] = []
        if func_trusted:
            kw = f"val {name}"
        elif can_emit_as_logic:
            kw = f"{'let rec function' if use_rec else 'let function'} {name}"
        elif is_and_clause:
            kw = f"and {name}"
        else:
            kw = f"{'let rec' if (use_rec or _scc_size > 1) else 'let'} {name}"
        lines.append(f"  {kw} {args_str} : {return_type}" if args_str
                     else f"  {kw} () : {return_type}")

        spec_refs = set() if is_method else ref_params
        func_exceptions = IRScanner.collect_escaping_exceptions(body_stmts)
        lines += self._emit_contracts(func.get("contracts", {}), spec_refs,
                                      func_variants, func_diverges, func_exceptions)

        if func_trusted:
            lines.append("")
            return lines

        lines.append("  =")
        lines.append(self._emit_body_code(func, body_stmts, local_refs, ghost_vars,
                                          ref_params, is_method, return_type))
        if _pos_in_scc == _scc_size - 1:
            lines.append("")
        return lines

    # ------------------------------------------------------------------
    # transpile() — thin orchestrator
    # ------------------------------------------------------------------

    def _emit_opaque_class_aliases(self, functions: List[Dict[str, Any]],
                                    out: List[str], declared_types: Set[str]) -> None:
        """Emit `type <cls> = int` aliases for classes used as `self_type`
        in methods but not declared as records."""
        for func in functions:
            if func.get("kind") == "method" and func.get("self_type"):
                st = func["self_type"].lower()
                if st not in declared_types:
                    declared_types.add(st)
                    out.append(f"  type {st} = int")
                    out.append("")

    def _build_method_return_type_map(self, functions: List[Dict[str, Any]]) -> Dict[str, str]:
        """Map method name (un-prefixed, e.g. `_emit_contracts`) → declared
        WhyML return type, used by `_handle_dotted_call` to pick the right
        return-type for `self.<method>(...)` abstract vals. Without this,
        every `self.foo(...)` is abstracted as `val self__foo_<n> ... :
        int`, even when `foo` returns a list (→ `array int`) or a tuple,
        producing downstream type mismatches at the call site."""
        result: Dict[str, str] = {}
        for func in functions:
            ret = IRScanner.find_return_type(func["body"])
            ann = func.get("return_annotation")
            if ann == "list" and ret == "int":
                ret = "array int"
            elif ann in ("set", "dict", "frozenset") and ret == "int":
                # Functions annotated `-> Set[T]` / `-> Dict[K, V]` are
                # auto-trusted via `_should_auto_trust_map_return`; their
                # abstract `val` must announce the map return so callers
                # don't pre-decl a `ref 0` (int) target and then `:=` a
                # map.
                ret = "map int (option int)"
            result[func["name"]] = ret
        return result

    @staticmethod
    def _symtype_to_whyml(symtype: Optional[str]) -> str:
        """Convert a Module5 symbol-table type tag to the WhyML type used
        in abstract val parameter declarations. Defaults to `int`."""
        if symtype in ("set", "dict", "frozenset"):
            return "map int (option int)"
        if symtype in ("list", "tuple"):
            return "array int"
        return "int"

    def _build_method_param_types_map(self, functions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Map function name → list of WhyML parameter types (excluding
        self). Used by `_handle_dotted_call` to emit abstract `val` decls
        with matching parameter types so cross-method calls type-check
        when params are set/dict/list-typed."""
        result: Dict[str, List[str]] = {}
        for func in functions:
            symtable = func.get("symbol_table", {})
            body = func.get("body", [])
            local_assignees = IRScanner.find_assigned_vars(body)
            param_types: List[str] = []
            for name, symtype in symtable.items():
                # Locals (assigned inside the body) are NOT params.
                if name in local_assignees:
                    continue
                param_types.append(self._symtype_to_whyml(symtype))
            result[func["name"]] = param_types
        return result

    def _find_abstract_val_insert_idx(self, out: List[str]) -> int:
        """Pick the insertion point for the abstract-val block. Abstract
        vals may reference class record types (e.g. `val getattr_FooClass
        (x: fooclass) (f: int) : int`); those types are emitted by
        `_emit_type_decls` AFTER `_emit_preamble_helpers'` `let pycsl_div`
        / `let pycsl_mod`. Inserting at the first `let` would place the
        vals BEFORE their referenced types and Why3 would reject the file
        with "unbound type symbol".

        Strategy: if any `type ...` line exists in `out`, insert
        immediately after the LAST such line (skipping a trailing blank).
        Otherwise, fall back to the historical "insert before first `let`
        / non-ghost `val`" behaviour."""
        last_type_idx = -1
        for i, line in enumerate(out):
            if line.strip().startswith("type "):
                last_type_idx = i
        if last_type_idx >= 0:
            insert_idx = last_type_idx + 1
            if insert_idx < len(out) and out[insert_idx].strip() == "":
                insert_idx += 1
            return insert_idx
        for i, line in enumerate(out):
            stripped = line.strip()
            if stripped.startswith("let ") or stripped.startswith("let rec "):
                return i
            if stripped.startswith("val ") and "ghost" not in line:
                return i
        return len(out) - 1

    def _insert_abstract_val_block(self, out: List[str]) -> None:
        """Insert the abstract-val block (collected during transpilation)
        at the position selected by `_find_abstract_val_insert_idx`."""
        if not self._abstract_ops:
            return
        insert_idx = self._find_abstract_val_insert_idx(out)
        abs_lines = ["", "  (* Abstract operations for unsupported Python patterns *)"]
        for decl in sorted(self._abstract_ops.values()):
            abs_lines.append(f"  {decl}")
        abs_lines.append("")
        for line in reversed(abs_lines):
            out.insert(insert_idx, line)

    def transpile(self) -> str:
        """Entry point: converts the entire program to a .mlw string."""
        functions = self.ir.get("functions", [])
        type_decls = self.ir.get("type_decls", [])
        all_bodies = [func["body"] for func in functions]

        self._all_record_fields = self._collect_record_fields(type_decls)

        needs = self._scan_preamble_needs(functions, all_bodies)
        out = self._emit_preamble(needs)
        out += self._emit_shared_state()

        type_lines, declared_types = self._emit_type_decls(type_decls)
        out += type_lines

        self._emit_opaque_class_aliases(functions, out, declared_types)

        self._module_func_names = {whyml_ident(func["name"]) for func in functions}
        self._module_method_return_types = self._build_method_return_type_map(functions)
        self._module_method_param_types = self._build_method_param_types_map(functions)

        sorted_functions, scc_info = sort_functions_by_scc(functions)
        for func in sorted_functions:
            out += self._emit_function(func, scc_info)

        out.append("end")
        self._insert_abstract_val_block(out)
        return "\n".join(out)
