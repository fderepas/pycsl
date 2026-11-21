from typing import Any, Dict


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(ir: Dict[str, Any]) -> int:
    seen = {g["name"] for g in ir["functions"]}
    other = seen
    seen.add("x")
    return 1 if "x" in other else 0


if __name__ == "__main__":
    print(f({"functions": []}))
