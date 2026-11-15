from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ assigns \nothing
def name(d: Dict[str, PyVal]) -> str:
    return d.get("a") or "z"

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    n = name(d)
    if len(n) > 0:
        return len(n[0])
    return 1

if __name__ == "__main__":
    r = f({"a": ["ab"]})
    print("VIOLATION contract" if r != 1 else "result", r)
