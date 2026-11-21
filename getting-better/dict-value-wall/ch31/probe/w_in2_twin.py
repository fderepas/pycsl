from typing import Any, Dict

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    holder: Dict[str, PyVal] = {"r": {"fields": {"a": 1}}}
    rec = holder.get("r")
    if "a" in rec["fields"]:
        return 1
    return 2


if __name__ == "__main__":
    print(g())
