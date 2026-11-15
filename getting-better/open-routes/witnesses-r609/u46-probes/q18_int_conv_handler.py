from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, str):
        try:
            n = int(v)
        except ValueError:
            return 0
        return 1
    return 1

if __name__ == "__main__":
    r = f({"a": "x"})
    print("VIOLATION contract" if r != 1 else "result", r)
