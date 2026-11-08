from typing import Any, Dict, List
PyVal = Any

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    holder: Dict[str, PyVal] = {"r": {"f": [*"q"]}}
    rec = holder.get("r")
    if "q" in rec["f"]:
        return 1
    return 2
if __name__ == "__main__":
    assert g() == 2, g()
