from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from module6_whyml.identifiers import op_translate, whyml_ident
from module6_whyml.ir_scanner import IRScanner


class ExpressionEmissionMixin:
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
            if self._in_spec:
                return f"(div {left} {right})"
            inner = f"(pycsl_div {left} {right})"
            return self._wrap_with_no_exception_assert(("binop", raw_op), [left, right], inner)
        if op == "mod":
            if self._in_spec:
                return f"(mod {left} {right})"
            inner = f"(pycsl_mod {left} {right})"
            return self._wrap_with_no_exception_assert(("binop", raw_op), [left, right], inner)
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
            # Strict-propagation mode (workplan §1.4): an unannotated
            # callee called from a function with `no_exception` is
            # treated pessimistically. Default mode preserves backward
            # compat — ambient.
            inner = f"({arity_fn} {' '.join(coerced_args) if coerced_args else '()'})"
            return self._wrap_unannotated_call_with_strict_assert(inner)
        # User-function call site. Look up the callee's raises summary;
        # if any clause names an exception the caller has committed to
        # avoid, prepend an assertion that the raises condition cannot
        # hold under the actual args.
        inner = f"({safe_fn} {' '.join(coerced_args) if coerced_args else '()'})"
        return self._wrap_call_with_callee_raises_assert(func_name, inner, args)

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
                inner = f"{value_str}[{index}]"
                # no_exception IndexError → assert in_bounds before the read.
                length_expr = f"(Array.length {value_str})"
                return self._wrap_with_no_exception_assert(
                    ("subscript", "read"), [length_expr, index], inner)
            elif is_dict:
                # Body dict subscript read: `d[k]` →
                # `match Map.get !d k with Some v -> v | None -> 0 end`.
                # For body-local dicts, `value_str` already includes the
                # `!` deref because `_handle_var_expr` treats them as
                # refs. For `self.<dict-field>` accesses, no deref is
                # needed (record-field access is direct).
                k = self._coerce_to_int(index)
                inner = f"(match Map.get {value_str} {k} with | Some v_ -> v_ | None -> 0 end)"
                # no_exception KeyError → assert has_key before the read.
                return self._wrap_with_no_exception_assert(
                    ("map_get", None), [value_str, k], inner)
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

