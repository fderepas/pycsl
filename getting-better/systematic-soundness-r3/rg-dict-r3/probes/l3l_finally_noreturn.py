from typing import Dict, Any, Set

#@ ensures \result == 1
def f(m: Dict[str, Any], t: Set[Any]) -> int:
    r = 2
    try:
        t.add(m.get("a"))
        r = 1
    finally:
        r = r + 0
    return r

if __name__ == "__main__":
    print(f({"a": [1]}, set()))
