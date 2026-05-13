import ast
import json
from typing import Any, Dict, List
from Module2_Parser import (
    CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    BinOp as CSLBinOp, UnaryOp as CSLUnaryOp, Var as CSLVar, 
    Number as CSLNumber, Result as CSLResult, Old as CSLOld, Nothing
)

class PyCSLToJSONEmitter(ast.NodeVisitor):
    """Walks the Annotated AST and translates it into a JSON-serializable IR."""
    
    def __init__(self):
        self.program_ir = {"functions": []}

    # --- 1. PyCSL Contract Serialization ---
    def _csl_to_ir(self, node: CSLNode) -> Dict[str, Any]:
        """Recursively translates PyCSL nodes into IR dictionaries."""
        if isinstance(node, CSLBinOp):
            return {"type": "BinOp", "op": node.op, "left": self._csl_to_ir(node.left), "right": self._csl_to_ir(node.right)}
        elif isinstance(node, CSLUnaryOp):
            return {"type": "UnaryOp", "op": node.op, "expr": self._csl_to_ir(node.expr)}
        elif isinstance(node, CSLVar):
            return {"type": "Var", "name": node.name}
        elif isinstance(node, CSLNumber):
            return {"type": "Number", "value": node.value}
        elif isinstance(node, CSLResult):
            return {"type": "Result"}
        elif isinstance(node, CSLOld):
            return {"type": "Old", "expr": self._csl_to_ir(node.expr)}
        elif isinstance(node, Nothing):
            return {"type": "Nothing"}
        elif isinstance(node, (Requires, Ensures, LoopInvariant, LoopVariant)):
            return self._csl_to_ir(node.expr)
        return {"type": "UnknownCSL"}

    def _csl_list_to_ir(self, csl_list: List[CSLNode]) -> List[Dict[str, Any]]:
        return [self._csl_to_ir(c) for c in csl_list]

    # --- 2. Python AST Serialization (Restricted Subset) ---
    def _py_op_to_str(self, op: ast.operator | ast.cmpop | ast.unaryop) -> str:
        """Maps Python AST operators to string literals."""
        ops = {
            ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "div",
            ast.Mod: "%",
            ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
            ast.USub: "-", ast.UAdd: "+", ast.Not: "not"
        }
        return ops.get(type(op), "?")

    def _py_expr_to_ir(self, expr: ast.expr) -> Dict[str, Any]:
        """Translates Python expressions into IR dictionaries."""
        if isinstance(expr, ast.Name):
            return {"type": "Var", "name": expr.id}
        elif isinstance(expr, ast.Constant):
            return {"type": "Number", "value": expr.value}
        elif isinstance(expr, ast.UnaryOp):
            return {
                "type": "UnaryOp", 
                "op": self._py_op_to_str(expr.op), 
                "expr": self._py_expr_to_ir(expr.operand)
            }
        elif isinstance(expr, ast.BinOp):
            return {"type": "BinOp", "op": self._py_op_to_str(expr.op), 
                    "left": self._py_expr_to_ir(expr.left), "right": self._py_expr_to_ir(expr.right)}
        elif isinstance(expr, ast.Compare):
            return {"type": "BinOp", "op": self._py_op_to_str(expr.ops[0]),
                    "left": self._py_expr_to_ir(expr.left), "right": self._py_expr_to_ir(expr.comparators[0])}
        elif isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Name):
                return {
                    "type": "Call",
                    "func": expr.func.id,
                    "args": [self._py_expr_to_ir(arg) for arg in expr.args]
                }
        elif isinstance(expr, ast.Tuple):
            return {"type": "Tuple", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}
        elif isinstance(expr, ast.Subscript):
            value = self._py_expr_to_ir(expr.value)
            # Python 3.9+: slice is the index directly; Python 3.8: wrapped in ast.Index
            slice_node = expr.slice
            if isinstance(slice_node, ast.Index):
                slice_node = slice_node.value
            index = self._py_expr_to_ir(slice_node)
            return {"type": "Subscript", "value": value, "index": index}
        return {"type": "UnknownPyExpr"}

    def _py_stmts_to_ir(self, stmts: List[ast.stmt]) -> List[Dict[str, Any]]:
        ir_stmts = []
        for stmt in stmts:
            if isinstance(stmt, ast.Assign):
                target = stmt.targets[0]
                if isinstance(target, ast.Name):
                    ir_stmts.append({"stmt": "Assign", "target": target.id, "value": self._py_expr_to_ir(stmt.value)})
            elif isinstance(stmt, ast.AugAssign):
                if isinstance(stmt.target, ast.Name):
                    ir_stmts.append({"stmt": "AugAssign", "target": stmt.target.id, 
                                     "op": self._py_op_to_str(stmt.op), "value": self._py_expr_to_ir(stmt.value)})
            elif isinstance(stmt, ast.Return):
                ir_stmts.append({"stmt": "Return", "value": self._py_expr_to_ir(stmt.value) if stmt.value else None})
            elif isinstance(stmt, ast.While):
                ir_stmts.append(self._process_while(stmt))
            elif isinstance(stmt, ast.For):
                ir_stmts.append(self._process_for(stmt))
            elif isinstance(stmt, ast.If):
                ir_stmts.append(self._process_if(stmt))
            elif isinstance(stmt, ast.Continue):
                ir_stmts.append({"stmt": "Continue"})
            elif isinstance(stmt, ast.Expr):
                ir_stmts.append({"stmt": "Expr", "value": self._py_expr_to_ir(stmt.value)})
        return ir_stmts

    def _process_while(self, node: ast.While) -> Dict[str, Any]:
        return {
            "stmt": "While",
            "test": self._py_expr_to_ir(node.test),
            "invariants": self._csl_list_to_ir(getattr(node, 'csl_invariants', [])),
            "variants": self._csl_list_to_ir(getattr(node, 'csl_variants', [])),
            "body": self._py_stmts_to_ir(node.body)
        }

    def _process_for(self, node: ast.For) -> Dict[str, Any]:
        target = node.target.id if isinstance(node.target, ast.Name) else "_for_target"
        return {
            "stmt": "For",
            "target": target,
            "iter": self._py_expr_to_ir(node.iter),
            "invariants": self._csl_list_to_ir(getattr(node, 'csl_invariants', [])),
            "variants": self._csl_list_to_ir(getattr(node, 'csl_variants', [])),
            "body": self._py_stmts_to_ir(node.body)
        }

    def _process_if(self, node: ast.If) -> Dict[str, Any]:
        return {
            "stmt": "If",
            "test": self._py_expr_to_ir(node.test),
            "body": self._py_stmts_to_ir(node.body),
            "orelse": self._py_stmts_to_ir(node.orelse)
        }

    # --- 3. Main Traversal Hooks ---
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        func_ir = {
            "name": node.name,
            "symbol_table": getattr(node, 'csl_symbol_table', {}),
            "contracts": {
                "requires": self._csl_list_to_ir(getattr(node, 'csl_requires', [])),
                "ensures": self._csl_list_to_ir(getattr(node, 'csl_ensures', [])),
                "assigns": [self._csl_to_ir(t) for a in getattr(node, 'csl_assigns', []) for t in a.targets]
            },
            "body": self._py_stmts_to_ir(node.body)
        }
        self.program_ir["functions"].append(func_ir)
        self.generic_visit(node)

class Module5_IREmitter:
    """Consumes the validated AAST and outputs a JSON string."""
    def __init__(self, tree: ast.AST):
        self.tree = tree

    def generate_json(self, indent: int = 2) -> str:
        emitter = PyCSLToJSONEmitter()
        emitter.visit(self.tree)
        return json.dumps(emitter.program_ir, indent=indent)
