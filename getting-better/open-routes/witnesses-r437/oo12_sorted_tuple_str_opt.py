from typing import List, Optional, Tuple

#@ no_exception \all
def f(xs: List[Tuple[str, Optional[int]]]) -> int:
    ys = sorted(xs)
    return len(ys)


if __name__ == "__main__":
    try:
        r = f([("a", 1), ("a", None)])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
