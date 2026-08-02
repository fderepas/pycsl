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
        # W8 capability (ii) — varargs-membership. A `*vals: str` vararg is the IMMUTABLE
        # `seq string` of the extra positional arguments. `seq` (not `array`) because the
        # tuple Python builds is immutable, and because a Why3 `array` is mutable and
        # therefore cannot be a pure parameter here. Gated on the Module5-recorded
        # `vararg_str_param` (str-annotated varargs only) -> byte-identical elsewhere.
        if arg == getattr(self, "_vararg_str_param", None):
            return f"({safe}: seq string)"
        # self-tcb-reduction giants (generic class-body lowering): a param annotated
        # `ast.ClassDef` whose `.body` is iterated is the opaque `py_classdef_node` AST
        # node (its `.body` reads the `class_body_ast` psl). Gated on the per-function
        # `_current_pyast_classdef_params` (only under `_uses_pyast_stmt`) -> byte-identical.
        if arg in getattr(self, "_current_pyast_classdef_params", set()):
            return f"({safe}: py_classdef_node)"
        # J2/J3 convergence (module-body dispatch): a param annotated `ast.Module` whose
        # `.body` is iterated is the opaque `py_module_node` AST node (its `.body` reads
        # the `module_body_ast` psl). Gated on `_current_pyast_module_params`.
        if arg in getattr(self, "_current_pyast_module_params", set()):
            return f"({safe}: py_module_node)"
        # L1 tparam reflection-node ADT: a param annotated `TParamNode` whose `.type_params`
        # is iterated is the opaque `py_tparam_node` AST node (its `.type_params` reads the
        # `type_params_of` tparam_list). Gated on `_current_tparam_node_params` (only under
        # `_uses_tparam`) -> byte-identical elsewhere.
        if arg in getattr(self, "_current_tparam_node_params", set()):
            return f"({safe}: py_tparam_node)"
        # compound-key const-map getter: the key parameter takes the native tuple key
        # type (`(string, option string)`) so `Map.get NAME k` type-checks. Gated on
        # the recognized getter → never fires for a corpus param (byte-identical).
        _ck = getattr(self, "_compound_key_params", {})
        if arg in _ck:
            return f"({safe}: {_ck[arg]})"
        if arg in ref_params:
            return f"({safe}: ref {int_type})"
        # stmt-list-append-mutation wall (C-bucket): a list param that is `.append`-ed a
        # `{"stmt":K}` statement node (fixpoint incl. transitive forwarding) is a
        # caller-visible mutable `ref (seq stmt_ir)` — passed BY REFERENCE, so the append
        # escapes to the caller (the SOUND model; the fable oracle's `push`). NOT the
        # by-value `array int` + `snapshot`-local shadow (invisible to the caller). Keyed
        # on the stmt-seq-mut set → corpus-inert (byte-identical everywhere else).
        if arg in getattr(self, "_stmt_seq_mut_params", set()):
            return f"({safe}: ref (seq stmt_ir))"
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
            # r1-setop I1 (self-tcb-reduction): a BY-REFERENCE `Set[str]`/`FrozenSet[str]`
            # param (a mutated-collection param → `ref (map …)`) is STRING-keyed `ref (map
            # string (option int))` (the set element IS the key), mirroring the dict branch's
            # κ threading — so `s.add(x)`/`x in s` on it read/write the RAW native string key
            # (no `str_hash_op`), matching the already-string-keyed set-op lowering. κ is taken
            # from `_dict_key_types` (Module5's usage-based inference: a `.add`/membership with
            # a provably-string key tags the param κ=string; cf. `_tag_str_keyed`).
            #   GATED ON `_mut_coll`: a by-ref set param genuinely EMITS the raw-string map
            # write (`s := map_update_some !s x 0`), so its type must agree. A NON-by-ref set
            # param (a METHOD's set param — `_seed_mutated_collection_params` excludes methods —
            # whose `.add` lowers to the sound `()` no-op, e.g. `_emit_new_ghost_ref`'s
            # `local_refs`/`declared_refs`) must STAY `map int`: it emits no raw-string op AND is
            # forwarded to sibling `val` bridges (`_stmts_to_whyml`) still typed `map int`, so a
            # `map string` here would mistype the bridge (that cross-method κ=string agreement is
            # the deferred I4 fixpoint). Byte-identical for every int-keyed / non-by-ref set param
            # (0821/0833 `Set[int]`, 0884's `Any`-erased `acc`, and all method set params).
            kt = getattr(self, "_dict_key_types", {}) or {}
            _sk = "string" if (_mut_coll and kt.get(arg) == "string") else "int"
            _smt = f"map {_sk} (option int)"
            if _mut_coll:
                return f"({safe}: ref ({_smt}))"
            return f"({safe}: {_smt})"
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
        # W8 capability (ii): the `*vals: str` vararg parameter of this function, or
        # None. Module5 only records a STRING-annotated vararg, so this is None for
        # every corpus / pycsl_lib function -> byte-identical.
        self._vararg_str_param = func.get("vararg_str_param")
        if self._vararg_str_param:
            # It is a real parameter, so a bare read of it must resolve to the
            # parameter name — NOT fall through to the opaque `val constant vals : int`
            # that the drop-the-vararg behaviour produced.
            self._current_params.add(self._vararg_str_param)
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
        # opaque-nested-map-reader (self-tcb-reduction): `X = getattr(self,
        # "<field>", {})` where <field> is an OPAQUE (undeclared, non-mutable-
        # state) instance map populated elsewhere, read ONLY as `k in X` and the
        # nested `X[k]["<litkey>"]` string projection. Maps the alias local ->
        # reader base name (`_record_types` -> `record_types`); membership lowers
        # to the opaque `<base>_mem k : bool`, the nested read to `<base>_<litkey>
        # k : string`. Distinct from §26: NO mutable-state / declared-field gate;
        # instead gated on the nested `X[k]["<lit>"]` read shape being present
        # (corpus-inert — see `_prescan_opaque_selfmap_aliases`).
        self._opaque_selfmap_aliases: Dict[str, str] = {}
        # opaque-nested-map-reader SPLIT form (self-tcb-reduction, drift-1
        # `_union_arm_whyml_type`): `_rt = getattr(self, "_record_types", {}).get(tag)`
        # binds a local to the INNER dict for the OUTER key `tag`; a later `_rt["<lit>"]`
        # / `_rt.get("<lit>")` string projection and the truthiness `if _rt` then read
        # `self._record_types[tag]["<lit>"]` / membership. This is the two-statement
        # split of the chained `record_types[tag]["whyml_name"]` shape the (non-split)
        # `_opaque_selfmap_aliases` already models. Maps the inner-alias local ->
        # (reader base, OUTER-key IR): `_rt.get("whyml_name")`/`_rt["whyml_name"]` lower
        # to `record_types_whyml_name <tag> : string`, `if _rt` to `record_types_mem
        # <tag> : bool` — the SAME abstract readers, keyed on the REAL outer key (no
        # int-hash, non-vacuous). Gated on the inner string-lit read shape being present
        # (see `_prescan_opaque_selfmap_aliases`) -> corpus byte-inert.
        self._opaque_selfmap_inner_aliases: Dict[str, Tuple[str, Any]] = {}
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
        # self-tcb-reduction giants (generic class-body lowering): the params annotated
        # `ast.ClassDef` (typed `py_classdef_node`) whose `.body` iterates the class-body
        # psl. Gated on `_uses_pyast_stmt` so a non-target file leaves these empty
        # (byte-identical). `_pyast_stmt_locals` accumulates the per-iteration `child`
        # loop targets (typed `pyast_stmt`) for the projector/isinstance lowerings.
        self._current_pyast_classdef_params: Set[str] = (
            {p for p, a in (func.get("param_ast_node_types") or {}).items()
             if a == "ClassDef"}
            if self._uses_pyast_stmt() else set())
        # J2/J3 convergence (module-body dispatch): the params annotated `ast.Module`
        # (typed `py_module_node`) whose `.body` iterates the module-body psl.
        self._current_pyast_module_params: Set[str] = (
            {p for p, a in (func.get("param_ast_node_types") or {}).items()
             if a == "Module"}
            if self._uses_pyast_stmt() else set())
        self._pyast_stmt_locals: Set[str] = set()
        # L1 tparam reflection-node ADT (self-tcb-reduction, collector-family unlock): the
        # params annotated `TParamNode` (typed `py_tparam_node`) whose `.type_params`
        # iterates the tparam_list. Gated on `_uses_tparam` so a non-target file leaves
        # these empty (byte-identical). `_tparam_locals` accumulates the per-iteration `tp`
        # loop targets (typed `tparam`) for the projector/isinstance lowerings.
        self._current_tparam_node_params: Set[str] = (
            {p for p, a in (func.get("param_annotations") or {}).items()
             if a == "TParamNode"}
            if self._uses_tparam() else set())
        self._tparam_locals: Set[str] = set()
        # 7a (self-tcb-reduction L4b): locals bound from `getattr(<node>,"type_params",
        # None) or []` — pure aliases for `(type_params_of <node>)` (the assignment emits
        # nothing; `for tp in <local>` iterates the modelled tparam_list). Empty for every
        # function with no such binding -> byte-inert.
        self._tparam_list_aliases: Dict[str, str] = (
            self._prescan_tparam_list_aliases(body_stmts)
            if self._uses_tparam() else {})
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
        # stmt-list-append-mutation wall (C-bucket): a list param appended a `{"stmt":K}`
        # node (fixpoint incl. transitive forwarding) is a caller-visible mutable
        # `ref (seq stmt_ir)` param with a `writes {p}` frame — the SOUND in-place-append
        # model (fable oracle's `push`), NOT the pre-feature `let p = ref (snapshot p)`
        # LOCAL-copy shadow (which was invisible to the caller). Promoted to `_seq_locals`
        # + `local_refs` so `!p` deref, `Seq.snoc`, `Seq.length !p`, `Seq.get !p i` all
        # resolve exactly as for a seq LOCAL; the snapshot-shadow path in `_emit_body_code`
        # is SKIPPED for these (the param IS the ref). Empty for every non-stmt-append
        # program → byte-identical.
        self._stmt_seq_mut_params: Set[str] = set(
            getattr(self, "_func_stmt_seq_mut_params", {}).get(func.get("name"), set()))
        if self._stmt_seq_mut_params:
            self._seq_locals |= self._stmt_seq_mut_params
            local_refs |= self._stmt_seq_mut_params
        # K4/#6 (local/return-position seq-pyval, self-tcb-reduction Tier-5): when the
        # function returns `seq hval` (`-> List[Dict[str, PyVal]]` / `-> List[PyVal]`,
        # `return_value_type == "hval"`), promote the RETURNED list local to
        # `_pyval_seq_locals` so its `.append({...})` snocs a real `<pyval-wrap x>` (not
        # `Seq.snoc !x 0`) and the `return x` is `!x` (no `materialize` seq int -> array
        # int bridge). The var is already in `_seq_locals` (Module5 `seq_promoted_vars`);
        # this subset marks it as the pyval-carrying one. Gated on the corpus-absent
        # `pyval` return sentinel -> byte-inert.
        self._pyval_seq_locals: Set[str] = set()
        if func.get("return_value_type") == "hval":
            _rv = self._returned_var_name(body_stmts)
            if _rv is not None:
                self._pyval_seq_locals.add(_rv)
        # K7 (pyval-chained `.get`, self-tcb-reduction Tier-5): the set of body locals
        # that RECEIVE a heterogeneous `pyval` value — a `.get` on a `map string (option
        # pyval)` self-field, a `.get` on another pyval local, an `x or {}` / `x or []`
        # default over a pyval, or an alias of a pyval local. Computed by a fixpoint over
        # the body (`_prescan_pyval_locals`). A pyval local is `let`-bound immutable
        # (not the int/string `ref` hoist), and its `.get(k)` lowers to the real
        # `match x with PMap m -> Map.get m k | _ -> ...` projection. Gated on a pyval
        # self-field being present -> corpus byte-inert.
        # `_self_field_dict_nu` (used by the prescan seed) reads `_current_self_type`,
        # which `_build_param_list` only sets AFTER this method returns — so seed it here
        # from `func` (harmlessly re-set to the same value there) so a
        # `self.<pyval-field>.get` seed resolves.
        if func.get("kind") == "method" and func.get("self_type"):
            self._current_self_type = whyml_ident(func["self_type"].lower())
        else:
            self._current_self_type = None
        self._pyval_locals: Set[str] = self._prescan_pyval_locals(body_stmts)
        # set-value-model-wall (self-tcb-reduction, Tier-5): the locals of THIS
        # function that are an emitter-local `Set[str]` value (annotated `Set[str]`
        # + `= set()` init). Their `= set()` lowers to `ref (StrSet.empty ())`,
        # `.add(x)` to `s := StrSet.add x !s`, and `in`/`not in` to a program-bool
        # `StrSet.mem` guard. Empty for every corpus function -> byte-inert.
        self._str_set_locals: Set[str] = self._str_set_locals_of(func)
        return local_refs, ghost_vars

    def _prescan_pyval_locals(self, body_stmts: List[Dict[str, Any]]) -> Set[str]:
        """K7 (pyval-chained `.get`, self-tcb-reduction Tier-5): fixpoint over the body
        collecting locals whose value is a heterogeneous `pyval`. Seeds:
          - `t = <recv>.get(k[, {}])` where <recv> is a `map string (option hval)`
            self-field (value_type "hval") -> `t` is hval (unwrapped `Some v_ -> v_`);
          - `t = <pyval-local>.get(k[, {}])` -> `t` is pyval;
          - `t = <pyval-producing> or {}` / `or []` -> `t` is pyval;
          - `t = <pyval-local>` (alias) -> `t` is pyval.
        Iterated to a fixpoint so a chain `registry = self.f.get(..); info =
        registry.get(..); bound = info.get(..)` all resolve. Returns the empty set for
        every function with no pyval self-field / pyval `.get` -> byte-inert."""
        pyval: Set[str] = set()

        def _rhs_is_pyval(v: Dict[str, Any]) -> bool:
            if not isinstance(v, dict):
                return False
            vt = v.get("type")
            # `x or {}` / `x or []`: the BinOp "or" left operand carries the value.
            if vt == "BinOp" and v.get("op") == "or":
                return _rhs_is_pyval(v.get("left") or {})
            # a `.get(...)` call on a pyval receiver (self-field or pyval local).
            if vt == "Call":
                fn = v.get("func", "")
                if isinstance(fn, str) and fn.endswith(".get"):
                    recv = fn[:-len(".get")]
                    if recv in pyval:
                        return True
                    # a `map string (option hval)` self-field receiver.
                    if self._self_field_dict_nu(recv) == "hval":
                        return True
                return False
            # alias of a pyval local.
            if vt == "Var":
                return v.get("name") in pyval
            return False

        # 7c (self-tcb-reduction L4b): a pyval-producing assignment can be NESTED inside
        # an If/For/While/Try/With body (e.g. `_collect_type_params`'s legacy branch
        # `registry = self.program_ir.get(..) or {}; info = registry.get(nm, {})` sits
        # two loops deep). Gather every Assign in the statement subtree so the fixpoint
        # resolves the chain regardless of nesting depth (byte-inert: a corpus function
        # with no pyval self-field / pyval `.get` still yields the empty set).
        assigns: List[Dict[str, Any]] = []

        def _gather_assigns(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign":
                    assigns.append(node)
                for _k in ("body", "orelse", "finalbody", "handlers"):
                    _v = node.get(_k)
                    if isinstance(_v, list):
                        _gather_assigns(_v)
            elif isinstance(node, list):
                for _s in node:
                    _gather_assigns(_s)

        _gather_assigns(body_stmts)

        changed = True
        while changed:
            changed = False
            for st in assigns:
                tgt = st.get("target")
                if not isinstance(tgt, str) or tgt in pyval:
                    continue
                if _rhs_is_pyval(st.get("value") or {}):
                    pyval.add(tgt)
                    changed = True
        return pyval

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
             "frozenset": "map int (option int)", "tuple": "array int",
             # self-tcb-reduction giants: an `Optional[ast.expr]` local's Some-arm
             # carries the already-lowered emit_ir sub-node.
             "emit_ir": "emit_ir"}
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

    # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): the COMPOUND
    # statement kinds a `_process_*` handler returns (`{"stmt": K}` → SWhile/
    # SIf/SFor). Nullary/return/expr kinds are NOT here (they never head a
    # `_process_*` return; they append at the `.append` site).
    _COMPOUND_STMT_RETURN_KINDS = frozenset({"While", "If", "For"})

    @staticmethod
    def _compound_stmt_dict_kind(v: Any) -> Optional[str]:
        """The compound statement kind K (While/If/For) if `v` is a `{"stmt": K, ...}`
        DictLit with a STRING `stmt` value in `_COMPOUND_STMT_RETURN_KINDS`, else None."""
        if not (isinstance(v, dict) and v.get("type") == "DictLit"):
            return None
        for k, vv in zip(v.get("keys", []) or [], v.get("values", []) or []):
            if (isinstance(k, dict) and k.get("type") == "String"
                    and k.get("value") == "stmt"
                    and isinstance(vv, dict) and vv.get("type") == "String"
                    and vv.get("value") in FunctionEmissionMixin._COMPOUND_STMT_RETURN_KINDS):
                return vv.get("value")
        return None

    def _returns_stmt_ir(self, body_stmts: List[Dict[str, Any]]) -> bool:
        """SUB-BODY recursion (C-bucket): True if the function RETURNS a constructed
        COMPOUND statement node — either a `return {"stmt": "While"/"If"/"For", ...}`
        dict LITERAL (the `_process_while`/`_process_if` return) OR a `return <local>`
        whose local is BOUND to such a compound dict-literal (the `_process_for`
        BUILD-UP shape `d = {"stmt":"For",..}; ..; return d`, recognized by
        `_recognize_stmtir_builder`). Drives the `stmt_ir` return-type override so
        `_py_stmt_*`'s `ir_stmts.append(self._process_*(stmt))` snocs a real `stmt_ir`
        value. @mutable_state-gated by the caller → False (inert) for the corpus."""
        # Top-level locals bound to a compound `{"stmt":K}` dict-literal (the build-up
        # local's binding). Only same-level assigns feed the same-level `return <local>`.
        compound_locals = {
            st.get("target") for st in body_stmts
            if (isinstance(st, dict) and st.get("stmt") == "Assign"
                and isinstance(st.get("target"), str)
                and self._compound_stmt_dict_kind(st.get("value")) is not None)}
        found = [False]

        def rec(n: Any) -> None:
            if isinstance(n, dict):
                if n.get("stmt") == "Return":
                    v = n.get("value")
                    if self._compound_stmt_dict_kind(v) is not None:
                        found[0] = True
                    elif (isinstance(v, dict) and v.get("type") == "Var"
                          and v.get("name") in compound_locals):
                        found[0] = True
                for x in n.values():
                    rec(x)
            elif isinstance(n, list):
                for x in n:
                    rec(x)
        rec(body_stmts)
        return found[0]

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

    def _recognize_stmtir_builder(
            self, func: Dict[str, Any],
            body_stmts: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """SUB-BODY recursion (self-tcb-reduction M5, C-bucket) BUILD-UP-DICT recognizer:
        recognize a COMPOUND statement handler that BUILDS its node dict INCREMENTALLY
        rather than returning a dict LITERAL — the `_process_for` shape

            target = <prelude>                                   (0..n leading Assign's)
            d = {"stmt": "For", "iter": .., "body": .., ...}
            if <guard>: d["tuple_targets"] = <V>                 (0..n conditional-adds)
            return d

        and REWRITE it to a single `Return` of the base construction dict, so the normal
        `_returns_stmt_ir` / `_lower_stmt_ir_construction` path emits `(SFor <iter>
        (seq_to_sl <body>))`. The SFor ctor reads only iter+body (`_STMT_IR_CTORS["For"]`);
        the DROPPED fields (target/line/invariants/variants/lineno/allow_iteration_mutation
        and the conditionally-added tuple_targets) are the same emitter-model-irrelevant
        children SWhile/SIf already drop (line/invariants/variants/orelse) — never lowered,
        so their AST-node-typed values (isinstance/attribute reads over `node.target`, the
        pure_ast boundary) are never emitted. TAG-PRESERVING (SFor, never erased): the node,
        its "For" tag and its real seq_to_sl sub-body are all carried. Fail-closed: None on
        any mismatch (a leading non-Assign, a conditional-add that is not an `if C: d[F]=V`,
        a ctor-payload field that references a dropped prelude local, or a kind not in
        `_STMT_IR_COMPOUND_KINDS`) → the body keeps its normal lowering. @mutable_state-gated
        (the emitter model) → corpus byte-inert."""
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
        # Locate the `d = {DictLit stmt:<compound>}` assignment (need not be first — a
        # `_process_for`-shaped handler assigns a prelude local before it).
        d_idx = None
        dlit = None
        for i, st in enumerate(body_stmts[:-1]):
            if (st.get("stmt") == "Assign" and st.get("target") == dname
                    and isinstance(st.get("value"), dict)
                    and st["value"].get("type") == "DictLit"):
                d_idx = i
                dlit = st["value"]
        if dlit is None:
            return None
        base: Dict[str, Any] = {}
        for k, v in zip(dlit.get("keys", []) or [], dlit.get("values", []) or []):
            if not (isinstance(k, dict) and k.get("type") == "String"):
                return None
            base[k.get("value")] = v
        kind_ir = base.get("stmt")
        if not (isinstance(kind_ir, dict) and kind_ir.get("type") == "String"):
            return None
        if kind_ir.get("value") not in self._STMT_IR_COMPOUND_KINDS:
            return None
        # Prelude (before the d-assign): Assign-only locals, DROPPED. Sound iff the ctor's
        # kept payload fields (iter/body) do not reference a dropped local.
        dropped_locals: Set[str] = set()
        for st in body_stmts[:d_idx]:
            if st.get("stmt") != "Assign":
                return None
            tgt = st.get("target")
            if isinstance(tgt, str):
                dropped_locals.add(tgt)
        cname_payload = self._STMT_IR_CTORS.get(kind_ir.get("value"))
        kept_fields = [f for f, _ck in (cname_payload[1] if cname_payload else [])]

        def _refs_dropped(n: Any) -> bool:
            if isinstance(n, dict):
                if (n.get("type") == "Var" and n.get("name") in dropped_locals):
                    return True
                return any(_refs_dropped(x) for x in n.values())
            if isinstance(n, list):
                return any(_refs_dropped(x) for x in n)
            return False
        for f in kept_fields:
            if f in base and _refs_dropped(base[f]):
                return None
        # Conditional-adds (between the d-assign and the return): each an `if <guard>:
        # d[F] = V` (single ArraySet on d, no else) — the DROPPED optional fields. Verify
        # the shape and drop them (the added field is not in the SFor ctor payload).
        for st in body_stmts[d_idx + 1:-1]:
            if st.get("stmt") != "If" or st.get("orelse"):
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
        return [{"stmt": "Return", "value": dlit}]

    # SAssert increment (self-tcb-reduction M5, C-bucket): the statement kinds whose
    # `_py_stmt_*` handler is a BUILD-UP-THEN-APPEND (bind a `{"stmt":K}` node local,
    # conditionally attach an optional field, then `ir_stmts.append(<local>)`) rather
    # than a build-up-then-RETURN (`_recognize_stmtir_builder`). Only "Assert" today.
    _STMT_IR_APPEND_BUILD_KINDS = frozenset({"Assert"})

    def _recognize_stmt_append_builder(
            self, func: Dict[str, Any],
            body_stmts: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """SAssert increment (self-tcb-reduction M5, C-bucket) BUILD-UP-THEN-APPEND
        recognizer: recognize the `_py_stmt_assert` shape

            ir_node = {"stmt": "Assert", "test": self._py_expr_to_ir(stmt.test)}
            if <guard>: ir_node["msg"] = stmt.msg.value        (0..n conditional-adds)
            ir_stmts.append(ir_node)

        and REWRITE it to a single `ir_stmts.append({"stmt":"Assert","test":..,
        "msg":stmt.msg})` — the conditionally-added optional field FOLDED into the node
        literal as the RAW option field read (`stmt.msg`), which `_lower_stmt_ir_node`'s
        "assert_msg" child kind lowers to the faithful `iropt_str`
        (`match stmt.msg with Some _m -> (if is_str _m then IrSSome (value_of _m) else
        IrSNone) | None -> IrSNone`). The append site then snocs `SAssert (py_expr_to_ir
        stmt.test) <iropt_str>` onto the `ref (seq stmt_ir)` param (the existing
        `_stmt_seq_append_params` marks it mutable — the build-up-then-append seed).

        UNLIKE `_recognize_stmtir_builder` (which DROPS the conditionally-added field),
        this KEEPS it as an option: the `msg` value is re-derived from the SAME `stmt.msg`
        field the conditional-add's value (`stmt.msg.value`) reads, so no field is invented.
        Fail-closed: None on ANY shape mismatch (a prelude local, a wrong terminal, a
        conditional-add that is not `if C: node[F]=stmt.F.value`, an unrecognized kind) →
        the body keeps its normal (unlowered) shape. @mutable_state-gated → corpus
        byte-inert."""
        if (getattr(self, "_current_self_type", None)
                not in getattr(self, "_mutable_state_classes", set())):
            return None
        if len(body_stmts) < 2:
            return None
        # Terminal: `<p>.append(<Var v>)`.
        last = body_stmts[-1]
        if last.get("stmt") not in ("Expr", "ExprStmt"):
            return None
        lv = last.get("value")
        if not (isinstance(lv, dict) and lv.get("type") == "Call"):
            return None
        fn = lv.get("func", "")
        if not (isinstance(fn, str) and fn.endswith(".append")):
            return None
        aargs = lv.get("args") or []
        if len(aargs) != 1:
            return None
        av = aargs[0]
        if not (isinstance(av, dict) and av.get("type") == "Var"):
            return None
        vname = av.get("name")
        # The base node literal must be the FIRST statement (no dropped prelude locals).
        base_st = body_stmts[0]
        if not (base_st.get("stmt") == "Assign" and base_st.get("target") == vname
                and isinstance(base_st.get("value"), dict)
                and base_st["value"].get("type") == "DictLit"):
            return None
        dlit = base_st["value"]
        keys = list(dlit.get("keys", []) or [])
        vals = list(dlit.get("values", []) or [])
        base: Dict[str, Any] = {}
        for k, v in zip(keys, vals):
            if not (isinstance(k, dict) and k.get("type") == "String"):
                return None
            base[k.get("value")] = v
        kind_ir = base.get("stmt")
        if not (isinstance(kind_ir, dict) and kind_ir.get("type") == "String"):
            return None
        skind = kind_ir.get("value")
        if skind not in self._STMT_IR_APPEND_BUILD_KINDS:
            return None
        # Conditional-adds (between base and terminal): each `if <guard>: v[F] = V`
        # (single ArraySet on v, no else). Collect field-name -> value.
        added: Dict[str, Any] = {}
        for st in body_stmts[1:-1]:
            if st.get("stmt") != "If" or st.get("orelse"):
                return None
            ifbody = st.get("body") or []
            if len(ifbody) != 1:
                return None
            aset = ifbody[0]
            if aset.get("stmt") != "ArraySet":
                return None
            arr = aset.get("array")
            if not (isinstance(arr, dict) and arr.get("type") == "Var"
                    and arr.get("name") == vname):
                return None
            idx = aset.get("index")
            if not (isinstance(idx, dict) and idx.get("type") == "String"):
                return None
            added[idx.get("value")] = aset.get("value")
        if skind == "Assert":
            # The ONLY optional field is `msg`, set to `stmt.msg.value`
            # (Attribute(Attribute(Var, "msg"), "value")). Extract `stmt.msg` — the
            # `option emit_ir` field the "assert_msg" child kind reads — as the value's
            # `.object`, so the msg option is derived from the SAME field, never invented.
            if set(added.keys()) != {"msg"}:
                return None
            raw = added["msg"]
            if not (isinstance(raw, dict) and raw.get("type") == "Attribute"
                    and raw.get("attr") == "value"):
                return None
            msg_field = raw.get("object")
            if not (isinstance(msg_field, dict) and msg_field.get("type") == "Attribute"
                    and msg_field.get("attr") == "msg"):
                return None
            new_dlit = {
                "type": "DictLit",
                "keys": keys + [{"type": "String", "value": "msg"}],
                "values": vals + [msg_field],
            }
            return [{
                "stmt": last.get("stmt"),
                "value": {"type": "Call", "func": fn, "args": [new_dlit]},
            }]
        return None

    @staticmethod
    def _is_slice_optfield_ternary(rhs: Any) -> bool:
        """True if `rhs` is the `_py_expr_slice` per-bound ternary shape
        `self.<disp>(expr.F) if expr.F else None` (IR: `IfExpr` with a `None`
        `orelse`, a recursive-IR-dispatcher `Call` body over an `Attribute`
        field read, and a `test` that reads the SAME field). `_lower_sliceN_
        optfield` re-checks the details; this is the shape gate for the body
        rewrite."""
        if not (isinstance(rhs, dict) and rhs.get("type") == "IfExpr"):
            return False
        orelse = rhs.get("orelse")
        if not (isinstance(orelse, dict) and orelse.get("type") == "None"):
            return False
        body = rhs.get("body")
        if not (isinstance(body, dict) and body.get("type") == "Call"):
            return False
        fn = body.get("func")
        if not (isinstance(fn, str)
                and fn.rsplit(".", 1)[-1] in ("_csl_to_ir", "_py_expr_to_ir")):
            return False
        bargs = body.get("args") or []
        if len(bargs) != 1:
            return False
        a0 = bargs[0]
        if not (isinstance(a0, dict) and a0.get("type") in ("Attribute", "FieldGet")):
            return False
        fname = a0.get("attr") or a0.get("field")
        test = rhs.get("test")
        # test reads the SAME optional field (faithful `if expr.F`)
        return (isinstance(test, dict) and test.get("type") in ("Attribute", "FieldGet")
                and (test.get("attr") or test.get("field")) == fname)

    def _recognize_slice_builder(
            self, func: Dict[str, Any],
            body_stmts: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """optional-field ext (monomorphic-option ADTs): recognize the
        `_py_expr_slice` body

            lower = self._py_expr_to_ir(expr.lower) if expr.lower else None   (×N)
            ...
            return {"type": "Slice", "lower": lower, "upper": upper, "step": step}

        — leading local Assigns each bound to the per-bound ternary
        (`_is_slice_optfield_ternary`), then a `Return` of a `{"type":"Slice",
        ...}` DictLit whose non-`type` values are Var refs to exactly those
        locals. Returns a REWRITTEN single-`Return` body whose DictLit is
        re-tagged `"SliceN"` (an internal lowering discriminant DISTINCT from the
        spec-side `_csl_slice` "Slice" → `IrSlice`) with each bound's Var replaced
        INLINE by its ternary, which `_lower_irnode_construction`/
        `_lower_sliceN_optfield` lowers to `(IrSliceN <opt> <opt> <opt>)`.
        Fail-closed: None on any mismatch (body keeps its normal lowering).
        @mutable_state-gated (the emitter model) → corpus byte-inert."""
        if (getattr(self, "_current_self_type", None)
                not in getattr(self, "_mutable_state_classes", set())):
            return None
        if len(body_stmts) < 2:
            return None
        last = body_stmts[-1]
        if last.get("stmt") != "Return":
            return None
        rv = last.get("value")
        if not (isinstance(rv, dict) and rv.get("type") == "DictLit"):
            return None
        keys = rv.get("keys", [])
        values = rv.get("values", [])
        if not keys or len(keys) != len(values):
            return None
        dfields: Dict[str, Any] = {}
        for k, v in zip(keys, values):
            if not (isinstance(k, dict) and k.get("type") == "String"):
                return None
            dfields[k.get("value")] = v
        kind = dfields.get("type")
        if not (isinstance(kind, dict) and kind.get("type") == "String"
                and kind.get("value") == "Slice"):
            return None
        # The leading statements are the per-bound local Assigns (ternary RHS).
        localmap: Dict[str, Any] = {}
        for st in body_stmts[:-1]:
            if st.get("stmt") != "Assign":
                return None
            tgt = st.get("target")
            if not isinstance(tgt, str):
                return None
            if not self._is_slice_optfield_ternary(st.get("value")):
                return None
            localmap[tgt] = st.get("value")
        # Every non-`type` dict value must be a Var ref to one of those locals;
        # inline each with its ternary (and re-tag "type" -> "SliceN").
        new_keys = list(keys)
        new_values = []
        for k, v in zip(keys, values):
            if k.get("value") == "type":
                new_values.append({"type": "String", "value": "SliceN"})
                continue
            if not (isinstance(v, dict) and v.get("type") == "Var"
                    and v.get("name") in localmap):
                return None
            new_values.append(localmap[v.get("name")])
        new_dlit = {"type": "DictLit", "keys": new_keys, "values": new_values}
        return [{"stmt": "Return", "value": new_dlit}]

    @staticmethod
    def _truthiness_guard_field(test: Any) -> Optional[str]:
        """The field name F if `test` is the BARE truthiness guard `node.F`
        (IR: an `Attribute`/`FieldGet` read with no comparison — the
        `if node.ordering:` shape), else None. Distinct from
        `_optfield_guard_name` (which matches the `node.F is not None` BinOp
        form)."""
        if not (isinstance(test, dict) and test.get("type") in ("Attribute", "FieldGet")):
            return None
        obj = test.get("object") or test.get("value")
        if not (isinstance(obj, dict) and obj.get("type") == "Var"):
            return None
        return test.get("attr") or test.get("field")

    def _recognize_functionvariant_builder(
            self, func: Dict[str, Any],
            body_stmts: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """optional-field ext (monomorphic-option ADTs): recognize the TYPE-LESS
        `_csl_function_variant` mutable-dict-conditional-add body

            ir = {"expr": self._csl_to_ir(node.expr)}
            if node.ordering: ir["ordering"] = node.ordering     (0..1 If's)
            return ir

        — a base dict with an `"expr"` key and NO `"type"` key, then 0-or-more
        BARE-truthiness-guarded (`_truthiness_guard_field`) conditional-adds, then
        `return <the dict local>`. Returns a REWRITTEN single-`Return` body whose
        DictLit is tagged with the INTERNAL `"type": "FunctionVariant"`
        discriminant (the source dict is type-less; this tag only routes the
        lowering) plus the merged conditional-add entries, which
        `_lower_irnode_construction`/`_lower_functionvariant_optfield` lowers to
        `(IrFunctionVariant <expr> <iropt_str>)`. Scoped to the type-less-with-
        `expr` shape (only `_csl_function_variant` has it). Fail-closed: None on
        any mismatch. @mutable_state-gated → corpus byte-inert."""
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
        # Scope: type-LESS base with an `expr` key (only _csl_function_variant).
        if "type" in base or "expr" not in base:
            return None
        merged_keys = [{"type": "String", "value": "type"}] + list(keys)
        merged_values = [{"type": "String", "value": "FunctionVariant"}] + list(values)
        for st in body_stmts[1:-1]:
            if st.get("stmt") != "If" or st.get("orelse"):
                return None
            f = self._truthiness_guard_field(st.get("test"))
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

    def _returned_var_name(self, body_stmts: List[Dict[str, Any]]) -> Optional[str]:
        """The name of the variable in the LAST top-level `return <Var>` of `body_stmts`,
        else None. Used to resolve a string-keyed dict return to the returned local's
        faithful `map string (option ν)` type."""
        _last: Optional[str] = None
        for st in body_stmts or []:
            if isinstance(st, dict) and st.get("stmt") == "Return":
                v = st.get("value")
                if isinstance(v, dict) and v.get("type") == "Var":
                    _last = v.get("name")
        return _last

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
        # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): two statement-IR
        # return-type overrides in the emitter model. (1) The trusted sub-body
        # dispatcher `_py_stmts_to_ir` — its result feeds `seq_to_sl` at an
        # SWhile/SIf/SFor ctor arg, so its LOGICAL return type is `seq stmt_ir`,
        # not the `array int` its `-> List[int]` annotation implies. (2) A
        # `_process_while`/`_process_if`/`_process_for` handler RETURNS a compound
        # `{"stmt": While/If/For, ...}` node, so its return type is the `stmt_ir`
        # sum. Both @mutable_state-gated → byte-identical for the corpus.
        if (getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            if func.get("name") == "_py_stmts_to_ir":
                return "seq stmt_ir"
            if self._returns_stmt_ir(body_stmts):
                return "stmt_ir"
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
            # K4/#6 (local/return-position seq-pyval, self-tcb-reduction Tier-5): a
            # `-> List[Dict[str, PyVal]]` / `-> List[PyVal]` return is the faithful
            # growable `seq hval` (the K1 self-field analogue for a RETURNED local) —
            # so a `fields.append({...}); return fields` builds+returns real `pyval`
            # entries instead of the int-erased `array int` + `materialize` (seq int ->
            # array int) bridge that drops the value carrier. `_emit_function` promotes
            # the returned local to `_pyval_seq_locals` so its append is a real
            # `Seq.snoc !fields (<pyval-wrap x>)` and the return is `!fields` (no
            # materialize). `pyval` is a corpus-absent sentinel -> byte-inert.
            elif func.get("return_value_type") == "hval":
                return_type = "seq hval"
        elif ann in ("set", "dict", "frozenset") and return_type == "int":
            return_type = "map int (option int)"
            # self-tcb-reduction giants (generic class-body lowering): a `-> Dict[str, int]`
            # return whose returned dict LOCAL is string-keyed (`constants[target] = iv`,
            # target a string) is the faithful `map string (option int)` — matching the
            # `map_update_some`-built body local (κ=string, ν=int), not the fixed
            # int-keyed default. Gated on a returned string-keyed dict local -> byte-safe.
            _rv = self._returned_var_name(body_stmts)
            if _rv is not None and getattr(self, "_dict_key_types", {}).get(_rv) == "string":
                _nu = getattr(self, "_dict_value_types", {}).get(_rv) or "int"
                # A compound value type (`seq string` for `Dict[str, List[str]]`) MUST be
                # parenthesized inside `option`, else WhyML parses `option seq string` as
                # the bare 0-arg `seq` ("Type symbol seq expects 1 argument but is applied
                # to 0"). Mirrors the byte-safe guard in `_emit_dict_map_type`: a scalar
                # `int` has no space -> no parens -> byte-identical for the corpus.
                _nu_arg = f"({_nu})" if " " in _nu else _nu
                return_type = f"map string (option {_nu_arg})"
        elif ann == "PyVal" and return_type in ("int", "unit"):
            # K7/#6 (scalar pyval return, self-tcb-reduction Tier-5): a `-> PyVal`
            # method (`return info` where `info` is a `pyval` chained-`.get` local)
            # returns the faithful heterogeneous `pyval` carrier, not the int-erased
            # `_union_*`/`int` its opaque body would otherwise imply. `PyVal` is a
            # corpus-absent annotation sentinel -> byte-inert.
            return_type = "hval"
        elif ann == "str" and (return_type == "int"
                or (return_type == "unit" and func.get("trusted"))):
            # self-tcb-reduction GAP #2 (unit-local type inference): a `\trusted`
            # mirror stub whose placeholder body is a bare `pass` yields
            # `find_return_type -> "unit"`, so the plain `return_type == "int"`
            # override misses it and its `val` announces `: unit` — a CONVERTED
            # caller's `ret = self._parse_mixin_type()` local (correctly typed
            # `string` by `_collect_str_call_result_locals`) then fails to
            # type-check against the `unit`-returning `val`. The DECLARED `-> str`
            # annotation is the authority on what a trusted stub returns, so its
            # `val` must announce `string` — the string-return counterpart of the
            # `-> "ExprIR"` unit-stub → `emit_ir` promotion below. Gated on
            # `func["trusted"]`: a real corpus `-> str` function has a return
            # statement (`return_type` never "unit"), so this is byte-identical for
            # the reference corpus (verified: full-corpus byte-diff 0).
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
                and return_type in ("int", "unit")):
            # NODE-CTOR (self-tcb-reduction): `"unit"` covers a still-`\trusted` mirror
            # stub whose placeholder body is a bare `pass` (find_return_type -> "unit")
            # rather than `return {}` ("int"). Its DECLARED annotation is the authority
            # on what it returns, so its `val` must announce `emit_ir` — otherwise a
            # CONVERTED caller's concrete `(<cls>__<m> self)` call is typed `()` and the
            # whole chain fails to type-check. Same 4 IR-node tags, which no corpus
            # program outside a @mutable_state mirror ever uses (byte-identical).
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

    def _is_py_stmt_try(self, func: Dict[str, Any]) -> bool:
        """STry + except_handler + handler_list increment (self-tcb-reduction M5,
        C-bucket): True iff `func` is the Module5 mirror's `_py_stmt_try` handler and
        the stmt_ir theory (STry ctor + AST readers + compaction) is emitted. Keyed on
        the method name + `_uses_stmt_ir()` → no corpus program has a `_py_stmt_try`
        method, so this is corpus-inert (byte-identical everywhere else)."""
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method"
                and (nm.endswith("__py_stmt_try") or nm.endswith("_py_stmt_try"))
                and not nm.endswith("py_stmt_try_x")  # defensive
                and self._uses_stmt_ir())

    def _emit_py_stmt_try_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """STry + except_handler + handler_list increment (self-tcb-reduction M5,
        C-bucket): emit the FAITHFUL whole-body lowering of `_py_stmt_try`:

            body_ir = self._py_stmts_to_ir(stmt.body)
            handlers = []
            for h in stmt.handlers:
                exc_type = None
                if h.type and isinstance(h.type, ast.Name):  exc_type = h.type.id
                elif h.type and isinstance(h.type, ast.Tuple):
                    exc_type = "|".join(n.id for n in h.type.elts
                                        if isinstance(n, ast.Name))
                handlers.append({"exc_type": exc_type, "name": h.name,
                                 "body": self._py_stmts_to_ir(h.body)})
            ir_stmts.append({"stmt":"Try","body":body_ir,"handlers":handlers,
                             "orelse":..., "finalbody":...})

        The `stmt` param is the typed `py_try_node`; `stmt.handlers` a `seq
        ast_excepthandler` read via `try_handlers_ast`. The accumulator `handlers` is a
        REAL `ref (seq except_handler)` grown by `Seq.snoc` of a REAL record (NOT the
        `Seq.snoc 0` erasure). The isinstance dispatch on the option `h.type` matches
        `eh_type_ast h : iropt_ir` then `is_var`/`is_mktuple` (NOT `isinstance_op`);
        `h.type.id -> name_of`, `h.name -> eh_name_ast : iropt_str`, and the Tuple
        `"|".join(...)` -> the CONCRETE `pipe_join (elts_of t)` compaction (NOT a
        length-only law). The Try node is the REAL `STry` ctor with a REAL `handler_list`
        (`seq_to_hl !handlers`, NOT HLNil-erased) + the three `stmt_list` sub-bodies.
        Bespoke because `_py_stmt_try`/`_py_stmt_match` are the only stmt handlers whose
        body is a `for x in stmt.<ast-list-field>: acc.append({rec})` accumulator loop —
        a construct the generic statement lowering int-erases end-to-end. Corpus-inert
        (fires only for this named mirror method under `_uses_stmt_ir`)."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        disp = "self__py_stmts_to_ir_1"
        L = [
            f"  let {name} (self: {cls}) (stmt: py_try_node)"
            f" (ir_stmts: ref (seq stmt_ir)) : unit",
            "    requires { true }",
            "    ensures  { true }",
            "    writes { ir_stmts }",
            "  =",
            "    let hs = try_handlers_ast stmt in",
            "    let handlers = ref (Seq.empty: seq except_handler) in",
            "    let _i = ref 0 in",
            "    while !_i < Seq.length hs do",
            "      invariant { 0 <= !_i <= Seq.length hs }",
            "      variant { Seq.length hs - !_i }",
            "      let h = Seq.get hs !_i in",
            "      let exc_type = (match eh_type_ast h with",
            "        | IrONone -> IrSNone",
            "        | IrOSome t -> if is_var t then IrSSome (name_of t)",
            "          else (if is_mktuple t then IrSSome (pipe_join (elts_of t))",
            "                else IrSNone)",
            "        end) in",
            "      handlers := Seq.snoc !handlers",
            "        { eh_exc_type = exc_type;",
            "          eh_name = eh_name_ast h;",
            f"          eh_body = seq_to_sl ({disp} (eh_body_ast h)) }};",
            "      _i := !_i + 1",
            "    done;",
            "    ir_stmts := Seq.snoc !ir_stmts",
            f"      (STry (seq_to_sl ({disp} (try_body_ast stmt)))",
            "            (seq_to_hl !handlers)",
            f"            (seq_to_sl ({disp} (try_orelse_ast stmt)))",
            f"            (seq_to_sl ({disp} (try_finalbody_ast stmt))))",
        ]
        return L

    def _is_py_stmt_match(self, func: Dict[str, Any]) -> bool:
        """SMatch + match_case + match_case_list increment (self-tcb-reduction M5,
        C-bucket): True iff `func` is the mirror's `_py_stmt_match` handler and the
        stmt_ir theory is emitted. Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method"
                and nm.endswith("_py_stmt_match")
                and self._uses_stmt_ir())

    def _emit_py_stmt_match_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """SMatch + match_case + match_case_list increment (self-tcb-reduction M5,
        C-bucket): the FAITHFUL whole-body lowering of `_py_stmt_match`:

            subject_ir = self._py_expr_to_ir(stmt.subject)
            cases = []
            for case in stmt.cases:
                pattern_ir = self._match_pattern_to_ir(case.pattern)
                guard_ir = self._py_expr_to_ir(case.guard) if case.guard else None
                body_ir = self._py_stmts_to_ir(case.body)
                cases.append({"pattern": pattern_ir, "guard": guard_ir, "body": body_ir})
            ir_stmts.append({"stmt":"Match","subject":subject_ir,"cases":cases})

        Sibling of `_emit_py_stmt_try_bespoke`: `stmt` : the typed `py_match_node`;
        `stmt.cases` : `seq ast_match_case`; the accumulator `cases` : a REAL `ref
        (seq match_case)` grown by `Seq.snoc` of a REAL `{ mc_pattern; mc_guard;
        mc_body }` record (NOT `Seq.snoc 0`). `mc_pattern` is a REAL emit_ir (the
        `_match_pattern_to_ir` pattern dispatcher, folded into `mc_pattern_ir`, NOT
        int-erased); `mc_guard` the `disp(case.guard) if case.guard else None` optional
        (`match mc_guard_ast case with IrONone -> IrONone | IrOSome g -> IrOSome
        (disp g)`); `mc_body` the case body sub-list (`seq_to_sl`). The Match node ->
        a REAL `SMatch (disp stmt.subject) (seq_to_mcl cases)` (NOT MCNil-erased).
        Corpus-inert (fires only for this named mirror method under `_uses_stmt_ir`)."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        disp_e = "self__py_expr_to_ir_1"
        disp_s = "self__py_stmts_to_ir_1"
        L = [
            f"  let {name} (self: {cls}) (stmt: py_match_node)"
            f" (ir_stmts: ref (seq stmt_ir)) : unit",
            "    requires { true }",
            "    ensures  { true }",
            "    writes { ir_stmts }",
            "  =",
            "    let cs = match_cases_ast stmt in",
            "    let cases = ref (Seq.empty: seq match_case) in",
            "    let _i = ref 0 in",
            "    while !_i < Seq.length cs do",
            "      invariant { 0 <= !_i <= Seq.length cs }",
            "      variant { Seq.length cs - !_i }",
            "      let _c = Seq.get cs !_i in",
            "      cases := Seq.snoc !cases",
            "        { mc_pattern = mc_pattern_ir _c;",
            "          mc_guard = (match mc_guard_ast _c with",
            "                      | IrONone -> IrONone",
            f"                      | IrOSome g -> IrOSome ({disp_e} g)",
            "                      end);",
            f"          mc_body = seq_to_sl ({disp_s} (mc_body_ast _c)) }};",
            "      _i := !_i + 1",
            "    done;",
            "    ir_stmts := Seq.snoc !ir_stmts",
            f"      (SMatch ({disp_e} (match_subject_ast stmt)) (seq_to_mcl !cases))",
        ]
        return L

    def _is_py_stmt_delete(self, func: Dict[str, Any]) -> bool:
        """SDelSubscript increment (self-tcb-reduction M5, C-bucket): True iff `func` is
        the mirror's `_py_stmt_delete` handler and the stmt_ir theory is emitted.
        Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method"
                and nm.endswith("_py_stmt_delete")
                and self._uses_stmt_ir())

    def _emit_py_stmt_delete_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """SDelSubscript increment (self-tcb-reduction M5, C-bucket): the FAITHFUL
        whole-body lowering of `_py_stmt_delete`:

            for tgt in stmt.targets:
                slice_node = getattr(tgt, "slice", None)
                # (the py<3.9 `ast.Index` unwrap is DEAD on 3.9+/3.14 — dropped, like
                #  augassign/subscript; byte-diff-0)
                if isinstance(tgt, ast.Subscript) and not isinstance(slice_node, ast.Slice):
                    ir_stmts.append({"stmt":"DelSubscript","array":self._py_expr_to_ir(
                        tgt.value),"index":self._py_expr_to_ir(slice_node)})
                else:
                    ir_stmts.append({"stmt":"Pass"})

        CRUX-1 (loop-append-to-OUTER): unlike try/match (which accumulate a LOCAL
        record-list then append once), this loop `Seq.snoc`s DIRECTLY onto the
        caller-visible `ir_stmts` ref per element — a real `for i in 0..Seq.length
        targets` loop with a `writes { ir_stmts }` frame, invariant `0 <= i <= len`,
        variant `len - i`. CRUX-2 (`getattr(tgt,"slice",None)`): `.slice` exists exactly
        when `tgt` is a Subscript (IrSub), so the getattr-with-default folds into the
        `is_sub tgt` guard — `slice_node = if is_sub tgt then IrOSome (sindex_of tgt)
        else IrONone`, and `not isinstance(slice_node, ast.Slice)` reduces (under the
        `is_sub tgt` conjunct) to `not (is_slice (sindex_of tgt))`. `isinstance(tgt,
        ast.Subscript)` -> `is_sub tgt`; `isinstance(_, ast.Slice)` -> `is_slice` — NO
        isinstance_op. `tgt.value` -> `svalue_of tgt` (IrSub array), `slice_node` ->
        `sindex_of tgt` (IrSub index), both re-lowered by the trusted `_py_expr_to_ir`.
        The subscript-delete appends a REAL `SDelSubscript` (array, index); every other
        target appends `SPass`. Corpus-inert (fires only for this named mirror method
        under `_uses_stmt_ir`)."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        disp_e = "self__py_expr_to_ir_1"
        L = [
            f"  let {name} (self: {cls}) (stmt: py_delete_node)"
            f" (ir_stmts: ref (seq stmt_ir)) : unit",
            "    requires { true }",
            "    ensures  { true }",
            "    writes { ir_stmts }",
            "  =",
            "    let ts = del_targets_ast stmt in",
            "    let _i = ref 0 in",
            "    while !_i < Seq.length ts do",
            "      invariant { 0 <= !_i <= Seq.length ts }",
            "      variant { Seq.length ts - !_i }",
            "      let tgt = Seq.get ts !_i in",
            "      (if is_sub tgt && not (is_slice (sindex_of tgt)) then",
            f"         ir_stmts := Seq.snoc !ir_stmts (SDelSubscript"
            f" ({disp_e} (svalue_of tgt)) ({disp_e} (sindex_of tgt)))",
            "       else",
            "         ir_stmts := Seq.snoc !ir_stmts SPass);",
            "      _i := !_i + 1",
            "    done",
        ]
        return L

    def _is_py_stmt_assign(self, func: Dict[str, Any]) -> bool:
        """SFieldAssign/SArraySliceSet/STupleUnpack increment (self-tcb-reduction M5,
        C-bucket): True iff `func` is the mirror's `_py_stmt_assign` handler and the
        stmt_ir theory is emitted. Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method"
                and nm.endswith("_py_stmt_assign")
                and self._uses_stmt_ir())

    def _emit_py_stmt_assign_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """SFieldAssign/SArraySliceSet/STupleUnpack increment (self-tcb-reduction M5,
        C-bucket): the FAITHFUL whole-body lowering of `_py_stmt_assign` (the biggest
        remaining stmt handler, 5 target-shape branches). `stmt` : the typed
        `py_assign_node`; `target = stmt.targets[0]` -> `assign_target0_ast stmt` (the
        HEAD target); `value = self._py_expr_to_ir(stmt.value)` -> `assign_value_ast stmt`.

        Branches (isinstance on the emit_ir target -> ADT discriminants, isinstance_op=0):
          - Name (`is_var target`) -> SAssign (name_of target) value.
          - self-Attribute (`is_attribute target` && `is_var (avalue_of target)` &&
            `str_eq_op (name_of (avalue_of target)) "self"`) -> SFieldAssign "self"
            (name_of target) value.
          - symtab-Attribute (... && `symtab_mem (name_of (avalue_of target))`, the opaque
            `target.value.id in self._cur_func_symtab` membership) -> SFieldAssign
            (name_of (avalue_of target)) (name_of target) value.
          - non-Name-Attribute (`not (is_var (avalue_of target))`) -> `raise
            PyCSLSemanticError` (the out-of-scope diagnostic; the f-string message +
            `type().__name__` reflection + kwargs are dropped — a raise takes only the
            exc NAME, and the raise path does not reach `ensures`).
          - else (Name base not in symtab, module-global) -> no-op.
          - Subscript (`is_sub target`): slice (`is_slice (sindex_of target)`) ->
            SArraySliceSet (disp (svalue_of target)) <lower iropt_ir> <upper iropt_ir>
            value (lower defaults to IrNum 0 when absent, upper stays IrONone — the
            sliceN_lower_of/sliceN_upper_of optional bounds); else -> SArraySet (disp
            (svalue_of target)) (disp (sindex_of target)) value.
          - Tuple (`is_mktuple target`) -> STupleUnpack (var_names_prog (elts_of target))
            value — the CONCRETE `[elt.id for elt in target.elts if isinstance(elt,
            ast.Name)]` compaction (`var_names_of` filter+project), NOT the abstract
            length-only law (the fable vacuity trap).
        Corpus-inert (fires only for this named mirror method under `_uses_stmt_ir`)."""
        # str_eq_op — the `target.value.id == 'self'` guard's string equality (the same
        # abstract op the normal string-comparison lowering registers).
        self._add_abstract_op(
            "val str_eq_op (a b: string) : bool\n"
            "    ensures { result <-> a = b }")
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        d = "self__py_expr_to_ir_1"
        L = [
            f"  let {name} (self: {cls}) (stmt: py_assign_node)"
            f" (ir_stmts: ref (seq stmt_ir)) : unit",
            "    requires { true }",
            "    ensures  { true }",
            "    raises { PyCSLSemanticError }",
            "    writes { ir_stmts }",
            "  =",
            "    let target = assign_target0_ast stmt in",
            "    let value = assign_value_ast stmt in",
            "    if is_var target then",
            "      ir_stmts := Seq.snoc !ir_stmts (SAssign (name_of target) value)",
            "    else if is_attribute target then",
            "      (if is_var (avalue_of target)"
            " && str_eq_op (name_of (avalue_of target)) \"self\" then",
            "         ir_stmts := Seq.snoc !ir_stmts"
            " (SFieldAssign \"self\" (name_of target) value)",
            "       else if is_var (avalue_of target)"
            " && symtab_mem (name_of (avalue_of target)) then",
            "         ir_stmts := Seq.snoc !ir_stmts"
            " (SFieldAssign (name_of (avalue_of target)) (name_of target) value)",
            "       else if not (is_var (avalue_of target)) then",
            "         raise PyCSLSemanticError",
            "       else ())",
            "    else if is_sub target then",
            "      (if is_slice (sindex_of target) then",
            "         (let lower = (match sliceN_lower_of (sindex_of target) with",
            f"                       | IrOSome lo -> IrOSome ({d} lo)",
            "                       | IrONone -> IrOSome (IrNum 0) end) in",
            "          let upper = (match sliceN_upper_of (sindex_of target) with",
            f"                       | IrOSome up -> IrOSome ({d} up)",
            "                       | IrONone -> IrONone end) in",
            "          ir_stmts := Seq.snoc !ir_stmts"
            f" (SArraySliceSet ({d} (svalue_of target)) lower upper value))",
            "       else",
            "         ir_stmts := Seq.snoc !ir_stmts"
            f" (SArraySet ({d} (svalue_of target)) ({d} (sindex_of target)) value))",
            "    else if is_mktuple target then",
            "      ir_stmts := Seq.snoc !ir_stmts"
            " (STupleUnpack (var_names_prog (elts_of target)) value)",
            "    else ()",
        ]
        return L

    def _is_py_expr_lambda(self, func: Dict[str, Any]) -> bool:
        """_py_expr_lambda increment (self-tcb-reduction M5, C-bucket): True iff `func`
        is the mirror's `_py_expr_lambda` handler and the stmt_ir theory is emitted.
        Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method"
                and nm.endswith("_py_expr_lambda")
                and self._uses_stmt_ir())

    def _emit_py_expr_lambda_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """_py_expr_lambda increment (self-tcb-reduction M5, C-bucket): the FAITHFUL
        whole-body lowering of `_py_expr_lambda`:

            params = [arg.arg for arg in expr.args.args]
            return {"type":"Lambda","params":params,"body":self._py_expr_to_ir(expr.body)}

        `expr` : the typed `py_lambda_node`; the `[arg.arg for arg in expr.args.args]`
        param-name projection -> the CONCRETE `lambda_param_names_prog (lambda_args_ast
        expr)` compaction (`name_of` over the args irlist, into IrVar param-name nodes,
        NOT an abstract length-only law); `expr.body` -> `lambda_body_ast` re-lowered.
        Returns the new gated `IrLambda <params irlist> <body>` emit_ir ctor.
        isinstance_op = 0. Corpus-inert."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        L = [
            f"  let {name} (self: {cls}) (expr: py_lambda_node) : emit_ir",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    (IrLambda (lambda_param_names_prog (lambda_args_ast expr))"
            " (self__py_expr_to_ir_1 (lambda_body_ast expr)))",
        ]
        return L

    def _expr_bespoke_body(self, func: Dict[str, Any], param_ty: str,
                           body_expr: str) -> List[str]:
        """Shared scaffold for a RETURN-value `_py_expr_*` bespoke: a `let <name> (self)
        (expr: <param_ty>) : emit_ir = <body_expr>` block. Corpus-inert (each caller keys
        on a named mirror method under `_uses_stmt_ir`)."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        return [
            f"  let {name} (self: {cls}) (expr: {param_ty}) : emit_ir",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            f"    {body_expr}",
        ]

    # base bool-recognizers (self-tcb-reduction M5, C-bucket): the class-base existence
    # recognizers, keyed on method name -> the target base string. Corpus-inert.
    _BASE_RECOGNIZERS = {
        "_is_typeddict_class": "TypedDict",
        "_is_namedtuple_class": "NamedTuple",
        "_is_protocol_class": "Protocol",
    }

    def _base_recognizer_target(self, func: Dict[str, Any]) -> Optional[str]:
        """base bool-recognizers: the target base name iff `func` is one of the three
        class-base recognizers and the stmt_ir theory is emitted; else None. Corpus-inert
        (no corpus program has these methods)."""
        if not self._uses_stmt_ir():
            return None
        nm = str(func.get("name", ""))
        for tail, target in self._BASE_RECOGNIZERS.items():
            if nm.endswith(tail):
                return target
        return None

    def _emit_base_recognizer_bespoke(self, func: Dict[str, Any],
                                      target: str) -> List[str]:
        """base bool-recognizers: emit the FAITHFUL whole-body lowering of
        `_is_typeddict_class`/`_is_namedtuple_class`/`_is_protocol_class`:

            for b in node.bases:
                if isinstance(b, ast.Name) and b.id == "<Base>": return True
                if isinstance(b, ast.Attribute) and b.attr == "<Base>": return True
            return False

        -> `bases_has_name "<Base>" (class_bases_ast node)` — the CONCRETE existence fold
        over the bases irlist (a base matches iff it is a Name/Attribute whose head name
        equals the target; `name_of` covers both `b.id` and `b.attr`). isinstance_op = 0,
        `assigns \nothing` (pure bool). Two are @staticmethod (no self param); one carries
        self. Corpus-inert."""
        name = whyml_ident(func["name"])
        # @staticmethod recognizers take no self; the self one prepends `(self: <cls>)`.
        is_static = (func.get("is_static") or func.get("staticmethod")
                     or not func.get("self_type"))
        self_part = ("" if is_static
                     else f"(self: {whyml_ident(func['self_type'].lower())}) ")
        return [
            f"  let {name} {self_part}(node: py_classdef_node) : bool",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            f"    bases_has_name_prog \"{target}\" (class_bases_ast node)",
        ]

    def _is_final_annotation(self, func: Dict[str, Any]) -> bool:
        """_is_final_annotation bool-recognizer (self-tcb-reduction M5, C-bucket):
        corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (nm.endswith("_is_final_annotation") and self._uses_stmt_ir())

    def _emit_is_final_annotation_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """_is_final_annotation bool-recognizer: `is_final_ann_prog ann_expr` — the
        CONCRETE fixed-shape Final/Final[T] discriminant chain. isinstance_op = 0,
        `assigns \nothing`. @staticmethod (the tool still gives it self). Corpus-inert."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        return [
            f"  let {name} (self: {cls}) (ann_expr: emit_ir) : bool",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    is_final_ann_prog ann_expr",
        ]

    def _is_py_expr_dict(self, func: Dict[str, Any]) -> bool:
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method" and nm.endswith("_py_expr_dict")
                and self._uses_stmt_ir())

    def _emit_py_expr_dict_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """_py_expr_dict increment: `keys=[disp(k) if k else None for k in expr.keys];
        values=[disp(v) for v in expr.values]; return {DictLit, keys, values}`. The DUAL
        child-list -> the CONCRETE `dict_keys_prog` (None-guarded keys map) +
        `dict_values_prog` (plain values map); the new gated IrDictLit ctor carries both
        irlists. isinstance_op = 0. Corpus-inert."""
        return self._expr_bespoke_body(
            func, "py_dict_node",
            "(IrDictLit (dict_keys_prog (dict_keys_ast expr))"
            " (dict_values_prog (dict_values_ast expr)))")

    def _is_py_expr_listcomp(self, func: Dict[str, Any]) -> bool:
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method" and nm.endswith("_py_expr_listcomp")
                and self._uses_stmt_ir())

    def _emit_py_expr_listcomp_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """_py_expr_listcomp increment: `{ListComp, disp(expr.elt),
        self._comprehension_generators_to_ir(expr.generators)}`. FIXED-CHILD: elt via
        `_py_expr_to_ir`, generators via the trusted `listcomp_gens_ir` (like
        `_match_pattern_to_ir`). The new gated IrListComp ctor. isinstance_op = 0."""
        return self._expr_bespoke_body(
            func, "py_listcomp_node",
            "(IrListComp (self__py_expr_to_ir_1 (listcomp_elt_ast expr))"
            " (listcomp_gens_ir expr))")

    def _is_py_expr_genexp(self, func: Dict[str, Any]) -> bool:
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method" and nm.endswith("_py_expr_genexp")
                and self._uses_stmt_ir())

    def _emit_py_expr_genexp_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """genexp-erasure-wall R2a: sibling of listcomp -> the gated IrGenExp ctor, so the
        mirror's `_py_expr_genexp` reads its `expr` parameter for real instead of erasing it
        (bin/check-emitted-vacuity.py flagged the erasing version as a NEW facade)."""
        return self._expr_bespoke_body(
            func, "py_genexp_node",
            "(IrGenExp (self__py_expr_to_ir_1 (genexp_elt_ast expr))"
            " (genexp_gens_ir expr))")

    def _is_py_expr_setcomp(self, func: Dict[str, Any]) -> bool:
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method" and nm.endswith("_py_expr_setcomp")
                and self._uses_stmt_ir())

    def _emit_py_expr_setcomp_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """_py_expr_setcomp increment: sibling of listcomp -> the gated IrSetComp ctor."""
        return self._expr_bespoke_body(
            func, "py_setcomp_node",
            "(IrSetComp (self__py_expr_to_ir_1 (setcomp_elt_ast expr))"
            " (setcomp_gens_ir expr))")

    def _is_py_expr_dictcomp(self, func: Dict[str, Any]) -> bool:
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method" and nm.endswith("_py_expr_dictcomp")
                and self._uses_stmt_ir())

    def _emit_py_expr_dictcomp_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """_py_expr_dictcomp increment: `{DictComp, disp(expr.key), disp(expr.value),
        generators}` -> the gated IrDictComp ctor (key + value + generators). isinstance_op
        = 0."""
        return self._expr_bespoke_body(
            func, "py_dictcomp_node",
            "(IrDictComp (self__py_expr_to_ir_1 (dictcomp_key_ast expr))"
            " (self__py_expr_to_ir_1 (dictcomp_value_ast expr)) (dictcomp_gens_ir expr))")

    def _is_emit_ghost_assign(self, func: Dict[str, Any]) -> bool:
        """SGhostArraySet/SGhostAssign increment (self-tcb-reduction M5, C-bucket): True
        iff `func` is the mirror's `_emit_ghost_assign` handler and the stmt_ir theory is
        emitted. Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method"
                and nm.endswith("_emit_ghost_assign")
                and self._uses_stmt_ir())

    def _emit_emit_ghost_assign_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """SGhostArraySet/SGhostAssign increment (self-tcb-reduction M5, C-bucket): the
        FAITHFUL whole-body lowering of `_emit_ghost_assign` (a RETURN-stmt-dict handler):

            if isinstance(ga, GhostArraySetDecl):
                return {"stmt":"GhostArraySet","target":ga.target,
                        "index":self._csl_to_ir(ga.index),"value":self._csl_to_ir(ga.value)}
            return {"stmt":"GhostAssign","target":ga.target,
                    "value":self._csl_to_ir(ga.value),"op":ga.op,
                    "ghost_type":getattr(ga,'declared_type','int')}

        `ga` : the typed `py_ghost_node`; `isinstance(ga, GhostArraySetDecl)` ->
        `ghost_is_arrayset ga` (the opaque CSL-class discriminant, like symtab_mem);
        `ga.target`/`ga.op` -> the string readers; `self._csl_to_ir(ga.index/value)` ->
        `csl_to_ir (ghost_index_ast/ghost_value_ast ga)` (the trusted CSL->IR dispatcher);
        `getattr(ga,'declared_type','int')` -> `ghost_declared_type_ast ga` (the default
        folded, like delete's getattr). Returns the REAL `SGhostArraySet` /`SGhostAssign`
        ctor. isinstance_op = 0. `_csl_to_ir` stays \trusted. Corpus-inert."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        L = [
            f"  let {name} (self: {cls}) (ga: py_ghost_node) : stmt_ir",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    if ghost_is_arrayset ga then",
            "      SGhostArraySet (ghost_target_ast ga)"
            " (csl_to_ir (ghost_index_ast ga)) (csl_to_ir (ghost_value_ast ga))",
            "    else",
            "      SGhostAssign (ghost_target_ast ga) (csl_to_ir (ghost_value_ast ga))"
            " (ghost_op_ast ga) (ghost_declared_type_ast ga)",
        ]
        return L

    def _is_py_expr_compare(self, func: Dict[str, Any]) -> bool:
        """_py_expr_compare increment (self-tcb-reduction M5, C-bucket): True iff `func`
        is the mirror's `_py_expr_compare` handler and the stmt_ir theory is emitted.
        Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method"
                and nm.endswith("_py_expr_compare")
                and self._uses_stmt_ir())

    def _emit_py_expr_compare_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """_py_expr_compare increment (self-tcb-reduction M5, C-bucket): the FAITHFUL
        whole-body lowering of `_py_expr_compare`:

            return {"type":"BinOp","op":self._py_op_to_str(expr.ops[0]),
                    "left":self._py_expr_to_ir(expr.left),
                    "right":self._py_expr_to_ir(expr.comparators[0])}

        A RETURN-value expr handler (unlike the stmt handlers which append). `expr` : the
        typed `py_compare_node`; the ast-LIST-HEAD accesses `expr.ops[0]` /
        `expr.comparators[0]` -> the opaque head readers `compare_op0_ast` /
        `compare_comp0_ast` (the same shape as `_py_stmt_assign`'s `stmt.targets[0]`);
        `expr.left` -> `compare_left_ast`. Returns the REAL certified `IrBinOp` ctor with
        the op string (`py_op_to_str (compare_op0_ast expr)`), the left, and the first
        comparator (both `_py_expr_to_ir`-lowered). No new ctor (reuses IrBinOp),
        isinstance_op = 0. Corpus-inert."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        L = [
            f"  let {name} (self: {cls}) (expr: py_compare_node) : emit_ir",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    (IrBinOp (self__py_op_to_str_1 (compare_op0_ast expr))"
            " (self__py_expr_to_ir_1 (compare_left_ast expr))"
            " (self__py_expr_to_ir_1 (compare_comp0_ast expr)))",
        ]
        return L

    def _is_py_expr_boolop(self, func: Dict[str, Any]) -> bool:
        """_py_expr_boolop increment (self-tcb-reduction M5, C-bucket): True iff `func`
        is the mirror's `_py_expr_boolop` handler and the stmt_ir theory is emitted.
        Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method"
                and nm.endswith("_py_expr_boolop")
                and self._uses_stmt_ir())

    def _emit_py_expr_boolop_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """_py_expr_boolop increment (self-tcb-reduction M5, C-bucket): the FAITHFUL
        whole-body lowering of `_py_expr_boolop`:

            op_str = "and" if isinstance(expr.op, ast.And) else "or"
            result = self._py_expr_to_ir(expr.values[0])
            for operand in expr.values[1:]:
                result = {"type":"BinOp","op":op_str,"left":result,
                          "right":self._py_expr_to_ir(operand)}
            return result

        The LEFT-FOLD over `expr.values[1:]` -> the CONCRETE recursive `boolop_fold`
        (each operand re-lowered by the dispatcher, folded into a left-nested IrBinOp
        tree), NOT an abstract length-only law. `isinstance(expr.op, ast.And)` ->
        `boolop_is_and expr`; `expr.values[0]` -> `boolop_val0_ast`; `expr.values[1:]`
        -> `boolop_rest_ast` (irlist). Reuses the certified IrBinOp ctor, isinstance_op =
        0. Corpus-inert."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        L = [
            f"  let {name} (self: {cls}) (expr: py_boolop_node) : emit_ir",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    let op_str = (if boolop_is_and expr then \"and\" else \"or\") in",
            "    boolop_fold op_str (boolop_dispatch (boolop_val0_ast expr))"
            " (boolop_rest_ast expr)",
        ]
        return L

    def _is_py_stmt_with(self, func: Dict[str, Any]) -> bool:
        """SCriticalSection increment (self-tcb-reduction M5, C-bucket): True iff `func`
        is the mirror's `_py_stmt_with` handler and the stmt_ir theory is emitted.
        Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (func.get("kind") == "method"
                and nm.endswith("_py_stmt_with")
                and self._uses_stmt_ir())

    def _emit_py_stmt_with_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """SCriticalSection increment (self-tcb-reduction M5, C-bucket): the FAITHFUL
        whole-body lowering of `_py_stmt_with`:

            mutex = getattr(stmt, 'csl_critical_mutex', None) or getattr(stmt,
                    'csl_acquires', None)
            body_ir = self._py_stmts_to_ir(stmt.body)
            if mutex:
                inv = self._get_mutex_invariant_ir(mutex)
                ir_stmts.append({"stmt":"CriticalSection","mutex":mutex,"body":body_ir,
                                 "assume_invariant":inv,"prove_invariant":inv})
            else:
                ir_stmts.extend(body_ir)

        GATE 0 (the weave-attr crux): `getattr(stmt, 'csl_critical_mutex', None) or
        getattr(stmt, 'csl_acquires', None)` reads WEAVE-INJECTED attrs the generic
        lowering int-erases to 0 (making the CriticalSection branch dead + the extend a
        no-op). The bespoke folds the getattr-or into the opaque `csl_mutex_ast stmt :
        iropt_str` reader (the honest model of the runtime mutex attribute) — the
        `if mutex:` truthiness is the is-Some test, isinstance_op = 0. The two branches:
          - mutex present (`IrSSome m`) -> `SCriticalSection m (seq_to_sl body_ir)
            (mutex_invariant_ir m) (mutex_invariant_ir m)` snoc'd onto ir_stmts.
          - no mutex (`IrSNone`) -> `ir_stmts := !ir_stmts ++ body_ir`, the seq-CONCAT
            extend (`ir_stmts.extend(body_ir)`, a REAL caller-visible mutation under
            `writes { ir_stmts }`, NOT the generic no-op).
        `_get_mutex_invariant_ir` stays \trusted. Corpus-inert."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        disp_s = "self__py_stmts_to_ir_1"
        L = [
            f"  let {name} (self: {cls}) (stmt: py_with_node)"
            f" (ir_stmts: ref (seq stmt_ir)) : unit",
            "    requires { true }",
            "    ensures  { true }",
            "    writes { ir_stmts }",
            "  =",
            f"    let body_ir = {disp_s} (with_body_ast stmt) in",
            "    match csl_mutex_ast stmt with",
            "    | IrSSome m ->",
            "        ir_stmts := Seq.snoc !ir_stmts",
            "          (SCriticalSection m (seq_to_sl body_ir)"
            " (mutex_invariant_ir m) (mutex_invariant_ir m))",
            "    | IrSNone ->",
            "        ir_stmts := !ir_stmts ++ body_ir",
            "    end",
        ]
        return L

    def _emit_deferred_cbw(self, walker_name, whyml_ident) -> List[str]:
        """Append the deferred BODY-WALK `_check_*` caller group(s) whose walker is
        `walker_name` (the just-emitted `_cp_walk`/`_gso_walk`/`_sa_walk`), once
        each. Keyed on the emitted walker's canonical name so each caller lands
        immediately after the walker it calls into (forward-reference resolution)."""
        from module6_whyml.generic_fold import (
            _canon_call, emit_check_body_walk_group)
        if not getattr(self, "_cbw_funcs", None) or walker_name is None:
            return []
        wcanon = _canon_call(walker_name)
        out: List[str] = []
        for f, desc in self._cbw_funcs:
            nm = f.get("name")
            if nm in self._cbw_emitted:
                continue
            if _canon_call(desc["walker_name"]) == wcanon:
                out += emit_check_body_walk_group(desc, whyml_ident)
                self._cbw_emitted.add(nm)
        return out

    def _note_emitted_walker(self, walker_name) -> None:
        """Record a just-emitted `_sa_walk`/`_cp_walk`-family walker's canonical
        name (drives the multi-walker CHECK-SUBSCRIPT-ASSIGNMENTS deferral)."""
        from module6_whyml.generic_fold import _canon_call
        if not hasattr(self, "_emitted_walker_names"):
            self._emitted_walker_names = set()
        if walker_name is not None:
            self._emitted_walker_names.add(_canon_call(walker_name))

    def _emit_deferred_csa(self, whyml_ident) -> List[str]:
        """Append the deferred CHECK-SUBSCRIPT-ASSIGNMENTS caller group(s) once
        ALL of a caller's required walkers (`_sa_immutable_walk` + `_sa_walk`)
        have been emitted (tracked in `_emitted_walker_names`)."""
        from module6_whyml.generic_fold import (
            _canon_call, emit_check_subscript_assignments_group)
        if not getattr(self, "_csa_funcs", None):
            return []
        out: List[str] = []
        for f, desc in self._csa_funcs:
            nm = f.get("name")
            if nm in self._csa_emitted:
                continue
            needed = {_canon_call(desc["imm_walker"]), _canon_call(desc["sa_walker"])}
            if needed <= getattr(self, "_emitted_walker_names", set()):
                out += emit_check_subscript_assignments_group(desc, whyml_ident)
                self._csa_emitted.add(nm)
        return out

    def _emit_function(self, func: Dict[str, Any], scc_info: Dict[str, tuple]) -> List[str]:
        """Emit one WhyML let/val function block. Returns the list of output lines."""
        name = whyml_ident(func["name"])
        # PB-TRIO FUSION (preamble/generic_fold): the `{_pb_stmt,_pb_body,
        # _pb_descend}` triad emits as ONE `let rec` group, DEFERRED to just
        # after the `_pb_expr` group it calls into. Each trio member's own slot
        # emits nothing here; the whole group is appended when `_pb_expr` is
        # emitted (see the `recognize_pbexpr` branch below).
        if getattr(self, "_pb_trio", None) and func.get("name") in self._pb_trio_names:
            return []
        # CS-TRIO FUSION: same deferral — the `{_cs_stmt,_cs_body,_cs_descend}`
        # triad emits as ONE group appended right after the `_cs_clause` group it
        # calls into (see the `recognize_cs_clause` branch below).
        if getattr(self, "_cs_trio", None) and func.get("name") in self._cs_trio_names:
            return []
        # CONCURRENCY CLUSTER (preamble/generic_fold): the 5-function held-mutex
        # / lock-order walk emits as ONE self-contained `let rec` block at the
        # first-reached member's slot; the other four members emit nothing.
        if getattr(self, "_conc_cluster", None) and func.get("name") in self._conc_names:
            if self._conc_emitted:
                return []
            from module6_whyml.generic_fold import emit_conc_cluster_group
            self._conc_emitted = True
            return emit_conc_cluster_group(self._conc_cluster, whyml_ident)
        # FINAL PAIR FUSION (preamble/generic_fold): the `{_final_walk_body,
        # _final_check_stmt}` pair emits as ONE `let rec` group — self-contained
        # (calls nothing external), so the whole group is emitted at whichever
        # member's slot is reached FIRST; the other member emits nothing. This
        # RE-BASES `_final_walk_body` from the `list int` void-dispatch model onto
        # the pyval spine and UN-TRUSTS `_final_check_stmt`.
        if getattr(self, "_final_pair", None) and func.get("name") in self._final_pair_names:
            if self._final_pair_emitted:
                return []
            from module6_whyml.generic_fold import (
                emit_final_pair_group, emit_check_final_group)
            self._final_pair_emitted = True
            lines = emit_final_pair_group(self._final_pair, whyml_ident)
            # CHECK-FINAL CALLER: append the `_check_final` driver group right
            # after the pair it calls into (once). `_check_final`'s own slot
            # emits nothing (deferred forward reference — see the gate below).
            if getattr(self, "_check_final_desc", None):
                lines = lines + emit_check_final_group(
                    self._check_final_desc, whyml_ident)
            return lines
        # CHECK-FINAL CALLER: `_check_final` is a forward reference to the pyval
        # `_final_walk_body` — DEFERRED, emitted with the pair group above. Its
        # own slot emits nothing.
        if getattr(self, "_check_final_name", None) and func.get("name") == self._check_final_name:
            return []
        # CHECK-CONTRACT-EXPRS caller (pdict-to-sdict-impl.md): the heterogeneous
        # `_check_contract_exprs` caller is DEFERRED (forward reference) — emitted
        # after the `_pb_expr` group + pb-trio it calls into (see the
        # `recognize_pbexpr` branch below). Its own slot emits nothing.
        if getattr(self, "_cce_names", None) and func.get("name") in self._cce_names:
            return []
        # BODY-WALK caller siblings (`_check_checkpoints`/`_check_ghost_string_ops`):
        # each is DEFERRED (forward reference) — emitted after its `_cp_walk`/
        # `_gso_walk` walker group (see the `recognize_cpwalk`/`recognize_sawalk`
        # branches below). Its own slot emits nothing.
        if getattr(self, "_cbw_names", None) and func.get("name") in self._cbw_names:
            return []
        # NoReturn dead-successor WALKER + CALLER (ghost-assign-bc6): both are
        # DEFERRED (forward references — the walker calls the textually-later
        # `_stmt_is_noreturn_call`; the caller calls the walker), emitted as one
        # append right after the `_stmt_is_noreturn_call` group (see the
        # `recognize_stmt_noreturn_call` branch below). Their own slots emit nothing.
        if getattr(self, "_nrw_names", None) and func.get("name") in self._nrw_names:
            return []
        if getattr(self, "_ccns_names", None) and func.get("name") in self._ccns_names:
            return []
        # CLOSURE-FORM existence walk (generic_fold.py module note): the lifted
        # `walk` sibling of a recognised `found=[False]` wrapper is SUPPRESSED
        # (emits nothing — the wrapper's self-contained catamorphism does not call
        # it, so no reference is dangled and no name collides across siblings).
        # Keyed on object identity; corpus-inert.
        if id(func) in getattr(self, "_clx_walk_ids", set()):
            return []
        # …and the wrapper itself emits the certified `list pyval` existence
        # catamorphism (proven; NO new type/axiom/cert, ledger 3), de-vacuifying
        # the int-erased `walk body` facade.
        _clx_desc = getattr(self, "_clx_outer_ids", {}).get(id(func))
        if _clx_desc is not None:
            from module6_whyml.generic_fold import emit_closure_existence_group
            return emit_closure_existence_group(func, _clx_desc, whyml_ident)
        # STRING first-match SEARCH closure (`_lemma_calls_trusted`): the lifted
        # `walk` sibling is SUPPRESSED; the wrapper emits the certified first-match
        # search catamorphism (`option string`, `map string bool` set-param
        # membership). Keyed on `id`; corpus-inert. See generic_fold.py note.
        if id(func) in getattr(self, "_lss_walk_ids", set()):
            return []
        _lss_desc = getattr(self, "_lss_outer_ids", {}).get(id(func))
        if _lss_desc is not None:
            from module6_whyml.generic_fold import emit_lemma_string_search_group
            return emit_lemma_string_search_group(func, _lss_desc, whyml_ident)
        # CHECK-SUBSCRIPT-ASSIGNMENTS caller (driver target #2): DEFERRED until
        # both its `_sa_immutable_walk`/`_sa_walk` walker groups are emitted (see
        # the `recognize_sawalk` branch). Its own slot emits nothing.
        if getattr(self, "_csa_names", None) and func.get("name") in self._csa_names:
            return []
        # CHECK-CONTRACT-SCOPE caller (driver target #3): DEFERRED to just after
        # the `_cs_clause` group + cs-trio it calls into (see the
        # `recognize_cs_clause` branch). Its own slot emits nothing.
        if getattr(self, "_ccs_names", None) and func.get("name") in self._ccs_names:
            return []
        # SCriticalSection increment (self-tcb-reduction M5, C-bucket): the `_py_stmt_with`
        # mutex/extend handler — bespoke (the generic lowering int-erases the weave-injected
        # mutex attrs + no-ops the extend). Corpus-inert.
        if self._is_py_stmt_with(func):
            return self._emit_py_stmt_with_bespoke(func)
        # SGhostArraySet/SGhostAssign increment (self-tcb-reduction M5, C-bucket): the
        # `_emit_ghost_assign` RETURN-stmt-dict handler (isinstance-on-CSL-class dispatch).
        # Corpus-inert.
        if self._is_emit_ghost_assign(func):
            return self._emit_emit_ghost_assign_bespoke(func)
        # _py_expr_lambda increment (self-tcb-reduction M5, C-bucket): the lambda-expr
        # handler (param-name compaction + body -> the gated IrLambda ctor). Corpus-inert.
        if self._is_py_expr_lambda(func):
            return self._emit_py_expr_lambda_bespoke(func)
        # base bool-recognizers (self-tcb-reduction M5, C-bucket): the class-base existence
        # recognizers (TypedDict/NamedTuple/Protocol) -> the concrete bases_has_name fold.
        _brt = self._base_recognizer_target(func)
        if _brt is not None:
            return self._emit_base_recognizer_bespoke(func, _brt)
        # _is_final_annotation bool-recognizer -> is_final_ann_prog. Corpus-inert.
        if self._is_final_annotation(func):
            return self._emit_is_final_annotation_bespoke(func)
        # dict/comprehension increments (gated-emit_ir-ctor): IrDictLit (dual compaction) /
        # IrListComp / IrSetComp / IrDictComp (fixed-child + trusted generators). Corpus-inert.
        if self._is_py_expr_dict(func):
            return self._emit_py_expr_dict_bespoke(func)
        if self._is_py_expr_genexp(func):
            return self._emit_py_expr_genexp_bespoke(func)
        if self._is_py_expr_listcomp(func):
            return self._emit_py_expr_listcomp_bespoke(func)
        if self._is_py_expr_setcomp(func):
            return self._emit_py_expr_setcomp_bespoke(func)
        if self._is_py_expr_dictcomp(func):
            return self._emit_py_expr_dictcomp_bespoke(func)
        # _py_expr_compare increment (self-tcb-reduction M5, C-bucket): the ast-LIST-HEAD
        # expr handler (`expr.ops[0]`/`expr.comparators[0]`) -> IrBinOp. Corpus-inert.
        if self._is_py_expr_compare(func):
            return self._emit_py_expr_compare_bespoke(func)
        # _py_expr_boolop increment (self-tcb-reduction M5, C-bucket): the LEFT-FOLD expr
        # handler (`values[1:]` fold -> left-nested IrBinOp via boolop_fold). Corpus-inert.
        if self._is_py_expr_boolop(func):
            return self._emit_py_expr_boolop_bespoke(func)
        # SFieldAssign/SArraySliceSet/STupleUnpack increment (self-tcb-reduction M5,
        # C-bucket): the `_py_stmt_assign` 5-branch handler — bespoke (the generic
        # lowering int-erases the target dispatch, the symtab membership, and the Tuple
        # compaction). Corpus-inert.
        if self._is_py_stmt_assign(func):
            return self._emit_py_stmt_assign_bespoke(func)
        # STry + except_handler + handler_list increment (self-tcb-reduction M5,
        # C-bucket): the `_py_stmt_try` accumulator-loop handler is emitted by a bespoke
        # lowering (the generic statement lowering int-erases the `for h in
        # stmt.handlers: handlers.append({rec})` record-list-building loop end-to-end).
        # Corpus-inert (fires only for the named mirror method under `_uses_stmt_ir`).
        if self._is_py_stmt_try(func):
            return self._emit_py_stmt_try_bespoke(func)
        # SDelSubscript increment (self-tcb-reduction M5, C-bucket): the `_py_stmt_delete`
        # loop-append-to-OUTER handler (per-element Seq.snoc onto ir_stmts) — bespoke.
        if self._is_py_stmt_delete(func):
            return self._emit_py_stmt_delete_bespoke(func)
        # SMatch + match_case + match_case_list increment (self-tcb-reduction M5,
        # C-bucket): the `_py_stmt_match` accumulator-loop handler — sibling of the try
        # bespoke, same record-list-emission capability. Corpus-inert.
        if self._is_py_stmt_match(func):
            return self._emit_py_stmt_match_bespoke(func)
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
            recognize_stmt_has, emit_stmt_has_group,
            recognize_bool_multiway, emit_bool_multiway_group,
            recognize_bool_lastelem, recognize_bool_earlyreturn,
            recognize_frt, emit_frt_group,
            recognize_sawalk, emit_sawalk_group,
            recognize_cpwalk, emit_cpwalk_group,
            recognize_pbexpr, emit_pbexpr_group,
            recognize_dictfold, emit_dictfold_group,
            recognize_void_dispatch, emit_void_dispatch_group,
            recognize_void_generic_descend, emit_void_generic_descend_group,
            recognize_wall2_items_walk, emit_wall2_items_walk_group,
            recognize_walk_dicts_generator, emit_walk_dicts_generator_group,
            recognize_walk_dicts_bool_consumer, emit_walk_dicts_bool_consumer_group,
            recognize_walk_dicts_void_consumer, emit_walk_dicts_void_consumer_group,
            emit_pb_trio_group,
            recognize_type_existence, emit_type_existence_group,
            recognize_named_field_existence, emit_named_field_existence_group,
            recognize_pyval_string_walker, emit_pyval_string_walker_group,
            recognize_pyval_list_walker, emit_pyval_list_walker_group,
            recognize_pyval_list_search, emit_pyval_list_search_group,
            recognize_pyval_flatten, emit_pyval_flatten_group,
            recognize_ir_free_vars, emit_ir_free_vars_group,
            recognize_cs_clause, emit_cs_clause_group,
            recognize_check_contract_exprs, emit_check_contract_exprs_group,
            recognize_check_body_walk, emit_check_body_walk_group,
            recognize_check_field_guard_raise, emit_check_field_guard_raise_group,
            recognize_check_guard_cascade, emit_check_guard_cascade_group,
            recognize_check_clause_fold, emit_check_clause_fold_group,
            recognize_check_lemma, emit_check_lemma_group,
            recognize_check_no_exception, emit_check_no_exception_group,
            recognize_check_warn_fold, emit_check_warn_fold_group)
        # genexp-erasure-wall / R2d+R3: the IRScanner `obj: Any` type-existence
        # fold (`uses_string`/`uses_subscript`/`uses_sum`/`uses_set_card`) — the
        # scalar-rooted pyval/pydict catamorphism keyed on the interned "type"
        # key, de-vacuifying the fully-erased predicate (wall-lessons (l)).
        # Fail-closed; a template bug is a loud unprovable instance.
        # class-variant-impl.md (driver-backlog item 3): the class-instance VARIANT
        # ADT carrier — a `\trusted` walker that isinstance-dispatches over a
        # frozen-dataclass UNION (the proof2why3 `Term` ADT) and reads named fields.
        # No existing value model carries a 9-way isinstance dispatch on distinct
        # dataclasses; this lowers the union onto a Why3 VARIANT `term` and
        # translates the isinstance-if-chain to a total positional `match`
        # (faithful, structurally terminating, co-landed axiom-free with the
        # Rocq/Lean TermIR cert; ledger 3). Fail-closed; a shape outside the
        # fragment stays `\trusted`. The spec is computed once in the preamble
        # needs-scan and stashed on `self._term_adt_spec`.
        from module6_whyml.generic_fold import (
            recognize_term_isinstance_fold, emit_term_isinstance_fold_group,
            recognize_term_isinstance_transform,
            emit_term_isinstance_transform_group,
            recognize_term_list_build, emit_term_list_build_group,
            recognize_term_flatten_arrow, emit_term_flatten_arrow_group,
            recognize_term_free_vars, emit_term_free_vars_group,
            recognize_term_string_pp, emit_term_string_pp_group,
            recognize_term_pp_wrapper, emit_term_pp_wrapper_group)
        # crosscheck_ir.py self-state carrier (class-variant-impl.md §OUTCOME-CC):
        # a `@property`-derived 0-arg self method over the `IRCrossCheckResult`
        # record whose body is the presence/string-empty boolean fragment
        # (`registry_skipped`). Disjoint from the term param-folds (0 formal
        # params, reads self-record fields). Gated on `_has_opaque_term_fields`
        # -> fires on 0 corpus programs + 0 other mirror files.
        if getattr(self, "_has_opaque_term_fields", False):
            from module6_whyml.generic_fold import (
                recognize_crosscheck_selfstate_bool,
                emit_crosscheck_selfstate_bool_group,
                recognize_crosscheck_term_method,
                emit_crosscheck_term_method_group)
            _css = recognize_crosscheck_selfstate_bool(func)
            if _css is not None:
                return emit_crosscheck_selfstate_bool_group(
                    func, _css, whyml_ident)
            # class-variant-impl.md §F3+§F4: the term-STRUCTURAL crosscheck
            # methods (`any_unsupported`/`all_present_unsupported` — isinstance
            # over the `option term` canon fields; `provers_agree`/`all_agree` —
            # structural `term_eq`). Gated on the certified `term` inductive
            # being available (`_term_adt_spec`). Fail-closed: a `\trusted` stub
            # body (`return False`) never matches the grammar -> emits as `val`.
            _tspec_cc = getattr(self, "_term_adt_spec", None)
            if _tspec_cc:
                _ctm = recognize_crosscheck_term_method(func)
                if _ctm is not None:
                    return emit_crosscheck_term_method_group(
                        func, _ctm, _tspec_cc, whyml_ident)
        _tspec = getattr(self, "_term_adt_spec", None)
        if _tspec:
            # class-variant-impl.md T-transform: a Term->Term (constructor-rebuild)
            # transform (`_flip_comparisons` shape) — disjoint from the bool fold
            # (it returns a Term, the fold a bool). Tried first; fail-closed.
            _tt = recognize_term_isinstance_transform(
                func, _tspec, getattr(self, "_term_const_dicts", {}))
            if _tt is not None:
                return emit_term_isinstance_transform_group(
                    func, _tt, _tspec, whyml_ident)
            _tf = recognize_term_isinstance_fold(func, _tspec)
            if _tf is not None:
                return emit_term_isinstance_fold_group(
                    func, _tf, _tspec, whyml_ident)
            # class-variant-impl.md §OUTCOME-TL: the T-set/list LEAF algebras.
            # `mk_arrow_chain` — a (`list term`, `term`) accumulator fold that
            # BUILDS a right-leaning chain via a term constructor. Fail-closed.
            _tlb = recognize_term_list_build(func, _tspec)
            if _tlb is not None:
                return emit_term_list_build_group(func, _tlb, _tspec, whyml_ident)
            # `flatten_arrow_chain` — a while-spine walk down the `->` chain,
            # returning `(list term, term)`. Fail-closed.
            _tfa = recognize_term_flatten_arrow(func, _tspec)
            if _tfa is not None:
                return emit_term_flatten_arrow_group(func, _tfa, _tspec, whyml_ident)
            # `free_vars` — a set-of-strings catamorphism over `term` (singleton /
            # `|`-union / `-`-diff / list-union), returning `map string bool` (the
            # certified L1 set repr). Fail-closed.
            _tfv = recognize_term_free_vars(func, _tspec)
            if _tfv is not None:
                return emit_term_free_vars_group(func, _tfv, _tspec, whyml_ident)
            # class-variant-impl.md T-string: a term->string BUILD catamorphism
            # (`_pp` shape) — f-string/`str()`/`" ".join` build with a threaded
            # `parent_prec: int` inherited attribute + a `_BINOP_PREC` str->int
            # const table. Disjoint (returns str, 2 params). Fail-closed.
            _tsp = recognize_term_string_pp(
                func, _tspec, getattr(self, "_term_pp_mc", {}),
                getattr(self, "_term_const_int_dicts", {}))
            if _tsp is not None:
                return emit_term_string_pp_group(func, _tsp, _tspec, whyml_ident)
            # §10.4 cascade: a delegating wrapper `return _pp(x, const)` (the sole
            # caller of a converted pp catamorphism) must type `x` as `term`.
            _tpw = recognize_term_pp_wrapper(
                func, getattr(self, "_term_pp_names", set()),
                getattr(self, "_term_pp_mc", {}))
            if _tpw is not None:
                return emit_term_pp_wrapper_group(func, _tpw, whyml_ident)
            # class-variant-impl.md §OUTCOME-TS RESIDUAL: the RECORD⇄VARIANT BRIDGE
            # for the 5 ir.py per-class `.pp` methods. A converted (non-`\trusted`)
            # pp method delegates `<cls>__pp (self: <rec>) = pp_term (<Ctor>
            # self.<f>...)` to the synthesized unified `pp_term` catamorphism
            # (emitted once, before the first delegation). `\trusted` pp methods
            # never reach here (they emit `val`), so the 5 targets convert one per
            # commit as their `\trusted` is removed. Fail-closed via the family
            # recognizer (needs-scan): a body outside the fragment -> family off.
            _fam = getattr(self, "_term_pp_family", None)
            if (_fam and not func.get("trusted", False)
                    and func.get("name") in _fam.get("method_names", set())):
                return self._emit_term_pp_delegation(
                    func, _fam, _tspec, whyml_ident)
        # FIELD-GUARD-RAISE `_check_*` caller (`_check_span`,
        # `_check_mutable_defaults`): a single-`If` field-guard whose only effect
        # is `raise PyCSLSemanticError`. Emitted inline (no walker, no forward
        # reference) — reads one key off `func`'s bridged pydict, raises on its
        # presence/absence else returns unit. Tried early: a single-statement
        # If-raise body never matches a fold/walker recogniser, but ordering here
        # keeps it disjoint by construction. Fail-closed; a shape outside the
        # fragment stays `\trusted`.
        _fgr = recognize_check_field_guard_raise(func)
        if _fgr is not None:
            return emit_check_field_guard_raise_group(_fgr, whyml_ident)
        # MULTI-GUARD CASCADE `_check_*` caller (`_check_diverges`): a sequence of
        # `if <field-guard | converted-predicate-call>: return` early-returns then
        # a terminal unconditional `raise`. Emitted inline (no walker, no forward
        # reference — the existence predicate is emitted earlier, callee-before-
        # caller) over the certified pydict/list `pyval` bridge. The predicate call
        # is gated on the converted-closure-existence name set (`_clx_pred_names`),
        # so a differently-typed / unconverted predicate stays `\trusted`.
        # Fail-closed; a shape outside the fragment stays `\trusted`.
        _gcc = recognize_check_guard_cascade(
            func, getattr(self, "_clx_pred_names", set()))
        if _gcc is not None:
            return emit_check_guard_cascade_group(_gcc, whyml_ident)
        # CLAUSE-LIST FIELD-CHECK FOLD `_check_*` caller
        # (`_check_assigns_regions`): a caller that folds ONE contract clause-list
        # (`contracts["assigns"]`), projecting each element's nested `type`/`base`
        # fields, `slookup`-ing `base` in the bridged symtab, and raising on a
        # `None` lookup or a non-member type. Emitted inline (bounded list fold, no
        # walker delegation, no forward reference) over the certified pydict->sdict
        # bridge + `slookup`. Fail-closed; a shape outside the fragment stays
        # `\trusted`.
        _ccf = recognize_check_clause_fold(func)
        if _ccf is not None:
            return emit_check_clause_fold_group(_ccf, whyml_ident)
        # LEMMA-SOUNDNESS `_check_*` caller (`_check_lemma`): the `#@ lemma`
        # well-formedness gate — a sequence of independent `if <cond>: raise`
        # guards over `func`'s bridged pydict, a bounded `contracts.assigns`
        # clause fold, and the two converted lemma predicates on the body list
        # (`_lemma_returns_value : list pyval -> bool`, gated on `_clx_pred_names`;
        # `_lemma_calls_trusted : list pyval -> map string bool -> string`, gated
        # on `_lss_pred_names`, threading `trusted_funcs` as the set PARAM).
        # Emitted inline over the certified pydict/list `pyval` bridge (no walker
        # delegation, no forward reference — both predicates are emitted earlier,
        # callee-before-caller). Fail-closed; a shape outside the fragment (or an
        # unconverted / differently-typed predicate) stays `\trusted`.
        _cl = recognize_check_lemma(
            func, getattr(self, "_clx_pred_names", set()),
            getattr(self, "_lss_pred_names", set()))
        if _cl is not None:
            return emit_check_lemma_group(_cl, whyml_ident)
        # TWO-LIST CROSS-REF FOLD `_check_*` caller (`_check_no_exception`): a
        # caller that folds ONE contract clause-list (`contracts["no_exception"]`)
        # while cross-referencing a SECOND (`contracts["raises"]` by `exc_type`)
        # and testing the finite `KNOWN_EXCEPTIONS` literal-set membership, raising
        # by exception TYPE. Emitted inline (bounded nested list fold + literal-set
        # disjunction over the certified pydict/list `pyval` bridge, no walker
        # delegation, no forward reference). Fail-closed; a shape outside the
        # fragment stays `\trusted`.
        _cne = recognize_check_no_exception(func)
        if _cne is not None:
            return emit_check_no_exception_group(_cne, whyml_ident)
        # IR-LIST WARN-FOLD `_check_*` caller (`_check_union_gt1`): the purest
        # report-only orchestrator — read ONE top-level list field off the
        # bridged `ir` pydict (`x = ir.get("<K>") or []`) and iterate it emitting
        # a `warnings.warn(...)` per element. `warnings.warn` is an unmodelled
        # side-channel (no verifiable value, no control flow), so the loop lowers
        # to a total, terminating UNIT fold over the field's list (each warn ->
        # no-op) over the certified pydict/list `pyval` bridge (`pget_list`). No
        # raise path, `ensures true`. The field key is load-bearing; only the
        # error-message-only warn `FString` is erased. Fail-closed; a loop body
        # with any non-`warnings.warn` statement stays `\trusted`.
        _cwf = recognize_check_warn_fold(func)
        if _cwf is not None:
            return emit_check_warn_fold_group(_cwf, whyml_ident)
        # HAPPY module-check orchestrator (`_check_happy`): reads `ir["happy"]`,
        # builds `method_names` = `set(happy["method_names"])`, folds
        # `ir["functions"]` through the converted set-collector to build the
        # `written` set, then folds `happy["properties"]` raising by
        # except-set/exec-method membership + a report-only warn tail. Lowered
        # over the certified pydict/list `pyval` bridge, reusing the collector.
        # Corpus-inert; fail-closed (any shape deviation stays `\trusted`).
        from module6_whyml.generic_fold import (
            recognize_check_happy, emit_check_happy_group)
        _chp = recognize_check_happy(func)
        if _chp is not None:
            return emit_check_happy_group(_chp, whyml_ident)
        # ACT well-formedness orchestrator (`_check_acts`): reads `func["acts"]`,
        # builds a local `defined` DICT (key membership + iteration only, VALUES
        # never read) that lowers to a locally-built `map string bool` set, folds
        # each act's `given_exprs` through the converted `_contains_result` bool
        # fold (duplicate-name / `\result`-in-guard raises), then folds `acts` a
        # second time raising on a `complete`/`disjoint` reference to an undefined
        # act. The `referenced` set + `warnings.warn` omission tail are report-only
        # (dropped under `ensures True`). Lowered over the certified pydict/list
        # `pyval` bridge, reusing `_contains_result`. Corpus-inert; fail-closed
        # (any shape deviation stays `\trusted`).
        from module6_whyml.generic_fold import (
            recognize_check_acts, emit_check_acts_group)
        _cac = recognize_check_acts(func)
        if _cac is not None:
            return emit_check_acts_group(_cac, whyml_ident)
        # string-keyed-set NoReturn cluster (check-noreturn-successors driver):
        # #1 the FLAT `ir["functions"]` set-projection fold
        # (`_collect_noreturn_names`) — read the one list field off `ir`'s
        # bridged pydict (`pget_list`) and fold each element dict's name string
        # into a `map string bool`. Corpus-inert; fail-closed.
        from module6_whyml.generic_fold import (
            recognize_collect_noreturn_names, emit_collect_noreturn_names_group,
            recognize_stmt_noreturn_call, emit_stmt_noreturn_call_group)
        _cnn = recognize_collect_noreturn_names(func)
        if _cnn is not None:
            return emit_collect_noreturn_names_group(_cnn, whyml_ident)
        # #2 the bool guard-cascade ending in read-only-set-param membership
        # (`_stmt_is_noreturn_call`) — nested `s.get(stmt/value/type/func)`
        # field reads terminating in `fn in <set_param>` (`Map.get`). The
        # `.rsplit(".",1)[-1]` second disjunct is provenance-drop (VC-irrelevant
        # under `ensures True`). Corpus-inert; fail-closed.
        _snc = recognize_stmt_noreturn_call(func)
        if _snc is not None:
            lines = emit_stmt_noreturn_call_group(_snc, whyml_ident)
            # #3/#4 (deferred): the `_noreturn_walk_stmts` walker calls this
            # `_stmt_is_noreturn_call` (forward reference), and the
            # `_check_noreturn_successors` caller calls the walker — so both are
            # appended here, callee-before-caller, once the leaf is emitted.
            from module6_whyml.generic_fold import (
                emit_noreturn_walk_stmts_group,
                emit_check_noreturn_successors_group)
            for f_w, desc_w in getattr(self, "_nrw_funcs", []):
                if f_w.get("name") in self._nrw_emitted:
                    continue
                lines += emit_noreturn_walk_stmts_group(desc_w, whyml_ident)
                self._nrw_emitted.add(f_w.get("name"))
            for f_c, desc_c in getattr(self, "_ccns_funcs", []):
                if f_c.get("name") in self._ccns_emitted:
                    continue
                lines += emit_check_noreturn_successors_group(desc_c, whyml_ident)
                self._ccns_emitted.add(f_c.get("name"))
            return lines
        _te = recognize_type_existence(func)
        if _te is not None:
            return emit_type_existence_group(func, _te, whyml_ident)
        # genexp-erasure-wall / wall-lessons (l),(j): the single-node named-field
        # self-recursive existence fold (`_pattern_has_constructor` shape) — the
        # SAME certified scalar pyval/pydict catamorphism, keyed on a `K_dyn`
        # dynamic key (non-`type` dispatch) with the named-field recursion
        # subsumed by the universal descend. De-vacuifies the `any(genexp)` →
        # `any_1` erasure. Fail-closed; a template bug is a loud unprovable
        # instance, never a false proof.
        _nfe = recognize_named_field_existence(func)
        if _nfe is not None:
            return emit_named_field_existence_group(func, _nfe, whyml_ident)
        # pyval-walker-impl.md (driver-backlog item 3): the GENERAL value-returning
        # pyval string walker — a string-RETURNING catamorphism over a heterogeneous
        # nested-tuple/list param (the `from_sexp` sertop s-expression shape), lowered
        # onto the certified pyval ADT via inline TOTAL pv_nth/pv_len/atom_of
        # projectors (axiom-free; ledger 3). Fires only when the Optional[str] return
        # resolves to a synthesized 2-arm (str-payload + None) union. Fail-closed; a
        # template bug is a loud unprovable instance, never a false proof.
        # C2 (pyval-walker-impl.md): pass the module's pyval-list-walker name set
        # so a `<var> = <sibling>(vref)` assign binds a `list string` local and
        # `<var>[-k] if <var> else None` reads its end (`_const_name`/
        # `_ind_short_name`, which call `_find_kername_components`).
        _pvw_sibs = getattr(self, "_pyval_list_walker_names", set())
        _pvw = recognize_pyval_string_walker(func, _pvw_sibs)
        if _pvw is not None:
            _ret = func.get("return_annotation")
            _vinfo = getattr(self, "_variant_types", {}).get(_ret)
            if _vinfo:
                _ctors = _vinfo.get("constructors", {})
                _some = _none = None
                for _cn, _cd in _ctors.items():
                    if _cd.get("arity") == 0:
                        _none = _cn
                    elif _cd.get("arity") == 1 and _cd.get("payload") in (
                            ["str"], ["string"]):
                        _some = _cn
                if _some and _none and len(_ctors) == 2:
                    _pvw["ret_whyml"] = _vinfo["whyml_name"]
                    _pvw["some_ctor"] = _some
                    _pvw["none_ctor"] = _none
                    return emit_pyval_string_walker_group(func, _pvw, whyml_ident)
        # pyval-walker-impl.md C1: the LIST-accumulator counterpart — a
        # `List[str]` (`list string`)-RETURNING catamorphism BUILT via
        # `.append`/`.extend`/`reversed` over the certified pyval spine (the
        # `from_sexp._walk_modpath` shape). Inline TOTAL projectors + list ops +
        # an axiom-free per-function size lemma for tree self-recursion (ledger
        # 3). Fail-closed; a template bug is a loud unprovable instance.
        # C1b: pass the module's pyval-list-walker name set so a cross-call to a
        # sibling walker (`_walk_kername`→`_walk_modpath`) is a legal listexpr.
        # pyval-walker-impl.md C3: the `list pyval` FLATTEN catamorphism
        # (`_flatten_tuples` — returns `List[Any]` = a list of the sub-nodes
        # themselves, not strings). A DISTINCT value model (pyval-element
        # accumulator) emitted as the certified mutual `{n}(v) with {n}__list(l)`
        # group + inline TOTAL `list pyval` append. Tried before the `list string`
        # walkers (its `.append(<pyval param>)` would make them bail anyway).
        # Fail-closed; a template bug is a loud unprovable instance.
        _pvf = recognize_pyval_flatten(func)
        if _pvf is not None:
            return emit_pyval_flatten_group(func, _pvf, whyml_ident)
        _pvl_sibs = getattr(self, "_pyval_list_walker_names", set())
        # C1b SEARCH catamorphism (`_find_kername_components`): a pyval tree search
        # for the first non-empty per-node reader result — emitted as the certified
        # mutual `{n}(v) with {n}__list(l)` group (auto-terminating). Tried first
        # (more specific structure); mutually exclusive with the accumulator walker.
        _pvls = recognize_pyval_list_search(func, _pvl_sibs)
        if _pvls is not None:
            return emit_pyval_list_search_group(func, _pvls, whyml_ident)
        _pvl = recognize_pyval_list_walker(func, _pvl_sibs)
        if _pvl is not None:
            return emit_pyval_list_walker_group(func, _pvl, whyml_ident)
        _gf = recognize_generic_fold(func)
        if _gf is not None:
            return emit_generic_fold_group(func, _gf, whyml_ident)
        # ir-traversal-residual A-bool: the statement-tree existence fold (the
        # lambda-lifted `_has_return*` closures). Fail-closed; loud unprovable
        # instance on any template bug.
        _be = recognize_bool_existence(func)
        if _be is not None:
            return emit_bool_existence_group(func, _be, whyml_ident)
        # tree-walk-wall-impl.md (self-tcb-reduction, GATE-S PROVEN): the FAITHFUL,
        # TYPED counterpart — the `_body_has_return`-shaped stmt_ir tree-walk
        # existence fold, emitted as the certified stmt_ir catamorphism (verbatim
        # from the full-M5-scale-proven standalone.mlw, LEXICOGRAPHIC variant) over
        # the certified stmt_ir ADT instead of the dynamic `pyval` fold. The tag(s)
        # drive the true-arm(s) (mutation-sensitive, non-facade). Same fail-closed
        # discipline. 4-descent-arm shape, so `recognize_bool_existence` (2-3 arms)
        # never matches it; ordered here for clarity.
        _sh = recognize_stmt_has(func)
        if _sh is not None:
            return emit_stmt_has_group(func, _sh, whyml_ident)
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
            lines = emit_sawalk_group(func, _sa, whyml_ident)
            # BODY-WALK caller siblings: append any deferred `_check_*` caller
            # whose walker is THIS just-emitted `_sa_walk`/`_gso_walk` (once).
            lines = lines + self._emit_deferred_cbw(func.get("name"), whyml_ident)
            # CHECK-SUBSCRIPT-ASSIGNMENTS: record this walker + append the
            # multi-walker caller once BOTH its walkers have been emitted.
            self._note_emitted_walker(func.get("name"))
            return lines + self._emit_deferred_csa(whyml_ident)
        # 2-arg checkpoint walk `_cp_walk(node, where)`: the `_sa_walk` sibling
        # with a SINGLE env param and a cross-call pre-action (`_contains_result`
        # on `node.get("test")`). Arity-2, so `recognize_sawalk` (exactly 3
        # params) never matches it; ordered here as the immediate sibling. Same
        # fail-closed discipline; a template bug is a loud unprovable instance.
        _cp = recognize_cpwalk(func)
        if _cp is not None:
            lines = emit_cpwalk_group(func, _cp, whyml_ident)
            # BODY-WALK caller siblings: append any deferred `_check_*` caller
            # whose walker is THIS just-emitted `_cp_walk` (once).
            lines = lines + self._emit_deferred_cbw(func.get("name"), whyml_ident)
            self._note_emitted_walker(func.get("name"))
            return lines + self._emit_deferred_csa(whyml_ident)
        # predicate-base walk `_pb_expr(node, ctx, symtab, known)`: the `_sa_walk`
        # sibling with a MULTI-ARM `node.get("type")` type dispatch (ArrayLen /
        # Valid / Separated / Forall|Exists), a 2nd env `known` modelled as
        # `sdict`-presence, and string-op guards (VC-free `__startswith` +
        # `pystr_eq`). Reuses the arity-generalized `_sa_walk_group_lines` walk
        # group. Same fail-closed discipline; a template bug is a loud unprovable
        # instance, never a false proof.
        # IR-FREE-VARS (generic_fold): the `_ir_free_vars` Set[str] union-fold —
        # a `map string bool` catamorphism over the pyval/pydict ADT. Corpus-inert
        # (fires only for the recognised mirror function). Same fail-closed
        # discipline; a template bug is a loud unprovable instance, never a false
        # proof.
        _fv = recognize_ir_free_vars(func)
        if _fv is not None:
            return emit_ir_free_vars_group(_fv, whyml_ident)
        # CS-CLAUSE (generic_fold): the `_cs_clause` scope-checker (the
        # `_ir_free_vars` set consumer). The `{_cs_stmt,_cs_body,_cs_descend}`
        # trio is appended right after (deferred, once), exactly as the pb trio
        # defers to `_pb_expr`. Corpus-inert; fail-closed.
        _csc = recognize_cs_clause(func)
        if _csc is not None:
            from module6_whyml.generic_fold import emit_pb_trio_group
            lines = emit_cs_clause_group(_csc, whyml_ident)
            if getattr(self, "_cs_trio", None) and not self._cs_trio_emitted:
                lines = lines + emit_pb_trio_group(self._cs_trio, whyml_ident,
                                                   clause_val_mid=" false")
                self._cs_trio_emitted = True
            # CHECK-CONTRACT-SCOPE caller (driver target #3): append the deferred
            # caller group(s) right after the `_cs_clause` group + cs-trio they
            # call into (`_cs_clause`/`_cs_clause__list` + `_cs_body`), once.
            if getattr(self, "_ccs_funcs", None) and not self._ccs_emitted:
                from module6_whyml.generic_fold import emit_check_contract_scope_group
                for _cf, _desc in self._ccs_funcs:
                    lines = lines + emit_check_contract_scope_group(_desc, whyml_ident)
                self._ccs_emitted = True
            return lines
        _pb = recognize_pbexpr(func)
        if _pb is not None:
            lines = emit_pbexpr_group(func, _pb, whyml_ident)
            # PB-TRIO FUSION: append the fused `{_pb_stmt,_pb_body,_pb_descend}`
            # group right after `_pb_expr` (which it calls into), once.
            if getattr(self, "_pb_trio", None) and not self._pb_trio_emitted:
                lines = lines + emit_pb_trio_group(self._pb_trio, whyml_ident)
                self._pb_trio_emitted = True
            # CHECK-CONTRACT-EXPRS callers (pdict-to-sdict-impl.md): append the
            # deferred `_check_contract_exprs` caller group(s) right after the
            # `_pb_expr` group + pb-trio they call into (once).
            if getattr(self, "_cce_funcs", None) and not self._cce_emitted:
                for _cf in self._cce_funcs:
                    _cce = recognize_check_contract_exprs(_cf)
                    if _cce is not None:
                        lines = lines + emit_check_contract_exprs_group(
                            _cce, whyml_ident)
                self._cce_emitted = True
            return lines
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
        # R-W2a: the void heterogeneous `.items()`-walk `for s in stmts: if not
        # isinstance(s,dict): continue; for k,v in s.items(): <compound k-guard +
        # isinstance(v,dict/list) dispatch>; leaf(v,*ctx); walk([v],*ctx)`. Lowers
        # onto the certified pyval/pydict L1 catamorphism; the `walk([v])` re-wrap
        # is normalized to the direct `walk__val v` descent (termination). The
        # leaf stays \trusted (opaque val, ensures true). Same fail-closed
        # discipline.
        _w2a = recognize_wall2_items_walk(func)
        if _w2a is not None:
            return emit_wall2_items_walk_group(func, _w2a, whyml_ident)
        # R-W2b: the `.values()` GENERATOR-walker family (ir_inline.py). The
        # generator `_walk_dicts(obj): if isinstance(obj,dict): yield obj; for v
        # in obj.values(): yield from self(v); elif isinstance(obj,list): for x
        # in obj: yield from self(x)` lowers onto the certified pyval/pydict L1
        # catamorphism as the `list pyval` flatten trio. Its bool consumer
        # `for node in _walk_dicts(obj): <tag/field/membership pred>; return
        # False` folds over `_walk_dicts obj` (obj stays live). ensures True;
        # membership is an opaque val. Fail-closed; corpus-inert.
        _wdg = recognize_walk_dicts_generator(func)
        if _wdg is not None:
            return emit_walk_dicts_generator_group(func, _wdg, whyml_ident)
        _wdc = recognize_walk_dicts_bool_consumer(func)
        if _wdc is not None and _wdc["walk_name"] in {
                f.get("name") for f in self.ir.get("functions", [])
                if isinstance(f, dict) and recognize_walk_dicts_generator(f)}:
            return emit_walk_dicts_bool_consumer_group(func, _wdc, whyml_ident)
        # R-W2c: the VOID `.values()`-walk consumer `_check_no_aliasing` — an
        # outer per-func `size_list` fold that walks `f.get("body")` and RAISES
        # `PyCSLSemanticError` on a per-node aliasing guard (assign-a-global or
        # pass-a-global-as-arg). Folds over `_walk_dicts obj`; the arg guard
        # nests a `size_list args` fold. ensures True; membership opaque; raise
        # declared. Same generator-present gate; fail-closed; corpus-inert.
        _wdv = recognize_walk_dicts_void_consumer(func)
        if _wdv is not None and _wdv["walk_name"] in {
                f.get("name") for f in self.ir.get("functions", [])
                if isinstance(f, dict) and recognize_walk_dicts_generator(f)}:
            return emit_walk_dicts_void_consumer_group(func, _wdv, whyml_ident)
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
        # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): rewrite a BUILD-UP-DICT
        # compound handler (`_process_for`: `target=..; d={"stmt":"For",..}; if C:
        # d["tuple_targets"]=..; return d`) to a single `Return` of the base construction
        # dict, so `_returns_stmt_ir`/`_lower_stmt_ir_construction` emit `(SFor <iter>
        # (seq_to_sl <body>))`. Fail-closed (None → unchanged); @mutable_state-gated →
        # corpus byte-inert.
        _sib = self._recognize_stmtir_builder(func, body_stmts)
        if _sib is not None:
            body_stmts = _sib
        # SAssert increment (self-tcb-reduction M5, C-bucket): rewrite a BUILD-UP-THEN-
        # APPEND handler (`_py_stmt_assert`: `ir_node = {"stmt":"Assert",...}; if C:
        # ir_node["msg"]=stmt.msg.value; ir_stmts.append(ir_node)`) to a single
        # `ir_stmts.append({"stmt":"Assert","test":..,"msg":stmt.msg})`, so the append
        # site snocs `SAssert (py_expr_to_ir stmt.test) <iropt_str>`. Fail-closed (None →
        # unchanged); @mutable_state-gated → corpus byte-inert.
        _sab = self._recognize_stmt_append_builder(func, body_stmts)
        if _sab is not None:
            body_stmts = _sab
        # optional-field ext (monomorphic-option ADTs): rewrite the
        # `_py_expr_slice` 3-ternary-bound body to a single `Return` of the
        # `{"type":"SliceN",...}` construction (ternaries inlined), so the normal
        # scaffolding emits `(IrSliceN <opt> <opt> <opt>)`. Fail-closed (None →
        # unchanged); @mutable_state-gated → corpus byte-inert.
        _slb = self._recognize_slice_builder(func, body_stmts)
        if _slb is not None:
            body_stmts = _slb
        # optional-field ext (monomorphic-option ADTs): rewrite the TYPE-LESS
        # `_csl_function_variant` body to a single `Return` of the
        # `{"type":"FunctionVariant",...}` construction, so the normal scaffolding
        # emits `(IrFunctionVariant <expr> <iropt_str>)`. Fail-closed (None →
        # unchanged); @mutable_state-gated → corpus byte-inert.
        _fvb = self._recognize_functionvariant_builder(func, body_stmts)
        if _fvb is not None:
            body_stmts = _fvb
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
            # stmt-list-append-mutation wall (C-bucket): a `ref (seq stmt_ir)` param
            # appended in the body carries a real `writes {p}` frame so Why3 accepts (and
            # CHECKS) the caller-visible in-place append — the frame the pre-feature
            # `assigns ir_stmts` lowered to `writes { }` (empty; fable Oracle 3). Empty set
            # → no clause → byte-identical.
            _ssp = getattr(self, "_stmt_seq_mut_params", set())
            if _ssp:
                _ord2 = [whyml_ident(p) for p in self._formal_params if p in _ssp]
                if _ord2:
                    lines.append(f"    writes {{ {', '.join(_ord2)} }}")

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

    def _emit_term_pp_delegation(self, func, fam, spec, whyml_ident) -> List[str]:
        """class-variant-impl.md §OUTCOME-TS RESIDUAL (record⇄variant bridge, part c):
        emit a converted per-class `.pp` method as a record→variant injection +
        delegation: `let <cls>__pp (self: <rec>) : string = pp_term (<Ctor>
        self.<f1> self.<f2> ...)` (ctor args in spec/variant order, `self.<label>`
        via `_field_label`). The shared `pp_term` catamorphism is emitted ONCE,
        before the first delegation (flag `_pp_term_emitted`). NO axiom (ledger 3)."""
        from module6_whyml.generic_fold import emit_pp_term_helper
        cls = func["self_type"]                       # e.g. "App"
        recname = whyml_ident(cls.lower())            # e.g. "app"
        fname = whyml_ident(func["name"])             # e.g. "app__pp"
        spec_fields = spec["ctors"][cls]              # [(head, string), (args, list term)]
        ctor_args = " ".join(
            f"self.{self._field_label(recname, fn)}" for (fn, _wt) in spec_fields)
        inject = f"{cls} {ctor_args}" if ctor_args else cls
        lines: List[str] = []
        if not getattr(self, "_pp_term_emitted", False):
            # Register the string-build abstract `val`s `pp_term` uses (dedup-identical
            # where a leaf pp method already registered them via `str()`/f-string
            # lowering — e.g. ir.py's intlit__pp/unsupported__pp).
            if fam.get("uses_strconcat"):
                self._add_abstract_op(
                    "val str_concat_op (a: string) (b: string) : string\n"
                    "    ensures { result = (concat a b) }\n"
                    "    ensures { String.length result = String.length a + String.length b }")
            if fam.get("uses_strofint"):
                self._add_abstract_op("val str_of_int (x: int) : string")
            lines += emit_pp_term_helper(fam, spec)
            self._pp_term_emitted = True
        lines.append(f"  let {fname} (self: {recname}) : string")
        lines.append("    requires { true } ensures { true }")
        lines.append(f"  = pp_term ({inject})")
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
        # SUB-BODY recursion (self-tcb-reduction M5, C-bucket): this class is the
        # emitter mirror iff some handler RETURNS a compound `{"stmt": While/If/For}`
        # node — the corpus-inert signal that keys the stmt_ir self-call retypes
        # below (no corpus function builds such a node).
        _emits_stmt_ir = any(
            self._returns_stmt_ir(f.get("body", [])) for f in functions)
        for func in functions:
            # SUB-BODY recursion (C-bucket): the self-call return-type SIBLINGS of
            # the `_compute_return_type` overrides (the emit_ir precedent at the
            # `ann in (...) -> emit_ir` branch below). A `_process_*` handler that
            # RETURNS a compound stmt node abstracts as `stmt_ir`; the trusted
            # sub-body dispatcher `_py_stmts_to_ir` (whose result feeds `seq_to_sl`)
            # abstracts as `seq stmt_ir` — so a `self.<m>(...)` call site sees the
            # right type instead of the `int`/`array int` its shape/annotation implies.
            if _emits_stmt_ir:
                if self._returns_stmt_ir(func.get("body", [])):
                    result[func["name"]] = "stmt_ir"
                    continue
                # `func["name"]` is the class-prefixed IR name
                # (`<cls>___py_stmts_to_ir`), so match the un-prefixed tail.
                if str(func.get("name", "")).endswith("_py_stmts_to_ir"):
                    result[func["name"]] = "seq stmt_ir"
                    continue
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
            elif ann == "str" and (ret == "int"
                    or (ret == "unit" and func.get("trusted"))):
                # no-more-int emitter campaign L1: a `-> str` function returns a
                # WhyML `string`, not the legacy int hash — so a caller can type a
                # `s = f(...)` local as string. (MEASUREMENT branch — gated.)
                # self-tcb-reduction GAP #2: the `ret == "unit"` disjunct (gated on
                # `func["trusted"]`) is the self-call-site sibling of the
                # `_compute_return_type` GAP #2 fix — a `\trusted` `-> str` mirror
                # stub with a bare `pass` body (`find_return_type -> "unit"`) must
                # abstract its `self.<m>(...)` call site as `: string`, else a
                # CONVERTED caller's `ret = self._parse_mixin_type()` local (typed
                # `string`) fails to type-check against the `unit`-returning abstract
                # `val`. Matches the `-> "ExprIR"` unit-stub → `emit_ir` disjunct
                # below. Byte-identical for the corpus (a real `-> str` function has
                # a return statement, so `ret` is never "unit").
                ret = "string"
            elif (ann in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR")
                    and ret in ("int", "unit")):
                # self-tcb-reduction spike (csl-ast-as-emit_ir): the `self.<method>(...)`
                # SELF-CALL abstract-val sibling of `_compute_return_type`'s ann-based
                # `emit_ir` fallback (line ~2260-2270) — a `trusted` IR-node dispatcher
                # called from WITHIN the same @mutable_state class (e.g. `_csl_binop`
                # calling `self._csl_to_ir(node.left)`) is abstracted here, not there, so
                # this map needs the SAME recognition or the self-call site sees `int`.
                ret = "emit_ir"
            elif ret == "int" and ann in getattr(self, "_record_types", {}) \
                    and getattr(self, "_record_array_fields", None):
                # W8 capability (vi): a method DECLARED `-> <RecordClass>` (the token
                # cursor's `def cur(self) -> _Tok`) returns the real record type, not the
                # erased `int`. Without this the `self.cur()` call site abstracts as
                # `val self_cur_0 () : int` and every projection off it (`self.cur().kind`)
                # falls through to an opaque `get_kind : int -> int` getter — an int-erasing
                # facade with no link to the receiver.
                # GATE (low blast radius, the (i)/(iii) gate): `_record_array_fields` is
                # non-empty only for a `@mutable_state` class carrying a `List[<record>]`
                # field, i.e. exactly the parser-cursor shape. `_record_types` is populated
                # by `_emit_type_decls`, which runs before this map is built.
                ret = self._record_types[ann]["whyml_name"]
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
        # r1-setop I3 (self-tcb-reduction): a PARAMETRIC set type in a cross-mixin
        # `#@ requires_method` signature (`local_refs: Set[str]`) lowers to a STRING-keyed
        # map when the element is `str` — the set element IS the map key, so the abstract-val
        # bridge for a string-name-set dependency agrees with the already-string-keyed
        # `.add`/membership lowering (I1/I2). `Set[int]`/bare `Set` stay int-keyed. This was
        # the `int` fallback (WORSE than the bare-`set` `map int`); no corpus program uses a
        # cross-mixin requires_method set param, so byte-inert. (Prerequisite for the I4
        # cross-method κ=string bridge fixpoint; until that lands, the mirror keeps `set`.)
        if symtype in ("Set[str]", "FrozenSet[str]"):
            return "map string (option int)"
        if symtype in ("Set[int]", "FrozenSet[int]", "Set", "FrozenSet"):
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

    @staticmethod
    def _is_stmt_ir_node(arg: Any) -> bool:
        """stmt-list-append-mutation wall (C-bucket): is `arg` a statement-IR node
        literal — a `DictLit` with a STRING-literal `"stmt"` key? That is the exact
        shape the `_py_stmt_*` handlers append (`{"stmt": "Pass"}`, `{"stmt": "Return",
        …}`) and NOTHING in the corpus produces it, so it is the sound discriminator of
        the mutable-ref stmt-append convention."""
        if not (isinstance(arg, dict) and arg.get("type") == "DictLit"):
            return False
        for k in arg.get("keys", []) or []:
            if (isinstance(k, dict) and k.get("type") == "String"
                    and k.get("value") == "stmt"):
                return True
        return False

    def _is_stmt_ir_append_arg(self, arg: Any,
                               stmt_ir_returning: Optional[Set[str]]) -> bool:
        """SUB-BODY recursion (C-bucket): is `arg` a stmt_ir-VALUED append element?
        EITHER a `{"stmt": K}` node LITERAL (`_py_stmt_pass/return/...`) OR a CALL to
        a `_process_*` handler that RETURNS a compound stmt node (`self._process_while(
        stmt)` in `_py_stmt_while/for/if`). The latter keeps the receiving `ir_stmts`
        param a `ref (seq stmt_ir)` even though the appended value is a call, not a
        literal. Corpus-inert: `stmt_ir_returning` is empty unless the file emits an
        SWhile/SIf/SFor."""
        if self._is_stmt_ir_node(arg):
            return True
        if (stmt_ir_returning and isinstance(arg, dict)
                and arg.get("type") == "Call"):
            callee = arg.get("func", "") or ""
            tail = callee[len("self."):] if callee.startswith("self.") else callee
            return bool(tail) and any(
                rn == tail or rn.endswith("_" + tail) or rn.endswith(tail)
                for rn in stmt_ir_returning)
        return False

    def _stmt_seq_append_params(self, func: Dict[str, Any],
                                stmt_ir_returning: Optional[Set[str]] = None) -> Set[str]:
        """stmt-list-append-mutation wall (C-bucket): the DIRECT seed — list params
        that are `.append`-ed a statement-IR node (`p.append({"stmt": K, …})`) in this
        function's own body. These become caller-visible mutable `ref (seq stmt_ir)`
        params with a real `writes {p}` frame (the sound in-place-append model; the fable
        oracle's `push`). Methods are INCLUDED (unlike the ref-map WL-05b seed): the
        `_py_stmt_*` handlers are methods, and the convention threads their param type
        consistently through the abstract-op call map (`_build_method_param_types_map`
        consults the same `_func_stmt_seq_mut_params`)."""
        params = set(func.get("formal_params", []) or [])
        mutated: Set[str] = set()

        def walk(stmts: List[Dict[str, Any]]) -> None:
            # SAssert increment (C-bucket): locals bound (earlier in THIS statement
            # list) to a `{"stmt": K}` node literal — the build-up-then-append shape
            # (`ir_node = {"stmt":"Assert",...}; ...; ir_stmts.append(ir_node)`). An
            # append of such a local is a stmt-ir append even though the arg is a Var,
            # so the receiving param is still a `ref (seq stmt_ir)`.
            built_stmt_locals: Set[str] = set()
            for st in stmts:
                if not isinstance(st, dict):
                    continue
                if (st.get("stmt") == "Assign" and isinstance(st.get("target"), str)
                        and self._is_stmt_ir_node(st.get("value"))):
                    built_stmt_locals.add(st["target"])
                if st.get("stmt") in ("Expr", "ExprStmt"):
                    val = st.get("value", {})
                    if isinstance(val, dict) and val.get("type") == "Call":
                        fn = val.get("func", "")
                        args = val.get("args", []) or []
                        a0 = args[0] if args else None
                        is_built_local = (
                            isinstance(a0, dict) and a0.get("type") == "Var"
                            and a0.get("name") in built_stmt_locals)
                        if (isinstance(fn, str) and fn.endswith(".append") and args
                                and (self._is_stmt_ir_append_arg(a0, stmt_ir_returning)
                                     or is_built_local)):
                            recv = fn.rsplit(".", 1)[0]
                            if recv in params:
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

    def _build_func_stmt_seq_mut_params(
            self, functions: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """stmt-list-append-mutation wall (C-bucket): module-level map func-name → set of
        list params modelled as a caller-visible mutable `ref (seq stmt_ir)`. FIXPOINT
        (the WL-05b `_build_func_mutated_collection_params` precedent): seed with directly
        stmt-appended params, then propagate — if A forwards its param `p` (a bare `Var`)
        into a position callee B treats as a stmt-seq-mut param, `p` is stmt-seq-mut in A
        too (Python's by-reference escape is transitive). Keeps a `driver(ir_stmts)` that
        forwards its param into `emit_pass(ir_stmts)` SOUND (both sides `ref (seq
        stmt_ir)`)."""
        by_name: Dict[str, Set[str]] = {}
        formals: Dict[str, List[str]] = {}
        # SUB-BODY recursion (C-bucket): the names of handlers that RETURN a compound
        # stmt node — so a `p.append(self._process_*(stmt))` keeps `p` a stmt-seq-mut
        # param (the appended value is a stmt_ir-valued call, not a dict literal).
        stmt_ir_returning = {
            f.get("name") for f in functions
            if self._returns_stmt_ir(f.get("body", []))}
        for func in functions:
            nm = func.get("name")
            if nm is None:
                continue
            by_name[nm] = self._stmt_seq_append_params(func, stmt_ir_returning)
            formals[nm] = list(func.get("formal_params", []) or [])
        changed = True
        while changed:
            changed = False
            for func in functions:
                nm = func.get("name")
                if nm is None:
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
            # K2 (self-tcb-reduction): the `_is_final_annotation` bool-recognizer is
            # emitted by a BESPOKE handler (`_emit_is_final_annotation_bespoke`) whose
            # signature is hardcoded `(ann_expr: emit_ir) : bool` — but its param
            # `ann_expr: ast.expr` resolves to symtype `Any` (→ `int`) through the generic
            # path above, so the ABSTRACT self-call stub (`self__is_final_annotation_1`)
            # a sibling method emits would take `int` and REJECT an `emit_ir` argument
            # (`stmt.annotation` → `stmt_annotation !stmt`). Align the stub's param type
            # with the real bespoke signature so `self._is_final_annotation(stmt.annotation)`
            # type-checks. Gated on the bespoke predicate (`_uses_stmt_ir` mirror only) ->
            # corpus + every non-emitter mirror byte-identical. The stub RETURN stays `int`
            # (the boolean call-site wraps it `(… <> 0)`); only the param is corrected.
            if self._is_final_annotation(func):
                param_types = ["emit_ir"]
            # W8 capability (ii): the `*vals: str` vararg is a real trailing parameter
            # of type `seq string`, but it is NOT in `symbol_table` (Module4 never sees
            # a vararg), so the loop above misses it. Append it so the call-site
            # coercion (`_coerce_dotted_args` zips args against this list) does not
            # TRUNCATE the packed sequence argument away. Always last.
            if func.get("vararg_str_param"):
                param_types = param_types + ["seq string"]
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

