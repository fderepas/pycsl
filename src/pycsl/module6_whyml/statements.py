from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from module6_whyml.identifiers import op_translate, whyml_ident, safe_mutex_name, safe_exc_name, stable_hash
from module6_whyml.ir_scanner import IRScanner
from module6_whyml.stmt_control_flow import ControlFlowStmtMixin

from ir_schema import (
    stmt_from_dict, _ABSENT,
    AssignStmt, AugAssignStmt, ArraySetStmt, ArraySliceSetStmt, DelSubscriptStmt,
    GhostAssignStmt, GhostArraySetStmt, TupleUnpackStmt,
    FieldAssignStmt, FieldAugAssignStmt, ExprStmt, CriticalSectionStmt,
    ReturnStmt, IfStmt, WhileStmt, ForStmt, TryStmt, MatchStmt,
    LabelStmt, RaiseStmt, ProofAssertStmt, AssertStmt,
    PassStmt, BreakStmt, ContinueStmt, OpaqueStmt,
)


class StatementEmissionMixin(ControlFlowStmtMixin):
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

    def _emit_first_assign(self, kind: str, indent: str, safe_target: str, target: str,
                           val: str, val_ir: Dict[str, Any],
                           local_refs=None) -> str:
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
            nu = self._dict_value_types.get(target)
            _empty = self._dv_empty_default(nu)
            if _empty:
                val = _empty
            # value-model-return-wall R3 (SOUNDNESS): a variable-valued dict LITERAL
            # `d = {"k": var}` must CONSTRUCT the real map — fold `map_update_some`
            # over the (key, value) pairs onto the empty base — not silently drop the
            # entries and declare an empty map (the latent false-theorem bug: an empty
            # map satisfies any `\result[k] == …` vacuously). `val` here is the empty
            # base (`(const (None: option ν))`); `_build_dict_literal_map` returns it
            # unchanged for an empty `{}` literal (byte-identical) and the folded map
            # for a non-empty one.
            val = self._build_dict_literal_map(val_ir, target, nu, val, local_refs)
            return f"{indent}let {safe_target} = ref {val} in\n"
        if kind == "bounded_int":
            return f"{indent}let {safe_target} = ref ({val} : int{self._bounded_int}) in\n"
        # self-ir-schema.md IR2: a REASSIGNED array-elem local first-bound from a record
        # array-field read (`body_stmts = stmt.body; body_stmts = body_stmts[:-1]`) must
        # COPY the field array — a `ref` aliasing a record's mutable-array field is an
        # illegal Why3 alias when later reassigned. `Array.copy` gives a fresh, reassignable
        # array. @mutable_state (the elem-type map is empty for the corpus).
        if (target in getattr(self, "_array_elem_types", {})
                and isinstance(val_ir, dict)
                and val_ir.get("type") in ("Attribute", "FieldGet")):
            val = f"(Array.copy {val})"
        if self._val_is_bool(val_ir):
            val = f"(if {val} then 1 else 0)"
        return f"{indent}let {safe_target} = ref {val} in\n"

    def _build_pyval_inner_map(self, val_ir: Dict[str, Any], local_refs=None) -> str:
        """J2/J3 convergence: build the INNER `map string (option hval)` for a nested
        dict literal `{"k": v, ...}` stored into a `Dict[str, Dict[str, PyVal]]` — native
        string keys, `_pyval_wrap`-tagged values, folded over the empty hval base. The
        bare-map analogue of `_pyval_wrap`'s `HMap` arm (which wraps the SAME fold as an
        `hval`). Corpus-inert (only the hval mirror stores a nested hval dict)."""
        base = "(const (None: option hval))"
        keys = val_ir.get("keys", []) or []
        values = val_ir.get("values", []) or []
        if not keys:
            return base
        self._add_abstract_op(
            "val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) "
            ": map 'k (option 'v)\n"
            "    ensures { result = Map.set m k (Some v) }")
        acc = base
        for k_ir, v_ir in zip(keys, values):
            k_low = self._expr_to_whyml(k_ir, local_refs)
            acc = f"(map_update_some {acc} {k_low} {self._pyval_wrap(v_ir, local_refs)})"
        return acc

    def _build_dict_literal_map(self, val_ir: Dict[str, Any], target: str,
                                nu: Optional[str], base: str,
                                local_refs=None) -> str:
        """value-model-return-wall R3 (SOUNDNESS FIX): construct the real map for a
        variable-valued dict literal `{"k0": v0, "k1": v1, …}` by folding the
        polymorphic `map_update_some` over the (key, value) pairs onto `base` (the
        empty `(const (None: option ν))` map).

        Returns `base` unchanged when `val_ir` is not a non-empty `DictLit`
        (byte-identical: an empty `{}` keeps the empty base, and a non-DictLit RHS
        is untouched). Each key is lowered per the dict's κ (native string key for a
        `Dict[str, _]`, `str_hash_op` for a string key into an int-keyed dict, else
        int-coerced) and each value per ν via `_dv_store_value` — the SAME
        key/value discipline as the proven `d[k] = v` subscript-store path
        (statements.py `map_update_some` branch), so the literal and the store agree.
        This supersedes the former silent empty-map drop (the latent false-theorem
        bug: an empty map vacuously satisfies any `\\result[k] == …`)."""
        if not (isinstance(val_ir, dict) and val_ir.get("type") == "DictLit"):
            return base
        keys = val_ir.get("keys", [])
        values = val_ir.get("values", [])
        if not keys:
            return base
        kappa = self._dict_key_types.get(target)
        self._add_abstract_op(
            "val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) "
            ": map 'k (option 'v)\n"
            "    ensures { result = Map.set m k (Some v) }")
        acc = base
        for k_ir, v_ir in zip(keys, values):
            k_low = self._expr_to_whyml(k_ir, local_refs)
            if kappa == "string":
                k_str = k_low
            elif not self._in_spec and self._is_string_expr(k_ir):
                self._add_abstract_op("val str_hash_op (s: string) : int")
                k_str = f"(str_hash_op {k_low})"
            else:
                k_str = self._coerce_to_int(k_low)
            if nu == "hval":
                # hval-value-model-wall: each heterogeneous value is FAITHFULLY tagged
                # into its `hval` constructor (str→HStr, int→HInt, list→HArr, …) — no
                # int-erasure. Key is the native string (κ = string for `Dict[str, PyVal]`).
                v_str = self._pyval_wrap(v_ir, local_refs)
            else:
                v_low = self._expr_to_whyml(v_ir, local_refs)
                v_str = self._dv_store_value(nu, v_low)
            acc = f"(map_update_some {acc} {k_str} {v_str})"
        return acc

    # --- tool-feature-5: Optional-typed MUTABLE program locals -----------------
    # A local declared `x: Optional[τ] = None` monomorphizes (Module5) to a
    # synthesized per-function union `_union_<fn>_<idx> = Arm_<idx>_0 τ |
    # Arm_<idx>_None` and lives as a `ref _union_<fn>_<idx>`. The three sites the
    # generic lowering must handle — decl/assign `x = v`, `x is None` guard, and a
    # union-context read `x` — all reuse this per-function union (NOT a parallel
    # type). GENERIC: keyed only on the local's declared Optional[τ] type and its
    # `None` init, never on any method/local name.

    def _union_local_symtype(self, name: str) -> Optional[str]:
        """The synthesized `_union_*` type of a mutable Optional LOCAL `name`
        (symbol-table τ starts with `_union_`, and `name` is not a formal
        parameter — a union PARAM keeps its own value/spec lowering). Else None."""
        if not isinstance(name, str):
            return None
        t = getattr(self, "_current_symbol_table", {}).get(name)
        if (isinstance(t, str) and t.startswith("_union_")
                and name not in set(self._formal_params)):
            return t
        return None

    def _union_ctors(self, symtype: str) -> "tuple":
        """(none_ctor, [some_ctor, ...]) for a synthesized union `symtype` —
        the nullary `Arm_*_None` and the payload-carrying `Arm_*_i` arms."""
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None, []
        none_ctor = None
        some_ctors: List[str] = []
        for cn, c in vinfo.get("constructors", {}).items():
            if c.get("arity") == 0 and "None" in cn:
                none_ctor = cn
            else:
                some_ctors.append(cn)
        return none_ctor, some_ctors

    def _union_wrap_rhs(self, symtype: str, val: str,
                        val_ir: Dict[str, Any]) -> Optional[str]:
        """Lift a plain RHS into the matching union arm ctor for an assignment to
        an Optional local: `None` → the nullary None-arm; a τ value → the single
        `Some`-arm `(Arm_i_0 v)`. Returns None for a multi-arm union with a
        non-None value (out of scope — Optional[τ] has exactly one Some-arm) so
        the caller falls back to the ordinary path."""
        none_ctor, some_ctors = self._union_ctors(symtype)
        if none_ctor is None:
            return None
        if val_ir.get("type") == "None":
            return none_ctor
        if len(some_ctors) == 1:
            return f"({some_ctors[0]} {val})"
        return None

    def _emit_array_local_reassign(self, target: str, safe_target: str, indent: str,
                                    val_ir: Dict[str, Any], local_refs: Set[str]) -> str:
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
        # opaque-nested-map-reader: `<local> = getattr(self, "_field", {})` where
        # <local> is a registered opaque-selfmap alias — emit NOTHING (the local is
        # never a real value; `k in <local>` and `<local>[k]["lit"]` route to the
        # boundary readers). Mirrors the `.to_dict()` alias suppression above.
        if target in getattr(self, "_opaque_selfmap_aliases", {}):
            _rest = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            return _rest if _rest else f"{indent}()"
        # opaque-nested-map-reader SPLIT form: `_rt = getattr(self, "_record_types",
        # {}).get(tag)` binds an inner-alias local — emit NOTHING (the local is never a
        # real value; `_rt["<lit>"]` / `_rt.get("<lit>")` / `if _rt` route to the boundary
        # readers keyed on the outer key). Mirrors the opaque-selfmap alias suppression above.
        if target in getattr(self, "_opaque_selfmap_inner_aliases", {}):
            _rest = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            return _rest if _rest else f"{indent}()"
        # 7a (self-tcb-reduction L4b): `tparams = getattr(<node>,"type_params",None) or []`
        # binds a pure tparam_list ALIAS (`_tparam_iter_recv` resolves `for tp in tparams`
        # to `(type_params_of node)`) — emit NOTHING, exactly like the `.to_dict()` /
        # opaque-selfmap alias suppression above. Byte-inert (`_tparam_list_aliases` empty
        # outside the tparam collector).
        if target in getattr(self, "_tparam_list_aliases", {}):
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

        # tool-feature-5: Optional MUTABLE local (`x: Optional[τ] = None; x = v`).
        # The local is a `ref _union_*`; wrap the RHS in the matching arm ctor
        # (None → the nullary None-arm, a τ value → the single Some-arm) so both
        # the first `let x = ref (Arm_i_None : _union) in` declaration and every
        # later `x := (Arm_i_0 v)` reassignment type-check against the union ref.
        # Reuses the SAME per-function union Module5 already synthesized for the
        # type (shared with the `-> Optional[τ]` return via the Module5 dedup).
        _ult = self._union_local_symtype(target)
        if _ult is not None:
            _wrapped = self._union_wrap_rhs(_ult, val, val_ir)
            if _wrapped is not None:
                if target not in declared_refs:
                    declared_refs.add(target)
                    _wn = self._variant_types[_ult]["whyml_name"]
                    code = f"{indent}let {safe_target} = ref ({_wrapped} : {_wn}) in\n"
                    rest_code = self._stmts_to_whyml(
                        rest, local_refs, declared_refs, indent, in_loop)
                    if not rest_code:
                        rest_code = f"{indent}()"
                    return code + rest_code
                code = f"{indent}{safe_target} := {_wrapped}"
                if rest:
                    code += ";\n" + self._stmts_to_whyml(
                        rest, local_refs, declared_refs, indent, in_loop)
                return code

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

        # set-value-model-wall (self-tcb-reduction, Tier-5): an emitter-local
        # `Set[str]` value (annotated `Set[str]` + `= set()`) is a `ref StrSet.set`
        # over the executable `set.SetApp[string]` clone. `set()` -> `StrSet.empty ()`
        # (NOT the int-erased `ref (const (None: option int))` / `ref 0`). Its `.add`
        # rebinds the ref (`s := StrSet.add x !s`, handled in `_handle_set_add_expr`)
        # and `in`/`not in` reads a program-bool `StrSet.mem` guard. Gated on
        # `_str_set_locals` -> corpus byte-inert.
        if target in getattr(self, "_str_set_locals", set()):
            safe = whyml_ident(target)
            if target not in declared_refs:
                declared_refs.add(target)
                local_refs.add(target)   # set locals are refs -> reads deref `!s`
                rest_code = self._stmts_to_whyml(
                    rest, local_refs, declared_refs, indent, in_loop)
                if not rest_code:
                    rest_code = f"{indent}()"
                return f"{indent}let {safe} = ref (StrSet.empty ()) in\n{rest_code}"
            code = f"{indent}{safe} := StrSet.empty ()"
            if rest:
                code += ";\n" + self._stmts_to_whyml(
                    rest, local_refs, declared_refs, indent, in_loop)
            return code

        # K7 (pyval-chained `.get`, self-tcb-reduction Tier-5): a `pyval`-valued chain
        # local (`registry = self.f.get(k) or {}`; `info = registry.get(k, {})`) is
        # `let`-bound IMMUTABLE (single-assignment SSA chain) — NOT the int/string `ref`
        # hoist that would int-erase it and route its `.get` to an opaque `registry_get_2`.
        # `val` already carries the faithful pyval lowering (the `_lower_dict_get_call`
        # PMap arm / the `_recognize_pyval_or_default` projection). Gated on
        # `_pyval_locals` -> corpus byte-inert.
        if (target in getattr(self, "_pyval_locals", set())
                and target not in declared_refs):
            declared_refs.add(target)
            code = f"{indent}let {safe_target} = {val} in\n"
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if not rest_code:
                rest_code = f"{indent}()"
            return code + rest_code

        if target not in declared_refs:
            declared_refs.add(target)
            kind = self._first_assign_kind(val, val_ir)
            code = self._emit_first_assign(kind, indent, safe_target, target, val,
                                           val_ir, local_refs)
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

    def _seq_init_expr(self, val_ir: Dict[str, Any], local_refs: Set[str]) -> str:
        """07-1705-rev4 P3: lower a seq-local's RHS to a `seq int` value. A list literal
        `[v0, v1, …]` becomes a `Seq.cons` chain (qualified); any other array-typed RHS
        is bridged with `snapshot`."""
        # module-const-dict READ (`list(X.values())` / `[v for k,v in X.items() if k in s]`)
        # -> a faithful `seq string` chain of the const dict's own value literals. Mirror-only
        # const-dict theory (byte-inert: no corpus program reads a module-const dict this way).
        _cds = self._const_dict_value_seq(val_ir, local_refs)
        if _cds is not None:
            return _cds
        if val_ir.get("type") == "ArrayLit":
            expr = "Seq.empty"
            for e in reversed(val_ir.get("elts", [])):
                es = self._coerce_to_int(self._expr_to_whyml(e, local_refs))
                expr = f"(Seq.cons {es} {expr})"
            return expr
        return self._seq_operand(val_ir, local_refs)

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

    def _call_returns_seq_string(self, func_name: str) -> bool:
        return self._call_returns_string_collection(func_name)

    def _seq_snapshot_op(self) -> None:
        """item34.md CF5: register the polymorphic `snapshot : array 'a -> seq 'a` bridge
        (fresh seq, length- and element-preserving). Used to seq-ify a name-collection at its
        SOURCE (`find_*`/`.split`) so the whole `try` collection flow is uniformly `seq`."""
        if getattr(self, "_mutable_state_classes", None):
            self._add_abstract_op(
                "val snapshot (a: array 'a) : seq 'a\n"
                "    ensures { Seq.length result = Array.length a }\n"
                "    ensures { forall i:int. 0 <= i < Array.length a -> Seq.get result i = a[i] }")
        else:
            self._add_abstract_op(
                "val snapshot (a: array int) : seq int\n"
                "    ensures { Seq.length result = Array.length a }\n"
                "    ensures { forall i:int. 0 <= i < Array.length a -> Seq.get result i = a[i] }")

    def _seq_value_producing(self, v: Any) -> bool:
        """item34.md CF5: does `v` ALREADY lower to a `seq string` (so `_seq_operand` must NOT
        re-`snapshot` it)? The seq-ified-at-source name-collection ops: `find_*`/`collect_*`,
        `<str>.split(…)`, `sorted(<seq>)`, a `[a]+[comp]` concat, and the ternary of such."""
        if not isinstance(v, dict):
            return False
        t, f = v.get("type"), v.get("func")
        # #15: `self._nested_seq_field.get(k)` already lowers to `seq _` (`Dict[str,List[T]]`) —
        # pass through, no `snapshot` (which expects an array).
        if (t == "Call" and isinstance(f, str) and f.endswith(".get")
                and f[:-len(".get")].startswith("self.")):
            _nu = self._self_field_dict_nu(f[:-len(".get")])
            if isinstance(_nu, str) and _nu.startswith("seq "):
                return True
        if t == "Call" and isinstance(f, str):
            if (f.startswith("IRScanner.find_") or f.startswith("IRScanner.collect_")
                    or f.endswith(".split")):
                return True
            if f == "sorted" and v.get("args"):
                _a0 = v["args"][0]
                return (isinstance(_a0, dict) and _a0.get("type") == "Var"
                        and _a0.get("name") in self._seq_locals)
            if f in ("set", "frozenset", "list") and v.get("args"):
                return self._seq_value_producing(v["args"][0])
        if (t == "BinOp" and v.get("op") == "+"
                and isinstance(v.get("left"), dict)
                and v["left"].get("type") in ("ArrayLit", "ListLit", "ListComp")):
            return True
        if t == "IfExpr":
            return (self._seq_value_producing(v.get("body"))
                    or self._seq_value_producing(v.get("orelse")))
        if t == "ListComp":
            # `[e for e in <seq>]` lowers to `list_comp_seq_*` (a `seq`) — pass through.
            for _g in (v.get("generators") or []):
                _it = _g.get("iter", {})
                if (isinstance(_it, dict) and _it.get("type") == "Var"
                        and _it.get("name") in self._seq_locals):
                    return True
        return False

    def _seq_operand(self, val_ir: Dict[str, Any], local_refs: Set[str]) -> str:
        """07-1705-rev4 P3: an operand that must be a `seq int` — `!b` if `b` is itself a
        seq local, else `snapshot(b)` to bridge an array-modelled value into seq."""
        if val_ir.get("type") == "Var" and val_ir.get("name") in self._seq_locals:
            return f"(!{whyml_ident(val_ir['name'])})"
        # seq-model-pivot.md SQ3: a SLICE of a seq local (`body_stmts[:-1]`) already lowers to
        # a `seq` value (`seq_sub`) — pass it through, no `snapshot` (which expects an array).
        if (val_ir.get("type") in ("Subscript", "SliceAccess")
                and isinstance(val_ir.get("value"), dict)
                and val_ir["value"].get("type") == "Var"
                and val_ir["value"].get("name") in self._seq_locals):
            return self._expr_to_whyml(val_ir, local_refs)
        # item34.md CF5: a value that ALREADY lowers to `seq string` — `find_*`/`collect_*`/
        # `<str>.split(…)` (snapshot-at-source), `sorted(<seq>)`, a `[a]+[comp]` concat, or the
        # `<split> if … else [x]` ternary of such — is passed through WITHOUT re-`snapshot`.
        if getattr(self, "_mutable_state_classes", None) and self._seq_value_producing(val_ir):
            return self._expr_to_whyml(val_ir, local_refs)
        # seq-model-pivot.md SQ2: POLYMORPHIC `snapshot` in a @mutable_state module (bridges a
        # `List[StmtIR]`/`List[str]` field → `seq emit_ir`/`seq string`); the corpus's
        # `array int → seq int` snapshot is byte-identical (no @mutable_state).
        if getattr(self, "_mutable_state_classes", None):
            self._add_abstract_op(
                "val snapshot (a: array 'a) : seq 'a\n"
                "    ensures { Seq.length result = Array.length a }\n"
                "    ensures { forall i:int. 0 <= i < Array.length a -> Seq.get result i = a[i] }")
        else:
            self._add_abstract_op(
                "val snapshot (a: array int) : seq int\n"
                "    ensures { Seq.length result = Array.length a }\n"
                "    ensures { forall i:int. 0 <= i < Array.length a -> Seq.get result i = a[i] }")
        return f"(snapshot {self._expr_to_whyml(val_ir, local_refs)})"

    def _materialize_bridge(self) -> None:
        """07-1705-rev4 P4: emit the faithful seq→array bridge val (fresh result, no
        region link), used where a seq-modelled value crosses into `array int` code."""
        self._add_abstract_op(
            "val materialize (s: seq int) : array int\n"
            "    ensures { Array.length result = Seq.length s }\n"
            "    ensures { forall i:int. 0 <= i < Seq.length s -> result[i] = Seq.get s i }")

    def _materialize_str_bridge(self) -> None:
        """str-list-elements: the STRING analogue of `_materialize_bridge` — bridges a
        `seq string` (a growable string list) to a fresh `array string` at the return
        slot, so a list of strings returns as `array string`."""
        self._add_abstract_op(
            "val materialize_str (s: seq string) : array string\n"
            "    ensures { Array.length result = Seq.length s }\n"
            "    ensures { forall i:int. 0 <= i < Seq.length s -> result[i] = Seq.get s i }")

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

    @staticmethod
    def _abstract_val_receiver_and_tail(existing: str, arity_fn: str) -> Tuple[str, str]:
        """Split an already-registered abstract `val <arity_fn> …` declaration into
        (receiver-binder prefix, trailing-clause tail) so a rewrite of its parameter
        list can carry both across.

        `_handle_dotted_call` gives a state-taking self-call's abstract op a leading
        `(self: <class>)` binder (A2c) plus a `writes { self.<f> }` clause (gap7) and
        `ensures` clauses; the tuple-unpack rewrite rebuilds only the `(xi: τ)` list, so
        without this both would be lost. Returns `("", "")` when the existing decl has
        neither (every declaration in the reference corpus) → byte-inert there."""
        if not existing:
            return "", ""
        head = existing.split("\n", 1)
        tail = "\n" + head[1] if len(head) > 1 else ""
        import re as _re
        m = _re.match(r"val\s+" + _re.escape(arity_fn) + r"\s+(\(self:[^)]*\)\s*)", head[0])
        return (m.group(1) if m else ""), tail

    def _partition_unpack_projs(self, val_ir: Dict[str, Any], targets: List[str],
                                 local_refs: Set[str]) -> Optional[List[str]]:
        """LEVER F1: a 3-target tuple-unpack whose RHS is `<str>.partition(<sep>)` /
        `<str>.rpartition(<sep>)` → the 3 faithful string projections
        `(<op>_before recv sep)`, `(<op>_sep recv sep)`, `(<op>_after recv sep)`, where
        the 3 ops are opaque `string→string→string` `val`s WITH NO ensures (axiom-free,
        the same trust class as the landed `__before`/`__after` in
        `emit_global_call_target_group`; rpartition = the last-separator variant). The
        expression-level, shape-driven counterpart of that whole-function facade. Returns
        None (fail-closed) unless the exact shape holds AND the receiver is string-typed
        AND we are in a @mutable_state emitter method → corpus byte-inert."""
        if (getattr(self, "_current_self_type", None)
                not in getattr(self, "_mutable_state_classes", set())):
            return None
        if len(targets) != 3:
            return None
        if val_ir.get("type") != "Call":
            return None
        func = val_ir.get("func")
        if not (isinstance(func, str) and "." in func):
            return None
        recv_name, method = func.rsplit(".", 1)
        if method not in ("partition", "rpartition"):
            return None
        args_ir = val_ir.get("args") or []
        if len(args_ir) != 1:
            return None
        recv_ir = {"type": "Var", "name": recv_name}
        if not self._is_string_expr(recv_ir):
            return None
        recv_w = self._expr_to_whyml(recv_ir, local_refs)
        sep_w = self._expr_to_whyml(args_ir[0], local_refs)
        op = "str_rpartition" if method == "rpartition" else "str_partition"
        for suffix in ("before", "sep", "after"):
            self._add_abstract_op(
                f"val {op}_{suffix} (s: string) (sep: string) : string")
        return [f"({op}_before {recv_w} {sep_w})",
                f"({op}_sep {recv_w} {sep_w})",
                f"({op}_after {recv_w} {sep_w})"]

    def _handle_tuple_unpack_stmt(self, stmt: TupleUnpackStmt, rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        targets = stmt.targets
        val_ir = stmt.value.to_dict()
        val_whyml = self._expr_to_whyml(val_ir, local_refs)
        safe_targets = [whyml_ident(t) for t in targets]
        # LEVER F1: string-triple partition/rpartition unpack — bypass the opaque
        # `<fn>_rpartition_1 (int):(int,int,int)` abstract-op path below and emit the
        # 3 faithful string projections instead (see `_partition_unpack_projs`).
        _partition_projs = self._partition_unpack_projs(val_ir, targets, local_refs)
        # resync-campaign.md R2 (continuation): every discard target (`_`) maps to
        # `whyml_ident("_") == "py_underscore"`. With MULTIPLE discards (`ret, _, _,
        # _ = f()`) they collide into one `_tu_py_underscore` binder (a Why3
        # duplicate-variable in the tuple pattern) AND one shared `py_underscore`
        # ref that then receives heterogeneously-typed slots (`array string`, int)
        # → an ill-typed `:=`. Give each SUBSEQUENT discard its own positional
        # name so the pattern binders are unique and each discard becomes its own
        # correctly-typed `let py_underscore_k = ref …`. Only repeated `_` slots
        # rename — a single `_` (the only form the corpus emits today; multi-`_`
        # was a hard Why3 error) is untouched, so emission is byte-identical there.
        _du_seen = 0
        for _du_i, _du_t in enumerate(targets):
            if _du_t == "_":
                if _du_seen > 0:
                    safe_targets[_du_i] = f"py_underscore_{_du_seen}"
                _du_seen += 1
        if _partition_projs is None and val_ir.get("type") == "Call":
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
                # frame-audit fix (state-taking tuple callee): `_handle_dotted_call`
                # registers the abstract `val` for a `self.<m>(...)` whose callee declares
                # a non-empty self-field frame WITH a leading receiver binder
                # `(self: <class>)` and a `writes { self.<f> }` clause, and emits a call
                # site that PASSES `self`. The rewrites below rebuild the declaration from
                # the callee's declared PARAMETER types only, so both the receiver binder
                # and the `writes` clause were silently dropped — the emitted application
                # `(self__m_3 self …)` then ill-typed against a receiver-less `val`
                # ("This expression has type <class> @rho, but is expected to have type
                # emit_ir"), and the lost `writes` re-introduced the very false frame the
                # non-empty `assigns` was declared to state. Carry both across the rewrite.
                _recv_pfx, _decl_tail = self._abstract_val_receiver_and_tail(
                    self._abstract_ops.get(arity_fn, ""), arity_fn)
                if nargs == 0:
                    self._abstract_ops[arity_fn] = (
                        f"val {arity_fn} {_recv_pfx}() : {tuple_ret}{_decl_tail}"
                        if _recv_pfx else f"val {arity_fn} () : {tuple_ret}{_decl_tail}")
                elif len(_cpt) == nargs:
                    params = " ".join(f"(x{i}: {_cpt[i]})" for i in range(nargs))
                    self._abstract_ops[arity_fn] = (
                        f"val {arity_fn} {_recv_pfx}{params} : {tuple_ret}{_decl_tail}")
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
                    self._abstract_ops[arity_fn] = (
                        f"val {arity_fn} {_recv_pfx}{params} : {tuple_ret}{_decl_tail}")
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
        _mt_recv = self._mktuple_elts_recv_ir(val_ir)
        if _partition_projs is not None:
            # LEVER F1: per-slot `let _tu_<t> = (<op>_before/sep/after recv sep) in` — the
            # 3 faithful string projections replace the opaque int-tuple destructure.
            lines = [f"{indent}let {tmp_names[i]} = {_partition_projs[i]} in"
                     for i in range(len(tmp_names))]
        elif _mt_recv is not None:
            # value-model campaign incr7 (primitive #2): `_a, _b = <emit_ir>.elts` in a dict
            # walker → per-index `irnth i (elts_of recv)` (the MODELLED IrMkTupleN element),
            # NOT the opaque `args_of` tuple-destructure the generic path emits. Each `_tu_<t>`
            # binds the i-th tuple element (an emit_ir node).
            _recv_w = self._expr_to_whyml(_mt_recv, local_refs)
            lines = [f"{indent}let {tmp_names[i]} = (irnth {i} (elts_of {_recv_w})) in"
                     for i in range(len(tmp_names))]
        else:
            pattern = ", ".join(tmp_names)
            lines = [f"{indent}let ({pattern}) = {val_whyml} in"]
        n_tu = len(tmp_names)
        i_tu = 0
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
        elif code.rstrip().endswith(" in"):
            # No `rest`: the follow-on block's last line is a `let … = ref … in`
            # with no body — a Why3 syntax error. This only arises when the unpack
            # is the LAST statement of its block AND its final target is a fresh
            # ref (e.g. the renamed 2nd+ discard `let py_underscore_k = ref …`).
            # Any such shape was previously an unemittable hard error, so a unit
            # `()` terminal here is byte-inert on the existing corpus.
            code += f"\n{indent}()"
        return code

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

    def _reject_param_collection_mutation(self, var_name: str, op_display: str):
        """wrong-lowering-to-fix.md §WL-05 — clean rejection of an in-place mutation
        of a dict/set PARAMETER (`d[k]=v`, `s.add(x)`, `s.discard(x)`, …).

        Python passes dicts/sets by reference, so the mutation must be VISIBLE to
        the caller. A faithful model needs proper aliasing/frame (a `writes {d}`
        effect on a mutable-map param) — the SAME hard problem for which RECORD-param
        mutation (static-ref ‡) and LIST inner mutation (nested-list-mutable) are
        documented OUT OF SCOPE. The by-value `map` param is not a `ref`, so emitting
        the ref-based write would produce internally-inconsistent WhyML. Raise a clear
        diagnostic instead (UB catalog `param-collection-mutation`), mirroring the
        record/list param-mutation boundary. Local collections and self-fields (which
        DO have a mutation frame) are never routed here."""
        from errors import PyCSLSemanticError
        raise PyCSLSemanticError(
            f"in-place mutation of dict/set parameter '{var_name}' (`{op_display}`) "
            f"is out of scope: Python mutates a dict/set argument BY REFERENCE, so the "
            f"write must be visible to the caller — a faithful model requires a "
            f"caller-visible mutation frame (`writes {{{var_name}}}`) that PyCSL's "
            f"by-value map parameter does not provide (the SAME boundary as record-param "
            f"and nested-list inner mutation). Rework the function to RETURN the updated "
            f"collection (`{var_name} = f({var_name})`), or mutate a LOCAL copy — a local "
            f"dict/set write-read-back is faithfully modelled and proves.",
            stage="module6-whyml",
            code="PYCSL-WHYML-PARAM-COLLECTION-MUT",
        )

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
                    # J2/J3 convergence: `registry[name] = {"bound": bound}` — the stored
                    # value is an INNER heterogeneous dict `map string (option hval)`; build
                    # it as the pyval-tagged `map_update_some` fold (native string keys,
                    # `_pyval_wrap` values), NOT the empty int base `val_expr` computed above.
                    _sv_ir = stmt.value.to_dict() if hasattr(stmt.value, "to_dict") else None
                    if (isinstance(nu, str) and nu.strip().endswith("(option hval)")
                            and isinstance(_sv_ir, dict) and _sv_ir.get("type") == "DictLit"):
                        v = self._build_pyval_inner_map(_sv_ir, local_refs)
                    else:
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

    def _handle_del_subscript_stmt(self, stmt: DelSubscriptStmt, rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        """wrong-lowering-to-fix.md §WL-05c (T7): lower `del d[k]` (a dict/set item
        deletion). The prior model was a blanket no-op (Module 5 flattened EVERY `del`
        to `Pass`), which was UNSOUND: after `del d[k]` a read/claim of the deleted key
        proved its OLD value (a severity-1 fail-OPEN, e.g. `del d["a"]` then
        `ensures d["a"] == 7`). Now:

          * a dict/set PARAMETER (`d` in `def m(self, d): del d[k]`) is REJECTED — the
            SAME caller-visible-mutation boundary as `d[k]=v` on a param (WL-05): the
            by-value `map` param carries no `writes {d}` frame, so the deletion cannot
            escape to the caller and must not be silently dropped.
          * a LOCAL dict/set is lowered FAITHFULLY to `map_update_none` (= `Map.set m k
            None`), so the key is cleared and a read-back is ABSENT (0). A false "old
            value survives the delete" claim now FAILS.
          * any other base (list `del a[i]`, a self-field, an unknown receiver) keeps the
            prior unmodelled no-op — strictly out of the dict/set item-delete scope, so
            byte-identical for every program that does not `del` a dict/set local/param.
        """
        arr = stmt.array.to_dict()
        code = f"{indent}()"
        if arr.get("type") == "Var":
            var_name = arr.get("name", "")
            is_local = var_name in getattr(self, "_dict_locals", set())
            is_param = (var_name in getattr(self, "_formal_params", [])
                        and var_name not in getattr(self, "_dict_locals", set()))
            st = getattr(self, "_current_symbol_table", {}) or {}
            is_coll = st.get(var_name) in ("dict", "set", "frozenset")
            if is_param and is_coll:
                # dict/set PARAM not promoted to a caller-visible ref (i.e. a METHOD
                # param): caller-visible deletion with no `writes {d}` frame → reject
                # (mirrors the `d[k]=v` / `s.discard(x)` param-mutation boundary). A
                # non-dict/set param (`del a[i]` on a list) is out of scope → no-op below.
                self._reject_param_collection_mutation(var_name, f"del {var_name}[...]")
            elif is_local:
                # LOCAL dict/set: faithful key clear via the existing `map_update_none`.
                index_expr = self._expr_to_whyml(stmt.index, local_refs)
                kappa = getattr(self, "_dict_key_types", {}).get(var_name)
                if kappa == "string":
                    k = index_expr
                elif (not self._in_spec
                      and self._is_string_expr(stmt.index.to_dict())):
                    self._add_abstract_op("val str_hash_op (s: string) : int")
                    k = f"(str_hash_op {index_expr})"
                else:
                    k = self._coerce_to_int(index_expr)
                _poly_none = (getattr(self, "_mutable_state_classes", None)
                              or kappa == "string")
                self._add_abstract_op(
                    ("val map_update_none (m: map 'k (option 'v)) (k: 'k) "
                     ": map 'k (option 'v)\n" if _poly_none else
                     "val map_update_none (m: map int (option int)) (k: int) "
                     ": map int (option int)\n")
                    + "    ensures { result = Map.set m k None }")
                safe = whyml_ident(var_name)
                code = f"{indent}{safe} := map_update_none !{safe} {k}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

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
        elif raw_op == "|" and target in getattr(self, "_str_set_locals", set()):
            # set-value-model-wall (self-tcb-reduction, Tier-5): `s |= t` where `s` is
            # an emitter-local `Set[str]` (`_str_set_locals`: annotated `Set[str]` AND
            # `= set()`-initialized) is the FAITHFUL set UNION over the executable
            # `set.SetApp[string]` clone — `s := StrSet.union !s <t>` — matching the
            # `StrSet.empty`/`StrSet.add`/`StrSet.mem` ops the same local already uses.
            # Without this arm the local fell through to the integer `bit_or` and the
            # emitted body type-errored (`StrSet.set` in an `int` slot) — the
            # `_handle_try_stmt` regression. `union` is a plain `SetApp` val (no new
            # axiom, ledger stays 3). Gated on `_str_set_locals`, which is empty for
            # every corpus function -> byte-identical.
            code = f"{indent}{safe_target} := (StrSet.union !{safe_target} {val})"
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
            if obj == "self" and self_type:
                self._add_abstract_op(f"val setattr_{self_type} (x: {self_type}) (f: int) (v: int) : unit")
                code = f"{indent}setattr_{self_type} {obj} {hash_field} {self._coerce_to_int(val)}"
            else:
                self._add_abstract_op("val setattr_3 (x: int) (f: int) (v: int) : unit")
                code = f"{indent}setattr_3 {self._coerce_to_int(obj)} {hash_field} {self._coerce_to_int(val)}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

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
        # self-tcb-reduction (_err-divergence): a bare-statement `self.<m>(...)` call to a
        # `-> NoReturn` callee never returns. `_handle_dotted_call` lowers it to
        # `(let _ = <call> in absurd)` (type `'a`). As a STATEMENT it must NOT be wrapped in
        # the usual `let _ = <expr> in ()` (that forces the result to `unit` and discards the
        # bottom-typing — the observed `type emit_ir but expected ()` at the trailing
        # `self._err(...)` of a `-> ExprIR` clause parser). Emit the self-terminating
        # `absurd` form as the tail VALUE so it unifies with the enclosing branch's type.
        # Any `rest` after it is genuinely dead (`absurd` discharges it); chain it unchanged.
        # Gated on the noreturn set → byte-identical for every module with no `-> NoReturn`.
        if val.get("type") == "Call":
            _nrf = val.get("func", "")
            if (_nrf.startswith("self.") and getattr(self, "_current_self_type", None)
                    and whyml_ident(
                        f"{self._current_self_type}__{_nrf[len('self.'):]}")
                    in getattr(self, "_module_method_noreturn", set())):
                expr_str = self._expr_to_whyml(stmt.value, local_refs)
                code = f"{indent}{expr_str}"
                if rest:
                    code += ";\n" + self._stmts_to_whyml(
                        rest, local_refs, declared_refs, indent, in_loop)
                return code
        if val.get("type") == "Call":
            func = val.get("func", "")
            if func.endswith(".append") and self._value_semantic:
                arr_name = func.rsplit(".", 1)[0].replace(".", "_")
                safe_arr = whyml_ident(arr_name)
                # stmt-list-append-mutation wall (C-bucket): appending a statement-IR node
                # `{"stmt": K, …}` to a caller-visible `ref (seq stmt_ir)` param grows the
                # seq on the ref ITSELF (`p := Seq.snoc !p <ctor>`), preserving the node
                # TAG via the stmt_ir constructor (SPass / SReturn …) — NOT the pre-feature
                # `_coerce_to_int` erasure to `0`. Keyed on the param being a stmt-seq-mut
                # param → corpus-inert.
                if arr_name in getattr(self, "_stmt_seq_mut_params", set()):
                    raw_arg = (val["args"][0].to_dict()
                               if hasattr(val["args"][0], "to_dict")
                               else val["args"][0])
                    # SUB-BODY recursion (C-bucket): the appended element is EITHER a
                    # `{"stmt": K}` dict LITERAL (`_py_stmt_pass/return/...` — lowered
                    # to its ctor by `_lower_stmt_ir_node`) OR a stmt_ir-VALUED
                    # expression, e.g. `self._process_while(stmt)` (the compound
                    # `_py_stmt_while/for/if` handlers) — a real `stmt_ir` value the
                    # dispatcher returns, lowered via `_expr_to_whyml`. Both snoc onto
                    # the ref itself.
                    if isinstance(raw_arg, dict) and raw_arg.get("type") == "DictLit":
                        node_arg = self._lower_stmt_ir_node(raw_arg, local_refs)
                    else:
                        node_arg = self._expr_to_whyml(val["args"][0], local_refs)
                    return f"{indent}{safe_arr} := Seq.snoc !{safe_arr} {node_arg}"
                if arr_name in getattr(self, "_pyval_seq_append_targets", set()):
                    # K1 (seq-pyval self-field append, self-tcb-reduction Tier-5, Bug 3
                    # fix): `self._field.append(x)` where `_field` is a `seq hval`
                    # self-field is a REAL faithful field write-back
                    # `self.<field> <- Seq.snoc self.<field> (<pyval-wrap x>)` — the
                    # fable-proven `getting-better/setenv_faithful.mlw` shape, axiom-free
                    # (`seq.Seq`/`snoc` intrinsic) — NOT the int-erased `Array.make 1024 0`
                    # shadow-local facade. `arr_name` is `self__field`; recover the field
                    # from the un-mangled call prefix (`self._field.append`). The appended
                    # value is tagged into its faithful `pyval` carrier by `_pyval_wrap`
                    # (a dict -> `PMap (map_update_some …)`, str-lit/var -> `PStr`, …).
                    # Gated on the `_pyval_seq_append_targets` set (populated only for a
                    # `List[Dict[str, PyVal]]`/`List[PyVal]` field) -> corpus byte-inert.
                    obj_field = func.rsplit(".", 1)[0]           # "self._field"
                    field = obj_field.split(".", 1)[1]           # "_field"
                    safe_field = self._field_label(
                        getattr(self, "_current_self_type", None), field)
                    raw_arg = (val["args"][0].to_dict()
                               if hasattr(val["args"][0], "to_dict")
                               else val["args"][0])
                    code = (f"{indent}self.{safe_field} <- "
                            f"Seq.snoc self.{safe_field} "
                            f"{self._pyval_wrap(raw_arg, local_refs)}")
                elif arr_name in getattr(self, "_pyval_seq_locals", set()):
                    # K4 (local/return-position seq-pyval, self-tcb-reduction Tier-5): a
                    # `List[Dict[str, PyVal]]`/`List[PyVal]` LOCAL that is appended to and
                    # RETURNED grows a real `seq hval` ref — `fields := Seq.snoc !fields
                    # (<pyval-wrap x>)` — tagging the appended dict/str/... into its
                    # faithful `pyval` carrier (the K1 self-field analogue for a local),
                    # NOT the int-erased `Seq.snoc !fields 0`. Gated on `_pyval_seq_locals`
                    # (populated only when the fn returns `seq hval`) -> byte-inert.
                    raw_arg = (val["args"][0].to_dict()
                               if hasattr(val["args"][0], "to_dict")
                               else val["args"][0])
                    code = (f"{indent}{safe_arr} := Seq.snoc !{safe_arr} "
                            f"{self._pyval_wrap(raw_arg, local_refs)}")
                else:
                    arg = self._expr_to_whyml(val["args"][0], local_refs)
                    arg = self._coerce_to_int(arg)
                    if arr_name in getattr(self, "_seq_locals", set()):
                        # return-arr.md follow-on: `.append()` on a seq-promoted local grows
                        # the immutable seq via Seq.snoc (so `len` = Seq.length tracks the
                        # logical length), instead of the array-local `arr[!len] <- v; len += 1`.
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
                # set-value-model-wall (self-tcb-reduction, Tier-5): a `.add`/`.discard`/
                # `.remove` on an emitter-local `Set[str]` value rebinds the ref over the
                # executable `set.SetApp[string]` clone — `s := StrSet.add x !s` /
                # `s := StrSet.remove x !s` — passing the RAW native string element
                # (matching the `StrSet.mem` membership read, NO `str_hash_op`/int-erase).
                # Gated on `_str_set_locals` -> corpus byte-inert.
                if obj_name in getattr(self, "_str_set_locals", set()):
                    safe_obj = whyml_ident(obj_name)
                    arg_ir = (val.get("args") or [{}])[0]
                    arg = self._expr_to_whyml(arg_ir, local_refs)
                    _sop = "add" if method == "add" else "remove"
                    code = f"{indent}{safe_obj} := StrSet.{_sop} {arg} !{safe_obj}"
                    if rest:
                        code += ";\n" + self._stmts_to_whyml(
                            rest, local_refs, declared_refs, indent, in_loop)
                    return code
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
        if isinstance(stmt, DelSubscriptStmt):
            return self._handle_del_subscript_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)
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
            pred = self._expr_to_whyml(stmt.test, local_refs)
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

    def _wrap_body_with_return_catch(self, body_code: str, return_type: str) -> str:
        """Wrap a function body with the `try ... with Return r -> r end`
        catch when early-returns can fire. Picks the right Return arm
        based on return type (unit / tuple_N / int). Array returns are
        intentionally not wrappable here — see `_handle_return_stmt` and
        the Class M auto-trust path."""
        arity = self._current_tuple_arity
        if return_type == "unit":
            return f"    try\n{body_code}\n    with Return_void -> () end"
        if return_type.startswith("option ("):
            # Optional-tuple return: catch the dedicated `Return_opttuple_<arity>`
            # exception, whose `option (τ...)` payload is handed straight back
            # (immutable — no materialize). Parallel to the `Return_<arity>` tuple arm.
            suffix = return_type[len("option "):].replace("(", "").replace(")", "").replace(" ", "").replace(",", "_")
            return f"    try\n{body_code}\n    with Return_opttuple_{suffix} r -> r end"
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
        if return_type == "emit_ir":
            # Return_emit_ir infra: an emit_ir-returning function (a recursive `_csl_*`-
            # style dispatcher building/returning a `{"type": K}` IR-node) with an
            # early/in-loop return raises `Return_emit_ir <emit_ir>`; the catch hands the
            # node payload straight back (immutable — no materialize needed), the same
            # shape as the Return_str arm just above.
            return f"    try\n{body_code}\n    with Return_emit_ir r -> r end"
        if return_type.startswith("_union_"):
            # value-model campaign incr5 (primitive c): a synthesized-union (`Optional[X]`)
            # return with an early/in-loop return is caught by its dedicated
            # `Return_<variant>` exception (declared in preamble.py; raised by
            # `_handle_return_stmt`). The payload is the already-injected variant value
            # (`Arm_N_0 <v>` / `Arm_N_None`), handed straight back — parallel to Return_str.
            return f"    try\n{body_code}\n    with Return_{return_type} r -> r end"
        return f"    try\n{body_code}\n    with Return r -> r end"

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

    def _collect_str_call_result_locals(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """no-more-int emitter L2/L3 (no-more-int-emitter-plan.md): a local whose
        first assignment is a `string`-VALUED expression must be a string-typed ref
        — never the integer `ref 0` pre-declaration — so the `s := <string>`
        typechecks. Two string-valued shapes are recognized:
          L2: a call to a `string`-returning function (return type from
              `_module_method_return_types`, keyed like `_handle_dotted_call`); and
          L3: an f-string whose every segment is string-typed (the same all-string
              condition `_handle_fstring_expr` uses to emit `str_concat_op`/`concat`).

        Resolved to a **fixpoint**: a later `code = f"{arr}[{idx}]"` becomes string
        only once its interpolated locals (`arr`, `idx`, bound from L2 calls) are
        themselves marked — so the symbol table is grown iteratively.

        Byte-identical for any local NOT bound from such an expression (the
        627-corpus does not consult one into a `ref 0` local via this path — an
        all-string f-string already lowers to a `string` value via b14 B2, and a
        corpus local receiving it would already be string-typed elsewhere)."""
        rt = getattr(self, "_module_method_return_types", {})
        st = getattr(self, "_current_symbol_table", None)

        def _ret_of(fn: str):
            if fn.startswith("self."):
                tail = fn[len("self."):]
                cls = getattr(self, "_current_self_type", None)
                key = f"{cls}__{tail}" if cls else tail
            else:
                key = fn
            return rt.get(key)

        out: Set[str] = set()   # accumulating string locals — consulted by `_is_str_val` (slice base)

        def _is_str_val(v: Any) -> bool:
            if not isinstance(v, dict):
                return False
            t = v.get("type")
            # G1 (09-2223 pure-classifier increment): a record `<var>.get("<str-field>")`
            # is a STRING value — its G1 lowering is the native field read
            # `<var>.<label> : string` — so the receiving local is a string ref
            # (`ref ""`), never the integer `ref 0`, and its `:=`/comparisons typecheck
            # and route through `str_eq_op`. Ungated (fires only on a record-typed
            # receiver via `_record_get_field`, never a plain dict) → corpus-byte-inert.
            _rgv = self._record_get_field(v)
            if _rgv is not None and _rgv[2] == "str":
                return True
            # option-of-record projection (boundary-1 G1 extension): a
            # `<optvar>.get("<str-field>")` on an `Optional[<record>]` receiver is a
            # STRING value (the Some arm projects `_r.<label> : string`), so the local
            # (`t = val_ir.get("type", "")`) is a string ref (`ref ""`). Gated on
            # `_option_record_get_field` → corpus-byte-inert.
            _orgv = self._option_record_get_field(v)
            if _orgv is not None and _orgv[2] == "str":
                return True
            # faithful-string-op.md §3: a local bound from `.replace`/`.lower`/`.upper`/
            # `.strip` or a `<string>.split(sep)[i]` element is a STRING local (pre-decl
            # `ref ""`), so its `:=` typechecks — outside @mutable_state too. Scoped to the
            # new ops (not the whole `_is_string_expr`) to stay byte-clean.
            if self._is_str_value_method(v):
                return True
            # an emit_ir str-attribute read (`var = node.var` -> name_of) is a string local, so a
            # dependent slice (`field = var[len("self."):]`) types as string. @mutable_state.
            if (t in ("Attribute", "FieldGet") and _ms_str and self._is_string_expr(v)):
                return True
            # a SLICE of a STRING (`var[len("self."):]` prefix strip) is a substring -> string.
            # A slice whose base is a GENUINELY string-typed value (a `str` param/symbol, e.g.
            # `_indent_width`'s `lead = body[:n]`) is a string local regardless of @mutable_state
            # — the slice lowers to `str_sub_op` (string), so `len(lead)` must route to
            # `str_length_op` and `"\t" in lead` to the string-contains path (else `len` wrongly
            # emits `Array.length` on a string). Keyed on `_is_string_expr(base)`, which is only
            # True for a declared-string base → corpus-byte-inert.
            if (t in ("Subscript", "SliceAccess")
                    and self._is_string_expr(v.get("value", {}))):
                return True
            # The base may instead be a string local recognized EARLIER in this same fixpoint
            # (`var = node.var`), so consult the accumulating `out` set too. @mutable_state.
            if (t in ("Subscript", "SliceAccess") and _ms_str
                    and isinstance(v.get("value"), dict)
                    and v["value"].get("type") == "Var"
                    and v["value"].get("name") in out):
                return True
            if (t in ("Subscript", "SliceAccess")
                    and self._split_call_recv_sep(v.get("value", {})) is not None):
                return True
            # item34.md CF5: `<seq/array string>[i]` element read (`var = sorted_assigned[i]`)
            # is a string local. @mutable_state.
            if (t in ("Subscript", "SliceAccess") and _ms_str
                    and isinstance(v.get("value"), dict)
                    and v["value"].get("type") == "Var"
                    and (getattr(self, "_seq_value_types", {}).get(v["value"].get("name")) == "string"
                         or getattr(self, "_array_elem_types", {}).get(v["value"].get("name")) == "string")):
                return True
            # item34.md CF5: `<str> or <str>` (`h.get("exc_type") or "PyCSL_Exception"`,
            # `"with" if … else "|"`) is a string local; a 1-arg `.get("k")` on a non-emit_ir
            # handler dict is string. @mutable_state.
            if (t == "BinOp" and v.get("op") == "or" and _ms_str
                    and self._is_string_expr(v.get("left", {}))
                    and self._is_string_expr(v.get("right", {}))):
                return True
            if _ms_str and self._is_string_expr(v):
                return True
            if t == "Call":
                if _ret_of(v.get("func", "")) == "string":
                    return True
            if t == "FString":
                parts = v.get("parts", [])
                if bool(parts) and all(self._is_string_expr(p) for p in parts):
                    return True
                # R3 (todict-reflection-plan.md): a @mutable_state class's MIXED str/int
                # f-string (a gensym) is string — `_handle_fstring_expr` converts its int
                # segments via `int_to_string`. So the receiving local types as string.
                if bool(parts) and (getattr(self, "_current_self_type", None)
                                    in getattr(self, "_mutable_state_classes", set())):
                    return True
            # R3 (todict-reflection-plan.md): in a @mutable_state class (the emitter
            # model), ANY string-typed value binds a string local — e.g. `obj =
            # stmt.object` (a `str` record field read), `s = other_str` (a str var).
            # Gated on @mutable_state → byte-identical for every other method.
            if (getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())
                    and self._is_string_expr(v)):
                return True
            # L18 S3 (ternary string-local): a ternary whose BOTH arms are string-valued
            # binds a string local (`ty = part.split(":")[-1].strip() if ":" in part else
            # "int"`) → pre-decl `ref ""`. An arm counts as string via `_is_str_val` (a
            # split-elem / str-method / fixpoint-dependency arm) OR `_is_string_expr` (a
            # string literal / genuine string expr). Fail-closed on BOTH arms being string
            # → a non-string ternary keeps its int/opaque typing (byte-inert). Ungated (a
            # non-@mutable_state method's both-string ternary — the 2177 case below requires
            # @mutable_state, so it does not cover this).
            if t == "IfExpr":
                _b18, _o18 = v.get("body", {}), v.get("orelse", {})
                if ((_is_str_val(_b18) or self._is_string_expr(_b18))
                        and (_is_str_val(_o18) or self._is_string_expr(_o18))):
                    return True
            # typed-ir-for-b-ceiling.md §18 (ghost_assign): a ternary `<str> if cond
            # else <str>` binds a string local — the emitter's `init_val = f"(…)"
            # if val == "Nil" else val`. Both arms must be string-valued; recurse via
            # `_is_str_val` (the fixpoint marks a dependency arm like `py_val` first).
            # @mutable_state-gated → byte-identical for every other method.
            if (t == "IfExpr"
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())):
                _b, _o = v.get("body", {}), v.get("orelse", {})
                _bs, _os = _is_str_val(_b), _is_str_val(_o)
                _bn = isinstance(_b, dict) and _b.get("type") == "None"
                _on = isinstance(_o, dict) and _o.get("type") == "None"
                # a string arm + a (string|None) arm → a string local (None → "").
                if (_bs or _os) and (_bs or _bn) and (_os or _on):
                    return True
            return False

        # Collect the FIRST assignment of each local (mirrors the ref-0 pre-decl,
        # which is keyed on the first bind); later re-assigns do not re-type.
        firsts: List[Tuple[str, Any]] = []
        seen: Set[str] = set()
        _ms_str = (getattr(self, "_current_self_type", None)
                   in getattr(self, "_mutable_state_classes", set()))

        tuple_str: Set[str] = set()
        # L18 S1c: (target, iter_ir) of every `for … in …` loop, evaluated in the fixpoint
        # below (a split iterable's receiver may only be typed `str` after an earlier pass).
        for_iters: List[Tuple[str, Any]] = []

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign" and isinstance(node.get("target"), str):
                    tgt = node["target"]
                    _v = node.get("value", {})
                    # i-feel-good.md I-B: skip a leading `x = None` (the `Optional[str] =
                    # None` init) so the first REAL assignment (`x = <str>`) classifies it.
                    # @mutable_state only → byte-identical elsewhere.
                    if tgt not in seen and not (
                            _ms_str and isinstance(_v, dict) and _v.get("type") == "None"):
                        seen.add(tgt)
                        firsts.append((tgt, _v))
                # item34.md CF4: a tuple-unpack target whose callee-return SLOT is `string`
                # (e.g. `len_expr, elem_expr, is_range = self._classify_iterable(...)` with
                # return `(string, string, int)`) is a string local — pre-decl `ref ""`.
                # @mutable_state-gated → corpus int-tuple unpacks unchanged.
                if (_ms_str and node.get("stmt") == "TupleUnpack"
                        and isinstance(node.get("value"), dict)
                        and node["value"].get("type") == "Call"):
                    _crt, _, _, _ = self._resolve_dotted_signature(
                        node["value"].get("func", ""))
                    if _crt and _crt.startswith("(") and _crt.endswith(")"):
                        _slots = [s.strip() for s in _crt[1:-1].split(",")]
                        for _i, _tg in enumerate(node.get("targets", [])):
                            if (_i < len(_slots) and _slots[_i] == "string"
                                    and _tg not in seen):
                                seen.add(_tg)
                                tuple_str.add(_tg)
                # LEVER F1 (string-triple-unpack): `a, _, b = <str>.rpartition(<sep>)` (and
                # `.partition`) — every one of the 3 targets is a `string` slice (the before /
                # separator / after projection). Pre-decl `ref ""` (not `ref 0`) so the later
                # `==`/f-string/`.get`-key reads route through `str_eq_op`/`str_concat_op`
                # (never `int_to_string`/int-hash). @mutable_state-gated → corpus inert.
                if (_ms_str and node.get("stmt") == "TupleUnpack"
                        and isinstance(node.get("value"), dict)
                        and node["value"].get("type") == "Call"
                        and isinstance(node["value"].get("func"), str)
                        and node["value"]["func"].rsplit(".", 1)[-1] in ("partition", "rpartition")
                        and "." in node["value"]["func"]
                        and len(node["value"].get("args", [])) == 1
                        and len(node.get("targets", [])) == 3):
                    for _tg in node.get("targets", []):
                        if _tg not in seen:
                            seen.add(_tg)
                            tuple_str.add(_tg)
                # cf6.md M1.6: a tuple-unpack from a TUPLE LOCAL (`_uvar, uinfo = union_info`) —
                # each target whose slot type is `string` is a string local. @mutable_state.
                if (_ms_str and node.get("stmt") == "TupleUnpack"
                        and isinstance(node.get("value"), dict)
                        and node["value"].get("type") == "Var"):
                    _slt = getattr(self, "_tuple_var_slot_types", {}).get(
                        node["value"].get("name"))
                    if _slt:
                        for _i, _tg in enumerate(node.get("targets", [])):
                            if (_i < len(_slt) and _slt[_i] == "string"
                                    and _tg not in seen):
                                seen.add(_tg)
                                tuple_str.add(_tg)
                # resync-campaign.md R2: a tuple-unpack from a TUPLE LITERAL (`_lhs, _cur =
                # f"{_fld} <-", _fld`) — each target whose element is string-typed is a string
                # local. @mutable_state.
                if (_ms_str and node.get("stmt") == "TupleUnpack"
                        and isinstance(node.get("value"), dict)
                        and node["value"].get("type") == "Tuple"):
                    _elts = node["value"].get("elts", [])
                    for _i, _tg in enumerate(node.get("targets", [])):
                        if (_i < len(_elts) and _tg not in seen
                                and self._is_string_expr(_elts[_i])):
                            seen.add(_tg)
                            tuple_str.add(_tg)
                # item34.md CF5: a for-loop target over a `string` name-collection (`for part
                # in raw_parts`, `for tag in candidates`, `for var in sorted_assigned`) is a
                # string local — so `part.strip()`/`whyml_ident(var)` type-check.
                if (_ms_str and node.get("stmt") == "For"
                        and isinstance(node.get("iter"), dict)
                        and node["iter"].get("type") == "Var"
                        and (getattr(self, "_array_elem_types", {}).get(
                                node["iter"].get("name")) == "string"
                             or getattr(self, "_seq_value_types", {}).get(
                                node["iter"].get("name")) == "string")
                        and isinstance(node.get("target"), str)
                        and node["target"] not in seen):
                    seen.add(node["target"])
                    tuple_str.add(node["target"])
                # L18 S1c: record every for-loop's (target, iterable) for the fixpoint.
                if (node.get("stmt") == "For"
                        and isinstance(node.get("iter"), dict)
                        and isinstance(node.get("target"), str)):
                    for_iters.append((node["target"], node["iter"]))
                for x in node.values():
                    rec(x)
            elif isinstance(node, list):
                for x in node:
                    rec(x)

        rec(body_stmts)

        # item34.md CF5: seed the for-target / tuple-slot string locals into the symbol table
        # BEFORE the fixpoint, so a dependent classification (`base = part.strip()`, `part` a
        # string for-target) sees `part : str` and marks `base` string too.
        if st is not None:
            for _tg in tuple_str:
                if st.get(_tg) in (None, "Any"):
                    st[_tg] = "str"

        changed = True
        while changed:
            changed = False
            for tgt, v in firsts:
                if tgt in out:
                    continue
                if _is_str_val(v):
                    out.add(tgt)
                    # grow the symbol table so a dependent f-string sees `tgt : str`
                    if st is not None and st.get(tgt) in (None, "Any"):
                        st[tgt] = "str"
                    changed = True
            # L18 S1c: a for-target over a `<string>.split(sep)`/`.rsplit` iterable is a
            # string local (split yields string ELEMENTS) — so a dependent classification
            # (`ty = part.split(":")[-1].strip() if … else "int"`) sees `part : str`. Run in
            # the fixpoint because the split RECEIVER may only become `str`-typed (seeded
            # into `st`) on an earlier pass. Fail-closed on `_split_call_recv_sep` → inert.
            for _ftg, _fit in for_iters:
                if _ftg in out or _ftg in seen:
                    continue
                if self._split_call_recv_sep(_fit) is not None:
                    out.add(_ftg)
                    seen.add(_ftg)
                    if st is not None and st.get(_ftg) in (None, "Any"):
                        st[_ftg] = "str"
                    changed = True
        for _tg in tuple_str:
            out.add(_tg)
            if st is not None and st.get(_tg) in (None, "Any"):
                st[_tg] = "str"
        return out

    def _mark_string_seq_locals(self, body_stmts: List[Dict[str, Any]]) -> None:
        """L18 S1c-join: for each Module5 seq-promoted local (`_seq_locals`) whose EVERY
        element source is string-valued, record `_seq_value_types[v] = "string"` so a
        `sep.join(v)` recognizes it as a `seq string` (`str_join_seq`) rather than the
        opaque int `join_1`. Element sources = a `.append(x)` arg, or a `v = [e0, e1, …]`
        literal init's elements, or a non-literal `v = <expr>` reassignment. Fail-closed:
        at least one source, and ALL string-valued (via `_is_string_expr`, a string-valued
        Call return, or a `<str-dict>[k]` read of a local all-string-literal-valued dict).
        Byte-inert: a corpus seq built from non-string sources is untouched (stays int)."""
        seqs = getattr(self, "_seq_locals", set())
        if not seqs:
            return
        svt = self._seq_value_types
        ann = getattr(self, "_module_method_return_annotations", {})
        rt = getattr(self, "_module_method_return_types", {})
        # local dict vars bound to a DictLit whose VALUES are all string literals
        # (`scalars = {"int":"int",…}`) → a `<dict>[k]` read is a string.
        str_dicts: Set[str] = set()

        def _scan_dicts(n: Any) -> None:
            if isinstance(n, dict):
                if n.get("stmt") == "Assign" and isinstance(n.get("target"), str):
                    _v = n.get("value", {})
                    if isinstance(_v, dict) and _v.get("type") == "DictLit":
                        _vals = _v.get("values", []) or []
                        if _vals and all(isinstance(x, dict) and x.get("type") == "String"
                                         for x in _vals):
                            str_dicts.add(n["target"])
                for x in n.values():
                    _scan_dicts(x)
            elif isinstance(n, list):
                for x in n:
                    _scan_dicts(x)
        _scan_dicts(body_stmts)

        def _src_is_str(src: Any) -> bool:
            if not isinstance(src, dict):
                return False
            if self._is_string_expr(src):
                return True
            if src.get("type") == "Call":
                _fn = src.get("func", "")
                if ann.get(_fn) == "str" or rt.get(_fn) == "string":
                    return True
            if src.get("type") in ("Subscript", "SliceAccess"):
                _b = src.get("value", {})
                if (isinstance(_b, dict) and _b.get("type") == "Var"
                        and _b.get("name") in str_dicts):
                    return True
            return False

        srcs: Dict[str, List[Any]] = {v: [] for v in seqs}

        def _scan_srcs(n: Any) -> None:
            if isinstance(n, dict):
                if n.get("stmt") == "Expr":
                    _c = n.get("value", {})
                    if (isinstance(_c, dict) and _c.get("type") == "Call"
                            and isinstance(_c.get("func"), str)
                            and _c["func"].endswith(".append")):
                        _tv = _c["func"][:-len(".append")]
                        if _tv in srcs:
                            _args = _c.get("args") or []
                            srcs[_tv].append(_args[0] if _args else {})
                if (n.get("stmt") == "Assign" and isinstance(n.get("target"), str)
                        and n["target"] in srcs):
                    _v = n.get("value", {})
                    if isinstance(_v, dict) and _v.get("type") in ("ArrayLit", "ListLit"):
                        for e in _v.get("elts", []) or []:
                            srcs[n["target"]].append(e)
                    elif isinstance(_v, dict):
                        srcs[n["target"]].append(_v)
                for x in n.values():
                    _scan_srcs(x)
            elif isinstance(n, list):
                for x in n:
                    _scan_srcs(x)
        _scan_srcs(body_stmts)

        for _v, _elems in srcs.items():
            if svt.get(_v):
                continue
            if _elems and all(_src_is_str(e) for e in _elems):
                svt[_v] = "string"

    def _collect_keyword_str_locals(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """J2/J3 convergence (Call-internals): locals whose value is a keyword string read
        (`<kw>.value.id` / `<kw>.value.attr` where `<kw>` iterates `.keywords`) or the call
        callee id (`<call>.func.id`). They are `string` locals. Empty for every corpus
        program -> byte-inert."""
        kw_loop_vars: Set[str] = set()

        def find_kw_loops(n: Any) -> None:
            if isinstance(n, dict):
                if n.get("stmt") in ("For", "ForStmt"):
                    _it = n.get("iter", {})
                    if (isinstance(_it, dict) and _it.get("type") == "Attribute"
                            and _it.get("attr") == "keywords"
                            and isinstance(n.get("target"), str)):
                        kw_loop_vars.add(n["target"])
                for x in n.values():
                    find_kw_loops(x)
            elif isinstance(n, list):
                for x in n:
                    find_kw_loops(x)
        find_kw_loops(body_stmts)
        emit_ir_vars = getattr(self, "_emit_ir_local_vars", set())

        def _is_kw_str_read(v: Any) -> bool:
            if not (isinstance(v, dict) and v.get("type") == "Attribute"):
                return False
            _a = v.get("attr")
            _o = v.get("object", {})
            # <kw>.value.id / <kw>.value.attr
            if (_a in ("id", "attr") and isinstance(_o, dict)
                    and _o.get("type") == "Attribute" and _o.get("attr") == "value"
                    and isinstance(_o.get("object"), dict)
                    and _o["object"].get("type") == "Var"
                    and _o["object"].get("name") in kw_loop_vars):
                return True
            # <call>.func.id
            if (_a == "id" and isinstance(_o, dict) and _o.get("type") == "Attribute"
                    and _o.get("attr") == "func"
                    and isinstance(_o.get("object"), dict)
                    and _o["object"].get("type") == "Var"
                    and _o["object"].get("name") in emit_ir_vars):
                return True
            return False

        out: Set[str] = set()

        def find_assigns(n: Any) -> None:
            if isinstance(n, dict):
                if (n.get("stmt") == "Assign" and isinstance(n.get("target"), str)
                        and _is_kw_str_read(n.get("value"))):
                    out.add(n["target"])
                for x in n.values():
                    find_assigns(x)
            elif isinstance(n, list):
                for x in n:
                    find_assigns(x)
        find_assigns(body_stmts)
        return out - set(self._formal_params)

    def _collect_tparam_str_locals(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """L1 tparam reflection-node ADT: locals whose value is a tparam string read —
        `type(<tp>).__name__` (`tp_kind_of`), `<tp>.name` (`tp_name`), or `<bnode>.id`/
        `<bnode>.attr` where `<bnode> = <tp>.bound` is the emit_ir bound sub-node
        (`name_of`). They are `string` locals (pre-declared `ref ""`, not `ref 0`). Empty
        for every corpus program -> byte-inert."""
        tp_loop_vars = self._tparam_body_loop_vars(body_stmts)
        if not tp_loop_vars:
            return set()

        def _tp_getattr_field(v: Any):
            """7a: `getattr(<tp>, "name"|"bound", …)` over a tparam loop var → the field
            name; else None. The Call form the live `_collect_type_params` uses."""
            if not (isinstance(v, dict) and v.get("type") == "Call"
                    and v.get("func") == "getattr"):
                return None
            _a = v.get("args") or []
            if (len(_a) >= 2 and isinstance(_a[0], dict) and _a[0].get("type") == "Var"
                    and _a[0].get("name") in tp_loop_vars
                    and isinstance(_a[1], dict) and _a[1].get("type") == "String"):
                return _a[1].get("value")
            return None

        # the bound sub-node locals: `<bnode> = <tp>.bound`
        bound_vars: Set[str] = set()

        def find_bounds(n: Any) -> None:
            if isinstance(n, dict):
                if n.get("stmt") == "Assign" and isinstance(n.get("target"), str):
                    _v = n.get("value", {})
                    if (isinstance(_v, dict) and _v.get("type") == "Attribute"
                            and _v.get("attr") == "bound"
                            and isinstance(_v.get("object"), dict)
                            and _v["object"].get("type") == "Var"
                            and _v["object"].get("name") in tp_loop_vars):
                        bound_vars.add(n["target"])
                    # 7a: `bnode = getattr(tp, "bound", None)` (the live Call form).
                    elif _tp_getattr_field(_v) == "bound":
                        bound_vars.add(n["target"])
                for x in n.values():
                    find_bounds(x)
            elif isinstance(n, list):
                for x in n:
                    find_bounds(x)
        find_bounds(body_stmts)

        def _is_tp_str_read(v: Any) -> bool:
            # 7a: `getattr(tp, "name", None)` (the live Call form) is a string read.
            if _tp_getattr_field(v) == "name":
                return True
            if not (isinstance(v, dict) and v.get("type") == "Attribute"):
                return False
            _a = v.get("attr")
            _o = v.get("object", {})
            # type(<tp>).__name__
            if (_a == "__name__" and isinstance(_o, dict) and _o.get("type") == "Call"
                    and _o.get("func") == "type"):
                _ca = _o.get("args") or []
                if (len(_ca) == 1 and isinstance(_ca[0], dict)
                        and _ca[0].get("type") == "Var"
                        and _ca[0].get("name") in tp_loop_vars):
                    return True
            # <tp>.name
            if (_a == "name" and isinstance(_o, dict) and _o.get("type") == "Var"
                    and _o.get("name") in tp_loop_vars):
                return True
            # <bnode>.id / <bnode>.attr  (bnode = tp.bound, an emit_ir sub-node)
            if (_a in ("id", "attr") and isinstance(_o, dict)
                    and _o.get("type") == "Var" and _o.get("name") in bound_vars):
                return True
            return False

        out: Set[str] = set()

        def find_assigns(n: Any) -> None:
            if isinstance(n, dict):
                if (n.get("stmt") == "Assign" and isinstance(n.get("target"), str)
                        and _is_tp_str_read(n.get("value"))):
                    out.add(n["target"])
                for x in n.values():
                    find_assigns(x)
            elif isinstance(n, list):
                for x in n:
                    find_assigns(x)
        find_assigns(body_stmts)
        return out - set(self._formal_params)

    def _pyast_body_loop_vars(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """J2/J3 convergence: the loop-target vars of a `for <x> in <p>.body` where `<p>`
        is a `py_classdef_node`/`py_module_node` param (the class-/module-body giants). At
        the pre-scan stage `_pyast_stmt_locals` is not yet populated, so this recovers them
        directly from the For loops over an ast-node param body. Empty for every corpus
        program -> byte-inert."""
        _params = (getattr(self, "_current_pyast_classdef_params", set())
                   | getattr(self, "_current_pyast_module_params", set()))
        if not _params:
            return set()
        found: Set[str] = set()

        def rec(n: Any) -> None:
            if isinstance(n, dict):
                if n.get("stmt") in ("For", "ForStmt"):
                    _it = n.get("iter", {})
                    if (isinstance(_it, dict) and _it.get("type") == "Attribute"
                            and _it.get("attr") == "body"):
                        _o = _it.get("object", {})
                        if (isinstance(_o, dict) and _o.get("type") == "Var"
                                and _o.get("name") in _params
                                and isinstance(n.get("target"), str)):
                            found.add(n["target"])
                for x in n.values():
                    rec(x)
            elif isinstance(n, list):
                for x in n:
                    rec(x)
        rec(body_stmts)
        return found

    def _tparam_body_loop_vars(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """L1 tparam reflection-node ADT: the loop-target vars of a `for <tp> in
        <node>.type_params` where `<node>` is a `py_tparam_node` param. Used only to keep
        the emit_ir-local collector running for the tparam giants (so `bnode = tp.bound` is
        typed emit_ir). Empty for every corpus program -> byte-inert."""
        _params = getattr(self, "_current_tparam_node_params", set())
        if not _params:
            return set()
        found: Set[str] = set()

        _aliases = getattr(self, "_tparam_list_aliases", {})

        def rec(n: Any) -> None:
            if isinstance(n, dict):
                if n.get("stmt") in ("For", "ForStmt"):
                    _it = n.get("iter", {})
                    if (isinstance(_it, dict) and _it.get("type") == "Attribute"
                            and _it.get("attr") == "type_params"):
                        _o = _it.get("object", {})
                        if (isinstance(_o, dict) and _o.get("type") == "Var"
                                and _o.get("name") in _params
                                and isinstance(n.get("target"), str)):
                            found.add(n["target"])
                    # 7a: `for tp in <tparams>` where <tparams> is a getattr-or-default
                    # tparam_list alias local (the live indirection).
                    elif (isinstance(_it, dict) and _it.get("type") == "Var"
                            and _it.get("name") in _aliases
                            and isinstance(n.get("target"), str)):
                        found.add(n["target"])
                for x in n.values():
                    rec(x)
            elif isinstance(n, list):
                for x in n:
                    rec(x)
        rec(body_stmts)
        return found

    def _collect_record_field_elem_locals(
            self, body_stmts: List[Dict[str, Any]]) -> Dict[str, str]:
        """W8/W1: map local name -> element RECORD name for every local whose FIRST
        assignment reads an element of an `array <record>` self-field
        (`t = self.toks[self.i]`). Such a local is record-typed, so it must be
        pre-declared with the element record's default literal rather than `ref 0`.
        `_record_array_fields` (field -> record) is populated by `_emit_type_decls`
        only for a `List[<record>]` record field, so this returns {} everywhere else."""
        raf = getattr(self, "_record_array_fields", None) or {}
        out: Dict[str, str] = {}
        seen: Set[str] = set()

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign" and isinstance(node.get("target"), str):
                    tgt = node["target"]
                    val = node.get("value", {})
                    if tgt not in seen:
                        seen.add(tgt)
                        if isinstance(val, dict) and val.get("type") == "Subscript":
                            base = val.get("value", {})
                            if isinstance(base, dict) and base.get("type") == "FieldGet":
                                obj = base.get("object")
                                if isinstance(obj, dict):
                                    obj = obj.get("name")
                                fld = base.get("field")
                                if obj == "self" and fld in raf:
                                    out[tgt] = raf[fld]
                        # W8 capability (vi): a local bound to a SAME-CLASS sibling
                        # call with a RECORD return (`t = self.cur()`, the opening
                        # line of every parser predicate) is record-typed too — the
                        # call lowers to the concrete `(<class>__cur self)`, so the
                        # integer `ref 0` pre-decl mistypes it and the projection
                        # `t.py_type` falls back to the opaque `(get_py_type !t)`.
                        elif (isinstance(val, dict) and val.get("type") == "Call"
                                and isinstance(val.get("func"), str)
                                and val["func"].startswith("self.")):
                            _crt = self._resolve_dotted_signature(val["func"])[0]
                            for _rc, _ri in getattr(
                                    self, "_record_types", {}).items():
                                if _ri.get("whyml_name") == _crt:
                                    out[tgt] = _rc
                                    break
                for v in node.values():
                    rec(v)
            elif isinstance(node, list):
                for v in node:
                    rec(v)

        rec(body_stmts)
        return out

    def _collect_emit_ir_result_locals(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """typed-ir-for-b-ceiling.md §19: locals whose FIRST assignment is an `emit_ir`
        value — an ExprIR field read (`assume_inv = stmt.assume_invariant`), an inline
        `{"type": K}` construction, a `d = node.to_dict()` alias, or another emit_ir
        local. They are pre-declared `ref (IrOther "")` (the emit_ir counterpart of the
        R3 `ref ""` string pre-decl), not the integer `ref 0`. @mutable_state only."""
        # J2/J3 convergence (call/target emit_ir bridge): the targets of a
        # `for <x> in <module/classdef param>.body` loop are pyast_stmt-typed; a
        # `call = <x>.value` / `target = <x>.targets[0]` read then projects a REAL
        # emit_ir (stmt_value / stmt_target0), so `call`/`target` are emit_ir locals
        # (pre-declared `ref (IrOther "")`, not `ref 0`). This pre-scan runs BEFORE
        # `_pyast_stmt_locals` is populated during loop emission, so it computes the
        # body-loop vars directly. Corpus-inert (no corpus program iterates an ast-node
        # param body). Recognized even outside @mutable_state (the class-body/module-body
        # giants are not mutable-state classes).
        _body_loop_vars = self._pyast_body_loop_vars(body_stmts)
        # L1 tparam: keep the collector running for the tparam giants too (so `bnode =
        # tp.bound` is typed emit_ir via `_is_emit_ir_expr(tp.bound)`).
        _tparam_loop_vars = self._tparam_body_loop_vars(body_stmts)
        if (not _body_loop_vars and not _tparam_loop_vars
                and getattr(self, "_current_self_type", None)
                not in getattr(self, "_mutable_state_classes", set())):
            return set()
        st = getattr(self, "_current_symbol_table", None)
        firsts: List[Tuple[str, Any]] = []
        seen: Set[str] = set()

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign" and isinstance(node.get("target"), str):
                    tgt = node["target"]
                    _v = node.get("value", {})
                    # self-ir-schema.md IR2: skip a leading `x = None` (the `Optional[emit_ir]
                    # = None` init, e.g. `tail_ret = None; tail_ret = body_stmts[-1]`) so the
                    # first REAL assignment classifies it — mirrors the string I-B skip.
                    if tgt not in seen and not (
                            isinstance(_v, dict) and _v.get("type") == "None"):
                        seen.add(tgt)
                        firsts.append((tgt, _v))
                # cf6.md M1.6: a tuple-unpack from a TUPLE LOCAL (`_uvar, uinfo = union_info`) —
                # each target whose slot type is `emit_ir` is an emit_ir local.
                if (node.get("stmt") == "TupleUnpack"
                        and isinstance(node.get("value"), dict)
                        and node["value"].get("type") == "Var"):
                    _slt = getattr(self, "_tuple_var_slot_types", {}).get(
                        node["value"].get("name"))
                    if _slt:
                        for _i, _tg in enumerate(node.get("targets", [])):
                            if _i < len(_slt) and _slt[_i] == "emit_ir":
                                tuple_emit.add(_tg)
                # tuple-return-of-emit_ir: `a, b = self.m(…)` (a DIRECT call unpack, no intermediate
                # tuple local) where `m`'s return type has an `emit_ir` slot — each such target is an
                # emit_ir local (mirrors the `string`-slot handling in _collect_string_result_locals).
                if (node.get("stmt") == "TupleUnpack"
                        and isinstance(node.get("value"), dict)
                        and node["value"].get("type") == "Call"):
                    _crt, _, _, _ = self._resolve_dotted_signature(
                        node["value"].get("func", ""))
                    if isinstance(_crt, str) and _crt.startswith("(") and _crt.endswith(")"):
                        _slots = [c.strip() for c in _crt[1:-1].split(",")]
                        for _i, _tg in enumerate(node.get("targets", [])):
                            if _i < len(_slots) and _slots[_i] == "emit_ir":
                                tuple_emit.add(_tg)
                # value-model campaign incr7 (primitive #2): a tuple-unpack from a TYPED
                # `<emit_ir>.elts` read (`_ki, vi = v.slice.elts` in a dict walker) — each target
                # is an IrMkTupleN element (`irnth i (elts_of recv)`), so it is an emit_ir local.
                if (node.get("stmt") == "TupleUnpack"
                        and self._mktuple_elts_recv_ir(node.get("value")) is not None):
                    for _tg in node.get("targets", []):
                        tuple_emit.add(_tg)
                for x in node.values():
                    rec(x)
            elif isinstance(node, list):
                for x in node:
                    rec(x)
        tuple_emit: Set[str] = set()
        rec(body_stmts)

        def _is_emit_ir_val(v: Any, known: Set[str]) -> bool:
            if not isinstance(v, dict):
                return False
            if self._is_emit_ir_expr(v):
                return True
            # J2/J3 bridge: `<bodyvar>.value` / `.target` / `.annotation` (Attribute) and
            # `<bodyvar>.targets[0]` (Subscript) project an emit_ir off a pyast_stmt body-
            # loop var — the exact `call = stmt.value` / `target = stmt.targets[0]` shape.
            if v.get("type") == "Attribute" and v.get("attr") in ("value", "target",
                                                                   "annotation"):
                _o = v.get("object", {})
                if (isinstance(_o, dict) and _o.get("type") == "Var"
                        and _o.get("name") in _body_loop_vars):
                    return True
            # L1 tparam bridge: `tp.bound` over a pre-scanned tparam loop var projects an
            # emit_ir sub-node (`tp_bound`), so `bnode = tp.bound` is an emit_ir local. At
            # pre-scan `_tparam_locals` is not yet populated, so use `_tparam_loop_vars`.
            if v.get("type") == "Attribute" and v.get("attr") == "bound":
                _o = v.get("object", {})
                if (isinstance(_o, dict) and _o.get("type") == "Var"
                        and _o.get("name") in _tparam_loop_vars):
                    return True
            # 7a: `bnode = getattr(tp, "bound", None)` (the live Call form) projects the
            # emit_ir bound sub-node just like `tp.bound`.
            if (v.get("type") == "Call" and v.get("func") == "getattr"):
                _ga = v.get("args") or []
                if (len(_ga) >= 2 and isinstance(_ga[0], dict)
                        and _ga[0].get("type") == "Var"
                        and _ga[0].get("name") in _tparam_loop_vars
                        and isinstance(_ga[1], dict) and _ga[1].get("type") == "String"
                        and _ga[1].get("value") == "bound"):
                    return True
            if v.get("type") in ("Subscript", "SliceAccess"):
                _val = v.get("value", {})
                _idx = v.get("index")
                if (isinstance(_val, dict) and _val.get("type") == "Attribute"
                        and _val.get("attr") == "targets"
                        and isinstance(_idx, dict) and _idx.get("type") == "Number"
                        and _idx.get("value") in (0, 0.0)):
                    _o = _val.get("object", {})
                    if (isinstance(_o, dict) and _o.get("type") == "Var"
                            and _o.get("name") in _body_loop_vars):
                        return True
            if v.get("type") == "Var" and v.get("name") in known:
                return True
            _fn = v.get("func")
            if (v.get("type") == "Call" and isinstance(_fn, str)
                    and _fn.endswith(".to_dict") and not v.get("args")):
                return True
            # isinstance-on-emit_ir batch (self-tcb-reduction M5): a CALL whose
            # resolved return type is the `emit_ir` sum — e.g.
            # `obj_ir = self._py_expr_to_ir(expr.value)`, the recursive expr-lowering
            # dispatcher — is an emit_ir local (pre-declared `ref (IrOther "")`). The
            # census-flagged general gap (ir_resolve.py): the collector previously only
            # recognized `.to_dict()`/field-read/Var/IfExpr emit_ir shapes, never a
            # generic emit_ir-returning method call. @mutable_state-gated (this whole
            # collector no-ops off the mutable-state classes), so corpus-inert.
            if v.get("type") == "Call" and isinstance(_fn, str):
                _crt, _, _, _ = self._resolve_dotted_signature(_fn)
                if _crt == "emit_ir":
                    return True
            # item34.md CF1: an `Optional[emit_ir]` ternary (`stmt.value.to_dict() if … else
            # None`) is an emit_ir local — one arm emit_ir, the other emit_ir/None.
            if v.get("type") == "IfExpr":
                _b, _o = v.get("body", {}), v.get("orelse", {})
                _bir = _is_emit_ir_val(_b, known) or self._is_emit_ir_expr(_b)
                _oir = _is_emit_ir_val(_o, known) or self._is_emit_ir_expr(_o)
                _bn = isinstance(_b, dict) and _b.get("type") == "None"
                _on = isinstance(_o, dict) and _o.get("type") == "None"
                if (_bir or _oir) and (_bir or _bn) and (_oir or _on):
                    return True
            return False

        out: Set[str] = set()
        changed = True
        while changed:
            changed = False
            for tgt, v in firsts:
                if tgt in out:
                    continue
                # J2/J3 convergence: an Optional-union local (`value: Optional[ast.expr]
                # = None` in `_collect_class_constants`) already lives as its synthesized
                # `_union_*` ref — never reclassify it emit_ir (the body-loop-var bridge
                # would otherwise clash a `_union_..._1` value against `emit_ir`).
                _tt = st.get(tgt) if st is not None else None
                if isinstance(_tt, str) and _tt.startswith("_union_"):
                    continue
                if _is_emit_ir_val(v, out):
                    out.add(tgt)
                    if st is not None and st.get(tgt) in (None, "Any"):
                        st[tgt] = "ExprIR"   # so reflection on the local sees emit_ir
                    changed = True
        # cf6.md M1.6: emit_ir targets of a tuple-local unpack (`uinfo`).
        for _tg in tuple_emit:
            out.add(_tg)
            if st is not None and st.get(_tg) in (None, "Any"):
                st[_tg] = "ExprIR"
        return out

    def _collect_pyval_read_locals(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """pyval-value-model-wall (self-tcb-reduction, Tier-5): locals whose first
        assignment is a subscript READ of a `Dict[str, PyVal]` (pyval-valued) dict —
        `v = d[k]`. The read lowers to `Map.get` projecting an `option hval` (arm
        projection to an `hval`), so `v` must be an `hval`-typed ref, let-bound at its
        first assignment — never the integer `ref 0` pre-declaration (which would fail
        L3 typecheck: `hval` vs `int`). Marks them "hval" in the symbol table and
        returns the set (unioned into `_typed_local_vars`). Byte-inert: only a
        `Dict[str, PyVal]`-annotated dict (absent from the corpus) feeds this."""
        dvt = getattr(self, "_dict_value_types", {}) or {}
        if "hval" not in dvt.values():
            return set()
        out: Set[str] = set()

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign" and isinstance(node.get("target"), str):
                    v = node.get("value", {})
                    if isinstance(v, dict) and v.get("type") == "Subscript":
                        base = v.get("value", {})
                        if (isinstance(base, dict) and base.get("type") == "Var"
                                and dvt.get(base.get("name")) == "hval"):
                            out.add(node["target"])
                for x in node.values():
                    rec(x)
            elif isinstance(node, list):
                for x in node:
                    rec(x)

        rec(body_stmts)
        st = getattr(self, "_current_symbol_table", None)
        if st is not None:
            for v in out:
                if st.get(v) in (None, "Any"):
                    st[v] = "hval"
        return out

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
        # list-comprehension-lowering.md L2/L6: element type of an array local (string /
        # emit_ir / int) — computed BEFORE the string-local collectors so `pattern = ",
        # ".join(xs)` and `xs[i]` are seen as string when their array carries strings.
        # cf6.md M2: a 2-pass fixpoint for the mutual dependency between array-element types and
        # emit_ir locals — (1) classify array elements (`cases` → emit_ir from its field
        # value_type), (2) classify emit_ir locals (now `c = cases[i]` / `pat = c["pattern"]`
        # are structurally emit_ir, so `pat` is tagged), (3) re-classify array elements (now
        # `existing_caps = pat.get("captures")` sees `pat` as emit_ir). Regression-safe: the
        # emit_ir surface is `cases`-field- and @mutable_state-gated, so no corpus/non-match
        # local reclassifies (pass 2 is a no-op there and pass 3 == pass 1).
        self._array_elem_types = self._collect_array_elem_types(body_stmts)
        self._emit_ir_local_vars = self._collect_emit_ir_result_locals(body_stmts)
        self._array_elem_types = self._collect_array_elem_types(body_stmts)
        # seq-model-pivot.md SQ1: a REASSIGNED list-elem local (assigned >1×) is modeled as
        # an immutable `seq` (freely reassignable), not a mutable `array` — a `ref (array _)`
        # cannot be reassigned to a slice (Why3 region alias). Promote it to `_seq_locals`
        # with its element value type; drop it from the array-elem map. @mutable_state.
        if getattr(self, "_mutable_state_classes", None) and self._array_elem_types:
            _acounts: Dict[str, int] = {}

            _firstv: Dict[str, Any] = {}

            def _acnt(n: Any) -> None:
                if isinstance(n, dict):
                    # item34.md CF5: an AugAssign (`try_assigned |= …`) IS a reassignment (it
                    # lowers to `x := <fresh>`, illegal for a `ref (array _)`), so count it.
                    if (n.get("stmt") in ("Assign", "AugAssign")
                            and isinstance(n.get("target"), str)):
                        _acounts[n["target"]] = _acounts.get(n["target"], 0) + 1
                        if n.get("stmt") == "Assign" and n["target"] not in _firstv:
                            _firstv[n["target"]] = n.get("value", {})
                    for _x in n.values():
                        _acnt(_x)
                elif isinstance(n, list):
                    for _x in n:
                        _acnt(_x)
            _acnt(body_stmts)

            def _is_seq_src(v: Any) -> bool:
                # item34.md CF5: the value is a `seq string` name-collection SOURCE — so its
                # var is seq (`sorted`/`split`/`find_`/`collect_`/`[a]+[comp]`/`set(coll)` or a
                # ternary of such). Even a single-assign such var (`raw_parts`/`candidates`/
                # `sorted_assigned`) is seq-valued → iterates/reassigns via Seq.
                if not isinstance(v, dict):
                    return False
                _t, _f = v.get("type"), v.get("func")
                # #15: `self._nested_seq_field.get(k)` yields the inner `seq _` (`Dict[str,List[T]]`),
                # and a bare list comprehension lowers to `seq` — both make the local seq-valued.
                if _t == "ListComp":
                    return True
                if (_t == "Call" and isinstance(_f, str) and _f.endswith(".get")
                        and _f[:-len(".get")].startswith("self.")):
                    _nu = self._self_field_dict_nu(_f[:-len(".get")])
                    if isinstance(_nu, str) and _nu.startswith("seq "):
                        return True
                if _t == "Call" and isinstance(_f, str):
                    if (_f.startswith("IRScanner.find_") or _f.startswith("IRScanner.collect_")
                            or _f.endswith(".split") or _f == "sorted"):
                        return True
                    # 7b (self-tcb-reduction L4b): a `self.<m>(...)` whose declared return
                    # resolves to `array string`/`seq string` (e.g. `names =
                    # self._extract_generic_arg_names(b.slice)`) yields a seq-string local —
                    # so its declaration (`ref (seq string)`) and its `for nm in names`
                    # iteration are uniformly seq (not a `ref 0` int + array-op mismatch).
                    if self._call_returns_string_collection(_f):
                        return True
                    if _f in ("set", "frozenset", "list") and v.get("args"):
                        return _is_seq_src(v["args"][0])
                if (_t == "BinOp" and v.get("op") == "+"
                        and isinstance(v.get("left"), dict)
                        and v["left"].get("type") in ("ArrayLit", "ListLit", "ListComp")):
                    return True
                if _t == "IfExpr":
                    return _is_seq_src(v.get("body")) or _is_seq_src(v.get("orelse"))
                if _t == "Var":
                    return v.get("name") in self._seq_locals
                return False

            for _nm, _et in list(self._array_elem_types.items()):
                if (_acounts.get(_nm, 0) >= 2
                        or (_et == "string" and _is_seq_src(_firstv.get(_nm)))):
                    self._seq_locals.add(_nm)
                    self._seq_value_types[_nm] = _et
                    self._array_elem_types.pop(_nm, None)
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
        # no-more-int emitter L2: locals bound from a `string`-returning call.
        string_vars |= self._collect_str_call_result_locals(body_stmts)
        # J2/J3 convergence (Call-internals): a local assigned a keyword string read
        # (`bound = kw.value.id` / `kw.value.attr`) or `call.func.id` is a `string` local
        # — so its `None` init lowers to `ref ""` and `{"bound": bound}` wraps `PStr bound`
        # (Optional[str] modelled as string with "" for None; the pyval PStr value tag).
        string_vars |= self._collect_keyword_str_locals(body_stmts)
        # L1 tparam reflection-node ADT: locals from a tparam string read
        # (`type(tp).__name__` / `tp.name` / `bnode.id`/`.attr`) are `string` locals.
        string_vars |= self._collect_tparam_str_locals(body_stmts)
        # A reassigned formal string PARAM (`s = s.strip()`) is NOT a fresh typed
        # local: it must follow the int-param entry-shadow path (`let s = ref s in`
        # + `s := …`), never a let-bind at first assign (which would deref `!s`
        # before the ref exists). The str-method collectors above re-added params
        # that the `string_vars` comprehension above (`name not in _formal_params`)
        # deliberately excluded; restore that exclusion so the param reaches
        # `pre_decl_vars` and is shadowed at function entry.
        string_vars -= set(self._formal_params)
        self._string_local_vars = string_vars
        # L18 S1c-join: a Module5 seq-promoted local (`types = []; types.append(<str>)`)
        # whose EVERY element source is string-valued is a `seq string` — record it in
        # `_seq_value_types` so `" ".join(types)` recognizes it (`str_join_seq`, a string)
        # rather than the opaque int `join_1`. Must run AFTER the string-local collectors
        # above (so a split-elem/str-method/dict-value append source is seen as string).
        self._mark_string_seq_locals(body_stmts)
        # typed-ir §19: emit_ir locals — excluded from the int `ref 0` pre-decl (they get
        # a `ref (IrOther "")` pre-decl in `_emit_body_code`), so their `:=` typechecks.
        self._emit_ir_local_vars = self._collect_emit_ir_result_locals(body_stmts)
        # 07-2333-rev2 Gap 3: a seq-promoted (growable) list LOCAL must NOT be pre-declared
        # as `ref 0 : ref int` — it is `ref (seq int)`, let-bound at its first assignment by
        # `_handle_seq_assign` (07-1705 P3). Excluding it here is what lets the first assign
        # emit `let items = ref (Seq.cons …)` instead of `items := …` onto an int ref (the
        # `seq int … expected int` leak). Params are not in pre_decl_vars, so unioning the
        # full set is safe.
        seq_local_vars = getattr(self, "_seq_locals", set()) - set(self._formal_params)
        # tool-feature-5: a mutable Optional local (`x: Optional[τ] = None`) carries a
        # synthesized `_union_*` type, NOT int — exclude it from the integer `ref 0`
        # pre-declaration so its first assign (`x = None`) let-binds `ref (Arm_i_None :
        # _union)` (the union ref) instead of `ref 0` + a type-clashing `:=`. Byte-inert:
        # no corpus program has an Optional-typed mutable local (only Optional params).
        _union_locals = {
            name for name, ty in getattr(self, "_current_symbol_table", {}).items()
            if isinstance(ty, str) and ty.startswith("_union_")
            and name not in set(self._formal_params)
        }
        self._optional_union_locals = _union_locals
        # hval-value-model-wall: locals bound from a `Dict[str, PyVal]` subscript read
        # are hval-typed refs (let-bound at first assign, not `ref 0`). Byte-inert.
        pyval_read_vars = self._collect_pyval_read_locals(body_stmts) - set(self._formal_params)
        self._pyval_local_vars = pyval_read_vars
        # 7a (self-tcb-reduction L4b): a tparam_list-alias local is never a real value (its
        # assignment emits nothing; iteration resolves to `type_params_of node`) — exclude
        # it from the `ref 0` pre-declaration so no dead `let tparams = ref 0` is emitted.
        tparam_alias_vars = (set(getattr(self, "_tparam_list_aliases", {}))
                             - set(self._formal_params))
        return (array_vars | dict_vars | lambda_vars | record_vars | variant_vars
                | set(tuple_vars) | string_vars | seq_local_vars | _union_locals
                | pyval_read_vars | tparam_alias_vars
                | getattr(self, "_str_set_locals", set())
                | getattr(self, "_emit_ir_local_vars", set()))

    def _collect_array_elem_types(self, body_stmts: List[Dict[str, Any]]) -> Dict[str, str]:
        """list-comprehension-lowering.md L1/L2/L6: map an array LOCAL → its element WhyML
        type ("string"/"emit_ir"/"int"), from the shapes the emitter builds string arrays
        with: a comprehension (`[elt for …]`), a list-repeat (`[e] * n`), an ArrayLit of
        strings, a `List[str]` record-field read, or another such local. @mutable_state only
        → empty (and inert) for every corpus function."""
        out: Dict[str, str] = {}
        if (getattr(self, "_current_self_type", None)
                not in getattr(self, "_mutable_state_classes", set())):
            return out
        rt = getattr(self, "_record_types", {})
        st = getattr(self, "_current_symbol_table", {})

        def _elt_ty(e: Any) -> Optional[str]:
            if not isinstance(e, dict):
                return None
            if self._is_string_expr(e):
                return "string"
            if self._is_emit_ir_expr(e):
                return "emit_ir"
            return "int"

        def _val_elem_ty(v: Any) -> Optional[str]:
            if not isinstance(v, dict):
                return None
            t = v.get("type")
            if t == "ListComp":
                # self-ir-schema.md IR2: bind each generator target to its iterable's
                # element class (a `sharedvar` for `self.ir.get("shared_vars")`) so the
                # element expr `sv["name"]` types; restore after.
                _saved = {}
                for _g in (v.get("generators") or []):
                    _ec = self._iter_elem_class(_g.get("iter", {}))
                    _tv = _g.get("target")
                    if _ec and isinstance(_tv, str) and st is not None:
                        _saved[_tv] = st.get(_tv)
                        st[_tv] = _ec
                _r = _elt_ty(v.get("elt", {}))
                for _tv, _old in _saved.items():
                    if _old is None: st.pop(_tv, None)
                    else: st[_tv] = _old
                return _r
            if t == "Call" and isinstance(v.get("func"), str) and v["func"].endswith(".findall"):
                return "string"      # L7: re.findall → array string
            # item34.md CF5: the seq string name-collection sources → `string` element.
            if t == "Call" and isinstance(v.get("func"), str):
                _fn = v["func"]
                # #15: `self._nested_seq_field.get(k)` (`Dict[str,List[T]]`) → the inner `seq T`
                # element type, so the local is a `seq T` (promoted via `_is_seq_src`).
                if _fn.endswith(".get") and _fn[:-len(".get")].startswith("self."):
                    _nu = self._self_field_dict_nu(_fn[:-len(".get")])
                    if isinstance(_nu, str) and _nu.startswith("seq "):
                        return _nu[len("seq "):]
                if (self._call_returns_string_collection(_fn) or _fn.endswith(".split")):
                    return "string"
                if _fn in ("sorted", "set", "frozenset", "list") and v.get("args"):
                    return _val_elem_ty(v["args"][0])
                # cf6.md M1.6: `<emit_ir>.get("captures"/"args")` reads the args LIST
                # (`args_of`) - an emit_ir-element array (`existing_caps`).
                if _fn.endswith(".get"):
                    _ga = v.get("args") or []
                    if (_ga and isinstance(_ga[0], dict) and _ga[0].get("type") == "String"
                            and _ga[0].get("value") in ("captures", "args", "parts", "elts", "alternatives")
                            and self._is_emit_ir_expr(
                                {"type": "Var", "name": _fn[:-len(".get")]})):
                        return "emit_ir"
            # self-tcb-reduction T1.a: `node.elts`/`node.parts` (a node-list attr) → emit_ir elem.
            if t in ("Attribute", "FieldGet") and (v.get("attr") or v.get("field")) in (
                    "elts", "parts", "args", "captures", "alternatives"):
                _o = v.get("object") or v.get("value")
                if isinstance(_o, dict) and self._is_emit_ir_expr(_o):
                    return "emit_ir"
            # cf6.md M1.6: `<array> or []` - the element class is the left array's.
            if t == "BinOp" and v.get("op") == "or":
                return _val_elem_ty(v.get("left", {}))
            if (t == "BinOp" and v.get("op") == "+"
                    and isinstance(v.get("left"), dict)
                    and v["left"].get("type") in ("ArrayLit", "ListLit", "ListComp")):
                return "string"
            if t == "IfExpr":
                for _arm in (v.get("body"), v.get("orelse")):
                    if (isinstance(_arm, dict) and _arm.get("type") == "Call"
                            and isinstance(_arm.get("func"), str)
                            and _arm["func"].endswith(".split")):
                        return "string"
                    if _val_elem_ty(_arm) == "string":
                        return "string"
            if t == "BinOp" and v.get("op") == "*":
                for side in ("left", "right"):
                    s = v.get(side, {})
                    if isinstance(s, dict) and s.get("type") in ("ArrayLit", "ListLit"):
                        _e = (s.get("elts") or [None])[0]
                        return _elt_ty(_e) if _e else None
            if t in ("ArrayLit", "ListLit"):
                _e = (v.get("elts") or [None])[0]
                return _elt_ty(_e) if _e else None
            if t in ("Attribute", "FieldGet"):     # a List[str] record field → string elems
                _recv = v.get("object")
                if isinstance(_recv, dict):
                    _recv = _recv.get("name")
                _fld = v.get("field") or v.get("attr")
                # `self.<field>` resolves via `_current_self_type`; a record-typed param
                # (`stmt.<field>`) via the symbol table.
                _cls = (getattr(self, "_current_self_type", None) if _recv == "self"
                        else (st.get(_recv) if _recv else None))
                _rec = (rt.get(_cls) or (rt.get(_cls.lower()) if _cls else None)) if _cls else None
                if _rec and _rec.get("field_types", {}).get(_fld) in ("list", "tuple"):
                    _vt = _rec.get("field_value_types", {}).get(_fld)
                    return _vt if _vt in ("string", "emit_ir") else "int"
            if t == "Var":
                return out.get(v.get("name"))
            return None

        firsts: List[Tuple[str, Any]] = []
        seen: Set[str] = set()

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign" and isinstance(node.get("target"), str):
                    tgt = node["target"]
                    if tgt not in seen:
                        seen.add(tgt)
                        firsts.append((tgt, node.get("value", {})))
                for x in node.values():
                    rec(x)
            elif isinstance(node, list):
                for x in node:
                    rec(x)
        rec(body_stmts)
        changed = True
        while changed:                       # fixpoint for var-to-var propagation
            changed = False
            for tgt, v in firsts:
                if tgt in out:
                    continue
                _ty = _val_elem_ty(v)
                if _ty is not None:
                    out[tgt] = _ty
                    changed = True
        return out

    def _prescan_todict_aliases(self, body_stmts):
        _ms = (getattr(self, "_current_self_type", None)
               in getattr(self, "_mutable_state_classes", set()))
        for st in body_stmts or []:
            if not isinstance(st, dict): continue
            if st.get("stmt") in ("assign", "Assign"):
                v = st.get("value", {})
                fn = v.get("func") if isinstance(v, dict) and v.get("type") == "Call" else None
                tgt = st.get("target")
                if isinstance(fn, str) and fn.endswith(".to_dict") and not v.get("args") and isinstance(tgt, str):
                    self._todict_aliases[tgt] = fn[:-len(".to_dict")]
                # §26: `X = getattr(self, "<field>", …)` where <field> is a dict/set
                # record field → alias X to `self.<field>` (@mutable_state only).
                if _ms and isinstance(tgt, str) and isinstance(v, dict):
                    _gf = self._getattr_self_field(v)
                    if _gf and self._self_field_dict_nu(f"self.{_gf}") is not None:
                        self._getattr_self_dict_aliases[tgt] = _gf
            for key in ("body", "orelse", "finalbody", "then", "else_body"):
                sub = st.get(key)
                if isinstance(sub, list): self._prescan_todict_aliases(sub)

    def _opaque_selfmap_getattr_field(self, v: Any) -> Optional[str]:
        """If `v` is `getattr(self, "<field>", {})` with an EMPTY dict-literal
        default (the opaque-instance-map defensive read), return `<field>`; else
        None. Distinct from §26's `_getattr_self_field` in requiring the empty-
        dict default (the distinguishing shape of an opaque map, not a scalar)."""
        if not (isinstance(v, dict) and v.get("type") == "Call"
                and v.get("func") == "getattr"):
            return None
        a = v.get("args", [])
        if not (len(a) == 3 and isinstance(a[0], dict) and a[0].get("name") == "self"
                and isinstance(a[1], dict) and a[1].get("type") == "String"):
            return None
        dflt = a[2]
        if not (isinstance(dflt, dict) and dflt.get("type") in ("DictLit", "Dict")
                and not dflt.get("keys") and not dflt.get("items")
                and not dflt.get("values")):
            return None
        return a[1].get("value")

    def _opaque_selfmap_inner_getattr(self, v: Any):
        """SPLIT form of the opaque-nested-map read: if `v` is
        `getattr(self, "<field>", {}).get(<key>)` (a `.get` on an opaque-instance-map
        getattr, binding the INNER dict for one OUTER key) return `(<field>, <key-ir>)`;
        else None. The receiver must be the empty-dict-default getattr (the opaque-map
        shape `_opaque_selfmap_getattr_field` recognizes); the call a single-arg `.get`."""
        if not (isinstance(v, dict) and v.get("type") == "Call"
                and v.get("func") == "get"):
            return None
        recv = v.get("receiver")
        fld = self._opaque_selfmap_getattr_field(recv)
        if not fld:
            return None
        args = v.get("args") or []
        if len(args) != 1 or not isinstance(args[0], dict):
            return None
        return (fld, args[0])

    def _inner_alias_str_reads(self, node: Any, local: str, out: Set[str]) -> None:
        """Collect the string litkeys `<lit>` for every read `<local>["<lit>"]` (Subscript)
        or `<local>.get("<lit>")` (Call) anywhere in an IR subtree — the read shape that
        distinguishes an opaque-nested-map INNER alias (used to gate registration so the
        recognizer is corpus-inert)."""
        if isinstance(node, dict):
            if node.get("type") == "Subscript":
                idx = node.get("index", {})
                inner = node.get("value", {})
                if (isinstance(idx, dict) and idx.get("type") == "String"
                        and isinstance(inner, dict) and inner.get("type") == "Var"
                        and inner.get("name") == local):
                    out.add(idx.get("value"))
            if (node.get("type") == "Call" and node.get("func") == "get"):
                recv = node.get("receiver")
                a = node.get("args") or []
                # ONLY a 1-arg leaf `.get("<lit>")` (no default) — a 2-arg
                # `.get("field_types", {})` returns a NESTED dict, not a leaf string,
                # and must NOT be modelled as the string reader (it would type-clash a
                # chained `.get(field)`). This scopes the recognizer to leaf-string
                # projections (the `_union_arm_whyml_type` shape).
                if (isinstance(recv, dict) and recv.get("type") == "Var"
                        and recv.get("name") == local and len(a) == 1
                        and isinstance(a[0], dict) and a[0].get("type") == "String"):
                    out.add(a[0].get("value"))
            for w in node.values():
                self._inner_alias_str_reads(w, local, out)
        elif isinstance(node, list):
            for w in node:
                self._inner_alias_str_reads(w, local, out)

    def _nested_str_subscript_reads(self, node: Any, local: str, out: Set[str]) -> None:
        """Collect the set of string litkeys `<lit>` for every nested read
        `<local>[<k>]["<lit>"]` anywhere in an IR subtree — the read shape that
        distinguishes an opaque nested-map alias (used to gate registration so
        the recognizer is corpus-inert)."""
        if isinstance(node, dict):
            if node.get("type") == "Subscript":
                idx = node.get("index", {})
                inner = node.get("value", {})
                if (isinstance(idx, dict) and idx.get("type") == "String"
                        and isinstance(inner, dict) and inner.get("type") == "Subscript"
                        and isinstance(inner.get("value"), dict)
                        and inner["value"].get("type") == "Var"
                        and inner["value"].get("name") == local):
                    out.add(idx.get("value"))
            for w in node.values():
                self._nested_str_subscript_reads(w, local, out)
        elif isinstance(node, list):
            for w in node:
                self._nested_str_subscript_reads(w, local, out)

    def _prescan_opaque_selfmap_aliases(self, body_stmts: List[Dict[str, Any]]) -> None:
        """Register each `<local> = getattr(self, "<field>", {})` whose alias local
        is later read via the nested `<local>[k]["<lit>"]` string projection as an
        opaque-instance-map alias (`_opaque_selfmap_aliases[local] = <base>`, base =
        the field name with leading underscores stripped). Gated on the nested-read
        shape being PRESENT so no other getattr-empty-dict usage changes emission."""
        assigns: List[Tuple[str, str]] = []
        inner_assigns: List[Tuple[str, str, Any]] = []
        def _walk(stmts):
            for st in stmts or []:
                if not isinstance(st, dict): continue
                if st.get("stmt") in ("assign", "Assign"):
                    tgt = st.get("target")
                    val = st.get("value", {})
                    fld = self._opaque_selfmap_getattr_field(val)
                    if isinstance(tgt, str) and fld:
                        assigns.append((tgt, fld))
                    else:
                        _inner = self._opaque_selfmap_inner_getattr(val)
                        if isinstance(tgt, str) and _inner:
                            inner_assigns.append((tgt, _inner[0], _inner[1]))
                for key in ("body", "orelse", "finalbody", "then", "else_body"):
                    sub = st.get(key)
                    if isinstance(sub, list): _walk(sub)
        _walk(body_stmts)
        for local, fld in assigns:
            litkeys: Set[str] = set()
            self._nested_str_subscript_reads(body_stmts, local, litkeys)
            if litkeys:
                self._opaque_selfmap_aliases[local] = fld.lstrip("_")
        for local, fld, key_ir in inner_assigns:
            litkeys: Set[str] = set()
            self._inner_alias_str_reads(body_stmts, local, litkeys)
            if litkeys:
                self._opaque_selfmap_inner_aliases[local] = (fld.lstrip("_"), key_ir)

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
        self._prescan_todict_aliases(body_stmts)
        self._opaque_selfmap_aliases = {}
        self._opaque_selfmap_inner_aliases = {}
        self._prescan_opaque_selfmap_aliases(body_stmts)
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
            # opaque-nested-map-reader: alias locals are never a real value (their
            # getattr assignment is suppressed; reads route to boundary readers) —
            # so no `ref 0` pre-declaration.
            and v not in self._opaque_selfmap_aliases
            # opaque-nested-map-reader SPLIT form: an inner-alias local is never a real
            # value (reads route to boundary readers) — so no `ref 0` pre-declaration.
            and v not in getattr(self, "_opaque_selfmap_inner_aliases", {})
            # K7 (pyval-chained `.get`, self-tcb-reduction Tier-5): a pyval chain local
            # is `let`-bound immutable at its assignment (single-assignment SSA), never
            # an int `ref 0` pre-decl (which would int-erase it). Gated -> byte-inert.
            and v not in getattr(self, "_pyval_locals", set())
        }
        # todict-reflection-plan.md R3: in a @mutable_state class (the emitter model),
        # a string local is PRE-DECLARED `ref ""` (not let-bound at first assign), so a
        # local first-assigned inside a conditional branch (`if …: hi = a else: hi = b`)
        # stays in scope after the branch — the string analogue of the int `ref 0`
        # pre-decl. Gated on @mutable_state → byte-identical for every other method.
        _ms_body = (is_method and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set()))
        _str_predecl: Set[str] = set()
        _emit_ir_predecl: Set[str] = set()
        if _ms_body:
            _str_predecl = {v for v in getattr(self, "_string_local_vars", set())
                            if v in local_refs and v not in ghost_vars
                            and v not in ref_params and v not in self._formal_params
                            and v not in struct_array_targets and v not in struct_pack_targets}
            pre_decl_vars |= _str_predecl
            # typed-ir §19: emit_ir locals pre-declare `ref (IrOther "")` (the emit_ir
            # counterpart of the string `ref ""` pre-decl above).
            _emit_ir_predecl = {v for v in getattr(self, "_emit_ir_local_vars", set())
                                if v in local_refs and v not in ghost_vars
                                and v not in ref_params and v not in self._formal_params
                                and v not in struct_array_targets and v not in struct_pack_targets
                                and v not in _str_predecl}
            pre_decl_vars |= _emit_ir_predecl

        # W8/W1: a local bound to an element of an `array <record>` self-field
        # (`t = self.toks[self.i]`, the token cursor's `advance`) is RECORD-typed, so
        # the integer `ref 0` pre-decl mistypes it. Pre-declare it with the element
        # record's default literal — the record counterpart of the `ref ""` / `ref
        # (IrOther "")` pre-decls above. `_record_array_fields` is non-empty only for a
        # `List[<record>]` record field, so this is inert everywhere else.
        _rec_predecl: Dict[str, str] = {}
        if getattr(self, "_record_array_fields", None):
            for _v, _rec in self._collect_record_field_elem_locals(body_stmts).items():
                if (_v in local_refs and _v not in ghost_vars
                        and _v not in ref_params and _v not in self._formal_params
                        and _v not in struct_array_targets
                        and _v not in struct_pack_targets
                        and _v not in _str_predecl and _v not in _emit_ir_predecl):
                    _rec_predecl[_v] = _rec
            pre_decl_vars |= set(_rec_predecl)
        # W8 capability (iii): publish the map so `t.<field>` on such a local
        # projects natively (`(!t).<label>`) instead of falling through to the
        # opaque `(get_<field> !t)` getter, which mistypes against the record.
        self._record_field_elem_locals = dict(_rec_predecl)

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
                # stmt-list-append-mutation wall (C-bucket): a `ref (seq stmt_ir)` param IS
                # already the caller-visible ref — do NOT shadow it with a `snapshot` local
                # copy (that was the wall: the append became invisible to the caller). The
                # param's own ref is written directly (`p := Seq.snoc !p v`).
                if var in getattr(self, "_stmt_seq_mut_params", set()):
                    continue
                self._add_abstract_op(
                    "val snapshot (a: array int) : seq int\n"
                    "    ensures { Seq.length result = Array.length a }\n"
                    "    ensures { forall i:int. 0 <= i < Array.length a -> Seq.get result i = a[i] }")
                body_code = f"    let {safe_var} = ref (snapshot {safe_var}) in\n{body_code}"
                continue
            # R3: a @mutable_state string local pre-declares `ref ""` (see above).
            if var in _str_predecl:
                init = '""'
            elif var in _emit_ir_predecl:
                init = '(IrOther "")'   # typed-ir §19: emit_ir local pre-decl
            elif var in _rec_predecl:
                # W8/W1: record-element local pre-decl (see above).
                init = self._record_default_literal(_rec_predecl[var])
            else:
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
            # K1 (seq-hval self-field append): a `seq hval` self-field target grows
            # via the REAL record write-back `self.<field> <- Seq.snoc self.<field> …`
            # (emitted at the `_handle_expr_stmt` append site), so it needs NEITHER the
            # `Array.make 1024 0` shadow-local NOR the `_len` counter — skip both.
            # Empty set for the corpus -> byte-inert.
            if tgt in getattr(self, "_pyval_seq_append_targets", set()):
                continue
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
                # stmt-list-append-mutation wall (C-bucket): the `ref (seq stmt_ir)` param
                # is already the caller-visible ref — no `snapshot` shadow (see the
                # pre_decl loop above).
                if tgt in getattr(self, "_stmt_seq_mut_params", set()):
                    continue
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

