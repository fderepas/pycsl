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
    _array_locals: Set[str] = None
    _dict_locals: Set[str] = None
    _current_array1d_params: Set[str] = None
    _variant_types: Dict[str, str] = None
    _mutable_state_classes: Set[str] = None

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _first_assign_kind(self, val: str, val_ir: int) -> str:
        return ""

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

    # M2 (2026-07-10 converter run): PARKED, NOT converted. `_rhs_yields_array` (below)
    # converts clean, but `_rhs_yields_map`'s `IfExpr` recursive arm —
    # `val_ir.get("body")` / `val_ir.get("orelse")` — hits a genuine emit_ir-ADT gap, not
    # a "fire an existing recognizer" case: `_EMIT_IR_PROJ` (module6_whyml/expressions.py)
    # has NO "orelse" entry at all (`orelse_of` does not exist in the preamble ADT), and
    # its "body" entry is hardwired to `stmts_of` (the stmt-list reader used by
    # IfStmt/TryStmt), which collides with the IfExprExpr ternary's SCALAR `body`
    # sub-expression — the shared table has no per-node-kind disambiguation. Reproduced:
    # `PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py src/self-annotate/src/module6_whyml/
    # types.py --import-path src/pycsl --fun typeinferencemixin___rhs_yields_map` ->
    # "This expression has type int, but is expected to have type ... emit_ir" (the
    # `orelse` arm hits the untagged `.get` fallback, which hashes the key to an int).
    # Fixing this needs a NEW ADT total-function projector (`orelse_of`) plus a
    # context-sensitive "body" override — out of scope for this increment (no new
    # opaque val, no ad-hoc ADT surface without a mandate). Kept on the trusted-stub path.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _rhs_yields_map(self, val_ir: "ExprIR") -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _resolve_effective_ghost_type(self, target: str, op: str, ghost_type: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_type_for(self, obj: str, field: str) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _field_type_of(self, attr_ir: "ExprIR") -> Optional[str]:
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_tuple_var_assigns(self, stmts: List[int]) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _call_return_whyml_type(self, fn: str) -> Optional[str]:
        return None

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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_struct_unpack_array_targets(self, stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_struct_pack_assign_targets(self, stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_variant_var_assigns(self, stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_dict_var_assigns(self, stmts: List[int]) -> int:
        return set()


