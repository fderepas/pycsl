from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {"a": [1]}}
    m = d.get("m") or {}
    x = m.get("a") or "z"
    if isinstance(x, str):
        return 0
    return 1

if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 0 else "result", r)
