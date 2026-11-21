from typing import List, Optional

#@ no_exception \all
def f(xs: List[Optional[int]]) -> int:
    ys = sorted(xs)
    return len(ys)


if __name__ == "__main__":
    try:
        r = f([1, None])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
