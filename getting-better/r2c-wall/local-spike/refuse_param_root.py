from typing import Any, Dict, List

PyVal = Any


#@ ensures True
#@ assigns \nothing
def refuse_param_root(generics: Dict[str, PyVal]) -> int:
    generics["G"]["methods"].append(1)
    return 0
