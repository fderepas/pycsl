from typing import Any, Dict

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f(ir: Dict[str, Any]) -> int:
    a = len(ir["functions"])
    ir["functions"].insert(0, 5)
    b = len(ir["functions"])
    return 1 if a == b else 0

if __name__ == "__main__":
    print(f({"functions": []}))
