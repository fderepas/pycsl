from typing import Any, Dict, List
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"a": [*range(0)]}
    if bool(d.get("a")):
        return 1
    return 2
if __name__ == "__main__":
    assert g() == 1, g()
