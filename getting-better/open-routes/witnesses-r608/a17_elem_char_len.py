from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, list) and len(v) > 0:
        y = v[0]
        if len(y) > 0:
            return len(y[0])
    return 1

if __name__ == "__main__":
    r = f({"a": [["ab"]]})
    print("VIOLATION contract" if r != 1 else "result", r)
