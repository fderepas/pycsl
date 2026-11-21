# pycsl-flags: --memory-model hoare
from typing import Dict

OP_MAP: Dict[str, str] = {"a": "x", "b": "y"}


#@ requires True
#@ ensures \result == "x"
#@ assigns \nothing
def f() -> str:
    OP_MAP["a"] = "z"
    return OP_MAP.get("a", "d")
