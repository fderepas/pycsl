from typing import Dict, Any

#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1

#@ no_exception \all
#@ ensures \result == 1
def caller(m: Dict[str, Any]) -> int:
    return h(m)

if __name__ == "__main__":
    print(caller({"a": [1]}))
