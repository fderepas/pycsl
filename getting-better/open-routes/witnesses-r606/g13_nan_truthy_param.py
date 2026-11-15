from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    w = d.get("a")
    if isinstance(v, float):
        if v == w:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f({"a": float("nan")})
    print("VIOLATION contract" if r != 0 else "result", r)
