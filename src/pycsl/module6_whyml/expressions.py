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

    # ----- no-more-int F1: dict value-type (ν) dispatch, consolidated -----
    # A dict's value type ν ∈ {int (default), "string", "seq int", "map …"}
    # drives three emission decisions — the empty-map literal (first assignment),
    # the missing-key placeholder (subscript read), and the stored-value coercion
    # (subscript write). These were a parallel `if ν == … elif …` ladder
    # duplicated at each of the three sites; these helpers centralise that ladder.
    # Output is byte-identical to the former inline branches.

    def _dv_empty_default(self, nu: Optional[str]) -> Optional[str]:
        """Empty-map literal for a dict local's first assignment; `None` for an
        int dict (the caller keeps the `(const (None: option int))` it has)."""
        if nu == "string":
            return "(const (None: option string))"
        if nu == "seq int":
            return "(const (None: option (seq int)))"
        if nu and nu.startswith("map "):
            return f"(const (None: option ({nu})))"
        return None

    def _dv_missing_default(self, nu: Optional[str]) -> str:
        """`None ->` placeholder for a dict subscript read (typed per ν; proven
        dead under `#@ no_exception KeyError`, the ambient default otherwise)."""
        if nu == "string":
            return '""'
        if nu == "seq int":
            return "(Seq.empty: seq int)"
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
        if nu == "string" or (nu and nu.startswith("map ")):
            return val_expr
        return self._coerce_to_int(val_expr)

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
        # §B′: len(d[k]) where d is a seq-valued dict (`Dict[_, List[int]]`) — the
        # read is a `seq int`, so its length is `Seq.length`.
        if atype == "Subscript":
            _b = arg_ir.get("value", {})
            if (isinstance(_b, dict) and _b.get("type") == "Var"
                    and getattr(self, "_dict_value_types", {}).get(_b.get("name", "")) == "seq int"):
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
                if getattr(self, "_current_symbol_table", {}).get(var_name) in ("list", "dict"):
                    is_array = True
            if is_array:
                arg0 = f"({args[0]})" if args[0].startswith("!") else args[0]
                return f"(Array.length {arg0})"
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

        # inductive.md: an applied inductive predicate (`even(0)`, `wf(JArr(h, s))`)
        # is a logic-level predicate application — emit `(p args)` directly (raw args,
        # no int-coercion, no abstract op), exactly like a constructor application.
        if func_name in getattr(self, "_inductive_preds", set()):
            p = whyml_ident(func_name.lower())
            return f"({p} {' '.join(args)})" if args else p

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
        safe_fn = whyml_ident(func_name)
        if (func_name not in local_refs
                and func_name not in self._current_params
                and safe_fn not in self._module_func_names):
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
        if formal_params and len(args) < len(formal_params):
            defaults = self._module_method_param_defaults.get(func_name, {})
            for nm in formal_params[len(args):]:
                if nm in defaults:
                    args = args + [self._expr_to_whyml(defaults[nm], local_refs,
                                                       invariant_ctx, subst)]
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
        if param_types:
            coerced_args = self._coerce_dotted_args(args, param_types[:len(args)])
        else:
            coerced_args = [self._coerce_to_int(a) for a in args]
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
            all_args = [recv] + [self._expr_to_whyml(a, local_refs, invariant_ctx, subst)
                                 for a in args]
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
            return self._handle_isinstance(expr)
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
                self._add_abstract_op(
                    f"val {ctor}_new (x: array int) : array int\n"
                    f"    ensures {{ Array.length result = Array.length x }}\n"
                    f"    ensures {{ forall i:int. 0 <= i < Array.length x -> "
                    f"result[i] = x[i] }}")
                return f"({ctor}_new {args[0]})"
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
                        return '"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"'
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

    def _tag_of_type(self, t_name: Optional[str]) -> Optional[str]:
        """Tag for a *type name* (the 2nd arg of isinstance / a class / datatype).
        None ⇒ unknown target type (fully uninterpreted)."""
        if not t_name:
            return None
        if t_name in self._METATYPE_TAGS:
            return self._METATYPE_TAGS[t_name]
        if t_name.lower() in getattr(self, "_record_types", {}):
            return "tag_record"
        if t_name in getattr(self, "_variant_types", {}):
            return "tag_variant"
        return None

    def _tag_of_value(self, x_ir: Dict[str, Any]) -> str:
        """Tag of a *value* from Γ's τ (decision B: only a stable, concrete τ decides;
        `Any`/unstable/non-var → a free symbolic tag via `typeof_op`, so introspection on
        it stays unknown — never a wrong-decided)."""
        name = x_ir.get("name") if isinstance(x_ir, dict) and x_ir.get("type") == "Var" else None
        tag = self._tag_of_type(getattr(self, "_current_symbol_table", {}).get(name)) if name else None
        if tag is not None:
            return tag
        self._add_abstract_op("val typeof_op (n: int) : int")
        return f"(typeof_op {sum(ord(c) for c in name) if name else 0})"

    def _handle_isinstance(self, expr: Dict[str, Any]) -> str:
        """`isinstance(x, T)` → `subtag (\\typeof x) T` (decision: \\subtag, not ==, so a
        base type like `object` decides true and a leaf≠leaf decides false). Decided when
        x has a concrete τ; symbolic at the `Any` tail; fully uninterpreted if T is an
        unknown type."""
        args_ir = expr.get("args", [])
        t_name = args_ir[1].get("name") if isinstance(args_ir[1], dict) else None
        t_tag = self._tag_of_type(t_name)
        if t_tag is None:
            self._add_abstract_op("val isinstance_op (x: int) (t: int) : bool")
            return "(isinstance_op 0 0)"
        self._emit_metatype_tags()
        return f"(subtag {self._tag_of_value(args_ir[0])} {t_tag})"

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

    def _handle_subscript(self, expr: Dict[str, Any], local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        value = expr["value"]
        index = self._expr_to_whyml(expr["index"], local_refs, invariant_ctx, subst)
        # 07-1705-rev4 P3/P5: element read of a seq-modelled list local is `Seq.get` —
        # BODY context only (in a contract a seq-promoted param is the array entry value).
        if (isinstance(value, dict) and value.get("type") == "Var"
                and value.get("name") in getattr(self, "_seq_locals", set())
                and not self._in_spec):
            base = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)  # `!a`
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
                var_name in getattr(self, "_inline_array_temps", set()) or
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
                # arity2.md (2b): parenthesise a ref-bound array deref (`!x`)
                # before subscripting, else `!x[i]` parses as `!(x[i])`.
                arr_e = f"({value_str})" if value_str.startswith("!") else value_str
                inner = f"{arr_e}[{index}]"
                # no_exception IndexError → assert in_bounds before the read.
                length_expr = f"(Array.length {arr_e})"
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
                # The missing-key placeholder is typed per ν (consolidated).
                default = self._dv_missing_default(
                    getattr(self, "_dict_value_types", {}).get(dvar))
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
        # 07-0903 W2: `\result.<field>` — field access on a record-returning function's
        # result. The WhyML result is the record value; emit `result.<field_label>`.
        if isinstance(obj_ir, dict) and obj_ir.get("type") == "Result":
            return f"result.{self._field_label(getattr(self, '_func_return_type', None), attr)}"
        # scc3.md Phase A: a quantifier-bound record var `o : C` (registered by
        # `_push_quant_binder`) — `o.field` is the record field, qualified via
        # `_field_label`, not an abstract `get_field` stub. (The class invariant is
        # already a Why3 type invariant on `c`, so the quantifier is sound.)
        if isinstance(obj_ir, dict) and obj_ir.get("type") == "Var":
            _vn = obj_ir.get("name", "")
            _qcls = self._quant_record_binders.get(_vn)
            if _qcls is not None:
                _cl = self._record_types[_qcls]["whyml_name"]
                return f"{whyml_ident(_vn)}.{self._field_label(_cl, attr)}"
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
            _cv = self._module_constants[name]
            # 0442.md C5 (no-more-int): a string-literal constant folds to a real Why3
            # string literal, not an int hash; an int constant folds to its value.
            if isinstance(_cv, str):
                return '"' + _cv.replace("\\", "\\\\").replace('"', '\\"') + '"'
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

    def _quant_binder_whyml(self, binder_type: Optional[str]) -> str:
        """quantification.md: map a quantifier binder type to its WhyML sort.
        `None` ⇒ legacy `int` (emitted verbatim → byte-identical for every existing
        quantifier). Scalars map int→int / bool→bool / str→string / float→real; a
        declared `#@ datatype` or class name lowers to its Why3 type (lowercased,
        e.g. `Color`→`color`). Module 4 has already rejected an unresolved name."""
        if binder_type is None:
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
            return ("noop", None)
        had = var in self._quant_record_binders
        prev = self._quant_record_binders.get(var)
        self._quant_record_binders[var] = binder_type
        return (had, prev)

    def _pop_quant_binder(self, var: Optional[str], token) -> None:
        kind, prev = token
        if kind == "noop":
            return
        if kind == "dict":
            if not prev:                      # was not previously a dict local
                self._dict_locals.discard(var)
            return
        if kind:
            self._quant_record_binders[var] = prev
        else:
            self._quant_record_binders.pop(var, None)

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
        if op == "~":
            # 0442.md C4: Python bitwise NOT on the int model is the two's-complement
            # identity `~x == -x - 1` (genuine int op, not a type-class leak).
            return f"((- {e}) - 1)"
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
            # 07-1705-rev4 P3/P5: `\length(a)` of a seq-modelled list — BODY context only.
            # In a pre/post-condition a seq-promoted *param* names the original `array int`
            # entry value (the body seq shadow is out of scope), so fall through to
            # `Array.length` there.
            if var in getattr(self, "_seq_locals", set()) and not self._in_spec:
                deref = "!" if var in local_refs else ""
                return f"(Seq.length {deref}{whyml_ident(var)})"
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

    def _handle_in_globals_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                                invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> str:
        """07-1839 P2: `\\in_globals(name)` — three-valued, true-only lower bound.
        decided-true (→ `true`) for a declared module binding; UNKNOWN otherwise → an
        uninterpreted bool (`in_globals_op`), so it is neither provably true nor false
        (open world: import/exec may inject the name). The unsound decided-false direction
        is never emitted."""
        name = expr.get("name", "")
        if name in self._module_binding_names():
            return "true"
        self._add_abstract_op("val in_globals_op (n: int) : bool")
        return f"(in_globals_op {sum(ord(c) for c in name)})"

    def _handle_in_scope_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                              invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> str:
        """07-1839 P3: `\\in_scope(name)` — three-valued via definite-assignment.
        decided-true (→ `true`) if `name` is assigned on all paths (param or top-level
        assignment before any branch/return); decided-false (→ `false`) if `name` is
        neither a param nor assigned anywhere; UNKNOWN (conditionally assigned) → an
        uninterpreted bool. A dynamic exec havocs the binding set, so the decided-false
        direction is withheld afterwards (decision C)."""
        name = expr.get("name", "")
        if name in getattr(self, "_scope_must", set()):
            return "true"
        if (not getattr(self, "_scope_dyn_exec", False)
                and name not in getattr(self, "_scope_all", set())
                and name not in getattr(self, "_scope_params", set())):
            return "false"
        self._add_abstract_op("val in_scope_op (n: int) : bool")
        return f"(in_scope_op {sum(ord(c) for c in name)})"

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

    def _handle_permutation_expr(
        self,
        expr: Dict[str, Any],
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
        a = self._expr_to_whyml(expr["left"], local_refs, invariant_ctx, subst)
        b = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
        if self._value_semantic:
            self._add_abstract_op("predicate permut (a: array int) (b: array int)")
            return f"(permut {a} {b})"
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
        if t == "Forall":
            bty = self._quant_binder_whyml(expr.get("binder_type"))
            saved = self._push_quant_binder(expr.get("var"), expr.get("binder_type"))
            body = self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)
            self._pop_quant_binder(expr.get("var"), saved)
            return f"(forall {expr['var']} : {bty}. {body})"
        if t == "Exists":
            bty = self._quant_binder_whyml(expr.get("binder_type"))
            saved = self._push_quant_binder(expr.get("var"), expr.get("binder_type"))
            body = self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)
            self._pop_quant_binder(expr.get("var"), saved)
            return f"(exists {expr['var']} : {bty}. {body})"
        if t == "ForallItems":
            # 07-1311 Q3: `\forall k, v in d.items(); P` → over the map+option model,
            # `forall k. match Map.get d k with Some v -> P | None -> true end`. The value
            # `v` is bound by the match; the key `k` (int) by the outer forall. Register
            # the map binder so a nested `d2[k]` in the body still lowers correctly.
            key, val = expr["key"], expr["val"]
            body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
            return (f"(forall {key} : int. match Map.get ({expr['map']}) ({key}) with "
                    f"| Some {val} -> {body} | None -> true end)")
        if t == "MapValueIs":
            # 07-1311 Q3: `\exists k. d[k] = Some v` — the value-membership witness for
            # `\forall v in d.values(); …`. A pure logic term over the `map`+`option` model.
            key = self._expr_to_whyml(expr["key"], local_refs, invariant_ctx, subst)
            val = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx, subst)
            return f"(Map.get ({expr['map']}) ({key}) = Some ({val}))"
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

