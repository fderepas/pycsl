from typing import Dict, Any, List

#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    n = hash(m.get("a"))
    return 1

#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def caller(m: Dict[str, Any], out: List[int]) -> None:
    out[0] = 2
    try:
        out[0] = h(m)
    finally:
        return

if __name__ == "__main__":
    o = [0]
    caller({"a": [1]}, o)
    print(o)
