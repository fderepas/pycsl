from typing import Any, Dict, List


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(ir: Dict[str, Any], names: List[str]) -> int:
    seen = {g["name"] for g in ir["functions"]}
    for n in names:
        seen.add(n)
    return 1 if "x" in seen else 0


if __name__ == "__main__":
    print(f({"functions": []}, ["x"]))
