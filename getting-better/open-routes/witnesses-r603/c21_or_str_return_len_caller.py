from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ assigns \nothing
def name(d: Dict[str, PyVal]) -> str:
    return d.get("name") or "anon"


#@ no_exception \all
#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return len(name(d))


if __name__ == "__main__":
    try:
        print("result", f({"name": 5}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
