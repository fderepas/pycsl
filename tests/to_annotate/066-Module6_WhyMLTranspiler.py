import json
from typing import Dict, Any, Set, List

class Module6_WhyMLTranspiler:
    """Reads the JSON IR and transpiles it into valid WhyML (.mlw) syntax."""
    
    def __init__(self, json_ir: str, memory_model: str = "hoare"):
        self.ir = json.loads(json_ir)
        self.memory_model = memory_model   # "hoare" | "typed" | "store"
        self._array2d_params: set = set()  # set during per-function transpilation
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

    @staticmethod
    def _whyml_ident(name: str) -> str:
        """WhyML identifiers must start with a lowercase letter."""
        if name and name[0].isupper():
            return name[0].lower() + name[1:]
        return name

    def _op(self, op: str) -> str:
        """Translates operators; defaults to the same string (e.g., +, -, >, <)."""
        return self.op_map.get(op, op)

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
            # If it's a local mutable variable, we must dereference it with '!'
            return f"!{name}" if name in local_refs else name
            
        elif t == "Number":
            # Why3 integers are unbounded, so format without decimal points
            return str(int(expr["value"]))

        elif t == "String":
            # WhyML string literal
            escaped = expr["value"].replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
            
        elif t == "Result":
            return "result"
            
        elif t == "BinOp":
            left = self._expr_to_whyml(expr["left"], local_refs, invariant_ctx, subst)
            right = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
            op = self._op(expr["op"])
            if op == "div":
                return f"(div {left} {right})"
            elif op == "mod":
                return f"(mod {left} {right})"
            return f"({left} {op} {right})"
            
        elif t == "UnaryOp":
            e = self._expr_to_whyml(expr["expr"], local_refs, invariant_ctx, subst)
            op = self._op(expr["op"])
            if op == "+":
                return e  # WhyML has no unary +; it's the identity
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
                    return f"(length {args[0]})"
                else:
                    arr_name = args[0].lstrip("!")
                    return f"{arr_name}_len"
            if func_name in ("min", "max") and len(args) == 2:
                fn = "Int.min" if func_name == "min" else "Int.max"
                return f"({fn} {args[0]} {args[1]})"
            args_str = " ".join(args) if args else "()"
            return f"({self._whyml_ident(func_name)} {args_str})"

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
                return f"{value_str}[{index}]"
            else:
                return f"(Map.get !{self._heap_var} ({value_str} + {index}))"

        elif t == "ArrayLit":
            return "(* ArrayLit: use Array.make instead *)"

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
                return f"(length {expr['var']})"
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

        return ""

    def _stmts_to_whyml(self, stmts: List[Dict[str, Any]], local_refs: Set[str], declared_refs: Set[str], indent: str) -> str:
        """Recursively translates imperative statements into WhyML strings."""
        if not stmts: return ""
        
        stmt = stmts[0]
        rest = stmts[1:]
        code = ""
        s_type = stmt["stmt"]
        
        if s_type == "Label":
            # `label L in <rest>` — scopes over the entire remaining block
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent)
            if not rest_code:
                rest_code = f"{indent}()"
            return f"{indent}label {stmt['name']} in\n{rest_code}"

        elif s_type == "Assign":
            target = stmt["target"]
            val = self._expr_to_whyml(stmt["value"], local_refs)
            
            if target not in declared_refs:
                declared_refs.add(target)
                code = f"{indent}let {target} = ref {val} in\n"
                rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent)
                
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
            op = self._op(stmt["op"])
            # Unroll AugAssign: x += 1 becomes x := !x + 1
            code = f"{indent}{target} := !{target} {op} {val}"

        elif s_type == "FieldAssign":
            obj = stmt["object"]
            field = stmt["field"]
            val = self._expr_to_whyml(stmt["value"], local_refs)
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
                    code = f"{indent}{array_expr}[{index_expr}] <- {val_expr}"
                else:
                    hv = self._heap_var
                    code = (f"{indent}{hv} := Map.set !{hv} "
                            f"({array_expr} + {index_expr}) {val_expr}")
            
        elif s_type == "While":
            test = self._expr_to_whyml(stmt["test"], local_refs)
            inner_indent = indent + "  "
            code = f"{indent}while {test} do\n"
            
            for inv in stmt.get("invariants", []):
                inv_str = self._expr_to_whyml(inv, local_refs)
                code += f"{inner_indent}invariant {{ {inv_str} }}\n"
                
            for var in stmt.get("variants", []):
                var_str = self._expr_to_whyml(var, local_refs)
                code += f"{inner_indent}variant {{ {var_str} }}\n"
                
            body_str = self._stmts_to_whyml(stmt["body"], local_refs, declared_refs.copy(), inner_indent)
            has_cont = self._has_continue(stmt.get("body", []))
            if has_cont:
                code += f"{inner_indent}try\n"
                code += body_str + "\n"
                code += f"{inner_indent}with PyCSL_Continue -> () end\n"
            else:
                code += body_str + "\n"
            code += f"{indent}done"
            
        elif s_type == "Return":
            val = self._expr_to_whyml(stmt["value"], local_refs)
            # In WhyML, the last expression is the return value. No semicolon!
            return f"{indent}{val}"

        elif s_type == "Continue":
            # Raise the continue exception caught by the enclosing For loop's try/with
            return f"{indent}raise PyCSL_Continue"

        elif s_type == "If":
            test = self._expr_to_whyml(stmt["test"], local_refs)
            body = stmt.get("body", [])
            orelse = stmt.get("orelse", [])
            body_str = self._stmts_to_whyml(body, local_refs, declared_refs.copy(), indent + "  ")
            if not body_str:
                body_str = f"{indent}  ()"
            body_returns = self._ends_with_return(body)

            if orelse:
                orelse_str = self._stmts_to_whyml(orelse, local_refs, declared_refs.copy(), indent + "  ")
                if not orelse_str:
                    orelse_str = f"{indent}  ()"
                code = (f"{indent}if {test} then begin\n{body_str}\n"
                        f"{indent}end else begin\n{orelse_str}\n{indent}end")
                # Both branches return → expression form, rest is dead code
                if body_returns and self._ends_with_return(orelse):
                    return code
            elif body_returns and rest:
                # No else, body returns, remaining stmts form the else branch
                rest_str = self._stmts_to_whyml(rest, local_refs, declared_refs, indent + "  ")
                if not rest_str:
                    rest_str = f"{indent}  ()"
                return (f"{indent}if {test} then begin\n{body_str}\n"
                        f"{indent}end else begin\n{rest_str}\n{indent}end")
            else:
                code = f"{indent}if {test} then begin\n{body_str}\n{indent}end"

        elif s_type == "For":
            target = stmt["target"]
            iter_ir = stmt["iter"]
            idx = f"_idx_{target}"
            inner_indent = indent + "  "

            body_local = local_refs | {target}
            body_declared = declared_refs.copy() | {target}
            inner_body = self._stmts_to_whyml(
                stmt.get("body", []), body_local, body_declared, inner_indent)
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
            elif self.memory_model == "hoare":
                iter_expr = self._expr_to_whyml(iter_ir, local_refs)
                len_expr = f"length {iter_expr}"
                elem_expr = f"{iter_expr}[!{idx}]"
            else:
                iter_expr = self._expr_to_whyml(iter_ir, local_refs)
                len_expr = f"{iter_expr}_len"
                elem_expr = f"Map.get !{self._heap_var} ({iter_expr} + !{idx})"

            while_parts = [f"{indent}while !{idx} < {len_expr} do"]
            # For range loops: substitute the loop variable with the counter ref
            # so invariants/variants using `i` render as `!_idx_i`, not the unbound `i`
            inv_subst = {target: idx} if is_range else None
            inv_refs = local_refs | {idx}
            for inv in stmt.get("invariants", []):
                inv_str = self._expr_to_whyml(inv, inv_refs, subst=inv_subst)
                while_parts.append(f"{inner_indent}invariant {{ {inv_str} }}")
            for var_ir in stmt.get("variants", []):
                var_str = self._expr_to_whyml(var_ir, inv_refs, subst=inv_subst)
                while_parts.append(f"{inner_indent}variant {{ {var_str} }}")

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
            while_parts.append(f"{indent}done")
            while_code = "\n".join(while_parts)

            # Introduce the index ref following the same pattern as Assign
            full_code = f"{indent}let {idx} = ref 0 in\n{while_code}"
            rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent)
            if rest_code:
                return full_code + ";\n" + rest_code
            return full_code
            
        elif s_type == "Expr":
            # Expression statement (e.g., void function call)
            val = stmt.get("value", {})
            code = self._expr_to_whyml(val, local_refs)

        # Chain sequence of statements with semicolons
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent)
            
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
            "list" in func.get("symbol_table", {}).values()
            for func in functions
        )
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
        needs_string = any(
            "str" in func.get("symbol_table", {}).values()
            for func in functions
        ) or any(self._uses_string(func) for func in functions)

        out = [
            "module PyCSL_Program",
            "  use int.Int",
            "  use int.EuclideanDivision",
            "  use ref.Ref",
        ]
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
        out.append("")

        # Emit record type declarations (Level 2) with optional invariants (Level 3)
        for td in type_decls:
            if td["kind"] == "record":
                type_name = td["name"].lower()
                field_strs = []
                for f in td["fields"]:
                    prefix = "mutable " if f.get("mutable") else ""
                    field_strs.append(f"{prefix}{f['name']}: {f['type']}")
                out.append(f"  type {type_name} = {{ {'; '.join(field_strs)} }}")

                # Level 3: class invariants
                class_invs = td.get("class_invariants", [])
                if class_invs:
                    for inv in class_invs:
                        inv_str = self._expr_to_whyml(inv, set(), invariant_ctx=True)
                        out.append(f"    invariant {{ {inv_str} }}")
                    # Witness (`by` clause) proving the type is inhabited
                    defaults = td.get("field_defaults", {})
                    witness_parts = []
                    for f in td["fields"]:
                        val = defaults.get(f["name"], 0)
                        witness_parts.append(f"{f['name']} = {val}")
                    out.append(f"    by {{ {'; '.join(witness_parts)} }}")

                out.append("")

        for func in functions:
            name = self._whyml_ident(func["name"])
            body_stmts = func["body"]
            is_method = func.get("kind") == "method"

            # Determine which variables are mutated locally
            local_refs = self._find_assigned_vars(body_stmts)
            symbol_table = func.get("symbol_table", {})
            array2d_params = set(func.get("array2d_params", []))
            array1d_params = set(func.get("array1d_params", []))
            self._array2d_params = array2d_params  # used by _expr_to_whyml / _stmts_to_whyml

            if is_method:
                # Method: prepend (self: <type>) as first arg, no ref_params logic
                self_type = func["self_type"].lower()
                args = list(symbol_table.keys())
                param_parts = [f"(self: {self_type})"]
                for arg in args:
                    if arg in local_refs:
                        continue
                    if arg in array2d_params:
                        param_parts.append(f"({arg}: matrix int)")
                    elif arg in array1d_params or symbol_table.get(arg) == "list":
                        if self.memory_model == "hoare":
                            param_parts.append(f"({arg}: array int)")
                        else:
                            param_parts.append(f"({arg}: loc) ({arg}_len: int)")
                    else:
                        param_parts.append(f"({arg}: int)")
                args_str = " ".join(param_parts)
            else:
                # Standalone function: use existing ref_params logic for obj_* vars
                ref_params = {v for v in symbol_table if v in local_refs and v.startswith("obj_")}
                args = [v for v in symbol_table if v not in local_refs or v in ref_params]

                def _param_type(arg: str) -> str:
                    if arg in ref_params:
                        return f"({arg}: ref int)"
                    if arg in array2d_params:
                        return f"({arg}: matrix int)"
                    if arg in array1d_params or symbol_table.get(arg) == "list":
                        if self.memory_model == "hoare":
                            return f"({arg}: array int)"
                        else:
                            return f"({arg}: loc) ({arg}_len: int)"
                    if symbol_table.get(arg) == "str":
                        return f"({arg}: string)"
                    return f"({arg}: int)"

                args_str = " ".join(_param_type(arg) for arg in args)

            return_type = self._find_return_type(body_stmts)
            # Use explicit return annotation if body inference defaults to int
            ret_ann = func.get("return_annotation")
            if ret_ann == "str" and return_type == "int":
                return_type = "string"
            # Track tuple arity for \result[i] postcondition support
            if return_type.startswith("(") and return_type.endswith(")"):
                self._current_tuple_arity = return_type.count(",") + 1
            else:
                self._current_tuple_arity = 0

            func_variants = func.get("function_variants", [])
            func_diverges = func.get("diverges", False)
            func_trusted = func.get("trusted", False)
            is_recursive = self._is_recursive(name, body_stmts)
            use_rec = bool(func_variants) or is_recursive

            if func_trusted:
                # Trusted: emit val declaration (no body, contracts become axioms)
                if args_str:
                    out.append(f"  val {name} {args_str} : {return_type}")
                else:
                    out.append(f"  val {name} () : {return_type}")
            else:
                let_kw = "let rec" if use_rec else "let"
                if args_str:
                    out.append(f"  {let_kw} {name} {args_str} : {return_type}")
                else:
                    out.append(f"  {let_kw} {name} () : {return_type}")

            # Contracts — methods use empty local_refs for spec (FieldGet handles itself)
            contracts = func.get("contracts", {})
            spec_refs = set() if is_method else (ref_params if not is_method else set())
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

            # Trusted functions: no body (val declaration only)
            if func_trusted:
                out.append("")
                continue

            out.append("  =")

            # Body
            if is_method:
                body_code = self._stmts_to_whyml(body_stmts, local_refs, set(), "    ")
            else:
                ref_params_set = ref_params if not is_method else set()
                body_code = self._stmts_to_whyml(body_stmts, local_refs, set(ref_params_set), "    ")
            out.append(body_code)
            out.append("")

        out.append("end")
        return "\n".join(out)
