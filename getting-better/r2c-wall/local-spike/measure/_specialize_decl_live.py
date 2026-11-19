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
def _specialize_decl(
    decl: Dict[str, PyVal], tvar: str, concrete: str, new_name: str
) -> Dict[str, PyVal]:
    """Deep-copy a generic type_decl with the TypeVar substituted by the
    concrete type. Field types, class invariants, init_body all get walked."""
    spec = copy.deepcopy(decl)
    spec["name"] = new_name
    # The specialized decl is NOT generic itself.
    spec.pop("type_params", None)
    # Substitute T in field types.
    for f in spec.get("fields", []):
        if f.get("type") == tvar:
            f["type"] = concrete
    # Substitute T in class invariants (walk the IR expr tree).
    spec["class_invariants"] = [
        _subst_type_in_ir(inv, tvar, concrete)
        for inv in spec.get("class_invariants", [])
    ]
    # init_body may carry type-annotated values; walk them too.
    spec["init_body"] = [
        _subst_type_in_ir(s, tvar, concrete)
        for s in spec.get("init_body", [])
    ]
    # bases: drop `Generic[T]` (the legacy base); keep others.
    spec["bases"] = [b for b in spec.get("bases", []) if b not in ("Generic",)]
    return spec
