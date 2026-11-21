from typing import Any, Dict

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f(ir: Dict[str, Any]) -> int:
    a = ir["functions"][0]
    ir["functions"].insert(0, 5)
    b = ir["functions"][0]
    return 1 if a == b else 0

if __name__ == "__main__":
    print(f({"functions": [7]}))
