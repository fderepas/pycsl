from __future__ import annotations
from typing import Dict, Any, Set, List, Tuple
""  # pycsl
class IRScanner:
    'Stateless recursive walkers over the IR dict tree.'
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_arrayset(stmts: List[int]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def ends_with_return(stmts: List[int]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_assigned_vars(stmts: List[int]) -> int:
        return set()

    #@ requires True
    #@ ensures True
    #@ assigns targets
    @staticmethod
    def find_named_expr_targets(obj: Any, targets: Set[str]) -> None:
        if isinstance(obj, dict):
            if obj.get("type") == "NamedExpr":
                targets.add(obj["target"])
            for k, v in obj.items():
                if k == "stmt":
                    continue
                IRScanner.find_named_expr_targets(v, targets)
        elif isinstance(obj, list):
            for item in obj:
                IRScanner.find_named_expr_targets(item, targets)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_ghost_vars(stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_ghost_type(stmts: List[int], types: int) -> bool:
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def collection_binder_kinds(obj: Any) -> Set[str]:
        """07-1311 Q4: collect the set of COLLECTION quantifier binder types
        (`list`/`bytes`/`bytearray`/`dict`) appearing anywhere in `obj` (a contract
        or body IR tree). Used by the preamble to trigger `use array.Array` /
        `use map.Map` for `\\forall a: list; …` / `\\forall m: dict; …`, since such a
        binder needs the theory even when the file has no array/map locals."""
        found: Set[str] = set()
        if isinstance(obj, dict):
            if obj.get("type") in ("Forall", "Exists"):
                bt = obj.get("binder_type")
                if bt in ("list", "bytes", "bytearray", "dict"):
                    found.add(bt)
            for v in obj.values():
                found |= IRScanner.collection_binder_kinds(v)
        elif isinstance(obj, list):
            for x in obj:
                found |= IRScanner.collection_binder_kinds(x)
        return found

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_array_and_dict_vars(stmts: List[int]) -> int:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_inline_set_or_dict_ops(obj: Any) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_lambda_vars(stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_record_vars(stmts: List[int], record_types: int) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_record_var_classes(stmts: List[int], record_types: int) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def has_continue(stmts: List[int]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_continue(stmts: List[int]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_break(stmts: List[int]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def collect_user_exceptions(stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def collect_escaping_exceptions(stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def has_direct_return(stmts: List[int]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def has_in_loop_return(stmts: List[int]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def has_early_return(stmts: List[int]) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_for(stmts: List[int]) -> bool:
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_subscript(obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "Subscript":
                return True
            return any(IRScanner.uses_subscript(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_subscript(item) for item in obj)
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_array_lit(obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "ArrayLit":
                return True
            if (obj.get("type") == "BinOp" and obj.get("op") == "*" and
                    isinstance(obj.get("left"), dict) and obj["left"].get("type") == "ArrayLit"):
                return True
            return any(IRScanner.uses_array_lit(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_array_lit(item) for item in obj)
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_minmax(obj: Any) -> bool:
        if isinstance(obj, dict):
            if (obj.get("type") == "Call" and
                    obj.get("func") in ("min", "max") and
                    len(obj.get("args", [])) == 2):
                return True
            return any(IRScanner.uses_minmax(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_minmax(item) for item in obj)
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def is_recursive(name: str, obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "Call" and obj.get("func") == name:
                return True
            return any(IRScanner.is_recursive(name, v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.is_recursive(name, item) for item in obj)
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_string(obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "String":
                return True
            return any(IRScanner.uses_string(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_string(item) for item in obj)
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_sum(obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "Sum":
                return True
            return any(IRScanner.uses_sum(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_sum(item) for item in obj)
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_set_card(obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "SetCard":
                return True
            return any(IRScanner.uses_set_card(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_set_card(item) for item in obj)
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_ord_chr(obj: Any) -> bool:
        """10-2300-spec-5: True if any `ord(...)`/`chr(...)` call appears, so the
        preamble pulls `use string.Char` (the char<->int bridge theory). Fires the
        SAME trigger as the emitter (expressions.py `_call_named_builtins`), so the
        `use` is emitted iff `ord_op`/`chr_op` is registered — keeping byte-additivity
        exact (no spurious `use string.Char` when ord/chr is absent)."""
        if isinstance(obj, dict):
            if obj.get("type") == "Call" and obj.get("func") in ("ord", "chr"):
                return True
            return any(IRScanner.uses_ord_chr(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_ord_chr(item) for item in obj)
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_divmod(stmts: Any) -> bool:
        def _check(obj: Any) -> bool:
            if isinstance(obj, dict):
                if obj.get("type") == "BinOp" and obj.get("op") in ("div", "/", "%"):
                    return True
                return any(_check(v) for v in obj.values())
            if isinstance(obj, list):
                return any(_check(item) for item in obj)
            return False
        return _check(stmts)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_append_targets(stmts: List[int]) -> int:
        return set()

    _MUTATING_METHODS: int = {'append', 'pop', 'clear', 'add', 'remove', 'discard', 'update', 'extend', 'insert', 'setdefault'}
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _collect_mutations(stmts: List[int], target_name: str, out: List[int]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_iteration_mutations(stmts: List[int]) -> List[int]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_return_type(stmts: List[int]) -> str:
        return ""


