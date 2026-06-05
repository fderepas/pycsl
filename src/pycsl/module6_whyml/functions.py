from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from module6_whyml.identifiers import whyml_ident, safe_mutex_name, safe_exc_name
from module6_whyml.ir_scanner import IRScanner


class FunctionEmissionMixin:
    """Function-emission: signature assembly, parameter typing, contract emission, return-type computation, per-function state reset, and the cross-method type maps populated by `transpile()` before any function body is emitted. Mixed into Module6_WhyMLTranspiler."""

    def _param_type_str(self, arg: str, ref_params: Set[str], array2d_params: Set[str],
                        array1d_params: Set[str], symbol_table: Dict[str, Any],
                        int_type: str) -> str:
        """Return the WhyML parameter type string for a standalone function argument."""
        safe = whyml_ident(arg)
        if arg in ref_params:
            return f"({safe}: ref {int_type})"
        if arg in array2d_params:
            return f"({safe}: matrix {int_type})"
        symtype = symbol_table.get(arg)
        # `Set[T]` / `Dict[K, V]` / `FrozenSet[T]` parameters are
        # modelled as `map int (option int)` (parallel to body-level
        # dicts). Must come before the `list` branch since dict/set
        # share the map model, not the array model.
        if symtype in ("set", "dict", "frozenset"):
            return f"({safe}: map int (option int))"
        if arg in array1d_params or symtype == "list":
            if self._value_semantic:
                return f"({safe}: array {int_type})"
            return f"({safe}: loc) ({safe}_len: int)"
        if symtype == "str":
            # strings-plan Stage 1: runtime `str` is a value-semantic Why3 string
            # (string.String), unifying with the ghost-string model.
            return f"({safe}: string)"
        if symtype == "float":
            # no-more-int Stage D: `float` is Why3 `real` (was the unsound τ(float)=int).
            return f"({safe}: real)"
        return f"({safe}: {int_type})"

    def _collect_record_fields(self, type_decls: List[Dict[str, Any]]) -> Set[str]:
        """Collect all declared record field names for FieldGet resolution."""
        fields: Set[str] = set()
        n = len(type_decls)
        i = 0
        while i < n:
            td = type_decls[i]
            if td["kind"] == "record":
                flds = td.get("fields", [])
                nf = len(flds)
                j = 0
                while j < nf:
                    fields.add(flds[j]["name"])
                    j += 1
            i += 1
        return fields

    def _reset_function_state(self, func: Dict[str, Any],
                               body_stmts: List[Dict[str, Any]]) -> Tuple[Set[str], Set[str]]:
        """Reset all per-function instance variables. Returns (local_refs, ghost_vars)."""
        self._bounded_int = func.get("bounded_int")
        # `no_exception` context for VC injection. `_current_no_exception`
        # is the set of exception names whose triggers must produce an
        # `assert { ... }` before the matching IR operation; the `_all`
        # flag (Phase 1.5) expands to the full Phase 1 set when consulted
        # at injection time. Populated from contracts.no_exception /
        # contracts.no_exception_all per the IR schema (PR 1).
        contracts = func.get("contracts", {})
        self._current_no_exception: Set[str] = set(contracts.get("no_exception", []) or [])
        self._current_no_exception_all: bool = bool(contracts.get("no_exception_all", False))
        symbol_table = func.get("symbol_table", {})
        local_refs = IRScanner.find_assigned_vars(body_stmts)
        local_refs -= self._shared_var_names
        ghost_vars = IRScanner.find_ghost_vars(body_stmts)
        self._current_params = (
            (set(symbol_table.keys()) | local_refs | ghost_vars) - self._shared_var_names
        )
        self._array_locals = set()
        self._dict_locals = set()
        self._lambda_locals = set()
        self._record_locals = set()
        self._ghost_string_vars: Set[str] = set()
        self._ghost_array_vars: Set[str] = set()
        self._ghost_dict_vars: Set[str] = set()
        self._ghost_list_vars: Set[str] = set()
        self._ghost_set_vars: Set[str] = set()
        self._ghost_tuple_vars: Dict[str, int] = {}  # name → arity (2, 3, or 4)
        self._known_collection_sizes = {}
        self._known_collection_elements = {}
        self._current_symbol_table = symbol_table
        # Formal-parameter names ONLY — Module5 exposes this as a
        # distinct field because `symbol_table` is polluted with loop
        # targets and locals.
        # Ordered list, NOT a set: the WhyML signature iterates this for the
        # parameter order (see `_build_param_list`), so a set would make the
        # emitted param order hash-seed-dependent (a source of proof flakiness,
        # e.g. `gcd (a) (b)` vs `(b) (a)`). Source order is deterministic.
        self._formal_params: List[str] = list(func.get("formal_params", []))
        self._current_array1d_params = set(func.get("array1d_params", []))
        self._array2d_params = set(func.get("array2d_params", []))
        return local_refs, ghost_vars

    def _build_param_list(self, func: Dict[str, Any],
                           local_refs: Set[str],
                           ghost_vars: Set[str]) -> Tuple[Set[str], str]:
        """Compute WhyML parameter string. Returns (ref_params, args_str).
        Mutates self._current_self_type."""
        is_method = func.get("kind") == "method"
        bounded_int = func.get("bounded_int")
        int_type = f"int{bounded_int}" if bounded_int else "int"
        symbol_table = self._current_symbol_table
        array2d_params = self._array2d_params
        array1d_params = self._current_array1d_params

        if is_method:
            self._current_self_type = func["self_type"].lower()
            param_parts = [f"(self: {self._current_self_type})"]
            for arg in symbol_table:
                if arg in local_refs or arg in ghost_vars:
                    continue
                safe = whyml_ident(arg)
                if arg in array2d_params:
                    param_parts.append(f"({safe}: matrix {int_type})")
                elif symbol_table.get(arg) in ("set", "dict", "frozenset"):
                    param_parts.append(f"({safe}: map int (option int))")
                elif (arg in array1d_params
                      or symbol_table.get(arg) in ("list", "bytes", "bytearray")):
                    # bytes/bytearray are modeled as `array int` per
                    # missing-bytes-struct-feature.md Phase 1: each
                    # cell is a byte value (0..255). Lifts the
                    # transpiler limit that previously auto-trusted
                    # struct.unpack call sites with array-int args.
                    if self._value_semantic:
                        param_parts.append(f"({safe}: array {int_type})")
                    else:
                        param_parts.append(f"({safe}: loc) ({safe}_len: int)")
                elif symbol_table.get(arg) == "str":
                    # strings-plan Stage 1: runtime `str` is a value-semantic Why3 string
                    # (mirrors _param_type_str for standalone functions — methods were
                    # missed, leaving str method params typed int while _is_string_expr,
                    # which reads the symbol table, treated them as string).
                    param_parts.append(f"({safe}: string)")
                elif symbol_table.get(arg) == "float":
                    param_parts.append(f"({safe}: real)")  # no-more-int Stage D
                else:
                    param_parts.append(f"({safe}: {int_type})")
            return set(), " ".join(param_parts)
        else:
            self._current_self_type = None
            ref_params = {v for v in symbol_table if v in local_refs and v.startswith("obj_")}
            # Formal parameters stay in `args` even if mutated in the
            # body — they get promoted to refs inside _emit_body_code
            # via shadowing (`let a = ref a in`). Without this, params
            # that are tuple-unpack targets (e.g., `a, b = b, a % b`)
            # silently disappear from the WhyML signature.
            #
            # Use `_formal_params` (unpolluted) not `symbol_table`
            # (which Module4 also fills with for-loop targets and
            # AnnAssign locals — those must NOT appear in the
            # function signature).
            args = [v for v in self._formal_params if v not in ghost_vars]
            args_str = " ".join(
                self._param_type_str(arg, ref_params, array2d_params, array1d_params,
                                     symbol_table, int_type)
                for arg in args
            )
            return ref_params, args_str

    def _emit_contracts(self, contracts: Dict[str, Any], spec_refs: Set[str],
                         func_variants: List[Any], func_diverges: bool,
                         func_exceptions: Set[str]) -> List[str]:
        """Emit requires/ensures/assigns/variant/raises lines.
        Toggles self._in_spec around emission."""
        lines: List[str] = []
        self._in_spec = True

        requires_exprs = contracts.get("requires", [])
        ensures_exprs  = contracts.get("ensures", [])

        for req in requires_exprs:
            lines.append(f"    requires {{ {self._expr_to_whyml(req, spec_refs)} }}")
        for ens in ensures_exprs:
            # Tag linear ensures with a comment so the runner can classify VCs.
            # Linear VCs are candidates for omega proofs in Lean 4 (Task 7).
            lin_tag = " (* linear *)" if self._is_linear_vc([ens], requires_exprs) else ""
            # Attribution: a desugared `act` ensures carries `act_name` (Module3/5)
            # so a proof failure points back to its named case.
            act_tag = (f" (* act {ens['act_name']} *)"
                       if isinstance(ens, dict) and ens.get("act_name") else "")
            lines.append(f"    ensures  {{ {self._expr_to_whyml(ens, spec_refs)} }}{act_tag}{lin_tag}")
        for fl in self._emit_frame_condition(contracts.get("assigns", []), spec_refs):
            lines.append(fl)
        for fv in func_variants:
            v_expr = self._expr_to_whyml(fv["expr"], spec_refs)
            if fv.get("ordering"):
                lines.append(f"    variant  {{ {v_expr} }} with {fv['ordering']}")
            else:
                lines.append(f"    variant  {{ {v_expr} }}")
        if func_diverges:
            lines.append("    diverges")

        raises_contracts = contracts.get("raises", [])
        if raises_contracts:
            for rc in raises_contracts:
                cond_str = self._expr_to_whyml(rc["condition"], spec_refs)
                lines.append(
                    f"    raises {{ {safe_exc_name(rc['exc_type'])} -> {cond_str} }}"
                )
            declared_exc = {safe_exc_name(rc["exc_type"])
                             for rc in raises_contracts}
            sanitized_func_exc = {safe_exc_name(e) for e in func_exceptions}
            for exc in sorted(sanitized_func_exc - declared_exc):
                lines.append(f"    raises {{ {exc} }}")
        elif func_exceptions:
            sanitized = sorted({safe_exc_name(e) for e in func_exceptions})
            lines.append(f"    raises {{ {', '.join(sanitized)} }}")

        self._in_spec = False
        return lines

    def _compute_return_type(self, func: Dict[str, Any], body_stmts: List[Dict[str, Any]]) -> str:
        """Compute the WhyML return type for one function, applying the
        `List[T] → array int`, `Set[T]`/`Dict[K, V]` → `map int (option int)`,
        and bounded-int overrides."""
        bounded_int = func.get("bounded_int")
        return_type = IRScanner.find_return_type(body_stmts)
        ann = func.get("return_annotation")
        if ann == "list" and return_type == "int":
            return_type = "array int"
        elif ann in ("set", "dict", "frozenset") and return_type == "int":
            return_type = "map int (option int)"
        elif ann == "str" and return_type == "int":
            return_type = "string"
        elif ann == "float" and return_type == "int":
            return_type = "real"  # no-more-int Stage D
        if bounded_int and return_type == "int":
            return_type = f"int{bounded_int}"
        return return_type

    def _emit_function(self, func: Dict[str, Any], scc_info: Dict[str, tuple]) -> List[str]:
        """Emit one WhyML let/val function block. Returns the list of output lines."""
        name = whyml_ident(func["name"])
        body_stmts = func["body"]
        is_method = func.get("kind") == "method"

        local_refs, ghost_vars = self._reset_function_state(func, body_stmts)
        ref_params, args_str = self._build_param_list(func, local_refs, ghost_vars)

        return_type = self._compute_return_type(func, body_stmts)
        # `_func_return_type` is read by `_handle_return_stmt` to pick
        # the right Return exception (int / array / tuple); set it AFTER
        # the `List[T] → array int` override so the array-Return slot
        # path fires.
        self._func_return_type = return_type
        self._current_tuple_arity = (
            return_type.count(",") + 1 if return_type.startswith("(") else 0
        )

        func_variants = func.get("function_variants", [])
        func_diverges = func.get("diverges", False)
        func_trusted = func.get("trusted", False)
        # `#@ \abstract` — emit a bodyless `val` defined by its contract alone
        # (an uninterpreted op, sound; see Module2_Parser.Abstract). Same WhyML
        # shape as a trusted stub (`val` + spec, no body) but distinct
        # provenance: it does NOT count as \trusted for the 0-trusted policy.
        func_abstract = func.get("abstract", False)
        emit_as_val = func_trusted or func_abstract
        if self._should_auto_trust_map_return(func, func_trusted):
            func_trusted = True
            self._auto_trusted_map_returns = (
                self._auto_trusted_map_returns + [func["name"]])
        if self._should_auto_trust_array_return(func, body_stmts, return_type, func_trusted):
            func_trusted = True
            self._auto_trusted_array_returns = (
                self._auto_trusted_array_returns + [func["name"]])
        if self._should_auto_trust_tuple_return(body_stmts, return_type, func_trusted):
            func_trusted = True
            self._auto_trusted_tuple_returns = (
                self._auto_trusted_tuple_returns + [func["name"]])
        if self._should_auto_trust_set_op(body_stmts, func_trusted):
            func_trusted = True
            self._auto_trusted_set_op = (
                self._auto_trusted_set_op + [func["name"]])

        func_pure = func.get("pure", False)
        is_recursive = IRScanner.is_recursive(name, body_stmts)
        use_rec = bool(func_variants) or is_recursive
        can_emit_as_logic = func_pure and not local_refs and not is_method

        _scc_idx, _pos_in_scc, _scc_size = scc_info.get(func["name"], (0, 0, 1))
        is_and_clause = _pos_in_scc > 0 and not emit_as_val and not can_emit_as_logic

        lines: List[str] = []
        if emit_as_val:
            kw = f"val {name}"
        elif can_emit_as_logic:
            kw = f"{'let rec function' if use_rec else 'let function'} {name}"
        elif is_and_clause:
            kw = f"and {name}"
        else:
            kw = f"{'let rec' if (use_rec or _scc_size > 1) else 'let'} {name}"
        lines.append(f"  {kw} {args_str} : {return_type}" if args_str
                     else f"  {kw} () : {return_type}")

        spec_refs = set() if is_method else ref_params
        func_exceptions = IRScanner.collect_escaping_exceptions(body_stmts)
        lines += self._emit_contracts(func.get("contracts", {}), spec_refs,
                                      func_variants, func_diverges, func_exceptions)

        if emit_as_val:
            lines.append("")
            return lines

        lines.append("  =")
        lines.append(self._emit_body_code(func, body_stmts, local_refs, ghost_vars,
                                          ref_params, is_method, return_type))
        if _pos_in_scc == _scc_size - 1:
            lines.append("")
        return lines

    def _emit_subtyping_goals(self, functions: List[Dict[str, Any]]) -> List[str]:
        """Layer D — emit a Liskov refinement goal per overriding method.

        For `Sub.m` overriding `Base.m`, prove
        `(pre_base -> pre_sub) /\\ (post_sub -> post_base)`: the override may
        only WEAKEN the precondition and STRENGTHEN the postcondition. An
        override that strengthens a precondition (or weakens a postcondition)
        leaves an unprovable goal, so verification fails — the substitutability
        contract is enforced mechanically.
        """
        overrides = self.ir.get("overrides", [])
        if not overrides:
            return []
        by_name = {f["name"]: f for f in functions}
        out: List[str] = []
        for ov in overrides:
            sub_fn = by_name.get(ov["sub_method"])
            base_fn = by_name.get(ov["base_method"])
            if sub_fn and base_fn:
                out += self._render_refinement_goal(ov, sub_fn, base_fn)
        return out

    def _render_refinement_goal(self, ov: Dict[str, Any], sub_fn: Dict[str, Any],
                                base_fn: Dict[str, Any]) -> List[str]:
        # Reuse the normal method setup so `self.field`, params, and `\result`
        # render exactly as in the method's own contract.
        local_refs, ghost_vars = self._reset_function_state(sub_fn, sub_fn["body"])
        _ref_params, args_str = self._build_param_list(sub_fn, local_refs, ghost_vars)
        ret = self._compute_return_type(sub_fn, sub_fn["body"])
        self._in_spec = True

        def conj(exprs: List[Any]) -> str:
            parts = [self._expr_to_whyml(e, set()) for e in (exprs or [])]
            parts = [p for p in parts if p and p != "true"]
            return " /\\ ".join(f"({p})" for p in parts) if parts else "true"

        sub_c = sub_fn.get("contracts", {})
        base_c = base_fn.get("contracts", {})
        base_pre = conj(base_c.get("requires", []))
        sub_pre = conj(sub_c.get("requires", []))
        sub_post = conj(sub_c.get("ensures", []))
        base_post = conj(base_c.get("ensures", []))
        self._in_spec = False

        # Convert function-style binders "(self: sub) (x: int)" into Why3
        # quantifier form "self: sub, x: int" (only the top-level parens are
        # stripped, so a nested `map int (option int)` type survives intact).
        core = args_str.strip()
        if core.startswith("(") and core.endswith(")"):
            core = core[1:-1]
        binders = core.replace(") (", ", ")
        if ret not in ("()", "unit", ""):
            binders += f", result: {ret}"
        gname = whyml_ident(f"{ov['sub_method']}_refines_{ov['base_type']}")
        return [
            f"  goal {gname} :",
            f"    forall {binders}.",
            f"    (({base_pre}) -> ({sub_pre})) /\\ (({sub_post}) -> ({base_post}))",
            "",
        ]

    def _build_method_return_type_map(self, functions: List[Dict[str, Any]]) -> Dict[str, str]:
        """Map method name (un-prefixed, e.g. `_emit_contracts`) → declared
        WhyML return type, used by `_handle_dotted_call` to pick the right
        return-type for `self.<method>(...)` abstract vals. Without this,
        every `self.foo(...)` is abstracted as `val self__foo_<n> ... :
        int`, even when `foo` returns a list (→ `array int`) or a tuple,
        producing downstream type mismatches at the call site."""
        result: Dict[str, str] = {}
        for func in functions:
            ret = IRScanner.find_return_type(func["body"])
            ann = func.get("return_annotation")
            if ann == "list" and ret == "int":
                ret = "array int"
            elif ann in ("set", "dict", "frozenset") and ret == "int":
                # Functions annotated `-> Set[T]` / `-> Dict[K, V]` are
                # auto-trusted via `_should_auto_trust_map_return`; their
                # abstract `val` must announce the map return so callers
                # don't pre-decl a `ref 0` (int) target and then `:=` a
                # map.
                ret = "map int (option int)"
            result[func["name"]] = ret
        return result

    def _build_method_result_ensures_map(self, functions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Map method name → the subset of its `ensures` clauses that
        reference ONLY `\\result` and constants (no params, locals, or
        self-fields). `_handle_dotted_call` converts these to WhyML and
        attaches them to the abstract self-call stub, so a caller can
        discharge bounds/length VCs on the returned value (e.g.
        `\\length(\\result) == 18` for inode reads, or
        `\\result >= -1 and \\result < 16` for slot finders). The stub
        would otherwise lose the contract entirely. Param-referencing
        ensures are excluded — the stub renames params to x0,x1,… so they
        would emit unbound symbols."""
        def result_only(node: Any) -> Optional[bool]:
            # Returns True if the subtree references \result and contains
            # no Var/FieldGet/param leaf; False if it references a
            # disallowed leaf; None if it references neither (pure const).
            if not isinstance(node, dict):
                return None
            t = node.get("type")
            if t in ("Var", "FieldGet", "Attribute", "OldVar", "OldField"):
                return False
            if t == "Result":
                return True
            if t == "ArrayLen":
                return True if node.get("var") == "\\result" else False
            saw_result = False
            for v in node.values():
                children = v if isinstance(v, list) else [v]
                for c in children:
                    r = result_only(c)
                    if r is False:
                        return False
                    if r is True:
                        saw_result = True
            return True if saw_result else None

        out: Dict[str, List[Dict[str, Any]]] = {}
        for func in functions:
            kept = [e for e in (func.get("contracts", {}).get("ensures", []) or [])
                    if result_only(e) is True]
            if kept:
                out[func["name"]] = kept
        return out

    def _build_method_param_result_ensures_map(
            self, functions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Map method name → its `ensures` clauses that reference `\\result`
        and/or the method's own PARAMS (plus constants) — but NO self-fields,
        `\\old`, or locals — with each formal-param Var renamed to `x0,x1,…`
        (the abstract self/record-call stub's positional param names).

        Complements `_build_method_result_ensures_map` (which keeps only
        `\\result`-and-constant clauses and excludes anything param-referencing).
        Those param-referencing clauses ARE expressible at a call site once the
        params are renamed to the stub's `x_i`, letting a driver discharge e.g.
        `\\array_eq(\\result, data)` on a record-instance method call —
        `b.roundtrip(data)` → the stub gets `ensures { \\array_eq(result, x0) }`.
        Self-field / `\\old` clauses stay excluded (heap state the caller can't
        see through an uninterpreted stub)."""
        def classify(node: Any, params: Set[str]) -> Optional[bool]:
            # True if the subtree references \result; False if it references a
            # disallowed leaf (self-field/old/non-param var); None otherwise.
            if not isinstance(node, dict):
                return None
            t = node.get("type")
            if t in ("FieldGet", "Attribute", "OldVar", "OldField"):
                return False
            if t == "Var":
                return None if node.get("name") in params else False
            if t == "Result":
                return True
            if t == "ArrayLen":
                v = node.get("var")
                if v == "\\result":
                    return True
                return None if v in params else False
            saw_result = False
            for val in node.values():
                for c in (val if isinstance(val, list) else [val]):
                    r = classify(c, params)
                    if r is False:
                        return False
                    if r is True:
                        saw_result = True
            return True if saw_result else None

        def refs_param(node: Any, params: Set[str]) -> bool:
            if not isinstance(node, dict):
                return False
            if node.get("type") == "Var" and node.get("name") in params:
                return True
            if node.get("type") == "ArrayLen" and node.get("var") in params:
                return True
            for val in node.values():
                for c in (val if isinstance(val, list) else [val]):
                    if refs_param(c, params):
                        return True
            return False

        def rename(node: Any, pmap: Dict[str, str]) -> Any:
            if not isinstance(node, dict):
                return node
            if node.get("type") == "Var" and node.get("name") in pmap:
                return {"type": "Var", "name": pmap[node["name"]]}
            new: Dict[str, Any] = {}
            for k, v in node.items():
                if k == "var" and node.get("type") == "ArrayLen" and v in pmap:
                    new[k] = pmap[v]
                elif isinstance(v, list):
                    new[k] = [rename(c, pmap) if isinstance(c, dict) else c for c in v]
                elif isinstance(v, dict):
                    new[k] = rename(v, pmap)
                else:
                    new[k] = v
            return new

        out: Dict[str, List[Dict[str, Any]]] = {}
        for func in functions:
            params = func.get("formal_params", []) or []
            if not params:
                continue
            pset = set(params)
            pmap = {p: f"x{i}" for i, p in enumerate(params)}
            kept = [rename(e, pmap)
                    for e in (func.get("contracts", {}).get("ensures", []) or [])
                    if classify(e, pset) is True and refs_param(e, pset)]
            if kept:
                out[func["name"]] = kept
        return out

    @staticmethod
    def _symtype_to_whyml(symtype: Optional[str]) -> str:
        """Convert a Module5 symbol-table type tag to the WhyML type used
        in abstract val parameter declarations. Defaults to `int`."""
        if symtype in ("set", "dict", "frozenset"):
            return "map int (option int)"
        if symtype in ("list", "tuple"):
            return "array int"
        if symtype == "str":
            return "string"
        if symtype == "float":
            return "real"  # no-more-int Stage D
        return "int"

    def _build_method_param_types_map(self, functions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Map function name → list of WhyML parameter types (excluding
        self). Used by `_handle_dotted_call` to emit abstract `val` decls
        with matching parameter types so cross-method calls type-check
        when params are set/dict/list-typed."""
        result: Dict[str, List[str]] = {}
        for func in functions:
            symtable = func.get("symbol_table", {})
            body = func.get("body", [])
            local_assignees = IRScanner.find_assigned_vars(body)
            param_types: List[str] = []
            for name, symtype in symtable.items():
                # Locals (assigned inside the body) are NOT params.
                if name in local_assignees:
                    continue
                param_types.append(self._symtype_to_whyml(symtype))
            result[func["name"]] = param_types
        return result

