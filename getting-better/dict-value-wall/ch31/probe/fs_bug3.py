from typing import Any, Dict

PyVal = Any


#@ ensures \result == "same"
#@ assigns \nothing
def g() -> str:
    d: Dict[str, PyVal] = {"a": "x", "b": "y"}
    a = d.get("a", "x")
    b = d.get("b", "y")
    s = f"{a}!"
    t = f"{b}!"
    if s == t:
        return "same"
    return "diff"


if __name__ == "__main__":
    print(g())
