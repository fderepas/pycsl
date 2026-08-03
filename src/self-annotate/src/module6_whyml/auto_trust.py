from __future__ import annotations
from typing import Any, Dict, List, Optional, Set
from module6_whyml.ir_scanner import IRScanner
""  # pycsl
class AutoTrustMixin:
    'Auto-trust decisions and linear-VC classification.\n\n    Auto-trust converts a function from `let` (full body emitted) to `val`\n    (contract-only) when the body cannot be cleanly typed in WhyML — typically\n    because map-typed values would need to flow through int-typed slots, or\n    because array/tuple returns hit early-return restrictions.\n\n    Linear-VC classification flags ensures/requires clauses that contain only\n    linear arithmetic so the runner can route them to omega proofs in Lean 4\n    instead of Why3/Alt-Ergo. See `docs/self-annotate-layer2-queue.md` for the\n    auto-trust class taxonomy.\n    '
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _build_witness_str(field_names: List[str], vals: int, field_types: int=None, array_lengths: int=None) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _extract_array_lengths(invs: List[Any]) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _check_witness_vals(self, vals: int, invs: List[Any], field_names: List[str]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_linear_expr(expr: Any) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_linear_vc(ensures_exprs: List[Any], requires_exprs: Optional[List[Any]]=None) -> bool:
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _should_auto_trust_map_return(self, func: Dict[str, Any], func_trusted: bool) -> bool:
        """Class M sub-case for set/dict-typed returns. Functions declared
        `-> Set[T]` / `-> Dict[K, V]` with early returns inside `if`
        branches emit `raise (Return (map_update_some ...))` which Why3
        rejects because `Return int` can't carry a `map int (option int)`
        payload. Auto-trust so the body is skipped and the contract alone
        is emitted. Tracked in `self._auto_trusted_map_returns`."""
        if func_trusted:
            return False
        return func.get("return_annotation") in ("set", "dict", "frozenset")

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_map_typed_locals(self, stmts: List[int]) -> int:
        return set()

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _test_contains_map(self, expr: Any, map_locals: Set[str]) -> bool:
        """Recursively check whether `expr` (an If/while test) contains
        a map-typed OR array-typed subexpression. Walks through
        UnaryOp(not, ...), BoolOp(and/or, ...), Compare wrappers —
        anywhere a collection could be used as a bool would trigger
        the `(X <> 0)` problem."""
        if not isinstance(expr, dict):
            return False
        # A subscript/slice yields an element (int), not the collection —
        # `if arr[i] == 1:` / `if d[k]:` does NOT use the collection as a
        # truthiness operand. Consume it: check only the index, never
        # recurse into the collection base (which would mis-flag the
        # enclosing function for auto-trust).
        if expr.get("type") in ("Subscript", "SliceAccess", "ChainedSubscript"):
            for key in ("index", "index1", "index2"):
                idx = expr.get(key)
                if isinstance(idx, dict) and self._test_contains_map(idx, map_locals):
                    return True
            return False
        if (expr.get("type") == "Var" and expr.get("name") in map_locals):
            return True
        if self._rhs_yields_map(expr) or self._rhs_yields_array(expr):
            return True
        for v in expr.values():
            if isinstance(v, dict):
                if self._test_contains_map(v, map_locals):
                    return True
            elif isinstance(v, list):
                for item in v:
                    if self._test_contains_map(item, map_locals):
                        return True
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _has_set_op_on_map(self, obj: Any, map_locals: int=None) -> bool:
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _should_auto_trust_set_op(self, body_stmts: List[int], func_trusted: bool) -> bool:
        if func_trusted:
            return False
        map_locals = self._collect_map_typed_locals(body_stmts)
        return self._has_set_op_on_map(body_stmts, map_locals)

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _should_auto_trust_array_return(self, func: int, body_stmts: List[Dict[str, Any]], return_type: str, func_trusted: bool) -> bool:
        if func_trusted or return_type != "array int":
            return False
        return (IRScanner.has_early_return(body_stmts)
                or IRScanner.has_in_loop_return(body_stmts))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _should_auto_trust_tuple_return(self, body_stmts: List[int], return_type: str, func_trusted: bool) -> bool:
        return False


