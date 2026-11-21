from typing import Dict, Any, List, Iterator

#@ requires True
#@ ensures True
def gen(m: Dict[str, Any]) -> Iterator[int]:
    try:
        yield 1
        n = hash(m.get("a"))
        yield 2
    except BaseException:
        pass

#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    r = 0
    for x in gen(m):
        r = r + x
    return r

if __name__ == "__main__":
    print(f({"a": [1]}))
