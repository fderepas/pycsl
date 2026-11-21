r"""Test 9995 -- route #603 (expected FAIL: PROVED at int61 e9e12b6a8 -- u45 base proof, scratch log 9995_*.pbase.prove --, REFUSED PYCSL-R603-PYVAL-STR-PASSED-AS-STR at HEAD): NO claim; `d.get("a") or "z"` (a PyVal the model types `string`) is passed to a same-file `is_s(s: str)` whose verified contract `\result == True` assumes a real str, so `f` would prove `\result == True`; CPython f({"a": 5}) is False
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def is_s(s: str) -> bool:
    return isinstance(s, str)


#@ ensures \result == True
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> bool:
    return is_s(d.get("a") or "z")


if __name__ == "__main__":
    print("VIOLATION contract" if f({"a": 5}) is not True else "result", f({"a": 5}))
