import copy
from typing import Any, Dict, List, Optional, Tuple

PyVal = Any


#@ requires True
#@ ensures True
#@ assigns \nothing
def _subst_type_in_ir(node: PyVal, tvar: str, concrete: str) -> PyVal:
    return node


#@ requires True
#@ ensures True
#@ assigns \nothing
def _specialize_function(
    func: Dict[str, PyVal], tvar: str, concrete: str,
    new_class_name: str, new_self_type: Optional[str] = None,
) -> Dict[str, PyVal]:
    """Deep-copy a generic function/method with T substituted."""
    spec = copy.deepcopy(func)
    # Substitute T in the symbol_table (param/return types).
    spec["symbol_table"] = {
        k: (concrete if v == tvar else v)
        for k, v in (spec.get("symbol_table") or {}).items()
    }
    if spec.get("return_annotation") == tvar:
        spec["return_annotation"] = concrete
    # self_type -> the specialized class name.
    if new_self_type is not None and spec.get("self_type"):
        spec["self_type"] = new_self_type
    # Substitute T in contract clauses (requires/ensures/assigns/raises) and body.
    contracts = spec.get("contracts") or {}
    for clause in ("requires", "ensures", "assigns"):
        if clause in contracts:
            contracts[clause] = [
                _subst_type_in_ir(c, tvar, concrete)
                for c in contracts[clause]
            ]
    spec["body"] = [
        _subst_type_in_ir(s, tvar, concrete)
        for s in spec.get("body", [])
    ]
    # The specialized function is NOT generic itself.
    return spec
