from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("a") or "z"
    if len(x) > 0:
        return len(x[0])
    return 1

if __name__ == "__main__":
    r = f({"a": ["ab"]})
    print("VIOLATION contract" if r != 1 else "result", r)
