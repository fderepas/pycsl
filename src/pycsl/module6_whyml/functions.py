from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from module6_whyml.identifiers import whyml_ident, safe_exc_name
from module6_whyml.ir_scanner import IRScanner
from module6_whyml.scc import emits_as_logic_symbol


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
        if arg in array1d_params or symtype in ("list", "bytes", "bytearray"):
            # 0442.md B2 (no-more-int): bytes/bytearray are the byte-buffer array class.
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
        if symtype in self._record_types:
            # no-more-int-2 Track 3: a bare class-typed param is reconstructed as its record
            # type (was coarsened to int with opaque getattr_<cls>), so `p.field` reads
            # directly. Read-only: mutating a record param is out of scope (value semantics).
            wn = self._record_types[symtype]["whyml_name"]
            self._record_locals.add(arg)
            self._record_param_classes[arg] = wn
            return f"({safe}: {wn})"
        if symtype in self._variant_types:
            # sum-types: a `#@ datatype`-typed param is its Why3 variant type.
            return f"({safe}: {self._variant_types[symtype]['whyml_name']})"
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
        # arity2.md (2b — operation selection): array locals that the
        # declaration path types correctly (via `_collect_array_var_assigns`'
        # call/transitive arm) but that the per-operation `is_array` sites must
        # ALSO recognise — chiefly inliner-introduced `ref (array int)` temps.
        # Consulted ONLY at operation sites (subscript read/write, `len`); never
        # at declaration/assign emission, so it cannot perturb the `ref`-vs-`let`
        # binding of existing array locals (that perturbation is what made the
        # blunt `_array_locals |= …` approach regress array-return locals).
        self._inline_array_temps: set = set()
        # 07-0903 W1: locals bound to a list/array of tuples (`a = [(x,y), …]`) → arity,
        # so `a[i][k]` destructures the element tuple rather than being read as a 2-D matrix.
        self._tuple_array_locals: Dict[str, int] = {}
        # 07-1705-rev4 P3/P5: list locals AND params modelled as a growable
        # `ref (seq int)` (the seq-promotion analysis, Module5 `seq_promoted_vars`).
        # Declared with `ref`, so reads deref (`!a`) and use qualified `Seq.*` ops;
        # concat rebinds the ref. P5: a seq-promoted PARAM is shadowed at function entry
        # with `let a = ref (snapshot a) in` (the array param → seq ref), then behaves
        # like a seq local; a `return a` materialises back to `array int` (P4).
        self._seq_locals: set = set(func.get("seq_promoted_vars", []))
        # str-list-elements: per-seq-var WhyML element type (only "string" is recorded;
        # absence ⇒ the default `seq int`/`array int`, byte-identical). Drives
        # `seq string` declaration, `Seq.snoc`/`Seq.get` string elements, the
        # string materialize bridge, the `Return_seq_str` payload, and the
        # `array string` return type.
        self._seq_value_types: Dict[str, str] = func.get("seq_value_types", {})
        self._dict_locals = set()
        # no-more-int-3 A1: dict var -> WhyML value type ν (string) for
        # string-valued dicts; consulted by the dict literal / declaration /
        # MapGet-default / MapSet sites to emit `map int (option string)`.
        self._dict_value_types: Dict[str, str] = func.get("dict_value_types", {})
        # no-more-int-3 A1 T1.2: dict var -> WhyML key type κ (string).
        self._dict_key_types: Dict[str, str] = func.get("dict_key_types", {})
        self._lambda_locals = set()
        self._record_locals = set()
        # no-more-int-2 Track 3: a bare class-typed parameter reconstructed as a record
        # (param name → whyml record type), so `p.field` is a direct read, not opaque getattr.
        self._record_param_classes: Dict[str, str] = {}
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
        # 07-1839 P3: definite-assignment sets for `\in_scope` (three-valued).
        self._scope_params, self._scope_must, self._scope_all = self._compute_scope_sets(func)
        # 07-1839 P5a/decision C: a dynamic `exec` can inject arbitrary names, so it havocs
        # the binding set → withhold the `\in_scope` decided-false direction downstream.
        self._scope_dyn_exec: bool = (bool(func.get("has_dynamic_exec", False))
                                      or self._has_dynamic_exec(func))
        return local_refs, ghost_vars

    def _has_dynamic_exec(self, func: Dict[str, Any]) -> bool:
        """07-1839 P5a: does the body contain an `exec(...)` call? `exec` is the one parser-
        family member that can BIND names in the caller's scope, so its presence havocs
        `\\in_scope` (decision C). (`eval`/`compile`/`ast.parse` return values and do not
        inject names — they don't havoc scope; their unknown *result* is handled separately.)
        Constant-source splicing is P5b; until then any `exec` is treated conservatively."""
        found = False
        stack = [func.get("body", [])]
        while stack and not found:
            node = stack.pop()
            if isinstance(node, dict):
                if node.get("type") == "Call" and node.get("func") == "exec":
                    found = True
                else:
                    stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
        return found

    def _compute_scope_sets(self, func: Dict[str, Any]):
        """07-1839 P3: (params, must-assigned, all-assigned) for `\\in_scope`.
        `must` = params ∪ top-level assignments that precede ANY control flow / return
        (assigned on all paths to function end); `all` = every assignment target anywhere
        (recursive). decided-true ⇐ must; decided-false ⇐ not in (params ∪ all); else unknown."""
        params = set(func.get("formal_params", []) or [])
        body = func.get("body", []) or []
        # Statement IR uses the key "stmt" for the statement kind (expressions use "type").
        control = {"If", "While", "For", "Try", "Return", "Raise", "Match", "With"}
        must = set(params)
        for st in body:
            if not isinstance(st, dict):
                continue
            if st.get("stmt") in control:
                break  # past this point assignment is no longer guaranteed on all paths
            if st.get("stmt") in ("Assign", "AugAssign") and isinstance(st.get("target"), str):
                must.add(st["target"])
        alla: Set[str] = set()
        self._collect_assign_targets(body, alla)
        return params, must, alla

    def _collect_assign_targets(self, node: Any, acc: Set[str]) -> None:
        """Recursively gather Assign/AugAssign simple-name targets anywhere in a stmt subtree."""
        if isinstance(node, dict):
            if node.get("stmt") in ("Assign", "AugAssign") and isinstance(node.get("target"), str):
                acc.add(node["target"])
            for v in node.values():
                self._collect_assign_targets(v, acc)
        elif isinstance(node, list):
            for v in node:
                self._collect_assign_targets(v, acc)

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
            # 07-0647-spec S1.1: reserved-word-safe self type name (matches the
            # `whyml_name` stored for the record/variant), so a class named e.g.
            # `Match` resolves to `py_match` consistently at type and field sites.
            self._current_self_type = whyml_ident(func["self_type"].lower())
            param_parts = [f"(self: {self._current_self_type})"]
            # Part B move 1: route each non-local/non-ghost symbol-table entry
            # through the single `_param_type_str` resolver. The method and
            # standalone paths previously carried parallel set/str/float/record/
            # variant dispatch ladders (the sum-type `variant` branch had to be
            # added to one but not the other — the duplication this consolidates).
            # Methods take no positional ref params, so pass an empty ref set;
            # bytes/bytearray reach `array int` via the `\valid`/array1d_params
            # path, so the old method-only bytes/bytearray symtype shortcut
            # (unused across the corpus) folds away.
            for arg in symbol_table:
                if arg in local_refs or arg in ghost_vars:
                    continue
                param_parts.append(
                    self._param_type_str(arg, set(), array2d_params,
                                         array1d_params, symbol_table, int_type))
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

    def _emit_narrowing_vc(self, name: str, args_str: str, return_type: str,
                           defc: Dict[str, Any], iface: Dict[str, Any],
                           spec_refs: Set[str]) -> List[str]:
        """b-spec §4 / b-impl §4 — the NARROWING VC: emit Why3 `goal`s proving the interface is a
        sound WEAKENING of the definition (interface ⊑ definition). Emitted only in the owning unit
        (where the function is a real `let`, so the definition is established by the body). Fail-loud:
        an interface that claims MORE than the definition proves makes the goal unprovable → rejected.

        ensures:  forall params result. def_requires -> def_ensures -> iface_ensures  (interface ⊑)
        requires: forall params. iface_requires -> def_requires                       (iface_pre ⟹ def_pre)

        `\\result` in the clauses is bound by aliasing it to a fresh `_res` quantified at the goal."""
        lines: List[str] = []
        self._in_spec = True
        prev_alias = getattr(self, "_result_alias", None)
        self._result_alias = "_res"

        def conj(exprs: List[Any]) -> str:
            parts = [self._expr_to_whyml(e, spec_refs) for e in (exprs or [])]
            return " /\\ ".join(f"({p})" for p in parts) if parts else "true"

        # Why3's `forall` wants the COMMA binder form (`a: int, r: t.`), not the parenthesised
        # `(a: int) (r: t)` of a function signature — convert args_str by splitting on `) (`.
        s = args_str.strip()
        if s.startswith("(") and s.endswith(")"):
            s = s[1:-1]
        groups = [g.strip() for g in s.split(") (")] if s else []
        ens_binder = ", ".join(groups + [f"_res: {return_type}"])
        def_req = conj(defc.get("requires", []))
        def_ens = conj(defc.get("ensures", []))

        # ensures direction — each INTERFACE ensures must follow from the definition.
        for k, ie in enumerate(iface.get("ensures", []) or []):
            ie_s = self._expr_to_whyml(ie, spec_refs)
            lines.append(f"  goal {name}__narrows_ens_{k} :")
            lines.append(f"    forall {ens_binder}. ({def_req}) -> ({def_ens}) -> ({ie_s})")

        # requires direction — the interface precondition must imply the definition's
        # (a caller establishing the interface pre satisfies the body's). Only when the
        # interface narrows requires; an absent interface requires inherits the definition (no VC).
        if iface.get("requires"):
            iface_req = conj(iface.get("requires", []))
            rbind = f"forall {', '.join(groups)}. " if groups else ""
            lines.append(f"  goal {name}__narrows_req :")
            lines.append(f"    {rbind}({iface_req}) -> ({def_req})")

        self._result_alias = prev_alias
        self._in_spec = False
        return lines

    def _returns_string_seq(self, body_stmts: List[Dict[str, Any]]) -> bool:
        """str-list-elements: does the function `return` a seq local that was inferred
        to carry STRING elements (`_seq_value_types[v] == "string"`)? Such a list is
        emitted as `array string` rather than the default `array int`."""
        svt = getattr(self, "_seq_value_types", {})
        if not svt:
            return False
        found = [False]

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Return":
                    v = node.get("value")
                    if (isinstance(v, dict) and v.get("type") == "Var"
                            and svt.get(v.get("name")) == "string"):
                        found[0] = True
                for x in node.values():
                    rec(x)
            elif isinstance(node, list):
                for x in node:
                    rec(x)

        rec(body_stmts)
        return found[0]

    def _first_tuple_return_elts(self, stmts: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """The element list of the FIRST `return (a, b, …)` (mirrors
        IRScanner.find_return_type's traversal so the per-slot types line up with
        the arity it computed). None if no tuple-valued return is found."""
        for stmt in stmts:
            if stmt.get("stmt") == "Return" and stmt.get("value"):
                val = stmt["value"]
                if isinstance(val, dict) and val.get("type") == "Tuple":
                    return val.get("elts", [])
            for key in ("body", "orelse"):
                if key in stmt:
                    r = self._first_tuple_return_elts(stmt[key])
                    if r is not None:
                        return r
            if stmt.get("stmt") == "Match":
                for c in stmt.get("cases", []):
                    r = self._first_tuple_return_elts(c.get("body", []))
                    if r is not None:
                        return r
        return None

    def _infer_tuple_slot_type(self, elt: Dict[str, Any], array_vars: Set[str],
                               dict_vars: Set[str], symtab: Dict[str, Any]) -> str:
        """The WhyML type of ONE tuple-return slot, refining the homogeneous
        `int` default. Mirrors the value-type recognition in
        `find_array_and_dict_vars` (the array/dict producers) so a slot bound to a
        `bytes(...)`/list/slice is typed `array int`, a dict `map int (option int)`,
        a str `string`, a float `real`. Anything else stays `int`."""
        if not isinstance(elt, dict):
            return "int"
        t = elt.get("type")
        if t == "Var":
            nm = elt.get("name")
            if nm in array_vars:
                return "array int"
            if nm in dict_vars:
                return "map int (option int)"
            st = symtab.get(nm)
            if st in ("list", "bytes", "bytearray"):
                return "array int"
            if st in ("set", "dict", "frozenset"):
                return "map int (option int)"
            if st == "str":
                return "string"
            if st == "float":
                return "real"
            return "int"
        if t in ("ListLit", "ArrayLit", "ListComp", "SliceAccess"):
            return "array int"
        if t in ("DictLit", "SetLit"):
            return "map int (option int)"
        if t == "String":
            return "string"
        if t == "Call":
            fn = (elt.get("func") or "")
            base = fn.rsplit(".", 1)[-1]
            if fn in ("list", "sorted", "bytes", "bytearray"):
                return "array int"
            if base in ("encode", "ljust", "rjust", "zfill"):
                return "array int"
            if fn in ("dict", "defaultdict", "Counter", "OrderedDict", "set", "frozenset"):
                return "map int (option int)"
        return "int"

    def _refine_tuple_return_type(self, func: Dict[str, Any],
                                  body_stmts: List[Dict[str, Any]], return_type: str) -> str:
        """Refine a homogeneous `(int, int, …)` tuple return type into per-slot
        types (e.g. `(int, array int)` for `_unpack_direntry`'s `(inode, name_bytes)`).
        find_return_type defaults every slot to `int`; here each slot is typed from
        the FIRST tuple return's element expressions. Without this, a tuple with an
        `array int`/`string`/`map` slot emits a `let` body that cannot type-check
        against the wrong `int` slot — the standalone-gate line-441 blocker."""
        if not (return_type.startswith("(") and "," in return_type):
            return return_type
        elts = self._first_tuple_return_elts(body_stmts)
        if not elts:
            return return_type
        array_vars, dict_vars = IRScanner.find_array_and_dict_vars(body_stmts)
        array_vars |= self._collect_array_var_assigns(body_stmts)
        symtab = func.get("symbol_table", {}) or {}
        slots = [self._infer_tuple_slot_type(e, array_vars, dict_vars, symtab) for e in elts]
        if len(slots) == return_type.count(",") + 1 and any(s != "int" for s in slots):
            return "(" + ", ".join(slots) + ")"
        return return_type

    def _compute_return_type(self, func: Dict[str, Any], body_stmts: List[Dict[str, Any]]) -> str:
        """Compute the WhyML return type for one function, applying the
        `List[T] → array int`, `Set[T]`/`Dict[K, V]` → `map int (option int)`,
        and bounded-int overrides."""
        bounded_int = func.get("bounded_int")
        return_type = IRScanner.find_return_type(body_stmts)
        return_type = self._refine_tuple_return_type(func, body_stmts, return_type)
        ann = func.get("return_annotation")
        if ann in ("list", "bytes", "bytearray") and return_type == "int":
            # 0442.md B2 (no-more-int): bytes/bytearray are the byte-buffer array class.
            return_type = "array int"
            # str-list-elements: a list whose returned seq local carries STRING elements
            # is `array string` (its elements stay string end-to-end, so a consumer's
            # `names[i]` is a `string` feeding a string-typed callee like sys_stat).
            if self._returns_string_seq(body_stmts):
                return_type = "array string"
        elif ann in ("set", "dict", "frozenset") and return_type == "int":
            return_type = "map int (option int)"
        elif ann == "str" and return_type == "int":
            return_type = "string"
        elif ann == "float" and return_type == "int":
            return_type = "real"  # no-more-int Stage D
        elif ann in getattr(self, "_variant_types", {}) and return_type == "int":
            # A4/A5: a `#@ datatype` return annotation (`-> Json`, `-> Option`)
            # resolves to the variant's Why3 type — params already did (§_param_type_str).
            return_type = self._variant_types[ann]["whyml_name"]
        elif ann in getattr(self, "_record_types", {}) and return_type == "int":
            return_type = self._record_types[ann]["whyml_name"]
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
        # lemma.md: a `#@ lemma` is a `-> None` proof function — its WhyML result is
        # `unit` (it computes nothing; the body is the proof).
        if func.get("lemma"):
            return_type = "unit"
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
        func_lemma = func.get("lemma", False)
        is_recursive = IRScanner.is_recursive(name, body_stmts)
        use_rec = bool(func_variants) or is_recursive
        # A lemma is `assigns \nothing` so the purity heuristic flags it pure, but it
        # must NOT emit as a `let function` (a term) — it is a `let [rec] lemma` whose
        # body is a proof. Exclude it from the logic path. `emits_as_logic_symbol`
        # (scc.py) is the SHARED classifier the SCC contract-edge collector also uses,
        # so the dependency graph and the emission agree on "is this a logic symbol";
        # the emitter alone adds the emission-time `not local_refs` term.
        can_emit_as_logic = emits_as_logic_symbol(func) and not local_refs

        _scc_idx, _pos_in_scc, _scc_size = scc_info.get(func["name"], (0, 0, 1))
        # A non-first member of a multi-function SCC is a mutual-recursion
        # continuation, chained to the group's opening `let rec [function]`.
        _mutual_cont = _pos_in_scc > 0 and _scc_size > 1 and not emit_as_val
        is_and_clause = _mutual_cont and not can_emit_as_logic

        lines: List[str] = []
        if emit_as_val:
            kw = f"val {name}"
        elif func_lemma:
            # lemma.md: `let lemma` (non-recursive) / `let rec lemma` (recursive or
            # in a mutual SCC). Why3 verifies the body, then exposes the contract as
            # a usable fact `forall params. requires -> ensures`.
            kw = f"{'let rec lemma' if (use_rec or _scc_size > 1) else 'let lemma'} {name}"
        elif _mutual_cont and can_emit_as_logic:
            # A5a-residual (functions): mutually-recursive PURE/logic functions
            # (`size_tree` ↔ `size_forest`) chain with WhyML's `with function`
            # continuation, so the forward call resolves within one `let rec`
            # group (the opening member emits `let rec function …`).
            kw = f"with function {name}"
        elif can_emit_as_logic:
            kw = f"{'let rec function' if (use_rec or _scc_size > 1) else 'let function'} {name}"
        elif is_and_clause:
            kw = f"and {name}"
        else:
            kw = f"{'let rec' if (use_rec or _scc_size > 1) else 'let'} {name}"
        lines.append(f"  {kw} {args_str} : {return_type}" if args_str
                     else f"  {kw} () : {return_type}")

        spec_refs = set() if is_method else ref_params
        func_exceptions = IRScanner.collect_escaping_exceptions(body_stmts)
        # b-spec Track B (P3): an imported/abstract `val` stub shows only the NARROW interface
        # contract. Per-kind: a specified interface clause REPLACES the definition's; an OMITTED kind
        # INHERITS the definition (so `#@ interface ensures \length==64` narrows ensures but keeps the
        # def's requires/assigns — sound, since the body still needs the def precondition). The
        # owning-unit `let` keeps the full definition (+ the narrowing VC below).
        _iface = func.get("interface") or {}
        if emit_as_val and _iface:
            _defc = func.get("contracts", {})
            contract_src = {
                "requires": _iface.get("requires") or _defc.get("requires", []),
                "ensures":  _iface.get("ensures")  or _defc.get("ensures", []),
                "assigns":  _iface.get("assigns")  or _defc.get("assigns", []),
                "raises":   _defc.get("raises", []),
                "no_exception": _defc.get("no_exception", []),
                "no_exception_all": _defc.get("no_exception_all", False),
            }
        else:
            contract_src = func.get("contracts", {})
        # 11-0632-spec-8 Part 2 (NARROW): flag that we are emitting a bodyless
        # `val`/trusted-stub contract, so the contract-position logic-symbol fallback
        # (`_emit_contract_logic_symbol`) fires ONLY here — never for a real `let`
        # function whose `ensures` references a symbol it ALSO program-calls in its body
        # (e.g. 0386's `external_helper`, which must keep its program `val` + strict
        # assert). A trusted stub has no body, so a contract-only unknown symbol there is
        # necessarily a logic predicate (the gap-7 `present` shape).
        self._emitting_val_contract = emit_as_val
        lines += self._emit_contracts(contract_src, spec_refs,
                                      func_variants, func_diverges, func_exceptions)
        self._emitting_val_contract = False

        if emit_as_val:
            lines.append("")
            return lines

        lines.append("  =")
        lines.append(self._emit_body_code(func, body_stmts, local_refs, ghost_vars,
                                          ref_params, is_method, return_type))
        # b-spec §4 (P2): in the owning unit (real `let`), prove the interface is a sound weakening
        # of the definition. Fail-loud — an over-claiming interface makes the goal unprovable.
        if _iface:
            lines += self._emit_narrowing_vc(name, args_str, return_type,
                                             func.get("contracts", {}), _iface, spec_refs)
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
            # body-gate gap-3: refine a homogeneous `(int, int, …)` tuple into per-slot
            # types so this map (consulted by `_call_return_whyml_type` for unpack-target
            # typing) agrees with the emitted `let` signature — e.g. `_unpack_direntry`
            # is `(int, array int)`, so `inode, name_bytes = _unpack_direntry(...)` types
            # `name_bytes` as `array int`, not a `ref 0` int.
            ret = self._refine_tuple_return_type(func, func["body"], ret)
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

    def _build_method_field_result_ensures_map(
            self, functions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Map method name → its `ensures` clauses that reference `\\result`
        AND self-fields (`self.x`) only — no params, `\\old`, locals, or
        non-self objects. Clauses are kept VERBATIM (the `self.x` FieldGet is
        preserved); the call site lowers them by giving the abstract op an
        explicit leading receiver parameter `(self: <class>)` and passing the
        receiver record, so `self.x` binds to the actual instance.

        This is the third and last propagation map (no-more-int-3 A2c). It
        closes the method-call contract gap that 0522 documented: a getter
        `def get_x(self): #@ ensures \\result == self.x` whose postcondition
        relates `\\result` to a self-FIELD. `_build_method_result_ensures_map`
        (result+constants) and `_build_method_param_result_ensures_map`
        (result+params) both drop `FieldGet`, so without this map such a
        clause propagated nowhere and a `b.get_x()` call proved nothing.
        Param-referencing field clauses (`\\result == self.x + k`) are excluded
        — mixing a self-field with a param would collide the receiver param
        with the positional `x_i`; those stay unpropagated (documented gap)."""
        def classify(node: Any, params: Set[str]) -> Optional[bool]:
            # Returns False if the subtree references a DISALLOWED leaf
            # (param/old/local/non-self object); None/True otherwise. The
            # `saw_*` flags are accumulated by the caller via the recursion.
            if not isinstance(node, dict):
                return None
            t = node.get("type")
            if t in ("OldVar", "OldField"):
                return False
            if t in ("FieldGet", "Attribute"):
                # Only `self.<field>` is allowed; `other.f` / a chained
                # `self.a.b` (object is itself a dict) is rejected.
                if node.get("object") != "self":
                    return False
                return None
            if t == "Var":
                # Any bare Var (param or local) is disallowed — a pure
                # field/result clause names neither.
                return False
            if t == "ArrayLen":
                v = node.get("var")
                return None if v == "\\result" else False
            for val in node.values():
                for c in (val if isinstance(val, list) else [val]):
                    if classify(c, params) is False:
                        return False
            return None

        def saw(node: Any, kind: str) -> bool:
            if not isinstance(node, dict):
                return False
            t = node.get("type")
            if kind == "result" and (t == "Result"
                                     or (t == "ArrayLen" and node.get("var") == "\\result")):
                return True
            if kind == "field" and t in ("FieldGet", "Attribute") and node.get("object") == "self":
                return True
            for val in node.values():
                for c in (val if isinstance(val, list) else [val]):
                    if saw(c, kind):
                        return True
            return False

        out: Dict[str, List[Dict[str, Any]]] = {}
        for func in functions:
            params = set(func.get("formal_params", []) or [])
            kept = [e for e in (func.get("contracts", {}).get("ensures", []) or [])
                    if classify(e, params) is not False
                    and saw(e, "result") and saw(e, "field")]
            if kept:
                out[func["name"]] = kept
        return out

    def _build_method_field_param_result_ensures_map(
            self, functions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """gap-9 (A2c+): map method name → its `ensures` clauses that reference
        `\\result` AND a self-field (`self.x`) AND/OR a param — but NO `\\old`,
        locals, or non-self objects. The os syscalls' presence link
        `(\\result == 0) <==> (dir_lookup(self.disk, 5, pathname) >= 0)` mixes a
        self-field (`self.disk`) with a param (`pathname`), so it propagated
        through NONE of the three earlier maps (result-only / param / field-only,
        each of which rejects the OTHER leaf kind — the documented A2c gap).

        Clauses are kept with the `self.x` FieldGet VERBATIM (the call site adds a
        leading `(self: <class>)` receiver param) and each formal-param Var
        renamed to `x_i` (the stub's positional params). `self` and `x_i` live in
        distinct namespaces, so there is no collision. Restricted to clauses that
        reference a self-field (otherwise the result/param maps already cover
        them) so existing files are byte-identical."""
        def classify(node: Any, params: Set[str]) -> Optional[bool]:
            # False if the subtree references a DISALLOWED leaf (\old, local, or
            # a non-self object field); None otherwise. A bare Var must be a
            # param (renamed later) — a non-param Var is a local → disallowed.
            if not isinstance(node, dict):
                return None
            t = node.get("type")
            if t in ("OldVar", "OldField"):
                return False
            if t in ("FieldGet", "Attribute"):
                if node.get("object") != "self":
                    return False
                return None
            if t == "Var":
                return None if node.get("name") in params else False
            if t == "ArrayLen":
                v = node.get("var")
                return None if (v == "\\result" or v in params) else False
            for val in node.values():
                for c in (val if isinstance(val, list) else [val]):
                    if classify(c, params) is False:
                        return False
            return None

        def saw(node: Any, kind: str, params: Set[str]) -> bool:
            if not isinstance(node, dict):
                return False
            t = node.get("type")
            if kind == "result" and (t == "Result"
                                     or (t == "ArrayLen" and node.get("var") == "\\result")):
                return True
            if kind == "field" and t in ("FieldGet", "Attribute") and node.get("object") == "self":
                return True
            for val in node.values():
                for c in (val if isinstance(val, list) else [val]):
                    if saw(c, kind, params):
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

        out: Dict[str, List[Dict[str, Any]]] = {}
        for func in functions:
            params = func.get("formal_params", []) or []
            if not params:
                continue
            pset = set(params)
            pmap = {p: f"x{i}" for i, p in enumerate(params)}
            # Require result + field + AT LEAST ONE param: a clause mixing all
            # three is the genuinely-new combination (`(\result==0) <==>
            # dir_lookup(self.disk, 5, pathname) >= 0`) that the result-only /
            # param / field-only maps all drop. A field+result clause WITHOUT a
            # param (`\result == self.x`) stays with `field_result_ensures`
            # (unchanged) — so existing files emit byte-identically.
            kept = [rename(e, pmap)
                    for e in (func.get("contracts", {}).get("ensures", []) or [])
                    if classify(e, pset) is not False
                    and saw(e, "result", pset) and saw(e, "field", pset)
                    and refs_param(e, pset)]
            if kept:
                out[func["name"]] = kept
        return out

    def _build_method_writes_map(self, functions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """gap7-spec-rev2 (O1/O2): map method name → the self-field names it `assigns`
        (`assigns self.x` → `["x"]`). Derived from the SAME `contracts.assigns` the method's
        `let` is verified against, so the abstract op's `writes {self.x}` cannot drift from the
        method's frame. Only `self.<field>` targets are collected (a non-self / `\nothing`
        assigns yields no writes — the call needs no `writes` clause)."""
        out: Dict[str, List[str]] = {}
        for func in functions:
            fields: List[str] = []
            for a in (func.get("contracts", {}).get("assigns", []) or []):
                if (isinstance(a, dict) and a.get("type") in ("FieldGet", "Attribute")
                        and a.get("object") == "self" and a.get("field")):
                    if a["field"] not in fields:
                        fields.append(a["field"])
            if fields:
                out[func["name"]] = fields
        return out

    def _build_method_field_old_ensures_map(
            self, functions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """gap7-spec-rev2: map method name → its `ensures` clauses that reference self-fields
        and/or `\\old(self.f)` (the MUTATING contract) but NO `\\result`, params, locals, or
        non-self objects. These are exactly the clauses the existing field-RESULT map drops
        (it rejects `OldVar`/`OldField`) — so a void mutating method (`inc`: `self.x ==
        \\old(self.x)+1`) propagated nowhere. The call site lowers them by giving the abstract
        op `(self: <class>)` + `writes {self.f}` and translating `\\old(self.f)` → `old self.f`.
        Excludes any clause that also references `\\result` (that's the non-void case — kept in
        the field-RESULT map) so each clause is filed by its kind (the rev2 partition)."""
        def classify(node: Any) -> Optional[bool]:
            # False if the subtree references a DISALLOWED leaf (param/local bare Var, \result,
            # or non-self object field); None otherwise (self-field / old-self-field / const).
            if not isinstance(node, dict):
                return None
            t = node.get("type")
            if t == "Result":
                return False
            if t in ("FieldGet", "Attribute", "OldField"):
                return False if node.get("object") != "self" else None
            if t == "OldVar":
                return False
            if t == "Var":
                return False
            if t == "ArrayLen":
                v = node.get("var")
                return None if (v == "self" or (isinstance(v, dict) and v.get("object") == "self")) else False
            for val in node.values():
                for c in (val if isinstance(val, list) else [val]):
                    if classify(c) is False:
                        return False
            return None

        def refs_self_field_or_old(node: Any) -> bool:
            if not isinstance(node, dict):
                return False
            if (node.get("type") in ("FieldGet", "Attribute", "OldField")
                    and node.get("object") == "self"):
                return True
            return any(refs_self_field_or_old(c)
                       for val in node.values()
                       for c in (val if isinstance(val, list) else [val]))

        out: Dict[str, List[Dict[str, Any]]] = {}
        for func in functions:
            kept = [e for e in (func.get("contracts", {}).get("ensures", []) or [])
                    if classify(e) is not False and refs_self_field_or_old(e)]
            if kept:
                out[func["name"]] = kept
        return out

    def _build_method_field_param_post_ensures_map(
            self, functions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Map method name → its NON-QUANTIFIED `ensures` clauses that reference a self-field
        AND a param but NO `\\result`, `\\old`, quantifier, local, or non-self object — each
        formal param renamed to `x_i`. These are the void-mutator WRITE POSTCONDITIONS
        (`slot_inode(self.disk, b, s) == inode`, `slot_name(self.disk, b, s) == name`,
        `slot_inode(self.disk, b, s) == 0`) that every existing map drops: `field_old` rejects
        params, `field_param_result` requires `\\result`. So a `#@ no_inline` mutator's boundary
        stub carried only `writes`, and a caller (mkdir/link/symlink: presence witness;
        unlink/rmdir: the just-zeroed slot) could prove nothing about what the call WROTE.

        Restricted to NON-QUANTIFIED clauses ON PURPOSE (plan §2.9): a non-quantified equality
        carries no trigger, so it CANNOT E-match-poison sibling goals (the failure mode that
        sank the quantified-frame attempt). The quantified FRAME (`\\forall k. … == \\old`) is a
        separate, opt-in concern handled elsewhere. Reuses the param-rename of the field+param
        +result map; rejects `\\old` and any quantifier so only the safe write-posts survive."""
        def classify(node: Any, params: Set[str]) -> Optional[bool]:
            if not isinstance(node, dict):
                return None
            t = node.get("type")
            if t in ("Result", "OldVar", "OldField", "Old",
                     "Forall", "Exists", "ForallItems"):
                return False
            if t in ("FieldGet", "Attribute"):
                return False if node.get("object") != "self" else None
            if t == "Subscript":
                _v = node.get("value", {})
                if isinstance(_v, dict) and _v.get("type") == "Var":
                    return False
            if t == "Var":
                return None if node.get("name") in params else False
            if t == "ArrayLen":
                v = node.get("var")
                if isinstance(v, dict):
                    return None if v.get("object") == "self" else False
                return None if (v == "self" or v in params) else False
            for k, val in node.items():
                if k == "type":
                    continue
                for c in (val if isinstance(val, list) else [val]):
                    if classify(c, params) is False:
                        return False
            return None

        def saw_field(node: Any) -> bool:
            if not isinstance(node, dict):
                return False
            if node.get("type") in ("FieldGet", "Attribute") and node.get("object") == "self":
                return True
            return any(saw_field(c) for val in node.values()
                       for c in (val if isinstance(val, list) else [val]))

        def refs_param(node: Any, params: Set[str]) -> bool:
            if not isinstance(node, dict):
                return False
            if node.get("type") == "Var" and node.get("name") in params:
                return True
            return any(refs_param(c, params) for val in node.values()
                       for c in (val if isinstance(val, list) else [val]))

        def rename(node: Any, pmap: Dict[str, str]) -> Any:
            if not isinstance(node, dict):
                return node
            if node.get("type") == "Var" and node.get("name") in pmap:
                return {"type": "Var", "name": pmap[node["name"]]}
            new: Dict[str, Any] = {}
            for k, v in node.items():
                if isinstance(v, list):
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
                    if classify(e, pset) is not False
                    and saw_field(e) and refs_param(e, pset)]
            if kept:
                out[func["name"]] = kept
        return out

    @staticmethod
    def _symtype_to_whyml(symtype: Optional[str]) -> str:
        """Convert a Module5 symbol-table type tag to the WhyML type used
        in abstract val parameter declarations. Defaults to `int`."""
        if symtype in ("set", "dict", "frozenset"):
            return "map int (option int)"
        if symtype in ("list", "tuple", "bytes", "bytearray"):
            # 0442.md B2 (no-more-int): bytes/bytearray are the byte-buffer array class.
            return "array int"
        if symtype == "str":
            return "string"
        if symtype == "float":
            return "real"  # no-more-int Stage D
        return "int"

    @staticmethod
    def _parse_mixin_sig(sig: str):
        """Parse a declared method signature `(self, x: int, y: str) -> int` into
        (params, return_type) where params is an ordered list of (name, py_type)
        excluding `self` and return_type is a Python type name (default 'int')."""
        params: List[tuple] = []
        ret = "int"
        s = (sig or "").strip()
        if "->" in s:
            lhs, rhs = s.rsplit("->", 1)
            ret = rhs.strip() or "int"
        else:
            lhs = s
        lhs = lhs.strip()
        if lhs.startswith("(") and lhs.endswith(")"):
            lhs = lhs[1:-1]
        for part in [p.strip() for p in lhs.split(",") if p.strip()]:
            if part == "self":
                continue
            if ":" in part:
                nm, ty = part.split(":", 1)
                params.append((nm.strip(), ty.strip()))
            else:
                params.append((part, "int"))
        return params, ret

    def _mixin_dep_pseudo_functions(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesize one pseudo-function per declared `depends_method`/
        `requires_method` (S1, verify-once). Each is keyed `<class>__<dep>` — the
        same shape `_resolve_dotted_signature` looks up for a `self.<dep>(…)` call —
        and carries the DECLARED interface's return type, params, and contract, so
        the existing contract-propagation maps attach the dependency's `ensures` to
        the abstract call. These never enter the emission list; they only populate
        the lookup maps. Non-mixin modules yield [] (no behavioural change)."""
        real_names = {f.get("name") for f in functions}
        pseudo: List[Dict[str, Any]] = []
        for func in functions:
            deps = func.get("method_deps") or []
            if not deps:
                continue
            name = func.get("name", "")
            cls = name.split("__")[0] if "__" in name else ""
            for dep in deps:
                params, ret = self._parse_mixin_sig(dep.get("sig", ""))
                key = f"{cls}__{dep['method']}" if cls else dep["method"]
                # Composition (S2): when the dependency has a REAL provider flattened
                # into this class (`<cls>__<dep>` exists), use that concrete contract,
                # not the abstract declared interface — skip the pseudo-func so it
                # doesn't shadow the real provider in the propagation maps.
                if key in real_names:
                    continue
                # Python-type symbol table (self excluded); `_symtype_to_whyml` and the
                # return-type map convert these exactly as for a real method.
                symtable = {nm: ty for nm, ty in params}
                pseudo.append({
                    "name": key,
                    "symbol_table": symtable,
                    "body": [],
                    "formal_params": [nm for nm, _ in params],
                    "return_annotation": ret if ret in ("list", "set", "dict", "frozenset") else None,
                    # WhyML return type from the declared sig — the empty body would
                    # otherwise derive `unit`; the transpiler overrides the return-type
                    # map with this (Module6_WhyMLTranspiler.transpile).
                    "_mixin_ret_whyml": self._symtype_to_whyml(ret),
                    "contracts": {
                        "requires": dep.get("requires", []),
                        "ensures": dep.get("ensures", []),
                        "assigns": [], "raises": [],
                        "no_exception": [], "no_exception_all": False,
                    },
                })
        return pseudo

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

    def _build_method_param_whyml_types_by_name(
            self, functions: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
        """10-1732-gap (Gaps 2/3 shared infra): map function name →
        {formal-param-name → WhyML param type}. Keyed by NAME (not position)
        so a call-site default-fill can lower an omitted/`None` default at the
        omitted parameter's faithful type (Gap 3). Derived from the same IR
        source as the sibling `_module_method_*` tables (the function's
        `formal_params` order + `symbol_table` py-type tags). Sorted by the
        declared formal-param order — deterministic."""
        result: Dict[str, Dict[str, str]] = {}
        for func in functions:
            symtable = func.get("symbol_table", {})
            by_name: Dict[str, str] = {}
            for pname in func.get("formal_params", []):
                by_name[pname] = self._symtype_to_whyml(symtable.get(pname))
            result[func["name"]] = by_name
        return result

    def _build_method_return_annotation_map(
            self, functions: List[Dict[str, Any]]) -> Dict[str, str]:
        """10-1732-gap (Gap 2 shared infra): map function name → the callee's
        Python `return_annotation` (e.g. `"str"`, `"int"`). Used by
        `_is_string_expr` to detect that `len(<call>)` wraps a str-returning
        call so it routes to `str_length_op` rather than the opaque
        `iter_length`. Separate from `_module_method_return_types` (a WhyML-type
        map consumed by the dotted-call abstraction) to keep that map's byte
        output unchanged."""
        result: Dict[str, str] = {}
        for func in functions:
            ann = func.get("return_annotation")
            if ann:
                result[func["name"]] = ann
        return result

