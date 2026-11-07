from typing import List, Tuple
def g(t: Tuple[List[int], int]) -> tuple:
    return t

#@ no_exception \all
def f(t: Tuple[List[int], int]) -> int:
    k = g(t)
    s = {k}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(([1], 1))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
