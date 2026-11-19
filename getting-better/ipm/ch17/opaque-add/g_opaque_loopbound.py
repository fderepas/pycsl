from typing import List


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def f(words: List[str]) -> int:
    s = {w for w in words}
    for s in [{"a"}]:
        pass
    s.add("x")
    return 1 if "x" in s else 0


if __name__ == "__main__":
    print(f(["a"]))
