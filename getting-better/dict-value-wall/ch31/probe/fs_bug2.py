from typing import Any, Dict

PyVal = Any


#@ ensures \result == "0!"
#@ assigns \nothing
def g(d: Dict[str, PyVal]) -> str:
    n = d.get("name", "abc")
    return f"{n}!"


if __name__ == "__main__":
    print(g({"name": "abc"}))
