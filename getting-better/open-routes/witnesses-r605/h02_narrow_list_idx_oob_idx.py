from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ no_exception IndexError
#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, list):
        x = v[5]
    return 0


if __name__ == "__main__":
    try:
        print("result", f({"a": [1]}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
