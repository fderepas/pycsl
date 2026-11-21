from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(cs: Dict[str, Dict[str, PyVal]]) -> int:
    for c in cs.values():
        x = c.get("a") or "z"
        if isinstance(x, str):
            return 0
        return 1
    return 0

if __name__ == "__main__":
    r = f({"k": {"a": 5}})
    print("VIOLATION contract" if r != 0 else "result", r)
