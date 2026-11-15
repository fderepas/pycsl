from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, list):
        try:
            a, b = v
        except ValueError:
            return 0
        return 1
    return 1

if __name__ == "__main__":
    r = f({"a": [1]})
    print("VIOLATION contract" if r != 1 else "result", r)
