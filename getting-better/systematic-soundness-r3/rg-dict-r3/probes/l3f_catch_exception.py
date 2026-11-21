from typing import Dict, Any

#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1

#@ ensures \result == 1
def caller(m: Dict[str, Any]) -> int:
    r = 0
    try:
        r = h(m)
    except Exception:
        r = 2
    return r

if __name__ == "__main__":
    print(caller({"a": [1]}))
