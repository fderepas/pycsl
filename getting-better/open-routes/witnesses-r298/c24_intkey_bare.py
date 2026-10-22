from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> bool:
    m = d["m"]
    for k in m:
        return isinstance(k, str)
    return True

if __name__ == "__main__":
    print(f({"m": {1: 2}}))
