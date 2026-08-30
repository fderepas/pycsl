from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from module6_whyml.identifiers import whyml_ident, safe_exc_name, whyml_string_literal
from module6_whyml.ir_scanner import IRScanner
from module6_whyml.scc import emits_as_logic_symbol


class FunctionEmissionMixin:
    """Function-emission: signature assembly, parameter typing, contract emission, return-type computation, per-function state reset, and the cross-method type maps populated by `transpile()` before any function body is emitted. Mixed into Module6_WhyMLTranspiler."""

    def _param_type_str(self, arg: str, ref_params: Set[str], array2d_params: Set[str],
                        array1d_params: Set[str], symbol_table: Dict[str, Any],
                        int_type: str) -> str:
        """Return the WhyML parameter type string for a standalone function argument."""
        safe = whyml_ident(arg)
        # self-tcb-reduction FunctionEmissionMixin WRITER class (`_build_param_list`): the
        # `local_refs`/`ghost_vars` `Set[str]` params are modelled as `seq string` (the
        # sequence of the set's elements) — the body only membership-tests them (`v in
        # local_refs`, `arg in ghost_vars`), which lowers to the existing `seq_mem_str`
        # over-approx; a `map int (option int)` would int-clash the raw-string key. Gated on
        # the file defining `_build_param_list` (only the functions.py mirror does) + these
        # two param names (only `_build_param_list` carries them) -> byte-inert for the
        # corpus and every other mirror.
        if self._uses_build_param_list() and arg in ("local_refs", "ghost_vars"):
            return f"({safe}: seq string)"
        # The trusted `_param_type_str` stub's own collection params (`ref_params`,
        # `array2d_params`, `array1d_params`, `symbol_table`) must match the `seq string`
        # arguments `_build_param_list` passes at the call site. Scoped to the
        # `_param_type_str` signature (via `_current_sig_func_name`) so a DIFFERENT method
        # reusing one of these names (`_emit_union_arm_vc`'s `symbol_table`) is unaffected.
        if (self._uses_build_param_list()
                and str(getattr(self, "_current_sig_func_name", "") or "")
                .endswith("_param_type_str")
                and arg in ("ref_params", "array2d_params", "array1d_params", "symbol_table")):
            return f"({safe}: seq string)"
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
            # `_collect_class_constants(node, field_names)`: a READ-ONLY `Set[str]` method
            # param whose ONLY use is the membership `target in field_names`, where `target`
            # is an `Optional[str]` UNION LOCAL. The emitted key is therefore the carrier
            # projection `(match !target with Arm_1_0 _v -> _v | _ -> "" end)` — a genuine
            # `string` — so the int-keyed default mistypes it and the whole membership
            # collapses to the opaque `ps_field_mem`, which DROPS `field_names` entirely
            # (that is the standing `KNOWN_ERASURES` entry for this method).
            #
            # Module 5's κ inference does not tag it, because it cannot see through the
            # union-local carrier projection to conclude "string key" — that gap is the
            # reopening capability, recorded in the backlog. Until it lands this is
            # SHAPE-gated, exactly like the `_build_param_list` `local_refs`/`ghost_vars`
            # precedent two branches above: the param is named `field_names` in a
            # `(node, field_names)` class-body collector. That shape is unique to the three
            # `_collect_class_*_constants` collectors and absent from every corpus program,
            # so byte-inertness is structural rather than argued; the byte-diff sweep is
            # still run. The param is NOT forwarded to any sibling bridge (its sole use is
            # the membership), so the cross-method κ agreement the deferred I4 fixpoint
            # worries about cannot bite.
            #
            # DELIBERATELY gated on `_formal_params` rather than a new `self._<name>` field
            # carrying the function name: `_build_param_list` has an UN-TRUSTED mirror
            # counterpart, so writing new emitter state there triggers the §10.4 verbatim
            # re-port AND a frame widening on a field the emitted record does not have
            # (the L14-b shape). `_param_type_str`'s mirror counterpart IS `\trusted`, so
            # keeping the whole decision inside it costs nothing. (Lesson (dd).)
            if (arg == "field_names"
                    and list(getattr(self, "_formal_params", []) or [])
                    == ["node", "field_names"]):
                _sk = "string"
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
        # faithful for-over-literal (self-tcb-reduction): {name: [String-elt IR]} for locals
        # bound to an all-string tuple/list literal (populated per-body in `_typed_local_vars`).
        self._str_literal_seq_locals = {}
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
        # tierA-listfield-impl.md: seq locals whose appended elements lowered to an
        # `emit_ir` ADT constructor application. Populated at the `.append` site
        # (statements.py) and read ONLY by the @mutable_state-gated
        # `_bind_listfield_from_seq` — write-only elsewhere, so byte-inert.
        self._emit_ir_seq_locals: set = set()
        # `_fin` RECOGNIZER vein: seq local -> the RECORD CLASS its elements carry, recorded
        # at the `.append` site from the callee's declared return. Read only by the
        # `@mutable_state`-gated `_bind_listfield_from_seq`; write-only elsewhere, so the
        # emitted text is unchanged wherever it is empty.
        self._record_seq_locals: dict = {}
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
        # self-tcb-reduction Tier-5 (union/match cluster C5): a local bound to an
        # OPTION-tuple-returning self-call (`union_info = self._match_subject_union_info
        # (...)`, return type `option (τ...)`). Distinct from `_ghost_tuple_vars` (a
        # BARE tuple, always-present) — this local is a real `option`, so its `is not
        # None` guard is a `match … with None/Some` discriminant and its tuple-unpack
        # unwraps the `Some`. name → the full `option (τ...)` WhyML type string.
        self._option_tuple_vars: Dict[str, str] = {}
        # self-tcb-reduction lever #1 sub-inc A cap (c): locals bound to an
        # `option string`-returning self-call (`_rec = self._record_valued_expr_whyml_type
        # (val_ir)`). Pre-declared `ref None`; `is not None` guard is a `match … None/Some`
        # discriminant; a bare `return <local>` threads into the Optional[str] union arm.
        self._option_str_return_vars: Set[str] = set()
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
        # self-tcb-reduction Tier-5 (union/match cluster, `_maybe_inject_union_return`):
        # a LOCAL bound from a nested-map self-field `.get` (`vinfo =
        # self._variant_types.get(func_ret)`, whose value type is `map string (option
        # hval)`) is itself a `map string (option hval)` — so a chained `.get` on it
        # (`constructors = vinfo.get("constructors", {})`) unwraps to a real `hval`. The
        # `_dict_value_types` registration that carries this fact is set only at
        # body-emission time (`_typed_local_vars`), TOO LATE for this setup-time prescan;
        # seed `vmap` here directly off the field type. Byte-inert: no corpus function
        # reads a `map string (option (map string (option hval)))` self-field.
        vmap: Set[str] = set()

        def _get_dotted_recv(v: Dict[str, Any]) -> Optional[str]:
            if not (isinstance(v, dict) and v.get("type") == "Call"):
                return None
            fn = v.get("func", "")
            if isinstance(fn, str) and fn.endswith(".get"):
                return fn[:-len(".get")]
            if fn == "get":
                fld = self._getattr_self_field(v.get("receiver") or {})
                if fld:
                    return "self.{}".format(fld)
            return None

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
                    # self-tcb-reduction Tier-5 (union/match cluster C1b): a `.get` on a
                    # `Dict[str, PyVal]` PARAM/LOCAL (`_dict_value_types` codomain "hval",
                    # e.g. `stmt.get("subject", {})` / `vinfo.get("constructors", {})`)
                    # unwraps the `option hval` to a real `hval` -> the target is pyval.
                    # Corpus-inert: no reference program has a `map string (option hval)`
                    # param/local `.get` receiver.
                    if getattr(self, "_dict_value_types", {}).get(recv) == "hval":
                        return True
                    # `_maybe_inject_union_return`: a `.get` on a `vmap` local (`vinfo`, a
                    # `map string (option hval)` bound from `self._variant_types.get`)
                    # unwraps the `option hval` to a real `hval` -> the target is pyval.
                    if recv in vmap:
                        return True
                return False
            # self-tcb-reduction _typeddict_field_access (b): a SUBSCRIPT
            # `self._record_types[rec_name]` on a `map string (option hval)` self-field
            # (value_type "hval") unwraps the `option hval` to an `hval` (the Layer-C
            # `_handle_subscript` path) -> the target local is pyval. Also a subscript on a
            # pyval LOCAL (`rec_info[k]`) is itself pyval. Corpus-inert (no `Dict[str, Any]`
            # subscript there).
            if vt == "Subscript":
                sv = v.get("value")
                if isinstance(sv, dict):
                    if sv.get("type") in ("Attribute", "FieldGet"):
                        so = sv.get("object")
                        sa = sv.get("attr") or sv.get("field")
                        dot = None
                        if isinstance(so, dict) and so.get("type") == "Var" and sa:
                            dot = "{}.{}".format(so.get("name"), sa)
                        elif isinstance(so, str) and sa:
                            dot = "{}.{}".format(so, sa)
                        if dot is not None and self._self_field_dict_nu(dot) == "hval":
                            return True
                    if sv.get("type") == "Var" and sv.get("name") in pyval:
                        return True
                    # self-tcb-reduction (union/match cluster): a NESTED subscript
                    # `vinfo["constructors"][ctor]` — the base `vinfo["constructors"]` is a
                    # subscript on a `vmap`/pyval hval-map local (`vinfo`), so it reads an
                    # `hval`, and the outer subscript reads the value `hval` (cap ii).
                    if sv.get("type") == "Subscript":
                        _ssv = sv.get("value")
                        if (isinstance(_ssv, dict) and _ssv.get("type") == "Var"
                                and (_ssv.get("name") in vmap or _ssv.get("name") in pyval)):
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

        # self-tcb-reduction Tier-5 (union/match cluster, `_maybe_inject_union_return`):
        # SEED `vmap` — a local bound from a `.get` on a nested-map self-field whose
        # value type is a `map string (option hval)` (`vinfo = self._variant_types.get`).
        # Such a local is a `map string (option hval)`, so a further `.get` on it yields
        # an `hval` (handled in `_rhs_is_pyval`). Byte-inert (no corpus self-field is a
        # `map string (option (map string (option hval)))`).
        for _st in assigns:
            _vt = _st.get("target")
            if not isinstance(_vt, str) or _vt in vmap:
                continue
            _recv = _get_dotted_recv(_st.get("value") or {})
            if _recv is None:
                continue
            _nu = self._self_field_dict_nu(_recv)
            if isinstance(_nu, str) and _nu.startswith("map ") and "hval" in _nu:
                vmap.add(_vt)

        # self-tcb-reduction Tier-5 (union/match cluster C4): SEED the VALUE target of a
        # `for k, v in <hval>.items()` loop as pyval — the loop var `v` (`ctor`) is a real
        # `hval` per iteration (bound `hval_values_get` in `_handle_for_stmt`), so a body
        # `payload = v.get("payload", [])` is itself pyval. The `_handle_for_stmt` loop
        # tagging happens only during BODY emission (too late for this setup-time prescan),
        # so seed it here. Byte-inert: no corpus loop iterates an hval `.items()`.
        def _seed_items(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "For":
                    _tt = node.get("tuple_targets") or []
                    _it = node.get("iter") or {}
                    if (len(_tt) == 2 and isinstance(_tt[1], str) and _tt[1] != "_"
                            and (self._hval_items_recv(_it) is not None
                                 or self._hval_items_local_recv(_it) is not None)):
                        pyval.add(_tt[1])
                for _v in node.values():
                    _seed_items(_v)
            elif isinstance(node, list):
                for _s in node:
                    _seed_items(_s)

        # Expose the GROWING `pyval` set as `self._pyval_locals` for the duration of the
        # fixpoint so the `.items()`-over-pyval-LOCAL recognizer (`_hval_items_local_recv`
        # -> `_expr_is_pyval`) sees a local that this same fixpoint just classified —
        # `for ctor_name, ctor in constructors.items()` can only be seeded AFTER
        # `constructors` (bound from `vinfo.get`) is itself recognized. Restored to the
        # final set by the caller (`_reset_function_state`). Byte-inert for any function
        # with no pyval self-field / union-map local (the set stays empty).
        self._pyval_locals = pyval

        changed = True
        while changed:
            changed = False
            if getattr(self, "_value_semantic", False):
                _before = len(pyval)
                _seed_items(body_stmts)
                if len(pyval) != _before:
                    changed = True
            for st in assigns:
                tgt = st.get("target")
                if not isinstance(tgt, str) or tgt in pyval:
                    continue
                if _rhs_is_pyval(st.get("value") or {}):
                    pyval.add(tgt)
                    changed = True
        # self-tcb-reduction _namedtuple_positional_access: a pyval local read as a
        # COLLECTION — `len(X)` or `X[<Number>]` (an ordered hval sequence like
        # `rec_info["fields"]`, not a string leaf) — must bind the RAW `hval` (so
        # `hval_len`/`hval_nth_str` type-check), NOT the `HStr`-projected string that a
        # string-consumed pyval local (`rec_info["whyml_name"]`) needs. Record such
        # locals so the assign binder reads their `X = <owner>[key]` RHS raw. Byte-inert
        # (empty when no pyval local is `len`/Number-index read).
        coll: Set[str] = set()

        def _scan_coll(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("type") == "Call" and node.get("func") == "len":
                    _la = node.get("args") or []
                    if (_la and isinstance(_la[0], dict) and _la[0].get("type") == "Var"
                            and _la[0].get("name") in pyval):
                        coll.add(_la[0]["name"])
                if node.get("type") == "Subscript":
                    _sv = node.get("value")
                    _si = node.get("index")
                    if (isinstance(_sv, dict) and _sv.get("type") == "Var"
                            and _sv.get("name") in pyval
                            and isinstance(_si, dict) and _si.get("type") == "Number"):
                        coll.add(_sv["name"])
                for _cv in node.values():
                    _scan_coll(_cv)
            elif isinstance(node, list):
                for _cs in node:
                    _scan_coll(_cs)

        _scan_coll(body_stmts)
        self._pyval_coll_locals = coll
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
        # set/frozenset arm: the faithful StrSet model `map string bool` (present=true),
        # matching the `frozenset`-RETURN model (subclasses_of/bases_closure emit
        # `map string bool` via set_add / const false) — NOT the old int-keyed
        # `map int (option int)`, which int-hashed a string key at a `k in <set>`
        # membership site (the "bare-set-key" bug). No corpus program has an
        # `Optional[set]`/`Union[..., set]` param, and the sole mirror consumer is
        # `exception_model.predicate_definitions.needed` -> byte-inert by construction.
        # `dict` is left on the int model (a separate, out-of-scope faithfulness gap).
        m = {"int": "int", "bool": "int", "str": "string", "float": "real",
             "list": "array int", "bytes": "array int", "bytearray": "array int",
             "dict": "map int (option int)", "set": "map string bool",
             "frozenset": "map string bool", "tuple": "array int",
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
        # V1 pyconst-dispatch (self-tcb-reduction M5, B-bucket): inside `_classify_literal_value`
        # the MIDDLE tuple slot is the Python constant VALUE — faithfully `pyconst_val`. In the
        # FIRST tuple return (`("int", None, {...})`, which `_refine_tuple_return_type` slots) the
        # middle is a `None` literal; other returns use a `True`/`False` literal or the pyconst_val
        # local `v`. Gated on the plain-BOOL flag `_pyconst_val_tuple_slot` (set only while emitting
        # `_classify_literal_value`, from the TRUSTED `_emit_function`) — a getattr-bool + set-
        # membership + tuple-`in`, the SAME clean shape as the `_mutable_state_classes` /
        # `_tuple_*_slot_locals` reads above, so it lowers to `False`/dead-code in every other
        # method incl. the giants (which never read `_current_emitting_func` as a string). Returns
        # the type-name STRING "pyconst_val" (no pyconst_val VALUE constructed here). slot-0 String
        # and slot-2 DictLit fall through to the string/emit_ir recognizers below.
        if getattr(self, "_pyconst_val_tuple_slot", False):
            if (t == "Var" and elt.get("name")
                    in getattr(self, "_pyconst_val_local_vars", set())):
                return "pyconst_val"
            if t in ("None", "Bool"):
                return "pyconst_val"
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
        # PYTHON-AST NODE CTOR FAMILY: a `-> "Tuple[List[ExprIR], List[ExprIR]]"` method
        # (`_call_args`) really returns a PAIR OF NODE LISTS. `ir_resolve` records the
        # WhyML tuple shape on `return_tuple_whyml`; without it the `\trusted` stub's
        # `pass` body gives `find_return_type -> "unit"` and BOTH slots int-erase at every
        # unpack site (`args, keywords = self._call_args(")")` bound two `ref 0`s). This
        # ONE refinement serves BOTH return-type producers (lesson (am), two producers):
        # `_compute_return_type` (the stub's own `val`) and `_build_method_return_type_map`
        # (the `self.<m>(...)` call site) each call this method on their raw type.
        # relaunch #16: honour whatever `ir_resolve` recorded, not just the two-node-list
        # literal. `ir_resolve` only records a shape whose every slot is in its CLOSED
        # per-slot table, so an unrecognised annotation still arrives here as `None` and
        # int-erases exactly as before. Still gated on `_uses_pyast_parser()`.
        _rtw = func.get("return_tuple_whyml", "")
        if _rtw and self._uses_pyast_parser():
            return _rtw
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
        _saved_cef = getattr(self, "_current_emitting_func", None)
        _st = dict(symtab)
        for _k, _ty in (func.get("param_annotations") or {}).items():
            if _st.get(_k) in (None, "Any"):
                _st[_k] = _ty
        self._current_symbol_table = _st
        _nm = func.get("name", "")
        if "__" in _nm:
            self._current_self_type = _nm.split("__", 1)[0]
        # self-tcb-reduction Layer-2: set the emitting-func context so any per-handler-scoped
        # emit_ir flow-typing (`_effective_emit_ir_node_keys`, e.g. the receiver/slice
        # recognizer's `lower`/`upper`/`step` node keys) fires here too — else a scoped
        # emit_ir tuple slot mis-types as int and the `let` unpack fails to type-check.
        self._current_emitting_func = _nm
        _saved_teisl = getattr(self, "_tuple_emit_ir_slot_locals", None)
        try:
            # tuple-return-of-emit_ir: a tuple slot bound to an emit_ir LOCAL (`slice_node`/
            # `lower_ir`, first-assigned from an emit_ir `.get(...)` projection) is not in the
            # func's symbol_table — collect the body's emit_ir locals so `_infer_tuple_slot_type`
            # types those slots `emit_ir` (matching the `ref (IrOther "")` body pre-decl), else
            # the `option (τ...)` return type mis-types them `int` and the unpack fails L3.
            self._tuple_emit_ir_slot_locals = self._collect_emit_ir_result_locals(body_stmts)
            slots = [self._infer_tuple_slot_type(e, array_vars, dict_vars, _st) for e in elts]
        finally:
            self._current_symbol_table = _saved_st
            self._current_self_type = _saved_cs
            self._current_emitting_func = _saved_cef
            self._tuple_emit_ir_slot_locals = _saved_teisl
        if len(slots) == return_type.count(",") + 1 and any(s != "int" for s in slots):
            return "(" + ", ".join(slots) + ")"
        # self-tcb-reduction Tier-5 (union/match cluster C1b): flow-type the tuple slots of
        # the two nested-hval union readers from their RETURNED locals. The first tuple
        # return's element expressions ARE `elts` (the real `return var_name, vinfo` /
        # `return ctor_name, ctor`), so keying the slot type on the returned Var's role is
        # exact (matches the body's actual hval-projection lowering): a name/tag var is a
        # `string`, `vinfo` is the nested `map string (option hval)` (a `_variant_types`
        # value), `ctor` is a single `hval`. Byte-inert: gated on these two method names,
        # which no reference program defines.
        _nm2 = func.get("name", "")
        if (_nm2.endswith("_match_subject_union_info")
                or _nm2.endswith("_union_ctor_for_arm_tag")):
            _slot_role = {
                "var_name": "string", "vinfo": "map string (option hval)",
                "ctor_name": "string", "ctor": "hval",
            }
            _names = [e.get("name") if (isinstance(e, dict) and e.get("type") == "Var")
                      else None for e in elts]
            _s = [_slot_role.get(n, "int") for n in _names]
            if (len(_s) == return_type.count(",") + 1
                    and all(x != "int" for x in _s)):
                return "(" + ", ".join(_s) + ")"
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
        # Optional-tuple return (self-tcb-reduction Tier-5 value model): a function
        # whose return annotation is a synthesized `_union_*` (an `Optional[X]`
        # normalized by Module5) AND whose body BOTH returns a tuple AND returns the
        # `None` literal is an `Optional[Tuple[τ...]]` reader. Its faithful WhyML type
        # is the BUILT-IN `option (τ...)` — not the raw tuple `(τ...)` (which cannot
        # carry `None`) and not the `Arm_i_0 int` union (whose synthesized payload is
        # a scalar `int`, not the tuple). Gated on an ACTUAL `return None`: such a
        # function currently emits `raise (Return_<arity> 0)` (bare int) against a
        # `(τ...)` tuple slot — an L3 type error — so NO passing corpus baseline
        # contains one (byte-inert). `option` + tuples are Why3 built-ins → no axiom.
        if (isinstance(ann, str) and ann.startswith("_union_")
                and return_type.startswith("(") and "," in return_type
                and IRScanner.has_none_return(body_stmts)):
            return f"option {return_type}"
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
        # TERM CARRIER, general path (L13 / cursor-nest): a method of a `@mutable_state`
        # class annotated `-> Term`, in a file where the CERTIFIED `term` inductive is
        # actually emitted (`_term_adt_spec` non-None), returns `term` — not the `int`
        # that the mirror's stubbed `Term = 0` alias (`proof2why3/ir.py:121`, the
        # string-form 9-arm union the stub generator cannot express) otherwise implies.
        # This is the SAME shape as the `_returns_stmt_ir`/`_returns_emit_ir` overrides
        # directly below: the Python type is one thing, the MODEL type is the sum.
        # Until this override, the `term` carrier was reachable ONLY through the
        # whole-function recognizers in `generic_fold.py` (measured: 6 of 80 emitted
        # signatures in parser.mlw were term-typed, every one recognizer-generated),
        # so no ordinary body could thread a `term` through the descent chain.
        # TRIPLE-GATED — `-> Term` annotation AND the certified inductive present AND
        # the emitter-model `@mutable_state` class.
        if (getattr(self, "_term_adt_spec", None)
                and func.get("return_annotation") == "Term"
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            return "term"
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
        # PYTHON-AST NODE CTOR FAMILY (increment 11): a `-> "List[ExprIR]"` method — the
        # STATEMENT cluster's return interface (`block`, `_if_tail`, `_else_block`,
        # `simple_stmt`, `statement`) — returns `array emit_ir`. Handled BEFORE the
        # `return_type == "int"` branch below because a `\trusted` stub's body is `pass`,
        # so `find_return_type` gives "unit" and that branch never fires; `-> str` already
        # carries the same `ret == "unit" and trusted` disjunct for the same reason.
        # `ir_resolve` sets `return_value_type` to the literal `emit_ir` only for that
        # annotation, so this is inert everywhere else.
        if (ann == "list" and func.get("return_value_type") == "emit_ir"
                and return_type in ("int", "unit")
                and self._uses_pyast_parser()):
            return "array emit_ir"
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
        elif ann == "bool" and return_type == "unit" and func.get("trusted"):
            # self-tcb-reduction GAP #2, PREDICATE TWIN: the `-> str` disjunct directly
            # above, for a `\trusted` stub declared `-> bool`. Same mechanism, same
            # reason: the stub's placeholder body is a bare `pass`, so
            # `find_return_type` gives "unit" and the `val` announces `: unit` — a
            # CONVERTED caller's `if self._line_ends_with_colon():` then has a `unit`
            # in a boolean position and the file fails L3-tc. The DECLARED annotation
            # is the authority on what a trusted stub returns.
            # THE PROMOTED TYPE IS `int`, NOT Why3's `bool`: this emitter models a
            # Python bool as the int 0/1 END-TO-END — every CONVERTED `-> bool` method
            # in the same mirror emits `: int` (`_with_parenthesized`,
            # `_looks_like_type_alias`), every boolean test is `(<e>) <> 0`, and the
            # `Return` exception carries an int. Promoting to `bool` would make the
            # trusted stub the ONLY bool-typed predicate in the file and re-break the
            # call site it is meant to fix. Gated on `func["trusted"]`: a real corpus
            # `-> bool` function has a return statement, so `return_type` is never
            # "unit" there -> byte-identical for the reference corpus.
            return_type = "int"
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
        elif ann == "PyConstVal" and return_type in ("int", "unit"):
            # LITERAL-VALUE MODEL (relaunch #12): the RETURN INTERFACE that makes a Python
            # literal VALUE modellable. `_parse_number(s)` is a pure total function of the
            # token text returning an int, a float or a complex; declared `-> "PyConstVal"`
            # its emitted `val` is an UNINTERPRETED `string -> pyconst_val`, the honest
            # abstraction (equal texts give equal values; nothing else claimed in either
            # direction). `"unit"` is the case that matters: the only such helper is a
            # `\trusted` stub whose placeholder body is a bare `pass`, so its DECLARED
            # annotation is the sole authority on what it returns. The tag names a type no
            # corpus program mentions, so every corpus file is byte-identical.
            return_type = "pyconst_val"
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

    def _is_should_skip_method(self, func: Dict[str, Any]) -> bool:
        """functiondef-node wall recognizer (self-tcb-reduction M5, C-bucket): True iff
        `func` is the Module5 mirror's `_should_skip_method` and the py_functiondef_node
        theory is emitted. Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (nm.endswith("_should_skip_method")
                and self._uses_py_functiondef_node())

    def _emit_should_skip_method_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """functiondef-node wall: emit the FAITHFUL whole-body lowering of

            def _should_skip_method(self, node: ast.FunctionDef) -> bool:
                if not self._current_class:
                    return False
                if node.name.startswith('__') and node.name.endswith('__'):
                    return True
                return False

        The dunder test lowers to the FAITHFUL `str_startswith_op`/`str_endswith_op`
        (substring-based ensures) over `func_name_ast node` — the accessor APPLIED TO the
        node, NOT a node-free hashed stub. `self._current_class` truthiness -> the opaque
        `m5_current_class_present` abstract reader (a sound abstraction of genuine instance
        state, like symtab_mem). `assigns \nothing` (pure bool). Corpus-inert.

        `@property` SUPPORT (relaunch #16): the decorator-existence disjunct is GONE from
        BOTH producers — the live/mirror source AND this synthesized body (lesson (am):
        a SYNTHESIZED body is a second producer, and editing only the source leaves the
        emitted theory silently stating the OLD behaviour)."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        self._add_abstract_op(
            "val str_startswith_op (s: string) (prefix: string) : int\n"
            "    ensures { (result = 0) || (result = 1) }\n"
            "    ensures { (result = 1) <->\n"
            "      (String.length prefix <= String.length s /\\\n"
            "       String.substring s 0 (String.length prefix) = prefix) }")
        self._add_abstract_op(
            "val str_endswith_op (s: string) (suffix: string) : int\n"
            "    ensures { (result = 0) || (result = 1) }\n"
            "    ensures { (result = 1) <->\n"
            "      (String.length suffix <= String.length s /\\\n"
            "       String.substring s (String.length s - String.length suffix)\n"
            "         (String.length suffix) = suffix) }")
        return [
            f"  let {name} (self: {cls}) (node: py_functiondef_node) : bool",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    if not m5_current_class_present then false",
            "    else if (str_startswith_op (func_name_ast node) \"__\" = 1)"
            " && (str_endswith_op (func_name_ast node) \"__\" = 1) then true",
            "    else false",
        ]

    def _is_build_overload_param_guard(self, func: Dict[str, Any]) -> bool:
        """functiondef-node cluster recognizer (self-tcb-reduction M5, C-bucket): True iff
        `func` is the Module5 mirror's `_build_overload_param_guard` and the arg-node theory
        is emitted. Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (nm.endswith("_build_overload_param_guard")
                and self._uses_build_overload_param_guard())

    def _emit_build_overload_param_guard_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """functiondef-node cluster: emit the FAITHFUL whole-body lowering of

            def _build_overload_param_guard(self, node) -> Optional[Dict]:
                guards = []
                for arg in node.args.args:
                    if arg.arg == 'self': continue
                    ann = arg.annotation
                    if ann is None: continue
                    t_name = self._overload_type_name(ann)
                    if t_name is None: continue
                    guards.append({Call isinstance [Var arg.arg, Var t_name]})
                if not guards: return None
                acc = guards[0]
                for g in guards[1:]: acc = {BinOp and acc g}
                return acc

        The loop lowers to the CONCRETE `build_overload_guard_acc None (func_args_ast node)`
        fold (theory-defined, structural over the real arg list): `func_args_ast node` TAKES
        the node, each guard is `IrCallN "isinstance" [IrVar (arg_name_ast a); IrVar tn]`
        (both args referenced, no node-free stub), conjoined left-associated via
        `IrBinOp "and"`. `arg.arg == 'self'` -> `arg_name_ast a = "self"`; `arg.annotation`
        None-test -> `option emit_ir` match; `self._overload_type_name(ann)` -> the opaque
        `overload_type_name_op` sibling reader. Returns `option emit_ir` (None iff no guard).
        isinstance_op = 0, `assigns \nothing` (pure). Corpus-inert."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        return [
            f"  let {name} (self: {cls}) (node: py_functiondef_node) : option emit_ir",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    build_overload_guard_acc_prog None (func_args_ast node)",
        ]

    def _is_synthesize_overload_guard(self, func: Dict[str, Any]) -> bool:
        """functiondef-node cluster recognizer (self-tcb-reduction M5, C-bucket): True iff
        `func` is the Module5 mirror's `_synthesize_overload_guard` and the ens_node theory
        is emitted. Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (nm.endswith("_synthesize_overload_guard")
                and self._uses_synthesize_overload_guard())

    def _emit_synthesize_overload_guard_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """functiondef-node cluster: emit the FAITHFUL whole-body lowering of

            def _synthesize_overload_guard(self, node) -> List[Dict]:
                guard = self._build_overload_param_guard(node)
                if guard is None: return []
                clauses = []
                for csl_ens in getattr(node, 'csl_ensures', []) or []:
                    q_ir = self._csl_to_ir(csl_ens.expr)
                    clauses.append({BinOp ==> guard q_ir})
                return clauses

        The guard `self._build_overload_param_guard(node)` -> the sibling
        `build_overload_guard_acc_prog None (func_args_ast node)` fold (`option emit_ir`);
        `guard is None -> return []` -> the `materialize_ir Seq.empty` empty-array arm; the
        clause loop -> the CONCRETE `synth_overload_clauses guard (func_csl_ensures_ast node)`
        fold, each clause `IrBinOp "==>" guard (csl_to_ir_op (ens_expr_ast e))` (both operands
        referenced, no node-free stub), CONSed head-first into a `seq emit_ir` and materialized
        to the CANONICAL `array emit_ir` List-return. `self._csl_to_ir` -> the opaque
        `csl_to_ir_op` sibling reader. Returns `array emit_ir`. `assigns \\nothing` (pure).
        Corpus-inert."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        return [
            f"  let {name} (self: {cls}) (node: py_functiondef_node) : array emit_ir",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    match build_overload_guard_acc_prog None (func_args_ast node) with",
            "    | None -> materialize_ir Seq.empty",
            "    | Some guard ->",
            "      materialize_ir (synth_overload_clauses_prog guard (func_csl_ensures_ast node))",
            "    end",
        ]

    def _is_is_overload_stub(self, func: Dict[str, Any]) -> bool:
        """functiondef-node cluster recognizer (self-tcb-reduction M5, C-bucket): True iff
        `func` is the Module5 mirror's `_is_overload_stub` and the pyast_stmt PSPass/
        PSExprEllipsis extension + func_body_ast + decorator_has_name_or_attr are emitted.
        Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (nm.endswith("_is_overload_stub")
                and self._uses_is_overload_stub())

    def _emit_is_overload_stub_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """functiondef-node cluster: emit the FAITHFUL whole-body lowering of

            @staticmethod
            def _is_overload_stub(node: ast.FunctionDef) -> bool:
                has_overload = False
                for d in node.decorator_list:
                    if isinstance(d, ast.Name) and d.id == "overload":
                        has_overload = True; break
                    if isinstance(d, ast.Attribute) and d.attr == "overload":
                        has_overload = True; break
                if not has_overload: return False
                body = node.body
                if len(body) != 1: return False
                stmt = body[0]
                if isinstance(stmt, ast.Pass): return True
                if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                        and stmt.value.value is Ellipsis): return True
                return False

        The `@overload` decorator scan (Name OR Attribute, `break`-on-first) lowers to the
        CONCRETE `decorator_has_name_or_attr_prog "overload" (func_decorator_list_ast node)`
        existence fold — `func_decorator_list_ast node` TAKES the node, a decorator matches
        iff `(is_var d || is_attribute d) && name_of d = "overload"` (name_of covers both
        `d.id` and `d.attr`). `node.body` -> `func_body_ast node` (the shared `psl` cons-list,
        TAKING the node); `len(body) != 1` -> `psl_len (func_body_ast node) <> 1`; `body[0]`
        -> `psl_nth 0 (func_body_ast node)`. The `isinstance(stmt, ast.Pass)` /
        `isinstance(stmt, ast.Expr(Constant(Ellipsis)))` discrimination lowers to the FAITHFUL
        `is_pass_node` / `is_expr_ellipsis_node` predicates over that REAL element (no node-free
        stub, no isinstance_op-0-0 constant). Every guard reads the node. `@staticmethod`
        (no self param), `assigns \\nothing` (pure bool). Corpus-inert."""
        name = whyml_ident(func["name"])
        is_static = (func.get("is_static") or func.get("staticmethod")
                     or not func.get("self_type"))
        self_part = ("" if is_static
                     else f"(self: {whyml_ident(func['self_type'].lower())}) ")
        return [
            f"  let {name} {self_part}(node: py_functiondef_node) : bool",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    if not (decorator_has_name_or_attr_prog \"overload\""
            " (func_decorator_list_ast node)) then false",
            "    else if psl_len (func_body_ast node) <> 1 then false",
            "    else",
            "      let stmt = psl_nth 0 (func_body_ast node) in",
            "      if is_pass_node stmt then true",
            "      else if is_expr_ellipsis_node stmt then true",
            "      else false",
        ]

    def _is_act_guard(self, func: Dict[str, Any]) -> bool:
        """csl_clause contract-clause recognizer (self-tcb-reduction, Module3 mirror): True
        iff `func` is the Module3_Weaver mirror's `_act_guard` and the csl_clause theory
        (act_node/csl_clause/clause_list + discriminants + clause_expr_of + act_clauses_of +
        act_guard_fold) is emitted. Corpus-inert (no corpus program has this method)."""
        nm = str(func.get("name", ""))
        return (nm.endswith("_act_guard")
                and self._uses_act_guard())

    def _emit_act_guard_bespoke(self, func: Dict[str, Any]) -> List[str]:
        """csl_clause: emit the FAITHFUL whole-body lowering of

            @staticmethod
            def _act_guard(act: Act) -> "ExprIR":
                givens = [cl.expr for cl in act.clauses if isinstance(cl, Given)]
                if not givens: return CSLBool(True)
                g = givens[0]
                for extra in givens[1:]: g = BinOp(g, "and", extra)
                return g

        The list-comprehension filter+project `[cl.expr for cl in act.clauses if
        isinstance(cl, Given)]` and the subsequent `BinOp "and"` fold lower to the CONCRETE
        certified `act_guard_fold None (act_clauses_of act)` (preamble.py csl_clause theory):
        `act.clauses` -> `act_clauses_of act` (the opaque `Act` node reader, TAKING the node);
        `isinstance(cl, Given)` -> the `is_given_node` discriminant; `cl.expr` ->
        `clause_expr_of`; `BinOp(g, "and", extra)` -> the certified `IrBinOp "and"` ctor
        (left-nested); `CSLBool(True)` -> `IrBoolC 1`. Every read is over the REAL clause list
        (no isinstance_op-0-0 constant, no int-erased facade). `@staticmethod` (no self param),
        `assigns \\nothing` (pure ExprIR construction). Corpus-inert."""
        name = whyml_ident(func["name"])
        is_static = (func.get("is_static") or func.get("staticmethod")
                     or not func.get("self_type"))
        self_part = ("" if is_static
                     else f"(self: {whyml_ident(func['self_type'].lower())}) ")
        return [
            f"  let {name} {self_part}(act: act_node) : emit_ir",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            "    act_guard_fold None (act_clauses_of act)",
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

    def _recognize_str_pair_lookup(self, func: Dict[str, Any]):
        """module-const-str-pairs first-match lookup recognizer (self-tcb-reduction):
        recognize the ORDERED linear-scan lookup over a module-level constant
        list-of-str-pairs (`module_const_str_pairs`, collected front-end):

            def f(name: str) -> str:
                for src, dst in NAME:
                    if name == src:
                        return dst
                return name

        Returns `(param, pairs)` for the faithful chained-if lowering, else None
        (fail-closed). Requires EXACTLY a `For`-over-the-const then a `return <param>`,
        a single `str` param, a 2-var tuple target `(src, dst)`, and a For body that is
        exactly `if <param> == <src>: return <dst>` (no `orelse`). Any other shape keeps
        its existing lowering. The const's ORDER is load-bearing (first match wins), so
        the chained `if` mirrors the list order. Fires only on this exact shape over a
        collected str-pair const → byte-identical for every corpus program."""
        pairs_map = getattr(self, "ir", {}) or {}
        pairs_map = pairs_map.get("module_const_str_pairs") or {}
        if not pairs_map:
            return None
        body = func.get("body") or []
        if len(body) != 2:
            return None
        s_for, s_ret = body[0], body[1]
        if not (isinstance(s_for, dict) and s_for.get("stmt") == "For"
                and isinstance(s_ret, dict) and s_ret.get("stmt") == "Return"):
            return None
        formals = func.get("formal_params") or []
        if len(formals) != 1:
            return None
        param = formals[0]
        if (func.get("param_annotations") or {}).get(param) != "str":
            return None

        def _is_var(n, nm):
            return (isinstance(n, dict) and n.get("type") == "Var"
                    and n.get("name") == nm)

        # final `return <param>`
        if not _is_var(s_ret.get("value"), param):
            return None
        # For over a collected str-pair const, tuple target (src, dst)
        it = s_for.get("iter") or {}
        if not (isinstance(it, dict) and it.get("type") == "Var"):
            return None
        pairs = pairs_map.get(it.get("name"))
        if pairs is None:
            return None
        tts = s_for.get("tuple_targets") or []
        if len(tts) != 2:
            return None
        src_name, dst_name = tts
        fb = s_for.get("body") or []
        if len(fb) != 1 or not (isinstance(fb[0], dict) and fb[0].get("stmt") == "If"):
            return None
        iff = fb[0]
        if iff.get("orelse"):
            return None
        test = iff.get("test") or {}
        if not (isinstance(test, dict) and test.get("type") == "BinOp"
                and test.get("op") == "=="):
            return None
        l, r = test.get("left") or {}, test.get("right") or {}
        if not ((_is_var(l, param) and _is_var(r, src_name))
                or (_is_var(l, src_name) and _is_var(r, param))):
            return None
        ifbody = iff.get("body") or []
        if len(ifbody) != 1 or not (isinstance(ifbody[0], dict)
                                    and ifbody[0].get("stmt") == "Return"):
            return None
        if not _is_var(ifbody[0].get("value"), dst_name):
            return None
        return (param, pairs)

    def _emit_str_pair_lookup_bespoke(self, func: Dict[str, Any],
                                      param: str, pairs) -> List[str]:
        """module-const-str-pairs first-match lookup: emit the FAITHFUL whole-body
        lowering as a chained string if-then-else over the captured const pairs
        (`if str_eq_op <param> "s1" then "d1" else ... else <param>`) — the ordered
        first-match scan, default = the param (the loop falls through to `return name`).
        String equality bridges the abstract `str_eq_op` (native `=` on strings is
        program-illegal), exactly as the module-const-dict `.get` lowering does.
        `assigns \\nothing` (pure). Corpus-inert (recognizer-gated)."""
        name = whyml_ident(func["name"])
        self._add_abstract_op(
            "val str_eq_op (a: string) (b: string) : bool\n"
            "    ensures { result <-> (a = b) }")
        self_part = ""
        if (func.get("self_type")
                and not (func.get("is_static") or func.get("staticmethod"))):
            self_part = f"(self: {whyml_ident(func['self_type'].lower())}) "
        p = whyml_ident(param)
        chain = p
        for s, d in reversed(list(pairs)):
            chain = (f"(if str_eq_op {p} {whyml_string_literal(s)} "
                     f"then {whyml_string_literal(d)} else {chain})")
        return [
            f"  let {name} {self_part}({p}: string) : string",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            f"    {chain}",
        ]

    def _recognize_sorted_const_set(self, func: Dict[str, Any]):
        """module-const-str-sets `sorted(NAME)` recognizer (self-tcb-reduction):
        recognize the ENTIRE-body finite-membership-table expansion over a
        module-level constant string set/frozenset (`module_const_str_sets`,
        collected front-end):

            def f() -> list:
                return sorted(NAME)

        Returns the SORTED element list for the faithful constant `array string`
        lowering, else None (fail-closed). Requires EXACTLY a single-statement body
        `return sorted(<Var>)`, NO formal params, and `<Var>` a collected str-set
        const. `sorted` of a captured compile-time-constant set is a compile-time
        FOLD (the elements sorted here, at emit time) — NOT a runtime sort, so no
        WhyML sorting is modelled. Any other shape keeps its existing lowering.
        Fires only on this exact shape over a collected str-set const → byte-identical
        for every corpus program (the const shape is absent corpus-wide)."""
        sets_map = getattr(self, "ir", {}) or {}
        sets_map = sets_map.get("module_const_str_sets") or {}
        if not sets_map:
            return None
        if (func.get("formal_params") or []):
            return None
        body = func.get("body") or []
        if len(body) != 1:
            return None
        s = body[0]
        if not (isinstance(s, dict) and s.get("stmt") == "Return"):
            return None
        v = s.get("value") or {}
        if not (isinstance(v, dict) and v.get("type") == "Call"
                and v.get("func") == "sorted"):
            return None
        args = v.get("args") or []
        if len(args) != 1:
            return None
        a0 = args[0]
        if not (isinstance(a0, dict) and a0.get("type") == "Var"):
            return None
        members = sets_map.get(a0.get("name"))
        if not members:
            return None
        return sorted(members)

    def _emit_sorted_const_set_bespoke(self, func: Dict[str, Any],
                                       members: List[str]) -> List[str]:
        """module-const-str-sets `sorted(NAME)`: emit the FAITHFUL whole-body
        lowering as the exact constant `array string` literal over the captured
        const's elements sorted at emit time — the SAME `Array.make` form the
        native list-literal lowering produces (`(let _alit = Array.make N "s0" in
        _alit[1] <- "s1"; ...; _alit)`). A compile-time fold: no runtime sort, no
        new axiom (pure array-literal construction). Corpus-inert (recognizer-gated);
        non-facade (perturbing a captured element moves the emitted literal)."""
        name = whyml_ident(func["name"])
        self_part = ""
        if (func.get("self_type")
                and not (func.get("is_static") or func.get("staticmethod"))):
            self_part = f"(self: {whyml_ident(func['self_type'].lower())}) "
        n = len(members)
        lits = [whyml_string_literal(m) for m in members]
        if n == 1:
            arr = f"(Array.make 1 ({lits[0]}))"
        else:
            sets = "; ".join(f"_alit[{i}] <- ({lits[i]})" for i in range(1, n))
            arr = f"(let _alit = Array.make {n} ({lits[0]}) in {sets}; _alit)"
        return [
            f"  let {name} {self_part}() : array string",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            f"    {arr}",
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
        # SHADOWED-SELFCALL (relaunch #15): this body is SYNTHESIZED, so the generic
        # `#@ sibling_concrete` route in `expressions._handle_dotted_call` never sees its
        # `self._py_op_to_str(...)` call — the avatar was hard-coded here. A synthesized
        # body must honour the marker exactly as a lowered one does, or a marked callee
        # stays shadowed at precisely the call sites no source line names (and the
        # shadowed-selfcall RATCHET, which is per-METHOD, cannot move even when every
        # other site is concrete). Unmarked -> the historical avatar, byte-identical.
        _opw = self._pyx_sibling_call(func, "_py_op_to_str", "(compare_op0_ast expr)")
        L = [
            f"  let {name} (self: {cls}) (expr: py_compare_node) : emit_ir",
            "    requires { true }",
            "    ensures  { true }",
            "  =",
            f"    (IrBinOp {_opw}"
            " (self__py_expr_to_ir_1 (compare_left_ast expr))"
            " (self__py_expr_to_ir_1 (compare_comp0_ast expr)))",
        ]
        return L

    def _pyx_sibling_call(self, func: Dict[str, Any], callee: str, arg: str) -> str:
        """SHADOWED-SELFCALL (relaunch #15): render a `self.<callee>(<arg>)` call inside a
        SYNTHESIZED body — the concrete sibling application `(<cls>__<callee> self <arg>)`
        when `<callee>` carries `#@ sibling_concrete` and really is an emitted definition
        in this module, else the historical receiver-less avatar `(self__<c>_1 <arg>)`.
        Both gates must hold, so an unmarked or non-emitted callee is byte-identical."""
        _cn = whyml_ident(f"{func['self_type'].lower()}__{callee}")
        if (_cn in getattr(self, "_sibling_concrete_methods", set())
                and _cn in getattr(self, "_module_func_names", set())):
            return f"({_cn} self {arg})"
        return f"(self__{callee.lstrip('_')}_1 {arg})"

    def _inject_pyx_dispatch_uses(self, functions: List[Dict[str, Any]]) -> None:
        """L2 DISPATCH-EXPANSION: give the recognized dispatcher explicit ORDERING edges to
        the 23 handlers it will call.

        The calls are synthesized by `_emit_pyx_dispatcher_bespoke` from the SOURCE table,
        so `find_calls_in_ir` cannot see them — the body's only call node names the handler
        LOCAL, not the methods. Without an edge the dispatcher sorts alphabetically BEFORE
        `_py_expr_unaryop` / `_py_expr_walrus` / `_py_expr_tuple` and Why3 rejects the file
        with `unbound function or predicate symbol` (measured). `uses` is the existing
        explicit ordering-citation channel `sort_functions_by_scc` already honours for
        `#@ uses <lemma>`; the edges are intra-class and acyclic (no handler calls the
        dispatcher — they all go through the abstract `self__py_expr_to_ir_1` val), so no
        SCC is created. No-op unless the dispatcher shape is recognized -> byte-inert."""
        for func in functions:
            rec = self._recognize_pyx_dispatcher(func)
            if rec is None:
                continue
            own = {str(f.get("name", "")) for f in functions
                   if f.get("kind") == "method"
                   and f.get("self_type") == func.get("self_type")}
            edges = list(func.get("uses") or [])
            for _cls, handler in rec[2]:
                for raw in sorted(own):
                    if raw == handler or raw.endswith("_" + handler) or raw.endswith(handler):
                        if raw not in edges:
                            edges.append(raw)
                        break
            func["uses"] = edges

    def _recognize_pyx_dispatcher(self, func: Dict[str, Any]
                                  ) -> Optional[Tuple[str, Tuple[str, str], List[List[str]]]]:
        """L2 DISPATCH-EXPANSION: recognize a TYPE-KEYED HANDLER DISPATCHER body in either of
        the two shapes the emitter actually contains, and return
        `(param_name, (default_kind, default_arg), entries)` — the table's
        `[[<Cls>, <handler method>], ...]` IN SOURCE ORDER — or None.

        SHAPE A — fall back to a node (`_py_expr_to_ir`):
            handler_name = self.<TABLE>.get(type(<param>))
            if handler_name is not None:
                return getattr(self, handler_name)(<param>)
            return {"type": "<kind>"}                       -> default ("ctor", "<kind>")

        SHAPE B — REJECT an unsupported node (`_csl_to_ir`):
            handler_name = self.<TABLE>.get(type(<param>))
            if handler_name is None:
                raise <Exc>(...)
            return getattr(self, handler_name)(<param>)     -> default ("raise", "<Exc>")

        Shape B is the STRONGER of the two: its default arm is the source's own raise, so the
        emitted body proves an unsupported node cannot silently produce an IR node.

        Returning the ENTRIES (not just True) is what keeps the bespoke emission honest: the
        arms are read off the SOURCE table, so editing the table changes the emitted match.
        FAIL-CLOSED on every structural axis — exactly three statements, the bind through
        `self.<TABLE>.get` on a `type(<param>)` of the function's OWN parameter, the None test
        on the SAME local in the polarity its shape requires, a single `SelfGetattrDispatch`
        on the SAME local and the SAME param (never the `UnknownPyExpr` erasure tag Module 5
        emits for an unrecognized expression), and a table `_pyx_dispatch_tables` has already
        certified as a handler table OF THIS CLASS with an ADT to dispatch over. Anything else
        returns None and the function emits exactly as before."""
        body = func.get("body") or []
        if len(body) != 3:
            return None
        st0, st1, st2 = body
        if st0.get("stmt") != "Assign" or st1.get("stmt") != "If":
            return None
        local = st0.get("target")
        v0 = st0.get("value") or {}
        if not isinstance(local, str) or v0.get("type") != "Call":
            return None
        fn0 = str(v0.get("func") or "")
        if not (fn0.startswith("self.") and fn0.endswith(".get")):
            return None
        tbl_name = fn0[len("self."):-len(".get")]
        a0 = v0.get("args") or []
        if len(a0) != 1 or a0[0].get("type") != "Call" or a0[0].get("func") != "type":
            return None
        ta = a0[0].get("args") or []
        if len(ta) != 1 or ta[0].get("type") != "Var":
            return None
        param = ta[0].get("name")
        test = st1.get("test") or {}
        if (test.get("type") != "BinOp"
                or (test.get("left") or {}).get("type") != "Var"
                or (test.get("left") or {}).get("name") != local
                or (test.get("right") or {}).get("type") != "None"
                or st1.get("orelse")):
            return None
        op = test.get("op")
        ib = st1.get("body") or []
        if len(ib) != 1:
            return None
        default: Optional[Tuple[str, str]] = None
        disp: Dict[str, Any] = {}
        if op == "!=":
            # SHAPE A: the guarded branch dispatches, the trailing Return is the default.
            if ib[0].get("stmt") != "Return" or st2.get("stmt") != "Return":
                return None
            disp = ib[0].get("value") or {}
            dflt = st2.get("value") or {}
            if dflt.get("type") != "DictLit":
                return None
            dk = dflt.get("keys") or []
            dv = dflt.get("values") or []
            if (len(dk) != 1 or len(dv) != 1
                    or dk[0].get("type") != "String" or dk[0].get("value") != "type"
                    or dv[0].get("type") != "String"):
                return None
            default = ("ctor", str(dv[0].get("value")))
        elif op == "==":
            # SHAPE B: the guarded branch RAISES, the trailing Return dispatches.
            if ib[0].get("stmt") != "Raise" or st2.get("stmt") != "Return":
                return None
            exc = ib[0].get("exc_type")
            if not isinstance(exc, str) or not exc:
                return None
            disp = st2.get("value") or {}
            default = ("raise", exc)
        else:
            return None
        if (disp.get("type") != "SelfGetattrDispatch"
                or disp.get("handler") != local):
            return None
        da = disp.get("args") or []
        if len(da) != 1 or da[0].get("type") != "Var" or da[0].get("name") != param:
            return None
        entries = self._pyx_dispatch_table_named(str(func.get("self_type") or ""), tbl_name)
        if entries is None:
            return None
        return (str(param), default, entries)

    def _emit_pyx_dispatcher_bespoke(self, func: Dict[str, Any], param: str,
                                     default: Tuple[str, str],
                                     entries: List[List[str]]) -> List[str]:
        """L2 DISPATCH-EXPANSION: the faithful whole-body lowering of the recognized
        type-keyed handler dispatcher — a TOTAL match over the input-side node ADT
        (`preamble.py::_emit_pyx_expr_adt`), one arm per table entry in source order, plus
        the source's OWN default on the `Unknown` arm:

            match <view> <param> with
            | <P>Name _p -> <cls>___py_expr_name self _p
            | ...
            | <P>Unknown -> IrOther "UnknownPyExpr"      (shape A)
            | <P>Unknown -> raise <Exc>                  (shape B)
            end

        WHAT THIS REPLACES. The method was a `\trusted` stub, i.e.
        `val <cls>___<m> (self: <cls>) (<param>: emit_ir) : emit_ir` — the table, the dispatch
        AND the result all assumed. After it only the node VIEW is assumed (uninterpreted,
        pinned to the node's runtime class by the CONCRETE kind law), and the dispatch is
        proved: for a node of class K the result is provably K's handler applied to a
        K-payload. NO axiom, NO certificate beyond the co-landed ADT one.

        The ARMS ARE DERIVED FROM THE SOURCE TABLE, so this is not a hand-written body
        pretending to be the source's: a change to the table changes the emission, and a
        handler whose emitted parameter type disagrees with its ADT arm is a LOUD Why3 type
        error at L3-tc. Corpus-inert (recognizer-gated on the exact three-statement shape over
        a certified handler table)."""
        name = whyml_ident(func["name"])
        cls = whyml_ident(func["self_type"].lower())
        tbl_name = None
        for _c, _t, _e in self._pyx_dispatch_tables():
            if _c == func.get("self_type") and _e == entries:
                tbl_name = _t
                break
        if tbl_name is None:
            return []
        _adt, pfx, view, _kind, _tag = self._PYX_TABLE_ADT[tbl_name]
        by_name = {str(f.get("name", "")): whyml_ident(str(f.get("name", "")))
                   for f in (self.ir.get("functions") or [])
                   if f.get("kind") == "method"
                   and f.get("self_type") == func.get("self_type")}
        # EVERY exception the emitted body can propagate has to be DECLARED, or Why3 rejects
        # the function with `this expression raises unlisted exception ...` (measured:
        # `_csl_ctor_payload` raises PyCSLSemanticError). The dispatcher's `raises` summary is
        # therefore the union over the arms it can take: the source's own default raise, plus
        # what each HANDLER escapes — computed exactly the way `_emit_function` computes a
        # handler's own summary (body-escaping raises + callee-declared raises + the
        # handler's `#@ raises` contract), so the two cannot drift. This is strictly MORE
        # faithful than the `val` it replaces, which declared no raises at all while the live
        # method really does propagate its handlers' errors.
        _exc: Set[str] = set()
        if default[0] == "raise":
            _exc.add(str(default[1]))
        _by_raw = {str(f.get("name", "")): f for f in (self.ir.get("functions") or [])
                   if f.get("kind") == "method"
                   and f.get("self_type") == func.get("self_type")}
        for _ast_cls, _handler in entries:
            for _raw, _f in _by_raw.items():
                if not (_raw == _handler or _raw.endswith("_" + _handler)
                        or _raw.endswith(_handler)):
                    continue
                _hb = _f.get("body") or []
                _exc |= IRScanner.collect_escaping_exceptions(_hb)
                _exc |= self._callee_raised_in(_hb)
                for _rc in ((_f.get("contracts") or {}).get("raises") or []):
                    _e = _rc.get("exc_type") if isinstance(_rc, dict) else None
                    if _e:
                        _exc.add(str(_e))
                break
        _raises = sorted({safe_exc_name(e) for e in _exc if e})
        L = [
            f"  let {name} (self: {cls}) ({whyml_ident(param)}: emit_ir) : emit_ir",
            "    requires { true }",
            "    ensures  { true }",
        ]
        if _raises:
            L.append(f"    raises {{ {', '.join(_raises)} }}")
        L.append("  =")
        L.append(f"    match {view} {whyml_ident(param)} with")
        for ast_cls, handler in entries:
            emitted = None
            for raw, ident in by_name.items():
                if raw == handler or raw.endswith("_" + handler) or raw.endswith(handler):
                    emitted = ident
                    break
            if emitted is None:      # unreachable: _pyx_dispatch_tables already checked
                return []
            L.append(f"    | {pfx}{ast_cls} _p -> {emitted} self _p")
        if default[0] == "raise":
            L.append(f"    | {pfx}Unknown -> raise {safe_exc_name(default[1])}")
        else:
            L.append(f"    | {pfx}Unknown -> IrOther \"{default[1]}\"")
        L.append("    end")
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

    def _emit_deferred_ssd(self, walker_names, whyml_ident) -> List[str]:
        """Record the just-emitted walker canon-name(s) into `_ssd_walkers_seen`,
        then append any SYMTAB-SET-DISPATCH driver group whose ALL walker deps are
        now emitted (forward-reference resolution — each driver lands after the
        LAST of its walkers). Each driver emitted once."""
        from module6_whyml.generic_fold import (
            _canon_call, emit_symtab_set_dispatch_group)
        if not getattr(self, "_ssd_funcs", None):
            return []
        if isinstance(walker_names, str):
            walker_names = [walker_names]
        for wn in walker_names:
            if wn is not None:
                self._ssd_walkers_seen.add(_canon_call(wn))
        out: List[str] = []
        for f, desc in self._ssd_funcs:
            nm = f.get("name")
            if nm in self._ssd_emitted:
                continue
            if desc["walker_deps"] <= self._ssd_walkers_seen:
                out += emit_symtab_set_dispatch_group(desc, whyml_ident)
                self._ssd_emitted.add(nm)
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
        # UNION-NARROWING cluster (preamble/generic_fold): the 4-function C8/C11
        # walk emits as ONE self-contained `let rec` block at the first-reached
        # member's slot; the other three members emit nothing.
        if getattr(self, "_union_cluster", None) and func.get("name") in self._union_names:
            if self._union_emitted:
                return []
            from module6_whyml.generic_fold import emit_union_cluster_group
            self._union_emitted = True
            lines = emit_union_cluster_group(self._union_cluster, whyml_ident)
            # SYMTAB-SET-DISPATCH driver (`_check_union_narrowing`) whose walker
            # is the `_union_c8_walk` just emitted here is appended once its deps
            # are satisfied.
            lines = lines + self._emit_deferred_ssd("_union_c8_walk", whyml_ident)
            return lines
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
        # SCAN-2D TRIO FUSION (preamble/generic_fold): the mutually-recursive
        # `{_scan_2d_in_expr,_scan_2d_in_stmt,_collect_2d_params}` triad emits as
        # ONE self-contained `let rec` group at whichever member slot is reached
        # FIRST; the other two members emit nothing.
        if getattr(self, "_scan2d_trio", None) and func.get("name") in self._scan2d_trio_names:
            if self._scan2d_trio_emitted:
                return []
            from module6_whyml.generic_fold import emit_scan2d_trio_group
            self._scan2d_trio_emitted = True
            return emit_scan2d_trio_group(self._scan2d_trio, whyml_ident)
        # CHECK-FINAL CALLER: `_check_final` is a forward reference to the pyval
        # `_final_walk_body` — DEFERRED, emitted with the pair group above. Its
        # own slot emits nothing.
        if getattr(self, "_check_final_name", None) and func.get("name") == self._check_final_name:
            return []
        # SYMTAB-SET-DISPATCH drivers (`_check_typeddict_access`/`_check_namedtuple_
        # access`/`_check_union_narrowing`): FORWARD REFERENCES to their converted
        # walker(s) — DEFERRED, emitted after all walker deps (see the wall2 /
        # union-cluster branches below). Own slot emits nothing.
        if getattr(self, "_ssd_names", None) and func.get("name") in self._ssd_names:
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
        # `_func_returns_string_seq` (generic_fold.py boundary-A): the lifted `rec`
        # sibling is SUPPRESSED; the wrapper emits the certified mutual
        # pyval/pydict/list existence catamorphism with `svt` threaded as a real
        # non-variant pydict param. Keyed on `id`; corpus-inert. See module note.
        if id(func) in getattr(self, "_frss_walk_ids", set()):
            return []
        _frss_desc = getattr(self, "_frss_outer_ids", {}).get(id(func))
        if _frss_desc is not None:
            from module6_whyml.generic_fold import emit_func_returns_string_seq_group
            return emit_func_returns_string_seq_group(func, _frss_desc, whyml_ident)
        # `_returns_string_seq` (generic_fold.py): the SELF-STATE sibling of
        # `_func_returns_string_seq`. Same catamorphism, but `svt` is sourced from the
        # self field `_seq_value_types` via an opaque-but-real `val <n>__svt (self):pydict`
        # and the walk is seeded with the PARAM `body_stmts` directly. The lifted `rec` is
        # SUPPRESSED. Keyed on `id`; corpus-inert. See generic_fold.py module note.
        if id(func) in getattr(self, "_rss_walk_ids", set()):
            return []
        _rss_desc = getattr(self, "_rss_outer_ids", {}).get(id(func))
        if _rss_desc is not None:
            from module6_whyml.generic_fold import emit_returns_string_seq_group
            return emit_returns_string_seq_group(func, _rss_desc, whyml_ident)
        # `_class_inv_refs_axiom_func` (generic_fold.py): the nonlocal-scalar-`hit` twin of
        # `_func_returns_string_seq`. The lifted `_walk` sibling is SUPPRESSED; the wrapper
        # emits the mutual pyval/pydict/list existence catamorphism over the REAL type_decls
        # ->class_invariants spine, leaf = `type=="Call" && Map.get axset func` (opaque-but-
        # real `val <n>__axset (self):map string bool`). Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_cira_walk_ids", set()):
            return []
        _cira_desc = getattr(self, "_cira_outer_ids", {}).get(id(func))
        if _cira_desc is not None:
            from module6_whyml.generic_fold import emit_class_inv_refs_axiom_group
            return emit_class_inv_refs_axiom_group(func, _cira_desc, whyml_ident)
        # `_inductive_refs_global_or_axiom_func` (generic_fold.py): the globals-set EXTENSION
        # of the class-inv twin. The lifted `_walk` sibling is SUPPRESSED; the wrapper emits
        # the mutual pyval/pydict/list existence catamorphism threading both the opaque-real
        # `axset` and the REAL `gset` (built from ir["module_globals"]), 3-disjunct leaf.
        # Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_iroaf_walk_ids", set()):
            return []
        _iroaf_desc = getattr(self, "_iroaf_outer_ids", {}).get(id(func))
        if _iroaf_desc is not None:
            from module6_whyml.generic_fold import emit_inductive_refs_group
            return emit_inductive_refs_group(func, _iroaf_desc, whyml_ident)
        # `_build_method_*_ensures_map` cluster: the LIFTED nested-def siblings
        # (`result_only`/`classify`/`saw`/`refs_self_field_or_old`) are SUPPRESSED — the
        # group-emit for each recognized outer is self-contained. Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_bmem_walk_ids", set()):
            return []
        # `_collect_struct_pack_assign_targets` (generic_fold.py boundary-A SET-COLLECT):
        # the lifted `_scan` sibling is SUPPRESSED; the wrapper emits the ref-accumulator
        # `map string bool` fold that reads the REAL `struct.pack` func + `target` off the
        # pydict and set_adds the target (only `parse_format(fmt)!=None` is opaque). The
        # sole caller `_emit_body_code` is `\trusted` → coupling-free. Keyed on `id`;
        # corpus-inert. See generic_fold.py module note.
        if id(func) in getattr(self, "_spat_walk_ids", set()):
            return []
        _spat_desc = getattr(self, "_spat_outer_ids", {}).get(id(func))
        if _spat_desc is not None:
            from module6_whyml.generic_fold import emit_struct_pack_targets_group
            return emit_struct_pack_targets_group(func, _spat_desc, whyml_ident)
        # `_collect_struct_unpack_array_targets` (generic_fold.py boundary-A SET-COLLECT,
        # the TUPLE-UNPACK twin of the pack collector): the lifted `_scan` sibling is
        # SUPPRESSED; the wrapper emits the ref-accumulator `map string bool` fold that
        # walks the REAL `targets` spine and set_adds the REAL target name, BOTH branches
        # reflected (only the per-slot `array int` decision is opaque). Coupling-free
        # (self type-lookups modeled opaque). Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_suat_walk_ids", set()):
            return []
        _suat_desc = getattr(self, "_suat_outer_ids", {}).get(id(func))
        if _suat_desc is not None:
            from module6_whyml.generic_fold import emit_struct_unpack_targets_group
            return emit_struct_unpack_targets_group(func, _suat_desc, whyml_ident)
        # `_contract_referenced_names` (generic_fold.py boundary-A SET-COLLECT): the
        # lifted `_walk` sibling is SUPPRESSED; the wrapper emits the certified mutual
        # pyval/pydict/list set-UNION catamorphism (`map string bool`). Keyed on `id`;
        # corpus-inert. See generic_fold.py module note.
        if id(func) in getattr(self, "_crn_walk_ids", set()):
            return []
        _crn_desc = getattr(self, "_crn_outer_ids", {}).get(id(func))
        if _crn_desc is not None:
            from module6_whyml.generic_fold import emit_contract_referenced_names_group
            return emit_contract_referenced_names_group(func, _crn_desc, whyml_ident)
        # `_collect_field_decode_str_locals` (generic_fold.py Module5 lambda-lift
        # capture-threading SET-COLLECT): the lifted `rec` sibling keeps its own
        # `\trusted` marker (emitted as a bodyless `val`, unused) so it never reaches the
        # let-emitter — but suppress defensively if it ever does. The wrapper emits the
        # certified mutual pyval/pydict/list set-UNION catamorphism (`map string bool`)
        # whose leaf set_adds the REAL `node["target"]` under the concrete field-decode
        # gate (only `_match_field_decode_idiom` is opaque). Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_fdsl_walk_ids", set()):
            return []
        _fdsl_desc = getattr(self, "_fdsl_outer_ids", {}).get(id(func))
        if _fdsl_desc is not None:
            from module6_whyml.generic_fold import emit_field_decode_str_locals_group
            return emit_field_decode_str_locals_group(func, _fdsl_desc, whyml_ident)
        # `_collect_str_decode_locals` (generic_fold.py Module5 lambda-lift
        # capture-threading SET-COLLECT, the DECODE-CALL sibling of
        # `_collect_field_decode_str_locals`): the lifted `rec` sibling is SUPPRESSED;
        # the wrapper emits the certified mutual pyval/pydict/list set-UNION
        # catamorphism (`map string bool`) whose leaf set_adds the REAL `node["target"]`
        # under the `stmt=="Assign"` + str-target gate and the OPAQUE
        # `self._is_decode_call(node.get("value"))` predicate over the REAL value pyval.
        # The sole caller `_detect_seq_promotion` is `\trusted`. Keyed on `id`;
        # corpus-inert. See generic_fold.py module note.
        if id(func) in getattr(self, "_sdl_walk_ids", set()):
            return []
        _sdl_desc = getattr(self, "_sdl_outer_ids", {}).get(id(func))
        if _sdl_desc is not None:
            from module6_whyml.generic_fold import emit_str_decode_locals_group
            return emit_str_decode_locals_group(func, _sdl_desc, whyml_ident)
        # `_collect_critical_mutexes` (generic_fold.py Module5 lambda-lift capture-threading
        # SET-COLLECT over `self.ir`): the lifted `walk` sibling is SUPPRESSED; the wrapper
        # emits the certified mutual pyval/pydict/list set-UNION catamorphism (`map string
        # bool`) whose leaf set_adds the REAL `s["mutex"]` under the `stmt=="CriticalSection"`
        # + present-`mutex` gate, driven by the REAL `self.ir` opaque-pyval + `pget_list`
        # fold, wrapped by the opaque `sorted(set) : list string`. The sole caller
        # `_emit_shared_state` is `\trusted`. Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_ccm_walk_ids", set()):
            return []
        _ccm_desc = getattr(self, "_ccm_outer_ids", {}).get(id(func))
        if _ccm_desc is not None:
            from module6_whyml.generic_fold import emit_critical_mutexes_group
            return emit_critical_mutexes_group(func, _ccm_desc, whyml_ident)
        # `_collect_shared_symbol_decls` (generic_fold.py, lambda-lifted `_symbol`
        # string-tokenizer + `self._AXIOM_FUNCTIONS.values()` catamorphism): the lifted
        # `_symbol` sibling is SUPPRESSED; the wrapper emits a FAITHFUL `_symbol` parser
        # (REAL split + guarded `pystr_eq` on the extracted parse literals) driving TWO
        # set-UNION folds — a `shared_lines` array fold building `shared_syms` and a
        # `.values()`->per-list fold `set_add`ing the REAL decl string under the REAL
        # `_symbol(d) in shared_syms` `Map.get` membership. Only `__axfns` (unmodeled
        # self-const) + `__split0`/`__strip` (whitespace ops) are opaque. Keyed on `id`;
        # corpus-inert (name-gated; sole caller `_transpile_modular` is `\trusted`).
        if id(func) in getattr(self, "_cssd_walk_ids", set()):
            return []
        _cssd_desc = getattr(self, "_cssd_outer_ids", {}).get(id(func))
        if _cssd_desc is not None:
            from module6_whyml.generic_fold import emit_shared_symbol_decls_group
            return emit_shared_symbol_decls_group(func, _cssd_desc, whyml_ident)
        # `_collect_string_elem_read_locals` (generic_fold.py TWO-SEQUENTIAL-CATAMORPHISM
        # SET-COLLECT): the lifted `rec` sibling is SUPPRESSED; the wrapper emits TWO
        # sequential total `map string bool` set-UNION catamorphisms (fold-1 `str_arrays`
        # gated by the opaque `in_ssf` func-name membership; fold-2 `elem_reads` threading
        # fold-1's result and reading `Map.get sa <base-name>`), composed `= f2 body
        # (f1 body)`. Keyed on `id`; corpus-inert. See generic_fold.py module note.
        if id(func) in getattr(self, "_serl_walk_ids", set()):
            return []
        _serl_desc = getattr(self, "_serl_outer_ids", {}).get(id(func))
        if _serl_desc is not None:
            from module6_whyml.generic_fold import emit_string_elem_read_locals_group
            return emit_string_elem_read_locals_group(func, _serl_desc, whyml_ident)
        # `_callee_raised_direct` (generic_fold.py raises-registry SET-COLLECT): the lifted
        # `walk` sibling is SUPPRESSED; the wrapper emits the certified mutual pyval/pydict/
        # list set-UNION catamorphism (`map string bool`) whose Call leaf looks the real
        # `func` up in the opaque-but-real `_module_func_raises` registry val and unions each
        # clause's real `exc_type` string. Keyed on `id`; corpus-inert. Sole caller
        # `_callee_raised_in` is `\trusted`. See generic_fold.py module note.
        if id(func) in getattr(self, "_crd_walk_ids", set()):
            return []
        _crd_desc = getattr(self, "_crd_outer_ids", {}).get(id(func))
        if _crd_desc is not None:
            from module6_whyml.generic_fold import emit_callee_raised_direct_group
            return emit_callee_raised_direct_group(func, _crd_desc, whyml_ident)
        # `_contract_referenced_var_names` (generic_fold.py boundary-A SET-COLLECT): the
        # bare-variable-NAME sibling of `_contract_referenced_names` — the lifted `_walk`
        # sibling is SUPPRESSED; the wrapper emits the certified mutual pyval/pydict/list
        # set-UNION catamorphism (`map string bool`) with a two-arm (Var/Attribute) leaf
        # and a third folded contract list (`assigns`). Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_crvn_walk_ids", set()):
            return []
        _crvn_desc = getattr(self, "_crvn_outer_ids", {}).get(id(func))
        if _crvn_desc is not None:
            from module6_whyml.generic_fold import \
                emit_contract_referenced_var_names_group
            return emit_contract_referenced_var_names_group(
                func, _crvn_desc, whyml_ident)
        # `_collect_map_typed_locals` (generic_fold.py boundary-A SET-COLLECT): the lifted
        # `walk` sibling is SUPPRESSED; the wrapper emits the ref-accumulator `map string
        # bool` fold that reads the REAL `target` off the pydict and set_adds it under the
        # opaque `_rhs_yields_map(value)` gate. Its sole caller `_should_auto_trust_set_op`
        # uses the ABSTRACT self-call val (coupling-free). Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_cmtl_walk_ids", set()):
            return []
        _cmtl_desc = getattr(self, "_cmtl_outer_ids", {}).get(id(func))
        if _cmtl_desc is not None:
            from module6_whyml.generic_fold import emit_collect_map_typed_locals_group
            return emit_collect_map_typed_locals_group(func, _cmtl_desc, whyml_ident)
        # `_has_set_op_on_map` (generic_fold.py): the recursive bool-existence predicate
        # over pyval. The lifted `yields_map` sibling is SUPPRESSED; the wrapper emits the
        # certified mutual bool-fold (real `map_locals` membership on the real operand;
        # `_rhs_yields_map` + the forward-ref `_test_contains_map` opaque). Its sole caller
        # `_should_auto_trust_set_op` uses the ABSTRACT self-call val (coupling-free).
        # Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_hsom_walk_ids", set()):
            return []
        _hsom_desc = getattr(self, "_hsom_outer_ids", {}).get(id(func))
        if _hsom_desc is not None:
            from module6_whyml.generic_fold import emit_has_set_op_on_map_group
            return emit_has_set_op_on_map_group(func, _hsom_desc, whyml_ident)
        # `_is_linear_expr` (auto_trust.py): the nested `def _check(e)` linear-arith
        # classifier. The lifted `_check` sibling is SUPPRESSED; the wrapper emits ONE
        # recursive bool catamorphism over pyval (discriminants reflected from the real
        # body; the `*` branch reads the real `type` off the real left/right child). Its
        # caller `_is_linear_vc` uses an ABSTRACT self-call val (coupling-free). Keyed on
        # `id`; corpus-inert.
        if id(func) in getattr(self, "_ile_walk_ids", set()):
            return []
        _ile_desc = getattr(self, "_ile_outer_ids", {}).get(id(func))
        if _ile_desc is not None:
            from module6_whyml.generic_fold import emit_is_linear_expr_group
            return emit_is_linear_expr_group(func, _ile_desc, whyml_ident)
        # `_body_references_bvar_0` (generic_fold.py boundary-A DE-BRUIJN DEPTH-THREADING):
        # a single self-recursive kind-dispatch walk over the real dict tree with an INT
        # `depth` threaded OUT of the `pv_size ast` structural variant (incremented only on
        # binder-body descents). Emitted as a `let rec` over the certified pyval/pydict ADT;
        # every child read via the certified size-bounded dynamic-key reader, the `idx` leaf
        # comparing the real int field to `depth`. Name-gated + fail-closed; corpus-inert.
        from module6_whyml.generic_fold import (
            recognize_refs_bvar, emit_refs_bvar_group)
        _rb_desc = recognize_refs_bvar(func)
        if _rb_desc is not None:
            return emit_refs_bvar_group(func, _rb_desc, whyml_ident)
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
        # functiondef-node wall: `_should_skip_method` -> faithful dunder (str_startswith/
        # endswith_op over func_name_ast) + @property (decorator_has_name) lowering.
        # Corpus-inert.
        if self._is_should_skip_method(func):
            return self._emit_should_skip_method_bespoke(func)
        # functiondef-node cluster: `_build_overload_param_guard` -> the faithful per-arg
        # isinstance-guard fold (build_overload_guard_acc over func_args_ast node).
        # Corpus-inert.
        if self._is_build_overload_param_guard(func):
            return self._emit_build_overload_param_guard_bespoke(func)
        # functiondef-node cluster: `_synthesize_overload_guard` -> the guarded-postcondition
        # synthesizer over `func_csl_ensures_ast node`, returning the canonical `array emit_ir`.
        # Corpus-inert.
        if self._is_synthesize_overload_guard(func):
            return self._emit_synthesize_overload_guard_bespoke(func)
        # functiondef-node cluster: `_is_overload_stub` -> the faithful @overload-decorator
        # scan (decorator_has_name_or_attr) + body[0] Pass/Expr-Ellipsis discrimination
        # (is_pass_node/is_expr_ellipsis_node over psl_nth 0 (func_body_ast node)). Corpus-inert.
        if self._is_is_overload_stub(func):
            return self._emit_is_overload_stub_bespoke(func)
        # csl_clause (Module3 mirror): `_act_guard` -> the certified `act_guard_fold None
        # (act_clauses_of act)` — the `given`-clause filter+`.expr`-project+`IrBinOp "and"`
        # fold over the real csl_clause list (IrBoolC 1 if none). Corpus-inert.
        if self._is_act_guard(func):
            return self._emit_act_guard_bespoke(func)
        # _is_final_annotation bool-recognizer -> is_final_ann_prog. Corpus-inert.
        if self._is_final_annotation(func):
            return self._emit_is_final_annotation_bespoke(func)
        # module-const-str-pairs first-match lookup (self-tcb-reduction): a
        # `for src, dst in NAME: if x == src: return dst; return x` scan over a
        # collected str-pair const -> the faithful chained-if string lowering.
        # Corpus-inert (recognizer-gated on the exact shape over a str-pair const).
        _spl = self._recognize_str_pair_lookup(func)
        if _spl is not None:
            return self._emit_str_pair_lookup_bespoke(func, _spl[0], _spl[1])
        # module-const-str-sets `sorted(NAME)` (self-tcb-reduction): a whole-body
        # `return sorted(NAME)` over a collected string set/frozenset const -> the
        # faithful constant `array string` literal (elements sorted at emit time).
        # Corpus-inert (recognizer-gated on the exact shape over a str-set const).
        _scs = self._recognize_sorted_const_set(func)
        if _scs is not None:
            return self._emit_sorted_const_set_bespoke(func, _scs)
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
        # L2 DISPATCH-EXPANSION (self-tcb-reduction, `_py_expr_to_ir`): the TYPE-KEYED
        # HANDLER dispatcher -> a total `match pyx_view expr with | PEx_<Cls> _p ->
        # <handler> self _p | ... end` over the input-side `pyast_expr` ADT. Recognizer-
        # gated on the exact three-statement body shape AND on a table `_pyx_dispatch_tables`
        # has certified as a handler table of this class -> corpus-inert.
        _pyxd = self._recognize_pyx_dispatcher(func)
        if _pyxd is not None:
            _lines = self._emit_pyx_dispatcher_bespoke(func, _pyxd[0], _pyxd[1], _pyxd[2])
            if _lines:
                return _lines
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
            recognize_self_method_calls, emit_self_method_calls_group,
            recognize_boolfold_isinstance, emit_boolfold_isinstance_group,
            recognize_flat_tag_func_pred, emit_flat_tag_func_pred_group,
            recognize_stmt_setfold, emit_stmt_setfold_group,
            recognize_substmap, emit_substmap_group,
            recognize_substitute, emit_substitute_group,
            recognize_subst_params, emit_subst_params_group,
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
            recognize_walk_dicts_set_consumer, emit_walk_dicts_set_consumer_group,
            emit_pb_trio_group,
            recognize_type_existence, emit_type_existence_group,
            recognize_named_field_existence, emit_named_field_existence_group,
            recognize_pyval_string_walker, emit_pyval_string_walker_group,
            recognize_pyval_list_walker, emit_pyval_list_walker_group,
            recognize_pyval_list_search, emit_pyval_list_search_group,
            recognize_pyval_flatten, emit_pyval_flatten_group,
            recognize_ir_free_vars, emit_ir_free_vars_group,
            recognize_cs_clause, emit_cs_clause_group,
            recognize_check_class_invariants, emit_check_class_invariants_group,
            recognize_check_gt3_schema_only, emit_check_gt3_schema_only_group,
            recognize_check_bounds, emit_check_bounds_group,
            recognize_extract_ast_subscript, emit_extract_ast_subscript_group,
            recognize_collect_instantiations_ast, emit_collect_instantiations_ast_group,
            recognize_collect_field_sites, emit_collect_field_sites_group,
            recognize_any_function_trusted, emit_any_function_trusted_group,
            recognize_contains_exec, emit_contains_exec_group,
            recognize_is_trivial_new, emit_is_trivial_new_group,
            recognize_collect_imports, emit_collect_imports_group,
            recognize_scan_node_for_subscript_calls, emit_scan_node_for_subscript_calls_group,
            recognize_find_subscript_calls, emit_find_subscript_calls_group,
            recognize_collect_protect_sites, emit_collect_protect_sites_group,
            recognize_collect_protect_index_sites, emit_collect_protect_index_sites_group,
            recognize_check_mutex_invariants, emit_check_mutex_invariants_group,
            recognize_check_callable_params, emit_check_callable_params_group,
            recognize_check_fresh_globals, emit_check_fresh_globals_group,
            recognize_module_binding_names, emit_module_binding_names_group,
            recognize_mutex_inv_params, emit_mutex_inv_params_group,
            recognize_check_noreturn, emit_check_noreturn_group,
            recognize_first_tuple_return, emit_first_tuple_return_group,
            recognize_find_assigned_vars, emit_find_assigned_vars_group,
            recognize_first_assign_value_ir, emit_first_assign_value_ir_group,
            recognize_frame_trigger_term, emit_frame_trigger_term_group,
            recognize_collect_mutations, emit_collect_mutations_group,
            recognize_find_iteration_mutations, emit_find_iteration_mutations_group,
            recognize_build_method_writes_map, emit_build_method_writes_map_group,
            recognize_build_method_return_type_map,
            emit_build_method_return_type_map_group,
            recognize_build_method_param_whyml_by_name,
            emit_build_method_param_whyml_by_name_group,
            recognize_build_method_param_types_map,
            emit_build_method_param_types_map_group,
            emit_extract_array_lengths_group,
            recognize_collect_record_fields, emit_collect_record_fields_group,
            recognize_verify_module_groups, emit_verify_module_groups_group,
            recognize_build_method_result_ensures_map,
            emit_build_method_result_ensures_map_group,
            recognize_build_method_field_result_ensures_map,
            emit_build_method_field_result_ensures_map_group,
            recognize_build_method_field_old_ensures_map,
            emit_build_method_field_old_ensures_map_group,
            emit_build_method_param_result_ensures_map_group,
            emit_build_method_field_param_result_ensures_map_group,
            emit_build_method_field_param_post_ensures_map_group,
            emit_build_method_result_frame_ensures_map_group,
            emit_build_method_field_param_frame_ensures_map_group,
            recognize_test_contains_map, emit_test_contains_map_group,
            recognize_is_linear_vc, emit_is_linear_vc_group,
            recognize_handler_catches, emit_handler_catches_group,
            recognize_subclasses_of, emit_subclasses_of_group,
            recognize_collect_escaping_exceptions,
            emit_collect_escaping_exceptions_group,
            recognize_callee_implicit_exceptions,
            emit_callee_implicit_exceptions_group,
            recognize_find_array_and_dict_vars,
            emit_find_array_and_dict_vars_group,
            recognize_compute_scope_sets, emit_compute_scope_sets_group,
            recognize_classify, emit_classify_group,
            recognize_global_call_target, emit_global_call_target_group,
            recognize_callable_whyml_arrow, emit_callable_whyml_arrow_group,
            recognize_method_edges, emit_method_edges_group,
            recognize_type_str_reader, emit_type_str_reader_group,
            recognize_has_dynamic_exec, emit_has_dynamic_exec_group,
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
        # driver-backlog "string-field twin": the STRING-FIELD analog of the
        # crosscheck term `all_agree` (`CrossCheckResult.all_agree` over `str`
        # record fields with a truthiness filter + string `==`). Disjoint from
        # the term carrier (no opaque_term fields here). Gated on
        # `_has_crosscheck_str_record` (a record whose EVERY field is `str`) ->
        # fires on 0 corpus programs + only `CrossCheckResult` among the
        # mirrors. Fail-closed: a `\trusted` stub body never matches -> `val`.
        if getattr(self, "_has_crosscheck_str_record", False):
            from module6_whyml.generic_fold import (
                recognize_crosscheck_str_agree,
                emit_crosscheck_str_agree_group)
            _csa = recognize_crosscheck_str_agree(func)
            if _csa is not None:
                return emit_crosscheck_str_agree_group(
                    func, _csa, whyml_ident)
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
        # seven-levers.md Lever 2 (option (b)): the 1-param `_csl_to_str` CSL-node
        # -> string catamorphism over the certified `emit_ir` variant ADT (Var->
        # IrVar / Number->IrNum / BinOp->IrBinOp). Fail-closed & exact-structural
        # (needs an `ExprIR`-annotated single param + the precise CSL-subclass
        # reads); a `\trusted` stub body (`return ""`) never matches -> emits
        # `val`. REUSES emit_ir (no new value shape / no new cert). No corpus
        # program shares the shape -> byte-inert.
        from module6_whyml.generic_fold import (
            recognize_csl_str_cata, emit_csl_str_cata_group)
        _cslc = recognize_csl_str_cata(func)
        if _cslc is not None:
            # The catamorphism BUILDS a string with the same abstract ops the
            # normal f-string / str() lowering registers; register them here since
            # the recognizer bypasses that path (str_of_int only if a Number arm).
            self._add_abstract_op(
                "val str_concat_op (a: string) (b: string) : string\n"
                "    ensures { result = (concat a b) }\n"
                "    ensures { String.length result"
                " = String.length a + String.length b }")
            if "IrNum" in _cslc["arms"]:
                self._add_abstract_op("val str_of_int (x: int) : string")
            return emit_csl_str_cata_group(func, _cslc, whyml_ident)
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
        # seven-levers §1 (Lever 1 — pydict WRITE half): the recursive in-place
        # Call-node rewriter (`_rewrite_ir_calls`) — a deep-dict-mutation walk
        # framed by the by-reference model (`#@ assigns obj`). Descends every
        # dict value / list element over the certified pyval bridge and `pput`s
        # `func` -> new_name at a matching Call node. Corpus-inert; fail-closed.
        from module6_whyml.generic_fold import (
            recognize_rewrite_ir_calls, emit_rewrite_ir_calls_group)
        _ric = recognize_rewrite_ir_calls(func)
        if _ric is not None:
            return emit_rewrite_ir_calls_group(_ric, whyml_ident)
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
        # scc.md §2.7: the self-method-call fold (`find_self_method_calls`) — a
        # returned-set catamorphism whose per-node pre-action adds a CONSTRUCTED
        # string (`self_type.lower()+"__"+f[len("self."):]`). Faithful,
        # mutation-sensitive reflect-the-literal lowering; same fail-closed
        # discipline (a template bug is a loud unprovable instance).
        _smc = recognize_self_method_calls(func)
        if _smc is not None:
            return emit_self_method_calls_group(func, _smc, whyml_ident,
                                                self._lower_fold_ensures(func))
        # bool analog of recognize_setfold: the isinstance-dispatch `.values()`/
        # list bool-existence catamorphism (`uses_inline_set_or_dict_ops`) —
        # OR-fold over the same certified pv_size/size_dict/size_list variant;
        # per-node predicate reflects tag/tuple/suffix literals; `.endswith` ->
        # opaque per-fn `val __suffix` (no axiom). Fail-closed; corpus-inert.
        _bfi = recognize_boolfold_isinstance(func)
        if _bfi is not None:
            return emit_boolfold_isinstance_group(func, _bfi, whyml_ident)
        # flat tag+func string predicate (`_is_decode_call`): non-recursive
        # single-node PDict read + tag guard + func string-predicate; `.endswith`
        # -> opaque per-fn `val __suffix` (no axiom). Fail-closed; corpus-inert.
        _ftf = recognize_flat_tag_func_pred(func)
        if _ftf is not None:
            return emit_flat_tag_func_pred_group(func, _ftf, whyml_ident)
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
        # ir-inline `_substitute`: the value-RETURNING pyval-tree deep-rewrite
        # walk (formal-Var / method-local / self-receiver substitution). Real
        # list-map + dict pput-rebuild + get-tag/Var lookup structure; the
        # self-receiver string-ops are opaque `val`s (ensures True). Fail-closed;
        # a template bug is a loud unprovable instance, never a false proof.
        _sub = recognize_substitute(func)
        if _sub is not None:
            return emit_substitute_group(func, _sub, whyml_ident)
        # ir-inline `_subst_params`: the value-RETURNING pyval-tree deep-rewrite
        # walk with a SINGLE substitution map + membership-guarded Var lookup (a
        # simplified sibling of `_substitute`; no self-receiver post-processing).
        # Real list-map + dict DCons-rebuild + get-tag/Var lookup structure.
        # Fail-closed; a template bug is a loud unprovable instance, never a
        # false proof.
        _subp = recognize_subst_params(func)
        if _subp is not None:
            return emit_subst_params_group(func, _subp, whyml_ident)
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
        # `_check_class_invariants`: the `_ir_free_vars` set-consumer wrapped in
        # type_decls/class_invariants list folds; reuses the cs_clause __anystr
        # membership-raise device + set_add field_set fold. Standalone, name-matched.
        _cci = recognize_check_class_invariants(func)
        if _cci is not None:
            return emit_check_class_invariants_group(_cci, whyml_ident)
        # `_check_gt3_schema_only`: nested generics.items()/type_params folds +
        # kind tag-check raise. Standalone, name-matched. Fail-closed; corpus-inert.
        _gt3 = recognize_check_gt3_schema_only(func)
        if _gt3 is not None:
            return emit_check_gt3_schema_only_group(_gt3, whyml_ident)
        _cb = recognize_check_bounds(func)
        if _cb is not None:
            return emit_check_bounds_group(_cb, whyml_ident)
        # `_extract_ast_subscript`: RAW-AST walk via the opaque-pyval VIEW —
        # `isinstance(n, _ast.<Cls>)` -> synthetic `_type` tag-test, `n.<attr>` ->
        # `pget_dyn`, `Set[str]` membership -> `Map.get`, `Optional[Tuple]` ->
        # `option (string,string)`, `_sanitize_type_name` cross-call destructured.
        # Name-gated + corpus-inert; fail-closed. Ledger 3 (reuses pyval).
        _eas = recognize_extract_ast_subscript(func)
        if _eas is not None:
            return emit_extract_ast_subscript_group(_eas, whyml_ident)
        # `_collect_instantiations_ast`: `_ast.walk` set-collect over the raw-ast
        # pyval VIEW — the recursive `.values()`/list catamorphism (pv_size measure)
        # runs the 3 kind-branches per descendant, threading a `map (string,string)
        # bool` set. The `_extract_ast_subscript` callee is a FORWARD reference
        # (defined later in the mirror) so it is INLINED, reflecting the certified
        # sibling's descriptor — converts ONLY when that sibling is the recognised
        # certified `_extract_ast_subscript`. Name-gated + corpus-inert; fail-closed.
        _cia = recognize_collect_instantiations_ast(func)
        if _cia is not None:
            _ext_sib = next((recognize_extract_ast_subscript(g)
                             for g in self.ir.get("functions", [])
                             if g.get("name") == "_extract_ast_subscript"
                             and recognize_extract_ast_subscript(g) is not None), None)
            if _ext_sib is not None:
                return emit_collect_instantiations_ast_group(_cia, _ext_sib, whyml_ident)
        # Weaver `_collect_field_sites`: raw-`ast.iter_child_nodes` recursive out-param
        # list-collector over the pyval VIEW (banked `__walk`/`__walkd`/`__walkl`
        # catamorphism threading `option string` enclosing-func + `list TUP` accumulator;
        # `_field_write_site` = opaque per-group `val …__fws`). Name-gated + corpus-inert.
        _cfsx = recognize_collect_field_sites(func)
        if _cfsx is not None:
            return emit_collect_field_sites_group(_cfsx, whyml_ident)
        # import_classifier `any_function_trusted`: raw-`ast.walk` bool existence walk
        # over the pyval VIEW (root-inclusive `__walk`/`__walkd`/`__walkl` catamorphism;
        # `_type == "<Cls>"` kind-check via pystr_eq + `getattr(node,"<key>",False)` bool
        # field read via pget_dyn, OR-folded). Name-gated + corpus-inert.
        _aft = recognize_any_function_trusted(func)
        if _aft is not None:
            return emit_any_function_trusted_group(_aft, whyml_ident)
        # exec_splice `_contains_exec`: raw-`ast.walk` bool existence walk over the
        # pyval VIEW (root-inclusive `__walk`/`__walkd`/`__walkl` catamorphism; NESTED
        # kind-check `_type == "Call"` + child `func`'s `_type == "Name"` + that child's
        # `id == "exec"`, all pystr_eq/pget_dyn, OR-folded). Name-gated + corpus-inert.
        _cex = recognize_contains_exec(func)
        if _cex is not None:
            return emit_contains_exec_group(_cex, whyml_ident)
        # Weaver `_is_trivial_new`: raw-ast STRAIGHT-LINE structural predicate over the
        # pyval VIEW (docstring `__filt` + concrete `Cons b0 Nil` singleton match + nested
        # `_type`/attr reads: Return head -> Call `value` -> Attribute `func` attr "__new__"
        # -> recv super()-Call or object-Name, all pystr_eq/pget_dyn). Name-gated + corpus-inert.
        _itn = recognize_is_trivial_new(func)
        if _itn is not None:
            return emit_is_trivial_new_group(_itn, whyml_ident)
        # import_classifier `collect_imports`: raw-`ast.walk` list-of-`(str,int)`
        # collector over the pyval VIEW (root-inclusive `__walk`/`__walkd`/`__walkl`
        # catamorphism threading a `list (string,int)` accumulator; Import->fold `names`
        # building `(alias.name, node.lineno)`, ImportFrom->`if node.module:` truthiness
        # building `(node.module, node.lineno)`; real pget_dyn reads + pystr_eq kind /
        # non-empty checks + PInt lineno). Name-gated + corpus-inert.
        _cimp = recognize_collect_imports(func)
        if _cimp is not None:
            return emit_collect_imports_group(_cimp, whyml_ident)
        # monomorphize `_scan_node_for_subscript_calls`: IR-dict recursive subscript-call
        # collector over the pyval VIEW — real "type"/"stmt"/"value"/"slice"/"name"/"func"
        # reads (pget_dyn) + "Subscript"/"Var"/"Call" kind-checks (pystr_eq) + `Set[str]`
        # membership (Map.get) threading a `list (string,string)` accumulator (banked
        # `__walk`/`__walkd`/`__walkl` catamorphism; the Call-func double-scan's variant
        # discharges from `pget_dyn`'s `pv_size v <= size_dict d` postcondition).
        # `_type_str` = opaque per-group `val …__type_str`. Name-gated + corpus-inert.
        _snsc = recognize_scan_node_for_subscript_calls(func)
        if _snsc is not None:
            return emit_scan_node_for_subscript_calls_group(_snsc, whyml_ident)
        # monomorphize `_find_subscript_calls`: folds `_scan_node_for_subscript_calls`
        # over `body`. The scan callee is a FORWARD reference (defined later in the
        # mirror) so it is INLINED, reflecting the certified sibling's descriptor —
        # converts ONLY when that sibling is the recognised, certified scan walker.
        _fsc = recognize_find_subscript_calls(func)
        if _fsc is not None:
            _scan_sib = next((recognize_scan_node_for_subscript_calls(g)
                              for g in self.ir.get("functions", [])
                              if g.get("name") == "_scan_node_for_subscript_calls"
                              and recognize_scan_node_for_subscript_calls(g) is not None), None)
            if _scan_sib is not None:
                return emit_find_subscript_calls_group(_fsc, _scan_sib, whyml_ident)
        # Weaver `_collect_protect_sites`: raw-`ast.iter_child_nodes` recursive out-param
        # list-collector with a per-node target-list fold + `_target_dotted_path` opaque
        # cross-call + `p in protected` membership. Name-gated + corpus-inert.
        _cpsx = recognize_collect_protect_sites(func)
        if _cpsx is not None:
            return emit_collect_protect_sites_group(_cpsx, whyml_ident)
        # Weaver `_collect_protect_index_sites`: like `_collect_protect_sites` but keeps
        # only Subscript point-writes to `path` (Index unwrap + non-Slice guard).
        _cpix = recognize_collect_protect_index_sites(func)
        if _cpix is not None:
            return emit_collect_protect_index_sites_group(_cpix, whyml_ident)
        _cmi = recognize_check_mutex_invariants(func)
        if _cmi is not None:
            return emit_check_mutex_invariants_group(_cmi, whyml_ident)
        _ccp = recognize_check_callable_params(func)
        if _ccp is not None:
            return emit_check_callable_params_group(_ccp, whyml_ident)
        _cfg = recognize_check_fresh_globals(func)
        if _cfg is not None:
            return emit_check_fresh_globals_group(_cfg, whyml_ident)
        # `_module_binding_names`: per-stub opaque-self pyval descent — the
        # `self`-only Set[str] accessor whose `self.ir` is read via an
        # uninterpreted `val …__ir : pyval` (no shared-field retype) then
        # descended with `pget_list`/`pget_dyn`/`set_add`/`set_union`. Real
        # `functions`/`classes`/`name` descent; name-gated + corpus-inert.
        _mbn = recognize_module_binding_names(func)
        if _mbn is not None:
            return emit_module_binding_names_group(_mbn, whyml_ident)
        # `_mutex_inv_params`: per-stub opaque-self pyval descent over
        # `self.ir["shared_vars"]` + a faithful string-containment guard — the
        # `(mutex, inv_str)` accessor read via an uninterpreted `val …__ir : pyval`
        # (no shared-field retype) then descended with `pget_list`/`pget_dyn`, keeping
        # names whose `"mutex"` field == the param AND whose mangled `!ident` occurs as
        # a substring of `inv_str` (`val …__contains`, pinned to the existential
        # substring witness). Name-gated + corpus-inert.
        _mip = recognize_mutex_inv_params(func)
        if _mip is not None:
            return emit_mutex_inv_params_group(_mip, whyml_ident)
        _cnr = recognize_check_noreturn(func)
        if _cnr is not None:
            return emit_check_noreturn_group(_cnr, whyml_ident)
        _ftr = recognize_first_tuple_return(func)
        if _ftr is not None:
            return emit_first_tuple_return_group(_ftr, whyml_ident)
        _fav = recognize_find_assigned_vars(func)
        if _fav is not None:
            return emit_find_assigned_vars_group(_fav, whyml_ident)
        # `_first_assign_value_ir`: value-returning first-match SEARCH over the
        # heterogeneous stmt tree (Any-tree-walker cluster). Emitted as the
        # certified mutual pyval search catamorphism (first non-empty); reuses the
        # pyval/pydict ADT + `pget_list`, NO axiom. Fail-closed; a template bug is a
        # loud unprovable instance, never a false proof.
        _favi = recognize_first_assign_value_ir(func)
        if _favi is not None:
            return emit_first_assign_value_ir_group(_favi, whyml_ident)
        # `_frame_trigger_term`: value-returning first-match `.values()` SEARCH over
        # the heterogeneous IR tree (Any-tree-walker cluster). Emitted as the
        # certified mutual pyval search catamorphism (BinOp==/Old-side read then a
        # pydict-VALUES descend, first non-None); reuses the pyval/pydict ADT +
        # size measures, NO axiom. Fail-closed; a template bug is a loud unprovable
        # instance, never a false proof.
        _fttm = recognize_frame_trigger_term(func)
        if _fttm is not None:
            return emit_frame_trigger_term_group(_fttm, whyml_ident)
        _cm = recognize_collect_mutations(func)
        if _cm is not None:
            _cm_members = (self.ir.get("class_str_set_constants", {})
                           .get(_cm["class_name"], {}).get(_cm["attr_name"]))
            if _cm_members:
                return emit_collect_mutations_group(_cm, _cm_members, whyml_ident)
        _fim = recognize_find_iteration_mutations(func)
        if _fim is not None:
            return emit_find_iteration_mutations_group(_fim, whyml_ident)
        _bmwm = recognize_build_method_writes_map(func)
        if _bmwm is not None:
            return emit_build_method_writes_map_group(func, _bmwm, whyml_ident)
        # `_build_method_return_type_map`: method-name -> WhyML-return-type `pydict` fold,
        # closed by the SELF-REFERENTIAL key-enum final block (`for _cls in {n.split("__",1)[0]
        # for n in result if "__" in n}: result.setdefault(...)`). `result` is a key-ITERABLE
        # `pydict` (not a keyless `map string ...`) so the self-ref key-enum is a real
        # structural fold + faithful split; corpus-inert (name-gated, mirror-only).
        _bmrt = recognize_build_method_return_type_map(func)
        if _bmrt is not None:
            return emit_build_method_return_type_map_group(func, _bmrt, whyml_ident)
        # `_build_method_param_whyml_types_by_name`: nested `map string (map string string)`
        # fold — outer over `functions`, inner over each func's `formal_params`, looking each
        # param's symtype up in the REAL `symbol_table` pydict (`__sget`) and mapping it through
        # the type-safety-only `__wtype` leaf. Keys read off real structure (mutation-sensitive).
        _bmpw = recognize_build_method_param_whyml_by_name(func)
        if _bmpw is not None:
            return emit_build_method_param_whyml_by_name_group(func, _bmpw, whyml_ident)
        # `_build_method_param_types_map`: `map string (list string)` fold — outer over
        # `functions`, inner over each func's REAL `symbol_table` pydict, appending a
        # type-safety-only `__ptype` leaf per entry. Value list folded off real structure.
        _bmpt = recognize_build_method_param_types_map(func)
        if _bmpt is not None:
            return emit_build_method_param_types_map_group(func, _bmpt, whyml_ident)
        # `_extract_array_lengths` (generic_fold.py pairs): the two lifted closures
        # `_field_of`/`_int_of` are SUPPRESSED; the outer emits the self-contained
        # `map string (option int)` fold with FAITHFUL field/int readers + a PINNED
        # `__setdefault` Map primitive. Keyed on `id`; corpus-inert.
        if id(func) in getattr(self, "_eal_walk_ids", set()):
            return []
        _eal_desc = getattr(self, "_eal_outer_ids", {}).get(id(func))
        if _eal_desc is not None:
            return emit_extract_array_lengths_group(func, _eal_desc, whyml_ident)
        _crf = recognize_collect_record_fields(func)
        if _crf is not None:
            return emit_collect_record_fields_group(_crf, whyml_ident)
        # `_verify_module_groups`: setdefault().append() -> `map string (list string)`
        # built by a pinned `__setappend` (pure `snoc` ensures) over the real
        # `functions` fold; keys read via `pget_dyn`. Corpus-inert.
        _vmg = recognize_verify_module_groups(func)
        if _vmg is not None:
            return emit_verify_module_groups_group(_vmg, whyml_ident)
        # `_build_method_{result,field_result,field_old}_ensures_map`: the pairs recognizer
        # (preamble) verified the LIFTED nested-def siblings' discriminant tags and stored the
        # emit `kind`; the standalone recognizers only name/param-gate (their discriminants are
        # hoisted out of the outer body).
        _bmem = getattr(self, "_bmem_outer_ids", {}).get(id(func))
        if _bmem is not None:
            _k = _bmem.get("kind")
            if _k == "result":
                return emit_build_method_result_ensures_map_group(_bmem, whyml_ident)
            if _k == "field_result":
                return emit_build_method_field_result_ensures_map_group(_bmem, whyml_ident)
            if _k == "field_old":
                return emit_build_method_field_old_ensures_map_group(_bmem, whyml_ident)
            if _k == "param_result":
                return emit_build_method_param_result_ensures_map_group(_bmem, whyml_ident)
            if _k == "field_param_result":
                return emit_build_method_field_param_result_ensures_map_group(_bmem, whyml_ident)
            if _k == "field_param_post":
                return emit_build_method_field_param_post_ensures_map_group(_bmem, whyml_ident)
            if _k == "result_frame":
                return emit_build_method_result_frame_ensures_map_group(_bmem, whyml_ident)
            if _k == "field_param_frame":
                return emit_build_method_field_param_frame_ensures_map_group(_bmem, whyml_ident)
        _tcm = recognize_test_contains_map(func)
        if _tcm is not None:
            return emit_test_contains_map_group(_tcm, whyml_ident)
        _ilv = recognize_is_linear_vc(func)
        if _ilv is not None:
            return emit_is_linear_vc_group(_ilv, whyml_ident)
        _hc = recognize_handler_catches(func)
        if _hc is not None:
            return emit_handler_catches_group(_hc, whyml_ident)
        _sco = recognize_subclasses_of(func)
        if _sco is not None:
            return emit_subclasses_of_group(_sco, whyml_ident)
        _cee = recognize_collect_escaping_exceptions(func)
        if _cee is not None:
            return emit_collect_escaping_exceptions_group(
                func, _cee, whyml_ident, self._lower_fold_ensures(func))
        # item 1b-A: `_callee_implicit_exceptions` per-callee Set[str] set-difference
        # (`declared - proved`). Return type emitted directly as `map string bool` ->
        # NO global `_compute_return_type` retype (every other `Set[str]` \trusted stub
        # keeps its `map int (option int)` val). Name+shape-gated -> byte-inert elsewhere.
        _cie = recognize_callee_implicit_exceptions(func)
        if _cie is not None:
            return emit_callee_implicit_exceptions_group(
                _cie, whyml_ident, self._lower_fold_ensures(func))
        _fadv = recognize_find_array_and_dict_vars(func)
        if _fadv is not None:
            return emit_find_array_and_dict_vars_group(
                func, _fadv, whyml_ident, self._lower_fold_ensures(func))
        _css = recognize_compute_scope_sets(func)
        if _css is not None:
            return emit_compute_scope_sets_group(_css, whyml_ident)
        _cls = recognize_classify(func)
        if _cls is not None:
            return emit_classify_group(_cls, whyml_ident)
        _gct = recognize_global_call_target(func)
        if _gct is not None:
            return emit_global_call_target_group(_gct, whyml_ident)
        # LEVER L19: `_callable_whyml_arrow` — constant-offset slice + `.partition` +
        # split-comp-map over the verified `_callable_tag_to_whyml` sibling + `" -> ".join`.
        # Register the faithful split/concat ops the fused map-join fold uses (the recognizer
        # bypasses the normal expression-lowering path that would register them). Ledger 3.
        _cwa = recognize_callable_whyml_arrow(func)
        if _cwa is not None:
            self._add_abstract_op(
                "val str_split_op (s: string) (sep: string) : array string\n"
                "    ensures { Array.length result >= 0 }")
            self._add_abstract_op(
                "val str_concat_op (a: string) (b: string) : string\n"
                "    ensures { result = (concat a b) }\n"
                "    ensures { String.length result = String.length a + String.length b }")
            return emit_callable_whyml_arrow_group(_cwa, whyml_ident)
        _me = recognize_method_edges(func)
        if _me is not None:
            return emit_method_edges_group(_me, whyml_ident)
        # self-tcb-reduction-driver: `functions.py` FunctionEmissionMixin._has_dynamic_exec —
        # a worklist DFS `∃ node in func.get("body") with type=="Call" && func=="exec"`,
        # lowered to the proven recursive existence fold over pyval. Fail-closed; ledger 3.
        _hde = recognize_has_dynamic_exec(func)
        if _hde is not None:
            return emit_has_dynamic_exec_group(_hde, whyml_ident)
        # self-tcb-reduction-driver: `monomorphize._type_str` — a flat pyval->
        # Optional[str] reader that DELEGATES to the verified `string->Optional[str]`
        # sibling `_sanitize_type_name`. Resolve BOTH functions' synthesized
        # Optional[str] union arm ctors (own from `func`, sibling by name from
        # `self._variant_types`); a cross-function Optional-union REWRAP re-injects
        # the sibling's arms into this function's union. Fail-closed: if either
        # union is not the 2-arm (string + None) Optional[str] shape, fall through
        # (stays `\trusted`). Non-facade (reflects the keys/tags/sibling); ledger 3.
        _tsr = recognize_type_str_reader(func)
        if _tsr is not None:
            _vts = getattr(self, "_variant_types", {})

            def _opt_str_arms(_uname):
                _vi = _vts.get(_uname)
                if not _vi:
                    return None
                _ct = _vi.get("constructors", {})
                if len(_ct) != 2:
                    return None
                _some = _none = None
                for _cn, _cd in _ct.items():
                    if _cd.get("arity") == 0:
                        _none = _cn
                    elif _cd.get("arity") == 1 and _cd.get("payload") in (
                            ["str"], ["string"]):
                        _some = _cn
                return (_some, _none) if (_some and _none) else None

            _own = _opt_str_arms(_tsr["union"])
            _sib = _tsr["sibling"]
            _sib_pref = f"_union_{_sib}_"
            _sib_union = None
            for _k in _vts:
                if _k.startswith(_sib_pref) and _k[len(_sib_pref):].isdigit():
                    _sib_union = _k
                    break
            _sibarms = _opt_str_arms(_sib_union) if _sib_union else None
            if _own is not None and _sibarms is not None:
                _tsr["some0"], _tsr["none0"] = _own
                _tsr["some1"], _tsr["none1"] = _sibarms
                return emit_type_str_reader_group(_tsr, whyml_ident)
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
            lines = emit_wall2_items_walk_group(func, _w2a, whyml_ident)
            # SYMTAB-SET-DISPATCH driver(s) whose walker is THIS just-emitted
            # wall2 walker are appended once all their walker deps are emitted.
            lines = lines + self._emit_deferred_ssd(func.get("name"), whyml_ident)
            return lines
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
        # R-W2d: the SET `.values()`-walk consumer `_assigned_locals` — a
        # `size_list` fold over `_walk_dicts subj` that `set_add`s a per-node
        # string key into a returned `map string bool` StrSet (certified
        # `set_add`/`const false` algebra, no axiom). Same generator-present
        # gate; fail-closed; corpus-inert.
        _wds = recognize_walk_dicts_set_consumer(func)
        if _wds is not None and _wds["walk_name"] in {
                f.get("name") for f in self.ir.get("functions", [])
                if isinstance(f, dict) and recognize_walk_dicts_generator(f)}:
            return emit_walk_dicts_set_consumer_group(func, _wds, whyml_ident)
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
        # self-tcb-reduction WRITER class (`_build_param_list`): record the name of the
        # function whose SIGNATURE is currently being built, so `_param_type_str` can type
        # the trusted `_param_type_str` stub's own `ref_params`/`array2d_params`/… params as
        # `seq string` (matching the `_build_param_list` call site) WITHOUT perturbing a
        # different method that reuses one of those param names (`_emit_union_arm_vc`'s
        # `symbol_table`). Only READ under the `_uses_build_param_list` gate -> byte-inert.
        self._current_sig_func_name = func.get("name")
        ref_params, args_str = self._build_param_list(func, local_refs, ghost_vars)

        # V1 pyconst-dispatch (self-tcb-reduction M5, B-bucket): set the plain-BOOL flag that
        # gates the `pyconst_val` MIDDLE-tuple-slot typing in `_infer_tuple_slot_type` (a verified
        # method that must NOT read the int-modelled `_current_emitting_func` as a string). Set
        # HERE — in the TRUSTED `_emit_function`, whose body is never lowered — so the flag is a
        # clean `False` default everywhere else. Must precede `_compute_return_type` (its refine
        # slots the return type). Byte-inert (True only for `_classify_literal_value`).
        _pv_fn = func.get("name", "") or ""
        self._pyconst_val_tuple_slot = (
            _pv_fn == "_classify_literal_value"
            or _pv_fn.endswith("___classify_literal_value"))

        return_type = self._compute_return_type(func, body_stmts)
        # self-tcb-reduction FunctionEmissionMixin WRITER class (`_build_param_list`): its
        # `Tuple[Set[str], str]` return is the `(seq string, string)` pair — the
        # `seq string` ref-params (the set modelled as a sequence, matching the body's
        # `Seq.empty`/set-comprehension result) and the joined `string`. `find_return_type`
        # defaults the slots to `(map int (option int), int)`, which clashes both slots.
        # Gated on the method name + the file sentinel -> byte-inert for the corpus and
        # every other mirror (this override fires for no other function).
        if (self._uses_build_param_list()
                and str(func.get("name", "")).endswith("_build_param_list")):
            return_type = "(seq string, string)"
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
        # Lever-7 (val-inherit): a lifted nested `def` whose enclosing function is
        # `#@ \trusted` (Module 5 stamps `trusted_parent: True`) is part of that
        # trusted, UNVERIFIED body — emit it as a bodyless `val` (contract only, no
        # goals), exactly as the trusted parent itself emits. Without this the
        # lifted helper acquires spurious verification obligations (e.g. an
        # unprovable `termination` VC from a nested `for`-loop) that the trusted
        # parent never has to discharge. SOUND: not verifying a fully-trusted
        # parent's helper verifies nothing LESS than intended. Fail-closed: the
        # flag is absent for every non-nested function and every nested def of a
        # NON-trusted parent → those stay byte-identical.
        func_trusted_parent = func.get("trusted_parent", False)
        emit_as_val = func_trusted or func_abstract or func_trusted_parent
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
        self._size_variant_param = None
        is_recursive = (IRScanner.is_recursive(func["name"], body_stmts)
                        or IRScanner.is_recursive(name, body_stmts))
        # SIBLING-CONCRETE SELF-RECURSION (relaunch #11): a `#@ sibling_concrete` method
        # whose own body calls `self.<m>(...)` has that call lowered CONCRETELY
        # (`expressions._handle_dotted_call`), so the emitted function really IS recursive.
        # `IRScanner.is_recursive` matches the IR name or the bare name, but the call
        # node's `func` is the DOTTED `"self.<m>"` — exactly the miss `scc.py`'s
        # `find_self_method_calls` documents for the ORDERING graph — so this read False,
        # the function emitted as a plain `let`, and its own concrete self-call was an
        # UNBOUND SYMBOL (measured on `_rhs_yields_map`: `unbound function or predicate
        # symbol 'statementemissionmixin___rhs_yields_map'`). Resolve the dotted form the
        # same way the SCC does. Gated on the opt-in `#@ sibling_concrete` marker, so it is
        # byte-inert for every method that does not carry it. `use_rec` and the
        # `variant { size <ir-param> }` injection below both follow from `is_recursive`,
        # which is exactly what a genuinely recursive emitted function needs.
        if (not is_recursive
                and whyml_ident(func["name"]) in getattr(
                    self, "_sibling_concrete_methods", set())):
            _bare = str(func.get("name", "")).split("__", 1)[-1]
            if _bare and IRScanner.is_recursive(f"self.{_bare}", body_stmts):
                is_recursive = True
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
            # WhyML chains a MUTUALLY RECURSIVE group with `with`, not with OCaml's
            # `and` (0942). This branch emitted `and <name>`, which Why3 rejects
            # outright — `let rec f ... and g ...` does not bind `g` at all
            # ("unbound function or predicate symbol 'g'"), and with a `variant`
            # present it fails earlier still ("unexpected 'variant' clause"). The
            # sibling LOGIC path two branches up already used the correct
            # `with function` continuation; only the PROGRAM path was wrong.
            # Measured before the change: NO emitted file reached this branch (0 of
            # 52 mirrors, 0 of 812 corpus programs contained an `and` continuation),
            # i.e. it was dead-but-wrong code, so the correction is byte-inert and
            # what it actually does is UNBLOCK mutual recursion for the first time.
            kw = f"with {name}"
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
            # KIND-LOCAL DISCRIMINANT FLOW (relaunch #11): record the parameter this
            # function's injected `variant { size <p> }` measures, so a kind-guard on a
            # LOCAL bound from `<p>.get("type", …)` may lower to the constructor
            # discriminant `(is_K <p>)` — the ONLY guard shape under which the guarded
            # size-decrease laws apply (see `statements._collect_kind_local_recv`). Scoped
            # to THIS receiver in THIS recursive function, so the mirror's already-proven
            # `kind_of` string path is untouched everywhere else.
            self._size_variant_param = _ir_p
        self._emitting_val_contract = False

        # mutable-self-plan.md M.4: a method of a `@mutable_state` class emits its
        # `#@ assigns self.x` (from `_module_method_writes`) as a WhyML `writes { … }`
        # clause on the CONCRETE `let` — so Why3 CHECKS the frame against the body (a
        # wrong or `\nothing` assigns on a mutating body FAILS: the soundness fix).
        # `writes { }` is valid Why3 and rejects any unlisted write. Opt-in via the
        # class decorator → byte-identical for every unmarked class.
        # DRIVER FRAME-SOUNDNESS FIX (2026-08-26, getting-better/cursor-nest/
        # trusted-frame-oracle.mlw): the `not emit_as_val` exclusion above was
        # HALF the story. A `writes` clause has TWO jobs — it CHECKS the frame
        # against a body (why the original fix skipped bodyless vals) and it
        # DECLARES the frame to CALLERS. Dropping it from a `\trusted`/`\abstract`
        # stub's `val` makes Why3 infer NO effect, so every converted caller
        # silently assumes the field is UNCHANGED across the call — an assumption
        # STRONGER than the mirror's own `#@ assigns self.f`, i.e. unsound.
        # Measured: `val _contractparser___parse_atom_primary` had no `writes`
        # though the mirror declares `#@ assigns self.i`; the oracle shows a
        # caller's `ensures self.i >= \old(self.i)` is Valid as emitted and
        # Unknown once the declared frame is restored. Emitting the clause for a
        # val too costs no check (there is no body) and restores the honest
        # caller-side assumption. Same @mutable_state gate => corpus byte-inert.
        if (is_method
                and self._current_self_type in getattr(self, "_mutable_state_classes", set())):
            _wf = self._module_method_writes.get(func["name"], [])
            # Filter to labels the record ACTUALLY emits (see the companion note in
            # preamble.py). An `#@ assigns self.f` naming a field Module5 dropped from
            # the record would otherwise emit an unbound symbol. When the registry is
            # absent (no record emitted) nothing is filtered -> byte-identical.
            _lbls = getattr(self, "_emitted_record_field_labels", {}).get(
                self._current_self_type)
            _wl = [self._field_label(self._current_self_type, f) for f in _wf]
            if _lbls is not None:
                _wl = [l for l in _wl if l in _lbls]
            # On the CONCRETE `let` path an EMPTY `writes { }` is meaningful - it
            # CHECKS that the body writes nothing - so it is always emitted there.
            # On the bodyless `val` path it conveys nothing a missing clause does not
            # already say (a val with no `writes` writes nothing), so suppress it and
            # keep emission byte-identical wherever the frame is empty. Measured: this
            # makes the fix CORPUS BYTE-INERT - 0 corpus/tests programs declare a
            # trusted/abstract method with a non-nothing self-field assigns (the only
            # two @mutable_state corpus programs with a trusted method, 0900/0901,
            # declare `assigns \nothing` on it).
            if _wl or not emit_as_val:
                _wc = ", ".join(f"self.{l}" for l in _wl)
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
        _uvc: List[str] = []
        if any(v and v.startswith("_union_") for v in _symtab.values()):
            _uvc = self._emit_union_arm_vc(name, _symtab)
        # cursor-nest `parse_atom_application`: a `goal` CLOSES a `let rec … with …`
        # group, so emitting these per-arm VCs straight after a NON-LAST member SPLITS
        # the mutual-recursion group — every later member then falls out of scope for
        # every earlier one (measured: `unbound function or predicate symbol
        # '_parser__parse_arith_add'` from inside `parse_comparison`, though both sit in
        # the same 8-member `with` chain). Latent until now only because no previous SCC
        # of size > 1 had a union-typed member. DEFER them to after the whole group; the
        # goals themselves are unchanged and the last member's own goals still land where
        # they always did, so a single-member "group" is byte-identical.
        if _scc_size > 1 and _pos_in_scc != _scc_size - 1:
            if getattr(self, "_deferred_union_arm_goals", None) is None:
                self._deferred_union_arm_goals = []
            self._deferred_union_arm_goals.extend(_uvc)
        else:
            lines += _uvc
        if _pos_in_scc == _scc_size - 1:
            if getattr(self, "_deferred_union_arm_goals", None):
                lines += self._deferred_union_arm_goals
                self._deferred_union_arm_goals = []
            lines.append("")
        # RECORD-ELEMENT seq->array RETURN BRIDGE (the third bridge, beside `materialize`
        # for `seq int` and `materialize_str` for `seq string`): a `-> List[<record>]`
        # function whose only normal exit is the tail return of a seq-modelled accumulator
        # crosses the seq->array boundary with a RECORD payload, and both existing bridges
        # type-clash on it. Same fresh-result / no-region-link shape and the same two
        # POINTWISE postconditions as those two, so the array is EQUAL to the seq and
        # nothing is erased.
        # WHY HERE. (a) Not at the return site: that body's own MIRROR models
        # `_add_abstract_op`'s argument as a HASHED INT (it has only ever seen string
        # LITERALS there), so a COMPUTED declaration string cannot be passed from it —
        # measured, it fails the mirror's L3-tc. (b) Not from the return TYPE alone: a
        # `-> List[<record>]` function that builds its result some other way (corpus
        # driver 0839's list LITERAL) never calls the bridge, and declaring an unused val
        # for it breaks byte-diff-0 — measured. So the trigger is the EMITTED BODY
        # actually naming the bridge.
        _rt = getattr(self, "_func_return_type", "") or ""
        if (_rt.startswith("array ")
                and _rt not in ("array int", "array real", "array string")):
            _mrb = _rt[len("array "):]
            if _mrb.isidentifier() and any(f"(materialize_{_mrb} " in _l for _l in lines):
                self._add_abstract_op(
                    f"val materialize_{_mrb} (s: seq {_mrb}) : array {_mrb}\n"
                    f"    ensures {{ Array.length result = Seq.length s }}\n"
                    f"    ensures {{ forall i:int. 0 <= i < Seq.length s -> result[i] = Seq.get s i }}")
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
            elif (ann in ("set", "frozenset") and ret == "int"
                  and not func.get("trusted")
                  and whyml_ident(str(func.get("name", "")))
                  in getattr(self, "_sibling_concrete_methods", set())):
                # MAP-KEY MODEL SPLIT (relaunch #17): a CONVERTED `-> Set[str]` method is
                # emitted by the set-union catamorphism as the FAITHFUL StrSet `map string
                # bool`, but this map recorded the generic `map int (option int)` for it —
                # so every `self.<m>()` call site int-HASHED its key (`Map.get
                # (self__module_binding_names_0 ()) (str_hash_op !name)`) against an
                # UNCONSTRAINED int-keyed map that has nothing to do with the proven body.
                # The conversion bought its caller nothing and the guard was a hash facade.
                # This is backlog item 1b(A)'s `Set[str]` retype — the one whose ATTEMPT #1
                # was REJECTED because it was GLOBAL and cascaded into every verified caller
                # written against the old int type. Here it is PER-CALLEE, gated on the
                # opt-in `#@ sibling_concrete` marker, which is exactly the per-consumer
                # gate that attempt lacked: an unmarked `-> Set[T]` method keeps the
                # historical `map int (option int)` byte-identically, and `dict` is left
                # alone entirely. Fail-closed — if the callee's emitted `let` is NOT the
                # StrSet shape, the call site is an L3-tc type error, not a silent erasure.
                ret = "map string bool"
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
            elif ann == "bool" and ret == "unit" and func.get("trusted"):
                # GAP #2, PREDICATE TWIN (self-call site): the `-> str` disjunct's
                # boolean sibling, and the CALL-SITE half of the `_compute_return_type`
                # `bool` disjunct. BOTH halves are needed and that is the whole reason
                # an earlier attempt measured "the `-> bool` annotation has no effect":
                # patching `_compute_return_type` alone fixes the stub's OWN `val`
                # while the `self.<m>()` call site still abstracts through THIS map and
                # stays `unit`. `int` (not `bool`) for the reason given there — the
                # emitter models Python bools as int 0/1 end-to-end. Byte-identical for
                # the corpus (a real `-> bool` function has a return statement, so
                # `ret` is never "unit").
                ret = "int"
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
            # Optional-tuple return (self-tcb-reduction Tier-5 value model): the
            # self-call-site sibling of the `_compute_return_type` override
            # (functions.py `option (τ...)` branch). A method whose annotation is a
            # synthesized `_union_*` (an `Optional[Tuple[...]]` normalized by Module5)
            # that BOTH returns a tuple AND returns `None` abstracts its `self.<m>(...)`
            # call site as `option (τ...)`, so a caller's `if <call> is not None:`
            # None-check type-checks against the real converted `let`'s `option`
            # return (else the bare tuple `(τ...)` bridge cannot carry `None`). Gated
            # on an ACTUAL `return None` against a `_union_*` annotation -> byte-inert.
            if (isinstance(ann, str) and ann.startswith("_union_")
                    and ret.startswith("(") and "," in ret
                    and IRScanner.has_none_return(func["body"])):
                ret = f"option {ret}"
            result[func["name"]] = ret
        # self-tcb-reduction lever #1 sub-inc A (_infer_return_value_type): two
        # cross-mixin helpers it calls are NOT ported into this mirror module, so their
        # abstract self-call vals default to `: int` and int-erase the type-string reads.
        # Register their real WhyML return shapes (name-gated to these emitter-internal
        # helpers, never a corpus symbol; `setdefault` never shadows a file that ports the
        # helper for real) -> corpus byte-identical.
        for _cls in {n.split("__", 1)[0] for n in result if "__" in n}:
            # cap (d): `_resolve_dotted_signature(func)` really returns a
            # `(ret_type, param_types, ...)` tuple whose [0] is the callee's WhyML
            # return-type STRING — model it as `array string` so `[0]` yields a real
            # `string` compared by `str_eq_op "string"` (not the int-hash 1776665034).
            result.setdefault(f"{_cls}___resolve_dotted_signature", "array string")
            # cap (c): `_record_valued_expr_whyml_type(val_ir)` returns `Optional[str]` —
            # model as `option string` so `_rec = self._record_valued_expr_whyml_type(...)`
            # types as an option local (`ref None`), its `is not None` guard lowers to a
            # `match … None/Some` discriminant, and `return _rec` threads into the
            # Optional[str] `_union_*` return arm.
            result.setdefault(f"{_cls}___record_valued_expr_whyml_type", "option string")
            # sub-inc B (`_maybe_inject_union_return`): `_infer_return_value_type(val_ir)`
            # returns `Optional[str]` (lowered as a per-fn synth `_union_*` variant, which
            # IS isomorphic to `option string`). Its `self.<m>(...)` call site
            # (`val_type = self._infer_return_value_type(val_ir)`) must abstract as
            # `option string` — same model as the sibling `_record_valued_expr_whyml_type`
            # — so `val_type` types as an option local (`ref None`), `if val_type is None`
            # lowers to a `match … None/Some` discriminant, and `arm_type == val_type`
            # option-unwraps to a faithful `str_eq_op` (not the int-hash facade). The map
            # default computed from the body is `int` (the synth-variant `raise` shape),
            # so an explicit OVERRIDE (not `setdefault`) is needed. Name-gated to this
            # emitter-internal helper -> corpus byte-identical.
            result[f"{_cls}___infer_return_value_type"] = "option string"
            # self-tcb-reduction `_compute_return_type` PATH(b): `_returned_var_name(
            # body_stmts)` returns `Optional[str]` (the returned local's name, else None) —
            # model as `option string` so `_rv = self._returned_var_name(...)` types as an
            # option local (`ref None`), its `is not None` guard lowers to a `match …
            # None/Some` discriminant, and the narrowed `_rv` is a real string map key.
            # Gated on the `_compute_return_type` file -> corpus/other-mirror byte-inert.
            if self._uses_compute_return_type():
                result.setdefault(f"{_cls}___returned_var_name", "option string")
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
        elif nu == "hval":
            # self-tcb-reduction Tier-5 (union/match cluster): a `Dict[str, PyVal]`
            # param is the faithful heterogeneous `map string (option hval)` — the
            # certified value carrier, NOT the int-erased default. `hval` is a
            # corpus-absent sentinel (no reference program has a `Dict[str, PyVal]`
            # param) -> byte-inert.
            v = "hval"
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
            _fname = str(func.get("name", "") or "")
            for name, symtype in symtable.items():
                if name in local_assignees and name not in _formal:
                    continue
                # self-tcb-reduction WRITER class (`_build_param_list`): the self-call
                # abstract val for `self._param_type_str(...)` must declare its collection
                # params `seq string` (matching the call-site args); `_build_param_list`'s
                # own `local_refs`/`ghost_vars` are `seq string` too. Gated on the file
                # sentinel + the exact method+param names -> byte-inert elsewhere.
                if self._uses_build_param_list():
                    if (_fname.endswith("_param_type_str")
                            and name in ("ref_params", "array2d_params",
                                         "array1d_params", "symbol_table")):
                        param_types.append("seq string")
                        continue
                    if (_fname.endswith("_build_param_list")
                            and name in ("local_refs", "ghost_vars")):
                        param_types.append("seq string")
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
                # self-tcb-reduction (auto_trust coupling): `_has_set_op_on_map`'s
                # `map_locals` param is `Optional[Set[str]]` (a synthesized union →
                # int). Its sibling `_collect_map_typed_locals` (annotated `-> Set[T]`)
                # abstracts its RETURN as `map int (option int)` (the set-return rule),
                # and `_should_auto_trust_set_op` threads that return straight into this
                # param — so the abstract-call param must agree. Name-gated (mirror-only)
                # → corpus byte-identical.
                if (name == "map_locals"
                        and str(func.get("name", "")).endswith("_has_set_op_on_map")):
                    param_types.append("map int (option int)")
                    continue
                # cursor-nest `parse_atom`: a `_union_*` PARAM keeps its union type.
                # `_symtype_to_whyml` collapses it to `int`, so `_coerce_dotted_args`
                # believed `expect`'s `value: Optional[str]` slot was int-typed and filled
                # the omitted default with the int witness `0` — `This expression has type
                # int, but is expected to have type _union_expect_1` against the CONCRETE
                # sibling, whose emitted signature does use the union. The registry was
                # simply lying about the emitted shape; this makes the two agree.
                # @mutable_state-gated, like the record widening a few lines below.
                if (isinstance(symtype, str) and symtype.startswith("_union_")
                        and getattr(self, "_mutable_state_classes", None)):
                    param_types.append(symtype)
                    continue
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
        # self-tcb-reduction (F2 fidelity): `_handle_return_stmt` calls the cross-mixin
        # helper `self._thread_optional_return(val_ir, local_refs)`, but that helper is
        # NOT ported into the mirror module here, so it never enters `functions` and thus
        # gets no registry entry — the auto-emitted abstract self-call val would default
        # its `local_refs: Set[str]` argument to `int`, an L3 type error against the
        # caller's `map int (option int)` term. Register the helper's signature under each
        # present class's `<cls>___thread_optional_return` key (the shape
        # `_resolve_dotted_signature` looks up for `self._thread_optional_return(...)`) so
        # x1 types as `map int (option int)`. `setdefault` never shadows a real provider.
        # Name-gated to this emitter-internal helper (never a corpus symbol) → corpus
        # byte-identical.
        for _cls in {n.split("__", 1)[0] for n in result if "__" in n}:
            result.setdefault(f"{_cls}___thread_optional_return",
                              ["emit_ir", "map int (option int)"])
            # self-tcb-reduction lever #1 sub-inc A cap (d): `_infer_return_value_type`
            # calls `self._resolve_dotted_signature(func)` with `func` a WhyML `string`
            # (`func_of val_ir`), but the un-ported helper's abstract val defaults its param
            # to `int`. Register the param as `["string"]` so the call type-checks. Paired
            # with the `array string` RETURN registration in `_build_method_return_type_map`.
            # Name-gated to this emitter-internal helper -> corpus byte-identical.
            result.setdefault(f"{_cls}___resolve_dotted_signature", ["string"])
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

