from typing import Any, Dict, List, Optional, Set, Tuple
PyVal = Any

_KNOWN = {"a": 1, "b": 2}


#@ assigns \nothing
def key(d: Dict[str, PyVal]) -> str:
    return d.get("a") or "z"


#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    if key(d) in _KNOWN:
        return 0
    return 0


if __name__ == "__main__":
    try:
        print("result", f({"a": [1]}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
