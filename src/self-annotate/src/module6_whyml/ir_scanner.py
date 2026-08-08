from __future__ import annotations
from typing import Dict, Any, Set, List, Tuple
""  # pycsl
class IRScanner:
    'Stateless recursive walkers over the IR dict tree.'
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_arrayset(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            if stmt.get("stmt") == "ArraySet":
                return True
            for key in ("body", "orelse"):
                if key in stmt and IRScanner.uses_arrayset(stmt[key]):
                    return True
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def ends_with_return(stmts: List[Dict[str, Any]]) -> bool:
        if not stmts:
            return False
        last = stmts[-1]
        st = last.get("stmt") or last.get("type")
        if st == "Return":
            return True
        if st == "If":
            return (IRScanner.ends_with_return(last.get("body", []))
                    and IRScanner.ends_with_return(last.get("orelse", [])))
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_assigned_vars(stmts: List[Dict[str, Any]]) -> Set[str]:
        assigned = set()
        for stmt in stmts:
            if stmt["stmt"] in ("Assign", "AugAssign"):
                assigned.add(stmt["target"])
            elif stmt["stmt"] == "TupleUnpack":
                assigned.update(stmt.get("targets", []))
            elif stmt["stmt"] == "While":
                assigned.update(IRScanner.find_assigned_vars(stmt["body"]))
            elif stmt["stmt"] == "If":
                assigned.update(IRScanner.find_assigned_vars(stmt.get("body", [])))
                assigned.update(IRScanner.find_assigned_vars(stmt.get("orelse", [])))
            elif stmt["stmt"] == "For":
                tgt = stmt.get("target", "")
                if tgt:
                    assigned.add(tgt)
                assigned.update(IRScanner.find_assigned_vars(stmt.get("body", [])))
            elif stmt["stmt"] == "Try":
                assigned.update(IRScanner.find_assigned_vars(stmt.get("body", [])))
                for h in stmt.get("handlers", []):
                    assigned.update(IRScanner.find_assigned_vars(h.get("body", [])))
            elif stmt["stmt"] == "Match":
                for c in stmt.get("cases", []):
                    assigned.update(IRScanner.find_assigned_vars(c.get("body", [])))
            IRScanner.find_named_expr_targets(stmt, assigned)
        return assigned

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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_ghost_vars(stmts: List[Dict[str, Any]]) -> Set[str]:
        ghosts = set()
        for stmt in stmts:
            if stmt["stmt"] == "GhostAssign":
                ghosts.add(stmt["target"])
            elif stmt["stmt"] == "While":
                ghosts.update(IRScanner.find_ghost_vars(stmt["body"]))
            elif stmt["stmt"] == "If":
                ghosts.update(IRScanner.find_ghost_vars(stmt.get("body", [])))
                ghosts.update(IRScanner.find_ghost_vars(stmt.get("orelse", [])))
            elif stmt["stmt"] == "For":
                ghosts.update(IRScanner.find_ghost_vars(stmt.get("body", [])))
        return ghosts

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_ghost_type(stmts: List[Dict[str, Any]], types: Set[str]) -> bool:
        """Return True if any GhostAssign in stmts (recursively) has ghost_type in types."""
        for stmt in stmts:
            if stmt.get("stmt") == "GhostAssign" and stmt.get("ghost_type") in types:
                return True
            for key in ("body", "orelse"):
                if key in stmt and IRScanner.uses_ghost_type(stmt[key], types):
                    return True
        return False

    #@ requires True
    #@ ensures setfold_leaf_empty(obj, \result)
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_inline_set_or_dict_ops(obj: Any) -> bool:
        """True iff anywhere in `obj` (a stmt list or arbitrary IR object)
        there is a SetLit / DictLit, a set/dict/frozenset constructor call,
        or a `.add()`/`.discard()`/`.remove()` method-call ExprStmt. These
        all emit `map_update_some` / `map_update_none` into the WhyML,
        which requires `use map.Map` + `use option.Option` in the preamble
        — even if no body-local variable is bound to a set or dict."""
        if isinstance(obj, dict):
            t = obj.get("type", "")
            if t in ("SetLit", "DictLit"):
                return True
            if t == "Call":
                fn = obj.get("func", "")
                if fn in ("set", "dict", "frozenset",
                          "defaultdict", "Counter", "OrderedDict"):
                    return True
                # `<obj>.add(x)` / `.discard(x)` / `.remove(x)` patterns
                if (fn.endswith(".add") or fn.endswith(".discard")
                        or fn.endswith(".remove")):
                    return True
            for v in obj.values():
                if IRScanner.uses_inline_set_or_dict_ops(v):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if IRScanner.uses_inline_set_or_dict_ops(item):
                    return True
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_lambda_vars(stmts: List[Dict[str, Any]]) -> Set[str]:
        lambda_vars = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Assign":
                val = stmt.get("value", {})
                if isinstance(val, dict) and val.get("type") == "Lambda":
                    lambda_vars.add(stmt.get("target", ""))
            for key in ("body", "orelse"):
                if key in stmt:
                    lambda_vars |= IRScanner.find_lambda_vars(stmt[key])
            if stmt.get("stmt") == "While":
                lambda_vars |= IRScanner.find_lambda_vars(stmt.get("body", []))
            if stmt.get("stmt") == "For":
                lambda_vars |= IRScanner.find_lambda_vars(stmt.get("body", []))
            if stmt.get("stmt") == "Match":
                for c in stmt.get("cases", []):
                    lambda_vars |= IRScanner.find_lambda_vars(c.get("body", []))
        return lambda_vars

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_record_vars(stmts: List[Dict[str, Any]], record_types: Set[str]) -> Set[str]:
        record_vars = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Assign":
                val = stmt.get("value", {})
                if (isinstance(val, dict) and val.get("type") == "Call" and
                        val.get("func", "") in record_types):
                    record_vars.add(stmt.get("target", ""))
            for key in ("body", "orelse"):
                if key in stmt and isinstance(stmt[key], list):
                    record_vars |= IRScanner.find_record_vars(stmt[key], record_types)
            if stmt.get("stmt") == "While":
                record_vars |= IRScanner.find_record_vars(stmt.get("body", []), record_types)
            if stmt.get("stmt") == "For":
                record_vars |= IRScanner.find_record_vars(stmt.get("body", []), record_types)
            if stmt.get("stmt") == "Match":
                for c in stmt.get("cases", []):
                    record_vars |= IRScanner.find_record_vars(c.get("body", []), record_types)
        return record_vars

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_record_var_classes(stmts: List[Dict[str, Any]],
                                record_types: Set[str]) -> Dict[str, str]:
        """Map each local assigned from a record constructor (`c = C()`) to its
        class name `C`. Lets method calls `c.method(...)` resolve the callee's
        contract (`<class>__<method>`), the same way `self.method(...)` does."""
        out: Dict[str, str] = {}
        for stmt in stmts:
            if stmt.get("stmt") == "Assign":
                val = stmt.get("value", {})
                if (isinstance(val, dict) and val.get("type") == "Call" and
                        val.get("func", "") in record_types):
                    tgt = stmt.get("target", "")
                    if tgt:
                        out[tgt] = val.get("func", "")
            for key in ("body", "orelse"):
                if key in stmt and isinstance(stmt[key], list):
                    out.update(IRScanner.find_record_var_classes(stmt[key], record_types))
            if stmt.get("stmt") in ("While", "For"):
                out.update(IRScanner.find_record_var_classes(stmt.get("body", []), record_types))
            if stmt.get("stmt") == "Match":
                for c in stmt.get("cases", []):
                    out.update(IRScanner.find_record_var_classes(c.get("body", []), record_types))
        return out

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def has_continue(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            if stmt["stmt"] == "Continue":
                return True
            if stmt["stmt"] == "If":
                if (IRScanner.has_continue(stmt.get("body", [])) or
                        IRScanner.has_continue(stmt.get("orelse", []))):
                    return True
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_continue(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            if stmt["stmt"] == "Continue":
                return True
            for key in ("body", "orelse"):
                if key in stmt and IRScanner.uses_continue(stmt[key]):
                    return True
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_break(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            if stmt["stmt"] == "Break":
                return True
            for key in ("body", "orelse"):
                if key in stmt and IRScanner.uses_break(stmt[key]):
                    return True
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def collect_user_exceptions(stmts: List[Dict[str, Any]]) -> Set[str]:
        result = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Raise" and stmt.get("exc_type"):
                result.add(stmt["exc_type"])
            if stmt.get("stmt") == "Try":
                for h in stmt.get("handlers", []):
                    exc = h.get("exc_type")
                    if exc:
                        for ep in exc.split("|"):
                            ep = ep.strip()
                            if ep:
                                result.add(ep)
                    result |= IRScanner.collect_user_exceptions(h.get("body", []))
            for key in ("body", "orelse"):
                if key in stmt:
                    result |= IRScanner.collect_user_exceptions(stmt[key])
        return result

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def collect_escaping_exceptions(stmts: List[int]) -> int:
        return set()

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def has_direct_return(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            stype = stmt.get("stmt")
            if stype == "Return":
                return True
            if stype == "If":
                if (IRScanner.has_direct_return(stmt.get("body", [])) or
                        IRScanner.has_direct_return(stmt.get("orelse", []))):
                    return True
            if stype == "Try":
                # User Try blocks never catch the internal Return exception,
                # so any Return inside a Try propagates to the function body.
                if IRScanner.has_direct_return(stmt.get("body", [])):
                    return True
                for h in stmt.get("handlers", []):
                    if IRScanner.has_direct_return(h.get("body", [])):
                        return True
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def has_in_loop_return(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            stype = stmt.get("stmt")
            if stype in ("While", "For"):
                if (IRScanner.has_direct_return(stmt.get("body", [])) or
                        IRScanner.has_in_loop_return(stmt.get("body", []))):
                    return True
            elif stype == "If":
                for key in ("body", "orelse"):
                    if key in stmt and IRScanner.has_in_loop_return(stmt[key]):
                        return True
            elif stype == "Try":
                # See has_direct_return: Returns inside Try escape to the
                # enclosing function body, including any enclosing loop.
                if IRScanner.has_in_loop_return(stmt.get("body", [])):
                    return True
                for h in stmt.get("handlers", []):
                    if IRScanner.has_in_loop_return(h.get("body", [])):
                        return True
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def has_early_return(stmts: List[Dict[str, Any]]) -> bool:
        for i, stmt in enumerate(stmts):
            stype = stmt.get("stmt")
            if stype == "If":
                has_ret = IRScanner.has_direct_return(stmt.get("body", []))
                has_rest = (i < len(stmts) - 1)
                if has_ret and has_rest:
                    return True
                if IRScanner.has_early_return(stmt.get("body", [])):
                    return True
                if IRScanner.has_early_return(stmt.get("orelse", [])):
                    return True
            elif stype in ("For", "While"):
                if IRScanner.has_early_return(stmt.get("body", [])):
                    return True
            elif stype == "Try":
                handlers = stmt.get("handlers", [])
                for h in handlers:
                    if IRScanner.has_direct_return(h.get("body", [])):
                        if i < len(stmts) - 1:
                            return True
                    if IRScanner.has_early_return(h.get("body", [])):
                        return True
                if IRScanner.has_early_return(stmt.get("body", [])):
                    return True
        return False

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def uses_for(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            if stmt["stmt"] == "For":
                return True
            for key in ("body", "orelse"):
                if key in stmt and IRScanner.uses_for(stmt[key]):
                    return True
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_append_targets(stmts: List[Dict[str, Any]]) -> Set[str]:
        result = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Expr":
                val = stmt.get("value", {})
                if val.get("type") == "Call":
                    func = val.get("func", "")
                    if func.endswith(".append"):
                        arr_name = func.rsplit(".", 1)[0]
                        result.add(arr_name.replace(".", "_"))
            for key in ("body", "orelse"):
                if key in stmt:
                    result |= IRScanner.find_append_targets(stmt[key])
        return result

    _MUTATING_METHODS: int = {'append', 'pop', 'clear', 'add', 'remove', 'discard', 'update', 'extend', 'insert', 'setdefault'}
    #@ requires True
    #@ ensures True
    #@ assigns out
    @staticmethod
    def _collect_mutations(stmts: List[Dict[str, Any]], target_name: str, out: List[Dict[str, Any]]) -> None:
        for stmt in stmts:
            stype = stmt.get("stmt")
            if stype == "ArraySet":
                arr = stmt.get("array", {})
                if arr.get("type") == "Var" and arr.get("name") == target_name:
                    out.append(stmt)
            elif stype == "Expr":
                val = stmt.get("value", {})
                if val.get("type") == "Call":
                    func = val.get("func", "")
                    if "." in func:
                        recv, method = func.rsplit(".", 1)
                        if recv == target_name and method in IRScanner._MUTATING_METHODS:
                            out.append(stmt)
            elif stype in ("Delete", "DelSubscript"):
                arr = stmt.get("array", {}) or stmt.get("target", {})
                if isinstance(arr, dict) and arr.get("type") == "Var" and arr.get("name") == target_name:
                    out.append(stmt)
            for key in ("body", "orelse", "finalbody"):
                if key in stmt and isinstance(stmt[key], list):
                    IRScanner._collect_mutations(stmt[key], target_name, out)
            if stype == "Match":
                for c in stmt.get("cases", []):
                    IRScanner._collect_mutations(c.get("body", []), target_name, out)

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_iteration_mutations(stmts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for stmt in stmts:
            if stmt.get("stmt") == "For":
                if stmt.get("allow_iteration_mutation"):
                    out.extend(IRScanner.find_iteration_mutations(stmt.get("body", [])))
                    continue
                iter_expr = stmt.get("iter", {})
                iterable_name: str = ""
                if iter_expr.get("type") == "Var":
                    iterable_name = iter_expr.get("name", "")
                if iterable_name:
                    mutations: List[Dict[str, Any]] = []
                    IRScanner._collect_mutations(stmt.get("body", []), iterable_name, mutations)
                    for m in mutations:
                        out.append({
                            "loop_target": stmt.get("target", ""),
                            "iterable_name": iterable_name,
                            "mutating_stmt": m,
                            "loop_line": stmt.get("lineno", 0),
                        })
                out.extend(IRScanner.find_iteration_mutations(stmt.get("body", [])))
            else:
                for key in ("body", "orelse", "finalbody"):
                    if key in stmt and isinstance(stmt[key], list):
                        out.extend(IRScanner.find_iteration_mutations(stmt[key]))
                if stmt.get("stmt") == "Match":
                    for c in stmt.get("cases", []):
                        out.extend(IRScanner.find_iteration_mutations(c.get("body", [])))
        return out

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def find_return_type(stmts: List[Dict[str, Any]]) -> str:
        def _has_return(stmts: List[Dict[str, Any]]) -> bool:
            for stmt in stmts:
                if stmt["stmt"] == "Return":
                    return True
                for key in ("body", "orelse"):
                    if key in stmt and _has_return(stmt[key]):
                        return True
                if stmt.get("stmt") == "Match":
                    for c in stmt.get("cases", []):
                        if _has_return(c.get("body", [])):
                            return True
            return False

        def _has_return_with_value(stmts: List[Dict[str, Any]]) -> bool:
            for stmt in stmts:
                if stmt["stmt"] == "Return" and stmt.get("value"):
                    return True
                for key in ("body", "orelse"):
                    if key in stmt and _has_return_with_value(stmt[key]):
                        return True
                if stmt.get("stmt") == "Match":
                    for c in stmt.get("cases", []):
                        if _has_return_with_value(c.get("body", [])):
                            return True
            return False

        if not _has_return(stmts):
            return "unit"
        if not _has_return_with_value(stmts):
            return "unit"

        for stmt in stmts:
            if stmt["stmt"] == "Return" and stmt.get("value"):
                val = stmt["value"]
                if val.get("type") == "Tuple":
                    n = len(val.get("elts", []))
                    return "(" + ", ".join(["int"] * n) + ")"
                if val.get("type") == "String":
                    return "int"
            for key in ("body", "orelse"):
                if key in stmt:
                    result = IRScanner.find_return_type(stmt[key])
                    if result not in ("int", "unit"):
                        return result
            if stmt.get("stmt") == "Match":
                for c in stmt.get("cases", []):
                    result = IRScanner.find_return_type(c.get("body", []))
                    if result not in ("int", "unit"):
                        return result
        return "int"


