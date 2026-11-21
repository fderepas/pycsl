from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x: str = d.get("a") or "z"
    if isinstance(x, str):
        return 0
    return 1


if __name__ == "__main__":
    r = f({"a": 5})
    print("VIOLATION contract" if r != 0 else "result", r)
