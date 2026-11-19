r"""Test 9979 -- route #605 (rt59 h16) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R605-PYVAL-INDEX-NO-BOUNDS-VC at HEAD): `args[0]` of a narrowed PyVal list under `no_exception IndexError` PROVED; CPython IndexError for {"args": []}
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ no_exception IndexError
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def first_arg(cfg: Dict[str, PyVal]) -> str:
    args = cfg.get("args")
    if isinstance(args, list):
        return args[0]
    return ""


if __name__ == "__main__":
    try:
        print("result", repr(first_arg({"args": []})))
    except IndexError as e:
        print("VIOLATION no_exception", type(e).__name__, e)
