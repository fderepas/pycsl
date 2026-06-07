from __future__ import annotations

from typing import Any, Dict, List, Optional, Set


# Bool-typed BinOp operators — RHS of any of these is a Python bool and
# needs `(if X then 1 else 0)` wrapping before flowing into a WhyML int slot.
_BOOL_BINOPS = frozenset({
    "==", "!=", "<", "<=", ">", ">=", "is", "is not", "in", "not in",
})


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
    def _val_is_bool(val_ir: Dict[str, Any]) -> bool:
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

    def _first_assign_kind(self, val: str, val_ir: Dict[str, Any]) -> str:
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

    def _rhs_yields_array(self, val_ir: Dict[str, Any]) -> bool:
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

    def _rhs_yields_map(self, val_ir: Dict[str, Any]) -> bool:
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

    def _field_type_of(self, attr_ir: Dict[str, Any]) -> Optional[str]:
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
        if not cls:
            return None
        for info in self._record_types.values():
            if info.get("whyml_name") == cls:
                return info.get("field_types", {}).get(field_name)
        return None

    def _bool_ir_to_int_wrap(self, val: str, val_ir: Optional[Dict[str, Any]]) -> str:
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
                    rt = rets.get(val.get("func", ""))
                    if isinstance(rt, str) and rt.startswith("(") and "," in rt:
                        found[tgt] = rt.count(",") + 1
            for k in ("body", "orelse"):
                if k in s:
                    found.update(self._collect_tuple_var_assigns(s[k]))
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found.update(self._collect_tuple_var_assigns(h.get("body", [])))
        return found

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
        for s in stmts:
            if s.get("stmt") == "Assign":
                val = s.get("value", {})
                tgt = s.get("target", "")
                if isinstance(val, dict) and val.get("type") == "Call":
                    fn = val.get("func", "")
                    if fn.startswith("self."):
                        tail = fn[len("self."):]
                        cls = self._current_self_type
                        key = f"{cls}__{tail}" if cls else tail
                        ret = self._module_method_return_types.get(key)
                        if ret == "array int" and tgt:
                            found.add(tgt)
                    else:
                        # inline.md: bare function calls (from inlined
                        # method bodies) whose return type is array int.
                        ret = self._module_method_return_types.get(fn)
                        if ret == "array int" and tgt:
                            found.add(tgt)
                elif isinstance(val, dict) and val.get("type") == "Var" and tgt:
                    var_assigns[tgt] = val.get("name", "")
            for k in ("body", "orelse"):
                if k in s:
                    found |= self._collect_array_var_assigns(s[k])
            if s.get("stmt") == "Try":
                for h in s.get("handlers", []):
                    found |= self._collect_array_var_assigns(h.get("body", []))
        # Transitive propagation: y = x where x is array → y is array
        changed = True
        while changed:
            changed = False
            for tgt, src in var_assigns.items():
                if tgt not in found and src in found:
                    found.add(tgt)
                    changed = True
        return found

    def _collect_struct_unpack_array_targets(
            self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Phase 2.3b: tuple-unpack LHS slots from
        `(a, b) = struct.unpack(fmt, data)` whose parsed slot type is
        `array int`. These are NOT hoisted — they get let-bound
        inside the loop iteration so Why3's region inference doesn't
        collapse fresh-region arrays across iterations.
        """
        from module6_whyml.struct_format import parse_format

        def _scan(stmts: List[Dict[str, Any]]) -> Set[str]:
            found: Set[str] = set()
            for s in stmts:
                if s.get("stmt") == "TupleUnpack":
                    val = s.get("value", {})
                    if (isinstance(val, dict)
                            and val.get("type") == "Call"
                            and val.get("func", "") == "struct.unpack"):
                        fmt_arg = (val.get("args") or [{}])[0]
                        if fmt_arg.get("type") == "String":
                            parsed = parse_format(fmt_arg.get("value", ""))
                            if parsed is not None:
                                targets = s.get("targets", [])
                                for tgt, slot_t in zip(targets, parsed.slots):
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
