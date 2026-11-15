from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ assigns \nothing
def name(d: Dict[str, PyVal]) -> str:
    return d.get("n") or "anon"

#@ assigns \nothing
def name2(d: Dict[str, PyVal]) -> str:
    s = name(d)
    return s

#@ no_exception \all
#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return len(name2(d))


if __name__ == "__main__":
    try:
        print("result", f({"n": 5}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
