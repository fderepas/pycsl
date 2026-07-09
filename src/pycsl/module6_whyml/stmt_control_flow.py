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
        # W2: extra loop-bound names (a tuple target binds i AND ch) + typing the
        # char binding as a string so its `== "("` guards route through str_eq_op.
        extra_locals: Set[str] = set()
        saved_str_locals = None
        if str_ci is not None:
            _op, _idx_name, _ch_name, _is_tuple = str_ci
            extra_locals = {n for n in (_idx_name, _ch_name) if n and n != "_"}
            saved_str_locals = getattr(self, "_string_local_vars", set())
            self._string_local_vars = set(saved_str_locals) | {_ch_name}

        body_local = local_refs | {target} | extra_locals
        body_declared = declared_refs.copy() | {target} | extra_locals
        inner_body = self._stmts_to_whyml(
            _body_d, body_local, body_declared, inner_indent, True)
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
        if (getattr(self, "_current_self_type", None)
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
        t = val_ir.get("type")
        if t in ("Number", "BinOp") or t == "UnaryOp":
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
        return None

    def _union_arm_whyml_type(self, tag: str) -> str:
        """Map a Union arm IR type tag to its WhyML type string."""
        m = {"int": "int", "bool": "int", "str": "string", "float": "real",
             "list": "array int", "bytes": "array int", "bytearray": "array int",
             "dict": "map int (option int)", "set": "map int (option int)",
             "frozenset": "map int (option int)", "tuple": "array int"}
        return m.get(tag, "int")

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
        val = self._maybe_inject_union_return(val, val_ir)
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
