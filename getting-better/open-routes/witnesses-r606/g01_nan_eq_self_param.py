from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(v: PyVal) -> int:
    if isinstance(v, float):
        if v == v:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f(float("nan"))
    print("VIOLATION contract" if r != 0 else "result", r)
