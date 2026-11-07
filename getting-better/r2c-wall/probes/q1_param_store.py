from typing import Any, Dict, List

PyVal = Any

#@ assigns func
def set_st(func: Dict[str, PyVal], v: PyVal) -> None:
    func["symbol_table"] = v
