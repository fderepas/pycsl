from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": {"k": 1}}
    x = d["a"]["k"]["j"]
    return 0

if __name__ == "__main__":
    try:
        print("result", f(0))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
