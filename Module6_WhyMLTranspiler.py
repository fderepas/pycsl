import json
from typing import Dict, Any, Set, List

class Module6_WhyMLTranspiler:
    """Reads the JSON IR and transpiles it into valid WhyML (.mlw) syntax."""
    
    def __init__(self, json_ir: str):
        self.ir = json.loads(json_ir)
        # Maps Python/IR operators to WhyML operators
        self.op_map = {
            "==": "=",   # WhyML equality is single =
            "!=": "<>",  # WhyML inequality is <>
            "and": "&&",
            "or": "||",
            "not": "not",
            "div": "div",
            "%": "mod"   # WhyML modulo from int.EuclideanDivision
        }

    def _op(self, op: str) -> str:
        """Translates operators; defaults to the same string (e.g., +, -, >, <)."""
        return self.op_map.get(op, op)

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

    def _find_return_type(self, stmts: List[Dict[str, Any]]) -> str:
        """Infer the function return type; returns 'int' or a tuple type string."""
        for stmt in stmts:
            if stmt["stmt"] == "Return" and stmt.get("value"):
                val = stmt["value"]
                if val.get("type") == "Tuple":
                    n = len(val.get("elts", []))
                    return "(" + ", ".join(["int"] * n) + ")"
            for key in ("body", "orelse"):
                if key in stmt:
                    result = self._find_return_type(stmt[key])
                    if result != "int":
                        return result
        return "int"

    def _expr_to_whyml(self, expr: Dict[str, Any], local_refs: Set[str]) -> str:
        """Recursively translates an expression dictionary into a WhyML string."""
        if not expr: return ""
        
        t = expr["type"]
        if t == "Var":
            name = expr["name"]
            # If it's a local mutable variable, we must dereference it with '!'
            return f"!{name}" if name in local_refs else name
            
        elif t == "Number":
            # Why3 integers are unbounded, so format without decimal points
            return str(int(expr["value"]))
            
        elif t == "Result":
            return "result"
            
        elif t == "BinOp":
            left = self._expr_to_whyml(expr["left"], local_refs)
            right = self._expr_to_whyml(expr["right"], local_refs)
            op = self._op(expr["op"])
            if op == "div":
                # Why3 treats alphabetic `div` as a prefix function from
                # int.EuclideanDivision; writing it infix (`a div b`) inside a
                # nested `let … in` chain causes the parser to mis-classify the
                # preceding sub-expression as a function applied to 3 arguments.
                # Emit prefix application `(div a b)` instead.
                return f"(div {left} {right})"
            elif op == "mod":
                # Same issue as `div`: `mod` is a prefix function in
                # int.EuclideanDivision, not an infix operator.
                return f"(mod {left} {right})"
            return f"({left} {op} {right})"
            
        elif t == "UnaryOp":
            e = self._expr_to_whyml(expr["expr"], local_refs)
            op = self._op(expr["op"])
            return f"({op} {e})"
            
        elif t == "Old":
            e = self._expr_to_whyml(expr["expr"], local_refs)
            return f"(old {e})"
        
        elif t == "Call":
            func_name = expr["func"]
            args = [self._expr_to_whyml(a, local_refs) for a in expr["args"]]
            if func_name == "len" and len(args) == 1:
                return f"(Seq.length {args[0]})"
            args_str = " ".join(args) if args else "()"
            return f"({func_name} {args_str})"

        elif t == "Tuple":
            elts = [self._expr_to_whyml(e, local_refs) for e in expr.get("elts", [])]
            return f"({', '.join(elts)})"

        elif t == "Subscript":
            value = self._expr_to_whyml(expr["value"], local_refs)
            index = self._expr_to_whyml(expr["index"], local_refs)
            return f"(Seq.get {value} {index})"

        return ""

    def _stmts_to_whyml(self, stmts: List[Dict[str, Any]], local_refs: Set[str], declared_refs: Set[str], indent: str) -> str:
        """Recursively translates imperative statements into WhyML strings."""
        if not stmts: return ""
        
        stmt = stmts[0]
        rest = stmts[1:]
        code = ""
        s_type = stmt["stmt"]
        
        if s_type == "Assign":
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
            if orelse:
                orelse_str = self._stmts_to_whyml(orelse, local_refs, declared_refs.copy(), indent + "  ")
                if not orelse_str:
                    orelse_str = f"{indent}  ()"
                code = (f"{indent}if {test} then begin\n{body_str}\n"
                        f"{indent}end else begin\n{orelse_str}\n{indent}end")
            else:
                code = f"{indent}if {test} then begin\n{body_str}\n{indent}end"

        elif s_type == "For":
            target = stmt["target"]
            iter_expr = self._expr_to_whyml(stmt["iter"], local_refs)
            idx = f"_idx_{target}"
            inner_indent = indent + "  "

            body_local = local_refs | {target}
            body_declared = declared_refs.copy() | {target}
            inner_body = self._stmts_to_whyml(
                stmt.get("body", []), body_local, body_declared, inner_indent)
            if not inner_body:
                inner_body = f"{inner_indent}()"

            has_cont = self._has_continue(stmt.get("body", []))

            while_parts = [f"{indent}while !{idx} < Seq.length {iter_expr} do"]
            for inv in stmt.get("invariants", []):
                inv_str = self._expr_to_whyml(inv, local_refs)
                while_parts.append(f"{inner_indent}invariant {{ {inv_str} }}")
            for var_ir in stmt.get("variants", []):
                var_str = self._expr_to_whyml(var_ir, local_refs)
                while_parts.append(f"{inner_indent}variant {{ {var_str} }}")

            if has_cont:
                while_parts.append(f"{inner_indent}try")
                while_parts.append(f"{inner_indent}  let {target} = ref (Seq.get {iter_expr} !{idx}) in")
                while_parts.append(inner_body)
                while_parts.append(f"{inner_indent}with PyCSL_Continue -> () end;")
            else:
                while_parts.append(
                    f"{inner_indent}let {target} = ref (Seq.get {iter_expr} !{idx}) in")
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
            
        # Chain sequence of statements with semicolons
        if rest:
            code += ";\n" + self._stmts_to_whyml(rest, local_refs, declared_refs, indent)
            
        return code

    def transpile(self) -> str:
        """Entry point: converts the entire program to a .mlw string."""
        functions = self.ir.get("functions", [])
        all_bodies = [func["body"] for func in functions]

        has_list_param = any(
            "list" in func.get("symbol_table", {}).values()
            for func in functions
        )
        needs_seq = has_list_param or \
                    any(self._uses_for(body) for body in all_bodies) or \
                    any(self._uses_subscript(body) for body in all_bodies)
        needs_continue = any(self._uses_continue(body) for body in all_bodies)

        out = [
            "module PyCSL_Program",
            "  use int.Int",
            "  use int.EuclideanDivision",
            "  use ref.Ref",
        ]
        if needs_seq:
            out.append("  use seq.Seq")
        if needs_continue:
            out.append("")
            out.append("  exception PyCSL_Continue")
        out.append("")

        for func in functions:
            name = func["name"]
            body_stmts = func["body"]

            # Determine which variables are mutated locally
            local_refs = self._find_assigned_vars(body_stmts)
            symbol_table = func.get("symbol_table", {})

            # Arguments are variables in scope that are NOT mutated locally
            args = [v for v in symbol_table if v not in local_refs]
            args_str = " ".join([
                f"({arg}: seq int)" if symbol_table.get(arg) == "list" else f"({arg}: int)"
                for arg in args
            ])

            return_type = self._find_return_type(body_stmts)
            if args_str:
                out.append(f"  let {name} {args_str} : {return_type}")
            else:
                out.append(f"  let {name} () : {return_type}")

            # Contracts
            contracts = func.get("contracts", {})
            for req in contracts.get("requires", []):
                # Preconditions only reference pre-state, so we pass an empty set for local_refs
                req_str = self._expr_to_whyml(req, set())
                out.append(f"    requires {{ {req_str} }}")

            for ens in contracts.get("ensures", []):
                ens_str = self._expr_to_whyml(ens, set())
                out.append(f"    ensures  {{ {ens_str} }}")

            out.append("  =")

            # Body
            body_code = self._stmts_to_whyml(body_stmts, local_refs, set(), "    ")
            out.append(body_code)
            out.append("")

        out.append("end")
        return "\n".join(out)
