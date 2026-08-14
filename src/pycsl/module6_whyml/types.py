from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, TypedDict


# Bool-typed BinOp operators — RHS of any of these is a Python bool and
# needs `(if X then 1 else 0)` wrapping before flowing into a WhyML int slot.
_BOOL_BINOPS = frozenset({
    "==", "!=", "<", "<=", ">", ">=", "is", "is not", "in", "not in",
})


class ValIRBoolView(TypedDict):
    """Closed-key view of the two IR-expression keys `_val_is_bool` reads
    (`type`, `op` — both `str`). Runtime-inert (a TypedDict IS a dict), it
    monomorphizes to a native WhyML record so the mirror's `val_ir.get("type")`
    lowers to the field read `val_ir.py_type` and the literal comparisons route
    through `str_eq_op` (09-2223 G1/G2), not an opaque int-hash op."""
    type: str
    op: str


class BoolWrapIRView(TypedDict):
    """Closed-key view of the three IR-expression keys `_bool_ir_to_int_wrap`
    reads (`type`, `op`, `func` — all `str`). Runtime-inert (a TypedDict IS a
    dict); `Optional[BoolWrapIRView]` monomorphizes to `option <record>` (the
    boundary-1 G1 option-of-record projection), so — after the `if val_ir is
    None` guard — `val_ir.get("type")` projects the field from the `Some` arm
    (`match val_ir with Some _r -> _r.py_type | None -> ""`) and the literal
    comparisons route through `str_eq_op`, not an opaque int-hash op."""
    type: str
    op: str
    func: str


class TypeInferenceMixin:
    """Type inference and collection-metadata tracking for the transpiler.

    Covers three concerns:

    * **First-assignment classification** (`_first_assign_kind`,
      `_emit_first_assign` callers): record vs lambda vs array vs dict vs
      bounded-int vs default, used to pick the `let X = ...` shape.
    * **RHS type queries** (`_rhs_yields_array`, `_rhs_yields_map`,
      `_field_type_for`, `_field_type_of`): does this IR expression
      produce an `array int` / `map int (option int)` / typed self-field?
      Drives the dict-vs-array vs int slot choices throughout statement
      emission.
    * **Collection constant-folding metadata** (`_track_collection_metadata`):
      records known sizes/elements of literal collections so `len(...)`
      and `sum(...)` can fold to constants during expression emission.

    Mixed into Module6_WhyMLTranspiler. State accessed via `self`:
    `_record_types`, `_known_collection_sizes`, `_known_collection_elements`,
    `_array_locals`, `_dict_locals`, `_current_symbol_table`,
    `_current_array1d_params`, `_current_self_type`,
    `_module_method_return_types`, `_bounded_int`, the various
    `_ghost_*_vars` sets.
    """

    def _track_collection_metadata(self, target: str, val_ir: Dict[str, Any]) -> None:
        """Update _known_collection_sizes/_elements for constant-folding of len/sum/index."""
        vt = val_ir.get("type", "")
        if vt in ("ArrayLit", "Tuple"):
            elts = val_ir.get("elts", [])
            self._known_collection_sizes[target] = len(elts)
            # WL-04c (wrong-lowering-to-fix.md §WL-04 record LITERAL residual): a LOCAL
            # bound from a `List[<record>]` LITERAL of full-arity, content-faithful
            # record CONSTRUCTORS (`a = [Point(1, 2), Point(3, 4)]`) is a record-array
            # local — register the element record's whyml name so `a[i].field` /
            # `a[i][k]` projects the faithful field natively (the local twin of
            # `_record_array_params`). A non-record / non-faithful literal is not
            # matched (byte-identical). No numeric fold is registered for a record
            # element (the elem_map below only folds Number elements).
            _rec_elem = self._record_ctor_list_elem(elts)
            if _rec_elem is not None:
                _info = self._record_types.get(_rec_elem, {})
                _wn = _info.get("whyml_name")
                if _wn is not None:
                    self._record_array_locals[target] = _wn
            # WL-04a: a PURE-float literal folds an indexed read to the FAITHFUL real
            # value (`a[1]` → `2.5`), matching the `array real` construction — never the
            # int-truncated `2` (which would be an `int` vs `real` type error against the
            # faithful element). Int / mixed literals keep the `str(int(...))` fold
            # (byte-identical); a str literal has no numeric fold (reads via `Array.get`).
            _all_float = bool(elts) and all(
                e.get("type") == "Number" and isinstance(e.get("value"), float)
                for e in elts)
            if _all_float:
                elem_map = {
                    i: (repr(e["value"]) if not float(e["value"]).is_integer()
                        else f'{int(e["value"])}.0')
                    for i, e in enumerate(elts)}
            else:
                elem_map = {i: str(int(e["value"])) for i, e in enumerate(elts)
                            if e.get("type") == "Number" and isinstance(e.get("value"), (int, float))}
            if elem_map:
                self._known_collection_elements[target] = elem_map
        elif vt == "String" and isinstance(val_ir.get("value"), str):
            self._known_collection_sizes[target] = len(val_ir["value"])
        elif vt == "DictLit":
            keys = val_ir.get("keys", [])
            self._known_collection_sizes[target] = len(keys)
            elem_map = {}
            for k, v in zip(keys, val_ir.get("values", [])):
                if (k.get("type") == "Number" and isinstance(k.get("value"), (int, float)) and
                        v.get("type") == "Number" and isinstance(v.get("value"), (int, float))):
                    elem_map[int(k["value"])] = str(int(v["value"]))
            if elem_map:
                self._known_collection_elements[target] = elem_map
        elif vt == "SetLit":
            elts = val_ir.get("elts", [])
            unique_vals = {int(e["value"]) if (e.get("type") == "Number" and
                           isinstance(e.get("value"), (int, float))) else id(e)
                           for e in elts}
            self._known_collection_sizes[target] = len(unique_vals)

    @staticmethod
    def _val_is_bool(val_ir: ValIRBoolView) -> bool:
        """RHS expression is bool-typed in Python — needs `if … then 1 else 0`
        when stored into a WhyML `int` slot."""
        vt = val_ir.get("type", "")
        if vt in ("Compare", "BoolOp"):
            return True
        if vt == "UnaryOp" and val_ir.get("op") == "not":
            return True
        if vt == "BinOp" and val_ir.get("op") in _BOOL_BINOPS:
            return True
        return False

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

    def _resolve_effective_ghost_type(self, target: str, op: str, ghost_type: str) -> str:
        """Infer ghost type for augmented-assign from tracked declaration sets.

        Augmented-assign IR nodes carry ghost_type='int' (the grammar default)
        because the transformer does not propagate declared_type.  Override from
        the sets that are populated when the declaration was first seen.
        """
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

    def _field_type_for(self, obj: str, field: str) -> Optional[str]:
        """Resolve `<obj>.<field>` (both as raw strings, the IR shape
        used by `_handle_fieldset_stmt`) to the field's declared type
        tag, or None if the obj/field doesn't match a known record."""
        if obj != "self":
            return None
        cls = self._current_self_type
        if not cls:
            return None
        for info in self._record_types.values():
            if info.get("whyml_name") == cls:
                return info.get("field_types", {}).get(field)
        return None

    def _field_type_of(self, attr_ir: "ExprIR") -> Optional[str]:
        """Resolve `self.<field>` or `global.<field>` to its declared IR type tag,
        or None if the target is not a known record-field access. Accepts both
        shapes: `Attribute(value=Var(name), attr=F)` and `FieldGet(object=name,
        field=F)` (Module5 uses both for different contexts).

        Lookup goes through `_record_types`, keyed by class name; the
        whyml_name matches `_current_self_type` (lowercased) for `self`, or the
        module-global class for global instances."""
        receiver_name = None
        field_name = None
        if attr_ir.get("type") == "Attribute":
            # 0442.md B1: Module5 emits an Attribute receiver under either `value`
            # (spec context) or `object` (body context, e.g. `d.disk[i]` on a global
            # record). Accept both, else a global array-field read falls through to the
            # abstract `subscript_get (x:int)` and mismatches the `array int` field.
            receiver = attr_ir.get("value") or attr_ir.get("object") or {}
            if isinstance(receiver, dict) and receiver.get("type") == "Var":
                receiver_name = receiver.get("name")
            field_name = attr_ir.get("attr")
        elif attr_ir.get("type") == "FieldGet":
            receiver_name = attr_ir.get("object")
            field_name = attr_ir.get("field")
        if receiver_name is None or field_name is None:
            return None
        # Determine the class name for the receiver
        cls = None
        if receiver_name == "self":
            cls = self._current_self_type
        else:
            # Check module-level global instances
            gcls = getattr(self, "_module_global_classes", {}).get(receiver_name)
            if gcls is not None and gcls in self._record_types:
                cls = self._record_types[gcls].get("whyml_name")
            else:
                # LOCAL record var: a driver `b = Bank()` then `b.balance[i]`. The
                # receiver's class comes from `_current_record_var_classes` (the same
                # map that lets `<recordvar>.method(...)` propagate a callee contract).
                # Without this, a record-local array-field subscript falls through to
                # the abstract `subscript_get (x:int)` and mismatches `array int` —
                # blocking a consequence driver from reading a record's field back.
                rvcls = getattr(self, "_current_record_var_classes", {}).get(receiver_name)
                if rvcls is not None and rvcls in self._record_types:
                    cls = self._record_types[rvcls].get("whyml_name")
                else:
                    # wrong-lowering.md §WL-03: a record-typed PARAMETER receiver
                    # (`b: Box` then `b.p[1]`) — `_record_param_classes` already maps
                    # the param to its record's whyml_name (set by `_param_type_str`).
                    # Without this a record-param field read falls through to the
                    # opaque `subscript_get`, blocking the faithful `Tuple[...]` field
                    # slot read. The value already IS the whyml_name.
                    pcls = getattr(self, "_record_param_classes", {}).get(receiver_name)
                    if pcls is not None:
                        cls = pcls
        if not cls:
            return None
        for info in self._record_types.values():
            if info.get("whyml_name") == cls:
                return info.get("field_types", {}).get(field_name)
        return None

    def _bool_ir_to_int_wrap(self, val: str, val_ir: Optional[BoolWrapIRView]) -> str:
        """If val_ir denotes a bool-typed IR expression, wrap val with
        an int coercion `(if X then 1 else 0)`. Mirrors the bool-source
        detection in _to_bool() so a `return isinstance(x, T)` style
        statement doesn't raise a bool inside `exception Return int`.

        Literal Bool atoms are handled by the caller's `val == "true"/"false"`
        branches and intentionally not detected here."""
        if val_ir is None:
            return val
        t = val_ir.get("type", "")
        op = val_ir.get("op", "")
        is_bool_source = (
            (t == "Compare")
            or (t == "BoolOp" and op in ("and", "or"))
            or (t == "UnaryOp" and op == "not")
            or (t == "BinOp" and op in ("==", "!=", "<", ">", "<=", ">=", "in", "not in"))
            or (t == "Call" and val_ir.get("func", "") in (
                "isinstance", "hasattr", "any", "all"))
            or (t in ("Exists", "Forall", "SetMem", "SetSubset", "SetEq",
                      "MapEq", "HasKey"))
        )
        if is_bool_source:
            return f"(if {val} then 1 else 0)"
        return val

    def _collect_tuple_array_locals(self, stmts: List[Dict[str, Any]]) -> Dict[str, int]:
        """07-0903 W1: locals assigned a list/array literal of uniform tuples
        (`a = [(x, y), …]`) → {name: tuple arity}. Used so `a[i][k]` destructures the
        element tuple (and is not mistaken for a 2-D matrix access)."""
        found: Dict[str, int] = {}
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                tgt = s.get("target", "")
                if isinstance(val, dict) and val.get("type") in ("ArrayLit", "ListLit") and tgt:
                    elts = val.get("elts", [])
                    tups = [e for e in elts
                            if isinstance(e, dict) and e.get("type") == "Tuple"]
                    if elts and len(tups) == len(elts):
                        arities = {len(e.get("elts", [])) for e in tups}
                        if len(arities) == 1:
                            found[tgt] = arities.pop()
            for k in ("body", "orelse"):
                if k in s:
                    found.update(self._collect_tuple_array_locals(s[k]))
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found.update(self._collect_tuple_array_locals(h.get("body", [])))
        return found

    def _split_tuple_slots(self, inner: str) -> List[str]:
        """Split a WhyML tuple body (`string, map string (option hval)`) on the
        TOP-LEVEL commas only — a nested `(…)` (a `map`'s codomain, or a nested
        tuple) is not split. Byte-identical to `inner.split(",")` (then `.strip()`)
        when there are no nested parens, so the existing flat-`(int,int)` path is
        unchanged."""
        slots: List[str] = []
        depth = 0
        cur = ""
        for ch in inner:
            if ch == "(":
                depth += 1
                cur += ch
            elif ch == ")":
                depth -= 1
                cur += ch
            elif ch == "," and depth == 0:
                slots.append(cur.strip())
                cur = ""
            else:
                cur += ch
        if cur.strip():
            slots.append(cur.strip())
        return slots

    def _collect_tuple_var_assigns(self, stmts: List[Dict[str, Any]]) -> Dict[str, int]:
        """0442.md C2: locals bound to a tuple-returning call (`p = mk(x)` where `mk`'s
        return type is `(int, …)`) → {name: arity}. The cross-method return-type map
        (`_module_method_return_types`, built in `transpile()`) supplies the tuple type;
        arity is the comma count + 1. Lets `p[i]` destructure and excludes `p` from the
        `ref 0` pre-decl (it is a tuple value, let-bound at first assignment)."""
        found: Dict[str, int] = {}
        rets = getattr(self, "_module_method_return_types", {})
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                tgt = s.get("target", "")
                if isinstance(val, dict) and val.get("type") == "Call" and tgt:
                    _fn = val.get("func", "")
                    rt = rets.get(_fn)
                    # cf6.md M1.6: a `self.<m>(…)` call — IR method names are stored
                    # `<class_lower>__<method>`, so resolve the key to catch `union_info =
                    # self._match_subject_union_info(…)` as a tuple local.
                    if rt is None and isinstance(_fn, str) and _fn.startswith("self."):
                        _cls = getattr(self, "_current_self_type", None)
                        rt = rets.get(f"{_cls}__{_fn[len('self.'):]}" if _cls else _fn)
                    if isinstance(rt, str) and rt.startswith("(") and "," in rt:
                        found[tgt] = rt.count(",") + 1
                        # cf6.md M1.6: record per-slot types so `a, b = <tuple local>` can type
                        # its targets (`uinfo` → emit_ir).
                        if not hasattr(self, "_tuple_var_slot_types"):
                            self._tuple_var_slot_types = {}
                        self._tuple_var_slot_types[tgt] = [
                            s.strip() for s in rt[1:-1].split(",")]
            for k in ("body", "orelse"):
                if k in s:
                    found.update(self._collect_tuple_var_assigns(s[k]))
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found.update(self._collect_tuple_var_assigns(h.get("body", [])))
        return found

    def _collect_option_tuple_locals(self, stmts: List[Dict[str, Any]]) -> Dict[str, str]:
        """self-tcb-reduction Tier-5 (union/match cluster C5): locals bound to an
        OPTION-tuple-returning call (`union_info = self._match_subject_union_info(...)`
        whose return type is `option (τ...)`) → {name: the full `option (τ...)` type}.
        Distinct from `_collect_tuple_var_assigns` (a BARE always-present tuple): a real
        option local's `is not None` guard and tuple-unpack lower to `match … with
        None/Some`. Also records the per-slot INNER tuple types in `_tuple_var_slot_types`
        so `a, b = <option local>` types its targets. This is a live-only helper called
        from the `\\trusted`-mirrored `_typed_local_vars`, so it needs no mirror body.
        Byte-inert: no corpus method returns `Optional[Tuple[...]]`."""
        found: Dict[str, str] = {}
        rets = getattr(self, "_module_method_return_types", {})
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                tgt = s.get("target", "")
                if isinstance(val, dict) and val.get("type") == "Call" and tgt:
                    _fn = val.get("func", "")
                    rt = rets.get(_fn)
                    if rt is None and isinstance(_fn, str) and _fn.startswith("self."):
                        _cls = getattr(self, "_current_self_type", None)
                        rt = rets.get(f"{_cls}__{_fn[len('self.'):]}" if _cls else _fn)
                    if (isinstance(rt, str) and rt.startswith("option (")
                            and rt.rstrip().endswith(")") and "," in rt):
                        _inner = rt[len("option "):].strip()
                        found[tgt] = rt
                        if not hasattr(self, "_tuple_var_slot_types"):
                            self._tuple_var_slot_types = {}
                        self._tuple_var_slot_types[tgt] = self._split_tuple_slots(_inner[1:-1])
            for k in ("body", "orelse"):
                if k in s:
                    found.update(self._collect_option_tuple_locals(s[k]))
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found.update(self._collect_option_tuple_locals(h.get("body", [])))
        return found

    def _collect_option_str_return_locals(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """self-tcb-reduction lever #1 sub-inc A cap (c): locals bound to a call whose
        registered abstract-val return type is `option string` (`_rec = self._record_valued_
        expr_whyml_type(val_ir)`). Such a local pre-declares `ref None` (an `option string`),
        its `is not None` guard lowers to a `match … with None/Some` discriminant, and a bare
        `return <local>` threads into the enclosing Optional[str] `_union_*` return arm — the
        scalar-string analogue of `_collect_option_tuple_locals`. Live-only helper called
        from the `\\trusted`-mirrored `_typed_local_vars`, so it needs no mirror body.
        Byte-inert: no corpus method's abstract self-call return is registered `option
        string` (only the lever-#1 emitter-internal helpers are)."""
        found: Set[str] = set()
        rets = getattr(self, "_module_method_return_types", {})
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                tgt = s.get("target", "")
                if isinstance(val, dict) and val.get("type") == "Call" and tgt:
                    _fn = val.get("func", "")
                    rt = rets.get(_fn)
                    if rt is None and isinstance(_fn, str) and _fn.startswith("self."):
                        _cls = getattr(self, "_current_self_type", None)
                        rt = rets.get(f"{_cls}__{_fn[len('self.'):]}" if _cls else _fn)
                    if rt == "option string":
                        found.add(tgt)
            for k in ("body", "orelse"):
                if k in s:
                    found.update(self._collect_option_str_return_locals(s[k]))
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found.update(self._collect_option_str_return_locals(h.get("body", [])))
        return found

    def _collect_optmap_getter_locals(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """self-tcb-reduction `_compute_return_type` PATH(b): local names bound from
        `getattr(self, "_compound_map_getter", None)` — an `Optional[Dict[str, str]]`
        self-field, modelled `option (map string (option string))`. Such a local
        pre-declares `ref (None: option (map string (option string)))`, its `is not None`
        guard lowers to a `match … None/Some` discriminant, and `<local>["<lit>"]` reads
        the inner map. Gated on emitting `_compute_return_type` -> byte-inert elsewhere."""
        if not self._emitting_compute_return_type():
            return set()
        out: Set[str] = set()

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") in ("Assign", "assign") and isinstance(
                        node.get("target"), str):
                    _v = node.get("value") or {}
                    if (isinstance(_v, dict) and _v.get("type") == "Call"
                            and _v.get("func") == "getattr"):
                        _a = _v.get("args") or []
                        if (len(_a) >= 2 and isinstance(_a[0], dict)
                                and _a[0].get("name") == "self"
                                and isinstance(_a[1], dict)
                                and _a[1].get("type") == "String"
                                and _a[1].get("value") == "_compound_map_getter"):
                            out.add(node["target"])
                for _x in node.values():
                    rec(_x)
            elif isinstance(node, list):
                for _x in node:
                    rec(_x)

        rec(stmts)
        return out

    def _collect_option_tuple_unpack_targets(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """self-tcb-reduction Tier-5 (union/match cluster C1b): the TARGET names of a
        `a, b = <option-tuple local>` unpack (`_uvar, uinfo = union_info`). These are
        let-bound FRESH inside the `Some (…)` arm with the SLOT's real type (string / map
        string (option hval) / hval), so they must be EXCLUDED from the integer `ref 0`
        pre-declaration (which would int-clash with a map/hval slot). Live-only helper
        called from the `\\trusted`-mirrored `_typed_local_vars`. Byte-inert: no corpus
        method unpacks an `Optional[Tuple[...]]`."""
        opt = getattr(self, "_option_tuple_vars", {})
        out: Set[str] = set()

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "TupleUnpack":
                    _v = node.get("value") or {}
                    if (isinstance(_v, dict) and _v.get("type") == "Var"
                            and _v.get("name") in opt):
                        for _t in node.get("targets", []) or []:
                            if isinstance(_t, str):
                                out.add(_t)
                for _x in node.values():
                    rec(_x)
            elif isinstance(node, list):
                for _x in node:
                    rec(_x)

        rec(stmts)
        return out - set(self._formal_params)

    def _call_return_whyml_type(self, fn: str) -> Optional[str]:
        """Resolve the declared WhyML return type of a call `fn` from the cross-method
        return-type map, for ALL receiver forms:
          - bare `func(...)`                      → `func`
          - `self.method(...)`                    → `<self_class>__method`
          - `<recordvar>.method(...)`             → via `_current_record_var_classes`
          - `<module_global>.method(...)`         → via `_module_global_classes`  ← the os
            `inode = _filesystem._read_inode(...)` case: a method on a module-global instance
            (07-2333 subscript_get gap — without this `inode` is typed int and `inode[2]`
            falls to the abstract `subscript_get` instead of `(!inode)[2]`).
        Returns the WhyML type string (e.g. `"array int"`) or None."""
        rmap = self._module_method_return_types
        if "." not in fn:
            return rmap.get(fn)
        obj, _, method = fn.rpartition(".")
        if obj == "self":
            cls = self._current_self_type
            return rmap.get(f"{cls}__{method}") if cls else None
        # receiver is a record-instance local OR a module-global instance
        cls = (getattr(self, "_current_record_var_classes", {}).get(obj)
               or getattr(self, "_module_global_classes", {}).get(obj))
        if cls:
            return rmap.get(f"{cls.lower()}__{method}")
        # last resort: the full dotted name might itself be a key (inlined forms)
        return rmap.get(fn)

    def _collect_array_var_assigns(self, stmts: List[Dict[str, Any]],
                                    seed: Optional[Set[str]] = None) -> Set[str]:
        """Post-pass to `IRScanner.find_array_and_dict_vars`: variables
        assigned to `self.<method>(...)` calls where <method> returns
        `array int` should also be tracked as arrays. The static
        IRScanner can't see this without the cross-method return-type
        map (built in `transpile()`).

        Also propagates array type transitively through var-to-var
        assignments (`y = x` where `x` is array → `y` is array).
        An optional `seed` set provides already-known array vars
        (e.g. from IRScanner) so transitive propagation covers
        cross-collector chains (inline.md: `_inl_res = arr_local`)."""
        found: Set[str] = set(seed) if seed else set()
        # Map target → source var for transitive propagation
        var_assigns: dict = {}
        # self-tcb-reduction (union/match cluster): target → (arm1_var, arm2_var) of a
        # both-arms-Var ternary (`true_branch_stmts = body if … else orelse`).
        ternary_assigns: dict = {}
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                tgt = s.get("target", "")
                if isinstance(val, dict) and val.get("type") == "Call":
                    fn = val.get("func", "")
                    if tgt and self._call_return_whyml_type(fn) == "array int":
                        found.add(tgt)
                    # list-comprehension-lowering.md L7: `re.findall(...)` → `array string`.
                    elif (tgt and isinstance(fn, str) and fn.endswith(".findall")
                          and getattr(self, "_mutable_state_classes", None)):
                        found.add(tgt)
                    # cf6.md M1.6: a DIRECT `<emit_ir>.get("captures"/"args"/"body")` →
                    # array local (`body_stmts = c.get("body", [])`). The `… or []` variant is
                    # a BinOp, handled in the elif below. @mutable_state.
                    elif (tgt and isinstance(fn, str) and fn.endswith(".get")
                          and getattr(self, "_mutable_state_classes", None)):
                        _ga = val.get("args") or []
                        if (_ga and isinstance(_ga[0], dict)
                                and _ga[0].get("type") == "String"
                                and _ga[0].get("value") in ("captures", "args", "body", "orelse", "parts", "elts", "alternatives")):
                            found.add(tgt)
                # list-comprehension-lowering.md L1: a local first-assigned a list
                # comprehension is an array local (its element-typed array from
                # `list_comp_<τ>`). @mutable_state-gated → byte-identical for the corpus.
                elif (isinstance(val, dict) and val.get("type") == "ListComp"
                      and tgt and getattr(self, "_mutable_state_classes", None)):
                    found.add(tgt)
                # cf6.md M1.6: a local first-assigned `<emit_ir>.get("captures"/"args"/"body")
                # or []` is an array local (`existing_caps`). NARROW condition (only `or`-BinOp,
                # since a direct Call is caught above) so it does NOT swallow the I-E Attribute
                # case below. @mutable_state-gated → byte-identical for the corpus.
                elif (tgt and getattr(self, "_mutable_state_classes", None)
                      and isinstance(val, dict)
                      and val.get("type") == "BinOp" and val.get("op") == "or"):
                    _vv = val.get("left", {})
                    if (isinstance(_vv, dict) and _vv.get("type") == "Call"
                            and isinstance(_vv.get("func"), str)
                            and _vv["func"].endswith(".get")):
                        _ga = _vv.get("args") or []
                        if (_ga and isinstance(_ga[0], dict)
                                and _ga[0].get("type") == "String"
                                and _ga[0].get("value") in ("captures", "args", "body", "orelse", "parts", "elts", "alternatives")):
                            found.add(tgt)
                elif isinstance(val, dict) and val.get("type") == "Var" and tgt:
                    var_assigns[tgt] = val.get("name", "")
                # self-tcb-reduction (union/match cluster): `X = A if C else B` where BOTH
                # arms are array-local Vars (`true_branch_stmts = body if true_is_none else
                # orelse`) → X is an array local. Recorded for the transitive fixpoint (both
                # arm vars must be array-classified first). @mutable_state-gated.
                elif (isinstance(val, dict) and val.get("type") == "IfExpr" and tgt
                      and getattr(self, "_mutable_state_classes", None)):
                    _av, _ov = val.get("body", {}), val.get("orelse", {})
                    if (isinstance(_av, dict) and _av.get("type") == "Var"
                            and isinstance(_ov, dict) and _ov.get("type") == "Var"):
                        ternary_assigns[tgt] = (_av.get("name", ""), _ov.get("name", ""))
                # i-feel-good.md I-E: a local first-assigned a `List`/`tuple` record-field
                # read (`targets = stmt.targets`) is an array local — the list-local-from-
                # field form. @mutable_state-gated → byte-identical for the corpus. The
                # receiver is a record-typed PARAM (`stmt: TupleUnpackStmt`), whose class is
                # in the symbol table (not `_current_record_var_classes`), so resolve the
                # field type directly rather than via `_field_type_of`.
                elif (isinstance(val, dict) and val.get("type") in ("Attribute", "FieldGet")
                      and tgt and getattr(self, "_mutable_state_classes", None)):
                    _recv = val.get("object")
                    if isinstance(_recv, dict):
                        _recv = _recv.get("name")
                    _fld = val.get("field") or val.get("attr")
                    _cls = getattr(self, "_current_symbol_table", {}).get(_recv) if _recv else None
                    _rt = getattr(self, "_record_types", {})
                    _rec = (_rt.get(_cls) or (_rt.get(_cls.lower()) if _cls else None)) if _cls else None
                    if _rec and _rec.get("field_types", {}).get(_fld) in ("list", "tuple"):
                        found.add(tgt)
                    # self-tcb-reduction T1.a: `elts = node.elts` — a node-LIST attr on an emit_ir
                    # node is an `array emit_ir` local (`args_of`). @mutable_state.
                    elif _fld in ("elts", "parts", "args", "captures", "alternatives") and isinstance(
                            val.get("object") or val.get("value"), dict) and self._is_emit_ir_expr(
                            val.get("object") or val.get("value")):
                        found.add(tgt)
            for k in ("body", "orelse"):
                if k in s:
                    found |= self._collect_array_var_assigns(s[k])
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found |= self._collect_array_var_assigns(h.get("body", []))
        # Transitive propagation: y = x where x is array → y is array; and a both-arms-
        # Var ternary target is array once BOTH arm vars are array-classified.
        changed = True
        while changed:
            changed = False
            for tgt, src in var_assigns.items():
                if tgt not in found and src in found:
                    found.add(tgt)
                    changed = True
            for tgt, (_a, _o) in ternary_assigns.items():
                if tgt not in found and _a in found and _o in found:
                    found.add(tgt)
                    changed = True
        return found

    def _split_tuple_type(self, rt: str) -> List[str]:
        """Split a WhyML tuple type `(int, array int, map int (option int))` into its
        top-level slot type strings. The slot types in play (int / array int / string /
        real / `map int (option int)`) contain NO top-level comma, so a comma split of
        the paren-stripped body is exact."""
        inner = rt.strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1]
        return [p.strip() for p in inner.split(",")]

    def _collect_struct_unpack_array_targets(
            self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Phase 2.3b: tuple-unpack LHS slots whose slot type is `array int`. From
        `(a, b) = struct.unpack(fmt, data)` (slot type from the format string) AND
        (body-gate gap-3) from `(a, b) = func(...)` where `func`'s cross-method return
        type is a tuple with an `array int` slot — e.g. `inode_num, name_bytes =
        _unpack_direntry(entry)` with `_unpack_direntry : (int, array int)`. These are
        NOT hoisted — they get let-bound inside the loop iteration so Why3's region
        inference doesn't collapse fresh-region arrays across iterations.
        """
        from module6_whyml.struct_format import parse_format

        def _scan(stmts: List[Dict[str, Any]]) -> Set[str]:
            found: Set[str] = set()
            for s in stmts:
                if s.get("stmt") == "TupleUnpack":
                    val = s.get("value", {})
                    if isinstance(val, dict) and val.get("type") == "Call":
                        fn = val.get("func", "")
                        targets = s.get("targets", [])
                        if fn == "struct.unpack":
                            fmt_arg = (val.get("args") or [{}])[0]
                            if fmt_arg.get("type") == "String":
                                parsed = parse_format(fmt_arg.get("value", ""))
                                if parsed is not None:
                                    for tgt, slot_t in zip(targets, parsed.slots):
                                        if slot_t == "array int":
                                            found.add(tgt)
                        else:
                            rt = self._call_return_whyml_type(fn)
                            if isinstance(rt, str) and rt.startswith("(") and "," in rt:
                                for tgt, slot_t in zip(targets, self._split_tuple_type(rt)):
                                    if slot_t == "array int":
                                        found.add(tgt)
                for k in ("body", "orelse"):
                    if k in s:
                        found |= _scan(s[k])
                if s.get("stmt") == "Try":
                    for h in s.get("handlers", []):
                        found |= _scan(h.get("body", []))
            return found

        return _scan(stmts)

    def _collect_struct_pack_assign_targets(
            self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Plain `X = struct.pack(fmt, ...)` assign targets — receive
        an `array int` from struct.pack and must be pre-declared as
        `ref (Array.make 0 0)`. Unlike the tuple-unpack-target case
        these ARE hoisted (single-shot bindings used later in the
        function body, typically outside any loop).
        """
        from module6_whyml.struct_format import parse_format

        def _scan(stmts: List[Dict[str, Any]]) -> Set[str]:
            found: Set[str] = set()
            for s in stmts:
                if s.get("stmt") == "Assign":
                    val = s.get("value", {})
                    if (isinstance(val, dict)
                            and val.get("type") == "Call"
                            and val.get("func", "") == "struct.pack"):
                        fmt_arg = (val.get("args") or [{}])[0]
                        if (fmt_arg.get("type") == "String"
                                and parse_format(fmt_arg.get("value", "")) is not None):
                            tgt = s.get("target", "")
                            if tgt:
                                found.add(tgt)
                for k in ("body", "orelse"):
                    if k in s:
                        found |= _scan(s[k])
                if s.get("stmt") == "Try":
                    for h in s.get("handlers", []):
                        found |= _scan(h.get("body", []))
            return found

        return _scan(stmts)

    def _collect_variant_var_assigns(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Locals whose RHS is a sum-type constructor — an applied ctor
        `o = Some(7)` (`Call` to a name in `self._constructors`) or a
        nullary ctor `o = Nothing` (`Var` whose name is a nullary ctor).
        Excluded from the integer `ref 0` pre-declaration path so the
        first-assign emits `let o = ref (Some 7) in` with the inferred
        variant type instead of a type-clashing `ref 0` + `:=`."""
        ctors = getattr(self, "_constructors", {})
        found: Set[str] = set()
        if not ctors:
            return found
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                if isinstance(val, dict):
                    is_ctor = (
                        (val.get("type") == "Call" and val.get("func") in ctors)
                        or (val.get("type") == "Var" and val.get("name") in ctors))
                    if is_ctor:
                        tgt = s.get("target", "")
                        if tgt:
                            found.add(tgt)
            for k in ("body", "orelse"):
                if k in s:
                    found |= self._collect_variant_var_assigns(s[k])
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found |= self._collect_variant_var_assigns(h.get("body", []))
        return found

    def _collect_dict_var_assigns(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Post-pass for body-dict / body-set local detection: variables
        whose RHS yields a `map int (option int)` value (via map-typed
        param Var, IfExpr branches, BinOp `|`/`&`/`-` between map-typed
        sides, etc.). Used to exclude them from the integer `ref 0`
        pre-declaration path."""
        found: Set[str] = set()
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                if isinstance(val, dict) and self._rhs_yields_map(val):
                    tgt = s.get("target", "")
                    if tgt:
                        found.add(tgt)
            for k in ("body", "orelse"):
                if k in s:
                    found |= self._collect_dict_var_assigns(s[k])
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found |= self._collect_dict_var_assigns(h.get("body", []))
        return found
