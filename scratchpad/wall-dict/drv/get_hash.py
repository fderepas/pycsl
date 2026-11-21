from typing import Dict, Any, Set

#@ no_exception \all
#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1

#@ no_exception \all
#@ ensures \result == 1
def g(f2: Dict[str, Any], seen: Set[Any]) -> int:
    seen.add(f2.get("name"))
    return 1

if __name__ == "__main__":
    print(f({"a": [1]}))
