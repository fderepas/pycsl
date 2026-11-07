from typing import Any, Dict

#@ no_exception \all
#@ ensures \result == 1
def g(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1

#@ no_exception \all
#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    v = m.get("a")
    s = {v}
    return 1

if __name__ == "__main__":
    print(g({"a": [1]}))
