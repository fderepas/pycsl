from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> bool:
    xs = d["xs"]
    for k, v in xs.items():
        return isinstance(k, str)
    return True

if __name__ == "__main__":
    print(f({"xs": {1: 2}}))
