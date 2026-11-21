from typing import Dict, Any

#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    r = 2
    for i in range(1):
        try:
            n = hash(m.get("a"))
            r = 1
        finally:
            break
    return r

if __name__ == "__main__":
    print(f({"a": [1]}))
