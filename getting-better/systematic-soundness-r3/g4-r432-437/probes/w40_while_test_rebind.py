from typing import Optional

#@ no_exception \all
def f(x: Optional[str]) -> int:
    n = 0
    if x is not None:
        while x.startswith("a"):
            x = None
            n += 1
    return n


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
