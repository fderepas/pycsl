from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("a") or "z"
    if len(x) > 0:
        #@ assert len(x[0]) == 1
        return 1
    return 1

if __name__ == "__main__":
    d = {"a": ["ab"]}
    x = d.get("a") or "z"
    print("VIOLATION assert" if len(x[0]) != 1 else "result", f(d))
