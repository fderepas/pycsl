import json
import unicodedata
from typing import Dict, Any, Optional, Set, List, Tuple

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
    def find_array_and_dict_vars(stmts: List[Dict[str, Any]]) -> Tuple[Set[str], Set[str]]:
        array_vars = set()
        dict_vars = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Assign":
                val = stmt.get("value", {})
                target = stmt.get("target", "")
                if isinstance(val, dict):
                    vt = val.get("type", "")
                    if vt == "Call" and val.get("func") in ("list",):
                        array_vars.add(target)
                    elif vt in ("ListLit", "ArrayLit"):
                        array_vars.add(target)
                    elif vt == "ListComp":
                        array_vars.add(target)
                    elif vt == "DictLit":
                        dict_vars.add(target)
                    elif vt == "Call" and val.get("func") in ("dict",):
                        dict_vars.add(target)
                    elif vt == "SetLit" or (vt == "Call" and val.get("func") in ("set", "frozenset")):
                        dict_vars.add(target)
                    elif vt == "SliceAccess":
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
                for h in stmt.get("handlers", []):
                    exc = h.get("exc_type")
                    if exc:
                        for ep in exc.split("|"):
                            ep = ep.strip()
                            if ep:
                                caught.add(ep)
                    raised |= IRScanner.collect_escaping_exceptions(h.get("body", []))
                raised |= (inner_raised - caught)
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
    def uses_divmod(stmts: Any) -> bool:
        def _check(obj):
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

    @staticmethod
    def find_return_type(stmts: List[Dict[str, Any]]) -> str:
        def _has_return(stmts):
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

        def _has_return_with_value(stmts):
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


class Module6_WhyMLTranspiler:
    """Reads the JSON IR and transpiles it into valid WhyML (.mlw) syntax."""
    
    def __init__(self, json_ir: str, memory_model: str = "hoare") -> None:
        self.ir = json.loads(json_ir)
        self.memory_model = memory_model   # "hoare" | "typed" | "store"
        self._array2d_params: set = set()  # set during per-function transpilation
        self._in_spec = False              # True when emitting contracts (no div-by-zero VCs)
        self._bounded_int = None           # Current function's bounded_int size (or None)
        self._abstract_ops: dict = {}      # Abstract val declarations: name → full decl string
        self._current_params: set = set()  # Parameters of current function being transpiled
        self._array_locals: set = set()    # Local array variables (no ! deref needed)
        self._dict_locals: set = set()     # Local dict variables (not real arrays)
        self._record_types: dict = {}      # class_name_lower → {fields: [...], defaults: {...}}
        self._record_locals: set = set()   # Local variables holding record instances
        self._shared_var_names: set = set()  # Module-level shared variable names (concurrent model)
        self._havoc_counter: int = 0         # Counter for unique havoc variable names

    @property
    def _heap_var(self) -> str:
        """Returns the name of the mutable heap variable for the current model."""
        if self.memory_model == "typed":
            return "int_mem"
        elif self.memory_model == "store":
            return "store"
        raise ValueError(f"No heap variable in Hoare model")

    # Maps Python/IR operators to WhyML operators
    _OP_MAP: Dict[str, str] = {
        "==": "=",    # WhyML equality is single =
        "!=": "<>",   # WhyML inequality is <>
        "==>": "->",  # WhyML implication
        "<==>": "<->",  # WhyML equivalence
        "and": "&&",
        "or": "||",
        "not": "not",
        "div": "div",
        "//": "div",  # contract floor-division maps to WhyML div
        "/": "div",   # contract `/` maps to WhyML `div` (Euclidean integer division)
        "%": "mod",   # WhyML modulo from int.EuclideanDivision
    }

    # Dispatch table for _expr_to_whyml: maps IR type string → method name.
    # All dispatched methods use the uniform quad signature (expr, local_refs, invariant_ctx, subst).
    # Non-standard-signature handlers (Var, FieldGet) are called explicitly before this dict.
    _EXPR_DISPATCH: Dict[str, str] = {
        "BinOp":        "_handle_binop",
        "Call":         "_handle_call_expr",
        "Subscript":    "_handle_subscript",
        "Attribute":    "_handle_attribute_expr",
        "FString":      "_handle_fstring_expr",
        "UnaryOp":      "_handle_unaryop_expr",
        "Old":          "_handle_old_expr",
        "At":           "_handle_at_expr",
        "IfExpr":       "_handle_ifexpr_expr",
        "NamedExpr":    "_handle_named_expr_expr",
        "SliceAccess":  "_handle_slice_access_expr",
        "ArrayLen":     "_handle_arraylen_expr",
        "Valid":        "_handle_valid_expr",
        "Separated":    "_handle_separated_expr",
        "Length2D":     "_handle_length2d_expr",
        "Valid2D":      "_handle_valid2d_expr",
        "IsSorted":     "_handle_issorted_expr",
        "Sum":          "_handle_sum_node_expr",
        "Lambda":       "_handle_lambda_expr",
        "SetLit":       "_handle_setlit_expr",
    }

    # WhyML reserved keywords that cannot be used as identifiers
    _WHYML_RESERVED = {
        "at", "any", "diverges", "val", "let", "in", "if", "then", "else",
        "while", "do", "done", "for", "to", "begin", "end", "match", "with",
        "try", "raise", "exception", "type", "use", "module", "theory",
        "import", "export", "clone", "goal", "lemma", "axiom", "predicate",
        "function", "constant", "mutable", "ghost", "invariant", "variant",
        "requires", "ensures", "returns", "raises", "reads", "writes",
        "assert", "assume", "check", "absurd", "true", "false", "not",
        "old", "ref", "abstract", "private", "model", "range",
        "float", "by", "so", "pure", "alias", "label", "epsilon",
        "exists", "forall", "rec", "and", "or", "mod", "div", "result",
    }

    @staticmethod
    def _whyml_ident(name: str) -> str:
        """WhyML identifiers must start with a lowercase letter, contain no dots, 
        and not be reserved keywords."""
        # Underscore alone is a wildcard in WhyML — rename it
        if name == "_":
            return "py_underscore"
        # Replace dots with underscores for valid WhyML identifiers
        name = name.replace(".", "_")
        # Sanitize non-ASCII characters to ASCII equivalents
        sanitized = []
        for ch in name:
            if ord(ch) > 127:
                decomp = unicodedata.normalize('NFD', ch)
                ascii_ch = ''.join(c for c in decomp if ord(c) < 128)
                sanitized.append(ascii_ch if ascii_ch else f"u{ord(ch)}")
            else:
                sanitized.append(ch)
        name = ''.join(sanitized)
        if name and name[0].isupper():
            name = name[0].lower() + name[1:]
        # Prefix reserved words to avoid conflicts
        if name in Module6_WhyMLTranspiler._WHYML_RESERVED:
            name = f"py_{name}"
        return name

    def _safe_mutex_name(self, mutex: str) -> str:
        """Convert a mutex expression (possibly 'locks[0]') to a valid WhyML identifier."""
        return self._whyml_ident(mutex.replace("[", "_").replace("]", "").replace(".", "_"))

    def _op(self, op: str) -> str:
        """Translates operators; defaults to the same string (e.g., +, -, >, <)."""
        return self._OP_MAP.get(op, op)

    def _add_abstract_op(self, decl: str) -> None:
        """Register an abstract val declaration, deduplicating by name+arity.
        Different arities for the same function get unique names (e.g., stmt_get, stmt_get_2)."""
        parts = decl.split()
        if len(parts) >= 2 and parts[0] == "val":
            if parts[1] == "constant":
                name = parts[2] if len(parts) > 2 else decl
            else:
                name = parts[1]
        else:
            name = decl
        if name not in self._abstract_ops:
            self._abstract_ops[name] = decl
        else:
            # If same name, same declaration → skip
            if self._abstract_ops[name] == decl:
                return
            # Different arity → store under name_N key
            # Count params in existing and new
            existing = self._abstract_ops[name]
            existing_params = existing.count("(x")
            new_params = decl.count("(x")
            if new_params != existing_params:
                # Store under arity-suffixed key
                arity_key = f"{name}_{new_params}"
                self._abstract_ops[arity_key] = decl
            else:
                # Same arity but different declaration — keep longer
                if len(decl) > len(existing):
                    self._abstract_ops[name] = decl

    def _to_bool(self, whyml_str: str, ir_expr: Dict[str, Any]) -> str:
        """Coerce a WhyML expression to bool if it might be int.
        Comparison operators and bool literals are already bool.
        Calls to isinstance_check, hasattr_check are already bool.
        Other expressions (int) need `<> 0` coercion."""
        t = ir_expr.get("type", "")
        op = ir_expr.get("op", "")
        # Already boolean: comparisons, not, bool literals, isinstance
        if t == "BinOp" and op in ("==", "!=", "<", ">", "<=", ">=", "in", "not in"):
            return whyml_str
        if t == "BinOp" and op in ("and", "or") and getattr(self, '_in_spec', False):
            # In spec context, and/or use && / || which are already bool
            return whyml_str
        if t == "UnaryOp" and op == "not":
            return whyml_str
        if t == "Bool":
            # In body context, Bool emits 1/0 but we need true/false for formulas
            if whyml_str == "1":
                return "true"
            if whyml_str == "0":
                return "false"
            return whyml_str
        if t == "Call" and ir_expr.get("func", "") in ("isinstance", "hasattr"):
            return whyml_str
        if t in ("Exists", "Forall", "Compare"):
            return whyml_str
        # Array locals can't be compared with <> 0; emit true (always allocated)
        if t == "Var":
            name = ir_expr.get("name", "")
            if name in getattr(self, '_array_locals', set()):
                return "true"
        # Coerce int → bool
        return f"({whyml_str} <> 0)"

    @staticmethod
    def _coerce_str_arg(whyml_str: str) -> str:
        """Convert a WhyML string literal to an int hash for abstract val arguments."""
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(hash(whyml_str) % 2147483647)
        return whyml_str

    def _coerce_to_int(self, whyml_str: str) -> str:
        """Coerce any non-int WhyML expression to int for abstract val arguments."""
        # String literals → int hash
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(hash(whyml_str) % 2147483647)
        # Array literals can't be passed where int is expected
        if whyml_str.startswith("(Array.make"):
            return "0"
        # Tuple literals (a, b, c) → hash to int
        if "," in whyml_str and whyml_str.startswith("(") and whyml_str.endswith(")"):
            return str(hash(whyml_str) % 2147483647)
        # Record self → convert to int via abstract op
        self_type = getattr(self, '_current_self_type', None)
        if whyml_str == "self" and self_type:
            conv_name = f"self_to_int_{self_type}"
            self._add_abstract_op(f"val {conv_name} (x: {self_type}) : int")
            return f"({conv_name} self)"
        return whyml_str


    def _match_pattern_cond(self, pat: Dict[str, Any], subject: str, local_refs: Set[str]) -> str:
        """Generate a WhyML boolean condition for a match pattern."""
        kind = pat.get("pattern", "Unknown")
        if kind == "Wildcard":
            return "true"
        elif kind == "Value":
            val = self._expr_to_whyml(pat["value"], local_refs)
            return f"({subject} = {val})"
        elif kind == "Capture":
            if pat.get("inner"):
                return self._match_pattern_cond(pat["inner"], subject, local_refs)
            return "true"
        elif kind == "Or":
            alts = [self._match_pattern_cond(a, subject, local_refs) for a in pat.get("alternatives", [])]
            return " || ".join(alts) if alts else "true"
        return "true"

    def _handle_binop(self, expr: Dict[str, Any], local_refs: Set[str],
                      invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        # [default] * size → Array.make size default
        if expr["op"] == "*" and expr["left"].get("type") == "ArrayLit":
            elts = expr["left"].get("elts", [])
            default_val = self._expr_to_whyml(elts[0], local_refs, invariant_ctx, subst) if elts else "0"
            size = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
            return f"(Array.make {size} {default_val})"
        left = self._expr_to_whyml(expr["left"], local_refs, invariant_ctx, subst)
        right = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
        op = self._op(expr["op"])
        # In body context, coerce string literals in comparisons to int
        if not self._in_spec and op in ("=", "<>"):
            left = self._coerce_str_arg(left)
            right = self._coerce_str_arg(right)
        if op == "div":
            if self._in_spec:
                return f"(div {left} {right})"
            return f"(pycsl_div {left} {right})"
        elif op == "mod":
            if self._in_spec:
                return f"(mod {left} {right})"
            return f"(pycsl_mod {left} {right})"
        elif op in ("&&", "||"):
            left_b = self._to_bool(left, expr["left"])
            right_b = self._to_bool(right, expr["right"])
            if getattr(self, '_in_spec', False):
                return f"({left_b} {op} {right_b})"
            else:
                # In body context, Python's and/or return int.
                # Use if-then-else to convert bool result back to int,
                # avoiding abstract vals that can't handle mixed bool/int args.
                return f"(if {left_b} {op} {right_b} then 1 else 0)"
        elif expr["op"] == "in":
            rhs = expr.get("right", {})
            if rhs.get("type") in ("Tuple", "ArrayLit", "SetLit"):
                elts = rhs.get("elts", [])
                if elts:
                    checks = []
                    for elt in elts:
                        elt_w = self._expr_to_whyml(elt, local_refs, invariant_ctx, subst)
                        checks.append(f"({self._coerce_str_arg(left)} = {self._coerce_str_arg(elt_w)})")
                    return f"({' || '.join(checks)})"
            self._add_abstract_op("val contains_check (x: int) (c: int) : bool")
            return f"(contains_check {self._coerce_str_arg(left)} {self._coerce_str_arg(right)})"
        elif expr["op"] == "not in":
            rhs = expr.get("right", {})
            if rhs.get("type") in ("Tuple", "ArrayLit", "SetLit"):
                elts = rhs.get("elts", [])
                if elts:
                    checks = []
                    for elt in elts:
                        elt_w = self._expr_to_whyml(elt, local_refs, invariant_ctx, subst)
                        checks.append(f"({self._coerce_str_arg(left)} = {self._coerce_str_arg(elt_w)})")
                    return f"(not ({' || '.join(checks)}))"
            self._add_abstract_op("val contains_check (x: int) (c: int) : bool")
            return f"(not (contains_check {self._coerce_str_arg(left)} {self._coerce_str_arg(right)}))"
        elif expr["op"] in ("&", "|", "^", "<<", ">>", "**"):
            # Bitwise/power ops: evaluate at compile time if both operands are literals
            left_ir = expr.get("left", {})
            right_ir = expr.get("right", {})
            if (left_ir.get("type") == "Number" and right_ir.get("type") == "Number"
                    and isinstance(left_ir.get("value"), int) and isinstance(right_ir.get("value"), int)):
                lv, rv = left_ir["value"], right_ir["value"]
                op_char = expr["op"]
                try:
                    if op_char == "&": result = lv & rv
                    elif op_char == "|": result = lv | rv
                    elif op_char == "^": result = lv ^ rv
                    elif op_char == "<<": result = lv << rv
                    elif op_char == ">>": result = lv >> rv
                    elif op_char == "**": result = lv ** rv
                    else: result = None
                    if result is not None:
                        return str(result)
                except (ValueError, OverflowError):
                    pass
            op_names = {"&": "bit_and", "|": "bit_or", "^": "bit_xor",
                        "<<": "bit_lshift", ">>": "bit_rshift", "**": "py_pow"}
            op_fn = op_names[expr["op"]]
            self._add_abstract_op(f"val {op_fn} (x: int) (y: int) : int")
            return f"({op_fn} {left} {right})"
        elif expr["op"] == "?":
            self._add_abstract_op("val unknown_op (x: int) (y: int) : int")
            return f"(unknown_op {left} {right})"
        return f"({left} {op} {right})"

    def _handle_len_call(self, expr: Dict[str, Any], args: List[str]) -> str:
        """Handle len(x): constant fold literals, array length in hoare model, or abstract."""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        atype = arg_ir.get("type", "")
        if atype == "String" and isinstance(arg_ir.get("value"), str):
            return str(len(arg_ir["value"]))
        if atype == "Tuple":
            return str(len(arg_ir.get("elts", [])))
        if atype in ("ArrayLit", "SetLit"):
            return str(len(arg_ir.get("elts", [])))
        if atype == "DictLit":
            return str(len(arg_ir.get("keys", [])))
        if atype == "Var":
            vname = arg_ir.get("name", "")
            known = getattr(self, "_known_collection_sizes", {})
            if vname in known:
                return str(known[vname])
        if self.memory_model in ("hoare", "concurrent"):
            var_name = arg_ir.get("name", "") if atype == "Var" else ""
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict and var_name:
                if getattr(self, "_current_symbol_table", {}).get(var_name) in ("list", "dict"):
                    is_array = True
            if is_array:
                return f"(length {args[0]})"
            self._add_abstract_op("val iter_length (x: int) : int")
            return f"(iter_length {args[0]})"
        return f"{args[0].lstrip('!')}_len"

    def _handle_join_call(self, expr: Dict[str, Any], args: List[str]) -> str:
        """Handle str.join(iterable): pick join_array for arrays, join_1 otherwise."""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        var_name = arg_ir.get("name", "") if arg_ir.get("type") == "Var" else ""
        is_array = (var_name in getattr(self, "_array_locals", set()) or
                    var_name in getattr(self, "_current_array1d_params", set()))
        if not is_array and var_name:
            if getattr(self, "_current_symbol_table", {}).get(var_name) in ("list", "dict"):
                is_array = True
        if not is_array:
            at = arg_ir.get("type", "")
            if at in ("ArrayLit", "ListLit", "ListComp"):
                is_array = True
            elif at == "BinOp" and arg_ir.get("op") == "*":
                for side in ("left", "right"):
                    if arg_ir.get(side, {}).get("type", "") in ("ArrayLit", "ListLit"):
                        is_array = True
        if not is_array and "Array.make" in args[0]:
            is_array = True
        if is_array:
            self._add_abstract_op("val join_array (a: array int) : int")
            return f"(join_array {args[0]})"
        self._add_abstract_op("val join_1 (x: int) : int")
        return f"(join_1 {args[0]})"

    def _handle_sum_call(self, expr: Dict[str, Any]) -> str:
        """Handle sum(iterable): constant fold if all elements are known literals."""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        if arg_ir.get("type") == "ArrayLit":
            elts = arg_ir.get("elts", [])
            if all(e.get("type") == "Number" and isinstance(e.get("value"), (int, float))
                   for e in elts):
                return str(sum(int(e["value"]) for e in elts))
        if arg_ir.get("type") == "Var":
            vname = arg_ir.get("name", "")
            known_elems = getattr(self, "_known_collection_elements", {})
            known_sizes = getattr(self, "_known_collection_sizes", {})
            if vname in known_elems and vname in known_sizes:
                size = known_sizes[vname]
                elems = known_elems[vname]
                if all(i in elems for i in range(size)):
                    return str(sum(int(elems[i]) for i in range(size)))
        return ""

    def _handle_dotted_call(self, func_name: str, args: List[str]) -> str:
        """Handle dotted method calls (x.method(...)): emit abstract val declaration."""
        safe_name = self._whyml_ident(func_name.replace(".", "_"))
        coerced = [self._coerce_to_int(a) for a in args]
        n = len(coerced)
        arity_name = f"{safe_name}_{n}"
        if n == 0:
            self._add_abstract_op(f"val {arity_name} () : int")
            return f"({arity_name} ())"
        params = " ".join(f"(x{i}: int)" for i in range(n))
        self._add_abstract_op(f"val {arity_name} {params} : int")
        return f"({arity_name} {' '.join(coerced)})"

    def _handle_call_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        func_name = expr["func"]
        args = [self._expr_to_whyml(a, local_refs, invariant_ctx, subst) for a in expr["args"]]

        if func_name == "len" and len(args) == 1:
            return self._handle_len_call(expr, args)
        if func_name in ("min", "max") and len(args) == 2:
            fn = "MinMax.min" if func_name == "min" else "MinMax.max"
            return f"({fn} {args[0]} {args[1]})"
        if func_name == "isinstance" and len(args) == 2:
            type_arg = self._coerce_to_int(args[1])
            self_type = getattr(self, '_current_self_type', None)
            if args[0] == "self" and self_type:
                op = f"isinstance_check_{self_type}"
                self._add_abstract_op(f"val {op} (x: {self_type}) (t: int) : bool")
            else:
                op = "isinstance_check"
                self._add_abstract_op("val isinstance_check (x: int) (t: int) : bool")
            return f"({op} {args[0]} {type_arg})"
        if func_name in ("set", "frozenset") and len(args) == 0:
            self._add_abstract_op("val set_empty () : int")
            return "(set_empty ())"
        if func_name == "dict" and len(args) == 0:
            self._add_abstract_op("val dict_new () : int")
            return "(dict_new ())"
        if func_name == "list" and len(args) <= 1:
            self._add_abstract_op("val list_new (x: int) : int")
            return f"(list_new {args[0] if args else '0'})"
        if func_name == "join" and len(args) == 1:
            return self._handle_join_call(expr, args)
        if func_name in ("str", "repr", "int", "bool", "abs") and len(args) == 1:
            arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
            if arg_ir.get("type") == "Number" and func_name in ("int", "abs"):
                val = arg_ir.get("value")
                if isinstance(val, (int, float)):
                    return str(int(val) if func_name == "int" else abs(int(val)))
            if func_name == "int":
                return args[0]
            wf = self._whyml_ident(func_name)
            self._add_abstract_op(f"val {wf}_conv (x: int) : int")
            return f"({wf}_conv {args[0]})"
        if func_name == "sum" and len(args) == 1:
            result = self._handle_sum_call(expr)
            if result:
                return result
        if func_name == "hasattr":
            a0 = args[0] if args else "0"
            a1 = self._coerce_str_arg(args[1] if len(args) > 1 else "0")
            self_type = getattr(self, '_current_self_type', None)
            if a0 == "self" and self_type:
                op = f"hasattr_check_{self_type}"
                self._add_abstract_op(f"val {op} (x: {self_type}) (a: int) : bool")
            else:
                op = "hasattr_check"
                self._add_abstract_op("val hasattr_check (x: int) (a: int) : bool")
            return f"({op} {a0} {a1})"
        if "." in func_name:
            return self._handle_dotted_call(func_name, args)
        if func_name in self._record_types and len(args) == 0:
            rec_info = self._record_types[func_name]
            field_inits = "; ".join(
                f"{fn} = {rec_info['defaults'].get(fn, 0)}" for fn in rec_info["fields"]
            )
            return f"{{ {field_inits} }}"
        coerced_args = [self._coerce_to_int(a) for a in args]
        safe_fn = self._whyml_ident(func_name)
        if (func_name not in local_refs
                and func_name not in getattr(self, '_current_params', set())
                and safe_fn not in getattr(self, '_module_func_names', set())):
            n = len(coerced_args)
            arity_fn = f"{safe_fn}_{n}"
            if n == 0:
                self._add_abstract_op(f"val {arity_fn} () : int")
            else:
                self._add_abstract_op(
                    f"val {arity_fn} {' '.join(f'(x{i}: int)' for i in range(n))} : int")
            return f"({arity_fn} {' '.join(coerced_args) if coerced_args else '()'})"
        return f"({safe_fn} {' '.join(coerced_args) if coerced_args else '()'})"

    def _handle_subscript(self, expr: Dict[str, Any], local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        value = expr["value"]
        index = self._expr_to_whyml(expr["index"], local_refs, invariant_ctx, subst)
        # \result[i] on a tuple return → let-destructure
        if value.get("type") == "Result" and hasattr(self, "_current_tuple_arity"):
            arity = self._current_tuple_arity
            if arity and arity > 0:
                try:
                    idx = int(index)
                except ValueError:
                    idx = -1
                if 0 <= idx < arity:
                    names = [f"_r{k}_" if k != idx else f"_r{idx}_" for k in range(arity)]
                    bindings = ", ".join(
                        names[k] if k == idx else "_" for k in range(arity)
                    )
                    return f"(let ({bindings}) = result in _r{idx}_)"
        # Detect 2D access: a[i][j] → Subscript(Subscript(Var(a), i), j)
        if (value.get("type") == "Subscript" and
                value.get("value", {}).get("type") == "Var" and
                value.get("value", {}).get("name") in getattr(self, "_array2d_params", set()) and
                value.get("value", {}).get("name") not in getattr(self, "_dict_locals", set())):
            base = value["value"]["name"]
            row = self._expr_to_whyml(value["index"], local_refs, invariant_ctx, subst)
            col = index
            return f"(get {base} {row} {col})"
        value_str = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            var_name = value.get("name", "") if value.get("type") == "Var" else ""
            index_ir = expr.get("index", {})
            if (var_name and index_ir.get("type") == "Number" and
                    isinstance(index_ir.get("value"), (int, float))):
                idx_val = int(index_ir["value"])
                known_elems = getattr(self, "_known_collection_elements", {})
                if var_name in known_elems and idx_val in known_elems[var_name]:
                    return known_elems[var_name][idx_val]
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict and var_name:
                st = getattr(self, "_current_symbol_table", {})
                if st.get(var_name) in ("list", "dict"):
                    is_array = True
            if is_array:
                return f"{value_str}[{index}]"
            else:
                self._add_abstract_op("val subscript_get (x: int) (i: int) : int")
                return f"(subscript_get {self._coerce_to_int(value_str)} {self._coerce_to_int(index)})"
        else:
            return f"(Map.get !{self._heap_var} ({value_str} + {index}))"

    def _handle_attribute_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                               invariant_ctx: bool, subst: Dict[str, str]) -> str:
        """Handle non-self attribute access: record field or abstract getter."""
        obj_ir = expr.get("object", {})
        attr = expr.get("attr", "unknown")
        if isinstance(obj_ir, str):
            return f"(get_{attr} {obj_ir})"
        if obj_ir.get("type") == "Var":
            var_name = obj_ir.get("name", "")
            if var_name in self._record_locals:
                return f"{self._whyml_ident(var_name)}.{attr}"
        obj_str = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
        self._add_abstract_op(f"val get_{attr} (x: int) : int")
        return f"(get_{attr} {obj_str})"

    def _handle_var_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                         subst: Optional[Dict[str, str]] = None) -> str:
        name = expr["name"]
        if subst and name in subst:
            name = subst[name]
        if name in getattr(self, '_array_locals', set()):
            return self._whyml_ident(name)
        if name in getattr(self, '_lambda_locals', set()):
            return self._whyml_ident(name)
        if name in getattr(self, '_record_locals', set()):
            return self._whyml_ident(name)
        if name in local_refs:
            return f"!{self._whyml_ident(name)}"
        if name in self._current_params or name == "self":
            return self._whyml_ident(name) if name != "self" else name
        if name in self._shared_var_names:
            return f"!{self._whyml_ident(name)}"
        safe = self._whyml_ident(name)
        self._add_abstract_op(f"val constant {safe} : int")
        return safe

    def _handle_field_get_expr(self, expr: Dict[str, Any], invariant_ctx: bool) -> str:
        if invariant_ctx:
            return expr['field']
        obj = expr['object']
        field = expr['field']
        safe_field = self._whyml_ident(field)
        decl_fields = getattr(self, '_all_record_fields', set())
        if field in decl_fields:
            return f"{obj}.{safe_field}"
        hash_field = hash(field) % 2147483647
        self_type = getattr(self, '_current_self_type', None)
        if obj == "self" and self_type:
            name = f"getattr_{self_type}"
            self._add_abstract_op(f"val {name} (x: {self_type}) (f: int) : int")
        else:
            name = "getattr_2"
            self._add_abstract_op(f"val {name} (x: int) (f: int) : int")
            obj = self._coerce_to_int(obj)
        return f"({name} {obj} {hash_field})"

    def _handle_fstring_expr(self, expr: Dict[str, Any], local_refs: Set[str],
                              invariant_ctx: bool, subst: Dict[str, str]) -> str:
        parts = expr.get("parts", [])
        if not parts:
            return "0"
        acc = self._coerce_str_arg(self._expr_to_whyml(parts[0], local_refs, invariant_ctx, subst))
        n_parts = len(parts)
        i_part = 1
        while i_part < n_parts:
            part = parts[i_part]
            p = self._coerce_str_arg(self._expr_to_whyml(part, local_refs, invariant_ctx, subst))
            self._add_abstract_op("val str_concat (x: int) (y: int) : int")
            acc = f"(str_concat {acc} {p})"
            i_part += 1
        return acc

    def _handle_unaryop_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        e = self._expr_to_whyml(expr["expr"], local_refs, invariant_ctx, subst)
        op = self._op(expr["op"])
        if op == "+":
            return e
        if op == "not":
            e = self._to_bool(e, expr["expr"])
        return f"({op} {e})"

    def _handle_old_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        inner = expr["expr"]
        if self.memory_model not in ("hoare", "concurrent") and inner.get("type") == "Subscript":
            value = self._expr_to_whyml(inner["value"], local_refs, invariant_ctx, subst)
            index = self._expr_to_whyml(inner["index"], local_refs, invariant_ctx, subst)
            return f"(Map.get (old !{self._heap_var}) ({value} + {index}))"
        e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
        return f"(old {e})"

    def _handle_at_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        label = expr["label"]
        inner = expr["expr"]
        if label == "PRE":
            e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
            return f"(old {e})"
        if inner.get("type") == "Subscript" and self.memory_model not in ("hoare", "concurrent"):
            value = self._expr_to_whyml(inner["value"], local_refs, invariant_ctx, subst)
            index = self._expr_to_whyml(inner["index"], local_refs, invariant_ctx, subst)
            return f"(Map.get ({self._heap_var} at {label}) ({value} + {index}))"
        e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
        return f"({e} at {label})"

    def _handle_ifexpr_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        test = self._expr_to_whyml(expr["test"], local_refs, invariant_ctx, subst)
        test = self._to_bool(test, expr["test"])
        body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
        orelse = self._expr_to_whyml(expr["orelse"], local_refs, invariant_ctx, subst)
        body = self._coerce_to_int(body)
        orelse = self._coerce_to_int(orelse)
        return f"(if {test} then {body} else {orelse})"

    def _handle_named_expr_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        target = self._whyml_ident(expr["target"])
        v = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx, subst)
        if target in local_refs:
            return f"(begin {target} := {v}; !{target} end)"
        local_refs.add(target)
        return f"(let {target} = ref {v} in !{target})"

    def _handle_slice_access_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        arr = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx, subst)
        sl = expr["slice"]
        lo = self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst) if sl.get("lower") else "0"
        hi = self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst) if sl.get("upper") else f"(Array.length {arr})"
        self._add_abstract_op("val array_slice (a: array int) (lo: int) (hi: int) : array int")
        return f"(array_slice {arr} {lo} {hi})"

    def _handle_arraylen_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self.memory_model in ("hoare", "concurrent"):
            var = expr['var']
            deref = "!" if var in local_refs else ""
            return f"(length {deref}{var})"
        return f"{expr['var']}_len"

    def _handle_valid_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        length = self._expr_to_whyml(expr["length"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"({length} >= 0 && {length} <= length {base})"
        return f"(valid !{self._heap_var} {base} {length})"

    def _handle_separated_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self.memory_model in ("hoare", "concurrent"):
            return "true"
        b1 = expr["base1"]
        l1 = self._expr_to_whyml(expr["len1"], local_refs, invariant_ctx, subst)
        b2 = expr["base2"]
        l2 = self._expr_to_whyml(expr["len2"], local_refs, invariant_ctx, subst)
        return f"(separated {b1} {l1} {b2} {l2})"

    def _handle_length2d_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        rows = self._expr_to_whyml(expr["rows"], local_refs, invariant_ctx, subst)
        cols = self._expr_to_whyml(expr["cols"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"({base}.rows = {rows} && {base}.columns = {cols})"
        return "true"

    def _handle_valid2d_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        row = self._expr_to_whyml(expr["row"], local_refs, invariant_ctx, subst)
        col = self._expr_to_whyml(expr["col"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"(valid_index {base} {row} {col})"
        return "true"

    def _handle_issorted_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        lo = self._expr_to_whyml(expr["lo"], local_refs, invariant_ctx, subst)
        hi = self._expr_to_whyml(expr["hi"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"(forall _si : int. {lo} <= _si /\\ _si < {hi} - 1 -> {base}[_si] <= {base}[_si + 1])"
        return "true"

    def _handle_sum_node_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = expr["base"]
        lo = self._expr_to_whyml(expr["lo"], local_refs, invariant_ctx, subst)
        hi = self._expr_to_whyml(expr["hi"], local_refs, invariant_ctx, subst)
        if self.memory_model in ("hoare", "concurrent"):
            return f"(pycsl_sum {base} {lo} {hi})"
        return "0"

    def _handle_lambda_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        params = expr.get("params", [])
        body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
        param_str = " ".join(f"({self._whyml_ident(p)}: int)" for p in params) if params else "()"
        return f"(fun {param_str} -> {body})"

    def _handle_setlit_expr(
        self,
        expr: Dict[str, Any],
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        elts = expr.get("elts", [])
        if not elts:
            self._add_abstract_op("val set_empty () : int")
            return "(set_empty ())"
        self._add_abstract_op("val set_new (x: int) : int")
        return "(set_new 0)"

    def _expr_to_whyml(self, expr: Dict[str, Any], local_refs: Set[str],
                       invariant_ctx: bool = False,
                       subst: Optional[Dict[str, str]] = None) -> str:
        """Recursively translates an expression dictionary into a WhyML string.
        When invariant_ctx is True, FieldGet emits bare field names (for record invariants).
        subst: optional name substitution dict applied before local_refs lookup (e.g. for-loop vars)."""
        if not expr: return ""
        t = expr["type"]

        # Simple literals and trivial 1-3-line branches — kept inline
        if t == "Number": return str(int(expr["value"]))
        if t == "String":
            escaped = expr["value"].replace('\\', '\\\\').replace('"', '\\"')
            return str(hash(f'"{escaped}"') % 2147483647)
        if t == "Result":   return "result"
        if t == "None":     return "0"
        if t == "ArrayLit": return "(Array.make 1024 0)"
        if t == "UnknownPyExpr": return "0"
        if t == "Slice":    return "0"
        if t == "OldField": return f"(old {expr['object']}.{expr['field']})"
        if t == "Starred":  return self._expr_to_whyml(expr.get("value", {}), local_refs, invariant_ctx, subst)
        if t == "Bool":
            if getattr(self, '_in_spec', False): return "true" if expr.get("value") else "false"
            return "1" if expr.get("value") else "0"
        if t == "Tuple":
            elts = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst) for e in expr.get("elts", [])]
            return f"({', '.join(elts)})"
        if t == "Forall":
            return f"(forall {expr['var']} : int. {self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)})"
        if t == "Exists":
            return f"(exists {expr['var']} : int. {self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)})"
        if t == "DictLit":
            self._add_abstract_op("val dict_new () : int")
            return "(dict_new ())"
        if t == "ListComp":
            self._add_abstract_op("val list_comp (x: int) : int")
            return "(list_comp 0)"
        if t == "SetComp":
            self._add_abstract_op("val set_comp (x: int) : int")
            return "(set_comp 0)"
        if t == "DictComp":
            self._add_abstract_op("val dict_comp (x: int) : int")
            return "(dict_comp 0)"

        # Non-standard-signature handlers — called explicitly
        if t == "Var":      return self._handle_var_expr(expr, local_refs, subst)
        if t == "FieldGet": return self._handle_field_get_expr(expr, invariant_ctx)

        # All other types via uniform-quad-signature dispatch
        handler = self._EXPR_DISPATCH.get(t)
        if handler:
            return getattr(self, handler)(expr, local_refs, invariant_ctx, subst)
        return ""

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

    def _handle_assign_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                             local_refs: Set[str], declared_refs: Set[str],
                             indent: str, in_loop: bool) -> str:
        target = stmt["target"]
        safe_target = self._whyml_ident(target)
        val_ir_raw = stmt.get("value", {})
        vt = val_ir_raw.get("type", "")
        self._track_collection_metadata(target, val_ir_raw)

        val = self._expr_to_whyml(stmt["value"], local_refs)
        # Tuple/Set literals can't be stored in int refs; use 0 as placeholder
        if vt in ("Tuple", "SetLit"):
            val = "0"

        # Assignment to a module-level shared variable (always a ref, never re-declared)
        if target in self._shared_var_names:
            code = f"{indent}{self._whyml_ident(target)} := {val}"
            if rest:
                code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            return code

        if target not in declared_refs:
            declared_refs.add(target)
            is_array_val = val.startswith("(Array.make") or val == "(Array.make 1024 0)"
            is_dict_val = val.startswith("(dict_new")
            is_lambda_val = (stmt.get("value", {}).get("type") == "Lambda")
            is_slice_val = (stmt.get("value", {}).get("type") == "SliceAccess")
            is_record_val = (stmt.get("value", {}).get("type") == "Call" and
                             stmt.get("value", {}).get("func", "") in self._record_types)
            if is_record_val:
                code = f"{indent}let {safe_target} = {val} in\n"
                self._record_locals.add(target)
            elif is_lambda_val:
                code = f"{indent}let {safe_target} = {val} in\n"
                self._lambda_locals.add(target)
            elif is_array_val or is_slice_val:
                code = f"{indent}let {safe_target} = {val} in\n"
                self._array_locals.add(target)
            elif is_dict_val:
                code = f"{indent}let {safe_target} = ref {val} in\n"
                self._dict_locals.add(target)
            elif self._bounded_int:
                code = f"{indent}let {safe_target} = ref ({val} : int{self._bounded_int}) in\n"
            else:
                val_ir = stmt.get("value", {})
                val_type = val_ir.get("type", "")
                is_bool_val = val_type in ("Compare", "BoolOp") or (
                    val_type == "UnaryOp" and val_ir.get("op") == "not") or (
                    val_type == "BinOp" and val_ir.get("op") in (
                        "==", "!=", "<", "<=", ">", ">=",
                        "is", "is not", "in", "not in"))
                if is_bool_val:
                    val = f"(if {val} then 1 else 0)"
                code = f"{indent}let {safe_target} = ref {val} in\n"
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if not rest_code:
                rest_code = f"{indent}()"
            return code + rest_code
        else:
            val_ir = stmt.get("value", {})
            val_type = val_ir.get("type", "")
            is_compare = val_type == "Compare"
            is_bool_op = val_type == "BoolOp"
            is_unary_not = val_type == "UnaryOp" and val_ir.get("op") == "not"
            is_cmp_binop = (val_type == "BinOp" and
                            val_ir.get("op") in ("==", "!=", "<", "<=", ">", ">=",
                                                  "is", "is not", "in", "not in"))
            if is_compare or is_bool_op or is_unary_not or is_cmp_binop:
                val = f"(if {val} then 1 else 0)"
            code = f"{indent}{safe_target} := {val}"
            if rest:
                code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            return code

    def _handle_while_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                            local_refs: Set[str], declared_refs: Set[str],
                            indent: str, in_loop: bool) -> str:
        test = self._expr_to_whyml(stmt["test"], local_refs)
        test = self._to_bool(test, stmt["test"])
        has_cont = IRScanner.has_continue(stmt.get("body", []))
        has_direct_ret = IRScanner.has_direct_return(stmt.get("body", []))

        loop_indent = (indent + "  ") if has_direct_ret else indent
        inner_indent = loop_indent + "  "

        body_str = self._stmts_to_whyml(
            stmt["body"], local_refs, declared_refs.copy(), inner_indent, in_loop=True)

        loop_code = f"{loop_indent}while {test} do\n"
        self._in_spec = True
        invariants_w = stmt.get("invariants", [])
        n_inv_w = len(invariants_w)
        i_inv_w = 0
        while i_inv_w < n_inv_w:
            inv = invariants_w[i_inv_w]
            inv_str = self._expr_to_whyml(inv, local_refs)
            loop_code += f"{inner_indent}invariant {{ {inv_str} }}\n"
            i_inv_w += 1
        variants_w = stmt.get("variants", [])
        n_var_w = len(variants_w)
        i_var_w = 0
        while i_var_w < n_var_w:
            var = variants_w[i_var_w]
            var_str = self._expr_to_whyml(var, local_refs)
            loop_code += f"{inner_indent}variant {{ {var_str} }}\n"
            i_var_w += 1
        self._in_spec = False
        if has_cont:
            loop_code += f"{inner_indent}try\n"
            loop_code += body_str + "\n"
            loop_code += f"{inner_indent}with PyCSL_Continue -> () end\n"
        else:
            loop_code += body_str + "\n"
        loop_code += f"{loop_indent}done"

        has_break = IRScanner.uses_break(stmt.get("body", []))
        if has_break:
            loop_code = (f"{loop_indent}try\n{loop_code}\n"
                         f"{loop_indent}with PyCSL_Break -> () end")

        if has_direct_ret and not in_loop:
            rest_code = self._stmts_to_whyml(
                rest, local_refs, declared_refs, indent + "  ", in_loop)
            inner = loop_code
            if rest_code:
                inner += ";\n" + rest_code
            return (f"{indent}try\n{inner}\n"
                    f"{indent}with Return r -> r end")

        code = loop_code
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    #@ requires 1 == 1
    #@ ensures \result[2] == 0 or \result[2] == 1
    #@ assigns self._abstract_ops
    def _classify_iterable(self, iter_ir: Dict[str, Any],
                            local_refs: Set[str], idx: str) -> Tuple[str, str, bool]:
        """Classify a For loop's iterable. Returns (len_expr, elem_expr, is_range)."""
        is_range = (iter_ir.get("type") == "Call" and
                    iter_ir.get("func") == "range" and
                    len(iter_ir.get("args", [])) == 1)
        if is_range:
            bound = self._expr_to_whyml(iter_ir["args"][0], local_refs)
            return bound, f"!{idx}", True
        if iter_ir.get("type") == "Var" and self.memory_model in ("hoare", "concurrent"):
            var_name = iter_ir.get("name", "")
            iter_expr = self._expr_to_whyml(iter_ir, local_refs)
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict:
                if getattr(self, "_current_symbol_table", {}).get(var_name) in ("list", "dict"):
                    is_array = True
            if is_array:
                return f"length {iter_expr}", f"{iter_expr}[!{idx}]", False
            self._add_abstract_op("val iter_length (x: int) : int")
            self._add_abstract_op("val iter_get (x: int) (i: int) : int")
            return f"(iter_length {iter_expr})", f"(iter_get {iter_expr} !{idx})", False
        if self.memory_model not in ("hoare", "concurrent"):
            iter_expr = self._expr_to_whyml(iter_ir, local_refs)
            return f"{iter_expr}_len", f"Map.get !{self._heap_var} ({iter_expr} + !{idx})", False
        iter_expr = self._coerce_to_int(self._expr_to_whyml(iter_ir, local_refs))
        self._add_abstract_op("val iter_length (x: int) : int")
        self._add_abstract_op("val iter_get (x: int) (i: int) : int")
        return f"(iter_length {iter_expr})", f"(iter_get {iter_expr} !{idx})", False

    def _handle_for_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                          local_refs: Set[str], declared_refs: Set[str],
                          indent: str, in_loop: bool) -> str:
        target = stmt["target"]
        safe_target = self._whyml_ident(target)
        iter_ir = stmt["iter"]
        idx = f"_idx_{safe_target}"
        has_direct_ret = IRScanner.has_direct_return(stmt.get("body", []))
        loop_indent = (indent + "  ") if has_direct_ret else indent
        inner_indent = loop_indent + "  "

        body_local = local_refs | {target}
        body_declared = declared_refs.copy() | {target}
        inner_body = self._stmts_to_whyml(
            stmt.get("body", []), body_local, body_declared, inner_indent, True)
        if not inner_body:
            inner_body = f"{inner_indent}()"

        has_cont = IRScanner.has_continue(stmt.get("body", []))
        len_expr, elem_expr, is_range = self._classify_iterable(iter_ir, local_refs, idx)

        while_parts = [f"{loop_indent}while !{idx} < {len_expr} do"]
        inv_subst = {target: idx} if is_range else None
        inv_refs = local_refs | {idx}
        self._in_spec = True
        invariants_f = stmt.get("invariants", [])
        n_inv_f = len(invariants_f)
        i_inv_f = 0
        while i_inv_f < n_inv_f:
            inv = invariants_f[i_inv_f]
            inv_str = self._expr_to_whyml(inv, inv_refs, subst=inv_subst)
            while_parts.append(f"{inner_indent}invariant {{ {inv_str} }}")
            i_inv_f += 1
        variants_f = stmt.get("variants", [])
        n_var_f = len(variants_f)
        i_var_f = 0
        while i_var_f < n_var_f:
            var_ir = variants_f[i_var_f]
            var_str = self._expr_to_whyml(var_ir, inv_refs, subst=inv_subst)
            while_parts.append(f"{inner_indent}variant {{ {var_str} }}")
            i_var_f += 1
        self._in_spec = False

        if has_cont:
            while_parts.append(f"{inner_indent}try")
            while_parts.append(f"{inner_indent}  let {safe_target} = ref ({elem_expr}) in")
            while_parts.append(inner_body)
            while_parts.append(f"{inner_indent}with PyCSL_Continue -> () end;")
        else:
            while_parts.append(f"{inner_indent}let {safe_target} = ref ({elem_expr}) in")
            while_parts.append(inner_body + ";")

        while_parts.append(f"{inner_indent}{idx} := !{idx} + 1")
        while_parts.append(f"{loop_indent}done")
        has_break = IRScanner.uses_break(stmt.get("body", []))
        while_code = "\n".join(while_parts)

        if has_break:
            while_code = (f"{loop_indent}try\n{while_code}\n"
                          f"{loop_indent}with PyCSL_Break -> () end")

        if self._bounded_int:
            idx_decl = f"{loop_indent}let {idx} = ref (0 : int{self._bounded_int}) in\n{while_code}"
        else:
            idx_decl = f"{loop_indent}let {idx} = ref 0 in\n{while_code}"

        if has_direct_ret and not getattr(self, '_has_early_ret', False) and not in_loop:
            rest_code = self._stmts_to_whyml(
                rest, local_refs, declared_refs, indent + "  ", in_loop)
            inner = idx_decl
            if rest_code:
                inner += ";\n" + rest_code
            func_ret = getattr(self, '_func_return_type', 'int')
            if func_ret == "unit":
                return (f"{indent}try\n{inner}\n"
                        f"{indent}with Return_void -> () end")
            return (f"{indent}try\n{inner}\n"
                    f"{indent}with Return r -> r end")
        else:
            full_code = idx_decl
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if rest_code:
                return full_code + ";\n" + rest_code
            return full_code

    def _handle_try_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                          local_refs: Set[str], declared_refs: Set[str],
                          indent: str, in_loop: bool) -> str:
        body_stmts = stmt.get("body", [])
        handlers = stmt.get("handlers", [])
        try_assigned = IRScanner.find_assigned_vars(body_stmts)
        n_ha = len(handlers)
        i_ha = 0
        while i_ha < n_ha:
            h = handlers[i_ha]
            try_assigned |= IRScanner.find_assigned_vars(h.get("body", []))
            i_ha += 1
        pre_decls = ""
        sorted_assigned = sorted(try_assigned)
        n_sa = len(sorted_assigned)
        i_sa = 0
        while i_sa < n_sa:
            var = sorted_assigned[i_sa]
            safe_var = self._whyml_ident(var)
            if safe_var not in declared_refs:
                pre_decls += f"{indent}let {safe_var} = ref 0 in\n"
                declared_refs.add(safe_var)
            i_sa += 1
        body_str = self._stmts_to_whyml(body_stmts, local_refs, declared_refs.copy(), indent + "  ", in_loop)
        if not body_str:
            body_str = f"{indent}  ()"
        if handlers:
            code = f"{pre_decls}{indent}try\n{body_str}\n"
            n_h = len(handlers)
            i_h = 0
            while i_h < n_h:
                h = handlers[i_h]
                exc = h.get("exc_type") or "PyCSL_Exception"
                exc_parts = exc.split("|") if "|" in exc else [exc]
                n_ep = len(exc_parts)
                i_ep = 0
                while i_ep < n_ep:
                    ep = exc_parts[i_ep].strip()
                    handler_body = self._stmts_to_whyml(
                        h.get("body", []), local_refs, declared_refs.copy(), indent + "  ", in_loop)
                    if not handler_body:
                        handler_body = f"{indent}  ()"
                    code += f"{indent}with {ep} -> \n{handler_body}\n"
                    i_ep += 1
                i_h += 1
            code += f"{indent}end"
        else:
            code = f"{pre_decls}{body_str}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_ghost_assign_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        target = stmt["target"]
        safe_target = self._whyml_ident(target)
        op = stmt.get("op", "=")
        val = self._expr_to_whyml(stmt["value"], local_refs | {target})
        if target not in declared_refs:
            declared_refs.add(target)
            local_refs.add(target)
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if not rest_code:
                rest_code = f"{indent}()"
            if self._bounded_int:
                return f"{indent}let ghost {safe_target} = ref ({val} : int{self._bounded_int}) in\n{rest_code}"
            return f"{indent}let ghost {safe_target} = ref {val} in\n{rest_code}"
        if op == "=":
            code = f"{indent}ghost {safe_target} := {val}"
        elif op == "+=":
            code = f"{indent}ghost {safe_target} := !{safe_target} + {val}"
        elif op == "-=":
            code = f"{indent}ghost {safe_target} := !{safe_target} - {val}"
        elif op == "*=":
            code = f"{indent}ghost {safe_target} := !{safe_target} * {val}"
        else:
            code = f"{indent}ghost {safe_target} := {val}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_tuple_unpack_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                   local_refs: Set[str], declared_refs: Set[str],
                                   indent: str, in_loop: bool) -> str:
        targets = stmt["targets"]
        val_whyml = self._expr_to_whyml(stmt["value"], local_refs)
        safe_targets = [self._whyml_ident(t) for t in targets]
        val_ir = stmt.get("value", {})
        if val_ir.get("type") == "Call":
            func_name = val_ir.get("func", "")
            nargs = len(val_ir.get("args", []))
            safe_fn = self._whyml_ident(func_name)
            arity_fn = f"{safe_fn}_{nargs}"
            if arity_fn in self._abstract_ops:
                tuple_ret = "(" + ", ".join(["int"] * len(targets)) + ")"
                if nargs == 0:
                    self._abstract_ops[arity_fn] = f"val {arity_fn} () : {tuple_ret}"
                else:
                    params = " ".join(f"(x{i}: int)" for i in range(nargs))
                    self._abstract_ops[arity_fn] = f"val {arity_fn} {params} : {tuple_ret}"
        tmp_names = [f"_tu_{t}" for t in safe_targets]
        pattern = ", ".join(tmp_names)
        lines = [f"{indent}let ({pattern}) = {val_whyml} in"]
        n_tu = len(tmp_names)
        i_tu = 0
        while i_tu < n_tu:
            tmp = tmp_names[i_tu]
            st = safe_targets[i_tu]
            if st in local_refs:
                lines.append(f"{indent}{st} := {tmp};")
            else:
                local_refs.add(st)
                lines.append(f"{indent}let {st} = ref {tmp} in")
            i_tu += 1
        code = "\n".join(lines)
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_array_set_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                local_refs: Set[str], declared_refs: Set[str],
                                indent: str, in_loop: bool) -> str:
        arr = stmt["array"]
        if arr.get("type") == "Var":
            var_name = arr.get("name", "")
            if var_name in getattr(self, "_dict_locals", set()):
                known_sizes = getattr(self, "_known_collection_sizes", {})
                if var_name in known_sizes:
                    known_sizes[var_name] = known_sizes[var_name] + 1
                else:
                    known_sizes[var_name] = 1
        if (arr.get("type") == "Subscript" and
                arr.get("value", {}).get("type") == "Var" and
                arr.get("value", {}).get("name") in getattr(self, "_array2d_params", set()) and
                arr.get("value", {}).get("name") not in getattr(self, "_dict_locals", set())):
            base = arr["value"]["name"]
            row_expr = self._expr_to_whyml(arr["index"], local_refs)
            col_expr = self._expr_to_whyml(stmt["index"], local_refs)
            val_expr = self._expr_to_whyml(stmt["value"], local_refs)
            code = f"{indent}set {base} {row_expr} {col_expr} {val_expr}"
        else:
            array_expr = self._expr_to_whyml(arr, local_refs)
            index_expr = self._expr_to_whyml(stmt["index"], local_refs)
            val_expr = self._expr_to_whyml(stmt["value"], local_refs)
            if self.memory_model in ("hoare", "concurrent"):
                var_name = arr.get("name", "") if arr.get("type") == "Var" else ""
                is_dict = var_name in getattr(self, "_dict_locals", set())
                is_array = not is_dict and (
                    var_name in getattr(self, "_array2d_params", set()) or
                    var_name in getattr(self, "_array_locals", set()) or
                    var_name in getattr(self, "_current_array1d_params", set()))
                if not is_array and not is_dict and var_name:
                    st = getattr(self, "_current_symbol_table", {})
                    if st.get(var_name) in ("list", "dict"):
                        is_array = True
                if is_array:
                    val_expr = self._coerce_to_int(val_expr)
                    code = f"{indent}{array_expr}[{index_expr}] <- {val_expr}"
                else:
                    self._add_abstract_op("val subscript_set (x: int) (i: int) (v: int) : unit")
                    code = (f"{indent}subscript_set {self._coerce_to_int(array_expr)} "
                            f"{self._coerce_to_int(index_expr)} {self._coerce_to_int(val_expr)}")
            else:
                hv = self._heap_var
                code = (f"{indent}{hv} := Map.set !{hv} "
                        f"({array_expr} + {index_expr}) {val_expr}")
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_if_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                        local_refs: Set[str], declared_refs: Set[str],
                        indent: str, in_loop: bool) -> str:
        test = self._expr_to_whyml(stmt["test"], local_refs)
        test = self._to_bool(test, stmt["test"])
        body = stmt.get("body", [])
        orelse = stmt.get("orelse", [])
        body_str = self._stmts_to_whyml(body, local_refs, declared_refs.copy(), indent + "  ", in_loop)
        if not body_str:
            body_str = f"{indent}  ()"
        body_returns = IRScanner.ends_with_return(body)
        if orelse:
            orelse_str = self._stmts_to_whyml(orelse, local_refs, declared_refs.copy(), indent + "  ", in_loop)
            if not orelse_str:
                orelse_str = f"{indent}  ()"
            code = (f"{indent}if {test} then begin\n{body_str}\n"
                    f"{indent}end else begin\n{orelse_str}\n{indent}end")
            if body_returns and IRScanner.ends_with_return(orelse):
                return code
        elif body_returns and rest:
            rest_str = self._stmts_to_whyml(rest, local_refs, declared_refs, indent + "  ", in_loop)
            if not rest_str:
                rest_str = f"{indent}  ()"
            return (f"{indent}if {test} then begin\n{body_str}\n"
                    f"{indent}end else begin\n{rest_str}\n{indent}end")
        else:
            stripped = body_str.rstrip()
            last_line = stripped.split('\n')[-1].strip() if stripped else ""
            body_returns_value = (last_line.startswith("(") and
                                  not last_line.startswith("()") and
                                  "raise " not in last_line and
                                  "<-" not in last_line and
                                  ":=" not in last_line and
                                  "subscript_set" not in last_line)
            if body_returns_value:
                code = (f"{indent}if {test} then begin\n{body_str}\n"
                        f"{indent}end else begin\n{indent}  0\n{indent}end")
            else:
                code = f"{indent}if {test} then begin\n{body_str}\n{indent}end"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_match_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                           local_refs: Set[str], declared_refs: Set[str],
                           indent: str, in_loop: bool) -> str:
        subject = self._expr_to_whyml(stmt["subject"], local_refs)
        cases = stmt.get("cases", [])
        lines = []
        n_cases = len(cases)
        i_case = 0
        while i_case < n_cases:
            c = cases[i_case]
            pat = c["pattern"]
            guard = c.get("guard")
            body_stmts = c.get("body", [])
            body_str = self._stmts_to_whyml(body_stmts, local_refs, declared_refs.copy(),
                                             indent + "  ", in_loop)
            if not body_str:
                body_str = f"{indent}  ()"
            cond = self._match_pattern_cond(pat, subject, local_refs)
            if guard:
                guard_str = self._expr_to_whyml(guard, local_refs)
                guard_str = self._to_bool(guard_str, guard)
                cond = f"({cond} && {guard_str})" if cond != "true" else guard_str
            if i_case == 0:
                lines.append(f"{indent}if {cond} then begin")
            elif cond == "true":
                lines.append(f"{indent}end else begin")
            else:
                lines.append(f"{indent}end else if {cond} then begin")
            lines.append(body_str)
            i_case += 1
        lines.append(f"{indent}end")
        code = "\n".join(lines)
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_critical_section_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
                                       local_refs: Set[str], declared_refs: Set[str],
                                       indent: str, in_loop: bool) -> str:
        mutex = stmt["mutex"]
        body_stmts = stmt["body"]
        assume_inv = stmt.get("assume_invariant")
        prove_inv = stmt.get("prove_invariant")
        safe_mutex = self._safe_mutex_name(mutex)
        shared_for_mutex = [
            sv["name"] for sv in self.ir.get("shared_vars", [])
            if sv.get("mutex") == mutex
        ]
        let_bindings: List[str] = []
        seq_parts: List[str] = []
        if assume_inv and shared_for_mutex:
            for var in shared_for_mutex:
                safe_var = self._whyml_ident(var)
                tmp = f"_any_{safe_var}_{self._havoc_counter}"
                self._havoc_counter += 1
                let_bindings.append(f"{indent}let {tmp} = any int in")
                seq_parts.append(f"{indent}{safe_var} := {tmp}")
            seq_parts.append(f"{indent}assume {{ {safe_mutex}_inv }}")
        elif assume_inv:
            self._in_spec = True
            inv_str = self._expr_to_whyml(assume_inv, local_refs)
            self._in_spec = False
            seq_parts.append(f"{indent}assume {{ {inv_str} }}")
        body_code = self._stmts_to_whyml(body_stmts, local_refs, declared_refs, indent, in_loop)
        if body_code:
            seq_parts.append(body_code)
        if prove_inv and shared_for_mutex:
            seq_parts.append(f"{indent}assert {{ {safe_mutex}_inv }}")
        elif prove_inv:
            self._in_spec = True
            inv_str = self._expr_to_whyml(prove_inv, local_refs)
            self._in_spec = False
            seq_parts.append(f"{indent}assert {{ {inv_str} }}")
        if not seq_parts:
            seq_parts = [f"{indent}()"]
        inner = ";\n".join(seq_parts)
        code = ("\n".join(let_bindings) + "\n" + inner) if let_bindings else inner
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_augassign_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        target = stmt["target"]
        safe_target = self._whyml_ident(target)
        val = self._expr_to_whyml(stmt["value"], local_refs)
        raw_op = stmt["op"]
        op = self._op(raw_op)
        bitwise_ops = {"&": "bit_and", "|": "bit_or", "^": "bit_xor",
                       "<<": "bit_lshift", ">>": "bit_rshift", "**": "py_pow"}
        if raw_op in bitwise_ops:
            op_fn = bitwise_ops[raw_op]
            self._add_abstract_op(f"val {op_fn} (x: int) (y: int) : int")
            code = f"{indent}{safe_target} := ({op_fn} !{safe_target} {val})"
        else:
            code = f"{indent}{safe_target} := !{safe_target} {op} {val}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_fieldassign_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        obj = stmt["object"]
        field = stmt["field"]
        val = self._expr_to_whyml(stmt["value"], local_refs)
        if val == "true":
            val = "1"
        elif val == "false":
            val = "0"
        safe_field = self._whyml_ident(field)
        decl_fields = getattr(self, '_all_record_fields', set())
        if field in decl_fields:
            code = f"{indent}{obj}.{safe_field} <- {val}"
        else:
            hash_field = hash(field) % 2147483647
            self_type = getattr(self, '_current_self_type', None)
            if obj == "self" and self_type:
                self._add_abstract_op(f"val setattr_{self_type} (x: {self_type}) (f: int) (v: int) : unit")
                code = f"{indent}setattr_{self_type} {obj} {hash_field} {self._coerce_to_int(val)}"
            else:
                self._add_abstract_op("val setattr_3 (x: int) (f: int) (v: int) : unit")
                code = f"{indent}setattr_3 {self._coerce_to_int(obj)} {hash_field} {self._coerce_to_int(val)}"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_fieldaugassign_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        obj = stmt["object"]
        field = stmt["field"]
        val = self._expr_to_whyml(stmt["value"], local_refs)
        op = self._op(stmt["op"])
        safe_field = self._whyml_ident(field)
        decl_fields = getattr(self, '_all_record_fields', set())
        if field in decl_fields:
            code = f"{indent}{obj}.{safe_field} <- {obj}.{safe_field} {op} {val}"
        else:
            hash_field = hash(field) % 2147483647
            self_type = getattr(self, '_current_self_type', None)
            if obj == "self" and self_type:
                getter = f"getattr_{self_type}"
                setter = f"setattr_{self_type}"
                self._add_abstract_op(f"val {getter} (x: {self_type}) (f: int) : int")
                self._add_abstract_op(f"val {setter} (x: {self_type}) (f: int) (v: int) : unit")
                code = f"{indent}{setter} {obj} {hash_field} (({getter} {obj} {hash_field}) {op} {self._coerce_to_int(val)})"
            else:
                self._add_abstract_op("val getattr_2 (x: int) (f: int) : int")
                self._add_abstract_op("val setattr_3 (x: int) (f: int) (v: int) : unit")
                obj_str = self._coerce_to_int(obj)
                code = f"{indent}setattr_3 {obj_str} {hash_field} ((getattr_2 {obj_str} {hash_field}) {op} {self._coerce_to_int(val)})"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _handle_return_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        """Reads self._has_early_ret, self._func_return_type, self._array_locals (no writes)."""
        val_ir = stmt.get("value")
        if val_ir is None:
            val = "()"
        else:
            if val_ir.get("type") == "Var" and val_ir.get("name") in self._array_locals:
                val = "0"
            else:
                val = self._expr_to_whyml(val_ir, local_refs)
        use_raise = in_loop or getattr(self, '_has_early_ret', False)
        if use_raise:
            func_ret = getattr(self, '_func_return_type', 'int')
            if func_ret == "unit":
                return f"{indent}raise Return_void"
            if val == "()":
                val = "0"
            elif val == "true":
                val = "1"
            elif val == "false":
                val = "0"
            val = self._coerce_to_int(val)
            return f"{indent}raise (Return {val})"
        return f"{indent}{val}"

    def _handle_expr_stmt(
        self,
        stmt: Dict[str, Any],
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        val = stmt.get("value", {})
        if val.get("type") == "Call":
            func = val.get("func", "")
            if func.endswith(".append") and self.memory_model in ("hoare", "concurrent"):
                arr_name = func.rsplit(".", 1)[0].replace(".", "_")
                safe_arr = self._whyml_ident(arr_name)
                arg = self._expr_to_whyml(val["args"][0], local_refs)
                arg = self._coerce_to_int(arg)
                len_ref = f"{safe_arr}_len"
                code = f"{indent}{safe_arr}[!{len_ref}] <- {arg};\n{indent}{len_ref} := !{len_ref} + 1"
            else:
                expr_str = self._expr_to_whyml(val, local_refs)
                code = f"{indent}let _ = {expr_str} in ()"
        else:
            expr_str = self._expr_to_whyml(val, local_refs)
            code = f"{indent}let _ = {expr_str} in ()"
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
        return code

    def _stmts_to_whyml(self, stmts: List[Dict[str, Any]], local_refs: Set[str], declared_refs: Set[str], indent: str, in_loop: bool = False) -> str:
        """Recursively translates imperative statements into WhyML strings."""
        if not stmts: return ""

        stmt = stmts[0]
        rest = stmts[1:]
        code = ""
        s_type = stmt["stmt"]

        if s_type == "Label":
            # `label L in <rest>` — scopes over the entire remaining block
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
            if not rest_code:
                rest_code = f"{indent}()"
            return f"{indent}label {stmt['name']} in\n{rest_code}"

        elif s_type == "GhostAssign":
            return self._handle_ghost_assign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Assign":
            return self._handle_assign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "TupleUnpack":
            return self._handle_tuple_unpack_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "AugAssign":
            return self._handle_augassign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "FieldAssign":
            return self._handle_fieldassign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "FieldAugAssign":
            return self._handle_fieldaugassign_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "ArraySet":
            return self._handle_array_set_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)


        elif s_type == "While":
            return self._handle_while_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Return":
            return self._handle_return_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Continue":
            # Raise the continue exception caught by the enclosing For loop's try/with
            return f"{indent}raise PyCSL_Continue"

        elif s_type == "Assert":
            # Python assert statements are runtime checks, not proof obligations.
            # Skip them in WhyML — the pycsl annotations define the proof goals.
            code = f'{indent}()'

        elif s_type == "Raise":
            exc_type = stmt.get("exc_type", "PyCSL_Exception")
            return f"{indent}raise {exc_type}"

        elif s_type == "If":
            return self._handle_if_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "For":
            return self._handle_for_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Expr":
            return self._handle_expr_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Try":
            return self._handle_try_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "Pass":
            code = f"{indent}()"

        elif s_type == "Break":
            # WhyML doesn't have break; model as exception
            code = f"{indent}raise PyCSL_Break"

        elif s_type == "Match":
            return self._handle_match_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        elif s_type == "CriticalSection":
            return self._handle_critical_section_stmt(stmt, rest, local_refs, declared_refs, indent, in_loop)

        # Chain sequence of statements with semicolons
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)

        return code

    def _emit_frame_condition(self, assigns_list: List[Dict[str, Any]],
                              spec_refs: Set[str]) -> List[str]:
        """Generate WhyML frame condition lines from \\assigns contracts.

        In the Hoare model: no frame condition (value-semantic arrays can't alias).
        In typed/store models: emits `writes` + quantified `ensures` for unchanged locations.
        Returns a list of WhyML lines to append after the function's `ensures` clauses.
        """
        if self.memory_model in ("hoare", "concurrent"):
            return []

        hv = self._heap_var
        regions = [a for a in assigns_list if a.get("type") == "AssignsRegion"]
        nothings = [a for a in assigns_list if a.get("type") == "Nothing"]

        if nothings:
            return [f"    ensures  {{ !{hv} = old !{hv} }}"]

        if not regions:
            return [f"    writes   {{ {hv} }}"]

        lines = [f"    writes   {{ {hv} }}"]
        exclusions = []
        for r in regions:
            base = r["base"]
            lo = self._expr_to_whyml(r["low"], spec_refs)
            hi = self._expr_to_whyml(r["high"], spec_refs)
            exclusions.append(f"({base} + {lo} <= l && l < {base} + {hi})")

        neg = " && ".join(f"(not {e})" for e in exclusions)
        lines.append(
            f"    ensures  {{ forall l: int. {neg}"
            f" -> Map.get !{hv} l = Map.get (old !{hv}) l }}"
        )
        return lines

    def _compute_sccs(self, names: Set[str], call_graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Compute SCCs via Tarjan's algorithm. Returns SCCs in topological order
        (callees before callers). Each SCC is a list of function names."""
        index_counter = [0]
        stack: List[str] = []
        lowlink: Dict[str, int] = {}
        index: Dict[str, int] = {}
        on_stack: Dict[str, bool] = {}
        sccs: List[List[str]] = []

        def strongconnect(v: str) -> None:
            index[v] = index_counter[0]
            lowlink[v] = index_counter[0]
            index_counter[0] += 1
            stack.append(v)
            on_stack[v] = True
            for w in call_graph.get(v, set()):
                if w not in names:
                    continue
                if w not in index:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif on_stack.get(w):
                    lowlink[v] = min(lowlink[v], index[w])
            if lowlink[v] == index[v]:
                scc: List[str] = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == v:
                        break
                sccs.append(scc)

        for v in sorted(names):  # sorted for determinism
            if v not in index:
                strongconnect(v)

        # Tarjan's outputs callees before callers — already the order we want
        return sccs

    # ------------------------------------------------------------------
    # Helpers hoisted from transpile() nested function definitions
    # ------------------------------------------------------------------

    def _find_calls_in_ir(self, obj: Any, func_names_set: Set[str]) -> Set[str]:
        """Find all function names called within an IR object."""
        calls: Set[str] = set()
        if isinstance(obj, dict):
            if obj.get("type") == "Call" and obj.get("func") in func_names_set:
                calls.add(obj["func"])
            for v in obj.values():
                calls |= self._find_calls_in_ir(v, func_names_set)
        elif isinstance(obj, list):
            for item in obj:
                calls |= self._find_calls_in_ir(item, func_names_set)
        return calls

    @staticmethod
    def _build_witness_str(field_names: List[str], vals: Dict[str, Any]) -> str:
        """Build a WhyML record literal witness string."""
        return "; ".join(f"{fn} = {vals.get(fn, 0)}" for fn in field_names)

    def _check_witness_vals(self, vals: Dict[str, Any], invs: List[Any], field_names: List[str]) -> bool:
        """Quick sanity check: evaluate invariant with witness values."""
        for inv_ir in invs:
            try:
                expr = self._expr_to_whyml(inv_ir, set(), invariant_ctx=True)
                test_expr = expr
                for fn in field_names:
                    test_expr = test_expr.replace(fn, str(vals.get(fn, 0)))
                test_expr = (test_expr.replace("=", "==")
                             .replace("!==", "!=")
                             .replace("<==", "<=")
                             .replace(">==", ">="))
                if not eval(test_expr):  # noqa: S307
                    return False
            except Exception:
                pass
        return True

    def _param_type_str(self, arg: str, ref_params: Set[str], array2d_params: Set[str],
                        array1d_params: Set[str], symbol_table: Dict[str, Any],
                        int_type: str) -> str:
        """Return the WhyML parameter type string for a standalone function argument."""
        safe = self._whyml_ident(arg)
        if arg in ref_params:
            return f"({safe}: ref {int_type})"
        if arg in array2d_params:
            return f"({safe}: matrix {int_type})"
        if arg in array1d_params or symbol_table.get(arg) in ("list", "dict"):
            if self.memory_model in ("hoare", "concurrent"):
                return f"({safe}: array {int_type})"
            return f"({safe}: loc) ({safe}_len: int)"
        if symbol_table.get(arg) == "str":
            return f"({safe}: {int_type})"
        return f"({safe}: {int_type})"

    # ------------------------------------------------------------------
    # transpile() Phase A — collect record field names
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # transpile() Phase B — scan preamble needs
    # ------------------------------------------------------------------

    def _scan_preamble_needs(self, functions: List[Dict[str, Any]],
                             all_bodies: List[Any]) -> Dict[str, Any]:
        """Scan all function bodies once to collect feature flags for preamble emission."""
        has_list_param = any(
            v in ("list", "dict")
            for func in functions
            for v in func.get("symbol_table", {}).values()
        )
        needs_matrix = any(func.get("array2d_params") for func in functions)
        if self.memory_model in ("hoare", "concurrent"):
            needs_array = (
                has_list_param
                or any(IRScanner.uses_for(body) for body in all_bodies)
                or any(IRScanner.uses_subscript(body) for body in all_bodies)
                or any(IRScanner.uses_arrayset(body) for body in all_bodies)
                or any(IRScanner.uses_array_lit(body) for body in all_bodies)
            )
        else:
            needs_array = False
        needs_minmax = any(IRScanner.uses_minmax(body) for body in all_bodies)
        needs_continue = any(IRScanner.uses_continue(body) for body in all_bodies)
        needs_break = any(IRScanner.uses_break(body) for body in all_bodies)
        needs_return_exc = False
        needs_return_void = False
        n = len(functions)
        i = 0
        while i < n:
            func = functions[i]
            has_ret = IRScanner.has_in_loop_return(func["body"]) or IRScanner.has_early_return(func["body"])
            if has_ret:
                ret_type = IRScanner.find_return_type(func["body"])
                if ret_type == "unit":
                    needs_return_void = True
                else:
                    needs_return_exc = True
            i += 1
        needs_string = False
        needs_sum = any(IRScanner.uses_sum(func) for func in functions)
        needs_divmod = any(IRScanner.uses_divmod(body) for body in all_bodies)
        bounded_sizes = {func["bounded_int"] for func in functions if func.get("bounded_int")}
        user_exceptions: Set[str] = set()
        n2 = len(all_bodies)
        i2 = 0
        while i2 < n2:
            user_exceptions |= IRScanner.collect_user_exceptions(all_bodies[i2])
            i2 += 1
        return {
            "needs_array": needs_array,
            "needs_matrix": needs_matrix,
            "needs_minmax": needs_minmax,
            "needs_continue": needs_continue,
            "needs_break": needs_break,
            "needs_return_exc": needs_return_exc,
            "needs_return_void": needs_return_void,
            "needs_string": needs_string,
            "needs_sum": needs_sum,
            "needs_divmod": needs_divmod,
            "bounded_sizes": bounded_sizes,
            "user_exceptions": user_exceptions,
        }

    # ------------------------------------------------------------------
    # transpile() Phase C — emit module preamble (use / exceptions / helpers)
    # ------------------------------------------------------------------

    def _emit_preamble_uses(self, needs: Dict[str, Any]) -> List[str]:
        """Phase A: emit module header and `use` declarations for libraries."""
        out = [
            "module PyCSL_Program",
            "  use int.Int",
            "  use int.EuclideanDivision",
            "  use ref.Ref",
        ]
        sorted_bsz = sorted(needs["bounded_sizes"])
        n = len(sorted_bsz)
        i = 0
        while i < n:
            out.append(f"  use mach.int.Int{sorted_bsz[i]}")
            i += 1
        if needs["needs_string"]:
            out.append("  use string.String")
        if self.memory_model in ("hoare", "concurrent"):
            if needs["needs_array"]:
                out.append("  use array.Array")
            if needs["needs_matrix"]:
                out.append("  use matrix.Matrix")
            if needs["needs_minmax"]:
                out.append("  use int.MinMax")
        else:
            out.append("  use map.Map")
            if needs["needs_minmax"]:
                out.append("  use int.MinMax")
            out.append("")
            out.append("  type loc = int")
            out.append("  constant max_addr : int = 1073741824")
            hv = self._heap_var
            out.append(f"  val ghost {hv} : ref (map loc int)")
            out.append("")
            out.append(f"  predicate valid (m: map loc int) (base: loc) (n: int) =")
            out.append(f"    n >= 0 /\\ base >= 0 /\\ base + n <= max_addr")
            out.append("")
            out.append(f"  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =")
            out.append(f"    a + na <= b \\/ b + nb <= a")
            out.append("")
        return out

    def _emit_preamble_exceptions(self, needs: Dict[str, Any]) -> List[str]:
        """Phase B: emit exception type declarations."""
        out: List[str] = []
        if needs["needs_continue"]:
            out.append("")
            out.append("  exception PyCSL_Continue")
        if needs["needs_break"]:
            out.append("")
            out.append("  exception PyCSL_Break")
        if needs["needs_return_exc"]:
            out.append("")
            out.append("  exception Return int")
        if needs["needs_return_void"]:
            out.append("")
            out.append("  exception Return_void")
        sorted_exc = sorted(needs["user_exceptions"])
        n = len(sorted_exc)
        i = 0
        while i < n:
            out.append(f"  exception {sorted_exc[i]}")
            i += 1
        return out

    def _emit_preamble_helpers(self, needs: Dict[str, Any]) -> List[str]:
        """Phase C: emit pycsl_sum, pycsl_div, pycsl_mod helper function bodies."""
        out: List[str] = []
        if needs["needs_sum"]:
            out.append("")
            out.append("  let rec function pycsl_sum (a: array int) (lo hi: int) : int")
            out.append("    requires { 0 <= lo }")
            out.append("    requires { hi <= length a }")
            out.append("    variant { hi - lo }")
            out.append("  = if lo >= hi then 0 else a[lo] + pycsl_sum a (lo + 1) hi")
            out.append("")
            out.append("  let rec lemma pycsl_sum_snoc (a: array int) (lo hi: int) : unit")
            out.append("    requires { 0 <= lo <= hi <= length a }")
            out.append("    variant { hi - lo }")
            out.append("    ensures { hi > lo -> pycsl_sum a lo hi = pycsl_sum a lo (hi - 1) + a[hi - 1] }")
            out.append("  = if lo < hi - 1 then pycsl_sum_snoc a (lo + 1) hi")
        if needs["needs_divmod"]:
            out.append("")
            if "ZeroDivisionError" in needs["user_exceptions"]:
                out.append("  let pycsl_div (x: int) (y: int) : int")
                out.append("    raises { ZeroDivisionError -> y = 0 }")
                out.append("    ensures { y <> 0 /\\ result = div x y }")
                out.append("  = if y = 0 then raise ZeroDivisionError else div x y")
                out.append("")
                out.append("  let pycsl_mod (x: int) (y: int) : int")
                out.append("    raises { ZeroDivisionError -> y = 0 }")
                out.append("    ensures { y <> 0 /\\ result = mod x y }")
                out.append("  = if y = 0 then raise ZeroDivisionError else mod x y")
            else:
                out.append("  let pycsl_div (x: int) (y: int) : int")
                out.append("    requires { [@expl:division by zero] y <> 0 }")
                out.append("    ensures { result = div x y }")
                out.append("  = div x y")
                out.append("")
                out.append("  let pycsl_mod (x: int) (y: int) : int")
                out.append("    requires { [@expl:modulo by zero] y <> 0 }")
                out.append("    ensures { result = mod x y }")
                out.append("  = mod x y")
        return out

    def _emit_preamble(self, needs: Dict[str, Any]) -> List[str]:
        """Emit the WhyML module header: use declarations, exception types, helper functions."""
        out = self._emit_preamble_uses(needs)
        out += self._emit_preamble_exceptions(needs)
        out += self._emit_preamble_helpers(needs)
        out.append("")
        return out

    # ------------------------------------------------------------------
    # transpile() Phase D — emit concurrent-model shared state
    # ------------------------------------------------------------------

    def _emit_shared_state(self) -> List[str]:
        """Emit shared variable declarations and mutex invariant predicates (concurrent model)."""
        out: List[str] = []
        shared_vars = self.ir.get("shared_vars", [])
        mutex_invariants_ir = self.ir.get("mutex_invariants", {})
        if shared_vars:
            self._shared_var_names = {sv["name"] for sv in shared_vars}
            out.append("  (* --- shared state (concurrent model) --- *)")
            n = len(shared_vars)
            i = 0
            while i < n:
                sv = shared_vars[i]
                safe_name = self._whyml_ident(sv["name"])
                out.append(f"  val {safe_name} : ref int")
                i += 1
            out.append("")
        if mutex_invariants_ir:
            sorted_mi = sorted(mutex_invariants_ir.items())
            n = len(sorted_mi)
            i = 0
            while i < n:
                mutex, inv_ir = sorted_mi[i]
                safe_mutex = self._safe_mutex_name(mutex)
                self._in_spec = True
                inv_str = self._expr_to_whyml(inv_ir, set())
                self._in_spec = False
                out.append(f"  predicate {safe_mutex}_inv = {inv_str}")
                i += 1
            out.append("")
            sorted_mi2 = sorted(mutex_invariants_ir.items())
            n2 = len(sorted_mi2)
            i2 = 0
            while i2 < n2:
                mutex2, _ = sorted_mi2[i2]
                safe_mutex2 = self._safe_mutex_name(mutex2)
                out.append(f"  let _check_initial_{safe_mutex2} () : unit =")
                out.append(f"    assert {{ {safe_mutex2}_inv }}")
                out.append("")
                i2 += 1
        return out

    # ------------------------------------------------------------------
    # transpile() Phase E — emit type declarations
    # ------------------------------------------------------------------

    def _emit_type_decls(self, type_decls: List[Dict[str, Any]]) -> Tuple[List[str], Set[str]]:
        """Emit record type declarations. Returns (lines, declared_types)."""
        out: List[str] = []
        declared_types: Set[str] = set()
        n = len(type_decls)
        i = 0
        while i < n:
            td = type_decls[i]
            if td["kind"] == "record":
                type_name = td["name"].lower()
                declared_types.add(type_name)
                self._record_types[td["name"]] = {
                    "whyml_name": type_name,
                    "fields": [f["name"] for f in td["fields"]],
                    "defaults": td.get("field_defaults", {}),
                }
                field_strs = []
                fields = td["fields"]
                nf = len(fields)
                j = 0
                while j < nf:
                    f = fields[j]
                    prefix = "mutable " if f.get("mutable") else ""
                    ftype = f['type']
                    if ftype == "string":
                        ftype = "int"
                    field_strs.append(f"{prefix}{f['name']}: {ftype}")
                    j += 1
                out.append(f"  type {type_name} = {{ {'; '.join(field_strs)} }}")
                class_invs = td.get("class_invariants", [])
                if class_invs:
                    self._in_spec = True
                    n_inv = len(class_invs)
                    i_inv = 0
                    while i_inv < n_inv:
                        inv = class_invs[i_inv]
                        inv_str = self._expr_to_whyml(inv, set(), invariant_ctx=True)
                        out.append(f"    invariant {{ {inv_str} }}")
                        i_inv += 1
                    self._in_spec = False
                    defaults = td.get("field_defaults", {})
                    field_names = [f["name"] for f in td["fields"]]
                    witness_vals = {fn: defaults.get(fn, 0) for fn in field_names}
                    if not self._check_witness_vals(witness_vals, class_invs, field_names):
                        combos = [
                            {fn: 0 for fn in field_names},
                            {fn: 1 for fn in field_names},
                            {fn: 10 for fn in field_names},
                        ]
                        nc = len(combos)
                        ic = 0
                        while ic < nc:
                            combo = combos[ic]
                            if self._check_witness_vals(combo, class_invs, field_names):
                                witness_vals = combo
                                break
                            ic += 1
                    out.append(f"    by {{ {self._build_witness_str(field_names, witness_vals)} }}")
                out.append("")
            i += 1
        return out, declared_types

    # ------------------------------------------------------------------
    # transpile() Phase G — topological sort via SCC
    # ------------------------------------------------------------------

    def _sort_functions_by_scc(
        self, functions: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, tuple]]:
        """Return functions in SCC-topological order and a scc_info dict."""
        func_names_set = {func["name"] for func in functions}
        func_by_name = {func["name"]: func for func in functions}
        call_graph: Dict[str, Set[str]] = {}
        n = len(functions)
        i = 0
        while i < n:
            func = functions[i]
            call_graph[func["name"]] = (
                self._find_calls_in_ir(func["body"], func_names_set) & func_names_set
            )
            i += 1
        ordered_sccs = self._compute_sccs(func_names_set, call_graph)
        sorted_names = [name for scc in ordered_sccs for name in scc]
        scc_info: Dict[str, tuple] = {}
        for scc_idx, scc in enumerate(ordered_sccs):
            scc_size = len(scc)
            for pos, name in enumerate(scc):
                scc_info[name] = (scc_idx, pos, scc_size)
        for func in functions:
            if func["name"] not in sorted_names:
                sorted_names.append(func["name"])
                scc_info[func["name"]] = (len(ordered_sccs), 0, 1)
        return [func_by_name[name] for name in sorted_names], scc_info

    # ------------------------------------------------------------------
    # transpile() Phase H — emit one function block (and helpers)
    # ------------------------------------------------------------------

    def _reset_function_state(self, func: Dict[str, Any],
                               body_stmts: List[Dict[str, Any]]) -> Tuple[Set[str], Set[str]]:
        """Reset all per-function instance variables. Returns (local_refs, ghost_vars)."""
        self._bounded_int = func.get("bounded_int")
        symbol_table = func.get("symbol_table", {})
        local_refs = IRScanner.find_assigned_vars(body_stmts)
        local_refs -= self._shared_var_names
        ghost_vars = IRScanner.find_ghost_vars(body_stmts)
        self._current_params = (
            (set(symbol_table.keys()) | local_refs | ghost_vars) - self._shared_var_names
        )
        self._array_locals = set()
        self._dict_locals = set()
        self._lambda_locals = set()
        self._record_locals = set()
        self._known_collection_sizes = {}
        self._known_collection_elements = {}
        self._current_symbol_table = symbol_table
        self._current_array1d_params = set(func.get("array1d_params", []))
        self._array2d_params = set(func.get("array2d_params", []))
        return local_refs, ghost_vars

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
            self._current_self_type = func["self_type"].lower()
            param_parts = [f"(self: {self._current_self_type})"]
            for arg in symbol_table:
                if arg in local_refs or arg in ghost_vars:
                    continue
                safe = self._whyml_ident(arg)
                if arg in array2d_params:
                    param_parts.append(f"({safe}: matrix {int_type})")
                elif arg in array1d_params or symbol_table.get(arg) in ("list", "dict"):
                    if self.memory_model in ("hoare", "concurrent"):
                        param_parts.append(f"({safe}: array {int_type})")
                    else:
                        param_parts.append(f"({safe}: loc) ({safe}_len: int)")
                else:
                    param_parts.append(f"({safe}: {int_type})")
            return set(), " ".join(param_parts)
        else:
            self._current_self_type = None
            ref_params = {v for v in symbol_table if v in local_refs and v.startswith("obj_")}
            args = [v for v in symbol_table
                    if (v not in local_refs or v in ref_params) and v not in ghost_vars]
            args_str = " ".join(
                self._param_type_str(arg, ref_params, array2d_params, array1d_params,
                                     symbol_table, int_type)
                for arg in args
            )
            return ref_params, args_str

    def _emit_contracts(self, contracts: Dict[str, Any], spec_refs: Set[str],
                         func_variants: List[Any], func_diverges: bool,
                         func_exceptions: Set[str]) -> List[str]:
        """Emit requires/ensures/assigns/variant/raises lines.
        Toggles self._in_spec around emission."""
        lines: List[str] = []
        self._in_spec = True

        for req in contracts.get("requires", []):
            lines.append(f"    requires {{ {self._expr_to_whyml(req, spec_refs)} }}")
        for ens in contracts.get("ensures", []):
            lines.append(f"    ensures  {{ {self._expr_to_whyml(ens, spec_refs)} }}")
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
            for rc in raises_contracts:
                cond_str = self._expr_to_whyml(rc["condition"], spec_refs)
                lines.append(f"    raises {{ {rc['exc_type']} -> {cond_str} }}")
            declared_exc = {rc["exc_type"] for rc in raises_contracts}
            for exc in sorted(func_exceptions - declared_exc):
                lines.append(f"    raises {{ {exc} }}")
        elif func_exceptions:
            lines.append(f"    raises {{ {', '.join(sorted(func_exceptions))} }}")

        self._in_spec = False
        return lines

    def _emit_body_code(self, func: Dict[str, Any], body_stmts: List[Dict[str, Any]],
                         local_refs: Set[str], ghost_vars: Set[str], ref_params: Set[str],
                         is_method: bool, return_type: str) -> str:
        """Build the WhyML body code string with pre-declared ref variables.
        Mutates self._array_locals, self._has_early_ret."""
        bounded_int = func.get("bounded_int")
        append_targets = IRScanner.find_append_targets(body_stmts)
        self._has_early_ret = IRScanner.has_early_return(body_stmts)
        body_array_vars, body_dict_vars = IRScanner.find_array_and_dict_vars(body_stmts)
        body_lambda_vars = IRScanner.find_lambda_vars(body_stmts)
        body_record_vars = IRScanner.find_record_vars(body_stmts, self._record_types)

        pre_decl_vars: Set[str] = {
            v for v in local_refs
            if v not in ghost_vars
            and v not in ref_params
            and v not in body_array_vars
            and v not in body_dict_vars
            and v not in body_lambda_vars
            and v not in body_record_vars
        }

        if is_method:
            initial_declared = {self._whyml_ident(v) for v in pre_decl_vars}
        else:
            initial_declared = set(ref_params) | {self._whyml_ident(v) for v in pre_decl_vars}

        body_code = self._stmts_to_whyml(
            body_stmts,
            local_refs | {f"{t}_len" for t in append_targets},
            initial_declared,
            "    ",
        )

        for var in sorted(pre_decl_vars):
            safe_var = self._whyml_ident(var)
            pfx = f"(0 : int{bounded_int})" if bounded_int else "0"
            body_code = f"    let {safe_var} = ref {pfx} in\n{body_code}"

        for tgt in sorted(append_targets):
            safe_tgt = self._whyml_ident(tgt)
            pfx = f"(0 : int{bounded_int})" if bounded_int else "0"
            body_code = f"    let {safe_tgt}_len = ref {pfx} in\n{body_code}"
            if tgt not in local_refs and tgt not in ref_params:
                body_code = f"    let {safe_tgt} = Array.make 1024 0 in\n{body_code}"
                self._array_locals.add(tgt)

        if not body_code.strip():
            body_code = "    ()"
        if self._has_early_ret:
            if return_type == "unit":
                body_code = f"    try\n{body_code}\n    with Return_void -> () end"
            else:
                body_code = f"    try\n{body_code}\n    with Return r -> r end"
        return body_code

    def _emit_function(self, func: Dict[str, Any], scc_info: Dict[str, tuple]) -> List[str]:
        """Emit one WhyML let/val function block. Returns the list of output lines."""
        name = self._whyml_ident(func["name"])
        body_stmts = func["body"]
        is_method = func.get("kind") == "method"

        local_refs, ghost_vars = self._reset_function_state(func, body_stmts)
        ref_params, args_str = self._build_param_list(func, local_refs, ghost_vars)

        bounded_int = func.get("bounded_int")
        int_type = f"int{bounded_int}" if bounded_int else "int"
        return_type = IRScanner.find_return_type(body_stmts)
        self._func_return_type = return_type
        if func.get("return_annotation") == "list" and return_type == "int":
            return_type = "array int"
        if bounded_int and return_type == "int":
            return_type = int_type
        self._current_tuple_arity = (
            return_type.count(",") + 1 if return_type.startswith("(") else 0
        )

        func_variants = func.get("function_variants", [])
        func_diverges = func.get("diverges", False)
        func_trusted = func.get("trusted", False)
        func_pure = func.get("pure", False)
        is_recursive = IRScanner.is_recursive(name, body_stmts)
        use_rec = bool(func_variants) or is_recursive
        can_emit_as_logic = func_pure and not local_refs and not is_method

        _scc_idx, _pos_in_scc, _scc_size = scc_info.get(func["name"], (0, 0, 1))
        is_and_clause = _pos_in_scc > 0 and not func_trusted and not can_emit_as_logic

        lines: List[str] = []
        if func_trusted:
            kw = f"val {name}"
        elif can_emit_as_logic:
            kw = f"{'let rec function' if use_rec else 'let function'} {name}"
        elif is_and_clause:
            kw = f"and {name}"
        else:
            kw = f"{'let rec' if (use_rec or _scc_size > 1) else 'let'} {name}"
        lines.append(f"  {kw} {args_str} : {return_type}" if args_str
                     else f"  {kw} () : {return_type}")

        spec_refs = set() if is_method else ref_params
        func_exceptions = IRScanner.collect_escaping_exceptions(body_stmts)
        lines += self._emit_contracts(func.get("contracts", {}), spec_refs,
                                      func_variants, func_diverges, func_exceptions)

        if func_trusted:
            lines.append("")
            return lines

        lines.append("  =")
        lines.append(self._emit_body_code(func, body_stmts, local_refs, ghost_vars,
                                          ref_params, is_method, return_type))
        if _pos_in_scc == _scc_size - 1:
            lines.append("")
        return lines

    # ------------------------------------------------------------------
    # transpile() — thin orchestrator
    # ------------------------------------------------------------------

    def transpile(self) -> str:
        """Entry point: converts the entire program to a .mlw string."""
        functions = self.ir.get("functions", [])
        type_decls = self.ir.get("type_decls", [])
        all_bodies = [func["body"] for func in functions]

        self._all_record_fields = self._collect_record_fields(type_decls)

        needs = self._scan_preamble_needs(functions, all_bodies)
        out = self._emit_preamble(needs)
        out += self._emit_shared_state()

        type_lines, declared_types = self._emit_type_decls(type_decls)
        out += type_lines

        # Opaque type aliases for classes used in methods but not declared as records
        n7 = len(functions)
        i7 = 0
        while i7 < n7:
            func = functions[i7]
            if func.get("kind") == "method" and func.get("self_type"):
                st = func["self_type"].lower()
                if st not in declared_types:
                    declared_types.add(st)
                    out.append(f"  type {st} = int")
                    out.append("")
            i7 += 1

        self._module_func_names = {self._whyml_ident(func["name"]) for func in functions}

        sorted_functions, scc_info = self._sort_functions_by_scc(functions)

        n8 = len(sorted_functions)
        i8 = 0
        while i8 < n8:
            out += self._emit_function(sorted_functions[i8], scc_info)
            i8 += 1

        out.append("end")

        # Insert abstract val declarations (collected during transpilation)
        if self._abstract_ops:
            insert_idx = None
            n9 = len(out)
            i9 = 0
            while i9 < n9:
                line = out[i9]
                if line.strip().startswith("let ") or line.strip().startswith("let rec "):
                    insert_idx = i9
                    break
                if line.strip().startswith("val ") and "ghost" not in line:
                    insert_idx = i9
                    break
                i9 += 1
            if insert_idx is None:
                insert_idx = len(out) - 1
            abs_lines = ["", "  (* Abstract operations for unsupported Python patterns *)"]
            sorted_decls10 = sorted(self._abstract_ops.values())
            n10d = len(sorted_decls10)
            i10d = 0
            while i10d < n10d:
                abs_lines.append(f"  {sorted_decls10[i10d]}")
                i10d += 1
            abs_lines.append("")
            rev_abs10 = list(reversed(abs_lines))
            n10r = len(rev_abs10)
            i10r = 0
            while i10r < n10r:
                out.insert(insert_idx, rev_abs10[i10r])
                i10r += 1

        return "\n".join(out)

