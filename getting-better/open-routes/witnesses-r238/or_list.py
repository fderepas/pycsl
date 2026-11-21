from typing import Any, Dict

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def g(d: Dict[str, PyVal]) -> int:
    a = d.get("args", []) or []
    return len(a)


if __name__ == "__main__":
    print(g({"args": [1, 2]}))
