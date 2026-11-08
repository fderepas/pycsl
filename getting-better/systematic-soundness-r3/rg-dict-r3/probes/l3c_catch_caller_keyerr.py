from typing import Dict

#@ ensures \result == 1
def h(d: Dict[str, int]) -> int:
    x = d["a"]
    return 1

#@ ensures \result == 1
def caller(d: Dict[str, int]) -> int:
    try:
        r = h(d)
    except KeyError:
        r = 2
    return r

if __name__ == "__main__":
    print(caller({}))
