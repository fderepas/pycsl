from typing import Dict, List

#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(d: Dict[str, int], out: List[int]) -> None:
    out[0] = 2
    try:
        x = d["a"]
        out[0] = 1
    finally:
        return

if __name__ == "__main__":
    o = [0]
    f({}, o)
    print(o)
