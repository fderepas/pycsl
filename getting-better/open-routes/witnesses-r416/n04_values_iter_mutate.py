from typing import Dict


#@ no_exception \all
def f(d: Dict[int, int]) -> int:
    for v in d.values():
        d[v + 100] = 0
    return 0


if __name__ == "__main__":
    try:
        r = f({1: 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
