from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from module6_whyml.identifiers import op_translate, whyml_ident, safe_mutex_name, safe_exc_name, stable_hash
from module6_whyml.ir_scanner import IRScanner
from module6_whyml.stmt_control_flow import ControlFlowStmtMixin
from dataclasses import dataclass
def mutable_state(cls): return cls

from ir_schema import (
    stmt_from_dict, _ABSENT,
    AssignStmt, AugAssignStmt, ArraySetStmt, ArraySliceSetStmt,
    GhostAssignStmt, GhostArraySetStmt, TupleUnpackStmt,
    FieldAssignStmt, FieldAugAssignStmt, ExprStmt, CriticalSectionStmt,
    ReturnStmt, IfStmt, WhileStmt, ForStmt, TryStmt, MatchStmt,
    LabelStmt, RaiseStmt, ProofAssertStmt, AssertStmt,
    PassStmt, BreakStmt, ContinueStmt, OpaqueStmt,
)

# ---------------------------------------------------------------------------
# Phase C step 2 (ir-schema-spec.md §4.1): the emitter's self-annotate model
# of its own INPUT type. In the real codebase `ir_schema.py` is resolvable, so
# `stmt: AssignStmt` makes `stmt.target` a typed (str) field access. In this
# single-file self-annotate isolation the `ir_schema` import is opaque (pycsl
# skips it), so `stmt.target` stays an Any-typed getattr — the typed-schema
# payoff does NOT transfer here. These `#@ datatype` declarations mirror the
# Phase-A sums as a WhyML model of the IR shapes the emitter consumes; they
# document the constructor-to-field mapping that WOULD make the `_handle_*`
# bodies typed-field-access (and thus body-faithful) once cross-file type
# resolution is available. They are logic-only (unconnected to the opaque
# Python annotations) and do not by themselves discharge any `_handle_*` body.
# ---------------------------------------------------------------------------

#@ datatype expr_ir = EVar(string) | EBinOp(string, expr_ir, expr_ir) | EIntLit(int) | EStrLit(string) | EArrayLit(int) | ESubscript(expr_ir, expr_ir) | ECall(string, int)

#@ datatype stmt_ir = SAssign(string, expr_ir) | SAugAssign(string, string, expr_ir) | SArraySet(string, expr_ir, expr_ir) | SIf(expr_ir, int, int) | SWhile(expr_ir, int) | SFor(string, string, int) | SReturn(expr_ir) | SExpr(expr_ir) | SPass | SBreak | SContinue | SRaise(string)


@mutable_state
@dataclass
class StatementEmissionMixin(ControlFlowStmtMixin):
    _slice_set_tmp_counter: int = 0
    _all_record_fields: Set[str] = None
    _array_locals: Set[str] = None
    _array2d_params: Set[str] = None
    _current_array1d_params: Set[str] = None
    _seq_locals: Set[str] = None
    _dict_locals: Set[str] = None
    _value_semantic: int = 0
    _current_symbol_table: Dict[str, str] = None
    _shared_var_names: Set[str] = None
    _decode_to_string: int = 0
    _ghost_string_vars: Set[str] = None
    _ghost_tuple_vars: Dict[str, int] = None
    _ghost_array_vars: Set[str] = None
    _ghost_dict_vars: Set[str] = None
    _ghost_list_vars: Set[str] = None
    _ghost_set_vars: Set[str] = None
    _bounded_int: int = 0
    _known_collection_sizes: Dict[str, int] = None
    _inline_array_temps: Set[str] = None
    _dict_value_types: Dict[str, str] = None
    _dict_key_types: Dict[str, str] = None
    _abstract_ops: Dict[str, str] = None
    _havoc_counter: int = 0
    _in_spec: int = 0
    # resync-campaign.md R0.2: state fields the re-ported (current-emitter) bodies read.
    _current_self_type: str = ""
    _heap_var: str = ""
    _todict_aliases: Dict[str, str] = None
    _getattr_self_dict_aliases: Dict[str, str] = None
    _string_local_vars: Set[str] = None
    _emit_ir_local_vars: Set[str] = None
    _mutable_state_classes: Set[str] = None
    _current_record_var_classes: Dict[str, str] = None
    """Statement-emission dispatch: every `_handle_*_stmt` handler plus the
    statement-stream orchestrator (`_stmts_to_whyml`), body-wrapping helpers
    (`_emit_body_code`, `_wrap_body_with_return_catch`), first-assignment
    emission (`_emit_first_assign`, `_emit_array_local_reassign`,
    `_emit_new_ghost_ref`), frame-condition emission, and iterable
    classification. Mixed into Module6_WhyMLTranspiler.
    """

    # Phase B (ir-schema-spec.md §6): the prior `_STMT_HANDLERS` string table
    # is REPLACED by the typed `isinstance` dispatch in `_stmts_to_whyml`. The
    # table-driven indirection (str-kind → method-name → getattr) is no longer
    # needed: each typed `StmtIR` subclass routes directly to its handler.
    #
    # Phase C (ir-schema-spec.md §7) — annotation status of the `_handle_*` body.
    # The bodies are now typed field accesses (`stmt.target`, `stmt.value`) in
    # the REAL codebase, but in this single-file self-annotate isolation four
    # residual blockers keep most methods `\trusted`:
    #   B1. OPAQUE IMPORT — `from ir_schema import AssignStmt, ...` is skipped
    #       by pycsl (no local source found), so `stmt: AssignStmt` is an
    #       opaque type and `stmt.target` is an Any-typed getattr. The typed-
    #       schema payoff (Phase A+B) does NOT transfer to single-file isolation
    #       without cross-file type resolution.
    #   B2. F-STRING HASHING — the bodies build the emitted WhyML string with
    #       f-strings (`f"{indent}let {safe_target} := {val}"`). pycsl lowers
    #       f-string LITERAL segments to hashed INTs (the "f-strings hash"
    #       limitation), so the body's `str_concat` receives an int where a
    #       string is expected → WhyML type error. This is a string-lowering
    #       limitation, NOT addressed by the typed-schema refactor.
    #   B3. TRUSTED SIBLING RETURNS — `_handle_*` bodies call `self._expr_to_whyml`
    #       / `self._stmts_to_whyml` (themselves `\trusted`, `ensures True`);
    #       the emitted string DEPENDS on those return values, which are
    #       unmodeled, so a real `ensures \result == <the WhyML string>` cannot
    #       pin the composed string without modeling the siblings.
    #   B4. SELF-MUTATION — many bodies mutate transpiler state
    #       (`self._dict_locals.add`, `self._record_locals.add`,
    #       `self._add_abstract_op`, `self._array_locals.add`, …); there is no
    #       transpiler-state record model, so the frame (`assigns`) cannot be
    #       stated soundly.
    # Body-faithful methods (B1-B4 do NOT apply): `_materialize_bridge`,
    # `_materialize_str_bridge` — single trusted `_add_abstract_op` call with an
    # adjacent-string-literal argument (no f-string, no sibling return-value
    # dependency, no self-field write visible to pycsl).
    #
    # ── LINK-3 re-discharge (the-finishable-path.md Step 1) ──────────────────
    # The `\trusted` stubs below are NOT "assumed correct by inspection". Their
    # correctness is re-sited onto the Rocq/Why3 side of the byte-diff, where it
    # is a finite set of per-handler coherence statements proved/audited in
    # `src/self-annotate/pycsl-wp-spec.mlw`, plus the extensional LINK-2 bridge
    # (`bin/extraction-byte-diff.sh`: the Rocq-extracted `emit_stmt_full_complete`
    # diffed against this emitter). The per-handler decision map (matched lemma /
    # audited axiom / no-WP-arm-audited-trusted) is `src/self-annotate/arm-coverage.md`.
    # Provenance, by handler:
    #   _handle_assign_stmt     ── validated-by: lemma assign_code_state_coherent      + LINK-2
    #   _handle_augassign_stmt  ── validated-by: lemma aug_assign_code_state_coherent  + LINK-2
    #   _handle_array_set_stmt  ── validated-by: axiom array_set_code_state_coherent (audited) + LINK-2
    #   _handle_seq_assign / _handle_tuple_unpack_stmt
    #                           ── validated-by: seq (axiom) ∘ assign (lemma), audited at this layer
    #   _handle_expr_stmt / _handle_fieldassign_stmt / _handle_fieldaugassign_stmt /
    #   _handle_critical_section_stmt / _handle_ghost_assign_stmt /
    #   _handle_ghost_array_set_stmt / _handle_array_slice_set_stmt
    #                           ── no base-WP arm yet: explicitly audited-trusted, LINK-2 only
    # (Note: PyCSL's grammar rejects a `#@ validated-by:` contract keyword, so this
    #  provenance is recorded as plain comments rather than inline `#@` directives.)

    # no-more-int emitter L2b (no-more-int-emitter-plan.md): explicit `\trusted`
    # stubs for the string-returning SIBLING emitters (B3) defined in the
    # `ExpressionEmissionMixin` file, which `StatementEmissionMixin` composes with
    # at runtime but does not inherit here. Declaring their `-> str` return type
    # makes it available in this module's `_module_method_return_types`, so a local
    # bound from `self._expr_to_whyml(...)` types as `string` (L2), not `ref 0`.
    # Faithful: the real siblings do return `str`; this only surfaces that fact.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _add_abstract_op(self, decl: str) -> None:
        return

    # resync-campaign.md R0.3: sibling stubs the re-ported handlers call.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _call_returns_string_collection(self, func_name: str) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _resolve_dotted_signature(self, func_name: str) -> Tuple[str, List[str], int, int]:
        return ("", [], 0, 0)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _str_operand_to_int(self, s: str) -> str:
        return ""

    # cf6.md M1.4: the emit_ir-node predicate (`_handle_array_set_stmt` uses it to no-op an
    # `<emit_ir>[k]=v` write). Cross-mixin (lives in ExpressionEmissionMixin); a \trusted stub
    # here so the reflecting mirror type-checks the call.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _is_emit_ir_expr(self, ir: "ExprIR") -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _field_label(self, record_lower: str, field: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _array_coerce_arg(self, val: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _coerce_to_int(self, val: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _field_type_for(self, obj: str, field: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _expr_to_whyml(self, expr: "ExprIR", local_refs: Set[str], invariant_ctx: bool = False,
                       subst: int = None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _expr_to_whyml_string_ctx(self, ir: "ExprIR", local_refs: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _is_string_expr(self, ir: "ExprIR") -> bool:
        return True

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _track_collection_metadata(self, target: str, val_ir: "ExprIR") -> None:
        return

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _first_assign_kind(self, val: str, val_ir: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _val_is_bool(self, val_ir: "ExprIR") -> bool:
        return True

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _resolve_effective_ghost_type(self, target: str, op: str, ghost_type: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _e(self, ir: "ExprIR", local_refs: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _field_type_of(self, attr_ir: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _maybe_emit_no_exception_assert(self, kind: tuple, args: List[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _dv_store_value(self, nu: str, val_expr: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _mutex_inv_application(self, mutex: str, inv_str: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _handle_return_stmt(self, stmt: "ExprIR", rest: List[Dict[str, Any]],
                            local_refs: Set[str], declared_refs: Set[str],
                            indent: str, in_loop: bool) -> str:
        return ""


    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_first_assign(self, kind: str, indent: str, safe_target: str, target: str,
                           val: str, val_ir: "ExprIR") -> str:
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
            # The dict's value type ν drives the empty-map literal (string /
            # seq-int snapshot / nested-map / int-default). Consolidated in
            # `_dv_empty_default`; None ⇒ keep the caller's int-default `val`.
            _empty = self._dv_empty_default(self._dict_value_types.get(target))
            if _empty is not None:
                val = _empty
            return f"{indent}let {safe_target} = ref {val} in\n"
        if kind == "bounded_int":
            return f"{indent}let {safe_target} = ref ({val} : int{self._bounded_int}) in\n"
        if self._val_is_bool(val_ir):
            val = f"(if {val} then 1 else 0)"
        return f"{indent}let {safe_target} = ref {val} in\n"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_array_local_reassign(self, target: str, safe_target: str, indent: str,
                                    val_ir: "ExprIR", local_refs: Set[str]) -> str:
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

    #@ requires True
    #@ ensures True
    #@ assigns self._decode_to_string, self._todict_aliases
    def _handle_assign_stmt(self, stmt: AssignStmt, rest: List[Dict[str, Any]],
                             local_refs: Set[str], declared_refs: Set[str],
                             indent: str, in_loop: bool) -> str:
        target = stmt.target
        safe_target = whyml_ident(target)
        val_ir = stmt.value.to_dict()
        vt = val_ir.get("type", "")
        # todict-reflection-plan.md R1: `d = <node>.to_dict()` binds `d` as a typed-node
        # ALIAS (record the receiver dotted-name), and emits NOTHING — `d` is never a
        # real value; every later `d.get(key)` routes to `node.<field>`
        # (`_lower_dict_get_call`). Fires only on a literal `.to_dict()` no-arg call →
        # byte-identical for every function that does not reflect on IR dicts.
        if (vt == "Call" and isinstance(val_ir.get("func"), str)
                and val_ir["func"].endswith(".to_dict") and not val_ir.get("args")):
            self._todict_aliases[target] = val_ir["func"][:-len(".to_dict")]
            _rest = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            return _rest if _rest else f"{indent}()"
        self._track_collection_metadata(target, val_ir)

        # str-list-elements: a `.decode()` RHS bound to a STRING-typed local lowers to a
        # string-returning val (so the decoded name is `string`, not the legacy opaque
        # int). The flag is scoped to this single RHS so decode calls elsewhere (compared
        # against ints in an inlined `_dir_lookup`) keep their byte-identical int model.
        _str_target = (getattr(self, "_current_symbol_table", {}).get(target)
                       in ("str", "string"))
        _prev_dts = getattr(self, "_decode_to_string", False)
        if _str_target:
            self._decode_to_string = True
        val = self._expr_to_whyml(val_ir, local_refs)
        self._decode_to_string = _prev_dts
        # Tuple/Set literals can't be stored in int refs; use 0 as placeholder
        if vt in ("Tuple", "SetLit"):
            val = "0"
        # i-feel-good.md I-B: `x = None` where x is a string local (an Optional[str], the
        # emitter's `self_field_name = None`) → "" (the absent sentinel), so the `ref ""`
        # string local stays string-typed. @mutable_state-gated → byte-identical elsewhere.
        if (vt == "None" and target in getattr(self, "_string_local_vars", set())
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            val = '""'
        # self-ir-schema.md IR2: `x = None` where x is an emit_ir local (an
        # `Optional[StmtIR]`, the emitter's `tail_ret = None`) → `(IrOther "")` (the emit_ir
        # absent sentinel), so the `ref (IrOther "")` stays emit_ir-typed. @mutable_state.
        if (vt == "None" and target in getattr(self, "_emit_ir_local_vars", set())
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            val = '(IrOther "")'

        # Assignment to a module-level shared variable (always a ref, never re-declared)
        if target in self._shared_var_names:
            code = f"{indent}{whyml_ident(target)} := {val}"
            if rest:
                code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            return code

        # 07-1705-rev4 P3: a seq-promoted (growable) list local is a `ref (seq int)`.
        if target in self._seq_locals:
            return self._handle_seq_assign(
                stmt, rest, local_refs, declared_refs, indent, in_loop)

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _seq_init_expr(self, val_ir: "ExprIR", local_refs: Set[str]) -> str:
        """07-1705-rev4 P3: lower a seq-local's RHS to a `seq int` value. A list literal
        `[v0, v1, …]` becomes a `Seq.cons` chain (qualified); any other array-typed RHS
        is bridged with `snapshot`."""
        if val_ir.get("type") == "ArrayLit":
            expr = "Seq.empty"
            for e in reversed(val_ir.get("elts", [])):
                es = self._coerce_to_int(self._expr_to_whyml(e, local_refs))
                expr = f"(Seq.cons {es} {expr})"
            return expr
        return self._seq_operand(val_ir, local_refs)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _seq_operand(self, val_ir: "ExprIR", local_refs: Set[str]) -> str:
        """07-1705-rev4 P3: an operand that must be a `seq int` — `!b` if `b` is itself a
        seq local, else `snapshot(b)` to bridge an array-modelled value into seq."""
        if val_ir.get("type") == "Var" and val_ir.get("name") in self._seq_locals:
            return f"(!{whyml_ident(val_ir['name'])})"
        self._add_abstract_op(
            "val snapshot (a: array int) : seq int\n"
            "    ensures { Seq.length result = Array.length a }\n"
            "    ensures { forall i:int. 0 <= i < Array.length a -> Seq.get result i = a[i] }")
        return f"(snapshot {self._expr_to_whyml(val_ir, local_refs)})"

    # Body-faithful (bucket 1): single call to trusted `_add_abstract_op` (frame
    # `\nothing` per its trusted contract); body verifies at the call level. Returns
    # None so the postcondition is vacuous — the real content is the side effect,
    # which is hidden behind the trusted stub's frame.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _materialize_bridge(self) -> None:
        """07-1705-rev4 P4: emit the faithful seq→array bridge val (fresh result, no
        region link), used where a seq-modelled value crosses into `array int` code."""
        self._add_abstract_op(
            "val materialize (s: seq int) : array int\n"
            "    ensures { Array.length result = Seq.length s }\n"
            "    ensures { forall i:int. 0 <= i < Seq.length s -> result[i] = Seq.get s i }")

    # Body-faithful (bucket 1): same shape as `_materialize_bridge` — single trusted
    # `_add_abstract_op` call, body verifies, `ensures True` (returns None).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _materialize_str_bridge(self) -> None:
        """str-list-elements: the STRING analogue of `_materialize_bridge` — bridges a
        `seq string` (a growable string list) to a fresh `array string` at the return
        slot, so a list of strings returns as `array string`."""
        self._add_abstract_op(
            "val materialize_str (s: seq string) : array string\n"
            "    ensures { Array.length result = Seq.length s }\n"
            "    ensures { forall i:int. 0 <= i < Seq.length s -> result[i] = Seq.get s i }")

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_seq_assign(self, stmt: AssignStmt, rest: List[Dict[str, Any]],
                           local_refs: Set[str], declared_refs: Set[str],
                           indent: str, in_loop: bool) -> str:
        target = stmt.target
        safe = whyml_ident(target)
        init = self._seq_init_expr(stmt.value.to_dict(), local_refs)
        if target not in declared_refs:
            declared_refs.add(target)
            local_refs.add(target)        # seq locals are refs → reads deref `!a`
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if not rest_code:
                rest_code = f"{indent}()"
            return f"{indent}let {safe} = ref {init} in\n{rest_code}"
        code = f"{indent}{safe} := {init}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns self._ghost_string_vars, self._ghost_tuple_vars, self._ghost_array_vars, self._array_locals, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars
    def _handle_ghost_assign_stmt(self, stmt: GhostAssignStmt, rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        target = stmt.target
        safe_target = whyml_ident(target)
        op = stmt.op
        ghost_type = self._resolve_effective_ghost_type(target, op, stmt.ghost_type)
        is_new = target not in declared_refs
        _val_d = stmt.value.to_dict()

        if ghost_type == "string":
            self._ghost_string_vars.add(target)
            val = self._expr_to_whyml_string_ctx(_val_d, local_refs | {target})
            if is_new:
                return self._emit_new_ghost_ref(safe_target, target, f"= ref ({val})",
                                                rest, local_refs, declared_refs, indent, in_loop)
            code = f"{indent}ghost {safe_target} := {val}"
        elif ghost_type in ("tuple2", "tuple3", "tuple4"):
            self._ghost_tuple_vars[target] = int(ghost_type[-1])
            val = self._expr_to_whyml(_val_d, local_refs | {target})
            if is_new:
                return self._emit_new_ghost_ref(safe_target, target, f"= ref {val}",
                                                rest, local_refs, declared_refs, indent, in_loop)
            code = f"{indent}ghost {safe_target} := {val}"
        elif ghost_type == "array":
            self._ghost_array_vars.add(target)
            # Ghost arrays are direct array values (not refs); add to _array_locals
            # so subscript access in invariants emits arr[i] not subscript_get arr i
            self._array_locals.add(target)
            val = self._expr_to_whyml(_val_d, local_refs | {target})
            if is_new:
                return self._emit_new_ghost_ref(safe_target, target, f"= {val}",
                                                rest, local_refs, declared_refs, indent, in_loop)
            code = f"{indent}ghost {safe_target} <- {val}"
        elif ghost_type == "ghost_dict":
            self._ghost_dict_vars.add(target)
            if op == "+=" and not is_new:
                val_ir = _val_d
                if val_ir.get("type") == "MkTuple" and len(val_ir.get("elts", [])) == 2:
                    k = self._e(val_ir["elts"][0], local_refs)
                    v = self._e(val_ir["elts"][1], local_refs)
                    code = f"{indent}ghost {safe_target} := (Map.set !{safe_target} {k} (Some {v}))"
                else:
                    val = self._expr_to_whyml(_val_d, local_refs | {target})
                    code = f"{indent}ghost {safe_target} := {val}"
            else:
                val = self._expr_to_whyml(_val_d, local_refs | {target})
                if is_new:
                    return self._emit_new_ghost_ref(safe_target, target, f"= ref {val}",
                                                    rest, local_refs, declared_refs, indent, in_loop)
                code = f"{indent}ghost {safe_target} := {val}"
        elif ghost_type == "ghost_list":
            self._ghost_list_vars.add(target)
            val = self._expr_to_whyml(_val_d, local_refs | {target})
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
            val = self._expr_to_whyml(_val_d, local_refs | {target})
            if is_new:
                return self._emit_new_ghost_ref(safe_target, target, f"= ref {val}",
                                                rest, local_refs, declared_refs, indent, in_loop)
            if op == "+=":
                code = f"{indent}ghost {safe_target} := (Map.set !{safe_target} {val} true)"
            else:
                code = f"{indent}ghost {safe_target} := {val}"
        else:
            # Default: int ghost (existing behaviour)
            val = self._expr_to_whyml(_val_d, local_refs | {target})
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

    # no-more-int emitter L5 (no-more-int-emitter-plan.md): this handler is no
    # longer a trusted stub — after B1.4 (field access) + L1-L4c the body
    # TYPE-CHECKS and its `assigns \nothing` frame is PROVEN. It is the FIRST
    # _handle_* emitter method verified with a checked (non-stub) body. A
    # body-faithful `ensures \result == ...` still needs the siblings' string
    # VALUES modelled (B3); this proves type-safety + frame.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_ghost_array_set_stmt(self, stmt: GhostArraySetStmt, rest: List[Dict[str, Any]],
                                      local_refs: Set[str], declared_refs: Set[str],
                                      indent: str, in_loop: bool) -> str:
        arr = whyml_ident(stmt.target)
        idx = self._expr_to_whyml(stmt.index, local_refs)
        val = self._expr_to_whyml(stmt.value, local_refs)
        # Why3 array element assignment: a[i] <- v
        code = f"{indent}{arr}[{idx}] <- {val}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops
    def _handle_tuple_unpack_stmt(self, stmt: TupleUnpackStmt, rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        targets = stmt.targets
        val_ir = stmt.value.to_dict()
        val_whyml = self._expr_to_whyml(val_ir, local_refs)
        safe_targets = [whyml_ident(t) for t in targets]
        if val_ir.get("type") == "Call":
            func_name = val_ir.get("func", "")
            nargs = len(val_ir.get("args", []))
            safe_fn = whyml_ident(func_name)
            arity_fn = f"{safe_fn}_{nargs}"
            if arity_fn in self._abstract_ops:
                tuple_ret = "(" + ", ".join(["int"] * len(targets)) + ")"
                # item34.md CF4: use the callee's DECLARED signature (e.g.
                # `_classify_iterable`'s `Tuple[str,str,bool]` → `(string,string,int)` and its
                # `(ExprIR, Set, str)` params) instead of the homogeneous-int default, so a
                # string/bool tuple slot and a non-int arg type-check. @mutable_state-gated →
                # the corpus's int-tuple unpacks are byte-identical.
                _cpt: List[str] = []
                if (getattr(self, "_current_self_type", None)
                        in getattr(self, "_mutable_state_classes", set())):
                    # resync-campaign.md R2: UNIQUE throwaway names (not `_, _`, which both
                    # lower to `_tu_py_underscore` → a Why3 duplicate-variable in the unpack).
                    _crt, _cpt, _re3, _re4 = self._resolve_dotted_signature(func_name)
                    if (_crt and _crt.startswith("(")
                            and _crt.count(",") + 1 == len(targets)):
                        tuple_ret = _crt
                if nargs == 0:
                    self._abstract_ops[arity_fn] = f"val {arity_fn} () : {tuple_ret}"
                elif len(_cpt) == nargs:
                    params = " ".join(f"(x{i}: {_cpt[i]})" for i in range(nargs))
                    self._abstract_ops[arity_fn] = f"val {arity_fn} {params} : {tuple_ret}"
                else:
                    # Per missing-bytes-struct-feature.md Phase 1:
                    # preserve the param types from the existing
                    # declaration (which `_handle_dotted_call` may
                    # have set to `array int` based on call-site
                    # arg-type inference) rather than blindly
                    # overwriting with `int`. Without this,
                    # `(a, b) = struct.unpack(fmt, array_int_data)`
                    # forced a (int, int) → (int, int) declaration
                    # that mismatched the call site.
                    import re as _re
                    existing = self._abstract_ops[arity_fn]
                    types_in_existing = _re.findall(
                        r"\(x\d+:\s*([a-z][a-z_ ]*?)\)", existing)
                    if len(types_in_existing) == nargs:
                        params = " ".join(
                            f"(x{i}: {types_in_existing[i]})"
                            for i in range(nargs))
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
        #@ loop invariant 0 <= i_tu and i_tu <= n_tu
        #@ loop invariant n_tu == len(tmp_names)
        #@ loop invariant len(safe_targets) == len(tmp_names)
        #@ loop variant n_tu - i_tu
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

    #@ requires True
    #@ ensures True
    #@ assigns self._slice_set_tmp_counter
    def _handle_array_slice_set_stmt(self, stmt: ArraySliceSetStmt, rest: List[Dict[str, Any]],
                                      local_refs: Set[str], declared_refs: Set[str],
                                      indent: str, in_loop: bool) -> str:
        """`dst[lo:hi] = src` (src array-typed) → bounded `Array.blit`.

        Emits `Array.blit src 0 dst lo (hi - lo)`. Why3's `blit` carries the
        bounds preconditions (`0 <= ofs`, `ofs+len <= length`), so the
        caller's `requires` + the record length invariant must make
        `hi <= length dst` and `(hi - lo) <= length src` provable. This is
        gap 4 of missing-pycsl-ir-features.md — the array-valued RHS forms
        `dst[a:b] = struct.pack(...)` and `dst[a:b] = b'\\x00' * N`.
        """
        arr = stmt.array.to_dict()
        dst = self._expr_to_whyml(arr, local_refs)
        lo = self._expr_to_whyml(stmt.lower, local_refs)
        if stmt.upper is not None:
            hi = self._expr_to_whyml(stmt.upper, local_refs)
        else:
            hi = f"(Array.length {dst})"
        src = self._expr_to_whyml(stmt.value, local_refs)
        # If `src` is a non-trivial expression (e.g. `Array.sub ...`), it
        # cannot be referenced inside a logic `assert {...}` (WhyML program
        # functions are not logic functions). Bind it to a fresh local first
        # so both the `Array.blit` call and the per-element equality assert
        # below reference the same let-bound array value.
        src_needs_let = not src.isidentifier()
        if src_needs_let:
            tmp_count = getattr(self, "_slice_set_tmp_counter", 0) + 1
            self._slice_set_tmp_counter = tmp_count
            src_var = f"__pycsl_slice_src_{tmp_count}"
            prologue = f"{indent}let {src_var} = {src} in\n"
            src = src_var
        else:
            prologue = ""
        code = f"{indent}Array.blit {src} 0 {dst} ({lo}) (({hi}) - ({lo}));"
        # Per-element equality hint (definitional fact from Why3's Array.blit
        # spec, zero TCB): surface `forall i. 0 <= i < n -> dst[lo+i] = src[i]`
        # so downstream ensures/assert clauses that reference individual dst
        # bytes after the blit can discharge. See toolfix-spec.md.
        code += (f"\n{indent}assert {{ forall i : int. (0 <= i /\\ i < (({hi}) - ({lo}))) "
                 f"-> ({dst}[({lo}) + i] = {src}[i]) }}")
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return prologue + code

    #@ requires True
    #@ ensures True
    #@ assigns self._known_collection_sizes
    def _handle_array_set_stmt(self, stmt: ArraySetStmt, rest: List[Dict[str, Any]],
                                local_refs: Set[str], declared_refs: Set[str],
                                indent: str, in_loop: bool) -> str:
        arr = stmt.array.to_dict()
        # cf6.md M1.4: `<emit_ir>[k] = v` (`c["pattern"] = new_pat`) writes to an IMMUTABLE
        # emit_ir value — the rewrite is UNMODELLED, a sound no-op for the type-safety+frame
        # contract (the reflected IR is never claimed updated; `cases` is a local copy so the
        # frame holds). @mutable_state / emit_ir-gated -> byte-identical elsewhere.
        if (getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and self._is_emit_ir_expr(arr)):
            return f"{indent}()"
        if arr.get("type") == "Var":
            var_name = arr.get("name", "")
            if var_name in getattr(self, "_dict_locals", set()):
                known_sizes = getattr(self, "_known_collection_sizes", {})
                if var_name in known_sizes:
                    known_sizes[var_name] = known_sizes[var_name] + 1
                else:
                    known_sizes[var_name] = 1
        _nested_seq_base = None
        if (arr.get("type") == "Subscript"
                and arr.get("value", {}).get("type") == "Var"):
            _nb = arr["value"]["name"]
            _nt = getattr(self, "_list_nested_elem", {}).get(_nb, "")
            if (_nt.startswith("seq ")
                    and arr.get("index", {}).get("type") != "String"
                    and stmt.index.to_dict().get("type") != "String"):
                _nested_seq_base = _nb
        if _nested_seq_base is not None:
            # WL-04f (wrong-lowering-to-fix.md §WL-04 nested-inner-mutation): in-place
            # inner ELEMENT mutation `a[i][j] = v` of a NON-int-leaf nested list
            # (`List[List[str]]` ~ `array (seq string)`, `List[List[float]]` ~
            # `array (seq real)`). The int leaf routes to the mutable `matrix int`
            # model (0802/0803); a non-int leaf has NO mutable 2-D built-in, but the
            # OUTER `array` IS mutable, so the write lowers to an outer-array store of
            # a FUNCTIONALLY-updated inner seq (option c, Gate-B spike
            # spikes/nested-list-inner-mutable-seq.mlw, Valid on Alt-Ergo + Z3):
            #     a[i][j] = v   ~~>   a[i] <- Seq.set a[i] j v
            # The inner `seq` stays PURE/immutable (`array (array τ)` is Why3 TYPE-
            # rejected). `Seq.set`'s `requires 0 <= j < length` is the IndexError
            # obligation. SOUND within PyCSL's expressible fragment: an inner list
            # can be neither bound to a local (`b = a[i]` type-fails: a local defaults
            # to int) nor shared across outer slots (`a = [row, row]` type-fails:
            # `array (array τ)` is rejected), so Python's reference-vs-value
            # (aliasing) divergence is UNOBSERVABLE — the value-semantics store is
            # faithful to every expressible post-state. `seq int` never reaches here
            # (it is matrix-routed); a `map`-leaf inner mutation and any other shape
            # fall through to the generic path and fail closed (TYPEERR).
            base = whyml_ident(_nested_seq_base)
            row_expr = self._expr_to_whyml(arr["index"], local_refs)
            col_expr = self._expr_to_whyml(stmt.index, local_refs)
            val_expr = self._expr_to_whyml(stmt.value, local_refs)
            row = f"{base}[{row_expr}]"
            code = f"{indent}{row} <- Seq.set {row} {col_expr} {val_expr}"
        elif (arr.get("type") == "Subscript" and
                arr.get("value", {}).get("type") == "Var" and
                arr.get("value", {}).get("name") in getattr(self, "_array2d_params", set()) and
                arr.get("value", {}).get("name") not in getattr(self, "_dict_locals", set())):
            base = arr["value"]["name"]
            row_expr = self._expr_to_whyml(arr["index"], local_refs)
            col_expr = self._expr_to_whyml(stmt.index, local_refs)
            val_expr = self._expr_to_whyml(stmt.value, local_refs)
            code = f"{indent}set {base} {row_expr} {col_expr} {val_expr}"
        else:
            array_expr = self._expr_to_whyml(arr, local_refs)
            index_expr = self._expr_to_whyml(stmt.index, local_refs)
            val_expr = self._expr_to_whyml(stmt.value, local_refs)
            if self._value_semantic:
                var_name = arr.get("name", "") if arr.get("type") == "Var" else ""
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
                self_field_name_alias = None
                if not is_array and not is_dict and var_name:
                    # §26: `X[k] = v` where X aliases a self dict-field → a write to
                    # `self.<field>` (the getattr-bound-local form of the field write).
                    self_field_name_alias = getattr(
                        self, "_getattr_self_dict_aliases", {}).get(var_name)
                    if self_field_name_alias is not None:
                        is_dict = True
                # `self.<field>[k] = v` where <field> is set/dict-typed.
                # Resolve via the record-type table; treat as a body-dict
                # write on the field reference. Module5 emits self-field
                # access as `FieldGet` in body context (alongside the
                # `Attribute` shape used elsewhere); accept both.
                self_field_name: Optional[str] = self_field_name_alias
                arr_type = arr.get("type")
                if self_field_name is None and not is_array and arr_type in ("Attribute", "FieldGet"):
                    ft = self._field_type_of(arr)
                    if ft in ("set", "dict", "frozenset"):
                        is_dict = True
                        self_field_name = (arr.get("attr") if arr_type == "Attribute"
                                            else arr.get("field"))
                    elif ft in ("list", "tuple", "bytes", "bytearray"):
                        is_array = True
                if is_array:
                    val_expr = self._coerce_to_int(val_expr)
                    # arity2.md (2b): a ref-bound array temp lowers to `!x`;
                    # `!x[i]` parses as `!(x[i])`, so parenthesise the deref
                    # before subscripting. Inert for let-bound arrays (`x[i]`).
                    arr_e = f"({array_expr})" if array_expr.startswith("!") else array_expr
                    body = f"{arr_e}[{index_expr}] <- {val_expr}"
                    # no_exception IndexError → prepend assert in_bounds.
                    length_expr = f"(Array.length {arr_e})"
                    pred = self._maybe_emit_no_exception_assert(
                        ("subscript", "write"), [length_expr, index_expr])
                    if pred:
                        code = f"{indent}{pred} {body}"
                    else:
                        code = f"{indent}{body}"
                elif is_dict:
                    # wrong-lowering-to-fix.md §WL-05: an item-mutation `d[k] = v`
                    # of a dict/set PARAMETER is REJECTED. Python passes dicts/sets
                    # by reference, so the write must be VISIBLE to the caller — a
                    # faithful model needs proper aliasing/frame (a `writes {d}`
                    # effect), the SAME hard problem for which RECORD-param mutation
                    # (static-ref ‡) and LIST inner mutation (nested-list-mutable) are
                    # documented OUT OF SCOPE. The by-value map param is not a `ref`,
                    # so the write path below (`d := map_update_some !d k v`) would emit
                    # internally-inconsistent WhyML (`d :=`/`!d` on a non-ref). Reject
                    # cleanly here instead of emitting broken WhyML (UB catalog
                    # `param-collection-mutation`). Local dicts (`_dict_locals`, a `ref`)
                    # and self-fields (`self_field_name`) are unaffected.
                    if (self_field_name is None and var_name
                            and var_name in getattr(self, "_formal_params", [])
                            and var_name not in getattr(self, "_dict_locals", set())):
                        self._reject_param_collection_mutation(var_name, f"{var_name}[...] = ...")
                    # Body dict subscript write: `d[k] = v`. `Map.set` is a
                    # pure logic function and Why3 refuses to assign its
                    # result back to a non-ghost ref ("ghost modification
                    # in non-ghost variable"). Wrap it in a program-level
                    # abstract val `map_update_some` whose contract is
                    # the equivalent `Map.set` semantics.
                    # no-more-int-3 A1: a POLYMORPHIC update op `map 'k (option 'v)`
                    # carries any key type κ and value type ν (Why3 infers them
                    # from the args); int dicts instantiate `'k='v=int`. A
                    # string-typed key (κ, `Dict[str, _]`) or value (ν,
                    # `Dict[_, str]`) is passed through unhashed — string has
                    # decidable equality, so distinct keys do not alias.
                    self._add_abstract_op(
                        "val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) "
                        ": map 'k (option 'v)\n"
                        "    ensures { result = Map.set m k (Some v) }")
                    op = "map_update_some"
                    nu = self._dict_value_types.get(var_name) if var_name else None
                    kappa = self._dict_key_types.get(var_name) if var_name else None
                    # cleared-hash S4: a record dict FIELD store (`self.<field>[k]=v`)
                    # reads the field's declared κ/ν (`map string (option ν)` for a
                    # `dict[str,ν]` field), so the write passes the RAW native string key
                    # and the ν-typed value — type-consistent with the field read/membership.
                    if self_field_name is not None:
                        _fo = (arr.get("object")
                               if arr.get("type") in ("Attribute", "FieldGet") else None)
                        if isinstance(_fo, dict) and _fo.get("type") == "Var":
                            _frecv = f"{_fo.get('name')}.{self_field_name}"
                        elif isinstance(_fo, str):
                            _frecv = f"{_fo}.{self_field_name}"
                        else:
                            _frecv = f"self.{self_field_name}"
                        _fk = self._self_field_dict_kappa(_frecv)
                        if _fk is not None:
                            kappa = _fk
                        _fn = self._self_field_dict_nu(_frecv)
                        if _fn is not None:
                            nu = _fn
                    if kappa == "string":
                        k = index_expr
                    elif (not self._in_spec
                          and self._is_string_expr(stmt.index.to_dict())):
                        # typed-ir §18: a STRING key into an int-keyed dict FIELD
                        # (`self._ghost_tuple_vars[target] = …`, a `Dict[str,int]` field
                        # → `map int (option int)`) is `str_hash_op`-hashed, matching the
                        # self-field-dict get/membership. Byte-identical (int key coerces).
                        self._add_abstract_op("val str_hash_op (s: string) : int")
                        k = f"(str_hash_op {index_expr})"
                    else:
                        k = self._coerce_to_int(index_expr)
                    # The stored value is coerced per ν (seq-int snapshot /
                    # string|map pass-through / int-coerce). Consolidated in
                    # `_dv_store_value`.
                    v = self._dv_store_value(nu, val_expr)
                    if self_field_name is not None:
                        # `self.<field>[k] = v` — record-field assignment.
                        # Why3 syntax: `self.field <- new_value`.
                        safe_field = whyml_ident(self_field_name)
                        code = (f"{indent}self.{safe_field} <- "
                                f"{op} self.{safe_field} {k} {v}")
                    else:
                        safe_name = whyml_ident(var_name) if var_name else array_expr.lstrip("!")
                        code = f"{indent}{safe_name} := {op} !{safe_name} {k} {v}"
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

    #@ requires True
    #@ ensures True
    #@ assigns self._havoc_counter, self._in_spec
    def _handle_critical_section_stmt(self, stmt: CriticalSectionStmt, rest: List[Dict[str, Any]],
                                       local_refs: Set[str], declared_refs: Set[str],
                                       indent: str, in_loop: bool) -> str:
        mutex = stmt.mutex
        body_stmts = stmt.body
        assume_inv = stmt.assume_invariant
        prove_inv = stmt.prove_invariant
        shared_for_mutex = [
            sv["name"] for sv in self.ir.get("shared_vars", [])
            if sv.get("mutex") == mutex
        ]
        let_bindings: List[str] = []
        seq_parts: List[str] = []
        # Faithful lock-acquire: entering the critical section calls the abstract
        # diverging `acquire_<mutex>` (declared in `_emit_shared_state`), since
        # acquiring a lock can block forever. This makes the enclosing worker's
        # body genuinely able to diverge, so why3 accepts its `#@ \diverges`
        # effect and the `.mlw` type-checks.
        safe_mutex = safe_mutex_name(mutex)
        seq_parts.append(f"{indent}acquire_{safe_mutex} ()")
        if assume_inv and shared_for_mutex:
            for var in shared_for_mutex:
                safe_var = whyml_ident(var)
                tmp = f"_any_{safe_var}_{self._havoc_counter}"
                self._havoc_counter += 1
                let_bindings.append(f"{indent}let {tmp} = any int in")
                seq_parts.append(f"{indent}{safe_var} := {tmp}")
            self._in_spec = True
            inv_str = self._expr_to_whyml(assume_inv, set())
            self._in_spec = False
            app = self._mutex_inv_application(mutex, inv_str)
            seq_parts.append(f"{indent}assume {{ {app} }}")
        elif assume_inv:
            self._in_spec = True
            inv_str = self._expr_to_whyml(assume_inv, local_refs)
            self._in_spec = False
            seq_parts.append(f"{indent}assume {{ {inv_str} }}")
        # 0417 (typecheck-audit.md residual): if the critical section is the TAIL of a
        # non-unit function — i.e. `return <v>` is the last statement INSIDE the `with`
        # block — then naively appending the exit-invariant `assert` AFTER the body makes
        # the section's tail `… ; <v> ; assert {…}`, whose type is `unit` while the
        # function is declared `: int` → why3 "This expression has type (), but is expected
        # to have type int". The invariant must still be checked at section EXIT (after the
        # body's mutations), so we hoist the trailing value PAST the assert: emit the body's
        # prefix (mutations), then the `assert`, then the return value as the section's tail.
        # This fires ONLY when the LAST body statement is a value-producing `Return` AND a
        # `prove_inv` is present; every other shape (return outside the `with`, as in 0250;
        # no prove_inv; void return) takes the unchanged path → byte-identical emission.
        tail_ret = None
        if (prove_inv and body_stmts and isinstance(body_stmts[-1], ReturnStmt)
                and body_stmts[-1].value is not None):
            tail_ret = body_stmts[-1]
            body_stmts = body_stmts[:-1]
        body_code = self._stmts_to_whyml(
            [s.to_dict() for s in body_stmts], local_refs, declared_refs, indent, in_loop)
        if body_code:
            seq_parts.append(body_code)
        if prove_inv and shared_for_mutex:
            self._in_spec = True
            inv_str = self._expr_to_whyml(prove_inv, set())
            self._in_spec = False
            app = self._mutex_inv_application(mutex, inv_str)
            seq_parts.append(f"{indent}assert {{ {app} }}")
        elif prove_inv:
            self._in_spec = True
            inv_str = self._expr_to_whyml(prove_inv, local_refs)
            self._in_spec = False
            seq_parts.append(f"{indent}assert {{ {inv_str} }}")
        if tail_ret is not None:
            # The hoisted return becomes the section's final (value-producing) expression,
            # rendered through the normal return path (handles raise vs tail-value, tuples,
            # arrays, …) with no `rest`.
            seq_parts.append(self._handle_return_stmt(
                tail_ret, [], local_refs, declared_refs, indent, in_loop))
        if not seq_parts:
            seq_parts = [f"{indent}()"]
        inner = ";\n".join(seq_parts)
        code = ("\n".join(let_bindings) + "\n" + inner) if let_bindings else inner
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_augassign_stmt(
        self,
        stmt: AugAssignStmt,
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        target = stmt.target
        safe_target = whyml_ident(target)
        _val_d = stmt.value.to_dict()
        val = self._expr_to_whyml(_val_d, local_refs)
        raw_op = stmt.op
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
        if raw_op == "+" and target in self._seq_locals:
            # 07-1705-rev4 P3: faithful growable concat. `a += b` → `a := !a ++ <b as seq>`
            # over the region-free `ref (seq int)`; length-additive and element-preserving
            # via the standard `seq.Seq` `++` axioms (proven in the 07-1732 P0 probe).
            rhs = self._seq_operand(_val_d, local_refs)
            code = f"{indent}{safe_target} := (!{safe_target} ++ {rhs})"
        elif raw_op == "+" and self._is_string_expr({"type": "Var", "name": target}) \
                and self._is_string_expr(_val_d):
            # 14-string-field-codec-plan Gap (str-augassign): `s += t` on a
            # string-typed local/param lowers to the SAME string-concat bridge
            # `s + t` uses in `_binop_to_whyml` (`str_concat_op` in body, `concat`
            # in spec), not the int `+`. Without this the AugAssign arm would
            # emit `s := !s + t` and Why3 type-errors (`string + string` →
            # expected int). Fires only when BOTH the target is a str-typed
            # symbol AND the RHS is a string expression — byte-identical for
            # every non-string target (the prior path type-errored anyway).
            val = self._expr_to_whyml(_val_d, local_refs)
            if getattr(self, "_in_spec", False):
                code = f"{indent}{safe_target} := (concat !{safe_target} {val})"
            else:
                self._add_abstract_op(
                    "val str_concat_op (a: string) (b: string) : string\n"
                    "    ensures { result = (concat a b) }\n"
                    "    ensures { String.length result = String.length a + String.length b }")
                code = f"{indent}{safe_target} := (str_concat_op !{safe_target} {val})"
        elif (raw_op == "|"
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and isinstance(_val_d, dict) and _val_d.get("type") == "Call"
                and self._call_returns_string_collection(_val_d.get("func", ""))):
            # item34.md CF5: `<seq> |= find_*(...)` / `|= self._callee_raised_in(...)`
            # (`try_assigned`/`body_raised`) is a UNION over the `seq string` name-lists. The
            # RHS is seq-ified via `_seq_operand` (seq passes through; a `List[str]` array
            # source is `snapshot`-bridged) so `arr_union (a b: seq string)` type-checks.
            self._add_abstract_op("val arr_union (a b: seq string) : seq string")
            _rhs_seq = self._seq_operand(_val_d, local_refs)
            code = f"{indent}{safe_target} := (arr_union !{safe_target} {_rhs_seq})"
        elif (raw_op == "|"
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and (target in getattr(self, "_dict_locals", set())
                     or (isinstance(_val_d, dict) and _val_d.get("type") == "Var"
                         and _val_d.get("name") in getattr(self, "_dict_locals", set())))):
            # item34.md CF5: `<set> |= <set>` on the map-based sets (`already_matched |=
            # seen_local`) is a MAP union — `map int (option int)`, not int `bit_or`.
            self._add_abstract_op(
                "val map_union (a b: map int (option int)) : map int (option int)")
            code = f"{indent}{safe_target} := (map_union !{safe_target} {val})"
        elif raw_op in bitwise_ops:
            op_fn = bitwise_ops[raw_op]
            self._add_abstract_op(f"val {op_fn} (x: int) (y: int) : int")
            code = f"{indent}{safe_target} := ({op_fn} !{safe_target} {val})"
        # 07-1705-rev4 P5: the effect-opaque `array_extend` arm (07-1321 S4) is REMOVED.
        # Every grown list var is now seq-promoted (P2) and handled by the faithful seq
        # concat above (locals via P3, params via the P5 entry shadow), so `array += array`
        # no longer needs the unit-return opaque fallback. A list `+=` target that somehow
        # escaped seq-promotion would fall through to the integer `+` below and fail LOUDLY
        # at Why3 type-check (never a silent int leak) — but no corpus driver reaches it.
        else:
            code = f"{indent}{safe_target} := !{safe_target} {op} {val}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_fieldassign_stmt(
        self,
        stmt: FieldAssignStmt,
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        obj = stmt.object
        field = stmt.field
        # wrong-lowering-to-fix.md §WL-05d: a field store to a record-typed PARAMETER
        # or LOCAL var (`p.x = v`, `obj != "self"`, Module 5 now emits it — was silently
        # dropped). A MUTABLE record lowers to `p.x <- v` below (Why3 infers `writes
        # {p.x}` on the `let` → caller-visible + sound). But a record pinned PURE because
        # it is a `List[<record>]` ELEMENT (in `_list_element_record_types`) has an
        # IMMUTABLE field, so `p.x <- v` would be Why3 TYPE-REJECTED; and even a
        # standalone param of that (globally-pure) class cannot carry a caller-visible
        # store. Reject cleanly here (fail CLOSED) instead of emitting a Why3-ill-typed
        # `<-`. `self` field stores are unaffected (records with a mutation frame).
        if obj != "self":
            _obj_cls = getattr(self, "_current_symbol_table", {}).get(obj)
            if _obj_cls and _obj_cls in getattr(self, "_list_element_record_types", set()):
                from errors import PyCSLSemanticError
                raise PyCSLSemanticError(
                    f"in-place field mutation `{obj}.{field} = ...` of a record whose class "
                    f"`{_obj_cls}` is used as a `List[<record>]` element is out of scope: such "
                    f"a record is modelled as a PURE (immutable) Why3 record (Why3 forbids a "
                    f"mutable element inside `array`), so the field store cannot be made "
                    f"caller-visible. Rebuild the record (`{obj} = {_obj_cls}(...)`) instead.",
                    stage="module6-whyml",
                    code="PYCSL-WHYML-PARAM-COLLECTION-MUT",
                )
        val = self._expr_to_whyml(stmt.value, local_refs)
        if val == "true":
            val = "1"
        elif val == "false":
            val = "0"
        # Qualify the field label for ambiguous names (a field shared by >1 record,
        # e.g. two mixins/classes each with `count`) so the assignment target matches
        # the record's declared label — consistent with `_handle_field_get_expr`.
        # `_field_label` returns the bare name when unambiguous → byte-identical for
        # non-overlapping corpus.
        _rec_lower = (self._current_self_type if obj == "self"
                      else (getattr(self, "_current_record_var_classes", {}).get(obj, "") or "").lower() or None)
        safe_field = self._field_label(_rec_lower, field)
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
            hash_field = stable_hash(field)
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_fieldaugassign_stmt(
        self,
        stmt: FieldAugAssignStmt,
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        obj = stmt.object
        field = stmt.field
        val = self._expr_to_whyml(stmt.value, local_refs)
        op = op_translate(stmt.op)
        safe_field = whyml_ident(field)
        decl_fields = self._all_record_fields
        if field in decl_fields:
            code = f"{indent}{obj}.{safe_field} <- {obj}.{safe_field} {op} {val}"
        else:
            hash_field = stable_hash(field)
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_expr_stmt(
        self,
        stmt: ExprStmt,
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        val = stmt.value.to_dict()
        if val.get("type") == "Call":
            func = val.get("func", "")
            if func.endswith(".append") and self._value_semantic:
                arr_name = func.rsplit(".", 1)[0].replace(".", "_")
                safe_arr = whyml_ident(arr_name)
                arg = self._expr_to_whyml(val["args"][0], local_refs)
                arg = self._coerce_to_int(arg)
                if arr_name in getattr(self, "_seq_locals", set()):
                    # return-arr.md follow-on: `.append()` on a seq-promoted local grows the
                    # immutable seq via Seq.snoc (so `len` = Seq.length tracks the logical
                    # length), instead of the array-local `arr[!len] <- v; len += 1`.
                    code = f"{indent}{safe_arr} := Seq.snoc !{safe_arr} {arg}"
                else:
                    len_ref = f"{safe_arr}_len"
                    code = f"{indent}{safe_arr}[!{len_ref}] <- {arg};\n{indent}{len_ref} := !{len_ref} + 1"
            elif (func.endswith((".add", ".discard", ".remove"))
                  and self._value_semantic):
                # Body-level set/dict method calls. Sets and dicts share
                # the `_dict_locals` tracking and `map int (option int)`
                # model. Use program-level wrappers (see comment on
                # `map_update_some`) — `Map.set` is logic-only and Why3
                # rejects direct `:= Map.set ...` on non-ghost refs.
                method = func.rsplit(".", 1)[1]
                obj_name = func.rsplit(".", 1)[0]
                # M.7 (mutable-self-plan.md): `self.<setfield>.add(x)` on a
                # @mutable_state class is a REAL write to the record's mutable map
                # field (`self.f <- map_update_some self.f k 0`), so the method's
                # `writes { self.f }` frame is genuinely exercised (non-vacuous) —
                # instead of the opaque abstract-op that mutates nothing. Gated on
                # @mutable_state → byte-identical for every unmarked class.
                _msf = (obj_name.startswith("self.")
                        and getattr(self, "_current_self_type", None)
                        in getattr(self, "_mutable_state_classes", set())
                        and obj_name[len("self."):] in self._all_record_fields)
                if obj_name in getattr(self, "_dict_locals", set()) or _msf:
                    arg_ir = (val.get("args") or [{}])[0]
                    _ms_add = (getattr(self, "_current_self_type", None)
                               in getattr(self, "_mutable_state_classes", set()))
                    # cleared-hash.md S5: a κ = string set LOCAL (`_dict_key_types[obj]
                    # == "string"`, inferred from string-key membership/`.add`) is
                    # `map string (option int)` with the NATIVE string element — the
                    # write passes the RAW string, matching the membership read
                    # (`x in s`, which now reads the raw key too). No `str_hash_op`.
                    _set_kappa = getattr(self, "_dict_key_types", {}).get(obj_name)
                    # cleared-hash S4: a κ=string record SET FIELD (`self.<field>.add(x)`
                    # on a `set[str]` field → `map string (option int)`) writes the RAW
                    # native string element, matching the membership read `x in self.<field>`.
                    if _set_kappa is None and self._self_field_dict_kappa(obj_name) == "string":
                        _set_kappa = "string"
                    if _set_kappa == "string":
                        arg = self._expr_to_whyml(arg_ir, local_refs)
                    elif (_msf or _ms_add) and self._is_string_expr(arg_ir):
                        # M.7: a `Set[str]` key is hashed into the int-keyed map
                        # (`str_hash_op` for a non-literal) so `map_update_some`'s
                        # `k: int` typechecks — the frame's `writes` is what matters
                        # here, not str-key content (the no-more-int str-set model is
                        # a separate concern).
                        arg = self._str_operand_to_int(
                            self._expr_to_whyml(arg_ir, local_refs))
                    else:
                        arg = self._coerce_to_int(self._expr_to_whyml(arg_ir, local_refs))
                    if _msf:
                        _fld = f"self.{self._field_label(self._current_self_type, obj_name[len('self.'):])}"
                        _lhs, _cur = f"{_fld} <-", _fld
                    else:
                        safe_obj = whyml_ident(obj_name)
                        _lhs, _cur = f"{safe_obj} :=", f"!{safe_obj}"
                    if method == "add":
                        # set.add(x) — mark key present with Some 0.
                        # list-comprehension-lowering.md L5: in a @mutable_state module the
                        # decl is POLYMORPHIC (`map 'k (option 'v)`) so it unifies with a
                        # string-VALUED dict field (`_abstract_ops: Dict[str,str]`) — the
                        # name-dedup means one decl serves every map write in the module.
                        # Corpus modules keep the fixed `map int (option int)` → byte-identical.
                        # cleared-hash.md S5: a κ = string set local also needs the
                        # POLYMORPHIC decl so `map_update_some !s "a" 0` unifies at
                        # `map string (option int)` (the raw string element).
                        _poly = (getattr(self, "_mutable_state_classes", None)
                                 or _set_kappa == "string")
                        self._add_abstract_op(
                            ("val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) "
                             ": map 'k (option 'v)\n" if _poly else
                             "val map_update_some (m: map int (option int)) (k: int) (v: int) "
                             ": map int (option int)\n")
                            + "    ensures { result = Map.set m k (Some v) }")
                        code = f"{indent}{_lhs} map_update_some {_cur} {arg} 0"
                    else:
                        # set.discard(x) / set.remove(x) / del d[k] — clear the key.
                        # cleared-hash.md S5: POLYMORPHIC decl for a κ = string set so the
                        # native string element typechecks (`map string (option int)`).
                        _poly_none = (getattr(self, "_mutable_state_classes", None)
                                      or _set_kappa == "string")
                        self._add_abstract_op(
                            ("val map_update_none (m: map 'k (option 'v)) (k: 'k) "
                             ": map 'k (option 'v)\n" if _poly_none else
                             "val map_update_none (m: map int (option int)) (k: int) "
                             ": map int (option int)\n")
                            + "    ensures { result = Map.set m k None }")
                        code = f"{indent}{_lhs} map_update_none {_cur} {arg}"
                elif (getattr(self, "_current_symbol_table", {}).get(obj_name)
                      in ("set", "dict", "frozenset")
                      and getattr(self, "_current_self_type", None)
                      in getattr(self, "_mutable_state_classes", set())):
                    # typed-ir-for-b-ceiling.md §13: a set/dict-typed PARAM (not a
                    # `_dict_locals` body-local, not a self-field) mutated via
                    # `.add`/`.discard`/`.remove` — e.g. `declared_refs.add(target)` in a
                    # reflecting emitter handler. The mutation is on a value param, so it
                    # does NOT escape for an `assigns \nothing` / type-safety contract: a
                    # sound no-op. (A Python set param IS mutated, but no contract here
                    # reads it — the recursion's `declared_refs` is a trusted sibling arg.)
                    # Gated on @mutable_state → byte-identical for the corpus.
                    code = f"{indent}()"
                elif (obj_name in getattr(self, "_formal_params", [])
                      and obj_name not in getattr(self, "_dict_locals", set())
                      and getattr(self, "_current_symbol_table", {}).get(obj_name)
                      in ("set", "dict", "frozenset")):
                    # wrong-lowering-to-fix.md §WL-05 (set/dict twin of `d[k]=v`): an
                    # in-place mutation `s.add(x)` / `s.discard(x)` / `s.remove(x)` /
                    # `d.pop(k)` of a set/dict PARAMETER is REJECTED for the same reason
                    # as the dict item-write — Python mutates it by reference, the caller
                    # must SEE it, and the by-value map param carries no `writes {s}` frame.
                    # (Silently dropping the mutation to a no-op is sound but UNFAITHFUL —
                    # a caller-visible write vanishes.) Local sets (`_dict_locals`) and the
                    # deliberate @mutable_state param no-op above are unaffected.
                    self._reject_param_collection_mutation(obj_name, f"{obj_name}.{method}(...)")
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _stmts_to_whyml(self, stmts: List[Dict[str, Any]], local_refs: Set[str], declared_refs: Set[str], indent: str, in_loop: bool = False) -> str:
        """Recursively translates imperative statements into WhyML strings.

        Phase B (ir-schema-spec.md §6): each wire dict is converted to a typed
        `StmtIR` sum at entry (one `stmt_from_dict` call), then dispatched on
        the typed sum via `isinstance`. The lowering (the WhyML string each
        handler emits) is byte-identical to the prior dict-indexing path — the
        typed sum is an in-memory representation change only. `to_dict` is the
        inverse of `stmt_from_dict`, so nested `ExprIR`/`List[StmtIR]` fields
        round-trip faithfully when passed back to the still dict-based
        `_expr_to_whyml` / `_stmts_to_whyml` (Phase B migrates statements only;
        expressions.py is a follow-on)."""
        if not stmts: return ""

        stmt_d = stmts[0]
        rest = stmts[1:]
        stmt = stmt_from_dict(stmt_d)
        code = ""

        # Typed dispatch on the sum constructor (replaces the prior
        # `_STMT_HANDLERS` string table + `s_type == "…"` inline branches).
        # Each handler receives the typed subclass and uses typed field access.
        if isinstance(stmt, GhostAssignStmt):
            return self._handle_ghost_assign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, GhostArraySetStmt):
            return self._handle_ghost_array_set_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, AssignStmt):
            return self._handle_assign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, TupleUnpackStmt):
            return self._handle_tuple_unpack_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, AugAssignStmt):
            return self._handle_augassign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, FieldAssignStmt):
            return self._handle_fieldassign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, FieldAugAssignStmt):
            return self._handle_fieldaugassign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, ArraySetStmt):
            return self._handle_array_set_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, ArraySliceSetStmt):
            return self._handle_array_slice_set_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, WhileStmt):
            return self._handle_while_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, ReturnStmt):
            return self._handle_return_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, IfStmt):
            return self._handle_if_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, ForStmt):
            return self._handle_for_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, ExprStmt):
            return self._handle_expr_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, TryStmt):
            return self._handle_try_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, MatchStmt):
            return self._handle_match_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
        if isinstance(stmt, CriticalSectionStmt):
            return self._handle_critical_section_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        # Inline statement types (formerly inline in this orchestrator).
        # Label/Continue/Raise return directly; ProofAssert/Assert/Pass/Break
        # set `code` and fall through to the rest-chaining tail.
        if isinstance(stmt, LabelStmt):
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if not rest_code:
                rest_code = f"{indent}()"
            return f"{indent}label {stmt.name} in\n{rest_code}"

        if isinstance(stmt, ContinueStmt):
            return f"{indent}raise PyCSL_Continue"

        if isinstance(stmt, RaiseStmt):
            exc_type = safe_exc_name(stmt.exc_type or "PyCSL_Exception")
            return f"{indent}raise {exc_type}"

        if isinstance(stmt, ProofAssertStmt):
            kw = "check" if stmt.assert_kind == "check" else "assert"
            self._in_spec = True
            pred = self._expr_to_whyml(stmt.test.to_dict(), local_refs)
            self._in_spec = False
            origin = stmt.origin if stmt.origin is not _ABSENT else None
            comment = f"{indent}(* {origin} *)\n" if origin else ""
            code = f"{comment}{indent}{kw} {{ {pred} }}"

        elif isinstance(stmt, AssertStmt):
            code = f'{indent}()'

        elif isinstance(stmt, PassStmt):
            code = f"{indent}()"

        elif isinstance(stmt, BreakStmt):
            code = f"{indent}raise PyCSL_Break"

        elif isinstance(stmt, OpaqueStmt):
            # An OpaqueStmt means `stmt_from_dict` could not faithfully class
            # the wire dict (extra attribution keys not modeled by the typed
            # schema, or an unknown stmt kind). The standing gate's byte-diff
            # catches any new occurrence loudly; extend the typed sum class to
            # cover the missing field rather than falling back to dict indexing.
            from errors import PyCSLSemanticError
            raise PyCSLSemanticError(
                f"untyped IR stmt kind {stmt.kind!r} (opaque) is not covered "
                f"by the typed StmtIR dispatch; raw keys: {sorted(stmt_d.keys())}",
                stage="module6-stmt-dispatch",
                code="PYCSL-IR-OPAQUESTMT",
            )

        # Chain sequence of statements with semicolons
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)

        return code

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_frame_condition(self, assigns_list: List[Dict[str, Any]],
                              spec_refs: Set[str]) -> List[str]:
        """Generate WhyML frame condition lines from \\assigns contracts.

        In the Hoare model: no frame condition (value-semantic arrays can't alias).
        In typed/store models: emits `writes` + quantified `ensures` for unchanged locations.
        Returns a list of WhyML lines to append after the function's `ensures` clauses.
        """
        # A `val` (trusted stub / imported function / `#@ \abstract`) has NO body, so Why3
        # cannot INFER its `writes` from mutations — they must be declared explicitly. Without
        # them, the val is treated as pure (writes nothing), so an `ensures` describing a
        # post-state field (`_filesystem.fd_open[fd] == 0`) is read on the UNCHANGED field and
        # contradicts any prior fact about it (a preceding `open`'s `fd_open[result] == 1`),
        # making every consumer that composes two such mutating stubs VACUOUS (it proves
        # `false`). This is needed even in the Hoare/value-semantic model, where the `let` path
        # (writes inferred from the body's mutations) needs none. Emit `writes` for each
        # field-target assigns (`self.f` / `_filesystem.fd_open`). Assigns node shape:
        # {type:"Attribute"/"FieldGet", object:{type:"Var",name:X} | "X", attr|field:"f"}.
        if getattr(self, "_emitting_val_contract", False):
            nothings = [a for a in assigns_list
                        if isinstance(a, dict) and a.get("type") == "Nothing"]
            field_targets: List[str] = []
            for a in assigns_list:
                if not isinstance(a, dict) or a.get("type") not in ("Attribute", "FieldGet"):
                    continue
                obj = a.get("object")
                objname = obj.get("name") if isinstance(obj, dict) else obj
                field = a.get("attr") or a.get("field")
                # Only GLOBAL-field assigns (`_filesystem.fd_open`) need an explicit `writes`
                # here. A method's `self.<field>` assigns is already turned into the val's
                # `writes` by the existing method-writes machinery; re-emitting it produces an
                # unbound/duplicate target (regressed formal_coll/formal_que: `self._size`).
                if objname and objname != "self" and field:
                    t = f"{objname}.{field}"
                    if t not in field_targets:
                        field_targets.append(t)
            if field_targets and not nothings:
                return [f"    writes   {{ {', '.join(field_targets)} }}"]

        if self._value_semantic:
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

    # Still \trusted (bucket 3). Blocker: the body uses f-strings with literal
    # segments (`f"    try\n{body_code}\n    with Return_void -> () end"`).
    # pycsl lowers f-string literal segments to hashed INTs (the "f-strings
    # hash" limitation), so the body's `str_concat` receives an int where a
    # string is expected → WhyML type error. The typed-schema refactor does not
    # address this (it's a string-lowering limitation, not an Any-typed dict
    # blocker). A real postcondition (`ensures \result == "    try\n" ^ body_code
    # ^ "\n    with Return_void -> () end"`) is expressible in the contract
    # grammar, but the BODY cannot be verified against it without restructuring
    # the f-strings into explicit `+` concatenation — which would diverge from
    # the real source (forbidden by the Phase-C "copy exactly" rule).
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
            # return-arr.md: early/in-loop returns in an array-returning function are raised as
            # an immutable `Return_seq (seq int)` (Why3 forbids a mutable array payload); the
            # catch materializes the seq back to `array int` at the single result-slot boundary.
            return f"    try\n{body_code}\n    with Return_seq s -> materialize s end"
        if return_type == "array string":
            # str-list-elements: a STRING-element list returns through the parallel
            # `Return_seq_str (seq string)` exception; the catch materializes the seq
            # string back to `array string` (the string analogue of the `array int` arm).
            self._materialize_str_bridge()
            return f"    try\n{body_code}\n    with Return_seq_str s -> materialize_str s end"
        if return_type == "string":
            # 10-1732-gap Gap 1: a `string`-returning function with an early/in-loop
            # return raises `Return_str <string>`; the catch hands the payload straight
            # back (no materialize needed — `string` is immutable). Structured so a later
            # `Return_<T>` generalization (real/record) extends this branch.
            return f"    try\n{body_code}\n    with Return_str r -> r end"
        return f"    try\n{body_code}\n    with Return r -> r end"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_string_elem_read_locals(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """str-list-elements: locals that read an element of a string-element list. Two
        steps over the body: (1) collect array locals bound to a string-element-list
        call (`names = listdir(...)`, `listdir` in `_module_string_seq_funcs`); (2) any
        local assigned `that[i]` for such a `that` is a `string` (its array element type).
        Returns the string-typed element-read locals. Empty when no module function
        returns `array string`."""
        ssf = getattr(self, "_module_string_seq_funcs", set())
        if not ssf:
            return set()
        str_arrays: Set[str] = set()
        elem_reads: Set[str] = set()

        #@ \trusted reviewer: pycsl-self-annotate
        #@ requires True
        #@ ensures True
        #@ \diverges
        #@ assigns \nothing
        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign" and isinstance(node.get("target"), str):
                    v = node.get("value", {})
                    if isinstance(v, dict):
                        if (v.get("type") == "Call"
                                and isinstance(v.get("func"), str)
                                and whyml_ident(v["func"]) in ssf):
                            str_arrays.add(node["target"])
                        elif (v.get("type") == "Subscript"
                              and isinstance(v.get("value"), dict)
                              and v["value"].get("type") == "Var"
                              and v["value"].get("name") in str_arrays):
                            elem_reads.add(node["target"])
                for x in node.values():
                    rec(x)
            elif isinstance(node, list):
                for x in node:
                    rec(x)

        # Two passes so a `names[i]` read after the `names = listdir()` bind is caught
        # regardless of nesting/order (str_arrays must be fully populated first).
        rec(body_stmts)
        rec(body_stmts)
        # Reflect the inferred string type into the symbol table so the per-operation
        # `_is_string_expr` sites (sys_stat arg, `.append` element typing, `not in`)
        # also see `name : str`.
        st = getattr(self, "_current_symbol_table", None)
        if st is not None:
            for v in elem_reads:
                if st.get(v) in (None, "Any"):
                    st[v] = "str"
        return elem_reads

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_field_decode_str_locals(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """Locals assigned the null-terminated-field NAME-decode idiom
        `arr[a:b].split(b'\\x00')[0].decode('utf-8', ...)`. The expression
        recognizer (`expressions._recognize_field_decode_idiom`) lowers that
        VALUE to a `field_to_str …` STRING term, so the receiving variable must
        be a string-typed ref — never the integer `ref 0` pre-declaration.

        Without this, a local whose string-ness was previously discoverable ONLY
        from a manual `name: str` annotation (e.g. `_dir_lookup`) typechecks, but
        the SAME idiom in an un-annotated local (e.g. `listdir`'s `name = …`)
        stays `ref 0 : ref int` and the string assignment fails L3 typecheck
        ('type string, but is expected to have type int'). Keying the variable
        type on the idiom shape — the EXACT shape the value recognizer fires on —
        makes the two consistent in every context the recognizer fires.

        Byte-identical for any local NOT assigned this idiom (e.g. corpus files
        that never read a fixed-width null-padded byte field as a string)."""
        out: Set[str] = set()

        #@ \trusted reviewer: pycsl-self-annotate
        #@ requires True
        #@ ensures True
        #@ \diverges
        #@ assigns \nothing
        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign" and isinstance(node.get("target"), str):
                    v = node.get("value", {})
                    if (isinstance(v, dict) and v.get("type") == "Call"
                            and v.get("func") == "decode"
                            and self._match_field_decode_idiom(v) is not None):
                        out.add(node["target"])
                for x in node.values():
                    rec(x)
            elif isinstance(node, list):
                for x in node:
                    rec(x)

        rec(body_stmts)
        # Reflect into the symbol table so the per-operation string sites (the
        # `slot_name … = !name` assert RHS, `not in ('.', '..')`, `.append(name)`)
        # also see `name : str`, exactly as the explicit-annotation path does.
        st = getattr(self, "_current_symbol_table", None)
        if st is not None:
            for v in out:
                if st.get(v) in (None, "Any"):
                    st[v] = "str"
        return out

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _typed_local_vars(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """Body locals that carry a NON-int WhyML type — array, dict/set, lambda,
        record, or variant — and so must be EXCLUDED from the integer `ref 0`
        pre-declaration in `_emit_body_code`; each is instead let-bound at its
        first assignment with its real type. One classification pass (Part B move
        2) replacing the former five hand-maintained `body_<kind>_vars`
        subtractions — the variant kind was the fifth.

        A user record type may share a name with a collections constructor (a
        class `Counter` vs `collections.Counter`, corpus 0441); record locals are
        unioned in regardless, so the result is identical whether or not the
        dict/array vars are first deduped against records."""
        array_vars, dict_vars = IRScanner.find_array_and_dict_vars(body_stmts)
        # arity2.md (2b): seed transitive array-type propagation from array
        # PARAMS too (`_current_array1d_params`), not just syntactic array
        # locals — an inlined method returning a param (`_inl_res = a; work =
        # _inl_res`) flows array-ness out of a param. Params themselves are
        # already recognised at op sites; this just feeds the var-to-var chain.
        array_param_seed = array_vars | getattr(self, "_current_array1d_params", set())
        array_vars |= self._collect_array_var_assigns(body_stmts, seed=array_param_seed)
        array_vars -= getattr(self, "_current_array1d_params", set())
        dict_vars |= self._collect_dict_var_assigns(body_stmts)
        lambda_vars = IRScanner.find_lambda_vars(body_stmts)
        record_vars = IRScanner.find_record_vars(body_stmts, self._record_types)
        variant_vars = self._collect_variant_var_assigns(body_stmts)
        # 0442.md C2: a local bound to a tuple-returning call is a tuple value —
        # register its arity (so `p[i]` destructures) and exclude it from the `ref 0`
        # pre-decl (let-bound at first assignment, like the other typed locals).
        tuple_vars = self._collect_tuple_var_assigns(body_stmts)
        self._ghost_tuple_vars.update(tuple_vars)
        # 07-0903 W1: locals bound to a list/array of tuples → element arity.
        self._tuple_array_locals.update(self._collect_tuple_array_locals(body_stmts))
        # arity2.md (2b): expose the array-local set to the per-operation
        # `is_array` sites WITHOUT touching `_array_locals` (declaration path).
        # Reset per body — `_typed_local_vars` is called once per `_emit_body_code`.
        self._inline_array_temps = set(array_vars)
        # 07-2333-rev2 TP-1 (str locals): a `str`-typed local (symbol-table τ = str/string,
        # not a formal param) must NOT be pre-declared as `ref 0 : ref int` — it is let-bound
        # at first assignment with its string value (`let r = "ab" in`), the local counterpart
        # of the str-param lowering (`functions._param_type_str`). The unified type environment
        # (Γ_w) subsumes this set; this is the string class of it.
        string_vars = {
            name for name, ty in getattr(self, "_current_symbol_table", {}).items()
            if ty in ("str", "string") and name not in set(self._formal_params)
        }
        # str-list-elements: cross-function element-type propagation. A local bound to a
        # STRING-element-list-returning call (`names = listdir(...)`) is a string-element
        # array; an element READ of it (`name = names[i]`) is a `string`. Mark those
        # element-read locals as string so they let-bind as a string ref (not `ref 0`),
        # feeding a string-typed consumer (sys_stat). Byte-identical when no module
        # function returns `array string` (`_module_string_seq_funcs` empty).
        string_vars |= self._collect_string_elem_read_locals(body_stmts)
        # field-decode idiom locals: a local assigned
        # `arr[a:b].split(b'\x00')[0].decode('utf-8', ...)` receives the
        # recognizer's `field_to_str …` STRING value, so it must be a string
        # ref (not `ref 0`). Keys on the SAME shape the value recognizer fires
        # on, so the variable type and the assigned value stay consistent in
        # every context (annotated `_dir_lookup` AND un-annotated `listdir`).
        string_vars |= self._collect_field_decode_str_locals(body_stmts)
        self._string_local_vars = string_vars
        # 07-2333-rev2 Gap 3: a seq-promoted (growable) list LOCAL must NOT be pre-declared
        # as `ref 0 : ref int` — it is `ref (seq int)`, let-bound at its first assignment by
        # `_handle_seq_assign` (07-1705 P3). Excluding it here is what lets the first assign
        # emit `let items = ref (Seq.cons …)` instead of `items := …` onto an int ref (the
        # `seq int … expected int` leak). Params are not in pre_decl_vars, so unioning the
        # full set is safe.
        seq_local_vars = getattr(self, "_seq_locals", set()) - set(self._formal_params)
        return (array_vars | dict_vars | lambda_vars | record_vars | variant_vars
                | set(tuple_vars) | string_vars | seq_local_vars)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_body_code(self, func: Dict[str, Any], body_stmts: List[Dict[str, Any]],
                         local_refs: Set[str], ghost_vars: Set[str], ref_params: Set[str],
                         is_method: bool, return_type: str) -> str:
        """Build the WhyML body code string with pre-declared ref variables.
        Mutates self._array_locals, self._has_early_ret."""
        bounded_int = func.get("bounded_int")
        append_targets = IRScanner.find_append_targets(body_stmts)
        # Expose append-targets to `_handle_len_call` so `len(X)` in
        # invariants/specs resolves to `!X_len` (the dynamic counter)
        # instead of constant-folding to the initial-list size.
        self._current_append_targets = append_targets
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
        # Locals carrying a non-int WhyML type (array/dict/set/lambda/record/
        # variant) are excluded from the integer `ref 0` pre-declaration below —
        # each is let-bound at its first assignment with its real type. One
        # classification pass (Part B move 2) replaces the former five separate
        # `body_<kind>_vars` subtractions (incl. the record-vs-collections 0441
        # dedup, now subsumed by the union).
        typed_local_vars = self._typed_local_vars(body_stmts)
        # var -> class name for record-instance locals (`c = C()`), so method
        # calls `c.method(...)` can resolve the callee contract like `self.`.
        self._current_record_var_classes = IRScanner.find_record_var_classes(
            body_stmts, self._record_types)
        # no-more-int-3 A2a: a method call on a record-typed PARAM (`p.m(args)`)
        # resolves the callee contract too. `functions.py::_param_type_str`
        # populates `_record_param_classes` (param -> lowercased record name);
        # union it in so a record param behaves like a record local at the
        # dotted-call resolution site (expressions.py::_resolve_dotted_signature).
        self._current_record_var_classes.update(
            getattr(self, "_record_param_classes", {}))
        # Phase 2.3 / 2.3b: variables receiving `array int` values
        # from compile-time struct calls get array-typed pre-decls
        # instead of `ref 0 : ref int`. Two flavours with different
        # scoping:
        #   - tuple-unpack array slots: NOT hoisted; let-bound
        #     inside the loop (region-fresh per iteration)
        #   - plain struct.pack assigns: HOISTED with
        #     `ref (Array.make 0 0)` (single-shot, used later)
        struct_array_targets = self._collect_struct_unpack_array_targets(body_stmts)
        struct_pack_targets = self._collect_struct_pack_assign_targets(body_stmts)

        pre_decl_vars: Set[str] = {
            v for v in local_refs
            if v not in ghost_vars
            and v not in ref_params
            and v not in typed_local_vars
            and v not in struct_array_targets
            and v not in struct_pack_targets
        }

        if is_method:
            initial_declared = {whyml_ident(v) for v in pre_decl_vars}
        else:
            initial_declared = set(ref_params) | {whyml_ident(v) for v in pre_decl_vars}

        # Phase 2.3b of missing-bytes-struct-feature.md: do NOT hoist
        # struct-unpack array-typed targets to a function-top ref —
        # Why3's region inference cannot prove the hoisted
        # `ref (array int)` disjoint from the fresh-region array a
        # `val function struct_unpack_<id>` returns each loop
        # iteration. Excluding them from local_refs causes
        # `_handle_tuple_unpack_stmt` to emit `let X = ref tmp in`
        # scoped to the loop body — fresh region each iteration,
        # no cross-iteration alias.
        # growable-list: a `.append`-ed param that is seq-promoted is shadowed
        # as a `ref seq` in the append-targets loop below (`let p = ref (snapshot p)`).
        # Add it to `local_refs` so body resolution deref's it (`!p`) wherever it
        # appears — `Seq.length !p`, `Seq.get !p i`, `p := Seq.snoc !p v` — exactly
        # as a seq LOCAL (which is already in `local_refs`) is handled.
        seq_promoted_params = {
            t for t in append_targets
            if t in self._seq_locals and t in self._formal_params
        }
        body_code = self._stmts_to_whyml(
            body_stmts,
            (local_refs | {f"{t}_len" for t in append_targets} | seq_promoted_params)
                - struct_array_targets - struct_pack_targets,
            initial_declared
                - {whyml_ident(v) for v in struct_array_targets}
                - {whyml_ident(v) for v in struct_pack_targets},
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
            # 07-1705-rev4 P5: a seq-promoted PARAM is shadowed as a seq ref —
            # `let a = ref (snapshot a) in` — bridging the `array int` parameter into the
            # immutable growable `seq int` model for the body (concat/len/read via P3,
            # `return a` materialises back via P4).
            if var in self._seq_locals and var in self._formal_params:
                self._add_abstract_op(
                    "val snapshot (a: array int) : seq int\n"
                    "    ensures { Seq.length result = Array.length a }\n"
                    "    ensures { forall i:int. 0 <= i < Array.length a -> Seq.get result i = a[i] }")
                body_code = f"    let {safe_var} = ref (snapshot {safe_var}) in\n{body_code}"
                continue
            init = safe_var if var in self._formal_params else pfx
            body_code = f"    let {safe_var} = ref {init} in\n{body_code}"

        # Phase 2.3b: struct-unpack array-int targets are NO LONGER
        # pre-declared as `ref (Array.make 0 0)` at function-top.
        # Instead they fall through to `_handle_tuple_unpack_stmt`'s
        # `let X = ref tmp in` path, which scopes the ref to the
        # loop iteration where Why3's region inference is happy.

        # Plain struct.pack assign targets are NOT hoisted — the
        # Assign emitter sees them absent from local_refs and emits
        # `let X = struct_pack_... in <rest>`, which avoids the
        # `ref (array int)` → struct_pack region collapse Why3 would
        # otherwise reject.

        for tgt in sorted(append_targets):
            safe_tgt = whyml_ident(tgt)
            # growable-list: a `.append`-ed PARAM that is seq-promoted is bound as a
            # `ref seq` (consistent with the `Seq.snoc !tgt v` the body emits at
            # `_handle_expr_stmt`), NOT the `Array.make 1024 0` + `_len` array-counter
            # backing used for fresh append-locals. The array backing would type-clash
            # (`array int` ref-assigned a `seq int`), so reuse the seq-param shadow
            # `let tgt = ref (snapshot tgt) in` — the same bridge the pre_decl shadow
            # above applies to seq-promoted params (which never reach here, being
            # absent from `local_refs`). `len(tgt)` resolves via `Seq.length !tgt`
            # (already handled), so the `_len` counter is unnecessary and omitted.
            if tgt in self._seq_locals and tgt in self._formal_params:
                self._add_abstract_op(
                    "val snapshot (a: array int) : seq int\n"
                    "    ensures { Seq.length result = Array.length a }\n"
                    "    ensures { forall i:int. 0 <= i < Array.length a -> Seq.get result i = a[i] }")
                body_code = f"    let {safe_tgt} = ref (snapshot {safe_tgt}) in\n{body_code}"
                continue
            body_code = f"    let {safe_tgt}_len = ref {pfx} in\n{body_code}"
            if tgt not in local_refs and tgt not in ref_params:
                body_code = f"    let {safe_tgt} = Array.make 1024 0 in\n{body_code}"
                self._array_locals.add(tgt)

        if not body_code.strip():
            body_code = "    ()"
        if self._has_early_ret:
            body_code = self._wrap_body_with_return_catch(body_code, return_type)
        return body_code

