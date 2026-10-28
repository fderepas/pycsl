from typing import Dict, Any, List

class CM:
    #@ requires True
    #@ ensures True
    def __enter__(self) -> "CM":
        return self

    #@ requires True
    #@ ensures \result == True
    def __exit__(self, a: Any, b: Any, c: Any) -> bool:
        return True

#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(m: Dict[str, Any], out: List[int]) -> None:
    out[0] = 2
    with CM():
        n = hash(m.get("a"))
        out[0] = 1

if __name__ == "__main__":
    o = [0]
    f({"a": [1]}, o)
    print(o)
