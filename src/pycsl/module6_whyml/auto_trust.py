from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from module6_whyml.ir_scanner import IRScanner


class AutoTrustMixin:
    """Auto-trust decisions and linear-VC classification.

    Auto-trust converts a function from `let` (full body emitted) to `val`
    (contract-only) when the body cannot be cleanly typed in WhyML — typically
    because map-typed values would need to flow through int-typed slots, or
    because array/tuple returns hit early-return restrictions.

    Linear-VC classification flags ensures/requires clauses that contain only
    linear arithmetic so the runner can route them to omega proofs in Lean 4
    instead of Why3/Alt-Ergo. See `docs/self-annotate-layer2-queue.md` for the
    auto-trust class taxonomy.
    """

    @staticmethod
    def _build_witness_str(field_names: List[str], vals: Dict[str, Any],
                           field_types: Optional[Dict[str, str]] = None,
                           array_lengths: Optional[Dict[str, int]] = None,
                           array_elem_witnesses: Optional[Dict[str, str]] = None) -> str:
        """Build a WhyML record literal witness string.

        Array-typed fields (`array int`) cannot take an int witness; they
        get `Array.make N 0`, where N is the length pinned by a class
        invariant `\\length(self.f) == N` (defaulting to 0 — an empty
        array — when no length invariant constrains the field). A
        `List[<record>]` field (`array <record>`, parser-primitives-wall-impl-2.md
        Gate S) instead gets `Array.make N <record-literal>` from
        `array_elem_witnesses` — the int `0` element would mistype against the
        record element."""
        field_types = field_types or {}
        array_lengths = array_lengths or {}
        array_elem_witnesses = array_elem_witnesses or {}
        parts: List[str] = []
        for fn in field_names:
            ft = field_types.get(fn, "int")
            if ft in ("list", "tuple", "bytes", "bytearray") or ft.startswith("array "):
                n = array_lengths.get(fn, 0)
                elem = array_elem_witnesses.get(fn, "0")
                parts.append(f"{fn} = (Array.make {n} {elem})")
            elif ft in ("dict", "set", "frozenset") or ft.startswith("map "):
                # Empty map witness (all keys → None); `const` is from
                # map.Const, matching the empty-dict idiom in expressions.py.
                parts.append(f"{fn} = (const (None: option int))")
            elif ft in ("real", "float"):
                # wrong-lowering-to-fix.md §WL-03b: a `real`-typed field (a faithful
                # `float` slot) needs a real witness literal — `0` is int-typed and
                # would mistype the record `by` clause. Additive: no pre-existing
                # corpus record has a real field, so this branch is only reached by a
                # float-field record that ALSO carries a class invariant.
                parts.append(f"{fn} = 0.0")
            elif ft in ("str", "string") or ft == "string":
                # b14 B1 prerequisite: a `str`-annotated field is Why3 `string`
                # (preamble.py `str`→`string`), so its witness must be the empty
                # string literal, not the int `0`. Purely additive — no
                # pre-existing corpus record reaches this branch (plain
                # `self.x = x` Assigns collapse to int; only an annotated
                # `self.x: str = x` AnnAssign yields a `string` field).
                parts.append(f'{fn} = ""')
            else:
                parts.append(f"{fn} = {vals.get(fn, 0)}")
        return "; ".join(parts)

    @staticmethod
    def _extract_elem_field_pins(invs: List[Any]) -> Dict[str, Dict[str, str]]:
        """Contract self-field subscript projection: scan class invariants for
        `self.<f>[<idx>].<sub> == "<literal>"` and return
        `{f: {sub: "<literal>"}}` — the STRING value the `array <record>` field
        `f`'s witness ELEMENT must carry for that invariant to hold.

        Sound because the `by` witness builds the array with `Array.make N <lit>`:
        every element is the SAME literal, so pinning `<sub>` to the required
        constant satisfies the invariant at every index, whatever `<idx>` is.
        Conflicting pins on the same `<sub>` are dropped (first wins is unsound),
        leaving the pre-existing empty-string default and an honestly failing
        inhabitance goal rather than a bogus witness.

        The matched IR is exactly what `Module5_IREmitter._csl_subscript_field`
        emits for the `self.`-prefixed base: `Attribute(Subscript(FieldGet(self,
        f), idx), sub)`. Absent (hence byte-inert) for every contract that does
        not use the form."""
        out: Dict[str, Dict[str, str]] = {}
        conflicts: Dict[str, set] = {}

        def _proj_of(node: Any):
            if not isinstance(node, dict) or node.get("type") != "Attribute":
                return None
            sub = node.get("attr")
            base = node.get("object")
            if not isinstance(base, dict) or base.get("type") != "Subscript":
                return None
            coll = base.get("value")
            if (not isinstance(coll, dict) or coll.get("type") != "FieldGet"
                    or coll.get("object") != "self"):
                return None
            if not isinstance(sub, str) or not isinstance(coll.get("field"), str):
                return None
            return coll["field"], sub

        def _str_of(node: Any):
            if isinstance(node, dict) and node.get("type") == "String":
                v = node.get("value")
                return v if isinstance(v, str) else None
            return None

        for inv in invs:
            if not isinstance(inv, dict) or inv.get("type") != "BinOp":
                continue
            if inv.get("op") not in ("==", "="):
                continue
            for a, b in ((inv.get("left"), inv.get("right")),
                         (inv.get("right"), inv.get("left"))):
                proj = _proj_of(a)
                lit = _str_of(b)
                if proj is None or lit is None:
                    continue
                fld, sub = proj
                prev = out.setdefault(fld, {}).get(sub)
                if prev is not None and prev != lit:
                    conflicts.setdefault(fld, set()).add(sub)
                out[fld][sub] = lit
        for fld, subs in conflicts.items():
            for sub in subs:
                out[fld].pop(sub, None)
        return {f: d for f, d in out.items() if d}

    @staticmethod
    def _extract_array_lengths(invs: List[Any]) -> Dict[str, int]:
        """Scan class invariants for a length constraint on an array field
        and return {field: N}, the length to give that field's witness in
        the record `by` clause. Handles `\\length(self.f) == N`,
        `\\length(self.f) >= N`, and the reversed `N <= \\length(self.f)`:
        an `Array.make N 0` witness (length exactly N) satisfies all three
        (N == N, N >= N, N <= N). Tolerates the constant on either side."""
        out: Dict[str, int] = {}

        def _field_of(node: Any) -> Optional[str]:
            if isinstance(node, dict) and node.get("type") == "ArrayLen":
                var = str(node.get("var", ""))
                return var[len("self."):] if var.startswith("self.") else var
            return None

        def _int_of(node: Any) -> Optional[int]:
            if isinstance(node, dict) and node.get("type") in ("Number", "Num", "Constant"):
                v = node.get("value", node.get("n"))
                if isinstance(v, (int, float)):
                    return int(v)
            return None

        for inv in invs:
            if not isinstance(inv, dict) or inv.get("type") != "BinOp":
                continue
            op = inv.get("op")
            if op not in ("==", "=", ">=", "<="):
                continue
            left, right = inv.get("left"), inv.get("right")
            f_left, f_right = _field_of(left), _field_of(right)
            # field-on-left forms: `len(f) == N`, `len(f) >= N`.
            if f_left is not None and op in ("==", "=", ">="):
                n = _int_of(right)
                if n is not None:
                    out.setdefault(f_left, n)
            # field-on-right forms: `N == len(f)`, `N <= len(f)`.
            elif f_right is not None and op in ("==", "=", "<="):
                n = _int_of(left)
                if n is not None:
                    out.setdefault(f_right, n)
        return out

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
        return all(AutoTrustMixin._is_linear_expr(e) for e in exprs)

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
        # A subscript/slice yields an element (int), not the collection —
        # `if arr[i] == 1:` / `if d[k]:` does NOT use the collection as a
        # truthiness operand. Consume it: check only the index, never
        # recurse into the collection base (which would mis-flag the
        # enclosing function for auto-trust).
        if expr.get("type") in ("Subscript", "SliceAccess", "ChainedSubscript"):
            for key in ("index", "index1", "index2"):
                idx = expr.get(key)
                if isinstance(idx, dict) and self._test_contains_map(idx, map_locals):
                    return True
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
