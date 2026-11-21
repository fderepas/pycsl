from typing import Dict, Any

#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    #@ ensures \result == 1
    def inner(m2: Dict[str, Any]) -> int:
        try:
            n = hash(m2.get("a"))
            return 1
        except TypeError:
            return 2
    return inner(m)

if __name__ == "__main__":
    print(f({"a": [1]}))
