from typing import Dict, Any, Set, List

#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(m: Dict[str, Any], t: Set[Any], out: List[int]) -> None:
    out[0] = 2
    try:
        t.add(m.get("a"))
        out[0] = 1
    finally:
        return

if __name__ == "__main__":
    o = [0]
    f({"a": [1]}, set(), o)
    print(o)
