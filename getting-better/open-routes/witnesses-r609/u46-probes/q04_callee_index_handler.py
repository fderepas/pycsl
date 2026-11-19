from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ assigns \nothing
def first(v: PyVal) -> PyVal:
    if isinstance(v, list):
        return v[0]
    return None

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    try:
        first(d.get("a"))
    except IndexError:
        return 0
    return 1

if __name__ == "__main__":
    r = f({"a": []})
    print("VIOLATION contract" if r != 1 else "result", r)
