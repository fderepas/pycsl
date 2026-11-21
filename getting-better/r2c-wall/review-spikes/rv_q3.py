from typing import Any, Dict, List

PyVal = Any

#@ assigns fns
def tag_all(fns: List[Dict[str, PyVal]], v: PyVal) -> None:
    for f in fns:
        f["symbol_table"] = v
