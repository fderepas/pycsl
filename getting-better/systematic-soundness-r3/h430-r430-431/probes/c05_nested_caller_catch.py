from typing import Dict, Any

#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    #@ ensures \result == 1
    def inner(m2: Dict[str, Any]) -> int:
        n = hash(m2.get("a"))
        return 1
    try:
        r = inner(m)
    except TypeError:
        r = 2
    return r

if __name__ == "__main__":
    print(f({"a": [1]}))
