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
        # Coerce int → bool
        return f"({whyml_str} <> 0)"

    @staticmethod
    def _coerce_str_arg(whyml_str: str) -> str:
        """Convert a WhyML string literal to an int hash for abstract val arguments."""
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(hash(whyml_str) % 2147483647)
        return whyml_str

    @staticmethod
    def _coerce_to_int(whyml_str: str) -> str:
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
            elif stmt["stmt"] == "While":
                assigned.update(self._find_assigned_vars(stmt["body"]))
            elif stmt["stmt"] == "If":
                assigned.update(self._find_assigned_vars(stmt.get("body", [])))
                assigned.update(self._find_assigned_vars(stmt.get("orelse", [])))
            elif stmt["stmt"] == "For":
                assigned.update(self._find_assigned_vars(stmt.get("body", [])))
        return assigned

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

    def _collect_user_exceptions(self, stmts: List[Dict[str, Any]]) -> Set[str]:
        """Collect user exception type names from Raise statements."""
        result: Set[str] = set()
        for stmt in stmts:
            if stmt.get("stmt") == "Raise" and stmt.get("exc_type"):
                result.add(stmt["exc_type"])
            for key in ("body", "orelse"):
                if key in stmt:
                    result |= self._collect_user_exceptions(stmt[key])
        return result

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
            return False

        if not _has_return(stmts):
            return "unit"

        for stmt in stmts:
            if stmt["stmt"] == "Return" and stmt.get("value"):
                val = stmt["value"]
                if val.get("type") == "Tuple":
                    n = len(val.get("elts", []))
                    return "(" + ", ".join(["int"] * n) + ")"
                if val.get("type") == "String":
                    return "string"
            for key in ("body", "orelse"):
                if key in stmt:
                    result = self._find_return_type(stmt[key])
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
                return name
            # If it's a local mutable variable, we must dereference it with '!'
            if name in local_refs:
                return f"!{name}"
            # If it's a known parameter or 'self', return as-is
            if name in self._current_params or name == "self":
                return name
            # Otherwise it's an external reference (imported module, global) — abstract constant
            safe = self._whyml_ident(name)
            self._add_abstract_op(f"val constant {safe} : int")
            return safe
            
        elif t == "Number":
            # Why3 integers are unbounded, so format without decimal points
            return str(int(expr["value"]))

        elif t == "String":
            escaped = expr["value"].replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
            
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
                # In spec context, use bool operators
                if getattr(self, '_in_spec', False):
                    left_b = self._to_bool(left, expr["left"])
                    right_b = self._to_bool(right, expr["right"])
                    return f"({left_b} {op} {right_b})"
                else:
                    # In body context, Python's and/or are value-returning
                    # Model as abstract int operations to avoid bool/int type conflicts
                    fn = "py_or" if op == "||" else "py_and"
                    self._add_abstract_op(f"val {fn} (x: int) (y: int) : int")
                    return f"({fn} {left} {right})"
            elif expr["op"] == "in":
                # Containment check: x in collection → abstract bool function
                self._add_abstract_op("val contains_check (x: int) (c: int) : bool")
                return f"(contains_check {self._coerce_str_arg(left)} {self._coerce_str_arg(right)})"
            elif expr["op"] == "not in":
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
            return f"{expr['object']}.{expr['field']}"

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
                    is_array = (var_name in getattr(self, "_array2d_params", set()) or
                                var_name in getattr(self, "_array_locals", set()) or
                                var_name in getattr(self, "_current_array1d_params", set()))
                    if not is_array and var_name:
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
                self._add_abstract_op("val isinstance_check (x: int) (t: int) : bool")
                # The type arg might be a tuple like (A, B, C) — coerce to int
                type_arg = self._coerce_to_int(args[1])
                return f"(isinstance_check {args[0]} {type_arg})"
            if func_name in ("set", "frozenset") and len(args) == 0:
                self._add_abstract_op("val set_empty () : int")
                return "(set_empty ())"
            if func_name == "dict" and len(args) == 0:
                self._add_abstract_op("val dict_new () : int")
                return "(dict_new ())"
            if func_name == "list" and len(args) <= 1:
                self._add_abstract_op("val list_new (x: int) : int")
                return f"(list_new {args[0] if args else '0'})"
            if func_name in ("str", "repr", "int", "bool", "abs") and len(args) == 1:
                wf = self._whyml_ident(func_name)
                self._add_abstract_op(f"val {wf}_conv (x: int) : int")
                return f"({wf}_conv {args[0]})"
            if func_name == "hasattr":
                self._add_abstract_op("val hasattr_check (x: int) (a: int) : bool")
                a0 = args[0] if args else '0'
                a1 = self._coerce_str_arg(args[1] if len(args) > 1 else '0')
                return f"(hasattr_check {a0} {a1})"
            # Dotted call (method or external module function)
            if "." in func_name:
                # Model as abstract function call — coerce string args to int
                safe_name = func_name.replace(".", "_")
                safe_name = self._whyml_ident(safe_name)
                coerced_args = [self._coerce_to_int(a) for a in args]
                nargs = len(coerced_args)
                # Include arity in name to avoid partial application conflicts
                arity_name = f"{safe_name}_{nargs}" if nargs > 0 else safe_name
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
                # Include arity in name to avoid conflicts
                arity_fn = f"{safe_fn}_{nargs}" if nargs > 0 else safe_fn
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
                    value.get("value", {}).get("name") in getattr(self, "_array2d_params", set())):
                base = value["value"]["name"]
                row = self._expr_to_whyml(value["index"], local_refs, invariant_ctx, subst)
                col = index
                return f"(get {base} {row} {col})"
            value_str = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
            if self.memory_model == "hoare":
                # Check if the value is a known array variable
                var_name = value.get("name", "") if value.get("type") == "Var" else ""
                is_array = (var_name in getattr(self, "_array2d_params", set()) or
                            var_name in getattr(self, "_array_locals", set()) or
                            var_name in getattr(self, "_current_array1d_params", set()))
                if not is_array and var_name:
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
            return "true" if expr.get("value") else "false"

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
                    return f"{indent}let ghost {target} = ref ({val} : int{self._bounded_int}) in\n{rest_code}"
                return f"{indent}let ghost {target} = ref {val} in\n{rest_code}"
            else:
                # Subsequent: ghost update
                if op == "=":
                    code = f"{indent}ghost {target} := {val}"
                elif op == "+=":
                    code = f"{indent}ghost {target} := !{target} + {val}"
                elif op == "-=":
                    code = f"{indent}ghost {target} := !{target} - {val}"
                elif op == "*=":
                    code = f"{indent}ghost {target} := !{target} * {val}"
                else:
                    code = f"{indent}ghost {target} := {val}"

        elif s_type == "Assign":
            target = stmt["target"]
            val = self._expr_to_whyml(stmt["value"], local_refs)
            
            if target not in declared_refs:
                declared_refs.add(target)
                # Arrays are already mutable — don't wrap in ref
                is_array_val = val.startswith("(Array.make") or val == "(Array.make 1024 0)"
                if is_array_val:
                    code = f"{indent}let {target} = {val} in\n"
                    # Track as array local (no ! deref needed)
                    self._array_locals.add(target)
                elif self._bounded_int:
                    # With bounded ints, annotate the initial value for type inference
                    code = f"{indent}let {target} = ref ({val} : int{self._bounded_int}) in\n"
                else:
                    code = f"{indent}let {target} = ref {val} in\n"
                rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
                
                # NEW: WhyML requires an expression after `in`. 
                # If there are no more statements, return unit `()`
                if not rest_code:
                    rest_code = f"{indent}()"
                    
                return code + rest_code
            else:
                # Standard reassignment
                code = f"{indent}{target} := {val}"
                
        elif s_type == "AugAssign":
            target = stmt["target"]
            val = self._expr_to_whyml(stmt["value"], local_refs)
            raw_op = stmt["op"]
            op = self._op(raw_op)
            # Bitwise/power ops → abstract function calls
            bitwise_ops = {"&": "bit_and", "|": "bit_or", "^": "bit_xor",
                           "<<": "bit_lshift", ">>": "bit_rshift", "**": "py_pow"}
            if raw_op in bitwise_ops:
                op_fn = bitwise_ops[raw_op]
                self._add_abstract_op(f"val {op_fn} (x: int) (y: int) : int")
                code = f"{indent}{target} := ({op_fn} !{target} {val})"
            else:
                # Unroll AugAssign: x += 1 becomes x := !x + 1
                code = f"{indent}{target} := !{target} {op} {val}"

        elif s_type == "FieldAssign":
            obj = stmt["object"]
            field = stmt["field"]
            val = self._expr_to_whyml(stmt["value"], local_refs)
            # Record fields are int; coerce bool values
            if val == "true":
                val = "1"
            elif val == "false":
                val = "0"
            code = f"{indent}{obj}.{field} <- {val}"

        elif s_type == "FieldAugAssign":
            obj = stmt["object"]
            field = stmt["field"]
            val = self._expr_to_whyml(stmt["value"], local_refs)
            op = self._op(stmt["op"])
            code = f"{indent}{obj}.{field} <- {obj}.{field} {op} {val}"

        elif s_type == "ArraySet":
            arr = stmt["array"]
            # Detect 2D write: a[i][j] = v → ArraySet(array=Subscript(Var(a),i), index=j, ...)
            if (arr.get("type") == "Subscript" and
                    arr.get("value", {}).get("type") == "Var" and
                    arr.get("value", {}).get("name") in getattr(self, "_array2d_params", set())):
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
                    is_array = (var_name in getattr(self, "_array2d_params", set()) or
                                var_name in getattr(self, "_array_locals", set()) or
                                var_name in getattr(self, "_current_array1d_params", set()))
                    if not is_array and var_name:
                        st = getattr(self, "_current_symbol_table", {})
                        if st.get(var_name) in ("list", "dict"):
                            is_array = True
                    if is_array:
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

            if has_direct_ret:
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
                # Return exception expects int; coerce bool/tuple/array
                if val == "true":
                    val = "1"
                elif val == "false":
                    val = "0"
                val = self._coerce_to_int(val)
                return f"{indent}raise (Return {val})"
            return f"{indent}{val}"

        elif s_type == "Continue":
            # Raise the continue exception caught by the enclosing For loop's try/with
            return f"{indent}raise PyCSL_Continue"

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
            iter_ir = stmt["iter"]
            idx = f"_idx_{target}"
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
                is_array = (var_name in getattr(self, "_array2d_params", set()) or
                            var_name in getattr(self, "_array_locals", set()) or
                            var_name in getattr(self, "_current_array1d_params", set()))
                if not is_array:
                    st = getattr(self, "_current_symbol_table", {})
                    if st.get(var_name) in ("list", "dict"):
                        is_array = True
                iter_expr = self._expr_to_whyml(iter_ir, local_refs)
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
                while_parts.append(f"{inner_indent}  let {target} = ref ({elem_expr}) in")
                while_parts.append(inner_body)
                while_parts.append(f"{inner_indent}with PyCSL_Continue -> () end;")
            else:
                while_parts.append(
                    f"{inner_indent}let {target} = ref ({elem_expr}) in")
                while_parts.append(inner_body + ";")

            while_parts.append(f"{inner_indent}{idx} := !{idx} + 1")
            while_parts.append(f"{loop_indent}done")
            while_code = "\n".join(while_parts)

            # Introduce the index ref following the same pattern as Assign
            if self._bounded_int:
                idx_decl = f"{loop_indent}let {idx} = ref (0 : int{self._bounded_int}) in\n{while_code}"
            else:
                idx_decl = f"{loop_indent}let {idx} = ref 0 in\n{while_code}"

            if has_direct_ret and not getattr(self, '_has_early_ret', False):
                # Wrap for-loop in try…with Return r -> r end
                rest_code = self._stmts_to_whyml(
                    rest, local_refs, declared_refs, indent + "  ", in_loop)
                inner = idx_decl
                if rest_code:
                    inner += ";\n" + rest_code
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
                    arg = self._expr_to_whyml(val["args"][0], local_refs)
                    len_ref = f"{arr_name}_len"
                    code = f"{indent}{arr_name}[!{len_ref}] <- {arg};\n{indent}{len_ref} := !{len_ref} + 1"
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
            body_str = self._stmts_to_whyml(body_stmts, local_refs, declared_refs.copy(), indent + "  ", in_loop)
            if not body_str:
                body_str = f"{indent}  ()"
            if handlers:
                code = f"{indent}try\n{body_str}\n"
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
                code = body_str

        elif s_type == "Pass":
            code = f"{indent}()"

        elif s_type == "Break":
            # WhyML doesn't have break; model as exception
            code = f"{indent}raise PyCSL_Break"

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

        has_list_param = any(
            v in ("list", "dict") for func in functions
            for v in func.get("symbol_table", {}).values()
        )
        # In the hoare model, str-typed parameters are mapped to array int (not string),
        # so they require use array.Array but not use string.String.
        has_str_param = any(
            "str" in func.get("symbol_table", {}).values()
            for func in functions
        )
        needs_matrix = any(func.get("array2d_params") for func in functions)
        if self.memory_model == "hoare":
            needs_array = has_list_param or \
                        (has_str_param) or \
                        any(self._uses_for(body) for body in all_bodies) or \
                        any(self._uses_subscript(body) for body in all_bodies) or \
                        any(self._uses_arrayset(body) for body in all_bodies)
        else:
            needs_array = False  # Heap models use map.Map, not array.Array
        needs_minmax = any(self._uses_minmax(body) for body in all_bodies)
        needs_continue = any(self._uses_continue(body) for body in all_bodies)
        needs_return_exc = any(
            self._has_in_loop_return(func["body"]) or self._has_early_return(func["body"])
            for func in functions)
        # In the hoare model str params are emitted as array int, so string.String is
        # only needed when the non-hoare model has str params or string literals appear.
        needs_string = any(
            (self.memory_model != "hoare" and "str" in func.get("symbol_table", {}).values())
            for func in functions
        ) or any(self._uses_string(func) for func in functions)
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
        if needs_return_exc:
            out.append("")
            out.append("  exception Return int")
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
        for td in type_decls:
            if td["kind"] == "record":
                type_name = td["name"].lower()
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
            self._current_symbol_table = symbol_table  # For type lookups in Subscript
            array2d_params = set(func.get("array2d_params", []))
            array1d_params = set(func.get("array1d_params", []))
            self._current_array1d_params = array1d_params
            self._array2d_params = array2d_params  # used by _expr_to_whyml / _stmts_to_whyml

            if is_method:
                # Method: prepend (self: <type>) as first arg, no ref_params logic
                self_type = func["self_type"].lower()
                args = list(symbol_table.keys())
                param_parts = [f"(self: {self_type})"]
                for arg in args:
                    if arg in local_refs or arg in ghost_vars:
                        continue
                    if arg in array2d_params:
                        param_parts.append(f"({arg}: matrix {int_type})")
                    elif arg in array1d_params or symbol_table.get(arg) in ("list", "dict"):
                        if self.memory_model == "hoare":
                            param_parts.append(f"({arg}: array {int_type})")
                        else:
                            param_parts.append(f"({arg}: loc) ({arg}_len: int)")
                    elif symbol_table.get(arg) == "str":
                        param_parts.append(f"({arg}: {int_type})")
                    else:
                        param_parts.append(f"({arg}: {int_type})")
                args_str = " ".join(param_parts)
            else:
                # Standalone function: use existing ref_params logic for obj_* vars
                ref_params = {v for v in symbol_table if v in local_refs and v.startswith("obj_")}
                args = [v for v in symbol_table if (v not in local_refs or v in ref_params) and v not in ghost_vars]

                def _param_type(arg: str) -> str:
                    if arg in ref_params:
                        return f"({arg}: ref {int_type})"
                    if arg in array2d_params:
                        return f"({arg}: matrix {int_type})"
                    if arg in array1d_params or symbol_table.get(arg) in ("list", "dict"):
                        if self.memory_model == "hoare":
                            return f"({arg}: array {int_type})"
                        else:
                            return f"({arg}: loc) ({arg}_len: int)"
                    if symbol_table.get(arg) == "str":
                        if is_method:
                            return f"({arg}: {int_type})"
                        if self.memory_model == "hoare":
                            return f"({arg}: string)"
                        return f"({arg}: string)"
                    return f"({arg}: {int_type})"

                args_str = " ".join(_param_type(arg) for arg in args)

            return_type = self._find_return_type(body_stmts)
            # Use explicit return annotation if body inference defaults to int
            ret_ann = func.get("return_annotation")
            if ret_ann == "str" and return_type == "int" and not is_method:
                return_type = "string"
            elif ret_ann == "list" and return_type == "int":
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
            func_exceptions = self._collect_user_exceptions(body_stmts)
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
            if is_method:
                body_code = self._stmts_to_whyml(body_stmts, local_refs | {f"{t}_len" for t in append_targets}, set(), "    ")
            else:
                ref_params_set = ref_params if not is_method else set()
                body_code = self._stmts_to_whyml(body_stmts, local_refs | {f"{t}_len" for t in append_targets}, set(ref_params_set), "    ")

            # Prepend length ref declarations for append targets
            for tgt in sorted(append_targets):
                if bounded_int:
                    body_code = f"    let {tgt}_len = ref (0 : int{bounded_int}) in\n{body_code}"
                else:
                    body_code = f"    let {tgt}_len = ref 0 in\n{body_code}"
                # If this target is not a parameter, declare the array too
                if tgt not in local_refs and tgt not in (ref_params if not is_method else set()):
                    body_code = f"    let {tgt} = Array.make 1024 0 in\n{body_code}"
                    self._array_locals.add(tgt)
            # Empty bodies (from `pass`-only functions) must emit `()` — the
            # WhyML unit value — so the parser doesn't treat the next `let` as
            # the current function's body.
            if not body_code.strip():
                body_code = "    ()"
            # Wrap entire function body in try/catch for early returns
            if self._has_early_ret:
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
