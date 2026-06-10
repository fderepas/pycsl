from __future__ import annotations

from typing import Any, Dict, List, Set

from module6_whyml.identifiers import whyml_ident, safe_exc_name
from module6_whyml.ir_scanner import IRScanner


class ControlFlowStmtMixin:
    """Control-flow statement handlers — `while` / `for` / `if` / `try` / `match`
    / `return` — plus their private helpers (`_classify_iterable`,
    `_first_assign_value_ir`, `_try_local_decl_kind`).

    Extracted verbatim from `StatementEmissionMixin` (Part B move 3e, mirroring
    the expressions.py split). `StatementEmissionMixin` inherits this mixin, so
    the handlers resolve via MRO through the facade's `_STMT_HANDLERS` table and
    recurse back into the core `self._stmts_to_whyml` / `self._expr_to_whyml`
    (which stay in `StatementEmissionMixin`)."""

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
        if not self._value_semantic:
            iter_expr = self._expr_to_whyml(iter_ir, local_refs)
            return f"{iter_expr}_len", f"Map.get !{self._heap_var} ({iter_expr} + !{idx})", False
        iter_expr = self._coerce_to_int(self._expr_to_whyml(iter_ir, local_refs))
        self._add_abstract_op("val iter_length (x: int) : int")
        self._add_abstract_op("val iter_get (x: int) (i: int) : int")
        return f"(iter_length {iter_expr})", f"(iter_get {iter_expr} !{idx})", False

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
        for a try-body local's pre-declaration: `record` | `dict` | `default`."""
        vt = val_ir.get("type", "")
        if vt == "Call" and val_ir.get("func", "") in self._record_types:
            return "record"
        if (vt in ("DictLit", "SetLit")
                or (vt == "Call" and val_ir.get("func") in ("dict", "set", "frozenset"))
                or self._rhs_yields_map(val_ir)):
            return "dict"
        return "default"

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
                # Sanitize each piece of a `|`-separated exc_type union;
                # leading-underscore local aliases like `_FooError` must
                # match the sanitized declaration emitted by the preamble.
                exc_parts = [safe_exc_name(p) for p in
                              (exc.split("|") if "|" in exc else [exc])]
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

    def _handle_match_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                           local_refs: Set[str], declared_refs: Set[str],
                           indent: str, in_loop: bool) -> str:
        subject = self._expr_to_whyml(stmt["subject"], local_refs)
        cases = stmt.get("cases", [])
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
        elif (val_ir.get("type") == "Var"
              and val_ir.get("name") in getattr(self, "_seq_locals", set())):
            # 07-1705-rev4 P4: returning a seq-modelled (growable) list local where the
            # function's declared return is `array int` (a `list`) crosses the seq→array
            # boundary — materialise to a FRESH array (legal: bound at the return slot,
            # never rebound into a regioned ref). Reuses the faithful `materialize` bridge.
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
            if func_ret == "string":
                # 10-1732-gap Gap 1: a `string`-returning function with an early/in-loop
                # return raises `Return_str <string>` (caught by the `with Return_str r -> r`
                # arm). `val` is already the lowered string expression — no int coercion.
                return f"{indent}raise (Return_str {val})"
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
