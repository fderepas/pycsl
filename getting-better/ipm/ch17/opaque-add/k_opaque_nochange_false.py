from typing import Any, Dict


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f(ir: Dict[str, Any]) -> int:
    seen = {g["name"] for g in ir["functions"]}
    a = len(seen)
    seen.add("x")
    b = len(seen)
    return 1 if a == b else 0


if __name__ == "__main__":
    print(f({"functions": []}))
