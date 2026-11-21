from typing import Dict, Any

#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    n = hash(m.get("a"))
    return 1

#@ ensures \result == 1
def caller(m: Dict[str, Any]) -> int:
    try:
        r = h(m)
    except BaseException:
        r = 2
    return r

if __name__ == "__main__":
    print(caller({"a": [1]}))
