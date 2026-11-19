from typing import Any, Dict, Tuple
PyVal = Any

#@ requires True
#@ ensures True
#@ assigns \nothing
def _collect_generic_decls(ir_data: Dict[str, PyVal]) -> Dict[str, PyVal]:
    generics: Dict[str, PyVal] = {}
    for decl in ir_data.get("type_decls", []):
        if decl.get("kind") == "variant":
            continue
        if decl.get("type_params"):
            generics[decl["name"]] = {
                "type_params": decl.get("type_params"), "decl": decl, "methods": [],
                "kind": "class",
            }
    for func in ir_data.get("functions", []):
        if func.get("type_params"):
            generics[func["name"]] = {
                "type_params": func.get("type_params"), "decl": None,
                "methods": [func], "kind": "function",
            }
    for func in ir_data.get("functions", []):
        pass
    return generics
