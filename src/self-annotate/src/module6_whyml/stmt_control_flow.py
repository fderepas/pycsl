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
    #@ ensures True
    def _stmts_to_whyml(self, rest: List[Dict[str, Any]], local_refs: Set[str],
                        declared_refs: Set[str], indent: str, in_loop: bool) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
    #@ assigns \nothing
    def _classify_iterable(self, iter_ir: "ExprIR", local_refs: Set[str],
                           idx: str) -> Tuple[str, str, bool]:
        return ("", "", False)

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _callee_raised_direct(self, node: Any) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _callee_raised_in(self, stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_try_stmt(self, stmt: int, rest: List[int], local_refs: int, declared_refs: int, indent: str, in_loop: bool) -> str:
        return ""

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
    #@ assigns \nothing
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _pattern_has_constructor(self, pat: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _render_match_pattern(self, pat: int, top: bool=False) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _match_subject_union_info(self, stmt: int) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_ctor_for_arm_tag(self, vinfo: int, arm_tag: str) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_match_stmt(self, stmt: int, rest: List[int], local_refs: int, declared_refs: int, indent: str, in_loop: bool) -> str:
        return ""

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_arm_whyml_type(self, tag: str) -> str:
        return ""

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


