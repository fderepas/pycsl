r"""Test 9993 -- route #605 control (expected PASS; advice of PYCSL-R605-PYVAL-INDEX-NO-BOUNDS-VC followed): witness 9979 iterating the narrowed PyVal list instead of reading `args[0]`, under `no_exception IndexError`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ no_exception IndexError
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def first_arg(cfg: Dict[str, PyVal]) -> str:
    args = cfg.get("args")
    if isinstance(args, list):
        for a in args:
            if isinstance(a, str):
                return a
            return ""
    return ""


if __name__ == "__main__":
    ok = first_arg({"args": []}) == "" and first_arg({"args": ["x"]}) == "x"
    print("result" if ok else "VIOLATION contract")
