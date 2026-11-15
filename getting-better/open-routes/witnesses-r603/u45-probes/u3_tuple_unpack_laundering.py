from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ assigns \nothing
def pair(d: Dict[str, PyVal]) -> Tuple[str, int]:
    return d.get("a") or "z", 1

#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    a, b = pair(d)
    if isinstance(a, str):
        return 0
    return 1


if __name__ == "__main__":
    r = f({"a": 5})
    print("VIOLATION contract" if r != 0 else "result", r)
