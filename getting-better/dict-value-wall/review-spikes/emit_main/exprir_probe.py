from typing import Any, Dict

#@ assigns \nothing
def ir_kind(node: "ExprIR") -> str:
    if node.get("type") == "Var":
        return node["name"]
    return ""
