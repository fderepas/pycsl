from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("k", {})
    if isinstance(x, dict):
        return 1
    return 0


if __name__ == "__main__":
    print(f({"k": "s"}))
