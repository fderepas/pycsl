import ast
import json
from typing import Any, Dict, List, Optional
from Module2_Parser import (
    CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    BinOp as CSLBinOp, UnaryOp as CSLUnaryOp, Var as CSLVar, 
    Number as CSLNumber, Result as CSLResult, Old as CSLOld, Nothing,
    FieldAccess as CSLFieldAccess, Forall, Exists, ArrayLength, SubscriptAccess,
    AssignsRegion, Valid, Separated, At as CSLAt,
    Length2D, Valid2D, FunctionVariant, StringLiteral as CSLStringLiteral,
    CallExpr, IsSorted, Sum, CSLBool, CSLNone, CSLIn, CSLNotIn, CSLSlice
)

class PyCSLToJSONEmitter(ast.NodeVisitor):
    """Walks the Annotated AST and translates it into a JSON-serializable IR."""
    
    def __init__(self):
        self.program_ir = {"type_decls": [], "functions": []}
        self._current_class: Optional[str] = None

    # --- 1. PyCSL Contract Serialization ---
    def _csl_to_ir(self, node: CSLNode) -> Dict[str, Any]:
        """Recursively translates PyCSL nodes into IR dictionaries."""
        if isinstance(node, CSLBinOp):
            return {"type": "BinOp", "op": node.op, "left": self._csl_to_ir(node.left), "right": self._csl_to_ir(node.right)}
        elif isinstance(node, CSLUnaryOp):
            return {"type": "UnaryOp", "op": node.op, "expr": self._csl_to_ir(node.expr)}
        elif isinstance(node, CSLFieldAccess):
            return {"type": "FieldGet", "object": node.object, "field": node.field}
        elif isinstance(node, CSLVar):
            return {"type": "Var", "name": node.name}
        elif isinstance(node, CSLNumber):
            return {"type": "Number", "value": node.value}
        elif isinstance(node, CSLStringLiteral):
            return {"type": "String", "value": node.value}
        elif isinstance(node, CSLBool):
            return {"type": "Bool", "value": node.value}
        elif isinstance(node, CSLNone):
            return {"type": "None"}
        elif isinstance(node, CSLResult):
            return {"type": "Result"}
        elif isinstance(node, CSLOld):
            # Old(FieldAccess) → OldField (flat node)
            if isinstance(node.expr, CSLFieldAccess):
                return {"type": "OldField", "object": node.expr.object, "field": node.expr.field}
            return {"type": "Old", "expr": self._csl_to_ir(node.expr)}
        elif isinstance(node, Nothing):
            return {"type": "Nothing"}
        elif isinstance(node, Forall):
            return {"type": "Forall", "var": node.var, "body": self._csl_to_ir(node.body)}
        elif isinstance(node, Exists):
            return {"type": "Exists", "var": node.var, "body": self._csl_to_ir(node.body)}
        elif isinstance(node, ArrayLength):
            return {"type": "ArrayLen", "var": node.var}
        elif isinstance(node, SubscriptAccess):
            if node.array == "\\result":
                return {"type": "Subscript",
                        "value": {"type": "Result"},
                        "index": self._csl_to_ir(node.index)}
            return {"type": "Subscript",
                    "value": {"type": "Var", "name": node.array},
                    "index": self._csl_to_ir(node.index)}
        elif isinstance(node, AssignsRegion):
            return {
                "type": "AssignsRegion",
                "base": node.base,
                "low": self._csl_to_ir(node.low),
                "high": self._csl_to_ir(node.high)
            }
        elif isinstance(node, Valid):
            return {
                "type": "Valid",
                "base": node.base,
                "length": self._csl_to_ir(node.length)
            }
        elif isinstance(node, Separated):
            return {
                "type": "Separated",
                "base1": node.base1,
                "len1": self._csl_to_ir(node.length1),
                "base2": node.base2,
                "len2": self._csl_to_ir(node.length2)
            }
        elif isinstance(node, CSLAt):
            return {"type": "At", "expr": self._csl_to_ir(node.expr), "label": node.label}
        elif isinstance(node, Length2D):
            return {
                "type": "Length2D",
                "base": node.base,
                "rows": self._csl_to_ir(node.rows),
                "cols": self._csl_to_ir(node.cols)
            }
        elif isinstance(node, Valid2D):
            return {
                "type": "Valid2D",
                "base": node.base,
                "row": self._csl_to_ir(node.row),
                "col": self._csl_to_ir(node.col)
            }
        elif isinstance(node, (Requires, Ensures, LoopInvariant, LoopVariant)):
            return self._csl_to_ir(node.expr)
        elif isinstance(node, FunctionVariant):
            ir = {"expr": self._csl_to_ir(node.expr)}
            if node.ordering:
                ir["ordering"] = node.ordering
            return ir
        elif isinstance(node, CallExpr):
            return {
                "type": "Call",
                "func": node.func,
                "args": [self._csl_to_ir(a) for a in node.args]
            }
        elif isinstance(node, IsSorted):
            return {
                "type": "IsSorted",
                "base": node.base,
                "lo": self._csl_to_ir(node.lo),
                "hi": self._csl_to_ir(node.hi)
            }
        elif isinstance(node, Sum):
            return {
                "type": "Sum",
                "base": node.base,
                "lo": self._csl_to_ir(node.lo),
                "hi": self._csl_to_ir(node.hi)
            }
        elif isinstance(node, CSLIn):
            # x in arr → ∃ _mem_i. 0 ≤ _mem_i ∧ _mem_i < length(arr) ∧ arr[_mem_i] == x
            elt_ir = self._csl_to_ir(node.element)
            coll_ir = self._csl_to_ir(node.collection)
            coll_name = coll_ir.get("name", "_coll")
            return {
                "type": "Exists", "var": "_mem_i",
                "body": {"type": "BinOp", "op": "and",
                    "left": {"type": "BinOp", "op": "and",
                        "left": {"type": "BinOp", "op": ">=",
                            "left": {"type": "Var", "name": "_mem_i"},
                            "right": {"type": "Number", "value": 0}},
                        "right": {"type": "BinOp", "op": "<",
                            "left": {"type": "Var", "name": "_mem_i"},
                            "right": {"type": "ArrayLen", "var": coll_name}}},
                    "right": {"type": "BinOp", "op": "==",
                        "left": {"type": "Subscript",
                            "value": {"type": "Var", "name": coll_name},
                            "index": {"type": "Var", "name": "_mem_i"}},
                        "right": elt_ir}}
            }
        elif isinstance(node, CSLNotIn):
            # x not in arr → ¬(x in arr)
            in_ir = self._csl_to_ir(CSLIn(node.element, node.collection))
            return {"type": "UnaryOp", "op": "not", "expr": in_ir}
        elif isinstance(node, CSLSlice):
            return {"type": "SliceAccess",
                    "value": {"type": "Var", "name": node.collection},
                    "slice": {"type": "Slice",
                              "lower": self._csl_to_ir(node.low),
                              "upper": self._csl_to_ir(node.high),
                              "step": None}}
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
            ast.USub: "-", ast.UAdd: "+", ast.Not: "not",
            ast.In: "in", ast.NotIn: "not in",
            ast.Is: "==", ast.IsNot: "!=",
            ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
            ast.LShift: "<<", ast.RShift: ">>", ast.Pow: "**",
        }
        return ops.get(type(op), "?")

    def _py_expr_to_ir(self, expr: ast.expr) -> Dict[str, Any]:
        """Translates Python expressions into IR dictionaries."""
        if isinstance(expr, ast.Name):
            return {"type": "Var", "name": expr.id}
        elif isinstance(expr, ast.Constant):
            if expr.value is None:
                return {"type": "None"}
            if isinstance(expr.value, bool):
                return {"type": "Bool", "value": expr.value}
            if isinstance(expr.value, str):
                return {"type": "String", "value": expr.value}
            if isinstance(expr.value, bytes):
                return {"type": "String", "value": expr.value.decode('utf-8', errors='replace')}
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
        elif isinstance(expr, ast.BoolOp):
            op_str = "and" if isinstance(expr.op, ast.And) else "or"
            result = self._py_expr_to_ir(expr.values[0])
            for operand in expr.values[1:]:
                result = {"type": "BinOp", "op": op_str, "left": result, "right": self._py_expr_to_ir(operand)}
            return result
        elif isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Name):
                return {
                    "type": "Call",
                    "func": expr.func.id,
                    "args": [self._py_expr_to_ir(arg) for arg in expr.args]
                }
            elif isinstance(expr.func, ast.Attribute):
                # Method/attribute call: a.b.c(x) → flattened func name
                parts = []
                node = expr.func
                while isinstance(node, ast.Attribute):
                    parts.append(node.attr)
                    node = node.value
                if isinstance(node, ast.Name):
                    parts.append(node.id)
                    parts.reverse()
                    return {
                        "type": "Call",
                        "func": ".".join(parts),
                        "args": [self._py_expr_to_ir(arg) for arg in expr.args]
                    }
                # Fallback: complex receiver expression
                receiver_ir = self._py_expr_to_ir(node)
                parts.reverse()
                return {
                    "type": "Call",
                    "func": ".".join(parts),
                    "args": [self._py_expr_to_ir(arg) for arg in expr.args],
                    "receiver": receiver_ir
                }
        elif isinstance(expr, ast.Tuple):
            return {"type": "Tuple", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}
        elif isinstance(expr, ast.Subscript):
            value = self._py_expr_to_ir(expr.value)
            slice_node = expr.slice
            if isinstance(slice_node, ast.Index):
                slice_node = slice_node.value
            if isinstance(slice_node, ast.Slice):
                slice_ir = self._py_expr_to_ir(slice_node)
                return {"type": "SliceAccess", "value": value, "slice": slice_ir}
            index = self._py_expr_to_ir(slice_node)
            return {"type": "Subscript", "value": value, "index": index}
        elif isinstance(expr, ast.List):
            return {"type": "ArrayLit", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}
        elif isinstance(expr, ast.Attribute):
            if isinstance(expr.value, ast.Name) and expr.value.id == 'self':
                return {"type": "FieldGet", "object": "self", "field": expr.attr}
            # Non-self attribute access: obj.attr → chained attribute path
            obj_ir = self._py_expr_to_ir(expr.value)
            return {"type": "Attribute", "object": obj_ir, "attr": expr.attr}
        elif isinstance(expr, ast.Dict):
            keys = [self._py_expr_to_ir(k) if k else {"type": "None"} for k in expr.keys]
            values = [self._py_expr_to_ir(v) for v in expr.values]
            return {"type": "DictLit", "keys": keys, "values": values}
        elif isinstance(expr, ast.Set):
            return {"type": "SetLit", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}
        elif isinstance(expr, ast.ListComp):
            elt = self._py_expr_to_ir(expr.elt)
            generators = []
            for gen in expr.generators:
                target = gen.target.id if isinstance(gen.target, ast.Name) else "_comp_var"
                generators.append({
                    "target": target,
                    "iter": self._py_expr_to_ir(gen.iter),
                    "ifs": [self._py_expr_to_ir(if_) for if_ in gen.ifs]
                })
            return {"type": "ListComp", "elt": elt, "generators": generators}
        elif isinstance(expr, ast.SetComp):
            elt = self._py_expr_to_ir(expr.elt)
            generators = []
            for gen in expr.generators:
                target = gen.target.id if isinstance(gen.target, ast.Name) else "_comp_var"
                generators.append({
                    "target": target,
                    "iter": self._py_expr_to_ir(gen.iter),
                    "ifs": [self._py_expr_to_ir(if_) for if_ in gen.ifs]
                })
            return {"type": "SetComp", "elt": elt, "generators": generators}
        elif isinstance(expr, ast.DictComp):
            key = self._py_expr_to_ir(expr.key)
            value = self._py_expr_to_ir(expr.value)
            generators = []
            for gen in expr.generators:
                target = gen.target.id if isinstance(gen.target, ast.Name) else "_comp_var"
                generators.append({
                    "target": target,
                    "iter": self._py_expr_to_ir(gen.iter),
                    "ifs": [self._py_expr_to_ir(if_) for if_ in gen.ifs]
                })
            return {"type": "DictComp", "key": key, "value": value, "generators": generators}
        elif isinstance(expr, ast.JoinedStr):
            # f-string: concatenation of literal parts and formatted values
            parts = []
            for v in expr.values:
                if isinstance(v, ast.Constant):
                    parts.append({"type": "String", "value": str(v.value)})
                elif isinstance(v, ast.FormattedValue):
                    parts.append(self._py_expr_to_ir(v.value))
                else:
                    parts.append(self._py_expr_to_ir(v))
            return {"type": "FString", "parts": parts}
        elif isinstance(expr, ast.IfExp):
            return {
                "type": "IfExpr",
                "test": self._py_expr_to_ir(expr.test),
                "body": self._py_expr_to_ir(expr.body),
                "orelse": self._py_expr_to_ir(expr.orelse)
            }
        elif isinstance(expr, ast.Starred):
            return {"type": "Starred", "value": self._py_expr_to_ir(expr.value)}
        elif isinstance(expr, ast.NamedExpr):
            # Walrus operator: (x := expr) → emits as NamedExpr IR
            target_name = expr.target.id if isinstance(expr.target, ast.Name) else "_walrus"
            return {"type": "NamedExpr", "target": target_name,
                    "value": self._py_expr_to_ir(expr.value)}
        elif isinstance(expr, ast.Lambda):
            params = [arg.arg for arg in expr.args.args]
            return {"type": "Lambda", "params": params,
                    "body": self._py_expr_to_ir(expr.body)}
        elif isinstance(expr, ast.Slice):
            lower = self._py_expr_to_ir(expr.lower) if expr.lower else None
            upper = self._py_expr_to_ir(expr.upper) if expr.upper else None
            step = self._py_expr_to_ir(expr.step) if expr.step else None
            return {"type": "Slice", "lower": lower, "upper": upper, "step": step}
        return {"type": "UnknownPyExpr"}

    def _py_stmts_to_ir(self, stmts: List[ast.stmt]) -> List[Dict[str, Any]]:
        ir_stmts = []
        for stmt in stmts:
            # Prepend any label declarations attached to this statement
            for lname in getattr(stmt, 'csl_labels', []):
                ir_stmts.append({"stmt": "Label", "name": lname})
            # Prepend any ghost assignments attached to this statement
            for ga in getattr(stmt, 'csl_ghost_assigns', []):
                ir_stmts.append({
                    "stmt": "GhostAssign",
                    "target": ga.target,
                    "value": self._csl_to_ir(ga.value),
                    "op": ga.op
                })
            if isinstance(stmt, ast.Assign):
                target = stmt.targets[0]
                if isinstance(target, ast.Name):
                    ir_stmts.append({"stmt": "Assign", "target": target.id, "value": self._py_expr_to_ir(stmt.value)})
                elif (isinstance(target, ast.Attribute) and
                      isinstance(target.value, ast.Name) and
                      target.value.id == 'self'):
                    ir_stmts.append({"stmt": "FieldAssign", "object": "self", "field": target.attr,
                                     "value": self._py_expr_to_ir(stmt.value)})
                elif isinstance(target, ast.Subscript):
                    array_ir = self._py_expr_to_ir(target.value)
                    slice_node = target.slice
                    if isinstance(slice_node, ast.Index):
                        slice_node = slice_node.value
                    index_ir = self._py_expr_to_ir(slice_node)
                    ir_stmts.append({"stmt": "ArraySet", "array": array_ir,
                                     "index": index_ir, "value": self._py_expr_to_ir(stmt.value)})
                elif isinstance(target, ast.Tuple):
                    targets = [elt.id for elt in target.elts if isinstance(elt, ast.Name)]
                    ir_stmts.append({"stmt": "TupleUnpack", "targets": targets,
                                     "value": self._py_expr_to_ir(stmt.value)})
            elif isinstance(stmt, ast.AugAssign):
                if isinstance(stmt.target, ast.Name):
                    ir_stmts.append({"stmt": "AugAssign", "target": stmt.target.id,
                                     "op": self._py_op_to_str(stmt.op), "value": self._py_expr_to_ir(stmt.value)})
                elif (isinstance(stmt.target, ast.Attribute) and
                      isinstance(stmt.target.value, ast.Name) and
                      stmt.target.value.id == 'self'):
                    ir_stmts.append({"stmt": "FieldAugAssign", "object": "self", "field": stmt.target.attr,
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
            elif isinstance(stmt, ast.Assert):
                ir_node = {"stmt": "Assert", "test": self._py_expr_to_ir(stmt.test)}
                if stmt.msg and isinstance(stmt.msg, ast.Constant) and isinstance(stmt.msg.value, str):
                    ir_node["msg"] = stmt.msg.value
                ir_stmts.append(ir_node)
            elif isinstance(stmt, ast.Raise):
                exc_ir: Dict[str, Any] = {"stmt": "Raise", "exc_type": None, "exc_value": None}
                if stmt.exc is not None:
                    if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                        exc_ir["exc_type"] = stmt.exc.func.id
                        if stmt.exc.args:
                            exc_ir["exc_value"] = self._py_expr_to_ir(stmt.exc.args[0])
                    elif isinstance(stmt.exc, ast.Name):
                        exc_ir["exc_type"] = stmt.exc.id
                ir_stmts.append(exc_ir)
            elif isinstance(stmt, ast.AnnAssign):
                if isinstance(stmt.target, ast.Name) and stmt.value is not None:
                    ir_stmts.append({"stmt": "Assign", "target": stmt.target.id,
                                     "value": self._py_expr_to_ir(stmt.value)})
            elif isinstance(stmt, ast.Expr):
                # Skip bare string-literal expressions (docstrings) — no WhyML equivalent.
                if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                    continue
                ir_stmts.append({"stmt": "Expr", "value": self._py_expr_to_ir(stmt.value)})
            elif isinstance(stmt, ast.Try):
                # try/except → emit body; handlers become catch clauses
                body_ir = self._py_stmts_to_ir(stmt.body)
                handlers = []
                for h in stmt.handlers:
                    exc_type = None
                    if h.type and isinstance(h.type, ast.Name):
                        exc_type = h.type.id
                    elif h.type and isinstance(h.type, ast.Tuple):
                        exc_type = "|".join(
                            n.id for n in h.type.elts if isinstance(n, ast.Name))
                    handlers.append({
                        "exc_type": exc_type,
                        "name": h.name,
                        "body": self._py_stmts_to_ir(h.body)
                    })
                ir_stmts.append({
                    "stmt": "Try",
                    "body": body_ir,
                    "handlers": handlers,
                    "orelse": self._py_stmts_to_ir(stmt.orelse),
                    "finalbody": self._py_stmts_to_ir(stmt.finalbody)
                })
            elif isinstance(stmt, ast.With):
                # with stmt → emit body (context manager is abstracted away)
                ir_stmts.extend(self._py_stmts_to_ir(stmt.body))
            elif isinstance(stmt, ast.Pass):
                ir_stmts.append({"stmt": "Pass"})
            elif isinstance(stmt, ast.Break):
                ir_stmts.append({"stmt": "Break"})
            elif isinstance(stmt, ast.Delete):
                ir_stmts.append({"stmt": "Pass"})  # model as no-op
            elif hasattr(ast, 'Match') and isinstance(stmt, ast.Match):
                subject_ir = self._py_expr_to_ir(stmt.subject)
                cases = []
                for case in stmt.cases:
                    pattern_ir = self._match_pattern_to_ir(case.pattern)
                    guard_ir = self._py_expr_to_ir(case.guard) if case.guard else None
                    body_ir = self._py_stmts_to_ir(case.body)
                    cases.append({"pattern": pattern_ir, "guard": guard_ir, "body": body_ir})
                ir_stmts.append({"stmt": "Match", "subject": subject_ir, "cases": cases})
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

    def _match_pattern_to_ir(self, pattern) -> Dict[str, Any]:
        """Translate a Python 3.10+ match pattern to IR."""
        if hasattr(ast, 'MatchValue') and isinstance(pattern, ast.MatchValue):
            return {"pattern": "Value", "value": self._py_expr_to_ir(pattern.value)}
        elif hasattr(ast, 'MatchSingleton') and isinstance(pattern, ast.MatchSingleton):
            if pattern.value is True:
                return {"pattern": "Value", "value": {"type": "Bool", "value": True}}
            elif pattern.value is False:
                return {"pattern": "Value", "value": {"type": "Bool", "value": False}}
            elif pattern.value is None:
                return {"pattern": "Value", "value": {"type": "None"}}
            return {"pattern": "Value", "value": {"type": "Number", "value": pattern.value}}
        elif hasattr(ast, 'MatchAs') and isinstance(pattern, ast.MatchAs):
            if pattern.name is None and pattern.pattern is None:
                return {"pattern": "Wildcard"}
            name = pattern.name if pattern.name else "_"
            if pattern.pattern:
                return {"pattern": "Capture", "name": name,
                        "inner": self._match_pattern_to_ir(pattern.pattern)}
            return {"pattern": "Capture", "name": name, "inner": None}
        elif hasattr(ast, 'MatchOr') and isinstance(pattern, ast.MatchOr):
            return {"pattern": "Or",
                    "alternatives": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
        elif hasattr(ast, 'MatchSequence') and isinstance(pattern, ast.MatchSequence):
            return {"pattern": "Sequence",
                    "elts": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
        return {"pattern": "Unknown"}

    def _scan_2d_in_expr(self, expr: Dict[str, Any], param_names: set, result: set) -> None:
        """Recursively scan an IR expression dict for a[i][j] access patterns."""
        if not isinstance(expr, dict):
            return
        t = expr.get("type", "")
        if t == "Subscript":
            inner = expr.get("value", {})
            if inner.get("type") == "Subscript":
                root = inner.get("value", {})
                if root.get("type") == "Var" and root.get("name") in param_names:
                    # Exclude dict-style access (string indices) from 2D array detection
                    idx1 = inner.get("index", {})
                    idx2 = expr.get("index", {})
                    if idx1.get("type") != "String" and idx2.get("type") != "String":
                        result.add(root["name"])
            self._scan_2d_in_expr(inner, param_names, result)
            self._scan_2d_in_expr(expr.get("index", {}), param_names, result)
        elif t in ("BinOp",):
            self._scan_2d_in_expr(expr.get("left", {}), param_names, result)
            self._scan_2d_in_expr(expr.get("right", {}), param_names, result)
        elif t in ("UnaryOp",):
            self._scan_2d_in_expr(expr.get("expr", {}), param_names, result)
        elif t in ("Call",):
            for arg in expr.get("args", []):
                self._scan_2d_in_expr(arg, param_names, result)

    def _scan_2d_in_stmt(self, stmt: Dict[str, Any], param_names: set, result: set) -> None:
        """Recursively scan an IR statement dict for a[i][j] access patterns."""
        s = stmt.get("stmt", "")
        if s == "ArraySet":
            arr = stmt.get("array", {})
            # a[i][j] = v  →  ArraySet(array=Subscript(Var(a), i), index=j, ...)
            if arr.get("type") == "Subscript":
                root = arr.get("value", {})
                if root.get("type") == "Var" and root.get("name") in param_names:
                    idx1 = arr.get("index", {})
                    idx2 = stmt.get("index", {})
                    if idx1.get("type") != "String" and idx2.get("type") != "String":
                        result.add(root["name"])
            self._scan_2d_in_expr(arr, param_names, result)
            self._scan_2d_in_expr(stmt.get("index", {}), param_names, result)
            self._scan_2d_in_expr(stmt.get("value", {}), param_names, result)
        elif s in ("Assign", "AugAssign", "Return"):
            self._scan_2d_in_expr(stmt.get("value", {}), param_names, result)
        elif s in ("While", "For"):
            self._scan_2d_in_expr(stmt.get("test", {}), param_names, result)
            for child in stmt.get("body", []):
                self._scan_2d_in_stmt(child, param_names, result)
        elif s == "If":
            self._scan_2d_in_expr(stmt.get("test", {}), param_names, result)
            for child in stmt.get("body", []):
                self._scan_2d_in_stmt(child, param_names, result)
            for child in stmt.get("orelse", []):
                self._scan_2d_in_stmt(child, param_names, result)

    def _collect_2d_params(self, body_ir: List[Dict[str, Any]],
                           param_names: set) -> List[str]:
        """Return sorted list of param names used as a[i][j] in the body IR."""
        result: set = set()
        for stmt in body_ir:
            self._scan_2d_in_stmt(stmt, param_names, result)
        return sorted(result)

    # --- 3. Main Traversal Hooks ---
    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        """Collect fields from __init__, extract class invariants, and emit a type_decl record."""
        self._current_class = node.name
        # Collect mutable fields and their initial values from __init__ assignments to self.*
        fields = []
        field_names_seen = set()
        field_defaults = {}  # field_name → initial constant value (for `by` witness)
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == '__init__':
                for stmt in ast.walk(child):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if (isinstance(target, ast.Attribute) and
                                    isinstance(target.value, ast.Name) and
                                    target.value.id == 'self' and
                                    target.attr not in field_names_seen):
                                fields.append({"name": target.attr, "type": "int", "mutable": True})
                                field_names_seen.add(target.attr)
                                if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, (int, float)):
                                    field_defaults[target.attr] = int(stmt.value.value)
                    elif isinstance(stmt, ast.AnnAssign):
                        if (isinstance(stmt.target, ast.Attribute) and
                                isinstance(stmt.target.value, ast.Name) and
                                stmt.target.value.id == 'self' and
                                stmt.target.attr not in field_names_seen):
                            fields.append({"name": stmt.target.attr, "type": "int", "mutable": True})
                            field_names_seen.add(stmt.target.attr)
                            if (stmt.value and isinstance(stmt.value, ast.Constant) and
                                    isinstance(stmt.value.value, (int, float))):
                                field_defaults[stmt.target.attr] = int(stmt.value.value)
        if fields:
            # Convert class invariants from CSL AST to IR
            class_invariants_ir = []
            for inv in getattr(node, 'csl_class_invariants', []):
                class_invariants_ir.append(self._csl_to_ir(inv.expr))

            # Build default witness from initial values (fallback to 0)
            field_witness = {}
            for f in fields:
                field_witness[f["name"]] = field_defaults.get(f["name"], 0)

            self.program_ir["type_decls"].append({
                "kind": "record",
                "name": node.name,
                "fields": fields,
                "class_invariants": class_invariants_ir,
                "field_defaults": field_witness
            })
        self.generic_visit(node)
        self._current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        # Skip dunder methods (__init__, __str__, …) and @property inside classes
        if self._current_class:
            if node.name.startswith('__') and node.name.endswith('__'):
                return
            if any(isinstance(d, ast.Name) and d.id == 'property'
                   for d in node.decorator_list):
                return

        func_name = (f"{self._current_class.lower()}__{node.name}"
                     if self._current_class else node.name)

        # symbol_table from Module4 already excludes 'self' and includes obj_* fields
        symbol_table = {
            k: v for k, v in getattr(node, 'csl_symbol_table', {}).items()
            if k != 'self'
        }

        # Extract return type annotation if present
        return_annotation = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_annotation = node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return_annotation = str(node.returns.value)

        func_ir = {
            "name": func_name,
            "symbol_table": symbol_table,
            "return_annotation": return_annotation,
            "contracts": {
                "requires": self._csl_list_to_ir(getattr(node, 'csl_requires', [])),
                "ensures": self._csl_list_to_ir(getattr(node, 'csl_ensures', [])),
                "assigns": [self._csl_to_ir(t) for a in getattr(node, 'csl_assigns', []) for t in a.targets],
                "raises": [{"exc_type": r.exc_type, "condition": self._csl_to_ir(r.condition)}
                           for r in getattr(node, 'csl_raises', [])]
            },
            "body": self._py_stmts_to_ir(node.body),
            "function_variants": self._csl_list_to_ir(getattr(node, 'csl_function_variants', [])),
            "diverges": getattr(node, 'csl_diverges', False),
            "trusted": getattr(node, 'csl_trusted', False),
            "bounded_int": getattr(node, 'csl_bounded_int', None)
        }
        # A function is pure if it assigns nothing, doesn't diverge, and isn't trusted
        assigns = func_ir["contracts"]["assigns"]
        is_pure = (len(assigns) == 1 and isinstance(assigns[0], dict)
                   and assigns[0].get("type") == "Nothing"
                   and not func_ir["diverges"]
                   and not func_ir["trusted"])
        if is_pure:
            func_ir["pure"] = True
        # Detect 2D array params: from \length2d contracts and from body a[i][j] patterns.
        # Include "Any"-typed params since untyped params may be 2D arrays.
        candidate_params = {k for k, v in symbol_table.items() if v in ("list", "Any")}
        array2d: set = set()
        # 1. Params declared via \length2d in requires contracts
        for req in func_ir["contracts"]["requires"]:
            if isinstance(req, dict) and req.get("type") == "Length2D":
                base = req.get("base")
                if base in candidate_params:
                    array2d.add(base)
        # 2. Params used as a[i][j] in the body
        if candidate_params:
            array2d.update(self._collect_2d_params(func_ir["body"], candidate_params))
        if array2d:
            func_ir["array2d_params"] = sorted(array2d)

        # Detect 1D array params from \valid contracts (params not already detected as 2D).
        array1d: set = set()
        for req in func_ir["contracts"]["requires"]:
            if isinstance(req, dict) and req.get("type") == "Valid":
                base = req.get("base")
                if base and base in candidate_params and base not in array2d:
                    array1d.add(base)
        if array1d:
            func_ir["array1d_params"] = sorted(array1d)
        if self._current_class:
            func_ir["kind"] = "method"
            func_ir["self_type"] = self._current_class
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
