r"""Test 9911 -- lvS hval f-string (expected FAIL): `f"{fn}:{ln}"` formats each hval segment by
carrier (an `HStr` segment is its text, any other carrier an unknown string), so `\str_length(\result) == 1`
is FALSE (CPython: "a.mlw:3" has length 7) and must NOT prove. Control: 9910.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \str_length(\result) == 1
#@ assigns \nothing
def sel(loc: Dict[str, PyVal]) -> str:
    fn = loc.get("file-name")
    ln = loc.get("start-line")
    s = f"{fn}:{ln}"
    return s


if __name__ == "__main__":
    r = sel({"file-name": "a.mlw", "start-line": 3})
    print("VIOLATION contract" if len(r) != 1 else "result", r)
