from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def h(d: Dict[str, PyVal]) -> int:
    x = d.get("k", {})
    if not isinstance(x, dict):
        return 0
    return 1


if __name__ == "__main__":
    print(h({"k": 5}))
