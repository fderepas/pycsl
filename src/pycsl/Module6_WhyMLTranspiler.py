import json
from typing import Dict, Any, Set, List

class Module6_WhyMLTranspiler:
    """Reads the JSON IR and transpiles it into valid WhyML (.mlw) syntax."""
    
    def __init__(self, json_ir: str, memory_model: str = "hoare"):
        self.ir = json.loads(json_ir)
        self.memory_model = memory_model   # "hoare" | "typed" | "store"
        self._array2d_params: set = set()  # set during per-function transpilation
        self._in_spec = False              # True when emitting contracts (no div-by-zero VCs)
        self._bounded_int = None           # Current function's bounded_int size (or None)
        self._abstract_ops: dict = {}      # Abstract val declarations: name → full decl string
        self._current_params: set = set()  # Parameters of current function being transpiled
        self._array_locals: set = set()    # Local array variables (no ! deref needed)
        self._dict_locals: set = set()     # Local dict variables (not real arrays)
        # Maps Python/IR operators to WhyML operators
        self.op_map = {
            "==": "=",   # WhyML equality is single =
            "!=": "<>",  # WhyML inequality is <>
            "==>": "->",  # WhyML implication
            "<==>": "<->",  # WhyML equivalence
            "and": "&&",
            "or": "||",
            "not": "not",
            "div": "div",
            "//": "div",  # contract floor-division maps to WhyML div
            "/": "div",  # contract `/` maps to WhyML `div` (Euclidean integer division)
            "%": "mod"   # WhyML modulo from int.EuclideanDivision
        }

    @property
    def _heap_var(self) -> str:
        """Returns the name of the mutable heap variable for the current model."""
        if self.memory_model == "typed":
            return "int_mem"
        elif self.memory_model == "store":
            return "store"
        raise ValueError(f"No heap variable in Hoare model")

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
        # Replace dots with underscores for valid WhyML identifiers
        name = name.replace(".", "_")
        if name and name[0].isupper():
            name = name[0].lower() + name[1:]
        # Prefix reserved words to avoid conflicts
        if name in Module6_WhyMLTranspiler._WHYML_RESERVED:
            name = f"py_{name}"
        return name

    def _op(self, op: str) -> str:
        """Translates operators; defaults to the same string (e.g., +, -, >, <)."""
        return self.op_map.get(op, op)

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

    def _uses_arrayset(self, stmts: List[Dict[str, Any]]) -> bool:
        """Recursively check if any statement is an ArraySet (subscript assignment)."""
        for stmt in stmts:
            if stmt.get("stmt") == "ArraySet":
                return True
            for key in ("body", "orelse"):
                if key in stmt and self._uses_arrayset(stmt[key]):
                    return True
        return False

    def _ends_with_return(self, stmts: List[Dict[str, Any]]) -> bool:
        """Check if a statement list always ends with a Return (on all paths)."""
        if not stmts:
            return False
        last = stmts[-1]
        st = last.get("stmt") or last.get("type")
        if st == "Return":
            return True
        if st == "If":
            return (self._ends_with_return(last.get("body", []))
                    and self._ends_with_return(last.get("orelse", [])))
        return False

    def _find_assigned_vars(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Scans the block to find which variables are mutated (local refs)."""
        assigned = set()
        for stmt in stmts:
            if stmt["stmt"] in ("Assign", "AugAssign"):
                assigned.add(stmt["target"])
            elif stmt["stmt"] == "TupleUnpack":
                assigned.update(stmt.get("targets", []))
            elif stmt["stmt"] == "While":
                assigned.update(self._find_assigned_vars(stmt["body"]))
            elif stmt["stmt"] == "If":
                assigned.update(self._find_assigned_vars(stmt.get("body", [])))
                assigned.update(self._find_assigned_vars(stmt.get("orelse", [])))
            elif stmt["stmt"] == "For":
                tgt = stmt.get("target", "")
                if tgt:
                    assigned.add(tgt)
                assigned.update(self._find_assigned_vars(stmt.get("body", [])))
            elif stmt["stmt"] == "Try":
                assigned.update(self._find_assigned_vars(stmt.get("body", [])))
                for h in stmt.get("handlers", []):
                    assigned.update(self._find_assigned_vars(h.get("body", [])))
            elif stmt["stmt"] == "Match":
                for c in stmt.get("cases", []):
                    assigned.update(self._find_assigned_vars(c.get("body", [])))
            # Also find walrus (NamedExpr) targets in all expressions
            self._find_named_expr_targets(stmt, assigned)
        return assigned

    def _find_named_expr_targets(self, obj: Any, targets: Set[str]) -> None:
        """Recursively walk an IR object to find NamedExpr targets (walrus operator)."""
        if isinstance(obj, dict):
            if obj.get("type") == "NamedExpr":
                targets.add(obj["target"])
            for k, v in obj.items():
                if k == "stmt":
                    continue
                self._find_named_expr_targets(v, targets)
        elif isinstance(obj, list):
            for item in obj:
                self._find_named_expr_targets(item, targets)

    def _find_ghost_vars(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Collect ghost variable names from GhostAssign IR nodes."""
        ghosts = set()
        for stmt in stmts:
            if stmt["stmt"] == "GhostAssign":
                ghosts.add(stmt["target"])
            elif stmt["stmt"] == "While":
                ghosts.update(self._find_ghost_vars(stmt["body"]))
            elif stmt["stmt"] == "If":
                ghosts.update(self._find_ghost_vars(stmt.get("body", [])))
                ghosts.update(self._find_ghost_vars(stmt.get("orelse", [])))
            elif stmt["stmt"] == "For":
                ghosts.update(self._find_ghost_vars(stmt.get("body", [])))
        return ghosts

    def _match_pattern_cond(self, pat: Dict[str, Any], subject: str, local_refs) -> str:
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

    def _find_array_and_dict_vars(self, stmts: List[Dict[str, Any]]) -> tuple:
        """Find variables assigned array or dict values (for correct pre-declaration)."""
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
                    a, d = self._find_array_and_dict_vars(stmt[key])
                    array_vars |= a
                    dict_vars |= d
            if stmt.get("stmt") == "While":
                a, d = self._find_array_and_dict_vars(stmt.get("body", []))
                array_vars |= a
                dict_vars |= d
            if stmt.get("stmt") == "For":
                a, d = self._find_array_and_dict_vars(stmt.get("body", []))
                array_vars |= a
                dict_vars |= d
            if stmt.get("stmt") == "Try":
                a, d = self._find_array_and_dict_vars(stmt.get("body", []))
                array_vars |= a
                dict_vars |= d
                for h in stmt.get("handlers", []):
                    a, d = self._find_array_and_dict_vars(h.get("body", []))
                    array_vars |= a
                    dict_vars |= d
        return array_vars, dict_vars

    def _find_lambda_vars(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Find variables whose first assignment is a Lambda expression."""
        lambda_vars = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Assign":
                val = stmt.get("value", {})
                if isinstance(val, dict) and val.get("type") == "Lambda":
                    lambda_vars.add(stmt.get("target", ""))
            for key in ("body", "orelse"):
                if key in stmt:
                    lambda_vars |= self._find_lambda_vars(stmt[key])
            if stmt.get("stmt") == "While":
                lambda_vars |= self._find_lambda_vars(stmt.get("body", []))
            if stmt.get("stmt") == "For":
                lambda_vars |= self._find_lambda_vars(stmt.get("body", []))
            if stmt.get("stmt") == "Match":
                for c in stmt.get("cases", []):
                    lambda_vars |= self._find_lambda_vars(c.get("body", []))
        return lambda_vars

    def _has_continue(self, stmts: List[Dict[str, Any]]) -> bool:
        """Check if statements contain a Continue node (not crossing For/While boundaries)."""
        for stmt in stmts:
            if stmt["stmt"] == "Continue":
                return True
            if stmt["stmt"] == "If":
                if (self._has_continue(stmt.get("body", [])) or
                        self._has_continue(stmt.get("orelse", []))):
                    return True
        return False

    def _uses_continue(self, stmts: List[Dict[str, Any]]) -> bool:
        """Recursively check if any statement uses Continue (crosses all boundaries)."""
        for stmt in stmts:
            if stmt["stmt"] == "Continue":
                return True
            for key in ("body", "orelse"):
                if key in stmt and self._uses_continue(stmt[key]):
                    return True
        return False

    def _uses_break(self, stmts: List[Dict[str, Any]]) -> bool:
        """Recursively check if any statement uses Break."""
        for stmt in stmts:
            if stmt["stmt"] == "Break":
                return True
            for key in ("body", "orelse"):
                if key in stmt and self._uses_break(stmt[key]):
                    return True
        return False

    def _collect_user_exceptions(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Collect ALL user exception type names (raised + caught) for module-level declarations."""
        result: Set[str] = set()
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
                    result |= self._collect_user_exceptions(h.get("body", []))
            for key in ("body", "orelse"):
                if key in stmt:
                    result |= self._collect_user_exceptions(stmt[key])
        return result

    def _collect_escaping_exceptions(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Collect exceptions that escape (raised but not fully caught at this level)."""
        raised: Set[str] = set()
        caught: Set[str] = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Raise" and stmt.get("exc_type"):
                raised.add(stmt["exc_type"])
            if stmt.get("stmt") == "Try":
                # Exceptions raised inside try body that are caught by handlers
                inner_raised = self._collect_escaping_exceptions(stmt.get("body", []))
                for h in stmt.get("handlers", []):
                    exc = h.get("exc_type")
                    if exc:
                        for ep in exc.split("|"):
                            ep = ep.strip()
                            if ep:
                                caught.add(ep)
                    raised |= self._collect_escaping_exceptions(h.get("body", []))
                raised |= (inner_raised - caught)
                continue
            for key in ("body", "orelse"):
                if key in stmt:
                    raised |= self._collect_escaping_exceptions(stmt[key])
        return raised

    def _has_direct_return(self, stmts: List[Dict[str, Any]]) -> bool:
        """Check if stmts contain a Return NOT inside a nested While loop.

        Recurses into If branches but stops at While/For boundaries so each
        loop level handles only its own in-loop returns.
        """
        for stmt in stmts:
            stype = stmt.get("stmt")
            if stype == "Return":
                return True
            if stype == "If":
                if (self._has_direct_return(stmt.get("body", [])) or
                        self._has_direct_return(stmt.get("orelse", []))):
                    return True
            # Do NOT recurse into While or For — they handle their own returns
        return False

    def _has_in_loop_return(self, stmts: List[Dict[str, Any]]) -> bool:
        """Recursively check if any While/For loop in stmts contains a direct Return."""
        for stmt in stmts:
            stype = stmt.get("stmt")
            if stype in ("While", "For"):
                if (self._has_direct_return(stmt.get("body", [])) or
                        self._has_in_loop_return(stmt.get("body", []))):
                    return True
            elif stype == "If":
                for key in ("body", "orelse"):
                    if key in stmt and self._has_in_loop_return(stmt[key]):
                        return True
        return False

    def _has_early_return(self, stmts: List[Dict[str, Any]]) -> bool:
        """Check if stmts have a return inside an if-block followed by more code."""
        for i, stmt in enumerate(stmts):
            stype = stmt.get("stmt")
            if stype == "If":
                has_ret = self._has_direct_return(stmt.get("body", []))
                has_rest = (i < len(stmts) - 1)
                if has_ret and has_rest:
                    return True
                if self._has_early_return(stmt.get("body", [])):
                    return True
                if self._has_early_return(stmt.get("orelse", [])):
                    return True
            elif stype in ("For", "While"):
                if self._has_early_return(stmt.get("body", [])):
                    return True
        return False

    def _uses_for(self, stmts: List[Dict[str, Any]]) -> bool:
        """Recursively check if any statement is a For loop."""
        for stmt in stmts:
            if stmt["stmt"] == "For":
                return True
            for key in ("body", "orelse"):
                if key in stmt and self._uses_for(stmt[key]):
                    return True
        return False

    def _uses_subscript(self, obj: Any) -> bool:
        """Recursively check if any expression or statement contains a Subscript node."""
        if isinstance(obj, dict):
            if obj.get("type") == "Subscript":
                return True
            return any(self._uses_subscript(v) for v in obj.values())
        if isinstance(obj, list):
            return any(self._uses_subscript(item) for item in obj)
        return False

    def _uses_minmax(self, obj: Any) -> bool:
        """Recursively check if any Call node uses min() or max() with 2 arguments."""
        if isinstance(obj, dict):
            if (obj.get("type") == "Call" and
                    obj.get("func") in ("min", "max") and
                    len(obj.get("args", [])) == 2):
                return True
            return any(self._uses_minmax(v) for v in obj.values())
        if isinstance(obj, list):
            return any(self._uses_minmax(item) for item in obj)
        return False

    def _is_recursive(self, name: str, obj: Any) -> bool:
        """Recursively check if any Call node calls the function `name`."""
        if isinstance(obj, dict):
            if obj.get("type") == "Call" and obj.get("func") == name:
                return True
            return any(self._is_recursive(name, v) for v in obj.values())
        if isinstance(obj, list):
            return any(self._is_recursive(name, item) for item in obj)
        return False

    def _uses_string(self, obj: Any) -> bool:
        """Recursively check if any node has type String."""
        if isinstance(obj, dict):
            if obj.get("type") == "String":
                return True
            return any(self._uses_string(v) for v in obj.values())
        if isinstance(obj, list):
            return any(self._uses_string(item) for item in obj)
        return False

    def _uses_sum(self, obj: Any) -> bool:
        """Recursively check if any node has type Sum."""
        if isinstance(obj, dict):
            if obj.get("type") == "Sum":
                return True
            return any(self._uses_sum(v) for v in obj.values())
        if isinstance(obj, list):
            return any(self._uses_sum(item) for item in obj)
        return False

    def _uses_divmod(self, stmts: List[Dict[str, Any]]) -> bool:
        """Check if any statement body uses div or mod operations."""
        def _check(obj: Any) -> bool:
            if isinstance(obj, dict):
                if obj.get("type") == "BinOp" and obj.get("op") in ("div", "/", "%"):
                    return True
                return any(_check(v) for v in obj.values())
            if isinstance(obj, list):
                return any(_check(item) for item in obj)
            return False
        return _check(stmts)

    def _find_append_targets(self, stmts: List[Dict[str, Any]]) -> set:
        """Return set of array names that have .append() calls in the body."""
        result = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Expr":
                val = stmt.get("value", {})
                if val.get("type") == "Call":
                    func = val.get("func", "")
                    if func.endswith(".append"):
                        arr_name = func.rsplit(".", 1)[0]
                        # Sanitize: replace dots for valid WhyML identifiers
                        result.add(arr_name.replace(".", "_"))
            for key in ("body", "orelse"):
                if key in stmt:
                    result |= self._find_append_targets(stmt[key])
        return result

    def _find_return_type(self, stmts: List[Dict[str, Any]]) -> str:
        """Infer the function return type: 'unit' if no return, 'int', 'string', or a tuple type string."""
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
            return "unit"  # only bare returns (no value) → void function

        for stmt in stmts:
            if stmt["stmt"] == "Return" and stmt.get("value"):
                val = stmt["value"]
                if val.get("type") == "Tuple":
                    n = len(val.get("elts", []))
                    return "(" + ", ".join(["int"] * n) + ")"
                if val.get("type") == "String":
                    return "int"  # model strings as int hashes
            for key in ("body", "orelse"):
                if key in stmt:
                    result = self._find_return_type(stmt[key])
                    if result not in ("int", "unit"):
                        return result
            if stmt.get("stmt") == "Match":
                for c in stmt.get("cases", []):
                    result = self._find_return_type(c.get("body", []))
                    if result not in ("int", "unit"):
                        return result
        return "int"

    def _expr_to_whyml(self, expr: Dict[str, Any], local_refs: Set[str],
                       invariant_ctx: bool = False,
                       subst: Dict[str, str] = None) -> str:
        """Recursively translates an expression dictionary into a WhyML string.
        When invariant_ctx is True, FieldGet emits bare field names (for record invariants).
        subst: optional name substitution dict applied before local_refs lookup (e.g. for-loop vars)."""
        if not expr: return ""
        
        t = expr["type"]
        if t == "Var":
            name = expr["name"]
            if subst and name in subst:
                name = subst[name]
            # Array locals don't need dereference (not in a ref)
            if name in getattr(self, '_array_locals', set()):
                return self._whyml_ident(name)
            # Lambda locals don't need dereference (let-bound, not ref)
            if name in getattr(self, '_lambda_locals', set()):
                return self._whyml_ident(name)
            # If it's a local mutable variable, we must dereference it with '!'
            if name in local_refs:
                return f"!{self._whyml_ident(name)}"
            # If it's a known parameter or 'self', return as-is (with safe name)
            if name in self._current_params or name == "self":
                return self._whyml_ident(name) if name != "self" else name
            # Otherwise it's an external reference (imported module, global) — abstract constant
            safe = self._whyml_ident(name)
            self._add_abstract_op(f"val constant {safe} : int")
            return safe
            
        elif t == "Number":
            # Why3 integers are unbounded, so format without decimal points
            return str(int(expr["value"]))

        elif t == "String":
            escaped = expr["value"].replace('\\', '\\\\').replace('"', '\\"')
            # Model strings as int hashes everywhere for type consistency
            return str(hash(f'"{escaped}"') % 2147483647)
            
        elif t == "Result":
            return "result"
            
        elif t == "BinOp":
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
                    # In spec context, use bool operators directly
                    return f"({left_b} {op} {right_b})"
                else:
                    # In body context, Python's and/or return int.
                    # Use if-then-else to convert bool result back to int,
                    # avoiding abstract vals that can't handle mixed bool/int args.
                    return f"(if {left_b} {op} {right_b} then 1 else 0)"
            elif expr["op"] == "in":
                # Containment check: x in collection
                rhs = expr.get("right", {})
                if rhs.get("type") == "Tuple":
                    # Expand x in (a, b, c) → x = a || x = b || x = c
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
                if rhs.get("type") == "Tuple":
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
                # Bitwise/power ops: model as abstract int operations
                op_names = {"&": "bit_and", "|": "bit_or", "^": "bit_xor",
                            "<<": "bit_lshift", ">>": "bit_rshift", "**": "py_pow"}
                op_fn = op_names[expr["op"]]
                self._add_abstract_op(f"val {op_fn} (x: int) (y: int) : int")
                return f"({op_fn} {left} {right})"
            elif expr["op"] == "?":
                # Fallback for unmapped operators
                self._add_abstract_op("val unknown_op (x: int) (y: int) : int")
                return f"(unknown_op {left} {right})"
            return f"({left} {op} {right})"
            
        elif t == "UnaryOp":
            e = self._expr_to_whyml(expr["expr"], local_refs, invariant_ctx, subst)
            op = self._op(expr["op"])
            if op == "+":
                return e  # WhyML has no unary +; it's the identity
            if op == "not":
                e = self._to_bool(e, expr["expr"])
            return f"({op} {e})"
            
        elif t == "Old":
            inner = expr["expr"]
            if self.memory_model != "hoare" and inner.get("type") == "Subscript":
                value = self._expr_to_whyml(inner["value"], local_refs, invariant_ctx, subst)
                index = self._expr_to_whyml(inner["index"], local_refs, invariant_ctx, subst)
                return f"(Map.get (old !{self._heap_var}) ({value} + {index}))"
            e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
            return f"(old {e})"

        elif t == "FieldGet":
            if invariant_ctx:
                return expr['field']
            obj = expr['object']
            field = expr['field']
            safe_field = self._whyml_ident(field)
            decl_fields = getattr(self, '_all_record_fields', set())
            if field in decl_fields:
                return f"{obj}.{safe_field}"
            # Undeclared field: use abstract getter with hashed field name
            hash_field = hash(field) % 2147483647
            # Determine the type of obj for the abstract val signature
            self_type = getattr(self, '_current_self_type', None)
            if obj == "self" and self_type:
                name = f"getattr_{self_type}"
                self._add_abstract_op(f"val {name} (x: {self_type}) (f: int) : int")
            else:
                name = "getattr_2"
                self._add_abstract_op(f"val {name} (x: int) (f: int) : int")
                obj = self._coerce_to_int(obj)
            return f"({name} {obj} {hash_field})"

        elif t == "OldField":
            return f"(old {expr['object']}.{expr['field']})"
        
        elif t == "Call":
            func_name = expr["func"]
            args = [self._expr_to_whyml(a, local_refs, invariant_ctx, subst) for a in expr["args"]]
            if func_name == "len" and len(args) == 1:
                if self.memory_model == "hoare":
                    # Check if the argument is a known array
                    arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
                    var_name = arg_ir.get("name", "") if arg_ir.get("type") == "Var" else ""
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
                        return f"(length {args[0]})"
                    else:
                        self._add_abstract_op("val iter_length (x: int) : int")
                        return f"(iter_length {args[0]})"
                else:
                    arr_name = args[0].lstrip("!")
                    return f"{arr_name}_len"
            if func_name in ("min", "max") and len(args) == 2:
                fn = "MinMax.min" if func_name == "min" else "MinMax.max"
                return f"({fn} {args[0]} {args[1]})"
            if func_name == "isinstance" and len(args) == 2:
                a0 = args[0]
                type_arg = self._coerce_to_int(args[1])
                self_type = getattr(self, '_current_self_type', None)
                if a0 == "self" and self_type:
                    op_name = f"isinstance_check_{self_type}"
                    self._add_abstract_op(f"val {op_name} (x: {self_type}) (t: int) : bool")
                else:
                    op_name = "isinstance_check"
                    self._add_abstract_op("val isinstance_check (x: int) (t: int) : bool")
                return f"({op_name} {a0} {type_arg})"
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
                # str.join(iterable) — argument may be an array
                arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
                var_name = arg_ir.get("name", "") if arg_ir.get("type") == "Var" else ""
                is_array = (var_name in getattr(self, "_array_locals", set()) or
                            var_name in getattr(self, "_current_array1d_params", set()))
                if not is_array and var_name:
                    st = getattr(self, "_current_symbol_table", {})
                    if st.get(var_name) in ("list", "dict"):
                        is_array = True
                # Also detect inline array expressions: BinOp("*", ArrayLit, ...) or ArrayLit
                if not is_array:
                    at = arg_ir.get("type", "")
                    if at in ("ArrayLit", "ListLit", "ListComp"):
                        is_array = True
                    elif at == "BinOp" and arg_ir.get("op") == "*":
                        lt = arg_ir.get("left", {}).get("type", "")
                        rt = arg_ir.get("right", {}).get("type", "")
                        if lt in ("ArrayLit", "ListLit") or rt in ("ArrayLit", "ListLit"):
                            is_array = True
                # Check if the emitted WhyML starts with Array.make (catch-all)
                if not is_array and "Array.make" in args[0]:
                    is_array = True
                if is_array:
                    self._add_abstract_op(
                        "val join_array (a: array int) : int")
                    return f"(join_array {args[0]})"
                else:
                    self._add_abstract_op("val join_1 (x: int) : int")
                    return f"(join_1 {args[0]})"
            if func_name in ("str", "repr", "int", "bool", "abs") and len(args) == 1:
                wf = self._whyml_ident(func_name)
                self._add_abstract_op(f"val {wf}_conv (x: int) : int")
                return f"({wf}_conv {args[0]})"
            if func_name == "hasattr":
                a0 = args[0] if args else '0'
                a1 = self._coerce_str_arg(args[1] if len(args) > 1 else '0')
                self_type = getattr(self, '_current_self_type', None)
                if a0 == "self" and self_type:
                    op_name = f"hasattr_check_{self_type}"
                    self._add_abstract_op(f"val {op_name} (x: {self_type}) (a: int) : bool")
                else:
                    op_name = "hasattr_check"
                    self._add_abstract_op("val hasattr_check (x: int) (a: int) : bool")
                return f"({op_name} {a0} {a1})"
            # Dotted call (method or external module function)
            if "." in func_name:
                # Model as abstract function call — coerce string args to int
                safe_name = func_name.replace(".", "_")
                safe_name = self._whyml_ident(safe_name)
                coerced_args = [self._coerce_to_int(a) for a in args]
                nargs = len(coerced_args)
                # Include arity in name to avoid partial application conflicts
                arity_name = f"{safe_name}_{nargs}"
                if nargs == 0:
                    self._add_abstract_op(f"val {arity_name} () : int")
                    return f"({arity_name} ())"
                else:
                    params = " ".join(f"(x{i}: int)" for i in range(nargs))
                    self._add_abstract_op(f"val {arity_name} {params} : int")
                    return f"({arity_name} {' '.join(coerced_args)})"
            # Coerce args for non-dotted abstract calls too
            coerced_args = [self._coerce_to_int(a) for a in args]
            safe_fn = self._whyml_ident(func_name)
            # If the function is not a known local/parameter/module function, declare an abstract val
            if (func_name not in local_refs 
                    and func_name not in getattr(self, '_current_params', set())
                    and safe_fn not in getattr(self, '_module_func_names', set())):
                nargs = len(coerced_args)
                # Always include arity in name to avoid clashes with constants
                arity_fn = f"{safe_fn}_{nargs}"
                if nargs == 0:
                    self._add_abstract_op(f"val {arity_fn} () : int")
                else:
                    params = " ".join(f"(x{i}: int)" for i in range(nargs))
                    self._add_abstract_op(f"val {arity_fn} {params} : int")
                args_str = " ".join(coerced_args) if coerced_args else "()"
                return f"({arity_fn} {args_str})"
            args_str = " ".join(coerced_args) if coerced_args else "()"
            return f"({safe_fn} {args_str})"

        elif t == "Tuple":
            elts = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst) for e in expr.get("elts", [])]
            return f"({', '.join(elts)})"

        elif t == "Subscript":
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
            if self.memory_model == "hoare":
                # Check if the value is a known array variable
                var_name = value.get("name", "") if value.get("type") == "Var" else ""
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
                    # Non-array subscript (dict access, string indexing, etc.)
                    self._add_abstract_op("val subscript_get (x: int) (i: int) : int")
                    return f"(subscript_get {self._coerce_to_int(value_str)} {self._coerce_to_int(index)})"
            else:
                return f"(Map.get !{self._heap_var} ({value_str} + {index}))"

        elif t == "ArrayLit":
            # Array literal → model as a fresh empty array (abstract)
            return "(Array.make 1024 0)"

        elif t == "Forall":
            var = expr["var"]
            body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
            return f"(forall {var} : int. {body})"

        elif t == "Exists":
            var = expr["var"]
            body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
            return f"(exists {var} : int. {body})"

        elif t == "ArrayLen":
            if self.memory_model == "hoare":
                var = expr['var']
                deref = "!" if var in local_refs else ""
                return f"(length {deref}{var})"
            else:
                return f"{expr['var']}_len"

        elif t == "Valid":
            base = expr["base"]
            length = self._expr_to_whyml(expr["length"], local_refs, invariant_ctx, subst)
            if self.memory_model == "hoare":
                return f"({length} >= 0 && {length} <= length {base})"
            else:
                return f"(valid !{self._heap_var} {base} {length})"

        elif t == "Separated":
            if self.memory_model == "hoare":
                return "true"
            else:
                b1 = expr["base1"]
                l1 = self._expr_to_whyml(expr["len1"], local_refs, invariant_ctx, subst)
                b2 = expr["base2"]
                l2 = self._expr_to_whyml(expr["len2"], local_refs, invariant_ctx, subst)
                return f"(separated {b1} {l1} {b2} {l2})"

        elif t == "At":
            label = expr["label"]
            inner = expr["expr"]
            # PRE is the implicit function pre-state; Why3 uses `old` for this
            if label == "PRE":
                e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
                return f"(old {e})"
            if inner.get("type") == "Subscript" and self.memory_model != "hoare":
                value = self._expr_to_whyml(inner["value"], local_refs, invariant_ctx, subst)
                index = self._expr_to_whyml(inner["index"], local_refs, invariant_ctx, subst)
                return f"(Map.get ({self._heap_var} at {label}) ({value} + {index}))"
            else:
                e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
                return f"({e} at {label})"

        elif t == "Length2D":
            base = expr["base"]
            rows = self._expr_to_whyml(expr["rows"], local_refs, invariant_ctx, subst)
            cols = self._expr_to_whyml(expr["cols"], local_refs, invariant_ctx, subst)
            if self.memory_model == "hoare":
                return f"({base}.rows = {rows} && {base}.columns = {cols})"
            return "true"

        elif t == "Valid2D":
            base = expr["base"]
            row = self._expr_to_whyml(expr["row"], local_refs, invariant_ctx, subst)
            col = self._expr_to_whyml(expr["col"], local_refs, invariant_ctx, subst)
            if self.memory_model == "hoare":
                return f"(valid_index {base} {row} {col})"
            return "true"

        elif t == "Attribute":
            # Non-self attribute access: obj.attr
            obj_ir = expr.get("object", {})
            attr = expr.get("attr", "unknown")
            if isinstance(obj_ir, str):
                # Legacy format: object is a plain string
                return f"(get_{attr} {obj_ir})"
            obj_str = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
            self._add_abstract_op(f"val get_{attr} (x: int) : int")
            return f"(get_{attr} {obj_str})"

        elif t == "None":
            return "0"

        elif t == "Bool":
            if getattr(self, '_in_spec', False):
                return "true" if expr.get("value") else "false"
            return "1" if expr.get("value") else "0"

        elif t == "DictLit":
            # Abstract: dictionaries modeled as opaque int values
            self._add_abstract_op("val dict_new () : int")
            return "(dict_new ())"

        elif t == "SetLit":
            elts = expr.get("elts", [])
            if not elts:
                self._add_abstract_op("val set_empty () : int")
                return "(set_empty ())"
            self._add_abstract_op("val set_new (x: int) : int")
            return "(set_new 0)"

        elif t == "ListComp":
            self._add_abstract_op("val list_comp (x: int) : int")
            return "(list_comp 0)"

        elif t == "SetComp":
            self._add_abstract_op("val set_comp (x: int) : int")
            return "(set_comp 0)"

        elif t == "DictComp":
            self._add_abstract_op("val dict_comp (x: int) : int")
            return "(dict_comp 0)"

        elif t == "FString":
            # f-strings: in body context, model as abstract int combination
            parts = expr.get("parts", [])
            if not parts:
                return "0"
            result = self._coerce_str_arg(self._expr_to_whyml(parts[0], local_refs, invariant_ctx, subst))
            for part in parts[1:]:
                p = self._coerce_str_arg(self._expr_to_whyml(part, local_refs, invariant_ctx, subst))
                self._add_abstract_op("val str_concat (x: int) (y: int) : int")
                result = f"(str_concat {result} {p})"
            return result

        elif t == "IfExpr":
            test = self._expr_to_whyml(expr["test"], local_refs, invariant_ctx, subst)
            test = self._to_bool(test, expr["test"])
            body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
            orelse = self._expr_to_whyml(expr["orelse"], local_refs, invariant_ctx, subst)
            # Coerce branches to same type (int)
            body = self._coerce_to_int(body)
            orelse = self._coerce_to_int(orelse)
            return f"(if {test} then {body} else {orelse})"

        elif t == "Starred":
            val = self._expr_to_whyml(expr.get("value", {}), local_refs, invariant_ctx, subst)
            return val

        elif t == "UnknownPyExpr":
            return "0"

        elif t == "IsSorted":
            base = expr["base"]
            lo = self._expr_to_whyml(expr["lo"], local_refs, invariant_ctx, subst)
            hi = self._expr_to_whyml(expr["hi"], local_refs, invariant_ctx, subst)
            if self.memory_model == "hoare":
                return f"(forall _si : int. {lo} <= _si /\\ _si < {hi} - 1 -> {base}[_si] <= {base}[_si + 1])"
            return "true"

        elif t == "Sum":
            base = expr["base"]
            lo = self._expr_to_whyml(expr["lo"], local_refs, invariant_ctx, subst)
            hi = self._expr_to_whyml(expr["hi"], local_refs, invariant_ctx, subst)
            if self.memory_model == "hoare":
                return f"(pycsl_sum {base} {lo} {hi})"
            return "0"

        elif t == "NamedExpr":
            # Walrus: (x := expr) → side-effectful; emit assignment then return value
            target = self._whyml_ident(expr["target"])
            val = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx, subst)
            if target in local_refs:
                return f"(begin {target} := {val}; !{target} end)"
            else:
                local_refs.add(target)
                return f"(let {target} = ref {val} in !{target})"

        elif t == "Lambda":
            params = expr.get("params", [])
            body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
            param_str = " ".join(f"({self._whyml_ident(p)}: int)" for p in params) if params else "()"
            return f"(fun {param_str} -> {body})"

        elif t == "SliceAccess":
            arr = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx, subst)
            sl = expr["slice"]
            lo = self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst) if sl.get("lower") else "0"
            hi = self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst) if sl.get("upper") else f"(Array.length {arr})"
            self._add_abstract_op("val array_slice (a: array int) (lo: int) (hi: int) : array int")
            return f"(array_slice {arr} {lo} {hi})"

        elif t == "Slice":
            # Standalone slice object — shouldn't normally be emitted as a top-level expr
            return "0"

        return ""

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
            target = stmt["target"]
            safe_target = self._whyml_ident(target)
            op = stmt.get("op", "=")
            ghost_refs = local_refs | {target}
            val = self._expr_to_whyml(stmt["value"], ghost_refs)

            if target not in declared_refs:
                # First occurrence: declare ghost ref, scopes over rest
                declared_refs.add(target)
                local_refs.add(target)
                rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
                if not rest_code:
                    rest_code = f"{indent}()"
                if self._bounded_int:
                    return f"{indent}let ghost {safe_target} = ref ({val} : int{self._bounded_int}) in\n{rest_code}"
                return f"{indent}let ghost {safe_target} = ref {val} in\n{rest_code}"
            else:
                # Subsequent: ghost update
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

        elif s_type == "Assign":
            target = stmt["target"]
            safe_target = self._whyml_ident(target)
            val = self._expr_to_whyml(stmt["value"], local_refs)
            
            if target not in declared_refs:
                declared_refs.add(target)
                # Arrays are already mutable — don't wrap in ref
                is_array_val = val.startswith("(Array.make") or val == "(Array.make 1024 0)"
                is_dict_val = val.startswith("(dict_new")
                is_lambda_val = (stmt.get("value", {}).get("type") == "Lambda")
                is_slice_val = (stmt.get("value", {}).get("type") == "SliceAccess")
                if is_lambda_val:
                    code = f"{indent}let {safe_target} = {val} in\n"
                    self._lambda_locals.add(target)
                elif is_array_val or is_slice_val:
                    code = f"{indent}let {safe_target} = {val} in\n"
                    # Track as array local (no ! deref needed)
                    self._array_locals.add(target)
                elif is_dict_val:
                    code = f"{indent}let {safe_target} = ref {val} in\n"
                    self._dict_locals.add(target)
                elif self._bounded_int:
                    # With bounded ints, annotate the initial value for type inference
                    code = f"{indent}let {safe_target} = ref ({val} : int{self._bounded_int}) in\n"
                else:
                    # Coerce bool to int for ref declaration
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
                
                # NEW: WhyML requires an expression after `in`. 
                # If there are no more statements, return unit `()`
                if not rest_code:
                    rest_code = f"{indent}()"
                    
                return code + rest_code
            else:
                # Standard reassignment — coerce bool to int for ref assignment
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
                
        elif s_type == "TupleUnpack":
            targets = stmt["targets"]
            val_whyml = self._expr_to_whyml(stmt["value"], local_refs)
            safe_targets = [self._whyml_ident(t) for t in targets]
            # Fix abstract op return type: if value is a Call to an unknown function,
            # the abstract val was declared with `: int` but should return a tuple.
            val_ir = stmt.get("value", {})
            if val_ir.get("type") == "Call":
                func_name = val_ir.get("func", "")
                nargs = len(val_ir.get("args", []))
                safe_fn = self._whyml_ident(func_name)
                arity_fn = f"{safe_fn}_{nargs}"
                # Check if this function was registered as an abstract op
                if arity_fn in self._abstract_ops:
                    # Re-declare with tuple return type
                    tuple_ret = "(" + ", ".join(["int"] * len(targets)) + ")"
                    if nargs == 0:
                        self._abstract_ops[arity_fn] = f"val {arity_fn} () : {tuple_ret}"
                    else:
                        params = " ".join(f"(x{i}: int)" for i in range(nargs))
                        self._abstract_ops[arity_fn] = f"val {arity_fn} {params} : {tuple_ret}"
            # let (a_tmp, b_tmp) = expr in a := a_tmp; b := b_tmp
            tmp_names = [f"_tu_{t}" for t in safe_targets]
            pattern = ", ".join(tmp_names)
            lines = [f"{indent}let ({pattern}) = {val_whyml} in"]
            for tmp, st in zip(tmp_names, safe_targets):
                if st in local_refs:
                    lines.append(f"{indent}{st} := {tmp};")
                else:
                    local_refs.add(st)
                    lines.append(f"{indent}let {st} = ref {tmp} in")
            code = "\n".join(lines)

        elif s_type == "AugAssign":
            target = stmt["target"]
            safe_target = self._whyml_ident(target)
            val = self._expr_to_whyml(stmt["value"], local_refs)
            raw_op = stmt["op"]
            op = self._op(raw_op)
            # Bitwise/power ops → abstract function calls
            bitwise_ops = {"&": "bit_and", "|": "bit_or", "^": "bit_xor",
                           "<<": "bit_lshift", ">>": "bit_rshift", "**": "py_pow"}
            if raw_op in bitwise_ops:
                op_fn = bitwise_ops[raw_op]
                self._add_abstract_op(f"val {op_fn} (x: int) (y: int) : int")
                code = f"{indent}{safe_target} := ({op_fn} !{safe_target} {val})"
            else:
                # Unroll AugAssign: x += 1 becomes x := !x + 1
                code = f"{indent}{safe_target} := !{safe_target} {op} {val}"

        elif s_type == "FieldAssign":
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

        elif s_type == "FieldAugAssign":
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

        elif s_type == "ArraySet":
            arr = stmt["array"]
            # Detect 2D write: a[i][j] = v → ArraySet(array=Subscript(Var(a),i), index=j, ...)
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
                if self.memory_model == "hoare":
                    # Check if target is a known array
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
                        # Non-array subscript set → abstract operation
                        self._add_abstract_op("val subscript_set (x: int) (i: int) (v: int) : unit")
                        code = f"{indent}subscript_set {self._coerce_to_int(array_expr)} {self._coerce_to_int(index_expr)} {self._coerce_to_int(val_expr)}"
                else:
                    hv = self._heap_var
                    code = (f"{indent}{hv} := Map.set !{hv} "
                            f"({array_expr} + {index_expr}) {val_expr}")
            
        elif s_type == "While":
            test = self._expr_to_whyml(stmt["test"], local_refs)
            test = self._to_bool(test, stmt["test"])
            has_cont = self._has_continue(stmt.get("body", []))
            has_direct_ret = self._has_direct_return(stmt.get("body", []))

            # If in-loop returns are present, indent the loop inside a try block
            loop_indent = (indent + "  ") if has_direct_ret else indent
            inner_indent = loop_indent + "  "

            body_str = self._stmts_to_whyml(
                stmt["body"], local_refs, declared_refs.copy(), inner_indent, in_loop=True)

            loop_code = f"{loop_indent}while {test} do\n"
            self._in_spec = True
            for inv in stmt.get("invariants", []):
                inv_str = self._expr_to_whyml(inv, local_refs)
                loop_code += f"{inner_indent}invariant {{ {inv_str} }}\n"
            for var in stmt.get("variants", []):
                var_str = self._expr_to_whyml(var, local_refs)
                loop_code += f"{inner_indent}variant {{ {var_str} }}\n"
            self._in_spec = False
            if has_cont:
                loop_code += f"{inner_indent}try\n"
                loop_code += body_str + "\n"
                loop_code += f"{inner_indent}with PyCSL_Continue -> () end\n"
            else:
                loop_code += body_str + "\n"
            loop_code += f"{loop_indent}done"

            # Wrap with break handler if the body uses break
            has_break = self._uses_break(stmt.get("body", []))
            if has_break:
                loop_code = (f"{loop_indent}try\n{loop_code}\n"
                             f"{loop_indent}with PyCSL_Break -> () end")

            if has_direct_ret and not in_loop:
                # Wrap while loop + remaining statements in try…with Return r -> r end
                rest_code = self._stmts_to_whyml(
                    rest, local_refs, declared_refs, indent + "  ", in_loop)
                inner = loop_code
                if rest_code:
                    inner += ";\n" + rest_code
                return (f"{indent}try\n{inner}\n"
                        f"{indent}with Return r -> r end")

            code = loop_code

        elif s_type == "Return":
            val_ir = stmt.get("value")
            if val_ir is None:
                val = "()"
            else:
                # Check if returning an array local — coerce to int
                if val_ir.get("type") == "Var" and val_ir.get("name") in self._array_locals:
                    val = "0"
                else:
                    val = self._expr_to_whyml(val_ir, local_refs)
            use_raise = in_loop or getattr(self, '_has_early_ret', False)
            if use_raise:
                func_ret = getattr(self, '_func_return_type', 'int')
                if func_ret == "unit":
                    return f"{indent}raise Return_void"
                # Return exception expects int; coerce bare return and bool/tuple/array
                if val == "()":
                    val = "0"
                elif val == "true":
                    val = "1"
                elif val == "false":
                    val = "0"
                val = self._coerce_to_int(val)
                return f"{indent}raise (Return {val})"
            return f"{indent}{val}"

        elif s_type == "Continue":
            # Raise the continue exception caught by the enclosing For loop's try/with
            return f"{indent}raise PyCSL_Continue"

        elif s_type == "Assert":
            test_whyml = self._expr_to_whyml(stmt["test"], local_refs)
            test_whyml = self._to_bool(test_whyml, stmt["test"])
            msg = stmt.get("msg", "assertion")
            code = f'{indent}check {{ [@expl:{msg}] {test_whyml} }}'

        elif s_type == "Raise":
            exc_type = stmt.get("exc_type", "PyCSL_Exception")
            return f"{indent}raise {exc_type}"

        elif s_type == "If":
            test = self._expr_to_whyml(stmt["test"], local_refs)
            test = self._to_bool(test, stmt["test"])
            body = stmt.get("body", [])
            orelse = stmt.get("orelse", [])
            body_str = self._stmts_to_whyml(body, local_refs, declared_refs.copy(), indent + "  ", in_loop)
            if not body_str:
                body_str = f"{indent}  ()"
            body_returns = self._ends_with_return(body)

            if orelse:
                orelse_str = self._stmts_to_whyml(orelse, local_refs, declared_refs.copy(), indent + "  ", in_loop)
                if not orelse_str:
                    orelse_str = f"{indent}  ()"
                code = (f"{indent}if {test} then begin\n{body_str}\n"
                        f"{indent}end else begin\n{orelse_str}\n{indent}end")
                # Both branches return → expression form, rest is dead code
                if body_returns and self._ends_with_return(orelse):
                    return code
            elif body_returns and rest:
                # No else, body returns, remaining stmts form the else branch
                rest_str = self._stmts_to_whyml(rest, local_refs, declared_refs, indent + "  ", in_loop)
                if not rest_str:
                    rest_str = f"{indent}  ()"
                return (f"{indent}if {test} then begin\n{body_str}\n"
                        f"{indent}end else begin\n{rest_str}\n{indent}end")
            else:
                # if-without-else: if body returns a value (not unit),
                # add else branch to match types
                stripped = body_str.rstrip()
                # if-without-else: only add else branch if body returns a value
                # (bare expression not followed by a statement)
                last_line = stripped.split('\n')[-1].strip() if stripped else ""
                body_returns_value = (last_line.startswith("(") and 
                                      not last_line.startswith("()")  and
                                      "raise " not in last_line and
                                      "<-" not in last_line and
                                      ":=" not in last_line and
                                      "subscript_set" not in last_line)
                if body_returns_value:
                    code = f"{indent}if {test} then begin\n{body_str}\n{indent}end else begin\n{indent}  0\n{indent}end"
                else:
                    code = f"{indent}if {test} then begin\n{body_str}\n{indent}end"

        elif s_type == "For":
            target = stmt["target"]
            safe_target = self._whyml_ident(target)
            iter_ir = stmt["iter"]
            idx = f"_idx_{safe_target}"
            has_direct_ret = self._has_direct_return(stmt.get("body", []))
            loop_indent = (indent + "  ") if has_direct_ret else indent
            inner_indent = loop_indent + "  "

            body_local = local_refs | {target}
            body_declared = declared_refs.copy() | {target}
            inner_body = self._stmts_to_whyml(
                stmt.get("body", []), body_local, body_declared, inner_indent, True)
            if not inner_body:
                inner_body = f"{inner_indent}()"

            has_cont = self._has_continue(stmt.get("body", []))

            # Detect range(n) — emit an integer counter loop (no array needed)
            is_range = (iter_ir.get("type") == "Call" and
                        iter_ir.get("func") == "range" and
                        len(iter_ir.get("args", [])) == 1)

            if is_range:
                bound = self._expr_to_whyml(iter_ir["args"][0], local_refs)
                len_expr = bound
                elem_expr = f"!{idx}"   # the loop variable IS the counter
            elif iter_ir.get("type") == "Var" and self.memory_model == "hoare":
                # Check if the variable is a known array
                var_name = iter_ir.get("name", "")
                iter_expr = self._expr_to_whyml(iter_ir, local_refs)
                is_dict = var_name in getattr(self, "_dict_locals", set())
                is_array = not is_dict and (
                    var_name in getattr(self, "_array2d_params", set()) or
                    var_name in getattr(self, "_array_locals", set()) or
                    var_name in getattr(self, "_current_array1d_params", set()))
                if not is_array and not is_dict:
                    st = getattr(self, "_current_symbol_table", {})
                    if st.get(var_name) in ("list", "dict"):
                        is_array = True
                if is_array:
                    len_expr = f"length {iter_expr}"
                    elem_expr = f"{iter_expr}[!{idx}]"
                else:
                    # Non-array variable — model with abstract ops
                    self._add_abstract_op("val iter_length (x: int) : int")
                    self._add_abstract_op("val iter_get (x: int) (i: int) : int")
                    len_expr = f"(iter_length {iter_expr})"
                    elem_expr = f"(iter_get {iter_expr} !{idx})"
            elif self.memory_model != "hoare":
                iter_expr = self._expr_to_whyml(iter_ir, local_refs)
                len_expr = f"{iter_expr}_len"
                elem_expr = f"Map.get !{self._heap_var} ({iter_expr} + !{idx})"
            else:
                # Complex iterable (attribute access, function call result, tuple) —
                # model with abstract length/get operations
                iter_expr = self._expr_to_whyml(iter_ir, local_refs)
                iter_expr = self._coerce_to_int(iter_expr)
                self._add_abstract_op("val iter_length (x: int) : int")
                self._add_abstract_op("val iter_get (x: int) (i: int) : int")
                len_expr = f"(iter_length {iter_expr})"
                elem_expr = f"(iter_get {iter_expr} !{idx})"

            while_parts = [f"{loop_indent}while !{idx} < {len_expr} do"]
            # For range loops: substitute the loop variable with the counter ref
            # so invariants/variants using `i` render as `!_idx_i`, not the unbound `i`
            inv_subst = {target: idx} if is_range else None
            inv_refs = local_refs | {idx}
            self._in_spec = True
            for inv in stmt.get("invariants", []):
                inv_str = self._expr_to_whyml(inv, inv_refs, subst=inv_subst)
                while_parts.append(f"{inner_indent}invariant {{ {inv_str} }}")
            for var_ir in stmt.get("variants", []):
                var_str = self._expr_to_whyml(var_ir, inv_refs, subst=inv_subst)
                while_parts.append(f"{inner_indent}variant {{ {var_str} }}")
            self._in_spec = False

            if has_cont:
                while_parts.append(f"{inner_indent}try")
                while_parts.append(f"{inner_indent}  let {safe_target} = ref ({elem_expr}) in")
                while_parts.append(inner_body)
                while_parts.append(f"{inner_indent}with PyCSL_Continue -> () end;")
            else:
                while_parts.append(
                    f"{inner_indent}let {safe_target} = ref ({elem_expr}) in")
                while_parts.append(inner_body + ";")

            while_parts.append(f"{inner_indent}{idx} := !{idx} + 1")
            while_parts.append(f"{loop_indent}done")
            has_break = self._uses_break(stmt.get("body", []))
            while_code = "\n".join(while_parts)

            # Wrap the while loop with break handler if needed
            if has_break:
                while_code = (f"{loop_indent}try\n{while_code}\n"
                              f"{loop_indent}with PyCSL_Break -> () end")

            # Introduce the index ref following the same pattern as Assign
            if self._bounded_int:
                idx_decl = f"{loop_indent}let {idx} = ref (0 : int{self._bounded_int}) in\n{while_code}"
            else:
                idx_decl = f"{loop_indent}let {idx} = ref 0 in\n{while_code}"

            if has_direct_ret and not getattr(self, '_has_early_ret', False) and not in_loop:
                # Wrap for-loop in try…with Return (only at top-level, not nested)
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
            
        elif s_type == "Expr":
            # Expression statement (e.g., void function call)
            val = stmt.get("value", {})
            if val.get("type") == "Call":
                func = val.get("func", "")
                if func.endswith(".append") and self.memory_model == "hoare":
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

        elif s_type == "Try":
            # try/except → try ... with ExcType -> handler end
            body_stmts = stmt.get("body", [])
            handlers = stmt.get("handlers", [])
            # Pre-declare variables assigned inside try/handlers that may be
            # referenced after the try block (try creates its own scope in WhyML).
            try_assigned = self._find_assigned_vars(body_stmts)
            for h in handlers:
                try_assigned |= self._find_assigned_vars(h.get("body", []))
            pre_decls = ""
            for var in sorted(try_assigned):
                safe_var = self._whyml_ident(var)
                if safe_var not in declared_refs:
                    pre_decls += f"{indent}let {safe_var} = ref 0 in\n"
                    declared_refs.add(safe_var)
            body_str = self._stmts_to_whyml(body_stmts, local_refs, declared_refs.copy(), indent + "  ", in_loop)
            if not body_str:
                body_str = f"{indent}  ()"
            if handlers:
                code = f"{pre_decls}{indent}try\n{body_str}\n"
                for h in handlers:
                    exc = h.get("exc_type") or "PyCSL_Exception"
                    # Handle multi-exception (piped)
                    exc_parts = exc.split("|") if "|" in exc else [exc]
                    for ep in exc_parts:
                        ep = ep.strip()
                        handler_body = self._stmts_to_whyml(
                            h.get("body", []), local_refs, declared_refs.copy(), indent + "  ", in_loop)
                        if not handler_body:
                            handler_body = f"{indent}  ()"
                        code += f"{indent}with {ep} -> \n{handler_body}\n"
                code += f"{indent}end"
            else:
                code = f"{pre_decls}{body_str}"

        elif s_type == "Pass":
            code = f"{indent}()"

        elif s_type == "Break":
            # WhyML doesn't have break; model as exception
            code = f"{indent}raise PyCSL_Break"

        elif s_type == "Match":
            # Lower match/case to if/elif chain
            subject = self._expr_to_whyml(stmt["subject"], local_refs)
            cases = stmt.get("cases", [])
            lines = []
            for i, c in enumerate(cases):
                pat = c["pattern"]
                guard = c.get("guard")
                body_stmts = c.get("body", [])
                body_str = self._stmts_to_whyml(body_stmts, local_refs, declared_refs.copy(), indent + "  ", in_loop)
                if not body_str:
                    body_str = f"{indent}  ()"
                cond = self._match_pattern_cond(pat, subject, local_refs)
                if guard:
                    guard_str = self._expr_to_whyml(guard, local_refs)
                    guard_str = self._to_bool(guard_str, guard)
                    cond = f"({cond} && {guard_str})" if cond != "true" else guard_str
                if i == 0:
                    lines.append(f"{indent}if {cond} then begin")
                elif cond == "true":
                    lines.append(f"{indent}end else begin")
                else:
                    lines.append(f"{indent}end else if {cond} then begin")
                lines.append(body_str)
            lines.append(f"{indent}end")
            code = "\n".join(lines)

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
        if self.memory_model == "hoare":
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

    def transpile(self) -> str:
        """Entry point: converts the entire program to a .mlw string."""
        functions = self.ir.get("functions", [])
        type_decls = self.ir.get("type_decls", [])
        all_bodies = [func["body"] for func in functions]

        # Collect all declared record fields for FieldGet resolution
        self._all_record_fields = set()
        for td in type_decls:
            if td["kind"] == "record":
                for f in td.get("fields", []):
                    self._all_record_fields.add(f["name"])

        has_list_param = any(
            v in ("list", "dict") for func in functions
            for v in func.get("symbol_table", {}).values()
        )
        # Strings are now modeled as int hashes, so str params no longer trigger array use
        needs_matrix = any(func.get("array2d_params") for func in functions)
        if self.memory_model == "hoare":
            needs_array = has_list_param or \
                        any(self._uses_for(body) for body in all_bodies) or \
                        any(self._uses_subscript(body) for body in all_bodies) or \
                        any(self._uses_arrayset(body) for body in all_bodies)
        else:
            needs_array = False  # Heap models use map.Map, not array.Array
        needs_minmax = any(self._uses_minmax(body) for body in all_bodies)
        needs_continue = any(self._uses_continue(body) for body in all_bodies)
        needs_break = any(self._uses_break(body) for body in all_bodies)
        needs_return_exc = False
        needs_return_void = False
        for func in functions:
            has_ret = self._has_in_loop_return(func["body"]) or self._has_early_return(func["body"])
            if has_ret:
                ret_type = self._find_return_type(func["body"])
                if ret_type == "unit":
                    needs_return_void = True
                else:
                    needs_return_exc = True
        # Strings are modeled as int hashes, so string.String is never needed
        needs_string = False
        needs_sum = any(self._uses_sum(func) for func in functions)
        needs_divmod = any(self._uses_divmod(body) for body in all_bodies)
        bounded_sizes = {func["bounded_int"] for func in functions if func.get("bounded_int")}
        user_exceptions: Set[str] = set()
        for body in all_bodies:
            user_exceptions |= self._collect_user_exceptions(body)

        out = [
            "module PyCSL_Program",
            "  use int.Int",
            "  use int.EuclideanDivision",
            "  use ref.Ref",
        ]
        for bsz in sorted(bounded_sizes):
            out.append(f"  use mach.int.Int{bsz}")
        if needs_string:
            out.append("  use string.String")
        if self.memory_model == "hoare":
            if needs_array:
                out.append("  use array.Array")
            if needs_matrix:
                out.append("  use matrix.Matrix")
            if needs_minmax:
                out.append("  use int.MinMax")
        else:
            out.append("  use map.Map")
            if needs_minmax:
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
        if needs_continue:
            out.append("")
            out.append("  exception PyCSL_Continue")
        if needs_break:
            out.append("")
            out.append("  exception PyCSL_Break")
        if needs_return_exc:
            out.append("")
            out.append("  exception Return int")
        if needs_return_void:
            out.append("")
            out.append("  exception Return_void")
        for exc_name in sorted(user_exceptions):
            out.append(f"  exception {exc_name}")
        if needs_sum:
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
        if needs_divmod:
            out.append("")
            out.append("  let pycsl_div (x: int) (y: int) : int")
            out.append("    requires { [@expl:division by zero] y <> 0 }")
            out.append("    ensures { result = div x y }")
            out.append("  = div x y")
            out.append("")
            out.append("  let pycsl_mod (x: int) (y: int) : int")
            out.append("    requires { [@expl:modulo by zero] y <> 0 }")
            out.append("    ensures { result = mod x y }")
            out.append("  = mod x y")
        out.append("")

        # Emit record type declarations (Level 2) with optional invariants (Level 3)
        declared_types = set()
        for td in type_decls:
            if td["kind"] == "record":
                type_name = td["name"].lower()
                declared_types.add(type_name)
                field_strs = []
                for f in td["fields"]:
                    prefix = "mutable " if f.get("mutable") else ""
                    ftype = f['type']
                    # Complex code: map string fields to int to avoid type conflicts
                    if ftype == "string":
                        ftype = "int"
                    field_strs.append(f"{prefix}{f['name']}: {ftype}")
                out.append(f"  type {type_name} = {{ {'; '.join(field_strs)} }}")

                # Level 3: class invariants
                class_invs = td.get("class_invariants", [])
                if class_invs:
                    self._in_spec = True
                    for inv in class_invs:
                        inv_str = self._expr_to_whyml(inv, set(), invariant_ctx=True)
                        out.append(f"    invariant {{ {inv_str} }}")
                    self._in_spec = False
                    # Witness (`by` clause) proving the type is inhabited.
                    # Try the __init__ defaults first; if they don't satisfy
                    # the invariant, attempt small fallback values.
                    defaults = td.get("field_defaults", {})
                    field_names = [f["name"] for f in td["fields"]]

                    def _build_witness(vals: dict) -> str:
                        return "; ".join(
                            f"{fn} = {vals.get(fn, 0)}" for fn in field_names
                        )

                    def _check_witness(vals: dict, invs: list) -> bool:
                        """Quick sanity check: evaluate invariant with witness values."""
                        for inv_ir in invs:
                            try:
                                expr = self._expr_to_whyml(inv_ir, set(), invariant_ctx=True)
                                # Simple eval: replace field names with values
                                test_expr = expr
                                for fn in field_names:
                                    test_expr = test_expr.replace(fn, str(vals.get(fn, 0)))
                                # Try to evaluate the boolean expression
                                test_expr = test_expr.replace("=", "==").replace("!==", "!=").replace("<==", "<=").replace(">==", ">=")
                                if not eval(test_expr):  # noqa: S307
                                    return False
                            except Exception:
                                pass  # can't evaluate — assume OK
                        return True

                    witness_vals = {fn: defaults.get(fn, 0) for fn in field_names}
                    if not _check_witness(witness_vals, class_invs):
                        # Try fallback combinations
                        for combo in [
                            {fn: 0 for fn in field_names},
                            {fn: 1 for fn in field_names},
                            {fn: 10 for fn in field_names},
                        ]:
                            if _check_witness(combo, class_invs):
                                witness_vals = combo
                                break

                    out.append(f"    by {{ {_build_witness(witness_vals)} }}")

                out.append("")

        # Emit opaque type aliases for classes used in methods but not declared as records
        for func in functions:
            if func.get("kind") == "method" and func.get("self_type"):
                st = func["self_type"].lower()
                if st not in declared_types:
                    declared_types.add(st)
                    out.append(f"  type {st} = int")
                    out.append("")

        # Collect all function names in the module so we don't create abstract vals for them
        self._module_func_names = {self._whyml_ident(func["name"]) for func in functions}

        for func in functions:
            name = self._whyml_ident(func["name"])
            body_stmts = func["body"]
            is_method = func.get("kind") == "method"
            bounded_int = func.get("bounded_int")
            int_type = f"int{bounded_int}" if bounded_int else "int"
            self._bounded_int = bounded_int

            # Determine which variables are mutated locally
            local_refs = self._find_assigned_vars(body_stmts)
            ghost_vars = self._find_ghost_vars(body_stmts)
            symbol_table = func.get("symbol_table", {})
            # Track current function's parameters for Var resolution
            self._current_params = set(symbol_table.keys()) | local_refs | ghost_vars
            self._array_locals = set()  # Reset per function
            self._dict_locals = set()   # Reset per function
            self._lambda_locals = set()  # Reset per function
            self._current_symbol_table = symbol_table  # For type lookups in Subscript
            array2d_params = set(func.get("array2d_params", []))
            array1d_params = set(func.get("array1d_params", []))
            self._current_array1d_params = array1d_params
            self._array2d_params = array2d_params  # used by _expr_to_whyml / _stmts_to_whyml

            if is_method:
                # Method: prepend (self: <type>) as first arg, no ref_params logic
                self_type = func["self_type"].lower()
                self._current_self_type = self_type
                args = list(symbol_table.keys())
                param_parts = [f"(self: {self_type})"]
                for arg in args:
                    if arg in local_refs or arg in ghost_vars:
                        continue
                    safe = self._whyml_ident(arg)
                    if arg in array2d_params:
                        param_parts.append(f"({safe}: matrix {int_type})")
                    elif arg in array1d_params or symbol_table.get(arg) in ("list", "dict"):
                        if self.memory_model == "hoare":
                            param_parts.append(f"({safe}: array {int_type})")
                        else:
                            param_parts.append(f"({safe}: loc) ({safe}_len: int)")
                    elif symbol_table.get(arg) == "str":
                        param_parts.append(f"({safe}: {int_type})")
                    else:
                        param_parts.append(f"({safe}: {int_type})")
                args_str = " ".join(param_parts)
            else:
                # Standalone function: use existing ref_params logic for obj_* vars
                self._current_self_type = None
                ref_params = {v for v in symbol_table if v in local_refs and v.startswith("obj_")}
                args = [v for v in symbol_table if (v not in local_refs or v in ref_params) and v not in ghost_vars]

                def _param_type(arg: str) -> str:
                    safe = self._whyml_ident(arg)
                    if arg in ref_params:
                        return f"({safe}: ref {int_type})"
                    if arg in array2d_params:
                        return f"({safe}: matrix {int_type})"
                    if arg in array1d_params or symbol_table.get(arg) in ("list", "dict"):
                        if self.memory_model == "hoare":
                            return f"({safe}: array {int_type})"
                        else:
                            return f"({safe}: loc) ({safe}_len: int)"
                    if symbol_table.get(arg) == "str":
                        return f"({safe}: {int_type})"
                    return f"({safe}: {int_type})"

                args_str = " ".join(_param_type(arg) for arg in args)

            return_type = self._find_return_type(body_stmts)
            self._func_return_type = return_type  # track for early return handling
            # Use explicit return annotation if body inference defaults to int
            ret_ann = func.get("return_annotation")
            if ret_ann == "list" and return_type == "int":
                return_type = "array int"
            # Bounded integers: replace int with intN in return type
            if bounded_int and return_type == "int":
                return_type = int_type
            # Track tuple arity for \result[i] postcondition support
            if return_type.startswith("(") and return_type.endswith(")"):
                self._current_tuple_arity = return_type.count(",") + 1
            else:
                self._current_tuple_arity = 0

            func_variants = func.get("function_variants", [])
            func_diverges = func.get("diverges", False)
            func_trusted = func.get("trusted", False)
            func_pure = func.get("pure", False)
            is_recursive = self._is_recursive(name, body_stmts)
            use_rec = bool(func_variants) or is_recursive

            # Pure functions that have no mutable locals can be emitted as
            # `let function` so they are usable in specifications.
            can_emit_as_logic = func_pure and not local_refs and not is_method

            if func_trusted:
                # Trusted: emit val declaration (no body, contracts become axioms)
                if args_str:
                    out.append(f"  val {name} {args_str} : {return_type}")
                else:
                    out.append(f"  val {name} () : {return_type}")
            elif can_emit_as_logic:
                let_kw = "let rec function" if use_rec else "let function"
                if args_str:
                    out.append(f"  {let_kw} {name} {args_str} : {return_type}")
                else:
                    out.append(f"  {let_kw} {name} () : {return_type}")
            else:
                let_kw = "let rec" if use_rec else "let"
                if args_str:
                    out.append(f"  {let_kw} {name} {args_str} : {return_type}")
                else:
                    out.append(f"  {let_kw} {name} () : {return_type}")

            # Contracts — methods use empty local_refs for spec (FieldGet handles itself)
            contracts = func.get("contracts", {})
            spec_refs = set() if is_method else (ref_params if not is_method else set())
            self._in_spec = True
            for req in contracts.get("requires", []):
                req_str = self._expr_to_whyml(req, spec_refs)
                out.append(f"    requires {{ {req_str} }}")

            for ens in contracts.get("ensures", []):
                ens_str = self._expr_to_whyml(ens, spec_refs)
                out.append(f"    ensures  {{ {ens_str} }}")

            # Frame condition from \assigns (typed/store models only)
            for fl in self._emit_frame_condition(contracts.get("assigns", []), spec_refs):
                out.append(fl)

            # Function variant / diverges
            for fv in func_variants:
                v_expr = self._expr_to_whyml(fv["expr"], spec_refs)
                if fv.get("ordering"):
                    out.append(f"    variant  {{ {v_expr} }} with {fv['ordering']}")
                else:
                    out.append(f"    variant  {{ {v_expr} }}")
            if func_diverges:
                out.append("    diverges")
            # Exception specification from #@ raises contracts and body analysis
            raises_contracts = contracts.get("raises", [])
            func_exceptions = self._collect_escaping_exceptions(body_stmts)
            if raises_contracts:
                for rc in raises_contracts:
                    cond_str = self._expr_to_whyml(rc["condition"], spec_refs)
                    out.append(f"    raises {{ {rc['exc_type']} -> {cond_str} }}")
                # Also ensure all body-raised exceptions are declared
                declared_exc = {rc["exc_type"] for rc in raises_contracts}
                for exc in sorted(func_exceptions - declared_exc):
                    out.append(f"    raises {{ {exc} }}")
            elif func_exceptions:
                exc_list = ", ".join(sorted(func_exceptions))
                out.append(f"    raises {{ {exc_list} }}")
            self._in_spec = False

            # Trusted functions: no body (val declaration only)
            if func_trusted:
                out.append("")
                continue

            out.append("  =")

            # Detect arrays with .append() — emit length tracking refs
            append_targets = self._find_append_targets(body_stmts)

            # Body — set flag for early returns
            self._has_early_ret = self._has_early_return(body_stmts)
            # Pre-declare ALL local ref variables at function entry to avoid
            # WhyML scoping issues (variables first assigned inside if/while/for/try
            # branches would be scoped to that branch otherwise).
            body_array_vars, body_dict_vars = self._find_array_and_dict_vars(body_stmts)
            body_lambda_vars = self._find_lambda_vars(body_stmts)
            pre_decl_vars = set()
            for v in local_refs:
                if v in ghost_vars:
                    continue
                if not is_method and v in (ref_params if not is_method else set()):
                    continue
                # Skip array/dict/lambda vars — they need special declarations
                if v in body_array_vars or v in body_dict_vars or v in body_lambda_vars:
                    continue
                pre_decl_vars.add(v)
            # Mark all pre-declared vars as already declared
            if is_method:
                initial_declared = {self._whyml_ident(v) for v in pre_decl_vars}
            else:
                initial_declared = set(ref_params) | {self._whyml_ident(v) for v in pre_decl_vars}
            if is_method:
                body_code = self._stmts_to_whyml(body_stmts, local_refs | {f"{t}_len" for t in append_targets}, initial_declared, "    ")
            else:
                body_code = self._stmts_to_whyml(body_stmts, local_refs | {f"{t}_len" for t in append_targets}, initial_declared, "    ")
            # Prepend ref declarations for pre-declared vars (non-array, non-dict)
            for var in sorted(pre_decl_vars):
                safe_var = self._whyml_ident(var)
                if bounded_int:
                    body_code = f"    let {safe_var} = ref (0 : int{bounded_int}) in\n{body_code}"
                else:
                    body_code = f"    let {safe_var} = ref 0 in\n{body_code}"

            # Prepend length ref declarations for append targets
            for tgt in sorted(append_targets):
                safe_tgt = self._whyml_ident(tgt)
                if bounded_int:
                    body_code = f"    let {safe_tgt}_len = ref (0 : int{bounded_int}) in\n{body_code}"
                else:
                    body_code = f"    let {safe_tgt}_len = ref 0 in\n{body_code}"
                # If this target is not a parameter, declare the array too
                if tgt not in local_refs and tgt not in (ref_params if not is_method else set()):
                    body_code = f"    let {safe_tgt} = Array.make 1024 0 in\n{body_code}"
                    self._array_locals.add(tgt)
            # Empty bodies (from `pass`-only functions) must emit `()` — the
            # WhyML unit value — so the parser doesn't treat the next `let` as
            # the current function's body.
            if not body_code.strip():
                body_code = "    ()"
            # Wrap entire function body in try/catch for early returns
            if self._has_early_ret:
                if return_type == "unit":
                    body_code = f"    try\n{body_code}\n    with Return_void -> () end"
                else:
                    body_code = f"    try\n{body_code}\n    with Return r -> r end"
            out.append(body_code)
            out.append("")

        out.append("end")

        # Insert abstract val declarations (collected during transpilation)
        if self._abstract_ops:
            # Find insertion point: right after exceptions/type-decls, before functions
            # We insert them right after the blank line before functions
            insert_marker = "  (* abstract operations *)"
            # Find the position in out to insert — after type decls, before let declarations
            insert_idx = None
            for i, line in enumerate(out):
                if line.strip().startswith("let ") or line.strip().startswith("let rec "):
                    insert_idx = i
                    break
                if line.strip().startswith("val ") and "ghost" not in line:
                    insert_idx = i
                    break
            if insert_idx is None:
                insert_idx = len(out) - 1  # before 'end'
            abs_lines = ["", "  (* Abstract operations for unsupported Python patterns *)"]
            for decl in sorted(self._abstract_ops.values()):
                abs_lines.append(f"  {decl}")
            abs_lines.append("")
            for line in reversed(abs_lines):
                out.insert(insert_idx, line)

        return "\n".join(out)
