from typing import Any, Dict, List

PyVal = Any

#@ assigns ir
def tag0(ir: Dict[str, PyVal], v: PyVal) -> None:
    ir["functions"][0]["symbol_table"] = v
