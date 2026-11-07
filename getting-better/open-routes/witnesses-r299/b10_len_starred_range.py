from typing import Any, Dict, List
PyVal = Any

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"a": [*range(2), 3]}
    return len(d.get("a"))
if __name__ == "__main__":
    assert g() == 2, g()
