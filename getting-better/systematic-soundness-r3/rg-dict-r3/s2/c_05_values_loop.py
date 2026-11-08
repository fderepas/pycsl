from typing import Dict, Any, Set


#@ ensures \result == 1
def f(m: Dict[str, Any], seen: Set[str]) -> int:
    for v in m.values():
        if v in seen:
            return 1
    return 1


if __name__ == "__main__":
    print(f({"a": [1]}, set()))
