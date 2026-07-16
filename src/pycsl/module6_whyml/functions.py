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
        # compound-key const-map getter: the key parameter takes the native tuple key
        # type (`(string, option string)`) so `Map.get NAME k` type-checks. Gated on
        # the recognized getter → never fires for a corpus param (byte-identical).
        _ck = getattr(self, "_compound_key_params", {})
        if arg in _ck:
            return f"({safe}: {_ck[arg]})"
        if arg in ref_params:
            return f"({safe}: ref {int_type})"
        if arg in array2d_params:
            return f"({safe}: matrix {int_type})"
        symtype = symbol_table.get(arg)
        # typing-engagement ty3 / 34-1700-typing-spec-10: a `Callable[[A1, ...],
        # R]`-typed parameter (C1) lowers to a curried WhyML function-type
        # parameter `<w1> -> ... -> <wr>`. The call site `f(a1, ..., an)`
        # already lowers to WhyML application `(f a1 ... an)`; Why3's own
        # typecheck discharges the arg-type match (C2) and the result type
        # (C3). Triggers ONLY when symtype starts with "callable:" →
        # byte-identical for every non-Callable driver.
        if isinstance(symtype, str) and symtype.startswith("callable:"):
            return f"({safe}: {self._callable_whyml_arrow(symtype)})"
        # `Set[T]` / `Dict[K, V]` / `FrozenSet[T]` parameters are
        # modelled as `map int (option int)` (parallel to body-level
        # dicts). Must come before the `list` branch since dict/set
        # share the map model, not the array model.
        # no-more-int-3 A1 T1.2 (param-form): a `Dict[str, ...]`-typed
        # parameter is a real `map string (option ν)`, NOT a fixed
        # `map int (option int)` — the body subscript/.get path passes
        # string keys through unhashed (κ=string), so the parameter
        # type MUST agree or Why3 rejects with "expected int, got
        # string". The value type ν (`Dict[_, str]`/`Dict[_, List[int]]`/
        # nested `Dict[_, Dict[int, int]]`) is threaded here too so a
        # string/seq/nested-map-valued dict parameter matches its body
        # reads. Byte-identical to the legacy `map int (option int)`
        # for every int-keyed/int-valued dict (no `dict_key_types` /
        # `dict_value_types` entry → the legacy default fires).
        # wrong-lowering-to-fix.md §WL-05b: an inner-mutated dict/set param is a
        # MUTABLE `ref (map …)` with a `writes {arg}` frame (caller-visible), so item
        # writes escape. A read-only param keeps the by-value `map …` (byte-identical).
        _mut_coll = arg in getattr(self, "_mutated_collection_params", set())
        if symtype == "dict":
            kt = getattr(self, "_dict_key_types", {}) or {}
            vt = getattr(self, "_dict_value_types", {}) or {}
            _mt = self._dict_param_whyml_type(arg, kt, vt)
            if _mut_coll:
                return f"({safe}: ref ({_mt}))"
            return f"({safe}: {_mt})"
        if symtype in ("set", "frozenset"):
            if _mut_coll:
                return f"({safe}: ref (map int (option int)))"
            return f"({safe}: map int (option int))"
        if arg in array1d_params or symtype in ("list", "bytes", "bytearray"):
            # 0442.md B2 (no-more-int): bytes/bytearray are the byte-buffer array class.
            if self._value_semantic:
                # nested-list.md S2: a `List[<container>]` param is `array (seq τ)` /
                # `array (map κ (option ν))` — the inner collection is a PURE Why3 type
                # (Why3 forbids a mutable element inside `array`; see the Gate-B spike).
                # Flat lists have no entry → `array int`, byte-identical.
                _ne = getattr(self, "_list_nested_elem", {}).get(arg)
                if _ne is not None:
                    return f"({safe}: array ({_ne}))"
                # WL-04: a FLAT `List[str]`/`List[float]` param is `array string`/
                # `array real` (the faithful non-int element), so `a[i]` reads the
                # faithful element type (`Array.get` is element-polymorphic; the
                # `is_array` subscript path is unchanged). A flat `List[int]`/
                # `List[bool]` has no entry → `array int`, byte-identical.
                _fe = getattr(self, "_param_list_flat_elem", {}).get(arg)
                if _fe is not None:
                    # WL-04b (record residual): a flat `List[<record>]` param — the
                    # element name resolves to a declared record — is `array <record>`,
                    # so `a[i]` reads a real record and `a[i].field` projects the
                    # faithful field. Register the param → element record whyml name so
                    # `_handle_attribute_expr` lowers `a[i].field` natively. Why3 forbids
                    # a mutable element inside `array`, so the element record is emitted
                    # PURE (Module5's `list_element_record_types` drives the preamble).
                    if _fe in self._record_types:
                        _wn = self._record_types[_fe]["whyml_name"]
                        self._record_array_params[arg] = _wn
                        return f"({safe}: array {_wn})"
                    return f"({safe}: array {_fe})"
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
            # directly. WL-05d (wrong-lowering-to-fix.md §WL-05d): a field STORE `p.field = v`
            # on a MUTABLE record param is now FAITHFUL and caller-visible — it lowers to the
            # native `p.field <- v` (Why3 infers the `writes {p.field}` frame). Only a record
            # pinned PURE because it is a `List[<record>]` element cannot be field-mutated
            # (immutable element) → that store fails closed (Module5/`_handle_fieldassign_stmt`).
            wn = self._record_types[symtype]["whyml_name"]
            self._record_locals.add(arg)
            self._record_param_classes[arg] = wn
            return f"({safe}: {wn})"
        # option-of-record projection (boundary-1 G1 extension): Module5 lowers an
        # `Optional[<record>]` param to the symtype `"option:<R>"` — render it as the
        # native `option <record>` and register the param → record whyml-name so a
        # None-guarded `p.get("k")` projects the field from the Some arm
        # (`_option_record_get_field`). A bare `is None` on `p` compares against the
        # option `None`. Byte-safe: no corpus param annotates `Optional[<record>]`.
        if isinstance(symtype, str) and symtype.startswith("option:"):
            _rname = symtype[len("option:"):]
            _rt = self._record_types.get(_rname)
            if _rt is not None:
                _wn = _rt["whyml_name"]
                self._option_record_param_classes[arg] = _wn
                return f"({safe}: option {_wn})"
            # Unknown record — fall through to the int collapse (never fires for a
            # declared record; keeps the branch total).
        if symtype in self._variant_types:
            # sum-types: a `#@ datatype`-typed param is its Why3 variant type.
            return f"({safe}: {self._variant_types[symtype]['whyml_name']})"
        # self-tcb-reduction T1.a: an IR-node-typed param (`node: "ExprIR"`) is `emit_ir` (the
        # signature counterpart of `_symtype_to_whyml`), so the `_handle_*_expr` handlers reflect
        # on it. Byte-safe: no corpus method annotates a param with the IR-node base names.
        if symtype in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR", "exprir"):
            return f"({safe}: emit_ir)"
        return f"({safe}: {int_type})"

    def _callable_whyml_arrow(self, symtype: str) -> str:
        """Render a `"callable:<a1>,...-><r>"` tag (typing-engagement ty3 /
        34-1700-typing-spec-10) as a curried WhyML function-arrow type
        `<w1> -> <w2> -> ... -> <wr>`.

        Each PyCSL tag maps to its WhyML type: `int`/`bool`→`int` (PyCSL
        int-encodes bool), `str`→`string`, `float`→`real`, a record/variant
        class name→its WhyML name (resolved against `_record_types`/
        `_variant_types`). A tag that resolves to None (an unknown class name
        in this delivery) falls back to `int` — Why3 then rejects the
        application if the arg type disagrees, which is sound (never weaker
        than S1)."""
        body = symtype[len("callable:"):]
        arg_part, _, ret_part = body.partition("->")
        arg_tags = [t for t in arg_part.split(",") if t]
        whyml_args = [self._callable_tag_to_whyml(t) for t in arg_tags]
        whyml_ret = self._callable_tag_to_whyml(ret_part)
        parts = whyml_args + [whyml_ret]
        return " -> ".join(parts)

    def _callable_tag_to_whyml(self, tag: str) -> str:
        """Map a single Callable arg/return PyCSL tag to its WhyML type."""
        if tag in ("int", "bool"):
            return "int"
        if tag == "str":
            return "string"
        if tag == "float":
            return "real"
        record_types = getattr(self, "_record_types", {})
        if tag in record_types:
            return record_types[tag]["whyml_name"]
        variant_types = getattr(self, "_variant_types", {})
        if tag in variant_types:
            return variant_types[tag]["whyml_name"]
        # Unknown bare name — sound fallback to `int`; Why3 rejects a mismatched
        # application rather than admitting an unsound type.
        return "int"

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
        # no-more-int emitter L4b: an imported/injected stub's symbol_table is
        # rebuilt with `Any` params (losing e.g. `name: str`). Restore the annotated
        # param types from the IR-preserved `param_annotations` (Module5), which
        # survives injection like `return_annotation`. Copy-on-write, and only fills
        # `Any`/missing — never overrides a resolved type — so it is byte-identical
        # whenever every param is already typed (the local case) or unannotated.
        _pann = func.get("param_annotations") or {}
        if _pann and any(symbol_table.get(k) in (None, "Any") for k in _pann):
            symbol_table = dict(symbol_table)
            for _k, _ty in _pann.items():
                if symbol_table.get(_k) in (None, "Any"):
                    symbol_table[_k] = _ty
        local_refs = IRScanner.find_assigned_vars(body_stmts)
        local_refs -= self._shared_var_names
        ghost_vars = IRScanner.find_ghost_vars(body_stmts)
        self._current_params = (
            (set(symbol_table.keys()) | local_refs | ghost_vars) - self._shared_var_names
        )
        # compound-key const-map getter: `return NAME.get(k, [])` where NAME is a
        # tuple-keyed const dict → the return type is `list <elem>` and the key param
        # `k` takes the native tuple key type. Recognized here so `_compute_return_type`
        # and `_param_type_str` (both called downstream in `_emit_function`) can consult
        # it. None for every other function → byte-identical.
        self._compound_map_getter = self._recognize_compound_map_getter(func, body_stmts)
        self._compound_key_params: Dict[str, str] = {}
        if self._compound_map_getter is not None:
            self._compound_key_params[self._compound_map_getter["key_param"]] = (
                self._compound_map_getter["key_whyml"])
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
        # nested-list.md S2: a `List[<container>]` param -> the outer list's WhyML
        # element type (`seq ..`/`map ..`). Drives the `array (seq τ)` param type and
        # the nested read `a[i][j]` (Seq.get / Map.get). Empty for flat lists.
        self._list_nested_elem: Dict[str, str] = func.get("param_list_nested_elem", {})
        # WL-04 (wrong-lowering-to-fix.md §WL-04): a FLAT `List[str]`/`List[float]`
        # param -> its faithful WhyML element type ("string"/"real"). Drives the
        # `array string`/`array real` param type in `_param_type_str`, so a
        # use-site read `a[i]` reads the faithful element (matching a str/float
        # return) instead of the collapsed `array int`. Empty for flat int lists
        # and nested lists → byte-identical.
        self._param_list_flat_elem: Dict[str, str] = func.get("param_list_flat_elem", {})
        self._dict_locals = set()
        # todict-reflection-plan.md R1: `d = node.to_dict()` binds `d` as an ALIAS of
        # the typed node (map target → the receiver dotted-name string). A later
        # `d.get(key)` routes to `node.<field>` (`_lower_dict_get_call`), dissolving
        # the IR-reflection into typed field access. Empty for every non-reflecting
        # function → byte-identical.
        self._todict_aliases: Dict[str, str] = {}
        # typed-ir-for-b-ceiling.md §26: `X = getattr(self, "<field>", {})` binds a
        # local aliasing a dict/set self-field (the emitter's `known_sizes =
        # getattr(self, "_known_collection_sizes", {})` / `st = getattr(self,
        # "_current_symbol_table", {})`). A later reference / `X[k]` / `k in X` /
        # `X.get(k)` routes to `self.<field>`. @mutable_state only → byte-identical.
        self._getattr_self_dict_aliases: Dict[str, str] = {}
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
        # option-of-record projection (boundary-1 G1 extension): an `Optional[<record>]`
        # param (Module5 symtype `"option:<R>"`) → the record's whyml name, so a
        # None-guarded `p.get("k")` projects the field from the `Some` arm
        # (`_option_record_get_field`) and `p is None` compares the option `None`.
        self._option_record_param_classes: Dict[str, str] = {}
        # WL-04b (wrong-lowering-to-fix.md §WL-04 record residual): a flat
        # `List[<record>]` param (or the loop target of a comprehension over one) →
        # the ELEMENT record's whyml name, so `a[i].field` lowers to a native record
        # projection `(a[i]).<label>` (not the opaque `get_field` collapse). Set by
        # `_param_type_str` (`array <record>`); consumed by `_handle_attribute_expr`
        # and the content-faithful comprehension.
        self._record_array_params: Dict[str, str] = {}
        # WL-04c (wrong-lowering-to-fix.md §WL-04 record LITERAL residual): a LOCAL
        # bound from a `List[<record>]` LITERAL of full-arity record CONSTRUCTORS
        # (`a = [Point(1, 2), Point(3, 4)]`) → the element record's whyml name, so
        # `a[i].field` lowers to a native record projection `(a[i]).<label>` (not the
        # opaque `get_field` collapse) — the local twin of `_record_array_params`.
        # Set by `_track_collection_metadata`; consumed by `_handle_attribute_expr`
        # and `_namedtuple_positional_access`.
        self._record_array_locals: Dict[str, str] = {}
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
        # wrong-lowering-to-fix.md §WL-05b (FAITHFUL caller-visible dict/set param
        # mutation): a STANDALONE function's dict/set PARAMETER that is ITEM-mutated in
        # the body (`d[k]=v`, `s.add/discard/remove(x)`) is modelled as a MUTABLE
        # `ref (map κ (option ν))` param with a `writes {d}` frame — so the mutation
        # escapes to the caller (Python passes dicts/sets BY REFERENCE), exactly as the
        # SMT-feasibility spike proves on Alt-Ergo + Z3
        # (test-suite/corpus/conformance/spikes/wl05b_param_mut_spike.mlw). USAGE-DRIVEN:
        # a READ-ONLY dict/set param keeps the by-value `map …` type (byte-identical);
        # only an inner-mutated one is promoted. The promoted params are ALSO added to
        # `_dict_locals` so every read/write site treats them like a local dict/set
        # (`!d` deref, `d := map_update_some !d k v`) — the uniform ref discipline that
        # the old inconsistent `d :=`/bare-`d` mix (the WL-05 bug) lacked. Methods are
        # out of scope here (their param types are ALSO mirrored into the abstract-op
        # call-contract map, which would drift) — a mutated dict/set method param keeps
        # the existing rejection / @mutable_state no-op.
        # §WL-05b: the module-level fixpoint map (built in Module6 setup) is the single
        # source of truth — it already excludes methods and folds in transitive param
        # forwarding. A `getattr` fallback keeps standalone/self-annotate reset paths
        # (where the map may not be built yet) at the empty default → byte-identical.
        self._mutated_collection_params: Set[str] = set(
            getattr(self, "_func_mutated_collection_params", {}).get(func.get("name"), set()))
        if self._mutated_collection_params:
            # Promote to the local-collection discipline (uniform `!d` reads / `d :=`
            # writes; also bypasses `_reject_param_collection_mutation`, which is gated
            # on `var not in _dict_locals`).
            self._dict_locals |= self._mutated_collection_params
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
            #
            # E0 param-extraction fix: iterate the UNPOLLUTED `_formal_params`
            # (source-ordered real parameters, `self` excluded) — NOT the
            # `symbol_table`, which Module4 also fills with for-loop tuple
            # targets and AnnAssign locals. Iterating `symbol_table` promoted
            # a `for i, ch in ...` loop target (`i`, `ch`) to method parameters,
            # AND skipping `local_refs` DROPPED a real param that the body
            # reassigns (e.g. `s = s.strip()`), yielding `unbound symbol 's'`.
            # This mirrors the standalone branch below: formal params stay in
            # the signature even when mutated — they are promoted to refs inside
            # `_emit_body_code` via `let X = ref X in` shadowing.
            for arg in self._formal_params:
                if arg in ghost_vars:
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
                         func_exceptions: Set[str],
                         func_is_noreturn: bool = False) -> List[str]:
        """Emit requires/ensures/assigns/variant/raises lines.
        Toggles self._in_spec around emission."""
        lines: List[str] = []
        self._in_spec = True

        requires_exprs = contracts.get("requires", [])
        ensures_exprs = contracts.get("ensures", [])

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
        # typing-engagement ty1 / 28-0000-typing-spec-4 §1.0 NR1: `-> NoReturn`
        # lowers to a `false` postcondition — the function never returns normally
        # (it raises or diverges). Emitted AFTER the user-written ensures (the
        # `false` postcondition is the NoReturn claim, additional to any explicit
        # contract). This is the SAME goal shape the non-vacuity gate INJECTS
        # (`ensures { [@expl:vacprobe] false }`); the gate EXEMPTS declared-
        # NoReturn functions (NR4) so this is the SPEC, not a vacuity signal.
        if func_is_noreturn:
            lines.append("    ensures { false }")
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
            from exception_model import handler_catches
            # `#@ raises OSError when COND` SUMMARISES the subclasses:
            # it covers a body `raise FileNotFoundError` under the same
            # condition. Why3 matches `raises {}` arms by exact tag, so a
            # declared base must be expanded into a conditioned arm for
            # every body-raised subclass it covers. The base tag itself is
            # still emitted (a literal `raise OSError`).
            declared_exc: set = set()
            covered_raw: set = set()  # raw raised names a declared arm covers
            for rc in raises_contracts:
                cond_str = self._expr_to_whyml(rc["condition"], spec_refs)
                base_raw = rc["exc_type"]
                base = safe_exc_name(base_raw)
                # Which raised exceptions are strict subclasses of this base
                # (modelled hierarchy)? Only relevant for hierarchy bases
                # like OSError; for a flat exception (ZeroDivisionError) this
                # is always empty.
                raised_subs = [r for r in sorted(func_exceptions)
                               if r != base_raw and handler_catches(base_raw, r)]
                # Emit the declared base arm UNLESS it is acting purely as a
                # SUMMARY: the base itself is not in the body's effect, yet
                # some subclass is. Why3 rejects `raises { OSError -> ... }`
                # when only FileNotFoundError is actually raised ("does not
                # raise exception OSError"), so in that case the base arm is
                # dropped and the subclass arms below carry the condition.
                # When the base has NO raised subclasses (the legacy flat
                # case, e.g. an implicit ZeroDivisionError trigger that is
                # not in func_exceptions), the declared arm is emitted as
                # before — preserving the pre-existing behaviour.
                summary_only = (base_raw not in func_exceptions) and bool(raised_subs)
                if not summary_only:
                    lines.append(f"    raises {{ {base} -> {cond_str} }}")
                    declared_exc.add(base)
                    covered_raw.add(base_raw)
                # conditioned arms for each subclass actually raised
                for raw in raised_subs:
                    sub = safe_exc_name(raw)
                    if sub not in declared_exc:
                        lines.append(f"    raises {{ {sub} -> {cond_str} }}")
                        declared_exc.add(sub)
                    covered_raw.add(raw)
            # Any raised exception NOT covered by a declared (base or
            # subclass) arm still needs an unconditioned `raises` arm.
            for raw in sorted(func_exceptions):
                if raw in covered_raw:
                    continue
                exc = safe_exc_name(raw)
                if exc not in declared_exc:
                    lines.append(f"    raises {{ {exc} }}")
                    declared_exc.add(exc)
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

    def _emit_union_arm_vc(self, name: str, symbol_table: Dict[str, Any]) -> List[str]:
        """typing-engagement ty1 / 25-1700-typing-spec-1 §2.2 — per-arm VCs for
        every parameter whose symbol-table entry is a synthesized `_union_*`
        variant. Emits:

          * C2 (arm membership / injection): `forall v: T_arm. exists (u:
            _union_N). u = Arm_i v` — proves the arm's payload type T_arm is
            injectable into the Union (non-vacuous: it constructs a witness).
          * C3 (reverse flow / projection): `forall (u: _union_N). match u with
            Arm_i v -> <v has type T_arm> | _ -> true end` — proves every arm
            projects to its declared payload type (non-vacuous: a wrong payload
            type makes the match ill-typed → Why3 rejects it).

        Both goals discharge via Why3 type-checking + the injection witness. A
        false-twin (an impossible postcondition injected via `bin/false-twin.py`)
        fails: the `exists` witness is the ONLY constructor that produces the
        arm, so an arm with a wrong type has no witness."""
        lines: List[str] = []
        variant_types = getattr(self, "_variant_types", {})
        seen_variants: Set[str] = set()
        for var, symtype in symbol_table.items():
            if not symtype or not symtype.startswith("_union_"):
                continue
            if symtype not in variant_types:
                continue
            if symtype in seen_variants:
                continue
            seen_variants.add(symtype)
            vinfo = variant_types[symtype]
            whyml_name = vinfo["whyml_name"]
            constructors = vinfo.get("constructors", {})
            for ctor_name, ctor in constructors.items():
                payload = ctor.get("payload", [])
                if not payload:
                    # Nullary constructor (Arm_None) — no injection/projection VC
                    # (it carries no value). C2/C3 are about arm *types*.
                    continue
                arm_tag = payload[0]
                arm_whyml = self._union_arm_whyml_type(arm_tag)
                safe_name = whyml_ident(name)
                gname_inj = f"{safe_name}__union_arm_{ctor_name}_inj"
                gname_proj = f"{safe_name}__union_arm_{ctor_name}_proj"
                # C2: injection — the arm type is assignable to the Union.
                lines.append(f"  goal {gname_inj} :")
                lines.append(f"    forall v: {arm_whyml}."
                             f" exists u: {whyml_name}. u = {ctor_name} v")
                # C3: projection — the Union arm projects back to the arm type.
                # A match that extracts the payload and asserts its identity.
                lines.append(f"  goal {gname_proj} :")
                lines.append(f"    forall u: {whyml_name}."
                             f" match u with"
                             f" | {ctor_name} v -> v = v"
                             f" | _ -> true"
                             f" end")
        return lines

    def _union_arm_whyml_type(self, tag: str) -> str:
        """Map a Union arm IR type tag to its WhyML type string."""
        m = {"int": "int", "bool": "int", "str": "string", "float": "real",
             "list": "array int", "bytes": "array int", "bytearray": "array int",
             "dict": "map int (option int)", "set": "map int (option int)",
             "frozenset": "map int (option int)", "tuple": "array int"}
        return m.get(tag, "int")

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
        # tuple-return-of-emit_ir feature: a slot that lowers to the `emit_ir` sum (an IR-node
        # sub-projection `expr["receiver"]`, an inline `{"type":K}` construction, an emit_ir local)
        # → `emit_ir`; a string-valued slot (a str attr projection / str local) → `string`. Checked
        # ahead of the DictLit→map / Var→int defaults. @mutable_state-gated → the corpus's
        # homogeneous-int tuples are unaffected.
        if getattr(self, "_mutable_state_classes", None):
            # string FIRST: a str-attr projection (`node.kind`/`.var`/`.op` → kind_of/name_of) is
            # `string`, but `_is_emit_ir_expr` over-claims any attr on an emit_ir node as a sub-node
            # — so the string check must precede it.
            if self._is_string_expr(elt) or (t == "Var" and elt.get("name") in getattr(
                    self, "_tuple_string_slot_locals", set())):
                return "string"
            if self._is_emit_ir_expr(elt) or (t == "Var" and elt.get("name") in getattr(
                    self, "_tuple_emit_ir_slot_locals", set())):
                return "emit_ir"
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
            # cf6.md M1.6: an emit_ir-typed slot (`_match_subject_union_info` returns
            # `(str, ExprIR)`) → `emit_ir`, so the union-info unpack types `uinfo` as a node.
            if st in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR"):
                return "emit_ir"
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
        # tuple-return-of-emit_ir: the emit_ir/string slot checks (`_is_emit_ir_expr` /
        # `_is_string_expr`) read `_current_symbol_table`/`_current_self_type`, which are NOT set
        # when this runs during return-type-MAP building (before per-function state). Set the
        # func's context (annotations merged, self_type from the `<class>__<method>` IR name) so a
        # tuple-of-(emit_ir,string) method's MAP entry matches its own emitted signature — else the
        # caller's unpack types the string slot as int (mirror of the P1 let-vs-val agreement).
        _saved_st = getattr(self, "_current_symbol_table", None)
        _saved_cs = getattr(self, "_current_self_type", None)
        _st = dict(symtab)
        for _k, _ty in (func.get("param_annotations") or {}).items():
            if _st.get(_k) in (None, "Any"):
                _st[_k] = _ty
        self._current_symbol_table = _st
        _nm = func.get("name", "")
        if "__" in _nm:
            self._current_self_type = _nm.split("__", 1)[0]
        try:
            slots = [self._infer_tuple_slot_type(e, array_vars, dict_vars, _st) for e in elts]
        finally:
            self._current_symbol_table = _saved_st
            self._current_self_type = _saved_cs
        if len(slots) == return_type.count(",") + 1 and any(s != "int" for s in slots):
            return "(" + ", ".join(slots) + ")"
        return return_type

    def _returns_emit_ir(self, body_stmts: List[Dict[str, Any]]) -> bool:
        """True if the function returns a constructed `emit_ir` node — a `return <local>` whose
        local's first assignment is an inline `{"type": K}` IR construction (or another emit_ir
        value), or a `return <emit_ir expr>` directly. Drives the `emit_ir` return-type override
        for the dict-literal IR-construction feature. @mutable_state-gated → False (inert) for the
        corpus, so the return type is unchanged there."""
        if (getattr(self, "_current_self_type", None)
                not in getattr(self, "_mutable_state_classes", set())):
            return False
        eir = self._collect_emit_ir_result_locals(body_stmts)
        found = [False]

        def rec(n: Any) -> None:
            if isinstance(n, dict):
                if n.get("stmt") == "Return":
                    v = n.get("value", {})
                    if isinstance(v, dict) and (
                            (v.get("type") == "Var" and v.get("name") in eir)
                            or self._is_emit_ir_expr(v)):
                        found[0] = True
                for x in n.values():
                    rec(x)
            elif isinstance(n, list):
                for x in n:
                    rec(x)
        rec(body_stmts)
        return found[0]

    # optional-field builder (monomorphic-option ADTs): the CSL-AST quantifier
    # nodes whose `_csl_*` handler is a mutable-dict-conditional-add construction
    # `d = {base}; if getattr(node, F, None) is not None: d[F] = V; return d`.
    # Maps the node kind → the emit_ir constructor (preamble.py `_emit_exprir_
    # theory`). The two OPTIONAL binder fields are `binder_type` (Optional[str] →
    # `iropt_str`) and `domain` (Optional[ExprIR] → `iropt_ir`). Fail-closed: a
    # kind not here keeps its normal (dict→map) lowering.
    _QUANTIFIER_OPT_CTORS = {"Forall": "IrForall", "Exists": "IrExists"}

    @staticmethod
    def _optfield_guard_name(test: Any, dname: str) -> Optional[str]:
        """The optional field name F if `test` is `getattr(node, "F", None) is not
        None` (IR: `BinOp !=`/`is not` with a `getattr(Var, String, None)` left and a
        `None` right) or the direct `node.F is not None` (`BinOp != Attribute None`),
        else None. `dname` is unused here — the guard reads `node`, distinct from the
        result local — kept for signature symmetry with the recognizer."""
        if not (isinstance(test, dict) and test.get("type") == "BinOp"
                and test.get("op") in ("!=", "is not")):
            return None
        right = test.get("right")
        if not (isinstance(right, dict) and right.get("type") == "None"):
            return None
        left = test.get("left")
        if not isinstance(left, dict):
            return None
        if left.get("type") == "Call" and left.get("func") == "getattr":
            args = left.get("args") or []
            if (len(args) >= 2 and isinstance(args[1], dict)
                    and args[1].get("type") == "String"):
                return args[1].get("value")
        if left.get("type") in ("Attribute", "FieldGet"):
            return left.get("attr") or left.get("field")
        return None

    def _recognize_optfield_builder(
            self, func: Dict[str, Any],
            body_stmts: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """optional-field builder (monomorphic-option ADTs): recognize the
        mutable-dict-conditional-add body of `_csl_forall`/`_csl_exists`

            d = {"type": K, "var": .., "body": ..}
            if getattr(node, F, None) is not None: d[F] = V     (0..n If's)
            return d

        (K in `_QUANTIFIER_OPT_CTORS`, each F a declared optional binder field).
        Returns a REWRITTEN single-`Return` body whose value is the MERGED emit_ir
        construction dict (base fields + the conditional-add optional entries),
        which `_lower_irnode_construction`/`_lower_quant_optfield` lowers to
        `(IrForall var body <iropt_str> <iropt_ir>)` — the optionals read from
        node's `option` record fields and converted at the ctor arg. Fail-closed:
        None on any mismatch (the body keeps its normal lowering). @mutable_state-
        gated (the emitter model) → corpus byte-inert."""
        if (getattr(self, "_current_self_type", None)
                not in getattr(self, "_mutable_state_classes", set())):
            return None
        if len(body_stmts) < 2:
            return None
        last = body_stmts[-1]
        if last.get("stmt") != "Return":
            return None
        rv = last.get("value")
        if not (isinstance(rv, dict) and rv.get("type") == "Var"):
            return None
        dname = rv.get("name")
        first = body_stmts[0]
        if first.get("stmt") != "Assign" or first.get("target") != dname:
            return None
        dlit = first.get("value")
        if not (isinstance(dlit, dict) and dlit.get("type") == "DictLit"):
            return None
        keys = dlit.get("keys", [])
        values = dlit.get("values", [])
        if not keys or len(keys) != len(values):
            return None
        base: Dict[str, Any] = {}
        for k, v in zip(keys, values):
            if not (isinstance(k, dict) and k.get("type") == "String"):
                return None
            base[k.get("value")] = v
        kind_ir = base.get("type")
        if not (isinstance(kind_ir, dict) and kind_ir.get("type") == "String"):
            return None
        if kind_ir.get("value") not in self._QUANTIFIER_OPT_CTORS:
            return None
        # The middle statements are the conditional-add If's — one optional field
        # each. Merge each `d[F] = V` into the construction dict as key F → V.
        merged_keys = list(keys)
        merged_values = list(values)
        for st in body_stmts[1:-1]:
            if st.get("stmt") != "If" or st.get("orelse"):
                return None
            f = self._optfield_guard_name(st.get("test"), dname)
            if f is None:
                return None
            ifbody = st.get("body") or []
            if len(ifbody) != 1:
                return None
            aset = ifbody[0]
            if aset.get("stmt") != "ArraySet":
                return None
            arr = aset.get("array")
            if not (isinstance(arr, dict) and arr.get("type") == "Var"
                    and arr.get("name") == dname):
                return None
            idx = aset.get("index")
            if not (isinstance(idx, dict) and idx.get("type") == "String"
                    and idx.get("value") == f):
                return None
            merged_keys.append({"type": "String", "value": f})
            merged_values.append(aset.get("value"))
        new_dlit = {"type": "DictLit", "keys": merged_keys, "values": merged_values}
        return [{"stmt": "Return", "value": new_dlit}]

    def _recognize_compound_map_getter(
            self, func: Dict[str, Any],
            body_stmts: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Recognize the compound-key const-map getter shape

            def f(k): return NAME.get(k, [])

        where NAME is a tuple-keyed const dict collected in
        `_module_const_compound_dicts`. Returns `{"map_name", "key_param",
        "key_whyml", "elem_whyml"}` for a faithful lowering, else None (fail-closed).
        Requires the body be EXACTLY one `Return` of `NAME.get(<Var>, [])` with an
        empty-list default — the shape whose `None -> Nil` arm is the honest `[]`
        default. Any other body keeps its existing lowering (byte-identical)."""
        mcc = getattr(self, "_module_const_compound_dicts", {}) or {}
        if not mcc or len(body_stmts) != 1:
            return None
        stmt = body_stmts[0]
        if stmt.get("stmt") != "Return":
            return None
        val = stmt.get("value")
        if not (isinstance(val, dict) and val.get("type") == "Call"):
            return None
        fn = val.get("func", "")
        if not (isinstance(fn, str) and fn.endswith(".get")):
            return None
        recv = fn[:-len(".get")]
        meta = mcc.get(recv)
        if meta is None:
            return None
        args = val.get("args") or []
        if len(args) != 2:
            return None
        key_arg, default_arg = args
        if not (isinstance(key_arg, dict) and key_arg.get("type") == "Var"):
            return None
        if not (isinstance(default_arg, dict)
                and default_arg.get("type") == "ArrayLit"
                and not default_arg.get("elts")):
            return None
        return {
            "map_name": recv,
            "key_param": key_arg.get("name"),
            "key_whyml": meta["key_whyml"],
            "elem_whyml": meta["elem_whyml"],
        }

    def _compute_return_type(self, func: Dict[str, Any], body_stmts: List[Dict[str, Any]]) -> str:
        """Compute the WhyML return type for one function, applying the
        `List[T] → array int`, `Set[T]`/`Dict[K, V]` → `map int (option int)`,
        and bounded-int overrides."""
        # compound-key const-map getter: `-> List[<tuple>]` returned as the map's
        # value list `list <elem_whyml>` (a PURE, immutable list of native tuples —
        # `array <record>` would be Why3-rejected for a mutable element). Gated on the
        # recognized getter shape → byte-identical for every other function.
        _cmg = getattr(self, "_compound_map_getter", None)
        if _cmg is not None:
            return f"list {_cmg['elem_whyml']}"
        bounded_int = func.get("bounded_int")
        return_type = IRScanner.find_return_type(body_stmts)
        return_type = self._refine_tuple_return_type(func, body_stmts, return_type)
        ann = func.get("return_annotation")
        # dict-literal emit_ir construction: a method that RETURNS a constructed IR node
        # (`node = {"type":"Var",…}; … return node`) is `emit_ir`, not the `map int (option int)`
        # its `-> Dict[str, Any]` annotation would otherwise imply (the Python type of an IR-node
        # dict is a dict; the MODEL type is the `emit_ir` sum). Overrides the `ann in
        # ("set","dict",…)` branch below. @mutable_state-gated → byte-identical for the corpus.
        if self._returns_emit_ir(body_stmts):
            return "emit_ir"
        # typing-engagement ty2 / 32-1700-typing-spec-8: a Protocol member is an
        # `abstract: True` bodyless `val` (the refinement target). Its body is
        # `...`/empty, so `find_return_type` returns "unit" — but the `-> T`
        # annotation is authoritative for an abstract member (the contract's
        # return type is the annotation, not the body). Promote the annotation
        # to the return type when the body carries no return statement. This
        # mirrors the existing `ann == "int" and return_type == "int"` override
        # path, generalized to the `unit`-from-empty-body case for abstract vals.
        if func.get("abstract") and return_type == "unit" and ann:
            return_type = "int"
        if ann in ("list", "bytes", "bytearray") and return_type == "int":
            # 0442.md B2 (no-more-int): bytes/bytearray are the byte-buffer array class.
            return_type = "array int"
            # str-list-elements: a list whose returned seq local carries STRING elements
            # is `array string` (its elements stay string end-to-end, so a consumer's
            # `names[i]` is a `string` feeding a string-typed callee like sys_stat).
            if self._returns_string_seq(body_stmts):
                return_type = "array string"
            # item34.md CF5: a `-> List[str]` annotation is authoritative for the element type
            # even when the body returns an empty list (`return []`).
            if func.get("return_value_type") == "string":
                return_type = "array string"
            # WL-04a: a `-> List[float]` return is the faithful `array real` (the float leaf),
            # so a float list-literal body type-checks and `\result[i] : real` is faithful.
            elif func.get("return_value_type") == "real":
                return_type = "array real"
            # WL-04b (record residual): a `-> List[<record>]` return is `array <record>`,
            # so a pass-through record-list return (`return a`) types coherently and
            # `\result[i].field` projects the faithful field.
            elif func.get("return_value_type") in self._record_types:
                return_type = f"array {self._record_types[func['return_value_type']]['whyml_name']}"
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
        # self-tcb-reduction spike (csl-ast-as-emit_ir): a `trusted` dispatcher whose
        # declared return annotation is an IR-node tag (`-> "ExprIR"`) resolves to
        # `emit_ir` — the return-side counterpart of `_symtype_to_whyml`'s param-side
        # mapping (line ~2260). `_returns_emit_ir` only fires for a body that
        # constructs a `{"type": K}` literal; a trusted stub's placeholder body
        # (`return {}`) has none, so this ann-based fallback is needed for the
        # dispatcher's `val` signature to type-check as `emit_ir -> emit_ir`. Only
        # reachable when `ann` carries one of the 4 recognized IR-node tags — no
        # corpus function outside a @mutable_state mirror uses them (byte-identical).
        elif (ann in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR")
                and return_type == "int"):
            return_type = "emit_ir"
        if bounded_int and return_type == "int":
            return_type = f"int{bounded_int}"
        return return_type

    def _bytes_param_range_requires(self) -> List[str]:
        """wrong-lowering-to-fix.md §WL-06c: emit the implicit byte-RANGE precondition
        `requires forall i. 0<=i<len(b) -> 0<=b[i]<256` for every `bytes`/`bytearray`
        PARAMETER of the function currently being emitted.

        Every real Python `bytes`/`bytearray` object has all elements in [0,256) — a
        TYPE-LEVEL guarantee (an out-of-range byte cannot exist), so the callee may
        ASSUME it. It is SOUND-and-additive: it only adds the range bound (a false
        SPECIFIC-value claim `b[k]==c` is NOT derivable from a range), and no verified
        corpus caller passes a bytes argument, so no call-site obligation arises.
        STRICTLY gated on symtype `bytes`/`bytearray` — a `List[int]`/`array int`
        param carries NO [0,256) bound and is NEVER emitted (soundness). Emitted in
        source-parameter order (deterministic); empty for every non-bytes-param
        function → byte-identical."""
        symtab = getattr(self, "_current_symbol_table", {}) or {}
        out: List[str] = []
        for p in getattr(self, "_formal_params", []):
            if symtab.get(p) in ("bytes", "bytearray"):
                b = whyml_ident(p)
                out.append(
                    f"    requires {{ (forall _wl06c_i : int. "
                    f"(((0 <= _wl06c_i) && (_wl06c_i < (Array.length {b}))) "
                    f"-> ((0 <= {b}[_wl06c_i]) && ({b}[_wl06c_i] < 256)))) }}")
        return out

    def _lower_fold_ensures(self, func: Dict[str, Any]) -> List[str]:
        """Lower a recognized fold method's `#@ ensures` clauses to WhyML strings
        for emission on the fold's TOP-LEVEL function (richer-contracts-bridge C1).

        Returns `["true"]` when the method carries only the default `ensures True`
        (or none) — so the emitted top-level `ensures` is byte-identical to the
        historical hardcoded `ensures { true }` (corpus-inert). A richer ensures
        (e.g. `wf_ir(\\result)` / `size(\\result) > 0`, a certified predicate the
        preamble pyval theory already puts in scope) is lowered through the normal
        contract path (`\\result` -> the WhyML `result` keyword) and emitted, so the
        certified fact becomes a checked postcondition instead of `True`."""
        ens_exprs = func.get("contracts", {}).get("ensures", []) or []
        # A relational ensures may reference the method's PARAMETERS (e.g.
        # `setfold_leaf_empty(obj, \result)`); register the formal params so a
        # bare param name emits bare (not a `!`-deref / abstract constant). Inert
        # for param-free ensures (`size(\result)`) => byte-identical.
        params = list(func.get("formal_params", []) or [])
        prev_spec = getattr(self, "_in_spec", False)
        prev_params = getattr(self, "_current_params", set())
        self._in_spec = True
        self._current_params = set(prev_params) | set(params)
        try:
            lowered = [self._expr_to_whyml(e, set()) for e in ens_exprs]
        finally:
            self._in_spec = prev_spec
            self._current_params = prev_params
        lowered = [s for s in lowered if s and s.strip() and s.strip() != "true"]
        return lowered or ["true"]

    def _lower_fold_requires(self, func: Dict[str, Any]) -> List[str]:
        """Lower a recognized fold method's `#@ requires` clauses to WhyML strings
        for emission on the fold's TOP-LEVEL function (richer-contracts-bridge
        C2). Returns `["true"]` when the method carries only the default
        `requires True` (byte-identical to the historical hardcoded
        `requires { true }`). A richer precondition (e.g. `wf_ir_deep(node)`, the
        deep well-formedness the substitution preserves) is threaded onto the
        emitted `let rec` so the per-helper preservation induction can discharge
        the recursive-call preconditions."""
        req_exprs = func.get("contracts", {}).get("requires", []) or []
        # A requires references the method's PARAMETERS (e.g. `wf_ir_deep(node)`).
        # A param is emitted BARE (not `!`-dereffed) exactly when it is in
        # `_current_params`; seeding `local_refs` instead would mis-lower it to a
        # `!node` deref of a non-ref. So temporarily register the formal params.
        params = list(func.get("formal_params", []) or [])
        prev_spec = getattr(self, "_in_spec", False)
        prev_params = getattr(self, "_current_params", set())
        self._in_spec = True
        self._current_params = set(prev_params) | set(params)
        try:
            lowered = [self._expr_to_whyml(e, set()) for e in req_exprs]
        finally:
            self._in_spec = prev_spec
            self._current_params = prev_params
        lowered = [s for s in lowered if s and s.strip() and s.strip() != "true"]
        return lowered or ["true"]

    def _emit_function(self, func: Dict[str, Any], scc_info: Dict[str, tuple]) -> List[str]:
        """Emit one WhyML let/val function block. Returns the list of output lines."""
        name = whyml_ident(func["name"])
        # bigger-build.md Phase 1: if the body is the A-unit generic-fold
        # catamorphism (recognizer, fail-closed), emit the type-derived
        # walk/walk_dict/walk_list group over the L1 `pyval`/`pydict` datatype
        # instead of the (broken) opaque-iterator loop lowering. The templater is
        # NOT in the TCB — a bug yields an unprovable instance (the `--fun`
        # re-proof is loud), never a false proof.
        from module6_whyml.generic_fold import (
            recognize_generic_fold, emit_generic_fold_group,
            recognize_setfold, emit_setfold_group,
            recognize_stmt_setfold, emit_stmt_setfold_group,
            recognize_substmap, emit_substmap_group,
            recognize_bool_existence, emit_bool_existence_group,
            recognize_bool_multiway, emit_bool_multiway_group,
            recognize_bool_lastelem, recognize_bool_earlyreturn,
            recognize_frt, emit_frt_group,
            recognize_sawalk, emit_sawalk_group,
            recognize_dictfold, emit_dictfold_group,
            recognize_void_dispatch, emit_void_dispatch_group,
            recognize_void_generic_descend, emit_void_generic_descend_group)
        _gf = recognize_generic_fold(func)
        if _gf is not None:
            return emit_generic_fold_group(func, _gf, whyml_ident)
        # ir-traversal-residual A-bool: the statement-tree existence fold (the
        # lambda-lifted `_has_return*` closures). Fail-closed; loud unprovable
        # instance on any template bug.
        _be = recognize_bool_existence(func)
        if _be is not None:
            return emit_bool_existence_group(func, _be, whyml_ident)
        # ir-traversal-residual A-bool MULTIWAY: the `stype = stmt.get("stmt")`
        # dispatch sibling of the above (`has_direct_return`/`has_in_loop_
        # return`-shaped) -- a genuine multiway `if stype == "<TAG>"`/`elif`
        # chain (incl. Try/handlers descend), reusing the same OR-descend
        # catamorphism generalized to N tags. Same fail-closed discipline.
        _bm = recognize_bool_multiway(func)
        if _bm is not None:
            return emit_bool_multiway_group(func, _bm, whyml_ident)
        # ir-traversal-residual A-bool LAST-ELEMENT dispatch: `ends_with_
        # return`-shaped (inspects only `<stmts>[-1]`). A third source shape
        # feeding the SAME `emit_bool_multiway_group` catamorphism -- see
        # generic_fold.py's module comment above `recognize_bool_lastelem`.
        _ble = recognize_bool_lastelem(func)
        if _ble is not None:
            return emit_bool_multiway_group(func, _ble, whyml_ident)
        # ir-traversal-residual A-bool ENUMERATE positional dispatch:
        # `has_early_return`-shaped (`for i, stmt in enumerate(stmts)` +
        # `i < len(stmts) - 1` guards). A fourth source shape feeding the
        # SAME catamorphism -- see generic_fold.py's module comment above
        # `recognize_bool_earlyreturn`.
        _ber = recognize_bool_earlyreturn(func)
        if _ber is not None:
            return emit_bool_multiway_group(func, _ber, whyml_ident)
        # ir-traversal-residual D + T2: the composed `find_return_type`
        # (outlined bool folds + first-match search + certified string tail).
        _frt = recognize_frt(func)
        if _frt is not None:
            # The certified string tail uses the same abstract string ops the
            # normal expression lowering would register; register them here since
            # the recognizer bypasses that path.
            self._add_abstract_op(
                "val str_concat_op (a: string) (b: string) : string\n"
                "    ensures { result = (concat a b) }\n"
                "    ensures { String.length result = String.length a + String.length b }")
            self._add_abstract_op(
                "val str_join_arr (sep: string) (xs: array string) : string\n"
                "    ensures { String.length result >= 0 }")
            return emit_frt_group(func, _frt, whyml_ident)
        # phase3.md §3.1: the A-set returned-set fold (result_algebra = SET). Same
        # fail-closed discipline; a template bug is a loud unprovable instance.
        _sf = recognize_setfold(func)
        if _sf is not None:
            return emit_setfold_group(func, _sf, whyml_ident,
                                      self._lower_fold_ensures(func))
        # bigger-build G-set-accumulate-multiway: the Set[str] statement-tree
        # accumulate fold (by-return sibling of `recognize_bool_existence`, same
        # `list pyval`/tag-dispatch/body-orelse-descend shape, `recognize_setfold`'s
        # `map string bool` algebra). Same fail-closed discipline.
        _ssf = recognize_stmt_setfold(func)
        if _ssf is not None:
            return emit_stmt_setfold_group(func, _ssf, whyml_ident,
                                           self._lower_fold_ensures(func))
        # ir-traversal-residual T1: the functorial-map RECONSTRUCTION traversal
        # (result_algebra = the value type itself). Same fail-closed discipline.
        _sm = recognize_substmap(func)
        if _sm is not None:
            return emit_substmap_group(func, _sm, whyml_ident,
                                       self._lower_fold_ensures(func),
                                       self._lower_fold_requires(func))
        # ir-traversal-residual T3: the context-threading walk `_sa_walk`
        # (env-threaded fold + `sdict` string-keyed symbol table + source-level
        # raise). Same fail-closed discipline; a template bug is a loud
        # unprovable instance, never a false proof.
        _sa = recognize_sawalk(func)
        if _sa is not None:
            return emit_sawalk_group(func, _sa, whyml_ident)
        # alist-adict-census §3: the returned-`sdict` dict-fold (result_algebra =
        # a string-keyed dict, by RETURN). The by-key-grouping twin of the A-set
        # returned-set fold; reuses the certified `sdict` + purely-defined
        # `sappend`. Same fail-closed discipline; a template bug is a loud
        # unprovable instance, never a false proof.
        _df = recognize_dictfold(func)
        if _df is not None:
            return emit_dictfold_group(func, _df, whyml_ident)
        # G-void-dispatch-thin: the void statement-list fan-out `for s in
        # stmts: if isinstance(s, dict): sibling(s, *ctx)`. The sibling stays
        # \trusted (opaque-`int` val, unchanged); the wrapper's own `stmts`
        # is modelled as `list int` (Cons/Nil) for free structural
        # termination. Same fail-closed discipline.
        _vd = recognize_void_dispatch(func)
        if _vd is not None:
            return emit_void_dispatch_group(func, _vd, whyml_ident)
        # G-void-generic-descend: the void UNTYPED tree descender
        # `if isinstance(v, dict): (if "stmt" in v: sibling(v, *ctx) else:
        # for x in v.values(): self(x, *ctx)) elif isinstance(v, list): for
        # x in v: self(x, *ctx)`. Unlike G-void-dispatch-thin, `v` is
        # genuinely heterogeneous (no `list` annotation) — modelled as the
        # real `pyval`/`pydict` L1 catamorphism. The sibling stays \trusted
        # (opaque-`int` val, unchanged). Same fail-closed discipline.
        _vgd = recognize_void_generic_descend(func)
        if _vgd is not None:
            return emit_void_generic_descend_group(func, _vgd, whyml_ident)
        body_stmts = func["body"]
        # optional-field builder (monomorphic-option ADTs): rewrite the
        # `_csl_forall`/`_csl_exists` mutable-dict-conditional-add body to a single
        # `Return` of the merged emit_ir construction dict, so the normal `let`
        # scaffolding (params, emit_ir return type via `_returns_emit_ir`,
        # `_lower_irnode_construction`) emits `(IrForall var body <opt> <opt>)`.
        # Fail-closed (None → unchanged); @mutable_state-gated → corpus byte-inert.
        _optb = self._recognize_optfield_builder(func, body_stmts)
        if _optb is not None:
            body_stmts = _optb
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
        # typing-engagement ty1 / 28-0000-typing-spec-4: the `-> NoReturn` IR flag
        # (NR1 — `ensures { false }` postcondition).
        func_is_noreturn = func.get("is_noreturn", False)
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
        is_recursive = (IRScanner.is_recursive(func["name"], body_stmts)
                        or IRScanner.is_recursive(name, body_stmts))
        use_rec = bool(func_variants) or is_recursive
        # A lemma is `assigns \nothing` so the purity heuristic flags it pure, but it
        # must NOT emit as a `let function` (a term) — it is a `let [rec] lemma` whose
        # body is a proof. Exclude it from the logic path. `emits_as_logic_symbol`
        # (scc.py) is the SHARED classifier the SCC contract-edge collector also uses,
        # so the dependency graph and the emission agree on "is this a logic symbol";
        # the emitter alone adds the emission-time `not local_refs` term.
        can_emit_as_logic = emits_as_logic_symbol(func) and not local_refs
        # cleared-array item 1: record that `name` is now a spec-callable logic
        # symbol (a pure `let function`), so a call comprehension `[name(x) for x
        # in a]` emitted LATER (in a caller's body, callee-before-caller SCC order)
        # can lift `result[i] = name(src[i])`. Recorded BEFORE the caller is
        # emitted; a non-logic function never enters the set → never liftable.
        if can_emit_as_logic:
            self._emitted_logic_funcs.add(name)
        # The function currently being emitted — the "using function" a deferred
        # call-comprehension `val` must be spliced in front of (item 1).
        self._current_emitting_func = name

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
        # Exceptions raised by called functions (via their declared
        # `#@ raises`) also escape this function unless caught — include
        # them so the emitted `raises {}` summary is complete (e.g. a
        # wrapper that calls `sys_open` propagates its FileNotFoundError).
        # `_callee_raised_in` already drops what an enclosing try/except in
        # the body catches. A callee raise the caller has committed to avoid
        # via `#@ no_exception E` is `assert`-and-`absurd`-wrapped at the
        # call site (so it provably does NOT escape) — subtract those, else
        # we would emit a spurious `raises {E}` on a function PyCSL is
        # otherwise free to emit as a pure `let function` (TR-BUG-2 / 0383).
        callee_escaping = self._callee_raised_in(body_stmts)
        if self._current_no_exception_all:
            from exception_model import all_phase1_exceptions
            callee_escaping -= set(all_phase1_exceptions())
        callee_escaping -= set(self._current_no_exception)
        func_exceptions |= callee_escaping
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
        # wrong-lowering-to-fix.md §WL-06c: an UNKNOWN `bytes`/`bytearray` PARAMETER
        # is the τ-blessed coarse `array int` buffer whose CONTENT is arbitrary to the
        # solver — but EVERY real Python `bytes`/`bytearray` object has all elements in
        # [0,256). That byte-RANGE fact is a TYPE-LEVEL guarantee (a caller cannot
        # construct an out-of-range byte), so it is emitted as an IMPLICIT precondition
        # `requires forall i. 0<=i<len(b) -> 0<=b[i]<256` for each bytes/bytearray param.
        # This is ADDITIVE and SOUND: it only adds the RANGE bound (a false SPECIFIC-value
        # claim like `b[0]==97` stays UNPROVEN — the range does not pin a value), the
        # false-twin coherence guards (0825/0594) still fail, and no verified caller
        # passes a bytes argument (all bytes-param corpus functions are leaves), so no
        # call-site obligation is created. A `bytes`/`bytearray` element WRITE never
        # reaches the body (bytes is rejected immutable, WL-06b; a bytearray param write
        # is rejected as a caller-visibility/frame boundary, §WL-05), so the entry range
        # invariant is never violated in-body. STRICTLY gated on symtype bytes/bytearray
        # (a `List[int]` param has NO [0,256) bound → never emitted). Byte-identical for
        # every function without a bytes/bytearray param.
        lines += self._bytes_param_range_requires()
        lines += self._emit_contracts(contract_src, spec_refs,
                                      func_variants, func_diverges,
                                      func_exceptions, func_is_noreturn)
        # tier3-p1 T3.1.4 (spike LAW 3): a recursive function over an IR-node (`emit_ir`)
        # param — the `_expr_to_whyml`/dispatcher recursion shape — carries NO natural
        # structural `variant` (its recursive call passes a PROJECTED sub-node
        # `node.get("left")` = `(left_of node)`, not a pattern-bound sub-term). Inject a
        # function-level `variant { size <param> }` on the ADT subtree measure; the guarded
        # size-decrease lemmas (`size_left_dec`/`size_right_dec`, emitted in the theory)
        # discharge each recursive call, and `size`'s `result >= 1` gives the int well-
        # foundedness lower bound. Only when recursive, no explicit `#@ variant`, and NOT a
        # trusted/abstract `val`. This is the piece tier-1's `ir_scanner` lacked.
        if (is_recursive and not func_variants and not emit_as_val
                and not func_lemma):
            _ir_p = next((p for p in getattr(self, "_formal_params", [])
                          if (self._current_symbol_table or {}).get(p)
                          in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR", "exprir", "emit_ir")),
                         None)
            if _ir_p is not None:
                lines.append(f"    variant  {{ size {whyml_ident(_ir_p)} }}")
        self._emitting_val_contract = False

        # mutable-self-plan.md M.4: a method of a `@mutable_state` class emits its
        # `#@ assigns self.x` (from `_module_method_writes`) as a WhyML `writes { … }`
        # clause on the CONCRETE `let` — so Why3 CHECKS the frame against the body (a
        # wrong or `\nothing` assigns on a mutating body FAILS: the soundness fix).
        # `writes { }` is valid Why3 and rejects any unlisted write. Opt-in via the
        # class decorator → byte-identical for every unmarked class.
        if (is_method and not emit_as_val
                and self._current_self_type in getattr(self, "_mutable_state_classes", set())):
            _wf = self._module_method_writes.get(func["name"], [])
            _wc = ", ".join(f"self.{self._field_label(self._current_self_type, f)}"
                            for f in _wf)
            lines.append(f"    writes {{ {_wc} }}")

        # wrong-lowering-to-fix.md §WL-05b: a STANDALONE function whose dict/set params
        # are item-mutated in the body carries a `writes { d, s, … }` frame so Why3
        # accepts (and CHECKS) the caller-visible in-place mutation of the `ref (map …)`
        # params. Emitted in source-parameter order (deterministic). Empty set →
        # no clause → byte-identical for every read-only-param program.
        if not emit_as_val:
            _mcp = getattr(self, "_mutated_collection_params", set())
            if _mcp:
                _ordered = [whyml_ident(p) for p in self._formal_params if p in _mcp]
                if _ordered:
                    lines.append(f"    writes {{ {', '.join(_ordered)} }}")

        if emit_as_val:
            lines.append("")
            return lines

        lines.append("  =")
        # fresh-globals.md: `#@ fresh_globals` re-establishes each module-global
        # singleton's CONSTRUCTOR post-state (the `#@ ensures`, `self` -> the global)
        # as an ASSUMED fact at this confined standalone driver's entry — the SOUND
        # surfacing of "a freshly-imported global ran its constructor". The SAME facts
        # are CHECKED of the global's literal initializer by `_emit_module_globals`
        # (`goal <g>_fresh_init_*`), so the assume is proof-backed, not blind. Module4
        # confines the directive to non-callee top-level drivers (soundness).
        if func.get("fresh_globals"):
            for fact in self._fresh_globals_facts():
                if fact and fact != "true":
                    lines.append(f"    assume {{ {fact} }};")
        lines.append(self._emit_body_code(func, body_stmts, local_refs, ghost_vars,
                                          ref_params, is_method, return_type))
        # b-spec §4 (P2): in the owning unit (real `let`), prove the interface is a sound weakening
        # of the definition. Fail-loud — an over-claiming interface makes the goal unprovable.
        if _iface:
            lines += self._emit_narrowing_vc(name, args_str, return_type,
                                             func.get("contracts", {}), _iface, spec_refs)
        # typing-engagement ty1 / 25-1700-typing-spec-1 §2.2: per-arm VCs for
        # Union-typed parameters (C2 injection, C3 projection).
        _symtab = func.get("symbol_table", {}) or {}
        if any(v and v.startswith("_union_") for v in _symtab.values()):
            lines += self._emit_union_arm_vc(name, _symtab)
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
                # item34.md CF5: `-> List[str]` (element in `return_value_type`) → `array
                # string`, so a `self.<m>(...)` call site abstracts as `array string`.
                if func.get("return_value_type") == "string":
                    ret = "array string"
            elif ann in ("set", "dict", "frozenset") and ret == "int":
                # Functions annotated `-> Set[T]` / `-> Dict[K, V]` are
                # auto-trusted via `_should_auto_trust_map_return`; their
                # abstract `val` must announce the map return so callers
                # don't pre-decl a `ref 0` (int) target and then `:=` a
                # map.
                ret = "map int (option int)"
            elif ann == "str" and ret == "int":
                # no-more-int emitter campaign L1: a `-> str` function returns a
                # WhyML `string`, not the legacy int hash — so a caller can type a
                # `s = f(...)` local as string. (MEASUREMENT branch — gated.)
                ret = "string"
            elif ann in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR") and ret == "int":
                # self-tcb-reduction spike (csl-ast-as-emit_ir): the `self.<method>(...)`
                # SELF-CALL abstract-val sibling of `_compute_return_type`'s ann-based
                # `emit_ir` fallback (line ~2260-2270) — a `trusted` IR-node dispatcher
                # called from WITHIN the same @mutable_state class (e.g. `_csl_binop`
                # calling `self._csl_to_ir(node.left)`) is abstracted here, not there, so
                # this map needs the SAME recognition or the self-call site sees `int`.
                ret = "emit_ir"
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
            if t == "OldVar":
                return False
            if t == "OldField":
                # `\old(self.<plainfield>)` flattens to OldField (Module5), whereas
                # `\old(self.arr[i])` stays an `Old` node — so a result-guarded counter
                # exposed to a caller (`\result==0 ==> self.n == \old(self.n)+1`)
                # propagated through NO map: field_old rejects \result; this map and
                # field_param_result rejected OldField. Allow OldField OF SELF here (the
                # shared field-ensures lowering already emits `old (self.f)`, as the
                # field_old void-mutator clauses prove). Requires a CURRENT self-field too
                # (the `saw("field")` gate below), so a pure `\result == \old(self.x)`
                # getter — no current field — is unaffected (byte-identical).
                return False if node.get("object") != "self" else None
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
        AND a param but NO `\\result`, quantifier, local, or non-self object — each formal param
        renamed to `x_i`. These are the void-mutator WRITE POSTCONDITIONS
        (`slot_inode(self.disk, b, s) == inode`, `slot_name(self.disk, b, s) == name`,
        `slot_inode(self.disk, b, s) == 0`) that every existing map drops: `field_old` rejects
        params, `field_param_result` requires `\\result`. So a `#@ no_inline` mutator's boundary
        stub carried only `writes`, and a caller (mkdir/link/symlink: presence witness;
        unlink/rmdir: the just-zeroed slot) could prove nothing about what the call WROTE.

        `\\old` IS allowed (it lowers to the val's pre-state and the no_inline method's own val
        proves the clause). It was originally lumped into the reject set, which dropped a
        post-state whose GUARD references `\\old` of a field — e.g. lseek's
        `(whence==0 ∧ offset≥0 ∧ fd<64 ∧ \\old(self.fd_open[fd])==1) → self.fd_offset[fd]==offset`
        (field+param+old, no result) — leaving the SEEK_SET stub unable to pin fd_offset.

        Restricted to NON-QUANTIFIED clauses ON PURPOSE (plan §2.9): a non-quantified equality
        carries no trigger, so it CANNOT E-match-poison sibling goals (the failure mode that
        sank the quantified-frame attempt) — this is why quantifiers (not `\\old`) are the real
        restriction. The quantified FRAME (`\\forall k. … == \\old`) is a separate, opt-in
        concern handled elsewhere. Reuses the param-rename of the field+param+result map."""
        def classify(node: Any, params: Set[str]) -> Optional[bool]:
            if not isinstance(node, dict):
                return None
            t = node.get("type")
            if t in ("Result", "Forall", "Exists", "ForallItems"):
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

    def _build_method_field_param_frame_ensures_map(
            self, functions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Map method name → its QUANTIFIED self-field FRAME `ensures`
        (`\\forall k. guard -> X == \\old(X)`), params renamed to `x_i` — but ONLY for methods
        the author OPTED IN with `#@ propagate_frame` (os-roadmap M4). These are the frames the
        boundary stub drops and that the absence/uniqueness proofs need (`_zero_entry`'s slot
        frame), yet which POISON term-rich callers if exposed broadly (§2.9). Gating on
        `propagate_frame` makes the author assert "this mutator's callers need + can absorb the
        frame" (e.g. `_zero_entry`, called only by unlink/rmdir/rename — never link/symlink).

        Kept clauses must: reference a self-field + a param, contain a quantifier, NO `\\result`,
        and (belt-and-braces, §2.9) have a frame term `X` that is a function APPLICATION (Call) so
        its trigger (pinned later in the Forall handler) is specific. Raw-array frames are dropped.
        Quantifier binders are threaded so the bound `k` is not mistaken for a local."""
        def classify(node: Any, params: Set[str], bound: Set[str]) -> Optional[bool]:
            if not isinstance(node, dict):
                return None
            t = node.get("type")
            if t == "Result":
                return False
            if t in ("FieldGet", "Attribute", "OldField"):
                return False if node.get("object") != "self" else None
            if t == "OldVar":
                return False
            if t == "Subscript":
                _v = node.get("value", {})
                if isinstance(_v, dict) and _v.get("type") == "Var":
                    return False
            if t == "Var":
                n = node.get("name")
                return None if (n in params or n in bound) else False
            if t == "ArrayLen":
                v = node.get("var")
                if isinstance(v, dict):
                    return None if v.get("object") == "self" else False
                return None if (v == "self" or v in params or v in bound) else False
            if t in ("Forall", "Exists", "ForallItems"):
                bv = node.get("var")
                if bv:
                    bound = bound | {bv}
            for k, val in node.items():
                if k in ("var", "binder_type", "type"):
                    continue
                for c in (val if isinstance(val, list) else [val]):
                    if classify(c, params, bound) is False:
                        return False
            return None

        def saw(node: Any, kind: str) -> bool:
            if not isinstance(node, dict):
                return False
            t = node.get("type")
            if kind == "field" and t in ("FieldGet", "Attribute", "OldField") \
                    and node.get("object") == "self":
                return True
            if kind == "forall" and t in ("Forall", "Exists", "ForallItems"):
                return True
            if kind == "result" and (t == "Result"
                                     or (t == "ArrayLen" and node.get("var") == "\\result")):
                return True
            return any(saw(c, kind) for val in node.values()
                       for c in (val if isinstance(val, list) else [val]))

        def refs_param(node: Any, params: Set[str]) -> bool:
            if not isinstance(node, dict):
                return False
            if node.get("type") == "Var" and node.get("name") in params:
                return True
            if node.get("type") == "ArrayLen" and node.get("var") in params:
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
            if not func.get("propagate_frame"):
                continue
            params = func.get("formal_params", []) or []
            if not params:
                continue
            pset = set(params)
            pmap = {p: f"x{i}" for i, p in enumerate(params)}
            kept = []
            for e in (func.get("contracts", {}).get("ensures", []) or []):
                if (classify(e, pset, set()) is not False
                        and saw(e, "field") and saw(e, "forall") and not saw(e, "result")
                        and refs_param(e, pset)):
                    tt = self._frame_trigger_term(e)
                    if isinstance(tt, dict) and tt.get("type") == "Call":
                        kept.append(rename(e, pmap))
            if kept:
                out[func["name"]] = kept
        return out

    def _build_method_result_frame_ensures_map(
            self, functions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Map method name → its QUANTIFIED self-field SINGLE-CELL FRAME `ensures` that
        REFERENCES `\\result` (`\\forall k. (… and k != \\result) -> self.f[k] == \\old(self.f[k])`),
        params renamed to `x_i` — but ONLY for methods that OPTED IN with `#@ propagate_frame`.

        This is the `\\result`-referencing TWIN of `_build_method_field_param_frame_ensures_map`
        (which deliberately DROPS `\\result`-bearing frames — see its `not saw(e, "result")`). The
        os fd-allocating syscalls (`sys_open`/`sys_dup`) touch AT MOST the returned slot of
        `self.fd_open`; the frame `\\forall k != \\result. fd_open[k] == \\old(fd_open[k])` lets a
        caller (the os `__init__` wrapper / a composed test) prove "the table is not full" survives
        a prior `open` — the honest free-slot side-condition `_alloc_fd` discharges. WITHOUT this
        the boundary `val` havocs the whole `fd_open` array (only the returned cell is pinned).

        BINDING: at the call site this is lowered inside the abstract `val ... : ty ensures { … }`
        where `\\result` lowers to Why3's `result` keyword — which IS the val's return value (the
        call result). So no explicit `\\result`→result-var substitution is needed; the existing
        lowering binds it correctly. The frame is a SOUND lowering of the leaf's real ensures (it
        is literally the same `\\forall` clause the body verifies), not a fabricated/over-broad one.

        Kept clauses must: reference a self-field, contain a quantifier, AND reference `\\result`;
        and (soundness) contain no local / non-self object / `\\old` of a non-self term. Restricted
        to `propagate_frame` opt-in so it fires ONLY for the marked fd allocators, never broadly."""
        def classify(node: Any, params: Set[str], bound: Set[str]) -> Optional[bool]:
            if not isinstance(node, dict):
                return None
            t = node.get("type")
            # `\result` IS permitted here (the whole point of this map).
            if t == "Result":
                return None
            if t in ("FieldGet", "Attribute", "OldField"):
                return False if node.get("object") != "self" else None
            if t == "OldVar":
                return False
            if t == "Subscript":
                _v = node.get("value", {})
                if isinstance(_v, dict) and _v.get("type") == "Var":
                    return False
            if t == "Var":
                n = node.get("name")
                return None if (n in params or n in bound) else False
            if t == "ArrayLen":
                v = node.get("var")
                if isinstance(v, dict):
                    return None if v.get("object") == "self" else False
                return None if (v == "self" or v in params or v in bound) else False
            if t in ("Forall", "Exists", "ForallItems"):
                bv = node.get("var")
                if bv:
                    bound = bound | {bv}
            for k, val in node.items():
                if k in ("var", "binder_type", "type"):
                    continue
                for c in (val if isinstance(val, list) else [val]):
                    if classify(c, params, bound) is False:
                        return False
            return None

        def saw(node: Any, kind: str) -> bool:
            if not isinstance(node, dict):
                return False
            t = node.get("type")
            if kind == "field" and t in ("FieldGet", "Attribute", "OldField") \
                    and node.get("object") == "self":
                return True
            if kind == "forall" and t in ("Forall", "Exists", "ForallItems"):
                return True
            if kind == "result" and (t == "Result"
                                     or (t == "ArrayLen" and node.get("var") == "\\result")):
                return True
            return any(saw(c, kind) for val in node.values()
                       for c in (val if isinstance(val, list) else [val]))

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
            if not func.get("propagate_frame"):
                continue
            params = func.get("formal_params", []) or []
            pset = set(params)
            pmap = {p: f"x{i}" for i, p in enumerate(params)}
            kept = []
            for e in (func.get("contracts", {}).get("ensures", []) or []):
                if (classify(e, pset, set()) is not False
                        and saw(e, "field") and saw(e, "forall") and saw(e, "result")):
                    kept.append(rename(e, pmap))
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
        # typed-ir-for-b-ceiling.md B-C2: an `ExprIR`/`StmtIR`/`IRNode`-annotated
        # param or field is the typed IR-node sum `exprir` (§2.1), so an inline
        # `{"type": K}` construction and a real IR field unify at a sibling that takes
        # both. Only present in a @mutable_state mirror → byte-identical for the corpus.
        if symtype in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR", "exprir"):
            return "emit_ir"
        return "int"

    @staticmethod
    def _dict_param_whyml_type(var_name: str,
                               key_types: Dict[str, str],
                               value_types: Dict[str, str],
                               default: str = "map int (option int)") -> str:
        """Compute the WhyML map type for a `dict`-typed parameter/local,
        honoring κ (key type) and ν (value type) from the IR's
        `dict_key_types` / `dict_value_types`. Falls back to `default`
        (the byte-identical pre-existing behaviour) when neither is set
        — i.e. for every int-keyed/int-valued dict the result is exactly
        `map int (option int)`. Mirrors the body-local inference that
        Why3 performs on the empty-map literal + polymorphic
        `map_update_some`, but for a parameter there is no first-assignment
        to drive inference, so the κ/ν must be in the declared type."""
        kappa = key_types.get(var_name) if key_types else None
        nu = value_types.get(var_name) if value_types else None
        if not kappa and not nu:
            return default
        k = "string" if kappa == "string" else "int"
        if nu == "string":
            v = "string"
        elif nu == "seq int":
            v = "seq int"
        elif nu and nu.startswith("map "):
            v = nu  # nested map value, e.g. `map int (option int)`
        else:
            v = "int"
        # A compound value type (`seq int`, `map …`) MUST be parenthesized inside
        # `option`, else WhyML parses `option seq int` as `option` applied to the
        # bare `seq` (0-arg) — "Type symbol seq expects 1 argument but is applied
        # to 0". A scalar `v` (`int`/`string`) needs no parens (byte-identical).
        v_arg = f"({v})" if " " in v else v
        return f"map {k} (option {v_arg})"

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
                    # 07-03-refactor (cross-file wiring): also propagate a `str` return so the
                    # `_module_method_return_annotations` map recognizes the dep as string-returning
                    # (a `self.<dep>(…)` call then routes through `str_concat`/no `int_to_string`).
                    "return_annotation": ret if ret in ("list", "set", "dict", "frozenset", "str") else None,
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

    def _collect_calls(self, body: List[Dict[str, Any]], acc: List[tuple]) -> None:
        """wrong-lowering-to-fix.md §WL-05b (fixpoint helper): gather every `(func_name,
        args_list)` call anywhere in a statement subtree (for the transitive
        param-forwarding analysis). Walks expression trees too, so a call nested in a
        subexpression is found."""
        def walk_expr(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("type") == "Call" and isinstance(node.get("func"), str):
                    acc.append((node["func"], node.get("args", []) or []))
                for v in node.values():
                    walk_expr(v)
            elif isinstance(node, list):
                for v in node:
                    walk_expr(v)
        walk_expr(body)

    def _seed_mutated_collection_params(self, func: Dict[str, Any]) -> Set[str]:
        """§WL-05b: the DIRECT seed — dict/set formal params item-mutated in this
        function's own body (`d[k]=v`, `s.add/discard/remove(x)`). Method functions are
        excluded (their param types feed the abstract-op call map, which the ref
        promotion would desync). Mirrors `_reject_param_collection_mutation`'s gating."""
        if func.get("kind") == "method":
            return set()
        params = set(func.get("formal_params", []) or [])
        symtab = func.get("symbol_table", {}) or {}

        def is_coll(name: str) -> bool:
            return name in params and symtab.get(name) in ("dict", "set", "frozenset")

        mutated: Set[str] = set()

        def walk(stmts: List[Dict[str, Any]]) -> None:
            for st in stmts:
                if not isinstance(st, dict):
                    continue
                kind = st.get("stmt")
                if kind in ("ArraySet", "DelSubscript"):
                    # §WL-05c (T7): `del d[k]` (DelSubscript) is an item mutation just
                    # like `d[k]=v` (ArraySet) — a standalone param that is del-mutated
                    # is promoted to a caller-visible `ref (map …)` so the deletion
                    # escapes (consistent with WL-05b). A METHOD is excluded above.
                    arr = st.get("array", {})
                    if (isinstance(arr, dict) and arr.get("type") == "Var"
                            and is_coll(arr.get("name", ""))):
                        mutated.add(arr["name"])
                elif kind in ("Expr", "ExprStmt"):
                    val = st.get("value", {})
                    if isinstance(val, dict) and val.get("type") == "Call":
                        fn = val.get("func", "")
                        if isinstance(fn, str) and fn.endswith((".add", ".discard", ".remove")):
                            recv = fn.rsplit(".", 1)[0]
                            if is_coll(recv):
                                mutated.add(recv)
                for key in ("body", "orelse", "finalbody"):
                    sub = st.get(key)
                    if isinstance(sub, list):
                        walk(sub)
                for hk in ("handlers", "cases"):
                    for h in (st.get(hk) or []):
                        if isinstance(h, dict):
                            walk(h.get("body", []) or [])
        walk(func.get("body", []) or [])
        return mutated

    def _build_func_mutated_collection_params(
            self, functions: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """§WL-05b: module-level map func-name → set of dict/set params modelled as a
        caller-visible mutable `ref (map …)` (a `writes {p}` frame). Computed as a
        FIXPOINT: seed with directly item-mutated params, then propagate — if function A
        forwards its param `p` (a bare `Var`) as the argument at a position that callee B
        mutates, then `p` is mutated in A too (Python's by-reference escape is
        transitive). This keeps call sites SOUND: an argument landing in a callee's
        mutated (ref) position is itself a ref (a local dict, or a now-promoted param)."""
        by_name: Dict[str, Set[str]] = {}
        formals: Dict[str, List[str]] = {}
        for func in functions:
            nm = func.get("name")
            if nm is None:
                continue
            by_name[nm] = self._seed_mutated_collection_params(func)
            formals[nm] = list(func.get("formal_params", []) or [])
        # Only standalone functions carry ref-collection params (methods excluded in the
        # seed), so the fixpoint stays within the standalone call graph.
        changed = True
        while changed:
            changed = False
            for func in functions:
                nm = func.get("name")
                if nm is None or func.get("kind") == "method":
                    continue
                params = set(func.get("formal_params", []) or [])
                calls: List[tuple] = []
                self._collect_calls(func.get("body", []) or [], calls)
                for callee, args in calls:
                    callee_mut = by_name.get(callee)
                    if not callee_mut:
                        continue
                    cf = formals.get(callee, [])
                    for i, a in enumerate(args):
                        if i >= len(cf):
                            break
                        if cf[i] not in callee_mut:
                            continue
                        if (isinstance(a, dict) and a.get("type") == "Var"
                                and a.get("name") in params
                                and a["name"] not in by_name[nm]):
                            by_name[nm].add(a["name"])
                            changed = True
        return by_name

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
            # no-more-int-3 A1 T1.2 (param-form): thread the per-param
            # κ/ν so a `Dict[str, ...]`-typed callee parameter's abstract
            # val matches the caller's string-keyed argument. Byte-
            # identical when the callee has no `dict_key_types` /
            # `dict_value_types` entries (every existing int dict).
            _kt = func.get("dict_key_types", {}) or {}
            _vt = func.get("dict_value_types", {}) or {}
            _plet = func.get("param_list_elem_types", {}) or {}
            param_types: List[str] = []
            _formal = set(func.get("formal_params", []))
            _pann = func.get("param_annotations", {}) or {}
            for name, symtype in symtable.items():
                if name in local_assignees and name not in _formal:
                    continue
                # i-feel-good.md I-B: a `List[str]` param → `array string` (not the
                # collapsed `array int`), so a caller passing a string-list literal
                # type-checks. @mutable_state-gated → byte-identical elsewhere.
                if (_plet.get(name) == "string"
                        and getattr(self, "_mutable_state_classes", None)):
                    param_types.append("array string")
                    continue
                # typed-ir §16: prefer a formal param's declared ANNOTATION over its
                # symbol-table type — the latter drifts to `Any`/int when the body
                # REASSIGNS the param (`val = _empty` in `_emit_first_assign`), which
                # would mistype the abstract self-call val. Gated on @mutable_state.
                if (name in _formal and name in _pann
                        and getattr(self, "_mutable_state_classes", None)):
                    symtype = _pann[name]
                if symtype == "dict" and (name in _kt or name in _vt):
                    param_types.append(
                        self._dict_param_whyml_type(name, _kt, _vt))
                else:
                    _wt = self._symtype_to_whyml(symtype)
                    if _wt == "int" and symtype and getattr(self, "_mutable_state_classes", None):
                        _rt = getattr(self, "_record_types", {})
                        _rec = (_rt.get(symtype) or _rt.get(str(symtype).lower())
                                or next((v for k, v in _rt.items() if k.lower() == str(symtype).lower()), None))
                        if _rec: _wt = _rec.get("whyml_name", str(symtype).lower())
                    param_types.append(_wt)
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
            # no-more-int-3 A1 T1.2 (param-form): see _build_method_param_types_map.
            _kt = func.get("dict_key_types", {}) or {}
            _vt = func.get("dict_value_types", {}) or {}
            by_name: Dict[str, str] = {}
            for pname in func.get("formal_params", []):
                symtype = symtable.get(pname)
                if symtype == "dict" and (pname in _kt or pname in _vt):
                    by_name[pname] = self._dict_param_whyml_type(pname, _kt, _vt)
                else:
                    by_name[pname] = self._symtype_to_whyml(symtype)
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

