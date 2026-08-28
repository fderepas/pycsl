from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, TypedDict

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

# Bool-typed BinOp operators — RHS of any of these is a Python bool.
_BOOL_BINOPS = frozenset({'==', '!=', '<', '<=', '>', '>=', 'is', 'is not', 'in', 'not in'})


class ValIRBoolView(TypedDict):
    """Closed-key view of the two IR-expression keys `_val_is_bool` reads
    (`type`, `op` — both `str`). Runtime-inert (a TypedDict IS a dict), it
    monomorphizes to a native WhyML record so `val_ir.get("type")` lowers to the
    field read `val_ir.py_type` and the literal comparisons route through
    `str_eq_op`, not an opaque int-hash op."""
    type: str
    op: str

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
    _record_types: Dict[str, Any] = None
    _heap_var: str = ""
    _todict_aliases: Dict[str, str] = None
    _getattr_self_dict_aliases: Dict[str, str] = None
    _string_local_vars: Set[str] = None
    _emit_ir_local_vars: Set[str] = None
    _mutable_state_classes: Set[str] = None
    _current_record_var_classes: Dict[str, str] = None
    # self-tcb-reduction (_field_type_of conversion): the receiver-class lookup maps the
    # ported `_field_type_of` reads (matching the TypeInferenceMixin twin in types.py).
    # Declared as `Dict[str, str]` so `.get(receiver_name)` yields a STRING class name
    # (otherwise the untyped getattr defaults to an opaque int map and `cls := <int>`
    # fails to type against the `string`-typed `cls`).
    _module_global_classes: Dict[str, str] = None
    _record_param_classes: Dict[str, str] = None
    # self-tcb-reduction (_first_assign_kind / _rhs_yields_* conversion): the
    # module-level method return-type map, read by the ported RHS-type queries
    # (matching the TypeInferenceMixin twin in types.py). Typed `Dict[str, str]`
    # so `.get(key)` yields a STRING return-type name (e.g. "array int").
    _module_method_return_types: Dict[str, str] = None
    _list_element_record_types: Set[str] = None
    # SOUNDNESS (frame audit): these five are WRITTEN by live bodies mirrored here
    # (`_record_locals.add` / `_lambda_locals.add` in `_emit_first_assign`,
    # `_tuple_array_locals.update` in `_typed_local_vars`, `_current_append_targets`
    # and `_has_early_ret` in `_emit_body_code`) but were undeclared, so no `assigns`
    # frame could NAME them — the note B4 above ("the frame cannot be stated soundly")
    # was the symptom. Live counterparts: Module6_WhyMLTranspiler.__init__ (135/145/149),
    # module6_whyml/functions.py:293, module6_whyml/statements.py:3120.
    _record_locals: Set[str] = None
    _lambda_locals: Set[str] = None
    _tuple_array_locals: Dict[str, int] = None
    _current_append_targets: Set[str] = None
    _has_early_ret: int = 0
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
    #   _handle_array_set_stmt  ── validated-by: lemma array_set_code_state_coherent (Z3-Valid) + LINK-2
    #   _handle_seq_assign / _handle_tuple_unpack_stmt
    #                           ── validated-by: seq (lemma) ∘ assign (lemma) — proved fragment + LINK-2
    #   _handle_expr_stmt / _handle_fieldassign_stmt / _handle_fieldaugassign_stmt /
    #   _handle_array_slice_set_stmt
    #                           ── validated-by: lemma {expr,field_assign,field_aug,slice_set}_code_state_coherent
    #                              (Z3-Valid, effect axiom is the audited D2 boundary) + PROVED-COMPOSED in Rocq
    #                              (Phase6L_ComposeIfWhile.v emit_stmts_coherent, 0 Admitted) + LINK-2
    #   _handle_ghost_assign_stmt / _handle_ghost_array_set_stmt
    #                           ── validated-by: PROVED-COMPOSED in Rocq (reduce to assign/arrayset:
    #                              Phase6L_ComposeIfWhile.v ghost_assign_coh / ghost_arrset_coh) + LINK-2
    #   _handle_critical_section_stmt
    #                           ── validated-by: PROVED-COMPOSED via its body (critical_havoc P = P;
    #                              atomic critical_wrapper axiom, Phase6L_ComposeIfWhile.v) + LINK-2
    #                              (real concurrency havoc = Phase-7, still audited-trusted)
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
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_returns_string_collection(self, func_name: str) -> bool:
        """item34.md CF5: does the callee return a `string` NAME-collection? `IRScanner.find_*`/
        `collect_*` (seq-ified at source) or a `self.<m>`/record method whose declared return
        resolves to `array string`/`seq string` (the `_callee_raised_*` `List[str]` stubs)."""
        if not isinstance(func_name, str):
            return False
        if (func_name.startswith("IRScanner.find_")
                or func_name.startswith("IRScanner.collect_")):
            return True
        try:
            ret, _, _, _ = self._resolve_dotted_signature(func_name)
        except Exception:
            return False
        return ret in ("array string", "seq string")

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _resolve_dotted_signature(self, func_name: str) -> Tuple[str, List[str], int, int]:
        return ("", [], 0, 0)

    # cross-mixin twin of the already-green ExpressionEmissionMixin._str_operand_to_int
    # (expressions.py mirror): a string operand -> legacy int-hash domain. A quoted literal
    # hashes to its decimal `str(stable_hash(...))`; a non-literal goes through the
    # uninterpreted `str_hash_op` (registered via the trusted-effect-free `_add_abstract_op`,
    # matching the green expressions.py copy's `assigns \nothing`). Verbatim body port of the
    # LIVE `_str_operand_to_int`; pure string ops (str_strip/startswith/endswith/concat, stable_hash),
    # no new device/ADT/axiom, non-vacuous (the `whyml_str` param drives every guard + return).
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _str_operand_to_int(self, whyml_str: str) -> str:
        s = whyml_str.strip()
        if s.startswith('"') and s.endswith('"'):
            return str(stable_hash(whyml_str))
        self._add_abstract_op("val str_hash_op (s: string) : int")
        return f"(str_hash_op {whyml_str})"

    # cf6.md M1.4: the emit_ir-node predicate (`_handle_array_set_stmt` uses it to no-op an
    # `<emit_ir>[k]=v` write). Cross-mixin (lives in ExpressionEmissionMixin); a \trusted stub
    # here so the reflecting mirror type-checks the call.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _is_emit_ir_expr(self, ir: "ExprIR") -> bool:
        return False

    # SHADOWED-SELFCALL REPAIR (lesson (ay)): CONVERTED and PROVED, yet every
    # `self._field_label(...)` call site in this file went through the receiver-less abstract
    # `val self___field_label_<n>`, whose result is UNCONSTRAINED — so no caller saw anything
    # this body computes. The opt-in marker is the SECOND admission route into the
    # concrete lowering; the first (`_record_array_fields`) is a PROXY that holds only
    # for the parser-cursor shape and is empty for this file. Sound: the callee is a
    # same-file VERIFIED method in `_module_func_names`, and `scc.find_self_method_calls`
    # already supplies the callee-before-caller ordering edge for a marked callee.
    # Corpus byte-inert BY CONSTRUCTION — no corpus program writes the directive.
    #@ sibling_concrete
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_label(self, record_lower: str, field: str) -> str:
        """WhyML label for a record field. Ambiguous names (shared by >1
        record, e.g. an inherited field) are qualified `<record>_<field>` to
        avoid Why3's global field-label collision; unique names stay bare."""
        base = whyml_ident(field)
        if field in getattr(self, "_ambiguous_fields", set()) and record_lower:
            return f"{whyml_ident(record_lower)}_{base}"
        return base

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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
        # Bare identifier or a dotted FIELD access (`self.fields`) — could be array-typed (callee's
        # responsibility); pass through. (Track C / cprobe: clobbering `self.fields` to a placeholder
        # severs it from its representation invariant, so a callee's array precondition can never
        # discharge from `0 <= self.fields[k] <= MAX`.)
        if stripped.replace("_", "").replace("!", "").replace(".", "").isalnum():
            return whyml_str
        # L2 sub-gap 2 (os-bodyvc-spec): a function application `(fn arg…)` or array-literal
        # `(let _alit = …)` in an array slot is an array-returning expression (e.g. `(pack16 x)`,
        # `(materialize !s)`, the `[..]` literal). Pass it through — clobbering it to a placeholder
        # discards the value, which breaks contract-composition round-trips
        # (`unpack(pack(x)) == x` lost `pack(x)` to `(Array.make 1 0)`). Only genuinely-scalar args
        # (`0`, a numeric `(a + b)`) still get the placeholder.
        if stripped.startswith("("):
            inner = stripped[1:].lstrip()
            head = inner.split(" ", 1)[0] if " " in inner else inner.rstrip(")")
            head_ok = head.lstrip("!").replace("_", "").replace(".", "").isalnum()
            if head and head_ok and not head.lstrip("!")[:1].isdigit():
                return whyml_str
        # Anything else (BinOp result, parenthesised int expression) —
        # coerce to placeholder since we can't recover the array.
        return "(Array.make 1 0)"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _coerce_to_int(self, val: str) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_type_for(self, obj: str, field: str) -> Optional[str]:
        if obj != "self":
            return None
        cls = self._current_self_type
        if not cls:
            return None
        for info in self._record_types.values():
            if info.get("whyml_name") == cls:
                return info.get("field_types", {}).get(field)
        return None

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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _first_assign_kind(self, val: str, val_ir: "ExprIR") -> str:
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
        # body-gate gap-4: a list/array literal (`inode = [0, 1, 1, mode, …]`) IS an
        # array value — the detection passes add it to `_array_locals`, so it must be
        # VALUE-declared (`let X = (let _alit = Array.make … in … _alit)`), NOT `ref`.
        # The lowered string starts with `(let _alit = Array.make …`, not `(Array.make`,
        # so the string-prefix check below missed it and it fell to the `ref` default —
        # leaving `_array_locals` (read bare) and the `ref` decl inconsistent, so passing
        # the local as a whole value emitted the ref instead of its array contents.
        if vt in ("ArrayLit", "ListLit"):
            return "array"
        if (val.startswith("(Array.make") or val == "(Array.make 1024 0)"
                or val.startswith("(sorted_1 ")
                or val.startswith("(struct_pack_")):
            # struct_pack returns `array int` (a pure value). Emit it
            # as `let X = (struct_pack_...) in` (NOT wrapped in ref)
            # to avoid Why3's `ref (array int)` region-collapse error.
            return "array"
        if vt == "Call" and val_ir.get("func", "").startswith("self."):
            method_tail = val_ir["func"][len("self."):]
            cls = self._current_self_type
            lookup = f"{cls}__{method_tail}" if cls else method_tail
            if self._module_method_return_types.get(lookup) == "array int":
                return "array"
        # inline.md: bare function calls (from inlined bodies) returning
        # array int, and Var references to known array locals.
        if self._rhs_yields_array(val_ir):
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

    # SHADOWED-SELFCALL REPAIR (lesson (ay)): CONVERTED and PROVED, yet every
    # `self._rhs_yields_array(...)` call site in this file went through the receiver-less abstract
    # `val self___rhs_yields_array_<n>`, whose result is UNCONSTRAINED — so no caller saw anything
    # this body computes. The opt-in marker is the SECOND admission route into the
    # concrete lowering; the first (`_record_array_fields`) is a PROXY that holds only
    # for the parser-cursor shape and is empty for this file. Sound: the callee is a
    # same-file VERIFIED method in `_module_func_names`, and `scc.find_self_method_calls`
    # already supplies the callee-before-caller ordering edge for a marked callee.
    # Corpus byte-inert BY CONSTRUCTION — no corpus program writes the directive.
    #@ sibling_concrete
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _rhs_yields_array(self, val_ir: "ExprIR") -> bool:
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
            # bytes/bytearray are array-int-typed per
            # missing-bytes-struct-feature.md Phase 1.
            if self._current_symbol_table.get(name) in (
                    "list", "tuple", "bytes", "bytearray"):
                return True
            return False
        if t in ("Attribute", "FieldGet"):
            return self._field_type_of(val_ir) in (
                "list", "tuple", "bytes", "bytearray")
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

    # orelse_of mini-M1 (post-m1-census.md): CONVERTED. The `IfExpr` recursive arm's
    # `val_ir.get("body", {})` / `val_ir.get("orelse", {})` now terminates: the emit_ir
    # ADT gained an `IrIfExpr emit_ir emit_ir` constructor (preamble.py
    # `_emit_exprir_theory`, following the IrBinOp precedent) with `body_of`/`orelse_of`
    # projectors + the PROVEN `size_ifexpr_body_dec`/`size_ifexpr_orelse_dec` lemmas, and
    # `_EMIT_IR_PROJ` gained an unambiguous "orelse" entry plus a default-argument-shape
    # override that routes ".get(\"body\", {})" to the new scalar `body_of` (vs the
    # existing ".get(\"body\", [])" stmt-list `stmts_of`, unchanged). The `variant { size
    # val_ir }` now discharges via those two lemmas.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _rhs_yields_map(self, val_ir: "ExprIR") -> bool:
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _val_is_bool(val_ir: ValIRBoolView) -> bool:
        vt = val_ir.get("type", "")
        if vt in ("Compare", "BoolOp"):
            return True
        if vt == "UnaryOp" and val_ir.get("op") == "not":
            return True
        if vt == "BinOp" and val_ir.get("op") in _BOOL_BINOPS:
            return True
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _resolve_effective_ghost_type(self, target: str, op: str, ghost_type: str) -> str:
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _e(self, ir: "ExprIR", local_refs: Set[str]) -> str:
        return ""

    # SHADOWED-SELFCALL REPAIR (lesson (ay)): CONVERTED and PROVED, yet every
    # `self._field_type_of(...)` call site in this file went through the receiver-less abstract
    # `val self___field_type_of_<n>`, whose result is UNCONSTRAINED — so no caller saw anything
    # this body computes. The opt-in marker is the SECOND admission route into the
    # concrete lowering; the first (`_record_array_fields`) is a PROXY that holds only
    # for the parser-cursor shape and is empty for this file. Sound: the callee is a
    # same-file VERIFIED method in `_module_func_names`, and `scc.find_self_method_calls`
    # already supplies the callee-before-caller ordering edge for a marked callee.
    # Corpus byte-inert BY CONSTRUCTION — no corpus program writes the directive.
    #@ sibling_concrete
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_type_of(self, attr_ir: "ExprIR") -> Optional[str]:
        receiver_name = None
        field_name = None
        if attr_ir.get("type") == "Attribute":
            receiver = attr_ir.get("value") or attr_ir.get("object") or {}
            if isinstance(receiver, dict) and receiver.get("type") == "Var":
                receiver_name = receiver.get("name")
            field_name = attr_ir.get("attr")
        elif attr_ir.get("type") == "FieldGet":
            receiver_name = attr_ir.get("object")
            field_name = attr_ir.get("field")
        if receiver_name is None or field_name is None:
            return None
        cls = None
        if receiver_name == "self":
            cls = self._current_self_type
        else:
            gcls = getattr(self, "_module_global_classes", {}).get(receiver_name)
            if gcls is not None and gcls in self._record_types:
                cls = self._record_types[gcls].get("whyml_name")
            else:
                rvcls = getattr(self, "_current_record_var_classes", {}).get(receiver_name)
                if rvcls is not None and rvcls in self._record_types:
                    cls = self._record_types[rvcls].get("whyml_name")
                else:
                    pcls = getattr(self, "_record_param_classes", {}).get(receiver_name)
                    if pcls is not None:
                        cls = pcls
        if not cls:
            return None
        for info in self._record_types.values():
            if info.get("whyml_name") == cls:
                return info.get("field_types", {}).get(field_name)
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _maybe_emit_no_exception_assert(self, kind: tuple, args: List[str]) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _dv_store_value(self, nu: Optional[str], val_expr: str) -> str:
        """The value stored at `d[k] = val`: a `seq int` snapshots the array
        (ownership-discipline §3), a string/nested-map value passes through
        unhashed, otherwise int-coerce."""
        if nu == "seq int":
            self._add_abstract_op(
                "val function array_to_seq (a: array int) : seq int\n"
                "    ensures { Seq.length result = Array.length a }")
            return f"(array_to_seq {self._array_coerce_arg(val_expr)})"
        if nu == "string" or nu == "emit_ir" or (nu and nu.startswith("map ")):
            # cap-5: an emit_ir value (`kv[fname] = v`, v a value IR node) passes through
            # unhashed, like the string / nested-map cases.
            return val_expr
        return self._coerce_to_int(val_expr)

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
    #@ assigns self._array_locals, self._dict_locals, self._lambda_locals, self._record_locals
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
    def _handle_assign_stmt(self, stmt: AssignStmt, rest: List[Dict[str, Any]],
                             local_refs: Set[str], declared_refs: Set[str],
                             indent: str, in_loop: bool) -> str:
        # re-trusted: _handle_assign_stmt — `getattr(self, "_current_self_type", None) in
        # getattr(self, "_mutable_state_classes", set())` reflection leak, value-model-gapped
        # (self-scalar getattr-default collapses to int-0 vs string-keyed set) (see generic-dict-str-and.md)
        return ""

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
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
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

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
    def _handle_ghost_assign_stmt(self, stmt: GhostAssignStmt, rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        # re-trusted: _handle_ghost_assign_stmt — `len(val_ir.get("elts", []))` over a MkTuple emit_ir node
        # lowers to opaque `iter_length` (int) vs the `array emit_ir` args, emit_ir-reflection
        # value-model-gapped (Array.length not routed for emit_ir args) (see generic-dict-str-and.md)
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
    def _handle_tuple_unpack_stmt(self, stmt: TupleUnpackStmt, rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        # re-trusted: _handle_tuple_unpack_stmt — `getattr(self, "_current_self_type", None) in
        # getattr(self, "_mutable_state_classes", set())` reflection leak, value-model-gapped
        # (self-scalar getattr-default collapses to int-0 vs string-keyed set) (see generic-dict-str-and.md)
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._known_collection_sizes, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
    def _handle_array_set_stmt(self, stmt: ArraySetStmt, rest: List[Dict[str, Any]],
                                local_refs: Set[str], declared_refs: Set[str],
                                indent: str, in_loop: bool) -> str:
        # re-trusted: _handle_array_set_stmt — `getattr(self, "_current_self_type", None) in
        # getattr(self, "_mutable_state_classes", set())` reflection leak, value-model-gapped
        # (self-scalar getattr-default collapses to int-0 vs string-keyed set; `self.<field>`
        # also lowers opaque here) (see generic-dict-str-and.md)
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
    def _handle_augassign_stmt(
        self,
        stmt: AugAssignStmt,
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        # re-trusted: _handle_augassign_stmt — `getattr(self, "_current_self_type", None) in
        # getattr(self, "_mutable_state_classes", set())` reflection leak, value-model-gapped
        # (self-scalar getattr-default collapses to int-0 vs string-keyed set) (see generic-dict-str-and.md)
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
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
        if field in self._all_record_fields:
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
            # self-tcb-reduction typed-self-field-WRITE cap (FOUNDATION, reusable): a
            # `self.<field> = <val>` whose RHS is NOT int-typed (a `map string (option
            # string)` symbol table, a `string` self-type, an `option`/seq local) cannot go
            # through `_coerce_to_int` (which erases a map to int -> an L3-tc error against a
            # map RHS). FunctionEmissionMixin is opaque-int (not a @mutable_state record), so
            # the field value is not observed after the write here (the method returns a
            # string and the sibling readers take the local, not the self-field). Model the
            # write as a POLYMORPHIC, EFFECT-FREE `val setattr_<self>_poly (v: 'a)` — it
            # typechecks with ANY RHS type and carries no `writes` clause, so the method's
            # `assigns \nothing` frame holds. Parametric over the RHS type -> reusable across
            # the whole FunctionEmissionMixin writer class. Gated per-method -> byte-inert for
            # the corpus and every other mirror (a real corpus `self.<field> = <int>` keeps
            # the int `setattr` below).
            if (obj == "self" and self_type
                    and (self._emitting_refine_tuple_return_type()
                         or self._emitting_build_param_list())):
                self._add_abstract_op(
                    f"val setattr_{self_type}_poly (x: {self_type}) (f: int) (v: 'a) : unit")
                code = f"{indent}setattr_{self_type}_poly {obj} {hash_field} {val}"
            elif obj == "self" and self_type:
                self._add_abstract_op(f"val setattr_{self_type} (x: {self_type}) (f: int) (v: int) : unit")
                code = f"{indent}setattr_{self_type} {obj} {hash_field} {self._coerce_to_int(val)}"
            elif (field in ("lineno", "col_offset", "end_lineno", "end_col_offset")
                  and self._uses_pyast_parser()
                  and obj.lstrip("!") in getattr(self, "_emit_ir_local_vars", set())):
                # PYTHON-AST NODE CTOR FAMILY: the FOUR ASDL LOCATION ATTRIBUTES stamped
                # onto a freshly-built node (`n.lineno = t.start[0]`, the manual twin of
                # what `_fin` does). The harvested node model DELIBERATELY does not carry
                # them — `_fin` itself is modelled as IDENTITY for exactly that reason —
                # so the faithful lowering of the stamp is the unit no-op, NOT an abstract
                # `setattr_3` (which is additionally a LIE here: `emit_ir` is an IMMUTABLE
                # ADT, so no operation can mutate the value the local is bound to, and the
                # int-erasing `setattr_3 (x: int)` mistypes against it anyway). Both forms
                # are semantically no-ops — `setattr_3` returns unit and has no `writes` —
                # so this changes only which no-op is emitted. TRIPLE-GATED: one of the
                # four location attributes, in the pure_ast parser file, on an emit_ir
                # local -> byte-inert everywhere else.
                code = f"{indent}()"
            else:
                self._add_abstract_op("val setattr_3 (x: int) (f: int) (v: int) : unit")
                code = f"{indent}setattr_3 {self._coerce_to_int(obj)} {hash_field} {self._coerce_to_int(val)}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
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
        if field in self._all_record_fields:
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
    def _handle_expr_stmt(
        self,
        stmt: ExprStmt,
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        # re-trusted: _handle_expr_stmt — `getattr(self, "_current_self_type", None) in
        # getattr(self, "_mutable_state_classes", set())` reflection leak, value-model-gapped
        # (self-scalar getattr-default collapses to int-0 vs string-keyed set) (see generic-dict-str-and.md)
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._array_locals, self._decode_to_string, self._dict_locals, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._havoc_counter, self._in_spec, self._lambda_locals, self._record_locals, self._slice_set_tmp_counter, self._todict_aliases
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
        if return_type == "array emit_ir":
            # THE STATEMENT-LIST CARRIER: the emit_ir twin of the two arms above. The
            # payload is an immutable `seq emit_ir` (Why3 forbids a mutable array exception
            # payload) and `materialize_ir` brings it back to `array emit_ir` at the single
            # result-slot boundary — a fresh result pinned POINTWISE, so nothing is erased.
            # Reuses the SAME name the generic per-element-type return bridge already
            # emits for a `-> List[<elem>]` TAIL return (`materialize_<elem>`, here
            # `materialize_emit_ir`) — identical declaration text, so `_add_abstract_op`
            # dedups and the file carries ONE bridge rather than two synonyms.
            self._add_abstract_op(
                "val materialize_emit_ir (s: seq emit_ir) : array emit_ir\n"
                "    ensures { Array.length result = Seq.length s }\n"
                "    ensures { forall i:int. 0 <= i < Seq.length s -> result[i] = Seq.get s i }")
            return (f"    try\n{body_code}\n"
                    f"    with Return_seq_ir s -> materialize_emit_ir s end")
        if return_type == "string":
            # 10-1732-gap Gap 1: a `string`-returning function with an early/in-loop
            # return raises `Return_str <string>`; the catch hands the payload straight
            # back (no materialize needed — `string` is immutable). Structured so a later
            # `Return_<T>` generalization (real/record) extends this branch.
            return f"    try\n{body_code}\n    with Return_str r -> r end"
        return f"    try\n{body_code}\n    with Return r -> r end"

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
    #@ assigns self._dict_key_types, self._dict_locals, self._dict_value_types, self._emit_ir_local_vars, self._ghost_tuple_vars, self._inline_array_temps, self._seq_locals, self._string_local_vars, self._tuple_array_locals
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
    #@ assigns self._abstract_ops, self._array_locals, self._current_append_targets, self._current_record_var_classes, self._decode_to_string, self._dict_locals, self._emit_ir_local_vars, self._getattr_self_dict_aliases, self._ghost_array_vars, self._ghost_dict_vars, self._ghost_list_vars, self._ghost_set_vars, self._ghost_string_vars, self._ghost_tuple_vars, self._has_early_ret, self._havoc_counter, self._in_spec, self._inline_array_temps, self._lambda_locals, self._record_locals, self._seq_locals, self._slice_set_tmp_counter, self._string_local_vars, self._todict_aliases, self._tuple_array_locals
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

