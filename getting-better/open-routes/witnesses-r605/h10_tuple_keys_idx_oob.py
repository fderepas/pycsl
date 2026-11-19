from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ no_exception IndexError
#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {"a": 1}}
    ks = tuple(d.get("m") or {})
    if ks[5] == "q":
        return 0
    return 0


if __name__ == "__main__":
    try:
        print("result", f(0))
    except IndexError as e:
        print("VIOLATION no_exception", type(e).__name__, e)
