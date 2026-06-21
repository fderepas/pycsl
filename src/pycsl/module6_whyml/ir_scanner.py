from __future__ import annotations

from typing import Dict, Any, Set, List, Tuple


class IRScanner:
    """Stateless recursive walkers over the IR dict tree."""

    @staticmethod
    def uses_arrayset(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            if stmt.get("stmt") == "ArraySet":
                return True
            for key in ("body", "orelse"):
                if key in stmt and IRScanner.uses_arrayset(stmt[key]):
                    return True
        return False

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

    @staticmethod
    def find_array_and_dict_vars(stmts: List[Dict[str, Any]]) -> Tuple[Set[str], Set[str]]:
        array_vars = set()
        dict_vars = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Assign":
                val = stmt.get("value", {})
                target = stmt.get("target", "")
                if isinstance(val, dict):
                    vt = val.get("type", "")
                    if vt == "Call" and val.get("func") in (
                            "list", "sorted", "bytes", "bytearray"):
                        # `sorted` is emitted as an abstract val returning
                        # `array int`; track its target as array-typed so
                        # the pre-decl path skips the `ref 0` declaration.
                        # (collections-plan: `deque()` lowers to an empty ArrayLit
                        # in Module5, so it is caught by the ArrayLit arm below.)
                        # 07-1321 S1: `bytes(...)`/`bytearray(...)` lower to faithful
                        # `array int` constructors (`bytes_new`/`bytearray_empty`), so a
                        # local bound to one is array-typed too (else `b[0]` would use the
                        # abstract int subscript and lose the element-equality contract).
                        array_vars.add(target)
                    elif (vt == "Call" and val.get("func", "").rsplit(".", 1)[-1]
                            in ("encode", "ljust", "rjust", "zfill")):
                        # 1009.md R2: bytes-producing methods lower to an abstract
                        # `val …_<n> : array int` (see `_call_bytes_methods`), so a
                        # local bound to one (`padded = name.encode(...).ljust(30,…)`)
                        # is array-typed — skip the `ref 0` pre-decl that would make
                        # `padded := (ljust_… …)` an int/array mismatch.
                        array_vars.add(target)
                    elif vt in ("ListLit", "ArrayLit"):
                        array_vars.add(target)
                    elif vt == "ListComp":
                        array_vars.add(target)
                    elif vt == "DictLit":
                        dict_vars.add(target)
                    elif vt == "Call" and val.get("func") in (
                            "dict", "defaultdict", "Counter", "OrderedDict"):
                        # collections-plan: the dict-family collections reduce to
                        # the `map int (option int)` model. `defaultdict(int)`'s
                        # missing-key default IS the model's missing→0; `Counter`
                        # is a count map; `OrderedDict` is a plain dict (order not
                        # modelled). The factory/iterable arg is dropped (empty).
                        dict_vars.add(target)
                    elif vt == "SetLit" or (vt == "Call" and val.get("func") in ("set", "frozenset")):
                        dict_vars.add(target)
                    elif vt == "SliceAccess":
                        array_vars.add(target)
                    elif (vt == "BinOp" and val.get("op") == "*"
                          and isinstance(val.get("left"), dict)
                          and val["left"].get("type") == "ArrayLit"):
                        # Python `[default] * N` allocates an N-element
                        # array via Module6's `_handle_binop` BinOp(`*`)
                        # arm — track the target as an array local.
                        array_vars.add(target)
            for key in ("body", "orelse"):
                if key in stmt:
                    a, d = IRScanner.find_array_and_dict_vars(stmt[key])
                    array_vars |= a
                    dict_vars |= d
            if stmt.get("stmt") == "While":
                a, d = IRScanner.find_array_and_dict_vars(stmt.get("body", []))
                array_vars |= a
                dict_vars |= d
            if stmt.get("stmt") == "For":
                a, d = IRScanner.find_array_and_dict_vars(stmt.get("body", []))
                array_vars |= a
                dict_vars |= d
            if stmt.get("stmt") == "Try":
                a, d = IRScanner.find_array_and_dict_vars(stmt.get("body", []))
                array_vars |= a
                dict_vars |= d
                for h in stmt.get("handlers", []):
                    a, d = IRScanner.find_array_and_dict_vars(h.get("body", []))
                    array_vars |= a
                    dict_vars |= d
        return array_vars, dict_vars

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

    @staticmethod
    def uses_continue(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            if stmt["stmt"] == "Continue":
                return True
            for key in ("body", "orelse"):
                if key in stmt and IRScanner.uses_continue(stmt[key]):
                    return True
        return False

    @staticmethod
    def uses_break(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            if stmt["stmt"] == "Break":
                return True
            for key in ("body", "orelse"):
                if key in stmt and IRScanner.uses_break(stmt[key]):
                    return True
        return False

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

    @staticmethod
    def collect_escaping_exceptions(stmts: List[Dict[str, Any]]) -> Set[str]:
        raised = set()
        caught = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Raise" and stmt.get("exc_type"):
                raised.add(stmt["exc_type"])
            if stmt.get("stmt") == "Try":
                inner_raised = IRScanner.collect_escaping_exceptions(stmt.get("body", []))
                handler_bases: Set[str] = set()
                for h in stmt.get("handlers", []):
                    exc = h.get("exc_type")
                    if exc:
                        for ep in exc.split("|"):
                            ep = ep.strip()
                            if ep:
                                handler_bases.add(ep)
                    raised |= IRScanner.collect_escaping_exceptions(h.get("body", []))
                # A handler `except B` catches B and every modelled subclass
                # of B (hierarchy-aware), so a raised `FileNotFoundError`
                # under `except OSError:` does NOT escape.
                from exception_model import handler_catches
                still_escapes = {
                    e for e in inner_raised
                    if not any(handler_catches(b, e) for b in handler_bases)
                }
                raised |= still_escapes
                continue
            for key in ("body", "orelse"):
                if key in stmt:
                    raised |= IRScanner.collect_escaping_exceptions(stmt[key])
        return raised

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

    @staticmethod
    def uses_for(stmts: List[Dict[str, Any]]) -> bool:
        for stmt in stmts:
            if stmt["stmt"] == "For":
                return True
            for key in ("body", "orelse"):
                if key in stmt and IRScanner.uses_for(stmt[key]):
                    return True
        return False

    @staticmethod
    def uses_subscript(obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "Subscript":
                return True
            return any(IRScanner.uses_subscript(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_subscript(item) for item in obj)
        return False

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

    @staticmethod
    def is_recursive(name: str, obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "Call" and obj.get("func") == name:
                return True
            return any(IRScanner.is_recursive(name, v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.is_recursive(name, item) for item in obj)
        return False

    @staticmethod
    def uses_string(obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "String":
                return True
            return any(IRScanner.uses_string(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_string(item) for item in obj)
        return False

    @staticmethod
    def uses_sum(obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "Sum":
                return True
            return any(IRScanner.uses_sum(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_sum(item) for item in obj)
        return False

    @staticmethod
    def uses_set_card(obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "SetCard":
                return True
            return any(IRScanner.uses_set_card(v) for v in obj.values())
        if isinstance(obj, list):
            return any(IRScanner.uses_set_card(item) for item in obj)
        return False

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

    # ---- UB-7.1 — mutation during iteration ------------------------
    # Mutating method names (dotted-call receivers that imply mutation
    # of the receiver collection). Reads do not appear here; only writes.
    _MUTATING_METHODS: Set[str] = {
        "append", "pop", "clear", "add", "remove", "discard",
        "update", "extend", "insert", "setdefault",
    }

    @staticmethod
    def _collect_mutations(stmts: List[Dict[str, Any]],
                            target_name: str,
                            out: List[Dict[str, Any]]) -> None:
        """Walk ``stmts`` and append entries to ``out`` for every
        statement that mutates the collection ``target_name``. Reaches
        into ``body`` / ``orelse`` recursively. Used by
        ``find_iteration_mutations``."""
        for stmt in stmts:
            stype = stmt.get("stmt")
            # `target[i] = v` — array/dict element write.
            if stype == "ArraySet":
                arr = stmt.get("array", {})
                if arr.get("type") == "Var" and arr.get("name") == target_name:
                    out.append(stmt)
            # `t.append(x)` / `t.pop()` / ... — dotted call as a statement.
            elif stype == "Expr":
                val = stmt.get("value", {})
                if val.get("type") == "Call":
                    func = val.get("func", "")
                    if "." in func:
                        recv, method = func.rsplit(".", 1)
                        if recv == target_name and method in IRScanner._MUTATING_METHODS:
                            out.append(stmt)
            # `del t[i]` — Python-AST `Delete`. Module 5 may emit this
            # as either a "Delete" stmt or via a synthesized helper;
            # cover both shapes conservatively.
            elif stype in ("Delete", "DelSubscript"):
                arr = stmt.get("array", {}) or stmt.get("target", {})
                if isinstance(arr, dict) and arr.get("type") == "Var" and arr.get("name") == target_name:
                    out.append(stmt)
            # Recurse into nested blocks. Skip nested `For` over the
            # same target — the inner loop has its own check.
            for key in ("body", "orelse", "finalbody"):
                if key in stmt and isinstance(stmt[key], list):
                    IRScanner._collect_mutations(stmt[key], target_name, out)
            if stype == "Match":
                for c in stmt.get("cases", []):
                    IRScanner._collect_mutations(c.get("body", []), target_name, out)

    @staticmethod
    def find_iteration_mutations(stmts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return a list of ``{loop_target, iterable_name, mutating_stmt}``
        records for every UB-7.1 violation found in ``stmts``.

        A violation is: a ``For`` loop whose ``iter`` is a `Var(name=C)`,
        and somewhere in its ``body`` a statement mutates ``C`` (via
        `C[i] = v`, `C.append(...)`, `C.pop(...)`, `del C[i]`, etc.).

        The detector respects the per-loop opt-in marker
        ``ir.get("allow_iteration_mutation", False)`` (set by Module 5
        from the ``#@ allow_iteration_mutation`` parser directive).
        """
        out: List[Dict[str, Any]] = []
        for stmt in stmts:
            if stmt.get("stmt") == "For":
                if stmt.get("allow_iteration_mutation"):
                    # Recurse into body for nested loops, but skip the
                    # check on this one.
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
                # Recurse into the body (handles nested for-loops).
                out.extend(IRScanner.find_iteration_mutations(stmt.get("body", [])))
            else:
                for key in ("body", "orelse", "finalbody"):
                    if key in stmt and isinstance(stmt[key], list):
                        out.extend(IRScanner.find_iteration_mutations(stmt[key]))
                if stmt.get("stmt") == "Match":
                    for c in stmt.get("cases", []):
                        out.extend(IRScanner.find_iteration_mutations(c.get("body", [])))
        return out

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
