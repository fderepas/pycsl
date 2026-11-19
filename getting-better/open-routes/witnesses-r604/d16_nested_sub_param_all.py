from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    if "a" in d:
        v = d["a"]
        if isinstance(v, list):
            x = d["a"]["k"]
    return 0


if __name__ == "__main__":
    try:
        print("result", f({"a": [1]}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
