from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, TypedDict
from dataclasses import dataclass
def mutable_state(cls): return cls
_BOOL_BINOPS = frozenset({'==', '!=', '<', '<=', '>', '>=', 'is', 'is not', 'in', 'not in'})


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
""  # pycsl
@mutable_state
@dataclass
class TypeInferenceMixin:
    'Type inference and collection-metadata tracking for the transpiler.\n\n    Covers three concerns:\n\n    * **First-assignment classification** (`_first_assign_kind`,\n      `_emit_first_assign` callers): record vs lambda vs array vs dict vs\n      bounded-int vs default, used to pick the `let X = ...` shape.\n    * **RHS type queries** (`_rhs_yields_array`, `_rhs_yields_map`,\n      `_field_type_for`, `_field_type_of`): does this IR expression\n      produce an `array int` / `map int (option int)` / typed self-field?\n      Drives the dict-vs-array vs int slot choices throughout statement\n      emission.\n    * **Collection constant-folding metadata** (`_track_collection_metadata`):\n      records known sizes/elements of literal collections so `len(...)`\n      and `sum(...)` can fold to constants during expression emission.\n\n    Mixed into Module6_WhyMLTranspiler. State accessed via `self`:\n    `_record_types`, `_known_collection_sizes`, `_known_collection_elements`,\n    `_array_locals`, `_dict_locals`, `_current_symbol_table`,\n    `_current_array1d_params`, `_current_self_type`,\n    `_module_method_return_types`, `_bounded_int`, the various\n    `_ghost_*_vars` sets.\n    '
    _record_types: Dict[str, Any] = None
    _current_symbol_table: Dict[str, str] = None
    _current_self_type: str = ""
    _module_method_return_types: Dict[str, str] = None
    _current_record_var_classes: Dict[str, str] = None
    _module_global_classes: Dict[str, str] = None
    _record_param_classes: Dict[str, str] = None
    # W8/W1 residual: local -> element RECORD CLASS name, for a local bound from an
    # element of an `array <record>` self-field or from a record-returning sibling call
    # (`t = self.cur()`). Mirror-only infra declaration, like the sibling maps above —
    # the live transpiler creates it in `statements._emit_body_code`. Without the
    # declaration the `getattr(self, "_record_field_elem_locals", {})` read is opaque and
    # its `.get(...)` result int-erases against the string-keyed `_record_types`.
    _record_field_elem_locals: Dict[str, str] = None
    _array_locals: Set[str] = None
    _dict_locals: Set[str] = None
    _current_array1d_params: Set[str] = None
    _variant_types: Dict[str, str] = None
    _mutable_state_classes: Set[str] = None
    _ghost_list_vars: Set[str] = None
    _ghost_set_vars: Set[str] = None
    _ghost_dict_vars: Set[str] = None
    _ghost_string_vars: Set[str] = None
    _ghost_tuple_vars: Dict[str, int] = None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _track_collection_metadata(self, target: str, val_ir: int) -> None:
        pass

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
    #@ sibling_concrete
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
                    else:
                        # W8/W1 residual: a RECORD-ELEMENT LOCAL — one bound from an
                        # element of an `array <record>` self-field, or from a sibling
                        # call with a record return (`t = self.cur()`, the opening line of
                        # every parser predicate) — resolves its field types exactly like
                        # a record PARAM receiver. `_record_field_elem_locals` already maps
                        # it (that map is what makes `t.<field>` project natively);
                        # without it here, `t.start[0]` — an integer subscript into a
                        # `Tuple[int,int]` FIELD — could not find the synthesized
                        # `pytuple_int_int` namedtuple record and fell through to the
                        # opaque `subscript_get (x: int)`, which mistypes against it.
                        # NOTE the map stores the record CLASS name, not its whyml name
                        # (unlike `_record_param_classes`) — translate. Empty for every
                        # file without an `array <record>` self-field -> byte-inert.
                        ecls = getattr(self, "_record_field_elem_locals", {}).get(
                            receiver_name)
                        if ecls is not None and ecls in self._record_types:
                            cls = self._record_types[ecls].get("whyml_name")
        if not cls:
            return None
        for info in self._record_types.values():
            if info.get("whyml_name") == cls:
                return info.get("field_types", {}).get(field_name)
        return None

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _bool_ir_to_int_wrap(self, val: str, val_ir: Optional[BoolWrapIRView]) -> str:
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns self._tuple_var_slot_types
    def _collect_tuple_var_assigns(self, stmts: List[Dict[str, Any]]) -> Dict[str, int]:
        """0442.md C2: locals bound to a tuple-returning call (`p = mk(x)` where `mk`'s
        return type is `(int, …)`) → {name: arity}."""
        found: Dict[str, int] = {}
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
                    if isinstance(rt, str) and rt.startswith("(") and "," in rt:
                        found[tgt] = rt.count(",") + 1
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_return_whyml_type(self, fn: str) -> Optional[str]:
        rmap = self._module_method_return_types
        if "." not in fn:
            return rmap.get(fn)
        obj, _, method = fn.rpartition(".")
        if obj == "self":
            cls = self._current_self_type
            return rmap.get(f"{cls}__{method}") if cls else None
        cls = (getattr(self, "_current_record_var_classes", {}).get(obj)
               or getattr(self, "_module_global_classes", {}).get(obj))
        if cls:
            return rmap.get(f"{cls.lower()}__{method}")
        return rmap.get(fn)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_array_var_assigns(self, stmts: List[int], seed: int=None) -> int:
        return set()

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _split_tuple_type(self, rt: str) -> List[str]:
        """Split a WhyML tuple type `(int, array int, map int (option int))` into its
        top-level slot type strings. The slot types in play (int / array int / string /
        real / `map int (option int)`) contain NO top-level comma, so a comma split of
        the paren-stripped body is exact."""
        inner = rt.strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1]
        return [p.strip() for p in inner.split(",")]

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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


