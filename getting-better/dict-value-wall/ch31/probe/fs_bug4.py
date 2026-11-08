from typing import Any, Dict

PyVal = Any


#@ ensures \result == "same"
#@ assigns \nothing
def g() -> str:
    d: Dict[str, PyVal] = {"a": "x"}
    a = d.get("a")
    c = 0
    s = f"{a}!"
    t = f"{c}!"
    if s == t:
        return "same"
    return "diff"


if __name__ == "__main__":
    print(g())
