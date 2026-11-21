from typing import Dict, Any

#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    try:
        s = {m.get("a")}
    except TypeError:
        return 2
    return 1

if __name__ == "__main__":
    print(f({"a": [1]}))
