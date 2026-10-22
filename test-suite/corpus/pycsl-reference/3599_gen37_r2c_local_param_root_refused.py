r"""Test 3599 — gen #37 r2c-wall R2c-local (expected FAIL).

REFUSAL: a path append whose root is a PARAMETER (the caller's tree, route (a), needs the call-site kill rule) is refused.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ ensures True
#@ assigns \nothing
def refuse_param_root(generics: Dict[str, PyVal]) -> int:
    generics["G"]["methods"].append(1)
    return 0
