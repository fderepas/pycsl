from contextlib import suppress
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    r = 0
    if isinstance(v, list):
        with suppress(IndexError):
            y = v[0]
            r = 1
        return r
    return 1

if __name__ == "__main__":
    r = f({"a": []})
    print("VIOLATION contract" if r != 1 else "result", r)
