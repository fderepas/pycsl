from typing import List, Tuple

def g3(t: Tuple[List[int], int]) -> Tuple:
    return t

#@ no_exception \all
def f(t: Tuple[List[int], int]) -> int:
    s = {g3(t)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(([1], 1))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
