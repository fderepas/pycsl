from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> bool:
    x = d.get("a") or "z"
    x *= 0
    return x == ""

if __name__ == "__main__":
    r = f({"a": [1]})
    print("VIOLATION contract" if r != True else "result", r)
