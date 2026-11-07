from typing import Optional, Tuple

#@ no_exception \all
def f(t: Tuple[str, Optional[str]]) -> int:
    return len("".join(t))


if __name__ == "__main__":
    try:
        r = f(("a", None))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
