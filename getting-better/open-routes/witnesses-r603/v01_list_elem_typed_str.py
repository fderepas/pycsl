from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": [{"b": 1}]}
    v = d.get("a")
    if isinstance(v, list):
        e = v[0]
        if isinstance(e, str):
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 0 else "result", r)
