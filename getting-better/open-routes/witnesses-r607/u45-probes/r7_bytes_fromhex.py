from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": bytes.fromhex("7879")}
    v = d.get("a")
    if isinstance(v, list):
        return 0
    return 1


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 0 else "result", r)
