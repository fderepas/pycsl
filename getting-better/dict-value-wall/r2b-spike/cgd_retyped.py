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
        tparams = decl.get("type_params")
        if tparams:
            generics[decl["name"]] = {
                "type_params": tparams, "decl": decl, "methods": [],
                "kind": "class",
            }
    for func in ir_data.get("functions", []):
        tparams = func.get("type_params")
        if tparams:
            generics[func["name"]] = {
                "type_params": tparams, "decl": None,
                "methods": [func], "kind": "function",
            }
    for func in ir_data.get("functions", []):
        self_type = func.get("self_type") or ""
        if self_type in generics and generics[self_type]["kind"] == "class":
            if func not in generics[self_type]["methods"]:
                generics[self_type]["methods"].append(func)
    return generics
