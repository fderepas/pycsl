from typing import List, Optional

#@ no_exception \all
def f(xs: List[Optional[str]]) -> int:
    ys = sorted(xs)
    return len(ys)


if __name__ == "__main__":
    try:
        r = f(["a", None])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
