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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _test_contains_map(self, expr: Any, map_locals: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _has_set_op_on_map(self, obj: Any, map_locals: int=None) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _should_auto_trust_set_op(self, body_stmts: List[int], func_trusted: bool) -> bool:
        return False

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


