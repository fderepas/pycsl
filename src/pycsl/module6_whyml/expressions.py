from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from module6_whyml.identifiers import op_translate, whyml_ident
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
            return str(hash(whyml_str) % 2147483647)
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
            return str(hash(whyml_str) % 2147483647)
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
        # strings-plan Stage 2: `needle in haystack` for strings is substring containment, an
        # uninterpreted bool op over string operands (content witness deferred — see plan).
        if self._is_string_expr(rhs):
            # strings-plan Stage 4: the containment witness. `needle in haystack` holds iff
            # `needle` occurs as a contiguous substring at some position — the existential
            # content goal Gate B flagged as the hard one. As an abstract `val` the `ensures`
            # is assumed (axiomatic), so callers get the witness in both directions: a known
            # occurrence proves membership true, and membership true yields a matching index.
            self._add_abstract_op(
                "val str_contains_op (haystack: string) (needle: string) : bool\n"
                "    ensures { result <->\n"
                "      (exists i: int. 0 <= i /\\\n"
                "        i + String.length needle <= String.length haystack /\\\n"
                "        String.substring haystack i (String.length needle) = needle) }")
            scall = f"(str_contains_op {right} {left})"
            return f"(not {scall})" if negate else scall
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
        # `val function` (Why3 idiom for "pure program + logic symbol"):
        # bit_and / bit_or / bit_xor / bit_lshift / bit_rshift / py_pow
        # are pure mathematical operations on int. `val function`
        # declares both a program-callable and a logical symbol, so
        # the body can call them AND `#@ proof rocq` axioms can
        # constrain them (axioms can only reference logical symbols).
        self._add_abstract_op(f"val function {op_fn} (x: int) (y: int) : int")
        return f"({op_fn} {self._coerce_to_int(left)} {self._coerce_to_int(right)})"

    def _is_string_expr(self, ir: Dict[str, Any]) -> bool:
        """True if an IR expression is string-typed: a literal, a string-producing op, or a
        `str`-typed variable. (strings-plan Stage 2 — used to route `+` to `concat`.)"""
        t = ir.get("type")
        if t == "String" or t in ("StrConcat", "StrSub"):
            return True
        if t == "Var":
            return getattr(self, "_current_symbol_table", {}).get(ir.get("name", "")) == "str"
        # Indexing/slicing a string yields a string (s[i] is a 1-char string, s[a:b] a
        # substring) — both reuse str_sub_op in their handlers, so the *result* of such a
        # node is string-typed exactly when its base is. Required so `s[a:b] == t` routes to
        # the real string-equality bridge rather than the mixed int-hash fallback (0471).
        if t in ("Subscript", "SliceAccess"):
            return self._is_string_expr(ir.get("value", {}))
        # `s + t` is a `BinOp(+)` node (string concatenation when both operands are
        # strings) — so a concat expression is itself string-typed. Required so e.g.
        # `len(s + t)` routes to str_length_op rather than the opaque iter_length.
        if t == "BinOp" and ir.get("op") == "+":
            return (self._is_string_expr(ir.get("left", {}))
                    and self._is_string_expr(ir.get("right", {})))
        return False

    def _is_float_expr(self, ir: Dict[str, Any]) -> bool:
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
            return str(hash(whyml_str) % 2147483647)
        self._add_abstract_op("val str_hash_op (s: string) : int")
        return f"(str_hash_op {whyml_str})"

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
            ls = self._is_string_expr(expr["left"])
            rs = self._is_string_expr(expr["right"])
            if ls and rs:
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                eq = f"(str_eq_op {left} {right})"
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
        if fn_short == "chain":
            if not args_ir:
                return "0"
            parts = []
            for sub in args_ir:
                p = self._iter_len_expr(sub, local_refs)
                if p is None:
                    p = f"(Array.length {self._expr_to_whyml(sub, local_refs)})"
                parts.append(p)
            return "(" + " + ".join(parts) + ")"
        return None

    def _handle_len_call(self, expr: Dict[str, Any], args: List[str]) -> str:
        """Handle len(x): constant fold literals, array length in hoare model, or abstract.
        (The `len(list(chain(…)))` itertools case is resolved earlier in
        `_handle_call_expr` via `_iter_len_expr`, before the inner args are lowered.)"""
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
            param_types = self._module_method_param_types.get(lookup_key, [])
            # Propagate the callee's result-only postconditions onto the
            # stub (array length, slot bounds, …) so the caller can
            # discharge VCs on the returned value. Param-referencing clauses
            # (already renamed to the stub's x_i) propagate too — e.g.
            # `\array_eq(\result, data)`.
            result_ensures = (
                getattr(self, "_module_method_result_ensures", {}).get(lookup_key, [])
                + getattr(self, "_module_method_param_result_ensures", {}).get(lookup_key, []))
            field_ens = getattr(self, "_module_method_field_result_ensures", {}).get(lookup_key, [])
            if field_ens and cls:
                # `self.<m>()` called from a sibling method: the enclosing
                # method's own `self` is the receiver, typed as the class.
                field_spec = ("self", cls, field_ens)
        else:
            # `<recordvar>.method(...)` — resolve the receiver's class so the
            # callee's result-only `ensures` propagates to this call site,
            # exactly like `self.method(...)`. Without this the call lowered to a
            # bare abstract op with no `ensures`, so a driver function that
            # constructs an instance and calls a method could prove nothing
            # about the result.
            matched_instance = False
            rv_classes = getattr(self, "_current_record_var_classes", {})
            parts = func_name.split(".")
            if len(parts) == 2 and parts[0] in rv_classes:
                cls = rv_classes[parts[0]].lower()
                lookup_key = f"{cls}__{parts[1]}"
                rens = getattr(self, "_module_method_result_ensures", {})
                prens = getattr(self, "_module_method_param_result_ensures", {})
                if (lookup_key in self._module_method_return_types
                        or lookup_key in rens or lookup_key in prens):
                    ret_type = self._module_method_return_types.get(lookup_key, "int")
                    param_types = self._module_method_param_types.get(lookup_key, [])
                    result_ensures = rens.get(lookup_key, []) + prens.get(lookup_key, [])
                    fens = getattr(self, "_module_method_field_result_ensures", {})
                    field_ens = fens.get(lookup_key, [])
                    if field_ens:
                        # `b.<m>()`: the receiver record `b` becomes the
                        # abstract op's leading `(self: cls)` parameter.
                        field_spec = (parts[0], cls, field_ens)
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
        coerced = self._coerce_dotted_args(args, param_types)
        # A2c: a self-FIELD-referencing callee ensure (`\result == self.x`) is
        # bound by giving the abstract op a leading receiver parameter
        # `(self: <class>)` and passing the receiver record, so `self.x` in the
        # propagated clause resolves to the actual instance's field.
        receiver_param = ""
        if field_spec is not None:
            receiver_expr, receiver_class, _ = field_spec
            receiver_param = f"(self: {receiver_class}) "
            coerced = [receiver_expr] + coerced
        ensures_suffix = self._dotted_ensures_suffix(result_ensures, n, param_types, field_spec)
        if n == 0 and not receiver_param:
            self._add_abstract_op(f"val {arity_name} () : {ret_type}{ensures_suffix}")
            return f"({arity_name} ())"
        params = " ".join(f"(x{i}: {ptype})" for i, ptype in enumerate(param_types))
        params = f"{receiver_param}{params}".rstrip()
        self._add_abstract_op(f"val {arity_name} {params} : {ret_type}{ensures_suffix}")
        return f"({arity_name} {' '.join(coerced)})"

    def _coerce_dotted_args(self, args: List[str], param_types: List[str]) -> List[str]:
        """Coerce each dotted-call arg to its declared param type. The caller's arg may be
        int while the param expects array or map (e.g. an int from an abstract `get_*`
        accessor flowing into a `Set[T]` slot). (Extracted from `_handle_dotted_call`.)"""
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
        return coerced

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
        if not result_ensures and not field_ensures:
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
        if field_ensures:
            _prev_self = self._current_self_type
            self._current_self_type = field_spec[1]   # receiver class
            for e in field_ensures:
                w = self._expr_to_whyml(e, set())
                ensures_suffix += f"\n    ensures {{ {w} }}"
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
        parsed = parse_format(fmt)
        if parsed is None:
            return None   # Unsupported char in format

        slot_id = parsed.slot_id()
        if func_name == "struct.unpack":
            # struct.unpack(fmt, data) → (t1, ..., tN)
            # Abstract: val struct_unpack_<slot_id> (fmt: int) (data: array int) : (t1, ..., tN)
            if parsed.arity == 0:
                ret_type = "unit"
            elif parsed.arity == 1:
                ret_type = parsed.slots[0]
            else:
                ret_type = "(" + ", ".join(parsed.slots) + ")"
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

    def _handle_call_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        func_name = expr["func"]
        # A3 (bounded itertools): resolve `len(list(chain(…)))` / `len(chain(…))`
        # to a sum of `Array.length` BEFORE lowering the inner args, so the
        # opaque `chain_*`/`list_new` abstract ops are never emitted.
        if func_name == "len" and len(expr.get("args", [])) == 1:
            _le = self._iter_len_expr(expr["args"][0], local_refs or set())
            if _le is not None:
                return _le
        args = [self._expr_to_whyml(a, local_refs, invariant_ctx, subst) for a in expr["args"]]

        # sum-types: an applied `#@ datatype` constructor (`Circle(5)`) builds the variant.
        if func_name in self._constructors:
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
        if "." in func_name:
            return self._handle_dotted_call(func_name, args)
        rec = self._call_record_constructor(args, func_name)
        if rec is not None:
            return rec
        bytes_call = self._call_bytes_methods(args, func_name)
        if bytes_call is not None:
            return bytes_call
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

    def _content_string_method(self, expr: Dict[str, Any], args: List[str],
                               func_name: str, local_refs: Set[str],
                               invariant_ctx: bool,
                               subst: Optional[Dict[str, str]]) -> Optional[str]:
        """strings-plan Stage 3: content-aware `str` methods with a substring-based witness.

        `s.startswith(p)` / `s.endswith(p)` / `s.find(sub)` are lowered to abstract ops whose
        `ensures` relate the (int) result to `String.substring` over the *receiver as an
        operand*. Applies ONLY to a simple, `str`-typed receiver with a single string
        argument; a chained receiver (`node.name.startswith(…)`) or a non-`str` receiver
        falls through to the opaque baked-into-the-name predicate path. startswith/endswith
        keep the 0/1 int result (so control-flow / `\result ∈ {0,1}` uses are unaffected) and
        gain a `(result = 1) <-> <substring condition>` clause; find returns an index ≥ -1
        with a found-index witness."""
        if "." not in func_name:
            return None
        recv, method = func_name.rsplit(".", 1)
        if method not in ("startswith", "endswith", "find"):
            return None
        if "." in recv or self._current_symbol_table.get(recv) != "str":
            return None
        if len(args) != 1 or not self._is_string_expr(expr["args"][0]):
            return None
        r = self._expr_to_whyml({"type": "Var", "name": recv}, local_refs,
                                invariant_ctx, subst)
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

    def _call_named_builtins(self, expr: Dict[str, Any], args: List[str],
                             func_name: str, local_refs: Optional[Set[str]] = None,
                             invariant_ctx: bool = False,
                             subst: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Named builtins and built-in-method idioms: len / min / max / string-predicate
        methods / isinstance / set / sorted / any / all / dict / list / join /
        str|repr|int|bool|abs / sum / hasattr. Returns the WhyML string, or None to fall
        through to the generic call path. (Extracted verbatim from `_handle_call_expr`.)"""
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
        return None

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

    def _call_record_constructor(self, args: List[str], func_name: str) -> Optional[str]:
        """`C(...)` for a known record type → a WhyML record literal with per-field,
        type-correct values. Returns None only if `func_name` is not a known record
        type. (Extracted from `_handle_call_expr`.)

        base_op.md Tier A — parametrized construction: when `C(a, b)` is called with
        args matching `__init__`'s formals, each scalar field whose `__init__` body
        set it from those params (`init_body`, captured by Module5) is initialised by
        substituting the actual args for the params; all other fields keep their
        type-correct default. A 0-arg `C()`, an arity mismatch, or a non-scalar /
        non-param-dependent field all fall back to the default witness (sound)."""
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
                return f"(Array.make {rec_info['defaults'].get(fn, 0)} 0)"
            if ft in ("dict", "set", "frozenset"):
                return "(const (None: option int))"
            return f"{rec_info['defaults'].get(fn, 0)}"

        # Parametrized overrides: map each param-initialised scalar field to its
        # arg-substituted value. Only when the call arity matches `__init__`. The
        # already-lowered arg strings are spliced in via `RawWhyml` IR nodes (a value
        # substitution — `subst` is a variable-RENAME map, not a value-injection one).
        init_map: Dict[str, str] = {}
        init_params = rec_info.get("init_params", [])
        init_body = rec_info.get("init_body", [])
        if args and init_params and len(args) == len(init_params):
            arg_nodes = {init_params[i]: {"type": "RawWhyml", "whyml": args[i]}
                         for i in range(len(init_params))}
            for ent in init_body:
                fn = ent["field"]
                # Only scalar (int-modelled) fields take a substituted value; a
                # list/dict/set field keeps its typed default (array/map construction
                # over a param is out of Tier-A scope).
                if field_types.get(fn, "int") in ("list", "array", "dict", "set", "frozenset"):
                    continue
                init_map[fn] = self._expr_to_whyml(
                    self._subst_params(ent["value"], arg_nodes), set())

        field_inits = "; ".join(
            f"{self._field_label(rec_lower, fn)} = {init_map.get(fn, _field_default(fn))}"
            for fn in rec_info["fields"]
        )
        return f"{{ {field_inits} }}"

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
                "(struct_pack", "(encode_", "(ljust_", "(rjust_", "(zfill_")
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
        self._add_abstract_op(f"val {arity_fn} {params} : array int")
        return f"({arity_fn} {' '.join(cargs) if cargs else '()'})"

    def _handle_subscript(self, expr: Dict[str, Any], local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        value = expr["value"]
        index = self._expr_to_whyml(expr["index"], local_refs, invariant_ctx, subst)
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
                if _nu and _nu.startswith("map "):
                    _inner_v = (_nu.split("(option ", 1)[1].rsplit(")", 1)[0]
                                if "(option " in _nu else "int")
                    _idef = '""' if _inner_v == "string" else "0"
                    # inner key κi: int keys are hashed, string keys pass through.
                    _k = index if "map string" in _nu else self._coerce_to_int(index)
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
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict and var_name:
                st = getattr(self, "_current_symbol_table", {})
                if st.get(var_name) == "list":
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
                dvar = value.get("name", "") if value.get("type") == "Var" else ""
                # no-more-int-3 A1 T1.2: a string KEY (κ) is passed through
                # unhashed (`map string …`); T1.1: a string VALUE reads back a
                # `string`, so the `None` arm is a typed placeholder (`""`) —
                # proven dead under `#@ no_exception KeyError` (faithful read),
                # the ambient default otherwise.
                if getattr(self, "_dict_key_types", {}).get(dvar) == "string":
                    k = index
                else:
                    k = self._coerce_to_int(index)
                _nu = getattr(self, "_dict_value_types", {}).get(dvar)
                if _nu == "string":
                    default = '""'
                elif _nu and _nu.startswith("map "):
                    # A1-residual: a nested-map value reads back a map; the
                    # `None` placeholder is the empty inner map (option-payload
                    # = the inner value type). Proven dead under no_exception.
                    inner_v = (_nu.split("(option ", 1)[1].rsplit(")", 1)[0]
                               if "(option " in _nu else "int")
                    default = f"(const (None: option {inner_v}))"
                else:
                    default = "0"
                inner = f"(match Map.get {value_str} {k} with | Some v_ -> v_ | None -> {default} end)"
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
        # module-constants-plan: a module-level int constant resolves to its literal,
        # in both body and contract (so e.g. `kinds[0] == K_IHDR` discharges). Comes
        # after the local/param/shared checks, so a same-named local correctly shadows
        # it. Replaces the opaque `val constant` for these names.
        if name in self._module_constants:
            return f"({self._module_constants[name]})"
        # sum-types: a nullary `#@ datatype` constructor used as a value (`Red`).
        if name in self._constructors and self._constructors[name]["arity"] == 0:
            return name
        safe = whyml_ident(name)
        self._add_abstract_op(f"val constant {safe} : int")
        return safe

    def _field_label(self, record_lower: Optional[str], field: str) -> str:
        """WhyML label for a record field. Ambiguous names (shared by >1
        record, e.g. an inherited field) are qualified `<record>_<field>` to
        avoid Why3's global field-label collision; unique names stay bare."""
        base = whyml_ident(field)
        if field in getattr(self, "_ambiguous_fields", set()) and record_lower:
            return f"{whyml_ident(record_lower)}_{base}"
        return base

    def _handle_field_get_expr(self, expr: Dict[str, Any], invariant_ctx: bool) -> str:
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
        if not self._value_semantic and inner.get("type") == "Subscript":
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
        if inner.get("type") == "Subscript" and not self._value_semantic:
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
        # strings-plan Stage 2: `s[a:b]` on a string is `String.substring s a (b-a)`. Spec
        # uses the logic symbol; body bridges through `str_sub_op` (and `str_length_op` for an
        # omitted upper bound), since `String.substring`/`String.length` aren't program values.
        if self._is_string_expr(expr["value"]):
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
        lo = self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst) if sl.get("lower") else "0"
        hi = self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst) if sl.get("upper") else f"(Array.length {arr})"
        # A known-array source (record array-field like `self.disk`, or an
        # array local/param) gets real `Array.sub` semantics: the result has
        # known length `hi-lo` and content `result[i] = arr[lo+i]`, so the
        # prover can reason about read-back content (needed for round-trip
        # proofs). Why3's `Array.sub` carries the bounds preconditions
        # (`0<=lo`, `0<=len`, `lo+len <= length arr`), discharged from the
        # caller's `requires`/invariants. Only genuinely-int sources (e.g.
        # `str_conv s` for a sliced string param) fall back to the opaque
        # `array_slice` placeholder.
        val = expr["value"]
        is_array_src = False
        if val.get("type") in ("Attribute", "FieldGet"):
            if self._field_type_of(val) in ("list", "tuple", "bytes", "bytearray"):
                is_array_src = True
        elif val.get("type") == "Var":
            vn = val.get("name", "")
            if (vn in getattr(self, "_array_locals", set()) or
                    vn in getattr(self, "_current_array1d_params", set()) or
                    self._current_symbol_table.get(vn) == "list"):
                is_array_src = True
        if is_array_src:
            return f"(Array.sub {arr} ({lo}) (({hi}) - ({lo})))"
        self._add_abstract_op("val array_slice (a: array int) (lo: int) (hi: int) : array int")
        arr = self._array_coerce_arg(arr)
        return f"(array_slice {arr} {lo} {hi})"

    def _handle_arraylen_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self._value_semantic:
            var = expr['var']
            if var == "\\result":
                return "(Array.length result)"
            if var.startswith("self."):
                field = var[len("self."):]
                # Mirror `_handle_field_get_expr`: in a type/class invariant
                # the record fields are bare; in a method contract `self`
                # is an in-scope parameter.
                ref = field if invariant_ctx else f"self.{field}"
                return f"(Array.length {ref})"
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
        if self._value_semantic:
            return f"({length} >= 0 && {length} <= Array.length {base})"
        return f"(valid !{self._heap_var} {base} {length})"

    def _handle_separated_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self._value_semantic:
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
        if self._value_semantic:
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
        if self._value_semantic:
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
        if self._value_semantic:
            return f"(forall _si : int. {lo} <= _si /\\ _si < {hi} - 1 -> {base}[_si] <= {base}[_si + 1])"
        return "true"

    def _handle_arrayeq_expr(
        self,
        expr: Dict[str, Any],
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
        a = self._expr_to_whyml(expr["left"], local_refs, invariant_ctx, subst)
        b = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return (f"((Array.length {a} = Array.length {b}) /\\ "
                    f"(forall _ae : int. 0 <= _ae /\\ _ae < Array.length {a} "
                    f"-> {a}[_ae] = {b}[_ae]))")
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
        if self._value_semantic:
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

    def _expr_to_whyml(self, expr: Dict[str, Any], local_refs: Set[str],
                       invariant_ctx: bool = False,
                       subst: Optional[Dict[str, str]] = None) -> str:
        """Recursively translates an expression dictionary into a WhyML string.
        When invariant_ctx is True, FieldGet emits bare field names (for record invariants).
        subst: optional name substitution dict applied before local_refs lookup (e.g. for-loop vars)."""
        if not expr: return ""
        t = expr["type"]

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
            escaped = expr["value"].replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        if t == "Result":   return "result"
        if t == "None":     return "0"
        if t == "ArrayLit":
            elts = expr.get("elts", [])
            if elts:
                # Build a concrete `array int` of the literal's elements:
                # `(let _alit = Array.make N e0 in _alit[1] <- e1; …; _alit)`.
                n = len(elts)
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
            # Why3 string.String exports 'concat' (not '^' / 'String.(^)', which is unbound) —
            # mirror _handle_strconcat_expr; `String.(^)` here made any `^` in a spec context
            # (check/ensures comparison) emit an unbound symbol.
            return f"(concat {l} {r})"
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

