from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from module6_whyml.identifiers import whyml_ident, safe_exc_name
from module6_whyml.ir_scanner import IRScanner
from ir_schema import ReturnStmt, IfStmt, WhileStmt, ForStmt, TryStmt, MatchStmt
def mutable_state(cls): return cls
""  # pycsl


# item34.md CF0: the control-flow mirror is a @mutable_state @dataclass so the emit_ir /
# string-local / seq machinery fires for its real bodies (item 4). The state fields below are
# the ones the ported handlers READ (`_has_early_ret`, `_func_return_type`, `_current_tuple_
# arity`) plus the collection sets they consult; all reads (no writes) → `assigns \nothing`.
@mutable_state
@dataclass
class ControlFlowStmtMixin:
    _has_early_ret: int = 0
    _func_return_type: str = ""
    _current_tuple_arity: int = 0
    _havoc_counter: int = 0
    _seq_locals: Set[str] = None
    _array_locals: Set[str] = None
    # W8 capability (v) / nested-string-map local: `_union_arm_whyml_type` reads
    # `self._record_types.get(tag)` (a `Dict[str, str]` record-metadata sub-dict, e.g.
    # `{"whyml_name": ...}`) then projects `_rt.get("whyml_name")` (a string). Annotated
    # `Dict[str, Dict[str, str]]` (NOT `Any`) so the emitter models it as
    # `map string (option (map string (option string)))` and the `_rt` local is a
    # nested-string-map (`map string (option string)`), not the int-erased `ref 0`.
    # Live: Module6_WhyMLTranspiler.__init__ (`self._record_types: Dict[str, Any] = {}`).
    _record_types: Dict[str, Dict[str, str]] = None
    # SOUNDNESS (frame audit): `_in_spec` is WRITTEN by the ported bodies
    # (`self._in_spec = True/False` around the invariant/variant emission in
    # `_handle_while_stmt` / `_handle_for_stmt`) but was undeclared, so no `assigns`
    # frame could name it. The header note above ("all reads (no writes) → assigns
    # \nothing") was FALSE for this field. Live: Module6_WhyMLTranspiler.__init__.
    _in_spec: int = 0
    # SOUNDNESS (frame audit, HIGH — the last open item): `_for_idx_init` is WRITTEN by
    # `_classify_iterable`'s LIVE body (`= start` / `= "0"` / the slice-lower expression)
    # and READ BACK by `_handle_for_stmt` (`idx_init = self._for_idx_init`). It was
    # undeclared on this mirror class, so no `assigns` frame could name it and the stub
    # carried `assigns \nothing` — a FALSE premise every caller inherited. Live:
    # Module6_WhyMLTranspiler.__init__ (`self._for_idx_init: str = "0"`).
    _for_idx_init: str = "0"
    "Control-flow statement handlers — `while` / `for` / `if` / `try` / `match`\n    / `return` — plus their private helpers (`_classify_iterable`,\n    `_first_assign_value_ir`, `_try_local_decl_kind`).\n\n    Extracted verbatim from `StatementEmissionMixin` (Part B move 3e, mirroring\n    the expressions.py split). `StatementEmissionMixin` inherits this mixin, so\n    the handlers resolve via MRO through the facade's `_STMT_HANDLERS` table and\n    recurse back into the core `self._stmts_to_whyml` / `self._expr_to_whyml`\n    (which stay in `StatementEmissionMixin`)."

    # item34.md CF0.3: cross-file recursion-leaf / bridge sibling stubs (defined in the
    # StatementEmissionMixin / expressions.py files the mixin composes with at runtime). Typed
    # `-> str` so the ported control-flow bodies compose their strings; effect-free registrar
    # helpers (`*_bridge`) are `assigns \nothing`.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _materialize_bridge(self) -> None:
        return

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _materialize_str_bridge(self) -> None:
        return

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _seq_init_expr(self, val_ir: "ExprIR", local_refs: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _bool_ir_to_int_wrap(self, val: str, val_ir: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _expr_to_whyml(self, expr: "ExprIR", local_refs: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _coerce_to_int(self, val: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _to_bool(self, whyml_str: str, ir_expr: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    # SOUNDNESS (relocated-stub frame audit): this stub carried NO `assigns` clause at all,
    # so it was emitted as an effect-FREE `val` — while its live body (which lives in
    # `statements.py`, a different file, which is why the same-file frame audit did not see
    # it) writes `self._in_spec` twice around its spec-context expression emission. A missing
    # frame is not "unspecified", it is the FALSE claim `\nothing`.
    #@ ensures True
    #@ assigns self._in_spec
    def _stmts_to_whyml(self, rest: List[Dict[str, Any]], local_refs: Set[str],
                        declared_refs: Set[str], indent: str, in_loop: bool) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns self._in_spec
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
        #@ loop invariant 0 <= i_inv_w and i_inv_w <= n_inv_w
        #@ loop invariant n_inv_w == len(invariants_w)
        #@ loop variant n_inv_w - i_inv_w
        while i_inv_w < n_inv_w:
            inv = invariants_w[i_inv_w]
            inv_str = self._expr_to_whyml(inv, local_refs)
            loop_code += f"{inner_indent}invariant {{ {inv_str} }}\n"
            i_inv_w += 1
        variants_w = stmt.variants
        n_var_w = len(variants_w)
        i_var_w = 0
        #@ loop invariant 0 <= i_var_w and i_var_w <= n_var_w
        #@ loop invariant n_var_w == len(variants_w)
        #@ loop variant n_var_w - i_var_w
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    # FRAME REPAIRED (frame audit, HIGH — was KNOWN-FALSE). The live body WRITES
    # `self._for_idx_init` (`= start` / `= "0"` / the slice-lower expression) and
    # `_handle_for_stmt` READS it back, so the former `assigns \nothing` was a lie every
    # caller inherited. The emitter defect that blocked the widening — the tuple-unpack
    # rewrite in `module6_whyml/statements.py::_handle_tuple_unpack_stmt` dropping the
    # `(self: <class>)` receiver binder and the `writes` clause from the abstract val that
    # `_handle_dotted_call` had registered, while the call site still passed `self` — is
    # fixed at source (`_abstract_val_receiver_and_tail`).
    #@ assigns self._for_idx_init
    def _classify_iterable(self, iter_ir: "ExprIR", local_refs: Set[str],
                           idx: str) -> Tuple[str, str, bool]:
        return ("", "", False)

    #@ requires True
    #@ ensures True
    # Frame completed: `self._classify_iterable(...)` (above) writes `_for_idx_init`, which
    # this body reads back as `idx_init`; the callee's effect propagates into this frame.
    #@ assigns self._in_spec, self._for_idx_init
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

        body_local = local_refs | {target}
        body_declared = declared_refs.copy() | {target}
        inner_body = self._stmts_to_whyml(
            _body_d, body_local, body_declared, inner_indent, True)
        if not inner_body:
            inner_body = f"{inner_indent}()"

        has_cont = IRScanner.has_continue(_body_d)
        len_expr, elem_expr, is_range = self._classify_iterable(iter_ir, local_refs, idx)

        while_parts = [f"{loop_indent}while !{idx} < {len_expr} do"]
        # seq-model-pivot.md SQ5: a @mutable_state for-loop (the emitter's `for var in
        # shared_for_mutex`) carries the index bound + a decreasing variant so the element
        # read's `0 <= idx` and the loop's termination discharge (the `idx < len` upper bound
        # is the loop condition). @mutable_state-gated → the corpus for-loops are byte-identical.
        if (getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            while_parts.append(f"{inner_indent}invariant {{ 0 <= !{idx} }}")
            while_parts.append(f"{inner_indent}variant {{ {len_expr} - !{idx} }}")
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _first_assign_value_ir(self, var: str, stmts: List[int]) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _try_local_decl_kind(self, val_ir: int) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _callee_raised_in(self, stmts: List[Dict[str, Any]]) -> List[str]:
        return []

    #@ requires True
    #@ ensures True
    # Inherited from `_stmts_to_whyml` (see its frame note).
    #@ assigns self._in_spec
    def _handle_try_stmt(self, stmt: TryStmt, rest: List[Dict[str, Any]],
                          local_refs: Set[str], declared_refs: Set[str],
                          indent: str, in_loop: bool) -> str:
        body_stmts = [s.to_dict() for s in stmt.body]
        handlers = stmt.handlers
        try_assigned = IRScanner.find_assigned_vars(body_stmts)
        n_ha = len(handlers)
        i_ha = 0
        #@ loop invariant 0 <= i_ha and i_ha <= n_ha
        #@ loop invariant n_ha == len(handlers)
        #@ loop variant n_ha - i_ha
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
        #@ loop invariant 0 <= i_sa and i_sa <= n_sa
        #@ loop invariant n_sa == len(sorted_assigned)
        #@ loop variant n_sa - i_sa
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
            #@ loop invariant 0 <= i_h and i_h <= n_h
            #@ loop invariant n_h == len(handlers)
            #@ loop variant n_h - i_h
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _try_union_is_none_match(self, stmt: "ExprIR", rest: List[Dict[str, Any]],
                                 local_refs: Set[str], declared_refs: Set[str],
                                 indent: str, in_loop: bool) -> str:
        return ""

    #@ requires True
    #@ ensures True
    # Inherited from `_stmts_to_whyml`, whose frame this audit corrected: the callee writes
    # `self._in_spec`, so this caller's `\nothing` was false too.
    #@ assigns self._in_spec
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _pattern_has_constructor(self, pat) -> bool:
        """True if `pat` is a constructor pattern, or an `Or` whose alternatives
        include one — the signal to use Why3's native `match` (A5c)."""
        p = pat.get("pattern")
        if p == "Constructor":
            return True
        if p == "Or":
            return any(self._pattern_has_constructor(a)
                       for a in pat.get("alternatives", []))
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _match_pattern_cond(self, pat: "ExprIR", subject: str, local_refs: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _render_match_pattern(self, pat: "ExprIR", top: bool=False) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _match_subject_union_info(self, stmt: "ExprIR") -> Tuple[str, "ExprIR"]:
        return ("", stmt)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_ctor_for_arm_tag(self, vinfo: "ExprIR", arm_tag: str) -> Tuple[str, "ExprIR"]:
        return ("", vinfo)

    #@ requires True
    #@ ensures True
    # Inherited from `_stmts_to_whyml` (see its frame note) — the callee writes
    # `self._in_spec`, so this caller's `\nothing` was false too.
    #@ assigns self._in_spec
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
                    # self-tcb-reduction Tier-5: the rewritten pattern is a
                    # HETEROGENEOUS `Dict[str, Any]` (two string values + a list of
                    # nested dicts), so it is annotated with the `PyVal` (~Any)
                    # sentinel and lowers to the faithful `map string (option hval)`
                    # with `HStr`/`HArr`/`HMap`-tagged values — never the int-erased
                    # `map string (option int)` (which int-hashes "Constructor" and
                    # type-rejects the string `arm_ctor`).
                    new_pat: Dict[str, PyVal] = {
                        "pattern": "Constructor", "ctor": arm_ctor,
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
        #@ loop invariant 0 <= i_case and i_case <= n_cases
        #@ loop invariant n_cases == len(cases)
        #@ loop variant n_cases - i_case
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _maybe_inject_union_return(self, val: str, val_ir: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _infer_return_value_type(self, val_ir: Any) -> Optional[str]:
        return None

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
            if func_ret == "emit_ir":
                # Return_emit_ir infra: an emit_ir-returning function's early/in-loop
                # return raises `Return_emit_ir <emit_ir>` (caught by the `with
                # Return_emit_ir r -> r` arm, statements.py::_wrap_body_with_return_catch).
                # `val` is already the lowered emit_ir constructor expression (e.g. `(IrAttr
                # ... ...)`) — no int coercion, mirroring the Return_str arm above.
                return f"{indent}raise (Return_emit_ir {val})"
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


